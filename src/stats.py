"""
Single statistics module used by every analysis script.

paired_wilcoxon   two-sided Wilcoxon signed-rank test with ONE deterministic procedure
                  for every comparison: zero differences are dropped (zero_method =
                  "wilcox"), tied |differences| receive mid-ranks, and the p-value is
                  computed from the EXACT conditional null distribution of T+ (all 2^n
                  sign patterns, by dynamic programming over doubled integer ranks).
                  Without ties this equals scipy.stats.wilcoxon(method="exact"); there
                  is no switch to a normal approximation, so equal win/loss patterns
                  always give equal p-values.
holm              Holm-Bonferroni step-down adjustment.
mean_ci           paired mean difference with a Student-t 95% CI and a percentile
                  bootstrap 95% CI (10,000 resamples, fixed seed).
"""

from typing import Dict, Sequence

import numpy as np
from scipy import stats as sps


def _exact_signed_rank_p(d: np.ndarray) -> float:
    d = d[d != 0]
    n = len(d)
    if n == 0:
        return 1.0
    r2 = np.rint(2 * sps.rankdata(np.abs(d))).astype(np.int64)   # doubled mid-ranks
    t_plus = int(np.sum(r2[d > 0]))
    total = int(np.sum(r2))
    dist = np.zeros(total + 1)
    dist[0] = 1.0
    for r in r2:
        shifted = np.zeros_like(dist)
        shifted[r:] = dist[:-r] if r > 0 else dist
        dist = 0.5 * (dist + shifted)
    cdf_lo = float(np.sum(dist[: t_plus + 1]))
    cdf_hi = float(np.sum(dist[t_plus:]))
    return min(1.0, 2.0 * min(cdf_lo, cdf_hi))


def paired_wilcoxon(a: Sequence[float], b: Sequence[float]) -> Dict[str, float]:
    """Compare paired samples a (method) and b (baseline); lower is better.
    Returns wins / ties / losses of a, the exact two-sided p-value and n_nonzero."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    d = np.round(a - b, 10)
    return dict(wins=int(np.sum(d < 0)), ties=int(np.sum(d == 0)), losses=int(np.sum(d > 0)),
                n_nonzero=int(np.sum(d != 0)), p_value=_exact_signed_rank_p(d))


def holm(pvals: Sequence[float]) -> np.ndarray:
    p = np.asarray(pvals, dtype=float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    running = 0.0
    m = len(p)
    for i, j in enumerate(order):
        running = max(running, (m - i) * p[j])
        adj[j] = min(1.0, running)
    return adj


def mean_ci(a: Sequence[float], b: Sequence[float], n_boot: int = 10000, seed: int = 12345) -> Dict[str, float]:
    """Mean of a - b with paired-t and bootstrap percentile 95% confidence intervals."""
    d = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    n = len(d)
    mean = float(np.mean(d))
    if n < 2:
        return dict(mean=mean, t_lo=float("nan"), t_hi=float("nan"), boot_lo=float("nan"), boot_hi=float("nan"))
    se = float(np.std(d, ddof=1) / np.sqrt(n))
    h = float(sps.t.ppf(0.975, n - 1) * se)
    rng = np.random.default_rng(seed)
    boots = d[rng.integers(0, n, size=(n_boot, n))].mean(axis=1)
    return dict(mean=mean, t_lo=mean - h, t_hi=mean + h,
                boot_lo=float(np.percentile(boots, 2.5)), boot_hi=float(np.percentile(boots, 97.5)))
