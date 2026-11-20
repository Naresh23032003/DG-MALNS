#!/bin/bash
# Revision 3 experiments, strictly one job at a time (resumable; logs in results/logs/).
# Deterministic work-protocol tables first, then the wall-clock jobs.
set -e
cd "$(dirname "$0")/.."
PY=${PY:-python}
for t in main validation commit_direct commit_pair levels prices restart; do
  $PY scripts/run_work_protocol.py $t >> results/logs/work_$t.log 2>&1
done
# then the wall-clock jobs:
# ./scripts/run_revision3_wall.sh
