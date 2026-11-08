"""
Mechanism diagnostic for the barrier rules (Table C instances: Medium + Large, test
seeds 101..110, eta = 1.25, P = 6): residual hub slack along the trajectory.

For PC-MALNS [MC-CRIP], PC-MALNS [BCRM-Greedy] and Greedy-Efficiency-Portfolio under the
LP-Round and direct starts, 5 runs per instance on the W = 4 pool with the Step 2
budgets. Logged per run: time-averaged mean normalized slack (mean_r s_r / d_r),
time-averaged bottleneck slack (min_r s_r / d_r), epochs, accepted moves, conflict
epochs and the final gap. The LP-Round runs must reproduce bench_A.csv exactly
(checked), so the logging does not change the search.
Output: results/raw/diag_slack.csv
"""

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.instance_generator import generate_instance
from src.engine import run_engine
from src.agent_pool import AgentPool
from scripts.run_benchmark import configs, ref_table, SCALES, BUDGET, TEST_SEEDS, PRIMARY

RAW = REPO_ROOT / "results" / "raw"
METHODS = [PRIMARY, "PC-MALNS [BCRM-Greedy]", "Greedy-Efficiency-Portfolio"]


def main():
    ref = ref_table()
    A = pd.read_csv(RAW / "bench_A.csv")
    pool = AgentPool(4)
    rows = []
    t0 = time.perf_counter()
    for init in ("lp_round", "direct"):
        for scale in ("Medium", "Large"):
            K, n = SCALES[scale]
            for seed in TEST_SEEDS:
                inst = generate_instance(K, n, P=6, tightness=1.25, seed=seed, scale=scale)
                lb = float(ref.loc[inst.name, "lower_bound"])
                cfgs = configs(init)
                for name in METHODS:
                    for rep in range(5):
                        cfg = cfgs[name]
                        cfg.time_budget_s, cfg.budget_clock, cfg.counterfactual = BUDGET[scale], "wall", False
                        r = run_engine(inst, cfg, lb, seed=seed, rep=rep, pool=pool)
                        assert r.feasible
                        rows.append(dict(init_mode=init, scale=scale, instance_name=inst.name, seed=seed,
                                         method=name, rep=rep, gap_pct=r.gap_pct, epochs_run=r.epochs_run,
                                         conflict_epochs=r.conflict_epochs, accepted_moves=r.accepted_moves,
                                         mean_slack=float(np.mean(r.trace_slack)),
                                         mean_bottleneck_slack=float(np.mean(r.trace_bottleneck)),
                                         final_slack=r.trace_slack[-1],
                                         final_bottleneck_slack=r.trace_bottleneck[-1]))
                print(f"[diag] {init} {inst.name} ({time.perf_counter() - t0:.0f}s)", flush=True)
    pool.close()
    df = pd.DataFrame(rows)
    df.to_csv(RAW / "diag_slack.csv", index=False)
    # same trajectories as table A? (wall-clock budgets make epoch counts vary slightly,
    # so compare the share of runs whose gap equals table A; reported, not asserted)
    a = A[A.method.isin(METHODS)].set_index(["instance_name", "method", "rep"]).gap_pct
    d = df[df.init_mode == "lp_round"].set_index(["instance_name", "method", "rep"]).gap_pct
    j = pd.concat([a, d], axis=1, keys=["A", "diag"]).dropna()
    print(f"runs identical to table A: {np.mean(np.abs(j.A - j.diag) < 1e-9):.2%}; "
          f"mean |diff| {np.mean(np.abs(j.A - j.diag)):.4f} pp")
    print(df.groupby(["init_mode", "method"])[["gap_pct", "mean_slack", "mean_bottleneck_slack", "final_slack",
                                                "epochs_run", "accepted_moves", "conflict_epochs"]].mean().round(4))


if __name__ == "__main__":
    main()
