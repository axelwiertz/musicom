"""Verify Artin braid group facts claimed by method 129 (ABGC)."""
from itertools import permutations

def apply_word(word, n):
    """word: list of (i, e) with i in 1..n-1, e in {+1,-1}. perm[k] = strand at position k."""
    perm = list(range(n))
    for i, e in word:
        assert 1 <= i <= n - 1
        perm[i - 1], perm[i] = perm[i], perm[i - 1]
    return perm

def writhe(word):
    return sum(e for _, e in word)

def components(perm):
    """number of cycles (orbits) of the permutation = link components of the closure"""
    n = len(perm)
    seen = [False] * n
    c = 0
    for s in range(n):
        if not seen[s]:
            c += 1
            x = s
            while not seen[x]:
                seen[x] = True
                x = perm[x]
    return c

def delta_word(n):
    """Half-twist Delta_n: (s1 s2 ... s_{n-1})(s1 ... s_{n-2}) ... (s1)."""
    w = []
    for k in range(n - 1, 0, -1):
        for i in range(1, k + 1):
            w.append((i, +1))
    return w

print("== braid relation s1 s2 s1 == s2 s1 s2 (n=3)")
a = [(1, 1), (2, 1), (1, 1)]
b = [(2, 1), (1, 1), (2, 1)]
print("perm A", apply_word(a, 3), "perm B", apply_word(b, 3), "same:", apply_word(a, 3) == apply_word(b, 3))
print("writhe A", writhe(a), "writhe B", writhe(b))

print("\n== far commutativity s1 s3 == s3 s1 (n=4)")
c = [(1, 1), (3, 1)]
d = [(3, 1), (1, 1)]
print(apply_word(c, 4), apply_word(d, 4))

print("\n== Delta_n: length, permutation, closure components")
for n in range(2, 8):
    w = delta_word(n)
    perm = apply_word(w, n)
    assert len(w) == n * (n - 1) // 2, (n, len(w))
    assert perm == list(range(n - 1, -1, -1)), (n, perm)
    print(f"n={n}: |Delta|={len(w)} (=n(n-1)/2) perm={perm} components={components(perm)}")

print("\n== identity braid closure == n components; full twist Delta^2 closure components")
for n in [3, 4, 5]:
    print(f"n={n}: identity comps={components(list(range(n)))}, Delta comps={components(apply_word(delta_word(n), n))},"
          f" Delta^2 comps={components(apply_word(delta_word(n) * 2, n))}")

print("\n== random walk on permutohedron: distinct permutations reachable, repetition bound n!")
import random
random.seed(7)
for n in [3, 4, 5]:
    cnt = {}
    perm = list(range(n))
    for t in range(20000):
        i = random.choice(range(1, n))
        perm[i - 1], perm[i] = perm[i], perm[i - 1]
        cnt[tuple(perm)] = cnt.get(tuple(perm), 0) + 1
    print(f"n={n}: visited {len(cnt)} of {len(list(permutations(range(n))))} perms (={__import__('math').factorial(n)})")

print("\n== writhe of a sign-balanced vs all-positive word (tension proxy)")
w1 = [(1, 1), (2, -1), (1, 1), (2, -1)]
print("balanced writhe", writhe(w1), "perm", apply_word(w1, 3))
