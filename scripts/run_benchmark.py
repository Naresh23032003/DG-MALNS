"""
Step 2 benchmark suite (revision 2). Every job runs strictly one at a time.

Primary method: PC-MALNS (Portfolio-Coordinated Multi-Agent LNS): LP-Round warm start,
four-level portfolio (l = 0..3), M = 5 chained destroy-repair steps per level, no
consolidation cap, no prices (lambda = 0), uniform quota s^(t)/K. Its two barrier
resolution modes are MC-CRIP (exact) and BCRM-Greedy (polynomial).

All LNS methods: 5 independent runs (rep = 0..4) per instance on a persistent W = 4
agent pool (real wall clock; the per-scale wall-clock budget includes the charged
LP-Round time). Deterministic methods (LP-Round, HiGHS) run once per instance.

Tables (results/raw/bench_<table>.csv, resumable per instance):
  A          main benchmark, P = 6, eta = 1.25, Small..XXXL, test seeds 101..110.
             HiGHS 1 thread: one long reference run (600 s Small/Medium, 60 s
             otherwise) whose incumbent trace gives HiGHS (5s), HiGHS (60s),
             HiGHS (600s) and HiGHS (CPU-matched); HiGHS (wall-matched) is a separate
             real run with 1 and 4 threads. Lower bound LB = max(LP bound, HiGHS dual
             bound) of the reference run (= objective when proven optimal).
  B          rich candidate pools, P in {20, 40}, Medium..XXL; reference HiGHS 30 s.
  C_direct   commit-rule isolation under the decentralized direct start
             (Medium/Large of table A, LB from table A).
  C_sync     commit-rule isolation on RPA-SH-Sync (Medium/Large); reference 60 s.
  sync_check same as C_sync on the validation seeds 1..3 (run before C_sync).
  E_sweep    tightness sweep on Large, eta in {0.85, 1.05, 1.45} (1.25 = table A).
  E_ablation price and quota variants of PC-MALNS [MC-CRIP] on Large (LB from A).
  E_scaling  wall clock of a fixed number of epochs: serial and W in {1, 2, 4, 8}.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.instance_generator import generate_instance
from src.sync_instances import generate_sync_instance
from src.baselines import solve_lp_relaxation, lp_round_start
from src.feasibility import evaluate_global_cost, verify_solution_feasibility
from src.engine import run_engine, method_configs, EngineConfig, primal_integral
from src.highs_runner import solve_highs
from src.agent_pool import AgentPool

RAW = REPO_ROOT / "results" / "raw"
TEST_SEEDS = list(range(101, 111))
VAL_SEEDS = [1, 2, 3]
REPS = 5
W_MAIN = 4
M_INNER = 5
SCALES = {"Small": (4, 30), "Medium": (8, 40), "Large": (12, 50), "X-Large": (16, 60),
          "XXL": (24, 100), "XXXL": (32, 125)}
BUDGET = {"Small": 0.5, "Medium": 1.0, "Large": 1.5, "X-Large": 2.0, "XXL": 4.0, "XXXL": 6.0}
PRIMARY = "PC-MALNS [MC-CRIP]"
RENAME = {"MC-CRIP": PRIMARY, "BCRM-Greedy": "PC-MALNS [BCRM-Greedy]"}
ALL_LNS = [PRIMARY, "PC-MALNS [BCRM-Greedy]", "Greedy-Efficiency-Portfolio", "Greedy-Gain-Portfolio",
           "Opt-Rollback", "Opt-SeqLock", "Opt-Rollback-Portfolio", "Opt-SeqLock-Portfolio",
           "Static-Quota", "Demand-Quota"]
TABLE_B_LNS = [PRIMARY, "PC-MALNS [BCRM-Greedy]", "Greedy-Efficiency-Portfolio", "Opt-Rollback", "Opt-SeqLock"]
COMMIT_LNS = [PRIMARY, "PC-MALNS [BCRM-Greedy]", "Greedy-Efficiency-Portfolio", "Greedy-Gain-Portfolio",
              "Opt-Rollback-Portfolio", "Opt-SeqLock-Portfolio", "Opt-Rollback", "Opt-SeqLock"]
SWEEP_LNS = [PRIMARY, "PC-MALNS [BCRM-Greedy]", "Greedy-Efficiency-Portfolio", "Opt-Rollback",
             "Opt-SeqLock", "Static-Quota"]

COLS = ["table", "instance_name", "scale", "K", "N_total", "P", "m_global", "eta", "seed", "method", "family",
        "rep", "init_mode", "inner_iters", "duals", "quota", "commit", "L", "workers_W", "threads",
        "best_obj", "initial_obj", "lower_bound", "gap_pct", "feasible", "wall_budget_s", "wall_clock_s",
        "cpu_time_s", "sim_parallel_s", "init_time_s", "pool_startup_s", "epochs_run", "conflict_epochs",
        "conflict_rate_pct", "accepted_moves", "proposals", "matcher_ms_mean", "matcher_fallbacks",
        "primal_integral", "highs_time_limit_s", "highs_actual_time_s", "highs_status", "highs_source",
        "cf_sum", "cf_strict_wins", "trace"]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def configs(init="lp_round", M=M_INNER):
    C = method_configs(init_mode=init, max_net=None, inner_iters=M)
    out = {}
    for k, cfg in C.items():
        cfg.name = RENAME.get(k, k)
        out[cfg.name] = cfg
    return out


def base_row(table, inst, scale):
    return dict(table=table, instance_name=inst.name, scale=scale, K=inst.K, N_total=inst.N_total, P=inst.P,
                m_global=inst.m_global, eta=inst.tightness, seed=inst.seed)


def lns_rows(table, inst, scale, lb, names, budget, pool, init="lp_round", reps=REPS, counterfactual=True,
             cfg_map=None, keep_trace_rep0=True):
    cfg_map = cfg_map or configs(init)
    rows = []
    for name in names:
        for rep in range(reps):
            cfg = cfg_map[name]
            cfg.time_budget_s, cfg.budget_clock = budget, "wall"
            cfg.counterfactual = counterfactual and cfg.commit == "MC-CRIP" and cfg.L >= 2
            r = run_engine(inst, cfg, lb, seed=inst.seed, rep=rep, pool=pool)
            if not r.feasible:
                raise RuntimeError(f"infeasible: {name} {inst.name} rep {rep}")
            d = base_row(table, inst, scale)
            d.update(method=name, family="LNS", rep=rep, init_mode=cfg.init_mode, inner_iters=cfg.inner_iters,
                     duals=cfg.duals, quota=cfg.quota, commit=cfg.commit, L=cfg.L, workers_W=r.workers_W,
                     best_obj=r.best_obj, initial_obj=r.initial_obj, lower_bound=lb, gap_pct=r.gap_pct,
                     feasible=r.feasible, wall_budget_s=budget, wall_clock_s=r.wall_clock_s,
                     cpu_time_s=r.cpu_time_s, sim_parallel_s=r.sim_parallel_s, init_time_s=r.init_time_s,
                     pool_startup_s=r.pool_startup_s, epochs_run=r.epochs_run, conflict_epochs=r.conflict_epochs,
                     conflict_rate_pct=100.0 * r.conflict_epochs / max(1, r.epochs_run),
                     accepted_moves=r.accepted_moves, proposals=r.proposals, matcher_ms_mean=r.matcher_ms_mean,
                     matcher_fallbacks=r.matcher_fallbacks, primal_integral=r.primal_integral,
                     cf_sum=json.dumps(r.cf_sum), cf_strict_wins=json.dumps(r.cf_strict_wins))
            if keep_trace_rep0 and rep == 0:
                d["trace"] = json.dumps([[round(t, 4), round(o, 4)] for t, o in zip(r.trace_t, r.trace_obj)])
            rows.append(d)
    return rows


def obj_at(trace, T):
    v = None
    for t, o in trace:
        if t <= T + 1e-9:
            v = o
    return v


def highs_row(table, inst, scale, lb, method, obj, T, threads, h, source, horizon=None):
    trace = h["trace"]
    tt = [t for t, _ in trace]
    to = [o for _, o in trace]
    hz = T if horizon is None else horizon
    if source == "run":   # final result of a real run (the callback trace can miss a last improvement)
        obj = h["obj"] if np.isfinite(h["obj"]) else None
    d = base_row(table, inst, scale)
    feasible = obj is not None and np.isfinite(obj)
    d.update(method=method, family="HiGHS", rep=0, workers_W=1, threads=threads,
             best_obj=obj if feasible else np.nan, lower_bound=lb,
             gap_pct=max(0.0, 100.0 * (obj - lb) / lb) if feasible else np.nan, feasible=feasible,
             wall_clock_s=min(T, h["highs_actual_time_s"]), highs_time_limit_s=T,
             highs_actual_time_s=h["highs_actual_time_s"] if source == "run" else min(T, h["highs_actual_time_s"]),
             highs_status=h["status"] if source == "run" else f"trace of {h['highs_time_limit_s']:.0f}s run",
             highs_source=source, primal_integral=primal_integral([0.0] + tt, [None] + to, lb, hz))
    return d


def reference(inst, T):
    lp = solve_lp_relaxation(inst)["lp_bound"]
    h = solve_highs(inst, T, threads=1)
    lb = max(lp, h["dual_bound"]) if np.isfinite(h["dual_bound"]) else lp
    if np.isfinite(h["obj"]):
        lb = min(lb, h["obj"])
    return lp, lb, h


def lp_round_row(table, inst, scale, lb):
    pats, lt, rt = lp_round_start(inst)
    obj = evaluate_global_cost(inst, pats)
    assert verify_solution_feasibility(inst, pats)[0]
    d = base_row(table, inst, scale)
    d.update(method="LP-Round", family="Deterministic", rep=0, init_mode="lp_round", best_obj=obj,
             initial_obj=obj, lower_bound=lb, gap_pct=max(0.0, 100.0 * (obj - lb) / lb), feasible=True,
             wall_clock_s=lt + rt, cpu_time_s=lt + rt, init_time_s=lt + rt)
    return d


def matched_rows(table, inst, scale, lb, rows, ref_h):
    """HiGHS wall-matched (real runs, 1T and 4T) and CPU-matched (1T, from the reference trace)."""
    prim = [r for r in rows if r["method"] == PRIMARY]
    T_wall = float(np.mean([r["wall_clock_s"] for r in prim]))
    T_cpu = float(np.mean([r["cpu_time_s"] for r in prim]))
    out = []
    for th in (1, 4):
        h = solve_highs(inst, T_wall, threads=th)
        o = h["obj"] if np.isfinite(h["obj"]) else None
        out.append(highs_row(table, inst, scale, lb, f"HiGHS ({th}T, wall-matched)", o, T_wall, th, h, "run"))
    if ref_h is not None:
        out.append(highs_row(table, inst, scale, lb, "HiGHS (1T, CPU-matched)", obj_at(ref_h["trace"], T_cpu),
                             T_cpu, 1, ref_h, "trace"))
    return out


class Sink:
    def __init__(self, table):
        self.path = RAW / f"bench_{table}.csv"
        self.done = set()
        if self.path.exists():
            self.done = set(pd.read_csv(self.path, usecols=["instance_name"])["instance_name"])

    def write(self, rows):
        df = pd.DataFrame(rows).reindex(columns=COLS)
        df.to_csv(self.path, mode="a", header=not self.path.exists(), index=False)


def log(table, inst, rows, t0):
    df = pd.DataFrame(rows)
    g = df.groupby("method", sort=False)["gap_pct"].mean()
    print(f"[{table}] {inst.name} ({time.perf_counter() - t0:.0f}s) " +
          " ".join(f"{m}={v:.2f}" for m, v in g.items()), flush=True)


def ref_table(path=None):
    path = path or RAW / "bench_reference.csv"
    return pd.read_csv(path).set_index("instance_name") if Path(path).exists() else None


def save_ref(inst, scale, T, lp, lb, h, table):
    path = RAW / "bench_reference.csv"
    row = dict(instance_name=inst.name, table=table, scale=scale, K=inst.K, P=inst.P, eta=inst.tightness,
               seed=inst.seed, lp_bound=lp, highs_obj=h["obj"], highs_dual=h["dual_bound"], highs_status=h["status"],
               highs_time_limit_s=T, highs_actual_time_s=h["highs_actual_time_s"], highs_nodes=h.get("nodes"),
               lower_bound=lb, trace=json.dumps(h["trace"]))
    pd.DataFrame([row]).to_csv(path, mode="a", header=not path.exists(), index=False)


# ---------------------------------------------------------------------------
# tables
# ---------------------------------------------------------------------------
def table_a(pool):
    sink = Sink("A")
    for scale in SCALES:
        K, n = SCALES[scale]
        T_long = 600.0 if scale in ("Small", "Medium") else 60.0
        for seed in TEST_SEEDS:
            inst = generate_instance(K, n, P=6, tightness=1.25, seed=seed, scale=scale)
            if inst.name in sink.done:
                continue
            t0 = time.perf_counter()
            lp, lb, h = reference(inst, T_long)
            save_ref(inst, scale, T_long, lp, lb, h, "A")
            rows = [lp_round_row("A", inst, scale, lb)]
            for T in (5.0, 60.0, 600.0):
                if T <= T_long:
                    rows.append(highs_row("A", inst, scale, lb, f"HiGHS ({T:.0f}s)", obj_at(h["trace"], T), T, 1, h,
                                          "trace" if T < T_long else "run"))
            lns = lns_rows("A", inst, scale, lb, ALL_LNS, BUDGET[scale], pool)
            rows += lns + matched_rows("A", inst, scale, lb, lns, h)
            sink.write(rows)
            log("A", inst, rows, t0)


def table_b(pool):
    sink = Sink("B")
    for P in (20, 40):
        for scale in ("Medium", "Large", "X-Large", "XXL"):
            K, n = SCALES[scale]
            for seed in TEST_SEEDS:
                inst = generate_instance(K, n, P=P, tightness=1.25, seed=seed, scale=scale)
                if inst.name in sink.done:
                    continue
                t0 = time.perf_counter()
                lp, lb, h = reference(inst, 30.0)
                save_ref(inst, scale, 30.0, lp, lb, h, "B")
                rows = [lp_round_row("B", inst, scale, lb),
                        highs_row("B", inst, scale, lb, "HiGHS (30s)", obj_at(h["trace"], 30.0), 30.0, 1, h, "run")]
                lns = lns_rows("B", inst, scale, lb, TABLE_B_LNS, BUDGET[scale], pool)
                rows += lns + matched_rows("B", inst, scale, lb, lns, h)
                sink.write(rows)
                log("B", inst, rows, t0)


def table_c_direct(pool):
    sink = Sink("C_direct")
    ref = ref_table()
    for scale in ("Medium", "Large"):
        K, n = SCALES[scale]
        for seed in TEST_SEEDS:
            inst = generate_instance(K, n, P=6, tightness=1.25, seed=seed, scale=scale)
            if inst.name in sink.done:
                continue
            t0 = time.perf_counter()
            lb = float(ref.loc[inst.name, "lower_bound"])
            rows = lns_rows("C_direct", inst, scale, lb, COMMIT_LNS, BUDGET[scale], pool, init="direct")
            sink.write(rows)
            log("C_direct", inst, rows, t0)


def sync_rows(table, inst, scale, pool, T_ref):
    lp, lb, h = reference(inst, T_ref)
    save_ref(inst, scale, T_ref, lp, lb, h, table)
    rows = [lp_round_row(table, inst, scale, lb),
            highs_row(table, inst, scale, lb, f"HiGHS ({T_ref:.0f}s)", obj_at(h["trace"], T_ref), T_ref, 1, h, "run")]
    lns = lns_rows(table, inst, scale, lb, COMMIT_LNS, BUDGET[scale], pool)
    return rows + lns + matched_rows(table, inst, scale, lb, lns, h)


def table_c_sync(pool, seeds, table, T_ref):
    sink = Sink(table)
    for scale in ("Medium", "Large"):
        K, n = SCALES[scale]
        for seed in seeds:
            inst = generate_sync_instance(K, n, P=6, tightness=1.25, seed=seed, scale=scale)
            if inst.name in sink.done:
                continue
            t0 = time.perf_counter()
            rows = sync_rows(table, inst, scale, pool, T_ref)
            sink.write(rows)
            log(table, inst, rows, t0)


def table_e_sweep(pool):
    sink = Sink("E_sweep")
    K, n = SCALES["Large"]
    for eta in (0.85, 1.05, 1.45):
        for seed in TEST_SEEDS:
            inst = generate_instance(K, n, P=6, tightness=eta, seed=seed, scale="Large")
            if inst.name in sink.done:
                continue
            t0 = time.perf_counter()
            lp, lb, h = reference(inst, 30.0)
            save_ref(inst, "Large", 30.0, lp, lb, h, "E_sweep")
            rows = [lp_round_row("E_sweep", inst, "Large", lb),
                    highs_row("E_sweep", inst, "Large", lb, "HiGHS (30s)", obj_at(h["trace"], 30.0), 30.0, 1, h, "run")]
            lns = lns_rows("E_sweep", inst, "Large", lb, SWEEP_LNS, BUDGET["Large"], pool)
            rows += lns + matched_rows("E_sweep", inst, "Large", lb, lns, h)
            sink.write(rows)
            log("E_sweep", inst, rows, t0)


def ablation_configs():
    base = dict(L=3, commit="MC-CRIP", init_mode="lp_round", max_net=None, inner_iters=M_INNER)
    C = {}
    for duals, quota in (("heuristic", "static"), ("heuristic", "dynamic"), ("mccrip_lp", "static"),
                         ("mccrip_lp", "dynamic"), ("none", "dynamic"), ("none", "demand")):
        name = f"PC-MALNS [MC-CRIP; prices={duals}, quota={quota}]"
        C[name] = EngineConfig(name, duals=duals, quota=quota, **base)
    return C


def table_e_ablation(pool):
    sink = Sink("E_ablation")
    ref = ref_table()
    K, n = SCALES["Large"]
    cfg_map = ablation_configs()
    for seed in TEST_SEEDS:
        inst = generate_instance(K, n, P=6, tightness=1.25, seed=seed, scale="Large")
        if inst.name in sink.done:
            continue
        t0 = time.perf_counter()
        lb = float(ref.loc[inst.name, "lower_bound"])
        rows = lns_rows("E_ablation", inst, "Large", lb, list(cfg_map), BUDGET["Large"], pool,
                        counterfactual=False, cfg_map=cfg_map)
        sink.write(rows)
        log("E_ablation", inst, rows, t0)


def table_e_scaling():
    """Fixed number of epochs (identical search for every W): serial in-process run and
    pools with W = 1, 2, 4, 8 processes; one job at a time."""
    path = RAW / "bench_E_scaling.csv"
    rows = []
    cases = [("Large", 40), ("XXL", 20)]
    for W in (None, 1, 2, 4, 8):
        pool = AgentPool(W) if W is not None else None
        for scale, epochs in cases:
            K, n = SCALES[scale]
            for seed in (101, 102, 103):
                inst = generate_instance(K, n, P=6, tightness=1.25, seed=seed, scale=scale)
                lp_round_start(inst)  # warm the LP cache once; its measured time is charged
                cfg = configs()[PRIMARY]
                cfg.epochs, cfg.time_budget_s = epochs, None
                r = run_engine(inst, cfg, 1.0, seed=inst.seed, rep=0, pool=pool)
                rows.append(dict(scale=scale, K=K, seed=seed, epochs=epochs, mode="serial" if W is None else "pool",
                                 workers_W=1 if W is None else W, wall_clock_s=r.wall_clock_s,
                                 cpu_time_s=r.cpu_time_s, sim_parallel_s=r.sim_parallel_s,
                                 init_time_s=r.init_time_s, best_obj=r.best_obj,
                                 pool_startup_s=r.pool_startup_s))
                print(f"[E_scaling] W={W} {scale} s{seed} wall {r.wall_clock_s:.2f}s obj {r.best_obj:.2f}", flush=True)
        if pool is not None:
            pool.close()
    df = pd.DataFrame(rows)
    ser = df[df["mode"] == "serial"].set_index(["scale", "seed"])
    df["speedup_vs_serial"] = [ser.loc[(s, sd), "wall_clock_s"] / w for s, sd, w in
                               zip(df["scale"], df["seed"], df["wall_clock_s"])]
    df["same_obj_as_serial"] = [abs(ser.loc[(s, sd), "best_obj"] - o) < 1e-6 for s, sd, o in
                                zip(df["scale"], df["seed"], df["best_obj"])]
    df.to_csv(path, index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("table", choices=["A", "B", "C_direct", "C_sync", "sync_check", "E_sweep", "E_ablation",
                                      "E_scaling"])
    a = ap.parse_args()
    t0 = time.perf_counter()
    if a.table == "E_scaling":
        table_e_scaling()
    else:
        pool = AgentPool(W_MAIN)
        print(f"pool W={W_MAIN} startup {pool.startup_s:.2f}s", flush=True)
        {"A": lambda: table_a(pool), "B": lambda: table_b(pool), "C_direct": lambda: table_c_direct(pool),
         "C_sync": lambda: table_c_sync(pool, TEST_SEEDS, "C_sync", 60.0),
         "sync_check": lambda: table_c_sync(pool, VAL_SEEDS, "sync_check", 30.0),
         "E_sweep": lambda: table_e_sweep(pool), "E_ablation": lambda: table_e_ablation(pool)}[a.table]()
        pool.close()
    print(f"BENCH {a.table} done in {time.perf_counter() - t0:.0f}s", flush=True)
