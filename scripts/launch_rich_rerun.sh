#!/bin/bash
# Sensitivity rerun of the slow stretch in rich (results/rerun_plan.md, addendum 2026-11-20).
# Usage:  bash scripts/launch_rich_rerun.sh
cd "$(dirname "$0")/.."
if pgrep -f run_wallclock_uniform.py > /dev/null; then echo "a wall-clock job is already running"; exit 1; fi
pmset -g batt | grep -q "AC Power" || { echo "not on AC power"; exit 1; }
mkdir -p results/logs
PY=${PY:-/opt/homebrew/bin/python3.11}
nohup caffeinate -dimsu $PY scripts/run_wallclock_uniform.py rich_rerun >> results/logs/uniform_queue.log 2>&1 &
sleep 2
ps -Ao pid,nice,etime,command | grep -E "caffeinate|run_wallclock_uniform" | grep -v grep
echo "log: results/logs/uniform_rich_rerun.log"
