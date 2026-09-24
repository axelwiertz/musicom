# Report 095 — Contour Theory Composition (CTC)

## Identity

| Field | Value |
|:---|:---|
| **Method ID** | 095 |
| **Acronym** | CTC |
| **Full Name** | Contour Theory Composition |
| **Paradigm** | Rules-Based |
| **Layer** | abstract |
| **One-line description** | Generates abstract contour prototypes (CAS/CSeg classes) independent of exact pitch classes, then maps them onto concrete scale degrees in the concrete layer. Contour = the shape of a melody/rhythm as a sequence of up/down/same relations. |

## Summary Table Row

```
|| **095** | abstract | Contour Theory Composition (CTC) | **Rules-Based** | Pitch, Rhythm, Structure, Texture | None (Contour-shape-defined) | Grid-Locked / Continuous | Meso / Contour Segment | $\mathcal{O}(N^2)$ segment gen, $\mathcal{O}(N \log N)$ real | Generates abstract contour prototypes (CAS/CSeg classes) independent of exact pitch — the shape of a melody as a sequence of up/down/same relations. ContourNetwork maps via I/R/RI transformations; concrete layer maps rank → scale degree. First abstract-layer method: feeds rules/subset_network.py. |
```

## Database Statistics

| Metric | Value |
|:---|:---|
| Lines before | 19936 |
| Lines after | 20022 |
| Delta | +86 lines |
| Summary row location | Line 105 |
| Method section location | Line 19939 |

## File Manifest

| File | Path |
|:---|:---|
| Method section (appended) | `/opt/data/projects/Research/CompositionMethods/methods_db.md` |
| Standalone method file | `/opt/data/projects/Research/CompositionMethods/method_095_CTC.md` |
| This report | `/opt/data/projects/Research/CompositionMethods/report_095.md` |

## Candidate Code Path

```python
# Abstract layer
rules/contour_theory.py          # CSeg, CAS, ContourVocabulary, transformations I/R/RI
rules/subset_network.py          # Integration point: ContourNetwork feeds PatternNetwork

# Concrete layer (downstream, separate methods)
generators/contour_realizer.py   # Maps CSeg ranks → scale degrees → MusicEvents
```

## Appended Method Section Text

The following was appended to `methods_db.md` (after the algorithmic methods table, before the Sound Production Methods Framework section):

```
---
### Method 095 — Contour Theory Composition (CTC)
**Paradigm**: Rules-Based
**Layer**: abstract

| Attribute | Value |
|:---|:---|
| **Method ID** | **095** |
| **Method Name** | Contour Theory Composition |
| **Acronym** | CTC |
| **Paradigm** | Rules-Based |
| **Layer** | abstract |
| **Primary Elements** | Pitch, Rhythm, Structure, Texture |
| **Tonal Gravity** | None (Contour-shape-defined) |
| **Metric Binding** | Grid-Locked / Continuous |
| **Memory Depth** | Meso / Contour Segment |
| **Time Complexity** | $\mathcal{O}(N^2)$ segment generation, $\mathcal{O}(N \log N)$ contour realization |
| **Description** | Generates abstract contour prototypes (CAS/CSeg classes) independent of exact pitch classes, then maps them onto concrete scale degrees in the concrete layer. Contour = the shape of a melody/rhythm as a sequence of up/down/same relations. |

### Source

- Friedmann, M. L. (1985). "A Methodology for the Discussion of Contour: Its Application to Schoenberg's Music." *Journal of Music Theory*, 29(2), 223–248.
- Marvin, E. W. & Laprade, P. A. (1987). "Relating Musical Contours: Extensions of a Theory for Contour." *Journal of Music Theory*, 31(2), 225–267.
- Morris, R. D. (1993). "New Directions in the Theory and Analysis of Musical Contour." *Music Theory Spectrum*, 15(2), 205–228.
- Quinn, I. (1997). "Fuzzy Extensions to the Theory of Contour." *Music Theory Spectrum*, 19(2), 232–263.
- Quinn, I. (1999). "The Combinatorial Model of Pitch Contour." *Music Perception*, 16(4), 439–456.
- Sampaio, M. S. (2018). "Contour Similarity Algorithms." *MusMat*, II(2), 49–75.
- Carter-Ényì, A. (2016). "Contour Recursion and Auto-Segmentation." *Music Theory Online*, 22(1).

### Layer

**Abstract** — CTC operates entirely in the abstract layer: it designs pure contour-shape sequences (pitch-direction patterns, combinatorial contour matrices) that are transposition- and interval-invariant. The output is a set of contour prototypes and a ContourNetwork (CAS → contour class → transformation graph) that feeds the concrete layer via `rules/subset_network.py`-style integration. No concrete pitch/velocity events are generated at this layer.

### Description

Contour Theory Composition (CTC) treats the **shape** of a musical line as the primary compositional parameter, decoupled from exact pitch-class content. The method is built on the following hierarchy:

1. **Contour Point (CP)** — a pitch ordered in time, abstracted as its rank in a set of points (e.g., in a 4-note figure the highest pitch is 3, lowest is 0).
2. **Comparison Function** — `CMP(a, b) =` `+` if b > a, `-` if b < a, `0` if b = a.
3. **Contour Adjacency Series (CAS)** — a string of `+`, `-`, `0` symbols encoding only the direction between *adjacent* points. Example: `< + - + + - >`.
4. **Combinatorial Contour** — the full upper-triangular comparison matrix encoding all *pairwise* relations (adjacent and non-adjacent). Two contours with the same matrix belong to the same **contour class**.
5. **Contour Class** — equivalence class under renormalization (translation of pitch ranks to {0, 1, ..., n-1}), inversion, retrograde, and retrograde-inversion. The combinatorial matrix is invariant under transposition.
6. **Contour Segment (CSeg)** — a normalized sequence of contour ranks. Example: CSeg `<0 2 1 3>` means the second point is highest, third is second-highest, fourth is highest, etc.
7. **Contour Reduction (Morris 1993)** — an algorithm that extracts the structural skeleton of a contour by removing points that are "embellishing" (non-essential to the large-scale shape), analogous to Schenkerian reduction but operating on pure shape.

The CTC method composes as follows:

**Phase A — Abstract Design (this layer)**:
1. Define a **ContourVocabulary** — a library of CSeg prototypes (e.g., `<0 1 2>` = ascending, `<0 2 1 3>` = arch, `<0 1 3 2>` = twist, `<0 3 1 2>` = leap-and-fill).
2. Construct a **ContourNetwork** — a graph where nodes are CSeg classes and edges are contour transformations (I, R, RI, Morris reduction, Quinn fuzzy embedding). The network encodes how one contour can be derived from another.
3. Choose a **CAS template** for each section of the piece — a string of `+`/`-`/`0` of length N that defines the large-scale directional profile of that section. Template selection can follow an arc (many + = rising section, many - = falling, alternation = stable oscillation).
4. Generate a **contour-tension curve** from the CAS: count directional changes (peaks = high tension), max-run length (sustained rise = building tension), CAS entropy (chaotic = unstable).
5. Output for the concrete layer: a **ContourProgression** — a sequence of `(CSeg_k, section_id, voice_id, transformation)` tuples that specify what shape each voice should play in each section.

**Phase B — Concrete Realization (separate method)**:
The concrete layer takes each CSeg and maps its ranked points {0, 1, ..., n-1} onto scale degrees within the section's key, then fills UnitMatrix cells with MusicEvents.

### Musical Elements Framework

- **PITCH**: Contour classes abstract pitch entirely. Only relative order matters. In realization, contour rank → scale degree (e.g., CSeg `<0 2 1 3>` in C major could map to pitches C–G–E–G'). The abstraction means the *same* contour can be realized in any key, mode, or register without changing the shape.
- **RHYTHM**: A CAS can encode rhythmic direction too: `+` = longer/louder, `-` = shorter/softer. Alternatively, a separate rhythmic contour layer can drive note durations (the "durational contour": long→short→medium).
- **HARMONY**: Contour polyphony emerges from aligning multiple CSegs vertically. The simultaneous turning points (all voices rising = tutti crescendo, contrary motion = textural stability) define harmonic density without pitch-class content.
- **STRUCTURE**: The macro-form is a sequence of CAS templates per section, optionally with Morris contour reduction producing a multi-level structural skeleton (reduced contour at the section level, elaborated at the phrase level).
- **TEXTURE**: Contour density (number of directional changes per unit time) drives textural complexity. A smooth, mostly-ascending CAS (few direction changes) produces legato, lyrical texture; a jagged CAS (frequent changes) produces angular, pointillistic texture. Parallel vs. contrary motion across voices is controlled by comparing CSeg transformation choices per voice.

### UnitMatrix Integration (Voices & Sections)

Each **voice** (row) gets its own ContourSequence — a list of CSeg assignments per section. The **section** (column) provides the scale/mode onto which contour ranks are mapped. The abstract ContourProgression looks like:

```
Section A (C major, 4 bars):
  Voice 1 (Lead):  CSeg <0 2 1 3>  CSeg <0 1 2 3>  CSeg <0 3 1 2>  CSeg <0 2 3 1>
  Voice 2 (Harmony): I(CSeg <0 2 1 3>)  R(CSeg <0 1 2 3>)  RI(CSeg <0 3 1 2>)  CSeg <0 1 2 3>
  Voice 3 (Bass):    CSeg <0 3 2 1>  CSeg <0 2 1 3>  CSeg <0 1 2 3>  CSeg <0 3 2 1>
```

The concrete layer then fills each UnitMatrix cell with a MusicUnit whose pitch sequence is the rank→scale-degree mapping of the CSeg, and whose durations follow the durational contour associated with the CAS.

### Pitfalls

1. **Contour equivalence is too loose**: Two contours that sound very different can share the same combinatorial matrix if they have the same rank order but different interval sizes. The method must be paired with a concrete-layer interval filter (e.g., "never map rank 0→rank 1 to a leap > an octave").
2. **Rhythmic contour coupling**: If the same CAS drives both pitch direction and durational contour, the two may lock into unmusical 1:1 correlation. Recommend independent CAS strings for pitch and rhythm.
3. **CSeg length constraints**: Short CSegs (3–5 points) are easy to hear as motivic shapes; long CSegs (8+ points) lose perceptual contour coherence (Miller's law: ~7±2 chunks). Prefer CSegs of length 3–7 for motivic material, using contour reduction to compress longer lines.
4. **Scale mapping ambiguity**: Mapping contour rank 0→tonic (1) and rank n-1→dominant (5) works for 3-note CSegs but breaks for 5+ note CSegs where the scale only has 7 degrees. Use chromatic passing tones or modal mixture for intermediate ranks.
5. **No built-in tonal gravity**: CTC generates pure shapes with no inherent tonal function. Tonal gravity must be added by the concrete layer (e.g., anchoring rank 0 to the tonic and rank n-1 to the dominant or leading tone).
6. **Similar methods**: CTC complements 081 NIRMC (which generates expectations from intervals at the concrete layer) by operating a layer up — CTC decides the shape, NIRMC decides the interval-level realization.
```

## Classification Details

| Attribute | Classification |
|:---|:---|
| **Paradigm** | Rules-Based — deterministic transformations (I/R/RI), CAS template matching, Morris reduction algorithm. No stochastic sampling, no training. |
| **Layer** | abstract — first abstract-layer method in the DB. Designs pitch-direction patterns independent of concrete pitch, feeds into `rules/subset_network.py` for concrete realization. |
| **Tonal Gravity** | None (Contour-shape-defined) — contour is completely independent of key/tonality. Tonal gravity only emerges when the concrete layer maps ranks to scale degrees. |
| **Metric Binding** | Grid-Locked / Continuous — CAS can be realized in either grid-locked (bar-aligned) or continuous (prose/recit) time depending on concrete-layer choices. |
| **Memory Depth** | Meso / Contour Segment — CSegs are motivic-level shapes (3–7 notes), not full-form. Multi-level memory only via Morris contour reduction. |
| **Time Complexity** | $\mathcal{O}(N^2)$ for CSIM similarity (pairwise matrix), $\mathcal{O}(N \log N)$ for OSC similarity (FFT), $\mathcal{O}(N)$ for CAS generation. |

## Verification

- `wc -l methods_db.md`: 20022 lines (was 19936, +86)
- Summary row `095` found at line 105 via grep
- Method section `### Method 095 — Contour Theory Composition (CTC)` found at line 19939 via grep
- Standalone file written: `method_095_CTC.md`
- Report written: `report_095.md`

## Quirks & Pitfalls Hit

1. **Table prefix issue**: The patch introduced `|||` (triple pipe) on the new rows instead of `||` (double pipe). Fixed with a second targeted patch.
2. **First abstract-layer method**: All 94 existing methods are `concrete`. CTC is the first `abstract` layer method — the LAYER_ARCHITECTURE.md explicitly identifies this as a gap.
3. **CSeg length constraints**: Perceptual research (Miller's law ~7±2 chunks) limits CSegs to 3–7 notes for motivic coherence.
4. **LaTeX escaping**: The patch tool correctly preserved `\` backslashes in the $\mathcal{O}$ notation without double-escaping.
5. **Method 095 does not duplicate existing methods**: The closest relatives are 081 NIRMC (interval-level expectations at concrete layer) and 065 TTSMC (12-tone row aggregate ordering). Neither operates on abstract contour shapes independent of pitch-class content.

## Next Free ID

**096** (since 094 was the previous max, 095 is now taken)