"""
Worst-case per-epoch ratios of the barrier rules relative to MC-CRIP on explicit
portfolios, plus property tests of the counterfactual logger, the MC-CRIP time-limit
fallback and the unified Wilcoxon procedure.

Portfolio convention (src/commit_rules.py): delta_c (K, L+1), raw_dD (m, K, L+1),
s_t (m,), q_all (m, K) with sum_k q_k = s_t; level 0 = incumbent (0, 0).
"""

import numpy as np
import pytest
from scipy import stats as sps

from src.commit_rules import (apply_rule, opt_rollback, opt_seqlock, greedy_gain, greedy_efficiency,
                              static_quota, selection_cost, selection_feasible, counterfactual_costs)
from src.bcrm_solver import solve_mccrip_exact, solve_bcrm_greedy, LAST_SOLVE_INFO
from src.stats import paired_wilcoxon, holm, mean_ci


class IdentityOrder:
    """Arrival order pi = (0, 1, ..., K-1)."""
    def permutation(self, n):
        return np.arange(n)

    def choice(self, a):
        return a[0]


def portfolio(levels, s):
    """levels[k] = [(dc, dD-vector), ...] for l = 0..L."""
    K, nl = len(levels), len(levels[0])
    m = len(s)
    dc = np.zeros((K, nl))
    dD = np.zeros((m, K, nl))
    for k, lv in enumerate(levels):
        for l, (c, d) in enumerate(lv):
            dc[k, l] = c
            dD[:, k, l] = d
    s = np.asarray(s, dtype=float)
    q = np.tile(s[:, None] / K, (1, K))
    return dc, dD, s, q


def mccrip_gain(dc, dD, s, q):
    sel = apply_rule("MC-CRIP", dc, dD, s, q, IdentityOrder())
    assert selection_feasible(dD, s, sel)
    return -selection_cost(dc, sel)


def test_static_quota_ratio_unbounded():
    """Static-Quota gains 0 while MC-CRIP gains 10 (donor quota of agent 1 is lent)."""
    z = (0.0, [0.0])
    mv = (-10.0, [1.0])
    dc, dD, s, q = portfolio([[z, z, mv, mv], [z, z, z, z]], [1.0])
    assert mccrip_gain(dc, dD, s, q) == pytest.approx(10.0)
    assert -selection_cost(dc, static_quota(dc, dD, s)) == pytest.approx(0.0)


@pytest.mark.parametrize("K", [3, 6, 10])
def test_opt_rollback_ratio_k_minus_1(K):
    """K equal moves, slack for K - 1: Opt-Rollback commits one, MC-CRIP K - 1."""
    z = (0.0, [0.0])
    mv = (-1.0, [1.0])
    dc, dD, s, q = portfolio([[z, z, mv, mv]] * K, [K - 1.0])
    _, expected = opt_rollback(dc, dD, s, np.random.default_rng(0), expected=True)
    assert mccrip_gain(dc, dD, s, q) / -expected == pytest.approx(K - 1.0)


@pytest.mark.parametrize("K", [4, 8, 16])
def test_opt_seqlock_ratio_omega_k(K):
    """Agent 0 arrives first with a hub-hogging cheapest level: ratio K / (1 + eps)."""
    eps = 0.01
    z = (0.0, [0.0])
    small = (-1.0, [1.0])
    hog = (-(1.0 + eps), [float(K)])
    levels = [[z, small, small, hog]] + [[z, small, small, small]] * (K - 1)
    dc, dD, s, q = portfolio(levels, [float(K)])
    seq = -selection_cost(dc, opt_seqlock(dc, dD, s, IdentityOrder()))
    assert seq == pytest.approx(1.0 + eps)
    assert mccrip_gain(dc, dD, s, q) / seq == pytest.approx(K / (1.0 + eps))


def test_greedy_gain_ratio_two_minus_eps():
    """One hub: a 2-unit move of gain 1 + eps blocks two 1-unit moves of gain 1."""
    eps = 0.01
    z = (0.0, [0.0])
    big = (-(1.0 + eps), [2.0])
    one = (-1.0, [1.0])
    dc, dD, s, q = portfolio([[z, z, big, big], [z, z, one, one], [z, z, one, one]], [2.0])
    g = -selection_cost(dc, greedy_gain(dc, dD, s))
    assert g == pytest.approx(1.0 + eps)
    assert mccrip_gain(dc, dD, s, q) / g == pytest.approx(2.0 / (1.0 + eps))


@pytest.mark.parametrize("m", [3, 5, 8])
def test_greedy_gain_ratio_omega_m(m):
    """m hubs: a move using every hub (gain 1 + eps) blocks m single-hub moves of gain 1."""
    eps = 0.01
    zv = [0.0] * m
    z = (0.0, zv)
    hog = (-(1.0 + eps), [1.0] * m)
    levels = [[z, z, hog, hog]]
    for j in range(m):
        e = [0.0] * m
        e[j] = 1.0
        levels.append([z, z, (-1.0, e), (-1.0, e)])
    dc, dD, s, q = portfolio(levels, [1.0] * m)
    g = -selection_cost(dc, greedy_gain(dc, dD, s))
    assert g == pytest.approx(1.0 + eps)
    assert mccrip_gain(dc, dD, s, q) / g == pytest.approx(m / (1.0 + eps))


def random_portfolio(rng, K=8, m=4):
    s = rng.uniform(1.0, 4.0, size=m)
    q = np.tile(s[:, None] / K, (1, K))
    dc = np.zeros((K, 4))
    dD = np.zeros((m, K, 4))
    for k in range(K):
        # level 0: donor (releases slack, no extra cost) or incumbent
        if rng.random() < 0.3:
            dD[:, k, 0] = -rng.uniform(0.0, 0.5, size=m)
        # level 1: quota-safe
        dD[:, k, 1] = rng.uniform(0.0, 1.0, size=m) * q[:, k]
        dc[k, 1] = -rng.uniform(0.0, 2.0)
        for l in (2, 3):
            dD[:, k, l] = rng.uniform(0.0, 2.0, size=m) * (rng.random(m) < 0.6)
            dc[k, l] = dc[k, 1] - rng.uniform(0.0, 3.0)
    return dc, dD, s, q


def test_counterfactual_mccrip_is_minimal_and_all_rules_feasible():
    rng = np.random.default_rng(7)
    for _ in range(60):
        dc, dD, s, q = random_portfolio(rng)
        cf = counterfactual_costs(dc, dD, s, q, np.zeros(len(s)), 0.0, np.random.default_rng(1))
        for rule, v in cf.items():
            assert cf["MC-CRIP"] <= v + 1e-9, rule
        for rule in ("BCRM-Greedy", "Greedy-Gain", "Greedy-Efficiency", "Static-Quota", "Opt-SeqLock",
                     "Opt-Rollback", "MC-CRIP"):
            sel = apply_rule(rule, dc, dD, s, q, np.random.default_rng(2))
            assert selection_feasible(dD, s, sel), rule


def test_mccrip_time_limit_fallback_never_worse_than_greedy_or_quota_safe():
    rng = np.random.default_rng(3)
    for _ in range(5):
        dc, dD, s, q = random_portfolio(rng, K=14, m=6)
        dslack = dD - q[:, :, None]
        sel, _ = solve_mccrip_exact(dc, dslack, time_limit_s=1e-6, max_enum_states=1)
        assert LAST_SOLVE_INFO["used_highs"]
        assert np.all(np.sum(dslack[:, np.arange(14), sel], axis=1) <= 1e-6)
        g, _ = solve_bcrm_greedy(dc, dslack, np.zeros(len(s)), 0.0)
        cost = float(np.sum(dc[np.arange(14), sel]))
        assert cost <= float(np.sum(dc[np.arange(14), g])) + 1e-9
        assert cost <= float(np.sum(dc[:, 1])) + 1e-9


def test_wilcoxon_matches_scipy_exact_without_ties_and_is_pattern_consistent():
    rng = np.random.default_rng(11)
    a, b = rng.normal(size=25), rng.normal(size=25)
    ours = paired_wilcoxon(a, b)["p_value"]
    ref = sps.wilcoxon(a - b, zero_method="wilcox", method="exact").pvalue
    assert ours == pytest.approx(ref, rel=1e-9)
    # 20 wins / 0 losses gives the same p-value whatever the magnitudes or zero count
    p1 = paired_wilcoxon(-rng.uniform(0.1, 1, 20), np.zeros(20))["p_value"]
    p2 = paired_wilcoxon(np.r_[-rng.uniform(0.1, 9, 20), np.zeros(5)], np.zeros(25))["p_value"]
    assert p1 == pytest.approx(2 * 0.5 ** 20) and p2 == pytest.approx(p1)


def test_holm_and_ci():
    adj = holm([0.01, 0.04, 0.03])
    assert np.allclose(adj, [0.03, 0.06, 0.06])
    ci = mean_ci([1.0, 2.0, 3.0, 4.0], [0.0, 0.0, 0.0, 0.0])
    assert ci["t_lo"] < 2.5 < ci["t_hi"] and ci["boot_lo"] <= 2.5 <= ci["boot_hi"]


@pytest.mark.parametrize("C", [10.0, 100.0, 1000.0])
def test_greedy_efficiency_ratio_unbounded(C):
    """One hub with slack C: a tiny move of high efficiency (gain 2 delta, usage delta)
    blocks a large move (gain C, usage C). Greedy-Efficiency gains 2 delta, MC-CRIP C."""
    delta = 1.0
    z = (0.0, [0.0])
    small = (-2.0 * delta, [delta])
    big = (-C, [C])
    dc, dD, s, q = portfolio([[z, z, small, small], [z, z, big, big]], [C])
    g = -selection_cost(dc, greedy_efficiency(dc, dD, s))
    assert g == pytest.approx(2.0 * delta)
    assert mccrip_gain(dc, dD, s, q) / g == pytest.approx(C / (2.0 * delta))
