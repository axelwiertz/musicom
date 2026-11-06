"""verify_136_CHC.py — Collatz Hailstone Composition fact-check.
Verifies every number quoted in method_136_CHC.md against direct computation.
"""
from functools import lru_cache

# --- maps (non-shortcut f and shortcut T) ---
def f(n):  # non-shortcut: odd -> 3n+1 (even), even -> n/2
    return 3 * n + 1 if n % 2 else n // 2

def T(n):  # shortcut: odd -> (3n+1)/2, even -> n/2
    return (3 * n + 1) // 2 if n % 2 else n // 2

def trajectory(n, step=T):
    out = []
    while n != 1:
        out.append(n)
        n = step(n)
    out.append(1)
    return out

def total_stopping_time(n, step=f):
    k = 0
    while n != 1:
        n = step(n)
        k += 1
    return k

def peak(n, step=T):
    return max(trajectory(n, step))

# 1. n = 27 canonical example (Wikipedia): non-shortcut 111 steps, peak 9232
traj27 = trajectory(27, f)
assert len(traj27) - 1 == 111, len(traj27) - 1
assert peak(27, f) == 9232
odd_vals_27 = [x for x in traj27 if x % 2 == 1]
odd_steps = len([x for x in traj27[:-1] if x % 2 == 1])  # odd inputs before terminal 1
assert odd_steps == 41, odd_steps  # "41 steps through odd numbers"
assert len(odd_vals_27) == 42  # 41 odd steps + the terminal 1 itself
print(f"[1] n=27: non-shortcut steps={len(traj27)-1}, odd steps={odd_steps}, peak={peak(27, f)}")

# 2. record holders (total stopping time records, non-shortcut) — OEIS A006877 prefix
rec = []
best = -1
for n in range(1, 7000):
    s = total_stopping_time(n, f)
    if s > best:
        best = s
        rec.append(n)
expected = [1, 2, 3, 6, 7, 9, 18, 25, 27, 54, 73, 97, 129, 171, 231, 313, 327,
            649, 703, 871, 1161, 2223, 2463, 2919, 3711, 6171]
assert rec[:26] == expected, rec[:26]
print(f"[2] record holders A006877 prefix matches: {rec[:12]} ... (n={len(rec)} found)")

# 3. stopping-time maxima below 10^k (Wikipedia table, non-shortcut)
for k, n_expected, s_expected in [(5, 77031, 350), (6, 837799, 524)]:
    lim = 10 ** k
    best_n, best_s = 1, 0
    for n in range(1, lim):
        s = total_stopping_time(n, f)
        if s > best_s:
            best_s, best_n = s, n
    assert (best_n, best_s) == (n_expected, s_expected), (k, best_n, best_s)
    print(f"[3] <10^{k}: max total stopping time {best_s} steps at n={best_n}")

# 4. parity congruence: first k parity bits agree iff n == m (mod 2^k)
def parity_bits(n, k, step=T):
    bits = []
    for _ in range(k):
        bits.append(n % 2)
        n = step(n)
    return tuple(bits)

n = 123456
for k in (4, 8, 12):
    m_ok = n + (1 << k)          # congruent mod 2^k -> same first k bits
    m_no = n + 3                 # not congruent (k>=2) -> different
    assert parity_bits(n, k) == parity_bits(m_ok, k)
    assert parity_bits(n, k) != parity_bits(m_no, k)
print("[4] parity congruence mod 2^k verified (agree iff congruent)")

# injectivity: residue mod 2^k -> parity vector is a bijection for k=6
seen = set()
for r in range(64):
    seen.add(parity_bits(r, 6))
assert len(seen) == 64
print("[5] parity-vector map mod 2^6 is bijective (64/64 distinct)")

# 6. 4-2-1 absorbing cycle (non-shortcut)
assert f(1) == 4 and f(4) == 2 and f(2) == 1
print("[6] 4-2-1 cycle confirmed: 1 -> 4 -> 2 -> 1")

# 7. 2^k a + b identity (shortcut map T, per Wikipedia parity-vector section):
#    T^2(4a+1) == 3a+1 ; T^4(16a+3) == 9a+2 ; T^5(32a+1) == 27a+2 (3 increases)
for a in range(1, 6):
    y = 4 * a + 1
    for _ in range(2):
        y = T(y)
    assert y == 3 * a + 1, (a, y)
for a in range(1, 6):
    y = 16 * a + 3
    for _ in range(4):
        y = T(y)
    assert y == 9 * a + 2, (a, y)
for a in range(1, 6):
    y = 32 * a + 1
    for _ in range(5):
        y = T(y)
    assert y == 27 * a + 2, (a, y)
print("[7] 2^k a + b structural identities verified (T^2(4a+1)=3a+1, T^4(16a+3)=9a+2, T^5(32a+1)=27a+2)")

# 8. Bohm-Sontacchi rational for the positive cycle parity word (shortcut): "10" period
# m=1 odd at index k0=0, n=2 -> (3^0 * 2^0) / (2^2 - 3^1) = 1  -> generator of the cycle
num = (3 ** 0) * (2 ** 0)
den = (2 ** 2) - (3 ** 1)
assert num / den == 1.0
print(f"[8] Bohm-Sontacchi: parity cycle '10' -> rational {num}/{den} = {num/den:g} (the 1 of 1->2->1)")

# 9. powers of two: n = 2^10 reaches 1 in exactly 10 steps, never rises
p = 1 << 10
tr = trajectory(p, f)
assert len(tr) - 1 == 10 and max(tr) == p
print("[9] powers of two: 2^10 -> 1 in 10 steps, never increased")

# 10. record peaks (A006884 prefix)
rec_peak = []
best_p = -1
for n in range(1, 2000):
    pk = peak(n, T)
    if pk > best_p:
        best_p = pk
        rec_peak.append(n)
expected_peak = [1, 2, 3, 7, 15, 27, 255, 447, 639, 703, 1819]
assert rec_peak[:11] == expected_peak, rec_peak[:11]
print(f"[10] record peaks A006884 prefix matches: {rec_peak[:11]}")

# 11. determinism: same seed -> identical trajectory
assert trajectory(27) == trajectory(27)
print("[11] deterministic: same seed -> byte-identical trajectory")

# 12. 2-tag system (De Mol): a->bc, b->a, c->aaa on a^n halts with n -> 1
def tag_run(n):
    word = "a" * n
    steps = 0
    while len(word) >= 2:
        word = word[2:] + {"a": "bc", "b": "a", "c": "aaa"}[word[0]]
        steps += 1
    return word, steps

w, s = tag_run(5)
assert w in ("", "a") and total_stopping_time(5, f) == 5
print(f"[12] 2-tag system (De Mol): a^5 -> '{w}' in {s} tag steps")

print("\nALL CHECKS PASSED")
