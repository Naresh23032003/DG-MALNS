"""
Analysis of the Step 2 benchmark CSVs (results/raw/bench_*.csv, parameter_sensitivity*).

Unit of analysis: the instance. Stochastic LNS methods: mean over the 5 runs of the
instance; deterministic methods (LP-Round, HiGHS): their single value. Every
comparison of PC-MALNS [MC-CRIP] (or another reference) against a method uses the
paired per-instance values: mean difference with paired-t and bootstrap 95% CIs
(src/stats.mean_ci), wins / ties / losses and the exact two-sided Wilcoxon signed-rank
p-value (src/stats.paired_wilcoxon), Holm-adjusted within each table family.
Negative differences favour the reference method.

Outputs: results/tables/bench_*.csv, results/tables/report_tables.md,
results/tables/summary.json (read by scripts/generate_paper_macros.py).
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.stats import paired_wilcoxon, holm, mean_ci

RAW = REPO_ROOT / "results" / "raw"
TAB = REPO_ROOT / "results" / "tables"
PRIMARY = "PC-MALNS [MC-CRIP]"
SCALE_ORDER = ["Small", "Medium", "Large", "X-Large", "XXL", "XXXL"]
MD = []
SUMMARY = {}


def load(name):
    p = RAW / f"bench_{name}.csv"
    return pd.read_csv(p) if p.exists() else None


def per_instance(df, value="gap_pct", keys=("instance_name",)):
    return df.groupby(list(keys) + ["method"], as_index=False)[value].mean()


def wide(df, value="gap_pct"):
    return per_instance(df, value).pivot(index="instance_name", columns="method", values=value)


def compare(W, ref, others, family):
    rows = []
    for m in others:
        if m not in W or ref not in W:
            continue
        pair = W[[ref, m]].dropna()
        if len(pair) == 0:
            continue
        w = paired_wilcoxon(pair[ref].values, pair[m].values)
        ci = mean_ci(pair[ref].values, pair[m].values)
        rows.append(dict(family=family, reference=ref, method=m, n=len(pair), ref_mean=pair[ref].mean(),
                         method_mean=pair[m].mean(), diff=ci["mean"], t_lo=ci["t_lo"], t_hi=ci["t_hi"],
                         boot_lo=ci["boot_lo"], boot_hi=ci["boot_hi"], wins=w["wins"], ties=w["ties"],
                         losses=w["losses"], p=w["p_value"]))
    out = pd.DataFrame(rows)
    if len(out):
        out["p_holm"] = holm(out["p"].values)
    return out


def fmt_p(p):
    return "<1e-4" if p < 1e-4 else f"{p:.4f}"


def md_compare(title, C):
    MD.append(f"\n**{title}** (difference = reference − method; negative favours the reference)\n")
    MD.append("| Method | n | Ref mean | Method mean | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |")
    MD.append("|---|---|---|---|---|---|---|---|---|")
    for r in C.itertuples():
        MD.append(f"| {r.method} | {r.n} | {r.ref_mean:.3f} | {r.method_mean:.3f} | {r.diff:+.3f} "
                  f"[{r.t_lo:+.3f}, {r.t_hi:+.3f}] | [{r.boot_lo:+.3f}, {r.boot_hi:+.3f}] | "
                  f"{r.wins}/{r.ties}/{r.losses} | {fmt_p(r.p)} | {fmt_p(r.p_holm)} |")


def md_table(title, df, floatfmt="{:.3f}"):
    MD.append(f"\n**{title}**\n")
    cols = list(df.columns)
    MD.append("| " + " | ".join(str(c) for c in cols) + " |")
    MD.append("|" + "---|" * len(cols))
    for row in df.itertuples(index=False):
        cells = []
        for v in row:
            if isinstance(v, (float, np.floating)):
                cells.append("–" if not np.isfinite(v) else floatfmt.format(v))
            else:
                cells.append(str(v))
        MD.append("| " + " | ".join(cells) + " |")


def by_scale(df, methods, value="gap_pct", scales=None):
    pi = per_instance(df, value, keys=("instance_name", "scale"))
    t = pi.groupby(["scale", "method"])[value].mean().unstack("method")
    scales = scales or [s for s in SCALE_ORDER if s in t.index]
    t = t.reindex(index=scales, columns=[m for m in methods if m in t.columns])
    allm = pi.groupby("method")[value].mean().reindex(t.columns)
    t.loc["All"] = allm
    return t


def counterfactual(df, label):
    """Per-conflict-epoch counterfactual barrier gains of PC-MALNS [MC-CRIP] runs."""
    d = df[(df.method == PRIMARY) & df.cf_sum.notna()]
    tot, wins = {}, {}
    conf = 0
    for cs, cw, ce in zip(d.cf_sum, d.cf_strict_wins, d.conflict_epochs):
        cs, cw = json.loads(cs), json.loads(cw)
        if not cs:
            continue
        conf += int(ce)
        for r, v in cs.items():
            tot[r] = tot.get(r, 0.0) + v
            wins[r] = wins.get(r, 0) + cw.get(r, 0)
    if not tot:
        return None
    ref = tot["MC-CRIP"]
    rows = [dict(regime=label, rule=r, mean_gain_per_conflict_epoch=-tot[r] / max(1, conf),
                 share_of_mccrip_gain_pct=100.0 * tot[r] / ref if ref else np.nan,
                 mccrip_strictly_better_pct=100.0 * wins[r] / max(1, conf), conflict_epochs=conf)
            for r in ["MC-CRIP", "BCRM-Greedy", "Greedy-Efficiency", "Greedy-Gain", "Opt-SeqLock", "Opt-Rollback",
                      "Static-Quota"] if r in tot]
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
def table_a():
    A = load("A")
    if A is None:
        return
    MD.append("\n## Table A — main benchmark (P = 6, η = 1.25, LP-Round start, W = 4)\n")
    methods = list(dict.fromkeys(A.method))
    order = ["LP-Round", PRIMARY] + [m for m in methods if m not in ("LP-Round", PRIMARY)]
    g = by_scale(A, order)
    g.reset_index().to_csv(TAB / "bench_A_gap.csv", index=False)
    md_table("Mean gap to LB (%) by scale", g.T.reset_index().rename(columns={"method": "Method"}))
    pi = by_scale(A[A.family != "Deterministic"], order, "primal_integral")
    pi.reset_index().to_csv(TAB / "bench_A_primal_integral.csv", index=False)
    md_table("Mean primal integral (s × gap fraction) by scale", pi.T.reset_index().rename(columns={"method": "Method"}),
             "{:.4f}")
    lns = A[A.family == "LNS"]
    tm = lns.groupby(["scale", "method"])[["wall_clock_s", "cpu_time_s", "conflict_rate_pct"]].mean()
    tm = tm.xs(PRIMARY, level="method").reindex([s for s in SCALE_ORDER if s in set(lns.scale)])
    md_table(f"{PRIMARY}: mean wall clock, CPU time and conflict rate", tm.reset_index())
    W = wide(A)
    C = compare(W, PRIMARY, [m for m in order if m != PRIMARY], "A pooled")
    C.to_csv(TAB / "bench_A_tests.csv", index=False)
    md_compare(f"Table A pooled over {W.shape[0]} instances: {PRIMARY} vs each method", C)
    SUMMARY["A"] = dict(gap=g.to_dict(), tests=C.set_index("method")[["diff", "t_lo", "t_hi", "wins", "ties",
                                                                         "losses", "p", "p_holm"]].to_dict("index"))
    ref = pd.read_csv(RAW / "bench_reference.csv")
    ra = ref[ref.table == "A"]
    st = ra.groupby("scale").agg(n=("instance_name", "size"),
                                 proven_optimal=("highs_status", lambda s: int((s == "Optimal").sum())),
                                 time_limit_s=("highs_time_limit_s", "first"),
                                 mean_time_s=("highs_actual_time_s", "mean"))
    st = st.reindex([s for s in SCALE_ORDER if s in st.index])
    md_table("HiGHS reference runs (1 thread)", st.reset_index())


def table_b():
    B = load("B")
    if B is None:
        return
    MD.append("\n## Table B — rich candidate pools (P = 20, 40), W = 4 wall clock\n")
    SUMMARY["B"] = {}
    for P in sorted(B.P.unique()):
        b = B[B.P == P]
        order = ["LP-Round", PRIMARY] + [m for m in dict.fromkeys(b.method) if m not in ("LP-Round", PRIMARY)]
        g = by_scale(b, order)
        md_table(f"P = {P}: mean gap to LB (%)", g.T.reset_index().rename(columns={"method": "Method"}))
        pi = by_scale(b[b.family != "Deterministic"], order, "primal_integral")
        md_table(f"P = {P}: mean primal integral", pi.T.reset_index().rename(columns={"method": "Method"}), "{:.4f}")
        C = compare(wide(b), PRIMARY, [m for m in order if m != PRIMARY], f"B P={P}")
        md_compare(f"P = {P} pooled: {PRIMARY} vs each method", C)
        Cpi = compare(wide(b[b.family != "Deterministic"], "primal_integral"), PRIMARY,
                      [m for m in order if m not in (PRIMARY, "LP-Round")], f"B P={P} PI")
        md_compare(f"P = {P} pooled, primal integral: {PRIMARY} vs each method", Cpi)
        pd.concat([C, Cpi]).to_csv(TAB / f"bench_B_P{P}_tests.csv", index=False)
        g.reset_index().to_csv(TAB / f"bench_B_P{P}_gap.csv", index=False)
        nosol = b[(b.family == "HiGHS") & ~b.feasible.astype(bool)].groupby("method").size()
        if len(nosol):
            MD.append(f"\nHiGHS runs without an incumbent (P = {P}): " +
                      ", ".join(f"{m}: {v}" for m, v in nosol.items()) + "\n")
        SUMMARY["B"][int(P)] = dict(gap=g.to_dict(), tests=C.set_index("method")[["diff", "wins", "losses", "p",
                                                                                   "p_holm"]].to_dict("index"))


def table_c():
    A = load("A")
    parts = []
    if A is not None:
        parts.append(("LP-Round start", A[A.scale.isin(["Medium", "Large"]) & (A.family == "LNS")]))
    for name, label in (("C_direct", "Direct start"), ("C_sync", "RPA-SH-Sync"), ("sync_check", "RPA-SH-Sync (validation seeds)")):
        d = load(name)
        if d is not None:
            parts.append((label, d[d.family == "LNS"] if "family" in d else d))
    if not parts:
        return
    MD.append("\n## Table C — commit-rule isolation (Medium + Large)\n")
    rules = [PRIMARY, "PC-MALNS [BCRM-Greedy]", "Greedy-Efficiency-Portfolio", "Greedy-Gain-Portfolio",
             "Opt-Rollback-Portfolio", "Opt-SeqLock-Portfolio", "Opt-Rollback", "Opt-SeqLock"]
    cfs = []
    SUMMARY["C"] = {}
    for label, d in parts:
        d = d[d.method.isin(rules)]
        g = by_scale(d, rules, scales=["Medium", "Large"])
        cr = by_scale(d, rules, "conflict_rate_pct", scales=["Medium", "Large"])
        md_table(f"{label}: mean gap (%)", g.T.reset_index().rename(columns={"method": "Method"}))
        md_table(f"{label}: mean conflict rate (% of epochs)", cr.T.reset_index().rename(columns={"method": "Method"}),
                 "{:.1f}")
        C = compare(wide(d), PRIMARY, [m for m in rules if m != PRIMARY], label)
        md_compare(f"{label}: {PRIMARY} vs each commit rule", C)
        C.to_csv(TAB / f"bench_C_{label.split()[0].lower().replace('-', '_')}_tests.csv", index=False)
        cf = counterfactual(d, label)
        if cf is not None:
            cfs.append(cf)
        SUMMARY["C"][label] = dict(gap=g.to_dict(), conflict=cr.to_dict(),
                                   tests=C.set_index("method")[["diff", "t_lo", "t_hi", "wins", "ties", "losses", "p",
                                                                "p_holm"]].to_dict("index"))
    if cfs:
        cf = pd.concat(cfs)
        cf.to_csv(TAB / "bench_C_counterfactual.csv", index=False)
        md_table("Counterfactual barrier analysis (all conflict epochs of the PC-MALNS [MC-CRIP] runs; every rule "
                 "applied to the same portfolios)", cf, "{:.2f}")
        SUMMARY["C"]["counterfactual"] = cf.to_dict("records")


def table_d():
    D = load("D_mmkp")
    if D is None:
        return
    MD.append("\n## Table D — public MMKP benchmarks (27 instances, K = 8 agents)\n")
    D = D.copy()
    D["set"] = np.where(D.mmkp.str.startswith("INST"), "INST01-20", "I07-I13")
    order = ["LP-Round", PRIMARY, "PC-MALNS [BCRM-Greedy]", "Opt-Rollback", "Opt-SeqLock", "Static-Quota",
             "HiGHS (1T, wall-matched)", "HiGHS (4T, wall-matched)", "HiGHS (60s)"]
    feas = D.groupby(["method"]).mmkp_feasible.mean().reindex(order) * 100
    gi = D.groupby(["instance_name", "set", "method"], as_index=False).gap_bks_pct.mean()
    t = gi.groupby(["set", "method"]).gap_bks_pct.mean().unstack("method").reindex(columns=order)
    t.loc["All"] = gi.groupby("method").gap_bks_pct.mean().reindex(order)
    md_table("Mean gap to the best known solution (%; MMKP-feasible runs)", t.T.reset_index())
    md_table("MMKP-feasible runs (%)", feas.reset_index().rename(columns={"mmkp_feasible": "feasible_pct"}), "{:.1f}")
    W = gi.pivot(index="instance_name", columns="method", values="gap_bks_pct")
    C = compare(W, PRIMARY, [m for m in order if m != PRIMARY], "D MMKP")
    md_compare(f"MMKP: {PRIMARY} vs each method (gap to BKS)", C)
    C.to_csv(TAB / "bench_D_tests.csv", index=False)
    t.reset_index().to_csv(TAB / "bench_D_gap.csv", index=False)
    SUMMARY["D"] = dict(gap=t.to_dict(), feasible_pct=feas.to_dict(),
                        tests=C.set_index("method")[["diff", "wins", "losses", "p", "p_holm"]].to_dict("index"))


def table_e():
    E = load("E_sweep")
    A = load("A")
    if E is not None:
        MD.append("\n## Table E1 — coupling tightness sweep (Large)\n")
        parts = [E]
        if A is not None:
            parts.append(A[(A.scale == "Large") & A.method.isin(set(E.method))])
        d = pd.concat(parts)
        pi = d.groupby(["instance_name", "eta", "method"], as_index=False).gap_pct.mean()
        order = ["LP-Round", PRIMARY] + [m for m in dict.fromkeys(E.method) if m not in ("LP-Round", PRIMARY)]
        t = pi.groupby(["eta", "method"]).gap_pct.mean().unstack("method").reindex(columns=order)
        md_table("Mean gap (%) by tightness η", t.T.reset_index())
        t.reset_index().to_csv(TAB / "bench_E_sweep.csv", index=False)
        rows = []
        for eta, g in pi.groupby("eta"):
            C = compare(g.pivot(index="instance_name", columns="method", values="gap_pct"), PRIMARY,
                        [m for m in order if m != PRIMARY], f"eta={eta}")
            rows.append(C)
        C = pd.concat(rows)
        C["p_holm"] = holm(C["p"].values)
        C.to_csv(TAB / "bench_E_sweep_tests.csv", index=False)
        md_compare("Tightness sweep: per η, Holm over the whole sweep", C.assign(method=C.family + ": " + C.method))
        SUMMARY["E_sweep"] = t.to_dict()
    Ab = load("E_ablation")
    if Ab is not None and A is not None:
        MD.append("\n## Table E2 — price / quota ablation (Large, η = 1.25)\n")
        base = A[(A.scale == "Large") & (A.method == PRIMARY)]
        d = pd.concat([base, Ab])
        W = wide(d)
        C = compare(W, PRIMARY, [m for m in W.columns if m != PRIMARY], "ablation")
        md_compare(f"{PRIMARY} (no prices, static quota) vs each price / quota variant", C)
        C.to_csv(TAB / "bench_E_ablation_tests.csv", index=False)
        SUMMARY["E_ablation"] = C.set_index("method")[["method_mean", "diff", "p", "p_holm"]].to_dict("index")
    S = load("E_scaling")
    if S is not None:
        MD.append("\n## Table E3 — multi-process wall-clock scaling (fixed epochs, one job at a time)\n")
        t = S.groupby(["scale", "mode", "workers_W"], as_index=False).agg(
            wall_clock_s=("wall_clock_s", "mean"), speedup=("speedup_vs_serial", "mean"),
            identical=("same_obj_as_serial", "all"))
        md_table("Wall clock and speedup vs the serial in-process run", t)
        t.to_csv(TAB / "bench_E_scaling.csv", index=False)
        SUMMARY["E_scaling"] = t.to_dict("records")
    T = RAW / "parameter_sensitivity_summary.csv"
    if T.exists():
        MD.append("\n## Table E4 — parameter tuning (validation seeds 1..10, Medium)\n")
        s = pd.read_csv(T)
        md_table("One-factor-at-a-time sensitivity (difference vs default; 30 paired runs)",
                 s[["factor", "value", "is_default", "mean_gap", "diff_vs_default", "ci_lo", "ci_hi", "wins",
                    "losses", "p_value", "p_holm", "adopt"]])
        SUMMARY["tuning"] = s.to_dict("records")


def main():
    TAB.mkdir(parents=True, exist_ok=True)
    for f in (table_a, table_b, table_c, table_d, table_e):
        f()
    (TAB / "report_tables.md").write_text("\n".join(MD) + "\n")
    (TAB / "summary.json").write_text(json.dumps(SUMMARY, indent=1, default=float))
    print("\n".join(MD))


if __name__ == "__main__":
    main()
