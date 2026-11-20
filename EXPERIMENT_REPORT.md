# Experiment report (revision 3)

This report says how every experiment of the manuscript was run and where its results are. It does not repeat the numbers: all tables, with paired-t and bootstrap confidence intervals, wins/ties/losses and exact Wilcoxon p-values (Holm-adjusted within each family), are generated into `results/tables/report_tables.md` and `results/tables/summary.json` by `scripts/analyze_revision3.py`, and every number in the manuscript comes from `summary.json` through `paper/generated_macros.tex` and `paper/tables/`.

## 1. Protocols

**Work protocol (main; `scripts/run_work_protocol.py`).** Every LNS method receives the same deterministic work budget: 25·E Regret-2 repair passes per agent, with E = 70, 70, 45, 35, 30, 25 from Small to XXXL. A portfolio epoch costs 25 passes per agent and a single-proposal epoch 10, so single-proposal methods run 2.5 times as many epochs. Barrier time is not charged. MC-CRIP calls HiGHS with a 60 s limit per solve. Every run repeats bit for bit.

**Wall-clock protocol (secondary; `scripts/run_wallclock_uniform.py`, plan `results/rerun_plan.md`).** Budgets of 0.5, 1, 1.5, 2, 4 and 6 s from Small to XXXL (2 s on MMKP) on W = 4 processes. All methods of an instance run back to back in a seeded random order. The HiGHS 1.16.0 runs are a one-thread reference run (600 s Small/Medium, 60 s Large–XXXL, 300 s rich pools, 60 s sweep, Pair and MMKP), wall-matched runs with 1 and 4 threads, CPU-matched runs, and runs with the LP-Round MIP start. A watchdog stops a HiGHS run that exceeds its limit by more than 30 s plus 10%.

## 2. Study plans

| Plan | Content | Committed |
|---|---|---|
| `results/validation_plan.md` | Greedy-Efficiency vs MC-CRIP on fresh seeds 201–210, one primary test | written before the runs, committed after them |
| `results/price_plan.md` | Best price variant vs no prices on fresh seeds 301–310 | before the runs |
| `results/rerun_plan.md` | Uniform-condition wall-clock runs, calibration and drift rule; addenda: HiGHS watchdog, sensitivity rerun of the rich-pool slow stretch | before the respective runs |

## 3. Run conditions

- Calibration (`results/raw/wall_calibration.csv`): a fixed work-protocol run at the start of every job, after every 10 instances and at the end. Its objective was identical every time.
- Three slow stretches, in which wall-clock and CPU time rose together: rich pools (calibrations 15–17, +73 to +77%), MMKP (+109 to +123%) and the end of the rich-pool rerun (+39 to +78%). No thermal warning was recorded; the machine is fanless, so silent thermal throttling is suspected but not verified. Comparisons within an instance are unaffected because all methods of an instance run back to back.
- The 40 rich-pool instances of the first stretch were rerun with the identical design (`wall_rich_rerun.csv`). Every verdict within instances is the same in both runs. The rerun slowed down again from about its 22nd instance on, so the manuscript makes no comparison across J.
- HiGHS 1.16.0 overran its time limit in presolve on the same 3 rich-pool instances in the original run and in the rerun (6 of 257 reference runs). The watchdog stopped these runs, and they contribute no dual bound.
- Two jobs paused while the machine was off mains power (sweep 2.1 h, Pair 12.0 h). No instance ran on battery.
- No HiGHS run proved optimality. Gaps are therefore upper bounds on the true gaps.

## 4. Where each result is

| Manuscript | Raw files | Section of `report_tables.md` |
|---|---|---|
| Main benchmark | `work_main.csv` | Main benchmark: work protocol |
| Serial baseline Seq-Commit | `work_seq.csv`, `work_main.csv` | Sequential baseline Seq-Commit |
| Commit-rule isolation, counterfactual, slack | `work_main.csv`, `work_commit_*.csv` | Commit-rule isolation |
| Non-conflict epochs | `work_cf_all.csv` | All-epoch counterfactual |
| Fresh barrier validation | `work_validation.csv` | Fresh validation |
| Wall clock vs HiGHS and Async-Lock, time to target, primal integral | `wall_main.csv`, `wall_reference.csv` | Main benchmark: wall-clock protocol |
| Rich pools and the sensitivity rerun | `wall_rich.csv`, `wall_rich_rerun.csv` | Rich candidate pools |
| Tightness sweep | `wall_sweep.csv`, `wall_main.csv` (η = 1.25) | Tightness sweep |
| MCA-SC-Pair (wall clock) | `wall_pair.csv` | MCA-SC-Pair |
| MMKP | `wall_mmkp.csv` | MMKP |
| Ablations | `work_levels.csv`, `work_prices.csv`, `work_prices_fresh.csv`, `work_restart.csv`, `work_rho0.csv` | Portfolio-level ablation, Price and quota ablation, Fresh price test, Restarts, rho0 |
| Lower bounds | `lower_bounds.csv` | (table in the manuscript appendix) |
| Tuning and scaling (preliminary version) | `parameter_sensitivity*.csv`, `bench_E_scaling.csv` | (tables in the manuscript appendix) |
