# Registration Report: Method 104 — Parsimonious Subset Sequence Composition (PSSC)

**Date:** 2026-10-03  
**Agent:** Hermes Research Agent (scheduled cron job)  
**Status:** SUCCESS

---

## Method Identification

| Field | Value |
|-------|-------|
| **Method ID** | 104 |
| **Acronym** | PSSC |
| **Full Name** | Parsimonious Subset Sequence Composition |
| **Paradigm** | Rules-Based |
| **Layer** | abstract |
| **One-line Description** | Generalises parsimonious voice leading from Neo-Riemannian theory to ANY n-subsets of ANY p-scale, constructing exhaustive non-redundant circular nrep chord progressions via set-theoretic relations Rp/Re/Rf, 2D table representation, and lexicographic walk with inversion bipartition. |

---

## Summary Table Row

```
|| **104** | abstract | Parsimonious Subset Sequence Composition (PSSC) | **Rules-Based** | Pitch, Harmony, Structure, Texture | Moderate (Scale-subset filtered) | Grid-Locked / Continuous | Macro / Circular Sequence | $\mathcal{O}(C(n,p) \cdot p)$ | Generalises parsimonious voice leading from Neo-Riemannian triadic theory to ANY n-subsets of any p-scale. Constructs exhaustive, non-redundant, circular (nrep) chord progressions via set-theoretic relations (Rp/Re/Rf), 2D table, and lexicographic walk. Inversion-bipartition (2024) yields paired voice strands. Abstract-layer subset design: feeds rules/subset_network.py. |
```

---

## Database Statistics

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| **methods_db.md line count** | 22726 lines | 22831 lines | +105 lines |

---

## Files Created

| File | Path | Status |
|------|------|--------|
| **Standalone method file** | `method_104_PSSC.md` | ✓ Created |
| **Report file** | `report_104.md` | ✓ Created |
| **Appended section in DB** | `methods_db.md` (method section) | ✓ Appended (lines 22729+) |
| **Summary table row** | `methods_db.md` (line 114) | ✓ Inserted |

---

## Complete Method Section Text (as appended to methods_db.md)

The following is the full text of the method section appended to methods_db.md:

```
### 104 — Parsimonious Subset Sequence Composition (PSSC)

### Source
Bedouelle, H. (2023). "Exhaustive chord progressions and their use in music composition." Journal of Mathematics and Music 18(1), 42–60. DOI: 10.1080/17459737.2023.2166136. — Bedouelle, H. (2024). "Parsimonious sequences of pitch-class sets: bipartition through inversion and its applications to music composition." Journal of Mathematics and Music 19, 108–121. DOI: 10.1080/17459737.2024.2432901. — Bedouelle, H. (2025). "A post-tonal method of music composition." HAL hal-05425426.

### Layer
abstract — designs pitch-class subset sequences (n-chord progressions from a p-scale) as abstract set-relations without concrete register/duration events. Outputs sequences of pc-sets that feed the concrete layer via rules/subset_network.py for voicing, rhythm, and register assignment.

### Paradigm
Rules-Based — the construction of exhaustive non-redundant parsimonious (nrep) sequences follows deterministic mathematical rules (set theory, lexicographic ordering, inversion bipartition, alternating concatenation).

### Description
Parsimonious Subset Sequence Composition (PSSC) generalises the classical Neo-Riemannian parsimonious voice-leading concept (P/L/R operations on triads) to ANY n-subsets of ANY p-scale, constructing chord progressions where successive chords differ by exactly one pitch class. Defines three fundamental relations: Rp (parsimonious: share n-1 pcs), Re (equivalence: Tn/TnI-related), Rf (fuzzy: composition of both). These are compatible with any musical transformation, creating a 48-form symmetry group. The 2D table representation arranges n-chords by (n-1)-subset rows and set-class columns. The central result proves existence of circular nrep sequences for p=2..9, n=2..5. Construction via lexicographic ordering, last-letter partition, parsimonious walk, and alternating concatenation. The 2024 inversion-bipartition extension splits n-chords into two complementary strands for symmetric scales.

### Musical Elements Framework
PITCH: Core domain — n-chord pc-subsets with single-pc stepwise changes. RHYTHM: Not directly specified; nrep order provides temporal sequence for concrete rhythm assignment. HARMONY: Primary output — the nrep progression IS the harmonic plan with maximal smoothness. STRUCTURE: Macro-form from segmentation of the circular nrep sequence across sections. TEXTURE: n cardinality controls density; alternating direct/retrograde creates registral arcs.

### UnitMatrix Integration
Voices (Rows): Multiple voices carry different 48-form variants (direct/retrograde/inverted/retrograde-inverted). Inversion-bipartition: Voice 1 = Strand A, Voice 2 = I(Strand A). Sections (Columns): nrep sequence divided across sections at natural breakpoints. Cells: Each receives one n-chord for concrete realization.

### Pitfalls
- Combinatorial explosion for p > 10
- Rhythm not specified (companion method needed)
- No register (must be set in concrete layer)
- Tonal gravity not inherent
- Inversion bipartition only for symmetric scales
```

---

## Candidate Code Path

| Component | Path |
|-----------|------|
| **Abstract-layer implementation** | `rules/subset_network.py` — new module for ParsimoniousSequence, nrep construction, InversionBipartition |
| **Core set theory dependency** | `rules/set_theory.py` — Forte normal/prime forms, ICV, set-class labelling |
| **Concrete realization** | `rules/realize.py` — `realize_progression()` maps nrep sequence to MusicEvent[] |
| **Optional generator** | `generators/pssc_generator.py` (can delegate to existing generators if preferred) |

---

## Classification Details

### Paradigm: Rules-Based
The construction is fully deterministic: set theory operations (subset relations, set-class equivalence, lexicographic ordering, concatenation rules) produce the same output for the same inputs. No stochastic sampling, no nature-inspired dynamics, no trained neural parameters.

### Layer: Abstract
PSSC operates on pitch-class subsets (pc-sets) as abstract mathematical objects. It produces sequences of pc-sets (n-chord progressions) without specifying:
- Which octave/register each pitch class occupies
- What duration/rhythm each chord receives
- What dynamics/velocity to apply
- What instrument/timbre performs each voice

These are determined by the downstream concrete layer through rules/subset_network.py and rules/realize.py.

### Comparison to Related Methods

| Related Method | Difference |
|----------------|------------|
| 011 Voice-Leading Graph Search | Neo-Riemannian P/L/R on triads only; PSSC generalises to ANY n-subsets of ANY p-scale |
| 014 Negative Harmony | Single polar axis; PSSC handles all 48 transformation forms |
| 050 Optimal Transport | Continuous Wasserstein distance; PSSC uses discrete set-theoretic relations |
| 065 TTSMC | 12-tone row only; PSSC handles any scale size p=2..12 |
| 069 CWCC | Binary word balance; PSSC handles n-chords of any cardinality |
| 083 QTSC | Aperiodic tiling; PSSC gives explicit nrep construction |
| 095 CTC | Contour-only; PSSC works on actual pitch-class sets |
| 099 SSMC | Form-design via SSM; PSSC works harmonically |

---

## Quirks / Pitfalls Encountered During Registration

1. **Newline concatenation**: The `cat >> append` merged the new section content directly after the previous method's last paragraph without a blank line, because the previous method section did not end with a double newline. Fixed with a targeted patch.

2. **LaTeX backslash doubling**: The `patch` tool double-escaped `\mathcal{}` to `\\mathcal{}` in the summary table row. Required a second patch to restore single backslashes.

3. **103 row deletion**: An earlier patch erroneously deleted the **103** GNNC row from the summary table. Caught during verification and restored.

4. **Table prefix inconsistency**: Rows 001–100 use `|| ` prefix, rows 101–104 use `||| ` prefix (from prior edits). Both are valid Markdown table syntax but inconsistent. Left as-is to match existing pattern.

5. **Unicode em-dash**: The section header uses a Unicode em-dash (—). This caused grep searches for the plain ASCII pattern to return 0 matches initially. Switched to searching for the method name without the dash.

---

## Verification

- ✓ Summary table row for 104 present at line 114
- ✓ Method 103 summary row present at line 113 (restored)
- ✓ Method section `### 104 — Parsimonious Subset Sequence Composition (PSSC)` present at line 22729
- ✓ Standalone file `method_104_PSSC.md` written
- ✓ LaTeX backslashes confirmed single in both table row and section content
- ✓ nrep construction algorithm fully documented
- ✓ inversion bipartition documented
- ✓ 48-form symmetry documented
- ✓ Python implementation sketch included in standalone file

---

## Next Free ID

The next free algorithmic method ID is **105**.