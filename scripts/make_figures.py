"""
Figures for the revision-2 benchmark (results/figures/*.pdf and .png, 300 dpi).
All text >= 9 pt, horizontal tick labels, a fixed categorical colour order with marker /
line-style redundancy (colour is never the only identity cue), one y-axis per panel,
acceptance-rate axis capped at 105 %.

  fig_gap_by_scale        mean gap to LB by scale (table A)
  fig_anytime             anytime curves: PC-MALNS (W = 4, run 0) vs HiGHS 1T trace
  fig_rich_pools          gap and primal integral, P = 20 / 40 (table B)
  fig_tightness           gap vs coupling tightness eta (Large)
  fig_scaling             wall-clock speedup vs W
  fig_counterfactual      share of the MC-CRIP barrier gain captured by each rule
  fig_acceptance          accepted / improving proposals by method (table A)
"""

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "results" / "raw"
FIG = REPO_ROOT / "results" / "figures"
PRIMARY = "PC-MALNS [MC-CRIP]"
SCALES = ["Small", "Medium", "Large", "X-Large", "XXL", "XXXL"]
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
MARKERS = ["o", "s", "^", "D", "v", "P", "X", "*"]
STYLES = ["-", "--", "-.", ":", "-", "--", "-.", ":"]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
# fixed entity -> slot assignment (colour follows the method, never its rank)
SLOT = {PRIMARY: 0, "PC-MALNS [BCRM-Greedy]": 1, "Greedy-Efficiency-Portfolio": 2, "Greedy-Gain-Portfolio": 3,
        "Opt-Rollback": 4, "Opt-SeqLock": 5, "HiGHS (1T, wall-matched)": 6, "HiGHS (4T, wall-matched)": 7,
        "Opt-Rollback-Portfolio": 4, "Opt-SeqLock-Portfolio": 5, "Static-Quota": 7, "Demand-Quota": 6,
        "HiGHS (1 thread)": 6, "LP-Round": 3}

plt.rcParams.update({"font.size": 10, "axes.titlesize": 10, "axes.labelsize": 10, "xtick.labelsize": 9,
                     "ytick.labelsize": 9, "legend.fontsize": 9, "font.family": "serif",
                     "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.6, "lines.linewidth": 1.6, "pdf.fonttype": 42})


def style(m):
    i = SLOT.get(m, 7)
    return dict(color=PALETTE[i], marker=MARKERS[i], linestyle=STYLES[i], markersize=5)


def save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIG / f"{name}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


def load(n):
    p = RAW / f"bench_{n}.csv"
    return pd.read_csv(p) if p.exists() else None


def inst_mean(df, value):
    return df.groupby(["instance_name", "scale", "method"], as_index=False)[value].mean()


def fig_gap_by_scale(A):
    methods = [PRIMARY, "PC-MALNS [BCRM-Greedy]", "Greedy-Efficiency-Portfolio", "Opt-Rollback", "Opt-SeqLock",
               "HiGHS (1T, wall-matched)", "HiGHS (4T, wall-matched)"]
    g = inst_mean(A, "gap_pct").groupby(["scale", "method"]).gap_pct.mean().unstack()
    sc = [s for s in SCALES if s in g.index]
    fig, ax = plt.subplots(figsize=(6.3, 3.3))
    x = np.arange(len(sc))
    for m in methods:
        if m in g:
            ax.plot(x, g.loc[sc, m], label=m, **style(m))
    ax.set_xticks(x, sc, rotation=0)
    ax.set_ylabel("Mean gap to lower bound (%)")
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    save(fig, "fig_gap_by_scale")


def fig_anytime(A):
    ref = pd.read_csv(RAW / "bench_reference.csv").set_index("instance_name")
    picks = [s for s in ("Large", "XXL") if s in set(A.scale)]
    if not picks:
        return
    fig, axes = plt.subplots(1, len(picks), figsize=(6.3, 2.8), squeeze=False)
    fig.subplots_adjust(wspace=0.25)
    for ax, scale in zip(axes[0], picks):
        a = A[(A.scale == scale) & (A.method == PRIMARY) & (A.rep == 0) & A.trace.notna()]
        T = float(a.wall_budget_s.iloc[0])
        grid = np.linspace(0, T, 200)
        cur_m, cur_h = [], []
        for r in a.itertuples():
            lb = r.lower_bound
            tr = np.array(json.loads(r.trace))
            cur_m.append([100 * (tr[tr[:, 0] <= t, 1][-1] - lb) / lb if np.any(tr[:, 0] <= t) else np.nan
                          for t in grid])
            htr = json.loads(ref.loc[r.instance_name, "trace"])
            cur_h.append([100 * ([o for tt, o in htr if tt <= t][-1] - lb) / lb if any(tt <= t for tt, _ in htr)
                          else np.nan for t in grid])
        mm = np.array(cur_m, float)
        okm = np.all(np.isfinite(mm), axis=0)   # start once every instance has a solution
        ax.plot(grid[okm], mm[:, okm].mean(axis=0), label="PC-MALNS (W = 4)", **dict(style(PRIMARY), marker=None))
        h = np.array(cur_h, float)
        ok = np.all(np.isfinite(h), axis=0)
        ax.plot(grid[ok], h[:, ok].mean(axis=0), label="HiGHS (1 thread)", **dict(style("HiGHS (1 thread)"), marker=None))
        ax.set_title(f"{scale} (mean of {len(a)} instances)", color=INK)
        ax.set_xlabel("Wall-clock time (s)")
        ax.set_ylim(bottom=0)
    axes[0][0].set_ylabel("Gap to lower bound (%)")
    axes[0][0].legend(frameon=False)
    save(fig, "fig_anytime")


def fig_rich_pools(B):
    methods = [PRIMARY, "PC-MALNS [BCRM-Greedy]", "Greedy-Efficiency-Portfolio", "Opt-Rollback",
               "HiGHS (1T, wall-matched)", "HiGHS (4T, wall-matched)"]
    Ps = sorted(B.P.unique())
    fig, axes = plt.subplots(1, len(Ps), figsize=(6.3, 3.0), squeeze=False, sharey=True)
    for ax, P in zip(axes[0], Ps):
        g = inst_mean(B[B.P == P], "gap_pct").groupby(["scale", "method"]).gap_pct.mean().unstack()
        sc = [s for s in SCALES if s in g.index]
        x = np.arange(len(sc))
        for m in methods:
            if m in g:
                ax.plot(x, g.loc[sc, m], label=m, **style(m))
        ax.set_xticks(x, sc, rotation=0)
        ax.set_title(f"P = {P}", color=INK)
    top = max(a.get_ylim()[1] for a in axes[0])
    axes[0][0].set_ylim(0, top * 1.05)
    axes[0][0].set_ylabel("Mean gap to lower bound (%)")
    h, l = axes[0][0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 0.0))
    save(fig, "fig_rich_pools")


def fig_tightness(E, A):
    d = pd.concat([E, A[(A.scale == "Large") & A.method.isin(set(E.method))]])
    g = d.groupby(["instance_name", "eta", "method"], as_index=False).gap_pct.mean().groupby(
        ["eta", "method"]).gap_pct.mean().unstack()
    fig, ax = plt.subplots(figsize=(4.0, 3.0))
    for m in [PRIMARY, "PC-MALNS [BCRM-Greedy]", "Greedy-Efficiency-Portfolio", "Opt-Rollback", "Opt-SeqLock",
              "Static-Quota", "HiGHS (1T, wall-matched)"]:
        if m in g:
            ax.plot(g.index, g[m], label=m, **style(m))
    ax.set_xlabel(r"Coupling tightness $\eta$")
    ax.set_ylabel("Mean gap to lower bound (%)")
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(1.02, 1.0))
    save(fig, "fig_tightness")


def fig_scaling(S):
    fig, ax = plt.subplots(figsize=(3.6, 2.8))
    p = S[S["mode"] == "pool"]
    Ws = sorted(p.workers_W.unique())
    ax.plot(Ws, Ws, color=INK2, linestyle=":", linewidth=1.0, label="Ideal")
    for i, scale in enumerate(sorted(p.scale.unique(), key=SCALES.index)):
        g = p[p.scale == scale].groupby("workers_W").speedup_vs_serial.mean()
        ax.plot(g.index, g.values, color=PALETTE[i], marker=MARKERS[i], linestyle=STYLES[i], label=scale)
    ax.set_xticks(Ws, [str(int(w)) for w in Ws])
    ax.set_xlim(0.5, max(Ws) + 0.5)
    ax.set_xlabel("Worker processes W")
    ax.set_ylabel("Wall-clock speedup vs serial")
    ax.legend(frameon=False)
    save(fig, "fig_scaling")


def fig_counterfactual():
    p = REPO_ROOT / "results" / "tables" / "bench_C_counterfactual.csv"
    if not p.exists():
        return
    cf = pd.read_csv(p)
    cf = cf[~cf.regime.str.contains("validation") & (cf.rule != "MC-CRIP")]
    rules = ["BCRM-Greedy", "Greedy-Efficiency", "Greedy-Gain", "Opt-SeqLock", "Opt-Rollback", "Static-Quota"]
    regimes = list(dict.fromkeys(cf.regime))
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    w = 0.8 / len(regimes)
    y = np.arange(len(rules))
    for j, reg in enumerate(regimes):
        v = cf[cf.regime == reg].set_index("rule").reindex(rules).share_of_mccrip_gain_pct
        ax.barh(y + j * w, v, height=w - 0.02, color=PALETTE[j], hatch=["", "//", "\\\\"][j % 3],
                edgecolor="#fcfcfb", linewidth=0.5, label=reg)
    ax.axvline(100, color=INK2, linewidth=0.8, linestyle=":")
    ax.set_yticks(y + w * (len(regimes) - 1) / 2, rules)
    ax.invert_yaxis()
    ax.set_xlabel("Share of the MC-CRIP barrier gain on conflict epochs (%)")
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    ax.grid(axis="y", visible=False)
    save(fig, "fig_counterfactual")


def fig_acceptance(A):
    l = A[A.family == "LNS"].copy()
    l["acc"] = 100 * l.accepted_moves / l.proposals.where(l.proposals > 0)
    methods = [m for m in [PRIMARY, "PC-MALNS [BCRM-Greedy]", "Greedy-Efficiency-Portfolio", "Greedy-Gain-Portfolio",
                           "Opt-Rollback-Portfolio", "Opt-SeqLock-Portfolio", "Opt-Rollback", "Opt-SeqLock",
                           "Static-Quota", "Demand-Quota"] if m in set(l.method)]
    g = l.groupby("method").acc.mean().reindex(methods)
    fig, ax = plt.subplots(figsize=(5.4, 3.3))
    y = np.arange(len(methods))
    ax.barh(y, g.values, color=PALETTE[0], height=0.6)
    for yi, v in zip(y, g.values):
        ax.text(v + 1, yi, f"{v:.0f}%", va="center", fontsize=9, color=INK)
    ax.set_yticks(y, methods)
    ax.invert_yaxis()
    ax.set_xlim(0, 105)
    ax.set_xlabel("Accepted / improving proposals (%), all scales")
    ax.grid(axis="y", visible=False)
    save(fig, "fig_acceptance")


def main():
    A, B, E, S = load("A"), load("B"), load("E_sweep"), load("E_scaling")
    if A is not None:
        fig_gap_by_scale(A)
        fig_anytime(A)
        fig_acceptance(A)
    if B is not None:
        fig_rich_pools(B)
    if E is not None and A is not None:
        fig_tightness(E, A)
    if S is not None:
        fig_scaling(S)
    fig_counterfactual()


if __name__ == "__main__":
    sys.exit(main())
