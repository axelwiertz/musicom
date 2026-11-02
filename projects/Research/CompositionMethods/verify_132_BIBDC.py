"""Verify facts for method 132: Balanced Incomplete Block Design Composition (BIBDC)."""
import itertools, math
from collections import Counter

def build_sts(v, limit=3_000_000):
    """Backtracking STS(v): all pairs covered exactly once."""
    allp = [frozenset(p) for p in itertools.combinations(range(v), 2)]
    uncovered = set(allp)
    blocks = []
    nodes = [0]

    def rec():
        nodes[0] += 1
        if nodes[0] > limit:
            raise RuntimeError("node limit")
        if not uncovered:
            return True
        best, best_c = None, 10**9
        for p in uncovered:
            a, b = tuple(p)
            c = sum(1 for x in range(v) if x not in p
                    and frozenset((a, x)) in uncovered and frozenset((b, x)) in uncovered)
            if c < best_c:
                best_c, best = c, p
        if best_c == 0:
            return False
        a, b = tuple(best)
        for x in range(v):
            if x in best:
                continue
            t = frozenset((a, b, x))
            trip = [frozenset(q) for q in itertools.combinations(sorted(t), 2)]
            if all(q in uncovered for q in trip):
                for q in trip:
                    uncovered.discard(q)
                blocks.append(tuple(sorted(t)))
                if rec():
                    return True
                blocks.pop()
                for q in trip:
                    uncovered.add(q)
        return False

    ok = rec()
    return (sorted(blocks), nodes[0]) if ok else (None, nodes[0])


def check_design(v, blocks):
    pairs = Counter()
    deg = Counter()
    for b in blocks:
        assert len(set(b)) == 3, b
        for x in b:
            deg[x] += 1
        for p in itertools.combinations(sorted(b), 2):
            pairs[frozenset(p)] += 1
    allp = list(itertools.combinations(range(v), 2))
    lam_ok = all(pairs[frozenset(p)] == 1 for p in allp)
    deg_ok = all(deg[x] == (v - 1) // 2 for x in range(v))
    return dict(b=len(blocks), b_formula=v * (v - 1) // 6, lam_ok=lam_ok,
                r=min(deg.values()), r_formula=(v - 1) // 2, deg_ok=deg_ok,
                npairs=len(pairs), npairs_formula=v * (v - 1) // 2)


def fano():
    return [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]


def ag23():
    """STS(9) = affine plane AG(2,3): points (x,y) in Z3^2, 4 directions x 3 offsets."""
    pts = [(x, y) for x in range(3) for y in range(3)]
    idx = {p: i for i, p in enumerate(pts)}
    lines = []
    # y = m*x + c  (slopes 0,1,2) plus the three verticals x = c
    for m in range(3):
        for c in range(3):
            lines.append([(x, (m * x + c) % 3) for x in range(3)])
    for c in range(3):
        lines.append([(c, y) for y in range(3)])
    cov = Counter()
    for L in lines:
        for p in itertools.combinations(sorted(L), 2):
            cov[p] += 1
    ok = len(lines) == 12 and len(cov) == 36 and all(x == 1 for x in cov.values())
    assert ok, (len(lines), len(cov))
    return [tuple(sorted(idx[p] for p in L)) for L in lines]


def parallel_classes(v, blocks):
    bset = [frozenset(b) for b in blocks]
    used = [False] * len(bset)
    classes = []
    for i in range(len(bset)):
        if used[i]:
            continue
        cls = [i]
        used[i] = True
        cover = set(bset[i])
        for j in range(i + 1, len(bset)):
            if not used[j] and not (cover & bset[j]):
                cover |= bset[j]
                used[j] = True
                cls.append(j)
        classes.append(cls)
        if len(cover) != v:
            return None, f"incomplete {len(cover)}/{v}"
    return classes, all(len(c) == v // 3 for c in classes)


print("== 1. Explicit Fano plane STS(7) ==")
F = fano()
print(check_design(7, F))
bp = [(i, j) for i in range(7) for j in range(i + 1, 7)]
print("block-pair intersections:", dict(Counter(len(set(F[i]) & set(F[j])) for i, j in bp)))
print("blocks:", F)
comp = tuple(sorted(set(range(7)) - set(F[0])))
print("complement of block0 =", comp, "| is a block?", comp in [tuple(sorted(b)) for b in F])

print("\n== 2. Backtracking STS for v = 7, 9, 13, 15 ==")
built = {}
for v in (7, 9, 13, 15):
    bl, nodes = build_sts(v)
    built[v] = bl
    print(v, check_design(v, bl), "nodes", nodes)

print("\n== 3. AG(2,3) = STS(9): 12 blocks, resolution into 4 parallel classes ==")
A = ag23()
print(len(A), check_design(9, A))
classes, ok = parallel_classes(9, A)
print("resolvable:", ok)
for c in classes:
    print("  class:", [sorted(A[i]) for i in c])

print("\n== 4. Kirkman resolution of STS(15) -> 7 parallel classes ==")
classes, ok = parallel_classes(15, built[15])
print("resolvable:", ok, "| n classes:", len(classes) if classes else None,
      "| sizes:", [len(c) for c in classes] if classes else None)

print("\n== 5. Pair-novelty tension curve for STS(7) ==")
print("pairs per block C(3,2) =", math.comb(3, 2), "| total 7*3 =", 21, "| v(v-1)/2 =", 21)
for name, order in (("forward", range(7)), ("reversed", reversed(range(7)))):
    seen, curve = set(), []
    for i in order:
        for p in itertools.combinations(sorted(F[i]), 2):
            seen.add(frozenset(p))
        curve.append(21 - len(seen))
    print(name, "novelty:", curve,
          "| monotone:", all(curve[k] >= curve[k + 1] for k in range(6)),
          "| terminal:", curve[-1])

print("\n== 6. BIBD counting identities vr = bk, lam(v-1) = r(k-1) ==")
for (v, k, lam) in [(7, 3, 1), (9, 3, 1), (13, 3, 1), (15, 3, 1), (7, 3, 2), (9, 4, 3), (6, 3, 2)]:
    r = lam * (v - 1) // (k - 1)
    b = v * r // k
    print(f"  v={v} k={k} lam={lam}: r={r} b={b} vr={v*r} bk={b*k} "
          f"lam(v-1)={lam*(v-1)} r(k-1)={r*(k-1)}")

print("\n== 7. STS admissibility v = 1,3 mod 6 ==")
print("admissible 7..19:", [v for v in range(7, 20) if v % 6 in (1, 3)])

print("\n== 8. Labelled STS(7) count (Fano uniqueness) ==")
cnt = 0
alltrip = [frozenset(t) for t in itertools.combinations(range(7), 3)]
for combo in itertools.combinations(alltrip, 7):
    cov = Counter()
    for t in combo:
        for p in itertools.combinations(sorted(t), 2):
            cov[frozenset(p)] += 1
    if len(cov) == 21 and all(x == 1 for x in cov.values()):
        cnt += 1
print("labelled STS(7):", cnt, "| /7! =", cnt / math.factorial(7),
      "| 7!/168 =", math.factorial(7) // 168)
