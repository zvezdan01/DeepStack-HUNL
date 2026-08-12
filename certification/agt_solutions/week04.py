#!/usr/bin/env python3
"""Certification reference implementations for AGT week 4 raw oracles
(Nash equilibrium LP, correlated equilibrium LP)."""

import numpy as np
from scipy.optimize import linprog


def find_nash_equilibrium(row_matrix):
    num_rows, num_cols = row_matrix.shape
    # variables: x_0..x_{m-1} (row strategy), v; maximize v
    c = np.zeros(num_rows + 1)
    c[-1] = -1.0
    # constraints: for every column j: -x^T A[:,j] + v <= 0
    a_ub = np.hstack([-np.transpose(row_matrix), np.ones((num_cols, 1))])
    b_ub = np.zeros(num_cols)
    a_eq = np.array([[1.0] * num_rows + [0.0]])
    b_eq = np.array([1.0])
    bounds = [(0.0, None)] * num_rows + [(None, None)]
    res = linprog(c, A_ub=a_ub, b_ub=b_ub, A_eq=a_eq, b_eq=b_eq, bounds=bounds, method='highs')
    row_strategy = np.array(res.x[:num_rows], np.float64)
    # column strategy from the duals of the inequality constraints
    col_strategy = np.array(res.ineqlin.marginals, np.float64)
    col_strategy = np.abs(col_strategy)
    col_strategy = col_strategy / np.sum(col_strategy)
    return row_strategy, col_strategy


def find_correlated_equilibrium(row_matrix, col_matrix):
    num_rows, num_cols = row_matrix.shape
    n = num_rows * num_cols
    # variables: p(i, j) flattened row-major
    a_ub = []
    b_ub = []
    # row player incentive constraints: for i, i': sum_j p(i,j) (u1(i',j) - u1(i,j)) <= 0
    for i in range(num_rows):
        for i2 in range(num_rows):
            row = np.zeros((num_rows, num_cols))
            row[i, :] = row_matrix[i2, :] - row_matrix[i, :]
            a_ub.append(row.ravel())
            b_ub.append(0.0)
    # column player incentive constraints
    for j in range(num_cols):
        for j2 in range(num_cols):
            row = np.zeros((num_rows, num_cols))
            row[:, j] = col_matrix[:, j2] - col_matrix[:, j]
            a_ub.append(row.ravel())
            b_ub.append(0.0)
    a_eq = np.ones((1, n))
    b_eq = np.array([1.0])
    res = linprog(
        c=np.zeros(n),
        A_ub=np.array(a_ub, np.float64),
        b_ub=np.array(b_ub, np.float64),
        A_eq=a_eq,
        b_eq=b_eq,
        bounds=[(0.0, 1.0)] * n,
        method='highs',
    )
    return np.array(res.x.reshape(num_rows, num_cols), np.float64)


def main() -> None:
    pass


if __name__ == '__main__':
    main()
