"""
LaTeX tables of the manuscript, generated from the Step 2 CSVs
(results/raw/bench_*.csv, parameter_sensitivity_summary.csv, diag_slack.csv) with the
same statistics as scripts/analyze_benchmark.py (instance means over the 5 runs,
paired-t 95% CIs, exact Wilcoxon, Holm within each table family).
Writes paper/tables/tab_*.tex.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.analyze_benchmark import load, wide, compare, per_instance, counterfactual, PRIMARY

RAW = REPO_ROOT / "results" / "raw"
OUT = REPO_ROOT / "paper" / "tables"
SC = ["Small", "Medium", "Large", "X-Large", "XXL", "XXXL"]
TT = {PRIMARY: r"\textbf{PC-MALNS [MC-CRIP]}", "PC-MALNS [BCRM-Greedy]": "PC-MALNS [BCRM-Greedy]"}


def tt(m):
    return TT.get(m, m)


def f(v, nd=2):
    return "--" if v is None or not np.isfinite(v) else f"{v:.{nd}f}"


def fp(p):
    return r"$<$0.0001" if p < 1e-4 else f"{p:.4f}"


def fd(v, nd=3):
    return "--" if not np.isfinite(v) else f"{v:+.{nd}f}".replace("-", "$-$")


def write(name, body):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.tex").write_text(body)
    print("wrote", name)


def scale_means(df, value="gap_pct", scales=SC):
    pi = per_instance(df, value, keys=("instance_name", "scale"))
    t = pi.groupby(["scale", "method"])[value].mean().unstack("method")
    t = t.reindex([s for s in scales if s in t.index])
    t.loc["All"] = pi.groupby("method")[value].mean()
    return t


def table_a():
    A = load("A")
    order = ["LP-Round", PRIMARY, "PC-MALNS [BCRM-Greedy]", "Greedy-Efficiency-Portfolio", "Greedy-Gain-Portfolio",
             "Opt-Rollback-Portfolio", "Opt-SeqLock-Portfolio", "Opt-Rollback", "Opt-SeqLock", "Static-Quota",
             "Demand-Quota", "HiGHS (1T, wall-matched)", "HiGHS (4T, wall-matched)", "HiGHS (1T, CPU-matched)",
             "HiGHS (5s)", "HiGHS (60s)", "HiGHS (600s)"]
    g = scale_means(A)
    pi = scale_means(A[A.family != "Deterministic"], "primal_integral")
    rows = []
    for m in order:
        if m == "PC-MALNS [BCRM-Greedy]" or m == "HiGHS (1T, wall-matched)" or m == "Opt-Rollback-Portfolio" \
                or m == "Static-Quota":
            rows.append(r"\addlinespace")
        cells = [f(g.loc[s, m]) if m in g else "--" for s in g.index]
        cells.append(f(pi.loc["All", m], 3) if m in pi and np.isfinite(pi.loc["All", m]) else "--")
        rows.append(tt(m) + " & " + " & ".join(cells) + r" \\")
    head = " & ".join(list(g.index)) + " & PI"
    body = (r"\begin{table}[!htb]" "\n" r"\centering" "\n"
            r"\caption{Main benchmark ($P = 6$, $\eta = 1.25$, 10 test instances per scale): mean gap to "
            r"the lower bound (\%) per scale and mean primal integral (PI, s $\times$ gap fraction) over all 60 "
            r"instances. LNS methods: mean over 5 runs per instance on $W = 4$ processes with wall-clock budgets "
            r"of 0.5, 1, 1.5, 2, 4 and 6 s. HiGHS (5s), (60s) and (CPU-matched) are read from the incumbent trace "
            r"of the 1-thread reference run (600 s on Small and Medium, 60 s otherwise); the wall-matched runs are "
            r"separate runs with the mean wall-clock time of PC-MALNS [MC-CRIP].}" "\n"
            r"\label{tab:main}" "\n" r"\footnotesize" "\n"
            r"\begin{tabular}{@{}l" + "r" * (len(g.index) + 1) + r"@{}}" "\n" r"\toprule" "\n"
            r"Method & " + head + r" \\" "\n" r"\midrule" "\n" + "\n".join(rows) + "\n"
            r"\bottomrule" "\n" r"\end{tabular}" "\n" r"\end{table}" "\n")
    write("tab_main", body)

    C = compare(wide(A), PRIMARY, [m for m in order if m != PRIMARY], "A")
    rows = []
    for r in C.itertuples():
        rows.append(f"{tt(r.method)} & {f(r.method_mean, 3)} & {fd(r.diff)} & [{fd(r.t_lo)}, {fd(r.t_hi)}] & "
                    f"[{fd(r.boot_lo)}, {fd(r.boot_hi)}] & {r.wins}/{r.ties}/{r.losses} & {fp(r.p_holm)}" r" \\")
    body = (r"\begin{table}[!htb]" "\n" r"\centering" "\n"
            r"\caption{Main benchmark, pooled over the 60 test instances: PC-MALNS [MC-CRIP] (mean gap "
            + f(C.ref_mean.iloc[0], 3) + r"\%) against every method. Diff $=$ PC-MALNS [MC-CRIP] $-$ method in "
            r"percentage points (negative favours PC-MALNS [MC-CRIP]) with paired-$t$ and bootstrap 95\% "
            r"confidence intervals; W/T/L counts the instances on which PC-MALNS [MC-CRIP] is better, equal or "
            r"worse; $p$: exact two-sided Wilcoxon signed-rank test, Holm-adjusted over the 16 comparisons.}" "\n"
            r"\label{tab:main_tests}" "\n" r"\footnotesize" "\n"
            r"\begin{tabular}{@{}lrrrrrr@{}}" "\n" r"\toprule" "\n"
            r"Method & Gap & Diff & $t$ 95\% CI & Bootstrap 95\% CI & W/T/L & $p_{\text{Holm}}$ \\" "\n"
            r"\midrule" "\n" + "\n".join(rows) + "\n" r"\bottomrule" "\n" r"\end{tabular}" "\n" r"\end{table}" "\n")
    write("tab_main_tests", body)


def table_b():
    B = load("B")
    order = ["LP-Round", PRIMARY, "PC-MALNS [BCRM-Greedy]", "Greedy-Efficiency-Portfolio", "Opt-Rollback",
             "Opt-SeqLock", "HiGHS (1T, wall-matched)", "HiGHS (4T, wall-matched)", "HiGHS (1T, CPU-matched)",
             "HiGHS (30s)"]
    blocks = []
    tests = {}
    for P in (20, 40):
        b = B[B.P == P]
        g = scale_means(b, scales=["Medium", "Large", "X-Large", "XXL"])
        pi = scale_means(b[b.family != "Deterministic"], "primal_integral", scales=["Medium", "Large", "X-Large", "XXL"])
        C = compare(wide(b), PRIMARY, [m for m in order if m != PRIMARY], f"B{P}").set_index("method")
        tests[P] = C
        rows = [rf"\multicolumn{{9}}{{@{{}}l}}{{\textit{{$P = {P}$}}}} \\"]
        for m in order:
            c = [f(g.loc[s, m]) for s in g.index]
            pic = f(pi.loc["All", m], 3) if m in pi and np.isfinite(pi.loc["All", m]) else "--"
            if m in C.index:
                r = C.loc[m]
                st = f"{fd(r['diff'])} & {r['wins']}/{r['ties']}/{r['losses']} & {fp(r['p_holm'])}"
            else:
                st = "& &"
            rows.append(tt(m) + " & " + " & ".join(c) + f" & {pic} & {st}" r" \\")
        blocks.append("\n".join(rows))
    body = (r"\begin{table}[!htb]" "\n" r"\centering" "\n"
            r"\caption{Rich candidate pools ($P \in \{20, 40\}$, 10 test instances per scale and $P$): mean "
            r"gap (\%) per scale and over all 40 instances (All), mean primal integral (PI), and the pooled "
            r"comparison of PC-MALNS [MC-CRIP] with each method (Diff in percentage points, W/T/L, exact Wilcoxon "
            r"$p$ Holm-adjusted within each $P$). Wall-clock budgets as in Table~\ref{tab:main}; HiGHS (30s) is the "
            r"1-thread reference run.}" "\n"
            r"\label{tab:rich}" "\n" r"\footnotesize" "\n" r"\resizebox{\textwidth}{!}{"
            r"\begin{tabular}{@{}lrrrrrrrrr@{}}" "\n" r"\toprule" "\n"
            r"Method & Medium & Large & X-Large & XXL & All & PI & Diff & W/T/L & $p_{\text{Holm}}$ \\" "\n"
            r"\midrule" "\n" + "\n\\midrule\n".join(blocks).replace(r"\multicolumn{9}", r"\multicolumn{10}") + "\n"
            r"\bottomrule" "\n" r"\end{tabular}}" "\n" r"\end{table}" "\n")
    write("tab_rich", body)


def table_c():
    A = load("A")
    parts = [("LP-Round start", A[A.scale.isin(["Medium", "Large"]) & (A.family == "LNS")]),
             ("Direct start", load("C_direct")), ("RPA-SH-Sync", load("C_sync"))]
    rules = [PRIMARY, "PC-MALNS [BCRM-Greedy]", "Greedy-Efficiency-Portfolio", "Greedy-Gain-Portfolio",
             "Opt-Rollback-Portfolio", "Opt-SeqLock-Portfolio", "Opt-Rollback", "Opt-SeqLock"]
    cols = []
    cfs = []
    for label, d in parts:
        d = d[d.method.isin(rules) & (d.family == "LNS")]
        W = wide(d)
        C = compare(W, PRIMARY, [m for m in rules if m != PRIMARY], label).set_index("method")
        cr = per_instance(d, "conflict_rate_pct").groupby("method").conflict_rate_pct.mean()
        cols.append((label, W.mean(), cr, C))
        cfs.append(counterfactual(d, label))
    rows = []
    for m in rules:
        cells = []
        for label, g, cr, C in cols:
            if m == PRIMARY:
                cells.append(f"{f(g[m])} & {f(cr[m], 1)} & & ")
            else:
                r = C.loc[m]
                cells.append(f"{f(g[m])} & {f(cr[m], 1)} & {fd(r['diff'])} & {r['wins']}/{r['ties']}/{r['losses']}"
                             + ("$^{*}$" if r["p_holm"] < 0.05 else ""))
        rows.append(tt(m) + " & " + " & ".join(cells) + r" \\")
    body = (r"\begin{table}[!htb]" "\n" r"\centering" "\n"
            r"\caption{Commit-rule isolation (Medium and Large, 20 test instances per regime, 5 runs per "
            r"instance). All rules see the same workers and operators; the portfolio rules see the same four-level "
            r"portfolio. Gap: mean gap (\%); Conf.: share of epochs in which the cheapest levels do not fit (\%); "
            r"Diff: PC-MALNS [MC-CRIP] $-$ rule (percentage points; negative favours MC-CRIP); W/T/L of "
            r"PC-MALNS [MC-CRIP]; $^{*}$: exact Wilcoxon $p < 0.05$ after Holm adjustment within the regime.}" "\n"
            r"\label{tab:commit}" "\n" r"\footnotesize" "\n" r"\resizebox{\textwidth}{!}{"
            r"\begin{tabular}{@{}l" + "rrrr" * 3 + r"@{}}" "\n" r"\toprule" "\n"
            r" & \multicolumn{4}{c}{LP-Round start} & \multicolumn{4}{c}{Direct start} & "
            r"\multicolumn{4}{c}{RPA-SH-Sync (LP-Round start)} \\" "\n"
            r"\cmidrule(lr){2-5}\cmidrule(lr){6-9}\cmidrule(l){10-13}" "\n"
            r"Rule & Gap & Conf. & Diff & W/T/L & Gap & Conf. & Diff & W/T/L & Gap & Conf. & Diff & W/T/L \\" "\n"
            r"\midrule" "\n" + "\n".join(rows) + "\n" r"\bottomrule" "\n" r"\end{tabular}}" "\n" r"\end{table}" "\n")
    write("tab_commit", body)

    cf = pd.concat(cfs)
    rr = ["BCRM-Greedy", "Greedy-Efficiency", "Greedy-Gain", "Opt-SeqLock", "Opt-Rollback", "Static-Quota"]
    rows = []
    for rule in rr:
        cells = []
        for label, *_ in cols:
            x = cf[(cf.regime == label) & (cf.rule == rule)].iloc[0]
            cells.append(f"{f(x.share_of_mccrip_gain_pct, 1)} & {f(x.mccrip_strictly_better_pct, 1)}")
        rows.append(rule + " & " + " & ".join(cells) + r" \\")
    n = [int(cf[cf.regime == label].conflict_epochs.iloc[0]) for label, *_ in cols]
    body = (r"\begin{table}[!htb]" "\n" r"\centering" "\n"
            r"\caption{Counterfactual barrier analysis. On every conflict epoch of the PC-MALNS [MC-CRIP] runs of "
            r"Table~\ref{tab:commit} (" + f"{n[0]:,}, {n[1]:,} and {n[2]:,}" + r" epochs, " f"{sum(n):,}"
            r" in total), every rule is applied to the same portfolios. Share: total cost reduction of the rule as "
            r"a percentage of the MC-CRIP reduction; Strict: percentage of these epochs in which MC-CRIP is strictly "
            r"better. Counterfactual evaluations use their own random stream and are not charged to any clock.}" "\n"
            r"\label{tab:counterfactual}" "\n" r"\footnotesize" "\n"
            r"\begin{tabular}{@{}lrrrrrr@{}}" "\n" r"\toprule" "\n"
            r" & \multicolumn{2}{c}{LP-Round start} & \multicolumn{2}{c}{Direct start} & "
            r"\multicolumn{2}{c}{RPA-SH-Sync} \\" "\n"
            r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(l){6-7}" "\n"
            r"Rule & Share & Strict & Share & Strict & Share & Strict \\" "\n"
            r"\midrule" "\n" + "\n".join(rows) + "\n" r"\bottomrule" "\n" r"\end{tabular}" "\n" r"\end{table}" "\n")
    write("tab_counterfactual", body)


def table_diag():
    p = RAW / "diag_slack.csv"
    if not p.exists():
        return
    d = pd.read_csv(p)
    d["acc_per_epoch"] = d.accepted_moves / d.epochs_run
    d["conf_pct"] = 100 * d.conflict_epochs / d.epochs_run
    agg = d.groupby(["init_mode", "instance_name", "method"], as_index=False)[
        ["gap_pct", "mean_slack", "mean_bottleneck_slack", "epochs_run", "acc_per_epoch", "conf_pct"]].mean()
    t = agg.groupby(["init_mode", "method"])[["gap_pct", "mean_slack", "mean_bottleneck_slack", "epochs_run",
                                              "acc_per_epoch", "conf_pct"]].mean()
    rows = []
    for init, lab in (("lp_round", "LP-Round start"), ("direct", "Direct start")):
        rows.append(rf"\multicolumn{{7}}{{@{{}}l}}{{\textit{{{lab}}}}} \\")
        for m in [PRIMARY, "PC-MALNS [BCRM-Greedy]", "Greedy-Efficiency-Portfolio"]:
            x = t.loc[(init, m)]
            rows.append(f"{tt(m)} & {f(x.gap_pct, 3)} & {f(100 * x.mean_slack, 2)} & "
                        f"{f(100 * x.mean_bottleneck_slack, 3)} & {f(x.epochs_run, 1)} & {f(x.acc_per_epoch, 2)} & "
                        f"{f(x.conf_pct, 1)}" r" \\")
    body = (r"\begin{table}[!htb]" "\n" r"\centering" "\n"
            r"\caption{Residual hub slack along the trajectory (Medium and Large, 20 test instances, 5 runs each; "
            r"separate diagnostic runs with the budgets of Table~\ref{tab:commit}). Slack: time average over the "
            r"epochs of $\frac{1}{m}\sum_r s_r^{(t)}/d_r$ (\%); Bottleneck: time average of $\min_r s_r^{(t)}/d_r$ "
            r"(\%); Acc./epoch: committed improving worker moves per epoch; Conf.: conflict epochs (\%).}" "\n"
            r"\label{tab:slack}" "\n" r"\footnotesize" "\n"
            r"\begin{tabular}{@{}lrrrrrr@{}}" "\n" r"\toprule" "\n"
            r"Rule & Gap & Slack & Bottleneck & Epochs & Acc./epoch & Conf. \\" "\n"
            r"\midrule" "\n" + "\n".join(rows) + "\n" r"\bottomrule" "\n" r"\end{tabular}" "\n" r"\end{table}" "\n")
    write("tab_slack", body)


def table_d():
    D = load("D_mmkp")
    order = [PRIMARY, "PC-MALNS [BCRM-Greedy]", "Opt-Rollback", "Opt-SeqLock", "Static-Quota",
             "HiGHS (1T, wall-matched)", "HiGHS (4T, wall-matched)", "HiGHS (60s)"]
    D = D.copy()
    D["set"] = np.where(D.mmkp.str.startswith("INST"), "INST", "I")
    gi = D.groupby(["instance_name", "set", "method"], as_index=False).agg(
        gap=("gap_bks_pct", "mean"), feas=("mmkp_feasible", "mean"), conf=("conflict_rate_pct", "mean"))
    W = gi.pivot(index="instance_name", columns="method", values="gap")
    C = compare(W, PRIMARY, [m for m in order if m != PRIMARY], "D").set_index("method")
    rows = []
    for m in order:
        g = gi[gi.method == m]
        cells = [f(g[g.set == "I"].gap.mean(), 3), f(g[g.set == "INST"].gap.mean(), 3), f(g.gap.mean(), 3),
                 f(100 * g.feas.mean(), 1), f(g.conf.mean(), 2) if g.conf.notna().any() else "--"]
        if m in C.index:
            r = C.loc[m]
            cells += [fd(r["diff"]), f"{r['wins']}/{r['ties']}/{r['losses']}", fp(r["p_holm"])]
        else:
            cells += ["", "", ""]
        rows.append(tt(m) + " & " + " & ".join(cells) + r" \\")
    body = (r"\begin{table}[!htb]" "\n" r"\centering" "\n"
            r"\caption{Public MMKP benchmarks (I07--I13 and INST01--INST20, groups split over $K = 8$ "
            r"agents; 2 s wall clock on $W = 4$ processes; 5 runs per instance). Gap to the best known solution "
            r"(\%, MMKP-feasible runs only), share of MMKP-feasible runs (\%), conflict epochs (\%), and the "
            r"comparison of PC-MALNS [MC-CRIP] with each method (26 instances with a feasible start; Holm-adjusted "
            r"exact Wilcoxon).}" "\n"
            r"\label{tab:mmkp}" "\n" r"\footnotesize" "\n" r"\resizebox{\textwidth}{!}{"
            r"\begin{tabular}{@{}lrrrrrrrr@{}}" "\n" r"\toprule" "\n"
            r"Method & I07--I13 & INST01--20 & All & Feasible & Conf. & Diff & W/T/L & $p_{\text{Holm}}$ \\" "\n"
            r"\midrule" "\n" + "\n".join(rows) + "\n" r"\bottomrule" "\n" r"\end{tabular}}" "\n" r"\end{table}" "\n")
    write("tab_mmkp", body)


def table_e():
    E, A, Ab = load("E_sweep"), load("A"), load("E_ablation")
    d = pd.concat([E, A[(A.scale == "Large") & A.method.isin(set(E.method))]])
    pi = d.groupby(["instance_name", "eta", "method"], as_index=False).gap_pct.mean()
    t = pi.groupby(["eta", "method"]).gap_pct.mean().unstack("method")
    order = ["LP-Round", PRIMARY, "PC-MALNS [BCRM-Greedy]", "Greedy-Efficiency-Portfolio", "Opt-Rollback",
             "Opt-SeqLock", "Static-Quota", "HiGHS (1T, wall-matched)", "HiGHS (1T, CPU-matched)"]
    rows = [tt(m) + " & " + " & ".join(f(t.loc[e, m]) for e in t.index) + r" \\" for m in order]
    body = (r"\begin{table}[!htb]" "\n" r"\centering" "\n"
            r"\caption{Coupling tightness sweep (Large, 10 test instances per $\eta$; $\eta = 1.25$ from "
            r"Table~\ref{tab:main}): mean gap (\%).}" "\n"
            r"\label{tab:sweep}" "\n" r"\footnotesize" "\n"
            r"\begin{tabular}{@{}lrrrr@{}}" "\n" r"\toprule" "\n"
            r"Method & " + " & ".join(rf"$\eta = {e:.2f}$" for e in t.index) + r" \\" "\n"
            r"\midrule" "\n" + "\n".join(rows) + "\n" r"\bottomrule" "\n" r"\end{tabular}" "\n" r"\end{table}" "\n")
    write("tab_sweep", body)

    base = A[(A.scale == "Large") & (A.method == PRIMARY)]
    W = wide(pd.concat([base, Ab]))
    C = compare(W, PRIMARY, [m for m in W.columns if m != PRIMARY], "abl")
    def lab(m):
        inner = m.split("; ", 1)[1].rstrip("]")
        prices = {"prices=none": "no prices", "prices=heuristic": "heuristic prices",
                  "prices=mccrip_lp": "MC-CRIP LP duals"}[inner.split(", ")[0]]
        quota = inner.split(", ")[1].replace("quota=", "") + " quota"
        return (prices + ", " + quota)[0].upper() + (prices + ", " + quota)[1:]
    rows = [f"No prices, static quota (default) & {f(W[PRIMARY].mean(), 3)} & & & " r"\\"]
    for r in C.itertuples():
        rows.append(f"{lab(r.method)} & {f(r.method_mean, 3)} & {fd(r.diff)} & "
                    f"{r.wins}/{r.ties}/{r.losses} & {fp(r.p_holm)}" r" \\")
    body = (r"\begin{table}[!htb]" "\n" r"\centering" "\n"
            r"\caption{Price and quota ablation of PC-MALNS [MC-CRIP] (Large, $\eta = 1.25$, 10 test instances, 5 "
            r"runs each): mean gap (\%), difference default $-$ variant, W/T/L of the default, exact Wilcoxon $p$ "
            r"Holm-adjusted over the six variants.}" "\n"
            r"\label{tab:ablation}" "\n" r"\footnotesize" "\n"
            r"\begin{tabular}{@{}lrrrr@{}}" "\n" r"\toprule" "\n"
            r"Variant & Gap & Diff & W/T/L & $p_{\text{Holm}}$ \\" "\n"
            r"\midrule" "\n" + "\n".join(rows) + "\n" r"\bottomrule" "\n" r"\end{tabular}" "\n" r"\end{table}" "\n")
    write("tab_ablation", body)

    s = pd.read_csv(RAW / "parameter_sensitivity_summary.csv")
    names = {"M": r"Chained steps $M$", "destroy": "Destroy fraction range", "noise": r"Regret-2 noise $\sigma$",
             "rho0": r"Borrower penalty $\rho_0$"}
    rows = []
    for fac in ["M", "destroy", "noise", "rho0"]:
        g = s[s.factor == fac]
        vals = []
        for r in g.itertuples():
            v = r.value.replace("(", "[").replace(")", "]")
            txt = f"{v}: {f(r.mean_gap, 3)}"
            if r.is_default:
                txt = r"\textbf{" + txt + "}"
            else:
                txt += f" ({fp(r.p_holm)})"
            vals.append(txt)
        rows.append(names[fac] + " & " + "; ".join(vals) + r" \\")
    body = (r"\begin{table}[!htb]" "\n" r"\centering" "\n"
            r"\caption{Parameter sensitivity on the validation seeds 1--10 (Medium, 3 runs each, 2 s CPU budget, "
            r"one factor at a time around the default in bold): level: mean gap (\%) (Holm-adjusted exact Wilcoxon "
            r"$p$ against the default over 30 paired runs). A level would replace the default only if it were better "
            r"with $p_{\text{Holm}} < 0.05$; no level qualified.}" "\n"
            r"\label{tab:tuning}" "\n" r"\footnotesize" "\n"
            r"\begin{tabular}{@{}lp{0.72\textwidth}@{}}" "\n" r"\toprule" "\n"
            r"Factor & Levels \\" "\n" r"\midrule" "\n" + "\n".join(rows) + "\n"
            r"\bottomrule" "\n" r"\end{tabular}" "\n" r"\end{table}" "\n")
    write("tab_tuning", body)

    S = load("E_scaling")
    t = S.groupby(["scale", "mode", "workers_W"], as_index=False).agg(
        wall=("wall_clock_s", "mean"), sp=("speedup_vs_serial", "mean"), same=("same_obj_as_serial", "all"))
    rows = []
    for scale in ["Large", "XXL"]:
        x = t[t.scale == scale]
        ser = x[x["mode"] == "serial"].iloc[0]
        cells = [f"{f(ser.wall)}"]
        for W in (1, 2, 4, 8):
            y = x[(x["mode"] == "pool") & (x.workers_W == W)].iloc[0]
            cells.append(f"{f(y.wall)} ({f(y.sp)}$\\times$)")
        rows.append(f"{scale} & " + " & ".join(cells) + r" \\")
    body = (r"\begin{table}[!htb]" "\n" r"\centering" "\n"
            r"\caption{Measured wall clock (s) of PC-MALNS [MC-CRIP] for a fixed number of epochs (Large: 40, XXL: 20; "
            r"seeds 101--103), serial in one process and on $W$ worker processes (speedup against serial). Every "
            r"run gives the same final objective as the serial run. Jobs were run one at a time on an Apple M4 "
            r"(4 performance and 6 efficiency cores).}" "\n"
            r"\label{tab:scaling}" "\n" r"\footnotesize" "\n"
            r"\begin{tabular}{@{}lrrrrr@{}}" "\n" r"\toprule" "\n"
            r"Scale & Serial & $W = 1$ & $W = 2$ & $W = 4$ & $W = 8$ \\" "\n" r"\midrule" "\n"
            + "\n".join(rows) + "\n" r"\bottomrule" "\n" r"\end{tabular}" "\n" r"\end{table}" "\n")
    write("tab_scaling", body)


if __name__ == "__main__":
    for fn in (table_a, table_b, table_c, table_diag, table_d, table_e):
        fn()
