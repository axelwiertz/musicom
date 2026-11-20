"""Verification of the MMTC (Metric Modulation Tempo-Network Composition) mathematics.

Every claim quoted in methods_db.md Method 147 is computed here.
Run:  $MUSICOM_PYTHON projects/Research/CompositionMethods/_web147_mmc/verify_mmc_math.py
"""
from fractions import Fraction
from math import gcd, lcm
from itertools import product

ok = 0
fail = 0


def check(name, cond, detail=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"PASS  {name} {detail}")
    else:
        fail += 1
        print(f"FAIL  {name} {detail}")


def qlcm(frs):
    """Least common multiple of rationals a_i/b_i (lowest terms) = lcm(a_i)/gcd(b_i)."""
    nums = [f.numerator for f in frs]
    dens = [f.denominator for f in frs]
    return Fraction(lcm(*nums), gcd(*dens))


# ---------------------------------------------------------------- 1. pivot law
def pivot_tempo(t_old, n_old, n_new):
    """new/old = (#pivot values in new unit) / (#pivot values in old unit)."""
    return Fraction(t_old) * Fraction(n_new, n_old)


# Wikipedia's Carter example (Eight Etudes and a Fantasy, Fantasy mm.16-17):
# 2 half notes at quarter = 84 ~ 3 half notes at the new tempo.
t2 = pivot_tempo(84, 2, 3)
check("pivot law 84 * 3/2", t2 == 126, f"-> {t2}")
# duration equality 2 halves@84  ==  3 halves@126
d_old = 2 * (Fraction(60, 84) * 2)   # 2 half notes, a half = 2 beats
d_new = 3 * (Fraction(60, 126) * 2)
check("pivot duration equality", d_old == d_new, f"{float(d_old):.4f}s == {float(d_new):.4f}s")
# the wiki's remark: quarter = 126 is dotted-quarter = 84
check("dotted-quarter identity", Fraction(126) * 2 == Fraction(84) * 3,
      "126 * 2/3 = 84 dotted-quarter")

# ------------------------------------------------- 2. tempo chain closure (cycle)
chain = [Fraction(3, 2), Fraction(4, 3), Fraction(1, 2)]
t = Fraction(84)
path = [t]
for r in chain:
    t *= r
    path.append(t)
check("tempo chain 84->126->168->84", path == [84, 126, 168, 84], f"{[int(x) for x in path]}")
check("chain product == 1 (tempo cycle)", chain[0] * chain[1] * chain[2] == 1)
check("168 = 2 x 84 (tempo octave)", path[2] == 2 * path[0])

# ------------------------------------------- 3. rational pulse lcm / coincidence
check("qlcm(3/2,4/3)=12", qlcm([Fraction(3, 2), Fraction(4, 3)]) == 12)
check("qlcm(2/3,4/5)=4", qlcm([Fraction(2, 3), Fraction(4, 5)]) == 4)
check("qlcm(1/2,1/3)=1", qlcm([Fraction(1, 2), Fraction(1, 3)]) == 1)
# both voices really hit an integer number of pulses inside that span
span = qlcm([Fraction(3, 2), Fraction(4, 3)])
check("coincidence divisibility", (span / Fraction(3, 2)).denominator == 1
      and (span / Fraction(4, 3)).denominator == 1, f"8 and 9 pulses in {int(span)}")

# Carter, Night Fantasies: 216:175 tempo relation
check("gcd(216,175)=1", gcd(216, 175) == 1)
check("216*175 = 37800", 216 * 175 == 37800)
coinc_s = 37800 * 0.032            # unit pulse ~32 ms
check("37800 unit pulses at 32 ms ~ 20.2 min", 20.0 < coinc_s / 60 < 21.0,
      f"{coinc_s / 60:.2f} min -> 'two points over 20+ minutes'")

# --------------------------------------- 4. zero-drift: section length must be a
# common multiple of every voice's pulse length in ticks
pulses = [Fraction(480), Fraction(320), Fraction(360)]   # 480*(1, 3/2, 4/3)
section = qlcm(pulses)
check("section lcm(480,320,360)=2880", section == 2880, f"-> {int(section)} ticks")
check("pulse counts 6/9/8", [int(section / p) for p in pulses] == [6, 9, 8],
      f"{[int(section / p) for p in pulses]}")
check("2880 = 1.5 bars of 4/4", Fraction(2880, 1920) == Fraction(3, 2))
# 6 beats per section: bar = 6 beats with beats_per_bar=6
check("6-beat bar exact", section == 6 * 480)

# ---------------------------------------------- 5. ratio alphabet size, n,m <= K
def alphabet(K):
    out = set()
    for n in range(1, K + 1):
        for m in range(1, K + 1):
            out.add(Fraction(n, m))
    return out


A7 = alphabet(7)
check("|alphabet(n,m<=7)| = 35", len(A7) == 35, f"-> {len(A7)}")
phi = {2: 1, 3: 2, 4: 2, 5: 4, 6: 2, 7: 6}
check("35 = 1 + 2*sum(phi(q))", 1 + 2 * sum(phi.values()) == 35,
      f"1+2*{sum(phi.values())}")

# closed chains (tempo cycles) of length 3 and 4 over the alphabet
cycles = {3: 0, 4: 0}
for d in (3, 4):
    for combo in product(A7, repeat=d):
        p = Fraction(1)
        for r in combo:
            p *= r
        if p == 1:
            cycles[d] += 1
check("tempo cycles length 3", cycles[3] > 0, f"{cycles[3]} of {len(A7)**3}")
check("tempo cycles length 4", cycles[4] > 0, f"{cycles[4]} of {len(A7)**4}")
# independent count: products r*s whose inverse is also in the alphabet
inv_pairs = sum(1 for r in A7 for s in A7 if (r * s) != 0 and (1 / (r * s)) in A7)
check("length-3 cycles counted independently", inv_pairs == cycles[3],
      f"{inv_pairs} == {cycles[3]}")
check("cycle count is not a multiple of |A7| (rotation is not free)",
      cycles[3] % len(A7) != 0, f"{cycles[3]} mod 35 = {cycles[3] % len(A7)}")

# ------------------------------------- 6. tempo classes modulo the octave (x2)
classes = set()
for r in A7:
    # reduce r to odd-part normal form: r = 2^k * odd/odd
    n, m = r.numerator, r.denominator
    while n % 2 == 0:
        n //= 2
    while m % 2 == 0:
        m //= 2
    classes.add(Fraction(n, m))
check("tempo classes mod doubling", len(classes) < len(A7), f"{len(classes)} classes for {len(A7)} ratios")
odd_only = {Fraction(n, m) for n in (1, 3, 5, 7) for m in (1, 3, 5, 7)}
check("13 classes = odd/odd ratios of 1,3,5,7", classes == odd_only and len(classes) == 13,
      f"{len(classes)} classes")
def octave_normal_form(r):
    n, m = r.numerator, r.denominator
    while n % 2 == 0:
        n //= 2
    while m % 2 == 0:
        m //= 2
    return Fraction(n, m)


check("3/2 and 3/1 collapse to one tempo class",
      octave_normal_form(Fraction(3, 2)) == octave_normal_form(Fraction(3, 1))
      and octave_normal_form(Fraction(3, 2)) == 3,
      "both -> 3/1")

# ------------------------------- 7. tick invariance under a tempo map (mode A)
# The same absolute ticks mean different seconds under a different tempo:
def seconds(ticks, tpb, bpm):
    return ticks / tpb * (60.0 / bpm)


check("ticks are tempo-map invariant, seconds are not",
      seconds(480, 480, 120) == 0.5 and seconds(480, 480, 180) == 1.0 / 3.0,
      f"480 ticks @120={seconds(480, 480, 120)}s @180={seconds(480, 480, 180):.4f}s")

# ------------------------------------- 8. TPB divisibility for tuplet notation
tpb = 480
div = [n for n in range(2, 13) if tpb % n == 0]
nondiv = [n for n in range(2, 13) if tpb % n != 0]
check("480 supports tuplets", div == [2, 3, 4, 5, 6, 8, 10, 12], f"{div}")
check("480 cannot express 7 and 9-tuplets", nondiv == [7, 9, 11], f"{nondiv}")
check("480*7=3360 covers 7", 3360 % 7 == 0, "3360 = 2^5*3*5*7")
check("480*21=10080 covers 7 and 9", 10080 % 7 == 0 and 10080 % 9 == 0, "10080 = 2^5*3^2*5*7")

print(f"\n{ok} passed, {fail} failed")
raise SystemExit(0 if fail == 0 else 1)
