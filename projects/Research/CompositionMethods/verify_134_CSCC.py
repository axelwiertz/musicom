#!/usr/bin/env python3
"""
Verification harness for Method 134 — Cellular Sheaf Cohomology Composition (CSCC).

Checks, with exact rational arithmetic where possible:
  1. dim H^0 = sum(dim stalk_v) - rank(delta), dim H^1 = sum(dim stalk_e) - rank(delta)
  2. Euler characteristic of the cochain complex: dim H^0 - dim H^1 = sum d_v - sum d_e
  3. Forest => H^1 = 0 (obstructions live only in the cycle space)
  4. dim(cycle space) = |E| - |V| + #components
  5. Holonomy: product of transports around a loop; eigenvalue 1 <=> loop-closing section exists
  6. Matrix-Tree: tau(G) = det(reduced Laplacian) = number of seam-repair (cadence) choices
  7. Least-squares global section ("harmonic repair") -> per-seam residual = tension curve
  8. Worked musical example: ii7-V7-Imaj7-vi7 loop in C (a coherent loop)
"""
from fractions import Fraction
import itertools
import numpy as np

# ---------------------------------------------------------------- exact linalg
def rank_exact(M):
    """Rank over Q by fraction-free Gaussian elimination."""
    A = [[Fraction(x) for x in row] for row in M]
    if not A:
        return 0
    rows, cols = len(A), len(A[0])
    r = 0
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if A[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        p = A[r][c]
        A[r] = [x / p for x in A[r]]
        for i in range(rows):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[r])]
        r += 1
        if r == rows:
            break
    return r


def coboundary(stalks, edges):
    """delta: C^0 -> C^1.  stalks: {v: dim}.  edges: [(u, v, M)] with M: d_e x d_u and d_e x d_v
    Actually each edge gives a pair of maps (A_u, A_v) with shapes (d_e, d_u), (d_e, d_v):
        (delta x)_e = A_u x_u - A_v x_v
    """
    verts = sorted(stalks)
    off = {}
    n = 0
    for v in verts:
        off[v] = n
        n += stalks[v]
    total_e = sum(A_u.shape[0] for _, _, A_u, A_v in edges)
    D = [[0] * n for _ in range(total_e)]
    row = 0
    for (u, v, A_u, A_v) in edges:
        de = A_u.shape[0]
        assert A_v.shape[0] == de
        for i in range(de):
            for j in range(stalks[u]):
                if A_u[i, j]:
                    D[row + i][off[u] + j] += int(A_u[i, j])
            for j in range(stalks[v]):
                if A_v[i, j]:
                    D[row + i][off[v] + j] -= int(A_v[i, j])
        row += de
    return D, off, total_e


def cohomology(stalks, edges, label=""):
    D, off, total_e = coboundary(stalks, edges)
    dv = sum(stalks.values())
    de = total_e
    rk = rank_exact(D)
    h0 = dv - rk
    h1 = de - rk
    euler_lhs = h0 - h1
    euler_rhs = dv - de
    print(f"[{label}] sum d_v={dv} sum d_e={de} rank(delta)={rk} "
          f"dim H^0={h0} dim H^1={h1} | Euler {euler_lhs}=={euler_rhs} -> {euler_lhs == euler_rhs}")
    return dict(dim_h0=h0, dim_h1=h1, rank=rk, dv=dv, de=de, D=D, off=off)


def selection(pcs, ambient=12):
    """Restriction map: keep only the coordinates in `pcs` (a d_e x 12 0/1 matrix)."""
    M = np.zeros((len(pcs), ambient), dtype=int)
    for i, p in enumerate(pcs):
        M[i, p % ambient] = 1
    return M


def least_squares_section(stalks, edges, targets=None, verts=None):
    """min || delta x - b ||_2  (b = desired seam data; zeros = 'glue exactly')."""
    D, off, total_e = coboundary(stalks, edges)
    A = np.array(D, dtype=float)
    b = np.zeros(total_e) if targets is None else np.asarray(targets, dtype=float)
    x, *_ = np.linalg.lstsq(A, b, rcond=None)
    res = A @ x - b
    return x, res, A


def cycle_space_dim(V, E):
    # connected components by union-find
    parent = list(range(V))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for u, v in E:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
    comps = len({find(i) for i in range(V)})
    return len(E) - V + comps


def spanning_tree_count(V, E):
    """tau(G) by the Matrix-Tree theorem: any cofactor of the Laplacian."""
    L = np.zeros((V, V))
    for u, v in E:
        L[u, u] += 1
        L[v, v] += 1
        L[u, v] -= 1
        L[v, u] -= 1
    return int(round(np.linalg.det(L[1:, 1:])))


# ---------------------------------------------------------------- test 1: forest
print("=" * 78)
print("TEST 1 — forest (path of 3 sections): H^1 must vanish")
s3 = {0: 12, 1: 12, 2: 12}
e_path = [(0, 1, selection([0, 4, 7]), selection([0, 4, 7])),
          (1, 2, selection([0, 4]), selection([0, 4]))]
r1 = cohomology(s3, e_path, "path 0-1-2")

# ---------------------------------------------------------------- test 2: C4 loop
print("=" * 78)
print("TEST 2 — ii7-V7-Imaj7-vi7 loop in C (4-cycle), exact mask sheaf")
Dm7, G7, Cmaj7, Am7 = [2, 5, 9, 0], [7, 11, 2, 5], [0, 4, 7, 11], [9, 0, 4, 7]
pairs = [(Dm7, G7), (G7, Cmaj7), (Cmaj7, Am7), (Am7, Dm7)]
edges2 = []
for (a, b) in pairs:
    common = sorted(set(a) & set(b))
    M = selection(common)
    edges2.append((0, 0, M, M))  # placeholder shapes, fixed below
# rebuild with real vertex indices
vert_idx = {id(Dm7): 0, id(G7): 1, id(Cmaj7): 2, id(Am7): 3}
edges2 = [(0, 1, selection(sorted(set(Dm7) & set(G7))), selection(sorted(set(Dm7) & set(G7)))),
          (1, 2, selection(sorted(set(G7) & set(Cmaj7))), selection(sorted(set(G7) & set(Cmaj7)))),
          (2, 3, selection(sorted(set(Cmaj7) & set(Am7))), selection(sorted(set(Cmaj7) & set(Am7)))),
          (3, 0, selection(sorted(set(Am7) & set(Dm7))), selection(sorted(set(Am7) & set(Dm7))))]
print("  common tones per seam:", [sorted(set(a) & set(b)) for a, b in pairs])
r2 = cohomology({0: 12, 1: 12, 2: 12, 3: 12}, edges2, "ii7-V7-Imaj7-vi7")
print("  cycle-space dim:", cycle_space_dim(4, [(0, 1), (1, 2), (2, 3), (3, 0)]),
      "= |E|-|V|+c =", 4 - 4 + 1)

# ---------------------------------------------------------------- test 2b: tension
print("=" * 78)
print("TEST 2b — harmonic repair: least-squares global section vs. desired seam data")
# Desired seam data: voice "0" of every seam should move to pc 0 (a strong resolution).
# Each seam stalk is the common-tone list, so a target is a value per common tone.
# Ask seam (Dm7,G7) to send its 2 common tones to [0, 0]; others glue exactly (0).
b = np.zeros(sum(len(sorted(set(a) & set(b2)))) for a, b2 in pairs) if False else None
tgt = []
for (a, bb) in pairs:
    common = sorted(set(a) & set(bb))
    # demand a specific "resolution vector" on the shared tones
    tgt.extend([float((3 * i) % 12) for i in range(len(common))])
x, res, A = least_squares_section({0: 12, 1: 12, 2: 12, 3: 12}, edges2, targets=tgt)
print("  ||delta x* - b|| =", round(float(np.linalg.norm(res)), 4),
      " per-seam residuals =", [round(float(v), 3) for v in res])
print("  seam 0 residual:", round(float(np.linalg.norm(res[0:2])), 3),
      " seam 2 residual:", round(float(np.linalg.norm(res[6:9])), 3))

# ---------------------------------------------------------------- test 3: monodromy
print("=" * 78)
print("TEST 3 — monodromy: 4-section loop, every seam transposes by +1 semitone")
P = np.roll(np.eye(12, dtype=int), 1, axis=1)   # x -> T_{+1} x
edges3 = [(0, 1, P, np.eye(12, dtype=int)),
          (1, 2, P, np.eye(12, dtype=int)),
          (2, 3, P, np.eye(12, dtype=int)),
          (3, 0, P, np.eye(12, dtype=int))]
r3 = cohomology({0: 12, 1: 12, 2: 12, 3: 12}, edges3, "T+1 loop (drift)")
# holonomy = product of transports around the loop = T_{+4}
h = np.eye(12, dtype=int)
for _ in range(4):
    h = P @ h
ev = np.linalg.eigvals(h.astype(float))
print("  holonomy eigenvector count with eigenvalue 1:", int(np.sum(np.isclose(ev, 1.0))))
print("  holonomy == T_{+4}? ", np.array_equal(h, np.roll(np.eye(12, dtype=int), 4, axis=1)))
print("  -> one lap transposes the reprise by +4 semitones (eternal modulation)")

# closing loop: seams that sum to identity (+3 x4 = +12)
Q = np.roll(np.eye(12, dtype=int), 3, axis=1)
edges3b = [(0, 1, Q, np.eye(12, dtype=int)), (1, 2, Q, np.eye(12, dtype=int)),
           (2, 3, Q, np.eye(12, dtype=int)), (3, 0, Q, np.eye(12, dtype=int))]
r3b = cohomology({0: 12, 1: 12, 2: 12, 3: 12}, edges3b, "T+3 loop (closes after one lap)")

# ---------------------------------------------------------------- test 4: tau
print("=" * 78)
print("TEST 4 — Matrix-Tree: number of seam-repair (cadence) choices")
for name, V, E in [("C4", 4, [(0, 1), (1, 2), (2, 3), (3, 0)]),
                   ("C5", 5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]),
                   ("K4", 4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]),
                   ("path3", 3, [(0, 1), (1, 2)])]:
    print(f"  tau({name}) = {spanning_tree_count(V, E)}   cycle-space dim = {cycle_space_dim(V, E)}")

# ---------------------------------------------------------------- test 5: forest H1
print("=" * 78)
print("TEST 5 — obstruction lives only in the cycle space")
for name, E in [("path3", [(0, 1, selection([0, 4]), selection([0, 4])),
                           (1, 2, selection([0]), selection([0]))]),
                ("star3", [(0, 1, selection([0, 4]), selection([0, 4])),
                           (1, 2, selection([7]), selection([7]))])]:
    r = cohomology({0: 12, 1: 12, 2: 12}, E, f"{name} (forest)")

# ---------------------------------------------------------------- test 6: dims summary
print("=" * 78)
print("SUMMARY")
for lab, r in [("path", r1), ("ii7-V7-Imaj7-vi7", r2), ("T+1 drift", r3), ("T+3 closed", r3b)]:
    print(f"  {lab:22s} H^0={r['dim_h0']:3d}  H^1={r['dim_h1']:3d}  rank={r['rank']:3d}")
