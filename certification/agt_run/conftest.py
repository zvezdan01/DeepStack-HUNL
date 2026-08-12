"""Certification hook: piggyback on the AGT pytest harness to additionally
record RAW byte-level comparison (tobytes equality, array_equal, max abs
diff, max ULP) of every obtained array against the immutable stored .npz
oracle. Does not alter pass/fail semantics of the original tests."""
import json
import os

import numpy as np
from pytest_regressions.ndarrays_regression import NDArraysRegressionFixture

RESULTS_PATH = os.environ.get(
    'AGT_RAW_RESULTS', os.path.join(os.path.dirname(__file__), 'raw_results.jsonl')
)

_original_check = NDArraysRegressionFixture.check


def _ulp_diff(a, b):
    a = np.asarray(a, np.float64).ravel()
    b = np.asarray(b, np.float64).ravel()
    ai = a.view(np.int64).copy()
    bi = b.view(np.int64).copy()
    ai[ai < 0] = np.int64(-(2**63) + 1) - ai[ai < 0] + 1
    bi[bi < 0] = np.int64(-(2**63) + 1) - bi[bi < 0] + 1
    return int(np.max(np.abs(ai - bi))) if len(ai) else 0


def _patched_check(self, data_dict, basename=None, fullpath=None, **kwargs):
    record = {'basename': basename, 'keys': {}}
    try:
        oracle_path = os.path.join(str(self.original_datadir), f'{basename}.npz')
        oracle = np.load(oracle_path, allow_pickle=True)
        for key, obtained in data_dict.items():
            obtained = np.asarray(obtained)
            expected = oracle[key]
            entry = {
                'byte_equal': bool(
                    obtained.dtype == expected.dtype
                    and obtained.shape == expected.shape
                    and obtained.tobytes() == expected.tobytes()
                ),
                'array_equal': bool(np.array_equal(obtained, expected)),
            }
            if np.issubdtype(expected.dtype, np.floating) and obtained.shape == expected.shape:
                diff = np.abs(np.asarray(obtained, np.float64) - np.asarray(expected, np.float64))
                entry['max_abs_diff'] = float(np.max(diff)) if diff.size else 0.0
                entry['max_ulp'] = _ulp_diff(obtained, expected)
            record['keys'][key] = entry
    except Exception as exc:  # pragma: no cover - diagnostics only
        record['error'] = repr(exc)
    with open(RESULTS_PATH, 'a') as fh:
        fh.write(json.dumps(record) + '\n')
    return _original_check(self, data_dict, basename=basename, fullpath=fullpath, **kwargs)


NDArraysRegressionFixture.check = _patched_check
