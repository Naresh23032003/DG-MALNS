
## Table A — main benchmark (P = 6, η = 1.25, LP-Round start, W = 4)


**Mean gap to LB (%) by scale**

| Method | Small | Medium | Large | X-Large | XXL | XXXL | All |
|---|---|---|---|---|---|---|---|
| LP-Round | 5.113 | 3.673 | 3.054 | 2.611 | 1.616 | 1.310 | 2.896 |
| PC-MALNS [MC-CRIP] | 2.547 | 1.832 | 1.656 | 1.411 | 0.902 | 0.733 | 1.514 |
| HiGHS (5s) | 0.899 | 0.687 | 0.475 | 0.449 | 1.739 | 1.458 | 0.951 |
| HiGHS (60s) | 0.590 | 0.417 | 0.357 | 0.338 | 0.222 | 0.164 | 0.348 |
| HiGHS (600s) | 0.472 | 0.324 | – | – | – | – | 0.398 |
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

**Mean primal integral (s × gap fraction) by scale**

| Method | Small | Medium | Large | X-Large | XXL | XXXL | All |
|---|---|---|---|---|---|---|---|
| PC-MALNS [MC-CRIP] | 0.0212 | 0.0346 | 0.0543 | 0.0775 | 0.1735 | 0.2867 | 0.1080 |
| HiGHS (5s) | 0.0710 | 0.0702 | 0.0844 | 0.1051 | 0.0841 | 0.0692 | 0.0807 |
| HiGHS (60s) | 0.4287 | 0.3368 | 0.3072 | 0.3058 | 0.2561 | 0.2713 | 0.3177 |
| HiGHS (600s) | 3.0915 | 2.2812 | – | – | – | – | 2.6863 |
| PC-MALNS [BCRM-Greedy] | 0.0210 | 0.0345 | 0.0535 | 0.0757 | 0.1691 | 0.2822 | 0.1060 |
| Greedy-Efficiency-Portfolio | 0.0210 | 0.0338 | 0.0526 | 0.0748 | 0.1683 | 0.2805 | 0.1052 |
| Greedy-Gain-Portfolio | 0.0212 | 0.0341 | 0.0536 | 0.0760 | 0.1708 | 0.2852 | 0.1068 |
| Opt-Rollback | 0.0218 | 0.0362 | 0.0559 | 0.0790 | 0.1753 | 0.2910 | 0.1099 |
| Opt-SeqLock | 0.0211 | 0.0360 | 0.0554 | 0.0784 | 0.1727 | 0.2862 | 0.1083 |
| Opt-Rollback-Portfolio | 0.0220 | 0.0369 | 0.0576 | 0.0813 | 0.1785 | 0.2960 | 0.1120 |
| Opt-SeqLock-Portfolio | 0.0215 | 0.0362 | 0.0560 | 0.0785 | 0.1732 | 0.2865 | 0.1087 |
| Static-Quota | 0.0284 | 0.0461 | 0.0670 | 0.0907 | 0.1872 | 0.3032 | 0.1204 |
| Demand-Quota | 0.0267 | 0.0440 | 0.0645 | 0.0873 | 0.1833 | 0.2983 | 0.1174 |
| HiGHS (1T, wall-matched) | 0.0230 | 0.0395 | 0.0489 | 0.0587 | 0.0681 | 0.0849 | 0.0538 |
| HiGHS (4T, wall-matched) | 0.0232 | 0.0391 | 0.0491 | 0.0589 | 0.0682 | 0.0849 | 0.0539 |
| HiGHS (1T, CPU-matched) | 0.0376 | 0.0609 | 0.0865 | 0.1129 | 0.1515 | 0.2039 | 0.1089 |

**PC-MALNS [MC-CRIP]: mean wall clock, CPU time and conflict rate**

| scale | wall_clock_s | cpu_time_s | conflict_rate_pct |
|---|---|---|---|
| Small | 0.504 | 1.733 | 3.323 |
| Medium | 1.007 | 3.638 | 5.122 |
| Large | 1.517 | 5.448 | 10.261 |
| X-Large | 2.031 | 6.911 | 14.980 |
| XXL | 4.077 | 12.930 | 18.101 |
| XXXL | 6.111 | 19.425 | 22.390 |

**Table A pooled over 60 instances: PC-MALNS [MC-CRIP] vs each method** (difference = reference − method; negative favours the reference)

| Method | n | Ref mean | Method mean | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| LP-Round | 60 | 1.514 | 2.896 | -1.382 [-1.578, -1.187] | [-1.574, -1.200] | 60/0/0 | <1e-4 | <1e-4 |
| HiGHS (5s) | 60 | 1.514 | 0.951 | +0.562 [+0.304, +0.820] | [+0.309, +0.810] | 20/0/40 | <1e-4 | <1e-4 |
| HiGHS (60s) | 60 | 1.514 | 0.348 | +1.166 [+1.036, +1.295] | [+1.043, +1.293] | 0/0/60 | <1e-4 | <1e-4 |
| HiGHS (600s) | 20 | 2.189 | 0.398 | +1.792 [+1.617, +1.966] | [+1.638, +1.954] | 0/0/20 | <1e-4 | <1e-4 |
| PC-MALNS [BCRM-Greedy] | 60 | 1.514 | 1.526 | -0.012 [-0.026, +0.001] | [-0.025, +0.001] | 40/0/20 | 0.0294 | 0.0336 |
| Greedy-Efficiency-Portfolio | 60 | 1.514 | 1.487 | +0.026 [+0.010, +0.043] | [+0.009, +0.041] | 16/0/44 | <1e-4 | <1e-4 |
| Greedy-Gain-Portfolio | 60 | 1.514 | 1.550 | -0.036 [-0.057, -0.015] | [-0.057, -0.016] | 46/0/14 | 0.0003 | 0.0012 |
| Opt-Rollback | 60 | 1.514 | 1.683 | -0.169 [-0.200, -0.139] | [-0.199, -0.140] | 58/0/2 | <1e-4 | <1e-4 |
| Opt-SeqLock | 60 | 1.514 | 1.659 | -0.145 [-0.172, -0.118] | [-0.172, -0.119] | 56/0/4 | <1e-4 | <1e-4 |
| Opt-Rollback-Portfolio | 60 | 1.514 | 1.686 | -0.172 [-0.200, -0.144] | [-0.201, -0.145] | 57/0/3 | <1e-4 | <1e-4 |
| Opt-SeqLock-Portfolio | 60 | 1.514 | 1.645 | -0.131 [-0.156, -0.107] | [-0.154, -0.107] | 57/0/3 | <1e-4 | <1e-4 |
| Static-Quota | 60 | 1.514 | 2.443 | -0.929 [-1.050, -0.808] | [-1.046, -0.814] | 60/0/0 | <1e-4 | <1e-4 |
| Demand-Quota | 60 | 1.514 | 2.244 | -0.730 [-0.826, -0.634] | [-0.823, -0.639] | 60/0/0 | <1e-4 | <1e-4 |
| HiGHS (1T, wall-matched) | 60 | 1.514 | 2.084 | -0.570 [-0.887, -0.254] | [-0.871, -0.261] | 44/0/16 | 0.0030 | 0.0089 |
| HiGHS (4T, wall-matched) | 60 | 1.514 | 1.956 | -0.443 [-0.760, -0.125] | [-0.746, -0.133] | 41/0/19 | 0.0168 | 0.0336 |
| HiGHS (1T, CPU-matched) | 60 | 1.514 | 0.512 | +1.001 [+0.907, +1.096] | [+0.912, +1.096] | 0/0/60 | <1e-4 | <1e-4 |

**HiGHS reference runs (1 thread)**

| scale | n | proven_optimal | time_limit_s | mean_time_s |
|---|---|---|---|---|
| Small | 10 | 0 | 600.000 | 600.051 |
| Medium | 10 | 0 | 600.000 | 600.011 |
| Large | 10 | 0 | 60.000 | 60.014 |
| X-Large | 10 | 0 | 60.000 | 60.032 |
| XXL | 10 | 0 | 60.000 | 60.118 |
| XXXL | 10 | 0 | 60.000 | 60.014 |

## Table B — rich candidate pools (P = 20, 40), W = 4 wall clock


**P = 20: mean gap to LB (%)**

| Method | Medium | Large | X-Large | XXL | All |
|---|---|---|---|---|---|
| LP-Round | 4.502 | 3.662 | 3.005 | 1.890 | 3.265 |
| PC-MALNS [MC-CRIP] | 2.999 | 2.510 | 2.143 | 1.404 | 2.264 |
| HiGHS (30s) | 1.790 | 2.073 | 0.666 | 0.948 | 1.369 |
| PC-MALNS [BCRM-Greedy] | 3.027 | 2.521 | 2.150 | 1.374 | 2.268 |
| Greedy-Efficiency-Portfolio | 2.912 | 2.488 | 2.092 | 1.358 | 2.213 |
| Opt-Rollback | 3.215 | 2.794 | 2.391 | 1.548 | 2.487 |
| Opt-SeqLock | 3.213 | 2.830 | 2.381 | 1.559 | 2.496 |
| HiGHS (1T, wall-matched) | 5.381 | 4.273 | 3.440 | 2.158 | 3.813 |
| HiGHS (4T, wall-matched) | 5.381 | 4.273 | 3.440 | 2.158 | 3.813 |
| HiGHS (1T, CPU-matched) | 5.381 | 4.273 | 3.440 | 2.158 | 3.813 |

**P = 20: mean primal integral**

| Method | Medium | Large | X-Large | XXL | All |
|---|---|---|---|---|---|
| PC-MALNS [MC-CRIP] | 0.0690 | 0.1142 | 0.1753 | 0.4218 | 0.1951 |
| HiGHS (30s) | 0.8775 | 0.8370 | 0.6223 | 0.5716 | 0.7271 |
| PC-MALNS [BCRM-Greedy] | 0.0691 | 0.1141 | 0.1746 | 0.4207 | 0.1946 |
| Greedy-Efficiency-Portfolio | 0.0681 | 0.1135 | 0.1735 | 0.4190 | 0.1935 |
| Opt-Rollback | 0.0707 | 0.1176 | 0.1786 | 0.4264 | 0.1983 |
| Opt-SeqLock | 0.0703 | 0.1173 | 0.1776 | 0.4242 | 0.1974 |
| HiGHS (1T, wall-matched) | 0.0497 | 0.0592 | 0.0644 | 0.0792 | 0.0631 |
| HiGHS (4T, wall-matched) | 0.0500 | 0.0596 | 0.0646 | 0.0792 | 0.0634 |
| HiGHS (1T, CPU-matched) | 0.1856 | 0.2204 | 0.2313 | 0.2800 | 0.2293 |

**P = 20 pooled: PC-MALNS [MC-CRIP] vs each method** (difference = reference − method; negative favours the reference)

| Method | n | Ref mean | Method mean | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| LP-Round | 40 | 2.264 | 3.265 | -1.001 [-1.137, -0.864] | [-1.132, -0.875] | 40/0/0 | <1e-4 | <1e-4 |
| HiGHS (30s) | 40 | 2.264 | 1.369 | +0.895 [+0.376, +1.413] | [+0.393, +1.368] | 11/0/29 | 0.0013 | 0.0026 |
| PC-MALNS [BCRM-Greedy] | 40 | 2.264 | 2.268 | -0.004 [-0.030, +0.021] | [-0.030, +0.019] | 21/0/19 | 0.6656 | 0.6656 |
| Greedy-Efficiency-Portfolio | 40 | 2.264 | 2.213 | +0.051 [+0.033, +0.069] | [+0.034, +0.069] | 5/0/35 | <1e-4 | <1e-4 |
| Opt-Rollback | 40 | 2.264 | 2.487 | -0.223 [-0.265, -0.182] | [-0.264, -0.185] | 39/0/1 | <1e-4 | <1e-4 |
| Opt-SeqLock | 40 | 2.264 | 2.496 | -0.232 [-0.271, -0.193] | [-0.271, -0.195] | 39/0/1 | <1e-4 | <1e-4 |
| HiGHS (1T, wall-matched) | 40 | 2.264 | 3.813 | -1.549 [-1.787, -1.311] | [-1.777, -1.330] | 40/0/0 | <1e-4 | <1e-4 |
| HiGHS (4T, wall-matched) | 40 | 2.264 | 3.813 | -1.549 [-1.787, -1.311] | [-1.777, -1.330] | 40/0/0 | <1e-4 | <1e-4 |
| HiGHS (1T, CPU-matched) | 40 | 2.264 | 3.813 | -1.549 [-1.787, -1.311] | [-1.777, -1.330] | 40/0/0 | <1e-4 | <1e-4 |

**P = 20 pooled, primal integral: PC-MALNS [MC-CRIP] vs each method** (difference = reference − method; negative favours the reference)

| Method | n | Ref mean | Method mean | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| HiGHS (30s) | 40 | 0.195 | 0.727 | -0.532 [-0.662, -0.402] | [-0.662, -0.412] | 40/0/0 | <1e-4 | <1e-4 |
| PC-MALNS [BCRM-Greedy] | 40 | 0.195 | 0.195 | +0.000 [+0.000, +0.001] | [+0.000, +0.001] | 16/0/24 | 0.0269 | 0.0537 |
| Greedy-Efficiency-Portfolio | 40 | 0.195 | 0.194 | +0.002 [+0.001, +0.002] | [+0.001, +0.002] | 2/0/38 | <1e-4 | <1e-4 |
| Opt-Rollback | 40 | 0.195 | 0.198 | -0.003 [-0.004, -0.003] | [-0.004, -0.003] | 38/0/2 | <1e-4 | <1e-4 |
| Opt-SeqLock | 40 | 0.195 | 0.197 | -0.002 [-0.003, -0.002] | [-0.003, -0.002] | 37/0/3 | <1e-4 | <1e-4 |
| HiGHS (1T, wall-matched) | 40 | 0.195 | 0.063 | +0.132 [+0.091, +0.173] | [+0.095, +0.173] | 0/0/40 | <1e-4 | <1e-4 |
| HiGHS (4T, wall-matched) | 40 | 0.195 | 0.063 | +0.132 [+0.091, +0.173] | [+0.095, +0.173] | 0/0/40 | <1e-4 | <1e-4 |
| HiGHS (1T, CPU-matched) | 40 | 0.195 | 0.229 | -0.034 [-0.069, +0.000] | [-0.065, +0.000] | 30/0/10 | 0.2766 | 0.2766 |

**P = 40: mean gap to LB (%)**

| Method | Medium | Large | X-Large | XXL | All |
|---|---|---|---|---|---|
| LP-Round | 4.619 | 3.511 | 2.904 | 1.774 | 3.202 |
| PC-MALNS [MC-CRIP] | 3.033 | 2.470 | 2.111 | 1.368 | 2.246 |
| HiGHS (30s) | 3.692 | 3.556 | 1.229 | 2.411 | 2.722 |
| PC-MALNS [BCRM-Greedy] | 3.019 | 2.474 | 2.175 | 1.371 | 2.260 |
| Greedy-Efficiency-Portfolio | 2.949 | 2.425 | 2.121 | 1.355 | 2.212 |
| Opt-Rollback | 3.226 | 2.730 | 2.407 | 1.555 | 2.480 |
| Opt-SeqLock | 3.278 | 2.785 | 2.376 | 1.546 | 2.496 |
| HiGHS (1T, wall-matched) | 5.724 | 4.441 | 3.851 | 2.411 | 4.107 |
| HiGHS (4T, wall-matched) | 5.724 | 4.441 | 3.851 | 2.444 | 4.115 |
| HiGHS (1T, CPU-matched) | 5.724 | 4.441 | 3.851 | 2.411 | 4.107 |

**P = 40: mean primal integral**

| Method | Medium | Large | X-Large | XXL | All |
|---|---|---|---|---|---|
| PC-MALNS [MC-CRIP] | 0.0965 | 0.1741 | 0.2953 | 0.7256 | 0.3229 |
| HiGHS (30s) | 1.1679 | 1.1263 | 0.8915 | 0.6859 | 0.9679 |
| PC-MALNS [BCRM-Greedy] | 0.0963 | 0.1734 | 0.2952 | 0.7237 | 0.3221 |
| Greedy-Efficiency-Portfolio | 0.0957 | 0.1726 | 0.2937 | 0.7243 | 0.3216 |
| Opt-Rollback | 0.0979 | 0.1763 | 0.2978 | 0.7292 | 0.3253 |
| Opt-SeqLock | 0.0982 | 0.1764 | 0.2968 | 0.7271 | 0.3246 |
| HiGHS (1T, wall-matched) | 0.0500 | 0.0584 | 0.0643 | 0.0759 | 0.0622 |
| HiGHS (4T, wall-matched) | 0.0506 | 0.0590 | 0.0653 | 0.0745 | 0.0624 |
| HiGHS (1T, CPU-matched) | 0.1900 | 0.2197 | 0.2437 | 0.2892 | 0.2357 |

**P = 40 pooled: PC-MALNS [MC-CRIP] vs each method** (difference = reference − method; negative favours the reference)

| Method | n | Ref mean | Method mean | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| LP-Round | 40 | 2.246 | 3.202 | -0.957 [-1.110, -0.803] | [-1.106, -0.817] | 40/0/0 | <1e-4 | <1e-4 |
| HiGHS (30s) | 40 | 2.246 | 2.722 | -0.477 [-1.070, +0.117] | [-1.035, +0.084] | 28/0/12 | 0.4680 | 0.4680 |
| PC-MALNS [BCRM-Greedy] | 40 | 2.246 | 2.260 | -0.014 [-0.043, +0.014] | [-0.040, +0.013] | 26/0/14 | 0.0725 | 0.1450 |
| Greedy-Efficiency-Portfolio | 40 | 2.246 | 2.212 | +0.033 [+0.012, +0.055] | [+0.013, +0.055] | 14/0/26 | 0.0056 | 0.0167 |
| Opt-Rollback | 40 | 2.246 | 2.480 | -0.234 [-0.274, -0.194] | [-0.271, -0.196] | 38/0/2 | <1e-4 | <1e-4 |
| Opt-SeqLock | 40 | 2.246 | 2.496 | -0.251 [-0.279, -0.223] | [-0.278, -0.224] | 40/0/0 | <1e-4 | <1e-4 |
| HiGHS (1T, wall-matched) | 40 | 2.246 | 4.107 | -1.861 [-2.119, -1.602] | [-2.113, -1.626] | 40/0/0 | <1e-4 | <1e-4 |
| HiGHS (4T, wall-matched) | 40 | 2.246 | 4.115 | -1.869 [-2.126, -1.613] | [-2.120, -1.635] | 40/0/0 | <1e-4 | <1e-4 |
| HiGHS (1T, CPU-matched) | 40 | 2.246 | 4.107 | -1.861 [-2.119, -1.602] | [-2.113, -1.626] | 40/0/0 | <1e-4 | <1e-4 |

**P = 40 pooled, primal integral: PC-MALNS [MC-CRIP] vs each method** (difference = reference − method; negative favours the reference)

| Method | n | Ref mean | Method mean | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| HiGHS (30s) | 40 | 0.323 | 0.968 | -0.645 [-0.820, -0.470] | [-0.812, -0.481] | 33/0/7 | <1e-4 | <1e-4 |
| PC-MALNS [BCRM-Greedy] | 40 | 0.323 | 0.322 | +0.001 [-0.000, +0.002] | [+0.000, +0.002] | 15/0/25 | 0.0770 | 0.1540 |
| Greedy-Efficiency-Portfolio | 40 | 0.323 | 0.322 | +0.001 [+0.000, +0.003] | [+0.000, +0.003] | 9/0/31 | 0.0008 | 0.0023 |
| Opt-Rollback | 40 | 0.323 | 0.325 | -0.002 [-0.004, -0.001] | [-0.003, -0.001] | 36/0/4 | <1e-4 | <1e-4 |
| Opt-SeqLock | 40 | 0.323 | 0.325 | -0.002 [-0.003, -0.001] | [-0.003, -0.001] | 34/0/6 | <1e-4 | <1e-4 |
| HiGHS (1T, wall-matched) | 40 | 0.323 | 0.062 | +0.261 [+0.184, +0.337] | [+0.192, +0.337] | 0/0/40 | <1e-4 | <1e-4 |
| HiGHS (4T, wall-matched) | 40 | 0.323 | 0.062 | +0.261 [+0.183, +0.338] | [+0.191, +0.337] | 0/0/40 | <1e-4 | <1e-4 |
| HiGHS (1T, CPU-matched) | 40 | 0.323 | 0.236 | +0.087 [+0.018, +0.156] | [+0.024, +0.156] | 21/0/19 | 0.4437 | 0.4437 |

## Table C — commit-rule isolation (Medium + Large)


**LP-Round start: mean gap (%)**

| Method | Medium | Large | All |
|---|---|---|---|
| PC-MALNS [MC-CRIP] | 1.832 | 1.656 | 1.744 |
| PC-MALNS [BCRM-Greedy] | 1.872 | 1.647 | 1.760 |
| Greedy-Efficiency-Portfolio | 1.800 | 1.585 | 1.693 |
| Greedy-Gain-Portfolio | 1.828 | 1.662 | 1.745 |
| Opt-Rollback-Portfolio | 2.042 | 1.819 | 1.930 |
| Opt-SeqLock-Portfolio | 2.033 | 1.812 | 1.922 |
| Opt-Rollback | 2.045 | 1.802 | 1.923 |
| Opt-SeqLock | 2.050 | 1.814 | 1.932 |

**LP-Round start: mean conflict rate (% of epochs)**

| Method | Medium | Large | All |
|---|---|---|---|
| PC-MALNS [MC-CRIP] | 5.1 | 10.3 | 7.7 |
| PC-MALNS [BCRM-Greedy] | 6.7 | 14.4 | 10.6 |
| Greedy-Efficiency-Portfolio | 6.8 | 13.9 | 10.3 |
| Greedy-Gain-Portfolio | 6.4 | 12.3 | 9.3 |
| Opt-Rollback-Portfolio | 17.3 | 38.4 | 27.9 |
| Opt-SeqLock-Portfolio | 9.1 | 16.6 | 12.9 |
| Opt-Rollback | 6.8 | 16.0 | 11.4 |
| Opt-SeqLock | 3.8 | 7.4 | 5.6 |

**LP-Round start: PC-MALNS [MC-CRIP] vs each commit rule** (difference = reference − method; negative favours the reference)

| Method | n | Ref mean | Method mean | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| PC-MALNS [BCRM-Greedy] | 20 | 1.744 | 1.760 | -0.016 [-0.042, +0.011] | [-0.039, +0.010] | 15/0/5 | 0.1769 | 0.3537 |
| Greedy-Efficiency-Portfolio | 20 | 1.744 | 1.693 | +0.052 [+0.021, +0.082] | [+0.024, +0.080] | 7/0/13 | 0.0094 | 0.0283 |
| Greedy-Gain-Portfolio | 20 | 1.744 | 1.745 | -0.001 [-0.033, +0.031] | [-0.029, +0.028] | 11/0/9 | 0.8408 | 0.8408 |
| Opt-Rollback-Portfolio | 20 | 1.744 | 1.930 | -0.186 [-0.230, -0.142] | [-0.229, -0.148] | 20/0/0 | <1e-4 | <1e-4 |
| Opt-SeqLock-Portfolio | 20 | 1.744 | 1.922 | -0.178 [-0.212, -0.144] | [-0.210, -0.149] | 20/0/0 | <1e-4 | <1e-4 |
| Opt-Rollback | 20 | 1.744 | 1.923 | -0.179 [-0.222, -0.136] | [-0.221, -0.141] | 20/0/0 | <1e-4 | <1e-4 |
| Opt-SeqLock | 20 | 1.744 | 1.932 | -0.188 [-0.223, -0.152] | [-0.221, -0.156] | 20/0/0 | <1e-4 | <1e-4 |

**Direct start: mean gap (%)**

| Method | Medium | Large | All |
|---|---|---|---|
| PC-MALNS [MC-CRIP] | 5.979 | 5.989 | 5.984 |
| PC-MALNS [BCRM-Greedy] | 5.636 | 5.819 | 5.727 |
| Greedy-Efficiency-Portfolio | 5.309 | 5.773 | 5.541 |
| Greedy-Gain-Portfolio | 6.231 | 6.181 | 6.206 |
| Opt-Rollback-Portfolio | 7.799 | 10.036 | 8.918 |
| Opt-SeqLock-Portfolio | 7.525 | 8.015 | 7.770 |
| Opt-Rollback | 7.255 | 7.283 | 7.269 |
| Opt-SeqLock | 7.662 | 7.461 | 7.562 |

**Direct start: mean conflict rate (% of epochs)**

| Method | Medium | Large | All |
|---|---|---|---|
| PC-MALNS [MC-CRIP] | 19.8 | 33.1 | 26.5 |
| PC-MALNS [BCRM-Greedy] | 25.2 | 39.6 | 32.4 |
| Greedy-Efficiency-Portfolio | 24.8 | 37.2 | 31.0 |
| Greedy-Gain-Portfolio | 22.7 | 38.9 | 30.8 |
| Opt-Rollback-Portfolio | 63.3 | 97.0 | 80.1 |
| Opt-SeqLock-Portfolio | 23.2 | 45.7 | 34.5 |
| Opt-Rollback | 25.4 | 47.6 | 36.5 |
| Opt-SeqLock | 10.7 | 20.8 | 15.8 |

**Direct start: PC-MALNS [MC-CRIP] vs each commit rule** (difference = reference − method; negative favours the reference)

| Method | n | Ref mean | Method mean | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| PC-MALNS [BCRM-Greedy] | 20 | 5.984 | 5.727 | +0.257 [+0.124, +0.390] | [+0.134, +0.378] | 3/0/17 | 0.0010 | 0.0020 |
| Greedy-Efficiency-Portfolio | 20 | 5.984 | 5.541 | +0.443 [+0.273, +0.613] | [+0.291, +0.598] | 4/0/16 | <1e-4 | 0.0002 |
| Greedy-Gain-Portfolio | 20 | 5.984 | 6.206 | -0.222 [-0.365, -0.079] | [-0.355, -0.090] | 15/0/5 | 0.0083 | 0.0083 |
| Opt-Rollback-Portfolio | 20 | 5.984 | 8.918 | -2.934 [-3.757, -2.110] | [-3.741, -2.248] | 20/0/0 | <1e-4 | <1e-4 |
| Opt-SeqLock-Portfolio | 20 | 5.984 | 7.770 | -1.786 [-2.168, -1.404] | [-2.167, -1.464] | 20/0/0 | <1e-4 | <1e-4 |
| Opt-Rollback | 20 | 5.984 | 7.269 | -1.285 [-1.606, -0.964] | [-1.572, -0.989] | 19/0/1 | <1e-4 | <1e-4 |
| Opt-SeqLock | 20 | 5.984 | 7.562 | -1.578 [-1.882, -1.273] | [-1.859, -1.303] | 20/0/0 | <1e-4 | <1e-4 |

**RPA-SH-Sync: mean gap (%)**

| Method | Medium | Large | All |
|---|---|---|---|
| PC-MALNS [MC-CRIP] | 2.297 | 1.941 | 2.119 |
| PC-MALNS [BCRM-Greedy] | 2.333 | 1.908 | 2.120 |
| Greedy-Efficiency-Portfolio | 2.216 | 1.853 | 2.035 |
| Greedy-Gain-Portfolio | 2.290 | 1.965 | 2.127 |
| Opt-Rollback-Portfolio | 2.500 | 2.155 | 2.327 |
| Opt-SeqLock-Portfolio | 2.459 | 2.105 | 2.282 |
| Opt-Rollback | 2.479 | 2.154 | 2.317 |
| Opt-SeqLock | 2.490 | 2.114 | 2.302 |

**RPA-SH-Sync: mean conflict rate (% of epochs)**

| Method | Medium | Large | All |
|---|---|---|---|
| PC-MALNS [MC-CRIP] | 11.5 | 15.3 | 13.4 |
| PC-MALNS [BCRM-Greedy] | 14.9 | 20.5 | 17.7 |
| Greedy-Efficiency-Portfolio | 12.9 | 20.8 | 16.8 |
| Greedy-Gain-Portfolio | 12.7 | 18.3 | 15.5 |
| Opt-Rollback-Portfolio | 33.6 | 59.0 | 46.3 |
| Opt-SeqLock-Portfolio | 15.3 | 22.7 | 19.0 |
| Opt-Rollback | 12.9 | 24.2 | 18.5 |
| Opt-SeqLock | 6.4 | 9.8 | 8.1 |

**RPA-SH-Sync: PC-MALNS [MC-CRIP] vs each commit rule** (difference = reference − method; negative favours the reference)

| Method | n | Ref mean | Method mean | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| PC-MALNS [BCRM-Greedy] | 20 | 2.119 | 2.120 | -0.002 [-0.042, +0.039] | [-0.038, +0.035] | 9/0/11 | 0.9563 | 1.0000 |
| Greedy-Efficiency-Portfolio | 20 | 2.119 | 2.035 | +0.084 [+0.039, +0.129] | [+0.043, +0.125] | 5/0/15 | 0.0014 | 0.0043 |
| Greedy-Gain-Portfolio | 20 | 2.119 | 2.127 | -0.009 [-0.052, +0.035] | [-0.047, +0.032] | 12/0/8 | 0.6477 | 1.0000 |
| Opt-Rollback-Portfolio | 20 | 2.119 | 2.327 | -0.209 [-0.242, -0.176] | [-0.239, -0.179] | 20/0/0 | <1e-4 | <1e-4 |
| Opt-SeqLock-Portfolio | 20 | 2.119 | 2.282 | -0.164 [-0.208, -0.119] | [-0.203, -0.123] | 19/0/1 | <1e-4 | <1e-4 |
| Opt-Rollback | 20 | 2.119 | 2.317 | -0.198 [-0.236, -0.160] | [-0.232, -0.162] | 20/0/0 | <1e-4 | <1e-4 |
| Opt-SeqLock | 20 | 2.119 | 2.302 | -0.183 [-0.231, -0.135] | [-0.228, -0.140] | 20/0/0 | <1e-4 | <1e-4 |

**RPA-SH-Sync (validation seeds): mean gap (%)**

| Method | Medium | Large | All |
|---|---|---|---|
| PC-MALNS [MC-CRIP] | 2.709 | 1.923 | 2.316 |
| PC-MALNS [BCRM-Greedy] | 2.599 | 1.813 | 2.206 |
| Greedy-Efficiency-Portfolio | 2.613 | 1.809 | 2.211 |
| Greedy-Gain-Portfolio | 2.647 | 1.847 | 2.247 |
| Opt-Rollback-Portfolio | 2.681 | 2.060 | 2.370 |
| Opt-SeqLock-Portfolio | 2.836 | 1.995 | 2.415 |
| Opt-Rollback | 2.781 | 2.097 | 2.439 |
| Opt-SeqLock | 2.779 | 2.043 | 2.411 |

**RPA-SH-Sync (validation seeds): mean conflict rate (% of epochs)**

| Method | Medium | Large | All |
|---|---|---|---|
| PC-MALNS [MC-CRIP] | 6.7 | 10.2 | 8.5 |
| PC-MALNS [BCRM-Greedy] | 10.3 | 17.9 | 14.1 |
| Greedy-Efficiency-Portfolio | 11.4 | 15.2 | 13.3 |
| Greedy-Gain-Portfolio | 8.1 | 16.2 | 12.2 |
| Opt-Rollback-Portfolio | 25.3 | 47.9 | 36.6 |
| Opt-SeqLock-Portfolio | 13.7 | 20.6 | 17.2 |
| Opt-Rollback | 10.8 | 19.1 | 15.0 |
| Opt-SeqLock | 5.6 | 8.4 | 7.0 |

**RPA-SH-Sync (validation seeds): PC-MALNS [MC-CRIP] vs each commit rule** (difference = reference − method; negative favours the reference)

| Method | n | Ref mean | Method mean | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| PC-MALNS [BCRM-Greedy] | 6 | 2.316 | 2.206 | +0.110 [+0.015, +0.205] | [+0.042, +0.174] | 1/0/5 | 0.0625 | 0.3125 |
| Greedy-Efficiency-Portfolio | 6 | 2.316 | 2.211 | +0.105 [+0.027, +0.184] | [+0.052, +0.157] | 0/0/6 | 0.0312 | 0.2188 |
| Greedy-Gain-Portfolio | 6 | 2.316 | 2.247 | +0.069 [-0.048, +0.187] | [-0.009, +0.148] | 2/0/4 | 0.2188 | 0.4688 |
| Opt-Rollback-Portfolio | 6 | 2.316 | 2.370 | -0.054 [-0.175, +0.067] | [-0.138, +0.029] | 4/0/2 | 0.5625 | 0.5625 |
| Opt-SeqLock-Portfolio | 6 | 2.316 | 2.415 | -0.099 [-0.230, +0.032] | [-0.198, -0.016] | 4/0/2 | 0.1562 | 0.4688 |
| Opt-Rollback | 6 | 2.316 | 2.439 | -0.123 [-0.230, -0.016] | [-0.198, -0.049] | 5/0/1 | 0.0625 | 0.3125 |
| Opt-SeqLock | 6 | 2.316 | 2.411 | -0.094 [-0.165, -0.024] | [-0.146, -0.049] | 6/0/0 | 0.0312 | 0.2188 |

**Counterfactual barrier analysis (all conflict epochs of the PC-MALNS [MC-CRIP] runs; every rule applied to the same portfolios)**

| regime | rule | mean_gain_per_conflict_epoch | share_of_mccrip_gain_pct | mccrip_strictly_better_pct | conflict_epochs |
|---|---|---|---|---|---|
| LP-Round start | MC-CRIP | 99.66 | 100.00 | 0.00 | 409 |
| LP-Round start | BCRM-Greedy | 79.31 | 79.58 | 58.19 | 409 |
| LP-Round start | Greedy-Efficiency | 83.68 | 83.97 | 51.34 | 409 |
| LP-Round start | Greedy-Gain | 83.63 | 83.92 | 43.03 | 409 |
| LP-Round start | Opt-SeqLock | 57.19 | 57.38 | 100.00 | 409 |
| LP-Round start | Opt-Rollback | 20.56 | 20.63 | 100.00 | 409 |
| LP-Round start | Static-Quota | 6.25 | 6.27 | 100.00 | 409 |
| Direct start | MC-CRIP | 2015.65 | 100.00 | 0.00 | 1109 |
| Direct start | BCRM-Greedy | 1925.09 | 95.51 | 54.28 | 1109 |
| Direct start | Greedy-Efficiency | 1694.25 | 84.05 | 47.61 | 1109 |
| Direct start | Greedy-Gain | 1876.82 | 93.11 | 37.78 | 1109 |
| Direct start | Opt-SeqLock | 1731.23 | 85.89 | 100.00 | 1109 |
| Direct start | Opt-Rollback | 213.94 | 10.61 | 100.00 | 1109 |
| Direct start | Static-Quota | 1502.18 | 74.53 | 100.00 | 1109 |
| RPA-SH-Sync | MC-CRIP | 105.57 | 100.00 | 0.00 | 437 |
| RPA-SH-Sync | BCRM-Greedy | 81.18 | 76.90 | 61.33 | 437 |
| RPA-SH-Sync | Greedy-Efficiency | 87.79 | 83.17 | 52.86 | 437 |
| RPA-SH-Sync | Greedy-Gain | 89.01 | 84.32 | 39.36 | 437 |
| RPA-SH-Sync | Opt-SeqLock | 63.79 | 60.42 | 99.77 | 437 |
| RPA-SH-Sync | Opt-Rollback | 20.45 | 19.37 | 100.00 | 437 |
| RPA-SH-Sync | Static-Quota | 6.12 | 5.80 | 100.00 | 437 |
| RPA-SH-Sync (validation seeds) | MC-CRIP | 119.07 | 100.00 | 0.00 | 119 |
| RPA-SH-Sync (validation seeds) | BCRM-Greedy | 90.73 | 76.20 | 63.87 | 119 |
| RPA-SH-Sync (validation seeds) | Greedy-Efficiency | 97.81 | 82.14 | 56.30 | 119 |
| RPA-SH-Sync (validation seeds) | Greedy-Gain | 99.04 | 83.18 | 43.70 | 119 |
| RPA-SH-Sync (validation seeds) | Opt-SeqLock | 73.45 | 61.69 | 100.00 | 119 |
| RPA-SH-Sync (validation seeds) | Opt-Rollback | 23.19 | 19.48 | 100.00 | 119 |
| RPA-SH-Sync (validation seeds) | Static-Quota | 7.89 | 6.63 | 100.00 | 119 |

## Table D — public MMKP benchmarks (27 instances, K = 8 agents)


**Mean gap to the best known solution (%; MMKP-feasible runs)**

| method | I07-I13 | INST01-20 | All |
|---|---|---|---|
| LP-Round | – | 0.476 | 0.476 |
| PC-MALNS [MC-CRIP] | 2.948 | 2.463 | 2.594 |
| PC-MALNS [BCRM-Greedy] | 2.980 | 2.481 | 2.615 |
| Opt-Rollback | 2.919 | 2.513 | 2.622 |
| Opt-SeqLock | 2.961 | 2.466 | 2.599 |
| Static-Quota | 3.131 | 2.828 | 2.909 |
| HiGHS (1T, wall-matched) | 0.089 | 0.233 | 0.195 |
| HiGHS (4T, wall-matched) | 0.089 | 0.233 | 0.195 |
| HiGHS (60s) | 0.049 | 0.152 | 0.125 |

**MMKP-feasible runs (%)**

| method | feasible_pct |
|---|---|
| LP-Round | 11.1 |
| PC-MALNS [MC-CRIP] | 96.3 |
| PC-MALNS [BCRM-Greedy] | 96.3 |
| Opt-Rollback | 96.3 |
| Opt-SeqLock | 96.3 |
| Static-Quota | 96.3 |
| HiGHS (1T, wall-matched) | 100.0 |
| HiGHS (4T, wall-matched) | 100.0 |
| HiGHS (60s) | 100.0 |

**MMKP: PC-MALNS [MC-CRIP] vs each method (gap to BKS)** (difference = reference − method; negative favours the reference)

| Method | n | Ref mean | Method mean | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| LP-Round | 3 | 0.182 | 0.476 | -0.294 [-1.367, +0.779] | [-0.792, -0.028] | 3/0/0 | 0.2500 | 0.7500 |
| PC-MALNS [BCRM-Greedy] | 26 | 2.594 | 2.615 | -0.022 [-0.053, +0.010] | [-0.053, +0.007] | 7/15/4 | 0.1748 | 0.6992 |
| Opt-Rollback | 26 | 2.594 | 2.622 | -0.029 [-0.066, +0.008] | [-0.064, +0.004] | 8/11/7 | 0.3028 | 0.7500 |
| Opt-SeqLock | 26 | 2.594 | 2.599 | -0.006 [-0.028, +0.017] | [-0.026, +0.015] | 7/12/7 | 0.7148 | 0.7500 |
| Static-Quota | 26 | 2.594 | 2.909 | -0.316 [-0.525, -0.107] | [-0.536, -0.146] | 17/9/0 | <1e-4 | <1e-4 |
| HiGHS (1T, wall-matched) | 26 | 2.594 | 0.187 | +2.406 [+1.743, +3.070] | [+1.790, +3.024] | 0/0/26 | <1e-4 | <1e-4 |
| HiGHS (4T, wall-matched) | 26 | 2.594 | 0.187 | +2.407 [+1.743, +3.070] | [+1.790, +3.024] | 0/0/26 | <1e-4 | <1e-4 |
| HiGHS (60s) | 26 | 2.594 | 0.119 | +2.475 [+1.798, +3.152] | [+1.847, +3.109] | 0/0/26 | <1e-4 | <1e-4 |

## Table E1 — coupling tightness sweep (Large)


**Mean gap (%) by tightness η**

| method | 0.85 | 1.05 | 1.25 | 1.45 |
|---|---|---|---|---|
| LP-Round | 2.934 | 3.055 | 3.054 | 1.708 |
| PC-MALNS [MC-CRIP] | 1.803 | 1.845 | 1.656 | 1.107 |
| HiGHS (30s) | 0.275 | 0.445 | – | 0.349 |
| PC-MALNS [BCRM-Greedy] | 1.796 | 1.851 | 1.647 | 1.125 |
| Greedy-Efficiency-Portfolio | 1.786 | 1.846 | 1.585 | 1.100 |
| Opt-Rollback | 1.700 | 1.817 | 1.802 | 1.213 |
| Opt-SeqLock | 1.703 | 1.792 | 1.814 | 1.217 |
| Static-Quota | 1.740 | 2.554 | 2.611 | 1.634 |
| HiGHS (1T, wall-matched) | 0.950 | 3.615 | 3.397 | 0.450 |
| HiGHS (4T, wall-matched) | 0.933 | 3.615 | 3.034 | 0.448 |
| HiGHS (1T, CPU-matched) | 0.322 | 0.474 | 0.466 | 0.413 |

**Tightness sweep: per η, Holm over the whole sweep** (difference = reference − method; negative favours the reference)

| Method | n | Ref mean | Method mean | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| eta=0.85: LP-Round | 10 | 1.803 | 2.934 | -1.131 [-1.325, -0.936] | [-1.304, -0.983] | 10/0/0 | 0.0020 | 0.0762 |
| eta=0.85: HiGHS (30s) | 10 | 1.803 | 0.275 | +1.528 [+1.448, +1.608] | [+1.468, +1.599] | 0/0/10 | 0.0020 | 0.0762 |
| eta=0.85: PC-MALNS [BCRM-Greedy] | 10 | 1.803 | 1.796 | +0.007 [-0.020, +0.034] | [-0.010, +0.033] | 5/1/4 | 0.8203 | 1.0000 |
| eta=0.85: Greedy-Efficiency-Portfolio | 10 | 1.803 | 1.786 | +0.017 [-0.040, +0.074] | [-0.027, +0.068] | 5/0/5 | 0.7695 | 1.0000 |
| eta=0.85: Opt-Rollback | 10 | 1.803 | 1.700 | +0.103 [+0.033, +0.172] | [+0.049, +0.164] | 1/0/9 | 0.0059 | 0.0938 |
| eta=0.85: Opt-SeqLock | 10 | 1.803 | 1.703 | +0.100 [+0.031, +0.169] | [+0.045, +0.160] | 2/0/8 | 0.0137 | 0.1914 |
| eta=0.85: Static-Quota | 10 | 1.803 | 1.740 | +0.063 [+0.004, +0.123] | [+0.014, +0.113] | 2/0/8 | 0.0371 | 0.4453 |
| eta=0.85: HiGHS (1T, wall-matched) | 10 | 1.803 | 0.950 | +0.853 [+0.046, +1.660] | [+0.103, +1.415] | 2/0/8 | 0.0840 | 0.9238 |
| eta=0.85: HiGHS (4T, wall-matched) | 10 | 1.803 | 0.933 | +0.870 [+0.059, +1.681] | [+0.111, +1.428] | 2/0/8 | 0.0840 | 0.9238 |
| eta=0.85: HiGHS (1T, CPU-matched) | 10 | 1.803 | 0.322 | +1.481 [+1.394, +1.568] | [+1.416, +1.558] | 0/0/10 | 0.0020 | 0.0762 |
| eta=1.05: LP-Round | 10 | 1.845 | 3.055 | -1.210 [-1.330, -1.091] | [-1.311, -1.116] | 10/0/0 | 0.0020 | 0.0762 |
| eta=1.05: HiGHS (30s) | 10 | 1.845 | 0.445 | +1.400 [+1.302, +1.497] | [+1.320, +1.478] | 0/0/10 | 0.0020 | 0.0762 |
| eta=1.05: PC-MALNS [BCRM-Greedy] | 10 | 1.845 | 1.851 | -0.006 [-0.030, +0.017] | [-0.026, +0.013] | 6/0/4 | 0.6250 | 1.0000 |
| eta=1.05: Greedy-Efficiency-Portfolio | 10 | 1.845 | 1.846 | -0.002 [-0.034, +0.031] | [-0.026, +0.028] | 6/0/4 | 0.6953 | 1.0000 |
| eta=1.05: Opt-Rollback | 10 | 1.845 | 1.817 | +0.028 [-0.029, +0.085] | [-0.016, +0.079] | 5/0/5 | 0.6250 | 1.0000 |
| eta=1.05: Opt-SeqLock | 10 | 1.845 | 1.792 | +0.053 [-0.010, +0.116] | [+0.001, +0.107] | 3/0/7 | 0.1055 | 0.9492 |
| eta=1.05: Static-Quota | 10 | 1.845 | 2.554 | -0.709 [-0.774, -0.645] | [-0.760, -0.655] | 10/0/0 | 0.0020 | 0.0762 |
| eta=1.05: HiGHS (1T, wall-matched) | 10 | 1.845 | 3.615 | -1.771 [-2.035, -1.506] | [-1.986, -1.554] | 10/0/0 | 0.0020 | 0.0762 |
| eta=1.05: HiGHS (4T, wall-matched) | 10 | 1.845 | 3.615 | -1.771 [-2.035, -1.506] | [-1.986, -1.554] | 10/0/0 | 0.0020 | 0.0762 |
| eta=1.05: HiGHS (1T, CPU-matched) | 10 | 1.845 | 0.474 | +1.371 [+1.283, +1.459] | [+1.299, +1.443] | 0/0/10 | 0.0020 | 0.0762 |
| eta=1.25: LP-Round | 10 | 1.656 | 3.054 | -1.397 [-1.527, -1.268] | [-1.499, -1.287] | 10/0/0 | 0.0020 | 0.0762 |
| eta=1.25: PC-MALNS [BCRM-Greedy] | 10 | 1.656 | 1.647 | +0.009 [-0.033, +0.051] | [-0.025, +0.044] | 6/0/4 | 0.8457 | 1.0000 |
| eta=1.25: Greedy-Efficiency-Portfolio | 10 | 1.656 | 1.585 | +0.071 [+0.026, +0.117] | [+0.033, +0.109] | 3/0/7 | 0.0273 | 0.3555 |
| eta=1.25: Opt-Rollback | 10 | 1.656 | 1.802 | -0.145 [-0.177, -0.113] | [-0.173, -0.120] | 10/0/0 | 0.0020 | 0.0762 |
| eta=1.25: Opt-SeqLock | 10 | 1.656 | 1.814 | -0.158 [-0.199, -0.118] | [-0.191, -0.125] | 10/0/0 | 0.0020 | 0.0762 |
| eta=1.25: Static-Quota | 10 | 1.656 | 2.611 | -0.955 [-1.016, -0.894] | [-1.008, -0.908] | 10/0/0 | 0.0020 | 0.0762 |
| eta=1.25: HiGHS (1T, wall-matched) | 10 | 1.656 | 3.397 | -1.741 [-2.023, -1.458] | [-1.973, -1.505] | 10/0/0 | 0.0020 | 0.0762 |
| eta=1.25: HiGHS (4T, wall-matched) | 10 | 1.656 | 3.034 | -1.378 [-2.120, -0.636] | [-1.850, -0.682] | 9/0/1 | 0.0059 | 0.0938 |
| eta=1.25: HiGHS (1T, CPU-matched) | 10 | 1.656 | 0.466 | +1.191 [+1.063, +1.319] | [+1.095, +1.299] | 0/0/10 | 0.0020 | 0.0762 |
| eta=1.45: LP-Round | 10 | 1.107 | 1.708 | -0.601 [-0.764, -0.439] | [-0.732, -0.466] | 10/0/0 | 0.0020 | 0.0762 |
| eta=1.45: HiGHS (30s) | 10 | 1.107 | 0.349 | +0.757 [+0.653, +0.861] | [+0.688, +0.858] | 0/0/10 | 0.0020 | 0.0762 |
| eta=1.45: PC-MALNS [BCRM-Greedy] | 10 | 1.107 | 1.125 | -0.019 [-0.050, +0.013] | [-0.044, +0.007] | 6/0/4 | 0.3223 | 1.0000 |
| eta=1.45: Greedy-Efficiency-Portfolio | 10 | 1.107 | 1.100 | +0.006 [-0.019, +0.031] | [-0.015, +0.027] | 5/0/5 | 0.6250 | 1.0000 |
| eta=1.45: Opt-Rollback | 10 | 1.107 | 1.213 | -0.106 [-0.145, -0.067] | [-0.138, -0.074] | 10/0/0 | 0.0020 | 0.0762 |
| eta=1.45: Opt-SeqLock | 10 | 1.107 | 1.217 | -0.110 [-0.160, -0.061] | [-0.151, -0.071] | 9/0/1 | 0.0039 | 0.0762 |
| eta=1.45: Static-Quota | 10 | 1.107 | 1.634 | -0.527 [-0.666, -0.388] | [-0.639, -0.410] | 10/0/0 | 0.0020 | 0.0762 |
| eta=1.45: HiGHS (1T, wall-matched) | 10 | 1.107 | 0.450 | +0.656 [+0.531, +0.782] | [+0.577, +0.776] | 0/0/10 | 0.0020 | 0.0762 |
| eta=1.45: HiGHS (4T, wall-matched) | 10 | 1.107 | 0.448 | +0.658 [+0.533, +0.784] | [+0.579, +0.778] | 0/0/10 | 0.0020 | 0.0762 |
| eta=1.45: HiGHS (1T, CPU-matched) | 10 | 1.107 | 0.413 | +0.693 [+0.572, +0.815] | [+0.613, +0.809] | 0/0/10 | 0.0020 | 0.0762 |

## Table E2 — price / quota ablation (Large, η = 1.25)


**PC-MALNS [MC-CRIP] (no prices, static quota) vs each price / quota variant** (difference = reference − method; negative favours the reference)

| Method | n | Ref mean | Method mean | Diff [t 95% CI] | Bootstrap 95% CI | W/T/L | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| PC-MALNS [MC-CRIP; prices=heuristic, quota=dynamic] | 10 | 1.656 | 1.629 | +0.028 [-0.011, +0.066] | [-0.004, +0.059] | 4/0/6 | 0.1934 | 1.0000 |
| PC-MALNS [MC-CRIP; prices=heuristic, quota=static] | 10 | 1.656 | 1.632 | +0.024 [-0.012, +0.060] | [-0.005, +0.053] | 4/0/6 | 0.1934 | 1.0000 |
| PC-MALNS [MC-CRIP; prices=mccrip_lp, quota=dynamic] | 10 | 1.656 | 1.627 | +0.029 [-0.009, +0.066] | [-0.002, +0.059] | 4/0/6 | 0.1934 | 1.0000 |
| PC-MALNS [MC-CRIP; prices=mccrip_lp, quota=static] | 10 | 1.656 | 1.635 | +0.021 [-0.017, +0.059] | [-0.011, +0.052] | 4/0/6 | 0.3223 | 1.0000 |
| PC-MALNS [MC-CRIP; prices=none, quota=demand] | 10 | 1.656 | 1.634 | +0.022 [-0.011, +0.055] | [-0.004, +0.050] | 4/0/6 | 0.1934 | 1.0000 |
| PC-MALNS [MC-CRIP; prices=none, quota=dynamic] | 10 | 1.656 | 1.662 | -0.006 [-0.018, +0.006] | [-0.015, +0.004] | 7/1/2 | 0.4258 | 1.0000 |

## Table E3 — multi-process wall-clock scaling (fixed epochs, one job at a time)


**Wall clock and speedup vs the serial in-process run**

| scale | mode | workers_W | wall_clock_s | speedup | identical |
|---|---|---|---|---|---|
| Large | pool | 1 | 3.165 | 0.987 | True |
| Large | pool | 2 | 1.827 | 1.722 | True |
| Large | pool | 4 | 1.320 | 2.367 | True |
| Large | pool | 8 | 1.131 | 2.763 | True |
| Large | serial | 1 | 3.125 | 1.000 | True |
| XXL | pool | 1 | 5.586 | 1.009 | True |
| XXL | pool | 2 | 3.617 | 1.562 | True |
| XXL | pool | 4 | 2.585 | 2.181 | True |
| XXL | pool | 8 | 1.975 | 2.862 | True |
| XXL | serial | 1 | 5.637 | 1.000 | True |

## Table E4 — parameter tuning (validation seeds 1..10, Medium)


**One-factor-at-a-time sensitivity (difference vs default; 30 paired runs)**

| factor | value | is_default | mean_gap | diff_vs_default | ci_lo | ci_hi | wins | losses | p_value | p_holm | adopt |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M | 1 | False | 1.938 | 0.087 | -0.001 | 0.174 | 10 | 20 | 0.028 | 0.083 | False |
| M | 2 | False | 1.910 | 0.059 | -0.021 | 0.139 | 10 | 20 | 0.158 | 0.158 | False |
| M | 5 | True | 1.851 | 0.000 | 0.000 | 0.000 | 0 | 0 | 1.000 | – | – |
| M | 10 | False | 1.799 | -0.052 | -0.125 | 0.021 | 19 | 11 | 0.035 | 0.083 | False |
| destroy | (0.08, 0.16) | False | 1.818 | -0.033 | -0.123 | 0.057 | 20 | 10 | 0.271 | 0.473 | False |
| destroy | (0.16, 0.3) | True | 1.851 | 0.000 | 0.000 | 0.000 | 0 | 0 | 1.000 | – | – |
| destroy | (0.3, 0.45) | False | 1.908 | 0.057 | -0.025 | 0.138 | 14 | 16 | 0.237 | 0.473 | False |
| noise | 0.0 | False | 1.846 | -0.005 | -0.094 | 0.084 | 16 | 14 | 0.808 | 1.000 | False |
| noise | 1.0 | False | 1.863 | 0.012 | -0.077 | 0.100 | 15 | 15 | 1.000 | 1.000 | False |
| noise | 2.0 | True | 1.851 | 0.000 | 0.000 | 0.000 | 0 | 0 | 1.000 | – | – |
| noise | 4.0 | False | 1.793 | -0.058 | -0.130 | 0.014 | 19 | 11 | 0.073 | 0.220 | False |
| rho0 | 0.0 | False | 1.874 | 0.023 | -0.044 | 0.090 | 10 | 16 | 0.635 | 1.000 | False |
| rho0 | 0.15 | False | 1.872 | 0.021 | -0.036 | 0.077 | 11 | 12 | 0.754 | 1.000 | False |
| rho0 | 0.35 | True | 1.851 | 0.000 | 0.000 | 0.000 | 0 | 0 | 1.000 | – | – |
| rho0 | 0.7 | False | 1.813 | -0.038 | -0.103 | 0.027 | 12 | 11 | 0.393 | 1.000 | False |
