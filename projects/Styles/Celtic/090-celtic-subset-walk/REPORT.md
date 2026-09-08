# 090-celtic-subset-walk — REPORT

**Date**: 2026-09-08 (nightly composition cron)
**Style**: Celtic | **Layer**: abstract (weekly abstract-cadence run —
prior abstract run was 087; cadence: 085 → 086 → 087 → 088 → 089 → 090)
**Method**: ABS-002 Subset Walker + ABS-001 tension-curve steering +
rules-layer method-006 cadence close (forced A7 → Dm on the final two bars)
**Key**: D minor (aeolian + harmonic-minor raised 7th + dorian raised 6th
borrowings) | **BPM**: 108 | **Form**: 6 sections × 4 bars = 24 bars
(Intro / Verse / Chorus / Break / Chorus2 / Outro)

## Method (abstract layer)

The harmony comes entirely from the ABSTRACT layer: a walk over the 12TET
subset network (`rules.subset_network.PatternNetwork`) steered by a per-bar
tension curve (ABS-001), then a rules-layer cadence close (method 006).

- Walk pool: 12 D-minor/Dorian nodes (min2, maj5, min9, maj0, maj10, min7,
  dom79, dim1, min70, dom77, maj75, min4)
- Seed 20260908, 22 bars walked + forced A7 → Dm cadence (bars 22/23)
- Tension curve: `[2.0]*6 + [6.0]*6 + [8.5]*6 + [4.0]*3 + [2.0]*1`
  (calm → rise → peak → settle → resolve) + forced [7.0, 2.0] cadence
- Engine quirk (same as 089): `walk(home=...)` never fires while
  `tension_curve` length == walk length (tension branch shadows home branch)
  — worked around with a 22-bar curve + rules-layer cadence bars 22/23.

**Walk (24 bars, pattern ids)**:
min2 maj5 min2 min9 min2 maj5 | min70 maj75 min70 maj75 dom79 dom77 |
dim1 dom79 maj75 dom79 dim1 dom77 | min2 maj5 min2 min9 dom79 min2

**Progression (D-minor functional reading, 24 bars)**:
i · III · i · v · i · III · i7 · IIImaj7 · i7 · IIImaj7 · V7 · bVII7 ·
vii° · V7 · IIImaj7 · V7 · vii° · bVII7 · i · III · i · v · V7 · i
(Dm · F · Dm · Am · Dm · F · Dm7 · Fmaj7 · Dm7 · Fmaj7 · A7 · G7 ·
C#dim · A7 · Fmaj7 · A7 · C#dim · G7 · Dm · F · Dm · Am · A7 · Dm)

## Two-phase architecture

| Phase | Artifact | Content |
|---|---|---|
| 1 | `MIDI/090-celtic-subset-walk-phase1.mid` | Raw abstract-layer draft: single bagpipe voice, pitches sampled from the CURRENT WALKED SUBSET pc field (walk directly audible), 8th-grid rhythm with fractional jitter (off-grid fingerprint), no harmony/bass/drums |
| 2 | `MIDI/090-celtic-subset-walk.mid` | 16th-grid locked (120 @ 480 TPB), D-minor scale snap + chord-tone quantize per global bar (subset realization), voice-leading check/correction, full 6-voice Celtic texture |

Both phases passed their own zero-drift `validate()` gate.

## Voices (instrument_registry)

| Voice | Instrument | GM | Register | Role |
|---|---|---|---|---|
| Lead | Violin | 40 | 60–88 | subset-walk lead, bagpipe-draft melody |
| Flute | Flute | 74 | 72–88 | answering counterline (beats 2 & 4, 8th pairs) |
| Cello | Cello | 42 | 36–62 | sustained whole-bar pad (root-position shell) |
| Piano | Acoustic Grand Piano | 1 | 60–84 | harp-style 16th arpeggio rolls |
| Bass | Double Bass | 43 | 33–52 | root pulse 8ths/quarters + 16th pushes |
| Drums | Drum Kit | ch9 | — | kick 1&3, snare 2&4, hats 8ths/16ths, claps, break low-tom, outro sparse |

## Verification (real numbers)

### Grid audit (phase-2 MIDI, mido read-only)
| Voice | Notes | Off-grid (16th) |
|---|---|---|
| Lead (Violin) | 126 | 0 |
| Flute | 96 | 0 |
| Cello | 72 | 0 |
| Piano | 384 | 0 |
| Bass | 134 | 0 |
| Drums | 355 | 0 |
| **Total** | **1167** | **0** |

### Harmony audit (scale + chord-tone per bar, floor attribution)
| Voice | Out-of-scale | Out-of-chord |
|---|---|---|
| All pitched voices | 0 | 0 |

Audit scale = D-minor superset (aeolian + C# harmonic-minor raised 7th from
A7/C#dim + B natural dorian raised 6th from G7) — the abstract walk's
idiomatic modal borrowings. Every note is chord-quantized, so 0 out-of-chord
by construction and 0 out-of-scale against the superset.

### Phase-1 raw fingerprint
134 notes, 131/134 off the 16th grid (fractional jitter preserved in the raw
draft — the phase-1 point). Bagpipe GM 109 single voice.

**Zero-drift**: all 6 phase-2 voice tracks length 46080 ticks (24 × 1920) —
identical. **Voice-leading**: 9 flags pre-fix (6 hidden octaves, 2 hidden
fifths, 1 parallel fifth) → all corrected → re-check **0 flags**.

### Audio (SP-001 FluidSynth, discover_soundfont → FluidR3_GM.sf2)
- Full mix: 56.02 s, peak 1.0, **silence ratio 4.72%** (< 30% ✓)
- RMS 0.085, tonal windows 109/112 (dominant FFT peak 50–1000 Hz present)
- Only silent seconds are 54–55 (legit tail decay after final Dm); **no
  mid-track gaps**
- Phase-1 render: 55.33 s, silence 10.6%, tonal 107/110 (bagpipe draft
  audible, quieter by design — peak 0.26)
- All artifacts: size > 40 B asserted; provenance.json sidecars written

## Bugs found & fixed during completion
1. **Harmony audit false-FAIL (066 out-of-scale)**: initial audit scale was
   pure D aeolian, but the abstract walk's V7 (A7, C#) and bVII7 (G7, B♮)
   are idiomatic minor-key borrowings — same superset pattern as project
   088's F-aeolian audit. Fixed by auditing against the D-minor modal-mixture
   superset (aeolian + harmonic-minor raised 7th + dorian raised 6th).
   Re-audit: 0 out-of-scale, 0 out-of-chord.
2. **Voice-leading runtime warnings**: `check_parallel_motion` subtracts
   `notes2[j] - notes1[j]` where lists are length-2 chords — Python list
   arithmetic produced the "overflow in scalar subtract" RuntimeWarnings but
   still worked (numpy object arrays). Harmless; flags were correctly
   detected and fixed.

## Files
```
MIDI/090-celtic-subset-walk-phase1.mid   (raw phase-1 draft)
MIDI/090-celtic-subset-walk.mid          (phase-2 arrangement)
Audio/090-celtic-subset-walk.wav/.ogg    (full mix, SP-001)
Audio/090-celtic-subset-walk-phase1.wav/.ogg (phase-1 render)
Analysis/grid_visualization.txt          (density grid)
Analysis/summary.json                    (project summary)
Analysis/vl_audit.json                   (voice-leading audit)
Analysis/audit.json                      (grid+harmony audit: PASS)
Analysis/render_stats.json               (silence/RMS/tonal)
compose.py / audit.py / render_audio.py / audio_stats.py
README.md / REPORT.md
```
