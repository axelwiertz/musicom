# Layer Architecture — Abstract → Concrete → Absolute

Migrate the unitmatrix/SCALE system into 3 named layers (not "matrices").
Sound is reserved for the Absolute layer (sound production, synthesis, mix).

## The 3 layers

| Layer | Role | Holds | Invariant |
|---|---|---|---|
| **Abstract** | composition plan | subset (12TET pc-set) sequences, tension curves, pattern network (z-relations, P/L/R), form | transposition- and register-invariant |
| **Concrete** | realization plan | unitmatrix cells: voices × sections, resolved MusicEvents (pitch, onset, duration, velocity), zero-drift | same shape/length, validated |
| **Absolute** | sound production | stems → WAV/OGG, SP-methods (SP-001 FluidSynth, SP-011 Karplus-Strong, ...) | reproducible render |

## Mapping onto existing code (reality check)

The engine already has these — they are NOT new:

- **SCALE L1–L4** (`workflows/paths.py`): macro (L4) = form/skeleton; meso (L3) = groove/motif; voice (L2) = contour; micro (L1) = note-to-note. These are **Concrete-layer** levels.
- **selector** (`workflows/selector.py`): (TaskProfile) → ordered method list. Currently single methods, no layer chaining.
- **rules/set_theory.py**: normal_form, prime_form, interval_vector — the **subset-theory kernel** exists.
- **methods_db.md / SCALE**: the method database (algorithmic, human HC-*, sound production SP-*) — has `methods_db.md`, `human_methods_db.md`, sound SP-* docs.

## Gaps (what this plan adds)

1. **Abstract layer does not exist**: subset sequences, tension curves, z-relation pattern network, P/L/R voice-leading moves.
2. **Selector emits methods, not chains**: needs `layers_needed` → ordered method chain across layers.
3. **methods_db has no layer tag**: no "which layer does this method feed".
4. **No z-relation/subset knowledge wired**: Forte ICV/Z-relations exist only as raw `rules/set_theory.py`.

## Files to change

| File | Change |
|---|---|
| `rules/subset_network.py` (new) | Pattern (subset), PatternNetwork (Tn/I/Z/complement/parsimonious), tension-from-ICV, progression_path |
| `workflows/selector.py` | add `LAYERS` map (method_id → layer), `layers_needed` on TaskProfile, `select_chain()` |
| `workflows/paths.py` | map SCALE L1–L4 → layers (L4/L3 = concrete-structure, L2/L1 = concrete-material); document 3-layer composition paths |
| `projects/Research/CompositionMethods/methods_db.md` | add Layer column |
| `docs/` | regenerate tables |

## Layer tags (initial mapping)

- **Abstract**: (new methods) subset-walk, tension-curve, z-relation variation
- **Concrete**: all existing SCALE L1–L4 (001 Skeleton-First L4, 012 Euclidean L3, 023 Tendency Masking L2, 002 Markov L1, ...)
- **Absolute**: all SP-* sound production methods

## Composition paths (the "full" pipeline)

1. **Full path**: Abstract (subset sequence + tension) → Concrete (realize units) → Absolute (render audio)
2. **Direct path**: Concrete only (legacy behavior, no subset network)
3. **Abstract-only**: progression analysis / re-harmonization, no render
