"""
Wall-clock protocol, revision 3: rerun under uniform machine conditions
(design: results/rerun_plan.md). Replaces the archived first attempt in
results/raw/archive_2026-11-14_battery/. Jobs run strictly one at a time.

Per instance, every compared method is run back to back:
  1. the LP bound and the LP-Round start (measured once; every method that starts from
     LP-Round is charged this measured time);
  2. all LNS units (method x run, 5 runs per method) in an order drawn with
     np.random.default_rng([ORDER_SEED, job id, instance position]);
  3. all HiGHS units in an order drawn from the same generator. Wall- and CPU-matched
     limits are the mean wall-clock / CPU time of the five PC-MALNS [Greedy-Efficiency]
     runs of step 2 (this session, same instance).
A calibration job (PC-MALNS [Greedy-Efficiency], Large seed 101, run 0, work protocol on
the W = 4 pool) runs at the start of each job, after every 10 instances and at the end;
drift above 10% (wall or CPU) relative to the first calibration of the run is logged
and flagged, and the run continues. Before every unit the power source is checked; on
battery power the run waits until AC power returns (the waiting time is recorded).
Every row records the time stamp, power source and charge, load averages, the index of
the latest calibration and the HiGHS version.

Jobs (outputs in results/raw/):
  calib  N calibration runs only (preflight), phase "preflight"
  main   P = 6, eta = 1.25, Small..XXXL, seeds 101..110            -> wall_main.csv
  rich   P = 20, 40, Medium..XXL, seeds 101..110                    -> wall_rich.csv
  sweep  Large, eta = 0.85, 1.05, 1.45, seeds 101..110             -> wall_sweep.csv
  pair   MCA-SC-Pair, Medium and Large, seeds 101..110             -> wall_pair.csv
  mmkp   the 27 MMKP instances, K = 8                              -> wall_mmkp.csv
HiGHS reference runs (dual bound, trace): wall_reference.csv; calibration: wall_calibration.csv.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.instance_generator import generate_instance
from src.sync_instances import generate_sync_instance
from src.baselines import solve_lp_relaxation, lp_round_start
from src.feasibility import evaluate_global_cost, verify_solution_feasibility
from src.highs_runner import solve_highs
from src.engine import run_engine, method_configs
from src.agent_pool import AgentPool
from src.async_lock import AsyncPool

RAW = REPO_ROOT / "results" / "raw"
SEEDS = list(range(101, 111))
SCALES = {"Small": (4, 30), "Medium": (8, 40), "Large": (12, 50), "X-Large": (16, 60),
          "XXL": (24, 100), "XXXL": (32, 125)}
BUDGET = {"Small": 0.5, "Medium": 1.0, "Large": 1.5, "X-Large": 2.0, "XXL": 4.0, "XXXL": 6.0}
MMKP_BUDGET, MMKP_K = 2.0, 8
REPS = 5
M_INNER = 5
MCCRIP_LIMIT = 2.0
ORDER_SEED = 20261114
JOB_ID = {"main": 1, "rich": 2, "sweep": 3, "pair": 4, "mmkp": 5,
          "rich_rerun": 2}   # same orders as rich: only the machine state differs
CAL_EVERY = 10
DRIFT_TOL = 0.10
CAL_SCALE, CAL_SEED, CAL_WORK = "Large", 101, 5 * M_INNER * 45   # work budget of Large

GE = "PC-MALNS [Greedy-Efficiency]"
MC = "PC-MALNS [MC-CRIP]"
QS = "PC-MALNS [Quota-Surplus]"
GG = "PC-MALNS [Greedy-Gain]"
LNS = {
    "main": [GE, MC, "Opt-Rollback", "Opt-SeqLock"],
    "rich": [GE, MC, QS, "Opt-Rollback", "Opt-SeqLock"],
    "sweep": [GE, MC, QS, "Opt-Rollback", "Opt-SeqLock", "Static-Quota"],
    "pair": [GE, MC, QS, GG, "Opt-Rollback-Portfolio", "Opt-SeqLock-Portfolio", "Opt-Rollback", "Opt-SeqLock"],
    "mmkp": [GE, MC, QS, "Opt-Rollback", "Opt-SeqLock", "Static-Quota"],
}
LNS["rich_rerun"] = LNS["rich"]
ASYNC = {"main"}                       # jobs that include Async-Lock
# rich_rerun (sensitivity, rerun_plan.md addendum 2026-11-20): the rich instances run between
# calibration 14 (last normal one before the slow stretch) and calibration 18 (first normal one after),
# rerun with the identical design into wall_rich_rerun.csv. The original rows stay primary.
RERUN_CALIBS = (14, 15, 16, 17)
T_REF = {"rich": 300.0, "rich_rerun": 300.0, "sweep": 60.0, "pair": 60.0, "mmkp": 60.0}   # main: 600 s Small/Medium, else 60 s
TRACE_POINTS = {"main": (5.0, 60.0), "rich": (5.0, 30.0), "rich_rerun": (5.0, 30.0), "sweep": (5.0, 30.0), "pair": (5.0,), "mmkp": (5.0,)}
WARM = {"main", "rich", "rich_rerun", "sweep", "pair"}   # HiGHS + LP-Round MIP start (not MMKP: its LP-Round start
                                           # leaves groups unassigned)


def _highs_version():
    import contextlib, io
    import highspy
    with contextlib.redirect_stdout(io.StringIO()):
        h = highspy.Highs()
    return f"{h.version()} ({h.githash()})"


HIGHS_VERSION = _highs_version()


# ---------------------------------------------------------------------------
# Machine state
# ---------------------------------------------------------------------------
def power():
    out = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True).stdout
    src = re.search(r"drawing from '([^']+)'", out)
    pct = re.search(r"(\d+)%", out)
    return (src.group(1) if src else "unknown"), (int(pct.group(1)) if pct else -1)


class State:
    def __init__(self, log):
        self.cal_index = -1
        self.cal0 = None          # (wall, cpu) of the first calibration of the run
        self.wait_s = 0.0
        self.log = log

    def wait_for_ac(self):
        src, pct = power()
        t0 = time.perf_counter()
        warned = False
        while src != "AC Power":
            if not warned:
                self.log(f"WAIT on {src} ({pct}%): paused until AC power returns")
                warned = True
            time.sleep(60)
            src, pct = power()
        if warned:
            self.wait_s += time.perf_counter() - t0
            self.log(f"RESUME on AC power after {time.perf_counter() - t0:.0f}s")

    def meta(self):
        src, pct = power()
        l1, l5, l15 = os.getloadavg()
        d = dict(timestamp=datetime.now().astimezone().isoformat(timespec="seconds"), power_source=src,
                 battery_pct=pct, load1=round(l1, 2), load5=round(l5, 2), load15=round(l15, 2),
                 calib_index=self.cal_index, ac_wait_s=round(self.wait_s, 1), highs_version=HIGHS_VERSION)
        self.wait_s = 0.0
        return d


def append(path, rows):
    if not rows:
        return
    df = pd.DataFrame(rows)
    if path.exists():
        cols = list(pd.read_csv(path, nrows=0).columns)
        new = [c for c in df.columns if c not in cols]
        if new:   # a column added during the run (e.g. highs_killed): widen the file, old rows empty
            old = pd.read_csv(path, low_memory=False)
            pd.concat([old, df.reindex(columns=cols + new)], ignore_index=True).to_csv(path, index=False)
            return
        df = df.reindex(columns=cols)
    df.to_csv(path, mode="a", header=not path.exists(), index=False)


def done(path):
    return set(pd.read_csv(path, usecols=["instance_name"])["instance_name"]) if path.exists() else set()


def obj_at(trace, T):
    v = None
    for t, o in trace:
        if t <= T + 1e-9:
            v = o
    return v


# ---------------------------------------------------------------------------
# Calibration
# ---------------------------------------------------------------------------
def calibrate(st, pool, phase, job):
    st.wait_for_ac()
    K, n = SCALES[CAL_SCALE]
    inst = generate_instance(K, n, P=6, tightness=1.25, seed=CAL_SEED, scale=CAL_SCALE)
    cfg = method_configs(init_mode="lp_round", max_net=None, inner_iters=M_INNER)[GE]
    cfg.work_budget, cfg.time_budget_s, cfg.counterfactual = CAL_WORK, None, False
    r = run_engine(inst, cfg, 1.0, seed=CAL_SEED, rep=0, pool=pool)
    path = RAW / "wall_calibration.csv"
    prev = pd.read_csv(path) if path.exists() else pd.DataFrame()
    st.cal_index = int(len(prev))
    row = dict(st.meta(), phase=phase, job=job, instance_name=inst.name, method=GE, work_budget=CAL_WORK,
               epochs_run=r.epochs_run, best_obj=r.best_obj, wall_clock_s=r.wall_clock_s, cpu_time_s=r.cpu_time_s)
    row["calib_index"] = st.cal_index
    if phase == "run":
        runs = prev[prev.phase == "run"] if len(prev) else prev
        if st.cal0 is None:
            st.cal0 = ((float(runs.iloc[0].wall_clock_s), float(runs.iloc[0].cpu_time_s)) if len(runs)
                       else (r.wall_clock_s, r.cpu_time_s))
        dw, dc = r.wall_clock_s / st.cal0[0] - 1.0, r.cpu_time_s / st.cal0[1] - 1.0
        row.update(drift_wall=round(dw, 4), drift_cpu=round(dc, 4),
                   drift_flag=bool(abs(dw) > DRIFT_TOL or abs(dc) > DRIFT_TOL))
    append(path, [row])
    msg = (f"[calib {st.cal_index}] {phase}/{job} wall {r.wall_clock_s:.3f}s cpu {r.cpu_time_s:.3f}s "
           f"obj {r.best_obj:.4f} load1 {row['load1']} {row['power_source']}")
    if row.get("drift_flag"):
        msg += f"  DRIFT wall {100 * row['drift_wall']:+.1f}% cpu {100 * row['drift_cpu']:+.1f}%"
    st.log(msg)
    return r


# ---------------------------------------------------------------------------
# Units
# ---------------------------------------------------------------------------
def lns_unit(st, inst, base, name, rep, budget, pool, lb, seed):
    st.wait_for_ac()
    cfg = method_configs(init_mode="lp_round", max_net=None, inner_iters=M_INNER)[name]
    cfg.time_budget_s, cfg.budget_clock, cfg.work_budget = budget, "wall", None
    cfg.counterfactual, cfg.mccrip_time_limit = False, MCCRIP_LIMIT
    m = st.meta()
    r = run_engine(inst, cfg, lb, seed=seed, rep=rep, pool=pool)
    if not r.feasible:
        raise RuntimeError(f"infeasible: {name} {inst.name} rep {rep}")
    return dict(base, **m, method=name, family="LNS", rep=rep, workers_W=r.workers_W, threads=np.nan,
                wall_budget_s=budget, best_obj=r.best_obj, initial_obj=r.initial_obj, feasible=r.feasible,
                wall_clock_s=r.wall_clock_s, cpu_time_s=r.cpu_time_s, init_time_s=r.init_time_s,
                epochs_run=r.epochs_run, barrier_s_total=r.barrier_s_total, conflict_epochs=r.conflict_epochs,
                accepted_moves=r.accepted_moves, proposals=r.proposals, matcher_ms_mean=r.matcher_ms_mean,
                matcher_fallbacks=r.matcher_fallbacks, l0_tries=r.l0_tries, l0_dominated=r.l0_dominated,
                l0_committed=r.l0_committed,
                trace=json.dumps([[round(t, 4), round(o, 4)] for t, o in zip(r.trace_t, r.trace_obj)]))


def async_unit(st, inst, base, rep, budget, ap, seed):
    st.wait_for_ac()
    m = st.meta()
    r = ap.run(inst, budget, seed=seed, rep=rep)
    if not r.feasible:
        raise RuntimeError(f"infeasible: Async-Lock {inst.name} rep {rep}")
    return dict(base, **m, method="Async-Lock", family="LNS", rep=rep, workers_W=4, threads=np.nan,
                wall_budget_s=budget, best_obj=r.best_obj, initial_obj=r.initial_obj, feasible=r.feasible,
                wall_clock_s=r.wall_clock_s, cpu_time_s=r.cpu_time_s, init_time_s=r.init_time_s,
                steps_total=r.steps_total, steps_per_agent=r.steps_per_agent, proposals=r.proposals,
                accepted_moves=r.accepted_moves, rejected_fit=r.rejected_fit,
                trace=json.dumps([[round(t, 4), round(o, 4)] for t, o in zip(r.trace_t, r.trace_obj)]))


def highs_unit(st, inst, base, label, T, threads, start=None, t_start=0.0):
    st.wait_for_ac()
    m = st.meta()
    h = solve_highs(inst, max(0.05, T - t_start), threads=threads, start_patterns=start)
    obj = h["obj"] if np.isfinite(h["obj"]) else None
    if obj is None and start is not None:
        obj = evaluate_global_cost(inst, start)       # the MIP start itself is a solution
    return h, dict(base, **m, method=label, family="HiGHS", rep=0, threads=threads,
                   start="lp_round" if start is not None else "cold", matched_time_s=T, start_time_s=t_start,
                   highs_time_limit_s=max(0.05, T - t_start), highs_actual_time_s=h["highs_actual_time_s"],
                   highs_status=h["status"], highs_dual=h["dual_bound"], nodes=h.get("nodes"),
                   highs_killed=bool(h.get("killed", False)),
                   best_obj=np.nan if obj is None else obj, feasible=obj is not None,
                   wall_clock_s=t_start + h["highs_actual_time_s"], highs_source="run",
                   trace=json.dumps([[round(t + t_start, 4), round(o, 4)] for t, o in h["trace"]]))


# ---------------------------------------------------------------------------
# One instance
# ---------------------------------------------------------------------------
def run_instance(st, job, pos, inst, scale, budget, T_ref, pool, ap, seed, extra=None, mmkp=None):
    rng = np.random.default_rng([ORDER_SEED, JOB_ID[job], pos])
    t0 = time.perf_counter()
    base = dict(job=job, instance_name=inst.name, scale=scale, K=inst.K, N_total=inst.N_total, P=inst.P,
                m_global=inst.m_global, eta=getattr(inst, "tightness", np.nan), seed=seed,
                order_seed=f"{ORDER_SEED}/{JOB_ID[job]}/{pos}", **(extra or {}))
    st.wait_for_ac()
    m = st.meta()
    lp = solve_lp_relaxation(inst)
    pats, lt, rt = lp_round_start(inst)                  # cached; every LP-Round start is charged lt + rt
    c0 = evaluate_global_cost(inst, pats)
    base["lp_bound"] = lp["lp_bound"]
    rows = [dict(base, **m, method="LP-Round", family="Deterministic", rep=0, order_pos=-1, best_obj=c0,
                 initial_obj=c0, feasible=bool(verify_solution_feasibility(inst, pats)[0]),
                 wall_clock_s=lt + rt, cpu_time_s=lt + rt, init_time_s=lt + rt)]

    units = [(nm, rep) for nm in LNS[job] for rep in range(REPS)]
    if job in ASYNC:
        units += [("Async-Lock", rep) for rep in range(REPS)]
    for j, idx in enumerate(rng.permutation(len(units))):
        nm, rep = units[idx]
        if nm == "Async-Lock":
            d = async_unit(st, inst, base, rep, budget, ap, seed)
        else:
            d = lns_unit(st, inst, base, nm, rep, budget, pool, lp["lp_bound"], seed)
        d["order_pos"] = j
        rows.append(d)

    ge = [r for r in rows if r["method"] == GE]
    T_wall = float(np.mean([r["wall_clock_s"] for r in ge]))
    T_cpu = float(np.mean([r["cpu_time_s"] for r in ge]))
    t_lpr = lt + rt
    hunits = [("ref", T_ref, 1, None), ("HiGHS (1T, wall-matched)", T_wall, 1, None),
              ("HiGHS (4T, wall-matched)", T_wall, 4, None), ("HiGHS (1T, CPU-matched)", T_cpu, 1, None)]
    if job in WARM:
        hunits += [("HiGHS+LP-Round (1T, wall-matched)", T_wall, 1, pats),
                   ("HiGHS+LP-Round (1T, CPU-matched)", T_cpu, 1, pats)]
    for j, idx in enumerate(rng.permutation(len(hunits))):
        lab, T, th, start = hunits[idx]
        name = f"HiGHS ({T:.0f}s)" if lab == "ref" else lab
        h, d = highs_unit(st, inst, base, name, T, th, start=start, t_start=t_lpr if start is not None else 0.0)
        d["order_pos"] = len(units) + j
        rows.append(d)
        if lab == "ref":
            append(RAW / "wall_reference.csv", [dict(
                instance_name=inst.name, job=job, scale=scale, K=inst.K, P=inst.P, eta=base["eta"], seed=seed,
                timestamp=d["timestamp"], highs_version=HIGHS_VERSION, lp_bound=lp["lp_bound"],
                lp_round_time_s=t_lpr, highs_obj=h["obj"], highs_dual=h["dual_bound"], highs_status=h["status"],
                highs_time_limit_s=T, highs_actual_time_s=h["highs_actual_time_s"], highs_nodes=h.get("nodes"),
                highs_killed=bool(h.get("killed", False)),
                trace=json.dumps(h["trace"]))])
            for Tp in TRACE_POINTS[job]:
                if Tp < T:
                    o = obj_at(h["trace"], Tp)
                    rows.append(dict(base, **{k: d[k] for k in ("timestamp", "power_source", "battery_pct", "load1",
                                                                "load5", "load15", "calib_index", "highs_version")},
                                     method=f"HiGHS ({Tp:.0f}s)", family="HiGHS", rep=0, threads=1, start="cold",
                                     matched_time_s=Tp, best_obj=np.nan if o is None else o, feasible=o is not None,
                                     highs_source=f"trace of HiGHS ({T:.0f}s)", order_pos=d["order_pos"]))
    if mmkp is not None:
        for r in rows:
            r.update(mmkp(r["best_obj"] if r.get("feasible") else None))
    out = RAW / f"wall_{job}.csv"
    append(out, rows)
    g = pd.DataFrame(rows).groupby("method", sort=False)["best_obj"].mean()
    st.log(f"[{job}] {inst.name} ({time.perf_counter() - t0:.0f}s, calib {st.cal_index}) " +
           " ".join(f"{k}={v:.1f}" for k, v in g.items()))


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------
def instances(job):
    if job == "main":
        for scale, (K, n) in SCALES.items():
            for s in SEEDS:
                yield scale, s, generate_instance(K, n, P=6, tightness=1.25, seed=s, scale=scale), BUDGET[scale], \
                    (600.0 if scale in ("Small", "Medium") else 60.0), None, None
    elif job in ("rich", "rich_rerun"):
        for P in (20, 40):
            for scale in ("Medium", "Large", "X-Large", "XXL"):
                K, n = SCALES[scale]
                for s in SEEDS:
                    yield scale, s, generate_instance(K, n, P=P, tightness=1.25, seed=s, scale=scale), \
                        BUDGET[scale], T_REF[job], None, None
    elif job == "sweep":
        K, n = SCALES["Large"]
        for eta in (0.85, 1.05, 1.45):
            for s in SEEDS:
                yield "Large", s, generate_instance(K, n, P=6, tightness=eta, seed=s, scale="Large"), \
                    BUDGET["Large"], T_REF[job], None, None
    elif job == "pair":
        for scale in ("Medium", "Large"):
            K, n = SCALES[scale]
            for s in SEEDS:
                yield scale, s, generate_sync_instance(K, n, P=6, tightness=1.25, seed=s, scale=scale), \
                    BUDGET[scale], T_REF[job], None, None
    elif job == "mmkp":
        from src.mmkp import NAMES, read_mmkp, read_certificate, to_instance
        from scripts.run_mmkp_benchmarks import mmkp_fields
        for name in NAMES:
            raw = read_mmkp(name)
            bkv, _ = read_certificate(name, raw)
            inst = to_instance(raw, MMKP_K)
            yield "MMKP", 0, inst, MMKP_BUDGET, T_REF[job], \
                dict(mmkp=name, n_groups=raw["n"], items=raw["l"], bkv=bkv), \
                (lambda cost, inst=inst, bkv=bkv: mmkp_fields(inst, cost, bkv))
    else:
        raise ValueError(job)


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("job", choices=["calib", "main", "rich", "rich_rerun", "sweep", "pair", "mmkp"])
    ap_.add_argument("--n", type=int, default=3, help="calib: number of calibration runs")
    a = ap_.parse_args()
    logf = open(REPO_ROOT / "results" / "logs" / f"uniform_{a.job}.log", "a")

    def log(msg):
        line = f"{datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
        print(line, flush=True)
        logf.write(line + "\n")
        logf.flush()

    st = State(log)
    t0 = time.perf_counter()
    pool = AgentPool(4)
    log(f"START {a.job}: highs {HIGHS_VERSION}, pool W=4 startup {pool.startup_s:.2f}s")
    if a.job == "calib":
        for _ in range(a.n):
            calibrate(st, pool, "preflight", "calib")
        pool.close()
        return
    asp = AsyncPool(4) if a.job in ASYNC else None
    calibrate(st, pool, "run", a.job)
    fin = done(RAW / f"wall_{a.job}.csv")
    keep = None
    if a.job == "rich_rerun":
        r0 = pd.read_csv(RAW / "wall_rich.csv", usecols=["instance_name", "calib_index"])
        keep = set(r0[r0.calib_index.isin(RERUN_CALIBS)].instance_name)
        log(f"rich_rerun: {len(keep)} instances (calibrations {RERUN_CALIBS})")
    count = 0
    for pos, (scale, seed, inst, budget, T_ref, extra, mm) in enumerate(instances(a.job)):
        if inst.name in fin or (keep is not None and inst.name not in keep):
            continue
        run_instance(st, a.job, pos, inst, scale, budget, T_ref, pool, asp, seed, extra, mm)
        count += 1
        if count % CAL_EVERY == 0:
            calibrate(st, pool, "run", a.job)
    if count % CAL_EVERY != 0:
        calibrate(st, pool, "run", a.job)
    if asp is not None:
        asp.close()
    pool.close()
    log(f"WALL-UNIFORM {a.job} done in {time.perf_counter() - t0:.0f}s ({count} instances)")


if __name__ == "__main__":
    main()
