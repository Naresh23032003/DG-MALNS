
## Main benchmark: work protocol (P = 6, η = 1.25, seeds 101–110)


**Mean gap (%) by scale**

| method | Small | Medium | Large | X-Large | XXL | XXXL | All |
|---|---|---|---|---|---|---|---|
| LP-Round | 5.055 | 3.652 | 3.032 | 2.592 | 1.609 | 1.306 | 2.874 |
| PC-MALNS [Greedy-Efficiency] | 2.523 | 1.779 | 1.562 | 1.361 | 0.870 | 0.713 | 1.468 |
| PC-MALNS [MC-CRIP] | 2.510 | 1.812 | 1.639 | 1.392 | 0.895 | 0.729 | 1.496 |
| PC-MALNS [Quota-Surplus] | 2.516 | 1.854 | 1.627 | 1.405 | 0.899 | 0.733 | 1.506 |
| PC-MALNS [Greedy-Gain] | 2.561 | 1.807 | 1.639 | 1.427 | 0.943 | 0.792 | 1.528 |
| Opt-Rollback-Portfolio | 2.686 | 2.021 | 1.794 | 1.552 | 1.039 | 0.875 | 1.661 |
| Opt-SeqLock-Portfolio | 2.577 | 2.010 | 1.783 | 1.554 | 0.996 | 0.814 | 1.622 |
| Opt-Rollback | 2.689 | 2.025 | 1.779 | 1.565 | 1.043 | 0.872 | 1.662 |
| Opt-SeqLock | 2.564 | 2.029 | 1.790 | 1.586 | 1.018 | 0.837 | 1.637 |
| Static-Quota | 4.141 | 3.093 | 2.590 | 2.209 | 1.380 | 1.139 | 2.425 |
| Demand-Quota | 3.764 | 2.842 | 2.381 | 2.017 | 1.280 | 1.043 | 2.221 |

**Main (work protocol): PC-MALNS [Greedy-Efficiency] vs each method** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| LP-Round | 60 | 1.468 | 2.874 | -1.407 [-1.597, -1.216] | [-1.592, -1.228] | 60/0/0 | <1e-4 | <1e-4 |
| PC-MALNS [MC-CRIP] | 60 | 1.468 | 1.496 | -0.028 [-0.043, -0.013] | [-0.042, -0.013] | 48/0/12 | <1e-4 | <1e-4 |
| PC-MALNS [Quota-Surplus] | 60 | 1.468 | 1.506 | -0.038 [-0.054, -0.021] | [-0.053, -0.022] | 51/0/9 | <1e-4 | <1e-4 |
| PC-MALNS [Greedy-Gain] | 60 | 1.468 | 1.528 | -0.060 [-0.082, -0.039] | [-0.081, -0.039] | 52/0/8 | <1e-4 | <1e-4 |
| Opt-Rollback-Portfolio | 60 | 1.468 | 1.661 | -0.193 [-0.225, -0.162] | [-0.224, -0.162] | 56/0/4 | <1e-4 | <1e-4 |
| Opt-SeqLock-Portfolio | 60 | 1.468 | 1.622 | -0.155 [-0.183, -0.126] | [-0.181, -0.126] | 56/0/4 | <1e-4 | <1e-4 |
| Opt-Rollback | 60 | 1.468 | 1.662 | -0.194 [-0.226, -0.162] | [-0.226, -0.164] | 57/0/3 | <1e-4 | <1e-4 |
| Opt-SeqLock | 60 | 1.468 | 1.637 | -0.170 [-0.202, -0.137] | [-0.201, -0.138] | 54/0/6 | <1e-4 | <1e-4 |
| Static-Quota | 60 | 1.468 | 2.425 | -0.957 [-1.077, -0.838] | [-1.072, -0.845] | 60/0/0 | <1e-4 | <1e-4 |
| Demand-Quota | 60 | 1.468 | 2.221 | -0.753 [-0.846, -0.660] | [-0.842, -0.665] | 60/0/0 | <1e-4 | <1e-4 |

**Main (work protocol): PC-MALNS [MC-CRIP] vs each LNS method** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| PC-MALNS [Greedy-Efficiency] | 60 | 1.496 | 1.468 | +0.028 [+0.013, +0.043] | [+0.013, +0.042] | 12/0/48 | <1e-4 | <1e-4 |
| PC-MALNS [Quota-Surplus] | 60 | 1.496 | 1.506 | -0.010 [-0.023, +0.004] | [-0.023, +0.004] | 39/0/21 | 0.0717 | 0.0717 |
| PC-MALNS [Greedy-Gain] | 60 | 1.496 | 1.528 | -0.032 [-0.052, -0.013] | [-0.052, -0.014] | 46/0/14 | 0.0007 | 0.0015 |
| Opt-Rollback-Portfolio | 60 | 1.496 | 1.661 | -0.165 [-0.193, -0.137] | [-0.193, -0.138] | 57/0/3 | <1e-4 | <1e-4 |
| Opt-SeqLock-Portfolio | 60 | 1.496 | 1.622 | -0.126 [-0.152, -0.101] | [-0.150, -0.101] | 56/0/4 | <1e-4 | <1e-4 |
| Opt-Rollback | 60 | 1.496 | 1.662 | -0.166 [-0.197, -0.135] | [-0.196, -0.136] | 58/0/2 | <1e-4 | <1e-4 |
| Opt-SeqLock | 60 | 1.496 | 1.637 | -0.141 [-0.170, -0.113] | [-0.169, -0.114] | 55/0/5 | <1e-4 | <1e-4 |
| Static-Quota | 60 | 1.496 | 2.425 | -0.929 [-1.051, -0.808] | [-1.046, -0.814] | 60/0/0 | <1e-4 | <1e-4 |
| Demand-Quota | 60 | 1.496 | 2.221 | -0.725 [-0.820, -0.630] | [-0.816, -0.635] | 60/0/0 | <1e-4 | <1e-4 |

**Epochs per run**

| method | Small | Medium | Large | X-Large | XXL | XXXL | All |
|---|---|---|---|---|---|---|---|
| Demand-Quota | 175.0 | 175.0 | 112.0 | 87.0 | 75.0 | 62.0 | 114.3 |
| Opt-Rollback | 175.0 | 175.0 | 112.0 | 87.0 | 75.0 | 62.0 | 114.3 |
| Opt-Rollback-Portfolio | 70.0 | 70.0 | 45.0 | 35.0 | 30.0 | 25.0 | 45.8 |
| Opt-SeqLock | 175.0 | 175.0 | 112.0 | 87.0 | 75.0 | 62.0 | 114.3 |
| Opt-SeqLock-Portfolio | 70.0 | 70.0 | 45.0 | 35.0 | 30.0 | 25.0 | 45.8 |
| PC-MALNS [Greedy-Efficiency] | 70.0 | 70.0 | 45.0 | 35.0 | 30.0 | 25.0 | 45.8 |
| PC-MALNS [Greedy-Gain] | 70.0 | 70.0 | 45.0 | 35.0 | 30.0 | 25.0 | 45.8 |
| PC-MALNS [MC-CRIP] | 70.0 | 70.0 | 45.0 | 35.0 | 30.0 | 25.0 | 45.8 |
| PC-MALNS [Quota-Surplus] | 70.0 | 70.0 | 45.0 | 35.0 | 30.0 | 25.0 | 45.8 |
| Static-Quota | 175.0 | 175.0 | 112.0 | 87.0 | 75.0 | 62.0 | 114.3 |

**Barrier time per conflict epoch (ms)**

| method | Small | Medium | Large | X-Large | XXL | XXXL | All |
|---|---|---|---|---|---|---|---|
| Opt-Rollback | 0.03 | 0.04 | 0.05 | 0.06 | 0.05 | 0.06 | 0.05 |
| Opt-Rollback-Portfolio | 0.04 | 0.05 | 0.06 | 0.06 | 0.06 | 0.06 | 0.05 |
| Opt-SeqLock | 0.02 | 0.03 | 0.05 | 0.06 | 0.06 | 0.07 | 0.05 |
| Opt-SeqLock-Portfolio | 0.02 | 0.04 | 0.05 | 0.06 | 0.07 | 0.09 | 0.06 |
| PC-MALNS [Greedy-Efficiency] | 0.04 | 0.07 | 0.12 | 0.16 | 0.20 | 0.24 | 0.14 |
| PC-MALNS [Greedy-Gain] | 0.03 | 0.05 | 0.09 | 0.12 | 0.14 | 0.17 | 0.10 |
| PC-MALNS [MC-CRIP] | 0.18 | 4.82 | 18.36 | 54.55 | 157.54 | 241.50 | 79.49 |
| PC-MALNS [Quota-Surplus] | 0.05 | 0.08 | 0.12 | 0.16 | 0.18 | 0.22 | 0.14 |

**Conflict epochs (% of epochs)**

| method | Small | Medium | Large | X-Large | XXL | XXXL | All |
|---|---|---|---|---|---|---|---|
| Demand-Quota | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Opt-Rollback | 2.8 | 6.9 | 15.8 | 25.9 | 34.6 | 51.8 | 23.0 |
| Opt-Rollback-Portfolio | 7.0 | 16.7 | 36.6 | 57.2 | 79.8 | 95.8 | 48.8 |
| Opt-SeqLock | 1.9 | 3.9 | 7.5 | 11.2 | 14.7 | 17.9 | 9.5 |
| Opt-SeqLock-Portfolio | 4.9 | 8.7 | 16.3 | 23.0 | 30.3 | 35.4 | 19.8 |
| PC-MALNS [Greedy-Efficiency] | 3.5 | 6.9 | 13.2 | 16.6 | 20.7 | 25.6 | 14.4 |
| PC-MALNS [Greedy-Gain] | 3.7 | 6.3 | 11.7 | 16.4 | 22.0 | 26.4 | 14.4 |
| PC-MALNS [MC-CRIP] | 3.6 | 5.5 | 9.6 | 13.3 | 14.9 | 18.5 | 10.9 |
| PC-MALNS [Quota-Surplus] | 4.1 | 6.9 | 13.7 | 18.2 | 21.9 | 25.0 | 15.0 |
| Static-Quota | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

**Per scale (Holm over the 18 tests): Greedy-Efficiency vs the other barriers** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| Small: PC-MALNS [MC-CRIP] | 10 | 2.523 | 2.510 | +0.013 [-0.053, +0.079] | [-0.033, +0.074] | 6/0/4 | 0.9219 | 1.0000 |
| Small: PC-MALNS [Quota-Surplus] | 10 | 2.523 | 2.516 | +0.007 [-0.066, +0.080] | [-0.053, +0.069] | 5/0/5 | 0.8457 | 1.0000 |
| Small: PC-MALNS [Greedy-Gain] | 10 | 2.523 | 2.561 | -0.038 [-0.157, +0.080] | [-0.137, +0.058] | 6/0/4 | 0.6250 | 1.0000 |
| Medium: PC-MALNS [MC-CRIP] | 10 | 1.779 | 1.812 | -0.033 [-0.079, +0.013] | [-0.073, +0.003] | 6/0/4 | 0.2754 | 1.0000 |
| Medium: PC-MALNS [Quota-Surplus] | 10 | 1.779 | 1.854 | -0.075 [-0.125, -0.025] | [-0.120, -0.039] | 9/0/1 | 0.0039 | 0.0508 |
| Medium: PC-MALNS [Greedy-Gain] | 10 | 1.779 | 1.807 | -0.029 [-0.093, +0.036] | [-0.082, +0.023] | 7/0/3 | 0.4316 | 1.0000 |
| Large: PC-MALNS [MC-CRIP] | 10 | 1.562 | 1.639 | -0.077 [-0.119, -0.034] | [-0.112, -0.041] | 10/0/0 | 0.0020 | 0.0352 |
| Large: PC-MALNS [Quota-Surplus] | 10 | 1.562 | 1.627 | -0.065 [-0.114, -0.016] | [-0.103, -0.021] | 9/0/1 | 0.0195 | 0.1367 |
| Large: PC-MALNS [Greedy-Gain] | 10 | 1.562 | 1.639 | -0.077 [-0.117, -0.036] | [-0.111, -0.045] | 10/0/0 | 0.0020 | 0.0352 |
| X-Large: PC-MALNS [MC-CRIP] | 10 | 1.361 | 1.392 | -0.031 [-0.059, -0.003] | [-0.053, -0.008] | 8/0/2 | 0.0488 | 0.2930 |
| X-Large: PC-MALNS [Quota-Surplus] | 10 | 1.361 | 1.405 | -0.045 [-0.064, -0.026] | [-0.060, -0.028] | 9/0/1 | 0.0039 | 0.0508 |
| X-Large: PC-MALNS [Greedy-Gain] | 10 | 1.361 | 1.427 | -0.067 [-0.100, -0.033] | [-0.093, -0.038] | 9/0/1 | 0.0059 | 0.0527 |
| XXL: PC-MALNS [MC-CRIP] | 10 | 0.870 | 0.895 | -0.025 [-0.037, -0.014] | [-0.035, -0.015] | 9/0/1 | 0.0039 | 0.0508 |
| XXL: PC-MALNS [Quota-Surplus] | 10 | 0.870 | 0.899 | -0.030 [-0.042, -0.017] | [-0.040, -0.020] | 10/0/0 | 0.0020 | 0.0352 |
| XXL: PC-MALNS [Greedy-Gain] | 10 | 0.870 | 0.943 | -0.074 [-0.100, -0.047] | [-0.097, -0.053] | 10/0/0 | 0.0020 | 0.0352 |
| XXXL: PC-MALNS [MC-CRIP] | 10 | 0.713 | 0.729 | -0.016 [-0.028, -0.005] | [-0.026, -0.007] | 9/0/1 | 0.0098 | 0.0781 |
| XXXL: PC-MALNS [Quota-Surplus] | 10 | 0.713 | 0.733 | -0.020 [-0.030, -0.010] | [-0.027, -0.011] | 9/0/1 | 0.0039 | 0.0508 |
| XXXL: PC-MALNS [Greedy-Gain] | 10 | 0.713 | 0.792 | -0.079 [-0.096, -0.062] | [-0.093, -0.065] | 10/0/0 | 0.0020 | 0.0352 |

- Mean standard deviation of the gap over the 5 runs of an instance (pp): Demand-Quota 0.089, Opt-Rollback 0.119, Opt-Rollback-Portfolio 0.117, Opt-SeqLock 0.120, Opt-SeqLock-Portfolio 0.127, PC-MALNS [Greedy-Efficiency] 0.113, PC-MALNS [Greedy-Gain] 0.109, PC-MALNS [MC-CRIP] 0.111, PC-MALNS [Quota-Surplus] 0.113, Static-Quota 0.078

## Commit-rule isolation: work protocol (Medium + Large)


**LP-Round start: mean gap (%)**

| method | Medium | Large | All |
|---|---|---|---|
| PC-MALNS [Greedy-Efficiency] | 1.779 | 1.562 | 1.670 |
| PC-MALNS [MC-CRIP] | 1.812 | 1.639 | 1.725 |
| PC-MALNS [Quota-Surplus] | 1.854 | 1.627 | 1.740 |
| PC-MALNS [Greedy-Gain] | 1.807 | 1.639 | 1.723 |
| Opt-Rollback-Portfolio | 2.021 | 1.794 | 1.907 |
| Opt-SeqLock-Portfolio | 2.010 | 1.783 | 1.896 |
| Opt-Rollback | 2.025 | 1.779 | 1.902 |
| Opt-SeqLock | 2.029 | 1.790 | 1.909 |

**LP-Round start: conflict epochs (%)**

| method | Medium | Large | All |
|---|---|---|---|
| PC-MALNS [Greedy-Efficiency] | 6.9 | 13.2 | 10.0 |
| PC-MALNS [MC-CRIP] | 5.5 | 9.6 | 7.5 |
| PC-MALNS [Quota-Surplus] | 6.9 | 13.7 | 10.3 |
| PC-MALNS [Greedy-Gain] | 6.3 | 11.7 | 9.0 |
| Opt-Rollback-Portfolio | 16.7 | 36.6 | 26.6 |
| Opt-SeqLock-Portfolio | 8.7 | 16.3 | 12.5 |
| Opt-Rollback | 6.9 | 15.8 | 11.4 |
| Opt-SeqLock | 3.9 | 7.5 | 5.7 |

**Direct start: mean gap (%)**

| method | Medium | Large | All |
|---|---|---|---|
| PC-MALNS [Greedy-Efficiency] | 5.173 | 5.711 | 5.442 |
| PC-MALNS [MC-CRIP] | 5.757 | 5.935 | 5.846 |
| PC-MALNS [Quota-Surplus] | 5.541 | 5.771 | 5.656 |
| PC-MALNS [Greedy-Gain] | 6.002 | 6.123 | 6.062 |
| Opt-Rollback-Portfolio | 7.429 | 8.847 | 8.138 |
| Opt-SeqLock-Portfolio | 7.312 | 7.928 | 7.620 |
| Opt-Rollback | 7.088 | 7.169 | 7.129 |
| Opt-SeqLock | 7.375 | 7.396 | 7.386 |

**Direct start: conflict epochs (%)**

| method | Medium | Large | All |
|---|---|---|---|
| PC-MALNS [Greedy-Efficiency] | 16.6 | 33.8 | 25.2 |
| PC-MALNS [MC-CRIP] | 14.1 | 29.6 | 21.9 |
| PC-MALNS [Quota-Surplus] | 17.1 | 36.0 | 26.6 |
| PC-MALNS [Greedy-Gain] | 15.9 | 35.8 | 25.9 |
| Opt-Rollback-Portfolio | 41.7 | 92.2 | 67.0 |
| Opt-SeqLock-Portfolio | 15.3 | 39.9 | 27.6 |
| Opt-Rollback | 17.0 | 43.8 | 30.4 |
| Opt-SeqLock | 7.2 | 19.4 | 13.3 |

**MCA-SC-Pair: mean gap (%)**

| method | Medium | Large | All |
|---|---|---|---|
| PC-MALNS [Greedy-Efficiency] | 2.159 | 1.821 | 1.990 |
| PC-MALNS [MC-CRIP] | 2.219 | 1.908 | 2.063 |
| PC-MALNS [Quota-Surplus] | 2.256 | 1.870 | 2.063 |
| PC-MALNS [Greedy-Gain] | 2.219 | 1.933 | 2.076 |
| Opt-Rollback-Portfolio | 2.428 | 2.110 | 2.269 |
| Opt-SeqLock-Portfolio | 2.393 | 2.062 | 2.228 |
| Opt-Rollback | 2.413 | 2.119 | 2.266 |
| Opt-SeqLock | 2.411 | 2.084 | 2.247 |

**MCA-SC-Pair: conflict epochs (%)**

| method | Medium | Large | All |
|---|---|---|---|
| PC-MALNS [Greedy-Efficiency] | 6.9 | 14.9 | 10.9 |
| PC-MALNS [MC-CRIP] | 5.9 | 10.6 | 8.2 |
| PC-MALNS [Quota-Surplus] | 8.3 | 14.6 | 11.4 |
| PC-MALNS [Greedy-Gain] | 6.9 | 13.1 | 10.0 |
| Opt-Rollback-Portfolio | 18.3 | 42.7 | 30.5 |
| Opt-SeqLock-Portfolio | 8.3 | 16.4 | 12.3 |
| Opt-Rollback | 7.3 | 18.2 | 12.7 |
| Opt-SeqLock | 3.7 | 7.3 | 5.5 |

**LP-Round start: PC-MALNS [Greedy-Efficiency] vs each commit rule (Holm over all regimes)** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| PC-MALNS [MC-CRIP] | 20 | 1.670 | 1.725 | -0.055 [-0.085, -0.025] | [-0.082, -0.028] | 16/0/4 | 0.0023 | 0.0093 |
| PC-MALNS [Quota-Surplus] | 20 | 1.670 | 1.740 | -0.070 [-0.102, -0.038] | [-0.099, -0.042] | 18/0/2 | 0.0002 | 0.0012 |
| PC-MALNS [Greedy-Gain] | 20 | 1.670 | 1.723 | -0.053 [-0.089, -0.016] | [-0.086, -0.020] | 17/0/3 | 0.0083 | 0.0219 |
| Opt-Rollback-Portfolio | 20 | 1.670 | 1.907 | -0.237 [-0.281, -0.193] | [-0.277, -0.198] | 20/0/0 | <1e-4 | <1e-4 |
| Opt-SeqLock-Portfolio | 20 | 1.670 | 1.896 | -0.226 [-0.256, -0.196] | [-0.253, -0.199] | 20/0/0 | <1e-4 | <1e-4 |
| Opt-Rollback | 20 | 1.670 | 1.902 | -0.232 [-0.276, -0.188] | [-0.272, -0.191] | 19/0/1 | <1e-4 | <1e-4 |
| Opt-SeqLock | 20 | 1.670 | 1.909 | -0.239 [-0.279, -0.199] | [-0.276, -0.204] | 20/0/0 | <1e-4 | <1e-4 |

**Direct start: PC-MALNS [Greedy-Efficiency] vs each commit rule (Holm over all regimes)** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| PC-MALNS [MC-CRIP] | 20 | 5.442 | 5.846 | -0.404 [-0.564, -0.243] | [-0.550, -0.256] | 16/0/4 | 0.0001 | 0.0008 |
| PC-MALNS [Quota-Surplus] | 20 | 5.442 | 5.656 | -0.214 [-0.358, -0.070] | [-0.345, -0.083] | 16/0/4 | 0.0083 | 0.0219 |
| PC-MALNS [Greedy-Gain] | 20 | 5.442 | 6.062 | -0.620 [-0.815, -0.425] | [-0.801, -0.440] | 18/0/2 | <1e-4 | 0.0001 |
| Opt-Rollback-Portfolio | 20 | 5.442 | 8.138 | -2.696 [-3.095, -2.297] | [-3.061, -2.332] | 20/0/0 | <1e-4 | <1e-4 |
| Opt-SeqLock-Portfolio | 20 | 5.442 | 7.620 | -2.178 [-2.597, -1.760] | [-2.587, -1.820] | 20/0/0 | <1e-4 | <1e-4 |
| Opt-Rollback | 20 | 5.442 | 7.129 | -1.687 [-2.013, -1.360] | [-1.986, -1.394] | 20/0/0 | <1e-4 | <1e-4 |
| Opt-SeqLock | 20 | 5.442 | 7.386 | -1.944 [-2.310, -1.579] | [-2.280, -1.614] | 20/0/0 | <1e-4 | <1e-4 |

**MCA-SC-Pair: PC-MALNS [Greedy-Efficiency] vs each commit rule (Holm over all regimes)** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| PC-MALNS [MC-CRIP] | 20 | 1.990 | 2.063 | -0.074 [-0.113, -0.034] | [-0.109, -0.038] | 15/0/5 | 0.0014 | 0.0072 |
| PC-MALNS [Quota-Surplus] | 20 | 1.990 | 2.063 | -0.073 [-0.110, -0.037] | [-0.107, -0.040] | 18/0/2 | 0.0003 | 0.0016 |
| PC-MALNS [Greedy-Gain] | 20 | 1.990 | 2.076 | -0.086 [-0.146, -0.026] | [-0.140, -0.032] | 15/0/5 | 0.0073 | 0.0219 |
| Opt-Rollback-Portfolio | 20 | 1.990 | 2.269 | -0.280 [-0.336, -0.224] | [-0.332, -0.229] | 20/0/0 | <1e-4 | <1e-4 |
| Opt-SeqLock-Portfolio | 20 | 1.990 | 2.228 | -0.238 [-0.295, -0.181] | [-0.291, -0.189] | 20/0/0 | <1e-4 | <1e-4 |
| Opt-Rollback | 20 | 1.990 | 2.266 | -0.277 [-0.327, -0.226] | [-0.323, -0.230] | 20/0/0 | <1e-4 | <1e-4 |
| Opt-SeqLock | 20 | 1.990 | 2.247 | -0.258 [-0.317, -0.198] | [-0.312, -0.203] | 20/0/0 | <1e-4 | <1e-4 |

**Counterfactual barrier analysis (conflict epochs of the PC-MALNS [MC-CRIP] runs)**

| index | regime | rule | mean_gain_per_conflict_epoch | share_of_mccrip_gain_pct | mccrip_strictly_better_pct | conflict_epochs |
|---|---|---|---|---|---|---|
| 0 | LP-Round start | MC-CRIP | 99.88 | 100.00 | 0.00 | 408 |
| 1 | LP-Round start | Greedy-Efficiency | 83.87 | 83.97 | 51.72 | 408 |
| 2 | LP-Round start | Quota-Surplus | 79.49 | 79.59 | 58.33 | 408 |
| 3 | LP-Round start | Greedy-Gain | 83.82 | 83.91 | 43.14 | 408 |
| 4 | LP-Round start | Opt-SeqLock | 57.31 | 57.38 | 100.00 | 408 |
| 5 | LP-Round start | Opt-Rollback | 20.61 | 20.63 | 100.00 | 408 |
| 6 | LP-Round start | Static-Quota | 6.27 | 6.27 | 100.00 | 408 |
| 0 | Direct start | MC-CRIP | 1924.59 | 100.00 | 0.00 | 1162 |
| 1 | Direct start | Greedy-Efficiency | 1617.85 | 84.06 | 45.78 | 1162 |
| 2 | Direct start | Quota-Surplus | 1838.13 | 95.51 | 52.67 | 1162 |
| 3 | Direct start | Greedy-Gain | 1792.09 | 93.12 | 36.32 | 1162 |
| 4 | Direct start | Opt-SeqLock | 1652.82 | 85.88 | 100.00 | 1162 |
| 5 | Direct start | Opt-Rollback | 204.62 | 10.63 | 100.00 | 1162 |
| 6 | Direct start | Static-Quota | 1433.67 | 74.49 | 100.00 | 1162 |
| 0 | MCA-SC-Pair | MC-CRIP | 104.05 | 100.00 | 0.00 | 444 |
| 1 | MCA-SC-Pair | Greedy-Efficiency | 86.55 | 83.19 | 52.25 | 444 |
| 2 | MCA-SC-Pair | Quota-Surplus | 80.04 | 76.93 | 60.59 | 444 |
| 3 | MCA-SC-Pair | Greedy-Gain | 87.75 | 84.34 | 38.74 | 444 |
| 4 | MCA-SC-Pair | Opt-SeqLock | 62.87 | 60.43 | 99.77 | 444 |
| 5 | MCA-SC-Pair | Opt-Rollback | 20.21 | 19.42 | 100.00 | 444 |
| 6 | MCA-SC-Pair | Static-Quota | 6.03 | 5.79 | 100.00 | 444 |

**Residual slack diagnostic (same runs; slack in % of capacity)**

| regime | n | slack_oracle | slack_primary | slack_qs | bott_oracle | bott_primary | acc_oracle | acc_primary | acc_qs | gap_oracle | gap_primary | gap_qs | slack_less_wins | slack_p | bott_less_wins | bott_p | acc_less_wins | acc_p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LP-Round start | 20 | 0.5407 | 0.6116 | 0.6120 | 0.0691 | 0.0808 | 0.3446 | 0.4434 | 0.4657 | 1.7251 | 1.6704 | 1.7403 | 19 | 0.0000 | 14 | 0.0083 | 19 | 0.0000 |
| Direct start | 20 | 2.2835 | 2.8830 | 2.5062 | 1.8506 | 2.0969 | 1.0092 | 1.2877 | 1.2700 | 5.8456 | 5.4419 | 5.6561 | 20 | 0.0000 | 20 | 0.0000 | 20 | 0.0000 |

## Fresh validation (seeds 201–210, gap to the LP bound)


**Mean gap to LP bound (%)**

| method | Small | Medium | Large | X-Large | XXL | XXXL | All |
|---|---|---|---|---|---|---|---|
| PC-MALNS [Greedy-Efficiency] | 3.463 | 2.391 | 1.836 | 1.556 | 0.910 | 0.764 | 1.820 |
| PC-MALNS [MC-CRIP] | 3.405 | 2.407 | 1.896 | 1.609 | 0.946 | 0.785 | 1.841 |
| PC-MALNS [Quota-Surplus] | 3.437 | 2.429 | 1.872 | 1.587 | 0.945 | 0.787 | 1.843 |

**Pre-declared test (results/validation_plan.md)** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| PC-MALNS [MC-CRIP] | 60 | 1.820 | 1.841 | -0.021 [-0.046, +0.004] | [-0.044, +0.006] | 47/0/13 | 0.0004 | 0.0008 |
| PC-MALNS [Quota-Surplus] | 60 | 1.820 | 1.843 | -0.023 [-0.057, +0.011] | [-0.053, +0.014] | 45/0/15 | 0.0007 | 0.0008 |

## Portfolio-level ablation: work protocol, 60 instances


**Mean gap (%)**

| method | Small | Medium | Large | X-Large | XXL | XXXL | All |
|---|---|---|---|---|---|---|---|
| PC-MALNS [Greedy-Efficiency] | 2.523 | 1.779 | 1.562 | 1.361 | 0.870 | 0.713 | 1.468 |
| PC-MALNS [Greedy-Efficiency] levels {1,3} | 2.496 | 1.824 | 1.622 | 1.388 | 0.913 | 0.739 | 1.497 |
| PC-MALNS [Greedy-Efficiency] levels {0,1,3} | 2.496 | 1.824 | 1.622 | 1.388 | 0.913 | 0.739 | 1.497 |
| PC-MALNS [Greedy-Efficiency] levels {1,2,3} | 2.523 | 1.779 | 1.562 | 1.361 | 0.870 | 0.713 | 1.468 |

**PC-MALNS [Greedy-Efficiency] (all four levels / no prices / no restarts) vs each variant** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| PC-MALNS [Greedy-Efficiency] levels {1,3} | 60 | 1.468 | 1.497 | -0.029 [-0.051, -0.008] | [-0.049, -0.007] | 50/0/10 | <1e-4 | 0.0002 |
| PC-MALNS [Greedy-Efficiency] levels {0,1,3} | 60 | 1.468 | 1.497 | -0.029 [-0.051, -0.008] | [-0.049, -0.007] | 50/0/10 | <1e-4 | 0.0002 |
| PC-MALNS [Greedy-Efficiency] levels {1,2,3} | 60 | 1.468 | 1.468 | -0.000 [-0.000, +0.000] | [-0.000, +0.000] | 1/59/0 | 1.0000 | 1.0000 |

## Price and quota ablation: work protocol, 60 instances


**Mean gap (%)**

| method | Small | Medium | Large | X-Large | XXL | XXXL | All |
|---|---|---|---|---|---|---|---|
| PC-MALNS [Greedy-Efficiency] | 2.523 | 1.779 | 1.562 | 1.361 | 0.870 | 0.713 | 1.468 |
| PC-MALNS [Greedy-Efficiency] prices=heuristic, quota=static | 2.433 | 1.743 | 1.529 | 1.329 | 0.862 | 0.702 | 1.433 |
| PC-MALNS [Greedy-Efficiency] prices=heuristic, quota=dynamic | 2.448 | 1.734 | 1.540 | 1.336 | 0.864 | 0.698 | 1.437 |
| PC-MALNS [Greedy-Efficiency] prices=mccrip_lp, quota=static | 2.443 | 1.722 | 1.527 | 1.315 | 0.860 | 0.700 | 1.428 |
| PC-MALNS [Greedy-Efficiency] prices=mccrip_lp, quota=dynamic | 2.460 | 1.727 | 1.531 | 1.333 | 0.866 | 0.701 | 1.436 |
| PC-MALNS [Greedy-Efficiency] prices=none, quota=dynamic | 2.502 | 1.795 | 1.548 | 1.363 | 0.871 | 0.713 | 1.465 |
| PC-MALNS [Greedy-Efficiency] prices=none, quota=demand | 2.452 | 1.786 | 1.556 | 1.340 | 0.867 | 0.710 | 1.452 |

**PC-MALNS [Greedy-Efficiency] (all four levels / no prices / no restarts) vs each variant** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| PC-MALNS [Greedy-Efficiency] prices=heuristic, quota=static | 60 | 1.468 | 1.433 | +0.035 [+0.017, +0.052] | [+0.019, +0.053] | 17/0/43 | <1e-4 | 0.0002 |
| PC-MALNS [Greedy-Efficiency] prices=heuristic, quota=dynamic | 60 | 1.468 | 1.437 | +0.031 [+0.012, +0.050] | [+0.014, +0.051] | 17/0/43 | 0.0003 | 0.0011 |
| PC-MALNS [Greedy-Efficiency] prices=mccrip_lp, quota=static | 60 | 1.468 | 1.428 | +0.040 [+0.023, +0.056] | [+0.024, +0.057] | 11/0/49 | <1e-4 | <1e-4 |
| PC-MALNS [Greedy-Efficiency] prices=mccrip_lp, quota=dynamic | 60 | 1.468 | 1.436 | +0.031 [+0.013, +0.049] | [+0.015, +0.050] | 15/0/45 | 0.0003 | 0.0011 |
| PC-MALNS [Greedy-Efficiency] prices=none, quota=dynamic | 60 | 1.468 | 1.465 | +0.002 [-0.010, +0.015] | [-0.009, +0.015] | 31/1/28 | 0.9791 | 0.9791 |
| PC-MALNS [Greedy-Efficiency] prices=none, quota=demand | 60 | 1.468 | 1.452 | +0.016 [-0.003, +0.035] | [-0.001, +0.035] | 26/0/34 | 0.1388 | 0.2776 |

## Restarts: work protocol, 60 instances


**Mean gap (%)**

| method | Small | Medium | Large | X-Large | XXL | XXXL | All |
|---|---|---|---|---|---|---|---|
| PC-MALNS [Greedy-Efficiency] | 2.523 | 1.779 | 1.562 | 1.361 | 0.870 | 0.713 | 1.468 |
| PC-MALNS [Greedy-Efficiency] + restarts | 2.502 | 1.825 | 1.581 | 1.372 | 0.873 | 0.714 | 1.478 |

**PC-MALNS [Greedy-Efficiency] (all four levels / no prices / no restarts) vs each variant** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| PC-MALNS [Greedy-Efficiency] + restarts | 60 | 1.468 | 1.478 | -0.010 [-0.022, +0.003] | [-0.021, +0.004] | 51/3/6 | <1e-4 | <1e-4 |

## Fresh price test (seeds 301–310, gap to the LP bound; results/price_plan.md)


**Mean gap to LP bound (%)**

| method | Small | Medium | Large | X-Large | XXL | XXXL | All |
|---|---|---|---|---|---|---|---|
| PC-MALNS [Greedy-Efficiency] | 3.538 | 2.371 | 1.827 | 1.570 | 0.963 | 0.760 | 1.838 |
| PC-MALNS [Greedy-Efficiency] prices=mccrip_lp, quota=static | 3.487 | 2.365 | 1.832 | 1.524 | 0.959 | 0.759 | 1.821 |

**Pre-declared test** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| PC-MALNS [Greedy-Efficiency] prices=mccrip_lp, quota=static | 60 | 1.838 | 1.821 | +0.017 [-0.002, +0.036] | [-0.000, +0.036] | 24/0/36 | 0.0649 | 0.0649 |

## Sequential baseline Seq-Commit: work protocol, 60 instances


**Mean gap (%)**

| method | Small | Medium | Large | X-Large | XXL | XXXL | All |
|---|---|---|---|---|---|---|---|
| PC-MALNS [Greedy-Efficiency] | 2.523 | 1.779 | 1.562 | 1.361 | 0.870 | 0.713 | 1.468 |
| PC-MALNS [MC-CRIP] | 2.510 | 1.812 | 1.639 | 1.392 | 0.895 | 0.729 | 1.496 |
| Seq-Commit | 2.588 | 2.007 | 1.789 | 1.584 | 1.022 | 0.862 | 1.642 |
| Opt-SeqLock | 2.564 | 2.029 | 1.790 | 1.586 | 1.018 | 0.837 | 1.637 |
| Opt-Rollback | 2.689 | 2.025 | 1.779 | 1.565 | 1.043 | 0.872 | 1.662 |

**Seq-Commit comparisons (Holm over the three tests)** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| GE vs Seq-Commit | 60 | 1.468 | 1.642 | -0.174 [-0.206, -0.142] | [-0.205, -0.143] | 55/0/5 | <1e-4 | <1e-4 |
| Seq-Commit vs Opt-SeqLock | 60 | 1.642 | 1.637 | +0.005 [-0.016, +0.025] | [-0.015, +0.025] | 25/0/35 | 0.5366 | 0.5366 |
| Seq-Commit vs Opt-Rollback | 60 | 1.642 | 1.662 | -0.020 [-0.049, +0.008] | [-0.049, +0.007] | 35/0/25 | 0.2306 | 0.4611 |

**GE vs Seq-Commit per scale (Holm over the six scales)** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| Small | 10 | 2.523 | 2.588 | -0.065 [-0.219, +0.090] | [-0.195, +0.056] | 6/0/4 | 0.4922 | 0.4922 |
| Medium | 10 | 1.779 | 2.007 | -0.229 [-0.339, -0.119] | [-0.313, -0.135] | 9/0/1 | 0.0039 | 0.0117 |
| Large | 10 | 1.562 | 1.789 | -0.227 [-0.271, -0.184] | [-0.264, -0.193] | 10/0/0 | 0.0020 | 0.0117 |
| X-Large | 10 | 1.361 | 1.584 | -0.223 [-0.254, -0.192] | [-0.249, -0.198] | 10/0/0 | 0.0020 | 0.0117 |
| XXL | 10 | 0.870 | 1.022 | -0.153 [-0.177, -0.128] | [-0.174, -0.134] | 10/0/0 | 0.0020 | 0.0117 |
| XXXL | 10 | 0.713 | 0.862 | -0.149 [-0.168, -0.129] | [-0.165, -0.133] | 10/0/0 | 0.0020 | 0.0117 |

## rho0 = 0 ablation: work protocol, 60 instances


**Mean gap (%)**

| method | Small | Medium | Large | X-Large | XXL | XXXL | All |
|---|---|---|---|---|---|---|---|
| PC-MALNS [Greedy-Efficiency] | 2.523 | 1.779 | 1.562 | 1.361 | 0.870 | 0.713 | 1.468 |
| PC-MALNS [Greedy-Efficiency] rho0=0 | 2.524 | 1.785 | 1.588 | 1.354 | 0.880 | 0.711 | 1.474 |

**PC-MALNS [Greedy-Efficiency] vs rho0 = 0** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| PC-MALNS [Greedy-Efficiency] rho0=0 | 60 | 1.468 | 1.474 | -0.006 [-0.021, +0.009] | [-0.020, +0.008] | 27/6/27 | 0.7007 | 0.7007 |

- Level-0 donors (work_cf_all and all wall-clock runs): {'tries': 2884584, 'dominated': 35, 'committed': 15, 'runs': 7310}
- MC-CRIP fallbacks: {'work_epochs': 0, 'work_runs': 0, 'wall_epochs': 4, 'wall_runs': 4, 'wall_total_runs': 1285}
- Lower bounds: {'n': 190, 'proven_optimal': 0, 'from_lp': 0, 'over_lp_mean': {'main': 0.3610720413288825, 'pair': 0.47868820151219393, 'rich': 0.09685735711808664, 'sweep': 0.29417428597585193}, 'highs_gap_median': {'main': 0.2645265990268749, 'pair': 0.4803670930724131, 'rich': 0.1830605321580404, 'sweep': 0.28028381082166576}, 'highs_gap_max': {'main': 0.4657095686080753, 'pair': 0.6288674374009682, 'rich': 0.6036263157145136, 'sweep': 0.4538977393716991}}

## All-epoch counterfactual (work_cf_all.csv)

- 600 runs; best objective identical to work_main in 600
- trajectories of PC-MALNS [Greedy-Efficiency]: 12171 non-conflict epochs; deviate % MC-CRIP 0.000, Quota-Surplus 0.000, Greedy-Gain 0.016, Greedy-Efficiency 0.140, Static-Quota 9.178; loss % of cheapest gain MC-CRIP 0.00, Quota-Surplus 0.00, Greedy-Gain 0.18, Greedy-Efficiency 1.18, Static-Quota 96.68
- trajectories of PC-MALNS [MC-CRIP]: 12529 non-conflict epochs; deviate % MC-CRIP 0.000, Quota-Surplus 0.000, Greedy-Gain 0.008, Greedy-Efficiency 0.176, Static-Quota 7.926; loss % of cheapest gain MC-CRIP 0.00, Quota-Surplus 0.00, Greedy-Gain 0.09, Greedy-Efficiency 2.13, Static-Quota 95.78

## Stall analysis (work protocol, rep-0 traces; fractions of the epoch budget)

- PC-MALNS [Greedy-Efficiency]: 95% of the improvement after 0.19 of the budget, last improvement at 0.52 (all runs: 0.50); by scale t95 = Small 0.25, Medium 0.27, Large 0.18, X-Large 0.16, XXL 0.12, XXXL 0.14
- PC-MALNS [MC-CRIP]: 95% of the improvement after 0.16 of the budget, last improvement at 0.48 (all runs: 0.46); by scale t95 = Small 0.36, Medium 0.12, Large 0.15, X-Large 0.18, XXL 0.07, XXXL 0.07
- Opt-Rollback-Portfolio: 95% of the improvement after 0.47 of the budget, last improvement at 0.74 (all runs: 0.73); by scale t95 = Small 0.20, Medium 0.26, Large 0.44, X-Large 0.57, XXL 0.62, XXXL 0.75
- Opt-SeqLock-Portfolio: 95% of the improvement after 0.21 of the budget, last improvement at 0.55 (all runs: 0.55); by scale t95 = Small 0.23, Medium 0.19, Large 0.22, X-Large 0.23, XXL 0.19, XXXL 0.22
- Opt-Rollback: 95% of the improvement after 0.31 of the budget, last improvement at 0.61 (all runs: 0.60); by scale t95 = Small 0.23, Medium 0.33, Large 0.26, X-Large 0.32, XXL 0.30, XXXL 0.39
- Opt-SeqLock: 95% of the improvement after 0.20 of the budget, last improvement at 0.50 (all runs: 0.52); by scale t95 = Small 0.29, Medium 0.19, Large 0.17, X-Large 0.23, XXL 0.13, XXXL 0.16

## Main benchmark: wall-clock protocol (uniform conditions), HiGHS 1.16.0


**Mean gap (%) by scale (HiGHS (600s): Small and Medium only)**

| method | Small | Medium | Large | X-Large | XXL | XXXL | All |
|---|---|---|---|---|---|---|---|
| LP-Round | 5.055 | 3.652 | 3.032 | 2.592 | 1.609 | 1.306 | 2.874 |
| PC-MALNS [Greedy-Efficiency] | 2.491 | 1.775 | 1.554 | 1.354 | 0.868 | 0.712 | 1.459 |
| PC-MALNS [MC-CRIP] | 2.476 | 1.812 | 1.628 | 1.385 | 0.893 | 0.729 | 1.487 |
| Opt-Rollback | 2.674 | 2.024 | 1.771 | 1.547 | 1.036 | 0.867 | 1.653 |
| Opt-SeqLock | 2.539 | 2.028 | 1.770 | 1.579 | 1.014 | 0.833 | 1.627 |
| Async-Lock | 2.602 | 2.043 | 1.793 | 1.545 | 1.003 | 0.850 | 1.639 |
| HiGHS (1T, wall-matched) | 1.030 | 0.674 | 1.507 | 2.792 | 1.732 | 1.454 | 1.532 |
| HiGHS (4T, wall-matched) | 1.030 | 0.653 | 1.482 | 2.694 | 1.732 | 1.454 | 1.508 |
| HiGHS (1T, CPU-matched) | 0.926 | 0.590 | 0.423 | 0.496 | 0.295 | 0.213 | 0.490 |
| HiGHS+LP-Round (1T, wall-matched) | 1.011 | 0.986 | 1.423 | 2.427 | 1.577 | 1.302 | 1.455 |
| HiGHS+LP-Round (1T, CPU-matched) | 0.947 | 0.595 | 0.448 | 0.440 | 0.275 | 0.236 | 0.490 |
| HiGHS (5s) | 0.715 | 0.574 | 0.426 | 0.539 | 1.732 | 1.454 | 0.907 |
| HiGHS (60s) | 0.497 | 0.350 | 0.330 | 0.301 | 0.285 | 0.213 | 0.329 |
| HiGHS (600s) | 0.395 | 0.278 | – | – | – | – | 0.336 |

**Wall clock: PC-MALNS [Greedy-Efficiency] vs each method (60 instances)** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| LP-Round | 60 | 1.459 | 2.874 | -1.415 [-1.609, -1.222] | [-1.604, -1.234] | 60/0/0 | <1e-4 | <1e-4 |
| PC-MALNS [MC-CRIP] | 60 | 1.459 | 1.487 | -0.028 [-0.045, -0.011] | [-0.044, -0.011] | 44/0/16 | <1e-4 | <1e-4 |
| Opt-Rollback | 60 | 1.459 | 1.653 | -0.194 [-0.227, -0.161] | [-0.226, -0.163] | 57/0/3 | <1e-4 | <1e-4 |
| Opt-SeqLock | 60 | 1.459 | 1.627 | -0.168 [-0.200, -0.136] | [-0.199, -0.138] | 54/0/6 | <1e-4 | <1e-4 |
| Async-Lock | 60 | 1.459 | 1.639 | -0.180 [-0.214, -0.147] | [-0.213, -0.148] | 56/0/4 | <1e-4 | <1e-4 |
| HiGHS (1T, wall-matched) | 60 | 1.459 | 1.532 | -0.072 [-0.392, +0.248] | [-0.382, +0.245] | 32/0/28 | 0.8465 | 1.0000 |
| HiGHS (4T, wall-matched) | 60 | 1.459 | 1.508 | -0.048 [-0.365, +0.268] | [-0.354, +0.267] | 32/0/28 | 0.9505 | 1.0000 |
| HiGHS (1T, CPU-matched) | 60 | 1.459 | 0.490 | +0.969 [+0.856, +1.082] | [+0.862, +1.080] | 0/0/60 | <1e-4 | <1e-4 |
| HiGHS+LP-Round (1T, wall-matched) | 60 | 1.459 | 1.455 | +0.005 [-0.291, +0.300] | [-0.283, +0.297] | 33/0/27 | 0.6530 | 1.0000 |
| HiGHS+LP-Round (1T, CPU-matched) | 60 | 1.459 | 0.490 | +0.969 [+0.860, +1.077] | [+0.866, +1.076] | 0/0/60 | <1e-4 | <1e-4 |
| HiGHS (5s) | 60 | 1.459 | 0.907 | +0.552 [+0.285, +0.819] | [+0.292, +0.807] | 20/0/40 | <1e-4 | <1e-4 |
| HiGHS (60s) | 60 | 1.459 | 0.329 | +1.130 [+0.989, +1.271] | [+0.996, +1.268] | 0/0/60 | <1e-4 | <1e-4 |

**Per scale (Holm over the family)** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| Small: Opt-Rollback | 10 | 2.491 | 2.674 | -0.183 [-0.378, +0.012] | [-0.348, -0.025] | 8/0/2 | 0.0645 | 0.4512 |
| Small: Opt-SeqLock | 10 | 2.491 | 2.539 | -0.048 [-0.201, +0.105] | [-0.187, +0.060] | 4/0/6 | 1.0000 | 1.0000 |
| Small: Async-Lock | 10 | 2.491 | 2.602 | -0.111 [-0.286, +0.063] | [-0.261, +0.024] | 6/0/4 | 0.2754 | 1.0000 |
| Small: HiGHS (1T, wall-matched) | 10 | 2.491 | 1.030 | +1.461 [+1.145, +1.777] | [+1.212, +1.733] | 0/0/10 | 0.0020 | 0.1055 |
| Small: HiGHS (4T, wall-matched) | 10 | 2.491 | 1.030 | +1.461 [+1.145, +1.777] | [+1.212, +1.733] | 0/0/10 | 0.0020 | 0.1055 |
| Small: HiGHS (1T, CPU-matched) | 10 | 2.491 | 0.926 | +1.565 [+1.257, +1.873] | [+1.307, +1.820] | 0/0/10 | 0.0020 | 0.1055 |
| Small: HiGHS+LP-Round (1T, wall-matched) | 10 | 2.491 | 1.011 | +1.479 [+1.162, +1.797] | [+1.229, +1.746] | 0/0/10 | 0.0020 | 0.1055 |
| Small: HiGHS+LP-Round (1T, CPU-matched) | 10 | 2.491 | 0.947 | +1.544 [+1.247, +1.840] | [+1.308, +1.794] | 0/0/10 | 0.0020 | 0.1055 |
| Small: HiGHS (5s) | 10 | 2.491 | 0.715 | +1.775 [+1.479, +2.071] | [+1.515, +2.008] | 0/0/10 | 0.0020 | 0.1055 |
| Medium: Opt-Rollback | 10 | 1.775 | 2.024 | -0.249 [-0.337, -0.161] | [-0.319, -0.174] | 9/0/1 | 0.0039 | 0.1055 |
| Medium: Opt-SeqLock | 10 | 1.775 | 2.028 | -0.254 [-0.325, -0.182] | [-0.313, -0.197] | 10/0/0 | 0.0020 | 0.1055 |
| Medium: Async-Lock | 10 | 1.775 | 2.043 | -0.268 [-0.375, -0.162] | [-0.355, -0.180] | 10/0/0 | 0.0020 | 0.1055 |
| Medium: HiGHS (1T, wall-matched) | 10 | 1.775 | 0.674 | +1.101 [+0.926, +1.275] | [+0.950, +1.239] | 0/0/10 | 0.0020 | 0.1055 |
| Medium: HiGHS (4T, wall-matched) | 10 | 1.775 | 0.653 | +1.122 [+0.951, +1.292] | [+0.972, +1.254] | 0/0/10 | 0.0020 | 0.1055 |
| Medium: HiGHS (1T, CPU-matched) | 10 | 1.775 | 0.590 | +1.185 [+1.032, +1.338] | [+1.048, +1.300] | 0/0/10 | 0.0020 | 0.1055 |
| Medium: HiGHS+LP-Round (1T, wall-matched) | 10 | 1.775 | 0.986 | +0.789 [-0.014, +1.591] | [+0.051, +1.238] | 1/0/9 | 0.0840 | 0.5039 |
| Medium: HiGHS+LP-Round (1T, CPU-matched) | 10 | 1.775 | 0.595 | +1.180 [+1.041, +1.318] | [+1.058, +1.285] | 0/0/10 | 0.0020 | 0.1055 |
| Medium: HiGHS (5s) | 10 | 1.775 | 0.574 | +1.201 [+1.051, +1.351] | [+1.065, +1.312] | 0/0/10 | 0.0020 | 0.1055 |
| Large: Opt-Rollback | 10 | 1.554 | 1.771 | -0.216 [-0.261, -0.172] | [-0.252, -0.179] | 10/0/0 | 0.0020 | 0.1055 |
| Large: Opt-SeqLock | 10 | 1.554 | 1.770 | -0.215 [-0.265, -0.166] | [-0.255, -0.173] | 10/0/0 | 0.0020 | 0.1055 |
| Large: Async-Lock | 10 | 1.554 | 1.793 | -0.239 [-0.282, -0.196] | [-0.273, -0.202] | 10/0/0 | 0.0020 | 0.1055 |
| Large: HiGHS (1T, wall-matched) | 10 | 1.554 | 1.507 | +0.047 [-0.924, +1.018] | [-0.807, +0.760] | 3/0/7 | 1.0000 | 1.0000 |
| Large: HiGHS (4T, wall-matched) | 10 | 1.554 | 1.482 | +0.072 [-0.910, +1.054] | [-0.791, +0.790] | 3/0/7 | 1.0000 | 1.0000 |
| Large: HiGHS (1T, CPU-matched) | 10 | 1.554 | 0.423 | +1.132 [+1.040, +1.224] | [+1.059, +1.208] | 0/0/10 | 0.0020 | 0.1055 |
| Large: HiGHS+LP-Round (1T, wall-matched) | 10 | 1.554 | 1.423 | +0.131 [-0.718, +0.981] | [-0.606, +0.775] | 3/0/7 | 1.0000 | 1.0000 |
| Large: HiGHS+LP-Round (1T, CPU-matched) | 10 | 1.554 | 0.448 | +1.106 [+1.013, +1.199] | [+1.030, +1.180] | 0/0/10 | 0.0020 | 0.1055 |
| Large: HiGHS (5s) | 10 | 1.554 | 0.426 | +1.128 [+1.036, +1.221] | [+1.055, +1.206] | 0/0/10 | 0.0020 | 0.1055 |
| X-Large: Opt-Rollback | 10 | 1.354 | 1.547 | -0.194 [-0.228, -0.159] | [-0.221, -0.166] | 10/0/0 | 0.0020 | 0.1055 |
| X-Large: Opt-SeqLock | 10 | 1.354 | 1.579 | -0.225 [-0.267, -0.183] | [-0.261, -0.193] | 10/0/0 | 0.0020 | 0.1055 |
| X-Large: Async-Lock | 10 | 1.354 | 1.545 | -0.192 [-0.225, -0.158] | [-0.218, -0.163] | 10/0/0 | 0.0020 | 0.1055 |
| X-Large: HiGHS (1T, wall-matched) | 10 | 1.354 | 2.792 | -1.438 [-1.945, -0.932] | [-1.741, -0.967] | 9/0/1 | 0.0039 | 0.1055 |
| X-Large: HiGHS (4T, wall-matched) | 10 | 1.354 | 2.694 | -1.340 [-1.838, -0.842] | [-1.661, -0.870] | 9/0/1 | 0.0039 | 0.1055 |
| X-Large: HiGHS (1T, CPU-matched) | 10 | 1.354 | 0.496 | +0.858 [+0.677, +1.039] | [+0.692, +0.986] | 0/0/10 | 0.0020 | 0.1055 |
| X-Large: HiGHS+LP-Round (1T, wall-matched) | 10 | 1.354 | 2.427 | -1.073 [-1.481, -0.666] | [-1.310, -0.694] | 9/0/1 | 0.0039 | 0.1055 |
| X-Large: HiGHS+LP-Round (1T, CPU-matched) | 10 | 1.354 | 0.440 | +0.913 [+0.779, +1.047] | [+0.795, +1.012] | 0/0/10 | 0.0020 | 0.1055 |
| X-Large: HiGHS (5s) | 10 | 1.354 | 0.539 | +0.814 [+0.620, +1.008] | [+0.639, +0.960] | 0/0/10 | 0.0020 | 0.1055 |
| XXL: Opt-Rollback | 10 | 0.868 | 1.036 | -0.168 [-0.191, -0.145] | [-0.188, -0.151] | 10/0/0 | 0.0020 | 0.1055 |
| XXL: Opt-SeqLock | 10 | 0.868 | 1.014 | -0.146 [-0.160, -0.132] | [-0.158, -0.135] | 10/0/0 | 0.0020 | 0.1055 |
| XXL: Async-Lock | 10 | 0.868 | 1.003 | -0.135 [-0.162, -0.107] | [-0.158, -0.113] | 10/0/0 | 0.0020 | 0.1055 |
| XXL: HiGHS (1T, wall-matched) | 10 | 0.868 | 1.732 | -0.864 [-0.981, -0.746] | [-0.959, -0.766] | 10/0/0 | 0.0020 | 0.1055 |
| XXL: HiGHS (4T, wall-matched) | 10 | 0.868 | 1.732 | -0.864 [-0.981, -0.746] | [-0.959, -0.766] | 10/0/0 | 0.0020 | 0.1055 |
| XXL: HiGHS (1T, CPU-matched) | 10 | 0.868 | 0.295 | +0.573 [+0.457, +0.689] | [+0.480, +0.668] | 0/0/10 | 0.0020 | 0.1055 |
| XXL: HiGHS+LP-Round (1T, wall-matched) | 10 | 0.868 | 1.577 | -0.709 [-0.769, -0.649] | [-0.760, -0.660] | 10/0/0 | 0.0020 | 0.1055 |
| XXL: HiGHS+LP-Round (1T, CPU-matched) | 10 | 0.868 | 0.275 | +0.593 [+0.492, +0.694] | [+0.509, +0.673] | 0/0/10 | 0.0020 | 0.1055 |
| XXL: HiGHS (5s) | 10 | 0.868 | 1.732 | -0.864 [-0.981, -0.746] | [-0.959, -0.766] | 10/0/0 | 0.0020 | 0.1055 |
| XXXL: Opt-Rollback | 10 | 0.712 | 0.867 | -0.154 [-0.172, -0.136] | [-0.170, -0.140] | 10/0/0 | 0.0020 | 0.1055 |
| XXXL: Opt-SeqLock | 10 | 0.712 | 0.833 | -0.121 [-0.145, -0.097] | [-0.141, -0.102] | 10/0/0 | 0.0020 | 0.1055 |
| XXXL: Async-Lock | 10 | 0.712 | 0.850 | -0.138 [-0.161, -0.115] | [-0.157, -0.119] | 10/0/0 | 0.0020 | 0.1055 |
| XXXL: HiGHS (1T, wall-matched) | 10 | 0.712 | 1.454 | -0.741 [-0.819, -0.664] | [-0.808, -0.680] | 10/0/0 | 0.0020 | 0.1055 |
| XXXL: HiGHS (4T, wall-matched) | 10 | 0.712 | 1.454 | -0.741 [-0.819, -0.664] | [-0.808, -0.680] | 10/0/0 | 0.0020 | 0.1055 |
| XXXL: HiGHS (1T, CPU-matched) | 10 | 0.712 | 0.213 | +0.499 [+0.429, +0.570] | [+0.438, +0.552] | 0/0/10 | 0.0020 | 0.1055 |
| XXXL: HiGHS+LP-Round (1T, wall-matched) | 10 | 0.712 | 1.302 | -0.590 [-0.636, -0.543] | [-0.629, -0.554] | 10/0/0 | 0.0020 | 0.1055 |
| XXXL: HiGHS+LP-Round (1T, CPU-matched) | 10 | 0.712 | 0.236 | +0.477 [+0.411, +0.542] | [+0.423, +0.529] | 0/0/10 | 0.0020 | 0.1055 |
| XXXL: HiGHS (5s) | 10 | 0.712 | 1.454 | -0.741 [-0.819, -0.664] | [-0.808, -0.680] | 10/0/0 | 0.0020 | 0.1055 |

**Epochs per run (wall clock)**

| method | Small | Medium | Large | X-Large | XXL | XXXL | All |
|---|---|---|---|---|---|---|---|
| Async-Lock | – | – | – | – | – | – | – |
| Opt-Rollback | 229.9 | 191.3 | 164.6 | 141.3 | 116.0 | 102.3 | 157.6 |
| Opt-SeqLock | 229.2 | 193.9 | 163.5 | 140.0 | 115.5 | 104.7 | 157.8 |
| PC-MALNS [Greedy-Efficiency] | 90.0 | 73.5 | 62.4 | 52.6 | 43.4 | 38.4 | 60.1 |
| PC-MALNS [MC-CRIP] | 90.0 | 72.9 | 60.6 | 50.1 | 38.8 | 33.7 | 57.7 |

**Budget overrun (% of the budget)**

| method | Small | Medium | Large | X-Large | XXL | XXXL | All |
|---|---|---|---|---|---|---|---|
| Async-Lock | 0.33 | 0.22 | 0.17 | 0.15 | 0.12 | 0.10 | 0.18 |
| Opt-Rollback | 0.21 | 0.31 | 0.34 | 0.30 | 0.45 | 0.47 | 0.35 |
| Opt-SeqLock | 0.22 | 0.29 | 0.35 | 0.42 | 0.41 | 0.44 | 0.35 |
| PC-MALNS [Greedy-Efficiency] | 0.58 | 0.73 | 0.77 | 1.05 | 1.01 | 1.35 | 0.92 |
| PC-MALNS [MC-CRIP] | 0.64 | 0.58 | 0.83 | 0.93 | 1.00 | 1.28 | 0.88 |

**Time for the 1-thread HiGHS reference run to reach the mean PC-MALNS [Greedy-Efficiency] objective (s)**

| scale | n | never | ttt_median | ttt_max | lns_wall_median | ratio_median | ratio_cpu_median |
|---|---|---|---|---|---|---|---|
| Small | 10 | 0 | 0.330 | 0.584 | 0.503 | 0.656 | 0.190 |
| Medium | 10 | 0 | 0.844 | 1.026 | 1.007 | 0.840 | 0.229 |
| Large | 10 | 0 | 1.677 | 2.078 | 1.512 | 1.109 | 0.297 |
| X-Large | 10 | 0 | 2.637 | 3.792 | 2.019 | 1.305 | 0.350 |
| XXL | 10 | 0 | 9.310 | 10.427 | 4.039 | 2.300 | 0.618 |
| XXXL | 10 | 0 | 10.853 | 16.480 | 6.079 | 1.784 | 0.485 |

**Primal integral over the PC-MALNS budget, divided by the budget**

| scale | pi_lns | pi_highs |
|---|---|---|
| Small | 0.0378 | 0.0597 |
| Medium | 0.0326 | 0.0614 |
| Large | 0.0337 | 0.0665 |
| X-Large | 0.0355 | 0.0592 |
| XXL | 0.0385 | 0.0502 |
| XXXL | 0.0425 | 0.0580 |

**Async-Lock: steps per agent, accepted, proposals, rejected (did not fit)**

| scale | steps_per_agent | accepted_moves | proposals | rejected_fit |
|---|---|---|---|---|
| Small | 256.6 | 14.7 | 21.9 | 7.1 |
| Medium | 201.6 | 22.7 | 36.4 | 13.7 |
| Large | 168.4 | 27.0 | 44.9 | 17.8 |
| X-Large | 142.2 | 35.2 | 56.7 | 21.5 |
| XXL | 120.3 | 42.3 | 67.4 | 25.2 |
| XXXL | 104.2 | 47.3 | 76.8 | 29.5 |

## Rich candidate pools: wall clock (uniform conditions), HiGHS 1.16.0


**J = 20: mean gap (%)**

| method | Medium | Large | X-Large | XXL | All |
|---|---|---|---|---|---|
| LP-Round | 4.471 | 3.648 | 2.997 | 1.887 | 3.251 |
| PC-MALNS [Greedy-Efficiency] | 2.855 | 2.457 | 2.078 | 1.355 | 2.186 |
| PC-MALNS [MC-CRIP] | 2.919 | 2.484 | 2.128 | 1.401 | 2.233 |
| PC-MALNS [Quota-Surplus] | 2.960 | 2.485 | 2.137 | 1.371 | 2.238 |
| Opt-Rollback | 3.115 | 2.754 | 2.375 | 1.545 | 2.447 |
| Opt-SeqLock | 3.123 | 2.774 | 2.362 | 1.556 | 2.454 |
| HiGHS (1T, wall-matched) | 5.350 | 4.259 | 3.432 | 2.156 | 3.799 |
| HiGHS (4T, wall-matched) | 5.350 | 4.259 | 3.432 | 2.156 | 3.799 |
| HiGHS (1T, CPU-matched) | 2.515 | 1.568 | 1.813 | 1.647 | 1.886 |
| HiGHS+LP-Round (1T, wall-matched) | 4.459 | 3.587 | 2.989 | 1.885 | 3.230 |
| HiGHS+LP-Round (1T, CPU-matched) | 1.972 | 1.568 | 1.753 | 1.415 | 1.677 |
| HiGHS (5s) | 2.288 | 2.864 | 3.432 | 2.156 | 2.685 |
| HiGHS (30s) | 0.804 | 0.690 | 0.632 | 0.201 | 0.582 |
| HiGHS (300s) | 0.361 | 0.262 | 0.253 | 0.144 | 0.255 |

**J = 40: mean gap (%)**

| method | Medium | Large | X-Large | XXL | All |
|---|---|---|---|---|---|
| LP-Round | 4.606 | 3.506 | 2.900 | 1.772 | 3.196 |
| PC-MALNS [Greedy-Efficiency] | 2.912 | 2.415 | 2.106 | 1.353 | 2.197 |
| PC-MALNS [MC-CRIP] | 3.005 | 2.465 | 2.101 | 1.367 | 2.234 |
| PC-MALNS [Quota-Surplus] | 2.988 | 2.463 | 2.165 | 1.369 | 2.246 |
| Opt-Rollback | 3.195 | 2.722 | 2.388 | 1.552 | 2.465 |
| Opt-SeqLock | 3.242 | 2.775 | 2.359 | 1.544 | 2.480 |
| HiGHS (1T, wall-matched) | 5.710 | 4.435 | 3.847 | 2.507 | 4.125 |
| HiGHS (4T, wall-matched) | 5.710 | 4.435 | 3.847 | 2.507 | 4.125 |
| HiGHS (1T, CPU-matched) | 3.098 | 4.435 | 3.847 | 2.409 | 3.447 |
| HiGHS+LP-Round (1T, wall-matched) | 4.587 | 3.492 | 2.900 | 1.772 | 3.188 |
| HiGHS+LP-Round (1T, CPU-matched) | 3.047 | 3.492 | 2.900 | 1.772 | 2.803 |
| HiGHS (5s) | 2.464 | 4.435 | 3.847 | 2.409 | 3.289 |
| HiGHS (30s) | 0.764 | 1.500 | 0.225 | 2.409 | 1.224 |
| HiGHS (300s) | 0.263 | 0.142 | 0.119 | 0.099 | 0.156 |

**J = 20: PC-MALNS [Greedy-Efficiency] vs each method (Holm over both J)** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| LP-Round | 40 | 2.186 | 3.251 | -1.065 [-1.209, -0.921] | [-1.204, -0.931] | 40/0/0 | <1e-4 | <1e-4 |
| PC-MALNS [MC-CRIP] | 40 | 2.186 | 2.233 | -0.047 [-0.064, -0.030] | [-0.063, -0.031] | 34/0/6 | <1e-4 | <1e-4 |
| PC-MALNS [Quota-Surplus] | 40 | 2.186 | 2.238 | -0.052 [-0.075, -0.030] | [-0.075, -0.032] | 34/0/6 | <1e-4 | <1e-4 |
| Opt-Rollback | 40 | 2.186 | 2.447 | -0.261 [-0.298, -0.225] | [-0.296, -0.227] | 39/0/1 | <1e-4 | <1e-4 |
| Opt-SeqLock | 40 | 2.186 | 2.454 | -0.268 [-0.307, -0.229] | [-0.305, -0.229] | 39/0/1 | <1e-4 | <1e-4 |
| HiGHS (1T, wall-matched) | 40 | 2.186 | 3.799 | -1.613 [-1.855, -1.371] | [-1.845, -1.390] | 40/0/0 | <1e-4 | <1e-4 |
| HiGHS (4T, wall-matched) | 40 | 2.186 | 3.799 | -1.613 [-1.855, -1.371] | [-1.845, -1.390] | 40/0/0 | <1e-4 | <1e-4 |
| HiGHS (1T, CPU-matched) | 40 | 2.186 | 1.886 | +0.300 [-0.065, +0.666] | [-0.050, +0.654] | 17/0/23 | 0.1150 | 0.1150 |
| HiGHS+LP-Round (1T, wall-matched) | 40 | 2.186 | 3.230 | -1.044 [-1.186, -0.901] | [-1.181, -0.911] | 40/0/0 | <1e-4 | <1e-4 |
| HiGHS+LP-Round (1T, CPU-matched) | 40 | 2.186 | 1.677 | +0.509 [+0.115, +0.904] | [+0.126, +0.885] | 17/0/23 | 0.0130 | 0.0391 |
| HiGHS (5s) | 40 | 2.186 | 2.685 | -0.499 [-0.910, -0.087] | [-0.880, -0.096] | 29/0/11 | 0.0232 | 0.0464 |
| HiGHS (30s) | 40 | 2.186 | 0.582 | +1.604 [+1.428, +1.781] | [+1.431, +1.767] | 1/0/39 | <1e-4 | <1e-4 |

**J = 40: PC-MALNS [Greedy-Efficiency] vs each method (Holm over both J)** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| LP-Round | 40 | 2.197 | 3.196 | -0.999 [-1.169, -0.830] | [-1.165, -0.846] | 40/0/0 | <1e-4 | <1e-4 |
| PC-MALNS [MC-CRIP] | 40 | 2.197 | 2.234 | -0.038 [-0.064, -0.012] | [-0.064, -0.015] | 28/0/12 | 0.0034 | 0.0134 |
| PC-MALNS [Quota-Surplus] | 40 | 2.197 | 2.246 | -0.050 [-0.075, -0.024] | [-0.075, -0.026] | 33/0/7 | <1e-4 | 0.0003 |
| Opt-Rollback | 40 | 2.197 | 2.465 | -0.268 [-0.307, -0.229] | [-0.306, -0.232] | 40/0/0 | <1e-4 | <1e-4 |
| Opt-SeqLock | 40 | 2.197 | 2.480 | -0.284 [-0.315, -0.253] | [-0.314, -0.255] | 40/0/0 | <1e-4 | <1e-4 |
| HiGHS (1T, wall-matched) | 40 | 2.197 | 4.125 | -1.928 [-2.191, -1.665] | [-2.187, -1.691] | 40/0/0 | <1e-4 | <1e-4 |
| HiGHS (4T, wall-matched) | 40 | 2.197 | 4.125 | -1.928 [-2.191, -1.665] | [-2.187, -1.691] | 40/0/0 | <1e-4 | <1e-4 |
| HiGHS (1T, CPU-matched) | 40 | 2.197 | 3.447 | -1.251 [-1.702, -0.799] | [-1.650, -0.789] | 35/0/5 | <1e-4 | 0.0003 |
| HiGHS+LP-Round (1T, wall-matched) | 40 | 2.197 | 3.188 | -0.991 [-1.157, -0.825] | [-1.154, -0.839] | 40/0/0 | <1e-4 | <1e-4 |
| HiGHS+LP-Round (1T, CPU-matched) | 40 | 2.197 | 2.803 | -0.606 [-0.953, -0.260] | [-0.911, -0.245] | 36/0/4 | 0.0002 | 0.0010 |
| HiGHS (5s) | 40 | 2.197 | 3.289 | -1.092 [-1.566, -0.619] | [-1.514, -0.617] | 33/0/7 | 0.0002 | 0.0010 |
| HiGHS (30s) | 40 | 2.197 | 1.224 | +0.972 [+0.469, +1.475] | [+0.497, +1.430] | 12/0/28 | 0.0001 | 0.0009 |

**Rich pools: time for the HiGHS reference run (300 s) to reach the PC-MALNS objective (s)**

| P | scale | n | never | ttt_median | ttt_max | lns_wall_median | ratio_median | ratio_cpu_median |
|---|---|---|---|---|---|---|---|---|
| 20 | Large | 10 | 0 | 5.030 | 8.910 | 1.516 | 3.316 | 0.899 |
| 20 | Medium | 10 | 0 | 2.656 | 7.089 | 1.008 | 2.634 | 0.715 |
| 20 | X-Large | 10 | 0 | 8.710 | 68.559 | 2.022 | 4.298 | 1.173 |
| 20 | XXL | 10 | 0 | 19.028 | 23.157 | 4.092 | 4.673 | 1.293 |
| 40 | Large | 10 | 0 | 13.494 | 100.123 | 1.535 | 8.744 | 2.461 |
| 40 | Medium | 10 | 0 | 4.804 | 23.829 | 1.015 | 4.731 | 1.322 |
| 40 | X-Large | 10 | 0 | 12.885 | 14.963 | 2.033 | 6.338 | 1.781 |
| 40 | XXL | 10 | 0 | 32.646 | 42.473 | 4.078 | 8.031 | 2.357 |

**Rich, slow-stretch instances (40), original runs: PC-MALNS [Greedy-Efficiency] vs each** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| Opt-Rollback | 40 | 2.197 | 2.460 | -0.263 [-0.303, -0.223] | [-0.303, -0.226] | 40/0/0 | <1e-4 | <1e-4 |
| Opt-SeqLock | 40 | 2.197 | 2.487 | -0.290 [-0.320, -0.260] | [-0.319, -0.262] | 40/0/0 | <1e-4 | <1e-4 |
| PC-MALNS [MC-CRIP] | 40 | 2.197 | 2.252 | -0.055 [-0.080, -0.031] | [-0.080, -0.033] | 33/0/7 | <1e-4 | <1e-4 |
| PC-MALNS [Quota-Surplus] | 40 | 2.197 | 2.244 | -0.047 [-0.072, -0.022] | [-0.072, -0.024] | 32/0/8 | 0.0001 | 0.0004 |
| HiGHS (1T, wall-matched) | 40 | 2.197 | 3.941 | -1.744 [-2.043, -1.446] | [-2.034, -1.473] | 40/0/0 | <1e-4 | <1e-4 |
| HiGHS (4T, wall-matched) | 40 | 2.197 | 3.941 | -1.744 [-2.043, -1.446] | [-2.034, -1.473] | 40/0/0 | <1e-4 | <1e-4 |
| HiGHS (1T, CPU-matched) | 40 | 2.197 | 2.783 | -0.586 [-1.114, -0.058] | [-1.085, -0.068] | 27/0/13 | 0.0368 | 0.0737 |
| HiGHS+LP-Round (1T, wall-matched) | 40 | 2.197 | 3.232 | -1.035 [-1.190, -0.881] | [-1.188, -0.897] | 40/0/0 | <1e-4 | <1e-4 |
| HiGHS+LP-Round (1T, CPU-matched) | 40 | 2.197 | 2.442 | -0.245 [-0.665, +0.175] | [-0.636, +0.170] | 28/0/12 | 0.2163 | 0.2163 |

**Rich, slow-stretch instances (40), rerun runs: PC-MALNS [Greedy-Efficiency] vs each** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| Opt-Rollback | 40 | 2.188 | 2.446 | -0.258 [-0.299, -0.218] | [-0.299, -0.221] | 39/0/1 | <1e-4 | <1e-4 |
| Opt-SeqLock | 40 | 2.188 | 2.475 | -0.287 [-0.317, -0.256] | [-0.317, -0.258] | 40/0/0 | <1e-4 | <1e-4 |
| PC-MALNS [MC-CRIP] | 40 | 2.188 | 2.244 | -0.057 [-0.083, -0.031] | [-0.083, -0.033] | 31/0/9 | <1e-4 | <1e-4 |
| PC-MALNS [Quota-Surplus] | 40 | 2.188 | 2.228 | -0.041 [-0.067, -0.014] | [-0.066, -0.016] | 31/0/9 | 0.0009 | 0.0028 |
| HiGHS (1T, wall-matched) | 40 | 2.188 | 3.941 | -1.753 [-2.054, -1.453] | [-2.046, -1.480] | 40/0/0 | <1e-4 | <1e-4 |
| HiGHS (4T, wall-matched) | 40 | 2.188 | 3.941 | -1.753 [-2.054, -1.453] | [-2.046, -1.480] | 40/0/0 | <1e-4 | <1e-4 |
| HiGHS (1T, CPU-matched) | 40 | 2.188 | 2.705 | -0.517 [-1.051, +0.017] | [-1.021, +0.002] | 25/0/15 | 0.0498 | 0.0995 |
| HiGHS+LP-Round (1T, wall-matched) | 40 | 2.188 | 3.232 | -1.045 [-1.204, -0.886] | [-1.200, -0.902] | 40/0/0 | <1e-4 | <1e-4 |
| HiGHS+LP-Round (1T, CPU-matched) | 40 | 2.188 | 2.362 | -0.175 [-0.587, +0.237] | [-0.556, +0.225] | 27/0/13 | 0.3611 | 0.3611 |

**Epochs of PC-MALNS [Greedy-Efficiency]: original vs rerun**

| P | scale | original | rerun |
|---|---|---|---|
| 20 | X-Large | 39.5 | 43.2 |
| 20 | XXL | 20.6 | 32.6 |
| 40 | Large | 24.6 | 25.5 |
| 40 | Medium | 31.3 | 43.9 |
| 40 | X-Large | 28.1 | 20.0 |

**Rich pools, combined (rerun rows for the slow stretch): time to target (s)**

| P | scale | n | never | ttt_median | ttt_max | lns_wall_median | ratio_median | ratio_cpu_median |
|---|---|---|---|---|---|---|---|---|
| 20 | Large | 10 | 0 | 5.030 | 8.910 | 1.516 | 3.316 | 0.899 |
| 20 | Medium | 10 | 0 | 2.656 | 7.089 | 1.008 | 2.634 | 0.715 |
| 20 | X-Large | 10 | 0 | 8.751 | 68.980 | 2.021 | 4.323 | 1.178 |
| 20 | XXL | 10 | 0 | 17.970 | 22.580 | 4.068 | 4.409 | 1.216 |
| 40 | Large | 10 | 0 | 13.296 | 94.836 | 1.528 | 8.702 | 2.452 |
| 40 | Medium | 10 | 0 | 4.521 | 22.401 | 1.010 | 4.489 | 1.247 |
| 40 | X-Large | 10 | 0 | 12.924 | 14.963 | 2.033 | 6.345 | 1.789 |
| 40 | XXL | 10 | 0 | 32.646 | 42.473 | 4.078 | 8.031 | 2.357 |

## Tightness sweep (Large, wall clock; eta = 1.25 from the main job)


**Mean gap (%) by eta**

| eta | LP-Round | PC-MALNS [Greedy-Efficiency] | PC-MALNS [MC-CRIP] | PC-MALNS [Quota-Surplus] | Opt-Rollback | Opt-SeqLock | Static-Quota | HiGHS (1T, wall-matched) | HiGHS+LP-Round (1T, wall-matched) | HiGHS (1T, CPU-matched) | HiGHS (5s) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.850 | 2.890 | 1.702 | 1.713 | 1.713 | 1.620 | 1.618 | 1.648 | 0.635 | 0.640 | 0.285 | 0.296 |
| 1.050 | 3.028 | 1.768 | 1.793 | 1.781 | 1.737 | 1.715 | 2.490 | 3.044 | 2.575 | 0.585 | 0.585 |
| 1.250 | 3.032 | 1.554 | 1.628 | – | 1.771 | 1.770 | – | 1.507 | 1.423 | 0.423 | 0.426 |
| 1.450 | 1.687 | 1.075 | 1.076 | 1.097 | 1.184 | 1.188 | 1.609 | 0.442 | 0.416 | 0.373 | 0.381 |

**Conflict epochs (%) by eta**

| eta | Async-Lock | Opt-Rollback | Opt-SeqLock | PC-MALNS [Greedy-Efficiency] | PC-MALNS [MC-CRIP] | PC-MALNS [Quota-Surplus] | Static-Quota |
|---|---|---|---|---|---|---|---|
| 0.8 | – | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 1.1 | – | 4.2 | 2.7 | 6.6 | 4.9 | 5.3 | 0.0 |
| 1.2 | – | 10.8 | 5.2 | 9.7 | 7.2 | – | – |
| 1.4 | – | 4.5 | 3.0 | 5.9 | 5.0 | 6.3 | 0.0 |

**Sweep: per eta, Holm over the whole sweep** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| eta=0.85: LP-Round | 10 | 1.702 | 2.890 | -1.188 [-1.384, -0.992] | [-1.365, -1.042] | 10/0/0 | 0.0020 | 0.0742 |
| eta=0.85: PC-MALNS [MC-CRIP] | 10 | 1.702 | 1.713 | -0.012 [-0.040, +0.017] | [-0.036, +0.010] | 6/0/4 | 0.4922 | 1.0000 |
| eta=0.85: PC-MALNS [Quota-Surplus] | 10 | 1.702 | 1.713 | -0.011 [-0.039, +0.016] | [-0.035, +0.010] | 5/0/5 | 0.5566 | 1.0000 |
| eta=0.85: Opt-Rollback | 10 | 1.702 | 1.620 | +0.081 [+0.048, +0.114] | [+0.055, +0.110] | 0/0/10 | 0.0020 | 0.0742 |
| eta=0.85: Opt-SeqLock | 10 | 1.702 | 1.618 | +0.084 [+0.050, +0.117] | [+0.058, +0.113] | 0/0/10 | 0.0020 | 0.0742 |
| eta=0.85: Static-Quota | 10 | 1.702 | 1.648 | +0.054 [+0.019, +0.089] | [+0.025, +0.083] | 1/0/9 | 0.0098 | 0.1465 |
| eta=0.85: HiGHS (1T, wall-matched) | 10 | 1.702 | 0.635 | +1.067 [+0.496, +1.637] | [+0.537, +1.374] | 1/0/9 | 0.0098 | 0.1465 |
| eta=0.85: HiGHS+LP-Round (1T, wall-matched) | 10 | 1.702 | 0.640 | +1.062 [+0.503, +1.621] | [+0.542, +1.379] | 1/0/9 | 0.0059 | 0.0938 |
| eta=0.85: HiGHS (1T, CPU-matched) | 10 | 1.702 | 0.285 | +1.417 [+1.337, +1.497] | [+1.347, +1.479] | 0/0/10 | 0.0020 | 0.0742 |
| eta=0.85: HiGHS (5s) | 10 | 1.702 | 0.296 | +1.406 [+1.321, +1.490] | [+1.332, +1.472] | 0/0/10 | 0.0020 | 0.0742 |
| eta=1.05: LP-Round | 10 | 1.768 | 3.028 | -1.260 [-1.382, -1.138] | [-1.363, -1.162] | 10/0/0 | 0.0020 | 0.0742 |
| eta=1.05: PC-MALNS [MC-CRIP] | 10 | 1.768 | 1.793 | -0.025 [-0.049, -0.001] | [-0.045, -0.005] | 8/0/2 | 0.0488 | 0.5371 |
| eta=1.05: PC-MALNS [Quota-Surplus] | 10 | 1.768 | 1.781 | -0.013 [-0.037, +0.012] | [-0.032, +0.008] | 6/0/4 | 0.2324 | 1.0000 |
| eta=1.05: Opt-Rollback | 10 | 1.768 | 1.737 | +0.031 [-0.020, +0.083] | [-0.010, +0.074] | 4/0/6 | 0.3223 | 1.0000 |
| eta=1.05: Opt-SeqLock | 10 | 1.768 | 1.715 | +0.053 [+0.009, +0.096] | [+0.017, +0.089] | 3/0/7 | 0.0488 | 0.5371 |
| eta=1.05: Static-Quota | 10 | 1.768 | 2.490 | -0.722 [-0.772, -0.672] | [-0.760, -0.679] | 10/0/0 | 0.0020 | 0.0742 |
| eta=1.05: HiGHS (1T, wall-matched) | 10 | 1.768 | 3.044 | -1.276 [-2.156, -0.397] | [-1.908, -0.480] | 8/0/2 | 0.0137 | 0.1777 |
| eta=1.05: HiGHS+LP-Round (1T, wall-matched) | 10 | 1.768 | 2.575 | -0.807 [-1.492, -0.122] | [-1.288, -0.176] | 8/0/2 | 0.0645 | 0.5801 |
| eta=1.05: HiGHS (1T, CPU-matched) | 10 | 1.768 | 0.585 | +1.183 [+0.997, +1.369] | [+1.018, +1.318] | 0/0/10 | 0.0020 | 0.0742 |
| eta=1.05: HiGHS (5s) | 10 | 1.768 | 0.585 | +1.183 [+0.997, +1.369] | [+1.018, +1.318] | 0/0/10 | 0.0020 | 0.0742 |
| eta=1.25: LP-Round | 10 | 1.554 | 3.032 | -1.478 [-1.607, -1.349] | [-1.582, -1.370] | 10/0/0 | 0.0020 | 0.0742 |
| eta=1.25: PC-MALNS [MC-CRIP] | 10 | 1.554 | 1.628 | -0.074 [-0.121, -0.027] | [-0.112, -0.034] | 7/0/3 | 0.0273 | 0.3281 |
| eta=1.25: Opt-Rollback | 10 | 1.554 | 1.771 | -0.216 [-0.261, -0.172] | [-0.252, -0.179] | 10/0/0 | 0.0020 | 0.0742 |
| eta=1.25: Opt-SeqLock | 10 | 1.554 | 1.770 | -0.215 [-0.265, -0.166] | [-0.255, -0.173] | 10/0/0 | 0.0020 | 0.0742 |
| eta=1.25: HiGHS (1T, wall-matched) | 10 | 1.554 | 1.507 | +0.047 [-0.924, +1.018] | [-0.807, +0.760] | 3/0/7 | 1.0000 | 1.0000 |
| eta=1.25: HiGHS+LP-Round (1T, wall-matched) | 10 | 1.554 | 1.423 | +0.131 [-0.718, +0.981] | [-0.606, +0.775] | 3/0/7 | 1.0000 | 1.0000 |
| eta=1.25: HiGHS (1T, CPU-matched) | 10 | 1.554 | 0.423 | +1.132 [+1.040, +1.224] | [+1.059, +1.208] | 0/0/10 | 0.0020 | 0.0742 |
| eta=1.25: HiGHS (5s) | 10 | 1.554 | 0.426 | +1.128 [+1.036, +1.221] | [+1.055, +1.206] | 0/0/10 | 0.0020 | 0.0742 |
| eta=1.45: LP-Round | 10 | 1.075 | 1.687 | -0.612 [-0.776, -0.448] | [-0.746, -0.475] | 10/0/0 | 0.0020 | 0.0742 |
| eta=1.45: PC-MALNS [MC-CRIP] | 10 | 1.075 | 1.076 | -0.001 [-0.026, +0.024] | [-0.022, +0.019] | 5/0/5 | 0.9219 | 1.0000 |
| eta=1.45: PC-MALNS [Quota-Surplus] | 10 | 1.075 | 1.097 | -0.022 [-0.050, +0.006] | [-0.047, -0.002] | 6/0/4 | 0.0840 | 0.6719 |
| eta=1.45: Opt-Rollback | 10 | 1.075 | 1.184 | -0.109 [-0.146, -0.072] | [-0.137, -0.078] | 10/0/0 | 0.0020 | 0.0742 |
| eta=1.45: Opt-SeqLock | 10 | 1.075 | 1.188 | -0.113 [-0.157, -0.069] | [-0.147, -0.075] | 9/0/1 | 0.0039 | 0.0742 |
| eta=1.45: Static-Quota | 10 | 1.075 | 1.609 | -0.535 [-0.675, -0.394] | [-0.649, -0.420] | 10/0/0 | 0.0020 | 0.0742 |
| eta=1.45: HiGHS (1T, wall-matched) | 10 | 1.075 | 0.442 | +0.633 [+0.524, +0.741] | [+0.548, +0.728] | 0/0/10 | 0.0020 | 0.0742 |
| eta=1.45: HiGHS+LP-Round (1T, wall-matched) | 10 | 1.075 | 0.416 | +0.659 [+0.553, +0.764] | [+0.578, +0.750] | 0/0/10 | 0.0020 | 0.0742 |
| eta=1.45: HiGHS (1T, CPU-matched) | 10 | 1.075 | 0.373 | +0.701 [+0.610, +0.793] | [+0.632, +0.783] | 0/0/10 | 0.0020 | 0.0742 |
| eta=1.45: HiGHS (5s) | 10 | 1.075 | 0.381 | +0.694 [+0.601, +0.787] | [+0.623, +0.779] | 0/0/10 | 0.0020 | 0.0742 |

**HiGHS (1T, wall-matched) by eta: incumbents, first incumbent (s), nodes, limit (s)**

| eta | n_inc | t_first | nodes | highs_time_limit_s |
|---|---|---|---|---|
| 0.850 | 4.100 | 0.048 | 0.000 | 1.516 |
| 1.050 | 3.200 | 0.049 | 0.000 | 1.512 |
| 1.250 | 3.600 | 0.050 | 0.000 | 1.512 |
| 1.450 | 4.300 | 0.045 | 0.000 | 1.512 |

**Sweep: time to target (s)**

| eta | n | never | ttt_median | ttt_max | lns_wall_median | ratio_median | ratio_cpu_median |
|---|---|---|---|---|---|---|---|
| 0.850 | 10 | 0 | 1.220 | 1.866 | 1.515 | 0.805 | 0.213 |
| 1.050 | 10 | 0 | 1.848 | 2.938 | 1.513 | 1.219 | 0.323 |
| 1.250 | 10 | 0 | 1.677 | 2.078 | 1.512 | 1.109 | 0.297 |
| 1.450 | 10 | 0 | 1.133 | 1.314 | 1.511 | 0.747 | 0.201 |

## MCA-SC-Pair: wall clock (uniform conditions)


**Mean gap (%)**

| method | Medium | Large | All |
|---|---|---|---|
| LP-Round | 4.569 | 3.723 | 4.146 |
| PC-MALNS [Greedy-Efficiency] | 2.160 | 1.813 | 1.986 |
| PC-MALNS [MC-CRIP] | 2.225 | 1.902 | 2.064 |
| PC-MALNS [Quota-Surplus] | 2.257 | 1.859 | 2.058 |
| PC-MALNS [Greedy-Gain] | 2.221 | 1.925 | 2.073 |
| Opt-Rollback-Portfolio | 2.432 | 2.100 | 2.266 |
| Opt-SeqLock-Portfolio | 2.396 | 2.058 | 2.227 |
| Opt-Rollback | 2.416 | 2.103 | 2.259 |
| Opt-SeqLock | 2.411 | 2.076 | 2.243 |
| HiGHS (1T, wall-matched) | 1.169 | 1.733 | 1.451 |
| HiGHS (4T, wall-matched) | 1.167 | 1.717 | 1.442 |
| HiGHS (1T, CPU-matched) | 0.961 | 0.622 | 0.791 |
| HiGHS+LP-Round (1T, wall-matched) | 1.145 | 1.918 | 1.532 |
| HiGHS+LP-Round (1T, CPU-matched) | 0.912 | 0.624 | 0.768 |
| HiGHS (5s) | 0.870 | 0.622 | 0.746 |
| HiGHS (60s) | 0.541 | 0.427 | 0.484 |

**Pair (wall clock): PC-MALNS [Greedy-Efficiency] vs each** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| LP-Round | 20 | 1.986 | 4.146 | -2.159 [-2.331, -1.988] | [-2.312, -2.000] | 20/0/0 | <1e-4 | <1e-4 |
| PC-MALNS [MC-CRIP] | 20 | 1.986 | 2.064 | -0.077 [-0.116, -0.038] | [-0.112, -0.042] | 15/0/5 | 0.0010 | 0.0061 |
| PC-MALNS [Quota-Surplus] | 20 | 1.986 | 2.058 | -0.071 [-0.110, -0.033] | [-0.107, -0.036] | 17/0/3 | 0.0010 | 0.0061 |
| PC-MALNS [Greedy-Gain] | 20 | 1.986 | 2.073 | -0.087 [-0.146, -0.027] | [-0.140, -0.033] | 15/0/5 | 0.0056 | 0.0169 |
| Opt-Rollback-Portfolio | 20 | 1.986 | 2.266 | -0.279 [-0.333, -0.226] | [-0.330, -0.231] | 20/0/0 | <1e-4 | <1e-4 |
| Opt-SeqLock-Portfolio | 20 | 1.986 | 2.227 | -0.241 [-0.296, -0.185] | [-0.292, -0.192] | 20/0/0 | <1e-4 | <1e-4 |
| Opt-Rollback | 20 | 1.986 | 2.259 | -0.273 [-0.321, -0.225] | [-0.317, -0.229] | 20/0/0 | <1e-4 | <1e-4 |
| Opt-SeqLock | 20 | 1.986 | 2.243 | -0.257 [-0.317, -0.197] | [-0.312, -0.203] | 20/0/0 | <1e-4 | <1e-4 |
| HiGHS (1T, wall-matched) | 20 | 1.986 | 1.451 | +0.536 [+0.091, +0.981] | [+0.077, +0.885] | 4/0/16 | 0.0049 | 0.0169 |
| HiGHS (4T, wall-matched) | 20 | 1.986 | 1.442 | +0.544 [+0.098, +0.990] | [+0.084, +0.894] | 4/0/16 | 0.0042 | 0.0169 |
| HiGHS (1T, CPU-matched) | 20 | 1.986 | 0.791 | +1.195 [+1.069, +1.321] | [+1.088, +1.315] | 0/0/20 | <1e-4 | <1e-4 |
| HiGHS+LP-Round (1T, wall-matched) | 20 | 1.986 | 1.532 | +0.455 [+0.002, +0.907] | [+0.018, +0.837] | 5/0/15 | 0.0296 | 0.0296 |
| HiGHS+LP-Round (1T, CPU-matched) | 20 | 1.986 | 0.768 | +1.218 [+1.097, +1.340] | [+1.112, +1.331] | 0/0/20 | <1e-4 | <1e-4 |
| HiGHS (5s) | 20 | 1.986 | 0.746 | +1.240 [+1.123, +1.358] | [+1.140, +1.352] | 0/0/20 | <1e-4 | <1e-4 |

**Pair: time to target (s)**

| scale | n | never | ttt_median | ttt_max | lns_wall_median | ratio_median | ratio_cpu_median |
|---|---|---|---|---|---|---|---|
| Large | 10 | 0 | 1.774 | 2.517 | 1.514 | 1.171 | 0.314 |
| Medium | 10 | 0 | 0.836 | 1.191 | 1.008 | 0.827 | 0.227 |

## MMKP (wall clock; excluded: INST04)


**Mean gap to the best known solution (%)**

| method | I07-I13 | INST01-20 | All |
|---|---|---|---|
| LP-Round | – | 0.476 | 0.476 |
| PC-MALNS [Greedy-Efficiency] | 2.959 | 2.481 | 2.609 |
| PC-MALNS [MC-CRIP] | 2.951 | 2.469 | 2.598 |
| PC-MALNS [Quota-Surplus] | 2.977 | 2.485 | 2.618 |
| Opt-Rollback | 2.919 | 2.521 | 2.628 |
| Opt-SeqLock | 2.947 | 2.468 | 2.597 |
| Static-Quota | 3.131 | 2.828 | 2.909 |
| HiGHS (1T, wall-matched) | 0.095 | 0.245 | 0.204 |
| HiGHS (4T, wall-matched) | 0.095 | 0.200 | 0.172 |
| HiGHS (1T, CPU-matched) | 0.065 | 0.177 | 0.147 |
| HiGHS (5s) | 0.081 | 0.197 | 0.166 |
| HiGHS (60s) | 0.037 | 0.127 | 0.102 |

**MMKP: PC-MALNS [Greedy-Efficiency] vs each method** (difference = reference − method; negative favours the reference)

| Method | n | Ref | Method | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| PC-MALNS [MC-CRIP] | 26 | 2.609 | 2.598 | +0.011 [+0.001, +0.022] | [+0.003, +0.022] | 2/17/7 | 0.0195 | 0.0781 |
| PC-MALNS [Quota-Surplus] | 26 | 2.609 | 2.618 | -0.008 [-0.035, +0.018] | [-0.033, +0.018] | 7/16/3 | 0.4316 | 0.8633 |
| Opt-Rollback | 26 | 2.609 | 2.628 | -0.019 [-0.052, +0.014] | [-0.050, +0.012] | 8/13/5 | 0.2439 | 0.7317 |
| Opt-SeqLock | 26 | 2.609 | 2.597 | +0.012 [-0.018, +0.043] | [-0.014, +0.042] | 7/12/7 | 0.5830 | 0.8633 |
| Static-Quota | 26 | 2.609 | 2.909 | -0.300 [-0.501, -0.099] | [-0.512, -0.138] | 17/9/0 | <1e-4 | <1e-4 |
| HiGHS (1T, wall-matched) | 26 | 2.609 | 0.204 | +2.405 [+1.741, +3.070] | [+1.788, +3.024] | 0/0/26 | <1e-4 | <1e-4 |
| HiGHS (4T, wall-matched) | 26 | 2.609 | 0.172 | +2.438 [+1.759, +3.116] | [+1.809, +3.072] | 0/0/26 | <1e-4 | <1e-4 |
| HiGHS (1T, CPU-matched) | 26 | 2.609 | 0.147 | +2.463 [+1.784, +3.142] | [+1.836, +3.096] | 0/0/26 | <1e-4 | <1e-4 |
| HiGHS (5s) | 26 | 2.609 | 0.166 | +2.443 [+1.769, +3.118] | [+1.821, +3.072] | 0/0/26 | <1e-4 | <1e-4 |
| HiGHS (60s) | 26 | 2.609 | 0.102 | +2.507 [+1.817, +3.197] | [+1.871, +3.152] | 0/0/26 | <1e-4 | <1e-4 |

## Run conditions

- {"n_calib": 34, "base_wall": 0.9471296249976148, "base_cpu": 3.5031104790323297, "objective_identical": true, "flagged": [{"index": 15, "job": "rich", "time": "2026-11-17T21:03:39+05:30", "drift_wall": 0.7324, "drift_cpu": 0.7713}, {"index": 16, "job": "rich", "time": "2026-11-17T22:13:41+05:30", "drift_wall": 0.7308, "drift_cpu": 0.7723}, {"index": 17, "job": "rich", "time": "2026-11-17T23:11:36+05:30", "drift_wall": 0.7281, "drift_cpu": 0.7671}, {"index": 30, "job": "mmkp", "time": "2026-11-19T07:11:32+05:30", "drift_wall": 1.0933, "drift_cpu": 1.1288}, {"index": 31, "job": "mmkp", "time": "2026-11-19T07:27:03+05:30", "drift_wall": 1.1889, "drift_cpu": 1.2313}, {"index": 35, "job": "rich_rerun", "time": "2026-11-20T11:15:57+05:30", "drift_wall": 0.7481, "drift_cpu": 0.781}, {"index": 36, "job": "rich_rerun", "time": "2026-11-20T12:15:36+05:30", "drift_wall": 0.3932, "drift_cpu": 0.4211}], "max_abs_drift_unflagged": 0.0756, "power_main": ["AC Power"], "power_rich": ["AC Power"], "power_sweep": ["AC Power"], "power_pair": ["AC Power"], "power_mmkp": ["AC Power"], "power_rich_rerun": ["AC Power"], "power_waits": [{"job": "sweep", "instance": "MCA_SC_K12_N600_P6_eta1.05_s104", "wait_s": 7384.1}, {"job": "pair", "instance": "MCA_SC_PAIR_K12_N600_P6_eta1.25_s104", "wait_s": 43343.1}], "rows": 9182, "n_reference": 257, "killed": [{"job": "rich", "instance_name": "MCA_SC_K16_N960_P20_eta1.25_s103"}, {"job": "rich", "instance_name": "MCA_SC_K16_N960_P20_eta1.25_s108"}, {"job": "rich", "instance_name": "MCA_SC_K8_N320_P40_eta1.25_s107"}, {"job": "rich_rerun", "instance_name": "MCA_SC_K16_N960_P20_eta1.25_s103"}, {"job": "rich_rerun", "instance_name": "MCA_SC_K16_N960_P20_eta1.25_s108"}, {"job": "rich_rerun", "instance_name": "MCA_SC_K8_N320_P40_eta1.25_s107"}], "reference_optimal": 0}

## Repeatability of wall-clock runs (revision-2 reruns)

- lp_round: n = 300, epochs_rerun = 58.72, epochs_orig = 58.75, epochs_ratio = 0.9994, identical_share = 0.8033, mean_abs_diff_all = 0.004225, mean_abs_diff_nonidentical = 0.02148, conflict_rerun = 8.703, conflict_orig = 9.536
- direct: n = 300, epochs_rerun = 52.63, epochs_orig = 42.77, epochs_ratio = 1.23, identical_share = 0.4933, mean_abs_diff_all = 0.06297, mean_abs_diff_nonidentical = 0.1243, conflict_rerun = 26.1, conflict_orig = 29.95
