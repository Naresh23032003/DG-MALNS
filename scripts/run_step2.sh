#!/bin/zsh
# Step 2 benchmark suite: every job strictly one at a time (no concurrent CPU work).
# Each table script is resumable per instance; rerunning this file continues where it stopped.
set -e
cd "$(dirname "$0")/.."
PY=${PYTHON:-/opt/homebrew/bin/python3.11}
mkdir -p results/logs
for t in A C_direct E_ablation C_sync B E_sweep; do
  $PY -u scripts/run_benchmark.py $t >> results/logs/bench_$t.log 2>&1
done
$PY -u scripts/run_mmkp_benchmarks.py >> results/logs/bench_D_mmkp.log 2>&1
[ -f results/raw/bench_E_scaling.csv ] || $PY -u scripts/run_benchmark.py E_scaling >> results/logs/bench_E_scaling.log 2>&1
echo "STEP2 DONE $(date)" >> results/logs/step2.log
