#!/bin/bash
# HUNL turn datagen pilot driver v3 (hardened):
#  - per-wave commits+push of raw shard data (NO VERDICT) — survives
#    container rollbacks;
#  - 3 concurrent single-thread workers (4x ~4 GB peaked above the 15 GB
#    cgroup and OOM-killed a worker on 2026-08-16; generator also gc's
#    between samples now);
#  - retry loop: waves are followed by passes that regenerate any shard
#    with a missing manifest (deterministic from seeds; completed shards
#    are skipped by the generator's manifest check).
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
run() { python3 "$QT/hunl_datagen/turn_datagen.py" "$1" 20 "$2" >> "$2/shard_$1.log" 2>&1; }
commit_wave() {
  cd "$QT"
  git add certification/hunl_datagen_pilot
  git commit -q -m "HUNL turn datagen pilot: raw shard data checkpoint $1 (NO VERDICT — certification pending)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Ukr38aYmTxERgmibugSBz4" || true
  git push -q -u origin claude/huhl-deepstack-certification-tutg3b || \
    (git pull -q --rebase origin claude/huhl-deepstack-certification-tutg3b && \
     git push -q -u origin claude/huhl-deepstack-certification-tutg3b)
  cd "$DS"
}
for pass in 1 2 3; do
  pending=""
  for s in 0 1 2 3 4 5 6 7 8 9 10 11; do
    [ -f "$OUT/shard_$(printf '%05d' "$s").json" ] || pending="$pending $s"
  done
  [ -z "$pending" ] && break
  echo "PASS $pass pending:$pending"
  n=0
  for s in $pending; do
    run "$s" "$OUT" &
    n=$((n+1))
    if [ "$n" -ge 3 ]; then wait; commit_wave "p${pass}"; n=0; fi
  done
  wait
  commit_wave "p${pass}-end"
done
missing=0
for s in 0 1 2 3 4 5 6 7 8 9 10 11; do
  [ -f "$OUT/shard_$(printf '%05d' "$s").json" ] || missing=$((missing+1))
done
[ "$missing" -eq 0 ] || { echo "PILOT INCOMPLETE: $missing shards missing after 3 passes"; exit 1; }
[ -f "$REP/shard_00000.json" ] || run 0 "$REP"
commit_wave "replay"
echo "PILOT GENERATION COMPLETE"
