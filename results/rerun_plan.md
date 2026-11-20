# Wall-clock rerun under uniform machine conditions

Written on 2026-11-14, before any run of this design. Script: `scripts/run_wallclock_uniform.py`; queue: `scripts/run_uniform_queue.sh`.

## Why

The first attempt at the revision-3 wall-clock jobs ran partly on battery power. The laptop hibernated from 01:00 to 08:35 IST on 2026-11-14, and CPU times varied from 0.51x to 2.11x for runs doing identical work. Those files are archived, unused, in `results/raw/archive_2026-11-14_battery/` (see its README). Every wall-clock and matched-time result in the manuscript comes from this rerun.

The work-protocol tables (`results/raw/work_*.csv`) are deterministic and are **not** rerun.

## Machine

- Apple MacBook Air (Mac16,13), Apple M4 (4 performance and 6 efficiency cores), 16 GB. The machine is fanless, so sustained load can lower its clock speed. macOS does not record this, so the calibration job below is the measure of it.
- Python 3.11, highspy 1.16.0 (HiGHS git f3f113d).
- The run uses `caffeinate -dimsu`, and the laptop is not used while it runs. Progress is checked at most every 30 minutes.

## Design

**Interleaving.** For each instance, every compared method is run back to back:
1. The LP bound and the LP-Round start are computed once. Every method that starts from LP-Round is charged this measured LP-Round time.
2. All LNS units (method × run, 5 runs per method, W = 4 processes) run in a random order.
3. All HiGHS units run in a random order.

The orders come from `np.random.default_rng([20261114, job id, instance position])`; each row records its seed and position (`order_seed`, `order_pos`). Any drift in machine speed therefore affects all methods of an instance alike.

**Matched limits.** For each instance, the wall-matched and CPU-matched HiGHS limits are the mean wall-clock and mean CPU time of the five PC-MALNS [Greedy-Efficiency] runs of step 2 of this session. They are not taken from `bench_A.csv`.

**HiGHS units** (one thread unless stated):
- a reference run of 600 s on Small and Medium, 60 s on Large to XXXL, 300 s on the rich pools, and 60 s on the tightness sweep, MCA-SC-Pair and MMKP;
- wall-matched runs with 1 and 4 threads;
- a CPU-matched run, now a real run rather than a reading of the reference trace;
- HiGHS + LP-Round, wall-matched and CPU-matched, with the LP-Round solution as MIP start and a time limit of the matched time minus the LP-Round time. Not run on MMKP, because its LP-Round start leaves groups unassigned.

HiGHS (5 s), (30 s) and (60 s) are read from the reference trace.

**Calibration.** A fixed job runs at the start of every job, after every 10 instances, and at the end:
- PC-MALNS [Greedy-Efficiency] on Large seed 101, run 0;
- work protocol with 1,125 repair passes per worker, on the W = 4 pool.

Its wall-clock and CPU time go to `results/raw/wall_calibration.csv`, together with the objective, which must be identical every time. A deviation of more than 10% in wall-clock or CPU time from the first calibration of the run is flagged in the file and the log, and reported. The run is not stopped, and no rows are excluded because of drift.

**Machine state per row.** Every row records:
- the time stamp;
- the power source and battery charge (`pmset -g batt`);
- the 1-, 5- and 15-minute load averages, which include the run's own load;
- the index of the latest calibration;
- the HiGHS version.

Before every unit the power source is checked. On battery power the run pauses until AC power returns, logs the pause and records the waiting time (`ac_wait_s`).

**Resumption.** Rows are written per instance, after all of its units. An interrupted instance is rerun from the start, and a finished instance is never rerun.

## What runs, in order

**Phase 1** (`main`): 60 instances (P = 6, η = 1.25, Small to XXXL, seeds 101–110), with wall-clock budgets of 0.5, 1, 1.5, 2, 4 and 6 s.
- LNS: PC-MALNS [Greedy-Efficiency], PC-MALNS [MC-CRIP], Opt-Rollback, Opt-SeqLock and Async-Lock, 5 runs each on W = 4. MC-CRIP has a 2 s limit per solve.
- LP-Round.
- All HiGHS units above.

**Phase 2**, with the same interleaving and calibration, keeping the method sets of the revision-2 tables:
- `rich`: P = 20 and 40, Medium to XXL, seeds 101–110 (80 instances). Methods: Greedy-Efficiency, MC-CRIP, Quota-Surplus, Opt-Rollback, Opt-SeqLock.
- `sweep`: Large, η ∈ {0.85, 1.05, 1.45}, seeds 101–110 (30 instances). Methods: the five above and Static-Quota.
- `pair`: MCA-SC-Pair, Medium and Large, seeds 101–110 (20 instances). Methods: the four PC-MALNS barrier rules, Opt-Rollback-Portfolio, Opt-SeqLock-Portfolio, Opt-Rollback, Opt-SeqLock.
- `mmkp`: the 27 MMKP instances, K = 8, 2 s budget. Methods: Greedy-Efficiency, MC-CRIP, Quota-Surplus, Opt-Rollback, Opt-SeqLock, Static-Quota.

**Phase 3** (work protocol, after all wall-clock jobs; `scripts/run_work_protocol.py`):
- `prices_fresh`: the price validation on seeds 301–310, following `results/price_plan.md`.
- `rho0`: PC-MALNS [Greedy-Efficiency] with ρ₀ = 0, 60 instances (seeds 101–110), 5 runs.
- Level-0 diagnostics: the engine counts, per run, the level-0 donor attempts (`l0_tries`), the attempts whose donor dominates the incumbent (`l0_dominated`) and those that were committed (`l0_committed`). The counters read only the deltas the engine already receives. Ten reruns of stored work-protocol runs gave bit-identical results with them. They are recorded in every row of this rerun and of phase 3.

## Outputs

- Phases 1 and 2: `results/raw/wall_<job>.csv`, `wall_reference.csv` and `wall_calibration.csv`, with logs in `results/logs/uniform_<job>.log`.
- Phase 3: `results/raw/work_prices_fresh.csv` and `work_rho0.csv`.

## Addendum, 2026-11-17: HiGHS watchdog

**What happened.** Phase 1 (`main`, 60 instances) and the first 22 instances of `rich` finished without incident. Every calibration gave the same objective, no drift flag was raised, and the run never paused for battery power. On `MCA_SC_K16_N960_P20_eta1.25_s103`, the 1-thread 300 s reference run of HiGHS 1.16.0 ignored its time limit. After 10.9 h it was still in `presolve::HPresolve::strengthenInequalities`, inside nested RINS sub-MIPs (from a stack sample). The queue was stopped at 17:30 IST. A rerun of that unit hung again, so the hang is deterministic. The 492 HiGHS runs completed before the hang all stopped within 0.14 s of their limits.

**Change.**
- `src/highs_runner.py` now streams every HiGHS incumbent to a file, and kills a solve once it runs 30 s + 10% of its limit past that limit.
- A killed run records:
  - status `killed (watchdog)` and `highs_killed = True`;
  - the last incumbent found within the time limit, taken from the streamed trace;
  - no dual bound;
  - `highs_actual_time_s` equal to the time limit.
- For such an instance, the lower bound uses the LP bound and the other available HiGHS dual bounds (`lower_bounds.csv` records the source).
- The column `highs_killed` was added to `wall_rich.csv` and `wall_reference.csv`. It is empty for earlier rows, all of which finished within their limits.

Nothing else changes. Finished instances are kept, and the interrupted instance s103 is rerun from the start, as the resumption rule above provides.

## Addendum, 2026-11-20: sensitivity rerun of the slow stretch in `rich`

Written after phases 1 to 3 finished and before any run of this addendum.

**What happened.** Calibrations 15, 16 and 17 of `rich` (17 Nov, 21:03 to 23:11 IST) were 73 to 77% slower in both wall-clock and CPU time than the first calibration. Calibration 14 (19:57) and calibration 18 (00:11) were normal. The objective was identical every time. macOS recorded no thermal or performance warning, and the machine stayed on AC power. The slow stretch coincides with whole cells of the design: every Medium and Large instance with P = 40 ran slow, and every Medium and Large instance with P = 20 ran at normal speed. Comparisons within an instance are not affected, because all methods of an instance ran back to back. Absolute times and any comparison across P are.

**What is rerun.** Every `rich` instance whose rows carry calibration index 14, 15, 16 or 17: the 40 instances run between the last normal calibration before the slow stretch and the first normal one after it. The rule uses only the calibration indices, not the results. Job `rich_rerun` in `scripts/run_wallclock_uniform.py` reruns them with the identical design: the same methods, budgets, HiGHS units, 300 s reference run and random orders (the same order seeds). Calibration runs at the start, after every 10 instances and at the end, as in the main design.

**Outputs.** `results/raw/wall_rich_rerun.csv`; reference runs are appended to `wall_reference.csv` with `job = rich_rerun`.

**Use.** The original `rich` rows remain the primary result, as the drift rule of this plan requires; no row is excluded. The rerun is reported next to them as a sensitivity analysis: per-instance verdicts in both runs, and absolute times and gaps from the rerun where the original instance ran in the slow stretch. Any comparison across P on the `rich` pools uses the rerun rows for these 40 instances and states so.
