"""Certification implementation for game_theory_2023 week1 tests
(archive ships stubs; expected values are hand-computed in the tests)."""
import numpy as np


def evaluate(matrix, row_strategy, column_strategy):
    return (row_strategy @ matrix @ column_strategy).item()


def best_response_value_row(matrix, row_strategy):
    # row player's value when the column player best-responds (zero-sum:
    # column minimizes the row player's payoff)
    return np.min(row_strategy @ matrix)


def best_response_value_column(matrix, column_strategy):
    # column player's value (= -row value) when the row player best-responds
    return -np.max(matrix @ column_strategy)
