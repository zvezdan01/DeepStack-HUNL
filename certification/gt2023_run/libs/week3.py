"""Certification implementation for game_theory_2023 week3 tests."""
import numpy as np

import libs.week1 as week1


def compute_deltas(matrix, row_strategy, column_strategy):
    value = week1.evaluate(matrix, row_strategy, column_strategy)
    row_br = np.max(matrix @ column_strategy)
    col_br = -np.min(row_strategy @ matrix)
    return np.array([row_br - value, col_br - (-value)])


def compute_exploitability(matrix, row_strategy, column_strategy):
    return float(np.sum(compute_deltas(matrix, row_strategy, column_strategy)) / 2)


def compute_epsilon(matrix, row_strategy, column_strategy):
    return float(np.max(compute_deltas(matrix, row_strategy, column_strategy)))


def compute_exploitability_zero_sum(matrix, row_strategy, column_strategy):
    return compute_exploitability(matrix, row_strategy, column_strategy)
