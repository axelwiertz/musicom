# Method 065 — Twelve-Tone Serial Matrix Composition (TTSMC)

**Paradigm**: Rules-Based (Deterministic) · **Classification**: Pitch, Rhythm, Harmony, Structure, Texture
**Tonal Gravity**: None (Aggregate Equality) · **Metric Binding**: Grid-Locked / Continuous · **Memory Depth**: Macro / Row Form · **Time Complexity**: $\mathcal{O}(F \cdot 12)$

## 1. Overview

Twelve-Tone Serial Matrix Composition (TTSMC) generates music from a single ordered 12-tuple of pitch classes — the **tone row** $P = (p_0, p_1, \dots, p_{11})$, a permutation of $\mathbb{Z}_{12}$ — and its 48 derived forms. The four basic operations generate the set-complex:

| Form | Definition |
|---|---|
| Prime $P$ | the row as written |
| Retrograde $R$ | $R_i = p_{11-i}$ (backwards) |
| Inversion $I$ | $I_i = (2p_0 - p_i) \bmod 12$ (intervals reversed about $p_0$) |
| Retrograde-Inversion $RI$ | $I$ read backwards |

Transposing any of the four by $t$ semitones gives $P_t, R_t, I_t, RI_t$ — **48 forms total**. The **12×12 serial matrix** (the "magic square") tabulates all 48 forms: row 0 is $P$, column 0 is $I$, each row is a transposition of $P$, each column a transposition of $I$, the anti-diagonals are $R$ forms, and the main diagonals are $RI$ forms.

Composition = *scheduling* row forms across the UnitMatrix. Each section (column) is assigned one or more row forms; each voice (row) reads a form (or a partition of one); the **aggregate property** — all 12 pitch classes sounding exactly once per row statement — replaces tonal function as the structural glue. Because every pitch class carries equal weight, the music is atonal by construction.

## 2. Extended Mathematics

### 2.1 The serial matrix

Fix $P$ (row 0). Column 0 is the inversion about $p_0$:

$$I_0 = (2p_0 - p_i) \bmod 12, \qquad i = 0 \dots 11$$

Row $t$ is then $P$ transposed by the interval from $p_0$ to $I_0[t]$:

$$M[t][i] = \big(p_i + (I_0[t] - p_0)\big) \bmod 12$$

so every row is a transposition of $P$ and every column a transposition of $I_0$. The 48 forms are read off the matrix: row $t$ = $P_t$, column $t$ = $I_t$, row $t$ reversed = $R_t$, column $t$ reversed = $RI_t$.

**Example.** $P = (0, 1, 5, 8, 7, 6, 3, 2, 4, 9, 10, 11)$ (a row whose first hexachord is the pitch-class set $\{0,1,5,6,7,8\}$). Then $I_0 = (0, 11, 7, 4, 5, 6, 9, 10, 8, 3, 2, 1)$, and row 6 of the matrix is $P_6 = (6, 7, 11, 2, 1, 0, 9, 8, 10, 3, 4, 5)$.

### 2.2 Invariants (Babbitt 1960)

A pitch-class set (segment) that maps to itself (or its complement) under a transformation is a **pivot**. If $P$'s first trichord equals $I_6$'s first trichord, that trichord is invariant and can bridge the two forms. Invariant pitch-class sets are the serial replacement for pivot chords: they let the composer move between row forms without an audible seam.

### 2.3 Combinatoriality (Babbitt 1955)

$P$ and $I_6$ are **hexachordally combinatorial** iff the first hexachord of $P$ and the first hexachord of $I_6$ are disjoint and together cover $\mathbb{Z}_{12}$:

$$\operatorname{hex}_1(P) \cap \operatorname{hex}_1(I_6) = \varnothing \quad\text{and}\quad \operatorname{hex}_1(P) \cup \operatorname{hex}_1(I_6) = \mathbb{Z}_{12}$$

Sounding both forms simultaneously produces complete 12-note aggregates every hexachord — the serial replacement for consonant chord progression. Schoenberg's Piano Piece Op. 33a uses exactly this $P_0$/$I_6$ pair.

### 2.4 Derivation

A row is **derived** if all its trichords/tetrachords are transformations of a single generator cell. Webern's Op. 24 row is derived from a single trichord $\{0, 1, 4\}$: every trichord of the row is a $T_n$/$I_n$ form of it. Derivation is the serial analogue of motivic unity — one cell generates the entire pitch surface.

### 2.5 Row counting

There are $12! = 479{,}001{,}600$ tone rows; $9{,}985{,}920$ classes up to transformation equivalence; $836{,}017$ distinct 12-tone cycles (Perle 1977).

### 2.6 Complexity

Matrix build: $\mathcal{O}(144)$. Each row statement: $\mathcal{O}(12)$. Total fill of a $V \times S$ UnitMatrix with $F$ statements: $\mathcal{O}(F \cdot 12)$ — linear, deterministic, seedable.

## 3. Musical Elements Framework

- **PITCH**: The row *is* the pitch material. Every melody is a row form (or a derived partition of one) read left-to-right; every simultaneity is a segment of a form read vertically (partitioning). Pitch repetition is forbidden within a statement — the aggregate is the unit of pitch syntax. Registral freedom (any octave) and rhythmic freedom (any duration) are the only degrees of freedom within a strict statement (Schoenberg's "topography").
- **RHYTHM**: The row fixes pitch *order* only, so rhythm is free — but serial practice derives it too: rhythmic series (durations as ordered sets, Babbitt's time-point system), or mapping row order numbers to onset offsets within a bar. Each section assigns a rhythmic profile (Euclidean groove 012, isorhythmic talea 032, or a serialized duration row) to its row statement.
- **HARMONY**: Vertical sonorities are *partitions* of a row form — adjacent segments stacked as chords. Any full partition sums to the aggregate. Combinatoriality is the harmonic engine ($P_0$/$I_6$ → 12-note aggregates every hexachord); invariant pitch-class sets act as pivot chords at form boundaries.
- **STRUCTURE**: Macro-form = row-form architecture. Sections are assigned forms from the matrix (A = $P_0$, B = $I_6$, A′ = $R_0$), so form is a network of transformations rather than key relationships. Choosing a path through the 48-form matrix *is* composing the form.
- **TEXTURE**: Texture = row distribution across voices. One form partitioned across $V$ voices = homophonic aggregate chords; $V$ voices each reading a different form = polyphonic aggregate counterpoint (Webern's multidimensional set presentations); derived rows = imitative texture.

## 4. UnitMatrix Integration (Voices & Sections)

- **Rows (Voices)**: Each voice reads a row form (or a partition of one) over a section. Voice 1 = $P_0$ melody; Voice 2 = $I_6$ counter-melody (combinatorial partner); Voice 3 = vertical partition of $P_0$ (chord tones); Voice 4 = $R_0$ in augmentation. Voices may share a form (partitioning = homophony) or read different forms (aggregate counterpoint); the aggregate property is enforced *per voice*.
- **Columns (Sections)**: Each section is assigned a row form $F_s$ from the 48-form matrix. The section's chord function is replaced by its *row-form region*; combinatorial pairs define section-scale aggregate blocks; invariant pivots smooth the joins.
- **Cells** $U_{v,s}$: `{PITCH}` = pitch-class segment of $F_s$ assigned to voice $v$, octave-registered; `{RHYTHM}` = onset offsets from the section's rhythmic profile; `{HARMONY}` = partition scheme (trichord/tetrachord/hexachord); `{TEXTURE}` = row distribution mode (partitioned / multi-form / derived).

## 5. Python Implementation Sketch

```python
import numpy as np

def serial_matrix(P):
    """P: length-12 permutation of Z_12. Returns 12x12 matrix M[t][i]."""
    P = np.array(P) % 12
    p0 = P[0]
    I0 = (2 * p0 - P) % 12          # inversion about p0 (column 0)
    M = np.zeros((12, 12), dtype=int)
    for t in range(12):
        M[t] = (P + (I0[t] - p0)) % 12   # row t = P transposed by I0[t]-p0
    return M

def row_forms(M):
    """All 48 forms: P_t, R_t, I_t, RI_t."""
    forms = {}
    for t in range(12):
        P_t = M[t].tolist()
        I_t = M[:, t].tolist()
        forms[f"P{t}"]  = P_t
        forms[f"R{t}"]  = P_t[::-1]
        forms[f"I{t}"]  = I_t
        forms[f"RI{t}"] = I_t[::-1]
    return forms

def partition(form, scheme):
    """Split a 12-tone form into segments (e.g. [3,3,3,3] or [4,4,4])."""
    out, i = [], 0
    for k in scheme:
        out.append(form[i:i+k]); i += k
    return out

def is_combinatorial(P, Q):
    """Hexachordal combinatoriality: first hexachords disjoint, union = Z_12."""
    return (set(P[:6]).isdisjoint(set(Q[:6]))
            and set(P[:6]) | set(Q[:6]) == set(range(12)))

def register(seg, center):
    """Octave-register pitch classes to a MIDI register center."""
    return [center + (pc - center) % 12 for pc in seg]

# --- musicom engine integration (sketch) ---
# from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit
# from structures import MidiInstrument
#
# composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
# composer.create_matrix(num_voices=4, num_sections=4)
# composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
# composer.add_voice("Counter", program=MidiInstrument.OBOE, channel=1)
# composer.add_voice("Chords", program=MidiInstrument.STRINGS, channel=2)
# composer.add_voice("Bass", program=MidiInstrument.ACOUSTIC_BASS, channel=3)
# composer.add_section("A", bars=2); composer.add_section("B", bars=2)
# composer.add_section("A'", bars=2); composer.add_section("C", bars=2)
#
# M = serial_matrix(P); F = row_forms(M)
# section_forms = {"A": F["P0"], "B": F["I6"], "A'": F["R0"], "C": F["RI6"]}
# for s, form in section_forms.items():
#     segs = partition(form, [3, 3, 3, 3])          # 4 voices x trichords
#     for v, seg in enumerate(segs):
#         # map order numbers to onset offsets within the section (rhythmic profile)
#         for i, pc in enumerate(seg):
#             pitch = register([pc], 72 if v < 2 else 48)[0]
#             start = i * 480                        # 8th-note grid (480 tpb)
#             composer.fill_voice_section(voice_names[v], s,
#                 create_note_unit(pitch, 480, start))
# ok, msg = composer.validate()   # MUST be True before to_midi
# composer.to_midi("ttsmc.mid")
```

## 6. Pitfalls

1. **Pitch-class vs. pitch confusion** — row is pitch *classes*, not pitches; naive same-octave output is cramped. Fix: octave-register to each voice's range.
2. **Aggregate violation** — repeating a pitch class before the row completes breaks the atonal premise. Fix: per-voice used-pitch-class set resetting at each statement end.
3. **Staccato / sparse texture** — strict serial pointillism produces the sparse, gap-filled texture the user rejected (011/032 failure mode). Fix: per the Method Hybridization rule, add a continuous fill layer (sustained aggregate pads, DPSM 026 row arpeggios, walking bass).
4. **Monotonous row recycling** — same form at same transposition = one 12-note loop. Fix: rotate through the 48-form matrix; use combinatorial pairs and invariant pivots.
5. **Atonal drift** — aggregate equality gives zero tonal gravity. Fix: derive the row from a scale, or pair with 022 MCWS quantization to pull pitches toward HOME.
6. **Rhythmic monotony** — same rhythmic profile per statement makes order predictable. Fix: serialize rhythm too (duration rows / Babbitt time-points), vary per section.
7. **Parallel octaves in partitioning** — overlapping pitch classes across voices create hollow parallel octaves. Fix: disjoint partition segments per simultaneity, distinct voice registers.
8. **Off-grid drift** — serialized onset offsets can land between ticks. Fix: quantize to the tick grid; run `composer.validate()` before export.

## 7. Comparison With Related Methods

| Method | Pitch Material | Determinism | Tonal Gravity |
|---|---|---|---|
| 002 Markov | local transition probabilities | stochastic | weak |
| 013 Inversion/Retrograde | motif transforms | deterministic | symmetric |
| 025 Xenakis Sieve | modular subsets | deterministic | strict (moduli) |
| 053 Lévy Flight | heavy-tailed random walk | stochastic | weak |
| **065 TTSMC** | **12-tone row + 48 forms** | **deterministic** | **none (aggregate)** |

## 8. References

- Schoenberg, A. (1975). *Style and Idea*. ("Composition with Twelve Tones", 1941.)
- Babbitt, M. (1960). "Twelve-Tone Invariants as Compositional Determinants." *Musical Quarterly* 46(2): 246–259.
- Babbitt, M. (1955). "Some Aspects of Twelve-Tone Composition." *Score and I.M.A. Magazine* 12: 53–61.
- Perle, G. (1977). *Twelve-Tone Tonality*. University of California Press.
- Perle, G. (1962). *Serial Composition and Atonality*. University of California Press.
- Wuorinen, C. (1979). *Simple Composition*. C. F. Peters.
- Hiller, L. & Isaacson, L. (1959). *Experimental Music: Composition with an Electronic Computer*. McGraw-Hill. (ILLIAC Suite — first computer serial composition.)
- Hauer, J. M. (1923). *Vom Wesen des Musikalischen*. ("Law of the twelve tones".)
- Wikipedia (2024). "Twelve-tone technique." (Consulted for historical/counting facts: 12! rows, 9,985,920 equivalence classes, 836,017 cycles.)
