"""Verification prototype #3 for Method 144 — LSPC (totality, worked pieces, scaling)."""
import time

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
    law = all(len(pos.get(k, [])) == 2 and pos[k][1] - pos[k][0] == d(k) for k in range(1, n + 1))
    filled = sum(1 for s in seq if s)
    return dict(law=law, slots=L, filled=filled, empty=L - filled,
                density=round(filled / L, 4),
                lags=[pos[k][1] - pos[k][0] for k in range(1, n + 1)])

print("== D. Totality: one piece per n in the family the theorem allows ==")
rows = []
for n in range(1, 49):
    r = n % 4
    if r in (0, 3):
        seq, _ = langford_first(n); fam = "Langford"
    elif r == 1:
        seq = skolem_first(n); fam = "Skolem"
    else:
        seq = skolem_first(n, hook=True); fam = "hooked Skolem"
    ok = seq is not None
    if ok:
        ok = audit(seq, n, "langford" if fam == "Langford" else "skolem")["law"]
    rows.append((n, fam, ok))
    print(f"  n={n:2d}  n%4={r}  family={fam:13s} valid={ok}")
print(f"  TOTAL n=1..48 valid: {sum(1 for x in rows if x[2])}/48")

print("\n== E. Worked pieces ==")
for n in (6, 7, 8, 12):
    fam = "langford" if n % 4 in (0, 3) else "skolem"
    seq = langford_first(n)[0] if fam == "langford" else skolem_first(n)
    a = audit(seq, n, fam)
    print(f"  n={n:2d} {fam:8s} {'-'.join(map(str, seq))}")
    print(f"        {a}")

print("\n== G. Density / span laws (Langford) ==")
for n in (3, 4, 7, 8, 11, 12, 15, 16):
    seq, nodes = langford_first(n)
    a = audit(seq, n, "langford")
    print(f"  n={n:2d}: span={a['slots']-1:3d} slots  events={a['filled']:3d}  empty={a['empty']}  "
          f"density={a['density']}  sum_lags={sum(a['lags']):4d}  n(n+3)/2={n*(n+3)//2:4d}  "
          f"nodes={nodes}")

print("\n== F. Scaling ==")
for n in (19, 20, 23, 24, 27, 28, 31, 32):
    t = time.time()
    seq, nodes = langford_first(n)
    print(f"  n={n:2d}  solved={seq is not None}  nodes={nodes:7d}  {time.time()-t:6.3f}s")
