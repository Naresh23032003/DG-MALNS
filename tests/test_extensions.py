"""Structure tests for the RPA-SH-Sync generator and the MMKP conversion."""

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
    # regular patterns of requests without a transfer are unchanged
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
