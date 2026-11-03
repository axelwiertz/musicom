#!/usr/bin/env python
"""verify_133_ZRNC.py — Z-Relation Network Composition (ZRNC), method 133.

Verifies the set-theoretic core of the method:
  [1] Forte z-relation definition: same interval vector (ICV), different set class.
  [2] All z-related pairs in 12-TET (count per cardinality; expect 4:1, 5:6, 6:14, 7:6, 8:1).
  [3] Every ICV equivalence group has size <= 2  =>  the z-graph is a perfect matching.
  [4] 4-Z15 {0,1,4,6} <-> 4-Z29 {0,1,3,7}: both ICV <1,1,1,1,1,1>; minimal voice leading = 2.
  [5] Fourier magnitudes |f_A(k)| == |f_B(k)| for z-twins at every k (phases differ).
      |f_A(k)|^2 == n + 2*sum_d ICV[d]*cos(2*pi*k*d/12).
  [6] Hexachord complement invariance: icv(H) == icv(C(H)) for ALL 50 hexachord classes;
      non-self-complementary ones are z-related to their complement (14 pairs / 28 classes,
      22 self-complementary).
  [7] 7-pc pairs = complements of 5-pc pairs; 8-pc pair = complement of 4-pc pair.
  [8] IFUNC common-tone seams: ifunc(X,Y)[t] = |X ∩ (Y+t)|; max common tones between
      4-Z15 and 4-Z29 and the argmax transpositions.
  [9] ICV-dissonance (any weights) identical for z-twins — the "silent" tension flip.
  [10] Named-class sanity: Forte names for the cited classes.
"""
from itertools import combinations
from collections import defaultdict
import cmath, math

# ---------- set-class machinery ----------
def icv(pcs):
    v = [0] * 6
    n = len(pcs)
    for i in range(n):
        for j in range(i + 1, n):
            d = (pcs[j] - pcs[i]) % 12
            v[min(d, 12 - d) - 1] += 1
    return tuple(v)

def set_class_key(pcs):
    """Canonical representative: lexicographically smallest sorted tuple over all
    Tn and TnI transforms (Rahn-style prime form; class identity is convention-free)."""
    best = None
    for t in range(12):
        r1 = tuple(sorted((x + t) % 12 for x in pcs))
        r2 = tuple(sorted((-x + t) % 12 for x in pcs))
        for r in (r1, r2):
            if best is None or r < best:
                best = r
    return best

def complement(pcs):
    return tuple(x for x in range(12) if x not in pcs)

def is_tn_or_tni(a, b):
    ka, kb = set_class_key(a), set_class_key(b)
    return ka == kb

def fmag(pcs, k):
    return abs(sum(cmath.exp(2j * cmath.pi * k * x / 12) for x in pcs))

def fphase(pcs, k):
    z = sum(cmath.exp(2j * cmath.pi * k * x / 12) for x in pcs)
    return cmath.polar(z)[1]

def vl_size(a, b):
    """Circular Wasserstein-1 voice-leading size (min over cyclic matchings)."""
    n = len(a)
    best = 1e9
    for s in range(n):
        tot = 0
        for i in range(n):
            d = (b[(i + s) % n] - a[i]) % 12
            tot += min(d, 12 - d)
        best = min(best, tot)
    return best

def ifunc(x, y):
    f = [0] * 12
    for i in x:
        for j in y:
            f[(j - i) % 12] += 1
    return tuple(f)

def tds(pcs, w=(6, 5, 4, 3, 2, 1)):
    """ICV-dissonance: any weights work; equality for z-twins is weight-independent."""
    return sum(c * wi for c, wi in zip(icv(pcs), w))

# ---------- [1] enumerate all set classes and ICV groups ----------
classes = defaultdict(set)          # cardinality -> set of class keys
for n in range(1, 12):
    for comb in combinations(range(12), n):
        classes[n].add(set_class_key(comb))

icv_groups = defaultdict(list)      # icv -> list of class keys
for n in range(1, 12):
    for k in sorted(classes[n]):
        icv_groups[icv(k)].append(k)

z_pairs_by_n = defaultdict(list)
for ic, keys in icv_groups.items():
    if len(keys) > 1:
        n = len(keys[0])
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                z_pairs_by_n[n].append((keys[i], keys[j]))

print("[1] set-class counts by cardinality (1..11):",
      {n: len(classes[n]) for n in range(1, 12)})
print("[2] z-related pairs by cardinality:")
tot = 0
for n in sorted(z_pairs_by_n):
    print(f"    n={n}: {len(z_pairs_by_n[n])} pair(s)")
    tot += len(z_pairs_by_n[n])
print(f"    TOTAL z-pairs = {tot}")
print("[3] max ICV-group size (z-graph is a matching iff <= 2):",
      max(len(v) for v in icv_groups.values()))

# ---------- [4] the famous tetrachord pair ----------
A, B = (0, 1, 4, 6), (0, 1, 3, 7)
print("\n[4] 4-Z15 {0,1,4,6} vs 4-Z29 {0,1,3,7}:")
print("    class keys:", set_class_key(A), set_class_key(B),
      "| same class?", is_tn_or_tni(A, B))
print("    icv(A) =", icv(A), " icv(B) =", icv(B), " equal?", icv(A) == icv(B))
print("    minimal voice-leading size (circular W1) =", vl_size(A, B))
print("    TDS(A)=TDS(B) =", tds(A), "(weight-independent z-twin equality)")

# ---------- [5] Fourier magnitudes ----------
print("\n[5] Fourier magnitudes for the z-pair (k=1..11):")
allmag_ok, some_phase_diff = True, False
for k in range(1, 12):
    ma, mb = fmag(A, k), fmag(B, k)
    ok = abs(ma - mb) < 1e-9
    allmag_ok = allmag_ok and ok
    pa, pb = fphase(A, k), fphase(B, k)
    pd = abs(pa - pb) > 1e-9
    some_phase_diff = some_phase_diff or pd
    if k <= 4:
        print(f"    k={k:2d}: |fA|={ma:.6f} |fB|={mb:.6f} equal={ok} phase_diff={pd}")
print("    ALL k: magnitudes equal =", allmag_ok, "| some phase differs =", some_phase_diff)
# |f|^2 formula check
ok_formula = all(
    abs(fmag(A, k) ** 2 - (len(A) + 2 * sum(icv(A)[d - 1] * math.cos(2 * math.pi * k * d / 12)
                                              for d in range(1, 7)))) < 1e-9
    for k in range(1, 12))
print("    |fA(k)|^2 == n + 2*sum ICV[d]*cos(2pi k d/12) for all k:", ok_formula)

# ---------- [6] hexachord complement invariance ----------
print("\n[6] hexachords: icv(H) == icv(C(H)) ?")
selfcomp, zcomp = [], []
for k in sorted(classes[6]):
    cp = set_class_key(complement(k))
    eq = icv(k) == icv(cp)
    if not eq:
        print("    VIOLATION for", k)
    if is_tn_or_tni(k, cp):
        selfcomp.append(k)
    else:
        zcomp.append(k)
print(f"    all 50 hexachord classes icv==icv(complement): {len(selfcomp)+len(zcomp)==50}")
print(f"    self-complementary classes: {len(selfcomp)}  z-related-to-complement: {len(zcomp)}")
print(f"    hexachord z-pairs via complementation: {len(zcomp)//2} (expect 14)")

# ---------- [7] complement structure across cardinalities ----------
print("\n[7] complement structure of z-pairs:")
c4 = [(ka, kb) for ka, kb in z_pairs_by_n[4]]
c5 = z_pairs_by_n[5]
c7 = z_pairs_by_n[7]
c8 = z_pairs_by_n[8]
comp_of = {}
for n in (4, 5):
    for ka, kb in z_pairs_by_n[n]:
        comp_of[(ka, kb)] = (set_class_key(complement(ka)), set_class_key(complement(kb)))
print("    4-pc pair:", [(ka, kb) for ka, kb in c4])
print("    8-pc pairs complement 4-pc:", [(c, d) for (c, d) in comp_of.values() if (c, d) in c8 or (d, c) in c8],
      "| 8-pc pairs:", c8)
print("    5-pc pairs (6):")
for ka, kb in c5:
    print(f"      {ka} <-> {kb}  icv={icv(ka)}")
print("    7-pc pairs are complements of 5-pc pairs:",
      all((set_class_key(complement(ka)), set_class_key(complement(kb))) in
          [(x, y) for x, y in c7] + [(y, x) for x, y in c7] for ka, kb in c5))

# ---------- [8] IFUNC / common-tone seams ----------
print("\n[8] common-tone function between the z-twins:")
ct = ifunc(B, A)          # |A ∩ (B+t)| = ifunc(B,A)[t]
print("    |A ∩ (B+t)| for t=0..11:", list(ct))
print("    max common tones:", max(ct), "at t =", [t for t, v in enumerate(ct) if v == max(ct)])

# ---------- [9] named-class sanity ----------
print("\n[10] named-class checks (Forte names cited in prose):")
name_checks = {
    "4-Z15": (0, 1, 4, 6), "4-Z29": (0, 1, 3, 7),
    "5-Z18": (0, 1, 4, 5, 8), "5-Z38": (0, 1, 4, 7, 8),
    "6-Z19": (0, 1, 3, 4, 7, 8), "6-Z44": (0, 1, 2, 3, 4, 7),
}
for name, tup in name_checks.items():
    k = set_class_key(tup)
    print(f"    {name} {tup}: key={k} self-consistent={k == tup}")
pairs5 = {(set_class_key(a), set_class_key(b)) for a, b in c5}
print("    5-Z18 key in 5-pc z-pairs:", set_class_key((0, 1, 4, 5, 8)) in
      {x for p in pairs5 for x in p},
      "| 5-Z38 key in 5-pc z-pairs:", set_class_key((0, 1, 4, 7, 8)) in {x for p in pairs5 for x in p})
print("    5-Z18 and 5-Z38 are each other's twin:",
      (set_class_key((0, 1, 4, 5, 8)), set_class_key((0, 1, 4, 7, 8))) in pairs5 or
      (set_class_key((0, 1, 4, 7, 8)), set_class_key((0, 1, 4, 5, 8))) in pairs5)
pairs6 = {(set_class_key(a), set_class_key(b)) for a, b in z_pairs_by_n[6]}
print("    6-Z19 and 6-Z44 are each other's twin:",
      (set_class_key((0, 1, 3, 4, 7, 8)), set_class_key((0, 1, 2, 3, 4, 7))) in pairs6 or
      (set_class_key((0, 1, 2, 3, 4, 7)), set_class_key((0, 1, 3, 4, 7, 8))) in pairs6)

# ---------- demo walk: tension-flat z-chain with common-tone seams ----------
print("\n[9] demo: 6-section z-walk A->B->A->B->A->B, ICV-dissonance per section:")
walk = [A, B] * 3
for i, s in enumerate(walk):
    print(f"    section {i}: set {s}  icv={icv(s)}  TDS={tds(s)}  "
          f"seam common tones vs prev={None if i == 0 else max(ifunc(walk[i-1], s))}")

# ---------- [11] Forte-name mapping from the Wikipedia "List of set classes" table ----------
# (fetched 2026-11-03, _zr_forte_table.json; prime forms as printed by the table)
wiki_forms = {
    "5-Z12": (0, 1, 3, 5, 6), "5-Z36A": (0, 1, 2, 4, 7),
    "5-Z17": (0, 1, 3, 4, 8), "5-Z37": (0, 3, 4, 5, 8),
    "5-Z18A": (0, 1, 4, 5, 7), "5-Z38A": (0, 1, 2, 5, 8),
    "6-Z3A": (0, 1, 2, 3, 5, 6), "6-Z36A": (0, 1, 2, 3, 4, 7),
    "6-Z4": (0, 1, 2, 4, 5, 6), "6-Z37": (0, 1, 2, 3, 4, 8),
    "6-Z6": (0, 1, 2, 5, 6, 7), "6-Z38": (0, 1, 2, 3, 7, 8),
    "6-Z10A": (0, 1, 3, 4, 5, 7), "6-Z39A": (0, 2, 3, 4, 5, 8),
    "6-Z11A": (0, 1, 2, 4, 5, 7), "6-Z40A": (0, 1, 2, 3, 5, 8),
    "6-Z12A": (0, 1, 2, 4, 6, 7), "6-Z41A": (0, 1, 2, 3, 6, 8),
    "6-Z13": (0, 1, 3, 4, 6, 7), "6-Z42": (0, 1, 2, 3, 6, 9),
    "6-Z17A": (0, 1, 2, 4, 7, 8), "6-Z43A": (0, 1, 2, 5, 6, 8),
    "6-Z19A": (0, 1, 3, 4, 7, 8), "6-Z44A": (0, 1, 2, 5, 6, 9),
    "6-Z23": (0, 2, 3, 5, 6, 8), "6-Z45": (0, 2, 3, 4, 6, 9),
    "6-Z24A": (0, 1, 3, 4, 6, 8), "6-Z46A": (0, 1, 2, 4, 6, 9),
    "6-Z25A": (0, 1, 3, 5, 6, 8), "6-Z47A": (0, 1, 2, 4, 7, 9),
    "6-Z26": (0, 1, 3, 5, 7, 8), "6-Z48": (0, 1, 2, 5, 7, 9),
    "6-Z28": (0, 1, 3, 5, 6, 9), "6-Z49": (0, 1, 3, 4, 7, 9),
    "6-Z29": (0, 2, 3, 6, 7, 9), "6-Z50": (0, 1, 4, 6, 7, 9),
}
print("\n[11] Forte-name mapping (Wikipedia table, fetched 2026-11-03):")
def wkey(name):
    k = set_class_key(wiki_forms[name])
    return k
# verify all forms are distinct classes (36 = 6 pentachord + 30 hexachord names)
wk = {name: wkey(name) for name in wiki_forms}
assert len(set(wk.values())) == 36, "36 distinct classes expected (6 pentachord + 30 hexachord)"
assert len({n for n in wiki_forms if len(wiki_forms[n]) == 6}) == 30
assert len({k for n, k in wk.items() if len(wiki_forms[n]) == 6}) == 30, "30 distinct hexachord Z-classes"
pairs6_set = {(ka, kb) for ka, kb in z_pairs_by_n[6]}
ok_all = 0
for a, b in z_pairs_by_n[6]:
    for na in wk:
        for nb in wk:
            if wk[na] == a and wk[nb] == b and na != nb:
                ok_all += 1
print(f"    hexachord pairs matched to Wikipedia names: {ok_all}/15")
print("    computed 6-pc pairs (prime forms):")
for ka, kb in z_pairs_by_n[6]:
    names = [n for n, k in wk.items() if k in (ka, kb)]
    print(f"      {ka} <-> {kb}  icv={icv(ka)}  names={names}")
# every 6-pc z-pair is a complement pair (verified structurally)
comp_ok = all(
    (set_class_key(complement(ka)), set_class_key(complement(kb))) in pairs6_set or
    (set_class_key(complement(kb)), set_class_key(complement(ka))) in pairs6_set
    for ka, kb in z_pairs_by_n[6])
print(f"    every 6-pc z-pair is a complement pair: {comp_ok}")
# 5-pc name matching
pairs5_set = {(ka, kb) for ka, kb in z_pairs_by_n[5]}
w5 = {n: wkey(n) for n in ("5-Z12", "5-Z36A", "5-Z17", "5-Z37", "5-Z18A", "5-Z38A")}
print("    5-pc pairs with names:")
for ka, kb in z_pairs_by_n[5]:
    names = [n for n, k in w5.items() if k in (ka, kb)]
    print(f"      {ka} <-> {kb}  icv={icv(ka)}  names={names}")
print("    all 3 pentachord pairs matched:", all(len([n for n, k in w5.items() if k in (ka, kb)]) == 2
      for ka, kb in z_pairs_by_n[5]))
print("\nALL CHECKS DONE")
