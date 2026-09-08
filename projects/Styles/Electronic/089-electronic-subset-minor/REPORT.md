# 089-electronic-subset-minor — REPORT

**Date**: 2026-09-08 (completed manually after cron run 2026-09-07 23:11 hit
iteration cap with compose.py written but unexecuted)
**Style**: Electronic | **Layer**: abstract (weekly abstract-cadence run)
**Method**: ABS-002 Subset Walker + ABS-001 tension-curve steering +
method-006 cadence close (rules layer)
**Key**: A natural minor (aeolian) | **BPM**: 112 | **Form**: 6 sections × 4
bars = 24 bars (Intro / Verse / Chorus / Break / Verse2 / Outro)

## Method (abstract layer)

The harmony comes entirely from the ABSTRACT layer: a walk over the 12TET
subset network (`rules.subset_network.PatternNetwork`) steered by a per-bar
tension curve (ABS-001), then a rules-layer cadence close (method 006).

- Walk pool: 13 A-minor nodes (min9, dim11, maj0, min2, min4, maj5, maj7,
  min79, min72, min74, maj75, maj70, dom77)
- Seed 2371, 22 bars walked + forced G7→Am cadence (bars 22/23)
- Tension curve: `[2.0]*6 + [7.0]*6 + [2.0]*10` (calm → tense → resolve)
- Engine quirk documented: `walk(home=...)` never fires while
  tension_curve length == walk length (tension branch shadows home branch) —
  worked around with a 22-bar curve + rules-layer cadence bars 22/23.

**Progression** (24 bars):
Am · Em · F · C · F · C · G7 · Dm7 · G7 · Em7 · G7 · Cmaj7 · G · Em · Dm · F
· Dm · Em · F · C · Dm · C · G7 · Am
Degrees: i v VI III VI III V7 iv7 V7 v7 V7 IIImaj7 VII v iv VI iv v VI III iv
III V7 i

## Two-phase architecture

| Phase | Artifact | Content |
|---|---|---|
| 1 | `MIDI/089-electronic-subset-minor-phase1.mid` | Raw abstract-layer draft: single marimba voice, pitches sampled from the CURRENT WALKED SUBSET pc field (walk directly audible), euclid-clustered rhythm with fractional jitter (off-grid fingerprint), no harmony/bass/drums |
| 2 | `MIDI/089-electronic-subset-minor.mid` | 16th-grid locked (120 @ 480 TPB), A-minor scale snap + chord-tone quantize per bar (global bar lookup), voice-leading check/correction, full 6-voice texture |

Both phases passed their own zero-drift `validate()` gate.

## Voices (instrument_registry)

| Voice | Instrument | GM | Register | Role |
|---|---|---|---|---|
| Lead | Marimba | 12 | 60–96 | subset-walk lead, euclid groove |
| Clarinet | Clarinet | 71 | 52–96 | counterline (beats 2 & 4, 8th pairs) |
| Cello | Cello | 42 | 36–72 | sustained whole-bar pad (root-position shell) |
| Dulcimer | Dulcimer | 15 | 60–96 | 16th arpeggio, chord tones |
| Bass | Double Bass | 43 | 28–55 | root pulse 8ths (root/fifth alternation) |
| Drums | Drum Kit | ch9 | — | kick 1&3, snare 2&4, hats 8ths/16ths, break drops, outro sparse |

## Verification (real numbers)

### Grid audit (phase-2 MIDI, mido read-only)
| Voice | Notes | Off-grid (16th) |
|---|---|---|
| Lead (Marimba) | 219 | 0 |
| Clarinet | 96 | 0 |
| Cello | 72 | 0 |
| Dulcimer | 384 | 0 |
| Bass | 192 | 0 |
| **Total** | **963** | **0** |

### Harmony audit (scale + chord-tone per bar, floor attribution)
| Voice | Out-of-scale | Out-of-chord |
|---|---|---|
| All pitched voices | 0 | 0 |

**Zero-drift**: all 6 voice tracks length 46080 ticks (24 × 1920) — identical.
**Voice-leading**: 3 flags pre-fix (hidden 5th bar 1, hidden octaves bars 13 &
17) → all corrected → re-check **0 flags**.

### Audio (SP-001 FluidSynth, discover_soundfont)
- Full mix WAV + OGG: 54.21 s, peak 1.0, **silence ratio 4.97%** (< 30% ✓)
- RMS profile healthy: 0.06–0.13 across all 54 s — the only near-zero seconds
  (52–54) are legit tail decay after the final Am; **no mid-track gaps**
- 6 per-track stems rendered (Marimba, Clarinet, Cello, Dulcimer, Contrabass,
  Drums → `track05_Acoustic_Grand_Piano` — known ch9/program-0 stem-label quirk)
- All artifacts: size > 40 B asserted; provenance.json sidecars written

## Bugs found & fixed during completion
1. **`chord_tones_for` empty-set bug** (compose.py): static octave range
   `range(-2,4)` returned EMPTY tone sets for high roots (A/root 9) in the
   60–96 window — root-anchored base only reached pitch 52. Fixed with dynamic
   `oct_lo/oct_hi` computed from lo/hi. This was the crash that stalled the
   cron run's compose.py.
2. **Audit zero-drift false FAIL**: audit counted track 0 (conductor tempo
   track, len 0 by design) as a voice track. Fixed: skip `mid.tracks[0]`.
3. **RenderPipeline stems**: needed absolute `fluidsynth_bin`
   (`/opt/data/micromamba/envs/musicom/bin/fluidsynth`) — bare `fluidsynth`
   not on PATH in cron env.

## Files
```
MIDI/089-electronic-subset-minor-phase1.mid   (raw phase-1 draft)
MIDI/089-electronic-subset-minor.mid          (phase-2 arrangement)
Audio/089-electronic-subset-minor.wav/.ogg    (full mix, SP-001)
Audio/stems/track0X_*.wav/.ogg                (6 per-track stems)
Analysis/grid_visualization.txt               (density grid)
Analysis/summary.json                         (project summary)
Analysis/vl_audit.json                        (voice-leading audit)
Analysis/audit_result.json                    (grid+harmony audit: PASS)
compose.py / audit.py / render_audio.py       (reproducible pipeline)
README.md / REPORT.md
```
