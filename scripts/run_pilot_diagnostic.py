"""
Pilot diagnostic (Step 1 of the revision-2 protocol).

Runs ONLY on validation seeds 1..3 (disjoint from the test seeds 101..110), so the
configuration chosen here is not selected on the test instances.

Instances: Medium (K = 8, N = 320) and Large (K = 12, N = 600), eta_tight in
{1.25, 1.45}, P in {6, 20} patterns per request -> 24 instances.
All runs are serial with an equal CPU budget (start time included):
Medium 2.0 s, Large 3.0 s. Runs execute strictly one at a time.

Stage ref  HiGHS (1 thread, 30 s) per instance: lower bound LB = max(LP bound,
           HiGHS dual bound); reference objective. -> results/raw/pilot_reference.csv
Stage A    regime: MC-CRIP (no prices, static quota) x init_mode {direct, booking,
           lp_round} x max_net {3, None} x inner_iters M {1, 5}, with counterfactual
           barrier logging. -> results/raw/pilot_stageA.csv
Stage B    in the chosen regime (command-line flags): all commit rules / baselines and
           MC-CRIP x prices {none, heuristic, mccrip_lp} x quotas {static, dynamic}.
           -> results/raw/pilot_stageB_<init>.csv
Stage C    real wall clock: MC-CRIP on a persistent W = 4 agent pool versus HiGHS
           (1 and 4 threads) with the same wall-clock limit. -> results/raw/pilot_stageC.csv
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
from src.baselines import solve_lp_relaxation
from src.engine import run_engine, method_configs, EngineConfig, primal_integral
from src.highs_runner import solve_highs
from src.agent_pool import AgentPool

RAW = REPO_ROOT / "results" / "raw"
VAL_SEEDS = [1, 2, 3]
SCALES = [("Medium", 8, 40, 2.0), ("Large", 12, 50, 3.0)]
ETAS = [1.25, 1.45]
PS = [6, 20]
REF_S = 30.0


def instances():
    for scale, K, n, budget in SCALES:
        for eta in ETAS:
            for P in PS:
                for seed in VAL_SEEDS:
                    yield scale, budget, generate_instance(K, n, P=P, tightness=eta, seed=seed, scale=scale)


def reference():
    path = RAW / "pilot_reference.csv"
    if path.exists():
        return pd.read_csv(path).set_index("instance_name")
    rows = []
    for scale, budget, inst in instances():
        lp = solve_lp_relaxation(inst)["lp_bound"]
        h = solve_highs(inst, REF_S, threads=1)
        lb = max(lp, h["dual_bound"]) if np.isfinite(h["dual_bound"]) else lp
        rows.append(dict(instance_name=inst.name, scale=scale, K=inst.K, P=inst.P, eta=inst.tightness,
                         seed=inst.seed, lp_bound=lp, highs30_obj=h["obj"], highs30_dual=h["dual_bound"],
                         highs30_status=h["status"], highs30_time_s=h["highs_actual_time_s"], lower_bound=min(lb, h["obj"])))
        print(f"[ref] {inst.name} LP {lp:.1f} HiGHS30 {h['obj']:.1f} dual {h['dual_bound']:.1f} {h['status']}", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
    return df.set_index("instance_name")


def res_row(scale, inst, r, extra=None):
    d = dict(instance_name=inst.name, scale=scale, K=inst.K, P=inst.P, eta=inst.tightness, seed=inst.seed,
             method=r.method, init_mode=r.config["init_mode"], max_net=str(r.config["max_net"]),
             inner_iters=r.config["inner_iters"], duals=r.config["duals"], quota=r.config["quota"],
             commit=r.config["commit"], L=r.config["L"],
             best_obj=r.best_obj, initial_obj=r.initial_obj, lower_bound=r.lower_bound, gap_pct=r.gap_pct,
             feasible=r.feasible, wall_clock_s=r.wall_clock_s, cpu_time_s=r.cpu_time_s,
             sim_parallel_s=r.sim_parallel_s, init_time_s=r.init_time_s, workers_W=r.workers_W,
             epochs_run=r.epochs_run, conflict_epochs=r.conflict_epochs,
             conflict_rate_pct=100.0 * r.conflict_epochs / max(1, r.epochs_run),
             accepted_moves=r.accepted_moves, proposals=r.proposals,
             matcher_ms_mean=r.matcher_ms_mean, matcher_fallbacks=r.matcher_fallbacks,
             primal_integral=r.primal_integral, cf_sum=json.dumps(r.cf_sum),
             cf_strict_wins=json.dumps(r.cf_strict_wins))
    if extra:
        d.update(extra)
    if not r.feasible:
        raise RuntimeError(f"infeasible: {r.method} {inst.name}")
    return d


def stage_a(ref):
    rows = []
    for scale, budget, inst in instances():
        lb = float(ref.loc[inst.name, "lower_bound"])
        for init in ("direct", "booking", "lp_round"):
            for max_net in (3, None):
                for M in (1, 5):
                    cfg = method_configs(init_mode=init, max_net=max_net, inner_iters=M)["MC-CRIP"]
                    cfg.name = f"MC-CRIP[{init},net={max_net},M={M}]"
                    cfg.time_budget_s, cfg.budget_clock, cfg.counterfactual = budget, "cpu", True
                    r = run_engine(inst, cfg, lb, seed=inst.seed)
                    rows.append(res_row(scale, inst, r))
        last = pd.DataFrame(rows[-12:])
        print(f"[A] {inst.name} " + " ".join(f"{m.split('[')[1][:-1]}={g:.2f}/{c:.0f}%"
              for m, g, c in zip(last.method, last.gap_pct, last.conflict_rate_pct)), flush=True)
    pd.DataFrame(rows).to_csv(RAW / "pilot_stageA.csv", index=False)


def stage_b(ref, init, max_net, M):
    rows = []
    for scale, budget, inst in instances():
        lb = float(ref.loc[inst.name, "lower_bound"])
        cfgs = list(method_configs(init_mode=init, max_net=max_net, inner_iters=M).values())
        for duals in ("heuristic", "mccrip_lp"):
            for quota in ("static", "dynamic"):
                cfgs.append(EngineConfig(f"MC-CRIP[{duals},{quota}]", L=3, commit="MC-CRIP", duals=duals,
                                         quota=quota, init_mode=init, max_net=max_net, inner_iters=M))
        cfgs.append(EngineConfig("MC-CRIP[none,dynamic]", L=3, commit="MC-CRIP", duals="none",
                                 quota="dynamic", init_mode=init, max_net=max_net, inner_iters=M))
        for cfg in cfgs:
            cfg.time_budget_s, cfg.budget_clock = budget, "cpu"
            cfg.counterfactual = cfg.name == "MC-CRIP"
            r = run_engine(inst, cfg, lb, seed=inst.seed)
            rows.append(res_row(scale, inst, r))
        last = pd.DataFrame(rows[-len(cfgs):])
        print(f"[B] {inst.name} " + " ".join(f"{m}={g:.2f}" for m, g in zip(last.method, last.gap_pct)), flush=True)
    pd.DataFrame(rows).to_csv(RAW / f"pilot_stageB_{init}.csv", index=False)


def stage_c(ref, init, max_net, M, W=4):
    rows = []
    pool = AgentPool(W)
    for scale, budget, inst in instances():
        lb = float(ref.loc[inst.name, "lower_bound"])
        for wall_budget in (budget / 2.0, budget):
            cfg = method_configs(init_mode=init, max_net=max_net, inner_iters=M)["MC-CRIP"]
            cfg.time_budget_s, cfg.budget_clock = wall_budget, "wall"
            r = run_engine(inst, cfg, lb, seed=inst.seed, pool=pool)
            rows.append(res_row(scale, inst, r, dict(wall_budget_s=wall_budget, pool_startup_s=pool.startup_s)))
            for th in (1, 4):
                h = solve_highs(inst, r.wall_clock_s, threads=th)
                obj = h["obj"] if np.isfinite(h["obj"]) else r.initial_obj
                tt = [t for t, _ in h["trace"]]
                to = [o for _, o in h["trace"]]
                rows.append(dict(instance_name=inst.name, scale=scale, K=inst.K, P=inst.P, eta=inst.tightness,
                                 seed=inst.seed, method=f"HiGHS ({th}T, wall-matched)", best_obj=obj,
                                 lower_bound=lb, gap_pct=max(0.0, 100 * (obj - lb) / lb), feasible=True,
                                 wall_clock_s=h["highs_actual_time_s"], highs_time_limit_s=h["highs_time_limit_s"],
                                 highs_actual_time_s=h["highs_actual_time_s"], highs_status=h["status"],
                                 threads=th, wall_budget_s=wall_budget,
                                 primal_integral=primal_integral([0.0] + tt, [None] + to, lb, h["highs_actual_time_s"])))
        last = pd.DataFrame(rows[-6:])
        print(f"[C] {inst.name} " + " ".join(f"{m}={g:.2f}({w:.2f}s)" for m, g, w in
                                          zip(last.method, last.gap_pct, last.wall_clock_s)), flush=True)
    pool.close()
    pd.DataFrame(rows).to_csv(RAW / "pilot_stageC.csv", index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["ref", "A", "B", "C"])
    ap.add_argument("--init", default="booking")
    ap.add_argument("--max-net", default="none")
    ap.add_argument("--M", type=int, default=1)
    a = ap.parse_args()
    mn = None if a.max_net.lower() == "none" else int(a.max_net)
    t0 = time.perf_counter()
    ref = reference()
    if a.stage == "A":
        stage_a(ref)
    elif a.stage == "B":
        stage_b(ref, a.init, mn, a.M)
    elif a.stage == "C":
        stage_c(ref, a.init, mn, a.M)
    print(f"PILOT {a.stage} done in {time.perf_counter() - t0:.0f}s", flush=True)
