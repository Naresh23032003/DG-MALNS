"""
HiGHS (highspy, pinned in requirements.txt) runs with an explicit thread count and an incumbent trace.

Each solve runs in a fresh spawned process (HiGHS fixes its global thread scheduler
at the first run of a process, so 1-thread and 4-thread runs must not share one).
Reported times are measured inside that process around Highs.run() only:
    highs_time_limit_s   the time limit passed to HiGHS
    highs_actual_time_s  the measured duration of run()
The incumbent trace (time, objective) comes from the kCallbackMipImprovingSolution
callback and is used for anytime curves and primal integrals.

Watchdog (added 2026-11-17): HiGHS 1.16.0 once ignored its time limit (a 300 s run on
MCA_SC_K16_N960_P20_eta1.25_s103 was still in presolve::HPresolve::strengthenInequalities
inside nested RINS sub-MIPs after 10.9 h). The solve process therefore streams every
incumbent to a file, and the parent kills it once it runs HARD_GRACE_ABS + HARD_GRACE_REL *
limit seconds past its time limit. A killed run reports status "killed (watchdog)", the
last incumbent found within the time limit (from the streamed trace; NaN if none), no
dual bound, highs_actual_time_s = the time limit, and killed = True.
"""

import multiprocessing as mp
import os
import tempfile
import time
from typing import Optional, Dict

import numpy as np

MILP_REL_GAP = 1e-4
HARD_GRACE_ABS = 30.0      # watchdog: seconds past the time limit ...
HARD_GRACE_REL = 0.10      # ... plus this fraction of the limit
BUILD_TIMEOUT = 600.0      # watchdog: longest model build before run() starts


def _solve(instance, time_limit_s: float, threads: int, start_patterns, rel_gap: float,
           stream_path: Optional[str] = None) -> Dict:
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
    fh = open(stream_path, "a", buffering=1) if stream_path else None

    def cb(cb_type, msg, data_out, data_in, user):
        trace.append((time.perf_counter() - t0[0], float(data_out.objective_function_value)))
        if fh is not None:
            fh.write(f"{trace[-1][0]!r} {trace[-1][1]!r}\n")

    h.setCallback(cb, None)
    h.startCallback(highspy.cb.HighsCallbackType.kCallbackMipImprovingSolution)
    t0[0] = time.perf_counter()
    if fh is not None:
        fh.write(f"START {time.time()!r}\n")
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
                nodes=int(info.mip_node_count), killed=False)


def _entry(conn, *args):
    conn.send(_solve(*args))
    conn.close()


def solve_highs(instance, time_limit_s: float, threads: int = 1,
                start_patterns: Optional[np.ndarray] = None, rel_gap: float = MILP_REL_GAP,
                grace_abs: float = HARD_GRACE_ABS, grace_rel: float = HARD_GRACE_REL) -> Dict:
    """Solve in a fresh spawned process under the watchdog (see module docstring)."""
    ctx = mp.get_context("spawn")
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "trace.txt")
        rx, tx = ctx.Pipe(duplex=False)
        proc = ctx.Process(target=_entry, args=(tx, instance, time_limit_s, threads, start_patterns, rel_gap, path))
        proc.start()
        tx.close()
        launched = time.time()
        deadline = time_limit_s + grace_abs + grace_rel * time_limit_s
        while True:
            if rx.poll(1.0):
                out = rx.recv()
                proc.join()
                return out
            start, trace = _read_stream(path)
            late = (start is not None and time.time() - start > deadline) or \
                   (start is None and time.time() - launched > BUILD_TIMEOUT)
            if not late and not proc.is_alive() and rx.poll(0):
                continue                     # finished between the two checks: collect the result
            if late or not proc.is_alive():
                status = "killed (watchdog)" if late else "crashed"
                proc.kill()
                proc.join()
                within = [(t, o) for t, o in trace if t <= time_limit_s]
                return dict(status=status, obj=within[-1][1] if within else float("nan"),
                            dual_bound=float("nan"), highs_time_limit_s=float(time_limit_s),
                            highs_actual_time_s=float(time_limit_s), threads=int(threads), trace=within,
                            patterns=None, nodes=None, killed=True)


def _read_stream(path):
    start, trace = None, []
    if not os.path.exists(path):
        return start, trace
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) != 2:
                continue
            try:
                if parts[0] == "START":
                    start = float(parts[1])
                else:
                    trace.append((float(parts[0]), float(parts[1])))
            except ValueError:
                pass      # a line being written
    return start, trace
