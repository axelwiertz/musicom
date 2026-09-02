# Abstract Layer Methods — subset walk, tension curve, z-variation

Composition methods that produce **abstract structure**: 12TET subset
sequences (chord/pitch-pool progressions), tension curves, and the pattern
network (z-relations, P/L/R moves). Output is transposition/register-
invariant; the concrete layer realizes it.

## Why these methods exist

Chord progression = walk through subset space. Tension/resolution falls out
of (dis)similarity between successive subsets — shared pitch classes,
interval-class-vector distance, z-relations, complementation. No functional
labels needed. See `subset_theory.md` for the theory.

## Method catalog (planned IDs)

| Method ID | Name | What it produces | Key idea |
|---|---|---|---|
| `ABS-001` | Tension Curve Planner | per-section tension targets from form | intro low → verse rise → chorus peak → bridge max → outro resolve |
| `ABS-002` | Subset Walker | pattern-id sequence | network walk, edge weight = closeness; tension_curve steers the walk |
| `ABS-003` | Z-Variation | re-harmonized pattern | swap a chord for its z-partner: same ICV (same color/tension), different notes |
| `ABS-004` | Parsimonious Voice Leading | smooth progression | P/L/R moves, ≤2 semitone total motion between adjacent subsets |
| `ABS-005` | Complement Contrast | maximal-change section | move a subset to its complement: matched tension, fresh harmony |

## Implementation (code reality)

All logic lives in `rules/subset_network.py` (Abstract layer, pure module):

- `Pattern` — a named 12TET subset with `icv`, `tension`, `prime`, `complement`.
- `PatternNetwork` — graph of patterns; edges typed TN / INV / Z / COMPL / PLR / VL with closeness weights.
- `PatternNetwork.walk(start, length, tension_curve, home)` — the subset walker (ABS-002).
- `interval_vector()` / `tension()` / `icv_distance()` / `common_tones()` / `voice_leading_distance()` — the metrics (ABS-001/003/004/005 building blocks).
- `diatonic_degree_patterns(tonic)` — map I–vii to library pattern ids (bridge to existing degree-based code).

## Verified behavior (smoke tests)

- Z-pair 4-Z15 {0,1,4,6} ↔ 4-Z29 {0,1,3,7}: same ICV [1,1,1,1,1,1], both T=8.5, prime forms differ → Z edge found. (theory-correct)
- Major triad T=2.0 (consonant), dim triad T=4.0, min7 T=5.0, dom7 T=7.0, whole-tone T=21.0 (tense). Monotone in dissonance. ✓
- Diatonic mapping C: I→maj0, V→maj7, vi→min9, IV→maj5. ✓
- Triad pairs with same prime (maj↔min on same root) → TN edge (correct: they are inversions, not z-related). ✓

## How a composer agent uses it

```python
from rules.subset_network import patterns_from_degrees, PatternNetwork

prog = patterns_from_degrees(0, ("I", "V", "vi", "IV"))   # pop anchor
net  = PatternNetwork(prog)
# tension curve across intro/verse/chorus/bridge/outro
walk = net.walk("maj0", 5, tension_curve=[0.5, 1.0, 1.5, 2.0, 0.8])
# walk = e.g. ["maj0", "min9", "maj7", "min9", "maj7"] — now feed to concrete layer
```

## References

- Forte 1973 (Z-relations, prime forms), Cohn 2012 (P/L/R), Tymoczko 2011 (voice-leading distance). Full list in `subset_theory.md`.
