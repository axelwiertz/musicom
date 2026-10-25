#!/usr/bin/env python3
"""verify_ldsc.py — Method 125 LDSC (Low-Discrepancy Sequence Composition)
Verification of the mathematical invariants claimed in method_125_LDSC.md.

Run: $MUSICOM_PYTHON verify_ldsc.py
Env: musicom (numpy 1.26.4). Deterministic: no RNG except explicit baselines.
"""
import numpy as np


def radical_inverse(n, b):
    """Van der Corput radical inverse g_b(n), n >= 1 (Wikipedia 2026-10-25)."""
    out, inc = 0.0, 1.0 / b
    while n > 0:
        d = n % b
        out += d * inc
        n //= b
        inc /= b
    return out


def vdc(n, b=2):
    return radical_inverse(n, b)


def halton(n, bases=(2, 3)):
    return tuple(radical_inverse(n, b) for b in bases)


def star_discrepancy(xs, mesh=8192):
    """Empirical star discrepancy D*_N over prefixes [0, x)."""
    xs = np.sort(np.asarray(xs, dtype=float))
    N = len(xs)
    if N == 0:
        return 1.0
    grid = np.linspace(0.0, 1.0, mesh)
    counts = np.searchsorted(xs, grid, side="left")
    return float(np.max(np.abs(counts / N - grid)))


results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")


# ---- 1. known first values (exact fractions) -----------------------------
v2 = [vdc(n, 2) for n in range(1, 9)]
v2_exp = [1/2, 1/4, 3/4, 1/8, 5/8, 3/8, 7/8, 1/16]
v3 = [vdc(n, 3) for n in range(1, 9)]
v3_exp = [1/3, 2/3, 1/9, 4/9, 7/9, 2/9, 5/9, 8/9]
check("vdc base-2 first 8 values exact",
      max(abs(a-b) for a, b in zip(v2, v2_exp)) < 1e-12, f"{v2}")
check("vdc base-3 first 8 values exact",
      max(abs(a-b) for a, b in zip(v3, v3_exp)) < 1e-12, f"{v3}")

# ---- 2. star discrepancy: vdc vs random ---------------------------------
N = 1024
xs_vdc = np.array([vdc(n, 2) for n in range(1, N + 1)])
rng = np.random.default_rng(0)
D_vdc = star_discrepancy(xs_vdc)
D_rand = np.mean([star_discrepancy(rng.random(N)) for _ in range(20)])
bound = (np.log2(N) + 2.0) / N
check("star discrepancy vdc2 <= (log2 N + 2)/N bound",
      D_vdc <= bound, f"D*_N(vdc)={D_vdc:.5f} bound={bound:.5f}")
check("star discrepancy vdc << random baseline",
      D_vdc < 0.6 * D_rand, f"D*_N(vdc)={D_vdc:.5f} vs random mean={D_rand:.5f}")

# ---- 3. largest-gap property (dyadic bisection fill) ---------------------
pts = [0.0, 1.0]
ok_lg = True
for n in range(1, 256):
    x = vdc(n, 2)
    # the gap of the OLD points (without x) that contains x must be the
    # largest gap of the old points (ties allowed)
    s_old = sorted(pts)
    old_gaps = [(s_old[i+1] - s_old[i], s_old[i], s_old[i+1])
                for i in range(len(s_old) - 1)]
    my_gap = next(g for g in old_gaps if g[1] <= x < g[2])
    if my_gap[0] < max(g[0] for g in old_gaps) - 1e-12:
        ok_lg = False
        break
    pts.append(x)
check("vdc2 largest-gap bisection fill (n=1..255)",
      ok_lg, "each new point lands in the largest empty gap")

# ---- 4. rhythmic evenness: min inter-onset gap, N=16 in [0,1) -------------
N16 = np.array([vdc(n, 2) for n in range(1, 17)])
gaps_vdc = np.diff(np.sort(np.r_[0.0, N16, 1.0]))
min_gap_vdc = gaps_vdc.min()
min_gap_rand = np.mean([np.diff(np.sort(np.r_[0.0, rng.random(16), 1.0])).min()
                        for _ in range(200)])
check("rhythm evenness: vdc min-gap >> random min-gap",
      min_gap_vdc > 2.0 * min_gap_rand,
      f"min-gap vdc={min_gap_vdc:.4f} vs random mean={min_gap_rand:.4f}")

# ---- 5. 2D Halton (2,3) pitch-class balance vs random --------------------
Nn = 120
pcs_h = np.array([int(vdc(n, 3) * 12) for n in range(1, Nn + 1)])
pcs_r = rng.integers(0, 12, size=Nn)
hist_h, hist_r = np.bincount(pcs_h, minlength=12), np.bincount(pcs_r, minlength=12)
check("Halton(2,3) pc histogram balanced (max dev <= 6)",
      np.max(np.abs(hist_h - Nn/12)) <= 6,
      f"max|dev| Halton={np.max(np.abs(hist_h-Nn/12))} random={np.max(np.abs(hist_r-Nn/12))}")

# ---- 6. region-visit frequencies = region widths (equidistribution) ------
widths = np.array([0.35, 0.20, 0.20, 0.25])          # HOME/LIFT/TENSE/TURN
M = 2000
region = np.array([np.searchsorted(np.cumsum(widths), vdc(n, 3), side="right")
                   for n in range(1, M + 1)])
counts = np.bincount(region, minlength=4) / M
check("region visit frequency == width (equidistribution)",
      np.max(np.abs(counts - widths)) < 0.02,
      f"max|dev|={np.max(np.abs(counts-widths)):.4f} counts={np.round(counts,3)}")

# ---- 7. scrambling: per-section variation with preserved balance ---------
def scramble(xs, mask, bits=24):
    """Digital shift (XOR) scramble: x ^ mask on the bit-reversed lattice."""
    out = []
    for x in xs:
        xi = int(round(x * (1 << bits)))
        out.append(((xi ^ mask) & ((1 << bits) - 1)) / (1 << bits))
    return np.array(out)

xs_vdc64 = np.array([vdc(n, 2) for n in range(1, 65)])
s0 = scramble(xs_vdc64, 0)
s1 = scramble(xs_vdc64, 0x5A5A5A)
s2 = scramble(xs_vdc64, 0x3C3C3C)
check("scramble changes order (variation)",
      not np.allclose(s1, s0) and not np.allclose(s2, s0), "")
D0, D1, D2 = star_discrepancy(s0), star_discrepancy(s1), star_discrepancy(s2)
b64 = (np.log2(64) + 2.0) / 64
check("scrambled sections keep low discrepancy (<= bound)",
      D1 <= b64 and D2 <= b64, f"D*={D0:.4f}/{D1:.4f}/{D2:.4f} bound={b64:.4f}")

# ---- 8. determinism -------------------------------------------------------
check("determinism (pure function of n)",
      np.array_equal(np.array([vdc(n, 2) for n in range(1, 129)]),
                     np.array([vdc(n, 2) for n in range(1, 129)])), "")

# ---- 9. multi-voice independence: 2D Halton (3,5) joint balance -----------
n2 = 400
x35 = np.array([vdc(n, 3) for n in range(1, n2 + 1)])
y35 = np.array([vdc(n, 5) for n in range(1, n2 + 1)])
cell = np.zeros((4, 4))
for a, b in zip((x35 * 4).astype(int), (y35 * 4).astype(int)):
    cell[a, b] += 1
expected = n2 / 16
check("multi-voice joint balance (2D Halton (3,5), 4x4 cells)",
      np.max(np.abs(cell - expected)) <= 6,
      f"max|dev|={np.max(np.abs(cell-expected)):.1f} (expected {expected:.0f}/cell)")

# ---- summary -------------------------------------------------------------
npass = sum(1 for _, ok, _ in results if ok)
nfail = sum(1 for _, ok, _ in results if not ok)
print(f"\n{'-'*60}\nRESULT: {npass} passed, {nfail} failed")
raise SystemExit(1 if nfail else 0)
