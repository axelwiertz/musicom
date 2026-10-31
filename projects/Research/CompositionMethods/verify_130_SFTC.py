"""Verify_130_SFTC.py — numeric verification of Subshift of Finite Type Composition claims.

Checks:
1. Golden-mean shift (forbid "11") word counts = Fibonacci F(n+2); entropy = log(phi).
2. Perron eigenvalue of golden-mean adjacency [[0,1],[1,1]] = phi.
3. (d,k) RLL capacities: (1,inf) = log phi; (2,inf) plastic constant ~1.46557.
4. Morse-Hedlund: p(n) <= n  =>  periodic (checked on a Fibonacci word prefix).
5. Parry measure row-stochasticity: p_ij = a_ij v_j / (lambda v_i).
6. Voice-crossing forbidden-word demo: product alphabet {a,b} x {c,d}, forbid columns
   where lower-voice pitch > upper-voice pitch => count of allowed 1-blocks.
7. De Bruijn graph of order 2 for golden-mean shift: states = allowed 2-blocks,
   edge labels = next symbol; bi-infinite paths == shift sequences.
"""
import math

phi = (1 + math.sqrt(5)) / 2

# ---- 1. golden mean shift word counts ----
def allowed_words(n):
    out = []
    def rec(s):
        if len(s) == n:
            out.append(s); return
        rec(s + '0')
        if not s or s[-1] != '1':
            rec(s + '1')
    rec('')
    return sorted(out)

def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

ok1 = True
for n in range(1, 12):
    cnt = len(allowed_words(n))
    if cnt != fib(n + 2):
        ok1 = False
        print(f"FAIL n={n}: allowed={cnt} fib={fib(n+2)}")
print(f"[1] golden-mean allowed words n=1..11 == F(n+2): {ok1}")
p8 = len(allowed_words(8))
print(f"    p(8)={p8}  empirical (1/8)ln p(8)={math.log(p8)/8:.5f}  log(phi)={math.log(phi):.5f}")

# ---- 2. Perron eigenvalue ----
A = [[0, 1], [1, 1]]
x = [1.0, 1.0]
nrm = 1.0
for _ in range(200):
    x = [A[0][0]*x[0] + A[0][1]*x[1], A[1][0]*x[0] + A[1][1]*x[1]]
    nrm = max(x)
    x = [v/nrm for v in x]
lam = nrm
print(f"[2] power-iter spectral radius of [[0,1],[1,1]] = {lam:.8f} (phi={phi:.8f})  match={abs(lam-phi)<1e-6}")

# ---- 3. RLL (d,inf) capacity: correct (d,inf) adjacency ----
# states 0..d: state j = j zeros since last 1; state 0 = last symbol was 1.
# (d,inf): >= d zeros between ones, unlimited zero-run length.
def rll_adjacency(d):
    m = d + 1
    B = [[0]*m for _ in range(m)]
    B[0][1] = 1                          # emit 0 -> one zero since last 1
    for j in range(1, d):
        B[j][j+1] = 1                    # emit 0 -> longer run (can't emit 1 yet)
    B[d][0] = 1                          # emit 1 -> run of d zeros is enough
    B[d][d] = 1                          # emit 0 -> stay at max run (k=inf)
    return B

def spectral_radius(B, iters=500):
    m = len(B)
    x = [1.0]*m
    nrm = 1.0
    for _ in range(iters):
        x = [sum(B[i][j]*x[j] for j in range(m)) for i in range(m)]
        nrm = max(x); x = [v/nrm for v in x]
    return nrm

# enumerate words directly for small n (independent cross-check)
def rll_words(d, n):
    out = []
    def rec(s):
        if len(s) == n:
            out.append(s); return
        if not s or s[-1] == '0':
            rec(s + '1')
        rec(s + '0')
    rec('')
    # filter: runs of zeros between ones >= d
    res = []
    for w in out:
        runs = [len(r) for r in w.split('1')]
        body = runs[1:-1]
        if all(r >= d for r in body):
            res.append(w)
    return res

c1 = spectral_radius(rll_adjacency(1))
c2 = spectral_radius(rll_adjacency(2))
print(f"[3] RLL(1,inf) lambda={c1:.6f} (phi={phi:.6f}) match={abs(c1-phi)<1e-5}")
# supergolden ratio: largest root of x^3 - x^2 - 1 = 0 (bisection)
def root_cubic_pm1(lo, hi):
    f = lambda x: x**3 - x**2 - 1
    for _ in range(80):
        mid = (lo + hi)/2
        if f(lo)*f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo+hi)/2
sg = root_cubic_pm1(1.4, 1.5)
print(f"    RLL(2,inf) lambda={c2:.6f} supergolden root(x^3-x^2-1)={sg:.6f} match={abs(c2-sg)<1e-5}")
print(f"    log-lambda RLL(1,inf)={math.log(c1):.5f} nats/sym = {math.log2(c1):.5f} bits/sym")
w4 = rll_words(2, 8)
w5 = rll_words(2, 9)
print(f"    direct count RLL(2,inf): p(8)={len(w4)} p(9)={len(w5)} "
      f"ratio={len(w5)/len(w4):.4f} (lambda={c2:.4f})")

# ---- 4. Morse-Hedlund: p(n) <= n => periodic ----
# Fibonacci word (fixed point of 0->01, 1->0): aperiodic, p(n) = n+1
w = '0'
for _ in range(20):
    w = w.replace('0', 'x').replace('1', '0').replace('x', '01')
w = w[:64]
def complexity(word, n):
    return len({word[i:i+n] for i in range(len(word)-n+1)})
mh_ok = all(complexity(w, n) >= n+1 for n in range(2, 20))
print(f"[4] Fibonacci word p(n) >= n+1 for n=2..19 (Morse-Hedlund bound): {mh_ok}")

# ---- 5. Parry measure row-stochasticity ----
v = [1.0, phi]                      # right PF eigenvector of golden-mean matrix
lam = phi
P = [[A[i][j]*v[j]/(lam*v[i]) for j in range(2)] for i in range(2)]
rows = [sum(r) for r in P]
print(f"[5] Parry P=[[{P[0][0]:.4f},{P[0][1]:.4f}],[{P[1][0]:.4f},{P[1][1]:.4f}]] row sums={rows}  stochastic={all(abs(r-1)<1e-9 for r in rows)}")

# ---- 6. voice-crossing as forbidden columns (2-voice product vertex shift) ----
# voice L alphabet {60,62,64} (C D E), voice U alphabet {60,62,64}; forbid crossing: L > U
low = [60, 62, 64]; up = [60, 62, 64]
cols = [(l, u) for l in low for u in up if l <= u]   # allowed columns (no crossing)
print(f"[6] 3x3 product alphabet, forbid L>U: {len(cols)}/9 columns allowed "
      f"(vs 6 if equal forbidden too)")
# parallel-perfect-fifth as forbidden 2-column word: (62,74) followed by (62,74) etc.
fifths = [((62, 74), (62, 74)), ((57, 69), (59, 71))]
print(f"    parallel-fifth detector: forbidden 2-block pairs = {fifths}")

# ---- 7. de Bruijn graph order 2 for golden-mean shift ----
states = allowed_words(2)           # 00, 01, 10
edges = []
for s in states:
    for a in '01':
        t = s[1] + a
        if '11' not in s + a and '11' not in t:
            edges.append((s, a, t))
print(f"[7] golden-mean de Bruijn graph (order 2): states={states} edges={[(s,a) for s,a,_ in edges]}")
# state paths of length k (k states) <-> words of length k+1; count length-L words
L = 6
paths = {(s,): 1 for s in states}
for _ in range(L - 2):                      # edges = L-2
    nxt = {}
    for path, c in paths.items():
        for s, a, t in edges:
            if s == path[-1]:
                key = path + (t,)
                nxt[key] = nxt.get(key, 0) + c
    paths = nxt
total = sum(paths.values())
print(f"    words of length {L} via de Bruijn-edge walks = {total} (F({L+2})={fib(L+2)})  "
      f"match={total==fib(L+2)}")
print(f"    direct allowed_words(6) = {len(allowed_words(6))}")

print("\nALL CHECKS DONE")
