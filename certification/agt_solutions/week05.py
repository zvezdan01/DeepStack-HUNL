#!/usr/bin/env python3
"""Certification reference implementations for AGT week 5 raw oracles
(Double Oracle)."""

import numpy as np

import week01
import week04


def double_oracle(row_matrix, eps, rng):
    num_rows, num_cols = row_matrix.shape
    row_set = [int(rng.integers(0, num_rows, None))]
    col_set = [int(rng.integers(0, num_cols, None))]

    strategies = []
    supports = []
    while True:
        restricted = row_matrix[np.ix_(row_set, col_set)]
        r_strat, c_strat = week04.find_nash_equilibrium(restricted)

        row_strategy = np.zeros(num_rows, np.float64)
        row_strategy[row_set] = r_strat
        col_strategy = np.zeros(num_cols, np.float64)
        col_strategy[col_set] = c_strat

        strategies.append((row_strategy, col_strategy))
        supports.append((np.array(row_set, np.int64), np.array(col_set, np.int64)))

        # best responses in the full game
        row_br_utils = row_matrix @ col_strategy
        row_br = int(np.argmax(row_br_utils))
        upper = row_br_utils[row_br]
        col_br_utils = row_strategy @ row_matrix
        col_br = int(np.argmin(col_br_utils))
        lower = col_br_utils[col_br]

        in_row = row_br in row_set
        in_col = col_br in col_set
        if (upper - lower < eps) or (in_row and in_col):
            break
        if not in_row:
            row_set.append(row_br)
        if not in_col:
            col_set.append(col_br)

    return strategies, supports


def main() -> None:
    pass


if __name__ == '__main__':
    main()
