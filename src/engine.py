"""
Unified concurrent multi-agent LNS engine (revision 2 experimental architecture).

Every LNS method in the revision experiments is one EngineConfig of this loop:

    start     init_mode in {"direct", "booking", "lp_round"}
                direct   : every request on its uncoupled pattern p = 0, lambda = 0,
                           alpha = 1/K (no central information, zero start cost)
                booking  : decentralized sequential agent booking (agents in random
                           order book their cheapest feasible pattern under d and b_k;
                           no LP, no prices); its measured time is charged
                lp_round : centralized LP relaxation + rounding (warm start); LP time
                           and rounding time are charged
    workers   portfolio of L + 1 levels (L = 3: donor / quota-safe / borrower /
              optimistic; L = 1: incumbent + one proposal), M = inner_iters chained
              destroy-repair steps per level, consolidation cap max_net (None = off)
    barrier   commit rule (src/commit_rules.py)
    prices    duals in {"none", "heuristic", "mccrip_lp"}
                heuristic : smoothed excess-demand step of the paper (Eq. 16)
                mccrip_lp : smoothed coupling-row duals of the LP relaxation of the
                            MC-CRIP master problem at the barrier
    quotas    quota in {"static", "demand", "dynamic"}
                static  : alpha = 1/K
                demand  : alpha_{r,k} = U_{r,k} / sum_j U_{r,j}, U = hub usage of the
                          agents' unconstrained cheapest patterns (fixed)
                dynamic : the paper's unrealized-gain reallocation (Eq. 17)

Clocks (all recorded):
    wall_clock_s      true elapsed time of the run (time.perf_counter), including the
                      start construction and, for W > 1, all inter-process traffic
                      (pool start-up is reported separately as pool_startup_s)
    cpu_time_s        start time + sum over epochs of (sum_k tau_k + tau_sync)
    sim_parallel_s    start time + sum over epochs of (max_k tau_k + tau_sync)
The anytime trace stores (wall-clock time, objective) after every epoch.
"""

from dataclasses import dataclass, field, asdict
import math
import time
from typing import Optional, List, Dict

import numpy as np
from scipy.optimize import linprog

from src.instance_generator import CoupledRoutingInstance
from src.feasibility import (evaluate_global_cost, compute_global_slack, compute_all_global_usage,
                             verify_solution_feasibility, TOL)
from src.worker import worker_step
from src.agent_pool import AgentPool
from src.commit_rules import apply_rule, counterfactual_costs, selection_feasible, selection_cost, KEEP
from src.bcrm_solver import LAST_SOLVE_INFO


@dataclass
class EngineConfig:
    name: str
    L: int = 3
    commit: str = "MC-CRIP"
    proposal_cap: str = "quota"     # L = 1 only: "quota" (q_k) or "optimistic" (s^{(t)})
    duals: str = "none"
    quota: str = "static"
    init_mode: str = "booking"
    max_net: Optional[int] = None
    inner_iters: int = 1
    epochs: int = 120
    time_budget_s: Optional[float] = None   # stop when the chosen clock reaches it
    budget_clock: str = "wall"              # "wall" | "cpu"
    rho_init: float = 0.35
    rho_decay: float = 0.985
    beta_dual: float = 0.15
    kappa_lp: float = 0.3                   # smoothing of the MC-CRIP LP duals
    omega_quota: float = 0.25
    counterfactual: bool = False


@dataclass
class EngineResult:
    method: str
    config: Dict
    instance_name: str
    best_obj: float
    initial_obj: float
    lower_bound: float
    gap_pct: float
    feasible: bool
    wall_clock_s: float
    cpu_time_s: float
    sim_parallel_s: float
    init_time_s: float
    pool_startup_s: float
    workers_W: int
    epochs_run: int
    fast_path_epochs: int
    conflict_epochs: int
    accepted_moves: int
    proposals: int
    matcher_ms_mean: float
    matcher_fallbacks: int
    primal_integral: float
    trace_t: List[float] = field(default_factory=list)
    trace_obj: List[float] = field(default_factory=list)
    trace_slack: List[float] = field(default_factory=list)    # mean_r s_r / d_r after each epoch
    trace_bottleneck: List[float] = field(default_factory=list)  # min_r s_r / d_r after each epoch
    cf_sum: Dict[str, float] = field(default_factory=dict)       # summed counterfactual Delta C
    cf_strict_wins: Dict[str, int] = field(default_factory=dict)  # epochs MC-CRIP strictly better
    patterns: Optional[np.ndarray] = None


# ---------------------------------------------------------------------------
# Starts
# ---------------------------------------------------------------------------
def booking_start(instance: CoupledRoutingInstance, utilization: float = 1.0) -> np.ndarray:
    """Decentralized sequential booking: agents in a random order (rng([seed, 77])),
    each takes its requests in random order and books its cheapest pattern that keeps
    hub usage <= utilization * d and wave usage <= b_k (else p = 0). No LP, no prices."""
    rng = np.random.default_rng([int(instance.seed), 77])
    K, N, m = instance.K, instance.N_per_agent, instance.m_global
    pats = np.zeros((K, N), dtype=np.int64)
    hub = np.zeros(m)
    cap = utilization * instance.d
    order_p = np.argsort(instance.c, axis=2, kind="stable")
    for k in rng.permutation(K):
        wave = np.zeros(instance.m_local)
        for i in rng.permutation(N):
            for p in order_p[k, i]:
                if p == 0:
                    break
                dD = instance.D[k, :, i, p]
                dA = instance.A[k, :, i, p]
                if np.all(hub + dD <= cap + TOL) and np.all(wave + dA <= instance.b[k] + TOL):
                    pats[k, i] = p
                    hub += dD
                    wave += dA
                    break
    return pats


def make_start(instance, init_mode):
    """Return (patterns, charged time in s)."""
    t0 = time.perf_counter()
    if init_mode == "direct":
        pats = np.zeros((instance.K, instance.N_per_agent), dtype=np.int64)
        return pats, time.perf_counter() - t0
    if init_mode == "booking":
        pats = booking_start(instance)
        return pats, time.perf_counter() - t0
    if init_mode == "lp_round":
        from src.baselines import lp_round_start
        pats, lp_t, rd_t = lp_round_start(instance)
        if getattr(instance, "mmkp_n", None) is not None:
            # MMKP instances: every group needs an item (src/mmkp.py); charged to the run
            from src.mmkp import mmkp_feasibility_repair
            t1 = time.perf_counter()
            pats = mmkp_feasibility_repair(instance, pats)
            rd_t += time.perf_counter() - t1
        return pats, lp_t + rd_t
    raise ValueError(init_mode)


def demand_alpha(instance) -> np.ndarray:
    """alpha_{r,k} = U_{r,k} / sum_j U_{r,j} with U the hub usage of every agent's
    unconstrained cheapest patterns; 1/K on hubs nobody demands."""
    K, N = instance.K, instance.N_per_agent
    p_star = np.argmin(instance.c, axis=2)
    U = np.stack([instance.D[k][:, np.arange(N), p_star[k]].sum(axis=1) for k in range(K)], axis=1)
    tot = U.sum(axis=1, keepdims=True)
    return np.where(tot > TOL, U / np.maximum(tot, TOL), 1.0 / K)


def mccrip_lp_duals(delta_c: np.ndarray, delta_slack: np.ndarray) -> np.ndarray:
    """Coupling-row duals mu >= 0 of the LP relaxation of MC-CRIP
    min sum c z  s.t.  sum delta z <= 0, sum_l z_kl = 1, 0 <= z <= 1."""
    m, K, nl = delta_slack.shape
    n = K * nl
    A_eq = np.zeros((K, n))
    for k in range(K):
        A_eq[k, k * nl:(k + 1) * nl] = 1.0
    res = linprog(delta_c.reshape(-1), A_ub=delta_slack.reshape(m, n), b_ub=np.zeros(m),
                  A_eq=A_eq, b_eq=np.ones(K), bounds=(0.0, 1.0), method="highs")
    if not res.success:
        return np.zeros(m)
    return np.maximum(0.0, -np.asarray(res.ineqlin.marginals, dtype=np.float64))


def primal_integral(trace_t, trace_obj, ref_obj, T) -> float:
    """Berthold (2013) primal integral on [0, T] (seconds x fraction) with the primal
    gap gamma(x) = |x - ref| / max(|x|, |ref|) (1 before the first solution)."""
    if T <= 0:
        return 0.0
    total, prev_t, prev_g = 0.0, 0.0, 1.0
    for t, o in zip(trace_t, trace_obj):
        t = min(max(t, 0.0), T)
        total += prev_g * (t - prev_t)
        prev_t = t
        prev_g = 0.0 if o is None else abs(o - ref_obj) / max(abs(o), abs(ref_obj), 1e-9)
    total += prev_g * (T - prev_t)
    return total


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
def run_engine(instance: CoupledRoutingInstance, cfg: EngineConfig, lower_bound: float,
               seed: int, rep: int = 0, pool: Optional[AgentPool] = None,
               keep_patterns: bool = False) -> EngineResult:
    """Serial run (pool=None, W = 1) or real multi-process run on a persistent
    AgentPool (W = pool.W processes, started once per experiment). The one-time
    process start-up is reported as pool_startup_s and not charged; shipping the
    instance and x^(0) to the processes is charged to wall_clock_s. Serial and pool
    runs give identical trajectories."""
    wall0 = time.perf_counter()
    K, m = instance.K, instance.m_global
    patterns, tau_init = make_start(instance, cfg.init_mode)
    # the LP-Round start is cached on the instance: charge its measured time to the
    # wall clock of every run, not only to the first run on this instance
    wall0 -= max(0.0, tau_init - (time.perf_counter() - wall0))
    initial_obj = evaluate_global_cost(instance, patterns)
    W = 1 if pool is None else pool.W
    pool_startup = 0.0 if pool is None else pool.startup_s
    if pool is not None:
        pool.load(instance)      # charged: instance data shipped to the W processes
        pool.reset(patterns)     # charged: x^(0) shipped once
    s_cur = compute_global_slack(instance, patterns)
    obj_cur = initial_obj
    prev_sel = None

    lambda_t = np.zeros(m)
    if cfg.duals != "none" and cfg.init_mode == "lp_round":
        from src.baselines import solve_lp_relaxation
        lambda_t = np.maximum(0.0, solve_lp_relaxation(instance)["lambda"].copy())
    alpha_t = demand_alpha(instance) if cfg.quota == "demand" else np.full((m, K), 1.0 / K)

    rng_rule = np.random.default_rng([int(seed), 991, int(rep)])
    rng_cf = np.random.default_rng([int(seed), 992, int(rep)])
    cpu_t = sim_t = tau_init
    trace_t = [time.perf_counter() - wall0]
    trace_obj = [initial_obj]
    d_pos = np.maximum(instance.d, TOL)
    trace_slack = [float(np.mean(s_cur / d_pos))]
    trace_bottleneck = [float(np.min(s_cur / d_pos))]
    fast = conflicts = accepted = proposals = fallbacks = 0
    matcher_ms: List[float] = []
    cf_sum: Dict[str, float] = {}
    cf_wins: Dict[str, int] = {}
    L = cfg.L
    t = 0

    def clock():
        return (time.perf_counter() - wall0) if cfg.budget_clock == "wall" else cpu_t

    while True:
        if cfg.time_budget_s is None:
            if t >= cfg.epochs:
                break
        elif clock() >= cfg.time_budget_s or t >= 50 * cfg.epochs:
            break
        s_t = s_cur.copy()
        rho_t = cfg.rho_init * (cfg.rho_decay ** t)
        q_all = alpha_t * s_t[:, None]
        duals_arg = lambda_t.copy() if cfg.duals != "none" else None
        optimistic = (L == 1 and cfg.proposal_cap == "optimistic")
        q_send = np.tile(s_t[:, None], (1, K)) if optimistic else q_all
        if pool is None:
            outs = [worker_step(instance, k, patterns[k], s_t, q_send[:, k].copy(), seed, t, L,
                                duals_arg, rho_t, rep, cfg.max_net, cfg.inner_iters)
                    for k in range(K)]
            portfolio = np.stack([o[0] for o in outs])
            outs = [o[1:] for o in outs]
        else:
            outs = pool.step(prev_sel, t, s_t, q_send, duals_arg, rho_t, seed, rep, L,
                             cfg.max_net, cfg.inner_iters)
        ts0 = time.perf_counter()
        delta_c = np.stack([o[0] for o in outs])
        raw_dD = np.stack([o[1] for o in outs], axis=1)
        taus = np.array([o[2] for o in outs])
        if L == 1 and cfg.proposal_cap == "optimistic":
            q_eff = np.tile(s_t[:, None], (1, K)) / K   # only used by quota-relative rules
        else:
            q_eff = q_all

        best_l = np.argmin(delta_c, axis=1)
        is_fast = bool(np.all(raw_dD[:, np.arange(K), best_l].sum(axis=1) <= s_t + TOL))
        fast += int(is_fast)
        conflicts += int(not is_fast)
        tm0 = time.perf_counter()
        sel = apply_rule(cfg.commit, delta_c, raw_dD, s_t, q_eff, rng_rule, lambda_t, rho_t)
        if cfg.commit == "MC-CRIP":
            fallbacks += int(not LAST_SOLVE_INFO["proven_optimal"])
        if not is_fast:
            matcher_ms.append(1000.0 * (time.perf_counter() - tm0))
            if cfg.counterfactual and L >= 2:
                tcf0 = time.perf_counter()
                cf = counterfactual_costs(delta_c, raw_dD, s_t, q_eff, lambda_t, rho_t, rng_cf)
                for r, v in cf.items():
                    cf_sum[r] = cf_sum.get(r, 0.0) + v
                    cf_wins[r] = cf_wins.get(r, 0) + int(cf["MC-CRIP"] < v - 1e-6)
                cf_time = time.perf_counter() - tcf0
                ts0 += cf_time      # logging is not charged to any clock
                wall0 += cf_time
        assert selection_feasible(raw_dD, s_t, sel), (cfg.name, t)

        proposals += int(np.sum(np.min(delta_c, axis=1) < -TOL))
        for k in range(K):
            if sel[k] >= 0:
                if delta_c[k, sel[k]] < -TOL:
                    accepted += 1
                if pool is None:
                    patterns[k] = portfolio[k, sel[k]]
                obj_cur += float(delta_c[k, sel[k]])
                s_cur = s_cur - raw_dD[:, k, sel[k]]
        prev_sel = sel.copy()

        # prices
        if cfg.duals == "heuristic":
            g_t = np.sum(raw_dD[:, :, L] - q_eff, axis=1)
            gamma_t = 0.25 * float(np.sum(np.abs(delta_c[:, L]))) / (float(g_t @ g_t) + 1.0)
            lambda_t = np.maximum(0.0, (1.0 - cfg.beta_dual) * lambda_t + gamma_t * g_t)
        elif cfg.duals == "mccrip_lp":
            mu = mccrip_lp_duals(delta_c, raw_dD - q_eff[:, :, None]) if not is_fast else np.zeros(m)
            lambda_t = (1.0 - cfg.kappa_lp) * lambda_t + cfg.kappa_lp * mu
        # quotas
        if cfg.quota == "dynamic" and L >= 2:
            unreal = np.maximum(0.0, delta_c[:, 1] - delta_c[:, L])
            unreal[sel == L] = 0.0
            excess = np.maximum(0.0, raw_dD[:, :, L] - q_eff)
            u_rk = np.where(excess > TOL, unreal[None, :] / np.maximum(excess, TOL), 0.0) + 1e-3
            alpha_t = (1 - cfg.omega_quota) * alpha_t + cfg.omega_quota * u_rk / u_rk.sum(axis=1, keepdims=True)

        tsync = time.perf_counter() - ts0
        cpu_t += float(np.sum(taus)) + tsync
        sim_t += float(np.max(taus)) + tsync
        t += 1
        trace_t.append(time.perf_counter() - wall0)
        trace_obj.append(obj_cur)
        trace_slack.append(float(np.mean(s_cur / d_pos)))
        trace_bottleneck.append(float(np.min(s_cur / d_pos)))

    if pool is not None:
        patterns = pool.finish(prev_sel)
    wall = time.perf_counter() - wall0
    obj = evaluate_global_cost(instance, patterns)
    assert abs(obj - obj_cur) <= 1e-6 * max(1.0, abs(obj)), (obj, obj_cur)
    assert np.allclose(compute_global_slack(instance, patterns), s_cur, atol=1e-6)
    feas, _ = verify_solution_feasibility(instance, patterns)
    gap = 100.0 * (obj - lower_bound) / max(1e-9, lower_bound)
    return EngineResult(
        method=cfg.name, config=asdict(cfg), instance_name=instance.name,
        best_obj=obj, initial_obj=initial_obj, lower_bound=lower_bound, gap_pct=max(0.0, gap),
        feasible=feas, wall_clock_s=wall, cpu_time_s=cpu_t, sim_parallel_s=sim_t,
        init_time_s=tau_init, pool_startup_s=pool_startup, workers_W=W, epochs_run=t,
        fast_path_epochs=fast, conflict_epochs=conflicts, accepted_moves=accepted,
        proposals=proposals,
        matcher_ms_mean=float(np.mean(matcher_ms)) if matcher_ms else float("nan"),
        matcher_fallbacks=fallbacks,
        primal_integral=primal_integral(trace_t, trace_obj, lower_bound, wall),
        trace_t=trace_t, trace_obj=trace_obj, trace_slack=trace_slack, trace_bottleneck=trace_bottleneck,
        cf_sum=cf_sum, cf_strict_wins=cf_wins,
        patterns=patterns.copy() if keep_patterns else None,
    )


# ---------------------------------------------------------------------------
# Method catalogue (mechanism names)
# ---------------------------------------------------------------------------
def method_configs(init_mode="booking", max_net=None, inner_iters=1, epochs=120,
                   duals="none", quota="static") -> Dict[str, EngineConfig]:
    base = dict(init_mode=init_mode, max_net=max_net, inner_iters=inner_iters, epochs=epochs)
    C = {}
    # single-proposal methods (L = 1: shared destroy + Regret-2 repair only)
    C["Opt-Rollback"] = EngineConfig("Opt-Rollback", L=1, commit="Opt-Rollback", proposal_cap="optimistic", **base)
    C["Opt-SeqLock"] = EngineConfig("Opt-SeqLock", L=1, commit="Opt-SeqLock", proposal_cap="optimistic", **base)
    C["Static-Quota"] = EngineConfig("Static-Quota", L=1, commit="Static-Quota", quota="static", **base)
    C["Demand-Quota"] = EngineConfig("Demand-Quota", L=1, commit="Static-Quota", quota="demand", **base)
    # four-level portfolio methods (L = 3: all four candidate generators)
    for rule in ("Greedy-Gain", "Greedy-Efficiency", "Opt-Rollback", "Opt-SeqLock"):
        C[f"{rule}-Portfolio"] = EngineConfig(f"{rule}-Portfolio", L=3, commit=rule, **base)
    C["BCRM-Greedy"] = EngineConfig("BCRM-Greedy", L=3, commit="BCRM-Greedy", duals=duals, quota=quota, **base)
    C["MC-CRIP"] = EngineConfig("MC-CRIP", L=3, commit="MC-CRIP", duals=duals, quota=quota, **base)
    return C
