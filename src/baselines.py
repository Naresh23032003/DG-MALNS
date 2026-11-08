"""
Shared LP components of the RPA-SH pipeline.

build_block_angular_matrices   sparse constraint matrix of the RPA-SH integer program
solve_lp_relaxation            LP relaxation (bound, hub duals, primal solution)
lp_round_start                 LP-Round warm start: LP relaxation, greedy rounding by
                               reduced-cost saving under d and b_k, and one local
                               upgrade pass; its time is charged to every LNS run
rate_pct                       percentage with an undefined (NaN) value for 0 / 0
"""

import time
from typing import Dict, Tuple

import numpy as np
import scipy.sparse as sp
from scipy.optimize import linprog

from src.instance_generator import CoupledRoutingInstance
from src.feasibility import TOL

MILP_REL_GAP = 1e-4


def rate_pct(num: int, den: int) -> float:
    """Acceptance rate in percent; undefined (NaN) when there were no proposals."""
    return 100.0 * num / den if den > 0 else float("nan")


def build_block_angular_matrices(
    instance: CoupledRoutingInstance,
) -> Tuple[np.ndarray, sp.csc_matrix, np.ndarray, np.ndarray]:
    """
    Construct the sparse block-angular constraint matrix for Equations (1)-(5)
    using scipy.sparse.csc_matrix.

    Decision vector x in {0,1}^{K * N_per_agent * P} flattened in C-order (k, i, p).
    Constraints:
    1. Global coupling (m_global rows): sum_k D_k x_k <= d
    2. Local wave capacities (K * m_local rows): A_k x_k <= b_k
    3. Request assignment (K * N_per_agent rows): sum_p x_{k,i,p} = 1
    """
    K = instance.K
    N_agent = instance.N_per_agent
    P = instance.P
    m_global = instance.m_global
    m_local = instance.m_local

    n_vars = K * N_agent * P
    c_flat = instance.c.reshape(n_vars)

    rows = []
    cols = []
    vals = []

    # 1. Global coupling rows: 0 .. m_global - 1
    for k in range(K):
        for r in range(m_global):
            nz_i, nz_p = np.nonzero(instance.D[k, r])
            if len(nz_i) > 0:
                var_idx = (k * N_agent + nz_i) * P + nz_p
                rows.append(np.full(len(nz_i), r, dtype=np.int64))
                cols.append(var_idx)
                vals.append(instance.D[k, r, nz_i, nz_p])

    offset_local = m_global
    # 2. Local wave capacity rows: offset_local .. offset_local + K * m_local - 1
    for k in range(K):
        for w in range(m_local):
            row_id = offset_local + k * m_local + w
            nz_i, nz_p = np.nonzero(instance.A[k, w])
            if len(nz_i) > 0:
                var_idx = (k * N_agent + nz_i) * P + nz_p
                rows.append(np.full(len(nz_i), row_id, dtype=np.int64))
                cols.append(var_idx)
                vals.append(instance.A[k, w, nz_i, nz_p])

    offset_assign = offset_local + K * m_local
    # 3. Assignment rows: offset_assign .. offset_assign + K * N_agent - 1
    req_ids = np.arange(K * N_agent)
    assign_rows = np.repeat(offset_assign + req_ids, P)
    assign_cols = np.arange(n_vars)
    assign_vals = np.ones(n_vars, dtype=np.float64)
    rows.append(assign_rows)
    cols.append(assign_cols)
    vals.append(assign_vals)

    all_rows = np.concatenate(rows)
    all_cols = np.concatenate(cols)
    all_vals = np.concatenate(vals)

    n_rows = offset_assign + K * N_agent
    A_csc = sp.csc_matrix((all_vals, (all_rows, all_cols)), shape=(n_rows, n_vars))

    lb = np.concatenate([
        np.full(m_global, -np.inf),
        np.full(K * m_local, -np.inf),
        np.ones(K * N_agent),
    ])
    ub = np.concatenate([
        instance.d,
        instance.b.reshape(K * m_local),
        np.ones(K * N_agent),
    ])

    return c_flat, A_csc, lb, ub


def solve_lp_relaxation(instance: CoupledRoutingInstance) -> Dict[str, object]:
    """
    LP relaxation of (1)-(5) with HiGHS. Returns the LP bound, the coupling duals
    lambda_LP >= 0 (shape m), the fractional solution x_LP (K, N, P) and the solve
    time in seconds. Cached on the instance; the time is reported with the result.
    """
    cached = getattr(instance, "_lp_cache", None)
    if cached is not None:
        return cached
    t0 = time.perf_counter()
    m = instance.m_global
    c_flat, A_csc, _, ub = build_block_angular_matrices(instance)
    n_ineq = m + instance.K * instance.m_local
    res = linprog(
        c=c_flat, A_ub=A_csc[:n_ineq, :], b_ub=ub[:n_ineq],
        A_eq=A_csc[n_ineq:, :], b_eq=ub[n_ineq:], bounds=(0.0, 1.0), method="highs",
    )
    elapsed = time.perf_counter() - t0
    if res.success:
        lam = np.maximum(0.0, -np.asarray(res.ineqlin.marginals[:m], dtype=np.float64))
        x_lp = res.x.reshape(instance.K, instance.N_per_agent, instance.P)
        bound = float(res.fun)
    else:
        lam = np.zeros(m)
        x_lp = np.zeros((instance.K, instance.N_per_agent, instance.P))
        bound = 0.0
    out = {"lp_bound": bound, "lambda": lam, "x_lp": x_lp, "time_s": elapsed}
    instance._lp_cache = out
    return out


def lp_round_start(instance: CoupledRoutingInstance) -> Tuple[np.ndarray, float, float]:
    """
    LP-Round: solve the LP relaxation, then round greedily. Candidate assignments
    (k, i, p >= 1) with x_LP > 0 are taken in decreasing order of reduced-cost saving
    c_{k,i,0} - (c_{k,i,p} + lambda_LP^T D_{k,i,p}) and accepted if request (k, i) is
    still on p = 0 and the hub (d) and wave (b_k) capacities allow it. One local
    upgrade pass then gives every request still on p = 0 its cheapest feasible
    pattern, in decreasing order of raw saving.

    Returns (patterns, lp_time_s, rounding_time_s); cached on the instance so every
    method uses the same warm start and the same measured tau_init.
    """
    cached = getattr(instance, "_lp_round_cache", None)
    if cached is not None:
        return cached[0].copy(), cached[1], cached[2]
    lp = solve_lp_relaxation(instance)
    t0 = time.perf_counter()
    K, N, P = instance.K, instance.N_per_agent, instance.P
    lam, x_lp = lp["lambda"], lp["x_lp"]
    c, D, A = instance.c, instance.D, instance.A
    pats = np.zeros((K, N), dtype=np.int64)
    hub = np.zeros(instance.m_global)
    wave = np.zeros((K, instance.m_local))

    red = c[:, :, :1] - (c + np.einsum("m,kmip->kip", lam, D))
    kk, ii, pp = np.nonzero((x_lp > 1e-6) & (np.arange(P)[None, None, :] >= 1))
    order = np.argsort(-red[kk, ii, pp], kind="stable")
    for j in order:
        k, i, p = kk[j], ii[j], pp[j]
        if pats[k, i] != 0:
            continue
        if np.all(hub + D[k, :, i, p] <= instance.d + TOL) and np.all(wave[k] + A[k, :, i, p] <= instance.b[k] + TOL):
            pats[k, i] = p
            hub += D[k, :, i, p]
            wave[k] += A[k, :, i, p]

    # one local upgrade pass for requests left on p = 0
    k0, i0 = np.nonzero(pats == 0)
    best_saving = c[k0, i0, 0] - np.min(c[k0, i0, 1:], axis=1)
    for j in np.argsort(-best_saving, kind="stable"):
        k, i = k0[j], i0[j]
        for p in np.argsort(c[k, i, 1:]) + 1:
            if c[k, i, p] >= c[k, i, 0]:
                break
            if np.all(hub + D[k, :, i, p] <= instance.d + TOL) and np.all(wave[k] + A[k, :, i, p] <= instance.b[k] + TOL):
                pats[k, i] = p
                hub += D[k, :, i, p]
                wave[k] += A[k, :, i, p]
                break
    round_time = time.perf_counter() - t0
    instance._lp_round_cache = (pats.copy(), float(lp["time_s"]), round_time)
    return pats, float(lp["time_s"]), round_time
