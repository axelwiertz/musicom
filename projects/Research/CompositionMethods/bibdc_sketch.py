"""BIBDC sketch — balanced incomplete block design -> UnitMatrix cell plan.

Runs standalone (design algebra only). The musicom fill is shown but imported lazily.
"""
import itertools
from collections import Counter


# ---------------------------------------------------------------- design layer
class BIBD:
    """2-(v, k, lambda) design: v points, b blocks of size k, every pair in lambda blocks."""

    def __init__(self, v, k, lam, blocks):
        self.v, self.k, self.lam = v, k, lam
        self.blocks = [tuple(sorted(b)) for b in blocks]
        self.b = len(self.blocks)
        self.r = lam * (v - 1) // (k - 1)

    def audit(self):
        pairs, deg = Counter(), Counter()
        for B in self.blocks:
            assert len(B) == self.k and len(set(B)) == self.k, B
            for x in B:
                deg[x] += 1
            for p in itertools.combinations(B, 2):
                pairs[p] += 1
        ok = (all(pairs[p] == self.lam for p in itertools.combinations(range(self.v), 2))
              and all(deg[x] == self.r for x in range(self.v))
              and self.v * self.r == self.b * self.k)
        return ok, dict(b=self.b, r=self.r, n_pairs=len(pairs))

    def se(self, i, j):
        """Seam common tones between consecutive blocks i, j."""
        return sorted(set(self.blocks[i]) & set(self.blocks[j]))

    def novelty_curve(self, order=None):
        """Remaining unmet voice pairs after each section (lambda=1 designs)."""
        order = order if order is not None else range(self.b)
        seen, curve = set(), []
        for m in order:
            for p in itertools.combinations(self.blocks[m], 2):
                seen.add(p)
            curve.append(self.v * (self.v - 1) // 2 - len(seen))
        return curve

    def dual(self):
        inc = [[1 if i in self.blocks[j] else 0 for j in range(self.b)] for i in range(self.v)]
        blocks = [tuple(i for i in range(self.v) if inc[i][j]) for j in range(self.b)]
        return BIBD(self.b, self.r, self.lam, blocks)

    def resolve(self):
        """Partition blocks into parallel classes, or None (most designs are not resolvable)."""
        used = [False] * self.b
        classes = []

        def rec():
            free = [i for i in range(self.b) if not used[i]]
            if not free:
                return True
            i = free[0]
            used[i] = True
            cls, cover = [i], set(self.blocks[i])

            def extend():
                if len(cover) == self.v:
                    classes.append(list(cls))
                    if rec():
                        return True
                    classes.pop()
                    return False
                for j in range(self.b):
                    if used[j] or (cover & set(self.blocks[j])):
                        continue
                    used[j] = True
                    cls.append(j)
                    cover.update(self.blocks[j])
                    if extend():
                        return True
                    cover.difference_update(self.blocks[j])
                    cls.pop()
                    used[j] = False
                return False

            if extend():
                return True
            used[i] = False
            return False

        return classes if rec() else None


def fano():
    """The unique STS(7) (Fano plane); points 0..6."""
    return BIBD(7, 3, 1, [(0, 1, 2), (0, 3, 4), (0, 5, 6),
                          (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)])


def sts_by_search(v, seed=0):
    """Backtracking STS(v); pair-cover driven. v must be 1 or 3 mod 6."""
    import random
    rng = random.Random(seed)
    uncovered = set(itertools.combinations(range(v), 2))
    blocks = []

    def rec():
        if not uncovered:
            return True
        best, bc = None, 10 ** 9
        for p in uncovered:
            a, b = p
            c = sum(1 for x in range(v) if x not in p
                    and (min(a, x), max(a, x)) in uncovered
                    and (min(b, x), max(b, x)) in uncovered)
            if c < bc:
                bc, best = c, p
        if bc == 0:
            return False
        a, b = best
        xs = [x for x in range(v) if x not in best]
        rng.shuffle(xs)
        for x in xs:
            t = tuple(sorted((a, b, x)))
            pr = list(itertools.combinations(t, 2))
            if all(p in uncovered for p in pr):
                uncovered.difference_update(pr)
                blocks.append(t)
                if rec():
                    return True
                blocks.pop()
                uncovered.update(pr)
        return False

    return BIBD(v, 3, 1, blocks) if rec() else None


# --------------------------------------------------------------- musical layer
SEATS = [0, 2, 4, 5, 7, 9, 11]          # voice i -> pc seat (Fano consort, 7 voices)
OCTAVE_LADDER = [0, 12, 7, 19, 14, 5, 24]  # optional per-section octave offset by block id


def cell_plan(design, section_ticks=1920, subdiv=4):
    """Return {(voice, section): [(pitch, start, dur), ...]} — empty list = rest cell."""
    step = section_ticks // subdiv
    plan = {}
    for m, B in enumerate(design.blocks):
        for i in range(design.v):
            plan[(i, m)] = []
        for j, i in enumerate(B):
            pitch = 60 + SEATS[i % len(SEATS)] + OCTAVE_LADDER[m % len(OCTAVE_LADDER)]
            plan[(i, m)] = [(pitch, j * step, step * (subdiv - j))]
    return plan


if __name__ == "__main__":
    D = fano()
    print("Fano audit:", D.audit())
    print("seams (common tones):", [D.se(i, i + 1) for i in range(6)])
    print("novelty:", D.novelty_curve(), "| reversed:",
          D.novelty_curve(list(reversed(range(7)))))
    print("self-dual:", D.dual().blocks == D.blocks, "| resolve:", D.resolve())
    for v in (9, 13):
        E = sts_by_search(v)
        print(f"STS({v}):", E.audit(), "| b =", E.b, "| resolvable:", E.resolve() is not None)
    plan = cell_plan(D)
    sounding = sum(1 for k, evs in plan.items() if evs)
    print("cells:", len(plan), "sounding:", sounding, "| per-voice:",
          [sum(1 for (i, m), e in plan.items() if i == v_ and e) for v_ in range(7)])
