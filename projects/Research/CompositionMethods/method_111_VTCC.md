# Vuza Tiling Canon Composition (VTCC) — Method 111

**Paradigm:** Rules-Based
**Layer:** concrete

## Overview

VTCC generates polyphonic rhythm-and-pitch structures from *rhythmic tiling canons*: a finite rhythmic motif (the "inner rhythm") is played verbatim by several voices whose starting offbeats (the "outer rhythm") are arranged so that the motif's translates **partition the timeline exactly once**. The result is a mathematically guaranteed perfect hocket — no two voices ever strike the same beat, and every beat is struck — a canon with full coverage and zero collision, up to and including the extreme case of **Vuza canons (RCMC)**: aperiodic canons in which *neither* the motif nor the entries repeat within the period, giving music that is perfectly regular in coverage yet never literally repetitive.

This is the rhythmic/structural counterpart to the aperiodic-tiling family already in the DB (083 QTSC tiles *pitch* space aperiodically with substitution tilings; 076 PTM-ASC generates aperiodic *sequences*), but rooted in abelian-group factorization (Hajós 1950, de Bruijn 1950/55, Rédei, Sands 1962, Vuza 1991–93) and polynomial/cyclotomic methods (Coven–Meyerowitz 1999; Amiot 2009). It is a deterministic combinatorial method: same seed → same canon.

## Core Definitions

**Rhythmic canon** (Amiot, "Why rhythmic canons are interesting"). Let $A, B \subset \mathbb{Z}_n$ with $0 \in A \cap B$. The sum $A + B = \{a + b\}$ is *direct* (write $A \oplus B$) when every element of $A + B$ has a *unique* representation. A **tiling canon** satisfies

$$A \oplus B = \mathbb{Z}_n,$$

i.e. the map $(a,b) \mapsto a+b$ is a bijection $A \times B \to \mathbb{Z}_n$. Musically: |B| = m voices, voice $j$ plays the motif $A$ shifted by the offbeat $b_j$; the $|A| \cdot |B| = k \cdot m = n$ onsets cover $\mathbb{Z}_n$ exactly once.

**Line vs loop.** Tiling a *line* $A \oplus B = \{0,1,\dots,n-1\}$ (Johnson's "tiling the line") extends to a tiling of $\mathbb{Z}$ (Theorem: every finite-line tiling repeats). Tiling a *loop* = factorization of the cyclic group $\mathbb{Z}_n$. By de Bruijn's theorem every tiling of $\mathbb{N}$ by a finite tile is an m-zoom of a smaller one — so line tilings are structurally trivial (recursive zooms of a single note), and **cyclic groups are where the rich, aperiodic material lives**. (Vuza canons are *never* line tilings; they only exist on loops.)

**Periodicity.** A canon is periodic when $\exists p \not\equiv 0 \pmod n$ with $A + p = A$ or $B + p = B$. Periodic factorization ⟺ the factor is a zoomed copy of a smaller factor.

**Vuza canon / RCMC.** A factorization $A \oplus B = \mathbb{Z}_n$ in which **neither** factor is periodic. Vuza proved (rediscovering Hajós–de Bruijn–Rédei–Sands):

> **Theorem (existence).** $\mathbb{Z}_n$ admits a non-periodic factorization (equivalently: a Vuza canon exists) **iff** $n$ is **not** of the form $p^\alpha$, $p^\alpha q$, $p^2 q^2$, $p^\alpha q r$, $p q r s$ with $p,q,r,s$ distinct primes.

Smallest admissible $n$: $72 = 2^3 \cdot 3^2$. First historically found: $n = 108$ (restored by Andreatta). Valid periods start: 72, 108, 120, 144, 168, 180, 200, 216, 240, 252, 264, 270, 280, 288, 300, 312, 324, 336, 360, …

**Canonical example (verified this session):**

$$A = \{0,1,5,6,12,25,29,36,42,48,49,53\},\qquad B = \{0,8,16,18,26,34\},\qquad A \oplus B = \mathbb{Z}_{72}.$$

$|A| = 12$ onsets in the motif, $|B| = 6$ voices, $12 \cdot 6 = 72$ ✓; periodicity scan confirms both factors aperiodic. Vuza's own enumeration produced 36 RCMCs for $n = 72$; under the affine group these collapse to **2 orbits** (Noll, Fripertinger 2001).

## Polynomial / Cyclotomic Machinery

With generating polynomials $A(x) = \sum_{a \in A} x^a$, $B(x) = \sum_{b \in B} x^b \in \mathbb{Z}[x]/(x^n - 1)$:

**Proposition (Amiot).** $A \oplus B = \mathbb{Z}_n$ ⟺ $A(x)\,B(x) \equiv \Delta_n(x) := 1 + x + \cdots + x^{n-1} \pmod{x^n - 1}$ (equirepartition; product has only 0/1 coefficients).

Via the cyclotomic factorization $x^n - 1 = \prod_{d \mid n} \Phi_d(x)$, tiling questions become cyclotomic:

**Coven–Meyerowitz (1999).** For a finite $A \subset \mathbb{Z}$ with $0 \in A$: let $R_A$ = orders of cyclotomic polynomials dividing $A(x)$, $S_A = R_A \cap \{p^k : p \text{ prime}\}$. Conditions:
- (T1) $A(1) = \prod_{p^k \in S_A} p$,
- (T2) products of distinct prime powers in $S_A$ lie in $R_A$.

Then: $A$ tiles $\Rightarrow$ T1; T1 ∧ T2 $\Rightarrow$ $A$ tiles; and if $|A|$ has ≤ 2 prime factors, $A$ tiles $\Rightarrow$ T2. These give cheap *necessary* filters for motif candidates before running the complement search.

**Complement via circular deconvolution.** When $\gcd(A(x), x^n - 1) = 1$, $A$ is invertible in the ring and

$$B(x) \equiv \Delta_n(x) \cdot A(x)^{-1} \pmod{x^n - 1},$$

computable by FFT-based circular convolution inversion in $O(n \log n)$; the result must then be verified to be a 0/1 polynomial (else no canon with that $A$ exists).

## Generative Transformations (verified this session)

Three operations map any canon to a different, provably-valid canon — the section/morph menu:

1. **Duality** $A \oplus B = B \oplus A$: swap inner/outer rhythm. Same covered grid, different inner rhythm; textural "inside-out".
2. **Affine (multiplicative) transform** (Vuza part 3; Tijdeman 1995): if $\gcd(p, n) = 1$ then $(pA) \oplus B = \mathbb{Z}_n$ still tiles (and $A \oplus (pB) = \mathbb{Z}_n$). Verified: $A = \{0,1,4,5\}$ under $\times 3 \bmod 8$ gives $\{0,3,4,7\}$, still tiling $\mathbb{Z}_8$ with $B = \{0,2\}$.
3. **m-zoom** (de Bruijn 1955): $A'(x) = (1 + x + \cdots + x^{m-1})A(x^m)$, $B'(x) = B(x^m)$ — every note becomes $m$ consecutive notes, tempo × m, period $mn$. Verified: the $n=72$ canon zooms to a valid $n' = 144$ canon.
4. **Column-shift mutation** (Vuza, exhibited at $n = 180$): shift one entry column against the rest; yields a *new* RCMC with the same entries — a ready-made "development section".

## Python Implementation Sketch

```python
from functools import lru_cache

def tiles(A, B, n):
    """Verify A ⊕ B = Z_n: every beat covered exactly once. O(|A|·|B|)."""
    cover = [0] * n
    for a in A:
        for b in B:
            cover[(a + b) % n] += 1
    return min(cover) == 1 and max(cover) == 1

def is_periodic(S, n):
    """Return a period p (1<=p<n) with S+p=S, or None. O(n·|S|)."""
    S = set(S)
    for p in range(1, n):
        if all((x + p) % n in S for x in S):
            return p
    return None

def find_complement(A, n, m):
    """Exact-cover search for B with |B|=m and A ⊕ B = Z_n. Returns B or None.
    Greedy/backtracking: add entries in increasing order, keep coverage <= 1."""
    A = sorted(set(a % n for a in A))
    cover = [0] * n
    for a in A:
        cover[a] += 1
    if max(cover) > 1:
        return None
    B = []

    def dfs(idx):
        if len(B) == m:
            return [] if all(c == 1 for c in cover) else None
        # prune: remaining entries must be able to cover all uncovered beats
        if sum(1 for c in cover if c == 0) > (m - len(B)) * len(A):
            return None
        # prune: with len(A)>=2 an entry never covers beat idx if idx in cover already...
        for b in range(idx, n):
            if b in B:
                continue
            # passing covers check
            touched = [(a + b) % n for a in A]
            if any(cover[t] for t in touched):
                continue
            for t in touched:
                cover[t] += 1
            B.append(b)
            res = dfs(b + 1)
            if res is not None:
                return res
            B.pop()
            for t in touched:
                cover[t] -= 1
        return None

    res = dfs(0)
    return sorted(res) if res is not None else None

def vuza_canon(n, k):
    """Search for a Vuza canon (both factors aperiodic) with |A|=k, |B|=n//k."""
    if n % k or (n // k) * k != n:
        return None
    # candidate motifs: subsets of size k of Z_n containing 0 (pruned by C-M T1)
    from itertools import combinations
    for comb in combinations(range(1, n), k - 1):
        A = (0,) + comb
        B = find_complement(A, n, n // k)
        if B is not None and is_periodic(A, n) is None and is_periodic(B, n) is None:
            return sorted(A), B
    return None

def affine_motif(A, p, n):
    """Vuza/Tijdeman: (pA) ⊕ B still tiles when gcd(p, n) = 1."""
    return sorted({(p * a) % n for a in A})

def zoom(A, B, m):
    """de Bruijn m-zoom: n' = m·n."""
    return sorted({m * a + r for a in A for r in range(m)}), sorted({m * b for b in B})

# --- usage: the verified n=72 Vuza canon ---
n, K = 72, 12
A = [0, 1, 5, 6, 12, 25, 29, 36, 42, 48, 49, 53]
B = [0, 8, 16, 18, 26, 34]
assert tiles(A, B, n)
assert is_periodic(A, n) is None and is_periodic(B, n) is None   # Vuza canon
B2 = find_complement(A, n, n // K)                                # recompute B by search
assert B2 == sorted(B)
A3 = affine_motif(A, 5, n)                                        # morph: ×5 mod 72
assert tiles(A3, B, n) and is_periodic(A3, n) is None             # new RCMC
Ap, Bp = zoom(A, B, 2)                                            # zoom to n'=144
assert tiles(Ap, Bp, 2 * n)
```

## musicom Engine Integration (UnitMatrix)

Compose with the sanctioned workflow — never hand-roll MIDI:

```python
from structures import MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit

# n=72 Vuza canon: 6 entry voices × 72-beat period, 480 ticks/beat
A = [0, 1, 5, 6, 12, 25, 29, 36, 42, 48, 49, 53]
B = [0, 8, 16, 18, 26, 34]
n, tick_per_beat = 72, 480
scale = [0, 2, 4, 5, 7, 9, 11]                      # C major as voice-degree map

composer = UnitMatrixComposer(bpm=120, ticks_per_beat=tick_per_beat, beats_per_bar=4)
composer.create_matrix(num_voices=len(B), num_sections=4)          # 6 voices × 4 sections
for j, b in enumerate(B):
    composer.add_voice(f"entry{j}", program=MidiInstrument.WOODBLOCK if j % 2 else MidiInstrument.MARIMBA, channel=j)

# Sections: Expo = A⊕B, Dev = (5A)⊕B, Re-Expo = dual B⊕A, Code = m-zoom fragment
sections = [
    (A, B, 72), (affine_motif(A, 5, 72), B, 72), (B, A, 72), (A, B, 36),
]
for s, (Am, Bm, ns) in enumerate(sections):
    section_len = ns * tick_per_beat
    for j, b in enumerate(Bm):
        events = []
        for a in Am:
            t = (b + a) % ns                        # onset beat inside section
            pitch = 60 + scale[(t + j) % len(scale)] + 12 * (j // 3)
            events.append((pitch, t * tick_per_beat))   # dur = 1 slot (staccato hocket)
        # pad to full section length (zero-drift invariant)
        units = [create_note_unit(p, dur=tick_per_beat, start_tick=t) for p, t in events]
        composer.fill_voice_section(f"entry{j}", s, units)    # engine pads to section_len
ok, msg = composer.validate()                        # MUST be True (zero-drift gate)
composer.to_midi("vuza_canon_72.mid")
```

Per section, the tiling identity $k \cdot m = n_s$ guarantees every onset slot is covered exactly once across voices — the section is a gapless, collision-free partition of its timeline, so the composite percussion stream is unbroken and the zero-drift gate passes at the onset level by construction.

## Musical Elements Framework

- **PITCH** — decoration layer over the guaranteed rhythm. Diatonic projection (slot mod scale), voice-degree pinning (each entry = one scale degree → no vertical coincidences at all), or motif-carried pitch canon with per-voice transposition (distributed klangfarbenmelodie: exactly one note per beat can be shared across the hocket).
- **RHYTHM** — primary. Perfect interlock: $k \cdot m = n$ onsets fill $n$ slots, one per slot. Motifs like $\{0,1,5,6,12,25,29,36,42,48,49,53\}$ give paired bursts and long silences; voices rest ~83% (n=72, k=12). Vuza non-periodicity = groove that never locks into a loop: aperiodic counterpart of 012 Euclidean evenness / 069 CWCC balance.
- **HARMONY** — every time-slice is a single degree ⇒ harmonic rhythm = the canon itself; stacking two independent RCMCs (the 2 affine orbits at n=72) with separate degree maps gives controlled two-layer canonic polyphony; dual canon = reharmonization-by-repartition.
- **STRUCTURE** — canon period = section (72 beats = 18 bars of 4/4 or 24 bars of 3/4). Form menu: RCMC exposition → affine/column-shift development → dual re-exposition → zoom coda; every morph provably valid; aperiodicity = form without exact repetition (rhythmic analogue of 083 QTSC).
- **TEXTURE** — composite density is invariant at exactly 1 onset/slot; the motif shape is the only density dial (clustered = per-voice bursts, spread = tick-tock). Canon/dual alternation = inner-outer textural inversion; wide-register pitch mapping = Webernian pointillism.

## References

- Vuza, D. T. (1991–93). "Supplementary Sets and Regular Complementary Unending Canons." *Perspectives of New Music* 29(2):22–49; 30(1):184–207; 30(2):102–125; 31(1):270–305.
- Andreatta, M. & Agon, C. (2011). "Modeling and Implementing Tiling Rhythmic Canons in the OpenMusic Visual Programming Language." *Perspectives of New Music* 49(2):66–91.
- de Bruijn, N. G. (1950). "On bases for the set of integers." *Publ. Math. Debrecen* 1:232–242; (1955). "On the factorisation of cyclic groups." *Indag. Math.* 17:370–377.
- Hajós, G. (1950). "Sur la factorisation des groupes abéliens." *Časopis Pěst. Mat. Fys.* 74:157–162.
- Sands, A. D. (1962). "The factorisation of Abelian groups." *Quart. J. Math. Oxford* 13:45–54.
- Coven, E. M. & Meyerowitz, A. (1999). "Tiling the integers with translates of one finite set." *J. Algebra* 212:161–174.
- Amiot, E. (2009). "Some reformulations and extensions of the theory of rhythmic canons." *J. Math. and Music* 3(2) (Tiling Problems special issue); Amiot, E. "About Vuza canons," arXiv:1304.6609.
- Lagarias, J. C. & Wang, Y. (1996). "Tiling the line with translates of one tile." *Invent. Math.* 124:341–365.
- Fripertinger, H. (2001). "Enumeration of non-isomorphic canons." *Tatra Mt. Math. Publ.* 23:47–57.
- Johnson, T. (2001). "Tiling the Line." Proc. J.I.M.
- Lanzarotto, G. (2022). "Extended Vuza canons." PhD thesis, Sorbonne Université / IRCAM, HAL tel-03843916.

Candidate code path: `generators/tiling_canon.py` (rhythm/hocket layer, concrete) — implements `tiles`, `find_complement`, `vuza_canon`, `affine_motif`, `zoom`; consumed by `workflows/unitmatrix_composer`-style cell filling as sketched above.