"""
Barrier commit rules applied to one and the same worker portfolio.

Inputs at epoch t (all rules):
    delta_c   (K, L+1)   cost change c_k^T (y_k^{(t,l)} - x_k^{(t)})
    raw_dD    (m, K, L+1) hub usage change D_k (y_k^{(t,l)} - x_k^{(t)})
    s_t       (m,)       residual hub slack s^{(t)} = d - sum_k D_k x_k^{(t)}
    q_all     (m, K)     slack quotas q_k^{(t)} with sum_k q_k^{(t)} = s^{(t)}

Every rule returns a selection sel (K,) with sel[k] = l (commit level l of worker k)
or sel[k] = KEEP (= -1: keep the incumbent x_k^{(t)}). Every returned selection
satisfies sum_k raw_dD[:, k, sel_k] <= s_t (hub feasibility), checked by
``selection_feasible``.

Rules (mechanism names used in all outputs):
    MC-CRIP            exact multiple-choice IP (src/bcrm_solver.solve_mccrip_exact)
    BCRM-Greedy        quota-safe start + efficiency-sorted upgrades (solve_bcrm_greedy)
    Greedy-Gain        all workers at l = 0; upgrades (k, l) sorted by cost reduction,
                       committed while the hub slack holds (at most one per worker)
    Greedy-Efficiency  as Greedy-Gain, sorted by gain per unit of extra hub usage
    Opt-Rollback       each worker proposes its cheapest level; if the batch does not
                       fit, it is rolled back and one random improving worker commits
                       (PALNS-style)
    Opt-SeqLock        cheapest levels checked in a random arrival order and committed
                       while they fit (DROP-LNS-style)
    Static-Quota       every worker commits its quota-safe level l = 1
"""

from typing import Dict, Optional
import numpy as np

from src.feasibility import TOL
from src.bcrm_solver import solve_mccrip_exact, solve_bcrm_greedy

KEEP = -1
RULES = ("MC-CRIP", "BCRM-Greedy", "Greedy-Gain", "Greedy-Efficiency",
         "Opt-Rollback", "Opt-SeqLock", "Static-Quota")


def _take(arr_kl: np.ndarray, sel: np.ndarray) -> np.ndarray:
    """Values of a (K, L+1) array at sel, 0 for KEEP."""
    K = arr_kl.shape[0]
    out = np.zeros(K)
    m = sel >= 0
    out[m] = arr_kl[np.arange(K)[m], sel[m]]
    return out


def selection_cost(delta_c: np.ndarray, sel: np.ndarray) -> float:
    return float(np.sum(_take(delta_c, sel)))


def selection_usage(raw_dD: np.ndarray, sel: np.ndarray) -> np.ndarray:
    m, K, _ = raw_dD.shape
    out = np.zeros(m)
    for k in range(K):
        if sel[k] >= 0:
            out += raw_dD[:, k, sel[k]]
    return out


def selection_feasible(raw_dD: np.ndarray, s_t: np.ndarray, sel: np.ndarray) -> bool:
    return bool(np.all(selection_usage(raw_dD, sel) <= s_t + TOL))


def _greedy_from_level0(delta_c, raw_dD, s_t, key):
    """All workers start at l = 0 (incumbent or dominating donor, D-change <= 0);
    upgrades (k, l) with lower cost than l = 0 are sorted by ``key`` (descending)
    and committed while the remaining hub slack allows (one upgrade per worker)."""
    m, K, nl = raw_dD.shape
    sel = np.zeros(K, dtype=np.int64)
    rem = s_t - selection_usage(raw_dD, sel)
    cands = []
    for k in range(K):
        for l in range(1, nl):
            gain = delta_c[k, 0] - delta_c[k, l]
            if gain > TOL:
                extra = raw_dD[:, k, l] - raw_dD[:, k, 0]
                cands.append((key(gain, extra), k, l))
    cands.sort(key=lambda c: (-c[0], c[1], c[2]))
    for _, k, l in cands:
        if sel[k] != 0:
            continue
        extra = raw_dD[:, k, l] - raw_dD[:, k, 0]
        if np.all(extra <= rem + TOL):
            sel[k] = l
            rem = rem - extra
    return sel


def greedy_gain(delta_c, raw_dD, s_t):
    return _greedy_from_level0(delta_c, raw_dD, s_t, key=lambda g, e: g)


def greedy_efficiency(delta_c, raw_dD, s_t):
    return _greedy_from_level0(
        delta_c, raw_dD, s_t,
        key=lambda g, e: g / (float(np.sum(np.maximum(0.0, e))) + 1e-6))


def _cheapest(delta_c):
    sel = np.argmin(delta_c, axis=1).astype(np.int64)
    best = delta_c[np.arange(delta_c.shape[0]), sel]
    sel[best >= -TOL] = KEEP
    return sel


def opt_rollback(delta_c, raw_dD, s_t, rng: np.random.Generator, expected: bool = False):
    """PALNS-style rule. With expected=True returns the expected cost change over the
    uniformly random choice of the single committing worker (for counterfactuals)."""
    sel = _cheapest(delta_c)
    if selection_feasible(raw_dD, s_t, sel):
        return (sel, selection_cost(delta_c, sel)) if expected else sel
    impr = np.where(sel >= 0)[0]
    one = np.full_like(sel, KEEP)
    if expected:
        vals = []
        for k in impr:
            o = one.copy(); o[k] = sel[k]
            vals.append(selection_cost(delta_c, o) if selection_feasible(raw_dD, s_t, o) else 0.0)
        return one, float(np.mean(vals)) if vals else 0.0
    if len(impr):
        k = int(rng.choice(impr))
        one[k] = sel[k]
        if not selection_feasible(raw_dD, s_t, one):
            one[k] = KEEP
    return one


def opt_seqlock(delta_c, raw_dD, s_t, rng: np.random.Generator):
    """DROP-LNS-style rule: cheapest levels in a random arrival order, committed while they fit."""
    cheap = _cheapest(delta_c)
    sel = np.full_like(cheap, KEEP)
    rem = s_t.copy()
    for k in rng.permutation(len(cheap)):
        if cheap[k] >= 0 and np.all(raw_dD[:, k, cheap[k]] <= rem + TOL):
            sel[k] = cheap[k]
            rem = rem - raw_dD[:, k, cheap[k]]
    return sel


def static_quota(delta_c, raw_dD, s_t):
    return np.ones(delta_c.shape[0], dtype=np.int64)


def apply_rule(rule: str, delta_c, raw_dD, s_t, q_all, rng, lambda_t=None, rho_t=0.0):
    """Selection of ``rule`` on this portfolio (KEEP = -1 allowed)."""
    if rule == "MC-CRIP":
        sel, _ = solve_mccrip_exact(delta_c, raw_dD - q_all[:, :, None])
        return sel
    if rule == "BCRM-Greedy":
        lam = np.zeros(raw_dD.shape[0]) if lambda_t is None else lambda_t
        sel, _ = solve_bcrm_greedy(delta_c, raw_dD - q_all[:, :, None], lam, rho_t)
        return sel
    if rule == "Greedy-Gain":
        return greedy_gain(delta_c, raw_dD, s_t)
    if rule == "Greedy-Efficiency":
        return greedy_efficiency(delta_c, raw_dD, s_t)
    if rule == "Opt-Rollback":
        return opt_rollback(delta_c, raw_dD, s_t, rng)
    if rule == "Opt-SeqLock":
        return opt_seqlock(delta_c, raw_dD, s_t, rng)
    if rule == "Static-Quota":
        return static_quota(delta_c, raw_dD, s_t)
    raise ValueError(rule)


def counterfactual_costs(delta_c, raw_dD, s_t, q_all, lambda_t, rho_t, rng,
                         n_perm: int = 20) -> Dict[str, float]:
    """Single-epoch cost change Delta C^{(t)} of every rule on this identical portfolio.
    Random rules are evaluated by their expectation (Opt-Rollback, exact) or by the
    mean over n_perm arrival orders (Opt-SeqLock). Uses its own generator, so the
    run trajectory is unchanged."""
    out = {}
    for rule in ("MC-CRIP", "BCRM-Greedy", "Greedy-Gain", "Greedy-Efficiency", "Static-Quota"):
        sel = apply_rule(rule, delta_c, raw_dD, s_t, q_all, rng, lambda_t, rho_t)
        assert selection_feasible(raw_dD, s_t, sel), rule
        out[rule] = selection_cost(delta_c, sel)
    out["Opt-Rollback"] = opt_rollback(delta_c, raw_dD, s_t, rng, expected=True)[1]
    vals = []
    for _ in range(n_perm):
        sel = opt_seqlock(delta_c, raw_dD, s_t, rng)
        vals.append(selection_cost(delta_c, sel))
    out["Opt-SeqLock"] = float(np.mean(vals))
    return out
