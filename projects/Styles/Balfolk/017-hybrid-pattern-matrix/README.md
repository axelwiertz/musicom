# 014 — Genre Pattern Matrix

Status: active learning/composition project.

Purpose: teach genres through Musicom pattern DNA and matrix composition.

## Core method

- Pattern = musical DNA.
- `MusicMatrix` / `UnitMatrix` = reserved Musicom structure from `axelwiertz/musicom`.
- Rows = voices / pitch-space layers.
- Columns = measures / sections / time-space segments.
- Cells = `MusicUnit` objects or measure-level musical material.
- Genre Pattern Matrix = semantic education layer that maps onto the actual MusicMatrix.
- Compose by filling cells, not by guessing notes.

Repo KB source:

- `/opt/data/repos/musicom/structures/matrix.py`
- See `Notes/musicom-repo-integration.md`.

## Project structure

- `Notes/genre-kb.md` — overview knowledge base.
- `Analysis/rhythm-dna.md` — rhythm grids and metrical gravity.
- `Exercises/exercise-01-balfolk-jazz-hybrid.md` — first guided composition exercise.
- `MIDI/` — editable DAW files.
- `Audio/` — Telegram-ready OGG renders.
- `Renders/` — WAV masters.
- `Scripts/` — local generators.
- `index.html` — dashboard.

## Exercise 1 files

Original mido fallback:

- Balfolk: `MIDI/exercise1a_balfolk_dorian_jig.mid`, `Audio/exercise1a_balfolk_dorian_jig.ogg`
- Jazz: `MIDI/exercise1b_jazz_ii_v_i_swing.mid`, `Audio/exercise1b_jazz_ii_v_i_swing.ogg`
- Hybrid: `MIDI/exercise1c_hybrid_balfolk_jazz.mid`, `Audio/exercise1c_hybrid_balfolk_jazz.ogg`
- Compare: `Audio/exercise1_all_three_compare.ogg`

MusicMatrix/music21 build:

- Balfolk: `MIDI/musicmatrix_exercise1a_balfolk_dorian_jig.mid`, `Audio/musicmatrix_exercise1a_balfolk_dorian_jig.ogg`
- Jazz: `MIDI/musicmatrix_exercise1b_jazz_ii_v_i_swing.mid`, `Audio/musicmatrix_exercise1b_jazz_ii_v_i_swing.ogg`
- Hybrid: `MIDI/musicmatrix_exercise1c_hybrid_balfolk_jazz.mid`, `Audio/musicmatrix_exercise1c_hybrid_balfolk_jazz.ogg`
- Compare: `Audio/musicmatrix_exercise1_all_three_compare.ogg`
- Builder notes: `Analysis/musicmatrix-builder.md`
- Manifest: `Analysis/musicmatrix_manifest.json`

MusicMatrix v2 — brighter + more dance:

- Hybrid v2: `MIDI/musicmatrix_exercise1d_hybrid_v2_bright_dance.mid`, `Audio/musicmatrix_exercise1d_hybrid_v2_bright_dance.ogg`
- V1/V2 compare: `Audio/musicmatrix_exercise1_hybrid_v1_v2_compare.ogg`
- Exercise note: `Exercises/exercise-01-v2-brighter-more-dance.md`
- Manifest: `Analysis/exercise1_v2_bright_dance_manifest.json`

MusicMatrix v3 — reduce brightness + add melody answer:

- Hybrid v3: `MIDI/musicmatrix_exercise1e_hybrid_v3_answer.mid`, `Audio/musicmatrix_exercise1e_hybrid_v3_answer.ogg`
- V2/V3 compare: `Audio/musicmatrix_exercise1_hybrid_v2_v3_compare.ogg`
- Exercise note: `Exercises/exercise-01-v3-reduce-brightness-add-answer.md`
- Manifest: `Analysis/exercise1_v3_answer_manifest.json`

MusicMatrix v4 — AABB + bass variation:

- Final v4: `MIDI/musicmatrix_exercise1f_hybrid_v4_aabb_bass.mid`, `Audio/musicmatrix_exercise1f_hybrid_v4_aabb_bass.ogg`
- Exercise note: `Exercises/exercise-01-v4-aabb-bass.md`
- Manifest: `Analysis/exercise1_v4_aabb_bass_manifest.json`

## Exercise 2 files

Classical motif development:

- Audio: `Audio/musicmatrix_exercise2_classical_motif_v1.ogg`
- MIDI: `MIDI/musicmatrix_exercise2_classical_motif_v1.mid`
- Exercise note: `Exercises/exercise-02-classical-motif-development.md`
- Manifest: `Analysis/exercise2_classical_motif_manifest.json`

## Learning target

Hear the difference between:

1. Balfolk = body pulse + modal melody.
2. Jazz = swing + chord-tone gravity.
3. Hybrid = Balfolk rhythm + Jazz color harmony.
