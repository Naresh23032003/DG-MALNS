"""Tests of the revision-3 additions: work budget, portfolio-level ablation, restarts and
the asynchronous lock baseline."""

import numpy as np
import pytest

from src.instance_generator import generate_instance
from src.engine import run_engine, method_configs
from src.worker import worker_step, repair_passes_per_epoch, perturb_agent
from src.baselines import lp_round_start
from src.feasibility import (verify_solution_feasibility, evaluate_global_cost, compute_global_slack,
                             compute_agent_global_usage)


def _inst():
    return generate_instance(4, 30, P=6, tightness=1.25, seed=7, scale="Small")


def test_repair_pass_accounting():
    assert repair_passes_per_epoch(3, 5) == 25
    assert repair_passes_per_epoch(1, 5) == 10
    assert repair_passes_per_epoch(3, 5, (1, 3)) == 20
    assert repair_passes_per_epoch(3, 5, (0, 1, 3)) == 20
    assert repair_passes_per_epoch(3, 5, (1, 2, 3)) == 25


@pytest.mark.parametrize("key,epochs", [("PC-MALNS [Greedy-Efficiency]", 8), ("PC-MALNS [MC-CRIP]", 8),
                                        ("Opt-Rollback", 20), ("Static-Quota", 20)])
def test_work_budget_is_deterministic_and_counts_passes(key, epochs):
    inst = _inst()
    out = []
    for _ in range(2):
        cfg = method_configs(init_mode="lp_round", inner_iters=5)[key]
        cfg.work_budget, cfg.time_budget_s = 200, None
        r = run_engine(inst, cfg, 1.0, seed=7, rep=1)
        assert r.feasible
        out.append((r.best_obj, r.epochs_run, r.repair_passes))
    assert out[0] == out[1]
    assert out[0][1] == epochs and out[0][2] <= 200


def test_disabled_levels_are_the_incumbent():
    inst = _inst()
    x, _, _ = lp_round_start(inst)
    s = compute_global_slack(inst, x)
    for k in range(inst.K):
        q = s / inst.K
        full = worker_step(inst, k, x[k], s, q, 7, 0, 3, None, 0.35, 0, None, 5)
        part = worker_step(inst, k, x[k], s, q, 7, 0, 3, None, 0.35, 0, None, 5, (1, 3))
        # levels 1 and 3 identical (same random state), levels 0 and 2 equal the incumbent
        assert np.array_equal(full[0][1], part[0][1]) and np.array_equal(full[0][3], part[0][3])
        assert np.array_equal(part[0][0], x[k]) and np.array_equal(part[0][2], x[k])
        assert part[1][0] == 0 and part[1][2] == 0 and np.all(part[2][:, [0, 2]] == 0)


def test_restart_kick_is_feasible_and_run_returns_best():
    inst = _inst()
    x, _, _ = lp_round_start(inst)
    rng = np.random.default_rng(3)
    for k in range(inst.K):
        y = perturb_agent(inst, k, x[k], rng)
        assert np.all(compute_agent_global_usage(inst, k, y) <= compute_agent_global_usage(inst, k, x[k]) + 1e-9)
    cfg = method_configs(init_mode="lp_round", inner_iters=5)["PC-MALNS [Greedy-Efficiency]"]
    cfg.work_budget, cfg.restart_stall = 25 * 30, 3
    r = run_engine(inst, cfg, 1.0, seed=7, rep=0, keep_patterns=True)
    assert r.feasible and r.restarts > 0
    assert abs(evaluate_global_cost(inst, r.patterns) - r.best_obj) < 1e-6
    assert r.best_obj <= min(r.trace_obj) + 1e-6


def test_async_lock_is_feasible():
    from src.async_lock import AsyncPool
    inst = _inst()
    ap = AsyncPool(2)
    try:
        r = ap.run(inst, 0.3, seed=7, rep=0)
    finally:
        ap.close()
    assert r.feasible and r.best_obj <= r.initial_obj + 1e-9
    assert r.accepted_moves + r.rejected_fit == r.proposals
