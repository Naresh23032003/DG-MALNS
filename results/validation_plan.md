# Fresh validation of the barrier rule (seeds 201–210)

Written on 2026-11-13, before any run on seeds 201–210. These seeds had not been generated or used for any earlier run.

**Why.** On validation seeds 1–3, MC-CRIP and Greedy-Efficiency tied (2.038% vs 2.031%, exact Wilcoxon p = 0.84). On test seeds 101–110, Greedy-Efficiency was better in every family. Choosing Greedy-Efficiency as the recommended barrier after seeing the test seeds is a selection on test data. This study checks that choice on new instances.

**Instances.** MCA-SC, P = 6, eta = 1.25. Six scales, Small to XXXL, with seeds 201–210 each: 60 instances in total.

**Methods.** Three variants, run 5 times each (rep 0–4) under the work protocol of `scripts/run_work_protocol.py`, table `validation`:
- PC-MALNS [Greedy-Efficiency]
- PC-MALNS [MC-CRIP]
- PC-MALNS [Quota-Surplus]

Everything else is unchanged.

**Measure.** For each instance, the mean over the 5 runs of `100 (C - LP) / LP`, where LP is the bound of the instance's LP relaxation. Because the comparisons are paired, the bound affects only the scale of the differences.

**Primary hypothesis.** PC-MALNS [Greedy-Efficiency] has a lower mean gap than PC-MALNS [MC-CRIP]. The test is an exact two-sided Wilcoxon signed-rank test over the 60 instances at alpha = 0.05.

**Secondary analyses.** The comparison of Greedy-Efficiency with Quota-Surplus is reported with Holm's adjustment over the two tests. Per-scale results are descriptive only.

**Decision.**
- If the primary hypothesis holds, Greedy-Efficiency is confirmed as the recommended barrier.
- If MC-CRIP is significantly better, the recommendation reverts to MC-CRIP.
- If neither is significantly better, the paper reports a tie and recommends Greedy-Efficiency only because it is cheaper.

The result is reported whatever it is.
