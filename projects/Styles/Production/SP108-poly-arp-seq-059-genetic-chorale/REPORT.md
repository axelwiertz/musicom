# SP-108 Polyphonic Arpeggiator + Step Sequencer — 059-genetic-chorale

**Job:** random-style production (SP methods) — LAYER-ALIGNED
**Date:** 2026-10-20  **Seed:** 2026102022

## Selection

| Field | Value |
|---|---|
| Registry source | `workflows.musicom_workflow.SP_METHODS` (54 registered) — the **implemented** dict, NOT `methods_db.md` spec-only, NOT stale ranges |
| Method | `SP-108` |
| Module | `sound.generators.poly_arp_seq` → `Arpeggiator`, `PolySequencer`, `ArpSeqCombined` |
| Description | Polyphonic Arpeggiator + Step Sequencer — Up/Down/UpDown/Random/Assign arp modes, 1–4 octave, dotted/triplet/swing; 512-step polyphonic sequencer with forward/backward/pendulum, chord recording, transpose (Prophet Rev4 firmware-mod-style) |
| Layer | ABSOLUTE — the whole piece's chordal texture is re-voiced as one flowing arpeggio line |
| Recent excluded (7d) | SP-006, SP-028, SP-032, SP-092, SP-099, SP-105, SP-111 |
| Already on source | (none) |
| Baseline excluded | SP-001 |
| Pool size | 47 |
| Well-formed candidates | 245 / 357 |

**Source composition:** `Styles/Experimental/059-genetic-chorale/MIDI/059-genetic-chorale.mid`
- 8-bar homophonic SATB chorale, **G natural minor** (i–iv–v–i–iv–v–iv–i), **88 BPM**, 4/4, TPB 480, **8 bars** = 15360 ticks = 21.8 s.
- 4 voices: Soprano (ch0, prog 74), Alto (ch1, prog 74), Tenor (ch2, prog 74), Bass (ch3, prog 33). 32 pitched notes (8 per voice, whole notes).
- Progression: Gm · Cm · Dm · Gm · Cm · Dm · Cm · Gm.

## PRE-FLIGHT AUDIT (3-rule gate)

| Rule | Count (before) | Count (after) | Verdict |
|---|---|---|---|
| Grid sync (16th = 120 ticks) | 0 off-grid | 0 | PASS |
| Harmony — in scale (G natural minor {7,9,10,0,2,3,5}) | 0 out-of-scale | 0 | PASS |
| Harmony — chord tone per bar | **1 out-of-chord** | 0 | FAIL → reworked |
| Zero-drift (note tracks equal length) | [15360] all equal | [15360] | PASS |

**Harmony finding + rework.** Tenor bar 1 plays note **48 (C3)** — pitch class C, the
perfect 4th of the bar's Gm triad (chord tones {G, Bb, D}), so it is a non-chord
tone. (The project README labels it "D3", i.e. note 50, so this is a transcription
slip in the original generator.) Fixed `rework`: snap Tenor bar 1 note 48 → **50 (D3)**
— the documented intent and a chord tone of Gm. **No other note moved; no duration or
onset changed.** Source preserved byte-for-byte as `MIDI/source_original.mid`; humanized
original kept as `MIDI/059-genetic-chorale-phase1.mid`.

**Re-audit after rework:** off-grid 0, out-of-scale 0, out-of-chord 0, zero-drift PASS.
Written to `MIDI/composition.mid`.

## Layer discipline (absolute)

SP-108 is an **absolute-layer** generator: the entire chorale's block-chord texture is
collapsed into a single flowing arpeggio line. Per-bar 4-note chords (from the reworked
source) are fed to the `Arpeggiator`; it emits a 16th-note arpeggio across 2 octaves,
up/down mode. The note stream is written as a new MIDI (`SP108-arp.mid`) and rendered
through a FluidSynth carrier (SP-001, piano program 0) → `master()` → WAV + Opus OGG.

| Param | Value |
|---|---|
| `mode` | `updown` |
| `octave_range` | 2 |
| `division` / step | `1/16` → 120 ticks (16 steps/bar × 8 bars = 128 events) |
| `gate` | 0.8 (ArpStep default — detached 16th onsets) |
| per-bar reset | `_step_index = 0` at each bar (consistent up-down from chord) |
| carrier | FluidSynth, program 0 (acoustic grand piano) |
| Mastering | `master()` → LUFS −14.0 (`target_for_style("experimental")`), ceiling −1 dBTP |

## Verification

| Metric | Value | Verdict |
|---|---|---|
| Pitch (FFT dominant peak / 0.5 s window, 50–1000 Hz) | **hit 1.000** (45/45 valid windows) | PASS |
| Harmonic energy (first 8 harmonics of dom. peak) | **0.5798** wet / 0.5789 dry (retention 1.002) | PASS (≥ 0.30) |
| Arp pitch classes | {0, 2, 3, 5, 7, 9, 10} ⊆ G natural minor | PASS |
| Silence ratio | **11.14%** (release tail + inter-onset gaps) | PASS (< 30%) |
| RMS | 0.1084 | — |
| Integrated LUFS | −14.00 | on target |
| True peak | −3.04 dBTP | below −1 ceiling (correct — ceiling is a cap, not a target) |
| Zero-drift (arp MIDI) | single note track spans exactly 15360 ticks | PASS |

Per-second RMS map (first 12 s): `[0.1084, 0.1115, 0.1132, 0.1101, 0.1088, 0.1124,
0.1110, 0.1097, 0.1109, 0.1118, 0.1093, 0.1101]` — even, no mid-track gaps; tail-only
silence after the final arp note.

## Files

| Path | Size | Role |
|---|---|---|
| `SP108-poly-arp-seq-059-genetic-chorale.wav` | 4 355 116 B | mastered full mix (stereo 44.1 kHz) |
| `SP108-poly-arp-seq-059-genetic-chorale.ogg` | 198 245 B | Opus 48k voip (delivery) |
| `SP108_arp_raw.wav` | 4 355 116 B | pre-master SP-108 render |
| `dry_full_mix_chorale_reference.wav` | 4 249 900 B | dry reworked chorale (pre-arpeggiation reference) |
| `MIDI/SP108-arp.mid` | 1 081 B | arpeggiated note stream |
| `MIDI/composition.mid` | — | reworked (zero-drift normalized) source |
| `MIDI/source_original.mid` | — | byte copy of original source |
| `MIDI/059-genetic-chorale-phase1.mid` | — | original pre-rework sidecar |
| `Audio/stems/track00_Recorder.wav` … `track03_Electric_Bass_finger.wav` | 4.2 MB ea | dry per-track stems (DAW import) |
| `provenance.json`, `Analysis/render_stats.json`, `Analysis/rework_audit.json` | — | records |

Stem label note: flute program 74 renders as `track0X_Recorder` and bass program 33 as
`track03_Electric_Bass_finger` under FluidR3_GM (verified 2026-09-10 stem-label table).

## Verdict

SP-108 applied as an absolute-layer arpeggiation of an 8-bar G-minor chorale. One
pre-flight harmony violation (non-chord Tenor C3 in bar 1) fixed to D3 before the
production pass; re-audit all-0. Render pitches verify clean (FFT hit 1.000, harmonic
energy 0.58), silence 11.1%, mastered to −14 LUFS / −3.04 dBTP.
