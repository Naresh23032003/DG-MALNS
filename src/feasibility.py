"""
Exact Primal and Dual Feasibility Verifier and Objective Evaluator
for RPA-SH within numerical tolerance 1e-6.
"""

from typing import Tuple, Dict, Any
import numpy as np
from src.instance_generator import CoupledRoutingInstance

TOL = 1e-6


def evaluate_agent_cost(instance: CoupledRoutingInstance, k: int, patterns_k: np.ndarray) -> float:
    """Compute local primal cost c_k^T x_k for agent k."""
    i_idx = np.arange(instance.N_per_agent)
    return float(np.sum(instance.c[k, i_idx, patterns_k]))


def evaluate_global_cost(instance: CoupledRoutingInstance, patterns: np.ndarray) -> float:
    """Compute global primal objective C(x) = sum_{k=1}^K c_k^T x_k."""
    k_idx = np.arange(instance.K)[:, None]
    i_idx = np.arange(instance.N_per_agent)[None, :]
    return float(np.sum(instance.c[k_idx, i_idx, patterns]))


def compute_agent_global_usage(
    instance: CoupledRoutingInstance, k: int, patterns_k: np.ndarray
) -> np.ndarray:
    """Compute D_k x_k in R^{m_global} for agent k."""
    i_idx = np.arange(instance.N_per_agent)
    # instance.D[k] has shape (m_global, N_per_agent, P)
    return np.sum(instance.D[k, :, i_idx, patterns_k], axis=0)


def compute_all_global_usage(
    instance: CoupledRoutingInstance, patterns: np.ndarray
) -> np.ndarray:
    """Compute sum_{k=1}^K D_k x_k in R^{m_global}."""
    total_usage = np.zeros(instance.m_global, dtype=np.float64)
    i_idx = np.arange(instance.N_per_agent)
    for k in range(instance.K):
        total_usage += np.sum(instance.D[k, :, i_idx, patterns[k]], axis=0)
    return total_usage


def compute_global_slack(
    instance: CoupledRoutingInstance, patterns: np.ndarray
) -> np.ndarray:
    """Compute residual global coupling slack s = d - sum_{k=1}^K D_k x_k."""
    return instance.d - compute_all_global_usage(instance, patterns)


def compute_agent_local_usage(
    instance: CoupledRoutingInstance, k: int, patterns_k: np.ndarray
) -> np.ndarray:
    """Compute A_k x_k in R^{m_local} for agent k."""
    i_idx = np.arange(instance.N_per_agent)
    # instance.A[k] has shape (m_local, N_per_agent, P)
    return np.sum(instance.A[k, :, i_idx, patterns_k], axis=0)


def is_agent_locally_feasible(
    instance: CoupledRoutingInstance,
    k: int,
    patterns_k: np.ndarray,
    tol: float = TOL,
) -> bool:
    """
    Check if patterns_k represents a valid binary assignment in X_k:
    1. Valid pattern indices in {0, ..., P-1} (representing sum_p x_{k,i,p} = 1, x in {0,1}).
    2. Local depot wave capacities: A_k x_k <= b_k + tol.
    """
    if patterns_k.shape != (instance.N_per_agent,):
        return False
    if np.any(patterns_k < 0) or np.any(patterns_k >= instance.P):
        return False
    local_usage = compute_agent_local_usage(instance, k, patterns_k)
    if np.any(local_usage > instance.b[k] + tol):
        return False
    return True


def verify_solution_feasibility(
    instance: CoupledRoutingInstance,
    patterns: np.ndarray,
    tol: float = TOL,
) -> Tuple[bool, Dict[str, Any]]:
    """
    Verify exact mathematical feasibility of a full multi-agent solution x
    against Equations (2)-(5) within numerical tolerance tol = 1e-6.

    Also verifies the flattened binary representation x_k in {0,1}^{n_k}.
    """
    if patterns.shape != (instance.K, instance.N_per_agent):
        return False, {"reason": f"Invalid shape {patterns.shape}"}

    # Verify binary representation and assignment constraints (Equations 4 & 5)
    x_bin = instance.patterns_to_binary(patterns)
    assignment_sums = np.sum(x_bin, axis=2)
    max_assign_err = float(np.max(np.abs(assignment_sums - 1.0)))
    if max_assign_err > tol:
        return False, {"reason": "Assignment constraint violated", "max_assign_err": max_assign_err}

    # Verify local depot wave capacities A_k x_k <= b_k (Equation 3)
    max_local_viol = 0.0
    for k in range(instance.K):
        if not is_agent_locally_feasible(instance, k, patterns[k], tol=tol):
            local_u = compute_agent_local_usage(instance, k, patterns[k])
            viol = float(np.max(local_u - instance.b[k], initial=0.0))
            return False, {
                "reason": f"Agent {k} local capacity violated",
                "max_local_violation": viol,
            }
        local_u = compute_agent_local_usage(instance, k, patterns[k])
        max_local_viol = max(max_local_viol, float(np.max(local_u - instance.b[k], initial=0.0)))

    # Verify global coupling constraints sum_{k=1}^K D_k x_k <= d (Equation 2)
    global_usage = compute_all_global_usage(instance, patterns)
    global_viol_vec = global_usage - instance.d
    max_global_viol = float(np.max(global_viol_vec))
    if max_global_viol > tol:
        return False, {
            "reason": "Global coupling capacity violated",
            "max_global_violation": max_global_viol,
        }

    obj_val = evaluate_global_cost(instance, patterns)
    return True, {
        "objective": obj_val,
        "max_local_violation": max(0.0, max_local_viol),
        "max_global_violation": max(0.0, max_global_viol),
        "min_global_slack": float(np.min(instance.d - global_usage)),
    }
