"""
Persistent agent-owning process pool with near-zero inter-process traffic.

W processes are spawned once per experiment (start-up time startup_s is reported
separately). Each run first ships its instance to every process ("load", charged to
the run's wall-clock time); process w owns agents k with k % W == w and keeps their
incumbents x_k and current portfolios locally. Per epoch, the main process sends one message per process
(the previous epoch's selected levels of its agents, residual slack s^{(t)}, quotas,
prices and scalars) and receives the cost and hub-usage changes of every level
(delta_c: L+1 floats, raw_dD: m x (L+1) floats per agent) plus the worker times.
Pattern vectors never cross process boundaries during the search; they are fetched
once at the end. The worker step and random streams are the same as in serial runs,
so results are identical to serial execution.
"""

import multiprocessing as mp
import time
from typing import List

import numpy as np


def _proc(conn, w: int, W: int):
    from src.worker import worker_step
    inc, port = {}, {}
    instance, agents = None, []
    conn.send(True)
    while True:
        msg = conn.recv()
        kind = msg[0]
        if kind == "load":
            instance = msg[1]
            agents = [k for k in range(instance.K) if k % W == w]
            conn.send(True)
        elif kind == "reset":
            pats = msg[1]
            inc = {k: pats[j].copy() for j, k in enumerate(agents)}
            port = {}
            conn.send(True)
        elif kind == "step":
            _, prev_sel, t, s_t, q_cols, duals, rho_t, seed, rep, L, max_net, M = msg
            if prev_sel is not None:
                for j, k in enumerate(agents):
                    if prev_sel[j] >= 0:
                        inc[k] = port[k][prev_sel[j]]
            outs = []
            for j, k in enumerate(agents):
                p, dc, dD, tau = worker_step(instance, k, inc[k], s_t, q_cols[:, j], seed, t, L,
                                             duals, rho_t, rep, max_net, M)
                port[k] = p
                outs.append((dc, dD, tau))
            conn.send(outs)
        elif kind == "finish":
            prev_sel = msg[1]
            if prev_sel is not None:
                for j, k in enumerate(agents):
                    if prev_sel[j] >= 0:
                        inc[k] = port[k][prev_sel[j]]
            conn.send({k: inc[k] for k in agents})
        elif kind == "stop":
            conn.close()
            return


class AgentPool:
    def __init__(self, W: int):
        t0 = time.perf_counter()
        ctx = mp.get_context("spawn")
        self.W = W
        self.K = 0
        self.loaded = None
        self.conns, self.procs = [], []
        for w in range(W):
            a, b = ctx.Pipe()
            p = ctx.Process(target=_proc, args=(b, w, W), daemon=True)
            p.start()
            self.conns.append(a)
            self.procs.append(p)
        for c in self.conns:
            c.recv()  # every process has imported numpy/scipy and is ready
        self.startup_s = time.perf_counter() - t0

    def load(self, instance):
        """Ship the instance to every process (once per run; charged to the run)."""
        self.K = instance.K
        self.owned = [[k for k in range(self.K) if k % self.W == w] for w in range(self.W)]
        for c in self.conns:
            c.send(("load", instance))
        for c in self.conns:
            c.recv()
        self.loaded = instance.name

    def reset(self, patterns: np.ndarray):
        for w, c in enumerate(self.conns):
            c.send(("reset", patterns[self.owned[w]]))
        for c in self.conns:
            c.recv()

    def step(self, prev_sel, t, s_t, q_all, duals, rho_t, seed, rep, L, max_net, M, q_override=None):
        for w, c in enumerate(self.conns):
            ks = self.owned[w]
            ps = None if prev_sel is None else prev_sel[ks]
            q_cols = q_all[:, ks] if q_override is None else q_override[:, ks]
            c.send(("step", ps, t, s_t, q_cols, duals, rho_t, seed, rep, L, max_net, M))
        outs = [None] * self.K
        for w, c in enumerate(self.conns):
            for k, o in zip(self.owned[w], c.recv()):
                outs[k] = o
        return outs

    def finish(self, prev_sel) -> np.ndarray:
        for w, c in enumerate(self.conns):
            c.send(("finish", None if prev_sel is None else prev_sel[self.owned[w]]))
        got = {}
        for c in self.conns:
            got.update(c.recv())
        return np.stack([got[k] for k in range(self.K)])

    def close(self):
        for c in self.conns:
            try:
                c.send(("stop",))
            except Exception:
                pass
        for p in self.procs:
            p.join(timeout=5)
