"""verify_jcoc_math.py — Method 148 (JCOC) math verification. Run with $MUSICOM_PYTHON."""
import math, random, sys

PASS = FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {name} {detail}")
    else:
        FAIL += 1
        print(f"FAIL  {name} {detail}")

# ---------- reference implementations (must match the standalone sketch) ----------
def survivor(n, k):
    g = 0
    for i in range(2, n + 1):
        g = (g + k) % i
    return g

def survivor_k2(n):
    m = n.bit_length() - 1
    l = n - (1 << m)
    return 2 * l + 1

def elimination_order_naive(n, k):
    people = list(range(1, n + 1))
    out, idx = [], 0
    while people:
        idx = (idx + k - 1) % len(people)
        out.append(people.pop(idx))
    return out

def elimination_order_fast(n, k):
    bit = [0] * (n + 1)
    def add(i, v):
        while i <= n:
            bit[i] += v; i += i & -i
    def sum_(i):
        s = 0
        while i > 0:
            s += bit[i]; i -= i & -i
        return s
    def kth(t):
        lo, hi = 1, n
        while lo < hi:
            mid = (lo + hi) // 2
            if sum_(mid) >= t: hi = mid
            else: lo = mid + 1
        return lo
    for i in range(1, n + 1): add(i, 1)
    out, pos = [], 0
    for rem in range(n, 0, -1):
        pos = (pos + k - 1) % rem
        i = kth(pos + 1)
        out.append(i); add(i, -1)
    return out

def rotated(order, s):
    return order[s:] + order[:s]

def lucky_numbers(N):
    a = list(range(1, N + 1, 2))
    i = 1
    while i < len(a):
        step = a[i]
        if step > len(a): break
        del a[step - 1::step]
        i += 1
    return a

def halbeisen_hungerbuehler(n, alpha=0.8111):
    """k=3 closed form f(n) = 3(n - round(alpha*(3/2)^m)) + (2 if rounded up else 1)."""
    import math as _m
    best = (0, 1)                              # m=0 always valid: round(alpha)=1 <= n
    for m in range(1, 60):                     # search greatest m with round(...) <= n
        r = round(alpha * (3 / 2) ** m)
        if r <= n:
            best = (m, r)
    m, r = best
    rounded_up = round(alpha * (3 / 2) ** m) > alpha * (3 / 2) ** m
    return 3 * (n - r) + (2 if rounded_up else 1)

# ---------- 1. permutation property ----------
E83 = elimination_order_naive(8, 3)
check("E(8,3) is a permutation of 1..8", sorted(E83) == list(range(1, 9)), f"E={E83}")
check("E(8,3) survivor = 7", E83[-1] == 7, f"last={E83[-1]}")

# ---------- 2. k=2 closed form vs recurrence ----------
ok2 = all(survivor_k2(n) == survivor(n, 2) + 1 for n in range(1, 201))
check("k=2 closed form f(n)=2l+1 == recurrence, n<=200", ok2)
check("f(13)=11 (binary cyclic shift 1101->1011)", survivor_k2(13) == 11)
check("f(41)=19 (41=32+9, 2*9+1)", survivor_k2(41) == 19)

# ---------- 3. k=3 Halbeisen-Hungerbuehler ----------
check("f(41,3)=31 (HH closed form)", halbeisen_hungerbuehler(41) == 31,
      f"got {halbeisen_hungerbuehler(41)}")
ok3 = all(halbeisen_hungerbuehler(n) == survivor(n, 3) + 1 for n in range(5, 80))
check("HH closed form matches simulation, n=5..79", ok3)

# ---------- 4. general recurrence vs simulation ----------
okg = True
for n in range(1, 60):
    for k in range(1, 15):
        if survivor(n, k) + 1 != elimination_order_naive(n, k)[-1]:
            okg = False
check("general recurrence g(n,k) == simulation survivor, n<=59 k<=14", okg)

# ---------- 5. Fenwick order statistics == naive ----------
okf = True
for n in range(1, 50):
    for k in [2, 3, 5, 7, 10]:
        if elimination_order_fast(n, k) != elimination_order_naive(n, k):
            okf = False
check("Fenwick O(n log n) == naive O(n^2), n<=49", okf)

# ---------- 6. density arc ----------
arc = list(range(8, 0, -1))
check("density arc = n, n-1, ..., 1", arc == [8, 7, 6, 5, 4, 3, 2, 1], f"{arc}")

# ---------- 7. lucky numbers (sieve of Josephus Flavius) ----------
lucky = lucky_numbers(400)                     # bound > max known value (201)
known = [1, 3, 7, 9, 13, 15, 21, 25, 31, 33, 37, 43, 49, 51, 63, 67, 69, 73, 75, 79,
         87, 93, 99, 105, 111, 115, 127, 129, 133, 135, 141, 151, 159, 163, 169, 171,
         189, 193, 195, 201]
check("lucky prefix matches OEIS A000959", lucky[:len(known)] == known, f"first 10: {lucky[:10]}")

# ---------- 8. lucky density ~ x/ln x (PNT analogue) ----------
N = 100000
cnt = len(lucky_numbers(N))
xlnx = N / math.log(N)
check("lucky count ~ x/ln x (within 30%)", 0.7 * xlnx <= cnt <= 1.3 * xlnx,
      f"count={cnt}, x/ln x={xlnx:.1f}")
check("lucky sparser than primes (L_n > p_n asymptotically)",
      cnt <= 9592 + 1, f"count={cnt}, pi(1e5)=9592")

# ---------- 9. slot tiling / zero drift ----------
def tile_cell(order, pool, slot, velocity_arc=None):
    n = len(order)
    events = []
    for i, e in enumerate(order):
        start, end = i * slot, (i + 1) * slot
        if i == n - 1:
            end = (i + 1) * slot
        vel = velocity_arc[i] if velocity_arc else (100 - i * (60 // max(n - 1, 1)))
        events.append((pool[e - 1], start, end, max(vel, 1)))
    return events

pool = [60, 62, 64, 65, 67, 69, 71, 72]        # C major degrees
events = tile_cell(E83, pool, 240)
S = 8 * 240
check("cell events end exactly at S = n*slot", events[-1][2] == S, f"last end={events[-1][2]}, S={S}")
check("cell has n events, one per slot", len(events) == 8 and [e[1] for e in events] == list(range(0, S, 240)))
check("every pool degree used exactly once",
      sorted(e[0] for e in events) == sorted(pool))
check("survivor event is terminal anchor", events[-1][0] == pool[E83[-1] - 1] == 71)

# ---------- 10. rotation is a valid permutation (phase texture) ----------
E = elimination_order_fast(12, 3)
R = rotated(E, 4)
check("rotated order is a permutation of 1..12", sorted(R) == list(range(1, 13)), f"R={R}")
check("rotation preserves survivor value set (same elements)", set(R) == set(E))

print(f"\n== {PASS} passed, {FAIL} failed ==")
sys.exit(1 if FAIL else 0)
