"""
Block-Angular Coupled Multi-Depot Pickup and Delivery / Routing Problem
with Shared Hubs (RPA-SH) Instance Generator.

Implements parametric instance synthesis rules and initial baseline solution
construction as specified in Section 3 and Section 4 of the mathematical specification.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np

# Hub utilization targeted by the uncoordinated initial booking x^{(0)}
INITIAL_HUB_UTILIZATION = 0.92


@dataclass
class CoupledRoutingInstance:
    """
    Represents a block-angular coupled combinatorial optimization instance
    across K concurrent agents (depots/subgraphs).

    Attributes:
        name: Instance identifier string.
        scale: Scale label ('Small', 'Medium', 'Large', 'X-Large').
        K: Number of concurrent agents (depots).
        N_per_agent: Number of customer requests per agent.
        N_total: Total number of customer requests (K * N_per_agent).
        P: Number of candidate route-schedule patterns per request.
        m_global: Number of global coupling constraints (shared transfer hubs).
        m_local: Number of local depot wave capacity constraints per agent.
        tightness: Coupling tightness ratio eta_tight.
        seed: Random number generator seed.
        c: Cost array of shape (K, N_per_agent, P).
        D: Global resource consumption array of shape (K, m_global, N_per_agent, P).
        A: Local wave consumption array of shape (K, m_local, N_per_agent, P).
        d: Global coupling capacity vector of shape (m_global,).
        b: Local depot wave capacity matrix of shape (K, m_local).
        initial_patterns: Starting feasible pattern assignment of shape (K, N_per_agent)
                          with integer entries in {0, ..., P-1}.
    """
    name: str
    scale: str
    K: int
    N_per_agent: int
    N_total: int
    P: int
    m_global: int
    m_local: int
    tightness: float
    seed: int
    c: np.ndarray
    D: np.ndarray
    A: np.ndarray
    d: np.ndarray
    b: np.ndarray
    initial_patterns: np.ndarray
    high_utility: Optional[np.ndarray] = None

    def patterns_to_binary(self, patterns: np.ndarray) -> np.ndarray:
        """
        Convert integer pattern assignment (K, N_per_agent) to binary decision
        tensor x of shape (K, N_per_agent, P).
        """
        x = np.zeros((self.K, self.N_per_agent, self.P), dtype=np.float64)
        k_idx = np.arange(self.K)[:, None]
        i_idx = np.arange(self.N_per_agent)[None, :]
        x[k_idx, i_idx, patterns] = 1.0
        return x

    def binary_to_patterns(self, x: np.ndarray) -> np.ndarray:
        """
        Convert binary decision tensor x of shape (K, N_per_agent, P) to
        integer pattern indices of shape (K, N_per_agent).
        """
        return np.argmax(x, axis=-1).astype(np.int64)


def generate_instance(
    K: int,
    N_per_agent: int,
    P: int = 6,
    m_global: int = 8,
    m_local: int = 4,
    tightness: float = 1.25,
    seed: int = 101,
    scale: str = "Custom",
) -> CoupledRoutingInstance:
    """
    Synthesize a parametric block-angular RPA-SH instance using a seeded
    NumPy generator (np.random.default_rng(seed)) following Section 3.2:

    1. Pattern p = 0 (Uncoupled Fallback Dispatch):
       For each (k, i), draw standalone cost c_{k,i,0} ~ Uniform(85.0, 140.0).
       Set D_{k,r,i,0} = 0 for all r and A_{k,w,i,0} = 0 for all w.
    2. Patterns p in {1, ..., P-1} (Consolidated Shared-Hub Routes):
       - Regional depot heterogeneity: a seeded random half of the depots
         (ceil(K/2)) are high-utility depots with gamma_{k,i,p} ~ Uniform(0.28, 0.52);
         the remaining depots are low-utility depots with
         gamma_{k,i,p} ~ Uniform(0.62, 0.85). Set c_{k,i,p} = round(c_{k,i,0} * gamma_{k,i,p}, 2).
       - Heterogeneous hub demand profiles: each depot k draws a hub preference
         vector pi_k ~ Dirichlet(1.5 * 1_m); the 2 active global coupling
         resources r of pattern p are sampled without replacement with
         probabilities pi_k; for each active r, set:
         D_{k,r,i,p} = round(u_{k,r,i,p} * (1.0 + 0.8*(1.0 - gamma_{k,i,p})), 2),
         where u_{k,r,i,p} ~ Uniform(1.0, 3.5).
       - Select 1 active local wave constraint w in {0, ..., m_local-1}
         uniformly and draw A_{k,w,i,p} ~ Uniform(1.0, 2.5) (rounded to 2 decimals).
    3. Local and Global Capacity Calibration via Tightness Ratio eta_tight:
       Let p^*_{k,i} = argmin_{p} c_{k,i,p}.
       U^{global}_r = sum_{k,i} D_{k,r,i,p^*_{k,i}}
       U^{local}_{k,w} = sum_{i} A_{k,w,i,p^*_{k,i}}
       b_{k,w} = max(4.0, round(0.82 * U^{local}_{k,w}, 2))
       d_r = max(8.0, round(U^{global}_r / tightness, 2))
    4. Starting Feasible Solution x^{(0)} (uncoordinated regional booking):
       depots book hub capacity one after another (random request order, cheapest
       feasible pattern) up to 92% of every hub capacity d_r, so s^{(0)} > 0 is small.
    """
    rng = np.random.default_rng(seed)
    N_total = K * N_per_agent

    c = np.zeros((K, N_per_agent, P), dtype=np.float64)
    D = np.zeros((K, m_global, N_per_agent, P), dtype=np.float64)
    A = np.zeros((K, m_local, N_per_agent, P), dtype=np.float64)

    # 1. Pattern p = 0 (Uncoupled Fallback Dispatch)
    c[:, :, 0] = np.round(rng.uniform(85.0, 140.0, size=(K, N_per_agent)), 2)

    # 2. Patterns p in {1, ..., P-1} (Consolidated Shared-Hub Routes)
    # Regional depot heterogeneity: high-utility depots (close to consolidation
    # hubs) obtain larger per-request savings than low-utility depots.
    n_high = int(np.ceil(K / 2.0))
    high_utility = np.zeros(K, dtype=bool)
    high_utility[rng.permutation(K)[:n_high]] = True
    gamma_range = np.where(high_utility[:, None], [[0.28, 0.52]], [[0.62, 0.85]])
    # Heterogeneous regional hub demand profiles
    hub_pref = rng.dirichlet(1.5 * np.ones(m_global), size=K)  # (K, m_global)

    for k in range(K):
        g_lo, g_hi = gamma_range[k]
        for i in range(N_per_agent):
            c0 = c[k, i, 0]
            for p in range(1, P):
                gamma = rng.uniform(g_lo, g_hi)
                c[k, i, p] = np.round(c0 * gamma, 2)

                # Select 2 active global coupling resources by the depot's hub profile
                active_r = rng.choice(
                    m_global, size=min(2, m_global), replace=False, p=hub_pref[k]
                )
                u_vals = rng.uniform(1.0, 3.5, size=len(active_r))
                D[k, active_r, i, p] = np.round(
                    u_vals * (1.0 + 0.8 * (1.0 - gamma)), 2
                )

                # Select 1 active local wave constraint uniformly
                active_w = rng.integers(0, m_local)
                A[k, active_w, i, p] = np.round(rng.uniform(1.0, 2.5), 2)

    # 3. Local and Global Capacity Calibration via Tightness Ratio
    p_star = np.argmin(c, axis=2)  # shape (K, N_per_agent)
    k_grid = np.arange(K)[:, None]
    i_grid = np.arange(N_per_agent)[None, :]

    # Extract D_{k, r, i, p^*_{k,i}} and A_{k, w, i, p^*_{k,i}}
    # D has shape (K, m_global, N_per_agent, P) -> transpose to (K, N_per_agent, P, m_global)
    D_trans = np.transpose(D, (0, 2, 3, 1))
    D_star = D_trans[k_grid, i_grid, p_star]  # shape (K, N_per_agent, m_global)
    U_global = np.sum(D_star, axis=(0, 1))    # shape (m_global,)

    A_trans = np.transpose(A, (0, 2, 3, 1))
    A_star = A_trans[k_grid, i_grid, p_star]  # shape (K, N_per_agent, m_local)
    U_local = np.sum(A_star, axis=1)          # shape (K, m_local)

    b = np.maximum(4.0, np.round(0.82 * U_local, 2))
    d = np.maximum(8.0, np.round(U_global / tightness, 2))

    # 4. Starting feasible solution x^{(0)}: uncoordinated regional booking.
    # Depots k = 0, ..., K-1 book hub capacity one after another; each depot takes
    # its requests in random order and assigns each to its cheapest pattern that
    # keeps global hub usage <= INITIAL_HUB_UTILIZATION * d and local wave usage
    # <= b_k (otherwise p = 0). Early depots therefore hold hub capacity with
    # requests that need not be the most valuable ones, and little residual slack
    # s^{(0)} remains.
    initial_patterns = np.zeros((K, N_per_agent), dtype=np.int64)
    hub_cap = INITIAL_HUB_UTILIZATION * d
    hub_use = np.zeros(m_global)
    for k in range(K):
        wave_use = np.zeros(m_local)
        for i in rng.permutation(N_per_agent):
            for p_cand in np.argsort(c[k, i, :], kind="stable"):
                if p_cand == 0:
                    break
                if np.all(hub_use + D[k, :, i, p_cand] <= hub_cap + 1e-9) and np.all(
                    wave_use + A[k, :, i, p_cand] <= b[k] + 1e-9
                ):
                    initial_patterns[k, i] = p_cand
                    hub_use += D[k, :, i, p_cand]
                    wave_use += A[k, :, i, p_cand]
                    break

    name = f"RPA_SH_K{K}_N{N_total}_P{P}_eta{tightness:.2f}_s{seed}"
    return CoupledRoutingInstance(
        name=name,
        scale=scale,
        K=K,
        N_per_agent=N_per_agent,
        N_total=N_total,
        P=P,
        m_global=m_global,
        m_local=m_local,
        tightness=tightness,
        seed=seed,
        c=c,
        D=D,
        A=A,
        d=d,
        b=b,
        initial_patterns=initial_patterns,
        high_utility=high_utility,
    )
