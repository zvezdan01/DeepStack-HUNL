#!/usr/bin/env python3
"""Certification reference implementations for AGT week 2 raw oracles."""

import itertools

import numpy as np
from scipy.optimize import linprog


def verify_support(matrix, row_support, col_support):
    """Find an opponent (column) strategy on col_support that makes every
    row action in row_support indifferent. Uses linprog with 'highs'."""
    k = len(col_support)
    # variables: q_0..q_{k-1}, v
    a_eq = []
    b_eq = []
    for i in row_support:
        row = list(matrix[i, col_support]) + [-1.0]
        a_eq.append(row)
        b_eq.append(0.0)
    a_eq.append([1.0] * k + [0.0])
    b_eq.append(1.0)
    bounds = [(0.0, None)] * k + [(None, None)]
    res = linprog(
        c=np.zeros(k + 1),
        A_eq=np.array(a_eq, np.float64),
        b_eq=np.array(b_eq, np.float64),
        bounds=bounds,
        method='highs',
    )
    if not res.success:
        return None
    return np.array(res.x[:k], np.float64)


def _full_strategy(support, probs, num_actions):
    strategy = np.zeros(num_actions, np.float64)
    strategy[support] = probs
    return strategy


def support_enumeration(row_matrix, col_matrix):
    num_rows, num_cols = row_matrix.shape
    equilibria = []
    for row_support in _all_supports(num_rows):
        for col_support in _all_supports(num_cols):
            col_probs = verify_support(row_matrix, row_support, col_support)
            if col_probs is None:
                continue
            row_probs = verify_support(np.transpose(col_matrix), col_support, row_support)
            if row_probs is None:
                continue
            row_strategy = _full_strategy(row_support, row_probs, num_rows)
            col_strategy = _full_strategy(col_support, col_probs, num_cols)
            if _is_equilibrium(row_matrix, col_matrix, row_strategy, col_strategy):
                equilibria.append((row_strategy, col_strategy))
    return equilibria


def _all_supports(num_actions):
    for size in range(1, num_actions + 1):
        for support in itertools.combinations(range(num_actions), size):
            yield np.array(support, np.int64)


def _is_equilibrium(row_matrix, col_matrix, row_strategy, col_strategy, tol=1e-9):
    row_utils = row_matrix @ col_strategy
    row_value = row_strategy @ row_utils
    if np.max(row_utils) > row_value + tol:
        return False
    col_utils = row_strategy @ col_matrix
    col_value = col_utils @ col_strategy
    if np.max(col_utils) > col_value + tol:
        return False
    return True


def main() -> None:
    pass


if __name__ == '__main__':
    main()
