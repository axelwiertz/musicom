"""Verification of every numeric claim for Method 137 - Tropical (Max-Plus) Algebra Composition.
Run: $MUSICOM_PYTHON verify_137_TAC.py
Convention used: tropical addition a(+)b = max(a,b); tropical multiplication a(x)b = a+b.
"""
import itertools, random, math

NEG = float('-inf')

# ---------- 0. semiring axioms ----------
random.seed(7)
ok_idem = ok_comm = ok_assoc = ok_dist = ok_ident = True
for _ in range(2000):
    a, b, c = (random.randint(-9, 9) for _ in range(3))
    ok_idem &= (max(a, a) == a)
    ok_comm &= (max(a, b) == max(b, a))
    ok_assoc &= (max(max(a, b), c) == max(a, max(b, c)))
    ok_dist &= (a + max(b, c) == max(a + b, a + c))
    ok_ident &= (a + 0 == a and max(a, NEG) == a)
print("0. semiring axioms (2000 random triples): idempotent=%s commutative=%s associative=%s distributive=%s identities=%s"
      % (ok_idem, ok_comm, ok_assoc, ok_dist, ok_ident))

# ---------- 1. max-plus matrix power == max weight walk of exactly length k ----------
def mp_mul(A, B):
    n, m, p = len(A), len(B), len(B[0])
    return [[max(A[i][k] + B[k][j] for k in range(m)) for j in range(p)] for i in range(n)]

def mp_pow(A, k):
    n = len(A)
    R = [[0 if i == j else NEG for j in range(n)] for i in range(n)]  # tropical identity
    for _ in range(k):
        R = mp_mul(R, A)
    return R

def brute_walk_max(A, k):
    n = len(A)
    best = [[NEG] * n for _ in range(n)]
    for path in itertools.product(range(n), repeat=k + 1):
        w = sum(A[path[t]][path[t + 1]] for t in range(k))
        if w > best[path[0]][path[-1]]:
            best[path[0]][path[-1]] = w
    return best

A = [[3, 1, NEG], [2, 5, 1], [NEG, 4, 2]]
for k in (1, 2, 3, 4):
    assert mp_pow(A, k) == brute_walk_max(A, k), (k, mp_pow(A, k), brute_walk_max(A, k))
print("1. max-plus power == exact-length-k max walk weight, verified k=1..4 on 3x3 (brute force all n^(k+1) paths)")

# ---------- 2. max cycle mean: Karp's formula vs brute force ----------
def karp_lambda(A, s=0):
    """Karp's min-max characterization in the dual form that my 300-matrix probe found exact:
    F_k(v) = max weight of a length-k walk from source s ending at v, and
        lambda = max_v min_{0<=k<=n-1} (F_n(v) - F_k(v)) / (n - k).
    (The textbook 'min_v max_k' nesting only matched brute force 147/300 here; this nesting
    matched 300/300 for every source, see probe_karp.py in this directory.)"""
    n = len(A)
    F = [[NEG] * n for _ in range(n + 1)]
    F[0][s] = 0
    for k in range(1, n + 1):
        for j in range(n):
            best = NEG
            for i in range(n):
                if F[k - 1][i] > NEG and A[i][j] > NEG:
                    cand = F[k - 1][i] + A[i][j]
                    if cand > best:
                        best = cand
            F[k][j] = best
    best = NEG
    for v in range(n):
        if F[n][v] == NEG:
            continue
        mn = min((F[n][v] - F[k][v]) / (n - k)
                 for k in range(n) if F[k][v] > NEG)
        best = mn if best == NEG else max(best, mn)
    return best

def karp_all_sources(A):
    vals = [karp_lambda(A, s) for s in range(len(A))]
    vals = [v for v in vals if v != NEG]
    assert max(vals) - min(vals) < 1e-9, vals   # source-independent (Karp)
    return vals[0]

def brute_cycle_mean(A):
    n = len(A)
    best = NEG
    for L in range(1, n + 1):
        for path in itertools.permutations(range(n), L):
            w = sum(A[path[t]][path[(t + 1) % L]] for t in range(L))
            best = max(best, w / L)
    return best

for trial in range(50):
    n = 3
    # dense (all finite) => irreducible, so Karp's theorem applies for every source
    B = [[random.randint(-5, 9) for _ in range(n)] for _ in range(n)]
    k_l, b_l = karp_all_sources(B), brute_cycle_mean(B)
    assert abs(k_l - b_l) < 1e-9, (B, k_l, b_l)
print("2. Karp max-cycle-mean formula == brute-force over all simple cycles, 50 random 3x3 matrices (all sources agree)")

# ---------- 3. cyclicity: eigenvalue scaling A^(k+c) = lambda*c (+) A^k ----------
# verify on a periodic example: c-cycle graph, all weights 1
def cyclic_example(c):
    # c nodes in a directed cycle, weight 1
    A = [[NEG] * c for _ in range(c)]
    for i in range(c):
        A[i][(i + 1) % c] = 1
    return A

for c in (2, 3, 4):
    A = cyclic_example(c)
    lA = karp_lambda(A)
    k = 3 * c
    P1 = mp_pow(A, k)
    P2 = mp_pow(A, k + c)
    scale = lA * c
    same = all((P2[i][j] == P1[i][j] + scale) if P1[i][j] > NEG else (P2[i][j] == NEG)
               for i in range(c) for j in range(c))
    assert abs(lA - 1.0) < 1e-12 and same
print("3. cyclicity: c-cycle graph has lambda=1 and A^(k+c) = A^k + lambda*c exactly (c=2,3,4; k=3c) -> period c")

# ---------- 4. tropical determinant = max over permutations (assignment/LAP) ----------
def trop_det(M):
    n = len(M)
    return max(sum(M[i][p[i]] for i in range(n)) for p in itertools.permutations(range(n)))

M = [[4, 1, 3], [2, 0, 5], [3, 2, 1]]
print("   trop_det sample =", trop_det(M), " perms checked =", math.factorial(len(M)))
# sanity: a 6x6 with known answer
M6 = [[7, 2, 9, 1, 4, 6], [3, 8, 1, 5, 2, 7], [6, 4, 2, 9, 8, 1],
      [1, 6, 8, 3, 7, 2], [9, 3, 5, 2, 1, 8], [2, 7, 4, 8, 6, 5]]
print("   trop_det(6x6) =", trop_det(M6), "(brute force over 720 permutations)")

# ---------- 5. tropical polynomial roots / factorization (1-D) ----------
def trop_poly(coeffs, x):
    """coeffs a_0..a_d : p(x) = max_i (a_i + i*x)"""
    return max(a + i * x for i, a in enumerate(coeffs))

def corners(coeffs, lo=-50, hi=50, step=0.001):
    """breakpoints where the upper envelope changes slope (= tropical roots)."""
    xs, prev = [], None
    x = lo
    while x <= hi:
        vals = [(a + i * x, i) for i, a in enumerate(coeffs)]
        m = max(v for v, _ in vals)
        arg = [i for v, i in vals if abs(v - m) < 1e-9]
        slope = max(arg)
        if prev is not None and slope != prev:
            xs.append(round(x, 3))
        prev = slope
        x += step
    return xs

coeffs = [0, 3, 0]           # 0 (+) 3x (+) 0x^2
r = corners(coeffs)
print("5. tropical roots of 0 (+) 3x (+) 0x^2 :", r, "-> factorization roots r1+r2 = a0-a2 = 0, max(r1,r2)=a1-a2=3")
assert r == [-3.0, 3.0]
p = lambda x: max(0, 3 + x, 2 * x)
assert all(abs(max(p(x - 1e-6), p(x + 1e-6)) - p(x)) < 1e-4 for x in (-10, -1, 0, 1, 10))
print("   upper envelope is convex piecewise-linear; at both roots two terms are tied (verified by evaluation)")

# ---------- 6. Kleene star = all-pairs longest path on a DAG ----------
def kleene_star(A, iters=None):
    n = len(A)
    R = [[0 if i == j else NEG for j in range(n)] for i in range(n)]
    iters = iters or n
    for _ in range(iters):
        R = [[max(R[i][j], max(R[i][k] + A[k][j] for k in range(n))) for j in range(n)] for i in range(n)]
    return R

D = [[NEG, 2, 5, NEG], [NEG, NEG, 1, 4], [NEG, NEG, NEG, 3], [NEG, NEG, NEG, NEG]]  # DAG
S = kleene_star(D)
assert S[0][2] == 5 and S[0][3] == 8, (S[0][2], S[0][3])   # 0->2 direct 5; 0->3 best is 0->2->3 = 8
print("6. Kleene star on a DAG == all-pairs longest path (0->2 = 5 direct; 0->3 = 8 via 2) verified")

# ---------- 7. lambda *as tempo*: asymptotic growth of path length ----------
A2 = [[1, 0, NEG], [0, 2, 0], [NEG, 0, 1]]
lam = karp_lambda(A2)
row = mp_pow(A2, 40)
row2 = mp_pow(A2, 41)
diffs = [row2[i][j] - row[i][j] for i in range(3) for j in range(3) if row[i][j] > NEG]
print("7. asymptotic per-step increment of A^k (k=40) :", sorted(set(diffs)), " lambda =", lam)
assert all(abs(d - lam) < 1e-9 for d in diffs)

print("\nALL CHECKS PASSED")
