#!/usr/bin/env python3
"""Extra checks for Method 134 (CSCC): max-drift loop + voice-exchange sheaf with real tension."""
from fractions import Fraction
import numpy as np
from verify_134_CSCC import rank_exact, coboundary, cohomology, selection, least_squares_section

print("=" * 78)
print("TEST 6 — max drift: 5-section loop, every seam transposes +1  => lap = +5")
P1 = np.roll(np.eye(12, dtype=int), 1, axis=1)
I12 = np.eye(12, dtype=int)
edges = [(i, (i + 1) % 5, P1, I12) for i in range(5)]
r = cohomology({i: 12 for i in range(5)}, edges, "T+1 x5 loop")
h = np.linalg.matrix_power(P1, 5)
ev = np.linalg.eigvals(h.astype(float))
print("  holonomy = T_{+5}; #eigenvalues==1:", int(np.sum(np.isclose(ev, 1.0))),
      "-> dim H^0 should equal that count")
print("  musical reading: only 1 pc survives a full lap; the other 11 rotate (perfect-4th escalator)")

print("=" * 78)
print("TEST 7 — 12-section loop, +1 each seam (lap = +12 = identity)")
edges = [(i, (i + 1) % 12, P1, I12) for i in range(12)]
r12 = cohomology({i: 12 for i in range(12)}, edges, "T+1 x12 loop")

print("=" * 78)
print("TEST 8 — voice-exchange sheaf: stalks R^3 (3 voices), seams permute voices")
# section v stalk = (soprano, alto, bass) coefficient vector
# seam map: x_v = perm * x_u  (voice exchange around the loop)
def perm_matrix(p):
    M = np.zeros((3, 3), dtype=int)
    for i, j in enumerate(p):
        M[i, j] = 1
    return M

# edges: 0->1 swaps top/bottom, 1->2 rotates, 2->3 swaps mid/top, 3->0 rotates back
p01 = perm_matrix([2, 1, 0])   # (s,a,b) -> (b,a,s)
p12 = perm_matrix([1, 2, 0])   # -> (a,b,s)
p23 = perm_matrix([0, 2, 1])   # -> (s,b,a)
p30 = perm_matrix([1, 2, 0])   # -> (a,b,s)
E3 = [(0, 1, p01, np.eye(3, dtype=int)),
      (1, 2, p12, np.eye(3, dtype=int)),
      (2, 3, p23, np.eye(3, dtype=int)),
      (3, 0, p30, np.eye(3, dtype=int))]
r3 = cohomology({0: 3, 1: 3, 2: 3, 3: 3}, E3, "voice-exchange C4")
hol = p30 @ p23 @ p12 @ p01
print("  product permutation matrix:\n", hol)
print("  cycle type of the holonomy permutation:",
      [len(c) for c in _cycles(list(range(3)), hol)] if False else "see rows")
# cycle decomposition
def cycles_of(M):
    seen, out = set(), []
    for i in range(M.shape[0]):
        if i in seen:
            continue
        c, j = [], i
        while j not in seen:
            seen.add(j)
            c.append(j)
            j = int(np.argmax(M[:, j]))
        out.append(c)
    return out
print("  cycles:", cycles_of(hol), " -> #orbits = dim H^0")

print("=" * 78)
print("TEST 8b — tension: demand each seam holds the top voice; measure unreachable part")
# target b: for each seam, force the shared coordinate to 0
E3t = []
tgt = []
for (u, v, Au, Av) in E3:
    E3t.append((u, v, Au, Av))
    tgt.extend([1.0, 0.0, 0.0])   # demand, per seam, a unit transfer on the first shared coordinate
x, res, A = least_squares_section({0: 3, 1: 3, 2: 3, 3: 3}, E3t, targets=tgt)
print("  ||delta x* - b|| =", round(float(np.linalg.norm(res)), 6),
      " per-seam residuals =", [round(float(v), 4) for v in res])
print("  rank(delta) =", rank_exact(A.astype(int).tolist()), " coker dim =", 4 - rank_exact(A.astype(int).tolist()))
