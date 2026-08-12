#!/usr/bin/env python3
"""Certification reference implementations for AGT week 1 raw oracles.

These are freshly written certification implementations (no project code
exists in this repository). They are validated against the immutable
.npz oracles in third_party/agt_tests/."""

import numpy as np


def evaluate_general_sum(row_matrix, col_matrix, row_strategy, col_strategy):
    row_utility = row_strategy @ row_matrix @ col_strategy
    col_utility = row_strategy @ col_matrix @ col_strategy
    return np.array([row_utility, col_utility])


def evaluate_zero_sum(row_matrix, row_strategy, col_strategy):
    row_utility = row_strategy @ row_matrix @ col_strategy
    return np.array([row_utility, -row_utility])


def calculate_best_response_against_row(col_matrix, row_strategy):
    utilities = row_strategy @ col_matrix
    response = np.zeros_like(utilities, np.float64)
    response[np.argmax(utilities)] = 1.0
    return response


def calculate_best_response_against_col(row_matrix, col_strategy):
    utilities = row_matrix @ col_strategy
    response = np.zeros_like(utilities, np.float64)
    response[np.argmax(utilities)] = 1.0
    return response


def evaluate_row_against_best_response(row_matrix, col_matrix, row_strategy):
    br = calculate_best_response_against_row(col_matrix, row_strategy)
    return row_strategy @ row_matrix @ br


def evaluate_col_against_best_response(row_matrix, col_matrix, col_strategy):
    br = calculate_best_response_against_col(row_matrix, col_strategy)
    return br @ col_matrix @ col_strategy


def find_strictly_dominated_actions(matrix):
    num_actions = matrix.shape[0]
    dominated = []
    for i in range(num_actions):
        for j in range(num_actions):
            if i != j and np.all(matrix[j] > matrix[i]):
                dominated.append(i)
                break
    return np.array(dominated, np.int64)


def iterated_removal_of_dominated_strategies(row_matrix, col_matrix):
    row_actions = np.arange(row_matrix.shape[0], dtype=np.int64)
    col_actions = np.arange(col_matrix.shape[1], dtype=np.int64)

    while True:
        row_dominated = find_strictly_dominated_actions(row_matrix)
        if len(row_dominated) > 0:
            keep = np.setdiff1d(np.arange(row_matrix.shape[0]), row_dominated)
            row_matrix = row_matrix[keep]
            col_matrix = col_matrix[keep]
            row_actions = row_actions[keep]
            continue

        col_dominated = find_strictly_dominated_actions(np.transpose(col_matrix))
        if len(col_dominated) > 0:
            keep = np.setdiff1d(np.arange(col_matrix.shape[1]), col_dominated)
            row_matrix = row_matrix[:, keep]
            col_matrix = col_matrix[:, keep]
            col_actions = col_actions[keep]
            continue

        break

    return row_matrix, col_matrix, row_actions, col_actions


def main() -> None:
    pass


if __name__ == '__main__':
    main()
