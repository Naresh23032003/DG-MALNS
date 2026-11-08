"""
HiGHS 1.8.0 (highspy) runs with an explicit thread count and an incumbent trace.

Each solve runs in a fresh spawned process (HiGHS fixes its global thread scheduler
at the first run of a process, so 1-thread and 4-thread runs must not share one).
Reported times are measured inside that process around Highs.run() only:
    highs_time_limit_s   the time limit passed to HiGHS
    highs_actual_time_s  the measured duration of run()
The incumbent trace (time, objective) comes from the kCallbackMipImprovingSolution
callback and is used for anytime curves and primal integrals.
"""

import multiprocessing as mp
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Optional, Dict

import numpy as np

MILP_REL_GAP = 1e-4


def _solve(instance, time_limit_s: float, threads: int, start_patterns, rel_gap: float) -> Dict:
    import highspy
    from src.baselines import build_block_angular_matrices
    from src.feasibility import verify_solution_feasibility, evaluate_global_cost
    c, A, lb, ub = build_block_angular_matrices(instance)
    A = A.tocsc()
    n = len(c)
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("time_limit", float(max(time_limit_s, 1e-3)))
    h.setOptionValue("mip_rel_gap", rel_gap)
    h.setOptionValue("threads", int(threads))
    lp = highspy.HighsLp()
    lp.num_col_, lp.num_row_ = n, A.shape[0]
    lp.col_cost_ = c
    lp.col_lower_, lp.col_upper_ = np.zeros(n), np.ones(n)
    lp.row_lower_, lp.row_upper_ = lb, ub
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
    lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = A.indptr, A.indices, A.data
    lp.integrality_ = [highspy.HighsVarType.kInteger] * n
    h.passModel(lp)
    if start_patterns is not None:
        sol = highspy.HighsSolution()
        sol.col_value = list(instance.patterns_to_binary(start_patterns).reshape(-1))
        h.setSolution(sol)
    trace = []
    t0 = [0.0]

    def cb(cb_type, msg, data_out, data_in, user):
        trace.append((time.perf_counter() - t0[0], float(data_out.objective_function_value)))

    h.setCallback(cb, None)
    h.startCallback(highspy.cb.HighsCallbackType.kCallbackMipImprovingSolution)
    t0[0] = time.perf_counter()
    h.run()
    elapsed = time.perf_counter() - t0[0]
    info = h.getInfo()
    status = h.modelStatusToString(h.getModelStatus())
    pats = None
    obj = float("nan")
    if info.primal_solution_status == 2:
        x = np.array(h.getSolution().col_value)
        cand = instance.binary_to_patterns(
            np.round(x).astype(np.int64).reshape(instance.K, instance.N_per_agent, instance.P))
        if verify_solution_feasibility(instance, cand)[0]:
            pats = cand
            obj = evaluate_global_cost(instance, cand)
    return dict(status=status, obj=obj, dual_bound=float(info.mip_dual_bound),
                highs_time_limit_s=float(time_limit_s), highs_actual_time_s=elapsed,
                threads=int(threads), trace=trace, patterns=pats,
                nodes=int(info.mip_node_count))


def solve_highs(instance, time_limit_s: float, threads: int = 1,
                start_patterns: Optional[np.ndarray] = None, rel_gap: float = MILP_REL_GAP) -> Dict:
    """Solve in a fresh spawned process (see module docstring)."""
    with ProcessPoolExecutor(max_workers=1, mp_context=mp.get_context("spawn")) as ex:
        return ex.submit(_solve, instance, time_limit_s, threads, start_patterns, rel_gap).result()
