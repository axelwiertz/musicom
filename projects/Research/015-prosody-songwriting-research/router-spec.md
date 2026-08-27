# Musicom Agent Router Spec

## Goal
One agent. Many methods. Forward, reverse, roundtrip.

This router is not only for a single project. It is the control layer for Musicom Agent itself.
It chooses how the agent composes, analyzes, reverses, and iterates across projects.

## Direction
This workflow now points toward a **genetic algorithm** loop:
- generate candidate variants
- evaluate with scorecard
- select winners
- mutate or crossover winners
- repeat across generations

## Human in the Loop
Human stays in control at key gates:
- choose the goal
- approve or reject candidate set
- adjust score weights
- override the winner
- decide when to stop evolving
- add subjective taste that scorecards miss

The agent proposes. Human disposes. Human may also steer mid-loop.

## Core Fields
- **direction**: `compose` | `reverse` | `roundtrip`
- **source_type**: `text` | `midi` | `audio` | `mixed`
- **method_id**: selected technique from methods DB
- **style**: style label, not genre label
- **target_outputs**: `midi`, `wav`, `notes`, `analysis`, `docs`
- **constraints**: key, meter, density, vocal range, narrative arc

## Router Logic
1. Read source.
2. Detect direction.
3. Select method by goal.
4. Run forward or reverse pipeline.
5. Analyze output.
6. Feed analysis back into method choice.
7. Save final method decision for project memory.

## Method Selection Rules

### Compose path
- **lyrics-first** -> `prosodic_narrative_coupling`
- **pattern-first** -> `skeleton_first`
- **probabilistic variation** -> `markov`
- **long-form transformation** -> `genetic`
- **tonal mirror** -> `negative_harmony`
- **loop/groove** -> `ostinato` or `groove_locked`

### Reverse path
- **MIDI source** -> `midi_analysis` + `reverse_music_analysis`
- **audio source** -> transcription first, then reverse map to UnitMatrix
- **unknown source** -> detect meter/key/rhythm, then infer method

### Roundtrip path
- Compose small seed.
- Reverse analyze seed.
- Compare intended method vs actual output.
- Recompose with corrections.

## Output Layout
- `README.md` -> compact report
- `research-notes.md` -> sources, observations, method comparisons
- `methods-additions.md` -> new Musicom methods or patches
- `manifest.json` -> machine-readable router data

## Project Reflection
This router makes Musicom less a pile of skills and more a controlled system.
It lets the same project move:
- from text to music
- from music back to structure
- from one method to another

## Research Direction
Best next research lanes:
1. Prosody-to-melody mapping.
2. Question/answer phrase shaping.
3. Tension/release cadence logic.
4. Reverse analysis into reusable pattern DNA.
5. Method scoring: which technique fits which input.
