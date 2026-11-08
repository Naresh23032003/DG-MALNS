"""
Shared LNS worker step used by EVERY LNS method (PC-MALNS, the greedy portfolio
rules, Opt-Rollback, Opt-SeqLock, Static-Quota and Demand-Quota).

All methods call ``worker_step`` with the same destroy/repair operators and the
same random stream: the generator of worker k at epoch t is
np.random.default_rng([seed, t, k]), independent of the method and of the number
of processes. Methods differ only in (i) the slack quota q_k given to the
quota-safe repair, (ii) whether dual prices lambda are passed, (iii) the number of
portfolio levels L, and (iv) the synchronization rule applied afterwards.

Portfolio levels (L = 3 for PC-MALNS and the -Portfolio rules; L = 1 for the
single-proposal baselines). All
levels are built from the SAME destroyed partial solution (price-free destroy, as in
the baselines):
    l = 0  incumbent x_k^{(t)}, replaced by the donor rebalance of x_k^{(t)} (hub
           weights w = lambda, or 1 without duals) only if the donor dominates it:
           no higher cost and no higher usage on any hub, lower on at least one
    l = 1  quota-safe repair y_hat_k: best-of-two Regret-2 repair on true cost c_k
           with D_k(y - x_k) <= q_k (falls back to x_k if not improving); with
           q_k = s/K this is exactly the Static-Quota proposal
    l = 2  borrower repair minimizing the excess-only surrogate (Eq. 8) with prices
           lambda (0 without duals) and gentle penalty rho_t, capped by
           D_k(y - x_k) <= 0.5 (q_k + s^{(t)})
    l = 3  optimistic repair y_bar_k: the same best-of-two repair with cap s^{(t)},
           from the same random-generator state as l = 1; this is exactly the
           Opt-Rollback / Opt-SeqLock proposal (falls back to x_k if not improving)
"""

import time
from typing import Optional, Tuple
import numpy as np

from src.instance_generator import CoupledRoutingInstance
from src.feasibility import evaluate_agent_cost, compute_agent_global_usage, TOL
from src.operators import (
    destroy_operator,
    base_repair_best_of_two,
    regret2_repair_proximal_al,
    donor_rebalance_repair,
    DESTROY_MIN_RATIO,
    DESTROY_MAX_RATIO,
    REPAIR_NOISE,
    MAX_NET_UPGRADES,
)

def worker_rng(seed: int, t: int, k: int, rep: int = 0) -> np.random.Generator:
    """Random stream of worker k at epoch t. rep > 0 gives independent algorithm
    replicates on the same instance; rep = 0 is the stream used in the main runs."""
    if rep == 0:
        return np.random.default_rng([int(seed), int(t), int(k)])
    return np.random.default_rng([int(seed), int(t), int(k), int(rep)])


def worker_step(
    instance: CoupledRoutingInstance,
    k: int,
    inc_k: np.ndarray,
    s_t: np.ndarray,
    q_k: np.ndarray,
    seed: int,
    t: int,
    L: int,
    dual_prices: Optional[np.ndarray],
    rho_t: float,
    rep: int = 0,
    max_net: Optional[int] = MAX_NET_UPGRADES,
    inner_iters: int = 1,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """
    Build the portfolio of worker k at epoch t.

    Returns:
        portfolio: (L+1, N_agent) pattern vectors y_k^{(t,l)}
        delta_c:   (L+1,) cost deltas c_k^T (y_k^{(t,l)} - x_k^{(t)})
        delta_D:   (m, L+1) hub usage deltas D_k (y_k^{(t,l)} - x_k^{(t)})
        tau:       worker wall-clock time in seconds

    max_net:     cap on net new consolidations per repair call (None = no cap).
    inner_iters: M >= 1 chained destroy-repair steps per level before the barrier.
                 Step j > 0 destroys the level's current trial solution and repairs
                 it against the remaining level cap; a step is kept only if it lowers
                 the agent cost. M = 1 reproduces the single-step worker exactly.
    """
    t0 = time.perf_counter()
    rng = worker_rng(seed, t, k, rep)
    m = instance.m_global
    N = instance.N_per_agent
    duals = dual_prices if (dual_prices is not None and np.any(dual_prices > TOL)) else None

    portfolio = np.zeros((L + 1, N), dtype=np.int64)
    delta_c = np.zeros(L + 1, dtype=np.float64)
    delta_D = np.zeros((m, L + 1), dtype=np.float64)

    c_inc = evaluate_agent_cost(instance, k, inc_k)
    u_inc = compute_agent_global_usage(instance, k, inc_k)

    def put(l, y):
        portfolio[l] = y
        delta_c[l] = evaluate_agent_cost(instance, k, y) - c_inc
        delta_D[:, l] = compute_agent_global_usage(instance, k, y) - u_inc

    def chain(step, gen):
        """Run M chained destroy-repair steps; step(y, u_used, partial, idx, gen) -> y_new."""
        y, c_y, u_used = inc_k.copy(), c_inc, np.zeros(m)
        for j in range(max(1, int(inner_iters))):
            if j == 0:
                part, idx = partial_k, destroyed_idx
            else:
                part, idx = destroy_operator(instance, k, y, gen, min_ratio=DESTROY_MIN_RATIO,
                                             max_ratio=DESTROY_MAX_RATIO, dual_prices=None)
            y_new = step(y, u_used, part, idx, gen)
            c_new = evaluate_agent_cost(instance, k, y_new)
            if c_new < c_y - TOL:
                y, c_y = y_new, c_new
                u_used = compute_agent_global_usage(instance, k, y) - u_inc
        return y if c_y < c_inc - TOL else inc_k.copy()

    def safe_repair(cap, gen):
        return chain(lambda y, u_used, part, idx, g: base_repair_best_of_two(
            instance, k, y, part, idx, max_global_delta=cap - u_used, rng=g,
            dual_prices=None, max_net_upgrades=max_net), gen)

    # Price-free destroy shared by every method and every level
    partial_k, destroyed_idx = destroy_operator(
        instance, k, inc_k, rng,
        min_ratio=DESTROY_MIN_RATIO, max_ratio=DESTROY_MAX_RATIO, dual_prices=None,
    )
    state = rng.bit_generator.state  # generator state shared by l = 1 and l = 3

    # l = 0: incumbent (or a dominating donor rebalance)
    put(0, inc_k)
    if L >= 2:
        w = duals if duals is not None else np.ones(m, dtype=np.float64)
        y0 = donor_rebalance_repair(instance, k, inc_k, hub_weights=w)
        dc0 = evaluate_agent_cost(instance, k, y0) - c_inc
        dD0 = compute_agent_global_usage(instance, k, y0) - u_inc
        if dc0 <= TOL and np.all(dD0 <= TOL) and np.any(dD0 < -TOL):
            put(0, y0)

    # l = 1: quota-safe repair y_hat (cap q_k)
    put(1, safe_repair(q_k, rng))

    if L >= 3:
        # l = 3: optimistic repair y_bar (cap s^{(t)}), same generator state as l = 1
        rng_opt = np.random.default_rng()
        rng_opt.bit_generator.state = state
        put(3, safe_repair(s_t, rng_opt))

    if L >= 2:
        # l = 2: borrower repair of the excess-only surrogate (Eq. 8)
        lam2 = duals if duals is not None else np.zeros(m)
        cap2 = 0.5 * (q_k + s_t)
        y2 = chain(lambda y, u_used, part, idx, g: regret2_repair_proximal_al(
            instance=instance, k=k, incumbent_k=y, partial_k=part, destroyed_indices=idx,
            q_k=q_k - u_used, dual_prices=lam2, rho_ell=rho_t,
            max_global_delta_cap=cap2 - u_used, rng=g, noise_scale=REPAIR_NOISE,
            max_net_upgrades=max_net), rng)
        put(2, y2)

    return portfolio, delta_c, delta_D, time.perf_counter() - t0


# ---------------------------------------------------------------------------
# Process-pool support (real multi-process execution of the worker step)
# ---------------------------------------------------------------------------
_POOL_INSTANCE: Optional[CoupledRoutingInstance] = None


def pool_initializer(instance: CoupledRoutingInstance) -> None:
    global _POOL_INSTANCE
    _POOL_INSTANCE = instance


def pool_task(args):
    return worker_step(_POOL_INSTANCE, *args)


def pool_batch(batch):
    """Run several worker steps in one task (one round trip per process and epoch)."""
    return [worker_step(_POOL_INSTANCE, *a) for a in batch]
