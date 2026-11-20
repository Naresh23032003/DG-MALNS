"""Structure tests for the MCA-SC-Pair generator and the MMKP conversion."""

import numpy as np
import pytest

from src.instance_generator import generate_instance
from src.sync_instances import generate_sync_instance
from src.mmkp import NAMES, read_mmkp, read_certificate, to_instance, mmkp_profit
from src.feasibility import verify_solution_feasibility, evaluate_global_cost
from src.baselines import lp_round_start


@pytest.mark.parametrize("seed", [1, 2])
def test_sync_instance_structure(seed):
    K, N = 8, 40
    base = generate_instance(K, N, seed=seed)
    s = generate_sync_instance(K, N, seed=seed)
    m_hub = base.m_global
    assert s.m_global == m_hub + K // 2
    assert np.all(s.D >= 0) and np.all(s.D[:, :, :, 0] == 0)
    for k in range(K):
        others = [j for j in range(K // 2) if j != k // 2]
        # an agent only uses its own pair's dock, in integer slot blocks of 1, 2 or 3
        assert np.all(s.D[k, m_hub + np.array(others)] == 0)
        dock = s.D[k, m_hub + k // 2]
        assert set(np.unique(dock)) <= {0.0, 1.0, 2.0, 3.0}
        assert np.all(dock[:, : s.P - 1] == 0)
    # regular patterns of requests without a paired pattern are unchanged
    no_tr = s.D[:, m_hub:, :, -1].sum(axis=1) == 0
    assert np.allclose(s.c[no_tr], base.c[no_tr])
    assert np.all(s.d[m_hub:] == np.floor(s.d[m_hub:])) and np.all(s.d[m_hub:] >= 1)
    pats, _, _ = lp_round_start(s)
    assert verify_solution_feasibility(s, pats)[0]


@pytest.mark.parametrize("name", ["I07", "INST01", "INST20"])
def test_mmkp_conversion_reproduces_certificate(name):
    raw = read_mmkp(name)
    bkv, items = read_certificate(name, raw)
    inst = to_instance(raw, 8)
    pats = np.zeros((inst.K, inst.N_per_agent), dtype=np.int64)
    flat = pats.reshape(-1)
    flat[: raw["n"]] = items + 1
    assert verify_solution_feasibility(inst, pats)[0]
    profit, ok = mmkp_profit(inst, pats)
    assert ok and profit == pytest.approx(bkv)
    assert evaluate_global_cost(inst, pats) == pytest.approx(raw["n"] * inst.mmkp_pmax - bkv)


def test_mmkp_all_names_present():
    assert len(NAMES) == 27


def test_cf_all_logging_leaves_search_unchanged():
    """The all-epoch counterfactual diagnostic must not change the trajectory of any barrier."""
    from src.instance_generator import generate_instance
    from src.engine import run_engine, method_configs
    inst = generate_instance(4, 30, P=6, tightness=1.25, seed=7, scale="Small")
    for nm in ("PC-MALNS [Greedy-Efficiency]", "PC-MALNS [MC-CRIP]"):
        res = []
        for flag in (False, True):
            cfg = method_configs(init_mode="lp_round", max_net=None, inner_iters=5)[nm]
            cfg.work_budget, cfg.time_budget_s, cfg.cf_all = 25 * 12, None, flag
            res.append(run_engine(inst, cfg, 1.0, seed=7, rep=0))
        assert res[0].best_obj == res[1].best_obj and res[0].epochs_run == res[1].epochs_run, nm
        assert res[0].trace_obj == res[1].trace_obj, nm
        if res[1].fast_path_epochs:
            assert "cheapest" in res[1].nc_sum
            assert res[1].nc_deviate.get("MC-CRIP", 0) == 0   # the exact barrier commits the cheapest levels


def test_seq_commit_is_deterministic_and_feasible():
    """Seq-Commit (sequential baseline): feasible, no conflict epochs, same epochs as the
    single-proposal methods under the same work budget, and repeatable bit for bit."""
    from src.instance_generator import generate_instance
    from src.engine import method_configs, run_engine
    inst = generate_instance(4, 30, P=6, tightness=1.25, seed=7, scale="Small")
    C = method_configs(init_mode="lp_round", max_net=None, inner_iters=2)
    a = C["Seq-Commit"]
    b = C["Opt-SeqLock"]
    a.work_budget = b.work_budget = 4 * 20
    r1 = run_engine(inst, a, 1.0, seed=7, rep=1)
    r2 = run_engine(inst, a, 1.0, seed=7, rep=1)
    r3 = run_engine(inst, b, 1.0, seed=7, rep=1)
    assert r1.feasible and r1.conflict_epochs == 0
    assert r1.best_obj == r2.best_obj and r1.epochs_run == r3.epochs_run
    assert r1.best_obj <= r1.initial_obj
