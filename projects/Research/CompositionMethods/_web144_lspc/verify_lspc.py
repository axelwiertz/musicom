"""Verification prototype for Method 144 — Langford–Skolem Distance-Pairing Composition (LSPC).

Pure Python, no external deps.  Every number printed here is measured.
"""
import sys, time
from functools import lru_cache

# ---------------------------------------------------------------- Langford ---
# slot model: 2n slots (0-based).  Symbol k (1..n) occupies two slots at
# distance k+1  ->  positions i, i+k+1  ->  exactly k slots *between* them.
def langford_all(n, limit=None):
    """Enumerate all Langford pairings of order n (undirected, first-half canon)."""
    out = []
    slots = [-1] * (2 * n)
    def rec(k):
        if limit is not None and len(out) >= limit:
            return
        if k == 0:
            out.append(tuple(slots)); return
        d = k + 1
        for i in range(0, 2 * n - d):
            if slots[i] == -1 and slots[i + d] == -1:
                slots[i] = slots[i + d] = k
                rec(k - 1)
                slots[i] = slots[i + d] = -1
    rec(n)
    return out

def langford_first(n, budget=None):
    """First solution found by largest-symbol-first backtracking; counts nodes."""
    counter = [0, 0]  # nodes, solutions
    slots = [-1] * (2 * n)
    found = []
    def rec(k):
        counter[0] += 1
        if budget and counter[0] > budget:
            return True
        if k == 0:
            found.append(tuple(slots)); counter[1] += 1
            return True
        d = k + 1
        for i in range(0, 2 * n - d):
            if slots[i] == -1 and slots[i + d] == -1:
                slots[i] = slots[i + d] = k
                if rec(k - 1):
                    return True
                slots[i] = slots[i + d] = -1
        return False
    rec(n)
    return (found[0] if found else None), counter[0]

# ---------------------------------------------------------------- Skolem -----
# Symbol k at positions i, i+k  ->  exactly k-1 slots between; distance k.
def skolem_all(n, hook=False):
    """hook=True adds one extra slot (hooked Skolem), total 2n+1 slots."""
    slots = [-1] * (2 * n + (1 if hook else 0))
    L = len(slots)
    out = []
    def rec(k):
        if k == 0:
            out.append(tuple(slots)); return
        d = k
        for i in range(0, L - d):
            if slots[i] == -1 and slots[i + d] == -1:
                slots[i] = slots[i + d] = k
                rec(k - 1)
                slots[i] = slots[i + d] = -1
    rec(n)
    return out

def skolem_first(n, hook=False):
    slots = [-1] * (2 * n + (1 if hook else 0))
    L = len(slots); found = []
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

# ------------------------------------------------------------- invariants ----
def check(seq, n, family):
    """Verify the defining law + perfect-cover invariant. Returns dict."""
    L = len(seq)
    pos = {}
    for i, s in enumerate(seq):
        if s > 0: pos.setdefault(s, []).append(i)
    ok_pairs = all(len(v) == 2 for v in pos.values()) and len(pos) == n
    if family == "langford":   d = lambda k: k + 1
    else:                      d = lambda k: k
    ok_dist = all((pos[k][1] - pos[k][0]) == d(k) for k in range(1, n + 1))
    filled = sum(1 for s in seq if s > 0)
    gaps = L - filled
    return dict(complete=ok_pairs, law=ok_dist, slots=L, events=filled,
                empty=gaps, density=filled / L,
                lag_spectrum=sorted(pos[k][1] - pos[k][0] for k in pos))

# ------------------------------------------------------------------- main ----
def main():
    print("== 1. Langford existence, n = 1..14 (first-solution search) ==")
    t0 = time.time()
    for n in range(1, 15):
        sol, nodes = langford_first(n, budget=3_000_000)
        pred = (n % 4) in (0, 3)
        print(f"  n={n:2d}   exists={sol is not None!s:5s}   predicted(n%4 in {{0,3}})={pred!s:5s}"
              f"   nodes={nodes:9d}   match={ (sol is not None)==pred }")
    print(f"  elapsed {time.time()-t0:.2f}s")

    print("\n== 2. Langford solution counts (exhaustive, n<=11) ==")
    counts = {}
    for n in range(1, 12):
        t = time.time()
        sols = langford_all(n)
        counts[n] = len(sols)
        print(f"  L({n}) = {len(sols):8d}   ({time.time()-t:.2f}s)")

    print("\n== 3. Skolem existence, n = 1..12 (plain) ==")
    for n in range(1, 13):
        s = skolem_first(n)
        pred = (n % 4) in (0, 1)
        print(f"  n={n:2d}   plain Skolem exists={s is not None!s:5s}  predicted={pred!s:5s}"
              f"  match={(s is not None)==pred}")

    print("\n== 4. Hooked Skolem existence, n = 1..12 (totality repair) ==")
    for n in range(1, 13):
        s = skolem_first(n, hook=True)
        pred = (n % 4) in (2, 3)
        print(f"  n={n:2d}   hooked exists={s is not None!s:5s}  predicted(n%4 in {{2,3}})={pred!s:5s}"
              f"  match={(s is not None)==pred}")

    print("\n== 5. Perfect-cover / law audit on concrete pieces ==")
    for n, fam in [(3, "langford"), (4, "langford"), (7, "langford"), (8, "langford"),
                   (4, "skolem"), (5, "skolem")]:
        if fam == "langford":
            seq, _ = langford_first(n)
        else:
            seq = skolem_first(n)
        r = check(seq, n, fam)
        print(f"  n={n} {fam:8s} seq={'-'.join(map(str, seq))}")
        print(f"     {r}")

    print("\n== 6. Lag-spectrum completeness (the musical invariant) ==")
    for n in (7, 8, 11):
        seq, _ = langford_first(n)
        r = check(seq, n, "langford")
        print(f"  n={n:2d} lag spectrum = {r['lag_spectrum']}  "
              f"complete(1..n once each) = {r['lag_spectrum'] == list(range(2, n + 2))}"
              f"  density={r['density']:.3f}  empty={r['empty']}")

    print("\n== 7. Scale: first-solution search cost for larger n ==")
    for n in (15, 16, 19, 20, 23, 24, 27, 28, 31, 32):
        t = time.time()
        seq, nodes = langford_first(n, budget=5_000_000)
        print(f"  n={n:2d}  solved={seq is not None!s:5s}  nodes={nodes:8d}  "
              f"{time.time()-t:6.2f}s")

    print("\n== 8. Reverse/complement symmetries ==")
    seq, _ = langford_first(7)
    n = 7
    rev = tuple(reversed(seq))
    r1 = check(rev, n, "langford")
    # interval-complement: map slot i -> 2n-1-i is the same as reverse; check
    # "pitch complement" k -> n+1-k is NOT a Langford (different distances):
    comp = tuple((n + 1 - s) if s > 0 else 0 for s in seq)
    r2 = check(comp, n, "langford")
    print(f"  original  {seq}")
    print(f"  reversed  {rev}  valid={r1['law']}")
    print(f"  relabelled k->n+1-k  {comp}  still-Langford={r2['law']}")

    print("\n== 9. Sum invariants ==")
    for n in (7, 8, 12):
        seq, _ = langford_first(n)
        pos = {}
        for i, s in enumerate(seq):
            if s: pos.setdefault(s, []).append(i)
        lags = [pos[k][1] - pos[k][0] for k in sorted(pos)]
        print(f"  n={n:2d}  sum(lags)={sum(lags)}  n(n+3)/2={n*(n+3)//2}"
              f"  mean lag={sum(lags)/n:.2f}  span={2*n-1}")

if __name__ == "__main__":
    main()
