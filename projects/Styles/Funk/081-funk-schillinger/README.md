# 081-funk-schillinger

**Style:** Funk · **Method:** 018 Schillinger System of Musical Design (resultant a=5, b=3)
**Date (UTC):** 2026-08-29 · **Key:** Bb major · **Tempo:** 100 BPM · **Form:** Intro / Verse / Chorus / Verse2 / Chorus2 / Outro (6 × 4 bars = 24 bars)

## Concept

A funk study built from Joseph Schillinger's rhythmic interference system. Two periodic
generators (a=5, b=3) interfere into a resultant duration pattern — the raw rhythmic DNA —
which drives the lead melody. Phase 2 locks it to the grid, quantizes every pitch to the
bar's chord, and wraps it in a classic funk texture: trumpet lead, Rhodes comp, wah guitar
stabs, octave bass pulse, clavinet horn stabs, backbeat drums.

## Two-Phase Architecture

- **Phase 1** (`MIDI/081-funk-schillinger-phase1.mid`): raw Schillinger resultant walk —
  single voice (trumpet), fractional tick durations (off-grid by design), raw sine-projection
  pitches + register drift, NO harmony.
- **Phase 2** (`MIDI/081-funk-schillinger.mid`): 16th-grid lock (120 ticks @ 100 BPM),
  scale + chord-tone quantization per bar (global bar lookup), leap cap ≤ 9 st, voice-leading
  check (rules.voice_leading), full 6-voice funk arrangement.

## Progression (24 bars, Bb major)

```
I ii iii V | I ii iii V | I IV V I | I V I ii | I ii iii V | I IV ii I
Bb Cm Dm F  | Bb Cm Dm F  | Bb Eb F Bb | Bb F Bb Cm | Bb Cm Dm F  | Bb Eb Cm Bb
```

## Voices

| # | Voice | GM | Role |
|---|-------|----|------|
| 0 | Lead | 56 Trumpet | Schillinger resultant lead, chord tones |
| 1 | Rhodes | 4 | Comp: 3rd/5th 8th rhythm |
| 2 | Guitar | 27 | Offbeat wah stabs (2&, 3&, 4&), 1& push in choruses |
| 3 | Bass | 33 | Root/fifth octave pulse, 16th push in choruses |
| 4 | Clav | 7 | Horn stabs in choruses (chord tones +24) |
| 5 | Drums | ch9 | Kick 1&3, snare 2&4, hats 8ths, claps + ride in choruses |

## Verification

- Grid audit: **0 off-grid** (16th/8th) on all 6 voices
- Harmony audit: **0 out-of-scale, 0 out-of-chord** on all pitched voices
- Zero-drift: validate() OK on both phases
- Audio: silence 5.5%, RMS steady 0.07–0.13, FFT tonal 120/120 windows

## Files

```
MIDI/081-funk-schillinger.mid            (+ .provenance.json)
MIDI/081-funk-schillinger-phase1.mid     (+ .provenance.json)
Audio/081-funk-schillinger.wav/.ogg      (+ provenance)
Audio/081-funk-schillinger-phase1.wav/.ogg (+ provenance)
Analysis/grid_visualization.txt
Analysis/audit.json
Analysis/summary.json
Analysis/render_stats.json
compose.py / audit.py / audio_stats.py / audio_provenance.py
REPORT.md
```
