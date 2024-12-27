from datetime import datetime
from pathlib import Path
from time import time

import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import seaborn as sns

from utils import sparsify_array, prepare_solver_kwargs

mu_f, sigma_f = 0., 1.
mu_e, sigma_e = 0., 1.
mu_A, sigma_A = 0., 1.
iterations: int = 100
n: int = 256
k: int = 2
points: int = 20

m: int = k * n
assert m > n
assert k >= 1

# Build an A structured to satisfy RIP with high probability
A = np.random.normal(mu_A, sigma_A, size=(m, n))
A /= np.linalg.norm(A, ord=2, keepdims=True, axis=0)

# Adapt problem from linear coding (m>n) to compressed sensing (m<n)
ckA = sp.linalg.null_space(A.T)  # Basis of co kernel of A
F = np.dot(ckA, np.linalg.pinv(ckA))  # orthogonal projection to co kernel of A
# F = ckA.T
assert np.allclose(np.dot(F, A), 0)
assert F.shape[0] <= F.shape[1]

# check if F is an orthogonal projection
assert np.allclose(np.dot(F, F), F)  # idempotent
assert np.allclose(F.T, F)  # symmetric

# Build random f
f = np.random.normal(mu_f, sigma_f, size=n)
Af = np.dot(A, f)

# sampling sparsity
s_down: int = m // (points * 2)
s_levels = np.arange(1, m // 2)[::s_down]

# auxiliar
fs = np.zeros_like(s_levels)
zero_indices_candidates = np.arange(m)
solver_kwargs = prepare_solver_kwargs(F)

for i, s in enumerate(s_levels):
    start_time = time()
    for _ in range(iterations):
        e = sparsify_array(s, array=np.random.normal(mu_e, sigma_e, size=m), zero_indices=zero_indices_candidates)
        y = Af + e
        ym = np.dot(F, y)
        e_star = sp.optimize.linprog(b_eq=ym, **solver_kwargs).x[:m]
        if np.allclose(e_star, e, rtol=1e-5):
            fs[i] += 1
    end_time = time()
    elapsed_time = end_time - start_time
    print(
        f'A {s} non-zero values vector recovered exactly {fs[i]}/{iterations} times in {elapsed_time // 60:.0f} min and {elapsed_time % 60:.0f} sec')

fig = sns.scatterplot(x='x', y='y', data={'x': s_levels / m, 'y': fs / iterations})
fig.set_xlabel('# Fraction of corrupted entries')
fig.set_ylabel(f'frequency @ iterations = {iterations}')
fig.set_title(f'Empirical frequency of exact reconstruction @ n={n}, m={k}n')

Path('figs').mkdir(exist_ok=True)
plt.savefig(f'figs/{datetime.now()}.png')
