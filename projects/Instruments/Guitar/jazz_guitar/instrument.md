---
type: instrument
family: Guitar
name: Jazz Guitar
midi_program: 26
gms: "Electric Guitar (jazz)"
range_min: 28
range_max: 84
solo_range: [43, 76]
role: [harmony, rhythm, comp, lead, melody, ornament, countermelody]
synthesis: [karplus-strong, modal, phase-mod]
---

# Jazz Guitar

## MIDI / GM

- **Program**: 26 (GM1 Electric Guitar (jazz) — archtop hollow-body electric guitar, warm/round tone)
- **Channel**: any melodic channel; polyphonic (6 strings, but jazz idiom is comping + single-line)
- **Pipeline stem label**: `GM_PROGRAMS[26] = "Electric Guitar (jazz)"` → `trackXX_Electric_Guitar_jazz.wav`
- **FluidR3 SF2 preset**: 26 = "Jazz Guitar" (SF2 uses the common name; pipeline uses the GM2 spec spelling — cosmetic only, **no routing impact**)

## Range

| Zone | MIDI | Pitches | Register |
|------|------|---------|----------|
| Full range | 28–84 | E1–C6 (GM patch span; real 22-fret guitar = E2–E6 = 40–76) |
| Low strings | 28–47 | E1–B2 — bass/fundamental zone: low roots, bass-note comping, walk-downs |
| Middle | 48–64 | C3–E4 — **THE jazz zone**: comping chords, shell voicings, thumb melodies |
| High | 65–84 | F4–C6 — bright bridge-pickup: octave melodies, single-note fills, block-chord tops |

The GM patch plays the whole 28–84 span (empirical FluidR3 sweep confirms full audibility, no gaps). Idiomatic writing zone is 40–76 (E2–E6, the real 22-fret neck); the classic jazz registers sit in the mid zone 48–72 (C3–C5).

## Timbre DNA

The jazz guitar is defined by **three choices working together** — archtop hollow body, flatwound strings, and the **thumb** attack:

- **Archtop hollow body**: the carved spruce top + f-holes act as an acoustic resonator first; the pickup amplifies that acoustic voice. The body adds ~200–300 Hz box warmth and absorbs the extreme highs — the tone is round and woody, never glassy.
- **Flatwound strings**: wound-flat steel (no round grooves) — dramatically less finger/pick noise and a darker, smoother harmonic top than roundwounds. Notes ring long (2–4 s) with a *smooth* decay, no zing.
- **Thumb attack** (Wes Montgomery's signature): the fleshy thumb strikes the string with a round, soft transient — no pick click, no bright scrape. The attack is the roundest of any guitar timbre; the note seems to *bloom* rather than *speak*.
- **Pickup**: usually a single neck-position humbucker or floating pickup — a dark bandpass (energy concentrated below ~3.5 kHz), the opposite of the clean-electric Stratocaster quack.

In the ideal:
- **Low E string (E2=82 Hz)**: full fundamental, dark woody thump
- **A string (A2=110 Hz)**: warm fundamental, the comping root zone
- **D string (D3=147 Hz)**: balanced warmth/clarity — the centre of the neck pickup
- **G string (G3=196 Hz)**: the vocal register — thumb melodies live here
- **B string (B3=247 Hz)**: bright region — octave-melody top notes
- **High E string (E4=330 Hz)**: sweet sparkle with no harshness — block-chord tops

Attack type:
- **Thumb**: round, warm, vocal — the default jazz guitar sound
- **Fingertip**: similar but lighter
- **Pick**: brighter attack, thinner tone — jazz-fusion edge (Metheny, Benson), still darker than a solidbody clean

## Articulations

| Technique | Velocity | Duration factor | Description |
|-----------|----------|----------------|-------------|
| thumb | 75 | 0.9 | Fleshy thumb stroke — the Wes Montgomery signature: round, warm, no pick click, full ring |
| pick | 72 | 0.35 | Plectrum — brighter attack, thinner tone (jazz-fusion) |
| finger | 65 | 1.0 | Fingertip pluck — warm, round, mellow |
| comp_chord | 60 | 0.25 | Freddie Green-style rhythm comp — short, percussive chord strokes on beats 2 & 4 |
| shell_voicing | 55 | 0.5 | 3-note shell chord (root-7th-3rd) — light, breathable comping, the jazz default |
| octave | 72 | 0.6 | Wes-style doubled octave melody — the classic jazz guitar lead texture |
| hammer_on | 72 | 0.5 | Legato slur up — connecting note without picking |
| pull_off | 62 | 0.5 | Legato slur down — connecting note without picking |
| slide | 70 | 0.8 | Continuous pitch glide — finger drag |
| bend | 80 | 0.9 | String bend — pitch rise, bluesy edge (jazz-blues) |
| vibrato | 68 | 0.9 | Finger vibrato — the vocal-like sustain that IS the jazz guitar lead sound |
| arpeggio | 62 | 0.3 | Fingerpicked rolled chord — fluid texture |
| ghost_note | 42 | 0.08 | Muted scratch — no defined pitch, rhythm texture |
| accent | 92 | 0.30 | Hard dig — cutting chord hit or lead peak |

## Synthesis

### Primary: Karplus-Strong (sound/synthesis/karplus_strong.py)

Jazz guitar IS a plucked string — Karplus-Strong is the exact physical model (waveguide loop with lowpass filter damping). The archtop + flatwounds + thumb define a dark, warm damping character:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| loop_gain | 0.9975 | Flatwound strings ring long & smooth (2–4 s); between steel_acoustic 0.9970 and harp 0.9985; overdriven 0.9990 is the compression sustain |
| excitation | "thumb" | Fleshy thumb — round attack, no pick click transient |
| lowpass_hz | 3500 | Archtop neck-pickup rolloff — darker than clean electric 5000: flatwounds + f-hole body absorb the highs |
| noise_component | 0.015 | Low — thumb is quiet, flatwounds reduce finger noise (vs pick scratch 0.025) |
| width | 0.50 | Moderate pulse width (round, not bright) |

### Secondary: ModalSynth (sound/synthesis/modal.py)

Stock 'string' preset with IR drop — jazz guitar is a string, but the archtop body colour needs custom damping:

| Parameter | Value |
|-----------|-------|
| preset | "string" |
| excitation | "impulse" |
| decay_rates | [4, 10, 18, 28, 40] — darker/slower than clean electric (body absorbs highs) |

### Tertiary: PhaseModSynth (sound/synthesis/phase_mod.py — SP-012)

FM synth approximation — a saw carrier through a resonant bandpass that mimics the pickup rolloff:

| Parameter | Value |
|-----------|-------|
| carrier_shape | saw (even+odd harmonics) |
| mod_freq_ratio | 1.0 (octave doubling) |
| mod_depth | 1.5 — gentle FM twang; jazz tone is NOT brassy, keep modulation shallow |
| attack | 0.01 s — fast thumb transient |
| release | 0.25 s — moderate damping |

## Production defaults

| Parameter | Value | Notes |
|-----------|-------|-------|
| REVERB_TAIL | 2.0 s | Jazz-club room / warm hall — the jazz guitar lives in small-room ambience; plate reverb on ballads (Wes: dry amp + room; Joe Pass: hall) |
| EQ_BODY | (250, -2.0) | Peaking cut at 250 Hz — reduce archtop boxiness/boominess from the hollow body |
| EQ_PRESENCE | (2800, 2.0) | Peaking boost at 2.8 kHz — neck-pickup warmth, thumb-attack definition without harshness |
| EQ_AIR | (7500, 1.0) | High shelf at 7.5 kHz — gentle air only: the jazz tone is DARK by design (vs clean electric 8 kHz +1.5) |
| PAN | -0.2 | Centre-left for standard guitar seating; stereo double at +0.2 |

## RenderPipeline stem-label quirk

**Name quirk (cosmetic).** `GM_PROGRAMS[26] = "Electric Guitar (jazz)"` → sanitized filename `Electric_Guitar_jazz`. FluidR3 preset 26 = "Jazz Guitar" — the SF2 uses the common name while the pipeline uses the GM2 spec spelling. STEM_LABEL = "Electric_Guitar_jazz" **matches the pipeline's real label** so stem-file lookups work (same discipline as the "Bag pipe"/"Shanai" quirks at 109/111). No routing impact.

## FluidSynth / SF2 notes

FluidR3_GM.sf2 preset 26 = "Jazz Guitar" (a hollow-body archtop sample set, thumb/soft-picked articulation). The patch is audible across the full 28–84 range with no gaps. Below 28 (C1), the patch plays the lowest sample looped — write root notes of chords > 40 for idiomatic timbre. The SF2 preset has a warm, rounded attack with no bright pick transient — it sits naturally dark in a mix, so it needs less high-frequency EQ than the clean electric patch.

## Identity

GM 26 = Electric Guitar (jazz) — the archtop hollow-body electric guitar. The archetypal sounds: Gibson ES-175 through a warm tube amp (the bebop/hard-bop standard), L-5 through a Fender Twin (Wes Montgomery's octaves), Super 400 (Joe Pass solo guitar).

The jazz guitar is a **fully polyphonic instrument** with two idiomatic faces:
1. **Comping** — Freddie Green-style rhythm chords (short, on beats 2 & 4), shell voicings (root-7th-3rd), and walking bass-note comping. This is the #1 role in a jazz ensemble: the harmonic glue under the horn/soloist.
2. **Melody** — single-note thumb lines and Wes-style **octave melodies** (the doubled-octave lead that cuts through without harshness). Block chords for solo-guitar statements.

Line-instrument quirks:
- NOT a sustain voice — notes decay naturally (2–4 s). Write rhythmic comping and phrase-shaped lines, not tied whole notes (vibrato is the sustain mechanism on long notes).
- The thumb attack means velocities sit naturally in the 60–95 band; the SF2 patch is dark so it needs +2 dB presence around 2.8 kHz to sit in a mix.
- Comping chords should stay SMALL: 2–4 notes (shell voicings, 3-note Freddie Green), NOT dense 6-string barre chords — the archtop's mid-focused tone turns dense chords into mud, and real jazz comping is intentionally sparse.
- Doubling quirk: idiomatic doubling with other instruments is octaves or nothing — never unison with another melodic patch (the 2026-09-01 comb-filter lesson).
- The dark EQ means the jazz guitar occupies the 200 Hz–4 kHz band — keep bass instruments below 200 Hz and bright instruments above 4 kHz for a clean separation.
