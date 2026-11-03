# Method 133 — Z-Relation Network Composition (ZRNC)

- **Paradigm**: Rules-Based
- **Layer**: abstract (designs pc-set sequences, ICV-dissonance tension curves, and the
  z-relation/complement pattern network — no concrete events; feeds
  `rules/subset_network.py`)
- **Module**: `rules/subset_network.py` — classes `ZNetwork`, `ZWalk`, `ICVTension`,
  `HomometryCheck` (concrete feeder later: `generators/zrelation.py`)
- **DB section**: `methods_db.md` → `# Z-Relation Network Composition (ZRNC) (Method 133)`

Composes by walking the z-relation graph of Forte set classes: nodes are set classes,
edges are homometric "twin" pairs — identical interval vector, different harmonic
identity. Twin flips keep ICV-dissonance exactly constant (the *spectrally silent*
transformation), complement pairs give aggregate-completing harmony, and IFUNC-max
transpositions give smooth common-tone seams.

---

## 1. The mathematical object

Let $A \subseteq \mathbb{Z}_{12}$ be a pitch-class set of cardinality $n$. Its
**interval vector** (ICV) counts unordered pairs by interval class:

$$\mathrm{ICV}(A)[d] = \#\{\{i,j\}\subseteq A:\ \min((j-i)\bmod 12,\ (i-j)\bmod 12) = d\},
\qquad d = 1..6 .$$

Two sets $A,B$ are **z-related** when $\mathrm{ICV}(A)=\mathrm{ICV}(B)$ yet $B$ is not
a transposition or inversion of $A$ (different set classes; Forte 1973). The "Z" suffix
in a Forte name (4-Z15, 6-Z44, ...) marks a class that has such a twin. The term
"homometric" comes from X-ray crystallography (Patterson 1939): two structures with the
same autocorrelation (Patterson function) — the ICV is the musical Patterson function.

**Why the twins are "invisible".** The discrete Fourier transform of a pc-set,
$f_A(k)=\sum_{i\in A} e^{2\pi i k i/12}$, satisfies

$$|f_A(k)|^2 = n + 2\sum_{d=1}^{6} \mathrm{ICV}(A)[d]\cos\!\bigl(2\pi k d/12\bigr)
\qquad (k=1..11)$$

(verified numerically, all $k$). The magnitudes are therefore *functions of the ICV
alone*: z-twins have identical $|f_A(k)|$ at every $k$ (Amiot 2016, homometry theorem)
and differ only in phase. Compositionally: switching twins is a change that Fourier-
magnitude methods (registered 113 PCFSC) provably cannot see. (Verified for
4-Z15/4-Z29: magnitudes equal at all $k=1..11$; phases differ at most $k$.)

**Verified census (2026-11-03, `verify_133_ZRNC.py`, exhaustive over all 4096
subsets of $\mathbb{Z}_{12}$, deduplicated by Tn/TnI set-class equivalence):**

| cardinality | # z-pairs | pairs (named via the Wikipedia Forte table) |
|---|---|---|
| 4 | 1 | 4-Z15 {0,1,4,6} ↔ 4-Z29 {0,1,3,7} (both ICV ⟨1,1,1,1,1,1⟩ — Babbitt's all-interval tetrachords) |
| 5 | 3 | 5-Z12 ↔ 5-Z36 · 5-Z17 ↔ 5-Z37 · 5-Z18 ↔ 5-Z38 |
| 6 | 15 | every pair is a complement pair: 6-Z3↔6-Z36, 6-Z4↔6-Z37, 6-Z6↔6-Z38, 6-Z10↔6-Z39, 6-Z11↔6-Z40, 6-Z12↔6-Z41, 6-Z13↔6-Z42, 6-Z17↔6-Z43, 6-Z19↔6-Z44, 6-Z23↔6-Z45, 6-Z24↔6-Z46, 6-Z25↔6-Z47, 6-Z26↔6-Z48, 6-Z28↔6-Z49, 6-Z29↔6-Z50 |
| 7 | 3 | complements of the 5-pc pairs (7-Z12↔7-Z36, 7-Z17↔7-Z37, 7-Z18↔7-Z38) |
| 8 | 1 | complement of the 4-pc pair |
| **total** | **23** | max ICV-group size = 2 ⇒ the z-graph is a perfect matching |

**The hexachord miracles.** For $n=6$ the complement obeys
$f_{C(H)}(k) = f_{\mathbb{Z}_{12}}(k) - f_H(k) = -f_H(k)$ for $k\ne0$ (the 12th roots
sum to zero), so magnitudes — hence ICVs — agree: $\mathrm{ICV}(H)=\mathrm{ICV}(C(H))$
for **all 50** hexachord classes (verified 50/50). Consequently every hexachord is
z-related to its complement: 20 classes are self-complementary (complement is Tn/In-
equivalent), the remaining 30 form the 15 z-pairs, and **every 6-pc z-pair is a
complement pair** (verified 15/15). Hexachord twins therefore sum to the full
12-tone aggregate — the twin flip is an aggregate-completing move.

**Tension-flat identity flips.** Any ICV-weighted dissonance
$T(A) = \sum_d w_d\,\mathrm{ICV}(A)[d]$ is equal on twins for *any* weight vector $w$
(identical ICV). With the canonical weights $w=(6,5,4,3,2,1)$:
$T(4\text{-}Z15) = T(4\text{-}Z29) = 21$ (verified). A z-walk is therefore a tension-
flat harmonic arc: tension changes only when the walk changes cardinality or leaves the
twin, never at a twin flip.

**Common-tone seams.** For transposition $t$, the common-tone count is the Lewin
interval function: $|A \cap (B+t)| = \mathrm{IFUNC}(B,A)(t)$ where
$\mathrm{IFUNC}(X,Y)(t) = \#\{(i,j)\in X\times Y : j-i \equiv t \pmod{12}\}$
(Lewin 2001; verified). For the tetrachord pair the common-tone vector
$\mathrm{IFUNC}(B,A)$ is $(2,2,0,2,1,2,2,0,0,2,1,2)$: **2 common tones at 7 of 12
transpositions** ($t\in\{0,1,3,5,6,9,11\}$) — smooth seams are abundant.

**Minimal voice leading between twins.** Circular Wasserstein-1 (min over cyclic
matchings) between 4-Z15 and 4-Z29 is **2 semitones** (verified: match 0→0, 1→1,
4→3, 6→7). Small — but the matching is *crossing* (4,6 pass 3,7 in opposite
directions), which is why parsimonious voice-leading solvers (050 OTVL) do not
register it as smooth unless crossings are permitted.

## 2. Musical mapping

- **PITCH** = per-section set class: the section's pc-material up to transposition/
  inversion; cardinality is a dial (4-/5-/6-pc sections); a twin flip changes the
  pitch-class identity while preserving the interval vocabulary exactly. Melodic
  contour is concrete-layer business (rank → scale degree, cf. 095 CTC); the abstract
  plan fixes *which pcs exist* per section.
- **RHYTHM** (abstract constraint) = walk cadence: one plan tuple per section; onset
  density, durations, and groove are concrete-layer. The ICV bounds voicing density
  ($\binom{n}{2}$ intervals per class); hexachord pairs suggest 6-note strata or
  aggregate-completing hockets.
- **HARMONY** = set class = chord quality; z-twin = *silent quality flip* (tension
  constant, identity changed); complement pairs = aggregate completion (twin +
  complement = 12-tone aggregate for all 15 hexachord pairs); progression smoothness =
  IFUNC-max common-tone transposition (2 common tones at 7 transpositions for the
  tetrachord pair); tension arc = ICV-dissonance trajectory with a fixed weight vector.
- **STRUCTURE** = macro-form is the walk schedule: per-section
  $(S_j, t_j, n_j, \mathrm{twin}_j)$ — set class, transposition, cardinality, twin
  flag. Reprise = return to the home class (twin chains closing on HOME = "theme that
  was never the same chord twice"); through-composed = long twin chains; the 23 edges
  are the *entire finite* universe of identity-flips; self-complementary hexachords are
  structural pivots (their own twin — the walk can turn in place).
- **TEXTURE** = cardinality = density; complement pairs = shadow-ensemble (the
  unplayed complement is the piece's negative); hexachord twin pairs = two 6-note
  choirs whose union is the aggregate; the matching structure = a finite, closed,
  exhaustive relational universe — ideal for rotation/hocket schemes.

## 3. Python implementation sketch

```python
# ---- abstract layer: rules/subset_network.py -------------------------------
from itertools import combinations
from collections import defaultdict
import cmath, math

def icv(pcs):
    v = [0] * 6
    for i in range(len(pcs)):
        for j in range(i + 1, len(pcs)):
            d = (pcs[j] - pcs[i]) % 12
            v[min(d, 12 - d) - 1] += 1
    return tuple(v)

def set_class_key(pcs):
    """Canonical class representative: lex-min sorted tuple over all Tn/TnI."""
    best = None
    for t in range(12):
        for r in (tuple(sorted((x + t) % 12 for x in pcs)),
                  tuple(sorted((-x + t) % 12 for x in pcs))):
            if best is None or r < best:
                best = r
    return best

def ifunc(x, y):
    f = [0] * 12
    for i in x:
        for j in y:
            f[(j - i) % 12] += 1
    return tuple(f)          # IFUNC(x,y)[t] = |x ∩ (y+t)|

def tds(pcs, w=(6, 5, 4, 3, 2, 1)):
    return sum(c * wi for c, wi in zip(icv(pcs), w))

def fmag(pcs, k):
    return abs(sum(cmath.exp(2j * cmath.pi * k * x / 12) for x in pcs))

class ZNetwork:
    """The 23-edge z-relation matching over Forte set classes (12-TET)."""
    def __init__(self):
        self.pairs = []                 # [(classA, classB), ...] per cardinality
        self.by_icv = defaultdict(list)
        for n in range(1, 12):
            seen = set()
            for comb in combinations(range(12), n):
                k = set_class_key(comb)
                if k in seen:
                    continue
                seen.add(k)
                self.by_icv[icv(k)].append(k)
        for ic, keys in self.by_icv.items():
            if len(keys) == 2:
                self.pairs.append(tuple(sorted(keys)))

class ZWalk:
    """Macro-form = a schedule of plan tuples over the z-graph."""
    def __init__(self, home, weights=(6, 5, 4, 3, 2, 1)):
        self.home = home
        self.w = weights
        self.sections = []              # [(class, transposition, cardinality, twin)]
    def append(self, cls, t, twin=False):
        n = len(cls)
        self.sections.append((cls, t % 12, n, twin))
    def seam_common_tones(self, j):
        (a, ta, _, _), (b, tb, _, _) = self.sections[j], self.sections[j + 1]
        A = tuple((x + ta) % 12 for x in a)
        B = tuple((x + tb) % 12 for x in b)
        return max(ifunc(A, B))         # best-case shared pcs at the seam
    def tension(self):
        return [tds(tuple((x + t) % 12 for x in cls), self.w)
                for cls, t, _, _ in self.sections]

class HomometryCheck:
    """Assert twin invisibility: |f_A(k)| == |f_B(k)| for all k."""
    @staticmethod
    def verify(a, b, tol=1e-9):
        return all(abs(fmag(a, k) - fmag(b, k)) < tol for k in range(1, 12))

# ---- usage: the verified 6-section tension-flat walk -------------------------
A, B = (0, 1, 4, 6), (0, 1, 3, 7)        # 4-Z15, 4-Z29
assert icv(A) == icv(B) == (1, 1, 1, 1, 1, 1)
assert HomometryCheck.verify(A, B)       # magnitudes equal at every k
walk = ZWalk(home=A)
for j in range(6):                       # A -> B -> A -> B -> A -> B, t=0
    walk.append(A if j % 2 == 0 else B, 0)
print(walk.tension())                    # [21, 21, 21, 21, 21, 21]  (tension-flat)
print([walk.seam_common_tones(j) for j in range(5)])  # [2, 2, 2, 2, 2]
```

Concrete realization (future `generators/zrelation.py`, not part of this abstract
registration): section class $(S_j + t_j)$ → scale-degree subset (map pcs onto the
current scale's degrees, cf. 095 CTC rank→degree), voice $v$ takes pc
$(S_j+t_j)[v \bmod n_j]$ in its register, onset/duration from the concrete rhythm
plan; then standard `UnitMatrixComposer` fill → `validate()` (zero-drift gate) →
`to_midi()` per AGENTS.md. The seam common-tone audit is exported as metadata
(per-section plan + IFUNC seam vector), like 132 BIBDC's pair-coverage export.

## 4. Verified numeric core

`verify_133_ZRNC.py` (2026-11-03, `$MUSICOM_PYTHON`) — all checks pass:

```
[1] set-class counts 1..11 = 1,6,12,29,38,50,38,29,12,6,1  (Forte's 208 = 3..9 pc)
[2] z-pairs: 4pc 1, 5pc 3, 6pc 15, 7pc 3, 8pc 1  ->  TOTAL 23
[3] max ICV-group size = 2  (z-graph is a perfect matching)
[4] 4-Z15 {0,1,4,6} vs 4-Z29 {0,1,3,7}: distinct classes, ICV <111111> equal,
    min circular voice leading = 2 st, TDS = 21 = 21 (weight-independent)
[5] Fourier: |fA(k)| == |fB(k)| for ALL k=1..11; phases differ at some k;
    |fA(k)|^2 == n + 2*sum ICV[d]*cos(2pi k d/12) for all k: True
[6] hexachords: icv(H) == icv(C(H)) for all 50; 20 self-complementary;
    30 z-related to complement = 15 complement pairs
[7] 7-pc pairs = complements of 5-pc pairs: True; 8-pc pair = complement of 4-pc
[8] common-tone vector (4-Z15 vs 4-Z29): [2,2,0,2,1,2,2,0,0,2,1,2] -> max 2 at
    t = {0,1,3,5,6,9,11}
[11] Forte-name mapping (Wikipedia table): hexachord pairs 15/15 matched;
     every 6-pc z-pair is a complement pair: True;
     pentachord pairs 3/3 matched (5-Z12/5-Z36, 5-Z17/5-Z37, 5-Z18/5-Z38)
[9] demo 6-section z-walk: TDS = 21 constant, 2 common tones per seam
```

## 5. Selection heuristics

| want | do |
|---|---|
| signature "same chord, different chord" moment | flip 4-Z15 ↔ 4-Z29 (T constant, identity changes) |
| tension-flat development | chain twins (any pair) — tension changes only at cardinality changes |
| tension rise / TENSE | move to a higher-ICV-dissonance class or increase cardinality |
| cadence / HOME | close the walk on the home class (twin chain returning to HOME) |
| aggregate-completing harmony | hexachord twin pairs (twin + complement = 12-tone aggregate, verified 15/15) |
| smooth seams | IFUNC-max transposition (4-Z15/4-Z29: 2 common tones at 7 transpositions) |
| structural pivot | self-complementary hexachords (20 of 50) — the walk turns in place |
| through-composed form | long twin chains with changing transpositions |
| shadow texture | play the complement pair as antiphonal choirs (the negative ensemble) |
| atonal/serial contexts | 065 TTSMC rows as home aggregate; z-walk between row segments |

## 6. References

- Forte, A. (1973). *The Structure of Atonal Music*. Yale University Press — the z-relation, set-class table, interval vectors.
- Lewin, D. (1976). "On the Interval Content of Invertible Hexachords." *Journal of Music Theory* 20(2), 185–216.
- Lewin, D. (2001). "Special Cases of the Interval Function between Pitch-Class Sets X and Y." *Journal of Music Theory* 45(1), 1–29 — IFUNC, the common-tone function (verified here).
- Rahn, J. (1980). *Basic Atonal Theory*. Longman.
- Amiot, E. (2016). *Music through Fourier Space*. Springer — homometry theorem: same ICV ⇔ same Fourier magnitudes; the DFT identity used here.
- Patterson, A. L. (1939). "Homometric structures." *Nature* 143, 939 — the crystallographic origin of "homometric".
- Babbitt, M. (1960). "Twelve-tone invariants as compositional determinants." *The Musical Quarterly* 46(2) — the all-interval tetrachords = 4-Z15/4-Z29.
- Wikipedia: "Interval vector" and "List of set classes" (fetched 2026-11-03, cache `_web133/`) — ICV definition and the Forte table used to name all 23 pairs.
- Novelty check (2026-11-03): no z-relation/homometric method in `methods_db.md` before entry (only incidental prose in 104/112/113); 113 PCFSC is provably blind to z-twins (identical magnitudes).

## 7. Pitfalls (short form)

1. Z-relation ≠ parsimonious voice-leading (104 PSSC): twin flips change every pc of the identity; the minimal matching (2 st) is crossing — 050 OTVL rejects it unless crossings are allowed.
2. The universe is tiny: exactly 23 z-edges in 12-TET (verified). It is an identity-flip vocabulary, not a melodic generator.
3. Twins always share cardinality ($\sum \mathrm{ICV} = \binom{n}{2}$); cardinality changes are separate moves (subset/complement), not z-moves.
4. Forte vs Rahn prime forms differ on 8 classes — match by Tn/TnI equivalence, name via the Wikipedia/Forte table (first draft here wrongly assumed 5-Z18 = 01458; the table says 01457).
5. Homometry is magnitude-only: phases differ — 113 PCFSC cannot distinguish twins; use ZRNC *with* PCFSC (magnitudes = quality, z-edges = identity).
6. Hexachord complement invariance is a 6-pc-only miracle ($f_{C(H)}(k) = -f_H(k)$); other cardinalities do not preserve ICV under complementation.
7. For hexachords the z-graph and the complement graph coincide (verified 15/15) — one edge, not two.
8. The z-graph is a matching (max group size 2): no neighborhoods beyond the single edge — the walk (order, transpositions, twin flags) is the composition.
9. TDS equality is twin-only; across cardinalities pick one weight vector and document it.
10. Abstract: no events until the concrete feeder; realize via scale-degree subset map, then `validate()`-gated UnitMatrix fill.
