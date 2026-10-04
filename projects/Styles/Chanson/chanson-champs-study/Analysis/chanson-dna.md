# Chanson Française — Composition Study

"Champs-Élysées"-style 1960s French pop. A focused study of what makes Chanson
Française / Variété sound the way it does, encoded as inspectable DNA.

## Style DNA → composition mapping

| Chanson trait (from brief) | Where it lives in this piece |
|---|---|
| Narrative, singable lyricism | Conjunct, stepwise trumpet melody (verse moves mostly by 2nd/3rd) |
| Buoyant march-like 4/4 | 126 BPM; kick on 1&3, snare backbeat on 2&4 |
| Musette / cabaret texture | Accordion (GM 21) sustained triad bed |
| Strummed acoustic guitar | 8th-note chord-tone strum (GM 25) |
| Light brass hook | Trumpet (GM 56) lead, upper register |
| Swinging strings | String ensemble (GM 49) sustained an octave up, swells into chorus |
| Catchy sing-along chorus | Chorus hook contour `5-6-5-3 | 3-4-3-1` (G-A-G-E …) |
| Lush mid-century arrangement | Upright oom-pah bass (GM 32) root→fifth march |

## Harmony & form

- Key **C major**, tempo **126 BPM**, 4/4.
- Verse: **I – V – vi – IV** (the chanson/pop workhorse).
- Chorus: **I – V – vi – IV | I – V – I – I** (resolves on tonic = the sing-along "amen" feel).
- Form: Intro (4) – Verse (8) – Chorus (8) – Verse (8) – Chorus (8) – Outro (4) = 40 bars.

## What to listen for

1. **The strut** — the oom-pah bass + kick-on-1&3 gives the walking Paris street feel.
2. **The accordion wash** — the harmonic bed is the musette signature; without it, it's just pop.
3. **The chorus lift** — strings swell + the trumpet climbs to the `5-6-5-3` hook; the melody rises above the verse register.
4. **The resolve** — the chorus ends on two bars of I (C), the "everyone sings along" landing.

## Verification (real numbers)

- `analyze_midi` → key **C major**, 1344 notes, 76.2 s, Forte **3-11** (diatonic triads).
- Progression detected: `I-V-vi-IV … I-V-I` per section (matches the plan).
- Density: accordion 100% · strings 100% · lead 90% · guitar 83% · bass 83% · drums 46%.
- WAV: peak 0.906, RMS 0.149, **silence 7.7%** (continuous flow — no sparse/staccato gaps).
- FFT dominant peaks 97/132/148 Hz = bass G2/C3/D3 fundamentals (tonal, not noise).

## Files

- `compose.py` — the generator (engine-native, zero-drift).
- `MIDI/chanson-champs-study.mid` — editable DAW source.
- `Audio/chanson-champs-study.ogg` — Opus render (FluidSynth, gain 1.2).
- `Analysis/grid_visualization.txt` — high-contrast █/░ timeline.
- `Analysis/verify.py` — the verification script (re-runnable).
