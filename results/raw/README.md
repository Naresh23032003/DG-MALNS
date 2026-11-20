# Raw results

Each file here is written by the scripts listed below, and nothing has been edited by hand. In revision 3, method and instance labels were renamed in the older files: `PC-MALNS [BCRM-Greedy]` became `PC-MALNS [Quota-Surplus]`, `Greedy-Efficiency-Portfolio` became `PC-MALNS [Greedy-Efficiency]`, and `RPA_SH_` became `MCA_SC_`. No number was changed.

Gaps are recomputed in `scripts/analyze_revision3.py` from `best_obj` and `lower_bounds.csv`. The `gap_pct` and `lower_bound` columns stored in some files use the lower bounds that were available when those runs were made. The column `P` is the number of patterns per request, called `J` in the manuscript.

## Used by the manuscript (revision 3)

### Work protocol (deterministic work budget; `scripts/run_work_protocol.py <table>`)

| File | Content |
|---|---|
| `work_main.csv` | Main benchmark: all LNS methods, 60 test instances (seeds 101–110), 5 runs each |
| `work_commit_direct.csv`, `work_commit_pair.csv` | Commit-rule isolation: direct start and MCA-SC-Pair (Medium, Large) |
| `work_cf_all.csv` | The GE and MC-CRIP runs of `work_main.csv`, repeated with every barrier rule logged in every epoch; the best objective is identical to `work_main.csv` in all 600 runs |
| `work_validation.csv` | Fresh barrier validation on seeds 201–210 (plan: `../validation_plan.md`) |
| `work_levels.csv`, `work_prices.csv`, `work_restart.csv`, `work_rho0.csv` | Ablations of the portfolio levels, prices and quotas, restarts, and ρ0 = 0 (60 test instances) |
| `work_prices_fresh.csv` | Fresh price validation on seeds 301–310 (plan: `../price_plan.md`) |

### Wall-clock protocol under uniform machine conditions (`scripts/run_wallclock_uniform.py <job>`; plan: `../rerun_plan.md`)

| File | Content |
|---|---|
| `wall_main.csv` | Main benchmark (J = 6): LNS methods, Async-Lock, LP-Round and all matched HiGHS 1.16.0 runs |
| `wall_rich.csv` | Rich candidate pools, J = 20 and 40 |
| `wall_rich_rerun.csv` | Sensitivity rerun of the 40 rich-pool instances of the first slow stretch (addendum of `../rerun_plan.md`) |
| `wall_sweep.csv` | Coupling-tightness sweep on Large, η = 0.85, 1.05, 1.45 |
| `wall_pair.csv` | MCA-SC-Pair |
| `wall_mmkp.csv` | MMKP benchmarks |
| `wall_reference.csv` | One-thread HiGHS 1.16.0 reference runs with incumbent traces (`highs_killed`: stopped by the watchdog) |
| `wall_calibration.csv` | Calibration runs with power source, load and drift |
| `lower_bounds.csv` | Final lower bound of every test instance and its source (`scripts/build_lower_bounds.py`) |

## Carried over from revision 2

| File | Use |
|---|---|
| `bench_reference.csv` | HiGHS 1.8.0 reference runs; their dual bounds enter `lower_bounds.csv` |
| `bench_E_scaling.csv` | Parallel scaling (appendix of the manuscript) |
| `parameter_sensitivity*.csv`, `pilot_*.csv` | Validation pilot and parameter tuning on seeds 1–10 (appendix) |
| `diag_slack.csv` | Revision-2 wall-clock reruns; only the repeatability summary in `results/tables/report_tables.md` uses them |

## Superseded, kept for the record

The manuscript does not use these files.
- `bench_A.csv`, `bench_B.csv`, `bench_C_direct.csv`, `bench_C_sync.csv`, `bench_D_mmkp.csv`, `bench_E_ablation.csv`, `bench_E_sweep.csv`, `bench_sync_check.csv`: the revision-2 wall-clock runs (HiGHS 1.8.0, non-uniform machine conditions), replaced by the `wall_*.csv` and `work_*.csv` files.
- `archive_2026-11-14_battery/`: the first attempt at the revision-3 wall-clock jobs, set aside because the machine ran on battery and hibernated (see its README).
