# Method 131 — Tonality Diamond Ratio-Pool Composition (TDRPC)

- **Paradigm**: Rules-Based
- **Layer**: abstract (designs ratio pitch pools, hexad chord vocabularies, identity
  progression networks, and Tenney-height tension curves — no concrete events; feeds
  `rules/subset_network.py`)
- **Module**: `rules/subset_network.py` — classes `TonalityDiamond`, `Hexad`,
  `IdentityLattice`, `HeightCurve` (concrete feeder later: `generators/tonality_diamond.py`)
- **DB section**: `methods_db.md` → `# Tonality Diamond Ratio-Pool Composition (TDRPC) (Method 131)`

Composes from Harry Partch's tonality diamond: the pitch pool is the set of octave-reduced
just ratios whose lowest-terms odd parts are bounded by an odd limit $n$, the chords are its
Otonality/Utonality hexads (shared numerary nexus), progression is an identity walk with
common-tone retention, and tension/gravity is ratio complexity (Tenney height).

---

## 1. The mathematical object

Let $n$ be an odd limit. The **$n$-limit odd tonality diamond** is

$$D(n)=\bigl\{\mathrm{oct}_2(a/b):\ \mathrm{oddpart}(a')\le n,\ \mathrm{oddpart}(b')\le n,\ a'/b'=a/b\ \text{in lowest terms}\bigr\}$$

where $\mathrm{oct}_2$ multiplies/divides by $2$ to land in $[1,2)$, and $\mathrm{oddpart}(x)$
removes powers of 2. Verified sizes (2026-11-01, `verify_131_TDRPC.py`):

| $n$ (odd limit) | $|D(n)|$ computed | cited | closed form $\sum_{m\le n,\ m\ \mathrm{odd}}\varphi(m)$ |
|---|---|---|---|
| 1 | 1 | 1 | 1 |
| 3 | 3 | 3 | 3 |
| 5 | 7 | 7 | 7 |
| 7 | 13 | 13 | 13 |
| 9 | 19 | 19 | 19 |
| 11 | 29 | 29 | 29 |
| 13 | 41 | 41 | 41 |
| 15 | 49 | 49 | 49 |

Asymptotic growth $\sim (2/\pi^2)\,n^2$. (Source-display trap: some texts print the totient
sum bound as $m<n$, which gives 19 for $n=11$ instead of 29 — the correct bound is $m\le n$;
verified against enumeration for all $n\le15$.)

**Otonality / Utonality hexads.** For each odd identity $m\le n$:

$$\mathrm{Uto}(m)=\{\mathrm{oct}_2(k/m): k\ \mathrm{odd},\ k\le n\},
\qquad \mathrm{Oto}(m)=\{\mathrm{oct}_2(m/k): k\ \mathrm{odd},\ k\le n\}.$$

Verified: six distinct tones each for $n=11$, all $m\in\{1,3,5,7,9,11\}$; the union of all 12
hexads equals $D(11)$. Examples (verified): $\mathrm{Uto}(3)=\{1/1, 7/6, 4/3, 3/2, 5/3, 11/6\}$,
$\mathrm{Oto}(3)=\{1/1, 12/11, 6/5, 4/3, 3/2, 12/7\}$ — intersection $\{1/1, 4/3, 3/2\}$ (3
common tones: smooth polarity flip).

**Structural facts (all verified 2026-11-01):**

| fact | value | check |
|---|---|---|
| famous gap, low ratios | cents(3/2) − cents(4/3) = 203.91 c | matches |
| famous gap, high ratios | cents(5/4) − cents(6/5) = 70.67 c | matches |
| neighbor steps | all adjacent pool gaps are superparticular $(k{+}1)/k$ (n=5: 6/5, 25/24, 16/15, 9/8, 16/15, 25/24; n=7: 12/12 gaps; n=11: all 28) | all superparticular |
| inversion symmetry | $D(n)$ closed under $r\mapsto\mathrm{oct}_2(1/r)$, n=5/7/11 | closed |
| hexad count | 6 tones per identity, n=11 | 6 distinct |
| height gradation | H(1/1)=0, H(3/2)=2.585, H(5/4)=4.322, H(9/8)=6.170, H(11/9)=6.629, H(16/9)=7.170, H(20/11)=7.781 | monotone |

**Tension meter.** Tenney height $H(a/b)=\log_2(ab)$ (lowest terms): lower = simpler = more
consonant. Tonal gravity: HOME = the $1/1$ nexus (H=0); LIFT = move to lower $H$; TENSE =
move to higher $H$ or high-$H$ identity; TURN = high-$H$ detour returning via a common tone.
Complementary meter: the diamond's spacing property — low-number ratios sit far apart
(203.91 c between 4/3 and 3/2), high-number ratios crowd (70.67 c between 6/5 and 5/4).

## 2. Musical mapping

- **Pitch** = the ratio pool: $|D(n)|$ exact just intervals per octave; pitch identity is a
  ratio, not a semitone. Melodic motion: superparticular comma steps (adjacent pool entries)
  vs ratio leaps; contour follows the height ordering. Realization must preserve ratios
  (pitch-bend / just renderer) — nearest-12-TET destroys the tuning.
- **Harmony** = otonality/utonality hexads replace triads; polarity (oto/uto) = quality knob;
  progression = identity walk with common-tone retention (≥1 shared ratio per seam, measured
  3 common tones between Uto(3)/Oto(3)); inversion symmetry = mirror harmony; numerary nexus
  = harmonic center.
- **Rhythm** (abstract constraint, not events) = hexad cycle length, identity-change rate,
  and height-slope map to onset-density arcs; the height curve $\{H_j\}$ is the energy
  envelope.
- **Structure** = section sequence $[(m_1,p_1,H_1),\dots,(m_S,p_S,H_S)]$; tension arc =
  height trajectory; reprise = return to opening identity+polarity; modulation = identity
  change; cadence = return to the $1/1$ nexus.
- **Texture** = voices are ratio roles inside shared hexads (≤6 per identity at n=11);
  multi-identity sections = polytonal stratification; $1/1$ nexus = tutti anchor; inversion
  = mirrored voice pairs.

## 3. Python implementation sketch

```python
from fractions import Fraction
from math import log2, gcd

# --- abstract layer: rules/subset_network.py ---------------------------------
def oddpart(x):
    while x % 2 == 0:
        x //= 2
    return x

def oct2(f):
    while f < 1: f *= 2
    while f >= 2: f /= 2
    return f

def cents(r):
    return 1200.0 * log2(float(r))

def tenney_height(r):
    return log2(r.numerator * r.denominator)   # lowest terms

class TonalityDiamond:
    """n-limit odd tonality diamond: the just-intonation pitch pool."""
    def __init__(self, limit):                 # limit = odd number (5, 7, 9, 11, ...)
        self.limit = limit
        self.ratios = self._build()
    def _build(self):
        out = set()
        n = self.limit
        for oa in range(1, n + 1, 2):
            for ob in range(1, n + 1, 2):
                base = Fraction(oa, ob)
                for i in range(-4, 5):
                    r = oct2(base * Fraction(2) ** i)
                    if oddpart(r.numerator) <= n and oddpart(r.denominator) <= n:
                        out.add(r)
        return sorted(out)
    def size_formula(self):                     # verified closed form
        return sum(phi(m) for m in range(1, self.limit + 1, 2))

def phi(x):
    r, k = x, 2
    while k * k <= x:
        if x % k == 0:
            while x % k == 0: x //= k
            r -= r // k
        k += 1
    if x > 1: r -= r // x
    return r

class Hexad:
    """Otonality (shared numerator) or Utonality (shared denominator) chord."""
    def __init__(self, identity, polarity, limit):   # polarity in {'oto','uto'}
        self.identity, self.polarity = identity, polarity
        tones = set()
        for k in range(1, limit + 1, 2):
            f = Fraction(k, identity) if polarity == 'uto' else Fraction(identity, k)
            tones.add(oct2(f))
        self.tones = sorted(tones)
    def common_with(self, other):
        return set(self.tones) & set(other.tones)

class IdentityLattice:
    """Adjacency of hexads over identities 1..limit; common-tone matrix."""
    def __init__(self, diamond):
        self.diamond = diamond
        self.ids = list(range(1, diamond.limit + 1, 2))
        self.hexads = {m: {p: Hexad(m, p, diamond.limit) for p in ('oto', 'uto')}
                       for m in self.ids}
    def common(self, m1, p1, m2, p2):
        return self.hexads[m1][p1].common_with(self.hexads[m2][p2])

class HeightCurve:
    """Tenney-height trajectory over sections = the tension curve."""
    def __init__(self, targets):
        self.targets = targets                    # list of (identity, polarity, H)
    def arc(self):
        return [tenney_height(Fraction(1, 1))] + \
               [t[2] for t in self.targets]       # HOME=0 baseline then per-section H
```

Concrete realization (future `generators/tonality_diamond.py`, not part of this abstract
registration): ratio → frequency $f = f_0 \cdot r$; MIDI + pitch-bend:
`midi = round(69 + 12*log2(r)); bend = round(8192 * 12*log2(r) % 1)` (or nearest-TET sketch
with cents recorded in provenance); then standard `UnitMatrixComposer` fill +
`validate()` + `to_midi()` (zero-drift gate per AGENTS.md).

## 4. Verified numeric core

`verify_131_TDRPC.py` (2026-11-01, python3) — all checks pass:

```
[1] diamond sizes n=1..15 == cited 1,3,7,13,19,29,41,49: ALL MATCH
[2] 11-limit diamond: 29 ratios (full list with cents and H printed)
[3] cents(3/2)-cents(4/3) = 203.91 ; cents(5/4)-cents(6/5) = 70.67
[4] all adjacent gaps superparticular: n=5 True, n=7 True, n=11 True
[5] inversion closure r -> oct2(1/r): n=5/7/11 True
[6] 12 hexads (6 tones each, n=11); union == D(11): True
[7] Tenney height monotone gradation: True
[8] closed form d(n)=sum_{m<=n odd} phi(m) == enumeration: ALL MATCH
```

## 5. Selection heuristics

| want | do |
|---|---|
| familiar-density pool | n=5 (7 tones) or n=7 (13 tones) |
| Partch's own palette | n=11 (29 tones) |
| extreme microtonal shimmer | n=13 (41) / n=15 (49), sparse textures only |
| bright open harmony | otonality polarities, low-H identities (3, 5) |
| dark undertone colour | utonality polarities (subharmonic rows) |
| smooth modulation | adjacent identities with max common tones (Uto(3)/Oto(3): 3 tones) |
| tension rise | per-section height targets climbing (TENSE), e.g. 3/2 → 9/8 → 11/9 → 20/11 |
| cadence / HOME | return to the 1/1 nexus (H=0) with common-tone seam |
| voice exchange | apply inversion symmetry r → oct2(1/r) to a voice's ratio stream |
| through-composed form | long identity walks (high-n lattices: 5/7-limit all tones one step from unison) |

## 6. References

- Partch, H. (1949; 2nd ed. 1974). *Genesis of a Music*. University of Wisconsin Press; Da Capo Press. — diamond, 43-tone scale, otonality/utonality, corporeal music.
- Meyer, M. F. (1901). *Contributions to a Psychological Theory of Music*. University of Missouri. — origin of the tonality-diamond idea.
- Helmholtz, H. von (1863). *On the Sensations of Tone*. — just-intonation consonance basis (Partch's 1923 conversion).
- Chalmers, J. H. (1993). *Divisions of the Tetrachord*. Frog Peak Music. — just-intonation scale theory incl. Partch's scale.
- Tenney, J. (1988). *A History of "Consonance" and "Dissonance"*. Excelsior. — Tenney height H = log2(ab).
- Wilson, E. (1970s, partly unpublished). Generalized diamonds (triadic → ogdoadic), unique interval directions.
- Wikipedia: "Tonality diamond" and "Harry Partch" (fetched 2026-11-01) — construction rules, size sequence, geometry, 43-tone facts.

## 7. Pitfalls (short form)

1. Diamond (29 ratios @ n=11) ≠ Partch's 43-tone instrument scale (+14 secondary tones). Register the pool, not the tuning trivia.
2. 12-TET projection destroys ratios, common tones, superparticular steps — keep ratios at the abstract layer; realize via pitch-bend/just renderer with cents in provenance.
3. Not 114 FSBC: FSBC = unbounded Farey/Stern–Brocot rationals for rhythm subdivision; TDRPC = bounded odd-limit pitch-pool/chord designer.
4. Totient bound trap: correct closed form is $\sum_{m\le n,\ m\ \mathrm{odd}}\varphi(m)$ ($m\le n$, not $m<n$); enumerate when in doubt.
5. gcd-reduce before octave-reduce, then dedupe (3/1, 9/3, 12/4 → 3/2).
6. Seam checks in ratio space — semitone projection makes common-tone seams illusory.
7. Register (octave multiplier) is a separate concrete-layer plan; the diamond is a pitch-class pool.
8. Hexads cap single-identity voicing at 6 (n=11); more voices need multi-identity (polytonal) sections.
9. Don't inflate the limit: 41/49-tone pools thin the common-tone structure; start at n=7 or n=11.
10. Oto ≠ major, Uto ≠ minor — polarity is a colour knob, not a mode.
