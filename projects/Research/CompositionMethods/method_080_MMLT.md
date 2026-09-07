# Method 080 — Messiaen Modes of Limited Transposition (MMLT)

- **Paradigm**: Rules-Based
- **Layer**: concrete
- **ID**: 080
- **Acronym**: MMLT
- **Category**: Scale / pitch-universe construction (transpositional symmetry)

## One-line description
Compose inside Olivier Messiaen's seven modes of limited transposition — symmetric
pitch-class sets invariant under a non-trivial transposition (only 2–6 distinct
transpositions, 33 in all), whose "charm of impossibilities" closes the harmonic
vocabulary down to symmetric truncation chords (augmented triads, diminished
sevenths, tritones).

## Summary-table row
```
| **080** | concrete | Messiaen Modes of Limited Transposition (MMLT) | **Rules-Based** | Pitch, Harmony, Structure, Texture | Strict (Mode/Truncation-guided) | Grid-Locked / Continuous | Meso / Phrase | $\mathcal{O}(N)$ | Generates music inside Messiaen's seven modes of limited transposition (whole-tone, octatonic, and five more) — pitch-class sets invariant under a non-trivial transposition, hence only 2–6 distinct transpositions (33 total, the "charm of impossibilities"). Melody is a walk on the mode; harmony is the mode's symmetric truncation chords (augmented triads, diminished sevenths, tritones); section = transposition shift (a color permutation) or a mode switch. No functional harmony — tension from mode choice, register, and truncation-chord. Symmetric-subset counterpart to 025 Xenakis Sieve / 069 CWCC; atonal cousin of 065 TTSMC. |
```

## The seven modes

| Mode | Interval pattern (cyclic) | Notes | Symmetry group $G_M$ | Transpositions | Signature truncation chord |
|---|---|---|---|---|---|
| 1 | 2 2 2 2 2 2 | 6 | $\{0,2,4,6,8,10\}$ | 2 | augmented triad $\{0,4,8\}$ |
| 2 | 1 2 1 2 1 2 1 2 | 8 | $\{0,3,6,9\}$ | 3 | diminished 7th $\{0,3,6,9\}$ + triads |
| 3 | 2 1 1 2 1 1 2 1 1 | 9 | $\{0,4,8\}$ | 4 | augmented triad |
| 4 | 1 1 3 1 1 1 3 1 | 8 | $\{0,6\}$ | 6 | tritone $\{0,6\}$ + dim7 |
| 5 | 1 4 1 1 4 1 | 6 | $\{0,6\}$ | 6 | tritone |
| 6 | 2 2 2 2 1 2 1 | 8 | $\{0,6\}$ | 6 | augmented triad + dim7 |
| 7 | 1 1 1 1 2 1 1 2 1 1 | 10 | $\{0,6\}$ | 6 | augmented triad + dim7 + tritone |

## Extended math

A pitch-class set $M \subseteq \mathbb{Z}_{12}$ is **limited in transposition** when
its symmetry group is non-trivial:

$$G_M = \{\, k \in \mathbb{Z}_{12} \;:\; M + k = M \,\}, \qquad |G_M| > 1$$

where $M + k = \{(p + k) \bmod 12 : p \in M\}$. The number of distinct
transpositions is $12 / |G_M|$ (Messiaen's 2, 3, 4, 6, 6, 6, 6). The symmetry group
is always a subgroup of $\mathbb{Z}_{12}$ (the cyclic group of order 12), hence
$|G_M| \in \{1, 2, 3, 4, 6, 12\}$. Only $|G_M| \in \{2,3,4,6\}$ are "limited" (the
diatonic scale has $|G_M|=1$).

**Construction.** A mode is the cyclic cumulative sum of its interval vector:

$$p_{i+1} = p_i + \mathrm{iv}_i \pmod{12}, \qquad \sum_i \mathrm{iv}_i \equiv 0 \pmod{12}$$

**Truncation chords.** Take every $r$-th note of the sorted cyclic mode. For a mode
with symmetry group $G_M$, truncating by $r = |G_M|$ (or a divisor of $12$) yields a
chord that is itself transposition-invariant — the augmented triad $\{0,4,8\}$
($r{=}2$ on Mode 1), the diminished seventh $\{0,3,6,9\}$ ($r{=}2$ on Mode 2), the
tritone $\{0,6\}$ ($r{=}6$ on Mode 4). These symmetric chords are the *entire*
native harmonic vocabulary — the "charm of impossibilities."

**Why no functional harmony.** A limited-transposition mode lacks the asymmetric
semitone/tone placement that creates leading tones and dominant pulls; transposition
is an internal permutation, so "modulation" is a color change, not a functional move.
Tension must therefore come from set relations (which degrees are emphasized, which
truncation chord is active, register/octave spread), not from V→I resolution.

## Python implementation sketch

```python
MESSIAEN_MODES = {
    1: [2, 2, 2, 2, 2, 2],              # whole-tone, 2 transpositions
    2: [1, 2, 1, 2, 1, 2, 1, 2],        # octatonic,  3 transpositions
    3: [2, 1, 1, 2, 1, 1, 2, 1, 1],     #             4 transpositions
    4: [1, 1, 3, 1, 1, 1, 3, 1],        #             6 transpositions
    5: [1, 4, 1, 1, 4, 1],              #             6 transpositions
    6: [2, 2, 2, 2, 1, 2, 1],           #             6 transpositions
    7: [1, 1, 1, 1, 2, 1, 1, 2, 1, 1],  #             6 transpositions
}

def mode_pcs(mode_id, root=0):
    """Pitch-class set of a Messiaen mode (cyclic interval pattern -> sorted PCs)."""
    pcs, acc = [], root % 12
    for iv in MESSIAEN_MODES[mode_id]:
        pcs.append(acc)
        acc = (acc + iv) % 12
    return sorted(set(pcs))

def symmetry_order(mode_id):
    """Return (|symmetry group|, number of distinct transpositions)."""
    pcs = mode_pcs(mode_id)
    g = sum(1 for k in range(12) if sorted((p + k) % 12 for p in pcs) == pcs)
    return g, 12 // g

def truncation_chord(mode_id, r):
    """Every r-th note of the mode (a symmetric 'truncation' chord)."""
    return sorted(mode_pcs(mode_id)[::r])

# symmetry_order(1) -> (6, 2)      whole-tone: 2 transpositions
# symmetry_order(2) -> (4, 3)      octatonic: 3 transpositions
# truncation_chord(1, 2) -> [0, 4, 8]      augmented triad
# truncation_chord(2, 2) -> [0, 3, 6, 9]   diminished seventh
```

## UnitMatrix integration
- **Voices (rows)** = one transposition of a mode per voice (all share one PC pool →
  vertical coherence) or one mode per voice.
- **Sections (columns)** = `(mode_id, transposition)` pairs; seams are limited
  transpositions (color shift) or mode switches (real contrast). Cyclic by
  construction (you run out of transpositions).
- **Cells (MusicUnit)** = `{PITCH}` from mode PC set, `{HARMONY}` = truncation-chord
  membership, `{STRUCTURE}` = transposition index, `{RHYTHM}` = onset/duration.

## Candidate code path
`generators/messiaen_modes.py` (concrete generator); the pure symmetry kernel
`transposition_symmetric_subsets()` could feed the abstract layer's
`rules/subset_network.py` (ABS-001..005), since a limited-transposition mode is
exactly a transposition-invariant subset of the 12TET network.

## References
- Messiaen, O. (1944). *Technique de mon langage musical*. Leduc. (Eng. trans. J. Satterfield, 1956.)
- Messiaen, O. (1941). *Quatuor pour la fin du temps*; (1944) *Vingt Regards sur l'Enfant-Jésus*; (1948) *Turangalîla-Symphonie*.
- Toop, R. (1974). "Messiaen/Goeyvaerts, Fano/Stockhausen, Boulez." *Perspectives of New Music* 13(1).
- Johnson, R. S. (1975). *Messiaen*. J. M. Dent.
- Tymoczko, D. (2011). *A Geometry of Music*. Oxford University Press.
- Forte, A. (1973). *The Structure of Atonal Music*. Yale University Press.
