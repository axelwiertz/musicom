# 222-flamenco-arc-register

Flamenco "por arriba" (E composite) · **Method 007 — Narrative Arc Register Planning** (concrete, Rules-Based).

Autonomous nightly composition job · 2026-10-04 · job `1fc3fd65d359`.

## Concept

The melody is **register-driven**: a narrative story arc (calm → rise → climax
→ fall → resolve) is mapped onto registral bands across 24 bars. Phase 1 emits
a raw register-wandered guitar walk on off-grid ticks; Phase 2 snaps it to the
16th grid, chord-quantizes to the Andalusian cadence **Am–G–F–E**, and builds a
5-voice flamenco texture.

## Quick facts

- **Key**: E flamenco composite = E F G G# A B C D (`{4,5,7,8,9,11,0,2}`)
- **BPM**: 120 · 4/4 · 480 TPB
- **Form**: Entrada | Letra | Falseta | Cumbre | Bajada | Cierre (6 × 4 = 24 bars)
- **Voices**: Lead (guitar 25), Cante (violin 40), Compas (clavi 7), Bajo (double bass 43), Palmas (drum kit ch9)

## Verification

- Zero-drift: PASS (5 tracks × 46080, equal length)
- Grid: **0 off-grid** (off16=0, off8=0 across 712 onsets)
- Harmony: **0 out-of-scale, 0 out-of-chord** (424 pitched onsets)
- Render: FluidSynth → WAV 10.7 MB → OGG 1.1 MB; silence 19.1%, peak 0.687

## Listen / edit

- `Audio/222-flamenco-arc-register.ogg` (Opus)
- `MIDI/222-flamenco-arc-register.mid` (DAW)
- `MIDI/222-flamenco-arc-register-phase1.mid` (raw pre-rules draft)

Full details: `REPORT.md` · audit JSON: `Analysis/audit.json`.
