"""
LaTeX tables of the manuscript (revision 3), written to paper/tables/tab_*.tex from
results/tables/summary.json (scripts/analyze_revision3.py) and, for the tuning, scaling
and lower-bound tables, from results/raw/.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "results" / "raw"
OUT = REPO_ROOT / "paper" / "tables"
S = json.loads((REPO_ROOT / "results" / "tables" / "summary.json").read_text())
SC = ["Small", "Medium", "Large", "X-Large", "XXL", "XXXL"]
PRIMARY = "PC-MALNS [Greedy-Efficiency]"
ORACLE = "PC-MALNS [MC-CRIP]"
QS = "PC-MALNS [Quota-Surplus]"
GG = "PC-MALNS [Greedy-Gain]"
OPT = ["Opt-Rollback-Portfolio", "Opt-SeqLock-Portfolio", "Opt-Rollback", "Opt-SeqLock"]


def tt(m):
    return r"\textbf{" + m + "}" if m == PRIMARY else m


def f(v, nd=2):
    return "--" if v is None or not np.isfinite(v) else f"{v:.{nd}f}"


def fp(p):
    return r"$<$0.0001" if p < 1e-4 else f"{p:.4f}"


def fd(v, nd=3):
    return "--" if v is None or not np.isfinite(v) else f"{v:+.{nd}f}".replace("-", "$-$")


def wtl(r):
    return f"{r['wins']}/{r['ties']}/{r['losses']}"


def table(name, caption, label, colspec, head, rows, size=r"\footnotesize"):
    body = (r"\begin{table}[!htb]" "\n" r"\centering" "\n" r"\caption{" + caption + "}\n"
            r"\label{" + label + "}\n" + size + "\n" r"\begin{tabular}{" + colspec + "}\n" r"\toprule" "\n"
            + head + "\n" r"\midrule" "\n" + "\n".join(rows) + "\n" r"\bottomrule" "\n" r"\end{tabular}" "\n"
            r"\end{table}" "\n")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.tex").write_text(body)
    print("wrote", name)


def get(d, m, s):
    return (d.get(m) or {}).get(s)


def hl(m):
    return m.replace("HiGHS+LP-Round", r"HiGHS\,+\,LP-Round")


# ---------------------------------------------------------------------------
def tab_main():
    M = S["main_work"]
    g, T = M["gap"], M["tests"]
    order = ["LP-Round", PRIMARY, ORACLE, QS, GG] + OPT + ["Static-Quota", "Demand-Quota"]
    rows = []
    for m in order:
        if m in (ORACLE, "Opt-Rollback-Portfolio", "Static-Quota"):
            rows.append(r"\addlinespace")
        cells = [f(get(g, m, s)) for s in SC + ["All"]]
        cells += [fd(T[m]["diff"]), wtl(T[m]), fp(T[m]["p_holm"])] if m in T else ["", "", ""]
        rows.append(tt(m) + " & " + " & ".join(cells) + r" \\")
    ep = M["epochs"]
    table("tab_main",
          r"Main benchmark under the work protocol ($J = 6$, $\eta = 1.25$, 10 test instances per scale, 5 runs "
          r"per instance): mean gap to the lower bound (\%) and pooled comparison with " + PRIMARY + r" over the "
          r"60 instances. Diff $=$ " + PRIMARY + r" $-$ method (percentage points; negative favours "
          + PRIMARY + r"); W/T/L: instances on which " + PRIMARY + r" is better, equal or worse; $p_{\text{Holm}}$: "
          r"exact two-sided Wilcoxon signed-rank test, Holm-adjusted over the " + str(len(T)) + r" comparisons. Every four-level "
          r"method runs " + ", ".join(str(int(get(ep, PRIMARY, s))) for s in SC) + r" epochs (Small to XXXL), every "
          r"single-proposal method " + ", ".join(str(int(get(ep, "Opt-Rollback", s))) for s in SC)
          + r"; all use the same number of repair passes.",
          "tab:main", r"@{}l" + "r" * 10 + r"@{}",
          r"Method & Small & Medium & Large & X-Large & XXL & XXXL & All & Diff & W/T/L & $p_{\text{Holm}}$ \\",
          rows, r"\scriptsize")


def tab_barrier():
    M, Wm = S["main_work"], S["wall_main"]
    rows = []
    for s in SC:
        rows.append(f"{s} & {f(get(M['conflict_pct'], PRIMARY, s), 1)} & {f(get(M['conflict_pct'], ORACLE, s), 1)} & "
                    f"{f(get(M['barrier_ms'], PRIMARY, s))} & {f(get(M['barrier_ms'], ORACLE, s), 1)} & "
                    f"{f(get(Wm['epochs'], PRIMARY, s), 1)} & {f(get(Wm['epochs'], ORACLE, s), 1)} & "
                    f"{f(get(Wm['epochs'], 'Opt-Rollback', s), 1)}" r" \\")
    table("tab_barrier",
          r"Epochs and barrier time per scale. Work protocol: share of conflict epochs (\%) and mean barrier time "
          r"per conflict epoch (ms) of " + PRIMARY + r" (GE) and " + ORACLE + r" (MC); the number of epochs is "
          r"fixed by the budget. Wall-clock protocol (Section~\ref{sec:solver}): mean epochs reached within the "
          r"budget by GE, MC and the single-proposal \texttt{Opt-Rollback} (OR).",
          "tab:barrier", r"@{}lrrrrrrr@{}",
          r" & \multicolumn{4}{c}{Work protocol} & \multicolumn{3}{c}{Wall-clock protocol} \\" "\n"
          r"\cmidrule(lr){2-5}\cmidrule(l){6-8}" "\n"
          r"Scale & Conf.\ GE & Conf.\ MC & ms GE & ms MC & Epochs GE & Epochs MC & Epochs OR \\",
          rows)


def tab_validation():
    V = S.get("validation")
    if not V:
        return
    g, T = V["gap"], V["tests"]
    rows = []
    for m in (PRIMARY, ORACLE, QS):
        cells = [f(get(g, m, s), 3) for s in SC + ["All"]]
        cells += [fd(T[m]["diff"]), wtl(T[m]), fp(T[m]["p"]), fp(T[m]["p_holm"])] if m in T else ["", "", "", ""]
        rows.append(tt(m) + " & " + " & ".join(cells) + r" \\")
    table("tab_validation",
          r"Fresh validation on 60 new instances (seeds 201--210, all six scales, $J = 6$, $\eta = 1.25$; work "
          r"protocol, 5 runs each), declared before the runs (\texttt{results/validation\_plan.md}). Gap to the LP "
          r"bound (\%). Diff $=$ " + PRIMARY + r" $-$ method; $p$: exact Wilcoxon (primary test: against "
          + ORACLE + r"); $p_{\text{Holm}}$ over the two tests.",
          "tab:validation", r"@{}l" + "r" * 11 + r"@{}",
          r"Method & Small & Medium & Large & X-Large & XXL & XXXL & All & Diff & W/T/L & $p$ & $p_{\text{Holm}}$ \\",
          rows, r"\scriptsize")


REG = ["LP-Round start", "Direct start", "MCA-SC-Pair"]
REGH = (r" & \multicolumn{2}{c}{LP-Round start} & \multicolumn{2}{c}{Direct start} & "
        r"\multicolumn{2}{c}{MCA-SC-Pair} \\" "\n" r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(l){6-7}" "\n")


def tab_commit():
    C = S["commit"]
    rules = [PRIMARY, ORACLE, QS, GG] + OPT
    rows = []
    for m in rules:
        cells = [f"{f(get(C[r]['gap'], m, 'All'), 3)} & {f(get(C[r]['conflict'], m, 'All'), 1)}" for r in REG]
        rows.append(tt(m) + " & " + " & ".join(cells) + r" \\")
    table("tab_commit",
          r"Commit-rule isolation under the work protocol (Medium and Large, 20 test instances per regime, 5 runs "
          r"each): mean gap (\%) and share of conflict epochs (Conf., \%). The \texttt{LP-Round} regime is the "
          r"Medium and Large subset of Table~\ref{tab:main}; the direct start puts every request on $p = 0$ and "
          r"so disables the warm start; MCA-SC-Pair uses the \texttt{LP-Round} start.",
          "tab:commit", r"@{}lrrrrrr@{}", REGH + r"Rule & Gap & Conf. & Gap & Conf. & Gap & Conf. \\", rows)
    rows = []
    for m in rules[1:]:
        cells = []
        for r in REG:
            t = C[r]["tests"][m]
            cells.append(f"{fd(t['diff'])} & {wtl(t)}" + ("$^{*}$" if t["p_holm"] < 0.05 else ""))
        rows.append(m + " & " + " & ".join(cells) + r" \\")
    table("tab_commit_tests",
          r"Commit-rule isolation: " + PRIMARY + r" against each rule per regime (Table~\ref{tab:commit}). Diff "
          r"$=$ " + PRIMARY + r" $-$ rule (percentage points; negative favours " + PRIMARY + r"); W/T/L over the "
          r"20 instances; $^{*}$: exact Wilcoxon $p < 0.05$ after Holm adjustment over all 21 comparisons.",
          "tab:commit_tests", r"@{}lrrrrrr@{}", REGH + r"Rule & Diff & W/T/L & Diff & W/T/L & Diff & W/T/L \\", rows)


def tab_counterfactual():
    cf = pd.DataFrame(S["counterfactual"])
    rr = ["Greedy-Efficiency", "Quota-Surplus", "Greedy-Gain", "Opt-SeqLock", "Opt-Rollback", "Static-Quota"]
    rows = []
    for rule in rr:
        cells = []
        for r in REG:
            x = cf[(cf.regime == r) & (cf.rule == rule)].iloc[0]
            cells.append(f"{f(x.share_of_mccrip_gain_pct, 1)} & {f(x.mccrip_strictly_better_pct, 1)}")
        rows.append(rule + " & " + " & ".join(cells) + r" \\")
    n = [int(cf[cf.regime == r].conflict_epochs.iloc[0]) for r in REG]
    table("tab_counterfactual",
          r"Counterfactual barrier analysis. On every conflict epoch of the " + ORACLE + r" runs of "
          r"Table~\ref{tab:commit} (" + f"{n[0]:,}, {n[1]:,} and {n[2]:,}" + r" epochs), every rule is applied to "
          r"the same portfolios. Share: total cost reduction of the rule as a percentage of the MC-CRIP reduction; "
          r"Strict: percentage of these epochs in which MC-CRIP is strictly better. Counterfactual evaluations use "
          r"their own random stream and do not change the run.",
          "tab:counterfactual", r"@{}lrrrrrr@{}", REGH + r"Rule & Share & Strict & Share & Strict & Share & Strict \\",
          rows)


def tab_slack():
    rows = []
    for x in S["slack"]:
        rows.append(rf"\multicolumn{{5}}{{@{{}}l}}{{\textit{{{x['regime']}}}}} \\")
        for m, k in ((PRIMARY, "primary"), (ORACLE, "oracle"), (QS, "qs")):
            bott = f(x[f"bott_{k}"], 3) if f"bott_{k}" in x else "--"
            rows.append(f"{tt(m)} & {f(x[f'gap_{k}'], 3)} & {f(x[f'slack_{k}'], 2)} & {bott} & "
                        f"{f(x[f'acc_{k}'], 2)}" r" \\")
    table("tab_slack",
          r"Residual slack along the trajectory (Medium and Large, 20 test instances, 5 runs each; the runs of "
          r"Table~\ref{tab:commit}). Slack: time average over the epochs of $\frac{1}{m}\sum_r s_r^{(t)}/d_r$ (\%); "
          r"Bottleneck: time average of $\min_r s_r^{(t)}/d_r$ (\%); Acc./epoch: committed improving worker moves "
          r"per epoch.",
          "tab:slack", r"@{}lrrrr@{}", r"Rule & Gap & Slack & Bottleneck & Acc./epoch \\", rows)


def _ablation_rows(key, labels):
    A = S[key]
    rows = [f"{labels[PRIMARY]} & {f(get(A['gap'], PRIMARY, 'All'), 3)} & & & " r"\\"]
    for m, t in A["tests"].items():
        rows.append(f"{labels.get(m, m)} & {f(t['method_mean'], 3)} & {fd(t['diff'])} & {wtl(t)} & "
                    f"{fp(t['p_holm'])}" r" \\")
    return rows


def _rho0_row():
    R = S["rho0"]
    t = R["tests"][R["method"]]
    return (r"All levels, $\rho_0 = 0$ in level $2$ & " + f"{f(t['method_mean'], 3)} & {fd(t['diff'])} & {wtl(t)} & "
            f"{fp(t['p_holm'])}$^{{\\dagger}}$" r" \\")


def tab_levels():
    if "levels" not in S:
        return
    lab = {PRIMARY: r"$\{0,1,2,3\}$ (all levels, default)"}
    for m in S["levels"]["tests"]:
        lab[m] = "$" + m.split("levels ")[1].replace("{", r"\{").replace("}", r"\}") + "$"
    table("tab_levels",
          r"Portfolio-level ablation of " + PRIMARY + r" (work protocol, all 60 instances of Table~\ref{tab:main}, "
          r"5 runs each). A level that is not generated is replaced by the incumbent; without level $0$ no donor "
          r"rebalance is tried. Every variant uses the same number of repair passes, so variants without level $2$ "
          r"run 25\% more epochs. Diff $=$ default $-$ variant (pp); W/T/L of the default; exact Wilcoxon $p$ "
          r"Holm-adjusted over the three variants. $^{\dagger}$Separate test: level $2$ without its quadratic "
          r"penalty ($\rho_t = 0$), unadjusted $p$.",
          "tab:levels", r"@{}lrrrr@{}", r"Generated levels & Gap & Diff & W/T/L & $p_{\text{Holm}}$ \\",
          _ablation_rows("levels", lab) + [r"\addlinespace", _rho0_row()])


def tab_prices():
    if "prices" not in S:
        return
    lab = {PRIMARY: "No prices, static quota (default)"}
    pn = {"none": "no prices", "heuristic": "heuristic prices", "mccrip_lp": "MC-CRIP LP duals"}
    for m in S["prices"]["tests"]:
        pr, qu = m.split("prices=")[1].split(", quota=")
        s = f"{pn[pr]}, {qu} quota"
        lab[m] = s[0].upper() + s[1:]
    rows = [r"\multicolumn{5}{@{}l}{\textit{Test instances (seeds 101--110)}} \\"] + _ablation_rows("prices", lab)
    F = S["prices_fresh"]
    t = F["tests"][F["method"]]
    rows += [r"\multicolumn{5}{@{}l}{\textit{Fresh instances (seeds 301--310), declared test, gap to the LP bound}} \\",
             f"{lab[PRIMARY]} & {f(get(F['gap'], PRIMARY, 'All'), 3)} & & & " r"\\",
             f"{lab[F['method']]} & {f(t['method_mean'], 3)} & {fd(t['diff'])} & {wtl(t)} & {fp(t['p'])}" r" \\"]
    table("tab_prices",
          r"Price and quota ablation of " + PRIMARY + r" (work protocol, 60 instances per block, 5 runs each): mean "
          r"gap (\%), Diff $=$ default $-$ variant (pp; positive: the variant is better), W/T/L of the default, exact "
          r"Wilcoxon $p$, Holm-adjusted over the six variants on the test instances. The fresh block repeats the best "
          r"variant on 60 new instances under the plan \texttt{results/price\_plan.md}, committed before the runs.",
          "tab:prices", r"@{}lrrrr@{}", r"Variant & Gap & Diff & W/T/L & $p$ \\", rows)


def tab_dynamics():
    st, sw, R = S.get("stall", {}), S.get("stall_wall", {}), S.get("restart")
    if not st or not R:
        return
    nm = list(R["tests"])[0]
    rows = []
    for s in SC + ["All"]:
        if s == "All":
            t95, last, lw = st[PRIMARY]["t95_mean"], st[PRIMARY]["last_mean"], sw["last_mean"]
        else:
            t95, last, lw = st[PRIMARY]["t95_by_scale"][s], st[PRIMARY]["last_by_scale"][s], sw["last_by_scale"][s]
        rows.append(f"{s} & {f(t95)} & {f(last)} & {f(lw)} & {f(get(R['gap'], PRIMARY, s), 3)} & "
                    f"{f(get(R['gap'], nm, s), 3)} & {f(get(R['restarts_per_run'], nm, s), 1)}" r" \\")
    t = R["tests"][nm]
    table("tab_dynamics",
          r"Search dynamics of " + PRIMARY + r". Stall: fraction of the epoch budget after which a run has reached "
          r"95\% of its total improvement ($t_{95}$) and made its last improvement (Last), from run 0 of every "
          r"instance under the work protocol; Last (wall): the same under the wall-clock protocol, as a fraction of "
          r"the time budget. Restarts: mean gap without and with restarts (a perturbation of the best solution "
          r"after 5 epochs without a new best) and restarts per run. Over the 60 instances the default is better "
          r"on " + str(t["wins"]) + r", equal on " + str(t["ties"]) + r" and worse on " + str(t["losses"])
          + r" instances (Diff " + fd(t["diff"]) + r" pp, exact Wilcoxon "
          + (r"$p < 10^{-4}$" if t["p"] < 1e-4 else r"$p = " + fp(t["p"]) + "$") + r").",
          "tab:dynamics", r"@{}lrrrrrr@{}",
          r" & \multicolumn{3}{c}{Stall} & \multicolumn{3}{c}{Restarts} \\" "\n"
          r"\cmidrule(lr){2-4}\cmidrule(l){5-7}" "\n"
          r"Scale & $t_{95}$ & Last & Last (wall) & Default & Restarts & Per run \\", rows)


HSOLVE = ["HiGHS (1T, wall-matched)", "HiGHS (4T, wall-matched)", "HiGHS+LP-Round (1T, wall-matched)",
          "HiGHS (1T, CPU-matched)", "HiGHS+LP-Round (1T, CPU-matched)", "HiGHS (5s)", "HiGHS (60s)", "HiGHS (600s)"]


def tab_solver():
    Wm = S["wall_main"]
    g, T = Wm["gap"], Wm["tests"]
    order = ["LP-Round", PRIMARY, ORACLE, "Opt-Rollback", "Opt-SeqLock", "Async-Lock"] + HSOLVE
    rows = []
    for m in order:
        if m in ("Opt-Rollback", HSOLVE[0]):
            rows.append(r"\addlinespace")
        cells = [f(get(g, m, s)) for s in SC]
        cells.append(f(get(g, m, "All")) + (r"$^{\dagger}$" if m == "HiGHS (600s)" else ""))
        cells += [fd(T[m]["diff"]), wtl(T[m]), fp(T[m]["p_holm"])] if m in T else ["", "", ""]
        rows.append(tt(hl(m)) + " & " + " & ".join(cells) + r" \\")
    table("tab_solver",
          r"Wall-clock protocol on the main benchmark (60 test instances; budgets 0.5, 1, 1.5, 2, 4 and 6 s on "
          r"$W = 4$ processes): mean gap (\%) and pooled comparison with " + PRIMARY + r" (Diff, W/T/L, exact "
          r"Wilcoxon $p$ Holm-adjusted over the " + str(len(T)) + r" comparisons). HiGHS 1.16.0 with one or four threads (1T, 4T); "
          r"wall-matched and CPU-matched limits are the mean wall-clock and CPU time of the five " + PRIMARY
          + r" runs; HiGHS\,+\,LP-Round receives the \texttt{LP-Round} solution as MIP start and the matched time "
          r"minus the \texttt{LP-Round} time. HiGHS (5s), (60s), (600s) and the cold CPU-matched values are read "
          r"from the incumbent trace of the reference run. $^{\dagger}$Small and Medium only (20 instances); not "
          r"included in the tests.",
          "tab:solver", r"@{}l" + "r" * 10 + r"@{}",
          r"Method & Small & Medium & Large & X-Large & XXL & XXXL & All & Diff & W/T/L & $p_{\text{Holm}}$ \\",
          rows, r"\scriptsize")


HRICH = ["HiGHS (1T, wall-matched)", "HiGHS (4T, wall-matched)", "HiGHS+LP-Round (1T, wall-matched)",
         "HiGHS (1T, CPU-matched)", "HiGHS+LP-Round (1T, CPU-matched)", "HiGHS (30s)", "HiGHS (300s)"]


def tab_rich():
    R = S["rich"]
    order = ["LP-Round", PRIMARY, ORACLE, QS, "Opt-Rollback", "Opt-SeqLock"] + HRICH
    sc = ["Medium", "Large", "X-Large", "XXL"]
    blocks = []
    for P in ("20", "40"):
        g, T = R[P]["gap"], R[P]["tests"]
        rows = [rf"\multicolumn{{9}}{{@{{}}l}}{{\textit{{$J = {P}$}}}} \\"]
        for m in order:
            cells = [f(get(g, m, s)) for s in sc + ["All"]]
            cells += [fd(T[m]["diff"]), wtl(T[m]), fp(T[m]["p_holm"])] if m in T else ["", "", ""]
            rows.append(tt(hl(m)) + " & " + " & ".join(cells) + r" \\")
        blocks.append("\n".join(rows))
    table("tab_rich",
          r"Rich candidate pools ($J \in \{20, 40\}$, 10 test instances per scale and $J$; wall-clock protocol): "
          r"mean gap (\%) and pooled comparison with " + PRIMARY + r" over the 40 instances of each $J$ (Diff, "
          r"W/T/L, exact Wilcoxon $p$ Holm-adjusted over both $J$). HiGHS 1.16.0 as in Table~\ref{tab:solver}; "
          r"the reference run has a 300 s limit, and HiGHS (5s) and (30s) are read from its trace.",
          "tab:rich", r"@{}lrrrrrrrr@{}",
          r"Method & Medium & Large & X-Large & XXL & All & Diff & W/T/L & $p_{\text{Holm}}$ \\",
          ["\n\\midrule\n".join(blocks)], r"\scriptsize")


def tab_sweep():
    Sw = S["sweep"]
    g = Sw["gap"]
    etas = sorted(g, key=float)
    order = ["LP-Round", PRIMARY, ORACLE, QS, "Opt-Rollback", "Opt-SeqLock", "Static-Quota",
             "HiGHS (1T, wall-matched)", "HiGHS+LP-Round (1T, wall-matched)", "HiGHS (1T, CPU-matched)", "HiGHS (5s)"]
    tests = {(r["family"].split("=")[1], r["method"]): r for r in Sw["tests"]}

    def cell(e, m):
        v = f(g[e].get(m))
        t = tests.get((e, m))
        if t is None or v == "--":
            return v
        return v + f" ({t['wins']}/{t['losses']})"

    rows = [tt(hl(m)) + " & " + " & ".join(cell(e, m) for e in etas) + r" \\" for m in order]
    rows.append(r"\addlinespace")
    rows.append(r"Conflict epochs of GE (\%) & " +
                " & ".join(f(Sw["conflict"][e].get(PRIMARY), 1) for e in etas) + r" \\")
    rows.append(r"Time to target / budget (median) & " +
                " & ".join(f(Sw["ttt"][e]["ratio_median"]) for e in etas) + r" \\")
    table("tab_sweep",
          r"Coupling tightness sweep (Large, 10 test instances per $\eta$, wall-clock protocol, 1.5 s; $\eta = 1.25$ "
          r"from Table~\ref{tab:solver}; \pqs{} and \texttt{Static-Quota} were not run at $\eta = 1.25$ in this "
          r"protocol): mean gap (\%) and, in parentheses, the instances on which " + PRIMARY + r" (GE) is better "
          r"and worse; share of conflict epochs of GE; median ratio of the time the HiGHS reference run needs to "
          r"reach the mean GE objective to the GE budget. With " + str(Sw["n_tests"]) + r" tests and 10 instances "
          r"per $\eta$, no comparison of the sweep is significant after Holm adjustment.",
          "tab:sweep", r"@{}l" + "r" * len(etas) + r"@{}",
          r"Method & " + " & ".join(rf"$\eta = {float(e):.2f}$" for e in etas) + r" \\", rows, r"\scriptsize")


def tab_mmkp():
    Mk = S["mmkp"]
    order = ["LP-Round", PRIMARY, ORACLE, QS, "Opt-Rollback", "Opt-SeqLock", "Static-Quota",
             "HiGHS (1T, wall-matched)", "HiGHS (4T, wall-matched)", "HiGHS (60s)"]
    rows = []
    for m in order:
        g = Mk["gap"].get(m, {})
        cells = [f(g.get("I07-I13"), 3), f(g.get("INST01-20"), 3), f(g.get("All"), 3),
                 f(Mk["feasible_pct"].get(m), 1)]
        t = Mk["tests"].get(m)
        cells += [fd(t["diff"]), wtl(t), fp(t["p_holm"])] if t else ["", "", ""]
        rows.append(tt(m) + " & " + " & ".join(cells) + r" \\")
    table("tab_mmkp",
          r"Public MMKP benchmarks (I07--I13 and INST01--INST20, groups split over $K = 8$ agents; 2 s wall clock "
          r"on $W = 4$ processes; 5 runs per instance; HiGHS 1.16.0). Gap to the best known solution (\%, "
          r"MMKP-feasible runs only), share of MMKP-feasible runs (\%), and the comparison of " + PRIMARY
          + r" with each method (Holm-adjusted exact Wilcoxon).",
          "tab:mmkp", r"@{}lrrrrrrr@{}",
          r"Method & I07--I13 & INST01--20 & All & Feasible & Diff & W/T/L & $p_{\text{Holm}}$ \\", rows,
          r"\scriptsize")


def tab_cfall():
    X = S["cf_all"]
    rules = ["MC-CRIP", "Quota-Surplus", "Greedy-Gain", "Greedy-Efficiency", "Static-Quota"]
    rows = []
    for r in rules:
        cells = []
        for m in (PRIMARY, ORACLE):
            v = X["by_trajectory"][m]
            cells.append(f"{v['deviate_epochs'][r]:,} & {f(v['deviate_pct'][r], 2)} & {f(v['loss_pct_of_gain'][r], 2)}")
        rows.append(r + " & " + " & ".join(cells) + r" \\")
    n = [X["by_trajectory"][m]["nonconflict_epochs"] for m in (PRIMARY, ORACLE)]
    table("tab_cfall",
          r"Rules in non-conflict epochs (work protocol, 60 test instances, 5 runs each; the runs of "
          r"Table~\ref{tab:main}, reproduced bit for bit with logging). In every non-conflict epoch of the "
          r"trajectories of " + PRIMARY + f" ({n[0]:,} epochs) and " + ORACLE + f" ({n[1]:,} epochs), every rule is "
          r"applied to the same portfolios. Epochs: number of epochs in which the rule commits a selection other "
          r"than the cheapest levels; Loss: cost reduction forgone against the cheapest levels, as a percentage of "
          r"the total cost reduction of the cheapest levels over these epochs.",
          "tab:cfall", r"@{}lrrrrrr@{}",
          r" & \multicolumn{3}{c}{Trajectories of GE} & \multicolumn{3}{c}{Trajectories of MC-CRIP} \\" "\n"
          r"\cmidrule(lr){2-4}\cmidrule(l){5-7}" "\n"
          r"Rule & Epochs & \% & Loss (\%) & Epochs & \% & Loss (\%) \\", rows)


def tab_time():
    Wm, R, Pw = S["wall_main"], S["rich"], S["pair_wall"]
    rows = [r"\multicolumn{6}{@{}l}{\textit{Main benchmark ($J = 6$)}} \\"]
    for s in SC:
        t, p = Wm["ttt"][s], Wm["pi"][s]
        rows.append(f"{s} & {f(t['lns_wall_median'])} & {f(t['ttt_median'])} & {f(t['ratio_median'])} & "
                    f"{f(p['pi_lns'], 3)} & {f(p['pi_highs'], 3)}" r" \\")
    rows.append(r"\multicolumn{6}{@{}l}{\textit{MCA-SC-Pair}} \\")
    for s in ("Medium", "Large"):
        t = Pw["ttt"][s]
        rows.append(f"{s} & {f(t['lns_wall_median'])} & {f(t['ttt_median'])} & {f(t['ratio_median'])} & & " r"\\")
    for J in ("20", "40"):
        rows.append(rf"\multicolumn{{6}}{{@{{}}l}}{{\textit{{Rich pools, $J = {J}$}}}} \\")
        for s in ("Medium", "Large", "X-Large", "XXL"):
            t = R["ttt_combined"][f"{J}|{s}"]
            rows.append(f"{s} & {f(t['lns_wall_median'])} & {f(t['ttt_median'])} & {f(t['ratio_median'])} & & " r"\\")
    never = sum(int(v["never"]) for v in list(Wm["ttt"].values()) + list(Pw["ttt"].values())
                + list(R["ttt_combined"].values()))
    table("tab_time",
          r"Time to target and primal integral (wall-clock protocol, medians over 10 instances). Budget: wall "
          r"clock of a " + PRIMARY + r" run; HiGHS: time the one-thread HiGHS reference run needs to reach the "
          r"mean " + PRIMARY + r" objective of the instance; Ratio: median of HiGHS time over budget (above 1: "
          r"HiGHS needs longer). The reference run reached the target on every instance (" + str(never)
          + r" misses). PI: primal integral over the budget, divided by the budget (mean; lower is better), "
          r"with primal gap 1 before the first solution. Rich pools: the 40 instances of the slow stretch use the "
          r"rerun (Section~\ref{sec:runconditions}).",
          "tab:time", r"@{}lrrrrr@{}",
          r"Scale & Budget (s) & HiGHS (s) & Ratio & PI \pge & PI HiGHS \\", rows)


def tab_rerun():
    Rr = S["rich"]["rerun"]
    meths = ["Opt-Rollback", "Opt-SeqLock", ORACLE, QS, "HiGHS (1T, wall-matched)", "HiGHS (1T, CPU-matched)",
             "HiGHS+LP-Round (1T, CPU-matched)"]
    rows = []
    for m in meths:
        a, b = Rr["tests"]["original"][m], Rr["tests"]["rerun"][m]
        rows.append(f"{hl(m)} & {fd(a['diff'])} & {wtl(a)} & {fp(a['p_holm'])} & {fd(b['diff'])} & {wtl(b)} & "
                    f"{fp(b['p_holm'])}" r" \\")
    rows.append(r"\addlinespace")
    for k, v in Rr["epochs"].items():
        J, s = k.split("|")
        rows.append(rf"Epochs of \pge, $J = {J}$, {s} & & {f(v['original'], 1)} & & & {f(v['rerun'], 1)} & " r"\\")
    table("tab_rerun",
          r"Sensitivity rerun of the " + str(Rr["n"]) + r" rich-pool instances that ran in the first slow stretch "
          r"(identical design and random orders). Comparison of " + PRIMARY + r" with each method in the original "
          r"runs and in the rerun (Diff in pp, W/T/L, exact Wilcoxon $p$ Holm-adjusted within each run), and mean "
          r"epochs of " + PRIMARY + r" per cell. The rerun itself slowed down from about its 22nd instance on "
          r"(Section~\ref{sec:runconditions}).",
          "tab:rerun", r"@{}lrrrrrr@{}",
          r" & \multicolumn{3}{c}{Original runs} & \multicolumn{3}{c}{Rerun} \\" "\n"
          r"\cmidrule(lr){2-4}\cmidrule(l){5-7}" "\n"
          r"Method & Diff & W/T/L & $p_{\text{Holm}}$ & Diff & W/T/L & $p_{\text{Holm}}$ \\", rows, r"\scriptsize")


def tab_pair():
    Pw = S["pair_wall"]
    g, T = Pw["gap"], Pw["tests"]
    order = ["LP-Round", PRIMARY, ORACLE, QS, GG] + OPT + ["HiGHS (1T, wall-matched)", "HiGHS (4T, wall-matched)",
                                                          "HiGHS+LP-Round (1T, wall-matched)", "HiGHS (1T, CPU-matched)",
                                                          "HiGHS (5s)", "HiGHS (60s)"]
    rows = []
    for m in order:
        if m in (ORACLE, "Opt-Rollback-Portfolio", "HiGHS (1T, wall-matched)"):
            rows.append(r"\addlinespace")
        cells = [f(get(g, m, s)) for s in ("Medium", "Large", "All")]
        cells += [fd(T[m]["diff"]), wtl(T[m]), fp(T[m]["p_holm"])] if m in T else ["", "", ""]
        rows.append(tt(hl(m)) + " & " + " & ".join(cells) + r" \\")
    table("tab_pair",
          r"MCA-SC-Pair under the wall-clock protocol (Medium and Large, 10 test instances each, 1 and 1.5 s on "
          r"$W = 4$ processes): mean gap (\%) and comparison with " + PRIMARY + r" (exact Wilcoxon $p$ "
          r"Holm-adjusted over the " + str(len(T)) + r" comparisons). HiGHS as in Table~\ref{tab:solver}; reference "
          r"run 60 s.",
          "tab:pair", r"@{}lrrrrrr@{}", r"Method & Medium & Large & All & Diff & W/T/L & $p_{\text{Holm}}$ \\", rows,
          r"\scriptsize")


def tab_tuning():
    s = pd.read_csv(RAW / "parameter_sensitivity_summary.csv")
    names = {"M": r"Chained steps $M$", "destroy": "Destroy fraction range", "noise": r"Regret-2 noise $\sigma$",
             "rho0": r"Borrower penalty $\rho_0$"}
    rows = []
    for fac in ["M", "destroy", "noise", "rho0"]:
        vals = []
        for r in s[s.factor == fac].itertuples():
            v = r.value.replace("(", "[").replace(")", "]")
            txt = f"{v}: {f(r.mean_gap, 3)}"
            vals.append(r"\textbf{" + txt + "}" if r.is_default else txt + f" ({fp(r.p_holm)})")
        rows.append(names[fac] + " & " + "; ".join(vals) + r" \\")
    table("tab_tuning",
          r"Parameter sensitivity, carried over from the preliminary version of this study: PC-MALNS [MC-CRIP] on "
          r"the tuning seeds 1--10 (Medium, 3 runs each, 2 s CPU budget), one factor at a time around the default "
          r"in bold: mean gap (\%) (Holm-adjusted exact Wilcoxon $p$ against the default over 30 paired runs). A "
          r"level would have replaced the default only if it were better with $p_{\text{Holm}} < 0.05$; none "
          r"qualified.",
          "tab:tuning", r"@{}lp{0.72\textwidth}@{}", r"Factor & Levels \\", rows)


def tab_scaling():
    E = pd.read_csv(RAW / "bench_E_scaling.csv")
    t = E.groupby(["scale", "mode", "workers_W"], as_index=False).agg(
        wall=("wall_clock_s", "mean"), sp=("speedup_vs_serial", "mean"))
    rows = []
    for scale in ["Large", "XXL"]:
        x = t[t.scale == scale]
        cells = [f(x[x["mode"] == "serial"].iloc[0].wall)]
        for W in (1, 2, 4, 8):
            y = x[(x["mode"] == "pool") & (x.workers_W == W)].iloc[0]
            cells.append(f"{f(y.wall)} ({f(y.sp)}$\\times$)")
        rows.append(f"{scale} & " + " & ".join(cells) + r" \\")
    table("tab_scaling",
          r"Parallel scaling, carried over from the preliminary version of this study: measured wall clock (s) of "
          r"PC-MALNS [MC-CRIP] for a fixed number of epochs (Large: 40, XXL: 20; seeds "
          r"101--103), serial in one process and on $W$ worker processes (speedup against serial). Every run gives "
          r"the same final objective as the serial run. Jobs ran one at a time on an Apple M4 (4 performance and 6 "
          r"efficiency cores).",
          "tab:scaling", r"@{}lrrrrr@{}", r"Scale & Serial & $W = 1$ & $W = 2$ & $W = 4$ & $W = 8$ \\", rows)


def tab_lb():
    L = pd.read_csv(RAW / "lower_bounds.csv")

    def code(r):
        if r.lb_source == "LP":
            k = "L"
        elif "1.8.0" in r.lb_source:
            k = "a"
        elif "reference" in r.lb_source:
            k = "b"
        else:
            k = "c"
        return k + ("$^{*}$" if r.proven_optimal else "")

    L["code"] = L.apply(code, axis=1)
    groups = []
    order = {"main": 0, "rich": 1, "sweep": 2, "pair": 3}
    lab = {"main": "Main", "rich": "Rich", "sweep": "Sweep", "pair": "Pair"}
    for (fam, P, eta, K), g in L.groupby(["family", "P", "eta", "K"]):
        name = f"{lab[fam]}, {g.scale.iloc[0]}" + (f", $J = {P}$" if fam == "rich" else "") + \
               (rf", $\eta = {eta:.2f}$" if fam == "sweep" else "")
        codes = [g[g.seed == s].code.iloc[0] if (g.seed == s).any() else "" for s in range(101, 111)]
        groups.append(((order[fam], P, eta, K), name + " & " + " & ".join(codes) + r" \\"))
    groups.sort(key=lambda x: x[0])
    table("tab_lb",
          r"Source of the lower bound LB of every test instance (seeds 101 to 110). L: LP bound; a: dual bound of "
          r"a HiGHS 1.8.0 reference run of the preliminary version; b: dual bound of the HiGHS 1.16.0 reference "
          r"run; c: dual bound of another HiGHS 1.16.0 run on the instance; $^{*}$: some run proved optimality "
          r"(none did). LB is the largest of these bounds; all values are in "
          r"\texttt{results/raw/lower\_bounds.csv}.",
          "tab:lb", r"@{}l" + "c" * 10 + r"@{}",
          "Instances & " + " & ".join(str(s) for s in range(101, 111)) + r" \\", [g[1] for g in groups],
          r"\scriptsize")


if __name__ == "__main__":
    # strict: a missing input is an error, never a silently skipped table
    for fn in (tab_main, tab_barrier, tab_validation, tab_commit, tab_counterfactual, tab_cfall, tab_slack,
               tab_levels, tab_prices, tab_dynamics, tab_solver, tab_time, tab_rich, tab_rerun, tab_sweep, tab_pair,
               tab_mmkp, tab_tuning, tab_scaling, tab_lb):
        fn()
