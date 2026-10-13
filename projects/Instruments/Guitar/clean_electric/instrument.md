---
type: instrument
family: Guitar
name: Clean Electric Guitar
midi_program: 27
gms: "Electric Guitar (clean)"
range_min: 28
range_max: 84
solo_range: [43, 76]
role: [harmony, rhythm, strum, lead, melody, ornament, countermelody]
synthesis: [karplus-strong, modal, phase-mod]
---

# Clean Electric Guitar

## MIDI / GM

- **Program**: 27 (GM1 Electric Guitar clean — solidbody electric guitar, clean/undistorted tone)
- **Channel**: any melodic channel; polyphonic (6 strings, but electric idiom is chord-based)
- **Pipeline stem label**: `GM_PROGRAMS[27] = "Electric Guitar (clean)"` → `trackXX_Electric_Guitar_clean.wav`
- **FluidR3 SF2 preset**: 27 = "Clean Guitar" (cosmetic SF2 name difference, no routing impact)

## Range

| Zone | MIDI | Pitches | Register |
|------|------|---------|----------|
| Full range | 28–84 | E1–C6 (GM patch span; real 22-fret guitar = E2–E6 = 40–76) |
| Low strings | 28–45 | E1–A2 — bass/fundamental zone: open-string roots, palm-muted chugs |
| Middle | 46–64 | A#2–E4 — midrange neck pickups: warm chords, neck-pickup leads |
| High | 65–84 | F4–C6 — bright bridge-pickup: cutting single-note lines, treble-rich chords |

The GM patch plays the whole 28–84 span (empirical FluidR3 sweep confirms full audibility, no gaps). Idiomatic writing zone is 40–76 (E2–E6, the real 22-fret neck).

## Timbre DNA

Clean electric guitar is defined by the **magnetic pickup** — the string's ferrous metal core vibrating in a magnetic field induces a voltage. The pickup acts as a **bandpass filter** (typically 80 Hz – 5 kHz), rolling off both the lowest fundamental (E1=41 Hz is ~6 dB down on a standard 6.4" single-coil) and the highest harmonic string shimmer. The body is a passive resonator that adds ~200–500 Hz box resonance; amplified to an amp, the speaker adds its own colour.

In the ideal:
- **Low E string (E2=82 Hz)**: full fundamental, ~50–150 Hz warmth
- **A string (A2=110 Hz)**: clear dominant fundamental, rich body
- **D string (D3=147 Hz)**: balanced warmth/clarity — the centre of the neck pickup's range
- **G string (G3=196 Hz)**: midrange attack — the "quack" zone of 2/4 position on a Stratocaster
- **B string (B3=247 Hz)**: bright region — chorus works best here
- **High E string (E4=330 Hz)**: sparkle with lower body — single-coil click articulation

Pick type:
- **Fingertip**: warm, round, mellow (Jazz, R&B)
- **Plectrum (pick)**: bright attack, cutting transient, thinner sustain — the default electric guitar sound
- **Palm mute**: short percussive chunk (rhythm chug, funk strum)

Pickup switch:
- **Neck**: dark, round, warm — jazz leads and mellow chords
- **Middle (2/4 on Strat)**: hollow quack — funk comping, clean rhythm
- **Bridge**: bright, thin, sharp — twang/country leads, surf

## Articulations

| Technique | Velocity | Duration factor | Description |
|-----------|----------|----------------|-------------|
| pick_down | 80 | 0.20 | Standard downstroke with plectrum — bright attack 
| pick_up | 70 | 0.18 | Upstroke — lighter, less percussive
| finger | 65 | 1.0 | Fingertip pluck — warm round tone (jazz, R&B)
| palm_mute | 50 | 0.12 | Edge-of-hand damped — percussive chug
| strum_down | 78 | 0.22 | Multi-string downstroke — chord rhythm
| strum_up | 68 | 0.18 | Multi-string upstroke — lighter chord accent
| hammer_on | 75 | 0.5 | Legato slur up — connecting note without picking
| pull_off | 65 | 0.5 | Legato slur down — connecting note without picking
| slide | 72 | 0.8 | Continuous pitch glide — finger drag
| bend | 82 | 0.9 | String bend — pitch rise, sustain increases
| vibrato | 70 | 0.9 | Whammy bar or finger vibrato — pitch modulation
| harmonic | 90 | 0.35 | Natural/artificial overtone — bell-like chime
| arpeggio | 62 | 0.15 | Fingerpicked rolled chord — fluid texture
| muted_attack | 95 | 0.08 | **ch.** — pick stops on string: percussive, no pitch (ghost note)
| accent | 96 | 0.20 | Emphatic hard pick dig — cutting downbeat

## Synthesis

### Primary: Karplus-Strong (sound/synthesis/karplus_strong.py)

Clean electric guitar IS a plucked stiff steel string — Karplus-Strong is the exact physical model (waveguide loop with lowpass filter damping). Parameters:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| loop_gain | 0.9960 | Steel strings ring 1–3 s; between clavi 0.9960 and steel_acoustic 0.9970 |
| excitation | "pick" | Bright hard attack from plectrum — noise_component 0.025 for pick transient |
| lowpass_hz | 5000 | Magnetic pickup bandpass — strings have energy to 8 kHz, pickup rolls off |
| noise_component | 0.025 | Pick click/scrape on wound strings — the "tik" attack transient |
| width | 0.60 | Moderate pulse width (stiffer than nylon = brighter) |

### Secondary: ModalSynth (sound/synthesis/modal.py)

Stock 'string' preset with IR drop — clean electric is a string, but the pickup/enclosure colour needs custom damping:

| Parameter | Value |
|-----------|-------|
| preset | "string" |
| excitation | "impulse" |
| decay_rates | [6, 12, 18, 25, 35] — slightly brighter than classical guitar |

### Tertiary: PhaseModSynth (sound/synthesis/phase_mod.py — SP-012)

FM synth approximation — a saw carrier through a resonant bandpass that mimics the pickup rolloff:

| Parameter | Value |
|-----------|-------|
| carrier_shape | saw (even+odd harmonics) |
| mod_freq_ratio | 1.0 (octave doubling) |
| mod_depth | 2.0 — moderate FM twang |
| attack | 0.005 s — fast pick transient |
| release | 0.20 s — short damping |

## Production defaults

| Parameter | Value | Notes |
|-----------|-------|-------|
| REVERB_TAIL | 1.8 s | Room/spring reverb — clean electric typically uses amp spring reverb (Fender outboard tank ~2.0 s decay character) |
| EQ_BODY | (300, -3.0) | Peaking cut at 300 Hz — reduce box resonance from the solidbody |
| EQ_PRESENCE | (3500, 2.5) | Peaking boost at 3.5 kHz — pick attack, fret noise, pickup "quack" |
| EQ_AIR | (8000, 1.5) | High shelf at 8 kHz — gentle string shimmer, NOT the harsh presence of a DI |
| PAN | -0.2 | Centre-left for a standard mono stage amp; stereo double has the other at +0.2 |

## RenderPipeline stem-label quirk

**No quirk.** `GM_PROGRAMS[27] = "Electric Guitar (clean)"` → sanitized filename `Electric_Guitar_clean`. FluidR3 preset 27 = "Clean Guitar" (internal SF2 name differs cosmetically — pipeline label and stem-file label both use `Electric_Guitar_clean`, no routing impact). STEM_LABEL = "Electric_Guitar_clean".

## FluidSynth / SF2 notes

FluidR3_GM.sf2 preset 27 = "Clean Guitar" (a Roland JC-120 style clean electric guitar sample set, picked articulation). The patch is audible across the full 28–84 range with no gaps. Below 28 (C1), the patch plays the lowest sample looped — write root notes of chords > 40 for idiomatic timbre. The SF2 preset has natural velocity crossfading — use velocities 60–100 for typical clean rhythm articulation; velocities > 110 trigger the amp breakup sample layer (slight natural overdrive from the SF2 volume envelope — NOT true distortion, but a forced-velocity brighter layer).

## Identity

GM 27 = Clean electric guitar — a solidbody electric guitar played through a clean amplifier (no distortion/overdrive). The archetypal sounds: Fender Stratocaster neck pickup → Fender Twin Reverb (smooth jazz/surf), Gibson Les Paul bridge pickup → Vox AC30 (jangly rock/country), Fender Telecaster bridge pickup → Fender Deluxe Reverb (twang/country).

The clean electric is a **fully polyphonic chord/strum/arpeggio instrument** — the most common rhythm-section chord voice after the acoustic guitar. Idiomatic textures: open-position cowboy chords, barre-chord rhythm comping, fingerpicked arpeggios, single-note picked leads (monophonic in the lead register, double-stops and chords in rhythm register).

Line-instrument quirks:
- NOT a sustain voice — clean electric notes decay naturally (1–3 s). Write rhythmic patterns, not tied whole notes.
- Palm-muted rhythm is the #1 identity (eighth-note chugs, reggae skank, funk scratch).
- Single-coil pickups hum at 50/60 Hz — in a dense mix this is a non-issue; in solo passages it adds character. The SF2 sample set has no hum, being a direct recorded sample.
- The default MIDI patch is "pick articulation" — write arpeggios and chord strokes, not long sustained lines.