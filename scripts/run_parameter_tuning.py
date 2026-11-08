"""
Parameter sensitivity / tuning of PC-MALNS [MC-CRIP] on the VALIDATION seeds 1..10
(disjoint from the test seeds 101..110). Medium instances (K = 8, N = 320), P = 6,
eta = 1.25, LP-Round start, no prices, static quota.

One factor at a time around the default (M = 5, destroy fraction U(0.16, 0.30),
Regret-2 noise sigma = 2.0, borrower penalty rho_0 = 0.35):
    M               {1, 2, 5, 10}
    destroy range   {(0.08, 0.16), (0.16, 0.30), (0.30, 0.45)}
    noise sigma     {0.0, 1.0, 2.0, 4.0}
    rho_0           {0.0, 0.15, 0.35, 0.70}
3 runs (rep 0..2) per instance and setting, serial, equal CPU budget of 2.0 s
(start time included). LB = max(LP bound, dual bound of a 30 s HiGHS run).

Selection rule (fixed before the runs): a non-default value replaces the default only
if its mean gap is lower and the exact Wilcoxon test on the 30 paired runs, Holm-adjusted
within the factor, gives p < 0.05; otherwise the default is kept.
Output: results/raw/parameter_sensitivity.csv (one row per run) and
results/raw/parameter_sensitivity_summary.csv.
"""

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import src.operators as ops
import src.worker as wrk
from src.instance_generator import generate_instance
from src.engine import run_engine, method_configs
from src.stats import paired_wilcoxon, holm, mean_ci
from scripts.run_benchmark import reference

RAW = REPO_ROOT / "results" / "raw"
SEEDS = list(range(1, 11))
REPS = 3
BUDGET = 2.0
DEFAULT = dict(M=5, destroy=(0.16, 0.30), noise=2.0, rho0=0.35)
GRID = {"M": [1, 2, 5, 10], "destroy": [(0.08, 0.16), (0.16, 0.30), (0.30, 0.45)],
        "noise": [0.0, 1.0, 2.0, 4.0], "rho0": [0.0, 0.15, 0.35, 0.70]}


def set_params(destroy, noise):
    for mod in (ops, wrk):
        mod.DESTROY_MIN_RATIO, mod.DESTROY_MAX_RATIO = destroy
        mod.REPAIR_NOISE = noise
    ops.REPAIR_NOISE_ALT = 1.35 * noise


def settings():
    out = [("default", dict(DEFAULT))]
    for f, vals in GRID.items():
        for v in vals:
            if v != DEFAULT[f]:
                s = dict(DEFAULT)
                s[f] = v
                out.append((f, s))
    return out


def main():
    rows = []
    t0 = time.perf_counter()
    for seed in SEEDS:
        inst = generate_instance(8, 40, P=6, tightness=1.25, seed=seed, scale="Medium")
        lp, lb, h = reference(inst, 30.0)
        for factor, s in settings():
            set_params(s["destroy"], s["noise"])
            for rep in range(REPS):
                cfg = method_configs(init_mode="lp_round", max_net=None, inner_iters=s["M"])["MC-CRIP"]
                cfg.name = "PC-MALNS [MC-CRIP]"
                cfg.rho_init = s["rho0"]
                cfg.time_budget_s, cfg.budget_clock = BUDGET, "cpu"
                r = run_engine(inst, cfg, lb, seed=seed, rep=rep)
                assert r.feasible
                value = "default" if factor == "default" else str(s[factor])
                rows.append(dict(instance_name=inst.name, seed=seed, factor=factor, value=value, M=s["M"],
                                 destroy_min=s["destroy"][0], destroy_max=s["destroy"][1], noise=s["noise"],
                                 rho0=s["rho0"], rep=rep, lower_bound=lb, best_obj=r.best_obj, gap_pct=r.gap_pct,
                                 cpu_time_s=r.cpu_time_s, epochs_run=r.epochs_run,
                                 conflict_rate_pct=100.0 * r.conflict_epochs / max(1, r.epochs_run)))
        set_params(DEFAULT["destroy"], DEFAULT["noise"])
        print(f"[tune] seed {seed} done ({time.perf_counter() - t0:.0f}s)", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(RAW / "parameter_sensitivity.csv", index=False)

    key = ["seed", "rep"]
    base = df[df.factor == "default"].set_index(key)["gap_pct"]
    summ = []
    for f in GRID:
        sub = []
        for v in GRID[f]:
            sel = (df.factor == "default") if v == DEFAULT[f] else ((df.factor == f) & (df.value == str(v)))
            g = df[sel].set_index(key)["gap_pct"].reindex(base.index)
            w = paired_wilcoxon(g.values, base.values)
            ci = mean_ci(g.values, base.values)
            sub.append(dict(factor=f, value=str(v), is_default=v == DEFAULT[f], mean_gap=float(g.mean()),
                            diff_vs_default=ci["mean"], ci_lo=ci["t_lo"], ci_hi=ci["t_hi"], wins=w["wins"],
                            ties=w["ties"], losses=w["losses"], p_value=w["p_value"]))
        nd = [i for i, x in enumerate(sub) if not x["is_default"]]
        adj = holm([sub[i]["p_value"] for i in nd])
        for i, a in zip(nd, adj):
            sub[i]["p_holm"] = a
            sub[i]["adopt"] = bool(a < 0.05 and sub[i]["diff_vs_default"] < 0)
        summ += sub
    s = pd.DataFrame(summ)
    s.to_csv(RAW / "parameter_sensitivity_summary.csv", index=False)
    print(s.to_string(), flush=True)
    print(f"TUNING done in {time.perf_counter() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
