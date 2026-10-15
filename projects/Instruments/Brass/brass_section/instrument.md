---
type: instrument
family: Brass
name: Brass Section
midi_program: 61
gms: "Brass Section"
range_min: 36
range_max: 96
solo_range: [48, 84]
role: [lead, accent, fanfare, counter, harmony, pad]
synthesis: [phase-mod, additive]
---

# Brass Section

## MIDI / GM

- **Program**: 61 (GM1 Brass Section — the full brass ensemble patch: trumpets, trombones, french horns optionally, tutti)
- **Channel**: any melodic channel; polyphonic
- **Pipeline stem label**: `GM_PROGRAMS[61] = "Brass Section"` → `trackXX_Brass_Section.wav`
- **FluidR3 SF2 preset**: 61 = "Brass Section" (same label)

## Range

| Zone | MIDI | Pitches | Register |
|------|------|--------|----------|
| Full range | 36–96 | C2–C7 (GM patch span) |
| Low brass | 36–55 | C2–G3 — ensemble bass: trombones + tuba in octaves, heavy pedal tones |
| Middle | 56–71 | B3–C5 — the tutti horn call zone: brass fanfares and sustained harmony |
| High | 72–84 | C5–C6 — piercing trumpet-dominant lead: fanfare top line, orchestral punch |
| Top extension | 85–96 | C6–C7 — thin ensemble scream, upper trumpet register |

The GM patch plays the whole 36–96 span. The idiomatic writing zone is 48–84 (C3–C6), where the ensemble has the richest harmonic blend.

## Timbre DNA

Brass Section (GM61) is the **full brass ensemble** — trumpets, trombones, and sometimes french horns or tuba playing together as a single patch on a single MIDI channel. The timbre is defined by the aggregate of multiple brass instruments:

- **Trumpets** dominate the upper register (C4–C6): bright, piercing, with a strong 6th–8th harmonic presence
- **Trombones** fill the middle (C3–C4): warm, weighty, with the characteristic brass buzz
- **Tuba/Horn** ground the bottom (C2–C3): deep, mellow, with a broad fundamental wave

The **ensemble compression** is baked into the FluidR3 sample — when the MIDI patch sounds a chord, each note is a pre-recorded multi-instrument sample. No intermodulation occurs because the samples are already mixed at the recording stage.

| Parameter | Solo Brass | Brass Section |
|-----------|-----------|--------------:|
| Timbre | Single instrument | Aggregate ensemble (3–5 players) |
| Dynamic range | ~35 dB | ~20 dB (pre-compressed) |
| Harmonic content | Instrument-specific | Stacked brass harmonics: rich 3rd–8th partials |
| Attack | Fast (0.02–0.05 s) | Slightly slower (0.04–0.08 s) — ensemble attack phase |
| Reverb | Depends on room | Deep hall, sampled wet |

## Arrangement roles

- **Lead/fanfare**: The iconic use — tutti brass fanfares, orchestral stabs, cinematic punches (think Star Wars main title, Olympic fanfares)
- **Harmony/pad**: Sustained brass chords behind a melody — warm, rich, stately (Aaron Copland, John Williams)
- **Countermelody**: The brass chorus against strings or woodwinds — big, confident secondary lines
- **Accent**: Sharp sforzando hits for dramatic punctuation

DO NOT use for:
- Solo lines (use individual trumpet/trombone/french_horn/horn patches)
- Muted effects (no individual mutes)
- Very fast passagework (the ensemble attacks are slightly smeared)

## Articulations

| Articulation | Velocity | Duration factor |
|---|---|---|
| sustain | 82 | 1.0 |
| fanfare_stab | 92 | 0.40 |
| marcato | 85 | 0.65 |
| accent | 98 | 0.30 |
| staccato | 70 | 0.20 |
| sfz | 100 | 0.25 |
| swell | 72 | 1.20 |
| sfp | 65 | 1.10 |

## Synthesis engine recommendation

**PhaseModSynth** primary (sound/synthesis/phase_mod.py):

The brass section is a sustained multi-brass ensemble. PhaseModSynth with a saw carrier (rich in odd+even harmonics) and a moderate modulator depth captures the stacked brass harmonic content.

```python
carrier_shape = "saw"       # Rich harmonics for brass ensemble
mod_shape = "sine"
mod_freq_ratio = 1.0        # Fundamental emphasis
mod_depth = 2.8             # Between french_horn (2.5) and muted_trumpet (3.5)
attack = 0.06               # Ensemble attack, not too fast
release = 0.30              # Medium release for brass resonance
```

**Additive** fallback — stack brass-appropriate harmonics 1.0, 0.85, 0.65, 0.50, 0.35, 0.20, 0.12, 0.08

## Production defaults

| Parameter | Value | Notes |
|-----------|-------|-------|
| Reverb tail | 2.5 s | Concert hall — brass needs more tail than woodwinds |
| EQ body | (250 Hz, -3.0 dB) | Cut 250 Hz — reduce low-mid mud from stacked brass |
| EQ presence | (2500 Hz, 3.5 dB) | Boost 2.5 kHz — brass edge and projection |
| EQ air | (8000 Hz, 1.0 dB) | Gentle top shelf — open the ensemble |
| Pan | -0.25 | Centre-left (brass sits stage-left in orchestra) |

## FluidSynth / SF2 behavior

- GM preset 61 = "Brass Section" in both FluidR3 and GM_PROGRAMS — labels match exactly, no quirk
- Empirical behavior: the patch covers the full 36–96 range
- The ensemble sample has a richer sound in the 48–84 range; extremes are thinner but usable
- Polyphony is well handled — the patch stacks well for 3–5 note chords
- Channel quirk: must use a melodic channel (0–9) with program 61 — channel 9 triggers the drum-kit map

## Stem label

`trackXX_Brass_Section.wav` — `GM_PROGRAMS[61] = "Brass Section"`; FluidR3 preset 61 = "Brass Section"; labels match exactly, **no quirk**.