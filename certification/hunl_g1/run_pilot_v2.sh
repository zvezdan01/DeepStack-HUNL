#!/bin/bash
# HUNL turn datagen pilot driver v2 — restart of the 2026-08-14 pilot
# after the container reclaim killed wave 1 (no shard data survived; the
# wave-1 logs on the old branch are 0-byte). Deltas vs the frozen
# run_pilot.sh: (a) branch + session provenance strings updated to this
# session; (b) the DS workspace is a placeholder directory (engine =
# in-repo hunl/ + restored datagen/th_random.py, see thrandom_oracle/);
# (c) push retries with backoff. Wave structure, output layout, seeds,
# and per-wave NO-VERDICT provenance commits are UNCHANGED.
set -e
QT=/home/user/quant-trade
DS=/workspace/deepstack_leduc_v1.1-bitexact-certified
BR=claude/generator-dat-pro-huhl-forenzic-rvclmx
cd "$DS"
export LD_LIBRARY_PATH=$DS
export PYTHONPATH=$QT:$DS
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
OUT=$QT/certification/hunl_datagen_pilot/shards
REP=$QT/certification/hunl_datagen_pilot/replay0
mkdir -p "$OUT" "$REP"
run() { python3 "$QT/hunl_datagen/turn_datagen.py" "$1" 20 "$2" > "$2/shard_$1.log" 2>&1; }
push_retry() {
  for d in 0 2 4 8 16; do
    sleep "$d"
    git push -q -u origin "$BR" && return 0
    git pull -q --rebase origin "$BR" || true
  done
  echo "PUSH FAILED after retries" >&2; return 1
}
commit_wave() {
  cd "$QT"
  git add certification/hunl_datagen_pilot
  git commit -q -m "HUNL turn datagen pilot v2: raw shard data wave $1 (NO VERDICT — certification pending)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Se6m4Dpzr7kPan6kHCTitX" || true
  push_retry || true
  cd "$DS"
}
w=0
for wave in "0 1 2 3" "4 5 6 7" "8 9 10 11"; do
  w=$((w+1))
  # v2.1: a wave is complete only when every shard manifest exists.
  # Workers can die (observed: OOM kill of one worker, 2026-08-14) and
  # bare `wait` does not surface that; missing shards are respawned and
  # resume from their per-sample checkpoints. Log lines are appended
  # (>>) so evidence of earlier attempts survives.
  attempt=0
  while true; do
    missing=""
    for s in $wave; do
      [ -f "$OUT/$(printf 'shard_%05d.json' "$s")" ] || missing="$missing $s"
    done
    [ -z "$missing" ] && break
    attempt=$((attempt+1))
    if [ "$attempt" -gt 25 ]; then echo "WAVE $w STUCK: missing$missing" >&2; exit 1; fi
    echo "WAVE $w attempt $attempt: running shards:$missing"
    for s in $missing; do
      python3 "$QT/hunl_datagen/turn_datagen.py" "$s" 20 "$OUT" >> "$OUT/shard_$s.log" 2>&1 &
    done
    wait
  done
  echo "WAVE $w DONE"
  commit_wave "$w"
done
attempt=0
until [ -f "$REP/shard_00000.json" ]; do
  attempt=$((attempt+1))
  [ "$attempt" -gt 25 ] && { echo "REPLAY0 STUCK" >&2; exit 1; }
  python3 "$QT/hunl_datagen/turn_datagen.py" 0 20 "$REP" >> "$REP/shard_0.log" 2>&1
done
echo "REPLAY0 DONE"
commit_wave "replay"
echo "PILOT GENERATION COMPLETE"
