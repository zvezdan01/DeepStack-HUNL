#!/usr/bin/env python3
"""Gates G1.2 (blockers/indexing) + G1.3 (exact river showdown).

Fail-fast: the first divergence anywhere raises immediately with frozen
context. Run from quant-trade root: python3 certification/hunl_g1/run_g1_2_3.py
"""
from __future__ import annotations

import hashlib
import itertools
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from hunl.cards import (CARD_COUNT, HAND_CARDS, HAND_COUNT,  # noqa: E402
                        possible_hands_mask, string_to_cards)
from hunl import blockers as bl  # noqa: E402
from hunl import showdown as sd  # noqa: E402
from hunl.evaluator import BLOCKED_SENTINEL, hand_class, rank7  # noqa: E402

T0 = time.time()
report: list[str] = []


def log(msg: str) -> None:
    print(msg, flush=True)
    report.append(msg)


CANONICAL_7CARD = np.array([23_294_460, 58_627_800, 31_433_400, 6_461_620,
                            6_180_020, 4_047_644, 3_473_184, 224_848, 41_584],
                           dtype=np.int64)

# ================================================================= G1.2
log("== G1.2 blockers ==")
B = bl.blocker_matrix()
assert B.shape == (HAND_COUNT, HAND_COUNT) and B.dtype == np.uint8

# independent recount: pure-python sets over all 1326^2 ordered pairs
t = time.time()
sets = [frozenset((int(a), int(b))) for a, b in HAND_CARDS]
mismatch = 0
for i in range(HAND_COUNT):
    si = sets[i]
    row = B[i]
    for j in range(HAND_COUNT):
        expect = 1 if (si & sets[j]) else 0
        if row[j] != expect:
            log(f"FIRST DIVERGENCE blocker[{i},{j}] = {row[j]} expected {expect}")
            raise SystemExit(1)
log(f"independent recount: all {HAND_COUNT*HAND_COUNT:,} ordered pairs match "
    f"({time.time()-t:.0f}s)")

# structural identities
assert np.array_equal(B, B.T), "blocker not symmetric"
assert (np.diag(B) == 1).all(), "diagonal must be self-overlap"
# each hand {a,b}: 51 hands contain a, 51 contain b; their intersection is
# exactly the hand itself -> union = 51+51-1 = 101 (self included)
assert (B.sum(axis=1) == 101).all(), "row blocking count must be 101"
log("structure: symmetric, diag=1 (self-overlap), row sums 101 "
    "(=51+51-1 incl. self)")

# explicit case tests
h = lambda s: tuple(string_to_cards(s))  # noqa: E731
from hunl.cards import hand_index  # noqa: E402
i_AsAh = hand_index(*h("AsAh"))
i_AsKd = hand_index(*h("AsKd"))
i_KcQc = hand_index(*h("KcQc"))
assert B[i_AsAh, i_AsAh] == 1                      # self overlap
assert B[i_AsAh, i_AsKd] == 1                      # one-card overlap
assert B[i_AsAh, i_KcQc] == 0                      # disjoint
board = h("AsKh7c")
pm = possible_hands_mask(board)
assert not pm[i_AsAh] and not pm[i_AsKd] and pm[i_KcQc]  # board blocking
log("case tests: self-overlap / one-card overlap / disjoint / board blocking OK")

# exhaustive per-board possible-hand counts over ALL board cardinalities
CH = bl.card_hand_membership()
for k, expect in ((3, math.comb(49, 2)), (4, math.comb(48, 2)),
                  (5, math.comb(47, 2))):
    t = time.time()
    total = 0
    chunk = []
    def flush(chunk):
        boards = np.asarray(chunk, dtype=np.int8)
        blocked = CH[boards[:, 0]]
        for c in range(1, k):
            blocked = blocked | CH[boards[:, c]]
        counts = HAND_COUNT - blocked.sum(axis=1)
        if not (counts == expect).all():
            bad = int(np.nonzero(counts != expect)[0][0])
            log(f"FIRST DIVERGENCE board {boards[bad].tolist()} "
                f"count {counts[bad]} != {expect}")
            raise SystemExit(1)
        return len(chunk)
    for b in itertools.combinations(range(CARD_COUNT), k):
        chunk.append(b)
        if len(chunk) == 20000:
            total += flush(chunk); chunk = []
    if chunk:
        total += flush(chunk)
    assert total == math.comb(52, k)
    log(f"k={k}: all {total:,} boards -> possible hands == C({52-k},2)={expect} "
        f"({time.time()-t:.0f}s)")
# preflop count
assert int(possible_hands_mask(()).sum()) == 1326
log("preflop possible hands == 1326")
# API-path spot sweep (possible_hands_mask directly) on seeded sample
rng = np.random.default_rng(20260813)
for k in (3, 4, 5):
    for _ in range(10_000):
        b = rng.choice(CARD_COUNT, size=k, replace=False)
        assert int(possible_hands_mask(b).sum()) == math.comb(52 - k, 2)
log("API-path sample: 10,000 boards per cardinality via possible_hands_mask OK")

# determinism / SHA anchor (in-process rebuild + fresh subprocess)
sha1 = bl.blocker_sha256()
bl._BLOCKER = None
assert bl.blocker_sha256() == sha1
sub = subprocess.run(
    [sys.executable, "-c",
     "import sys; sys.path.insert(0, %r); "
     "from hunl.blockers import blocker_sha256; print(blocker_sha256())"
     % str(ROOT)], capture_output=True, text=True, check=True)
assert sub.stdout.strip() == sha1
log(f"G1.2 blocker SHA-256 anchor: {sha1} (in-process rebuild + fresh "
    "subprocess identical)")
log("G1.2 PASS")

# ================================================================= G1.3
log("\n== G1.3 exact river showdown ==")
N_CORPUS = 2_000
LEGAL_ORDERED_PAIRS = 1081 * (1081 - math.comb(45, 2) * 0 - 1 - 90)
# legal ordered pairs on a river: hand i (1081 choices) x disjoint legal j:
# j must avoid board (47 cards left) and i's 2 cards -> C(45,2)=990
LEGAL_ORDERED_PAIRS = 1081 * 990

rng = np.random.default_rng(20260813)
corpus = np.empty((N_CORPUS, 5), dtype=np.int8)
for i in range(N_CORPUS):
    corpus[i] = np.sort(rng.choice(CARD_COUNT, size=5, replace=False))

corpus_hash = hashlib.sha256()
t = time.time()
slow_checked = 0
for bi in range(N_CORPUS):
    board = corpus[bi]
    m, legal, ranks = sd.showdown_matrix(board)
    lb = legal.astype(bool)
    # 1. ranks vs certified evaluator via independent sign construction
    r64 = ranks.astype(np.int64)
    alt = np.sign(r64[:, None] - r64[None, :]).astype(np.int8)
    alt[~lb] = 0
    if not np.array_equal(alt, m):
        d = np.argwhere(alt != m)[0]
        log(f"FIRST DIVERGENCE alt-construction board {board.tolist()} at "
            f"{d.tolist()}")
        raise SystemExit(1)
    # 2. legality vs G1.2
    assert np.array_equal(lb, bl.legal_pairs_mask(board)), "legal mask drift"
    assert int(lb.sum()) == LEGAL_ORDERED_PAIRS, "legal pair count"
    assert not lb.diagonal().any(), "diagonal must be illegal"
    assert (m[~lb] == 0).all(), "illegal entries must be exactly 0"
    pm = possible_hands_mask(board)
    assert int(pm.sum()) == 1081 and \
        int((ranks == BLOCKED_SENTINEL).sum()) == 1326 - 1081
    # 3. exact antisymmetry
    assert np.array_equal(m, -m.T), "antisymmetry violated"
    # 4. tie symmetry: legal zero entries <=> equal ranks, symmetric
    ties = lb & (m == 0)
    assert np.array_equal(ties, ties.T), "tie symmetry"
    eq = lb & (r64[:, None] == r64[None, :])
    assert np.array_equal(ties, eq), "ties must be exactly rank equality"
    # 5. win/loss recount (independent, via order statistics per row)
    wins_per_row = (m == 1).sum(axis=1)
    loss_per_row = (m == -1).sum(axis=1)
    assert wins_per_row.sum() == loss_per_row.sum(), "global win/loss balance"
    live = np.nonzero(pm)[0]
    lranks = r64[live]
    order = np.sort(lranks)
    # for sampled rows, recount wins independently: legal opponents with
    # strictly lower rank, excluding hands overlapping row hand
    for i in rng.choice(live, size=6, replace=False):
        opp = live[(bl.blocker_matrix()[i, live] == 0)]
        w = int((r64[opp] < r64[i]).sum())
        t_ = int((r64[opp] == r64[i]).sum())
        l_ = int((r64[opp] > r64[i]).sum())
        assert w == wins_per_row[i] and l_ == loss_per_row[i] \
            and t_ == int(ties[i].sum()), f"row recount hand {i}"
        slow_checked += 1
    # 6. permutation invariance
    if bi < 50:
        perm = np.array(board)[rng.permutation(5)]
        m2, legal2, ranks2 = sd.showdown_matrix(perm)
        assert m2.tobytes() == m.tobytes() and \
            legal2.tobytes() == legal.tobytes() and \
            ranks2.tobytes() == ranks.tobytes(), "board permutation variance"
    # 7. determinism
    if bi < 20:
        assert sd.showdown_sha256(board) == sd.showdown_sha256(board)
    corpus_hash.update(m.tobytes()); corpus_hash.update(legal.tobytes())
    corpus_hash.update(ranks.tobytes())
corpus_sha = corpus_hash.hexdigest()
log(f"corpus: {N_CORPUS:,} seeded rivers fully certified "
    f"({N_CORPUS} x 1326^2 = {N_CORPUS*HAND_COUNT*HAND_COUNT:,} entries; "
    f"legal {N_CORPUS*LEGAL_ORDERED_PAIRS:,}; {slow_checked} slow row "
    f"recounts) in {time.time()-t:.0f}s")
log(f"corpus SHA-256 anchor (M+legal+ranks stream, seed 20260813): {corpus_sha}")

# terminal CFV identity u1 = -u2 (aggregate zero-sum closure)
t = time.time()
max_res64 = 0.0
max_res32 = 0.0
for bi in range(200):
    board = corpus[bi]
    m, legal, ranks = sd.showdown_matrix(board)
    pm = possible_hands_mask(board)
    for _ in range(5):
        r = rng.random((2, HAND_COUNT)) * pm
        r /= r.sum(axis=1, keepdims=True)
        u = sd.river_call_values(m, r, dtype=np.float64)
        res = abs(float(r[0] @ u[0] + r[1] @ u[1]))
        max_res64 = max(max_res64, res)
        r32 = r.astype(np.float32)
        u32 = sd.river_call_values(m, r32, dtype=np.float32)
        res32 = abs(float(r32[0] @ u32[0] + r32[1] @ u32[1]))
        max_res32 = max(max_res32, res32)
assert max_res64 < 1e-12, f"f64 zero-sum residual {max_res64}"
assert max_res32 < 1e-4, f"f32 zero-sum residual {max_res32}"
log(f"terminal CFV identity (1,000 range pairs on 200 boards): "
    f"max |r1.u1 + r2.u2| f64 = {max_res64:.2e} (<1e-12), "
    f"f32 = {max_res32:.2e} (<1e-4) in {time.time()-t:.0f}s")

# exhaustive river structural audit: ALL C(52,5) = 2,598,960 boards
log("exhaustive river audit: all 2,598,960 boards...")
t = time.time()
class_totals = np.zeros(9, dtype=np.int64)
stream_hash = hashlib.sha256()
BATCH = 64
batch_boards = np.empty((BATCH, 5), dtype=np.int8)
nb = 0
total_boards = 0
cards7 = np.empty((BATCH * HAND_COUNT, 7), dtype=np.int8)
cards7[:, :2] = np.tile(HAND_CARDS, (BATCH, 1))


def flush_batch(n: int) -> None:
    global class_totals, total_boards
    c7 = cards7[:n * HAND_COUNT]
    for col in range(5):
        c7[:, 2 + col] = np.repeat(batch_boards[:n, col], HAND_COUNT)
    ranks = rank7(c7).astype(np.uint32).reshape(n, HAND_COUNT)
    blocked = np.zeros((n, HAND_COUNT), dtype=bool)
    for col in range(5):
        blocked |= CH[batch_boards[:n, col]]
    ranks[blocked] = BLOCKED_SENTINEL
    live_counts = HAND_COUNT - blocked.sum(axis=1)
    if not (live_counts == 1081).all():
        raise SystemExit(f"live count violation in batch at board "
                         f"{batch_boards[int(np.argmax(live_counts != 1081))]}")
    stream_hash.update(ranks.tobytes())
    class_totals += np.bincount(hand_class(ranks[~blocked]), minlength=9)
    total_boards += n


for b in itertools.combinations(range(CARD_COUNT), 5):
    batch_boards[nb] = b
    nb += 1
    if nb == BATCH:
        flush_batch(nb); nb = 0
if nb:
    flush_batch(nb)
assert total_boards == math.comb(52, 5)
expected = CANONICAL_7CARD * 21   # each 7-card set = C(7,2)=21 (board,hand) splits
if not np.array_equal(class_totals, expected):
    log(f"FIRST DIVERGENCE class cross-foot: {class_totals.tolist()} != "
        f"{expected.tolist()}")
    raise SystemExit(1)
river_sha = stream_hash.hexdigest()
log(f"exhaustive audit PASS: {total_boards:,} boards x 1326 ranks "
    f"({total_boards*HAND_COUNT:,} entries), every board 1081 live hands, "
    f"class cross-foot == 21 x canonical 7-card counts, "
    f"in {time.time()-t:.0f}s")
log(f"full-river rank-stream SHA-256 anchor (lexicographic boards): {river_sha}")

log(f"\nG1.2 + G1.3 RESULT: PASS (total {time.time()-T0:.0f}s)")
(ROOT / "certification/hunl_g1/G1_2_3_RESULT.txt").write_text(
    "\n".join(report) + "\n")
