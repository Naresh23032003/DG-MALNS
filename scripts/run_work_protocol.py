"""
Main protocol (revision 3): deterministic work budget for every comparison among LNS
methods. Every job runs strictly one at a time.

Work unit: one Regret-2 repair pass of one worker (src/worker.repair_passes_per_epoch).
A four-level portfolio epoch costs 5M = 25 passes per worker (levels 1 and 3 run a
best-of-two repair, level 2 one repair, M = 5 chained steps); a single-proposal epoch
costs 2M = 10 passes, so single-proposal methods run 2.5 times as many epochs. The
budget per worker is 25 * E_scale passes, where E_scale is the median number of epochs
that the four-level portfolio methods reached under the wall-clock protocol of
results/raw/bench_A.csv, rounded to a multiple of 5 (fixed before any run of this
script). Wall-clock time, CPU time and barrier time are recorded but do not stop a run,
so every run is repeatable bit for bit (serial and W = 4 pool runs coincide). MC-CRIP
gets a 60 s HiGHS limit per solve under this protocol (its barrier time is not charged).

Tables (results/raw/work_<table>.csv, resumable per instance):
  main          all LNS methods, P = 6, eta = 1.25, Small..XXXL, test seeds 101..110
  validation    fresh seeds 201..210 (never used before), Small..XXXL: the three
                PC-MALNS barriers; plan declared in results/validation_plan.md
  commit_direct commit-rule isolation, direct start (all requests on p = 0), Medium/Large
  commit_pair   commit-rule isolation on MCA-SC-Pair, Medium/Large
  levels        portfolio-level ablation of PC-MALNS [Greedy-Efficiency], all 60 instances
  prices        price and quota variants of PC-MALNS [Greedy-Efficiency], all 60 instances
  restart       PC-MALNS [Greedy-Efficiency] with restarts (kick after 5 epochs without
                a new best), all 60 instances
  prices_fresh  fresh seeds 301..310 (never used before), Small..XXXL: PC-MALNS
                [Greedy-Efficiency] without prices (static quota) and with MC-CRIP LP prices
                (static quota); plan declared in results/price_plan.md
  rho0          PC-MALNS [Greedy-Efficiency] with rho_0 = 0 (no quota-excess penalty in
                the level-2 repair), all 60 instances
  cf_all        diagnostic: PC-MALNS [Greedy-Efficiency] and [MC-CRIP] on the 60 test instances with
                every barrier rule logged on the same portfolio in every epoch (conflict epochs:
                all rules; non-conflict epochs: the deterministic rules), search unchanged
Every row records the level-0 donor diagnostics l0_tries, l0_dominated, l0_committed
(added in revision 3 after the tables main..restart had been run; empty there).
Gaps are recomputed in the analysis from best_obj and the final lower bounds.
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
from src.baselines import solve_lp_relaxation
from src.engine import run_engine, method_configs, EngineConfig
from src.agent_pool import AgentPool

RAW = REPO_ROOT / "results" / "raw"
TEST_SEEDS = list(range(101, 111))
FRESH_SEEDS = list(range(201, 211))
PRICE_SEEDS = list(range(301, 311))
REPS = 5
M_INNER = 5
SCALES = {"Small": (4, 30), "Medium": (8, 40), "Large": (12, 50), "X-Large": (16, 60),
          "XXL": (24, 100), "XXXL": (32, 125)}
EPOCHS = {"Small": 70, "Medium": 70, "Large": 45, "X-Large": 35, "XXL": 30, "XXXL": 25}
WORK = {s: 5 * M_INNER * e for s, e in EPOCHS.items()}
MCCRIP_LIMIT = 60.0
PRIMARY = "PC-MALNS [Greedy-Efficiency]"
ORACLE = "PC-MALNS [MC-CRIP]"
BARRIERS = [PRIMARY, ORACLE, "PC-MALNS [Quota-Surplus]", "PC-MALNS [Greedy-Gain]"]
ALL_LNS = BARRIERS + ["Opt-Rollback-Portfolio", "Opt-SeqLock-Portfolio", "Opt-Rollback", "Opt-SeqLock",
                      "Static-Quota", "Demand-Quota"]
COMMIT_LNS = BARRIERS + ["Opt-Rollback-Portfolio", "Opt-SeqLock-Portfolio", "Opt-Rollback", "Opt-SeqLock"]
LEVEL_SETS = {"{1,3}": (1, 3), "{0,1,3}": (0, 1, 3), "{1,2,3}": (1, 2, 3)}


def configs(init="lp_round"):
    return method_configs(init_mode=init, max_net=None, inner_iters=M_INNER)


def level_configs():
    C = {}
    for tag, lv in LEVEL_SETS.items():
        nm = f"{PRIMARY} levels {tag}"
        C[nm] = EngineConfig(nm, L=3, commit="Greedy-Efficiency", init_mode="lp_round", inner_iters=M_INNER,
                             levels=lv)
    return C


def price_configs():
    C = {}
    for duals, quota in (("heuristic", "static"), ("heuristic", "dynamic"), ("mccrip_lp", "static"),
                         ("mccrip_lp", "dynamic"), ("none", "dynamic"), ("none", "demand")):
        nm = f"{PRIMARY} prices={duals}, quota={quota}"
        C[nm] = EngineConfig(nm, L=3, commit="Greedy-Efficiency", init_mode="lp_round", inner_iters=M_INNER,
                             duals=duals, quota=quota)
    return C


def restart_configs():
    nm = f"{PRIMARY} + restarts"
    return {nm: EngineConfig(nm, L=3, commit="Greedy-Efficiency", init_mode="lp_round", inner_iters=M_INNER,
                             restart_stall=5)}


def prices_fresh_configs():
    C = {PRIMARY: configs()[PRIMARY]}
    nm = f"{PRIMARY} prices=mccrip_lp, quota=static"
    C[nm] = price_configs()[nm]
    return C


def cf_all_configs():
    """Diagnostic (revision 3, after the review of 2026-11-20): the barriers that do not first try the
    cheapest levels (Greedy-Efficiency) and the exact barrier, with the rules logged in every epoch.
    The logging uses its own generators, so every run must reproduce its work_main.csv row bit for bit."""
    C = {}
    for nm in (PRIMARY, ORACLE):
        cfg = configs()[nm]
        cfg.cf_all = True
        C[nm] = cfg
    return C


def rho0_configs():
    nm = f"{PRIMARY} rho0=0"
    return {nm: EngineConfig(nm, L=3, commit="Greedy-Efficiency", init_mode="lp_round", inner_iters=M_INNER,
                             rho_init=0.0)}


def reference_lb():
    ref = pd.read_csv(RAW / "bench_reference.csv").drop_duplicates("instance_name", keep="last")
    return ref.set_index("instance_name")["lower_bound"]


def run_rows(table, inst, scale, lb, cfg_map, names, pool, counterfactual=True):
    rows = []
    for name in names:
        for rep in range(REPS):
            cfg = cfg_map[name]
            cfg.work_budget, cfg.time_budget_s = WORK[scale], None
            cfg.mccrip_time_limit = MCCRIP_LIMIT
            cfg.counterfactual = counterfactual and cfg.commit == "MC-CRIP" and cfg.L >= 2
            r = run_engine(inst, cfg, lb, seed=inst.seed, rep=rep, pool=pool)
            if not r.feasible:
                raise RuntimeError(f"infeasible: {name} {inst.name} rep {rep}")
            d = dict(table=table, instance_name=inst.name, scale=scale, K=inst.K, N_total=inst.N_total, P=inst.P,
                     m_global=inst.m_global, eta=inst.tightness, seed=inst.seed, method=name, rep=rep,
                     init_mode=cfg.init_mode, commit=cfg.commit, L=cfg.L,
                     levels="" if cfg.levels is None else json.dumps(list(cfg.levels)),
                     duals=cfg.duals, quota=cfg.quota, restart_stall=cfg.restart_stall,
                     workers_W=r.workers_W, work_budget=cfg.work_budget, repair_passes=r.repair_passes,
                     epochs_run=r.epochs_run, best_obj=r.best_obj, initial_obj=r.initial_obj,
                     lower_bound_at_run=lb, feasible=r.feasible, wall_clock_s=r.wall_clock_s,
                     cpu_time_s=r.cpu_time_s, init_time_s=r.init_time_s, barrier_s_total=r.barrier_s_total,
                     conflict_epochs=r.conflict_epochs, accepted_moves=r.accepted_moves, proposals=r.proposals,
                     matcher_ms_mean=r.matcher_ms_mean, matcher_fallbacks=r.matcher_fallbacks,
                     restarts=r.restarts, last_improve_epoch=r.last_improve_epoch,
                     l0_tries=r.l0_tries, l0_dominated=r.l0_dominated, l0_committed=r.l0_committed,
                     mean_slack=float(np.mean(r.trace_slack)),
                     mean_bottleneck_slack=float(np.mean(r.trace_bottleneck)),
                     final_slack=r.trace_slack[-1], cf_sum=json.dumps(r.cf_sum),
                     cf_strict_wins=json.dumps(r.cf_strict_wins), fast_path_epochs=r.fast_path_epochs,
                     nc_sum=json.dumps(r.nc_sum), nc_deviate=json.dumps(r.nc_deviate))
            if rep == 0:
                d["trace"] = json.dumps([round(o, 4) for o in r.trace_obj])   # objective after each epoch
            rows.append(d)
    return rows


class Sink:
    def __init__(self, table):
        self.path = RAW / f"work_{table}.csv"
        self.done = set()
        if self.path.exists():
            self.done = set(pd.read_csv(self.path, usecols=["instance_name"])["instance_name"])

    def write(self, rows):
        df = pd.DataFrame(rows)
        if self.path.exists():
            df = df.reindex(columns=pd.read_csv(self.path, nrows=0).columns)
        df.to_csv(self.path, mode="a", header=not self.path.exists(), index=False)


def log(table, inst, rows, t0):
    df = pd.DataFrame(rows)
    g = df.groupby("method", sort=False)["best_obj"].mean()
    print(f"[{table}] {inst.name} ({time.perf_counter() - t0:.0f}s) " +
          " ".join(f"{m}={v:.1f}" for m, v in g.items()), flush=True)


def instances(seeds, scales=tuple(SCALES), pair=False):
    for scale in scales:
        K, n = SCALES[scale]
        for seed in seeds:
            gen = generate_sync_instance if pair else generate_instance
            yield scale, gen(K, n, P=6, tightness=1.25, seed=seed, scale=scale)


def run_table(table, pool):
    sink = Sink(table)
    lbs = reference_lb()
    if table == "main":
        it, cfg_map, names, init = instances(TEST_SEEDS), None, ALL_LNS, "lp_round"
    elif table == "validation":
        it, cfg_map, names, init = instances(FRESH_SEEDS), None, BARRIERS[:3], "lp_round"
    elif table == "commit_direct":
        it, cfg_map, names, init = instances(TEST_SEEDS, ("Medium", "Large")), None, COMMIT_LNS, "direct"
    elif table == "commit_pair":
        it, cfg_map, names, init = instances(TEST_SEEDS, ("Medium", "Large"), pair=True), None, COMMIT_LNS, "lp_round"
    elif table == "levels":
        cfg_map = level_configs()
        it, names, init = instances(TEST_SEEDS), list(cfg_map), "lp_round"
    elif table == "prices":
        cfg_map = price_configs()
        it, names, init = instances(TEST_SEEDS), list(cfg_map), "lp_round"
    elif table == "restart":
        cfg_map = restart_configs()
        it, names, init = instances(TEST_SEEDS), list(cfg_map), "lp_round"
    elif table == "prices_fresh":
        cfg_map = prices_fresh_configs()
        it, names, init = instances(PRICE_SEEDS), list(cfg_map), "lp_round"
    elif table == "cf_all":
        cfg_map = cf_all_configs()
        it, names, init = instances(TEST_SEEDS), list(cfg_map), "lp_round"
    elif table == "rho0":
        cfg_map = rho0_configs()
        it, names, init = instances(TEST_SEEDS), list(cfg_map), "lp_round"
    else:
        raise ValueError(table)
    for scale, inst in it:
        if inst.name in sink.done:
            continue
        t0 = time.perf_counter()
        if inst.name in lbs.index:
            lb = float(lbs.loc[inst.name])
        else:   # fresh seeds (validation, prices_fresh): LP bound (the comparison is paired, see the plan)
            lb = float(solve_lp_relaxation(inst)["lp_bound"])
        rows = run_rows(table, inst, scale, lb, cfg_map or configs(init), names, pool)
        sink.write(rows)
        log(table, inst, rows, t0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("table", choices=["main", "validation", "commit_direct", "commit_pair", "levels", "prices",
                                      "restart", "prices_fresh", "rho0", "cf_all"])
    a = ap.parse_args()
    t0 = time.perf_counter()
    pool = AgentPool(4)
    print(f"pool W=4 startup {pool.startup_s:.2f}s", flush=True)
    run_table(a.table, pool)
    pool.close()
    print(f"WORK {a.table} done in {time.perf_counter() - t0:.0f}s", flush=True)
