"""Certification implementation for game_theory_2023 week2 tests."""
from typing import List, Optional

import numpy as np
from scipy.optimize import linprog


def verify_support_one_side(matrix: np.ndarray, support_row: List, support_col: List) -> Optional[List]:
    k = len(support_col)
    a_eq, b_eq = [], []
    for i in support_row:
        a_eq.append(list(np.asarray(matrix, float)[i, support_col]) + [-1.0])
        b_eq.append(0.0)
    a_eq.append([1.0] * k + [0.0])
    b_eq.append(1.0)
    res = linprog(np.zeros(k + 1), A_eq=np.array(a_eq), b_eq=np.array(b_eq),
                  bounds=[(0.0, None)] * k + [(None, None)], method='highs')
    if not res.success:
        return None
    return list(res.x[:k])
