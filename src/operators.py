"""
Vectorized Destroy and Regret-2 Repair Operators for Concurrent Multi-Agent LNS.

Implements:
1. Local Destroy Operator D_k balancing slack-releasing removals (coupled requests
   with p > 0) and high-saving upgrade candidates across epochs.
2. Vectorized Hard-Constrained Regret-2 Repair Operator R_k (used by every LNS
   method; levels l = 1 and l = 3 of the portfolio).
3. Vectorized Proximal Augmented Lagrangian Regret-2 Repair Operator (used by PC-MALNS
   Candidates l in {2, ..., L} for aggressive slack-borrowing repairs).
"""

from typing import Tuple, Optional
import numpy as np
from src.instance_generator import CoupledRoutingInstance
from src.feasibility import (
    compute_agent_global_usage,
    compute_agent_local_usage,
    TOL,
)


# ---------------------------------------------------------------------------
# Shared worker configuration. Every LNS method uses exactly these settings, so that comparisons isolate
# the synchronization / coordination rule rather than operator tuning.
# ---------------------------------------------------------------------------
DESTROY_MIN_RATIO = 0.16
DESTROY_MAX_RATIO = 0.30
REPAIR_NOISE = 2.0
REPAIR_NOISE_ALT = 1.35 * REPAIR_NOISE
MAX_NET_UPGRADES = 3  # per-epoch net upgrade batch per worker (identical for every method)


# Tie-breaking weight of the non-negative prices in the quota-safe repair (l = 1):
# eff_c = c + TIE_BREAK_EPS * lambda^T D. Small relative to the repair noise, so the
# l = 1 repair minimizes true primal cost and only prefers less congested hubs when
# primal savings are similar.
TIE_BREAK_EPS = 0.05
# Release moves of the donor repair (l = 2) before one compensating upgrade.
DONOR_RELEASES = 2


def base_repair_best_of_two(
    instance: CoupledRoutingInstance,
    k: int,
    incumbent_k: np.ndarray,
    partial_k: np.ndarray,
    destroyed_indices: np.ndarray,
    max_global_delta: np.ndarray,
    rng: np.random.Generator,
    dual_prices: Optional[np.ndarray] = None,
    max_net_upgrades: Optional[int] = MAX_NET_UPGRADES,
) -> np.ndarray:
    """
    Shared worker repair used by every method: two noisy Regret-2 repairs under
    the hard global-increment cap ``max_global_delta`` (identical noise levels for
    all methods); the cheaper of the two (by raw cost c_k) is returned.
    """
    ys = []
    for noise in (REPAIR_NOISE, REPAIR_NOISE_ALT):
        ys.append(
            regret2_repair_hard_quota(
                instance=instance,
                k=k,
                incumbent_k=incumbent_k,
                partial_k=partial_k,
                destroyed_indices=destroyed_indices,
                max_global_delta=max_global_delta,
                dual_prices=dual_prices,
                rng=rng,
                noise_scale=noise,
                max_net_upgrades=max_net_upgrades,
            )
        )
    i_idx = np.arange(instance.N_per_agent)
    costs = [float(np.sum(instance.c[k, i_idx, y])) for y in ys]
    return ys[int(np.argmin(costs))]


def destroy_operator(
    instance: CoupledRoutingInstance,
    k: int,
    patterns_k: np.ndarray,
    rng: np.random.Generator,
    min_ratio: float = 0.20,
    max_ratio: float = 0.35,
    dual_prices: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Local destroy operator Omega_k removing min_ratio-max_ratio of the requests of agent k.
    About 45% of the removals are currently coupled requests (p > 0); with global
    prices lambda > 0 they are chosen by the dual-to-saving ratio, otherwise by local
    cost alone. The remaining removals target high-cost / suboptimal requests.

    Returns:
        partial_patterns_k: Copy of patterns_k with destroyed requests reset to p = 0.
        destroyed_indices: 1D integer array of destroyed request indices i in I_k.
    """
    N_agent = instance.N_per_agent
    frac = rng.uniform(min_ratio, max_ratio)
    num_destroy = max(2, min(N_agent, int(np.round(frac * N_agent))))

    i_idx = np.arange(N_agent)
    cur_costs = instance.c[k, i_idx, patterns_k]
    min_costs = np.min(instance.c[k], axis=1)
    potential_gain = (cur_costs - min_costs) + rng.uniform(0.5, 18.0, size=N_agent)

    active_coupled = np.where(patterns_k > 0)[0]
    selected_list = []

    # Release a subset of active coupled requests (slack-releasing removals)
    n_release = min(len(active_coupled), max(1, int(0.45 * num_destroy)))
    if n_release > 0:
        p_act = patterns_k[active_coupled]
        saving = instance.c[k, active_coupled, 0] - cur_costs[active_coupled]
        if dual_prices is not None and np.any(dual_prices > TOL):
            # Dual-guided destroy: remove coupled requests with the highest
            # dual-to-saving ratio ((lambda^T D_{k,i,p} + 0.1) / (saving + 1)),
            # i.e. low-saving requests that sit on congested hubs.
            dual_burden = instance.D[k, :, active_coupled, p_act] @ dual_prices
            score = (dual_burden + 0.1) / (saving + 1.0)
            score = score + rng.uniform(0.0, 1e-3, size=len(active_coupled))
        else:
            # No global prices: coupled requests are ranked by local cost alone
            # (local wave burden per unit of saving).
            a_burden = 2.0 * np.sum(instance.A[k, :, active_coupled, p_act], axis=1)
            score = a_burden / np.maximum(1.0, saving)
            score = score + rng.uniform(0.0, 0.25, size=len(active_coupled))
        top_release = active_coupled[np.argsort(-score)[:n_release]]
        selected_list.append(top_release)

    already = np.concatenate(selected_list) if selected_list else np.array([], dtype=np.int64)
    rem_pool = np.setdiff1d(i_idx, already, assume_unique=True)
    n_rem = num_destroy - len(already)

    if n_rem > 0 and len(rem_pool) > 0:
        scores = potential_gain[rem_pool]
        scores = scores + rng.uniform(0.0, 22.0, size=len(rem_pool))
        chosen_rem = rem_pool[np.argsort(-scores)[:n_rem]]
        selected_list.append(chosen_rem)

    destroyed_indices = np.concatenate(selected_list).astype(np.int64)
    partial_patterns_k = patterns_k.copy()
    partial_patterns_k[destroyed_indices] = 0
    return partial_patterns_k, destroyed_indices


def _vectorized_swap_or_upgrade_fallback(
    instance: CoupledRoutingInstance,
    k: int,
    incumbent_k: np.ndarray,
    d_idx: np.ndarray,
    max_total_global: np.ndarray,
    eff_c_d: np.ndarray,
    allow_net_upgrade: bool = True,
) -> np.ndarray:
    """
    Fast 3D NumPy vectorized single-request upgrade or 1-for-1 inter-request swap
    within destroyed_indices when multi-request greedy reinsertion gets blocked by
    local wave capacities. Guarantees strict local and global quota feasibility.
    """
    inc_global = compute_agent_global_usage(instance, k, incumbent_k)
    inc_local = compute_agent_local_usage(instance, k, incumbent_k)
    rem_g = max_total_global - inc_global
    rem_l = instance.b[k] - inc_local

    n_d = len(d_idx)
    row_d = np.arange(n_d)
    c_u = instance.c[k, d_idx, :]        # (n_d, P)
    D_u = instance.D[k][:, d_idx, :]     # (m_global, n_d, P)
    A_u = instance.A[k][:, d_idx, :]     # (m_local, n_d, P)

    p_old = incumbent_k[d_idx]
    d_old = D_u[:, row_d, p_old]         # (m_global, n_d)
    a_old = A_u[:, row_d, p_old]         # (m_local, n_d)
    c_old = c_u[row_d, p_old]            # (n_d,)
    eff_old = eff_c_d[row_d, p_old]      # (n_d,)

    # 1. Test all single-request upgrades/pattern changes (i, p_new) simultaneously
    d_diff = D_u - d_old[:, :, None]
    a_diff = A_u - a_old[:, :, None]
    c_diff = c_u - c_old[:, None]
    eff_diff = eff_c_d - eff_old[:, None]

    feas_1 = (
        np.all(d_diff <= rem_g[:, None, None] + TOL, axis=0)
        & np.all(a_diff <= rem_l[:, None, None] + TOL, axis=0)
        & (c_diff < -TOL)
    )
    if not allow_net_upgrade:
        # Only refine already-coupled requests (p_old > 0 -> p_new > 0)
        feas_1[p_old == 0, :] = False

    if np.any(feas_1):
        scores_1 = np.where(feas_1, eff_diff, np.inf)
        flat_idx = int(np.argmin(scores_1))
        pos_i, p_best = divmod(flat_idx, instance.P)
        y_out = incumbent_k.copy()
        y_out[d_idx[pos_i]] = p_best
        return y_out

    # 2. Test 1-for-1 inter-request swaps across top coupled candidates in d_idx
    coupled_pos = np.where(p_old > 0)[0]
    if len(coupled_pos) > 0:
        rel_order = coupled_pos[np.argsort(-eff_old[coupled_pos])[: min(4, len(coupled_pos))]]
        best_swap_score = np.inf
        best_rel = -1
        best_pos_i = -1
        best_p = -1
        for rel_pos in rel_order:
            rel_pos_int = int(rel_pos)
            loss_raw = float(c_u[rel_pos_int, 0] - c_old[rel_pos_int])
            loss_eff = float(eff_c_d[rel_pos_int, 0] - eff_old[rel_pos_int])
            rem_g_swap = rem_g + d_old[:, rel_pos_int]
            rem_l_swap = rem_l + a_old[:, rel_pos_int]

            feas_swap = (
                np.all(d_diff <= rem_g_swap[:, None, None] + TOL, axis=0)
                & np.all(a_diff <= rem_l_swap[:, None, None] + TOL, axis=0)
                & ((c_diff + loss_raw) < -TOL)
            )
            feas_swap[rel_pos_int, :] = False
            if np.any(feas_swap):
                scores_swap = np.where(feas_swap, eff_diff + loss_eff, np.inf)
                flat_idx = int(np.argmin(scores_swap))
                sc = float(scores_swap.reshape(-1)[flat_idx])
                if sc < best_swap_score:
                    best_swap_score = sc
                    best_rel = rel_pos_int
                    best_pos_i, best_p = divmod(flat_idx, instance.P)

        if best_rel >= 0:
            y_out = incumbent_k.copy()
            y_out[d_idx[best_rel]] = 0
            y_out[d_idx[best_pos_i]] = best_p
            return y_out

    return incumbent_k.copy()


def regret2_repair_hard_quota(
    instance: CoupledRoutingInstance,
    k: int,
    incumbent_k: np.ndarray,
    partial_k: np.ndarray,
    destroyed_indices: np.ndarray,
    max_global_delta: np.ndarray,
    dual_prices: Optional[np.ndarray] = None,
    rng: Optional[np.random.Generator] = None,
    noise_scale: float = 0.0,
    max_net_upgrades: Optional[int] = None,
) -> np.ndarray:
    """
    Vectorized Regret-2 repair operator R_k minimizing linear (or dual-adjusted) cost
    subject to strict local feasibility y_k in X_k and strict global incremental
    quota constraint:
        D_k (y_k - x_k^{(t)}) <= max_global_delta.

    Uses 3D NumPy broadcasting across all unassigned requests simultaneously.
    """
    y_k = partial_k.copy()
    d_idx = np.array(destroyed_indices, dtype=np.int64)
    if len(d_idx) == 0:
        return y_k

    inc_global = compute_agent_global_usage(instance, k, incumbent_k)
    max_total_global = inc_global + max_global_delta

    cur_global = compute_agent_global_usage(instance, k, y_k)
    cur_local = compute_agent_local_usage(instance, k, y_k)
    b_k = instance.b[k]

    c_d = instance.c[k, d_idx, :]        # (n_d, P)
    D_d = instance.D[k][:, d_idx, :]     # (m_global, n_d, P)
    A_d = instance.A[k][:, d_idx, :]     # (m_local, n_d, P)

    eff_c_d = (c_d - c_d[:, 0:1]).copy()
    if dual_prices is not None and np.any(dual_prices > TOL):
        lam = np.maximum(0.0, dual_prices)
        eff_c_d = eff_c_d + TIE_BREAK_EPS * np.einsum("m,mip->ip", lam, D_d)
    if rng is not None and noise_scale > 0.0:
        eff_c_d = eff_c_d + rng.normal(0.0, noise_scale, size=eff_c_d.shape)

    eff_c_d[:, 0] = 0.0

    prev_coupled_count = int(np.sum(incumbent_k[d_idx] > 0))
    max_coupled_allowed = (
        prev_coupled_count + max_net_upgrades
        if max_net_upgrades is not None
        else len(d_idx)
    )
    coupled_inserted = 0
    active_pos = np.arange(len(d_idx))

    while len(active_pos) > 0:
        if coupled_inserted >= max_coupled_allowed:
            break

        n_u = len(active_pos)
        rem_global = max_total_global - cur_global
        rem_local = b_k - cur_local

        D_u = D_d[:, active_pos, :]
        A_u = A_d[:, active_pos, :]

        feas_global = np.all(D_u <= rem_global[:, None, None] + TOL, axis=0)
        feas_local = np.all(A_u <= rem_local[:, None, None] + TOL, axis=0)
        feas_mask = feas_global & feas_local
        feas_mask[:, 0] = True

        costs_u = np.where(feas_mask, eff_c_d[active_pos, :], np.inf)
        order = np.argsort(costs_u, axis=1)

        row_arange = np.arange(n_u)
        p1_arr = order[:, 0]
        c1_arr = costs_u[row_arange, p1_arr]
        c2_arr = costs_u[row_arange, order[:, 1]]
        c2_arr = np.where(np.isfinite(c2_arr), c2_arr, c1_arr)

        regret_arr = 0.70 * (-c1_arr) + 0.30 * (c2_arr - c1_arr)
        regret_arr = np.where(p1_arr > 0, regret_arr, -1e9)

        best_sub = int(np.lexsort((c1_arr, -np.round(regret_arr, 7)))[0])
        best_pos = int(active_pos[best_sub])
        best_req = int(d_idx[best_pos])
        best_pattern = int(p1_arr[best_sub])

        if best_pattern == 0:
            break

        y_k[best_req] = best_pattern
        cur_global += D_d[:, best_pos, best_pattern]
        cur_local += A_d[:, best_pos, best_pattern]
        coupled_inserted += 1
        active_pos = np.delete(active_pos, best_sub)

    c_inc_sub = float(np.sum(c_d[np.arange(len(d_idx)), incumbent_k[d_idx]]))
    c_new_sub = float(np.sum(c_d[np.arange(len(d_idx)), y_k[d_idx]]))
    if c_new_sub >= c_inc_sub - TOL:
        allow_up = True if max_net_upgrades is None else (max_net_upgrades > 0)
        return _vectorized_swap_or_upgrade_fallback(
            instance, k, incumbent_k, d_idx, max_total_global, eff_c_d, allow_net_upgrade=allow_up
        )

    return y_k


def regret2_repair_proximal_al(
    instance: CoupledRoutingInstance,
    k: int,
    incumbent_k: np.ndarray,
    partial_k: np.ndarray,
    destroyed_indices: np.ndarray,
    q_k: np.ndarray,
    dual_prices: np.ndarray,
    rho_ell: float,
    max_global_delta_cap: Optional[np.ndarray] = None,
    rng: Optional[np.random.Generator] = None,
    noise_scale: float = 0.0,
    max_net_upgrades: Optional[int] = None,
) -> np.ndarray:
    """
    Vectorized Regret-2 repair operator minimizing the quota-penalized augmented
    Lagrangian surrogate (Equation 8), penalizing only the quota excess
    e = D_k(y_k - x_k^{(t)}) - q_k^{(t)}:
        F_tilde_k(y_k | x^{(t)}, lambda^{(t)}, rho_ell) =
            c_k^T y_k + (lambda^{(t)})^T [e]_+ + (rho_ell / 2) * || [e]_+ ||_2^2,
    with lambda^{(t)} >= 0. Inside the quota the surrogate is the true cost c_k^T y_k.
    over y_k in X_k using 3D NumPy broadcasting across all unassigned requests.
    """
    y_k = partial_k.copy()
    d_idx = np.array(destroyed_indices, dtype=np.int64)
    if len(d_idx) == 0:
        return y_k

    inc_global = compute_agent_global_usage(instance, k, incumbent_k)
    quota_threshold = inc_global + q_k

    if max_global_delta_cap is not None:
        hard_global_cap = inc_global + max_global_delta_cap
    else:
        hard_global_cap = None

    cur_global = compute_agent_global_usage(instance, k, y_k)
    cur_local = compute_agent_local_usage(instance, k, y_k)
    b_k = instance.b[k]

    c_d = instance.c[k, d_idx, :]        # (n_d, P)
    D_d = instance.D[k][:, d_idx, :]     # (m_global, n_d, P)
    A_d = instance.A[k][:, d_idx, :]     # (m_local, n_d, P)

    lin_c_d = (c_d - c_d[:, 0:1]).copy()
    lam = np.maximum(0.0, np.asarray(dual_prices, dtype=np.float64))
    if rng is not None and noise_scale > 0.0:
        lin_c_d = lin_c_d + rng.normal(0.0, noise_scale, size=lin_c_d.shape)

    lin_c_d[:, 0] = 0.0

    prev_coupled_count = int(np.sum(incumbent_k[d_idx] > 0))
    max_coupled_allowed = (
        prev_coupled_count + max_net_upgrades
        if max_net_upgrades is not None
        else len(d_idx)
    )
    coupled_inserted = int(np.sum(y_k[d_idx] > 0))
    active_pos = np.arange(len(d_idx))

    while len(active_pos) > 0:
        if coupled_inserted >= max_coupled_allowed:
            break

        n_u = len(active_pos)
        rem_local = b_k - cur_local
        D_u = D_d[:, active_pos, :]
        A_u = A_d[:, active_pos, :]

        feas_local = np.all(A_u <= rem_local[:, None, None] + TOL, axis=0)
        if hard_global_cap is not None:
            rem_global = hard_global_cap - cur_global
            feas_global = np.all(D_u <= rem_global[:, None, None] + TOL, axis=0)
            feas_mask = feas_local & feas_global
        else:
            feas_mask = feas_local
        feas_mask[:, 0] = True

        # Excess-only penalty (Eq. 8): lambda^T [e]_+ + (rho/2) ||[e]_+||^2 with
        # e = D_k(y_k - x_k) - q_k; zero inside the quota.
        cur_excess = np.maximum(0.0, cur_global - quota_threshold)
        cur_pen = float(lam @ cur_excess) + 0.5 * rho_ell * float(np.dot(cur_excess, cur_excess))

        new_globals = cur_global[:, None, None] + D_u
        excess = np.maximum(0.0, new_globals - quota_threshold[:, None, None])
        penalties = np.einsum("m,mip->ip", lam, excess) + 0.5 * rho_ell * np.sum(excess * excess, axis=0)
        marginal_vals = lin_c_d[active_pos, :] + (penalties - cur_pen)

        vals_u = np.where(feas_mask, marginal_vals, np.inf)
        order = np.argsort(vals_u, axis=1)

        row_arange = np.arange(n_u)
        p1_arr = order[:, 0]
        v1_arr = vals_u[row_arange, p1_arr]
        v2_arr = vals_u[row_arange, order[:, 1]]
        v2_arr = np.where(np.isfinite(v2_arr), v2_arr, v1_arr)

        regret_arr = 0.70 * (-v1_arr) + 0.30 * (v2_arr - v1_arr)
        regret_arr = np.where(p1_arr > 0, regret_arr, -1e9)

        best_sub = int(np.lexsort((v1_arr, -np.round(regret_arr, 7)))[0])
        best_pos = int(active_pos[best_sub])
        best_req = int(d_idx[best_pos])
        best_pattern = int(p1_arr[best_sub])

        if best_pattern == 0:
            break

        y_k[best_req] = best_pattern
        cur_global += D_d[:, best_pos, best_pattern]
        cur_local += A_d[:, best_pos, best_pattern]
        coupled_inserted += 1
        active_pos = np.delete(active_pos, best_sub)

    if hard_global_cap is not None:
        c_inc_sub = float(np.sum(c_d[np.arange(len(d_idx)), incumbent_k[d_idx]]))
        c_new_sub = float(np.sum(c_d[np.arange(len(d_idx)), y_k[d_idx]]))
        if c_new_sub >= c_inc_sub - TOL:
            allow_up = True if max_net_upgrades is None else (max_net_upgrades > 0)
            return _vectorized_swap_or_upgrade_fallback(
                instance, k, incumbent_k, d_idx, hard_global_cap, lin_c_d, allow_net_upgrade=allow_up
            )

    return y_k


def donor_rebalance_repair(
    instance: CoupledRoutingInstance,
    k: int,
    incumbent_k: np.ndarray,
    hub_weights: np.ndarray,
    n_release: int = DONOR_RELEASES,
) -> np.ndarray:
    """
    Slack-releasing (donor / hub-rebalancing) repair for portfolio level l = 2.

    Hub weights w >= 0: w = lambda^{(t)} with dual prices, w = 1 without (No-Duals).
    1. Release: up to ``n_release`` currently coupled requests with the largest
       weighted hub burden per unit of saving, w^T D_{k,i,p_i} / (c_{k,i,0} - c_{k,i,p_i} + 1),
       are each moved to the cheapest pattern p' (another hub pattern or p = 0) with
       w^T D_{k,i,p'} < w^T D_{k,i,p_i}.
    2. Compensate: one upgrade of another request (i, p'') with the largest cost
       saving whose added weighted hub usage does not exceed the weighted usage
       released in step 1, so the net weighted hub usage of the move is <= 0.
    Local wave capacities b_k are kept throughout. Global feasibility of the move is
    checked by the barrier through delta_{r,k,2}.
    """
    y = incumbent_k.copy()
    N = instance.N_per_agent
    i_all = np.arange(N)
    D_k, A_k, c_k = instance.D[k], instance.A[k], instance.c[k]
    w = np.maximum(0.0, np.asarray(hub_weights, dtype=np.float64))
    wD = np.einsum("m,mip->ip", w, D_k)  # (N, P)
    cur_local = compute_agent_local_usage(instance, k, y)
    touched = np.zeros(N, dtype=bool)
    released_total = 0.0

    for _ in range(int(n_release)):
        coupled = np.where((y > 0) & ~touched)[0]
        if len(coupled) == 0:
            break
        burden = wD[coupled, y[coupled]] / (c_k[coupled, 0] - c_k[coupled, y[coupled]] + 1.0)
        moved = False
        for i in coupled[np.argsort(-burden, kind="stable")]:
            p_old = y[i]
            a_diff = A_k[:, i, :] - A_k[:, i, p_old][:, None]          # (m_local, P)
            ok = (wD[i] < wD[i, p_old] - TOL) & np.all(a_diff <= (instance.b[k] - cur_local)[:, None] + TOL, axis=0)
            if not np.any(ok):
                continue
            p_new = int(np.argmin(np.where(ok, c_k[i], np.inf)))
            released_total += float(wD[i, p_old] - wD[i, p_new])
            cur_local += A_k[:, i, p_new] - A_k[:, i, p_old]
            y[i] = p_new
            touched[i] = True
            moved = True
            break
        if not moved:
            break

    if released_total > TOL:
        p_cur = y
        added = wD - wD[i_all, p_cur][:, None]                          # (N, P)
        saving = c_k[i_all, p_cur][:, None] - c_k                       # (N, P)
        a_diff = A_k - A_k[:, i_all, p_cur][:, :, None]
        ok = (
            (~touched)[:, None]
            & (added <= released_total + TOL)
            & (saving > TOL)
            & np.all(a_diff <= (instance.b[k] - cur_local)[:, None, None] + TOL, axis=0)
        )
        if np.any(ok):
            i_best, p_best = np.unravel_index(int(np.argmax(np.where(ok, saving, -np.inf))), saving.shape)
            y[i_best] = p_best
    return y
