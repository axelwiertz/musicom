"""Verify_131_TDRPC.py — ground-truth checks for Tonality Diamond Ratio-Pool Composition.

Checks (2026-11-01):
[1] Diamond size d(n) for odd limits 1,3,5,7,9,11,13,15 == cited sequence 1,3,7,13,19,29,41,49
[2] 11-limit diamond = 29 distinct octave-reduced ratios; sorted list + cents printed
[3] Famous gap checks: cents(3/2)-cents(4/3) = 203.91; cents(5/4)-cents(6/5) = 70.67
[4] Adjacent diamond ratios differ by superparticular ratios (n+1)/n  (5-, 7-, 11-limit)
[5] Octave symmetry in cents: D(n) closed under inversion r -> octave_reduce(1/r)
[6] Otonality/Utonality hexads: for identity m in {1,3,5,7,9,11}, build 6-tone chord
    {octave_reduce(k/m): k odd <= 11} (utonality, shared denominator m) and
    {octave_reduce(m/k): k odd <= 11} (otonality, shared numerator m); verify 6 distinct
    tones each and that D(11) == union of all 12 hexads
[7] Tenney height H = log2(a*b) of lowest-terms ratio: consonant anchor 1/1 -> H=0;
    verify H ordering 3/2 < 5/4 < 9/8 < 11/9 (simplicity gradation used for tension)
"""
from fractions import Fraction
from math import log2, gcd

CENTS = 1200.0 / log2(2)  # 1200 cents per octave
ODDS = [1, 3, 5, 7, 9, 11]


def oddpart(x):
    while x % 2 == 0:
        x //= 2
    return x


def oct_reduce(f):
    """Bring Fraction f into [1,2) by multiplying/dividing by 2."""
    while f < 1:
        f *= 2
    while f >= 2:
        f /= 2
    return f


def diamond(n):
    """n-limit odd tonality diamond: distinct octave-reduced ratios a/b whose
    lowest-terms odd parts are both <= n."""
    out = set()
    for oa in range(1, n + 1, 2):
        for ob in range(1, n + 1, 2):
            for i in range(-4, 5):
                for j in range(-4, 5):
                    f = Fraction(oa, ob) * (Fraction(2) ** i) * (Fraction(2) ** -j)
                    r = oct_reduce(f)
                    if r.denominator != 1 or r.numerator != 1:  # keep 1/1 anyway below
                        pass
                    # require lowest-terms odd parts <= n
                    num, den = r.numerator, r.denominator
                    if oddpart(num) <= n and oddpart(den) <= n:
                        out.add(r)
    return sorted(out)


def cents(f):
    return 1200.0 * log2(float(f))


def hexad(m, n, mode):
    """Utonality (mode='uto'): shared denominator m; Otonality (mode='oto'): shared numerator m."""
    tones = set()
    for k in range(1, n + 1, 2):
        f = Fraction(k, m) if mode == 'uto' else Fraction(m, k)
        tones.add(oct_reduce(f))
    return sorted(tones)


# [1] sizes
cited = {1: 1, 3: 3, 5: 7, 7: 13, 9: 19, 11: 29, 13: 41, 15: 49}
print('[1] diamond sizes vs cited sequence')
ok = True
for n in sorted(cited):
    d = diamond(n)
    match = len(d) == cited[n]
    ok &= match
    print(f'    n={n:2d}: computed {len(d):2d}  cited {cited[n]:2d}  match={match}')
print('    ALL MATCH:', ok)

# [2] 11-limit list
D11 = diamond(11)
print(f'[2] 11-limit diamond: {len(D11)} ratios (cents)')
for r in D11:
    print(f'    {str(r):>6}  {cents(r):8.2f} c  H={log2(r.numerator*r.denominator):.3f}')

# [3] famous gaps
g1 = cents(Fraction(3, 2)) - cents(Fraction(4, 3))
g2 = cents(Fraction(5, 4)) - cents(Fraction(6, 5))
print(f'[3] cents(3/2)-cents(4/3) = {g1:.2f} (expect 203.91); '
      f'cents(5/4)-cents(6/5) = {g2:.2f} (expect 70.67)')

# [4] superparticular neighbours
for n in (5, 7, 11):
    D = diamond(n)
    good = True
    pairs = []
    for a, b in zip(D, D[1:]):
        q = b / a
        p = q.numerator - q.denominator
        sp = p == 1
        good &= sp
        pairs.append(f'{str(a)}->{str(b)}: {q} superparticular={sp}')
    print(f'[4] n={n}: all {len(D)-1} adjacent gaps superparticular: {good}')
    if n == 5:
        for p in pairs:
            print('    ', p)

# [5] octave symmetry (inversion closure)
for n in (5, 7, 11):
    D = diamond(n)
    inv = {oct_reduce(Fraction(1, r)) for r in D}
    print(f'[5] n={n}: inversion-closed in cents-symmetric octave: {inv == set(D)}')

# [6] hexads
print('[6] otonality/utonality hexads (n=11), identity m in {1,3,5,7,9,11}')
union = set()
for m in ODDS:
    u = hexad(m, 11, 'uto')
    o = hexad(m, 11, 'oto')
    union |= set(u) | set(o)
    print(f'    m={m:2d} uto({len(u)})={[str(x) for x in u]}')
    print(f'           oto({len(o)})={[str(x) for x in o]}')
print(f'    union of 12 hexads has {len(union)} distinct tones == D(11)? {union == set(D11)}')

# [7] Tenney height ordering
Hs = [(r, log2(r.numerator * r.denominator)) for r in (Fraction(1, 1), Fraction(3, 2),
       Fraction(5, 4), Fraction(9, 8), Fraction(11, 9), Fraction(16, 9), Fraction(20, 11))]
print('[7] Tenney height H=log2(a*b), lowest terms')
for r, h in Hs:
    print(f'    {str(r):>6}  H={h:.3f}')
print('    monotone increasing (simplicity gradation):',
      all(Hs[i][1] <= Hs[i + 1][1] for i in range(len(Hs) - 1)))

# [8] closed-form size formula: d(n) == sum(phi(m) for odd m <= n)
def phi(x):
    r, k = x, 2
    while k * k <= x:
        if x % k == 0:
            while x % k == 0:
                x //= k
            r -= r // k
        k += 1
    if x > 1:
        r -= r // x
    return r

print('[8] closed form d(n) = sum_{m<=n, m odd} phi(m)  vs enumeration')
ok8 = True
for n in (1, 3, 5, 7, 9, 11, 13, 15):
    s = sum(phi(m) for m in range(1, n + 1, 2))
    match = s == len(diamond(n))
    ok8 &= match
    print(f'    n={n:2d}: formula {s:2d}  enumerated {len(diamond(n)):2d}  match={match}')
print('    ALL MATCH:', ok8)

print()
print('ALL CHECKS DONE')
