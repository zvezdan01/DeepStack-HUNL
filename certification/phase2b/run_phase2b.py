#!/usr/bin/env python3
"""Phase 2B — production dataset generation over the CERTIFIED datagen path.

Everything numeric goes through the read-only certified code:
  - engine: Golden Baseline v1.0  (DS branch golden-baseline-v1.0-m2m4 @ 2ab6dde…)
  - datagen: certified generator  (DS branch phase2-datagen @ 7967622…)
This runner only orchestrates: seed derivation, sharding, workers, QA,
audit resolves, manifests. It contains NO sampling or solver math.

Run from the DS repo root:
  LD_LIBRARY_PATH=$PWD PYTHONPATH=. python3 run_phase2b.py generate
  LD_LIBRARY_PATH=$PWD PYTHONPATH=. python3 run_phase2b.py finalqa
  LD_LIBRARY_PATH=$PWD PYTHONPATH=. python3 run_phase2b.py replay

Fail-fast policy: any anomaly (non-finite value, malformed shard, audit
mismatch, SHA mismatch) raises immediately; the failing shard's temp files
are left in place for inspection; completed shards are never rewritten.
There are no retries at any level. The only rejection loop anywhere is the
board sampler inside the certified generator itself, which is part of the
original algorithm (random_card_generator.lua) and its RNG draws are part
of the certified stream.
"""
from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import os
import random
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------- constants
MASTER_SEED = 20260813
SHARD_SIZE = 1000              # samples per shard; 100 batches of 10
VALID_SHARDS = list(range(0, 10))      # shards 0000-0009  -> validation
TRAIN_SHARDS = list(range(10, 110))    # shards 0010-0109  -> training
ALL_SHARDS = VALID_SHARDS + TRAIN_SHARDS
AUDIT_ROWS_PER_SHARD = 2
TARGET_ABS_BOUND = 12.5        # theory: |cfv|/pot <= stack/min_pot = 12;
                               # certified data max 8.42
REPLAY_SHARDS = [0, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 109]

ENGINE_SHA = '2ab6dde943ebad2f5458779dc561ed203f796e39'
DATAGEN_SHA = '7967622e5b66e35a8e9a17506f97db86c2e6b543'
WEIGHTS_SHA = 'd5fcba4402cec46a9b02cea0f96cb78bda83f284ea36f6d5db84529e83eb59a1'
PILOT_SEED = 20260812
PILOT_SHAS = {                 # certified Phase-2A appendix (both runs)
    'valid.inputs': '725d0e9956d56e056c5690739cdfcd490a338e818a5e672567235de5c002234a',
    'valid.targets': '492be8c99c89a772917d05640cfd0a0261915fe11f1f34093ab0633178fcb91f',
    'valid.mask': '443ff6cc22cbbe49f96627a97e5b6a9f9835a8394dbafaaef8d0a95111d9ef4f',
    'train.inputs': '7d23fa31b18d998b21d2e8b1ba74633a4014c8db07d88b06bc3051cb4891bc81',
    'train.targets': '120d8d40dc7f28eb3148753ff38f9d1a9cef7838ee962c79973c7063ca4fcb3a',
    'train.mask': '01a03fc77edc65c586fbdf9a3603f7018b103b25a41f119786acf70397278688',
}

OUT_DIR = Path('/home/user/quant-trade/certification/phase2b')
SHARD_DIR = OUT_DIR / 'shards'
BUCKETS = 36
CARDS = 6

# ------------------------------------------------------- certified imports
from datagen.generator import (BucketConversionF32, generate_data,   # noqa: E402
                               generate_data_file, resolve_targets)
from datagen.th_random import THRandom                               # noqa: E402
from deepstack_leduc.config import Config                            # noqa: E402
from deepstack_leduc.torch7_blas import BIT_EXACT_BACKEND            # noqa: E402
from deepstack_leduc.torch7_tensor import load_float_tensor          # noqa: E402
from deepstack_leduc.value_model import load_original_value_net      # noqa: E402

assert BIT_EXACT_BACKEND, 'bit-exact BLAS backend required'

CONFIG_CANON = {
    'master_seed': MASTER_SEED,
    'seed_derivation': "u32 = int.from_bytes(sha256(f'phase2b:{MASTER_SEED}:"
                       "shard:{idx:05d}').digest()[:4], 'big')",
    'shard_size': SHARD_SIZE,
    'valid_shards': VALID_SHARDS,
    'train_shards': [TRAIN_SHARDS[0], TRAIN_SHARDS[-1]],
    'gen_batch_size': 10,
    'config': repr(Config()),
    'net': f'final_cpu.model sha256={WEIGHTS_SHA}',
    'audit_rows_per_shard': AUDIT_ROWS_PER_SHARD,
    'target_abs_bound': TARGET_ABS_BOUND,
    'engine_sha': ENGINE_SHA,
    'datagen_sha': DATAGEN_SHA,
}
CONFIG_HASH = hashlib.sha256(
    json.dumps(CONFIG_CANON, sort_keys=True).encode()).hexdigest()


def shard_seed(idx: int) -> int:
    h = hashlib.sha256(f'phase2b:{MASTER_SEED}:shard:{idx:05d}'.encode())
    return int.from_bytes(h.digest()[:4], 'big')


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_pins() -> None:
    """The DS working tree must be the certified generator commit, clean."""
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True,
                          text=True, check=True).stdout.strip()
    dirty = subprocess.run(['git', 'status', '--porcelain'],
                           capture_output=True, text=True, check=True).stdout
    assert head == DATAGEN_SHA, f'DS HEAD {head} != certified {DATAGEN_SHA}'
    assert dirty.strip() == '', f'DS working tree not clean:\n{dirty}'
    parent = subprocess.run(['git', 'rev-parse', 'HEAD^'], capture_output=True,
                            text=True, check=True).stdout.strip()
    assert parent == ENGINE_SHA, f'generator parent {parent} != golden'
    w = sha256_file(Path('deepstack_leduc/models/final_cpu.model'))
    assert w == WEIGHTS_SHA, 'final_cpu.model hash mismatch'


# ------------------------------------------------------------ shard worker
_NET = None


def _init_worker() -> None:
    global _NET
    _NET = load_original_value_net()


def board_masks() -> np.ndarray:
    out = np.zeros((CARDS, BUCKETS), dtype=np.float32)
    for b in range(CARDS):
        conv = BucketConversionF32()
        conv.set_board(b)
        out[b] = conv.get_possible_bucket_mask().reshape(-1)
    return out


def invert_row(inputs_row: np.ndarray, mask_row: np.ndarray):
    """Certified inversion (invert_and_verify.py): board from mask block,
    card ranges from input bucket blocks, pot via double round-trip."""
    blocks = mask_row.reshape(6, 6)
    cands = [b for b in range(6) if blocks[b].sum() == 5]
    assert len(cands) == 1, f'ambiguous board in mask: {cands}'
    board = cands[0]
    ranges = np.zeros((2, CARDS), dtype=np.float32)
    for player in range(2):
        block = inputs_row[player * BUCKETS:(player + 1) * BUCKETS]
        for card in range(CARDS):
            if card != board:
                ranges[player, card] = block[board * 6 + card]
    pot_size = float(inputs_row[-1]) * 1200.0
    return board, ranges, pot_size


def qa_shard(idx: int, inputs: np.ndarray, targets: np.ndarray,
             mask: np.ndarray, bmasks: np.ndarray) -> dict:
    n = SHARD_SIZE
    assert inputs.shape == (n, 2 * BUCKETS + 1), inputs.shape
    assert targets.shape == (n, 2 * BUCKETS), targets.shape
    assert mask.shape == (n, BUCKETS), mask.shape
    for name, a in (('inputs', inputs), ('targets', targets), ('mask', mask)):
        assert np.isfinite(a).all(), f'shard {idx}: non-finite in {name}'

    # mask rows must equal exactly one legal board mask; recover boards
    boards = np.full(n, -1, dtype=np.int64)
    for b in range(CARDS):
        hit = (mask == bmasks[b]).all(axis=1)
        boards[hit] = b
    assert (boards >= 0).all(), f'shard {idx}: illegal mask row'
    # board constant within each generation batch of 10
    assert (boards.reshape(-1, 10) == boards.reshape(-1, 10)[:, :1]).all()

    # ranges: nonneg, zero on impossible buckets, possible-mass ~1 (f32)
    for player in range(2):
        block = inputs[:, player * BUCKETS:(player + 1) * BUCKETS]
        assert (block >= 0).all(), f'shard {idx}: negative range mass'
        assert (block * (1.0 - mask) == 0).all(), \
            f'shard {idx}: mass on impossible bucket'
        sums = block.sum(axis=1)
        assert sums.min() > 0.999 and sums.max() < 1.001, \
            f'shard {idx}: range sums [{sums.min()},{sums.max()}]'

    pot_feat = inputs[:, -1]
    # exact f32-chain bounds of the certified pot pipeline: rand_float can
    # store exactly 0.0f and (after f32 rounding of u32max*2^-32) exactly
    # 1.0f, so the inclusive bounds follow the generator's own op chain
    min_pot = np.float32(100.0)
    pot_range = np.float32(1200 - 0.1 - 100)
    max_pot = np.float32(np.float32(np.float32(1.0) * pot_range) + min_pot)
    inv1200 = np.float32(1.0 / 1200.0)
    lo = np.float32(min_pot * inv1200)
    hi = np.float32(max_pot * inv1200)
    assert pot_feat.min() >= lo and pot_feat.max() <= hi, \
        f'shard {idx}: pot feature out of range [{pot_feat.min()},{pot_feat.max()}]'

    amax = float(np.abs(targets).max())
    assert amax <= TARGET_ABS_BOUND, f'shard {idx}: |target| {amax}'
    # targets zero on impossible buckets
    tt = targets.reshape(n, 2, BUCKETS)
    assert (tt * (1.0 - mask[:, None, :]) == 0).all(), \
        f'shard {idx}: target mass on impossible bucket'

    return {'boards': np.bincount(boards, minlength=6).tolist(),
            'pot_min': float(pot_feat.min() * 1200), 'pot_max': float(pot_feat.max() * 1200),
            'pot_mean': float(pot_feat.mean() * 1200), 'target_absmax': amax}


def audit_shard(idx: int, inputs: np.ndarray, targets: np.ndarray,
                mask: np.ndarray, net, cfg: Config) -> list[int]:
    """Deterministic fresh resolve of randomly selected rows; require the
    full 72-value target row byte-identical to what was stored."""
    sel = random.Random(f'audit:{MASTER_SEED}:{idx}')
    rows = sorted(sel.sample(range(SHARD_SIZE), AUDIT_ROWS_PER_SHARD))
    for r in rows:
        board, ranges, pot_size = invert_row(inputs[r], mask[r])
        vals = resolve_targets(board, pot_size, ranges[0], ranges[1], net, cfg)
        conv = BucketConversionF32()
        conv.set_board(board)
        recomputed = np.concatenate([
            conv.card_range_to_bucket_range(vals[p:p + 1]).reshape(-1)
            for p in range(2)])
        if not np.array_equal(recomputed, targets[r]):
            diff = np.nonzero(recomputed != targets[r])[0]
            freeze = {
                'shard': idx, 'row': r, 'board': board, 'pot_size': pot_size,
                'first_idx': int(diff[0]),
                'stored_bits': targets[r][diff[0]].tobytes().hex(),
                'recomputed_bits': recomputed[diff[0]].tobytes().hex(),
                'n_diff': int(len(diff)),
            }
            (OUT_DIR / 'FREEZE_DIVERGENCE.json').write_text(
                json.dumps(freeze, indent=2))
            raise AssertionError(f'AUDIT DIVERGENCE frozen: {freeze}')
    return rows


def run_shard(idx: int) -> dict:
    cfg = Config()
    seed = shard_seed(idx)
    prefix = SHARD_DIR / f'shard_{idx:05d}'
    manifest_path = SHARD_DIR / f'shard_{idx:05d}.json'
    if manifest_path.exists():
        m = json.loads(manifest_path.read_text())
        for part in ('inputs', 'targets', 'mask'):
            p = Path(str(prefix) + '.' + part)
            assert p.exists() and sha256_file(p) == m['sha256'][part], \
                f'shard {idx}: existing files do not match manifest'
        m['skipped'] = True
        return m

    tmp_prefix = SHARD_DIR / f'.tmp_shard_{idx:05d}'
    for part in ('inputs', 'targets', 'mask'):   # clear stale temps only
        Path(str(tmp_prefix) + '.' + part).unlink(missing_ok=True)

    t0 = time.time()
    rng = THRandom(seed)
    generate_data_file(SHARD_SIZE, tmp_prefix, rng, _NET, cfg)
    gen_seconds = time.time() - t0

    inputs = load_float_tensor(str(tmp_prefix) + '.inputs')
    targets = load_float_tensor(str(tmp_prefix) + '.targets')
    mask = load_float_tensor(str(tmp_prefix) + '.mask')
    stats = qa_shard(idx, inputs, targets, mask, board_masks())
    audited = audit_shard(idx, inputs, targets, mask, _NET, cfg)

    shas = {}
    for part in ('inputs', 'targets', 'mask'):
        src = Path(str(tmp_prefix) + '.' + part)
        dst = Path(str(prefix) + '.' + part)
        assert not dst.exists(), f'refusing to overwrite {dst}'
        os.rename(src, dst)                     # atomic on same fs
        shas[part] = sha256_file(dst)

    manifest = {
        'shard': idx, 'split': 'valid' if idx in VALID_SHARDS else 'train',
        'seed': seed, 'samples': SHARD_SIZE,
        'sha256': shas, 'config_hash': CONFIG_HASH,
        'engine_sha': ENGINE_SHA, 'datagen_sha': DATAGEN_SHA,
        'weights_sha': WEIGHTS_SHA,
        'qa': stats, 'audit_rows': audited, 'audit': 'BYTE_EXACT',
        'gen_seconds': round(gen_seconds, 1),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return manifest


# ------------------------------------------------------------ entry points
def cmd_generate() -> None:
    verify_pins()
    SHARD_DIR.mkdir(parents=True, exist_ok=True)
    seeds = [shard_seed(i) for i in ALL_SHARDS]
    assert len(set(seeds)) == len(seeds), 'shard seed collision'
    t0 = time.time()
    done = 0
    with mp.Pool(4, initializer=_init_worker) as pool:
        for m in pool.imap_unordered(run_shard, ALL_SHARDS):
            done += 1
            tag = 'skip' if m.get('skipped') else f"{m['gen_seconds']:.0f}s"
            print(f"[{done}/{len(ALL_SHARDS)}] shard {m['shard']:05d} "
                  f"{m['split']} seed={m['seed']} {tag}", flush=True)
    print(f'ALL SHARDS COMPLETE in {(time.time() - t0) / 3600:.2f} h')


def cmd_finalqa() -> None:
    """Cross-shard QA + master manifest."""
    shard_manifests = []
    all_boards = np.zeros(6, dtype=np.int64)
    pots = []
    row_hashes = set()
    dup = 0
    tmax = 0.0
    total = 0
    per_split = {'train': 0, 'valid': 0}
    for idx in ALL_SHARDS:
        m = json.loads((SHARD_DIR / f'shard_{idx:05d}.json').read_text())
        assert m['config_hash'] == CONFIG_HASH, f'shard {idx} config drift'
        assert m['audit'] == 'BYTE_EXACT'
        prefix = SHARD_DIR / f'shard_{idx:05d}'
        for part in ('inputs', 'targets', 'mask'):
            assert sha256_file(Path(f'{prefix}.{part}')) == m['sha256'][part], \
                f'shard {idx} {part} SHA drift since generation'
        inputs = load_float_tensor(f'{prefix}.inputs')
        all_boards += np.array(m['qa']['boards'])
        pots.append(inputs[:, -1].astype(np.float64) * 1200)
        for r in range(inputs.shape[0]):
            h = hashlib.sha256(inputs[r].tobytes()).digest()
            if h in row_hashes:
                dup += 1
            row_hashes.add(h)
        tmax = max(tmax, m['qa']['target_absmax'])
        total += m['samples']
        per_split[m['split']] += m['samples']
        shard_manifests.append(m)
    assert dup == 0, f'{dup} duplicate input rows'
    pots = np.concatenate(pots)
    batches = total // 10
    exp = batches / 6
    chi2 = float(((all_boards / 10 - exp) ** 2 / exp).sum())
    qa = {
        'total_samples': total, 'split': per_split,
        'board_counts': all_boards.tolist(),
        'board_chi2_df5': round(chi2, 2), 'board_chi2_crit_0001': 20.5,
        'pot_min': round(float(pots.min()), 3),
        'pot_max': round(float(pots.max()), 3),
        'pot_mean': round(float(pots.mean()), 2), 'pot_mean_expected': 649.95,
        'duplicate_input_rows': dup,
        'target_absmax': tmax, 'target_bound': TARGET_ABS_BOUND,
    }
    assert chi2 < 20.5, 'board distribution drift'
    assert abs(qa['pot_mean'] - 649.95) < 4.0, 'pot mean drift (>4σ)'

    # distribution drift vs certified pilot: regenerate pilot, anchor SHAs
    pilot_dir = OUT_DIR / '.pilot_regen'
    pilot_dir.mkdir(exist_ok=True)
    if not (pilot_dir / 'train.targets').exists():
        net = load_original_value_net()
        generate_data(100, 100, pilot_dir, THRandom(PILOT_SEED), net, Config())
    for name, want in PILOT_SHAS.items():
        got = sha256_file(pilot_dir / name)
        assert got == want, f'pilot regen {name} SHA {got} != certified {want}'
    pt = np.concatenate([
        load_float_tensor(pilot_dir / 'train.targets').ravel(),
        load_float_tensor(pilot_dir / 'valid.targets').ravel()])
    bt = np.concatenate([load_float_tensor(
        SHARD_DIR / f'shard_{i:05d}.targets').ravel() for i in REPLAY_SHARDS])
    qs = [1, 5, 25, 50, 75, 95, 99]
    qa['pilot_reanchor'] = 'SHA_MATCH_6_OF_6'
    qa['target_quantiles_pilot'] = [round(float(v), 4) for v in
                                    np.percentile(pt[pt != 0], qs)]
    qa['target_quantiles_bulk'] = [round(float(v), 4) for v in
                                   np.percentile(bt[bt != 0], qs)]

    # virtual merged SHAs (concat in shard order) for the training consumer
    merged = {}
    for split, ids in (('valid', VALID_SHARDS), ('train', TRAIN_SHARDS)):
        for part in ('inputs', 'targets', 'mask'):
            h = hashlib.sha256()
            for i in ids:
                h.update(load_float_tensor(
                    SHARD_DIR / f'shard_{i:05d}.{part}').tobytes())
            merged[f'{split}.{part}'] = h.hexdigest()

    master = {
        'phase': '2B production dataset', 'master_seed': MASTER_SEED,
        'seed_derivation': CONFIG_CANON['seed_derivation'],
        'config_canon': CONFIG_CANON, 'config_hash': CONFIG_HASH,
        'engine_sha': ENGINE_SHA, 'datagen_sha': DATAGEN_SHA,
        'weights_sha': WEIGHTS_SHA,
        'env': {'python': sys.version.split()[0], 'numpy': np.__version__,
                'bit_exact_blas': True},
        'qa': qa, 'merged_sha256_concat_by_shard_order': merged,
        'shards': shard_manifests,
    }
    (OUT_DIR / 'MANIFEST.json').write_text(json.dumps(master, indent=2))
    print(json.dumps(qa, indent=2))
    print('MANIFEST written')


def cmd_replay() -> None:
    """Independent replay of a representative shard subset from the same
    seeds in this fresh process; require identical SHA-256. An optional
    argv[2] comma-list restricts the subset so several fresh processes can
    replay disjoint parts in parallel."""
    verify_pins()
    global _NET
    _init_worker()
    cfg = Config()
    tmp = OUT_DIR / '.replay'
    tmp.mkdir(exist_ok=True)
    subset = ([int(x) for x in sys.argv[2].split(',')]
              if len(sys.argv) > 2 else REPLAY_SHARDS)
    assert set(subset) <= set(REPLAY_SHARDS)
    ok = 0
    for idx in subset:
        m = json.loads((SHARD_DIR / f'shard_{idx:05d}.json').read_text())
        prefix = tmp / f'replay_{idx:05d}'
        rng = THRandom(shard_seed(idx))
        generate_data_file(SHARD_SIZE, prefix, rng, _NET, cfg)
        for part in ('inputs', 'targets', 'mask'):
            got = sha256_file(Path(f'{prefix}.{part}'))
            assert got == m['sha256'][part], \
                f'REPLAY MISMATCH shard {idx} {part}: {got} != {m["sha256"][part]}'
            Path(f'{prefix}.{part}').unlink()
        ok += 1
        print(f'replay shard {idx:05d}: 3/3 SHA identical '
              f'[{ok}/{len(REPLAY_SHARDS)}]', flush=True)
    print(f'REPLAY COMPLETE: {ok}/{len(REPLAY_SHARDS)} shards SHA-identical')


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'generate'
    {'generate': cmd_generate, 'finalqa': cmd_finalqa,
     'replay': cmd_replay}[mode]()
