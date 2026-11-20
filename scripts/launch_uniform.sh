#!/bin/bash
# Start the uniform wall-clock queue (results/rerun_plan.md) detached from the calling
# shell, at normal priority (zsh would lower the priority of a background job) and
# with sleep prevented. Usage:  bash scripts/launch_uniform.sh
cd "$(dirname "$0")/.."
if pgrep -f run_uniform_queue.sh > /dev/null; then echo "queue already running"; exit 1; fi
pmset -g batt | grep -q "AC Power" || { echo "not on AC power"; exit 1; }
mkdir -p results/logs
nohup caffeinate -dimsu bash scripts/run_uniform_queue.sh > /dev/null 2>&1 &
sleep 2
ps -Ao pid,nice,etime,command | grep -E "caffeinate|run_uniform_queue|run_wallclock_uniform" | grep -v grep
echo "log: results/logs/uniform_queue.log"
