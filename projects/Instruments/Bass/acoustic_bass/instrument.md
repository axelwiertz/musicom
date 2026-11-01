---
type: instrument
family: Bass
name: Acoustic Bass
midi_program: 32
gms: "Acoustic Bass"
range_min: 24
range_max: 72
solo_range: [36, 60]
role: [bass, rhythm, countermelody, accent, melody]
synthesis: [karplus, bowed, modal]
---

# Acoustic Bass

## MIDI / GM

- **Program**: 32 (GM1 Acoustic Bass; 0-indexed — matches FluidR3 preset 32
  and the RenderPipeline `GM_PROGRAMS[32]`). NOT in
  `structures/instrument.py` `MidiInstrument` enum (10 only) — use raw
  `program=32` in `add_voice`.
- **Channel**: any melodic channel (0–9). Monophonic in practice — one note
  at a time (double-stops on adjacent strings possible but rare; chords are
  NOT idiomatic).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 32 =
  **"Acoustic Bass"** (phdr-verified). RenderPipeline stem label:
  `GM_PROGRAMS[32] = "Acoustic Bass"` → sanitized
  `trackXX_Acoustic_Bass.wav` — matches exactly, **no quirk**.
- **Identity**: the upright double bass played pizzicato — the jazz
  walking-bass voice (Ray Brown, Paul Chambers, Ron Carter, Charlie Haden,
  NHØP, Stanley Clarke), the bluegrass slap voice, the rockabilly thump.
  The same instrument as the orchestral Contrabass (GM43) but in its
  plucked idiom: finger-plucked gut/steel strings over a huge wooden body
  give a fundamental-rich woody thump with a long natural ring and NO
  electronics in the signal path. GM33 Electric Bass (finger) is the
  amplified magnetic-pickup cousin; GM35 Fretless is the frets-pulled
  electric; GM38 Synth Bass 1 is the oscillator voice. GM32 is the acoustic
  original.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range (GM patch) | 24–72 | C1–C5 | Extended bass / GM patch |
| Sub (open/pedal) | 24–35 | C1–E2 | Chest thump, felt > heard, single notes only |
| Walking (primary) | 36–52 | C2–E3 | Jazz walking bass, root-fifth lines, bluegrass half-notes |
| Mid (melodic) | 53–64 | F3–E4 | Melodic fills, pizz solos, singing woody tone |
| High (thumb) | 65–72 | F4–C5 | Thin, cello-like, exposed solos only |

Practical 4-string upright tuned E1–G4: 28–67. Standard tuning
E1–A1–D2–G2 = 28, 33, 38, 43. The GM patch (FluidR3) sounds convincingly
across the full GM range 24–72 (C1–C5), with the sweet spot at 40–57
(E2–A3) — the jazz walking pocket. (Empirical FluidR3 pitch sweep in
REPORT.md.)

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Pizz (default) | 65–80 | full note | Finger pluck, round, woody — the voice |
| Walking | 65–80 | 0.85–0.95 | Quarter-note pulse, even, detached |
| Slap (rockabilly) | 85–105 | 0.2–0.4 | String slaps fingerboard — percussive thwack |
| Ghost / dead note | 30–50 | 0.1–0.2 | Left-hand damp — no pitch, groove filler |
| Legato (hammer) | 60–75 | full, smooth | Slurred pizz, connected without re-pluck |
| Slide (gliss) | 55–70 | note + glide | Fingered slide, woody portamento |
| Arco (jazz bow) | 70–85 | full | Bowed — sustained, reedy, cello-like |
| Staccato | 60–75 | 0.3–0.4 | Short damped pizz — tight, dry |
| Accent | 85–100 | full, strong | Emphatic downbeat pluck |

## Timbre DNA

- **Harmonic content**: strong fundamental (dominant below ~200 Hz — the
  walking bass line IS the pitch), woody midrange body resonance in the
  100–300 Hz band, and a fast roll-off above ~2 kHz (the wooden body absorbs
  the highs). Gut strings are smoother than steel; steel strings add a
  brighter attack transient.
- **Attack**: 5–15 ms finger transient. The pizz attack is a soft woody
  thump (softer than the electric bass pick click). The slap attack is the
  loudest in the family — the string physically hits the fingerboard.
- **Decay**: long ring — the upright's strings are long, thick, and lightly
  damped (gut especially); a pizz note rings 2–4 s in a small room. Less
  sustain than harp 0.9985 (body absorbs some energy) but more than the
  electric bass (no magnetic pickup sustain).
- **Noise**: finger scrape / string squeak, body creak — PART of the jazz
  idiom (players embrace it; the EQ preset adds a gentle 4 kHz air shelf).
- **Character**: woody, warm, fundamental-rich — the acoustic original of
  the bass family. A walking bass line in the C2–E3 pocket is the most
  recorded jazz bass sound (Ray Brown with Oscar Peterson, Paul Chambers
  with Miles Davis).

## Role in Arrangement

- **Bass** (primary): walking bass, root-fifth groove, pedal tones — the
  harmonic foundation of the jazz/blues/folk rhythm section. Locks with the
  kick and defines the chord root.
- **Rhythm**: slap patterns (rockabilly/bluegrass), ghost-note grooves,
  broken-octave fills.
- **Countermelody**: melodic fills at phrase ends, contrary motion against
  the horn/vocal line.
- **Accent**: slap bursts, emphatic downbeat plucks.
- **Melody**: pizz solos in the mid register (53–64) — the singing woody
  tone (NHØP, Stanley Clarke).
- NOT a harmony/pad voice (one note at a time, double-stops rare);
  NOT a high-register sustain voice (above ~C4 the upright is thin and
  cello-like — exposed solos only).

## Synthesis Engines (musicom)

1. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
   **primary**. Plucked waveguide is the exact physical model: the string
   vibration of a finger-plucked upright bass string. `loop_gain` 0.9975
   (long ring — between electric bass 0.9970 and harp 0.9985, matching the
   sitar/fretless class), `lowpass_hz` 1600 (the HUGE wooden body rolls the
   top off into the woody thump band — the acoustic-bass signature, darker
   than the electric bass). Same engine family as sitar, koto, harp,
   electric bass — with the darkest lowpass of the plucked basses.

2. **BowedString** (`sound/synthesis/bowed.py`) — arco-only alternative.
   Bow velocity 0.18 / force 1.3 for a woody jazz-bow tone; NOT the default
   voice (the GM32 patch is a pizz patch).

3. **ModalSynth** (`sound/synthesis/modal.py`) — weak fallback. `'string'`
   preset (harmonic stack, no wooden-body resonance).

4. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — weak alternative.
   Sine carrier + gentle mod for a cheap synth-bass approximation. Not
   idiomatic.

## Production

- **Reverb**: jazz-club room 1.8 s — the upright lives in a small wooden
  room, not a hall. Too much verb thins the low end and smears the walking
  line (double_bass 1.8 precedent).
- **EQ**: cut 220 Hz (body boxiness — the woody thump itself is LOWER,
  ~100 Hz, keep that); boost 700 Hz (finger attack / pizz growl); gentle
  4 kHz shelf for finger scrape / string shimmer. High-pass below ~40 Hz in
  a dense mix.
- **Compression**: light opto (LA-2A) — the upright is the most dynamic
  bass (plucked by hand, no pickup); even it out for a mix but preserve the
  attack. Mix-stage decision, not baked into the defaults.
- **Pan**: center (100% mono). Acoustic bass is universally centered.
- **Track**: condenser mic 30–50 cm off the f-hole + a DI/contact pickup
  blend is the standard jazz recording chain.

## Verification

- GM32 → stem `trackXX_Acoustic_Bass.wav` (label matches, no quirk;
  FluidR3 preset 32 = "Acoustic Bass" phdr-verified)
- Zero-drift: units end flush at BAR (terminal landmark)
- Solo render only (no unison doubling — comb-filtering buzz rule applies)
- Spectral 4–8 kHz buzz well below 20% (acoustic bass is a LOW instrument
  with very little energy above 4 kHz)
- Karplus-Strong smoke test: plucked waveguide produces audible low-frequency
  output with the expected "pluck then ring" transient
- Empirical FluidR3 pitch sweep: preset 32 audible across the full
  documented range, no gaps — SF2 never clips a composition (REPORT.md)
