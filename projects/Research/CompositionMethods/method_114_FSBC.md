# Method 114 — Farey–Stern–Brocot Composition (FSBC)

**ID:** 114 · **Paradigm:** Rules-Based · **Layer:** concrete · **Registered:** 2026-10-13

**One-line:** Composes from the rational-number hierarchy of Farey sequences (all reduced fractions a/b with b ≤ N, sorted → maximal rational subdivision of the bar) and the Stern–Brocot tree (every positive rational exactly once; depth = Tenney-height consonance gradation) — polyrhythmic density via denominator budget, pitch via ratio→MIDI/cents mapping, form via tree walks or the Calkin–Wilf enumeration.

---

## 1. The mathematics: Farey sequences, Stern–Brocot tree, Stern diatomic series

### 1.1 Farey sequences

The **Farey sequence of order N**, written $F_N$, is the ascending list of all reduced fractions $a/b \in [0,1]$ with denominator $b \le N$ (Farey 1816; Hardy & Wright §3.2):

$$F_5 = \left\{ \frac01, \frac15, \frac14, \frac13, \frac25, \frac12, \frac35, \frac23, \frac34, \frac45, \frac11 \right\}$$

Two structural facts that make it musical:

1. **Neighbor property**: consecutive fractions $a/b < p/q$ satisfy $b p - a q = 1$. This means every successive pair is coprime — the interval between them, $\Delta = \frac{1}{bd}$ of the bar (Knott §1.3; Hardy & Wright Theorem 28), decomposes the bar into rational slices with coprime endpoints.
2. **Mediant insertion**: the first fraction that appears between neighbours $a/b$ and $p/q$ as N grows is their mediant $(a+p)/(b+q)$. This is exactly how $F_N$ builds up from $F_{N-1}$, and it is the same recursive law that generates the Stern–Brocot tree.

**Size**: $|F_N| = 1 + \sum_{k=1}^{N} \varphi(k) \sim \frac{3 N^2}{\pi^2}$ (Hardy & Wright). Growth examples: $|F_5| = 11$, $|F_8| = 23$, $|F_{11}| = 43$, $|F_{13}| = 59$, $|F_{20}| \approx 128$.

**Euler totient** enters naturally: the number of fractions in $F_N$ with denominator exactly $b$ is $\varphi(b)$ — the count of reduced playable nodes for partial b on a string (Nicholson & Sabat 2020). So $F_N$ is simultaneously a rhythm grid and a map of harmonic-series filters.

### 1.2 Stern–Brocot tree

The **Stern–Brocot tree** (Stern 1858; Brocot 1862) is the infinite binary tree whose vertices are in bijection with the positive rationals. Root = $1/1$. Every vertex is the **mediant** of its two nearest ancestors:

$$\text{mediant}\!\left(\frac{a}{b}, \frac{p}{q}\right) = \frac{a+p}{b+q}$$

Left child of $(a/b, p/q)$-interval = mediant with left bound; right child = mediant with right bound. First rows (Knott §3.2):

```
Level 0:                        1/1
Level 1:                  1/2        2/1
Level 2:              1/3    2/3   3/2    3/1
Level 3:          1/4  3/5  2/5  3/4  4/3  5/3  3/2? → 5/2  4/1
```

**Key theorems** (Graham–Knuth–Patashnik §4.5; Wikipedia):
- Every positive rational appears **exactly once** (in lowest terms).
- The tree is ordered like a binary search tree: left subtree = values in (0,1), right subtree = values in (1,∞). This is why it powers exact binary-search rational approximation.
- **Continued-fraction correspondence**: the path from root to $q = [a_0; a_1, \ldots, a_k]$ visits the *continued-fraction truncations* of q — each ancestor is the best rational approximation to q with denominator below the next convergent's denominator. Paths are encoded as $a_0$ R's, $a_1$ L's, $a_2$ R's, ... (with the last run shortened by 1; see Pitfall 4).
- **Tenney height**: for ratio $p/q$, $H(p/q) = \log_2(p \cdot q)$ (Tenney 1983). In the tree, H increases monotonically along every root-to-leaf path — tree depth is a faithful proxy for ratio complexity/dissonance. This is the built-in consonance metric FSBC exploits; no psychoacoustic model or corpus statistics needed.

### 1.3 Stern diatomic series and the Calkin–Wilf enumeration

**Stern's diatomic series** $s(n)$, OEIS A002487 (Stern 1858): $s(0)=0$, $s(1)=1$, $s(2n)=s(n)$, $s(2n+1)=s(n)+s(n+1)$ — the sequence $0, 1, 1, 2, 1, 3, 2, 3, 1, 4, 3, 5, 2, 5, 3, 4, 1, \ldots$

**Calkin–Wilf tree** (Calkin & Wilf 2000): the enumeration $q_n = s(n)/s(n+1)$ lists *every positive rational exactly once*:

$$1/1,\; 1/2,\; 2/1,\; 1/3,\; 3/2,\; 2/3,\; 3/1,\; 1/4,\; 4/3,\; 3/5,\; 5/2,\; \ldots$$

Two properties perfect for composition:
- **Coprimality is built in**: $\gcd(s(n), s(n+1)) = 1$ for all n — every adjacent pair of events forms a coprime ratio, i.e., a just interval in lowest terms with no silent cancellation. Voice-leading between successive events is always a *pure* rational step.
- **Total coverage + zero repetition**: the sequence never loops, never repeats a ratio — a built-in through-composed non-repetitive form (contrast with 076 Thue–Morse which repeats motifs; FSBC's CW form guarantees no repeated rational anywhere).

## 2. Compositional machinery

The method maps the triple (Farey grid, SB tree, CW enumeration) onto the three classical parameters:

### 2.1 RHYTHM — Farey subdivision grid

Given a bar of length $T$ ticks and denominator budget $N$:

- Onset set = $\{t = \lfloor (a/b) \cdot T \rceil : a/b \in F_N\}$ (all reduced fractions).
- The bar is subdivided by every tuplet order $\le N$ simultaneously (divisive polyrhythmic array, Wannamaker 2012 — Tenney's *Spectral CANON for Conlon Nancarrow* is the canonical musical instance).
- Inter-onset interval between consecutive fractions $a/b < p/q$: $\Delta = T/(b q)$ (from $b p - a q = 1$).
- **Density filter**: restrict to fractions whose denominator is in a subset $D \subseteq \{2..N\}$ (e.g., $D=\{2,3\}$ = only binary+ternary grid → hemiola-heavy; $D=\{5\}$ = pure quintuplet; odd-only denominators = limping/offbeat feel).
- **Accent filter**: keep/drop by numerator parity or by Tenney height threshold $H \le H_{\max}$.

Grid-locked constraint: all onsets must land on integer ticks with a section length whose LCM of used denominators fits. With BAR = 1920 ticks (480 tpb × 4/4), LCM(1..8) = 840 ≤ 1920 ✓; LCM(1..9) = 2520 > 1920 ✗. So N ≤ 8 grid-locked; N > 8 continuous-time or nearest-tick (document the approximation; it degrades the fraction exactly, so prefer continuous for pure-JI use).

### 2.2 PITCH — Stern–Brocot ratio → pitch

Every positive rational $r = p/q$ is a frequency ratio:

$$\text{cents}(p/q) = 1200 \log_2(p/q), \qquad \text{MIDI}_{12\text{TET}}(p/q) = \text{root} + \text{round}\!\left(12 \log_2(p/q)\right)$$

Generation modes:
- **TET mode**: quantize to 12-TET scale degrees; simple ratios → familiar intervals (3/2→7 semitones = P5, 5/4→4 = M3, 6/5→3 = m3, 4/3→5 = P4, 9/8→2 = M2). Complex ratios (e.g. 11/8 ≈ 551¢ ≈ +51¢ off the tritone) produce chromatic enrichments or near-unison microtones depending on the walk.
- **JI mode**: keep the exact cents and render via pitch-bend (bend range ±50¢ ×k) or via absolute frequency instrument. The rationals themselves are the composition — the piece IS a just-intonation map.
- **Tree-walk continuity**: walking one edge at a time moves through *convergents* — each ancestor of $p/q$ is the best rational approximation with a smaller denominator, so pitch motion is perceptually graded: big approximate steps early (coarse), fine steps near the target (fine) — a natural "approach then settle" melodic contour, entirely deterministic.

### 2.3 HARMONY — rational chords

- **Tree row chord**: all $2^d$ nodes at depth d → a chord of 2^d ratios; shallow rows = consonant stacks (1/1, 2/1, 3/2...), deep rows = dense microtonal clusters (Tenney-height graded).
- **Farey triad**: from neighbors $a/b < p/q$ in $F_N$ insert mediant $m/n = (a+p)/(b+q)$; the triple forms a closure—the three pitch-classes share the neighbor property pairwise → parsimonious voice-leading, exactly the "mediant harmony" Sabat describes for playable-string aggregates (Nicholson & Sabat 2020).
- **Convergent cascade chord**: use the convergents of a target ratio as chord tones (C: 1/1, 2/1, 3/2, 5/3, 13/8, ... approaching $\varphi$); the chord "reaches" toward the irrational limit — harmonic tension = distance to the limit.

### 2.4 STRUCTURE — three canonical forms

1. **Farey-order arc**: sections with increasing denominator budgets (2→3→5→7→11→13→...→7→5→3→2). Density and complexity ramp up then resolve; N primes = maximally separated tuplets (no shared subgrid until the LCM boundary).
2. **SB tree walk**: form = a path in the tree; each section = one edge; the target ratio's continued fraction dictates the macro contour ($a_0$ R's = expansion above unison, $a_1$ L's = contraction below, ...). A walk to 3/2 then back to 1/1 is a literal I–V–I in rational space.
3. **CW timeline**: partition the piece's N_events by $\log_2(q_n)$ magnitude — regions where ratios < 1 (below root), > 1 (above), near 1 (consonant clusters). Zero repeats → a guaranteed through-composed arc.

### 2.5 Complexity

- Farey $F_N$ construction: $O(N^2)$ one-time per section (sorting reduced fractions; or O(N) incremental via neighbor recurrence).
- SB path for $p/q$: $O(\log \max(p,q))$ steps (binary search on the tree).
- CW enumeration: $O(1)$ amortized per event via the $s(n)$ recurrence.
- Per-cell generation: $O(1)$ per event after the section grid is built.
- Total for a V×S matrix with E events: $O(V \cdot S \cdot N^2 + E)$, dominated by the largest Farey budget used.

## 3. Python implementation sketch

```python
from math import gcd, log2
from fractions import Fraction
from collections import deque

# ---------- 1. Farey sequence of order N (ascending, reduced) ----------
def farey_sequence(N):
    """Ascending list of all reduced fractions a/b in [0,1] with b <= N."""
    out = []
    a, b, c, d = 0, 1, 1, N          # standard neighbor recurrence: a/b, c/d
    out.append(Fraction(0, 1))
    while c <= N:
        k = (N + b) // d
        a, b, c, d = c, d, k * c - a, k * d - b
        out.append(Fraction(a, b))
    return out                       # |F_N| ~ 3N^2/pi^2

# ---------- 2. Stern-Brocot tree walk (mediant bisection) ----------
def sb_find(p, q):
    """Path (list of 'L'/'R') from root 1/1 to p/q via mediant bisection.
    Bounds kept as (num, den) tuples (den=0 = +inf sentinel); mediants
    built as reduced Fractions exactly when they are finite."""
    lo, hi = (0, 1), (1, 0)                       # 0/1 and +inf sentinel
    target = Fraction(p, q)
    path = []
    while True:
        med = Fraction(lo[0] + hi[0], lo[1] + hi[1])
        if med == target:
            return path
        if target < med:
            hi = (med.numerator, med.denominator)
            path = path + ['L']
        else:
            lo = (med.numerator, med.denominator)
            path = path + ['R']

def sb_walk(path):
    """Yield the rationals visited when walking a path from the root."""
    lo, hi = (0, 1), (1, 0)
    cur = Fraction(1, 1)
    yield cur
    for step in path:
        if step == 'L':
            hi = (cur.numerator, cur.denominator)
        else:
            lo = (cur.numerator, cur.denominator)
        cur = Fraction(lo[0] + hi[0], lo[1] + hi[1])
        yield cur

# ---------- 3. Stern diatomic series / Calkin-Wilf enumeration ----------
def stern_diatomic(n):
    """s(n): s(0)=0, s(1)=1, s(2n)=s(n), s(2n+1)=s(n)+s(n+1). O(n)."""
    s = [0] * (n + 2); s[1] = 1
    for i in range(1, n // 2 + 1):
        s[2 * i] = s[i]
        if 2 * i + 1 <= n:
            s[2 * i + 1] = s[i] + s[i + 1]
    return s

def calkin_wilf(n_events):
    """First n_events positive rationals, each exactly once: s(k)/s(k+1)."""
    s = stern_diatomic(n_events + 1)
    return [Fraction(s[k], s[k + 1]) for k in range(1, n_events + 1)]

# ---------- 4. Pitch / rhythm mapping ----------
def ratio_to_midi(p, q, root=60, mode="tet12"):
    cents = 1200.0 * log2(p / q)
    if mode == "tet12":
        return root + round(cents / 100.0)     # 12-TET quantization
    return root, cents                         # JI: (midi root, bend cents)

def tenney_height(p, q):
    return log2(p * q)                         # consonance grade (lower = simpler)

def farey_onsets_TET(N, T, root=60, mode="all"):
    """Onset ticks from F_N scaled into [0, T); returns (tick, midi) pairs."""
    F = farey_sequence(N)
    out = []
    for frac in F[1:-1]:                       # drop 0/1 and 1/1 = bar boundaries
        a, b = frac.numerator, frac.denominator
        if mode == "odd" and b % 2 == 0: continue
        if mode == "binary" and b not in (2, 4, 8): continue
        tick = round((a / b) * T)
        if 0 < tick < T:
            midi = ratio_to_midi(b, 1, root)   # ratio b:1 = harmonic b of root
            out.append((tick, midi))
    return sorted(out)

# ---------- 5. Demo: 2-bar Farey grid + SB walk ----------
BAR = 1920                                    # 480 tpb x 4/4
onsets = farey_onsets_TET(5, 2 * BAR, root=60)  # quintuplet-max grid, 2 bars
print("Farey F5 onsets in 2 bars:", len(onsets), "first:", onsets[:5])

path = sb_find(5, 3)                           # path to 5:3 (major sixth)
print("SB path to 5/3:", "".join(path))
print("walk ratios:", [str(r) for r in sb_walk("".join(path))])
```

## 4. UnitMatrix filling (concrete)

- **Voices** = rows, each a (stalk, budget, mode) triple: Voice 1 Lead (deep path, N=7, tet12), Voice 2 Harmony (medium path, N=3, tet12), Voice 3 Bass (shallow path, N=2, tet12), optional Voice 4 Percussion (Farey-only onsets on channel 9, e.g. odd-denominator filter for limping groove).
- **Sections** = columns, each a denominator budget + target ratio + pitch mode: e.g., Intro (N=3, root), Verse (N=5, 3/2), Chorus (N=7, 5/3), Bridge (N=4, 4/3), Outro (N=3, 1/1=HOME).
- **Cells**: for each (voice, section): generate Farey onsets → map ratio to MIDI via `ratio_to_midi` → `create_note_unit(pitch, dur, vel)` events → pad to `section_len` ticks → `composer.validate()` → `composer.to_midi()`. Zero-drift invariant intact; JI voices render as pitch-bend events (or a microtonal instrument) if absolute tuning is used.

## 5. References

- Farey, J. (1816). "On a curious property of vulgar fractions." *Philosophical Magazine* 47, 385–386.
- Stern, M. A. (1858). "Ueber eine zahlentheoretische Function." *Journal für die reine und angewandte Mathematik* 55, 193–220.
- Brocot, A. (1862). *Calcul des roulements par la méthode des approximations.* Paris: Mallet-Bachelier.
- Hardy, G. H. & Wright, E. M. (2008). *An Introduction to the Theory of Numbers*, 6th ed., §3.2–3.14. Oxford University Press.
- Graham, R. L., Knuth, D. E. & Patashnik, O. (1994). *Concrete Mathematics*, 2nd ed., §4.5 (Farey sequences and Stern–Brocot trees). Addison-Wesley.
- Calkin, N. & Wilf, H. (2000). "Recounting the rationals." *American Mathematical Monthly* 107(4), 360–363.
- Wannamaker, R. (2012). "Rhythmicon Relationships, Farey Sequences, and James Tenney's *Spectral CANON for Conlon Nancarrow* (1974)." *Music Theory Spectrum* 34(2), 48–70.
- Nicholson, T. & Sabat, M. (2020). "Farey Sequences Map Playable Nodes on a String." *TEMPO* 74(291), 86–97.
- Tenney, J. (1983). "John Cage and the Theory of Harmony." *Plans for the Future: Darmstadt Summer Courses Texts.*
- Sethares, W. (2005). *Tuning, Timbre, Spectrum, Scale*, 2nd ed. Springer (Ch. 5 on rational approximations; App. B on continued fractions).
- Knott, R. (2018). "Fractions in the Farey Series and the Stern-Brocot Tree." r-knott.surrey.ac.uk.

## 6. Distinguishing the method

FSBC is the first **rational-number-tree** method in the DB. Siblings/foils: 012 Euclidean (Björklund distributes ONE k/n — FSBC generates ALL n ≤ N subdivisions hierarchically; both are continued-fraction cousins), 069 Christoffel (primitive binary balanced words = *special* Stern–Brocot/Sturmian paths; FSBC walks the full tree), 076 Thue–Morse (automatic sequence over Z_2 — different number-theoretic object, no rational coverage), 084 Zipf–Mandelbrot (logarithmic rank law — FSBC uses Tenney-height *geometry*, not frequency statistics), 111 Vuza tiling (additive factorizations of Z_n — FSBC is multiplicative rational structure), 112 Costas (2D distinct displacement — FSBC's Farey neighbor property is the 1D distinct-interval cousin), 025 Xenakis sieves (modular congruences — FSBC is mediant/continued-fraction arithmetic, not congruence lattices).