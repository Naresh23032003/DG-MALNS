# Portfolio-Coordinated Multi-Agent Large Neighborhood Search (PC-MALNS)

[![Repository](https://img.shields.io/badge/GitHub-Naresh23032003%2FDG--MALNS-181717?logo=github)](https://github.com/Naresh23032003/DG-MALNS)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Pytest-36%2F36_Passed-brightgreen.svg)](tests/)
[![Feasibility](https://img.shields.io/badge/Feasibility_Tolerance-1e--6_Verified-brightgreen.svg)](src/feasibility.py)

Source code, instance generators, raw results and reproduction scripts for the manuscript

> **Portfolio Conflict Resolution in Concurrent Multi-Agent Large Neighborhood Search for Coupled Multiple-Choice Allocation**
> Naresh R, Birla Institute of Technology and Science, Pilani (BITS Pilani). ORCID [0009-0000-0735-2066](https://orcid.org/0009-0000-0735-2066).

## 1. Overview

Concurrent LNS workers that improve a block-angular allocation problem compete for shared capacities, so their moves must be reconciled at a synchronization barrier. In **PC-MALNS** every worker sends a four-level, capacity-stratified portfolio of candidate moves:

| Level | Candidate | Capacity cap |
|---|---|---|
| 0 | incumbent, or a donor rebalance that dominates it | none (uses no more capacity) |
| 1 | quota-safe repair | quota `s/K` |
| 2 | borrower repair with a quadratic quota-excess penalty | `(q + s)/2` |
| 3 | optimistic repair (the proposal of the optimistic baselines) | residual slack `s` |

Levels 1 to 3 start from the same destroyed solution and run `M = 5` chained destroy–repair steps. The barrier selects one level per worker so that the selection fits into the residual slack: exactly by the multiple-choice conflict-resolution integer program **MC-CRIP** (primary mode), or greedily (**BCRM-Greedy**, quota-surplus greedy upgrade; **Greedy-Efficiency-Portfolio**; **Greedy-Gain-Portfolio**). The quotas cancel in the barrier constraint and only diversify the portfolio. Every epoch is feasible with monotone descent.

The test problem is **RPA-SH**, route-pattern allocation with shared hubs: a block-angular multiple-choice multidimensional knapsack problem. Its variant **RPA-SH-Sync** adds inter-depot transfers with lumpy, pair-shared dock capacities. The 27 classical **MMKP** benchmarks (I07–I13, INST01–INST20) are included as a boundary study.

## 2. Repository structure

```
src/
  instance_generator.py   RPA-SH generator (seeded)
  sync_instances.py       RPA-SH-Sync generator (paired agents, transfer docks)
  mmkp.py                 MMKP reader, certificate check, RPA-SH conversion, MMKP start
  feasibility.py          objective, slack and 1e-6 feasibility checks
  operators.py            destroy, Regret-2 repairs, donor rebalance
  worker.py               worker step: four-level portfolio with M chained steps
  commit_rules.py         barrier rules (MC-CRIP, BCRM-Greedy, Greedy-*, Opt-*, Static-Quota)
  bcrm_solver.py          MC-CRIP (enumeration / HiGHS with fallback) and BCRM-Greedy
  engine.py               concurrent LNS loop: starts, clocks, prices/quotas (ablation), traces
  agent_pool.py           persistent agent-owning worker processes (real wall clock)
  highs_runner.py         HiGHS 1.8.0 runs with thread count and incumbent trace
  baselines.py            LP relaxation and LP-Round warm start
  stats.py                exact Wilcoxon signed-rank test, Holm, paired-t and bootstrap CIs
scripts/
  run_pilot_diagnostic.py     validation pilot (seeds 1-3): start, cap, M, prices, quotas
  run_parameter_tuning.py     validation tuning (seeds 1-10)
  run_benchmark.py            test benchmark tables (A, B, C, E) on seeds 101-110
  run_mmkp_benchmarks.py      MMKP benchmarks (table D)
  run_slack_diagnostic.py     residual-slack mechanism diagnostic
  run_step2.sh                runs the full test suite one job at a time
  analyze_benchmark.py        statistics -> results/tables/
  generate_paper_tables.py    LaTeX tables -> paper/tables/
  generate_paper_macros.py    LaTeX number macros -> paper/generated_macros.tex
  make_figures.py             figures -> results/figures/
tests/                        36 unit tests (theory, worst-case ratios, generators, pool)
data/mmkp/                    MMKP instances and best-known-solution certificates
results/raw/                  all raw CSVs (bench_*, diag_slack, parameter_sensitivity*, pilot_*)
results/tables/, results/figures/, paper/
EXPERIMENT_REPORT.md          full results with confidence intervals and exact p-values
```

## 3. Installation and reproduction

```bash
pip install -r requirements.txt          # Python 3.11, highspy 1.8.0
python -m pytest -q                      # 36 tests

python scripts/run_pilot_diagnostic.py ref && python scripts/run_pilot_diagnostic.py A   # validation pilot
python scripts/run_parameter_tuning.py                                                     # validation tuning
python scripts/run_benchmark.py sync_check                                                 # validation, RPA-SH-Sync
./scripts/run_step2.sh                   # test benchmark, about 11 h, one job at a time
python scripts/run_slack_diagnostic.py   # mechanism diagnostic, about 13 min

python scripts/analyze_benchmark.py && python scripts/generate_paper_tables.py \
  && python scripts/generate_paper_macros.py && python scripts/make_figures.py
cd paper && pdflatex paper1_cor.tex && pdflatex paper1_cor.tex
```

Timing results depend on the machine. Ours were measured on an Apple M4 (4 performance and 6 efficiency cores). Every run is checked for feasibility to `1e-6`.

## 4. Main results (test seeds 101–110)

The LNS methods run 5 times per instance on `W = 4` processes with real wall-clock budgets (0.5, 1, 1.5, 2, 4 and 6 s from Small to XXXL). HiGHS runs once per instance. Gaps are to `max(LP bound, HiGHS dual bound)`. Comparisons use instance means with exact two-sided Wilcoxon tests, Holm-adjusted within each table; Diff is PC-MALNS [MC-CRIP] minus the method, so a negative value favours PC-MALNS [MC-CRIP]. All numbers come from `results/raw/`; see `EXPERIMENT_REPORT.md` for confidence intervals and the remaining tables.

**Main benchmark** (P = 6, η = 1.25, 60 instances), mean gap (%):

| Method | Small | Medium | Large | X-Large | XXL | XXXL | All | vs PC-MALNS [MC-CRIP]: W/T/L, Diff |
|---|---|---|---|---|---|---|---|---|
| LP-Round | 5.11 | 3.67 | 3.05 | 2.61 | 1.62 | 1.31 | 2.90 | 60/0/0, −1.382 |
| **PC-MALNS [MC-CRIP]** | 2.55 | 1.83 | 1.66 | 1.41 | 0.90 | 0.73 | 1.51 | – |
| PC-MALNS [BCRM-Greedy] | 2.57 | 1.87 | 1.65 | 1.42 | 0.91 | 0.74 | 1.53 | 40/0/20, −0.012 |
| Greedy-Efficiency-Portfolio | 2.57 | 1.80 | 1.59 | 1.38 | 0.88 | 0.72 | 1.49 | 16/0/44, +0.026 |
| Opt-Rollback | 2.74 | 2.05 | 1.80 | 1.58 | 1.05 | 0.88 | 1.68 | 58/0/2, −0.169 |
| Opt-SeqLock | 2.62 | 2.05 | 1.81 | 1.61 | 1.02 | 0.84 | 1.66 | 56/0/4, −0.145 |
| Static-Quota | 4.18 | 3.11 | 2.61 | 2.23 | 1.39 | 1.14 | 2.44 | 60/0/0, −0.929 |
| HiGHS (1 thread, wall-matched) | 1.31 | 1.56 | 3.40 | 3.05 | 1.74 | 1.46 | 2.08 | 44/0/16, −0.570 |
| HiGHS (1 thread, CPU-matched) | 1.11 | 0.69 | 0.47 | 0.40 | 0.23 | 0.18 | 0.51 | 0/0/60, +1.001 |
| HiGHS (60 s) | 0.59 | 0.42 | 0.36 | 0.34 | 0.22 | 0.16 | 0.35 | 0/0/60, +1.166 |

**Findings**

- **Portfolio coordination beats optimistic commit and quotas.** PC-MALNS beats rollback and sequential-lock commit also when those rules receive the same four-level portfolio (57/60 each), and beats static and demand-proportional quotas on 60/60 instances.
- **The exact barrier wins single epochs but not whole runs.** Over 1,955 conflict epochs it gains about 20% more than greedy-efficiency resolution, yet Greedy-Efficiency-Portfolio finishes 0.03 to 0.44 pp better in every test family at η = 1.25. In the diagnostic, MC-CRIP leaves less residual slack (19/20 instances) and commits fewer moves per epoch. MC-CRIP remains the primary mode because it was fixed on the validation seeds, where the two rules tied (p = 0.84).
- **Rich candidate pools favour PC-MALNS over a time-matched exact solver.** With P = 20 and P = 40, PC-MALNS (2.26% and 2.25%) beats wall-clock-matched and CPU-matched HiGHS (3.81% and 4.11%) on 40/40 instances each. With compact pools (P = 6), HiGHS wins at equal CPU time and with ≥ 5 s on Small to X-Large.
- **Prices and dynamic quotas add nothing.** None of the six variants differs from the default (Holm p = 1.0).
- **MMKP is a limit, not a win.** On the 27 instances PC-MALNS stalls at 2.59% from the best known solutions (HiGHS with the same wall clock: 0.20%), because improvement-only workers cannot release capacity across agents.
- **Measured scaling.** Speedup is 2.18–2.37× at W = 4 and 2.76–2.86× at W = 8, with results identical to serial execution.

## 5. Citation

```bibtex
@unpublished{naresh2026pcmalns,
  title  = {Portfolio Conflict Resolution in Concurrent Multi-Agent Large Neighborhood Search for Coupled Multiple-Choice Allocation},
  author = {R, Naresh},
  note   = {Manuscript under review. Code and data: https://github.com/Naresh23032003/DG-MALNS},
  year   = {2026}
}
```
