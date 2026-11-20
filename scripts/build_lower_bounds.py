"""
Final lower bound LB of every MCA-SC / MCA-SC-Pair test instance, with its source.

    LB = max{ LP bound, every HiGHS dual bound recorded for the instance }
capped by the best HiGHS incumbent (a dual bound may exceed it by at most the relative
MIP gap 1e-4). Every dual bound is a valid bound whatever the machine conditions of its
run, so taking the maximum only tightens LB. Sources:
  - HiGHS 1.16.0, uniform-condition runs (results/rerun_plan.md): the reference runs in
    wall_reference.csv (jobs main, rich, rich_rerun, sweep, pair) and the dual bounds of
    every other HiGHS run in wall_<job>.csv (rows with highs_source == "run");
  - HiGHS 1.8.0 reference runs of the preliminary version (bench_reference.csv).
Reference runs stopped by the watchdog (highs_killed) have no dual bound.
MMKP instances are not included; their gaps use the best known values.
Output: results/raw/lower_bounds.csv with lb_source naming the bound that defines LB and
proven_optimal (some HiGHS run closed the gap to the MIP tolerance 1e-4).
"""

from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "results" / "raw"
JOBS = ("main", "rich", "rich_rerun", "sweep", "pair")
FAMILY = {"A": "main", "B": "rich", "E_sweep": "sweep", "C_sync": "pair",
          "main": "main", "rich": "rich", "rich_rerun": "rich", "sweep": "sweep", "pair": "pair"}


def bounds():
    """One row per (instance, HiGHS run) with a primal value and possibly a dual bound."""
    parts = []
    old = pd.read_csv(RAW / "bench_reference.csv")
    old = old[old.table.isin(["A", "B", "E_sweep", "C_sync"])]
    parts.append(pd.DataFrame(dict(
        instance_name=old.instance_name, family=old.table.map(FAMILY), scale=old.scale, K=old.K, P=old.P,
        eta=old.eta, seed=old.seed, lp_bound=old.lp_bound, obj=old.highs_obj, dual=old.highs_dual,
        status=old.highs_status, label="HiGHS 1.8.0 reference (" + old.highs_time_limit_s.map("{:.0f}".format) + " s)")))
    ref = pd.read_csv(RAW / "wall_reference.csv")
    ref = ref[ref.job.isin(JOBS)]
    parts.append(pd.DataFrame(dict(
        instance_name=ref.instance_name, family=ref.job.map(FAMILY), scale=ref.scale, K=ref.K, P=ref.P,
        eta=ref.eta, seed=ref.seed, lp_bound=ref.lp_bound, obj=ref.highs_obj,
        dual=ref.highs_dual.where(ref.highs_killed != True), status=ref.highs_status,
        label="HiGHS 1.16.0 reference (" + ref.highs_time_limit_s.map("{:.0f}".format) + " s)")))
    for job in JOBS:
        p = RAW / f"wall_{job}.csv"
        if not p.exists():
            continue
        w = pd.read_csv(p, low_memory=False)
        h = w[(w.family == "HiGHS") & (w.highs_source == "run") & ~w.method.str.match(r"HiGHS \(\d+s\)$")]
        parts.append(pd.DataFrame(dict(
            instance_name=h.instance_name, family=FAMILY[job], scale=h.scale, K=h.K, P=h.P, eta=h.eta,
            seed=h.seed, lp_bound=h.lp_bound, obj=h.best_obj, dual=h.highs_dual, status=h.highs_status,
            label="HiGHS 1.16.0 " + h.method)))
    return pd.concat(parts, ignore_index=True)


def main():
    B = bounds()
    rows = []
    for name, g in B.groupby("instance_name"):
        lp = float(g.lp_bound.max())
        cands = [("LP", lp)] + [(r.label, float(r.dual)) for r in g.itertuples() if np.isfinite(r.dual)]
        src, lb = max(cands, key=lambda c: c[1])
        objs = g.obj[np.isfinite(g.obj)]
        best_obj = float(objs.min()) if len(objs) else np.nan
        if np.isfinite(best_obj) and lb > best_obj:
            lb = best_obj
        first = g.iloc[0]
        rows.append(dict(instance_name=name, family=first.family, scale=first.scale, K=first.K, P=first.P,
                         eta=first.eta, seed=first.seed, lp_bound=lp, lower_bound=lb, lb_source=src,
                         best_highs_obj=best_obj, proven_optimal=bool((g.status == "Optimal").any()),
                         lb_over_lp_pct=100.0 * (lb - lp) / lp,
                         highs_gap_pct=100.0 * (best_obj - lb) / best_obj if np.isfinite(best_obj) else np.nan))
    out = pd.DataFrame(rows).sort_values(["family", "P", "eta", "K", "seed"])
    out.to_csv(RAW / "lower_bounds.csv", index=False)
    print(out.groupby(["family", "lb_source"]).size().to_string())
    print("proven optimal:", int(out.proven_optimal.sum()), "of", len(out))


if __name__ == "__main__":
    main()
