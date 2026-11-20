# Portfolio-Coordinated Multi-Agent Large Neighborhood Search (PC-MALNS)

[![Repository](https://img.shields.io/badge/GitHub-Naresh23032003%2FPC--MALNS-181717?logo=github)](https://github.com/Naresh23032003/PC-MALNS)
[![Python](https://img.shields.io/badge/Python-3.11-green.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Pytest-48%2F48_Passed-brightgreen.svg)](tests/)
[![Feasibility](https://img.shields.io/badge/Feasibility_Tolerance-1e--6_Verified-brightgreen.svg)](src/feasibility.py)

Source code, instance generators, raw results, study plans and reproduction scripts for the manuscript

> **Portfolio Conflict Resolution in Concurrent Multi-Agent Large Neighborhood Search for Coupled Multiple-Choice Allocation**
> Naresh R, Birla Institute of Technology and Science, Pilani (BITS Pilani). ORCID [0009-0000-0735-2066](https://orcid.org/0009-0000-0735-2066).

## 1. Overview

When several LNS agents improve a block-angular allocation problem at once, their moves compete for shared capacities and must be reconciled at a synchronization barrier. In **PC-MALNS** every agent sends a four-level, capacity-stratified portfolio of candidate moves:

| Level | Candidate | Capacity cap |
|---|---|---|
| 0 | incumbent, or a rebalance that dominates it | uses no more capacity than the incumbent |
| 1 | quota-safe repair | quota `s/K` |
| 2 | borrowing repair with a quadratic quota-excess penalty | `(q + s)/2` |
| 3 | optimistic repair (the proposal of the optimistic baselines) | residual slack `s` |

The barrier selects one level per agent so that the selection fits into the residual slack. The recommended rule is **PC-MALNS [Greedy-Efficiency]**, which scans upgrades by gain per unit of extra capacity. The alternatives are the exact multiple-choice program **MC-CRIP**, **Quota-Surplus** and **Greedy-Gain**. Every epoch is feasible and does not increase the cost.

The test problem is **MCA-SC**, a synthetic block-angular multiple-choice allocation problem with shared capacities. Its variant **MCA-SC-Pair** adds lumpy capacities shared by pairs of agents. The 27 classical **MMKP** benchmarks (I07–I13, INST01–INST20) are included as a boundary study.

## 2. Repository structure

```
src/
  instance_generator.py   MCA-SC generator (seeded)
  sync_instances.py       MCA-SC-Pair generator
  mmkp.py                 MMKP reader, certificate check, MCA-SC conversion, MMKP start
  feasibility.py          objective, slack and 1e-6 feasibility checks
  operators.py            destroy, Regret-2 repairs, level-0 rebalance
  worker.py               agent step: four-level portfolio with M chained steps
  commit_rules.py         barrier rules (Greedy-*, Quota-Surplus, Opt-*, quotas) and counterfactual logging
  barrier_solvers.py      MC-CRIP (enumeration / HiGHS with fallback) and Quota-Surplus
  engine.py               synchronous LNS loop: starts, work and wall-clock budgets, prices/quotas (ablation)
  agent_pool.py           persistent agent-owning worker processes
  async_lock.py           Async-Lock baseline (commit on arrival, no barrier)
  highs_runner.py         HiGHS runs with thread count, incumbent trace and watchdog
  baselines.py            LP relaxation and LP-Round start
  stats.py                exact Wilcoxon signed-rank test, Holm, paired-t and bootstrap CIs
scripts/
  run_work_protocol.py    work-protocol tables (main, commit_*, validation, levels, prices, restart,
                          prices_fresh, rho0, cf_all, seq)
  run_wallclock_uniform.py  wall-clock jobs under uniform conditions (main, rich, rich_rerun, sweep, pair, mmkp)
  build_lower_bounds.py   final lower bounds -> results/raw/lower_bounds.csv
  analyze_revision3.py    all statistics -> results/tables/report_tables.md, summary.json
  generate_paper_tables.py  LaTeX tables -> paper/tables/
  generate_paper_macros.py  every number in the text -> paper/generated_macros.tex
  make_figures.py         figures -> results/figures/
  make_submission.py      flat LaTeX package for Editorial Manager -> paper/submission.zip
tests/                    48 unit tests (properties, worst-case constructions, generators, pool, logging)
data/mmkp/                MMKP instances and best-known-solution certificates
results/raw/              all raw CSVs (see results/raw/README.md)
results/*_plan.md         study plans: validation, prices, wall-clock rerun (with addenda)
results/tables/, results/figures/, paper/
EXPERIMENT_REPORT.md      protocols, run conditions and where every result is
```

## 3. Installation and reproduction

```bash
pip install -r requirements.txt          # Python 3.11, highspy 1.16.0
python -m pytest -q                      # 48 tests

python scripts/run_work_protocol.py main       # and: commit_direct, commit_pair, validation, levels,
                                               #      prices, restart, prices_fresh, rho0, cf_all, seq
python scripts/run_wallclock_uniform.py main   # and: rich, rich_rerun, sweep, pair, mmkp (one at a time)

python scripts/build_lower_bounds.py && python scripts/analyze_revision3.py \
  && python scripts/generate_paper_tables.py && python scripts/generate_paper_macros.py \
  && python scripts/make_figures.py
cd paper && pdflatex paper1_cor.tex && pdflatex paper1_cor.tex
python scripts/make_submission.py        # flat, self-compiling upload package
```

Work-protocol results are deterministic and repeat bit for bit on any machine. Wall-clock results depend on the machine; ours were measured on an Apple MacBook Air M4 (4 performance and 6 efficiency cores, 16 GB, no fan). Every run is checked for feasibility to `1e-6`.

## 4. Main results

All numbers come from `results/raw/` through `scripts/analyze_revision3.py`; `results/tables/report_tables.md` has every table with confidence intervals and exact p-values.

- Portfolio coordination beats optimistic commit and quotas when capacities bind. Under the work protocol (60 test instances, 5 runs each), PC-MALNS [Greedy-Efficiency] beats rollback and sequential-lock commit on 54 to 57 of 60 instances, also when those rules receive the same portfolio, and beats static and demand-proportional quotas on all 60. A serial baseline in which the agents commit one after another (Seq-Commit, same work) is no better than the optimistic rules and loses to Greedy-Efficiency on 55 of 60 instances. Choosing among candidates is what matters. With loose capacities (η = 0.85) the optimistic rules are better.
- The exact barrier wins single epochs but not whole runs. MC-CRIP is strictly better than Greedy-Efficiency in about half of the conflict epochs and gains about a fifth more per conflict epoch, yet Greedy-Efficiency finishes better on 48 of 60 test instances and on 47 of 60 fresh instances (seeds 201–210, plan declared before the runs). The mean difference is small (0.02 to 0.03 pp).
- Against HiGHS 1.16.0. With four processes and budgets of 0.5 to 6 s, the HiGHS reference run needs 1.1 to 2.3 times the PC-MALNS time to reach its solution quality on the J = 6 instances from Large upwards, and 2.6 to 8.7 times with J = 20 or 40. HiGHS is faster on Small and Medium, better with equal CPU time on compact instances and on MCA-SC-Pair, and better with tens of seconds everywhere.
- Ablations. The borrowing level 2 pays (removing it costs 0.029 pp, 50/60 instances); level 0 is inert. Capacity prices helped on the test instances (0.03–0.04 pp) but not significantly on fresh instances (p = 0.065), so the default has no prices. Dynamic quotas give nothing, and restarts make the search slightly worse.
- MMKP is a limit, not a win. On the 26 MMKP instances with a feasible start, all LNS methods stall about 2.6% from the best known solutions (HiGHS with the same wall clock: 0.20%), because improvement-only agents cannot release capacity across agents.

## 5. Citation

```bibtex
@unpublished{naresh2026pcmalns,
  title  = {Portfolio Conflict Resolution in Concurrent Multi-Agent Large Neighborhood Search for Coupled Multiple-Choice Allocation},
  author = {R, Naresh},
  note   = {Manuscript under review. Code and data: https://github.com/Naresh23032003/PC-MALNS},
  year   = {2026}
}
```
