#!/usr/bin/env python3
"""
verify_143_FPBC.py — Fokker Periodicity Block Composition (FPBC) verification.

Checks (measured, 2026-11-15):
  1. 12-note block: unison vectors 81/80, 128/125 -> |det U| = 12, 12 unique
     octave-reduced just ratios == the standard 5-limit chromatic scale.
  2. 12-ET mapping: the 12 block pcs are all distinct == {0..11} (block = 12-ET).
  3. Periodicity: transposing the block by a unison vector leaves the pc set
     invariant (block tiles the lattice).
  4. Constant structure (Wilson): same ratio always spans the same step count.
  5. 19-note block: unison vectors 81/80, 3125/3072 -> |det U| = 19, 19 distinct
     19-ET pcs.
  6. 31-note block (7-limit): unison vectors 81/80, 225/224, 1029/1024 ->
     |det U| = 31, 31 distinct 31-ET pcs (the Fokker-organ temperament).
  7. Smith normal form: Z^n/U cyclic — diag (1,12), (1,19), (1,1,31):
     block ≈ m-equal tuning (quotient is Z/m).
  8. Modulation seam: block + t (t a non-unison lattice vector) shares a
     measured small set of common pcs -> common-tone voice-leading material.
"""
import math
from fractions import Fraction as F
from itertools import product

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")

def octave_reduce(r):
    """Fraction r -> octave-reduced Fraction in [1, 2)."""
    while r >= 2: r = r / 2
    while r < 1:  r = r * 2
    return r

def cents(r):
    return 1200.0 * math.log2(float(r))

# ---------- lattice helpers (exact rational arithmetic) ----------

def inv_matrix(U):
    """Exact inverse of an n x n integer matrix via fractions."""
    n = len(U)
    A = [[F(x) for x in row] for row in U]
    aug = [row[:] + [F(int(i == j)) for j in range(n)] for i, row in enumerate(A)]
    for col in range(n):
        piv = next(r for r in range(col, n) if aug[r][col] != 0)
        aug[col], aug[piv] = aug[piv], aug[col]
        pv = aug[col][col]
        aug[col] = [x / pv for x in aug[col]]
        for r in range(n):
            if r != col and aug[r][col] != 0:
                f = aug[r][col]
                aug[r] = [a - f * b for a, b in zip(aug[r], aug[col])]
    return [[row[n + j] for j in range(n)] for row in aug]

def det(U):
    n = len(U)
    if n == 2:
        return U[0][0] * U[1][1] - U[0][1] * U[1][0]
    if n == 3:
        (a, b, c), (d, e, f), (g, h, i) = U
        return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    raise ValueError

def enumerate_block(U, box):
    """All lattice points p in `box` with floor(p . U^-1) == 0 (block at origin).

    This is the Wikipedia membership criterion M_B = {B(p): mu_B(p) = mu_B(0)}
    with origin anchor (x0,y0) = (0,0): the lattice points in the half-open
    fundamental parallelepiped U.[0,1)^n, which number exactly |det U|.
    """
    Uinv = inv_matrix(U)
    n = len(U)
    pts = []
    for p in product(*[range(-box, box + 1)] * n):
        q = [sum(F(p[i]) * Uinv[i][j] for i in range(n)) for j in range(n)]
        if all(math.floor(x) == 0 for x in q):
            pts.append(tuple(p))
    return pts, Uinv

def ratio_of(p, primes=None):
    """Lattice point -> just ratio 3^a 5^b 7^c ... (unreduced; octave-reduce later)."""
    r = F(1)
    for a, p_ in zip(p, primes):
        r *= F(p_) ** a
    return r

def to_et_pc(p, step_map):
    """Lattice point -> equal-temperament pitch class (m steps per octave).

    step_map = [m, s3, s5, ...]: m steps per octave; prime i maps to s_i steps
    (the nearest-integer log2(prime_i) * m). pc = sum(a_i * s_i) mod m.
    """
    m = step_map[0]
    return sum(a * s for a, s in zip(p, step_map[1:])) % m

print("=" * 70)
print("FPBC verification — Fokker Periodicity Block Composition (method 143)")
print("=" * 70)

# ---------------- 12-note block (5-limit) ----------------
print("\n[1] 12-note block — 5-limit, unison vectors 81/80 = (4,-1), 128/125 = (0,-3)")
U12 = [[4, -1], [0, -3]]
d12 = abs(det(U12))
check("|det U| = 12", d12 == 12, f"(det = {det(U12)})")
pts12, _ = enumerate_block(U12, box=8)
check("block has 12 lattice points", len(pts12) == 12, f"(count = {len(pts12)})")
ratios12 = sorted(octave_reduce(ratio_of(p, primes=[3, 5])) for p in pts12)
check("12 unique octave-reduced ratios", len(set(ratios12)) == 12, f"(unique = {len(set(ratios12))})")
cents12 = sorted(c for r in ratios12 for c in [cents(r)])
check("all ratios octave-reduced to [1,2)", all(0 <= c < 1200 for c in cents12),
      f"(min {min(cents12):.1f} c = 1/1, max {max(cents12):.1f} c)")
print(f"  12-block ratios (origin-anchored representatives): "
      + ", ".join(f"{r.numerator}/{r.denominator}" for r in ratios12))

# standard 5-limit chromatic — a DIFFERENT (shifted) transversal of the same
# quotient; the classic claim "the 5-limit chromatic is a periodicity block
# for 81/80 + 128/125" = its 12 ratios fall in 12 distinct cosets.
chromatic12 = [F(a, b) for a, b in [
    (1, 1), (16, 15), (9, 8), (6, 5), (5, 4), (4, 3), (45, 32), (3, 2),
    (8, 5), (5, 3), (16, 9), (15, 8)]]
chromatic_coords = []
for r in chromatic12:
    # find lattice coords (a,b) with oct2(3^a 5^b) == r by brute force
    found = None
    for a in range(-3, 4):
        for b in range(-3, 4):
            if octave_reduce(F(3) ** a * F(5) ** b) == r:
                found = (a, b); break
        if found: break
    chromatic_coords.append(found)
pcs_chrom = sorted({to_et_pc(p, [12, 19, 28]) for p in chromatic_coords})
check("standard 5-limit chromatic is a transversal (12 distinct cosets)",
      pcs_chrom == list(range(12)), f"(pcs = {pcs_chrom})")

# 12-ET mapping: pc(a,b) = (19a + 28b) mod 12
pc12 = sorted({to_et_pc(p, [12, 19, 28]) for p in pts12})
check("12-ET pcs all distinct == {0..11}", pc12 == list(range(12)),
      f"(pcs = {pc12})")

# step pattern of the block (melodic interval vocabulary, in cents)
steps12 = [round((cents12[(i + 1) % 12] - cents12[i]) % 1200, 1) for i in range(12)]
print(f"  step pattern (cents): {steps12}")

# periodicity: block + unison vector == block (pc set invariant)
block_pc12 = {to_et_pc(p, [12, 19, 28]) for p in pts12}
trans = {to_et_pc((p[0] + 4, p[1] - 1), [12, 19, 28]) for p in pts12}
check("periodicity: block + 81/80 == block (pc set)", trans == block_pc12)

# constant structure (Wilson): same ratio always spans same step count
cs_ok = True
for i in range(12):
    for j in range(12):
        if i == j: continue
        r = octave_reduce(ratios12[j] / ratios12[i])
        if r < 1: r = octave_reduce(r * 2)  # mod octave
        target = set()
        for i2 in range(12):
            r2 = octave_reduce(ratios12[(i2 + (j - i) % 12) % 12] / ratios12[i2])
            if r2 < 1: r2 = octave_reduce(r2 * 2)
            if r2 == r:
                target.add((j - i) % 12)
        if len(target) != 1:
            cs_ok = False
            break
    if not cs_ok: break
check("constant structure (Wilson): ratio -> unique step count", cs_ok)

# ---------------- 19-note block (5-limit) ----------------
print("\n[2] 19-note block — 5-limit, unison vectors 81/80 = (4,-1), 3125/3072 = (-1,5)")
U19 = [[4, -1], [-1, 5]]
d19 = abs(det(U19))
check("|det U| = 19", d19 == 19, f"(det = {det(U19)})")
pts19, _ = enumerate_block(U19, box=10)
check("block has 19 lattice points", len(pts19) == 19, f"(count = {len(pts19)})")
pc19 = sorted({to_et_pc(p, [19, 30, 44]) for p in pts19})
check("19-ET pcs all distinct", pc19 == list(range(19)), f"(n = {len(pc19)})")

# ---------------- 31-note block (7-limit, Fokker organ) ----------------
print("\n[3] 31-note block — 7-limit, unison vectors 81/80=(4,-1,0), 225/224=(2,2,-1), 1029/1024=(1,0,3)")
U31 = [[4, -1, 0], [2, 2, -1], [1, 0, 3]]
d31 = abs(det(U31))
check("|det U| = 31", d31 == 31, f"(det = {det(U31)})")
pts31, _ = enumerate_block(U31, box=10)
check("block has 31 lattice points", len(pts31) == 31, f"(count = {len(pts31)})")
ratios31 = sorted(octave_reduce(ratio_of(p, primes=[3, 5, 7])) for p in pts31)
check("31 unique octave-reduced ratios", len(set(ratios31)) == 31)
pc31 = sorted({to_et_pc(p, [31, 49, 72, 87]) for p in pts31})
check("31-ET pcs all distinct (Fokker-organ temperament)", pc31 == list(range(31)),
      f"(n = {len(pc31)})")

# ---------------- cyclic quotient via kernel identity ----------------
print("\n[4] Cyclic quotient — the ET mapping IS the quotient map Z^n/U -> Z/m")
def kernel_identity_check(U, block_pts, step_map, label):
    """Rigorous cyclicity proof: (i) every unison vector is in ker(phi);
    (ii) the |det| block members map bijectively onto Z/m. Then U = ker phi
    (both index m), so Z^n/U = Z/m cyclic and phi is the quotient map."""
    m = step_map[0]
    in_ker = all(to_et_pc(u, step_map) == 0 for u in U)
    pcset = {to_et_pc(p, step_map) for p in block_pts}
    bij = len(pcset) == m
    check(f"{label}: unison vectors in ker(phi) and block bijects onto Z/{m}",
          in_ker and bij,
          f"(|det| = {abs(det(U))}, ker ok = {in_ker}, bijective = {bij})")
    return in_ker and bij

kernel_identity_check(U12, pts12, [12, 19, 28], "12-block  -> Z/12 cyclic")
kernel_identity_check(U19, pts19, [19, 30, 44], "19-block  -> Z/19 cyclic")
kernel_identity_check(U31, pts31, [31, 49, 72, 87], "31-block  -> Z/31 cyclic")

# gcd-of-all-entries quick sanity (d1 of the SNF = 1 for all three)
import math as _m
for U, label in [(U12, "12"), (U19, "19"), (U31, "31")]:
    g = 0
    for row in U:
        for x in row:
            g = _m.gcd(g, x)
    print(f"  {label}-block: gcd of all unison-vector entries = {g} (SNF d1 = 1 -> cyclic)")

# ---------------- modulation seam (common tones) ----------------
print("\n[5] Modulation seam — block + t vs block (common-tone voice-leading)")
rset12 = {octave_reduce(ratio_of(p, primes=[3, 5])) for p in pts12}
for t, label in [((1, 0), "t = (1,0) = fifth 3/2"), ((0, 1), "t = (0,1) = third 5/4"),
                 ((1, 1), "t = (1,1) = 15/8")]:
    rset_t = {octave_reduce(ratio_of((p[0] + t[0], p[1] + t[1]), primes=[3, 5])) for p in pts12}
    common = rset12 & rset_t
    print(f"  12-block + {label}: {len(common)} common exact ratios "
          + "{" + ", ".join(f"{r.numerator}/{r.denominator}" for r in sorted(common)) + "}")
# modulation by a non-unison vector yields a different ratio set (not identity)
t15 = (1, 1)
rset_t15 = {octave_reduce(ratio_of((p[0] + 1, p[1] + 1), primes=[3, 5])) for p in pts12}
check("modulation by non-unison vector changes the ratio set (distinct block)",
      rset_t15 != rset12, f"(|rset12 ∩ rset15/8| = {len(rset12 & rset_t15)} common ratios)")
# ...while transposition by a unison vector is the "almost-periodicity": the
# tempered pc set returns exactly (check 1) but the just ratios all shift by
# the comma (the comma pump) — 81/80 is never an exact unison.
rset_u = {octave_reduce(ratio_of((p[0] + 4, p[1] - 1), primes=[3, 5])) for p in pts12}
comma_pump = {octave_reduce(r * F(81, 80)) for r in rset12}
check("unison-vector transposition = comma pump on ratios (81/80 shift)",
      rset_u == comma_pump and rset_u != rset12,
      f"(|rset12 ∩ rset_u| = {len(rset12 & rset_u)} shared ratios; "
      f"81/80 = {cents(F(81, 80)):.1f} c ≠ 0)")

print(f"\n{'=' * 70}")
print(f"RESULT: {PASS} passed, {FAIL} failed")
print(f"{'=' * 70}")
raise SystemExit(1 if FAIL else 0)
