"""
Analysis of all revision-3 results. Every number of the manuscript comes from here
(through results/tables/summary.json, read by generate_paper_tables.py,
generate_paper_macros.py and make_figures.py).

Unit of analysis: the instance (mean over the 5 runs of an LNS method; the single value
of a deterministic method). Gaps are recomputed from best_obj and the final lower bounds
of results/raw/lower_bounds.csv (scripts/build_lower_bounds.py); the fresh validation
seeds use the LP bound. Every comparison: paired mean difference (reference - method,
negative favours the reference) with paired-t and bootstrap 95% CIs, wins / ties /
losses, exact two-sided Wilcoxon signed-rank p-value, Holm-adjusted within each family.

Protocols:
  work  (main protocol)  results/raw/work_*.csv: deterministic work budget
  wall  (secondary)      results/raw/wall_<job>.csv, wall_reference.csv and
                         wall_calibration.csv: all wall-clock and HiGHS 1.16.0 runs under
                         uniform machine conditions (results/rerun_plan.md), including the
                         sensitivity rerun wall_rich_rerun.csv
The bench_*.csv files of revision 2 are superseded; their HiGHS 1.8.0 dual bounds still
enter LB.
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
SC = ["Small", "Medium", "Large", "X-Large", "XXL", "XXXL"]
PRIMARY = "PC-MALNS [Greedy-Efficiency]"
ORACLE = "PC-MALNS [MC-CRIP]"
QS = "PC-MALNS [Quota-Surplus]"
GG = "PC-MALNS [Greedy-Gain]"
BARRIERS = [PRIMARY, ORACLE, QS, GG]
OPT = ["Opt-Rollback-Portfolio", "Opt-SeqLock-Portfolio", "Opt-Rollback", "Opt-SeqLock"]
QUOTA = ["Static-Quota", "Demand-Quota"]
ALL_LNS = BARRIERS + OPT + QUOTA
S = {}
MD = []


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------
def _lb():
    return pd.read_csv(RAW / "lower_bounds.csv").set_index("instance_name")["lower_bound"]


LB = None


def gapify(df, lb_col=None):
    df = df.copy()
    lb = df[lb_col] if lb_col else df.instance_name.map(LB)
    if lb.isna().any():
        raise ValueError(f"missing LB for {df.instance_name[lb.isna()].unique()[:3]}")
    df["LB"] = lb.values
    df["gap_pct"] = np.maximum(0.0, 100.0 * (df.best_obj - df.LB) / df.LB)
    return df


def read(name):
    p = RAW / name
    return pd.read_csv(p) if p.exists() else None


def lp_round_rows(table_csv):
    d = read(table_csv)
    d = d[d.method.notna()]
    return d[d.method == "LP-Round"][["instance_name", "scale", "P", "eta", "seed", "method", "best_obj"]]


def per_instance(df, value="gap_pct", keys=("instance_name",)):
    return df.groupby(list(keys) + ["method"], as_index=False)[value].mean()


def wide(df, value="gap_pct"):
    return per_instance(df, value).pivot(index="instance_name", columns="method", values=value)


def scale_means(df, value="gap_pct", scales=SC, key="scale"):
    pi = per_instance(df, value, keys=("instance_name", key))
    t = pi.groupby([key, "method"])[value].mean().unstack("method")
    t = t.reindex([s for s in scales if s in t.index])
    t.loc["All"] = pi.groupby("method")[value].mean()
    return t


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


def tests_dict(C):
    return C.set_index("method")[["n", "ref_mean", "method_mean", "diff", "t_lo", "t_hi", "boot_lo", "boot_hi",
                                  "wins", "ties", "losses", "p", "p_holm"]].to_dict("index")


def fmt_p(p):
    return "<1e-4" if p < 1e-4 else f"{p:.4f}"


def md_compare(title, C):
    MD.append(f"\n**{title}** (difference = reference − method; negative favours the reference)\n")
    MD.append("| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |")
    MD.append("|---|---|---|---|---|---|---|---|---|")
    for r in C.itertuples():
        MD.append(f"| {r.method} | {r.n} | {r.ref_mean:.3f} | {r.method_mean:.3f} | {r.diff:+.3f} "
                  f"[{r.t_lo:+.3f}, {r.t_hi:+.3f}] | [{r.boot_lo:+.3f}, {r.boot_hi:+.3f}] | "
                  f"{r.wins}/{r.ties}/{r.losses} | {fmt_p(r.p)} | {fmt_p(r.p_holm)} |")


def md_table(title, df, floatfmt="{:.3f}"):
    MD.append(f"\n**{title}**\n")
    df = df.reset_index() if df.index.name or not isinstance(df.index, pd.RangeIndex) else df
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


def tdict(t):
    return {str(c): {str(i): (None if not np.isfinite(v) else float(v)) for i, v in t[c].items()} for c in t.columns}


# ---------------------------------------------------------------------------
# main benchmark, work protocol
# ---------------------------------------------------------------------------
def main_work():
    W = read("work_main.csv")
    if W is None:
        return None
    W = gapify(W)
    lpr = gapify(lp_round_rows("wall_main.csv"))
    d = pd.concat([W, lpr], ignore_index=True)
    MD.append("\n## Main benchmark: work protocol (P = 6, η = 1.25, seeds 101–110)\n")
    order = ["LP-Round"] + ALL_LNS
    g = scale_means(d)[[m for m in order if m in set(d.method)]]
    md_table("Mean gap (%) by scale", g.T)
    C = compare(wide(d), PRIMARY, [m for m in order if m != PRIMARY], "main-work")
    md_compare(f"Main (work protocol): {PRIMARY} vs each method", C)
    C.to_csv(TAB / "work_main_tests.csv", index=False)
    g.to_csv(TAB / "work_main_gap.csv")
    # oracle vs others (secondary family)
    C2 = compare(wide(d), ORACLE, [m for m in ALL_LNS if m != ORACLE], "main-work-oracle")
    md_compare(f"Main (work protocol): {ORACLE} vs each LNS method", C2)
    ep = scale_means(W, "epochs_run")
    bt = scale_means(W[W.conflict_epochs > 0], "matcher_ms_mean")
    btot = scale_means(W, "barrier_s_total")
    wall = scale_means(W, "wall_clock_s")
    cr = scale_means(W.assign(cr=100.0 * W.conflict_epochs / W.epochs_run), "cr")
    acc = scale_means(W.assign(a=W.accepted_moves / W.epochs_run), "a")
    fb = W[W.method == ORACLE].matcher_fallbacks.sum()
    md_table("Epochs per run", ep.T, "{:.1f}")
    md_table("Barrier time per conflict epoch (ms)", bt.T, "{:.2f}")
    md_table("Conflict epochs (% of epochs)", cr.T, "{:.1f}")
    # per-scale tests of the barrier rules (fixed epochs: same work, same epochs)
    per_scale = []
    for s in SC:
        Cs = compare(wide(d[d.scale == s]), PRIMARY, [ORACLE, QS, GG], f"scale {s}")
        per_scale.append(Cs.assign(scale=s))
    PS = pd.concat(per_scale)
    PS["p_holm"] = holm(PS["p"].values)
    md_compare("Per scale (Holm over the 18 tests): Greedy-Efficiency vs the other barriers",
               PS.assign(method=PS.scale + ": " + PS.method))
    # counterfactual over all conflict epochs of the MC-CRIP runs
    cf = counterfactual(W, "LP-Round start, all scales")
    sd = W.groupby(["instance_name", "method"]).gap_pct.std(ddof=1).groupby("method").mean()
    S["run_sd"] = {m: float(v) for m, v in sd.items()}
    MD.append("\n- Mean standard deviation of the gap over the 5 runs of an instance (pp): "
              + ", ".join(f"{m} {v:.3f}" for m, v in sd.items()))
    S["main_work"] = dict(gap=tdict(g), tests=tests_dict(C), tests_oracle=tests_dict(C2), epochs=tdict(ep),
                          barrier_ms=tdict(bt), barrier_s_total=tdict(btot), wall_s=tdict(wall),
                          conflict_pct=tdict(cr), accepted_per_epoch=tdict(acc), mccrip_fallbacks=int(fb),
                          per_scale_barrier_tests=PS.to_dict("records"),
                          counterfactual_all=None if cf is None else cf.to_dict("records"),
                          n_runs=int(len(W)), n_instances=int(W.instance_name.nunique()))
    return d


def counterfactual(df, label):
    d = df[(df.method == ORACLE) & df.cf_sum.notna()]
    tot, wins, conf = {}, {}, 0
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
            for r in ["MC-CRIP", "Greedy-Efficiency", "Quota-Surplus", "Greedy-Gain", "Opt-SeqLock", "Opt-Rollback",
                      "Static-Quota"] if r in tot]
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# commit-rule isolation (work protocol): LP-Round (subset of main), direct, Pair
# ---------------------------------------------------------------------------
def commit_work(main_d):
    rules = BARRIERS + OPT
    parts = []
    if main_d is not None:
        parts.append(("LP-Round start", main_d[main_d.scale.isin(["Medium", "Large"]) & main_d.method.isin(rules)]))
    for f, label in (("work_commit_direct.csv", "Direct start"), ("work_commit_pair.csv", "MCA-SC-Pair")):
        d = read(f)
        if d is not None:
            parts.append((label, gapify(d)))
    if not parts:
        return
    MD.append("\n## Commit-rule isolation: work protocol (Medium + Large)\n")
    S["commit"] = {}
    cfs = []
    fam = []
    for label, d in parts:
        g = scale_means(d, scales=["Medium", "Large"])[[m for m in rules if m in set(d.method)]]
        d2 = d.assign(cr=100.0 * d.conflict_epochs / d.epochs_run)
        cr = scale_means(d2, "cr", scales=["Medium", "Large"])[[m for m in rules if m in set(d.method)]]
        C = compare(wide(d), PRIMARY, [m for m in rules if m != PRIMARY], label)
        fam.append(C)
        cf = counterfactual(d, label)
        if cf is not None:
            cfs.append(cf)
        S["commit"][label] = dict(gap=tdict(g), conflict=tdict(cr), n=int(d.instance_name.nunique()))
        md_table(f"{label}: mean gap (%)", g.T)
        md_table(f"{label}: conflict epochs (%)", cr.T, "{:.1f}")
    F = pd.concat(fam)
    F["p_holm"] = holm(F["p"].values)          # one Holm family over the three regimes
    for label, _ in parts:
        Cl = F[F.family == label]
        md_compare(f"{label}: {PRIMARY} vs each commit rule (Holm over all regimes)", Cl)
        S["commit"][label]["tests"] = tests_dict(Cl)
    F.to_csv(TAB / "work_commit_tests.csv", index=False)
    if cfs:
        cf = pd.concat(cfs)
        cf.to_csv(TAB / "work_counterfactual.csv", index=False)
        md_table("Counterfactual barrier analysis (conflict epochs of the PC-MALNS [MC-CRIP] runs)", cf, "{:.2f}")
        S["counterfactual"] = cf.to_dict("records")
    # residual-slack diagnostic from the same runs (identical by construction)
    rows = []
    for label, d in parts[:2]:
        sub = d[d.method.isin([PRIMARY, ORACLE, QS])].assign(acc=lambda x: x.accepted_moves / x.epochs_run)
        agg = sub.groupby("method")[["gap_pct", "mean_slack", "mean_bottleneck_slack", "final_slack", "acc",
                                     "epochs_run"]].mean()
        Wm = wide(sub, "mean_slack")
        Wb = wide(sub, "mean_bottleneck_slack")
        Wa = wide(sub, "acc")
        ts = paired_wilcoxon(Wm[ORACLE].values, Wm[PRIMARY].values)
        tb = paired_wilcoxon(Wb[ORACLE].values, Wb[PRIMARY].values)
        ta = paired_wilcoxon(Wa[ORACLE].values, Wa[PRIMARY].values)
        rows.append(dict(regime=label, n=int(len(Wm)),
                         slack_oracle=100 * agg.loc[ORACLE, "mean_slack"], slack_primary=100 * agg.loc[PRIMARY, "mean_slack"],
                         slack_qs=100 * agg.loc[QS, "mean_slack"],
                         bott_oracle=100 * agg.loc[ORACLE, "mean_bottleneck_slack"],
                         bott_primary=100 * agg.loc[PRIMARY, "mean_bottleneck_slack"],
                         acc_oracle=agg.loc[ORACLE, "acc"], acc_primary=agg.loc[PRIMARY, "acc"],
                         acc_qs=agg.loc[QS, "acc"],
                         gap_oracle=agg.loc[ORACLE, "gap_pct"], gap_primary=agg.loc[PRIMARY, "gap_pct"],
                         gap_qs=agg.loc[QS, "gap_pct"],
                         slack_less_wins=ts["wins"], slack_p=ts["p_value"], bott_less_wins=tb["wins"],
                         bott_p=tb["p_value"], acc_less_wins=ta["wins"], acc_p=ta["p_value"]))
    sl = pd.DataFrame(rows)
    sl.to_csv(TAB / "work_slack.csv", index=False)
    md_table("Residual slack diagnostic (same runs; slack in % of capacity)", sl, "{:.4f}")
    S["slack"] = sl.to_dict("records")


# ---------------------------------------------------------------------------
# fresh validation (seeds 201..210)
# ---------------------------------------------------------------------------
def validation():
    V = read("work_validation.csv")
    if V is None:
        return
    V = gapify(V, "lower_bound_at_run")
    MD.append("\n## Fresh validation (seeds 201–210, gap to the LP bound)\n")
    g = scale_means(V)[[PRIMARY, ORACLE, QS]]
    md_table("Mean gap to LP bound (%)", g.T)
    C = compare(wide(V), PRIMARY, [ORACLE, QS], "validation")
    md_compare("Pre-declared test (results/validation_plan.md)", C)
    C.to_csv(TAB / "work_validation_tests.csv", index=False)
    S["validation"] = dict(gap=tdict(g), tests=tests_dict(C), n=int(V.instance_name.nunique()),
                           primary_p_unadjusted=float(C.set_index("method").loc[ORACLE, "p"]))


# ---------------------------------------------------------------------------
# ablations (work protocol, all 60 instances): levels, prices/quotas, restarts
# ---------------------------------------------------------------------------
def ablations(main_d):
    if main_d is None:
        return
    base = main_d[main_d.method == PRIMARY]
    for f, key, title in (("work_levels.csv", "levels", "Portfolio-level ablation"),
                          ("work_prices.csv", "prices", "Price and quota ablation"),
                          ("work_restart.csv", "restart", "Restarts")):
        A = read(f)
        if A is None:
            continue
        A = gapify(A)
        d = pd.concat([base, A], ignore_index=True)
        names = list(dict.fromkeys(A.method))
        g = scale_means(d)[[PRIMARY] + names]
        C = compare(wide(d), PRIMARY, names, key)
        ep = scale_means(A, "epochs_run")
        MD.append(f"\n## {title}: work protocol, 60 instances\n")
        md_table("Mean gap (%)", g.T)
        md_compare(f"{PRIMARY} (all four levels / no prices / no restarts) vs each variant", C)
        C.to_csv(TAB / f"work_{key}_tests.csv", index=False)
        S[key] = dict(gap=tdict(g), tests=tests_dict(C), epochs=tdict(ep))
        if key == "restart":
            S[key]["restarts_per_run"] = tdict(scale_means(A, "restarts"))
            S[key]["last_improve_frac"] = tdict(scale_means(A.assign(f=A.last_improve_epoch / A.epochs_run), "f"))


def extras(main_d):
    """Fresh price test (seeds 301-310, results/price_plan.md), rho0 = 0 ablation, level-0
    donor diagnostics and the all-epoch counterfactual (work_cf_all.csv)."""
    F = read("work_prices_fresh.csv")
    if F is not None:
        F = gapify(F, "lower_bound_at_run")
        priced = [m for m in F.method.unique() if m != PRIMARY][0]
        g = scale_means(F)[[PRIMARY, priced]]
        C = compare(wide(F), PRIMARY, [priced], "prices_fresh")
        MD.append("\n## Fresh price test (seeds 301–310, gap to the LP bound; results/price_plan.md)\n")
        md_table("Mean gap to LP bound (%)", g.T)
        md_compare("Pre-declared test", C)
        S["prices_fresh"] = dict(gap=tdict(g), tests=tests_dict(C), n=int(F.instance_name.nunique()),
                                 method=priced)
    Q = read("work_seq.csv")
    if Q is not None and main_d is not None:
        Q = gapify(Q)
        d = pd.concat([main_d[main_d.method.isin([PRIMARY, ORACLE, "Opt-SeqLock", "Opt-Rollback"])], Q],
                      ignore_index=True)
        g = scale_means(d)[[PRIMARY, ORACLE, "Seq-Commit", "Opt-SeqLock", "Opt-Rollback"]]
        C = compare(wide(d), PRIMARY, ["Seq-Commit"], "seq")
        C2 = compare(wide(d), "Seq-Commit", ["Opt-SeqLock", "Opt-Rollback"], "seq-vs-opt")
        F = pd.concat([C, C2], ignore_index=True)
        F["p_holm"] = holm(F["p"].values)
        MD.append("\n## Sequential baseline Seq-Commit: work protocol, 60 instances\n")
        md_table("Mean gap (%)", g.T)
        md_compare("Seq-Commit comparisons (Holm over the three tests)", F.assign(
            method=F.reference.str.replace("PC-MALNS [Greedy-Efficiency]", "GE") + " vs " + F.method))
        per = []
        for sc in SC:
            Cs = compare(wide(d[d.scale == sc]), PRIMARY, ["Seq-Commit"], sc)
            per.append(Cs.assign(scale=sc))
        PS = pd.concat(per, ignore_index=True)
        PS["p_holm"] = holm(PS["p"].values)
        md_compare("GE vs Seq-Commit per scale (Holm over the six scales)", PS.assign(method=PS.scale))
        S["seq"] = dict(gap=tdict(g), tests={f"{r.reference}|{r.method}": {k: getattr(r, k) for k in
                        ("n", "ref_mean", "method_mean", "diff", "t_lo", "t_hi", "wins", "ties", "losses", "p", "p_holm")}
                        for r in F.itertuples()},
                        per_scale={r.scale: {k: getattr(r, k) for k in ("diff", "wins", "ties", "losses", "p", "p_holm")}
                                   for r in PS.itertuples()},
                        epochs=tdict(scale_means(Q, "epochs_run")))
    R = read("work_rho0.csv")
    if R is not None and main_d is not None:
        R = gapify(R)
        base = main_d[main_d.method == PRIMARY]
        d = pd.concat([base, R], ignore_index=True)
        name = R.method.iloc[0]
        g = scale_means(d)[[PRIMARY, name]]
        C = compare(wide(d), PRIMARY, [name], "rho0")
        MD.append("\n## rho0 = 0 ablation: work protocol, 60 instances\n")
        md_table("Mean gap (%)", g.T)
        md_compare(f"{PRIMARY} vs rho0 = 0", C)
        S["rho0"] = dict(gap=tdict(g), tests=tests_dict(C), method=name)
    W = read("work_main.csv")
    X = read("work_cf_all.csv")
    # level-0 donor diagnostics: the work-protocol runs that record them (work_cf_all reproduces the
    # GE and MC-CRIP runs of work_main) and every wall-clock run
    l0 = dict(tries=0, dominated=0, committed=0, runs=0)
    srcs = [X] + [read(f"wall_{j}.csv") for j in ("main", "rich", "rich_rerun", "sweep", "pair", "mmkp")]
    for d in srcs:
        if d is not None and "l0_tries" in d:
            d = d[d.l0_tries.notna()]
            l0["tries"] += int(d.l0_tries.sum())
            l0["dominated"] += int(d.l0_dominated.sum())
            l0["committed"] += int(d.l0_committed.sum())
            l0["runs"] += int(len(d))
    S["level0"] = l0
    MD.append(f"\n- Level-0 donors (work_cf_all and all wall-clock runs): {l0}")
    # MC-CRIP time-limit fallbacks (epochs in which HiGHS stopped at its limit without proving optimality)
    fb = dict(work_epochs=0, work_runs=0, wall_epochs=0, wall_runs=0, wall_total_runs=0)
    for f, kind in [("work_main.csv", "work"), ("work_commit_direct.csv", "work"), ("work_commit_pair.csv", "work"),
                    ("work_validation.csv", "work")] + \
                   [(f"wall_{j}.csv", "wall") for j in ("main", "rich", "rich_rerun", "sweep", "pair", "mmkp")]:
        d = read(f)
        if d is None or "matcher_fallbacks" not in d:
            continue
        d = d[d.method == ORACLE]
        fb[f"{kind}_epochs"] += int(d.matcher_fallbacks.sum())
        fb[f"{kind}_runs"] += int((d.matcher_fallbacks > 0).sum())
        if kind == "wall":
            fb["wall_total_runs"] += int(len(d))
    S["fallbacks"] = fb
    MD.append(f"- MC-CRIP fallbacks: {fb}")
    L = read("lower_bounds.csv")
    S["lb"] = dict(n=int(len(L)), proven_optimal=int(L.proven_optimal.sum()),
                   from_lp=int((L.lb_source == "LP").sum()),
                   over_lp_mean=L.groupby("family").lb_over_lp_pct.mean().to_dict(),
                   highs_gap_median=L.groupby("family").highs_gap_pct.median().to_dict(),
                   highs_gap_max=L.groupby("family").highs_gap_pct.max().to_dict())
    MD.append(f"- Lower bounds: {S['lb']}")
    if X is not None and W is not None:
        key = ["instance_name", "method", "rep"]
        j = X.merge(W, on=key, suffixes=("", "_m"))
        identical = int((j.best_obj == j.best_obj_m).sum())
        rules = ["MC-CRIP", "Quota-Surplus", "Greedy-Gain", "Greedy-Efficiency", "Static-Quota"]
        out = {}
        for m in (PRIMARY, ORACLE):
            sub = X[X.method == m]
            nc = int((sub.epochs_run - sub.conflict_epochs).sum())
            tot, dev, cheap = {r: 0.0 for r in rules}, {r: 0 for r in rules}, 0.0
            by_scale = {}
            for r in sub.itertuples():
                s, dv = json.loads(r.nc_sum), json.loads(r.nc_deviate)
                cheap += s["cheapest"]
                bs = by_scale.setdefault(r.scale, dict(nc=0, dev=0, loss=0.0, cheap=0.0))
                bs["nc"] += int(r.epochs_run - r.conflict_epochs)
                bs["cheap"] += s["cheapest"]
                for k in rules:
                    tot[k] += s[k] - s["cheapest"]
                    dev[k] += int(dv[k])
                bs["dev"] += int(dv["Greedy-Efficiency"])
                bs["loss"] += s["Greedy-Efficiency"] - s["cheapest"]
            out[m] = dict(nonconflict_epochs=nc,
                          deviate_pct={k: 100.0 * dev[k] / nc for k in rules},
                          deviate_epochs=dev,
                          loss_pct_of_gain={k: 100.0 * tot[k] / -cheap for k in rules},
                          ge_by_scale={sc: dict(dev_pct=100.0 * v["dev"] / v["nc"],
                                                loss_pct=100.0 * v["loss"] / -v["cheap"])
                                       for sc, v in by_scale.items()})
        S["cf_all"] = dict(runs=int(len(X)), identical_to_main=identical, by_trajectory=out)
        MD.append("\n## All-epoch counterfactual (work_cf_all.csv)\n")
        MD.append(f"- {len(X)} runs; best objective identical to work_main in {identical}")
        for m, v in out.items():
            MD.append(f"- trajectories of {m}: {v['nonconflict_epochs']} non-conflict epochs; deviate % "
                      + ", ".join(f"{k} {x:.3f}" for k, x in v["deviate_pct"].items())
                      + "; loss % of cheapest gain " + ", ".join(f"{k} {x:.2f}" for k, x in v["loss_pct_of_gain"].items()))


# ---------------------------------------------------------------------------
# stall analysis (fix: time-to-stall)
# ---------------------------------------------------------------------------
def stall(main_d):
    W = read("work_main.csv")
    if W is None:
        return
    rows = []
    for r in W[W.trace.notna()].itertuples():
        tr = np.array(json.loads(r.trace))
        imp = tr[0] - tr[-1]
        n = len(tr) - 1
        if imp <= 1e-9 or n == 0:
            t95, last = np.nan, np.nan
        else:
            t95 = int(np.argmax(tr <= tr[0] - 0.95 * imp)) / n
            dec = np.where(np.diff(tr) < -1e-9)[0]
            last = (dec[-1] + 1) / n if len(dec) else np.nan
        rows.append(dict(method=r.method, scale=r.scale, instance_name=r.instance_name, t95=t95, last=last))
    st = pd.DataFrame(rows)
    allruns = W.assign(last_all=W.last_improve_epoch / W.epochs_run)
    out = {}
    for m in [PRIMARY, ORACLE] + OPT:
        sm = st[st.method == m]
        if not len(sm):
            continue
        out[m] = dict(t95_by_scale=sm.groupby("scale").t95.mean().reindex(SC).to_dict(),
                      last_by_scale=sm.groupby("scale")["last"].mean().reindex(SC).to_dict(),
                      t95_mean=float(sm.t95.mean()), last_mean=float(sm["last"].mean()),
                      last_all_runs_mean=float(allruns[allruns.method == m].last_all.mean()),
                      n_traces=int(len(sm)))
    MD.append("\n## Stall analysis (work protocol, rep-0 traces; fractions of the epoch budget)\n")
    for m, v in out.items():
        MD.append(f"- {m}: 95% of the improvement after {v['t95_mean']:.2f} of the budget, last improvement at "
                  f"{v['last_mean']:.2f} (all runs: {v['last_all_runs_mean']:.2f}); by scale t95 = "
                  + ", ".join(f"{s} {x:.2f}" for s, x in v["t95_by_scale"].items()))
    S["stall"] = out
    # wall-clock traces of the uniform-condition main job (fraction of the budget), all runs
    A = wall("main")
    if A is None:
        return
    rows = []
    for r in A[(A.method == PRIMARY) & A.trace.notna()].itertuples():
        tr = np.array(json.loads(r.trace))
        if len(tr) < 2:
            continue
        t, o = tr[:, 0], tr[:, 1]
        imp = o[0] - o[-1]
        if imp <= 1e-9:
            continue
        t95 = t[int(np.argmax(o <= o[0] - 0.95 * imp))] / r.wall_budget_s
        dec = np.where(np.diff(o) < -1e-9)[0]
        rows.append(dict(scale=r.scale, t95=t95, last=t[dec[-1] + 1] / r.wall_budget_s))
    sw = pd.DataFrame(rows)
    S["stall_wall"] = dict(t95_by_scale=sw.groupby("scale").t95.mean().reindex(SC).to_dict(),
                           last_by_scale=sw.groupby("scale")["last"].mean().reindex(SC).to_dict(),
                           t95_mean=float(sw.t95.mean()), last_mean=float(sw["last"].mean()))


# ---------------------------------------------------------------------------
# wall-clock protocol (secondary): uniform-condition runs of results/rerun_plan.md
# (wall_<job>.csv, wall_reference.csv, wall_calibration.csv)
# ---------------------------------------------------------------------------
HCOLD = ["HiGHS (1T, wall-matched)", "HiGHS (4T, wall-matched)", "HiGHS (1T, CPU-matched)"]
HWARM = ["HiGHS+LP-Round (1T, wall-matched)", "HiGHS+LP-Round (1T, CPU-matched)"]


def wall(job):
    d = read(f"wall_{job}.csv")
    if d is None:
        return None
    d = d[d.method.notna()].copy()
    return d


def ref_rows(job):
    R = read("wall_reference.csv")
    return None if R is None else R[R.job == job].drop_duplicates("instance_name", keep="last").set_index("instance_name")


def time_to_target(d, job, target_method=PRIMARY):
    """Time the 1-thread HiGHS reference run needs to reach the mean objective of target_method
    on the same instance (NaN if never within its limit), next to the mean wall-clock time of
    target_method."""
    R = ref_rows(job)
    if R is None:
        return None
    m = d[d.method == target_method].groupby("instance_name").agg(target=("best_obj", "mean"),
                                                                  wall=("wall_clock_s", "mean"),
                                                                  cpu=("cpu_time_s", "mean"),
                                                                  scale=("scale", "first"), P=("P", "first"),
                                                                  eta=("eta", "first"))
    rows = []
    for inst, r in m.iterrows():
        if inst not in R.index:
            continue
        tr = json.loads(R.loc[inst, "trace"]) if isinstance(R.loc[inst, "trace"], str) else []
        lim = float(R.loc[inst, "highs_time_limit_s"])
        t = next((a for a, o in tr if o <= r.target + 1e-6 and a <= lim), np.nan)
        rows.append(dict(instance_name=inst, scale=r.scale, P=r.P, eta=r.eta, ttt=t, lns_wall=r.wall, lns_cpu=r.cpu,
                         limit=lim,
                         killed=bool(R.loc[inst, "highs_killed"]) if "highs_killed" in R and R.loc[inst, "highs_killed"] == R.loc[inst, "highs_killed"] else False))
    return pd.DataFrame(rows)


def primal_integral_common(d, job, T_col="wall_budget_s"):
    """Primal integral of target LNS runs and of the HiGHS reference trace over the same horizon
    (the LNS budget of the instance), primal gap |C - LB| / max(|C|, |LB|), 1 before the first solution."""
    from src.engine import primal_integral
    R = ref_rows(job)
    out = []
    for r in d[d.method == PRIMARY].itertuples():
        T = float(getattr(r, T_col))
        lb = LB.get(r.instance_name, np.nan)
        if not np.isfinite(lb):
            continue
        tr = json.loads(r.trace) if isinstance(r.trace, str) else []
        pi_l = primal_integral([a for a, _ in tr], [o for _, o in tr], lb, T) / T
        hr = json.loads(R.loc[r.instance_name, "trace"]) if R is not None and r.instance_name in R.index else []
        pi_h = primal_integral([a for a, _ in hr], [o for _, o in hr], lb, T) / T
        out.append(dict(instance_name=r.instance_name, scale=r.scale, P=r.P, pi_lns=pi_l, pi_highs=pi_h))
    o = pd.DataFrame(out)
    return o.groupby(["instance_name", "scale", "P"], as_index=False).mean()


def ttt_summary(tt, keys):
    g = tt.groupby(keys).agg(n=("instance_name", "count"), never=("ttt", lambda x: int(x.isna().sum())),
                            ttt_median=("ttt", "median"), ttt_max=("ttt", "max"), lns_wall_median=("lns_wall", "median"))
    g["ratio_median"] = tt.assign(r=tt.ttt / tt.lns_wall).groupby(keys).r.median()
    # the reference run uses one thread; against the CPU time of the four-process LNS run
    g["ratio_cpu_median"] = tt.assign(r=tt.ttt / tt.lns_cpu).groupby(keys).r.median()
    return g


def wall_main():
    d = wall("main")
    if d is None:
        return
    d = gapify(d)
    order = ["LP-Round", PRIMARY, ORACLE, "Opt-Rollback", "Opt-SeqLock", "Async-Lock"] + HCOLD + HWARM + \
            ["HiGHS (5s)", "HiGHS (60s)", "HiGHS (600s)"]
    g = scale_means(d)[[m for m in order if m in set(d.method)]]
    MD.append("\n## Main benchmark: wall-clock protocol (uniform conditions), HiGHS 1.16.0\n")
    md_table("Mean gap (%) by scale (HiGHS (600s): Small and Medium only)", g.T)
    C = compare(wide(d), PRIMARY, [m for m in order if m not in (PRIMARY, "HiGHS (600s)")], "wall-main")
    md_compare(f"Wall clock: {PRIMARY} vs each method (60 instances)", C)
    C.to_csv(TAB / "wall_main_tests.csv", index=False)
    rows = []
    for s in SC:
        Cs = compare(wide(d[d.scale == s]), PRIMARY,
                     ["Opt-Rollback", "Opt-SeqLock", "Async-Lock"] + HCOLD + HWARM + ["HiGHS (5s)"], s)
        rows.append(Cs.assign(scale=s))
    PS = pd.concat(rows)
    PS["p_holm"] = holm(PS["p"].values)
    PS.to_csv(TAB / "wall_main_by_scale.csv", index=False)
    md_compare("Per scale (Holm over the family)", PS.assign(method=PS.scale + ": " + PS.method))
    L = d[d.family == "LNS"]
    ep = scale_means(L, "epochs_run")
    over = scale_means(L.assign(o=100 * (L.wall_clock_s / L.wall_budget_s - 1)), "o")
    cpu = scale_means(L.assign(c=L.cpu_time_s / L.wall_clock_s), "c")
    md_table("Epochs per run (wall clock)", ep.T, "{:.1f}")
    md_table("Budget overrun (% of the budget)", over.T, "{:.2f}")
    tt = time_to_target(d, "main")
    ts = ttt_summary(tt, ["scale"]).reindex(SC)
    md_table("Time for the 1-thread HiGHS reference run to reach the mean PC-MALNS [Greedy-Efficiency] objective (s)", ts)
    pi = primal_integral_common(d, "main")
    pis = pi.groupby("scale")[["pi_lns", "pi_highs"]].mean().reindex(SC)
    md_table("Primal integral over the PC-MALNS budget, divided by the budget", pis, "{:.4f}")
    AS = d[d.method == "Async-Lock"]
    a = AS.groupby("scale")[["steps_per_agent", "accepted_moves", "proposals", "rejected_fit"]].mean().reindex(SC)
    md_table("Async-Lock: steps per agent, accepted, proposals, rejected (did not fit)", a, "{:.1f}")
    S["wall_main"] = dict(gap=tdict(g), tests=tests_dict(C), by_scale=PS.to_dict("records"), epochs=tdict(ep),
                          overrun_pct=tdict(over), cpu_per_wall=tdict(cpu),
                          ttt={s: {k: (None if not np.isfinite(v) else float(v)) for k, v in r.items()}
                               for s, r in ts.to_dict("index").items()},
                          pi={s: {k: float(v) for k, v in r.items()} for s, r in pis.to_dict("index").items()},
                          async_stats={c: {s: float(a.loc[s, c]) for s in a.index} for c in a.columns})


def rich():
    d = wall("rich")
    if d is None:
        return
    d = gapify(d)
    rr = wall("rich_rerun")
    order = ["LP-Round", PRIMARY, ORACLE, QS, "Opt-Rollback", "Opt-SeqLock"] + HCOLD + HWARM + \
            ["HiGHS (5s)", "HiGHS (30s)", "HiGHS (300s)"]
    S["rich"] = {}
    MD.append("\n## Rich candidate pools: wall clock (uniform conditions), HiGHS 1.16.0\n")
    fam = []
    for P in (20, 40):
        b = d[d.P == P]
        g = scale_means(b, scales=["Medium", "Large", "X-Large", "XXL"])[[m for m in order if m in set(b.method)]]
        md_table(f"J = {P}: mean gap (%)", g.T)
        C = compare(wide(b), PRIMARY, [m for m in order if m not in (PRIMARY, "HiGHS (300s)")], f"P={P}")
        fam.append(C)
        S["rich"][P] = dict(gap=tdict(g))
    F = pd.concat(fam)
    F["p_holm"] = holm(F["p"].values)
    for P in (20, 40):
        Cl = F[F.family == f"P={P}"]
        md_compare(f"J = {P}: {PRIMARY} vs each method (Holm over both J)", Cl)
        S["rich"][P]["tests"] = tests_dict(Cl)
    F.to_csv(TAB / "wall_rich_tests.csv", index=False)
    pooled = compare(wide(d), PRIMARY, [m for m in order if m not in (PRIMARY, "HiGHS (300s)")], "rich-all")
    S["rich"]["pooled"] = tests_dict(pooled)
    tt = time_to_target(d, "rich")
    ts = ttt_summary(tt, ["P", "scale"])
    md_table("Rich pools: time for the HiGHS reference run (300 s) to reach the PC-MALNS objective (s)", ts)
    S["rich"]["ttt"] = {f"{k[0]}|{k[1]}": {c: (None if not np.isfinite(v) else float(v)) for c, v in r.items()}
                        for k, r in ts.to_dict("index").items()}
    # sensitivity rerun of the slow stretch (rerun_plan.md, addendum 2026-11-20)
    if rr is not None and len(rr):
        rr = gapify(rr)
        common = sorted(set(rr.instance_name) & set(d.instance_name))
        S["rich"]["rerun"] = dict(n=len(common))
        o = d[d.instance_name.isin(common)]
        n = rr[rr.instance_name.isin(common)]
        out = {}
        for lab, x in (("original", o), ("rerun", n)):
            Cx = compare(wide(x), PRIMARY, ["Opt-Rollback", "Opt-SeqLock", ORACLE, QS] + HCOLD + HWARM, lab)
            out[lab] = tests_dict(Cx)
            md_compare(f"Rich, slow-stretch instances ({len(common)}), {lab} runs: {PRIMARY} vs each", Cx)
        ep = pd.DataFrame({lab: x[x.method == PRIMARY].groupby(["P", "scale"]).epochs_run.mean()
                           for lab, x in (("original", o), ("rerun", n))})
        md_table("Epochs of PC-MALNS [Greedy-Efficiency]: original vs rerun", ep, "{:.1f}")
        S["rich"]["rerun"].update(tests=out, epochs={f"{k[0]}|{k[1]}": {c: float(v) for c, v in r.items()}
                                                     for k, r in ep.to_dict("index").items()})
        # combined data set: rerun rows replace the slow-stretch rows (for absolute values and J trends)
        comb = pd.concat([d[~d.instance_name.isin(common)], n], ignore_index=True)
        gcomb = {P: tdict(scale_means(comb[comb.P == P], scales=["Medium", "Large", "X-Large", "XXL"]))
                 for P in (20, 40)}
        S["rich"]["combined_gap"] = gcomb
        ttc = time_to_target(n, "rich_rerun")
        if ttc is not None and len(ttc):
            ttc_all = pd.concat([tt[~tt.instance_name.isin(common)], ttc])
            tsc = ttt_summary(ttc_all, ["P", "scale"])
            md_table("Rich pools, combined (rerun rows for the slow stretch): time to target (s)", tsc)
            S["rich"]["ttt_combined"] = {f"{k[0]}|{k[1]}": {c: (None if not np.isfinite(v) else float(v))
                                                            for c, v in r.items()} for k, r in tsc.to_dict("index").items()}


def sweep():
    d = wall("sweep")
    m = wall("main")
    if d is None or m is None:
        return
    d = pd.concat([gapify(d), gapify(m[m.scale == "Large"])], ignore_index=True)
    order = ["LP-Round", PRIMARY, ORACLE, QS, "Opt-Rollback", "Opt-SeqLock", "Static-Quota",
             "HiGHS (1T, wall-matched)", "HiGHS+LP-Round (1T, wall-matched)", "HiGHS (1T, CPU-matched)", "HiGHS (5s)"]
    pi = d.groupby(["instance_name", "eta", "method"], as_index=False).gap_pct.mean()
    t = pi.groupby(["eta", "method"]).gap_pct.mean().unstack("method").reindex(columns=[m for m in order if m in set(pi.method)])
    L = d[d.family == "LNS"]
    cr = L.assign(cr=100 * L.conflict_epochs / L.epochs_run).groupby(["eta", "method"]).cr.mean().unstack("method")
    MD.append("\n## Tightness sweep (Large, wall clock; eta = 1.25 from the main job)\n")
    md_table("Mean gap (%) by eta", t)
    md_table("Conflict epochs (%) by eta", cr, "{:.1f}")
    rows = []
    for eta, g in pi.groupby("eta"):
        rows.append(compare(g.pivot(index="instance_name", columns="method", values="gap_pct"), PRIMARY,
                            [m for m in order if m != PRIMARY], f"eta={eta}"))
    C = pd.concat(rows)
    C["p_holm"] = holm(C["p"].values)
    C.to_csv(TAB / "wall_sweep_tests.csv", index=False)
    md_compare("Sweep: per eta, Holm over the whole sweep", C.assign(method=C.family + ": " + C.method))
    Hw = d[d.method == "HiGHS (1T, wall-matched)"].copy()
    Hw["n_inc"] = Hw.trace.apply(lambda x: len(json.loads(x)) if isinstance(x, str) and x else 0)
    Hw["t_first"] = Hw.trace.apply(lambda x: json.loads(x)[0][0] if isinstance(x, str) and x and json.loads(x) else np.nan)
    hd = Hw.groupby("eta")[["n_inc", "t_first", "nodes", "highs_time_limit_s"]].mean()
    md_table("HiGHS (1T, wall-matched) by eta: incumbents, first incumbent (s), nodes, limit (s)", hd)
    tt = pd.concat([time_to_target(d[d.eta != 1.25], "sweep"), time_to_target(d[d.eta == 1.25], "main")])
    ts = ttt_summary(tt, ["eta"])
    md_table("Sweep: time to target (s)", ts)
    S["sweep"] = dict(gap={str(k): v for k, v in tdict(t.T).items()}, conflict={str(k): v for k, v in tdict(cr.T).items()},
                      tests=C.to_dict("records"), n_tests=int(len(C)),
                      highs_diag={str(e): {c: float(hd.loc[e, c]) for c in hd.columns} for e in hd.index},
                      ttt={str(k): {c: (None if not np.isfinite(v) else float(v)) for c, v in r.items()}
                           for k, r in ts.to_dict("index").items()})


def pair_wall():
    d = wall("pair")
    if d is None:
        return
    d = gapify(d)
    order = ["LP-Round", PRIMARY, ORACLE, QS, GG, "Opt-Rollback-Portfolio", "Opt-SeqLock-Portfolio",
             "Opt-Rollback", "Opt-SeqLock"] + HCOLD + HWARM + ["HiGHS (5s)", "HiGHS (60s)"]
    g = scale_means(d, scales=["Medium", "Large"])[[m for m in order if m in set(d.method)]]
    C = compare(wide(d), PRIMARY, [m for m in order if m not in (PRIMARY, "HiGHS (60s)")], "pair-wall")
    MD.append("\n## MCA-SC-Pair: wall clock (uniform conditions)\n")
    md_table("Mean gap (%)", g.T)
    md_compare(f"Pair (wall clock): {PRIMARY} vs each", C)
    tt = time_to_target(d, "pair")
    ts = ttt_summary(tt, ["scale"])
    md_table("Pair: time to target (s)", ts)
    S["pair_wall"] = dict(gap=tdict(g), tests=tests_dict(C),
                          ttt={s: {k: (None if not np.isfinite(v) else float(v)) for k, v in r.items()}
                               for s, r in ts.to_dict("index").items()})


def mmkp():
    d = wall("mmkp")
    if d is None:
        return
    d["set"] = np.where(d.mmkp.str.startswith("INST"), "INST01-20", "I07-I13")
    order = ["LP-Round", PRIMARY, ORACLE, QS, "Opt-Rollback", "Opt-SeqLock", "Static-Quota",
             "HiGHS (1T, wall-matched)", "HiGHS (4T, wall-matched)", "HiGHS (1T, CPU-matched)", "HiGHS (5s)", "HiGHS (60s)"]
    feas = d.assign(f=d.mmkp_feasible.astype(str).str.lower().eq("true")).groupby("method").f.mean().reindex(order) * 100
    excl = sorted(d[(d.family == "LNS") & ~d.mmkp_feasible.astype(str).str.lower().eq("true")].mmkp.unique())
    e = d[~d.mmkp.isin(excl)]
    gi = e.groupby(["instance_name", "set", "method"], as_index=False).gap_bks_pct.mean()
    t = gi.groupby(["set", "method"]).gap_bks_pct.mean().unstack("method").reindex(columns=order)
    t.loc["All"] = gi.groupby("method").gap_bks_pct.mean().reindex(order)
    W = gi.pivot(index="instance_name", columns="method", values="gap_bks_pct")
    C = compare(W, PRIMARY, [m for m in order if m not in (PRIMARY, "LP-Round")], "mmkp")
    L = e[e.family == "LNS"]
    stall0 = L.assign(s=(L.best_obj - L.initial_obj).abs() < 1e-6).groupby("method").s.mean()
    ident = L.groupby("instance_name").best_obj.nunique()
    MD.append(f"\n## MMKP (wall clock; excluded: {', '.join(excl)})\n")
    md_table("Mean gap to the best known solution (%)", t.T)
    md_compare(f"MMKP: {PRIMARY} vs each method", C)
    C.to_csv(TAB / "wall_mmkp_tests.csv", index=False)
    S["mmkp"] = dict(gap={m: {s: (None if not np.isfinite(t.loc[s, m]) else float(t.loc[s, m])) for s in t.index}
                          for m in t.columns},
                     feasible_pct={m: float(v) for m, v in feas.items() if np.isfinite(v)}, excluded=excl,
                     n=int(W.shape[0]), tests=tests_dict(C),
                     no_improvement_share={m: float(v) for m, v in stall0.items()},
                     all_lns_identical=int((ident == 1).sum()),
                     conflict_pct=float(100 * (L[L.method == PRIMARY].conflict_epochs / L[L.method == PRIMARY].epochs_run).mean()))


def run_conditions():
    """Calibration history, drift flags, power waits, watchdog kills, budget overruns."""
    cal = read("wall_calibration.csv")
    if cal is None:
        return
    run = cal[cal.phase == "run"]
    base = run.iloc[0]
    out = dict(n_calib=int(len(run)), base_wall=float(base.wall_clock_s), base_cpu=float(base.cpu_time_s),
               objective_identical=bool(run.best_obj.nunique() == 1),
               flagged=[dict(index=int(r.calib_index), job=r.job, time=r.timestamp, drift_wall=float(r.drift_wall),
                             drift_cpu=float(r.drift_cpu)) for r in run[run.drift_flag == True].itertuples()],
               max_abs_drift_unflagged=float(run[run.drift_flag != True][["drift_wall", "drift_cpu"]].abs().max().max()))
    waits, rows_total = [], 0
    for job in ("main", "rich", "sweep", "pair", "mmkp", "rich_rerun"):
        w = wall(job)
        if w is None:
            continue
        rows_total += len(w)
        for r in w[w.ac_wait_s > 0].itertuples():
            waits.append(dict(job=job, instance=r.instance_name, wait_s=float(r.ac_wait_s)))
        out[f"power_{job}"] = sorted(set(w.power_source.dropna()))
    R = read("wall_reference.csv")
    out.update(power_waits=waits, rows=int(rows_total), n_reference=int(len(R)),
               killed=R[R.highs_killed == True][["job", "instance_name"]].to_dict("records"),
               reference_optimal=int((R.highs_status == "Optimal").sum()))
    S["run_conditions"] = out
    MD.append("\n## Run conditions\n")
    MD.append("- " + json.dumps(out, default=str))


# ---------------------------------------------------------------------------
def wall_repeatability():
    """Revision 2 reran the same wall-clock configurations for its slack diagnostic
    (diag_slack.csv) on the instances of bench_A (LP-Round start) and bench_C_direct
    (direct start); comparing the paired runs measures how repeatable wall-clock runs are."""
    D = read("diag_slack.csv")
    if D is None:
        return
    out = {}
    for init, f in (("lp_round", "bench_A.csv"), ("direct", "bench_C_direct.csv")):
        src = read(f)
        d = D[D.init_mode == init].set_index(["instance_name", "method", "rep"])
        o = src[src.method.isin(set(D.method))].set_index(["instance_name", "method", "rep"])
        j = d[["epochs_run", "gap_pct", "conflict_epochs"]].join(o[["epochs_run", "gap_pct", "conflict_epochs"]],
                                                                rsuffix="_orig", how="inner")
        diff = (j.gap_pct - j.gap_pct_orig).abs()
        out[init] = dict(n=int(len(j)), epochs_rerun=float(j.epochs_run.mean()), epochs_orig=float(j.epochs_run_orig.mean()),
                         epochs_ratio=float(j.epochs_run.mean() / j.epochs_run_orig.mean()),
                         identical_share=float((diff < 1e-9).mean()), mean_abs_diff_all=float(diff.mean()),
                         mean_abs_diff_nonidentical=float(diff[diff >= 1e-9].mean()),
                         conflict_rerun=float(100 * (j.conflict_epochs / j.epochs_run).mean()),
                         conflict_orig=float(100 * (j.conflict_epochs_orig / j.epochs_run_orig).mean()))
    S["wall_repeat"] = out
    MD.append("\n## Repeatability of wall-clock runs (revision-2 reruns)\n")
    for k, v in out.items():
        MD.append(f"- {k}: " + ", ".join(f"{a} = {b:.4g}" for a, b in v.items()))


def scaling_tuning():
    E = read("bench_E_scaling.csv")
    if E is not None:
        t = E.groupby(["scale", "mode", "workers_W"], as_index=False).agg(
            wall_clock_s=("wall_clock_s", "mean"), speedup=("speedup_vs_serial", "mean"),
            identical=("same_obj_as_serial", "all"))
        S["scaling"] = t.to_dict("records")
    T = read("parameter_sensitivity_summary.csv")
    if T is not None:
        S["tuning"] = T.to_dict("records")


def main():
    global LB
    TAB.mkdir(parents=True, exist_ok=True)
    LB = _lb()
    d = main_work()
    commit_work(d)
    validation()
    ablations(d)
    extras(d)
    stall(d)
    wall_main()
    rich()
    sweep()
    pair_wall()
    mmkp()
    run_conditions()
    wall_repeatability()
    scaling_tuning()
    (TAB / "report_tables.md").write_text("\n".join(MD) + "\n")
    (TAB / "summary.json").write_text(json.dumps(S, indent=1, default=float))
    print("\n".join(MD))


if __name__ == "__main__":
    main()
