"""Verification prototype #2 for Method 144 — LSPC.

Adds: Skolem solution counts (vs OEIS A004075), plain-vs-hooked comparison,
the totality audit (every n covered by Langford | Skolem | hooked Skolem),
and constructive scaling.
"""
import time

def langford_all(n):
    slots = [-1] * (2 * n); out = []
    def rec(k):
        if k == 0:
            out.append(tuple(slots)); return
        d = k + 1
        for i in range(0, 2 * n - d):
            if slots[i] == -1 and slots[i + d] == -1:
                slots[i] = slots[i + d] = k; rec(k - 1); slots[i] = slots[i + d] = -1
    rec(n)
    return out

def langford_first(n, budget=5_000_000):
    slots = [-1] * (2 * n); found = []; nodes = [0]
    def rec(k):
        nodes[0] += 1
        if nodes[0] > budget: return True
        if k == 0:
            found.append(tuple(slots)); return True
        d = k + 1
        for i in range(0, 2 * n - d):
            if slots[i] == -1 and slots[i + d] == -1:
                slots[i] = slots[i + d] = k
                if rec(k - 1): return True
                slots[i] = slots[i + d] = -1
        return False
    rec(n)
    return (found[0] if found else None), nodes[0]

def skolem_all(n, hook=False):
    L = 2 * n + (1 if hook else 0)
    slots = [-1] * L; out = []
    def rec(k):
        if k == 0:
            out.append(tuple(slots)); return
        d = k
        for i in range(0, L - d):
            if slots[i] == -1 and slots[i + d] == -1:
                slots[i] = slots[i + d] = k; rec(k - 1); slots[i] = slots[i + d] = -1
    rec(n)
    return out

def skolem_first(n, hook=False):
    L = 2 * n + (1 if hook else 0)
    slots = [-1] * L; found = []
    def rec(k):
        if k == 0:
            found.append(tuple(slots)); return True
        for i in range(0, L - k):
            if slots[i] == -1 and slots[i + k] == -1:
                slots[i] = slots[i + k] = k
                if rec(k - 1): return True
                slots[i] = slots[i + k] = -1
        return False
    rec(n)
    return found[0] if found else None

def audit(seq, n, fam):
    L = len(seq); pos = {}
    for i, s in enumerate(seq):
        if s: pos.setdefault(s, []).append(i)
    d = (lambda k: k + 1) if fam == "langford" else (lambda k: k)
    law = all(len(pos[k]) == 2 and pos[k][1] - pos[k][0] == d(k) for k in range(1, n + 1))
    filled = sum(1 for s in seq if s)
    return dict(law=law, slots=L, filled=filled, empty=L - filled,
                density=round(filled / L, 4),
                lags=[pos[k][1] - pos[k][0] for k in range(1, n + 1)])

print("== A. Skolem solution counts (exhaustive) vs OEIS A004075 ==")
oeis = {0: 1, 1: 1, 2: 0, 3: 0, 4: 6, 5: 10, 6: 0, 7: 0, 8: 504, 9: 2656}
for n in range(1, 10):
    t = time.time()
    c = len(skolem_all(n))
    print(f"  n={n}: measured={c:5d}  OEIS a({n})={oeis[n]:5d}  match={c == oeis[n]}  ({time.time()-t:.2f}s)")

print("\n== B. Langford counts summary (measured) ==")
for n in (3, 4, 7, 8, 11):
    c = len(langford_all(n))
    print(f"  n={n:2d}: {c:6d} oriented solutions = 2 x A014552({n}) "
          f"= {2 * {3: 1, 4: 1, 7: 26, 8: 150, 11: 17792}[n]}")

print("\n== C. Hooked Skolem: does the hook genuinely repair n=2,3 mod 4? ==")
for n in range(1, 11):
    plain = skolem_first(n)
    hooked = skolem_first(n, hook=True)
    need = (n % 4) in (2, 3)
    extra = "" if plain is None else f" (plain already exists: {plain})"
    print(f"  n={n:2d} n%4={n%4}  plain={'YES' if plain else 'no ':3s} "
          f"hooked={'YES' if hooked else 'no ':3s}  hook_required={need}  "
          f"repair_worked={(hooked is not None) if need else True}{extra}")

print("\n== D. Totality audit: every n >= 1 realizable in SOME family ==")
worst = []
for n in range(1, 41):
    fam = None
    if n % 4 in (0, 3):
        s = langford_first(n)[0]
        if s: fam = "Langford"
    if fam is None:
        s = skolem_first(n)
        if s: fam = "Skolem"
    if fam is None:
        s = skolem_first(n, hook=True)
        if s: fam = "hooked Skolem"
    worst.append((n, fam))
bad = [x for x in worst if x[1] is None]
print(f"  n=1..40 covered: {len(worst)-len(bad)}/40   uncovered={bad}")
print("  sample:", worst[:14])

print("\n== E. Worked pieces (musical payload) ==")
for n in (6, 7, 8):
    fam = "langford" if n % 4 in (0, 3) else "skolem"
    seq = langford_first(n)[0] if fam == "langford" else skolem_first(n)
    r = audit(seq, n, fam)
    tag = "".join(str(s) if s else "." for s in seq)
    print(f"  n={n} {fam:8s} {tag}   {r}")

print("\n== F. Scaling: bitset-backed search cost ==")
for n in (15, 16, 19, 20, 23, 24, 31, 32, 39, 40, 47, 48):
    if n % 4 not in (0, 3):
        continue
    t = time.time()
    s, nodes = langford_first(n)
    print(f"  n={n:2d}  solved={s is not None}  nodes={nodes:8d}  {time.time()-t:6.3f}s")

print("\n== G. Density / span laws ==")
for n in (3, 4, 7, 8, 11, 12):
    seq = langford_first(n)[0]
    r = audit(seq, n, "langford")
    print(f"  n={n:2d}: span={r['slots']-1} slots, events={r['filled']}, empty={r['empty']}, "
          f"density={r['density']}, sum_lags={sum(r['lags'])}, n(n+3)/2={n*(n+3)//2}")
