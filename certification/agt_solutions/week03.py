#!/usr/bin/env python3
"""Certification reference implementations for AGT week 3 raw oracles
(deviation incentives, NashConv, exploitability, fictitious play)."""

import numpy as np

import week01


def compute_deltas(row_matrix, col_matrix, row_strategy, col_strategy):
    row_value = row_strategy @ row_matrix @ col_strategy
    col_value = row_strategy @ col_matrix @ col_strategy
    row_br_value = np.max(row_matrix @ col_strategy)
    col_br_value = np.max(row_strategy @ col_matrix)
    return np.array([row_br_value - row_value, col_br_value - col_value])


def compute_nash_conv(row_matrix, col_matrix, row_strategy, col_strategy):
    row_delta, col_delta = compute_deltas(row_matrix, col_matrix, row_strategy, col_strategy)
    return row_delta + col_delta


def compute_exploitability(row_matrix, col_matrix, row_strategy, col_strategy):
    return compute_nash_conv(row_matrix, col_matrix, row_strategy, col_strategy) / 2


def fictitious_play(row_matrix, col_matrix, num_iters, naive):
    num_rows, num_cols = row_matrix.shape
    avg_row = np.full(num_rows, 1.0 / num_rows)
    avg_col = np.full(num_cols, 1.0 / num_cols)
    last_row = avg_row
    last_col = avg_col

    strategies = []
    for t in range(num_iters):
        target_row = last_col if naive else avg_col
        target_col = last_row if naive else avg_row
        br_row = week01.calculate_best_response_against_col(row_matrix, target_row)
        br_col = week01.calculate_best_response_against_row(col_matrix, target_col)

        avg_row = avg_row + (br_row - avg_row) / (t + 1)
        avg_col = avg_col + (br_col - avg_col) / (t + 1)
        last_row, last_col = br_row, br_col

        strategies.append((avg_row.copy(), avg_col.copy()))

    return strategies


def plot_exploitability(row_matrix, col_matrix, strategies, label):
    values = [
        compute_exploitability(row_matrix, col_matrix, row_strategy, col_strategy)
        for row_strategy, col_strategy in strategies
    ]
    return values


def main() -> None:
    pass


if __name__ == '__main__':
    main()
