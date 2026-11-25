from itertools import combinations

class Matroid:
    """Independence oracle. Partition or graphic in practice."""
    def __init__(self, E, indep): self.E, self.indep = frozenset(E), indep
    def is_indep(self, S):  return self.indep(frozenset(S))
    def rank(self, S):
        for r in range(len(S), -1, -1):
            if any(self.is_indep(c) for c in combinations(tuple(S), r)): return r
        return 0
    def bases(self):
        out = {S for r in range(len(self.E) + 1)
                 for S in map(frozenset, combinations(self.E, r)) if self.is_indep(S)}
        return {S for S in out if all(not self.is_indep(S | {x}) for x in self.E - S)}
    def circuits(self):
        return {S for S in self._dep() if all(self.is_indep(S - {x}) for x in S)}
    def _dep(self):
        return {frozenset(c) for r in range(1, len(self.E) + 1)
                for c in combinations(self.E, r) if not self.is_indep(c)}

def partition_matroid(blocks, caps):
    def indep(S): return all(sum(x in b for x in S) <= k for b, k in zip(blocks, caps))
    return Matroid(range(12), indep)

def greedy_basis(M, w):
    B, acc = frozenset(), set()
    for x in sorted(M.E, key=lambda p: (-w[p], p)):     # deterministic ties
        if M.is_indep(B | {x}): B |= {x}
    B = frozenset(B)
    assert all(not M.is_indep(B | {x}) for x in M.E - B)   # is a basis
    return B

def exchange_path(M, A, B):
    """d(A,B) single-element basis exchanges."""
    path, cur = [A], A
    while cur != B:
        for x in cur - B:
            for y in B - cur:
                nxt = frozenset(cur - {x} | {y})
                if M.is_indep(nxt) and len(nxt & B) > len(cur & B):
                    path.append(nxt); cur = nxt; break
            else: continue
            break
    return path

def dual(M):
    """S is independent in M* iff E\\S SPANS M (r(E\\S) = r(E)) — not "complement is independent"."""
    return Matroid(M.E, lambda S: M.rank(M.E - frozenset(S)) == M.rank(M.E))
