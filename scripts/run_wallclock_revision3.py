"""
Secondary (wall-clock) protocol, revision 3: comparisons that need real time.
Every job runs strictly one at a time, after the work-protocol jobs.

  async        Async-Lock (src/async_lock.py) on the main benchmark (P = 6, eta = 1.25,
               Small..XXXL, seeds 101..110), 5 runs per instance, W = 4, the wall-clock
               budgets of results/raw/bench_A.csv.
  highs_main   HiGHS 1.16.0 on the main benchmark:
                 reference run, 1 thread, 600 s (Small, Medium) or 60 s (Large..XXXL);
                 its incumbent trace gives HiGHS (5s), (60s), (600s) and the cold
                 CPU-matched value; wall-matched cold runs with 1 and 4 threads;
                 HiGHS + LP-Round start (MIP start), wall-matched and CPU-matched real runs
                 with 1 thread, whose time limit is the matched time minus the measured
                 LP-Round time (so the start is charged as for PC-MALNS).
               Matched times: mean wall-clock / CPU time of the five
               PC-MALNS [Greedy-Efficiency] runs of the instance in bench_A.csv.
  highs_rich   the same on the rich-pool instances (P = 20, 40; Medium..XXL) of
               bench_B.csv with a 300 s reference run (trace gives HiGHS (30s)).
  highs_sweep  the same on the tightness sweep (Large, eta 0.85, 1.05, 1.45) of
               bench_E_sweep.csv with a 60 s reference run.
  highs_pair   reference (60 s) and wall-matched 1-thread runs on MCA-SC-Pair (C_sync).
  mmkp         HiGHS 1.16.0 (60 s, wall-matched 1 and 4 threads) on the 27 MMKP
               instances, plus 5 wall-clock runs of PC-MALNS [Greedy-Efficiency]
               (appended to bench_D_mmkp.csv; the other LNS rows are unchanged).
Outputs: results/raw/wall_async.csv, highs116_<table>.csv, highs116_reference.csv.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.instance_generator import generate_instance
from src.sync_instances import generate_sync_instance
from src.baselines import solve_lp_relaxation, lp_round_start
from src.feasibility import evaluate_global_cost
from src.highs_runner import solve_highs
from src.engine import run_engine, primal_integral, method_configs
from src.async_lock import AsyncPool

RAW = REPO_ROOT / "results" / "raw"
TEST_SEEDS = list(range(101, 111))
SCALES = {"Small": (4, 30), "Medium": (8, 40), "Large": (12, 50), "X-Large": (16, 60),
          "XXL": (24, 100), "XXXL": (32, 125)}
BUDGET = {"Small": 0.5, "Medium": 1.0, "Large": 1.5, "X-Large": 2.0, "XXL": 4.0, "XXXL": 6.0}
PRIMARY = "PC-MALNS [Greedy-Efficiency]"
REPS = 5


def append(path, rows):
    df = pd.DataFrame(rows)
    if path.exists():
        df = df.reindex(columns=pd.read_csv(path, nrows=0).columns)
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
def run_async():
    path = RAW / "wall_async.csv"
    fin = done(path)
    ap = AsyncPool(4)
    print(f"async pool startup {ap.startup_s:.2f}s", flush=True)
    for scale, (K, n) in SCALES.items():
        for seed in TEST_SEEDS:
            inst = generate_instance(K, n, P=6, tightness=1.25, seed=seed, scale=scale)
            if inst.name in fin:
                continue
            rows = []
            for rep in range(REPS):
                r = ap.run(inst, BUDGET[scale], seed=seed, rep=rep)
                assert r.feasible
                d = dict(table="A", instance_name=inst.name, scale=scale, K=K, seed=seed, method="Async-Lock",
                         rep=rep, workers_W=4, wall_budget_s=BUDGET[scale], best_obj=r.best_obj,
                         initial_obj=r.initial_obj, feasible=r.feasible, wall_clock_s=r.wall_clock_s,
                         cpu_time_s=r.cpu_time_s, init_time_s=r.init_time_s, steps_total=r.steps_total,
                         steps_per_agent=r.steps_per_agent, proposals=r.proposals,
                         accepted_moves=r.accepted_moves, rejected_fit=r.rejected_fit)
                if rep == 0:
                    d["trace"] = json.dumps([[round(t, 4), round(o, 4)] for t, o in zip(r.trace_t, r.trace_obj)])
                rows.append(d)
            append(path, rows)
            print(f"[async] {inst.name} {np.mean([r['best_obj'] for r in rows]):.1f} "
                  f"steps/agent {np.mean([r['steps_per_agent'] for r in rows]):.1f}", flush=True)
    ap.close()


# ---------------------------------------------------------------------------
def save_reference(inst, scale, table, T, lp, h, t_lp):
    row = dict(instance_name=inst.name, table=table, scale=scale, K=inst.K, P=inst.P, eta=inst.tightness,
               seed=inst.seed, highs_version="1.16.0", lp_bound=lp, lp_time_s=t_lp, highs_obj=h["obj"],
               highs_dual=h["dual_bound"], highs_status=h["status"], highs_time_limit_s=T,
               highs_actual_time_s=h["highs_actual_time_s"], highs_nodes=h.get("nodes"),
               trace=json.dumps(h["trace"]))
    append(RAW / "highs116_reference.csv", [row])


def hrow(table, inst, scale, method, obj, T, threads, h, source, start="cold", t_start=0.0):
    tr = h["trace"]
    return dict(table=table, instance_name=inst.name, scale=scale, K=inst.K, P=inst.P, eta=inst.tightness,
                seed=inst.seed, method=method, family="HiGHS", start=start, threads=threads,
                highs_version="1.16.0", best_obj=np.nan if obj is None else obj,
                feasible=obj is not None and np.isfinite(obj), matched_time_s=T, start_time_s=t_start,
                highs_time_limit_s=T - t_start if source == "run" else T,
                highs_actual_time_s=h["highs_actual_time_s"] if source == "run" else min(T, h["highs_actual_time_s"]),
                highs_status=h["status"] if source == "run" else f"trace of {h['highs_time_limit_s']:.0f}s run",
                highs_source=source, nodes=h.get("nodes") if source == "run" else np.nan,
                trace=json.dumps([[round(t + t_start, 4), round(o, 4)] for t, o in tr]) if source == "run" else "")


def highs_instance(table, inst, scale, T_ref, trace_points, lns, threads4=True, warm=True):
    """lns: rows of PC-MALNS [Greedy-Efficiency] for this instance (wall-clock protocol)."""
    t0 = time.perf_counter()
    lp = solve_lp_relaxation(inst)["lp_bound"]
    pats, lt, rt = lp_round_start(inst)
    t_lpr = lt + rt
    h = solve_highs(inst, T_ref, threads=1)
    save_reference(inst, scale, table, T_ref, lp, h, t_lpr)
    rows = []
    for T in trace_points:
        if T < T_ref:
            rows.append(hrow(table, inst, scale, f"HiGHS ({T:.0f}s)", obj_at(h["trace"], T), T, 1, h, "trace"))
    hobj = h["obj"] if np.isfinite(h["obj"]) else None
    rows.append(hrow(table, inst, scale, f"HiGHS ({T_ref:.0f}s)", hobj, T_ref, 1, h, "run"))
    T_wall = float(np.mean(lns["wall_clock_s"]))
    T_cpu = float(np.mean(lns["cpu_time_s"]))
    rows.append(hrow(table, inst, scale, "HiGHS (1T, CPU-matched)", obj_at(h["trace"], T_cpu), T_cpu, 1, h,
                     "trace"))
    for th in ((1, 4) if threads4 else (1,)):
        hm = solve_highs(inst, T_wall, threads=th)
        rows.append(hrow(table, inst, scale, f"HiGHS ({th}T, wall-matched)",
                         hm["obj"] if np.isfinite(hm["obj"]) else None, T_wall, th, hm, "run"))
    if warm:
        for lab, T in (("wall-matched", T_wall), ("CPU-matched", T_cpu)):
            hw = solve_highs(inst, max(0.05, T - t_lpr), threads=1, start_patterns=pats)
            o = hw["obj"] if np.isfinite(hw["obj"]) else evaluate_global_cost(inst, pats)
            rows.append(hrow(table, inst, scale, f"HiGHS+LP-Round (1T, {lab})", o, T, 1, hw, "run",
                             start="lp_round", t_start=t_lpr))
    append(RAW / f"highs116_{table}.csv", rows)
    g = {r["method"]: r["best_obj"] for r in rows}
    print(f"[highs_{table}] {inst.name} ({time.perf_counter() - t0:.0f}s) " +
          " ".join(f"{m}={v:.1f}" for m, v in g.items()), flush=True)


def lns_rows(csv, inst_name, method=PRIMARY):
    df = pd.read_csv(RAW / csv, usecols=["instance_name", "method", "wall_clock_s", "cpu_time_s"])
    sub = df[(df.instance_name == inst_name) & (df.method == method)]
    assert len(sub) == REPS, (csv, inst_name, len(sub))
    return sub


def run_highs_main():
    fin = done(RAW / "highs116_main.csv")
    for scale, (K, n) in SCALES.items():
        T_ref = 600.0 if scale in ("Small", "Medium") else 60.0
        for seed in TEST_SEEDS:
            inst = generate_instance(K, n, P=6, tightness=1.25, seed=seed, scale=scale)
            if inst.name not in fin:
                highs_instance("main", inst, scale, T_ref, (5.0, 60.0), lns_rows("bench_A.csv", inst.name))


def run_highs_rich():
    fin = done(RAW / "highs116_rich.csv")
    for P in (20, 40):
        for scale in ("Medium", "Large", "X-Large", "XXL"):
            K, n = SCALES[scale]
            for seed in TEST_SEEDS:
                inst = generate_instance(K, n, P=P, tightness=1.25, seed=seed, scale=scale)
                if inst.name not in fin:
                    highs_instance("rich", inst, scale, 300.0, (5.0, 30.0), lns_rows("bench_B.csv", inst.name))


def run_highs_sweep():
    fin = done(RAW / "highs116_sweep.csv")
    K, n = SCALES["Large"]
    for eta in (0.85, 1.05, 1.45):
        for seed in TEST_SEEDS:
            inst = generate_instance(K, n, P=6, tightness=eta, seed=seed, scale="Large")
            if inst.name not in fin:
                highs_instance("sweep", inst, "Large", 60.0, (5.0, 30.0), lns_rows("bench_E_sweep.csv", inst.name))


def run_highs_pair():
    fin = done(RAW / "highs116_pair.csv")
    for scale in ("Medium", "Large"):
        K, n = SCALES[scale]
        for seed in TEST_SEEDS:
            inst = generate_sync_instance(K, n, P=6, tightness=1.25, seed=seed, scale=scale)
            if inst.name not in fin:
                highs_instance("pair", inst, scale, 60.0, (5.0,), lns_rows("bench_C_sync.csv", inst.name),
                               threads4=False, warm=False)


def run_mmkp():
    from src.mmkp import NAMES, read_mmkp, read_certificate, to_instance
    from src.agent_pool import AgentPool
    from scripts.run_mmkp_benchmarks import mmkp_fields, K_AGENTS, BUDGET as MB, T_HIGHS
    path = RAW / "highs116_mmkp.csv"
    fin = done(path)
    dpath = RAW / "bench_D_mmkp.csv"
    pool = AgentPool(4)
    cfg = method_configs(init_mode="lp_round", max_net=None, inner_iters=5)[PRIMARY]
    for name in NAMES:
        raw = read_mmkp(name)
        bkv, _ = read_certificate(name, raw)
        inst = to_instance(raw, K_AGENTS)
        if inst.name in fin:
            continue
        t0 = time.perf_counter()
        ref_cost = raw["n"] * inst.mmkp_pmax - bkv
        base = dict(instance_name=inst.name, mmkp=name, n_groups=raw["n"], items=raw["l"], m=raw["m"], K=K_AGENTS)
        d = pd.read_csv(dpath)
        lrows = []
        if not ((d.instance_name == inst.name) & (d.method == PRIMARY)).any():
            for rep in range(REPS):
                cfg.time_budget_s, cfg.budget_clock, cfg.counterfactual = MB, "wall", False
                r = run_engine(inst, cfg, ref_cost, seed=0, rep=rep, pool=pool)
                assert r.feasible
                lrows.append(dict(base, method=PRIMARY, family="LNS", rep=rep, workers_W=4, best_obj=r.best_obj,
                                  wall_budget_s=MB, wall_clock_s=r.wall_clock_s, cpu_time_s=r.cpu_time_s,
                                  epochs_run=r.epochs_run,
                                  conflict_rate_pct=100.0 * r.conflict_epochs / max(1, r.epochs_run),
                                  matcher_ms_mean=r.matcher_ms_mean, matcher_fallbacks=r.matcher_fallbacks,
                                  primal_integral=r.primal_integral, **mmkp_fields(inst, r.best_obj, bkv)))
            append(dpath, lrows)
        d = pd.read_csv(dpath)
        T = float(d[(d.instance_name == inst.name) & (d.method == PRIMARY)].wall_clock_s.mean())
        rows = []
        for lab, TL, th in (("HiGHS (60s)", T_HIGHS, 1), ("HiGHS (1T, wall-matched)", T, 1),
                            ("HiGHS (4T, wall-matched)", T, 4)):
            h = solve_highs(inst, TL, threads=th)
            tr = h["trace"]
            rows.append(dict(base, method=lab, family="HiGHS", rep=0, threads=th, highs_version="1.16.0",
                             best_obj=h["obj"], wall_clock_s=h["highs_actual_time_s"], highs_status=h["status"],
                             highs_time_limit_s=TL, highs_actual_time_s=h["highs_actual_time_s"],
                             primal_integral=primal_integral([0.0] + [t for t, _ in tr], [None] + [o for _, o in tr],
                                                             ref_cost, TL),
                             **mmkp_fields(inst, h["obj"], bkv)))
        append(path, rows)
        print(f"[mmkp] {name} ({time.perf_counter() - t0:.0f}s) " +
              " ".join(f"{r['method']}={r['gap_bks_pct']:.3f}" for r in rows), flush=True)
    pool.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("job", choices=["async", "highs_main", "highs_rich", "highs_sweep", "highs_pair", "mmkp"])
    a = ap.parse_args()
    t0 = time.perf_counter()
    {"async": run_async, "highs_main": run_highs_main, "highs_rich": run_highs_rich,
     "highs_sweep": run_highs_sweep, "highs_pair": run_highs_pair, "mmkp": run_mmkp}[a.job]()
    print(f"WALL {a.job} done in {time.perf_counter() - t0:.0f}s", flush=True)
