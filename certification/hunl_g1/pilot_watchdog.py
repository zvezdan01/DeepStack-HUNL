#!/usr/bin/env python3
"""HUNL pilot watchdog: every 30 min check worker PIDs, CPU-time deltas
(/proc/<pid>/stat) and per-shard log size/mtime. SUSPECT only when CPU
AND log are both frozen for >=2 consecutive checks; silence alone is
never a restart reason. Exits 0 on completion, 1 when pilot is dead."""
import json, os, time, glob, sys
STATE = "/tmp/pilot_watch_state.json"
SH = "/home/user/quant-trade/certification/hunl_datagen_pilot/shards"
REP = "/home/user/quant-trade/certification/hunl_datagen_pilot/replay0"

def workers():
    out = {}
    for pid in os.listdir("/proc"):
        if not pid.isdigit(): continue
        try:
            cmd = open(f"/proc/{pid}/cmdline").read().split("\0")
            hits = [c for c in cmd if "turn_datagen.py" in c]
            if hits:
                shard = cmd[cmd.index(hits[0]) + 1]
                st = open(f"/proc/{pid}/stat").read().split()
                out[pid] = (int(shard), int(st[13]) + int(st[14]))
        except Exception: pass
    return out

def driver_alive():
    for pid in os.listdir("/proc"):
        if not pid.isdigit(): continue
        try:
            if "run_pilot.sh" in open(f"/proc/{pid}/cmdline").read(): return True
        except Exception: pass
    return False

prev = json.load(open(STATE)) if os.path.exists(STATE) else {}
while True:
    done = len(glob.glob(f"{SH}/shard_*.json"))
    replay = len(glob.glob(f"{REP}/shard_*.json")) > 0
    if done >= 12 and replay:
        print("PILOT COMPLETE: 12/12 shards + replay0"); sys.exit(0)
    w = workers(); drv = driver_alive()
    if not w and not drv:
        print(f"PILOT DEAD: no driver/workers, {done}/12 shards done — restart needed"); sys.exit(1)
    now = time.time(); cur = {}; ok = []; sus = []
    for pid, (shard, cpu) in sorted(w.items(), key=lambda x: x[1][0]):
        log = f"{SH}/shard_{shard}.log"
        try: lsize, lm = os.path.getsize(log), os.path.getmtime(log)
        except OSError: lsize, lm = 0, 0
        p = prev.get(pid, {})
        stalled = p and cpu == p.get("cpu") and lsize == p.get("lsize")
        strikes = p.get("strikes", 0) + 1 if stalled else 0
        cur[pid] = {"cpu": cpu, "lsize": lsize, "strikes": strikes}
        tag = f"shard{shard} pid{pid} cpu+{cpu - p.get('cpu', cpu)}j log{lsize}B/{int((now-lm)/60) if lm else '?'}m"
        (sus if strikes >= 2 else ok).append(tag)
    prev = cur; json.dump(cur, open(STATE, "w"))
    line = (f"{time.strftime('%H:%M:%S')} {len(w)} workers "
            f"[{'; '.join(ok)}] drv={drv} {done}/12 shards, replay={replay}")
    with open("/tmp/pilot_watch.log", "a") as f:
        f.write(line + "\n")
    if sus:
        # actionable event: exit so the supervisor wakes up exactly once
        print(f"SUSPECT (cpu+log frozen >=2 checks): {'; '.join(sus)} | "
              f"healthy: {'; '.join(ok)} | {done}/12")
        sys.exit(2)
    time.sleep(1800)
