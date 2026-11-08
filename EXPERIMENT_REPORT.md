# Experiment Report — Revision 2 (PC-MALNS)

All numbers below come from `results/raw/bench_*.csv` and
`results/raw/parameter_sensitivity*.csv`, produced by `scripts/analyze_benchmark.py`.
Every table, including the per-scale primal integrals and the full sweep tests, is in
`results/tables/report_tables.md`. `paper/generated_macros.tex` holds 743 LaTeX macros for
these numbers, generated from `results/tables/summary.json`. Figures are in `results/figures/`.

- **Feasibility:** every reported solution was checked feasible to 1e-6, and the engine
  additionally asserts per-epoch feasibility and objective consistency.
- **Tests:** `pytest`, 36/36 pass (after porting the legacy-pipeline tests to the engine).
- **Runtime:** Step 2 ran from 06:22 to 17:07 on 2026-11-13, with every job run strictly
  one at a time.

## 1. Protocol

| Item | Setting |
|---|---|
| Method | **PC-MALNS** (Portfolio-Coordinated Multi-Agent LNS): LP-Round warm start, 4-level portfolio (l = 0..3), M = 5 chained destroy–repair steps per level, no consolidation cap, no prices (λ = 0), uniform quota s⁽ᵗ⁾/K |
| Barrier modes | `PC-MALNS [MC-CRIP]` (exact; primary) and `PC-MALNS [BCRM-Greedy]` |
| Test instances | Seeds 101..110. Parameters were chosen on validation seeds 1..10 only (pilot: 1..3; tuning: 1..10) |
| LNS runs | 5 independent runs (streams 0..4) per instance and method, on a persistent W = 4 agent-owning process pool, measured in real wall clock. Wall-clock budgets: Small 0.5 s, Medium 1 s, Large 1.5 s, X-Large 2 s, XXL 4 s, XXXL 6 s. The budget includes the charged LP-Round time and the shipping of the instance to the processes |
| Deterministic methods | LP-Round and HiGHS 1.8.0, once per instance |
| HiGHS references | 1 thread: 600 s on Small/Medium, 60 s on Large–XXXL (Table A), 30 s in Tables B/E1, 60 s on RPA-SH-Sync |
| HiGHS from reference traces | HiGHS (5s), HiGHS (60s) and HiGHS (1T, CPU-matched) are read from the incumbent trace of the reference run |
| HiGHS wall-matched | Separate real runs with 1 and 4 threads, with time limit = mean wall clock of the 5 PC-MALNS [MC-CRIP] runs |
| HiGHS timing scope | Measured around `run()`. Model build and pass take at most 0.04 s, measured up to XXL with P = 40, and are not charged |
| Lower bound | LB = max(LP bound, dual bound of the reference HiGHS run). **No reference run proved optimality, not even Small at 600 s**, so all gaps are to a bound, not to an optimum |
| Statistics | Unit = instance (mean over 5 runs; single value for deterministic methods). Paired mean difference with Student-t and bootstrap 95% CIs (10,000 resamples). Exact two-sided Wilcoxon signed-rank (zero_method = wilcox, mid-ranks, exact conditional distribution, never a normal approximation), Holm-adjusted within each table family. "Diff" = PC-MALNS [MC-CRIP] − method; **negative favours PC-MALNS [MC-CRIP]**. W/T/L counts instances where MC-CRIP is better / equal / worse |

## 2. Headline findings

1. **The portfolio and an LP-Round warm start are what make the method work; prices and quota steering add nothing.**
   - PC-MALNS beats all four optimistic commit rules (Opt-Rollback, Opt-SeqLock and their portfolio versions) on every instance family, by 0.13–0.25 pp, with 56–60 wins out of 60 and Holm p < 1e-4.
   - It beats Static-Quota and Demand-Quota on 60/60 instances.
   - None of the six price or quota variants differs significantly from the price-free default on Large (Table E2: all Holm p = 1.0).
2. **MC-CRIP is not the best barrier rule in final solution quality.**
   - Greedy-Efficiency-Portfolio is slightly but significantly better than MC-CRIP in every test-seed family:
     - Table A: +0.026 pp, 44/60 instances, Holm p < 1e-4;
     - Table B, P = 20: +0.051 pp, 35/40, p < 1e-4;
     - Table B, P = 40: +0.033 pp, 26/40, p = 0.017;
     - direct start: +0.44 pp, 16/20, p = 0.0002;
     - RPA-SH-Sync: +0.084 pp, 15/20, p = 0.004.
   - MC-CRIP still has the larger gain on each conflict epoch (the greedy rules capture 77–96% of it) and the lowest conflict rate. That per-epoch optimality does not carry through to the final objective.
   - On the validation pilot the two rules tied (p = 0.84). The difference was only detected on the test seeds, so swapping the primary mode now would be selection on test data (see §5).
3. **The exact barrier did not help on transfer-synchronised instances.** RPA-SH-Sync (design fixed before any run) was built to give single-agent greedy rules a hard time:
   - MC-CRIP ties BCRM-Greedy and Greedy-Gain-Portfolio;
   - it loses to Greedy-Efficiency-Portfolio;
   - it beats only the optimistic rules.
4. **Against HiGHS, PC-MALNS wins only in short real-time regimes.**
   - At matched wall clock it wins on 44/60 P = 6 instances (Large and above) and on 40/40 P = 20 and P = 40 instances.
   - HiGHS wins as soon as it gets about 5 s, and at matched CPU time it wins on 60/60 P = 6 instances.
   - On P = 20/40, PC-MALNS also beats HiGHS (1T, CPU-matched) in gap on 40/40 instances, but not in primal integral.
5. **HiGHS 1.8 does not profit from 4 threads.** The 4-thread runs are essentially identical to the 1-thread runs; its branch-and-bound is serial.
6. **Real wall-clock scaling is below the 3.2–3.8× target.** Measured speedups vs serial are 2.18–2.37× at W = 4 and 2.76–2.86× at W = 8 (§3.7), with results identical to serial.
7. **PC-MALNS cannot release capacity across agents.** No worker ever proposes a move that raises its own cost (with or without prices). On the public MMKP benchmarks:
   - the search stalls at 2.59% from the best known solution (from a 2.91% start), against 0.19% for wall-matched HiGHS;
   - barrier conflicts are almost absent (< 0.5% of epochs), so the commit rules barely differ.

## 3. Tables

### 3.1 Table A — main benchmark (P = 6, η = 1.25, 60 instances)

Mean gap to LB (%):

| Method | Small | Medium | Large | X-Large | XXL | XXXL | All |
|---|---|---|---|---|---|---|---|
| LP-Round | 5.113 | 3.673 | 3.054 | 2.611 | 1.616 | 1.310 | 2.896 |
| **PC-MALNS [MC-CRIP]** | 2.547 | 1.832 | 1.656 | 1.411 | 0.902 | 0.733 | 1.514 |
| PC-MALNS [BCRM-Greedy] | 2.569 | 1.872 | 1.647 | 1.424 | 0.906 | 0.737 | 1.526 |
| Greedy-Efficiency-Portfolio | 2.566 | 1.800 | 1.585 | 1.379 | 0.876 | 0.717 | 1.487 |
| Greedy-Gain-Portfolio | 2.616 | 1.828 | 1.662 | 1.446 | 0.951 | 0.796 | 1.550 |
| Opt-Rollback | 2.743 | 2.045 | 1.802 | 1.583 | 1.049 | 0.875 | 1.683 |
| Opt-SeqLock | 2.618 | 2.050 | 1.814 | 1.605 | 1.024 | 0.841 | 1.659 |
| Opt-Rollback-Portfolio | 2.753 | 2.042 | 1.819 | 1.572 | 1.048 | 0.880 | 1.686 |
| Opt-SeqLock-Portfolio | 2.631 | 2.033 | 1.812 | 1.573 | 1.003 | 0.818 | 1.645 |
| Static-Quota | 4.181 | 3.112 | 2.611 | 2.225 | 1.386 | 1.141 | 2.443 |
| Demand-Quota | 3.820 | 2.866 | 2.409 | 2.037 | 1.286 | 1.045 | 2.244 |
| HiGHS (1T, wall-matched) | 1.305 | 1.557 | 3.397 | 3.048 | 1.739 | 1.458 | 2.084 |
| HiGHS (4T, wall-matched) | 1.305 | 1.416 | 3.034 | 2.785 | 1.739 | 1.458 | 1.956 |
| HiGHS (1T, CPU-matched) | 1.112 | 0.687 | 0.466 | 0.396 | 0.234 | 0.178 | 0.512 |
| HiGHS (5s) | 0.899 | 0.687 | 0.475 | 0.449 | 1.739 | 1.458 | 0.951 |
| HiGHS (60s) | 0.590 | 0.417 | 0.357 | 0.338 | 0.222 | 0.164 | 0.348 |
| HiGHS (600s) | 0.472 | 0.324 | – | – | – | – | – |

PC-MALNS [MC-CRIP] resources:

| Scale | Wall clock (s) | CPU time (s) | Conflict epochs (%) |
|---|---|---|---|
| Small | 0.50 | 1.73 | 3.3 |
| Medium | 1.01 | 3.64 | 5.1 |
| Large | 1.52 | 5.45 | 10.3 |
| X-Large | 2.03 | 6.91 | 15.0 |
| XXL | 4.08 | 12.93 | 18.1 |
| XXXL | 6.11 | 19.43 | 22.4 |

Pooled tests (60 instances, Holm within the table):

| PC-MALNS [MC-CRIP] vs | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p (Holm) |
|---|---|---|---|---|
| LP-Round | −1.382 [−1.578, −1.187] | [−1.574, −1.200] | 60/0/0 | <1e-4 |
| PC-MALNS [BCRM-Greedy] | −0.012 [−0.026, +0.001] | [−0.025, +0.001] | 40/0/20 | 0.034 |
| Greedy-Efficiency-Portfolio | **+0.026** [+0.010, +0.043] | [+0.009, +0.041] | 16/0/44 | <1e-4 |
| Greedy-Gain-Portfolio | −0.036 [−0.057, −0.015] | [−0.057, −0.016] | 46/0/14 | 0.0012 |
| Opt-Rollback | −0.169 [−0.200, −0.139] | [−0.199, −0.140] | 58/0/2 | <1e-4 |
| Opt-SeqLock | −0.145 [−0.172, −0.118] | [−0.172, −0.119] | 56/0/4 | <1e-4 |
| Opt-Rollback-Portfolio | −0.172 [−0.200, −0.144] | [−0.201, −0.145] | 57/0/3 | <1e-4 |
| Opt-SeqLock-Portfolio | −0.131 [−0.156, −0.107] | [−0.154, −0.107] | 57/0/3 | <1e-4 |
| Static-Quota | −0.929 [−1.050, −0.808] | [−1.046, −0.814] | 60/0/0 | <1e-4 |
| Demand-Quota | −0.730 [−0.826, −0.634] | [−0.823, −0.639] | 60/0/0 | <1e-4 |
| HiGHS (1T, wall-matched) | −0.570 [−0.887, −0.254] | [−0.871, −0.261] | 44/0/16 | 0.0089 |
| HiGHS (4T, wall-matched) | −0.443 [−0.760, −0.125] | [−0.746, −0.133] | 41/0/19 | 0.034 |
| HiGHS (1T, CPU-matched) | +1.001 [+0.907, +1.096] | [+0.912, +1.096] | 0/0/60 | <1e-4 |
| HiGHS (5s) | +0.562 [+0.304, +0.820] | [+0.309, +0.810] | 20/0/40 | <1e-4 |
| HiGHS (60s) | +1.166 [+1.036, +1.295] | [+1.043, +1.293] | 0/0/60 | <1e-4 |

How the comparison with wall-matched HiGHS splits by scale:
- HiGHS is better on Small (1.31% vs 2.55%) and on Medium with 4 threads (1.42% vs 1.83%).
- PC-MALNS is better on Large, X-Large, XXL and XXXL.
- On XXL and XXXL, 4–6 s is too short for HiGHS to improve on its first incumbents.

### 3.2 Table B — rich candidate pools (P = 20, 40; Medium–XXL; 40 instances each)

| Mean gap (%) | P = 20 | P = 40 |
|---|---|---|
| LP-Round | 3.265 | 3.202 |
| **PC-MALNS [MC-CRIP]** | 2.264 | 2.246 |
| PC-MALNS [BCRM-Greedy] | 2.268 | 2.260 |
| Greedy-Efficiency-Portfolio | 2.213 | 2.212 |
| Opt-Rollback | 2.487 | 2.480 |
| Opt-SeqLock | 2.496 | 2.496 |
| HiGHS (1T, wall-matched) | 3.813 | 4.107 |
| HiGHS (4T, wall-matched) | 3.813 | 4.115 |
| HiGHS (1T, CPU-matched) | 3.813 | 4.107 |
| HiGHS (30s) | 1.369 | 2.722 |

PC-MALNS [MC-CRIP] vs wall-matched HiGHS:

| Comparison | Diff [t 95% CI] | W/T/L | p (Holm) |
|---|---|---|---|
| P = 20, 1 thread | −1.549 [−1.787, −1.311] | 40/0/0 | <1e-4 |
| P = 40, 1 thread | −1.861 [−2.119, −1.602] | 40/0/0 | <1e-4 |
| P = 20 / 40, 4 threads | same as 1 thread | 40/0/0 | <1e-4 |
| P = 20 / 40, CPU-matched (1T) | same as wall-matched | 40/0/0 | <1e-4 |

PC-MALNS [MC-CRIP] vs HiGHS (30s):

| P | Diff [t 95% CI] | W/T/L | p (Holm) | Verdict |
|---|---|---|---|---|
| 20 | +0.895 [+0.376, +1.413] | 11/0/29 | 0.0026 | HiGHS better |
| 40 | −0.477 [−1.070, +0.117] | 28/0/12 | 0.47 | Not significant |

The CPU-matched rows equal the wall-matched ones because HiGHS's incumbent did not change between the two time limits on these instances.

**Primal integral (Table B; caveat).**
- Wall-matched HiGHS has the lower primal integral (P = 20: 0.063 vs 0.195; P = 40: 0.062 vs 0.323) despite its much worse final gap.
- The reason: by definition the PC-MALNS primal gap is 1 until the LP-Round start exists, and that start, plus shipping the instance to the processes, takes up to 0.36 s (P = 20) and 0.67 s (P = 40) at XXL.
- HiGHS finds a first incumbent quickly, but a weak one, and keeps it.
- So the claim "beats wall-matched HiGHS in primal integral" is **not supported**; the claim about final gap is.

### 3.3 Table C — commit-rule isolation (Medium + Large, 20 instances per regime)

Mean gap (%):

| Rule | LP-Round start | Direct start | RPA-SH-Sync |
|---|---|---|---|
| **PC-MALNS [MC-CRIP]** | 1.744 | 5.984 | 2.119 |
| PC-MALNS [BCRM-Greedy] | 1.760 | 5.727 | 2.120 |
| Greedy-Efficiency-Portfolio | 1.693 | 5.541 | 2.035 |
| Greedy-Gain-Portfolio | 1.745 | 6.206 | 2.127 |
| Opt-Rollback-Portfolio | 1.930 | 8.918 | 2.327 |
| Opt-SeqLock-Portfolio | 1.922 | 7.770 | 2.282 |
| Opt-Rollback | 1.923 | 7.269 | 2.317 |
| Opt-SeqLock | 1.932 | 7.562 | 2.302 |

Conflict rate of PC-MALNS [MC-CRIP] (% of epochs): 7.7 (LP-Round start), 26.5 (direct start), 13.4 (RPA-SH-Sync).

PC-MALNS [MC-CRIP] vs each rule, as diff (W/T/L, Holm p):

| vs | LP-Round start | Direct start | RPA-SH-Sync |
|---|---|---|---|
| BCRM-Greedy | −0.016 (15/0/5, 0.35) | **+0.257** (3/0/17, 0.002) | −0.002 (9/0/11, 1.0) |
| Greedy-Efficiency-Portfolio | **+0.052** (7/0/13, 0.028) | **+0.443** (4/0/16, 0.0002) | **+0.084** (5/0/15, 0.004) |
| Greedy-Gain-Portfolio | −0.001 (11/0/9, 0.84) | −0.222 (15/0/5, 0.008) | −0.009 (12/0/8, 1.0) |
| Opt-Rollback-Portfolio | −0.186 (20/0/0, <1e-4) | −2.934 (20/0/0, <1e-4) | −0.209 (20/0/0, <1e-4) |
| Opt-SeqLock-Portfolio | −0.178 (20/0/0, <1e-4) | −1.786 (20/0/0, <1e-4) | −0.164 (19/0/1, <1e-4) |
| Opt-Rollback | −0.179 (20/0/0, <1e-4) | −1.285 (19/0/1, <1e-4) | −0.198 (20/0/0, <1e-4) |
| Opt-SeqLock | −0.188 (20/0/0, <1e-4) | −1.578 (20/0/0, <1e-4) | −0.183 (20/0/0, <1e-4) |

Compared with the pilot, on the test seeds:

| Pilot expectation | Test-seed result |
|---|---|
| Direct start: 2.7–4.7 pp over Opt-* | 1.3–2.9 pp |
| Direct start: 45% conflict rate | 26.5% conflict rate |
| Direct start: MC-CRIP ties BCRM-Greedy and Greedy-Efficiency | MC-CRIP loses to both |

The win over Greedy-Gain-Portfolio under the direct start holds (15/20, Holm p = 0.008).

**Counterfactual barrier analysis.** Every rule is applied to the same portfolios on each conflict epoch of the PC-MALNS [MC-CRIP] runs:

| Rule | LP-Round: share of MC-CRIP gain | LP-Round: MC-CRIP strictly better | Direct: share | Direct: strictly better | Sync: share | Sync: strictly better |
|---|---|---|---|---|---|---|
| BCRM-Greedy | 79.6% | 58.2% | 95.5% | 54.3% | 76.9% | 61.3% |
| Greedy-Efficiency | 84.0% | 51.3% | 84.1% | 47.6% | 83.2% | 52.9% |
| Greedy-Gain | 83.9% | 43.0% | 93.1% | 37.8% | 84.3% | 39.4% |
| Opt-SeqLock | 57.4% | 100% | 85.9% | 100% | 60.4% | 99.8% |
| Opt-Rollback | 20.6% | 100% | 10.6% | 100% | 19.4% | 100% |
| Static-Quota | 6.3% | 100% | 74.5% | 100% | 5.8% | 100% |

Conflict epochs analysed: 409 (LP-Round), 1,109 (direct), 437 (Sync).

The per-epoch dominance of MC-CRIP (Proposition 1) is confirmed empirically. Its size relative to the greedy rules (16–20% more gain per conflict epoch) does not turn into better final objectives. Mechanism diagnostic (`scripts/run_slack_diagnostic.py`, `results/raw/diag_slack.csv`, same instances and budgets; 80% of the LP-Round runs reproduce Table A exactly, the rest differ by 0.004 pp on average):

| Start | Rule | Gap | Time-avg. mean slack (% of d) | Time-avg. bottleneck slack (%) | Improving moves / epoch |
|---|---|---|---|---|---|
| LP-Round | PC-MALNS [MC-CRIP] | 1.745 | 0.54 | 0.068 | 0.33 |
| LP-Round | PC-MALNS [BCRM-Greedy] | 1.760 | 0.61 | 0.082 | 0.43 |
| LP-Round | Greedy-Efficiency-Portfolio | 1.693 | 0.61 | 0.080 | 0.41 |
| Direct | PC-MALNS [MC-CRIP] | 5.923 | 2.51 | 2.062 | 1.10 |
| Direct | PC-MALNS [BCRM-Greedy] | 5.688 | 2.67 | 2.034 | 1.34 |
| Direct | Greedy-Efficiency-Portfolio | 5.480 | 3.08 | 2.249 | 1.36 |

MC-CRIP leaves less mean slack than Greedy-Efficiency on 19/20 instances under both starts (exact Wilcoxon p < 1e-4), less bottleneck slack on 14/20 and 16/20 (p = 0.005, 0.004), and commits about a quarter fewer improving moves per epoch. This is consistent with MC-CRIP spending slack on capacity-hungry high-gain combinations; it is an association, not a causal test.

### 3.4 Table D — public MMKP benchmarks (27 instances, K = 8 agents, 2 s wall clock)

| Method | Mean gap to BKS (%) | MMKP-feasible runs |
|---|---|---|
| LP-Round (raw) | 0.48 (3 feasible instances only) | 11.1% |
| PC-MALNS [MC-CRIP] | 2.594 | 96.3% |
| PC-MALNS [BCRM-Greedy] | 2.615 | 96.3% |
| Opt-Rollback | 2.622 | 96.3% |
| Opt-SeqLock | 2.599 | 96.3% |
| Static-Quota | 2.909 | 96.3% |
| HiGHS (1T / 4T, wall-matched) | 0.195 | 100% |
| HiGHS (60s) | 0.125 | 100% |

The BKS values come from verified certificates for all 27 instances.

**Start construction.**
- LP-Round leaves at least one group without an item on 24 of 27 instances, and no LNS method (with or without prices) repairs it.
- Every LNS method therefore starts from the classic two-phase MMKP construction (Khan et al., 2002: lightest item per group, then best profit-per-added-weight upgrades), with its time charged.
- On INST04 neither start is feasible, so all LNS runs there are MMKP-infeasible.

**Results.**
- PC-MALNS improves on its start on 17 of 26 instances (mean gap 2.91% → 2.59%).
- MC-CRIP differs significantly only from Static-Quota (17/9/0, Holm p < 1e-4).
- Conflicts occur on under 0.5% of epochs.
- MMKP shows the limitation of finding 7 and does **not** support a competitive claim.

### 3.5 Table E1 — tightness sweep (Large, 10 instances per η)

| Mean gap (%) | η = 0.85 | 1.05 | 1.25 | 1.45 |
|---|---|---|---|---|
| LP-Round | 2.934 | 3.055 | 3.054 | 1.708 |
| **PC-MALNS [MC-CRIP]** | 1.803 | 1.845 | 1.656 | 1.107 |
| PC-MALNS [BCRM-Greedy] | 1.796 | 1.851 | 1.647 | 1.125 |
| Greedy-Efficiency-Portfolio | 1.786 | 1.846 | 1.585 | 1.100 |
| Opt-Rollback | **1.700** | 1.817 | 1.802 | 1.213 |
| Opt-SeqLock | 1.703 | **1.792** | 1.814 | 1.217 |
| Static-Quota | 1.740 | 2.554 | 2.611 | 1.634 |
| HiGHS (1T, wall-matched) | 0.950 | 3.615 | 3.397 | 0.450 |
| HiGHS (1T, CPU-matched) | 0.322 | 0.474 | 0.466 | 0.413 |

- With loose coupling (η = 0.85), the optimistic single-proposal rules are *better* than PC-MALNS: 9/10 and 8/10 instances, unadjusted p = 0.006 and 0.014.
- The portfolio pays off only once the hubs bind (η ≥ 1.25).
- Holm over all 40 sweep tests, with n = 10 per η, leaves no comparison significant at 0.05: the smallest attainable adjusted p is 0.076. The family was fixed before the runs and is reported as is.

### 3.6 Table E2 — price / quota ablation (Large, η = 1.25, 10 instances)

All variants use MC-CRIP; the reference is the default (no prices, static quota).

| Variant | Mean gap (%) | Diff vs default | W/T/L | p (Holm) |
|---|---|---|---|---|
| Default (no prices, static quota) | 1.656 | – | – | – |
| Heuristic prices, static quota | 1.632 | +0.024 | 4/0/6 | 1.0 |
| Heuristic prices, dynamic quota | 1.629 | +0.028 | 4/0/6 | 1.0 |
| MC-CRIP LP duals, static quota | 1.635 | +0.021 | 4/0/6 | 1.0 |
| MC-CRIP LP duals, dynamic quota | 1.627 | +0.029 | 4/0/6 | 1.0 |
| No prices, demand quota | 1.634 | +0.022 | 4/0/6 | 1.0 |
| No prices, dynamic quota | 1.662 | −0.006 | 7/1/2 | 1.0 |

The variants are slightly better on average but not significantly so. This supports "prices and quota steering are redundant given the portfolio". It does not support "they hurt".

### 3.7 Table E3 — wall-clock scaling

Fixed epochs (Large 40, XXL 20), seeds 101–103, one job at a time:

| Scale | Serial (s) | W = 1 | W = 2 | W = 4 | W = 8 |
|---|---|---|---|---|---|
| Large | 3.13 | 0.99× | 1.72× | 2.37× | 2.76× |
| XXL | 5.64 | 1.01× | 1.56× | 2.18× | 2.86× |

- All runs produce objectives identical to serial.
- The CPU and simulated-parallel clocks allow 7–8× with perfect parallelism, so the measured shortfall comes from process communication, instance shipping, load imbalance and the serial barrier.
- The machine is an Apple M4 with 4 performance and 6 efficiency cores.
- The pilot's 3.4× (persistent pool, M = 5) was not reproduced in this fixed-epoch protocol.

### 3.8 Table E4 — parameter tuning

Validation seeds 1..10, Medium, 3 runs each, 2 s CPU. Adoption rule fixed in advance: Holm p < 0.05 and better than the default.

| Factor | Levels (mean gap %) | Adopted |
|---|---|---|
| M | 1 (1.94), 2 (1.91), **5 (1.85)**, 10 (1.80; 19/11, Holm p = 0.083) | No, default kept |
| Destroy range | (0.08, 0.16) 1.82, **(0.16, 0.30) 1.85**, (0.30, 0.45) 1.91 | No |
| Noise σ | 0 (1.85), 1 (1.86), **2 (1.85)**, 4 (1.79; p_holm 0.22) | No |
| ρ₀ | 0 (1.87), 0.15 (1.87), **0.35 (1.85)**, 0.70 (1.81) | No |

The default (in bold) is within noise of the best level on every factor; M = 1 is the worst (10/20, unadjusted p = 0.028).

## 4. Implementation notes relevant to the referees

- **Clocks.** `wall_clock_s` is real elapsed time. `cpu_time_s` is the sum of the worker times plus the barrier. `sim_parallel_s` is the maximum worker time plus the barrier. The LP-Round time is charged to the wall clock of every run; it is cached per instance, and before this revision only the first run on each instance paid it. HiGHS records `highs_time_limit_s` and `highs_actual_time_s` separately, together with the thread count.
- **MC-CRIP fallback** (unified). If MC-CRIP is not proven optimal within its limit, it returns the cheapest feasible of: the HiGHS incumbent, BCRM-Greedy, and the all-quota-safe selection. In Step 2 the fallback was triggered 9 times, all in Table A: once in each of 9 of the 100 PC-MALNS [MC-CRIP] runs on XXL/XXXL (K = 24/32), out of 3–6 conflict epochs per run. It never triggered on Small–X-Large or in Tables B–E.
- **Bug found and fixed during Step 2 preparation.** `verify_solution_feasibility` crashed for `m_local = 0` (all MMKP instances); a unit test caught it.
- **New tests.** `tests/test_worst_case_bounds.py` (18, including the unbounded worst-case ratio of Greedy-Efficiency) and `tests/test_extensions.py` (6). The legacy-pipeline tests were ported to the engine; the quota test is now `test_proposition_1_quota_safe_selection_is_feasible`.
- **Worst-case ratios (Proposition 2).** Static-Quota: unbounded; Opt-Rollback: K − 1 (expected); Opt-SeqLock: K/(1+ε); Greedy-Gain: 2/(1+ε) with one hub and m/(1+ε) with m hubs; Greedy-Efficiency: **unbounded** (C/2 for every C > 2, the classical ratio-greedy knapsack failure), not 2 − ε. These are lower bounds on the worst case, not proven tight.

## 5. Recommendations for the manuscript rewrite

1. **Name.** Use **PC-MALNS**; prices are not part of the method. Move the dual-price and dynamic-quota machinery to an ablation subsection with Table E2.
2. **Do not claim that the exact barrier (MC-CRIP) improves final solution quality** over efficiency-greedy resolution. The defensible claims are:
   - (a) the four-level portfolio and its barrier rules dominate optimistic rollback and sequential-lock commit (Tables A, C; 56–60 of 60 instances);
   - (b) MC-CRIP is per-epoch optimal and captures 16–20% more gain per conflict epoch than the greedy rules (counterfactual table);
   - (c) this per-epoch advantage does not carry over to the final objective. Greedy-Efficiency resolution is equally good or slightly better at negligible cost. That is a useful, honest result.
3. **Primary barrier mode.** Keep MC-CRIP as the primary mode in the tables (pre-registered). State explicitly that Greedy-Efficiency-Portfolio is the best rule on the test seeds, and that this choice was not made on validation data. Making Greedy-Efficiency the default would require a fresh validation-only selection, ideally confirmed on new seeds.
4. **HiGHS claims.** Use "Under a hard real-time budget of 0.5–6 s on 4 cores, PC-MALNS beats wall-clock-matched HiGHS on the larger instances (Large–XXXL with P = 6; all instances with P = 20/40)". Also state that HiGHS wins with ≥ 5 s, and at matched CPU time on every P = 6 instance. Drop the primal-integral superiority claim for Table B.
5. **Transfer synchronisation.** Report RPA-SH-Sync as a negative result for the exact barrier.
6. **MMKP.** Report as a limitation (no cross-agent capacity release), not as a competitive benchmark.
7. **Scaling.** Report the measured 2.2–2.4× at W = 4, not 3.2–3.8×.
8. **Legacy files.** Removed: the revision-1 CSVs, the scripts `run_experiments.py`, `run_revision_experiments.py`, `compute_significance.py`, `generate_paper_artifacts.py`, the old serial pipeline `src/dg_malns.py` and the legacy runners in `src/baselines.py`, and the old figures and tables.
