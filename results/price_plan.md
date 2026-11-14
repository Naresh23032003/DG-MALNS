# Fresh validation of capacity prices (seeds 301–310)

Written on 2026-11-14, before any run on seeds 301–310. These seeds have not been generated or used for any earlier run: no file in `results/` or `data/` names an instance `*_s301` to `*_s310`.

**Why.** The recommended configuration, PC-MALNS [Greedy-Efficiency], uses no capacity prices (lambda = 0) and a static quota. The price/quota ablation on the test seeds 101–110 (`results/raw/work_prices.csv`) compared six variants with it under the work protocol. The variant with MC-CRIP LP prices and a static quota was best: its mean gap was 0.040 pp lower, on 49 of 60 instances, with an exact Wilcoxon p = 2e-6. Choosing that variant out of six after seeing test results is a selection on test data. This study checks the choice on new instances.

**Instances.** MCA-SC, P = 6, eta = 1.25. Six scales (Small, Medium, Large, X-Large, XXL, XXXL) with seeds 301–310 each: 60 instances.

**Methods.** Two variants, run 5 times each (rep 0–4) under the work protocol of `scripts/run_work_protocol.py`, table `prices_fresh`:
- **Current:** PC-MALNS [Greedy-Efficiency], prices = none, quota = static (the recommended configuration).
- **Prices:** PC-MALNS [Greedy-Efficiency], prices = mccrip_lp, quota = static.

Both use the work budget of their scale, the LP-Round start and identical random streams. Everything else is unchanged.

**Measure.** For each instance, the mean over the 5 runs of `100 (C - LP) / LP`, where LP is the bound of the instance's LP relaxation. Because the comparison is paired, the bound affects only the scale of the differences.

**Hypothesis (the only one).** The Prices variant has a different mean gap from the Current variant. The test is an exact two-sided Wilcoxon signed-rank test over the 60 per-instance differences (Prices minus Current) at alpha = 0.05: zero differences dropped, mid-ranks, exact conditional null distribution.

**Also reported.**
- The mean difference, with a paired Student-t 95% interval and a bootstrap 95% interval (10,000 resamples over instances, fixed seed 0).
- Wins, ties and losses.
- Descriptive only, with no tests:
  - results per scale;
  - wall-clock, CPU and barrier time of both variants, since the work protocol does not charge the time spent computing prices.

**Decision.**
- **Prices significantly better** (p < 0.05 and a negative mean difference): the recommended configuration becomes PC-MALNS [Greedy-Efficiency] with MC-CRIP LP prices and a static quota. The paper states that this choice was made after the test seeds and confirmed here. The tables on seeds 101–110 keep both variants as they were run.
- **Prices significantly worse** (p < 0.05 and a positive mean difference): the recommendation stays lambda = 0. The paper reports that the advantage seen on the test seeds did not replicate.
- **No significant difference** (p >= 0.05): the recommendation stays lambda = 0, which is simpler and needs no LP solve per epoch. The paper reports no detected difference on fresh instances.

The result is reported whatever it is. This study runs in phase 3 of `results/rerun_plan.md`, after all wall-clock jobs.
