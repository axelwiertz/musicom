---
type: instrument
family: Bass
name: Electric Bass (finger)
midi_program: 33
gms: "Electric Bass (finger)"
range_min: 24
range_max: 84
solo_range: [31, 55]
role: [bass, rhythm, countermelody, accent]
synthesis: [karplus, additive, phase_mod]
---

# Electric Bass (finger)

## MIDI / GM

- **Program**: 33 (GM1 Electric Bass (finger); 0-indexed). NOT in
  `structures/instrument.py` `MidiInstrument` enum (10 only) — use raw
  `program=33` in `add_voice`.
- **Channel**: any melodic channel (0-9); line voice — one note at a time
  (double-stops on adjacent strings possible but rare).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 33 =
  "Electric Bass (finger)" (phdr-verified). RenderPipeline stem label:
  GM_PROGRAMS[33] = "Electric Bass (finger)" →
  `trackXX_Electric_Bass_finger.wav` — matches exactly, **no quirk**.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range (GM patch) | 24–84 | C1–C5 | Extended bass / GM patch |
| Contrabass | 24–35 | C1–E2 | Sub-bass fundamental: chest thump, felt > heard |
| Groove (root pocket) | 36–50 | E2–D3 | Primary rhythm register: root-fifth, walking lines |
| Mid (fretboard centre) | 51–65 | D#3–F4 | Melodic fills, singing tone, ghost-note slaps |
| High (tenor) | 66–84 | F#4–C5 | Bright, aggressive: slap/pop solos, harmonics |

Practical 4-string tuned E1–G4: 28–67. Standard tuning E1–A1–D2–G2 = 28, 33,
38, 43. The GM patch (FluidR3) sounds convincingly across the full GM range
24–84 (C1–C5), with the sweet spot at 40–65 (E2–F4) — the groove pocket.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Finger (warm) | 65–80 | full note | Fingertip pluck, round, smooth — the default |
| Pick (bright) | 80–95 | 0.75–0.9 | Plectrum attack, bright, aggressive, thinner sustain |
| Slap (thumb) | 85–100 | 0.2–0.4 | Percussive thwack, string hits fret — short, punchy |
| Pop (finger snap) | 95–105 | 0.1–0.3 | Hook-finger snap, bright harmonic click |
| Muted / ghost | 30–55 | 0.1–0.3 | Palm-muted or fret-hand damped — no pitch |
| Legato (H/P) | 60–75 | full, smooth | Hammer-on / pull-off, connected without re-pick |
| Slide (gliss) | 55–70 | note + glide | Finger slide across fretwire, audible pitch bend |
| Accent | 85–100 | full, strong | Hard finger pluck or pick dig for downbeat emphasis |

## Timbre DNA

- **Harmonic content**: strong fundamental (especially below ~120 Hz),
  moderately warm upper partials (2–6 Hz bandwidth). Electric bass pickups
  roll off above ~5 kHz naturally. Roundwound strings add fret buzz / string
  noise in the 2–5 kHz band; flatwound strings are smoother.
- **Attack**: 2–10 ms pick/finger transient. The fingerstyle attack is a
  broad midrange thump; the pick attack is a sharper click. Both are softer
  than the slap attack (which includes the string hitting the fret).
- **Decay**: wound steel strings sustain 1–3 s depending on gauge and pickup
  position. Electric bass has LESS sustain than a harp or sitar because the
  magnetic pickup + steel string combination has higher internal damping.
- **Noise**: fret buzz at low velocities, finger/pick scrape on roundwound
  strings, slide-on-fretwire squeak — these are PART of the idiom
  (especially in funk and rock). The EQ preset adds a gentle air shelf at
  5 kHz for this reason.
- **Character**: warm, round, punchy — the foundational modern bass sound.
  A Precision Bass in the finger pocket (E2–D3) is the most-recorded bass
  sound in popular music history (James Jamerson, Paul McCartney, Carol Kaye).

## Role in Arrangement

- **Bass** (primary): root-fifth groove, walking lines, pedal tones, the
  harmonic foundation of the rhythm section. The bass locks with the kick
  drum and defines the chord's root.
- **Rhythm**: ghost-note grooves, slap/pop patterns, octave-displacement
  riffs (the "octave trick").
- **Countermelody**: melodic fills at phrase ends, contrary motion against
  the vocal/sax line, walking-bass counterlines.
- **Accent**: aggressive pick accents on the downbeat, slap bursts, fret
  noise / pick scrape as textural hits.
- NOT a lead voice (though solo passages exist in funk, jazz, rock);
  NOT a harmony/pad voice (bass plays one note at a time, double-stops
  on neighbouring strings only).
- NOT a high-register sustain voice (bass above ~C4 is thin and
  aggressive — use it for accents, not sustained melody).

## Synthesis Engines (musicom)

1. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
   **primary**. Plucked waveguide is the exact physical model: the string
   vibration on a plucked wire string with magnetic pickup. `loop_gain`
   0.9970 (moderate damping — wound steel strings ring 1–3 s), `width` 0.6
   (subtle stereo tail). This is the same engine used for sitar, koto,
   harp, harpsichord — but with bass-specific loop_gain damping (shorter
   than harp 0.9985, longer than shamisen 0.9955).

2. **Additive** (`sound/synthesis/additive.py`) — fallback. A low-frequency
   oscillator stack tuned to the lower register.

3. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — weak alternative.
   Saw carrier + sub-octave mod (0.5 ratio) for a cheap PWM bass
   approximation. Not idiomatic but usable for 8-bit / chipmunk
   simulations.

## Production

- **Reverb**: room 1.4 s — electric bass is typically dry (DI / close-mic
  amp). Verb is a mix choice for exposed solos; too much verb thins the low
  end.
- **EQ**: cut 250 Hz (mud — the P-Bass / Jazz-Bass box resonance); boost
  800 Hz (finger attack / growl); gentle 5 kHz shelf for string noise /
  roundwound shimmer. Below 40 Hz: high-pass in a dense mix to preserve
  headroom.
- **Compression**: 1176 / LA-2A style — bass NEEDS compression to sit
  consistently. Not specified in production defaults (it's a mix-stage
  decision, not a baked EQ/reverb).
- **Pan**: center (100% mono). Electric bass is universally centered in the
  stereo field. A subtle stereo spread on the harmonic tail (0.6 width in
  KS) is the maximum.
- **Track**: DI signal with amp simulation (SVT, B-15, Ampeg) is the
  standard recording chain.

## Verification

- GM33 → stem `trackXX_Electric_Bass_finger.wav` (label matches, no quirk;
  FluidR3 preset 33 = "Electric Bass (finger)" phdr-verified)
- Zero-drift: units end flush at BAR (terminal landmark)
- Solo render only (no unison doubling — comb-filtering buzz rule applies
  if a second melodic patch plays the same bass line an octave apart)
- Spectral 4–8 kHz buzz well below 20% (electric bass is a LOW instrument
  with very little energy above 4 kHz; the 5 kHz shelf is for string noise,
  not harmonic content)
- Karplus-Strong smoke test: plucked waveguide produces audible low-frequency
  output with the expected "pluck then ring" transient