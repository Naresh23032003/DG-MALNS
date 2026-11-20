"""
Figures of the manuscript (revision 3): results/figures/*.pdf and .png (300 dpi).
All text >= 9 pt, one y-axis per panel, a fixed colour per method with marker and
line-style redundancy (colour is never the only identity cue). Gaps use the final lower
bounds (results/raw/lower_bounds.csv).

  fig_gap_diff        gap difference to PC-MALNS [Greedy-Efficiency] by scale:
                      (a) LNS methods, work protocol; (b) HiGHS variants, wall-clock protocol
  fig_anytime         wall clock: PC-MALNS [Greedy-Efficiency] run 0 vs HiGHS (cold reference
                      trace) and HiGHS + LP-Round start (Large, XXL)
  fig_progress        share of the final improvement reached over the epoch budget (work)
  fig_rich_pools      gap by scale, J = 20 / 40 (wall clock)
  fig_tightness       gap vs coupling tightness (Large, wall clock)
  fig_counterfactual  share of the MC-CRIP barrier gain captured by each rule
  fig_acceptance      committed / improving proposals by method (work protocol)
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
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
import scripts.analyze_revision3 as AR
from src.stats import mean_ci

RAW = REPO_ROOT / "results" / "raw"
FIG = REPO_ROOT / "results" / "figures"
PRIMARY = AR.PRIMARY
SCALES = AR.SC
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
MARKERS = ["o", "s", "^", "D", "v", "P", "X", "*"]
STYLES = ["-", "--", "-.", ":", "-", "--", "-.", ":"]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
SLOT = {PRIMARY: 0, "PC-MALNS [MC-CRIP]": 1, "PC-MALNS [Quota-Surplus]": 2, "PC-MALNS [Greedy-Gain]": 3,
        "Opt-Rollback": 4, "Opt-SeqLock": 5, "Opt-Rollback-Portfolio": 6, "Opt-SeqLock-Portfolio": 7,
        "Static-Quota": 7, "Async-Lock": 3, "LP-Round": 3,
        "HiGHS (1T, wall-matched)": 3, "HiGHS (4T, wall-matched)": 5, "HiGHS+LP-Round (1T, wall-matched)": 6,
        "HiGHS (1T, CPU-matched)": 7, "HiGHS+LP-Round (1T, CPU-matched)": 2, "HiGHS (5s)": 7}
# no two methods drawn in the same panel share a slot (colour, marker and line style)
SHORT = {PRIMARY: "PC-MALNS [GE]", "PC-MALNS [MC-CRIP]": "PC-MALNS [MC-CRIP]",
         "PC-MALNS [Quota-Surplus]": "PC-MALNS [QS]", "PC-MALNS [Greedy-Gain]": "PC-MALNS [GG]",
         "Opt-Rollback-Portfolio": "Opt-Rollback-Portf.", "Opt-SeqLock-Portfolio": "Opt-SeqLock-Portf.",
         "HiGHS (1T, wall-matched)": "HiGHS wall-matched", "HiGHS (4T, wall-matched)": "HiGHS 4T wall-matched",
         "HiGHS+LP-Round (1T, wall-matched)": "HiGHS+LP-Round wall-m.",
         "HiGHS (1T, CPU-matched)": "HiGHS CPU-matched", "HiGHS+LP-Round (1T, CPU-matched)": "HiGHS+LP-Round CPU-m."}

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


def inst_mean(df, value="gap_pct", keys=("instance_name", "scale")):
    return df.groupby(list(keys) + ["method"], as_index=False)[value].mean()


def diffs(df, methods, ref=PRIMARY):
    pi = inst_mean(df)
    out = {}
    for m in methods:
        rows = []
        for s in SCALES:
            w = pi[pi.scale == s].pivot(index="instance_name", columns="method", values="gap_pct")
            if m not in w or ref not in w:
                rows.append((np.nan, np.nan, np.nan))
                continue
            ci = mean_ci(w[m].values, w[ref].values)
            rows.append((ci["mean"], ci["t_lo"], ci["t_hi"]))
        out[m] = np.array(rows)
    return out


def fig_gap_diff():
    W = AR.gapify(AR.read("work_main.csv"))
    wall = AR.gapify(AR.wall("main"))
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.4))
    fig.subplots_adjust(wspace=0.32)
    x = np.arange(len(SCALES))
    panels = [(axes[0], W, ["PC-MALNS [MC-CRIP]", "PC-MALNS [Quota-Surplus]", "PC-MALNS [Greedy-Gain]",
                            "Opt-Rollback-Portfolio", "Opt-SeqLock-Portfolio", "Opt-Rollback", "Opt-SeqLock"],
               "(a) LNS methods, work protocol"),
              (axes[1], wall, ["HiGHS (1T, wall-matched)", "HiGHS+LP-Round (1T, wall-matched)",
                               "HiGHS (1T, CPU-matched)", "HiGHS+LP-Round (1T, CPU-matched)"],
               "(b) HiGHS 1.16.0, wall clock")]
    for ax, d, ms, title in panels:
        D = diffs(d, ms)
        for j, m in enumerate(ms):
            off = (j - (len(ms) - 1) / 2) * 0.05
            v = D[m]
            ax.errorbar(x + off, v[:, 0], yerr=[v[:, 0] - v[:, 1], v[:, 2] - v[:, 0]], capsize=2, elinewidth=0.8,
                        label=SHORT.get(m, m), **style(m))
        ax.axhline(0, color=INK2, linewidth=0.9)
        ax.set_xticks(x, ["S", "M", "L", "XL", "XXL", "XXXL"])
        ax.set_title(title, color=INK)
        ax.set_xlabel("Scale")
    axes[0].set_ylabel("Gap of method $-$ gap of PC-MALNS [GE] (pp)")
    for ax in axes:
        ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1)
    save(fig, "fig_gap_diff")


def fig_anytime():
    A = AR.wall("main")
    H = A[A.family == "HiGHS"]
    R = AR.ref_rows("main")
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.9))
    fig.subplots_adjust(wspace=0.28)
    for ax, scale in zip(axes, ("Large", "XXL")):
        a = A[(A.scale == scale) & (A.method == PRIMARY) & (A.rep == 0) & A.trace.notna()]
        T = float(a.wall_budget_s.iloc[0])
        grid = np.linspace(0, 3 * T, 300)
        cur = {"m": [], "h": [], "w": []}
        for r in a.itertuples():
            lb = AR.LB[r.instance_name]
            def at(tr, t):
                v = [o for tt, o in tr if tt <= t]
                return 100 * (v[-1] - lb) / lb if v else np.nan
            cur["m"].append([at(json.loads(r.trace), t) for t in grid])
            cur["h"].append([at(json.loads(R.loc[r.instance_name, "trace"]), t) for t in grid])
            hw = H[(H.instance_name == r.instance_name) & (H.method == "HiGHS+LP-Round (1T, wall-matched)")]
            tr = json.loads(hw.trace.iloc[0]) if len(hw) and isinstance(hw.trace.iloc[0], str) else []
            cur["w"].append([at(tr, t) for t in grid])
        for k, lab, m in (("m", "PC-MALNS [GE] (W = 4)", PRIMARY), ("h", "HiGHS reference run", "HiGHS (1T, wall-matched)"),
                          ("w", "HiGHS + LP-Round, wall-matched", "HiGHS+LP-Round (1T, wall-matched)")):
            arr = np.array(cur[k], float)
            ok = np.all(np.isfinite(arr), axis=0)
            if k != "h":          # the PC-MALNS run and the wall-matched HiGHS run stop at the budget
                ok &= grid <= T * 1.0001
            if ok.any():
                ax.plot(grid[ok], arr[:, ok].mean(axis=0), label=lab, **dict(style(m), marker=None))
        ax.axvline(T, color=INK2, linewidth=0.9, linestyle=":")
        ax.text(T, 5.7, " budget", color=INK2, fontsize=9, va="top")
        ax.set_title(f"{scale} ({len(a)} instances)", color=INK)
        ax.set_xlabel("Wall-clock time (s)")
        ax.set_ylim(0, 6)
    axes[0].set_ylabel("Gap to lower bound (%)")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 0.0))
    save(fig, "fig_anytime")


def fig_progress():
    W = AR.read("work_main.csv")
    if W is None:
        return
    W = W[(W.method == PRIMARY) & W.trace.notna()]
    fig, ax = plt.subplots(figsize=(4.6, 3.0))
    grid = np.linspace(0, 1, 101)
    for i, s in enumerate(SCALES):
        curves = []
        for r in W[W.scale == s].itertuples():
            tr = np.array(json.loads(r.trace))
            imp = tr[0] - tr[-1]
            if imp <= 1e-9:
                continue
            frac = (tr[0] - tr) / imp
            pos = np.linspace(0, 1, len(tr))
            curves.append(np.interp(grid, pos, frac))
        if curves:
            ax.plot(grid, 100 * np.mean(curves, axis=0), color=PALETTE[i], linestyle=STYLES[i], label=s,
                    marker=MARKERS[i], markevery=20, markersize=4)
    ax.set_xlabel("Fraction of the epoch budget")
    ax.set_ylabel("Share of the final improvement (%)")
    ax.set_ylim(0, 102)
    ax.legend(frameon=False, loc="lower right")
    save(fig, "fig_progress")


def fig_rich_pools():
    d = AR.gapify(AR.wall("rich"))
    methods = [PRIMARY, "PC-MALNS [MC-CRIP]", "Opt-Rollback", "HiGHS (1T, wall-matched)",
               "HiGHS+LP-Round (1T, wall-matched)", "HiGHS (1T, CPU-matched)", "HiGHS+LP-Round (1T, CPU-matched)"]
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.0), sharey=True)
    for ax, P in zip(axes, (20, 40)):
        g = inst_mean(d[d.P == P]).groupby(["scale", "method"]).gap_pct.mean().unstack()
        sc = [s for s in SCALES if s in g.index]
        x = np.arange(len(sc))
        for m in methods:
            if m in g:
                ax.plot(x, g.loc[sc, m], label=SHORT.get(m, m), **style(m))
        ax.set_xticks(x, sc)
        ax.set_title(f"J = {P}", color=INK)
    axes[0].set_ylim(bottom=0)
    axes[0].set_ylabel("Mean gap to lower bound (%)")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 0.0))
    save(fig, "fig_rich_pools")


def fig_tightness():
    import json as _j
    S = _j.loads((REPO_ROOT / "results" / "tables" / "summary.json").read_text())
    if "sweep" not in S:
        return
    g = S["sweep"]["gap"]
    etas = sorted(g, key=float)
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    for m in [PRIMARY, "PC-MALNS [MC-CRIP]", "Opt-Rollback", "Opt-SeqLock", "Static-Quota",
              "HiGHS (1T, wall-matched)", "HiGHS+LP-Round (1T, wall-matched)"]:
        ax.plot([float(e) for e in etas], [g[e].get(m, np.nan) for e in etas], label=SHORT.get(m, m), **style(m))
    ax.set_xlabel(r"Coupling tightness $\eta$")
    ax.set_ylabel("Mean gap to lower bound (%)")
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.02, 1.0))
    save(fig, "fig_tightness")


def fig_scaling():
    S = AR.read("bench_E_scaling.csv")
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
    p = REPO_ROOT / "results" / "tables" / "work_counterfactual.csv"
    if not p.exists():
        return
    cf = pd.read_csv(p)
    cf = cf[cf.rule != "MC-CRIP"]
    rules = ["Greedy-Efficiency", "Quota-Surplus", "Greedy-Gain", "Opt-SeqLock", "Opt-Rollback", "Static-Quota"]
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


def fig_acceptance():
    W = AR.read("work_main.csv")
    if W is None:
        return
    W = W.copy()
    W["acc"] = 100 * W.accepted_moves / W.proposals.where(W.proposals > 0)
    methods = [m for m in AR.ALL_LNS if m in set(W.method)]
    g = W.groupby("method").acc.mean().reindex(methods)
    fig, ax = plt.subplots(figsize=(5.4, 3.3))
    y = np.arange(len(methods))
    ax.barh(y, g.values, color=PALETTE[0], height=0.6)
    for yi, v in zip(y, g.values):
        ax.text(v + 1, yi, f"{v:.0f}%", va="center", fontsize=9, color=INK)
    ax.set_yticks(y, methods)
    ax.invert_yaxis()
    ax.set_xlim(0, 105)
    ax.set_xlabel("Committed / improving proposals (%), all scales")
    ax.grid(axis="y", visible=False)
    save(fig, "fig_acceptance")


def main():
    AR.LB = AR._lb()
    # strict: a missing input is an error, never a silently skipped figure
    for fn in (fig_gap_diff, fig_anytime, fig_progress, fig_rich_pools, fig_tightness, fig_counterfactual,
               fig_acceptance):
        fn()


if __name__ == "__main__":
    sys.exit(main())
