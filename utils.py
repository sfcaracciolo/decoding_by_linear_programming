import numpy as np


def sparsify_array(s: int, array: np.ndarray, zero_indices: np.ndarray = None):
    """
    s: amount of non-zero entries
    """
    m = array.size
    assert s <= m
    assert s >= 0

    zero_indices = np.arange(m) if zero_indices is None else zero_indices
    np.random.shuffle(zero_indices)
    zero_indices = zero_indices[:-s]
    array[zero_indices] = 0
    return array


def prepare_solver_kwargs(a: np.ndarray):
    m, n = a.shape
    assert m <= n

    A_eq = np.zeros((m, 2 * n))
    A_eq[:, :n] = a

    c = np.zeros(2 * n)
    c[n:] = 1

    id = np.eye(n)
    A_ub = np.block([[id, -id], [-id, -id]])

    b_ub = np.zeros(2 * n)

    bounds = np.zeros((2 * n, 2))
    bounds[:n, 0] = -np.inf
    bounds[:, 1] = np.inf

    return {'c': c, 'A_ub': A_ub, 'b_ub': b_ub, 'A_eq': A_eq, 'bounds': bounds}
