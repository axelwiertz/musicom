# Rework Report — 268-pop-workflow-rework

**Date:** 2026-10-26 (nightly rework job)
**Source:** `Styles/Pop/workflow-demo` (pop-001.mid, 28 bars, C major, 120 BPM)
**Decision:** REDESIGN (audit failed) → rebuild through canonical `UnitMatrixComposer` two-phase pipeline, extend + add variation.

## Source identity (preserved)
- Genre: Pop · Key: C major · Tempo: 120 BPM · 4/4 · 480 tpb
- Motif: C–E–G–C arpeggio (scale degrees 0,2,4,7)
- Voices: Lead (Flute 74) · Pad (Bright Piano 1) · Bass (Contrabass 43) · Arp (Clarinet 71) · Drums (ch9)

## Audit result (which standards failed)
1. **Engine evidence missing** — no `compose.py` in source project (provenance sidecar says
   `musicom_workflow.compose(style=pop, method=001)`, but no authoring script to verify).
2. **Phase-1 artifact missing** — only `pop-001.mid`, no `-phase1.mid`.
3. **Sidecars missing** — no project-level `provenance.json`, no `index.html`.
Passed: zero-drift (all 5 tracks 53760 ticks), rhythm-grid sync (0 off-grid), 5-voice setup.

## What changed
- Rebuilt from scratch through `UnitMatrixComposer` (engine, not hand-rolled).
- Two-phase: Phase 1 raw generative draft → Phase 2 musicom rules (chord-tone quantize,
  grid-snap to 120, dedup, section-boundary clamp, register enforcement).
- Form extended 28 → **32 bars**, 5 → **8 sections**:
  `Intro(4) VerseA(4) VerseB(4) PreChorus(4) ChorusA(4) Bridge(4) ChorusB(4) Outro(4)`.

## Per-section harmonic regions (midpoint-chord root — no bar-0 tonic collapse)
| Section | Bars | Progression | Midpoint degree → root |
|---|---|---|---|
| Intro | 0–3 | I–IV–V–I | V → **G** |
| VerseA | 4–7 | I–V–vi–IV | vi → **A** |
| VerseB | 8–11 | vi–IV–I–V | I → **C** |
| PreChorus | 12–15 | IV–V–vi–V | vi → **A** |
| ChorusA | 16–19 | I–V–vi–IV | vi → **A** |
| Bridge | 20–23 | ii–IV–vi–V | vi → **A** |
| ChorusB | 24–27 | I–V–vi–IV | vi → **A** |
| Outro | 28–31 | I–IV–I–I | I → **C** |

## Variation techniques (6 — requirement ≥3)
1. **Transposition** — VerseB motif raised a fifth (+4 scale degrees); ChorusB +2 octaves.
2. **Inversion** — Bridge uses descending contour (7,4,2,0,2,4).
3. **Retrograde** — Outro reverses the motif (2,4,7,4,2,0).
4. **Augmentation** — Outro lead rhythm halved (4 slots/bar vs 8).
5. **Diminution** — PreChorus lead + arp run 16ths (vs 8ths).
6. **Register shift** — ChorusA/ChorusB lead raised an octave/two octaves.

## Dual-version note
`-perfect.mid` = grid-locked compositional truth (off-grid 0).
`-humanized.mid` = style(pop)+per-instrument DNA jitter (off-grid > 0 proves it ran).
Humanize seed **44111** (md5 of project name). Per-voice: Lead 3.84σ ticks, Bass +8 ms
layback (7.3 ticks mean shift), Drums anchor 2 ms (1.92σ ticks, mean shift 1.16).

## Phase-1 note
`-phase1.mid` is the raw generative draft (single voice, unquantized). Expected off-grid
267 / scale-viol 113 / chord-viol 210 — contrast with the phase-2 rules layer (0 / 0 / 0).
