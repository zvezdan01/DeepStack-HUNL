#!/usr/bin/env python3
"""Certification reference implementations for AGT week 6 raw oracles
(regret matching / regret minimization)."""

import numpy as np


def regret_matching(regrets):
    positive = np.maximum(regrets, 0.0)
    total = np.sum(positive)
    if total > 0:
        return positive / total
    return np.full(len(regrets), 1.0 / len(regrets))


def regret_minimization(row_matrix, col_matrix, num_iters):
    num_rows, num_cols = row_matrix.shape
    row_regrets = np.zeros(num_rows)
    col_regrets = np.zeros(num_cols)
    avg_row = np.full(num_rows, 1.0 / num_rows)
    avg_col = np.full(num_cols, 1.0 / num_cols)

    strategies = []
    for t in range(num_iters):
        row_strategy = regret_matching(row_regrets)
        col_strategy = regret_matching(col_regrets)

        row_action_utils = row_matrix @ col_strategy
        row_value = row_strategy @ row_action_utils
        row_regrets += row_action_utils - row_value

        col_action_utils = row_strategy @ col_matrix
        col_value = col_action_utils @ col_strategy
        col_regrets += col_action_utils - col_value

        avg_row = avg_row + (row_strategy - avg_row) / (t + 1)
        avg_col = avg_col + (col_strategy - avg_col) / (t + 1)
        strategies.append((avg_row.copy(), avg_col.copy()))

    return strategies


def main() -> None:
    pass


if __name__ == '__main__':
    main()
