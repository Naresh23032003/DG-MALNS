"""
Standard MMKP benchmark instances as RPA-SH instances (m_local = 0).

Source: classical instances I07-I13 (Khan et al., 2002) and INST01-INST20
(Hifi et al., 2004/2006), as distributed by Chen & Hao (2014),
https://leria-info.univ-angers.fr/~jinkao.hao/mmkp.html (ClassicINST.zip), with the
best known values (BKV) of the solution certificates linked on that page.

File format: "n l m", the m capacities, then for every group g its index followed by
l lines "profit w_1 ... w_m". MMKP: choose exactly one item per group, maximize total
profit subject to sum of weights <= capacity on every resource.

Mapping to RPA-SH (minimization, every request needs a zero-usage pattern p = 0):
  - groups -> requests, distributed over K agents in contiguous blocks; the last agent
    is padded with dummy requests (all patterns cost 0, use 0) so that every agent has
    N_per_agent = ceil(n / K) requests;
  - item j of group g -> pattern p = j + 1 with cost c = p_max - profit and usage D = w;
  - pattern p = 0 ("no item", D = 0) has the penalty cost
        PEN = n * (p_max - p_min) + p_max + 1,
    larger than any total profit difference, so any solution with a p = 0 request is
    worse than every feasible MMKP solution; a final solution that still has a p = 0
    request is reported as MMKP-infeasible.
  MMKP profit of a solution without p = 0 = n * p_max - cost.
"""

from pathlib import Path
from typing import Dict, Tuple

import numpy as np

from src.instance_generator import CoupledRoutingInstance

DATA = Path(__file__).resolve().parent.parent / "data" / "mmkp"
NAMES = [f"I{j:02d}" for j in range(7, 14)] + [f"INST{j:02d}" for j in range(1, 21)]


def read_mmkp(name: str) -> Dict:
    toks = (DATA / "ClassicINST" / f"{name}.txt").read_text().split()
    pos = 0

    def nxt():
        nonlocal pos
        pos += 1
        return toks[pos - 1]

    n, l, m = int(nxt()), int(nxt()), int(nxt())
    cap = np.array([float(nxt()) for _ in range(m)])
    profit = np.zeros((n, l))
    w = np.zeros((n, l, m))
    for g in range(n):
        nxt()  # group index
        for j in range(l):
            profit[g, j] = float(nxt())
            w[g, j] = [float(nxt()) for _ in range(m)]
    # trailing reference solutions / bounds of some files (e.g. "Solutions by HEU") are ignored
    return dict(name=name, n=n, l=l, m=m, cap=cap, profit=profit, w=w)


def read_certificate(name: str, raw: Dict) -> Tuple[float, np.ndarray]:
    """Best known value and its item choice; verifies profit and feasibility."""
    lines = (DATA / "certificates" / f"{name}result.txt").read_text().split("\n")
    bkv = float(lines[0].strip())
    idx = np.array([int(v) for v in " ".join(lines[1:]).split()], dtype=np.int64)
    g = idx // raw["l"]
    j = idx % raw["l"]
    assert np.array_equal(g, np.arange(raw["n"])), name
    prof = float(raw["profit"][g, j].sum())
    use = raw["w"][g, j].sum(axis=0)
    assert abs(prof - bkv) < 1e-6, (name, prof, bkv)
    assert np.all(use <= raw["cap"] + 1e-9), name
    return bkv, j


def to_instance(raw: Dict, K: int) -> CoupledRoutingInstance:
    n, l, m = raw["n"], raw["l"], raw["m"]
    N = -(-n // K)
    P = l + 1
    pmax, pmin = float(raw["profit"].max()), float(raw["profit"].min())
    pen = n * (pmax - pmin) + pmax + 1.0
    c = np.zeros((K, N, P))
    D = np.zeros((K, m, N, P))
    for g in range(n):
        k, i = divmod(g, N)
        c[k, i, 0] = pen
        c[k, i, 1:] = pmax - raw["profit"][g]
        D[k, :, i, 1:] = raw["w"][g].T
    inst = CoupledRoutingInstance(
        name=f"MMKP_{raw['name']}_K{K}", scale="MMKP", K=K, N_per_agent=N, N_total=K * N, P=P,
        m_global=m, m_local=0, tightness=float("nan"), seed=0, c=c, D=D,
        A=np.zeros((K, 0, N, P)), d=raw["cap"].copy(), b=np.zeros((K, 0)),
        initial_patterns=np.zeros((K, N), dtype=np.int64))
    inst.mmkp_n = n
    inst.mmkp_pmax = pmax
    inst.mmkp_pen = pen
    return inst


def mmkp_profit(inst: CoupledRoutingInstance, patterns: np.ndarray) -> Tuple[float, bool]:
    """(MMKP profit, MMKP-feasible) of an RPA-SH solution of a converted instance."""
    n, N = inst.mmkp_n, inst.N_per_agent
    flat = patterns.reshape(-1)[:n]
    if np.any(flat == 0):
        return float("nan"), False
    k_idx, i_idx = np.divmod(np.arange(n), N)
    cost = float(inst.c[k_idx, i_idx, flat].sum())
    return n * inst.mmkp_pmax - cost, True


def mmkp_feasibility_repair(inst: CoupledRoutingInstance, patterns: np.ndarray) -> np.ndarray:
    """Start for MMKP instances (every group must receive an item; p = 0 only marks an
    unassigned group). Classic two-phase MMKP construction (Khan et al., 2002, HEU
    phases 1-2): every group takes its item with the smallest normalized weight
    sum_r w_r / cap_r; then the feasible single-group item change with the largest
    profit gain per unit of added normalized weight (any gain if no weight is added) is
    applied until none improves. Returns the cheaper of this construction and the given
    solution (LP-Round) when the latter assigns every group. Deterministic; used
    identically as the start of every LNS method on MMKP instances."""
    n, N = inst.mmkp_n, inst.N_per_agent
    cap = inst.d
    D = inst.D.transpose(0, 2, 3, 1).reshape(inst.K * N, inst.P, inst.m_global)[:n]   # (n, P, m)
    c = inst.c.reshape(inst.K * N, inst.P)[:n]
    cur = 1 + np.argmin((D[:, 1:] / cap).sum(axis=2), axis=1)
    use = D[np.arange(n), cur].sum(axis=0)
    if np.any(use > cap + 1e-9):
        return patterns.copy()                       # no lightest-item start; keep LP-Round
    for _ in range(50 * n):
        dw = D[:, 1:, :] - D[np.arange(n), cur][:, None, :]
        dc = c[:, 1:] - c[np.arange(n), cur][:, None]
        ok = (dc < -1e-9) & np.all(use + dw <= cap + 1e-9, axis=2)
        if not np.any(ok):
            break
        extra = (np.maximum(dw, 0.0) / cap).sum(axis=2)
        score = np.where(ok, -dc / (extra + 1e-6), -np.inf)
        h, j = np.unravel_index(int(np.argmax(score)), score.shape)
        use += dw[h, j]
        cur[h] = j + 1
    heu = patterns.copy()
    heu.reshape(-1)[:n] = cur
    given_ok = not np.any(patterns.reshape(-1)[:n] == 0)
    if given_ok and float(np.sum(c[np.arange(n), patterns.reshape(-1)[:n]])) <= float(np.sum(c[np.arange(n), cur])):
        return patterns.copy()
    return heu
