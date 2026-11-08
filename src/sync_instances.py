"""
RPA-SH-Sync: RPA-SH with inter-depot transfers between paired agents.

Design (fixed before any experiment was run on these instances; not tuned afterwards):

  Agents are paired (k, k^) with k^ = k xor 1 (K even); pair j = k // 2 shares one
  transfer dock (a cross-dock between the two depots) with an integer number of
  wave slots. Starting from the base RPA-SH instance with the same (K, N, P, eta,
  seed), a fraction TRANSFER_FRAC of the requests of every agent receives an
  inter-depot transfer pattern, which replaces its last regular pattern p = P - 1:

    cost     c = round(c_0 * gamma_T, 2), gamma_T ~ U(0.18, 0.32): the shipment is
             consolidated with the partner depot's flow, cheaper than the agent's
             own consolidated patterns;
    hubs     outbound wave at a hub r1 of agent k and inbound wave at a hub r2 of the
             partner k^ (r1, r2 drawn by the hub-usage profiles of k and k^, r2 != r1),
             each with usage U(1.0, 3.5) * 1.8 (rounded to 2 decimals);
    dock     a lumpy block of B in {1, 2, 3} slots (prob. 0.5 / 0.3 / 0.2: partial,
             half and full trailer) on the pair's dock row m + j; agents k and k^
             compete for the same integer slots;
    local    the local wave usage A of the replaced pattern is kept.

  Capacities use the base formulas on the new cheapest patterns: hubs
  d_r = max(8, round(U_r / eta, 2)), local waves b = max(4, round(0.82 U_local, 2)),
  and every dock gets max(1, floor(U_T,j / SLOT_TIGHTNESS)) slots, U_T,j being the
  slot demand of the pair's cheapest patterns (about half of the transfers fit).

  m_global = m_hub + K / 2 coupling rows. All usages are non-negative, so p = 0 is
  still feasible and the model is a standard RPA-SH instance; every method runs on
  it unchanged.
"""

import numpy as np

from src.instance_generator import generate_instance, CoupledRoutingInstance

TRANSFER_FRAC = 0.30
SLOT_TIGHTNESS = 2.0
GAMMA_T = (0.18, 0.32)
BLOCKS = np.array([1.0, 2.0, 3.0])
BLOCK_P = np.array([0.5, 0.3, 0.2])


def generate_sync_instance(K: int, N_per_agent: int, P: int = 6, tightness: float = 1.25,
                           seed: int = 101, scale: str = "Custom") -> CoupledRoutingInstance:
    assert K % 2 == 0, "RPA-SH-Sync pairs the agents: K must be even"
    base = generate_instance(K, N_per_agent, P=P, tightness=tightness, seed=seed, scale=scale)
    rng = np.random.default_rng([int(seed), 5150])
    m_hub, N = base.m_global, N_per_agent
    m = m_hub + K // 2
    c = base.c.copy()
    D = np.zeros((K, m, N, P))
    D[:, :m_hub] = base.D
    A = base.A.copy()

    # hub-usage profile of every agent (its regular consolidated patterns)
    prof = base.D[:, :, :, 1:].sum(axis=(2, 3)) + 1e-9
    prof = prof / prof.sum(axis=1, keepdims=True)
    for k in range(K):
        kp, j = k ^ 1, k // 2
        for i in range(N):
            if rng.random() >= TRANSFER_FRAC:
                continue
            p = P - 1
            c[k, i, p] = np.round(c[k, i, 0] * rng.uniform(*GAMMA_T), 2)
            D[k, :, i, p] = 0.0
            r1 = rng.choice(m_hub, p=prof[k])
            w2 = prof[kp].copy()
            w2[r1] = 0.0
            r2 = rng.choice(m_hub, p=w2 / w2.sum())
            D[k, r1, i, p] = np.round(rng.uniform(1.0, 3.5) * 1.8, 2)
            D[k, r2, i, p] = np.round(rng.uniform(1.0, 3.5) * 1.8, 2)
            D[k, m_hub + j, i, p] = rng.choice(BLOCKS, p=BLOCK_P)

    p_star = np.argmin(c, axis=2)
    kg, ig = np.arange(K)[:, None], np.arange(N)[None, :]
    U = np.transpose(D, (0, 2, 3, 1))[kg, ig, p_star].sum(axis=(0, 1))
    U_loc = np.transpose(A, (0, 2, 3, 1))[kg, ig, p_star].sum(axis=1)
    d = np.empty(m)
    d[:m_hub] = np.maximum(8.0, np.round(U[:m_hub] / tightness, 2))
    d[m_hub:] = np.maximum(1.0, np.floor(U[m_hub:] / SLOT_TIGHTNESS))
    b = np.maximum(4.0, np.round(0.82 * U_loc, 2))

    inst = CoupledRoutingInstance(
        name=f"RPA_SH_SYNC_K{K}_N{K * N}_P{P}_eta{tightness:.2f}_s{seed}", scale=scale, K=K,
        N_per_agent=N, N_total=K * N, P=P, m_global=m, m_local=base.m_local, tightness=tightness,
        seed=seed, c=c, D=D, A=A, d=d, b=b, initial_patterns=np.zeros((K, N), dtype=np.int64),
        high_utility=base.high_utility)
    inst.m_hub = m_hub
    return inst
