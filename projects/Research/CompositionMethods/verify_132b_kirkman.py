"""Find a RESOLVABLE STS(15) (Kirkman triple system) by randomized backtracking.

Not every STS(15) is resolvable (v = 3 mod 6 is necessary but not sufficient for a
*given* design); this script searches random STS(15)s until one admits 7 parallel
classes of 5 disjoint triples, then prints it and verifies all invariants.
"""
import itertools, random
from collections import Counter


def build_sts_random(v, rng, limit=200_000):
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
        best, best_c = None, 10 ** 9
        pairs = list(uncovered)
        rng.shuffle(pairs)
        for p in pairs:
            a, b = tuple(p)
            c = sum(1 for x in range(v) if x not in p
                    and frozenset((a, x)) in uncovered and frozenset((b, x)) in uncovered)
            if c < best_c:
                best_c, best = c, p
        if best_c == 0:
            return False
        a, b = tuple(best)
        xs = [x for x in range(v) if x not in best]
        rng.shuffle(xs)
        for x in xs:
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

    try:
        if not rec():
            return None
    except RuntimeError:
        return None
    return sorted(blocks)


def resolve_exact(v, blocks, limit=200_000):
    bs = [frozenset(b) for b in blocks]
    used = [False] * len(bs)
    classes = []
    nodes = [0]

    def first_unused():
        for i in range(len(bs)):
            if not used[i]:
                return i
        return None

    def rec():
        nodes[0] += 1
        if nodes[0] > limit:
            raise RuntimeError
        i = first_unused()
        if i is None:
            return True
        used[i] = True
        cls, cover = [i], set(bs[i])

        def extend():
            if len(cover) == v:
                classes.append(list(cls))
                if rec():
                    return True
                classes.pop()
                return False
            for k in range(len(bs)):
                if used[k] or (cover & bs[k]):
                    continue
                used[k] = True
                cls.append(k)
                cover.update(bs[k])
                if extend():
                    return True
                cover.difference_update(bs[k])
                cls.pop()
                used[k] = False
            return False

        if extend():
            return True
        used[i] = False
        return False

    try:
        ok = rec()
    except RuntimeError:
        return None
    return classes if ok else None


if __name__ == "__main__":
    rng = random.Random(20261102)
    for attempt in range(400):
        bl = build_sts_random(15, rng)
        if bl is None:
            continue
        classes = resolve_exact(15, bl)
        if classes:
            print("found resolvable STS(15) on attempt", attempt, "| blocks", len(bl),
                  "| classes", len(classes))
            print("DESIGN =", bl)
            cov = Counter()
            for b in bl:
                for p in itertools.combinations(b, 2):
                    cov[p] += 1
            print("pairs covered:", len(cov), "| all exactly once:",
                  all(x == 1 for x in cov.values()) and len(cov) == 105)
            for ci, c in enumerate(classes):
                pts = sorted(set().union(*[set(bl[i]) for i in c]))
                print(f"  class {ci}: {[bl[i] for i in c]} covers {len(pts)} points")
            print("block sizes in classes:", sorted({len(c) for c in classes}))
            break
    else:
        print("no resolvable STS(15) found in 400 random designs")
