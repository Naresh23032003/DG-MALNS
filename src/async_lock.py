"""
Asynchronous lock baseline (Async-Lock): no synchronization barrier.

W persistent processes; process w owns the agents k with k % W == w and cycles through
them. For each agent it runs one worker step with the optimistic cap (the current
residual slack s it last received, L = 1, M chained steps, the same operators and
random stream worker_rng(seed, j, k, rep) as the synchronous methods, j being the
agent's step counter), sends the proposal (Delta c, Delta D) to the coordinator the
moment it is finished, and waits only for that proposal's answer. The coordinator
validates every proposal against the CURRENT slack under a lock, in arrival order: an
improving proposal that fits (Delta D <= s) is committed at once and s is updated; the
answer carries the new s. Each agent's block changes only through its own proposals,
so every committed proposal keeps the solution feasible. This is our own adaptation of
lock-protected, commit-on-arrival updates to shared capacities. It does not reimplement
DROP-LNS (Chan et al. 2024), where a worker's whole solution replaces the best one under a
mutex if it is cheaper and no merge against shared capacities takes place. Wall-clock
protocol only (results depend on timing).
"""

import multiprocessing as mp
from multiprocessing.connection import wait
import time
from dataclasses import dataclass, field
from typing import List

import numpy as np

from src.feasibility import (evaluate_global_cost, compute_global_slack, verify_solution_feasibility, TOL)


def _proc(conn, w: int, W: int):
    from src.worker import worker_step
    instance, agents = None, []
    conn.send(True)
    while True:
        msg = conn.recv()
        kind = msg[0]
        if kind == "load":
            instance = msg[1]
            agents = [k for k in range(instance.K) if k % W == w]
            conn.send(True)
        elif kind == "run":
            _, pats, s, seed, rep, M = msg
            inc = {k: pats[j].copy() for j, k in enumerate(agents)}
            steps = {k: 0 for k in agents}
            stop = len(agents) == 0
            while not stop:
                for k in agents:
                    p, dc, dD, tau = worker_step(instance, k, inc[k], s, s.copy(), seed, steps[k], 1, None, 0.0,
                                                 rep, None, M)
                    steps[k] += 1
                    conn.send(("prop", k, float(dc[1]), dD[:, 1].copy(), tau))
                    ok, s, stop = conn.recv()
                    if ok:
                        inc[k] = p[1]
                    if stop:
                        break
            conn.send(("done", {k: inc[k] for k in agents}, steps))
        elif kind == "stop":
            conn.close()
            return


@dataclass
class AsyncResult:
    best_obj: float
    initial_obj: float
    feasible: bool
    wall_clock_s: float
    cpu_time_s: float
    init_time_s: float
    steps_total: int
    steps_per_agent: float
    proposals: int
    accepted_moves: int
    rejected_fit: int
    trace_t: List[float] = field(default_factory=list)
    trace_obj: List[float] = field(default_factory=list)


class AsyncPool:
    def __init__(self, W: int):
        t0 = time.perf_counter()
        ctx = mp.get_context("spawn")
        self.W = W
        self.conns, self.procs = [], []
        for w in range(W):
            a, b = ctx.Pipe()
            p = ctx.Process(target=_proc, args=(b, w, W), daemon=True)
            p.start()
            self.conns.append(a)
            self.procs.append(p)
        for c in self.conns:
            c.recv()
        self.startup_s = time.perf_counter() - t0

    def run(self, instance, budget_s: float, seed: int, rep: int, M: int = 5) -> AsyncResult:
        from src.engine import make_start
        wall0 = time.perf_counter()
        pats, tau_init = make_start(instance, "lp_round")
        wall0 -= max(0.0, tau_init - (time.perf_counter() - wall0))   # cached LP-Round time is charged
        K, W = instance.K, self.W
        owned = [[k for k in range(K) if k % W == w] for w in range(W)]
        for c in self.conns:
            c.send(("load", instance))
        for c in self.conns:
            c.recv()
        s = compute_global_slack(instance, pats)
        obj0 = obj = evaluate_global_cost(instance, pats)
        for w, c in enumerate(self.conns):
            c.send(("run", pats[owned[w]], s.copy(), seed, rep, M))
        trace_t, trace_obj = [time.perf_counter() - wall0], [obj]
        cpu = tau_init
        props = acc = rej = steps_total = 0
        final = {}
        active = list(self.conns)
        while active:
            for c in wait(active):
                msg = c.recv()
                if msg[0] == "prop":
                    tc0 = time.perf_counter()
                    _, k, dc, dD, tau = msg
                    cpu += tau
                    stop = (time.perf_counter() - wall0) >= budget_s
                    ok = False
                    if dc < -TOL:
                        props += 1
                        if np.all(dD <= s + TOL):
                            ok = True
                            s = s - dD
                            obj += dc
                            acc += 1
                            trace_t.append(time.perf_counter() - wall0)
                            trace_obj.append(obj)
                        else:
                            rej += 1
                    c.send((ok, s.copy(), stop))
                    cpu += time.perf_counter() - tc0
                else:
                    final.update(msg[1])
                    steps_total += int(sum(msg[2].values()))
                    active.remove(c)
        patterns = np.stack([final[k] for k in range(K)])
        wall = time.perf_counter() - wall0
        best = evaluate_global_cost(instance, patterns)
        assert abs(best - obj) <= 1e-6 * max(1.0, abs(best)), (best, obj)
        feas, _ = verify_solution_feasibility(instance, patterns)
        return AsyncResult(best_obj=best, initial_obj=obj0, feasible=feas, wall_clock_s=wall, cpu_time_s=cpu,
                           init_time_s=tau_init, steps_total=steps_total, steps_per_agent=steps_total / K,
                           proposals=props, accepted_moves=acc, rejected_fit=rej, trace_t=trace_t,
                           trace_obj=trace_obj)

    def close(self):
        for c in self.conns:
            try:
                c.send(("stop",))
            except Exception:
                pass
        for p in self.procs:
            p.join(timeout=5)
