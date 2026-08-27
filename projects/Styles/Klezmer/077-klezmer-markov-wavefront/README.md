# 077 — Klezmer Markov Wavefront

**Style:** Klezmer (Eastern European Jewish wedding/dance music)
**Method:** 022 — Markov-Constraint Wavefront Sequencing (MCWS), Stochastic
**Date:** 2026-08-24 (nightly cron)
**Seed:** 77022

## Concept

A freylekh-style dance in D harmonic minor (freygish-flavored), 132 BPM, 32 bars.
Phase 1 lets a weighted Markov walk wander the scale under a phrase-arc constraint
envelope; Phase 2 snaps every note to the local chord tones, smooths leaps,
adds grace ornaments, and locks a 5-voice zero-drift UnitMatrix.

## Parameters

| Param | Value |
|-------|-------|
| Key | D harmonic minor (D E F G A Bb C#) |
| BPM | 132 |
| Bars | 32 (8 sections x 4 bars) |
| Form | ABCD ABCD (A: F–C–Dm–A, B: Dm–G–A–F) |
| Voices | Violin (41) lead, Trumpet (57) harmony, Acoustic Bass (33), Synth Pad (88), Drums ch9 |
| Drums | Freylekh oom-pah: kick 1&3, snare 2&4, 8th hats |

## Phase 1 vs Phase 2

- **Phase 1** (`-phase1.mid`): raw Markov walk, single lead voice, no harmony —
  wandering, unanchored, rhythmically flat (4 quarter-notes per bar).
- **Phase 2** (final): chord-tone quantization pins the melody to F/C/Dm/A;
  leap smoothing + grace ornaments give the klezmer "krekht" vocal inflection;
  bass/pad/harmony/drums add the dance groove. Audible: melody goes from
  aimless meander to dancing over a clear harmony.

## Files

- `MIDI/077-klezmer-markov-wavefront.mid` — final (Phase 2, 5 voices)
- `MIDI/077-klezmer-markov-wavefront-phase1.mid` — raw draft (Phase 1, 1 voice)
- `Audio/077-klezmer-markov-wavefront.wav` — FluidSynth render (TimGM6mb.sf2)
- `Audio/077-klezmer-markov-wavefront.ogg` — Opus/voip delivery format
- `Analysis/grid_visualization.txt` — high-contrast UnitMatrix timeline
- `Analysis/summary.json` — parameters
- `Analysis/provenance.json` — AI-generated labels (per MIDI artifact)

## Verification

- `validate()` Phase 1: True / Phase 2: True (zero-drift gate)
- WAV: 126.8s, 7.9% silence (tail only), RMS 0.10-0.16 across music
- MIDI: 6 tracks (conductor + 5 voices), 58.2s
- Preflight: exit 0 (compliant, no raw-MIDI)
