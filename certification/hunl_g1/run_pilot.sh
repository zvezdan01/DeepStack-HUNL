#!/bin/bash
# HUNL turn datagen pilot driver (hardened after the 2026-08-14 local
# filesystem rollback): shard outputs are committed+pushed after every
# wave as explicit "NO VERDICT" provenance commits, so raw pilot data
# survive infrastructure resets. The certification verdict comes only
# from the separate gate harness after full QA.
set -e
QT=/home/user/quant-trade
DS=/workspace/deepstack_leduc_v1.1-bitexact-certified
cd "$DS"
export LD_LIBRARY_PATH=$DS
export PYTHONPATH=$QT:$DS
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
OUT=$QT/certification/hunl_datagen_pilot/shards
REP=$QT/certification/hunl_datagen_pilot/replay0
mkdir -p "$OUT" "$REP"
run() { python3 "$QT/hunl_datagen/turn_datagen.py" "$1" 20 "$2" > "$2/shard_$1.log" 2>&1; }
commit_wave() {
  cd "$QT"
  git add certification/hunl_datagen_pilot
  git commit -q -m "HUNL turn datagen pilot: raw shard data wave $1 (NO VERDICT — certification pending)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Ukr38aYmTxERgmibugSBz4" || true
  git push -q -u origin claude/huhl-deepstack-certification-tutg3b || \
    (git pull -q --rebase origin claude/huhl-deepstack-certification-tutg3b && \
     git push -q -u origin claude/huhl-deepstack-certification-tutg3b)
  cd "$DS"
}
w=0
for wave in "0 1 2 3" "4 5 6 7" "8 9 10 11"; do
  w=$((w+1))
  for s in $wave; do run "$s" "$OUT" & done
  wait
  echo "WAVE $w DONE"
  commit_wave "$w"
done
run 0 "$REP"
echo "REPLAY0 DONE"
commit_wave "replay"
echo "PILOT GENERATION COMPLETE"
