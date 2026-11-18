"""Verify the mathematics behind Method 145 Dyck Path Ballot Composition (DPBC).

Pure combinatorics checks (no musicom engine needed):
1. Catalan numbers C_n = binom(2n,n)/(n+1) vs OEIS A000108 (first 20 terms).
2. Brute-force count of Dyck paths of semilength n (never below 0, ends at 0) == C_n.
3. Bertrand ballot: # {p A's, q B's, A strictly ahead throughout} = (p-q)/(p+q)*binom(p+q,p).
4. Narayana: # Dyck paths of semilength n with exactly k peaks == N(n,k) = C(n-1,k-1)*C(n,k-1)/k; sum_k == C_n (OEIS A001263).
5. Arch decomposition: # Dyck paths with exactly k arches == Narayana row (second interpretation).
6. Chung-Feller equipartition: for each k in 0..n, # {+-1 paths (0,0)->(2n,0) with exactly 2k steps above axis} == C_n, and (n+1)*C_n == binom(2n,n).
7. Cycle-lemma uniform sampling: sample uniformly via rotation of random balanced word; chi-square-ish sanity: empirical mean peak count vs Narayana expectation.
8. Motzkin generalization: level steps (rests) -- Motzkin numbers A001006 (first 10).
"""
from math import comb, factorial
from collections import Counter
import random

def catalan(n):
    return comb(2*n, n) // (n + 1)

# 1. Catalan vs OEIS A000108
oeis = [1,1,2,5,14,42,132,429,1430,4862,16796,58786,208012,742900,2674440,
        9694845,35357670,129644790,477638700,1767263190,6564120420]
got = [catalan(n) for n in range(21)]
assert got == oeis, (got[:10], oeis[:10])
print("[1] Catalan C_n n=0..20 == OEIS A000108  : OK")

# 2. Brute-force Dyck count
def dyck_count(n):
    # paths of 2n steps, U=+1, D=-1, never below 0, end at 0
    cnt = 0
    def rec(h, u, d):
        nonlocal cnt
        if u == 0 and d == 0:
            if h == 0: cnt += 1
            return
        if u > 0: rec(h+1, u-1, d)
        if d > 0 and h > 0: rec(h-1, u, d-1)
    rec(0, n, n)
    return cnt
for n in range(1, 9):
    assert dyck_count(n) == catalan(n), (n, dyck_count(n), catalan(n))
print("[2] brute-force Dyck count n=1..8 == C_n  : OK")

# 3. Bertrand ballot (strict lead)
def ballot(p, q):
    # A gets p votes, B gets q votes, p>q; count orders where A STRICTLY leads
    # after every prefix. Place B only when lead > 1 (after placing, lead-1 > 0).
    cnt = 0
    def rec(a, b, lead):
        nonlocal cnt
        if a == p and b == q:
            cnt += 1   # strict lead throughout is guaranteed by the placement rule
            return
        if a < p: rec(a+1, b, lead+1)
        if b < q and lead > 1: rec(a, b+1, lead-1)
    rec(0, 0, 0)
    return cnt
for (p, q) in [(3,1),(3,2),(4,1),(4,2),(5,2),(5,3),(6,3)]:
    assert ballot(p, q) == (p-q)/(p+q) * comb(p+q, p)
print("[3] Bertrand ballot STRICT-lead counts == (p-q)/(p+q)*C(p+q,p) : OK")

# 3b. Ties-allowed ballot: # sequences with #A>=#B after every prefix == C_n when p=q=n
# (and in general (p-q+1)/(p+1)*C(p+q,p) -- the "weak" ballot number; p>=q)
def ballot_ties(p, q):
    cnt = 0
    def rec(a, b, lead):
        nonlocal cnt
        if a == p and b == q:
            cnt += 1
            return
        if a < p: rec(a+1, b, lead+1)
        if b < q and lead > 0: rec(a, b+1, lead-1)
    rec(0, 0, 0)
    return cnt
for n in range(1, 8):
    assert ballot_ties(n, n) == catalan(n)
print("[3b] ties-allowed ballot p=q=n == C_n (this is exactly the Dyck count) : OK")

# 4. Narayana peaks
def narayana(n, k):
    return comb(n-1, k-1) * comb(n, k-1) // k
def dyck_peaks_dist(n):
    # a peak = an up-step immediately followed by a down-step (maximal run U...D)
    dist = Counter()
    def rec(h, u, d, peaks, prev_up):
        if u == 0 and d == 0:
            dist[peaks] += 1
            return
        if u > 0: rec(h+1, u-1, d, peaks, True)
        if d > 0 and h > 0: rec(h-1, u, d-1, peaks + (1 if prev_up else 0), False)
    rec(0, n, n, 0, False)
    return dist
for n in range(1, 9):
    dist = dyck_peaks_dist(n)
    assert sum(dist.values()) == catalan(n)
    for k in range(1, n+1):
        assert dist[k] == narayana(n, k), (n, k, dist[k], narayana(n,k))
print("[4] Narayana peak distribution N(n,k)=C(n-1,k-1)*C(n,k-1)/k, sum=C_n : OK")

# 5. Arch decomposition: every Dyck path = concatenation of PRIMITIVE Dyck paths
# (arches, which touch height 0 only at their ends). # primitive of semilength m == C_{m-1};
# # k-arch paths of semilength n == [x^n] (x*C(x))^k where C(x) = Catalan GF = (1-sqrt(1-4x))/(2x).
def primitive_count(m):
    # Dyck paths of semilength m returning to 0 ONLY at the very end
    cnt = 0
    def rec(h, u, d):
        nonlocal cnt
        if u == 0 and d == 0:
            if h == 0: cnt += 1
            return
        if u > 0: rec(h+1, u-1, d)
        if d > 0 and h > 0:
            # a D landing on 0 is allowed only as the FINAL step (u==0 and d==1)
            if h - 1 == 0 and not (u == 0 and d == 1):
                return
            rec(h-1, u, d-1)
    rec(0, m, m)
    return cnt
for m in range(1, 8):
    assert primitive_count(m) == catalan(m-1), (m, primitive_count(m), catalan(m-1))
print("[5a] primitive Dyck paths of semilength m == C_{m-1} : OK")

def dyck_arches_dist(n):
    dist = Counter()
    def rec(h, u, d, arches, at_zero):
        if u == 0 and d == 0:
            dist[arches] += 1
            return
        if u > 0:
            rec(h+1, u-1, d, arches + (1 if at_zero else 0), False)
        if d > 0 and h > 0:
            rec(h-1, u, d-1, arches, h == 1)
    rec(0, n, n, 0, True)
    return dist
# polynomial: B(x) = x*C(x) = (1 - sqrt(1-4x))/2 ; arch-GF A_k(x) = B(x)^k
def catalan_poly(N):
    # coefficients of C(x) up to x^N : C(x) = 1 + x*C(x)^2
    c = [0]*(N+1); c[0] = 1
    for n in range(1, N+1):
        c[n] = sum(c[i]*c[n-1-i] for i in range(n))
    return c
def mul(p, q, N):
    r = [0]*(N+1)
    for i, a in enumerate(p):
        if a == 0: continue
        for j, b in enumerate(q):
            if i+j <= N: r[i+j] += a*b
    return r
for n in range(1, 9):
    dist = dyck_arches_dist(n)
    C = catalan_poly(n)
    B = [0]*(n+1)                       # x*C(x)
    for i in range(1, n+1): B[i] = C[i-1]
    P = [1] + [0]*n
    for k in range(1, n+1):
        P = mul(P, B, n)                # B(x)^k
        assert dist[k] == P[n], (n, k, dist[k], P[n])
print("[5b] k-arch count == [x^n](x*C(x))^k (first-return decomposition) : OK")

# 6. Chung-Feller equipartition
def chung_feller(n):
    # count +-1 paths with exactly 2k steps strictly ABOVE the axis
    # (interior of the step above y=0: U step from h>=0, or D step from h>=1)
    res = {}
    for mask in range(1 << (2*n)):
        if bin(mask).count("1") != n:      # need exactly n up steps (end at height 0)
            continue
        h = 0; above = 0
        for i in range(2*n):
            up = (mask >> i) & 1
            if up:
                if h >= 0: above += 1      # U step, interior y in (h, h+1)
                h += 1
            else:
                if h >= 1: above += 1      # D step, interior y in (h-1, h)
                h -= 1
        res[above] = res.get(above, 0) + 1
    return res
for n in range(1, 6):
    cf = chung_feller(n)
    for k in range(0, n+1):
        assert cf.get(2*k, 0) == catalan(n), (n, k, cf.get(2*k), catalan(n))
    assert sum(cf.values()) == comb(2*n, n)
    assert (n+1) * catalan(n) == comb(2*n, n)
print("[6] Chung-Feller equipartition: exactly 2k steps above axis -> C_n each; (n+1)C_n=C(2n,n) : OK")

# 7. Uniform Dyck sampling sanity (recursive first-return sampler; mean peaks vs
# Narayana expectation, mean arches vs return-probability expectation)
def sample_dyck(n, rng):
    # recursive uniform sampler via first-return decomposition:
    # Dyck(n) = primitive(j) + Dyck(n-j), primitive(j) = U + Dyck(j-1) + D,
    # P(first arch has semilength j) = C_{j-1} * C_{n-j} / C_n
    memo = {}
    def dyck(m):
        if m == 0: return []
        if m in memo: return memo[m]
        # choose first-arch semilength j in 1..m
        probs = [catalan(j-1) * catalan(m-j) for j in range(1, m+1)]
        tot = catalan(m)
        r = rng.random() * tot
        acc = 0
        for j in range(1, m+1):
            acc += probs[j-1]
            if r < acc: break
        arch = [1] + dyck(j-1) + [-1]     # primitive arch: U (Dyck(j-1)) D
        rest = dyck(m-j)
        memo[m] = arch + rest
        return memo[m]
    return dyck(n)
def peaks_of(path):
    # count U-then-D pairs
    return sum(1 for i in range(len(path)-1) if path[i] == 1 and path[i+1] == -1)
def arches_of(path):
    # count returns to 0 (including the final return) = number of arches
    h = 0; a = 0
    for s in path:
        h += s
        if h == 0: a += 1
    return a
rng = random.Random(145)
n = 10
N = 20000
pk_emp = sum(peaks_of(sample_dyck(n, rng)) for _ in range(N)) / N
pk_th  = sum(k * narayana(n, k) for k in range(1, n+1)) / catalan(n)
assert abs(pk_emp - pk_th) < 0.05, (pk_emp, pk_th)
ar_emp = sum(arches_of(sample_dyck(n, rng)) for _ in range(N)) / N
ar_th  = sum(catalan(j) * catalan(n-j) for j in range(1, n+1)) / catalan(n)  # E[# returns]
assert abs(ar_emp - ar_th) < 0.05, (ar_emp, ar_th)
print(f"[7] recursive uniform sampler n=10, N={N}: mean peaks {pk_emp:.3f} (theory {pk_th:.3f}), "
      f"mean arches {ar_emp:.3f} (theory {ar_th:.3f}) : OK")
# note: rotation-to-first-minimum is BIASED (weights Dyck path D by 1/#arches(D)):
# UUDD gets 4 balanced words, UDUD gets 2 (n=2) -- the bijective uniform route is
# the recursive first-return sampler above or the generalized cycle lemma with
# rejection on the good-rotation count.

# 8. Motzkin numbers (level steps = rests) A001006
def motzkin(n):
    # paths (0,0)->(n,0) steps U,D,level, never below 0
    cnt = 0
    def rec(i, h):
        nonlocal cnt
        if i == n:
            if h == 0: cnt += 1
            return
        rec(i+1, h+1)      # U
        if h > 0: rec(i+1, h-1)  # D
        rec(i+1, h)        # level
    rec(0, 0)
    return cnt
oeis_motzkin = [1,1,2,4,9,21,51,127,323,835,2188]
got_m = [motzkin(n) for n in range(11)]
assert got_m == oeis_motzkin, (got_m, oeis_motzkin)
print("[8] Motzkin M_n n=0..10 == OEIS A001006 (level step = rest) : OK")

print()
print("ALL 8 MATHEMATICAL CHECKS PASSED")
