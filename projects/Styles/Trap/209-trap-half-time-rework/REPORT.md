# 209-trap-half-time-rework — Rework Report

## Source
- Project: `001-trap-half-time` (Trap) — `/opt/data/projects/Styles/Trap/001-trap-half-time/`
- Primary MIDI: `MIDI/trap-half-time.mid` (16 bars, 4 sections)

## Audit result (2026-09-28)
| Standard | Result |
|---|---|
| S1 Engine (UnitMatrixComposer) | PASS |
| S2 Zero-drift (all tracks equal) | PASS (5 tracks @ 30720) |
| S3 Rhythm-grid sync (pitched) | PASS (0 off-grid; 8 ch9 drum 32nds exempt) |
| S4 >= 4 voice tracks | PASS (5 voices) |
| S5 Two-phase artifacts | FAIL (no `-phase1.mid`) |
| S6 provenance.json + index.html | FAIL (index.html missing) |

**Decision: REDESIGN** (2 standards failed). Source already engine-compliant on
core S1–S4; rebuild fresh via canonical workflow preserving identity.

## Preserved identity
- Genre: Trap (half-time)
- Tempo: 140 BPM
- Key: C natural minor (source pads carried a phrygian b9 + G-major V; normalized to clean C aeolian)
- Core motif contour: up-up-down
- Instrumentation: 808 sub, dark pad, sparse square lead, half-time kick/snare, 16th hats

## What changed (longer + more varied)
- **Form**: 16 bars → **24 bars / 6 sections** (Intro, VerseA, Chorus, VerseB, Bridge, Outro).
- **Two-phase**: Phase 1 = Brownian-walk raw draft (single voice, unquantized). Phase 2 = musicom rules (chord-tone quantize, grid snap, dedup, register + voice-leading).

### Variation techniques (5 applied)
| Technique | Section |
|---|---|
| Augmentation + register drop | Intro |
| Diminution + density rise (counterline voice) | Chorus |
| Transposition +5 semitones (P4) | VerseB |
| Inversion + register drop | Bridge |
| Augmentation + fade | Outro |

### Per-section harmonic regions (each section own progression)
| Section | Chords | Midpoint root |
|---|---|---|
| Intro | Cm Cm Ab Ab | C |
| VerseA | Cm Gm Ab Bb | G |
| Chorus | Ab Eb Bb Cm | Eb |
| VerseB | Cm Gm Fm Bb | G |
| Bridge | Fm Ab Gm Cm | Ab |
| Outro | Cm Ab Cm Cm | Ab |

(Sections Chorus/Bridge do not start on tonic — avoids the bar-0 tonic bug.)

## Verification (read-only mido)
- Phase 2: 6 voice tracks, all len 46080 ticks (zero-drift).
- Off-grid pitched onsets: **0**
- Scale violations: **0**
- Chord violations: **0**
- Phase 1 (raw): 1 voice track len 46080; off-grid/scale/chord violations expected (pre-rules).
- Audio: WAV 48.75 s, peak 0.891, silent ratio 12.4% (< 30%), RMS -18.4 dBFS.

## Files
- `MIDI/209-trap-half-time-rework.mid` (phase 2, full)
- `MIDI/209-trap-half-time-rework-phase1.mid` (phase 1, raw)
- `Audio/209-trap-half-time-rework.ogg` / `.wav`
- `Analysis/grid_visualization.txt`
- provenance sidecars for both MIDI artifacts
