#!/bin/bash
# Revision 3, wall-clock jobs (run after scripts/run_revision3.sh; strictly one at a time).
set -e
cd "$(dirname "$0")/.."
PY=${PY:-python}
for j in async highs_main highs_rich highs_sweep highs_pair mmkp; do
  $PY scripts/run_wallclock_revision3.py $j >> results/logs/wall_$j.log 2>&1
done
