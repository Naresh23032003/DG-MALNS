# Archived wall-clock runs of 2026-11-13/14 (not used by the manuscript)

These files hold the first attempt at the revision-3 wall-clock jobs. They are kept so that the record is complete. The manuscript does not use them: every wall-clock and matched-time experiment was rerun under uniform machine conditions (`../../rerun_plan.md`).

## Why they were set aside

1. **Battery drain and hibernation.** The laptop ran on battery while the queue was running. At 01:00:48 IST on 2026-11-14 the charge reached 1% and macOS entered "Low Power Sleep", then hibernated until 08:35:28 IST. This comes from `pmset -g log`. The HiGHS runs on `MCA_SC_K4_N120_P6_eta1.25_s105` straddled the hibernation, and their results are inconsistent: the 4-thread wall-matched run reached 7607.5, against 7372.0 with one thread. Those rows were deleted at 08:40 IST, before the files were archived, and the queue was restarted under `caffeinate -ims`. The restarted queue was stopped again before it completed any instance.
2. **Machine conditions were not uniform.** Some pairs of work-protocol runs do the same work, with the same epochs and the same final solution:
   - the `levels {1,2,3}` rows of `work_levels.csv`;
   - the corresponding `PC-MALNS [Greedy-Efficiency]` rows of `work_main.csv`.

   Across the 299 such run pairs, the ratio of their CPU times ranged from 0.51x to 2.11x (median 0.84x). The objective values of the work protocol are deterministic and remain valid. Time-limited results, such as those of HiGHS and Async-Lock, are not.

   The matched HiGHS limits in these files were also derived from the revision-2 wall-clock runs in `bench_A.csv`, not from runs in the same session.

## Contents

| File | Content |
|---|---|
| `highs116_main.csv`, `highs116_reference.csv` | HiGHS 1.16.0 runs on `MCA_SC_*_s101` to `_s104` (Small) |
| `wall_async.csv` | Async-Lock under the wall-clock protocol, 60 instances (finished at 00:11 IST, before the hibernation) |
| `logs/` | Copies of the run logs |
