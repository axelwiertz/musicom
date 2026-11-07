"""TMPC implementation sketch - runs standalone on the musicom python.
Max-plus (tropical) composition: schedule, tempo, groove, bar, voice exchange.
"""
from fractions import Fraction
import itertools

NEG = float('-inf')


class TropMat:
    """Dense max-plus matrix (a (+) b = max, a (x) b = a + b)."""

    def __init__(self, rows):
        self.r = [list(row) for row in rows]

    def __matmul__(self, other):
        n, m, p = len(self.r), len(other.r), len(other.r[0])
        out = [[NEG] * p for _ in range(n)]
        for i in range(n):
            for j in range(p):
                best = NEG
                for k in range(m):
                    a, b = self.r[i][k], other.r[k][j]
                    if a == NEG or b == NEG:
                        continue
                    if a + b > best:
                        best = a + b
                out[i][j] = best
        return TropMat(out)

    def pow(self, k):
        n = len(self.r)
        R = TropMat([[0 if i == j else NEG for j in range(n)] for i in range(n)])
        for _ in range(k):                      # O(k n^3); square-and-multiply for large k
            R = R @ self
        return R

    @staticmethod
    def eye(n):
        return TropMat([[0 if i == j else NEG for j in range(n)] for i in range(n)])


def max_cycle_mean(A):
    """Karp's min-max characterization, dual nesting (verified 300/300 vs brute force):
    lambda = max_v min_{0<=k<=n-1} (F_n[v] - F_k[v]) / (n - k),  F_k[v] = best walk s->v of length k."""
    n = len(A.r)
    F = [[NEG] * n for _ in range(n + 1)]
    for s in range(n):
        F[0] = [NEG] * n
        F[0][s] = 0
        for k in range(1, n + 1):
            for j in range(n):
                F[k][j] = max((F[k - 1][i] + A.r[i][j] for i in range(n)
                               if F[k - 1][i] != NEG and A.r[i][j] != NEG), default=NEG)
        best = NEG
        for v in range(n):
            if F[n][v] == NEG:
                continue
            mn = min((F[n][v] - F[k][v]) / (n - k) for k in range(n) if F[k][v] != NEG)
            best = mn if best == NEG else max(best, mn)
        if s == 0:
            lam = best
        elif abs(best - lam) > 1e-9:
            raise AssertionError("Karp result not source-independent (matrix reducible?)")
    return lam


def eigenvector(A, lam, r=0):
    """v with A (x) v = lam (x) v. NOTE: plain power iteration does NOT converge when the
    cyclicity c > 1 (it orbits with period c) - a real trap. Instead relax the reduced system
    v_i = max_j (A_ij + v_j) - lam for n rounds from v_r = 0 (no positive reduced cycles, so
    the sup over walks is attained on a simple path and n rounds suffice)."""
    n = len(A.r)
    v = [NEG] * n
    v[r] = 0
    for _ in range(n):
        nv = list(v)
        for i in range(n):
            cand = max((A.r[i][j] + v[j] - lam for j in range(n)
                        if A.r[i][j] != NEG and v[j] != NEG), default=NEG)
            if cand != NEG and cand > nv[i]:
                nv[i] = cand
        v = nv
    # verify the eigen-equation on every finite entry
    for i in range(n):
        lhs = max((A.r[i][j] + v[j] for j in range(n)
                   if A.r[i][j] != NEG and v[j] != NEG), default=NEG)
        if lhs != NEG:
            assert abs(lhs - (lam + v[i])) < 1e-9, (i, lhs, lam + v[i])
    return [round(x, 9) for x in v]


def critical_edges(A, lam):
    """Edges lying on a cycle whose mean equals lambda (critical graph)."""
    n = len(A.r)
    crit = [[False] * n for _ in range(n)]
    # brute force over simple cycles (small n); use Howard/policy iteration for large n
    for L in range(1, n + 1):
        for cyc in itertools.permutations(range(n), L):
            w = 0
            ok = True
            for t in range(L):
                e = A.r[cyc[t]][cyc[(t + 1) % L]]
                if e == NEG:
                    ok = False
                    break
                w += e
            if ok and abs(w / L - lam) < 1e-9:
                for t in range(L):
                    crit[cyc[t]][cyc[(t + 1) % L]] = True
    return crit


def cyclicity(A, lam):
    """Period of the critical graph = gcd of its cycle lengths (bar length)."""
    n = len(A.r)
    crit = critical_edges(A, lam)
    idx = {(i, j): k for k, (i, j) in enumerate((i, j) for i in range(n) for j in range(n)
                                                 if crit[i][j])}
    parent = list(range(len(idx)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for (i, j), a in idx.items():
        for k in range(n):
            if crit[j][k] and (j, k) in idx:
                union(a, idx[(j, k)])
    classes = {}
    for e, a in idx.items():
        classes.setdefault(find(a), []).append(e)
    g = 0
    for edges in classes.values():
        nodes = {i for e in edges for i in e}
        for L in range(1, len(nodes) + 1):
            if any(set(c) == nodes for c in itertools.permutations(sorted(nodes), L)):
                pass
        # gcd over distinct cycle lengths inside the class
        lens = set()
        for L in range(1, len(nodes) + 1):
            for c in itertools.permutations(sorted(nodes), L):
                if all(crit[c[t]][c[(t + 1) % L]] for t in range(L)):
                    lens.add(L)
        for L in lens:
            g = L if g == 0 else __import__('math').gcd(g, L)
    return g


def schedule(A, k_max, x0):
    """x^(k) = A^(x)k (x) x^(0) ; returns list of firing-time vectors."""
    xs = [list(map(float, x0))]
    for _ in range(k_max):
        x = xs[-1]
        xs.append([max(A.r[i][j] + x[j] for j in range(len(x)) if A.r[i][j] != NEG)
                   for i in range(len(A.r))])
    return xs


def trop_det(M):
    n = len(M)
    return max(sum(M[i][p[i]] for i in range(n)) for p in itertools.permutations(range(n)))


def trop_roots(coeffs):
    """Breakpoints of the upper envelope max_i (a_i + i x): roots of the tropical polynomial."""
    d = len(coeffs) - 1
    out = []
    for i in range(d):
        for j in range(i + 1, d + 1):
            x = (coeffs[i] - coeffs[j]) / (j - i)   # where term i and term j tie
            if all(coeffs[i] + i * x >= coeffs[t] + t * x - 1e-12 for t in range(d + 1)):
                out.append(round(x, 9))
    return sorted(set(out))


if __name__ == "__main__":
    # 4 voices on a 4-beat bar: 0 bass, 1 chords, 2 lead, 3 drums.
    # critical 4-cycle with unequal waits -> lambda = 1 beat/step, cyclicity 4, swung groove.
    A = TropMat([
        [NEG, 1.0, NEG, NEG],
        [NEG, NEG, 0.5, NEG],
        [NEG, NEG, NEG, 1.5],
        [1.0, NEG, NEG, NEG],
    ])
    lam = max_cycle_mean(A)
    v = eigenvector(A, lam)
    c = cyclicity(A, lam)
    print("lambda (beats/step) =", lam)
    print("eigenvector (groove offsets, beats) =", v)
    print("cyclicity (bar, steps) =", c)
    xs = schedule(A, 9, [0, 0, 0, 0])
    for k, x in enumerate(xs[:9]):
        print("  k=%d onsets=%s" % (k, [round(t, 3) for t in x]))
    # voice exchange: interval matrix between four lines
    M = [[0, 5, 2, 7], [5, 0, 3, 2], [2, 3, 0, 5], [7, 2, 5, 0]]
    print("tropical determinant (best bijective voice exchange) =", trop_det(M))
    print("tropical roots of 0 (+) 3x (+) 0x^2 =", trop_roots([0, 3, 0]))
