# REPORT — SP-115 Chord-Driven Generative Arranger on 262-harmonic-chorale-variations

**Date:** 2026-10-31 · **Job:** random-style production (SP methods) — LAYER-ALIGNED · **Status:** complete + verified

## 1. Selection

| Field | Value |
|---|---|
| **Method** | `SP-115` → `sound.generators.chord_arranger` |
| **Method desc** | Chord-Driven 3-Track Generative Arranger (Midicake UNA-style) |
| **Registry source** | `workflows.musicom_workflow.SP_METHODS` (implemented registry, 72 entries) |
| **Source composition** | `Styles/Experimental/262-harmonic-chorale-variations` |
| **Selected MIDI (selector pick)** | `MIDI/262-harmonic-chorale-variations-humanized.mid` |
| **Production source (grid-locked)** | `MIDI/262-harmonic-chorale-variations-perfect.mid` |
| **Seed** | 20261031 |
| **Selection pool** | 65 methods (72 − 7 excluded: 6 recent 7-day + SP-001 baseline) |
| **Recent excluded** | SP-078, SP-092, SP-094, SP-109, SP-119, SP-127 |

## 2. Source identity (preserved)

F major (ionian) · 92 BPM · 4/4 · 480 TPB · **24 bars** (46080 ticks) · SATB
chorale (Soprano Flute 73 / Alto Strings 48 / Tenor Cello 42 / Bass Contrabass
43). Harmony per 4-bar section: `I–vi–IV–V` · `V–IV–vi–I` · `V–I–ii–V` ·
`IV–ii–V–I` · `I–IV–ii–V` · `IV–V–I–I`. F-major pitch-class set
`{0,2,4,5,7,9,10}` (C D E F G A B♭).

The 24-bar chord plan (root MIDI / quality) fed to the arranger was derived
from the documented per-section harmony and **cross-checked against the
source's beat-1 voicing** (per-bar lowest note + pitch-class set) — exact
match:

```
A: F(53) Dm(50) Bb(58) C(60)   B: C(60) Bb(58) Dm(50) F(53)
C: C(60) F(53)  Gm(55) C(60)   D: Bb(58) Gm(55) C(60)  F(53)
E: F(53) Bb(58) Gm(55) C(60)   F: Bb(58) C(60)  F(53)  F(53)
```

## 3. Pre-flight rules adherence gate (source composition)

Three-rule audit on the source. **No rework required** — the source passed all
three on the grid-locked perfect layer.

| Version | tracks | voice len | notes | off-grid | out-of-scale | out-of-chord | zero-drift |
|---|---|---|---|---|---|---|---|
| **perfect** (production source) | 4 | 46080 | 215 | **0** | **0** | **0** | ✓ (all 46080) |
| humanized (selector pick) | 4 | 46080 | 215 | 182 (>0 ✓) | 0 | 17* | ✓ (all 46080) |

\* The 17 humanized "out-of-chord" hits are bar-boundary whole-note onsets
shifted a few ticks back by humanization → a `t//BAR` attribution artifact,
NOT a pitch problem (out-of-scale stays 0; the humanizer never moves pitch).
The authoritative gate is the grid-locked perfect layer: **0 / 0 / 0**.

**Verdict: PASS all three. No composition rework needed.**

## 4. SP-115 layer application (ABSOLUTE)

The whole production layer is replaced by a **chord-driven 3-track generative
arrangement** — chord/rhythm pad (String Ensemble 48, ch0), arpeggiated melody
(Flute 73, ch1), harmony-following bass (Contrabass 43, ch2) — generated from
the source's 24-bar F-major chord plan. Pure MIDI-event level (no audio DSP).

`ChordDrivenArranger(bpm=92, bars=24, seed=20261031).generate(chords, macros)`
→ **1417 events**: chord 999 · melody 217 · bass 201.

**8 macro knobs** (chorale-appropriate — straight, legato, no ratchets/octave):

| macro | value | macro | value |
|---|---|---|---|
| density | 0.5 | ratchet | 0.0 |
| probability | 0.7 | octave | 0.0 |
| swing | 0.0 | gate | 0.6 |
| accent | 0.4 | spread | 0.3 |

Pattern tools active: euclidean-mask chord rhythm (10/16 pulses), random
block/strum/euclid/drone chord kinds per bar, arp up/down/updown/random,
root±fifth bass walk, 16-step probability/velocity/gate/octave lanes (seeded).

## 5. MIDI serialization

Arrangement written as a 4-track MIDI (conductor tempo 92 BPM + 3 note
tracks). Program changes are placed **in each note track** (not only the
conductor) so per-track stem renders get the correct GM timbre. Every note
clamped to the 46080-tick span (no seam crossing) → **zero-drift: all three
note tracks = 46080 ticks**.

## 6. Render + master

FluidSynth (FluidR3_GM.sf2, `-ni -R 0 -C 0 -g 1.2`) → dry WAV → `master()` to
`target_for_style("Experimental")` = **−14 LUFS** (genre fallback), ceiling
**−1 dBTP** → Opus OGG.

| metric | value |
|---|---|
| LUFS | **−14.06** |
| true peak | **−1.00 dBTP** |
| peak | 0.8913 |
| RMS | 0.1211 |
| silence ratio | **5.24 %** |
| duration | 65.0 s (24 bars @ 92 BPM = 62.6 s + release tail) |

## 7. Pitch verification (mandatory, post-synthesis)

FFT dominant-peak per 0.5 s window (50–1000 Hz) vs F-major pitch classes, +
harmonic-energy ratio (8 harmonics of lowest fundamental).

| layer | hit rate | mean harmonic energy | windows |
|---|---|---|---|
| wet (mastered) | **0.9921** | **0.4934** | 128 |
| dry (pre-master) | 0.9921 | 0.4906 | 128 |

**Verdict: PASS** (hit ≥ 0.60 AND HE ≥ 0.30). Tonal, in-key, not noise.

Arrangement MIDI self-audit: grid 0 · out-of-scale 0 · out-of-chord 0 ·
zero-drift ✓ · 1417 notes · pitch classes `{0,2,4,5,7,9,10}` (exactly F major).

## 8. Fixes applied (this job's pipeline, not the source)

1. **Note-seam clamp** — first pass left one note track ending at 46219 ticks
   (a bar-boundary note overran the 46080 span). Clamped every note to the
   span → zero-drift now `[46080]` on all three tracks.
2. **Stem program placement** — program changes originally sat only in the
   conductor track, so `render_stems` labeled/rendered all three stems as
   `Acoustic_Grand_Piano` (program 0). Moved program changes into each note
   track → stems now `track00_String_Ensemble_1` / `track01_Flute` /
   `track02_Contrabass`, correct timbre.

## 9. Files

```
SP115-chord-arranger-262-harmonic-chorale-variations.wav   11,464,492 B  (mastered)
SP115-chord-arranger-262-harmonic-chorale-variations.ogg      434,226 B  (Opus 48k)
dry_sp115_arrangement.wav                                   11,464,492 B  (pre-master reference)
MIDI/SP115-arrangement.mid                                      9,782 B  (3-track generative arrangement)
MIDI/source_perfect.mid                                         2,004 B  (copies)
MIDI/source_humanized.mid                                      1,906 B
Audio/stems/track00_String_Ensemble_1.wav                  11,397,420 B  (chord pad)
Audio/stems/track01_Flute.wav                              11,464,492 B  (arp melody)
Audio/stems/track02_Contrabass.wav                         11,461,420 B  (bass)
Analysis/render_stats.json
provenance.json
Scripts/produce_sp115_cron.py
```

## 10. What to listen for

The source's SATB overtone chorale is re-cast as a **generative pad + arp +
bass arrangement**: the string-ensemble chord pad carries the `I–vi–IV–V`
harmonic drift (block/strum/euclid/drone texture varies bar to bar), the flute
arpeline weaves the chord tones, and the contrabass roots the changes. Straight
time (no swing), legato gate, moderate density — a calm, evolving 65 s chorale
rather than the source's held block chords.
