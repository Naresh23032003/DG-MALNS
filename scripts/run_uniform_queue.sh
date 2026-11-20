#!/bin/bash
# Revision 3: wall-clock rerun under uniform machine conditions, then the phase-3
# work-protocol tables (results/rerun_plan.md). Strictly one job at a time.
# Launch:  caffeinate -dimsu bash scripts/run_uniform_queue.sh
set -e
cd "$(dirname "$0")/.."
PY=${PY:-/opt/homebrew/bin/python3.11}
mkdir -p results/logs
for j in main rich sweep pair mmkp; do                       # phases 1 and 2
  $PY scripts/run_wallclock_uniform.py $j >> results/logs/uniform_queue.log 2>&1
done
for t in prices_fresh rho0; do                               # phase 3
  $PY scripts/run_work_protocol.py $t >> results/logs/work_$t.log 2>&1
done
echo "$(date '+%Y-%m-%d %H:%M:%S') UNIFORM QUEUE done" >> results/logs/uniform_queue.log
