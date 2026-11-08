"""
Automated Pytest Suite Verifying Mathematical Formulation, Feasibility Tolerance,
Proposition 1 (Collision-Free Parallel Sufficiency), and Theorem 1 (Strict
Feasibility and Monotonic Descent of PC-MALNS).
"""

import sys
from pathlib import Path
import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.instance_generator import generate_instance
from src.feasibility import (
    verify_solution_feasibility,
    compute_global_slack,
    compute_agent_global_usage,
    evaluate_global_cost,
    TOL,
)
from src.operators import destroy_operator, regret2_repair_hard_quota
from src.bcrm_solver import solve_mccrip_exact, solve_bcrm_greedy
from src.baselines import lp_round_start, rate_pct
from src.engine import run_engine, method_configs, EngineConfig


def test_instance_generation_and_initial_feasibility():
    """Verify instance synthesis rules and strict feasibility of starting solution x^{(0)}."""
    inst = generate_instance(K=4, N_per_agent=30, tightness=1.25, seed=101, scale="Small")
    assert inst.K == 4
    assert inst.N_per_agent == 30
    assert inst.N_total == 120
    # Verify Pattern p=0 has zero global and local resource consumption
    assert np.all(inst.D[:, :, :, 0] == 0.0)
    assert np.all(inst.A[:, :, :, 0] == 0.0)
    # Verify initial baseline solution x^{(0)} is strictly feasible within 1e-6
    feas, info = verify_solution_feasibility(inst, inst.initial_patterns, tol=TOL)
    assert feas, f"Initial solution infeasible: {info}"
    s0 = compute_global_slack(inst, inst.initial_patterns)
    assert np.all(s0 > 0.0), "Initial global slack s^{(0)} must be strictly positive"


def test_proposition_1_quota_safe_selection_is_feasible():
    """
    Proposition 1 (i)-(ii), quota cancellation identity (eq. cancellation):
    If x^{(t)} is globally feasible (s^{(t)} >= 0) and every agent k in K
    satisfies the local quota condition D_k(y_k^{(t,1)} - x_k^{(t)}) <= q_k^{(t)},
    where q_k^{(t)} = alpha_k^{(t)} o s^{(t)} and sum_{k=1}^K alpha_{r,k}^{(t)} = 1,
    then the merged state (y_1^{(t,1)}, ..., y_K^{(t,1)}) is strictly globally
    feasible (sum_{k=1}^K D_k y_k^{(t,1)} <= d) with zero thread rollbacks.
    """
    for seed in [101, 102, 103]:
        inst = generate_instance(K=8, N_per_agent=40, tightness=1.30, seed=seed, scale="Medium")
        rng = np.random.default_rng(seed)
        patterns = inst.initial_patterns.copy()

        for epoch in range(15):
            s_t = compute_global_slack(inst, patterns)
            assert np.all(s_t >= -TOL)

            # Generate random positive quota shares summing to 1 across agents for each row r
            raw_weights = rng.uniform(0.1, 2.0, size=(inst.m_global, inst.K))
            alpha_t = raw_weights / np.sum(raw_weights, axis=1, keepdims=True)
            assert np.allclose(np.sum(alpha_t, axis=1), 1.0, atol=1e-12)

            merged_y1 = np.zeros_like(patterns)
            for k in range(inst.K):
                q_k = alpha_t[:, k] * s_t
                partial_k, destroyed_idx = destroy_operator(inst, k, patterns[k], rng)
                y_k_1 = regret2_repair_hard_quota(
                    instance=inst,
                    k=k,
                    incumbent_k=patterns[k],
                    partial_k=partial_k,
                    destroyed_indices=destroyed_idx,
                    max_global_delta=q_k,
                )
                # Verify local quota condition D_k(y_k^{(t,1)} - x_k^{(t)}) <= q_k^{(t)}
                delta_usage = (
                    compute_agent_global_usage(inst, k, y_k_1)
                    - compute_agent_global_usage(inst, k, patterns[k])
                )
                assert np.all(delta_usage <= q_k + TOL), "Local quota condition violated"
                merged_y1[k] = y_k_1

            # Verify merged state (y_1^{(t,1)}, ..., y_K^{(t,1)}) is strictly globally feasible
            feas, info = verify_solution_feasibility(inst, merged_y1, tol=TOL)
            assert feas, f"Proposition 1 violated at epoch {epoch}: {info}"
            patterns = merged_y1




def test_bcrm_and_mccrip_dominance_over_quota_safe():
    """
    Verify directly on synthetic and real portfolio tensors that both MC-CRIP and
    BCRM-Greedy are always feasible and achieve objective delta <= sum_k Delta c_{k,1}^{(t)} <= 0.
    """
    inst = generate_instance(K=8, N_per_agent=40, tightness=1.30, seed=102, scale="Medium")
    rng = np.random.default_rng(102)
    K = inst.K
    m = inst.m_global
    L = 3

    # Construct a realistic portfolio with quota-safe l=1 and aggressive borrowers l=2,3
    delta_c = np.zeros((K, L + 1))
    delta_slack = np.zeros((m, K, L + 1))

    for k in range(K):
        q_k = np.full(m, 2.5)
        delta_c[k, 0] = 0.0
        delta_slack[:, k, 0] = -q_k

        # Quota-safe l=1 leaves some surplus slack on each constraint
        delta_c[k, 1] = -rng.uniform(5.0, 20.0)
        delta_slack[:, k, 1] = -rng.uniform(0.5, 1.8, size=m)

        # Aggressive l=2, 3 reduce cost further while borrowing slack
        delta_c[k, 2] = delta_c[k, 1] - rng.uniform(10.0, 35.0)
        delta_slack[:, k, 2] = delta_slack[:, k, 1] + rng.uniform(0.2, 2.2, size=m)

        delta_c[k, 3] = delta_c[k, 2] - rng.uniform(10.0, 40.0)
        delta_slack[:, k, 3] = delta_slack[:, k, 2] + rng.uniform(0.5, 2.5, size=m)

    sel_exact, ms_exact = solve_mccrip_exact(delta_c, delta_slack)
    sel_greedy, ms_greedy = solve_bcrm_greedy(
        delta_c, delta_slack, dual_prices=np.ones(m), rho_t=5.0
    )

    quota_safe_obj = float(np.sum(delta_c[:, 1]))
    exact_obj = float(np.sum(delta_c[np.arange(K), sel_exact]))
    greedy_obj = float(np.sum(delta_c[np.arange(K), sel_greedy]))

    # Feasibility check: sum_k delta_{r, k, l_k^*} <= 0
    assert np.all(np.sum(delta_slack[:, np.arange(K), sel_exact], axis=1) <= TOL)
    assert np.all(np.sum(delta_slack[:, np.arange(K), sel_greedy], axis=1) <= TOL)

    # Monotonic descent dominance: exact_obj <= greedy_obj <= quota_safe_obj <= 0
    assert exact_obj <= greedy_obj + TOL
    assert greedy_obj <= quota_safe_obj + TOL
    assert quota_safe_obj <= 0.0






def test_mccrip_dominates_sequential_lock_and_static_quota():
    """
    Proposition 1 (per-epoch dominance): if every portfolio contains the incumbent,
    the static-quota repair and the optimistic repair, then for every arrival
    permutation the Opt-SeqLock selection and the Static-Quota selection are feasible for
    MC-CRIP, so the MC-CRIP cost delta is no larger.
    """
    rng = np.random.default_rng(7)
    for _ in range(200):
        K, m = 6, 4
        s = rng.uniform(1.0, 4.0, size=m)
        q = s[:, None] / K * np.ones((m, K))                       # uniform quota
        # level 0: incumbent, level 1: static-quota repair, level 2: optimistic repair
        dD = np.zeros((m, K, 3)); dc = np.zeros((K, 3))
        dD[:, :, 1] = rng.uniform(-0.5, 1.0, size=(m, K)) * q
        dc[:, 1] = -rng.uniform(0, 5, size=K)
        dD[:, :, 2] = rng.uniform(-0.5, 1.0, size=(m, K)) * s[:, None]
        dc[:, 2] = -rng.uniform(0, 15, size=K)
        delta_slack = dD - q[:, :, None]
        sel, _ = solve_mccrip_exact(dc, delta_slack)
        best = float(dc[np.arange(K), sel].sum())
        assert np.all(delta_slack[:, np.arange(K), sel].sum(axis=1) <= TOL)
        assert best <= float(dc[:, 1].sum()) + TOL                 # Static-Quota selection
        for _p in range(5):                                        # Opt-SeqLock selections
            s_rem, z = s.copy(), np.zeros(K, dtype=int)
            for k in rng.permutation(K):
                if dc[k, 2] < 0 and np.all(dD[:, k, 2] <= s_rem + TOL):
                    z[k] = 2
                    s_rem -= dD[:, k, 2]
            assert best <= float(dc[np.arange(K), z].sum()) + TOL






def test_mccrip_enumeration_and_highs_paths_agree():
    """Above MAX_ENUM_STATES the HiGHS path returns the same optimum as full enumeration."""
    import src.bcrm_solver as bs
    rng = np.random.default_rng(11)
    for _ in range(20):
        K, m, L1 = 7, 4, 4                       # 4^7 = 16,384 > 4,096 combinations
        dc = np.concatenate([np.zeros((K, 1)), -rng.uniform(0, 10, size=(K, L1 - 1))], axis=1)
        ds = np.concatenate([-rng.uniform(0.2, 1.0, size=(m, K, 1)),
                             rng.uniform(-1.0, 1.5, size=(m, K, L1 - 1))], axis=2)
        sel_h, _ = bs.solve_mccrip_exact(dc, ds)
        old = bs.MAX_ENUM_STATES
        bs.MAX_ENUM_STATES = 10 ** 6
        try:
            sel_e, _ = bs.solve_mccrip_exact(dc, ds)
        finally:
            bs.MAX_ENUM_STATES = old
        assert np.all(ds[:, np.arange(K), sel_h].sum(axis=1) <= TOL)
        assert abs(dc[np.arange(K), sel_h].sum() - dc[np.arange(K), sel_e].sum()) <= 1e-6


def test_portfolio_contains_baseline_proposals():
    """
    Proposition 1 holds literally: for the same incumbent, seed and epoch, level 3 of
    the PC-MALNS portfolio is exactly the Opt-Rollback / Opt-SeqLock proposal (cap s^{(t)}),
    level 1 with alpha = 1/K is exactly the Static-Quota proposal (cap s^{(t)}/K), and level 0
    is the incumbent or dominates it.
    """
    from src.worker import worker_step
    inst = generate_instance(K=6, N_per_agent=30, tightness=1.30, seed=105, scale="Small")
    x = inst.initial_patterns
    s = compute_global_slack(inst, x)
    lam = np.linspace(1.0, 4.0, inst.m_global)
    for t in range(5):
        for k in range(inst.K):
            port, dc, dD, _ = worker_step(inst, k, x[k], s, s / inst.K, 105, t, 3, lam, 0.35)
            opt, _, _, _ = worker_step(inst, k, x[k], s, s, 105, t, 1, None, 0.0)
            sq, _, _, _ = worker_step(inst, k, x[k], s, s / inst.K, 105, t, 1, None, 0.0)
            assert np.array_equal(port[3], opt[1])
            assert np.array_equal(port[1], sq[1])
            assert dc[0] <= TOL and np.all(dD[:, 0] <= TOL)




def test_portfolio_contains_baseline_proposals_pc_malns_configuration():
    """Same statement for the PC-MALNS configuration (M = 5 chained steps, no cap):
    level 3 equals the single optimistic proposal (cap s^{(t)}) of Opt-Rollback /
    Opt-SeqLock and level 1 equals the Static-Quota proposal (cap s^{(t)}/K)."""
    from src.worker import worker_step
    inst = generate_instance(K=6, N_per_agent=30, tightness=1.30, seed=106, scale="Small")
    x = inst.initial_patterns
    s = compute_global_slack(inst, x)
    for t in range(3):
        for k in range(inst.K):
            port, dc, dD, _ = worker_step(inst, k, x[k], s, s / inst.K, 106, t, 3, None, 0.35, 0, None, 5)
            opt, _, _, _ = worker_step(inst, k, x[k], s, s, 106, t, 1, None, 0.0, 0, None, 5)
            sq, _, _, _ = worker_step(inst, k, x[k], s, s / inst.K, 106, t, 1, None, 0.0, 0, None, 5)
            assert np.array_equal(port[3], opt[1])
            assert np.array_equal(port[1], sq[1])
            assert dc[0] <= TOL and np.all(dD[:, 0] <= TOL)


def _all_engine_configs():
    cfgs = list(method_configs(init_mode="lp_round", max_net=None, inner_iters=5, epochs=12).values())
    for duals, quota in (("heuristic", "dynamic"), ("mccrip_lp", "static"), ("none", "demand")):
        cfgs.append(EngineConfig(f"MC-CRIP[{duals},{quota}]", L=3, commit="MC-CRIP", duals=duals, quota=quota,
                                 init_mode="lp_round", inner_iters=5, epochs=12))
    return cfgs


def test_proposition_1_global_feasibility_and_monotone_descent_all_methods():
    """Proposition 1 (i)-(iii) on real runs: every method of the study (and the price /
    quota variants) keeps every epoch feasible (asserted inside run_engine), never
    increases the objective and ends at a verified feasible solution."""
    inst = generate_instance(K=8, N_per_agent=40, tightness=1.25, seed=101, scale="Medium")
    for cfg in _all_engine_configs():
        r = run_engine(inst, cfg, 1.0, seed=101, keep_patterns=True)
        assert r.feasible and verify_solution_feasibility(inst, r.patterns, tol=TOL)[0], cfg.name
        assert np.all(np.diff(r.trace_obj) <= TOL), cfg.name
        assert np.all(np.array(r.trace_bottleneck) >= -TOL), cfg.name
        assert r.best_obj < r.initial_obj, cfg.name


def test_all_lns_methods_start_from_lp_round_and_charge_it():
    inst = generate_instance(K=4, N_per_agent=30, tightness=1.25, seed=104, scale="Small")
    lp_obj = evaluate_global_cost(inst, lp_round_start(inst)[0])
    for cfg in method_configs(init_mode="lp_round", max_net=None, inner_iters=5, epochs=10).values():
        r = run_engine(inst, cfg, 1.0, seed=104)
        assert abs(r.initial_obj - lp_obj) <= TOL, cfg.name
        assert r.best_obj <= lp_obj + TOL, cfg.name
        assert r.init_time_s > 0.0 and r.cpu_time_s >= r.init_time_s and r.wall_clock_s >= r.init_time_s


def test_rate_pct_undefined_without_proposals():
    assert np.isnan(rate_pct(0, 0))
    assert rate_pct(3, 4) == 75.0


def test_budgets_and_independent_replicates():
    """A CPU budget is respected; rep = 0 is reproducible and rep = 1 gives a different,
    reproducible run."""
    inst = generate_instance(K=4, N_per_agent=30, tightness=1.25, seed=106, scale="Small")
    cfg = method_configs(init_mode="lp_round", max_net=None, inner_iters=5)["MC-CRIP"]
    cfg.time_budget_s, cfg.budget_clock = 0.3, "cpu"
    r = run_engine(inst, cfg, 1.0, seed=106)
    assert r.cpu_time_s >= 0.3 and r.epochs_run >= 1
    cfg.time_budget_s, cfg.epochs = None, 15
    a0, a0b = run_engine(inst, cfg, 1.0, seed=106), run_engine(inst, cfg, 1.0, seed=106)
    a1, a1b = run_engine(inst, cfg, 1.0, seed=106, rep=1), run_engine(inst, cfg, 1.0, seed=106, rep=1)
    assert a0.trace_obj == a0b.trace_obj and a1.trace_obj == a1b.trace_obj
    assert a0.trace_obj != a1.trace_obj


def test_agent_pool_reproduces_serial_trajectory():
    """The multi-process pool exchanges only per-level cost and usage changes and gives
    the same trajectory as serial execution."""
    from src.agent_pool import AgentPool
    inst = generate_instance(K=8, N_per_agent=40, tightness=1.25, seed=107, scale="Medium")
    cfg = method_configs(init_mode="lp_round", max_net=None, inner_iters=5, epochs=8)["MC-CRIP"]
    serial = run_engine(inst, cfg, 1.0, seed=107, keep_patterns=True)
    pool = AgentPool(3)
    try:
        par = run_engine(inst, cfg, 1.0, seed=107, pool=pool, keep_patterns=True)
    finally:
        pool.close()
    assert np.array_equal(serial.patterns, par.patterns)
    assert np.allclose(serial.trace_obj, par.trace_obj)

