"""
Quota-Surplus Greedy Upgrade (BCRM-Greedy) and Exact Multi-Choice
Conflict-Resolution Integer Programming (MC-CRIP) Solver via HiGHS.

Implements Section 5.3 of the mathematical specification:
1. Zero-Conflict Fast Path: l_k^* = argmin_l Delta c_{k,l} for every k, accepted only
   if sum_k delta_{r,k,l_k^*} <= 0 holds for ALL r in {1,...,m} (O(K(L+m)) time).
2. Exact Multi-Choice Conflict-Resolution IP (MC-CRIP) via vectorized exact
   enumeration over all agents and levels l in {0, ..., L} (after dominance pruning)
   when at most 4,096 level combinations remain, and scipy.optimize.milp (HiGHS,
   mip_rel_gap = 0) otherwise.
3. Rollback-free single-pass Quota-Surplus Greedy Upgrade (BCRM-Greedy) with
   Shadow Efficiency Ratio sorting.
"""

import time
from typing import Tuple, List
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from src.feasibility import TOL

MAX_ENUM_STATES = 4096
# Status of the last MC-CRIP solve: False if the HiGHS path stopped without a proof of
# optimality (time limit); the returned selection is then the better of the HiGHS
# incumbent and the all-quota-safe selection z_{k,1} = 1.
LAST_SOLVE_INFO = {"proven_optimal": True, "used_highs": False, "fallback_choice": ""}


def solve_mccrip_exact(
    delta_c: np.ndarray,
    delta_slack: np.ndarray,
    time_limit_s: float = 2.0,
    max_enum_states: int = MAX_ENUM_STATES,
) -> Tuple[np.ndarray, float]:
    """
    Solve the Exact Multi-Choice Conflict-Resolution IP (MC-CRIP) in Equations (10)-(13):
        min_{z} sum_{k=0}^{K-1} sum_{l=0}^{L} delta_c[k, l] * z_{k, l}
        s.t.    sum_{k=0}^{K-1} sum_{l=0}^{L} delta_slack[r, k, l] * z_{k, l} <= 0,  forall r in {1..m}
                sum_{l=0}^{L} z_{k, l} = 1,                                         forall k in K
                z_{k, l} in {0, 1}.

    Args:
        delta_c: Array of shape (K, L+1) with net primal cost delta Delta c_{k,l}^{(t)}.
        delta_slack: Array of shape (m_global, K, L+1) with net quota-relative slack
                     consumption delta_{r,k,l}^{(t)} = D_{r,k}(y_k^{(t,l)} - x_k^{(t)}) - q_{r,k}^{(t)}.

    Returns:
        selected_levels: Integer array of shape (K,) with optimal portfolio indices l_k^* in {0, ..., L}.
        solve_time_ms: Wall-clock runtime in milliseconds.
    """
    t0 = time.perf_counter()
    m_global, K, num_levels = delta_slack.shape
    L = num_levels - 1
    LAST_SOLVE_INFO["proven_optimal"] = True
    LAST_SOLVE_INFO["used_highs"] = False
    LAST_SOLVE_INFO["fallback_choice"] = ""

    # Zero-Conflict Fast Path: per-agent argmin over l in {0..L}, accepted only if
    # the selection satisfies the coupling rows for ALL m resources; otherwise the
    # full MC-CRIP below is solved.
    best_l = np.argmin(delta_c, axis=1).astype(np.int64)
    best_sum = np.sum(delta_slack[:, np.arange(K), best_l], axis=1)
    if np.all(best_sum <= TOL):
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return best_l, elapsed_ms

    # Exact solve over ALL agents and ALL levels l in {0, ..., L}; level l = 0 keeps
    # the incumbent and therefore acts as a pure slack-donor move.
    # (i) Dominance pruning: level a dominates level b of the same agent if it is
    #     no more expensive and consumes no more slack on every row.
    options: List[np.ndarray] = []
    for k in range(K):
        keep = []
        for b_l in range(num_levels):
            dominated = False
            for a_l in range(num_levels):
                if a_l == b_l:
                    continue
                le = (delta_c[k, a_l] <= delta_c[k, b_l] + 1e-12) and np.all(
                    delta_slack[:, k, a_l] <= delta_slack[:, k, b_l] + 1e-12
                )
                if le:
                    strict = (delta_c[k, a_l] < delta_c[k, b_l] - 1e-12) or np.any(
                        delta_slack[:, k, a_l] < delta_slack[:, k, b_l] - 1e-12
                    )
                    if strict or a_l < b_l:
                        dominated = True
                        break
            if not dominated:
                keep.append(b_l)
        options.append(np.array(keep, dtype=np.int64))

    free_k = np.array([k for k in range(K) if len(options[k]) > 1], dtype=np.int64)
    fixed_levels = np.array([options[k][0] for k in range(K)], dtype=np.int64)
    fixed_mask = np.ones(K, dtype=bool)
    fixed_mask[free_k] = False
    fixed_slack = np.sum(delta_slack[:, np.where(fixed_mask)[0], fixed_levels[fixed_mask]], axis=1)

    selected_levels = np.ones(K, dtype=np.int64)
    n_states = int(np.prod([len(options[k]) for k in free_k])) if len(free_k) else 1

    # (ii) Exact vectorized enumeration when the number of level combinations of the
    #      active agents is at most MAX_ENUM_STATES (4^6 = 4,096)
    if n_states <= max_enum_states:
        sel = fixed_levels.copy()
        if len(free_k) == 0:
            if np.all(fixed_slack <= TOL):
                selected_levels = sel
        else:
            grids = np.meshgrid(*[options[k] for k in free_k], indexing="ij")
            combos = np.stack([g.reshape(-1) for g in grids], axis=1)  # (n_states, K_act)
            costs = np.sum(delta_c[free_k[None, :], combos], axis=1)
            slacks = fixed_slack[:, None] + np.sum(
                delta_slack[:, free_k[None, :], combos], axis=2
            )  # (m, n_states)
            feas = np.all(slacks <= TOL, axis=0)
            valid = np.where(feas, costs, np.inf)
            j = int(np.argmin(valid))
            if np.isfinite(valid[j]):
                sel[free_k] = combos[j]
                selected_levels = sel
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return selected_levels, elapsed_ms

    # (iii) Larger active sets: HiGHS branch-and-bound with mip_rel_gap = 0
    K_act = len(free_k)
    n_vars = K_act * num_levels
    c_obj = delta_c[free_k, :].reshape(-1)
    A_cap = delta_slack[:, free_k, :].reshape(m_global, n_vars)
    A_choice = np.zeros((K_act, n_vars), dtype=np.float64)
    ub_var = np.zeros(n_vars)
    for idx_k, k in enumerate(free_k):
        A_choice[idx_k, idx_k * num_levels:(idx_k + 1) * num_levels] = 1.0
        ub_var[idx_k * num_levels + options[k]] = 1.0
    res = milp(
        c=c_obj,
        integrality=np.ones(n_vars),
        bounds=Bounds(np.zeros(n_vars), ub_var),
        constraints=[
            LinearConstraint(A_cap, -np.inf, -fixed_slack),
            LinearConstraint(A_choice, 1.0, 1.0),
        ],
        options={"time_limit": float(time_limit_s), "mip_rel_gap": 0.0},
    )
    LAST_SOLVE_INFO["used_highs"] = True
    LAST_SOLVE_INFO["proven_optimal"] = bool(res.status == 0)

    def feasible(sel):
        return bool(np.all(np.sum(delta_slack[:, np.arange(K), sel], axis=1) <= TOL))

    def cost(sel):
        return float(np.sum(delta_c[np.arange(K), sel]))

    cands = []
    if res.x is not None:
        sel = fixed_levels.copy()
        sel[free_k] = np.argmax(res.x.reshape(K_act, num_levels), axis=1).astype(np.int64)
        if feasible(sel):
            cands.append(("highs", sel))
    if LAST_SOLVE_INFO["proven_optimal"] and cands:
        selected_levels = cands[0][1]
    else:
        # Unified time-limit fallback: the best feasible selection among the HiGHS
        # incumbent, BCRM-Greedy (no prices) and the all-quota-safe selection z_{k,1} = 1.
        greedy_sel, _ = solve_bcrm_greedy(delta_c, delta_slack, np.zeros(m_global), 0.0)
        if feasible(greedy_sel):
            cands.append(("bcrm_greedy", greedy_sel))
        qs = np.ones(K, dtype=np.int64)
        if feasible(qs):
            cands.append(("quota_safe", qs))
        if cands:
            name, selected_levels = min(cands, key=lambda c: (cost(c[1]), c[0] != "highs"))
            LAST_SOLVE_INFO["fallback_choice"] = name

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return selected_levels, elapsed_ms


def solve_bcrm_greedy(
    delta_c: np.ndarray,
    delta_slack: np.ndarray,
    dual_prices: np.ndarray,
    rho_t: float,
) -> Tuple[np.ndarray, float]:
    """
    Quota-Surplus Greedy Upgrade (BCRM-Greedy), a rollback-free single pass,
    as specified in Section 5.3 (Equation 14):

    1. Zero-Conflict Fast Path: return l_k^* = argmin_l Delta c_{k,l} if that selection
       satisfies all m coupling rows.
    2. Initialize every agent at its quota-safe candidate l_k^* = 1, yielding
       total available global slack surplus:
           S_pool = -sum_{k=1}^K delta_{k,1}^{(t)} >= 0.
    3. For every borrower candidate (u, l) with l in {2, ..., L} that strictly
       improves upon agent u's quota-safe move (Delta c_{u,l}^{(t)} < Delta c_{u,1}^{(t)}),
       compute incremental slack requirement:
           beta_{u,l}^- = D_u(y_u^{(t,l)} - y_u^{(t,1)}) = delta_{u,l}^{(t)} - delta_{u,1}^{(t)}
       and the Shadow Efficiency Ratio:
           eta_{u,l} = (Delta c_{u,1}^{(t)} - Delta c_{u,l}^{(t)}) /
                       ( (lambda^{(t)})^T [beta_{u,l}^-]_+ + rho_t ||[beta_{u,l}^-]_+||_2^2 + 1e-6 ).
    4. Sort candidate upgrades (u, l) in descending order of eta_{u,l} and greedily
       upgrade l_u^* <- l (at most one upgrade per agent) whenever
       beta_{u,l}^- <= S_pool, then set S_pool <- S_pool - beta_{u,l}^-.
    The scan is a single pass (no swap refinement and no l = 0 donor moves).
    """
    t0 = time.perf_counter()
    m_global, K, num_levels = delta_slack.shape
    L = num_levels - 1

    # Zero-Conflict Fast Path (same rule as MC-CRIP: all m rows must hold)
    best_l = np.argmin(delta_c, axis=1).astype(np.int64)
    if np.all(np.sum(delta_slack[:, np.arange(K), best_l], axis=1) <= TOL):
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return best_l, elapsed_ms

    # Initialize at quota-safe candidate l_k^* = 1
    selected_levels = np.ones(K, dtype=np.int64)
    S_pool = -np.sum(delta_slack[:, :, 1], axis=1).copy()

    # Build candidate list (eta_{u,l}, u, l)
    candidates: List[Tuple[float, int, int]] = []
    for u in range(K):
        dc_1 = delta_c[u, 1]
        for ell in range(2, num_levels):
            dc_ell = delta_c[u, ell]
            if dc_ell < dc_1 - 1e-9:
                beta_minus = delta_slack[:, u, ell] - delta_slack[:, u, 1]
                beta_pos = np.maximum(0.0, beta_minus)
                denom = (
                    float(np.dot(dual_prices, beta_pos))
                    + rho_t * float(np.dot(beta_pos, beta_pos))
                    + 1e-6
                )
                eta = float((dc_1 - dc_ell) / denom)
                candidates.append((eta, u, ell))

    if not candidates:
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return selected_levels, elapsed_ms

    candidates.sort(key=lambda item: item[0], reverse=True)

    # Greedy upgrade pass: at most one upgrade l >= 2 per agent u; S_pool is
    # decremented by beta_{u,l}^- after every committed upgrade.
    for _, u, ell in candidates:
        if selected_levels[u] != 1:
            continue
        beta_minus = delta_slack[:, u, ell] - delta_slack[:, u, 1]
        if np.all(beta_minus <= S_pool + TOL):
            selected_levels[u] = ell
            S_pool -= beta_minus

    # Final safeguard: the selection must satisfy all m coupling rows
    if np.any(np.sum(delta_slack[:, np.arange(K), selected_levels], axis=1) > TOL):
        selected_levels = np.ones(K, dtype=np.int64)

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return selected_levels, elapsed_ms
