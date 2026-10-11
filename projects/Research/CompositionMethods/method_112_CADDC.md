# Costas Array Distinct-Displacement Composition (CADDC) — Method 112

**Paradigm:** Rules-Based
**Layer:** concrete

## Overview

CADDC generates melodies, rhythmic skeletons, and hocket polyphony from **Costas arrays** (Costas 1965; independently Gilbert 1965): an $n \times n$ set of $n$ dots, one per row and one per column (a *permutation matrix*), such that **all $\binom{n}{2} = n(n-1)/2$ displacement vectors between pairs of dots are pairwise distinct**:

$$\forall\, i<j,\ k<l:\quad \big(j-i,\ \pi(j)-\pi(i)\big) = \big(l-k,\ \pi(l)-\pi(k)\big) \ \Longrightarrow\ (i,j)=(k,l).$$

Reading rows as time slots and columns as pitch degrees, this is the **2D generalization of the 1D Golomb ruler** (090 GRDC): not just *differences* (ruler marks on a line) but *displacement vectors* (lag, interval) on a plane are all unique. The consequence for melody is a mathematically guaranteed "no hidden transposition at any offset": every ordered pair of notes in the melody has a unique (time-lag, pitch-interval) signature.

This is the discrete analogue of the ideal "thumbtack" ambiguity function that made Costas arrays the standard waveform family for sonar and radar (Costas 1984) — a musical self-similarity bound: the melody's autocorrelation at every non-zero lag is minimal, so any repetition the listener hears is a *compositional* choice, never an accident of the construction.

## Core Definitions

**Permutation representation.** A Costas array of order $n$ is a permutation $\pi \in S_n$; the dot in row $i$ sits in column $\pi(i)$. The Costas property depends only on the set of difference pairs:

$$\mathcal{D}(\pi) = \{(j-i,\ \pi(j)-\pi(i)) : 1 \le i < j \le n\},\qquad |\mathcal{D}(\pi)| = \binom{n}{2}.$$

**Verification.** The property is checkable in $O(n^2 \log n)$ (build the set, test distinctness; Barker–Drakakis–Rickard 2009). For composition this is the *safety gate*: never trust an unverified permutation.

**Enumeration (OEIS A008404).** $C(1..8) = 1, 2, 4, 12, 40, 116, 200, 444$ (verified by brute force this session). The density collapses: Warnke–Correll–Swanson (2023) proved $C(n)/n! \le e^{-\Theta(n)}$. Full enumeration is open; counts to order 29 are known (Drakakis et al. 2008–2011; Beard 2006/2008/2017 to order 1030).

## Constructions (deterministic, verified this session)

### Welch (exponential)

For prime $p$ and a primitive root $g \bmod p$:

$$\pi(i) = g^{i} \bmod p, \qquad i = 1, 2, \dots, p-1 \quad\Rightarrow\quad \text{order } n = p-1.$$

Example: $p = 5$, $g = 3$: $3^1{=}3,\ 3^2{=}9{\equiv}4,\ 3^3{=}27{\equiv}2,\ 3^4{=}81{\equiv}1 \pmod 5$ → $\pi = [3,4,2,1]$, valid (verified). The **transpose** (logarithmic Welch) is also Costas — verified for all primitive roots of $p \in \{5,7,11,13\}$:

| $p$ | $g$ | $\pi$ (exponential) | valid |
|---|---|---|---|
| 5 | 2 | [2,4,3,1] | ✓ |
| 5 | 3 | [3,4,2,1] | ✓ |
| 7 | 3 | [3,2,6,4,5,1] | ✓ |
| 7 | 5 | [5,4,6,2,3,1] | ✓ |
| 11 | 2 | [2,4,8,5,10,9,7,3,6,1] | ✓ |
| 13 | 2 | [2,4,8,3,6,12,11,9,5,10,7,1] | ✓ |

### Lempel–Golomb

For a prime power $q$ and primitive elements $\alpha, \beta$ of $\mathrm{GF}(q)$, place a dot at $(i,j)$ iff

$$\alpha^{i} + \beta^{j} = 1, \qquad i, j = 1, \dots, q-2 \quad\Rightarrow\quad \text{order } q-2.$$

If $\alpha + \beta = 1$, deleting the first row and column yields order $q-3$ (such pairs exist for every prime power $q > 2$). Verified in $\mathrm{GF}(4)$ ($w^2 = w+1$; primitive elements $w, w+1$): all four $(\alpha,\beta)$ choices give the valid order-2 arrays $[2,1]$ / $[1,2]$.

### Morphs (validity-preserving transformations, verified)

Every transform below maps one Costas array to another — the formal section menu:

| Morph | Definition | Musical meaning |
|---|---|---|
| Identity | $\pi$ | exposition |
| Time reversal | $\pi'(i) = \pi(n+1-i)$ | retrograde (R) |
| Pitch inversion | $\pi'(i) = n+1-\pi(i)$ | interval inversion (I) |
| 90° rotation | transpose | logarithmic Welch flavour |
| Dihedral | any of the 8 D₄ symmetries | 8 formal variants |
| $T_4$ / $G_4$ edits | Golomb 1992; Golomb–Taylor 1984 row/column surgery | resize to fit bar counts |

Associated to Costas arrays: **NAKCAs** (non-attacking kings — no two dots diagonally adjacent; forbids stepwise motion in both axes) and the conjecturally-trivial **NAQCAs** (also an $n$-queens solution; only $n=1$ known).

## Musical Interpretation (verified this session)

Welch $p = 13$, $g = 2$ decoded chromatically (order 12 → 12 pitch classes):

$$\pi = [2, 4, 8, 3, 6, 12, 11, 9, 5, 10, 7, 1]$$

- The **stepwise** intervals are $\{+2,+4,-5,+3,+6,-1,-2,-4,+5,-3,-6\}$ — **all 11 distinct** (verified).
- Every pair of the 66 note pairs has a distinct (lag, interval) vector, so **no interval recurs at any fixed lag**: for each $d = 1..11$, the $12-d$ intervals at that lag are all distinct (verified).
- The melody is a **12-tone aggregate** (every pitch class exactly once, like a 065 TTSMC row) *plus* the interval-uniqueness guarantee.
- Dihedral/time-reversal/pitch-inversion transforms all verified to preserve the property.

## Python Implementation Sketch

```python
# generators/costas_array_generator.py (candidate path)
from itertools import permutations  # small-n search only

def is_costas(pi: tuple) -> bool:
    """Costas property: all n(n-1)/2 displacement vectors distinct. O(n^2)."""
    seen = set()
    for i in range(len(pi)):
        for j in range(i + 1, len(pi)):
            v = (j - i, pi[j] - pi[i])
            if v in seen:
                return False
            seen.add(v)
    return True

def primitive_roots(p: int):
    """All primitive roots modulo prime p."""
    out = []
    for g in range(2, p):
        seen, x = set(), 1
        for _ in range(p - 1):
            x = (x * g) % p
            if x in seen:
                break
            seen.add(x)
        if len(seen) == p - 1:
            out.append(g)
    return out

def welch_array(p: int, g: int) -> tuple:
    """Exponential Welch, order n = p-1. Requires p prime, g primitive root."""
    assert all(p % d for d in range(2, int(p ** 0.5) + 1)), "p must be prime"
    assert g in primitive_roots(p), "g must be a primitive root mod p"
    return tuple(pow(g, i, p) for i in range(1, p))

def lempel_golomb_array(q: int, alpha, beta) -> tuple:
    """GF(q) construction, order q-2. alpha, beta primitive in GF(q)."""
    # GF(q) arithmetic (poly representation over the defining irreducible);
    # place dot at (i,j) iff alpha^i + beta^j == 1; see session script for GF(4) demo.
    ...

def morph(pi: tuple, kind: str) -> tuple:
    """kind in {'identity','reverse','invert','transpose','d4-*'}. Preserves Costas."""
    if kind == "identity":
        return pi
    if kind == "reverse":
        return tuple(reversed(pi))
    if kind == "invert":
        n = len(pi)
        return tuple(n + 1 - v for v in pi)
    if kind == "transpose":  # logarithmic Welch
        inv = [0] * len(pi)
        for idx, val in enumerate(pi):
            inv[val - 1] = idx + 1
        return tuple(inv)
    raise ValueError(kind)

def decode(pi: tuple, mode="chromatic", scale=None, register=60):
    """Map order-n array to MIDI pitches."""
    if mode == "chromatic":
        return [register + (v - 1) for v in pi]
    if mode == "modal":
        return [register + scale[(v - 1) % len(scale)] for v in pi]
    raise ValueError(mode)

# ---- UnitMatrix filling (musicom engine) ----
# from structures import MusicEvent, UnitMatrix
# from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit
#
# slot_len = 480  # one quarter-note slot (ticks_per_beat=480)
# pi = welch_array(13, 2)                       # order 12 -> 12 slots
# for i, v in enumerate(pi):
#     unit = create_note_unit(pitch=decode((v,), "chromatic", register=60)[0],
#                             dur=slot_len // 2)   # staccato hocket
#     composer.fill_voice_section(voice, section, unit, start_tick=i * slot_len)
# ok, msg = composer.validate()   # zero-drift gate
```

## References

- Costas, J. P. (1984). "A Study of a Class of Detection Waveforms Having Nearly Ideal Range–Doppler Ambiguity Properties." *Proc. IEEE* 72(8), 996–1009.
- Gilbert, E. N. (1965). "Latin Squares Which Contain No Repeated Digrams." *SIAM Review* 7(2), 189–198.
- Golomb, S. W. & Taylor, H. (1984). "Construction and Properties of Costas Arrays." *Proc. IEEE* 72(9), 1143–1163.
- Golomb, S. W. (1984). "Algebraic Constructions for Costas Arrays." *J. Combin. Theory Ser. A* 37(1), 13–21.
- Golomb, S. W. (1992). "The $T_4$ and $G_4$ constructions for Costas arrays." *IEEE Trans. Inf. Theory* 38(4), 1404–1406.
- Drakakis, K. et al. (2008, 2011). "Results of the Enumeration of Costas Arrays of Order 27/28/29." *IEEE Trans. Inf. Theory* 54(10); *Adv. Math. Commun.* 5(3).
- Warnke, L., Correll, B. & Swanson, C. (2023). "The Density of Costas Arrays Decays Exponentially." *IEEE Trans. Inf. Theory* 69(1), 575–581.
- Barker, L., Drakakis, K. & Rickard, S. (2009). "On the Complexity of the Verification of the Costas Property." *Proc. IEEE* 97(3), 586–593.
- OEIS A008404 / A001441.