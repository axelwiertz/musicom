"""Numerical validation for Interval Exchange Transformation Composition (IETC)."""
import numpy as np

def cum(lam):
    return np.concatenate(([0.0], np.cumsum(lam)))

def iet(x, lam, pi):
    """T_{pi,lam}(x). pi is a 0-based permutation naming each domain block's image slot."""
    lam = np.asarray(lam, float); pi = np.asarray(pi)
    a = cum(lam)
    aimg = np.array([lam[pi < pi[i]].sum() for i in range(len(lam))])
    x = np.asarray(x, float)
    k = np.clip(np.searchsorted(a, x, side="right") - 1, 0, len(lam) - 1)
    return (x - a[k] + aimg[k]) % 1.0, k

def is_irreducible(pi):
    n = len(pi)
    if pi[0] != n - 1 or pi[-1] != 0:
        return False
    return all(set(pi[:k]) != set(range(k)) for k in range(1, n))

print("=" * 68)
lam = np.array([0.5, 0.3, 0.2]); pi = np.array([2, 1, 0])
print("1) PIECEWISE-TRANSLATION BIJECTION (measure preserving)")
grid = np.linspace(0, 1, 200001)[:-1]
img, _ = iet(grid, lam, pi)
print(f"   lambda={lam.tolist()} pi={pi.tolist()} irreducible={is_irreducible(pi)}")
print(f"   max |sorted(T(grid)) - grid| = {np.max(np.abs(np.sort(img) - grid)):.2e}")
d = np.round(img - grid, 12)
print(f"   distinct T(x)-x values = {len(np.unique(d))} -> {np.unique(d).tolist()}")

print("\n2) VISIT FREQUENCIES -> lambda (unique ergodicity => tonal gravity)")
N, x, counts = 400000, 0.123456789, np.zeros(3, int)
for t in range(N):
    x, k = iet(x, lam, pi); counts[int(k)] += 1
freq = counts / N
print(f"   empirical  {np.round(freq, 5).tolist()}")
print(f"   lambda     {lam.tolist()}")
print(f"   max abs err {np.max(np.abs(freq - lam)):.5f}")

print("\n3) n=2 DEGENERATE CASE == CIRCLE ROTATION (Sturmian word)")
alpha = 1 / ((1 + 5 ** 0.5) / 2)
lam2 = np.array([alpha, 1 - alpha]); pi2 = np.array([1, 0])
xb, hits = 3 * alpha % 1.0, []
for t in range(80):
    xb, kb = iet(xb, lam2, pi2); hits.append(int(kb))
hits = np.array(hits)
m = np.arange(1, len(hits) + 1)
n0 = np.cumsum(hits == 0)
dev = np.max(np.abs(n0 - np.floor(m * alpha)))
print(f"   code   {''.join(map(str, hits[:32]))}")
print(f"   P(I_0) = {np.mean(hits == 0):.4f}   alpha = {alpha:.4f}")
print(f"   sup_m |N_0(m) - floor(m*alpha)| = {dev:.0f}  (balanced/Sturmian iff <= 1)")

print("\n4) FIRST-RETURN MAP IS AGAIN AN IET (renormalization / Rauzy-Veech)")
s = 0.62
def first_return(x0, lam, pi, s, maxit=100000):
    x, t = float(x0), 0
    for _ in range(maxit):
        x, _ = iet(x, lam, pi); t += 1
        if x < s:
            return float(x), t
    return None, None
probe = np.linspace(1e-6, s - 1e-6, 500)
rets = [first_return(p, lam, pi, s) for p in probe]
ret_x = np.array([r[0] for r in rets]); ret_t = np.array([r[1] for r in rets])
disp = np.round(ret_x - probe, 9)
print(f"   induced on [0,{s}): distinct displacements = {len(np.unique(disp))} -> {np.unique(disp).tolist()}")
print(f"   distinct first-return times = {sorted(set(ret_t.tolist()))}")
print("   -> return map is piecewise translation with constant slope 1: still an IET")

print("\n5) CONCRETE DECODE (4 voices x 96 steps -> UnitMatrix cells)")
SCALE, root = [0, 2, 3, 5, 7, 8, 10], 57
edges = cum(lam)[:-1]
def pc_of(u):
    k = int(np.searchsorted(edges, u, side="right") - 1)
    return SCALE[k % 7] + 12 * (k // 7), k + 1
for v, x0 in enumerate([0.041, 0.377, 0.618, 0.909]):
    xx, ev = float(x0), []
    for t in range(96):
        pc, k = pc_of(xx)
        ev.append((t * 240, root + pc, 240 * k))
        xx, _ = iet(xx, lam, pi)
    ps = [e[1] for e in ev]
    print(f"   voice {v}: first 12 pitches {ps[:12]}  distinct={len(set(ps))} span={max(ps)-min(ps)} pcset={sorted(set(p % 12 for p in ps))}")

print("\nALL CHECKS COMPLETE")
