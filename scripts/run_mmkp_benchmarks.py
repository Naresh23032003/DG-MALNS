"""
Table D: public MMKP benchmarks (27 classical instances I07-I13 and INST01-INST20) as
RPA-SH instances (src/mmkp.py), with the n groups split over K = 8 agents.

Methods: PC-MALNS [MC-CRIP], PC-MALNS [BCRM-Greedy], Opt-Rollback, Opt-SeqLock,
Static-Quota; LP-Round start, M = 5, 5 runs per instance on the W = 4 agent pool with a
2.0 s wall-clock budget. HiGHS (1 thread, 60 s) and HiGHS wall-matched (1 and 4
threads), once per instance (deterministic).

Gap to the published best known solution (verified certificate, src/mmkp.py):
    gap_bks_pct = 100 (BKV - profit) / BKV,   profit = n p_max - cost.
A solution with some group still on p = 0 (no item) costs more than PEN >
n (p_max - p_min) and is reported as MMKP-infeasible (profit NaN).
The primal integral uses the BKS cost n p_max - BKV as reference.
Output: results/raw/bench_D_mmkp.csv (resumable per instance).
"""

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.mmkp import NAMES, read_mmkp, read_certificate, to_instance
from src.engine import run_engine, primal_integral
from src.highs_runner import solve_highs
from src.agent_pool import AgentPool
from src.baselines import lp_round_start
from src.feasibility import evaluate_global_cost
from scripts.run_benchmark import configs, PRIMARY

RAW = REPO_ROOT / "results" / "raw"
K_AGENTS = 8
REPS = 5
BUDGET = 2.0
T_HIGHS = 60.0
METHODS = [PRIMARY, "PC-MALNS [BCRM-Greedy]", "Opt-Rollback", "Opt-SeqLock", "Static-Quota"]


def mmkp_fields(inst, cost, bkv):
    n, pmax = inst.mmkp_n, inst.mmkp_pmax
    ok = cost is not None and np.isfinite(cost) and cost < inst.mmkp_pen - 1e-6
    profit = n * pmax - cost if ok else np.nan
    return dict(mmkp_feasible=bool(ok), profit=profit, bkv=bkv,
                gap_bks_pct=100.0 * (bkv - profit) / bkv if ok else np.nan)


def main():
    path = RAW / "bench_D_mmkp.csv"
    done = set(pd.read_csv(path)["instance_name"]) if path.exists() else set()
    pool = AgentPool(4)
    t00 = time.perf_counter()
    for name in NAMES:
        raw = read_mmkp(name)
        bkv, _ = read_certificate(name, raw)
        inst = to_instance(raw, K_AGENTS)
        if inst.name in done:
            continue
        t0 = time.perf_counter()
        ref_cost = raw["n"] * inst.mmkp_pmax - bkv
        base = dict(instance_name=inst.name, mmkp=name, n_groups=raw["n"], items=raw["l"], m=raw["m"],
                    K=K_AGENTS)
        rows = []
        pats, lt, rt = lp_round_start(inst)
        c0 = evaluate_global_cost(inst, pats)
        rows.append(dict(base, method="LP-Round", family="Deterministic", rep=0, best_obj=c0,
                         wall_clock_s=lt + rt, **mmkp_fields(inst, c0, bkv)))
        h = solve_highs(inst, T_HIGHS, threads=1)
        tr = h["trace"]
        rows.append(dict(base, method="HiGHS (60s)", family="HiGHS", rep=0, threads=1, best_obj=h["obj"],
                         wall_clock_s=h["highs_actual_time_s"], highs_status=h["status"],
                         highs_time_limit_s=T_HIGHS, highs_actual_time_s=h["highs_actual_time_s"],
                         primal_integral=primal_integral([0.0] + [t for t, _ in tr], [None] + [o for _, o in tr],
                                                         ref_cost, T_HIGHS),
                         **mmkp_fields(inst, h["obj"], bkv)))
        cfgs = configs()
        walls = []
        for mname in METHODS:
            for rep in range(REPS):
                cfg = cfgs[mname]
                cfg.time_budget_s, cfg.budget_clock, cfg.counterfactual = BUDGET, "wall", False
                r = run_engine(inst, cfg, ref_cost, seed=0, rep=rep, pool=pool)
                assert r.feasible
                if mname == PRIMARY:
                    walls.append(r.wall_clock_s)
                rows.append(dict(base, method=mname, family="LNS", rep=rep, workers_W=4, best_obj=r.best_obj,
                                 wall_budget_s=BUDGET, wall_clock_s=r.wall_clock_s, cpu_time_s=r.cpu_time_s,
                                 epochs_run=r.epochs_run,
                                 conflict_rate_pct=100.0 * r.conflict_epochs / max(1, r.epochs_run),
                                 matcher_ms_mean=r.matcher_ms_mean, matcher_fallbacks=r.matcher_fallbacks,
                                 primal_integral=r.primal_integral, **mmkp_fields(inst, r.best_obj, bkv)))
        T = float(np.mean(walls))
        for th in (1, 4):
            hm = solve_highs(inst, T, threads=th)
            tr = hm["trace"]
            rows.append(dict(base, method=f"HiGHS ({th}T, wall-matched)", family="HiGHS", rep=0, threads=th,
                             best_obj=hm["obj"], wall_clock_s=hm["highs_actual_time_s"], highs_status=hm["status"],
                             highs_time_limit_s=T, highs_actual_time_s=hm["highs_actual_time_s"],
                             primal_integral=primal_integral([0.0] + [t for t, _ in tr], [None] + [o for _, o in tr],
                                                             ref_cost, T),
                             **mmkp_fields(inst, hm["obj"], bkv)))
        df = pd.DataFrame(rows)
        if path.exists():
            df = df.reindex(columns=pd.read_csv(path, nrows=0).columns)
        df.to_csv(path, mode="a", header=not path.exists(), index=False)
        g = df.groupby("method", sort=False)["gap_bks_pct"].mean()
        print(f"[D] {name} ({time.perf_counter() - t0:.0f}s) " + " ".join(f"{m}={v:.3f}" for m, v in g.items()),
              flush=True)
    pool.close()
    print(f"MMKP done in {time.perf_counter() - t00:.0f}s", flush=True)


if __name__ == "__main__":
    main()
