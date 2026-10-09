---
type: instrument
family: Guitar
name: Acoustic Guitar (steel)
midi_program: 26
gms: "Acoustic Guitar (steel)"
range_min: 40
range_max: 86
solo_range: [50, 79]
role: [harmony, rhythm, strum, lead, melody, ornament, countermelody]
synthesis: [karplus_strong, modal]
---

# Acoustic Guitar (steel)

## MIDI / GM

- **Program**: 25 (GM1 Steel String Guitar — 0-indexed; the 26th entry of the GM1 list).
  NOT in `structures/instrument.py` `MidiInstrument` enum (10 only) — use raw
  `program=25` in `add_voice`.
- **Channel**: melodic channel (0-9) — plucked string instrument, NOT channel 9 percussion.
|- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 25 =
  "Steel String Guitar" (phdr-verified). RenderPipeline stem label: GM_PROGRAMS[25] =
    "Acoustic Guitar (steel)" → pipeline stem is `trackXX_Acoustic_Guitar_steel.wav` (matches,
    **no quirk**). FluidR3 preset 25 = "Steel String Guitar" — internal SF2 name differs from
- GM neighbors: 24 Acoustic Guitar (nylon), 25 Acoustic Guitar (steel), 26 Electric
  Guitar (jazz) — the acoustic guitar block of GM1. The steel-string is brighter,
  louder, and has more percussive attack than the nylon cousin at program 24.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 40–86 | E2–C#6 | steel-string acoustic (20-fret, ~6 octaves including harmonics) |
| Sweet spot | 50–79 | D3–G5 | strongest fundamental, best projection, brightest tone |
| Low | 40–50 | E2–D3 | bass strings (E A D) — open chord roots, bass runs, percussive thump |
| Mid | 51–66 | D#3–G4 | full fundamental range for chords and fingerpicking |
| High | 67–86 | G#4–C#6 | melodic lead, harmonics, bright cutting top |

The standard steel-string acoustic guitar has 6 strings tuned E2–A2–D3–G3–B3–E4
(MIDI 40, 45, 50, 55, 59, 64) over a ~20-fret fingerboard. The GM patch
(FluidR3 "Steel String Guitar") audibly supports 40–86 with a bright,
percussive, complex tone. The sweetest fingerpicking range is D3–G5 (50–79).
Above G#5 (68) the tone thins but remains usable for melodic accents. The
nylon-string cousin (GM25) is warmer and rounder; the steel-string has more
high-frequency content, faster attack (steel is stiffer), and greater volume.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Strum (down) | 70–90 | 1/4–1/2 | full strum across all strings, percussive attack, ringing sustain |
| Strum (up) | 65–80 | 1/4–1/2 | lighter upward sweep, less percussive |
| Fingerpick (thumb) | 60–75 | full | warm round attack from the thumb (bass strings) |
| Fingerpick (index/m) | 55–70 | full | medium attack, balanced tone (treble strings) |
| Flatpick (pick) | 75–95 | 1/8–1/4 | bright aggressive attack from plectrum — cutting rhythmic drive |
| Arpeggio (finger) | 60–75 | 1/8–1/4 | rolled chord, each string picked individually, fluid texture |
| Hammer-on | 72–85 | 1/2 | legato slur upward — second note sounded by fretting hand only |
| Pull-off | 60–75 | 1/2 | legato slur downward — string plucked by pulling finger off fret |
| Muted (palm) | 40–55 | 1/8 | palm rest on bridge — damped percussive "chunk" |
| Harmonics (natural) | 95–100 | 1/2–full | bell-like overtone at the 12th/7th/5th fret nodes |
| Slide | 65–80 | 1/2–full | continuous pitch glide between two frets along the string |
| Accent (hard pick) | 90–100 | 1/8 | aggressive percussive strike — cutting, driving downbeat |

## Timbre DNA

- **Harmonic content**: bright, complex — steel strings produce a strong
  harmonic series up to the 10th+ partial, with a prominent 2nd, 3rd, 4th,
  and 5th. The steel-string has significantly more upper partials (3–8 kHz
  band) than nylon, which gives it the characteristic "sparkle" and "cut."
  The wound bass strings (E, A, D) have a smoother decay with fewer upper
  partials than the plain treble strings (G, B, high E).
- **Attack**: ~1–5 ms (steel pick/plectrum on steel string) — very fast, with
  a characteristic percussive "chirp" transient as the pick releases and the
  string snaps back. Flesh attack (fingerstyle) is ~3–8 ms — softer but still
  faster than nylon due to the stiffer strings.
- **Decay**: medium — steel strings sustain 1–3 s depending on string gauge,
  attack force, and body resonance. The body's topwood (spruce/cedar)
  resonance and the bridge-saddle coupling determine the actual sustain curve.
  Steels strings are stiffer = more sustain than nylon at equal tension.
- **Pickup noise**: significant for a flatpick — the pick scrape over the
  wound strings creates the characteristic percussive "click" that is part of
  the steel-string identity. Fingerstyle is quieter but the nail strike on
  steel still produces a bright tap.
- **Body resonance**: the soundbox (spruce top + rosewood/mahogany sides)
  resonates strongly from ~100–300 Hz with a low-frequency "body boom"
  near 100–120 Hz and a "honk" region near 200–400 Hz.
- **Vibrato**: wide and expressive on sustained notes (bend + release), NOT
  inherent like a bowed string — do not simulate without pitch-bend events.
- **Character**: bright, percussive, cutting — the classic folk/country/rock
  rhythm and fingerpicking voice. Brighter and louder than nylon, with a
  distinctive "chirpy" attack transient. The open strings ring pure and
  clear; the fretted notes are slightly warmer but still bright.

## Role in Arrangement

- Rhythm (strumming patterns, 50–72 range) — the steel-string's primary
  role: chordal accompaniment across all six strings, variably muffled
  (palm mute) or open ringing
- Lead melody (fingerstyle/flatpick, 60–79 range) — melodic lines,
  flatpicked fiddle tunes (Doc Watson, Tony Rice), single-note runs
- Arpeggio (fingerpicked rolled chords, 40–72 range) — Travis picking,
  Carter family style, classical fingerpicking patterns
- Countermelody (above or below the vocal line, 55–79 range)
- Ornament (hammer-ons, pull-offs, slides, bends, harmonics — idiomatic
  to steel-string country/blues/folk)
- NOT a bass voice (the lowest note is E2=40; use acoustic bass or upright
  for strong bass below E2)
- NOT a sustain/pad voice — the steel-string decays within 1–3 s; rolls
  and tremolo patterns are the sustain mechanism

## Synthesis Engines (musicom)

1. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) — **primary**.
   The exact physical model for a plucked steel string: waveguide loop with
   lowpass filter and adjustable decay. Recommended parameters:
   - `loop_gain`: 0.9970 — steel strings ring 1–3 s (between clavi 0.9960
     and harp 0.9985; similar to electric bass 0.9970)
   - `width`: 0.65 — moderate pulse width (steel string is stiffer than
     nylon, gives brighter attack with more pronounced harmonic partials)
   - `excitation`: "pick" for the bright hard attack, or "finger" for the
     warmer flesh tone
   - `lowpass_hz`: 5000–8000 — steel string has energy up to ~8 kHz before
     body damping (wider band than nylon)
   - `noise_component`: 0.02 — pick scrape noise on wound strings

2. **ModalSynth** (`sound/synthesis/modal.py`) — fallback. Stock `'string'`
   preset with impulse excitation and a harmonic stack (1:2:3:4:5) at
   moderate decay rates for the body resonance. The body's low-frequency
   resonance (~100–300 Hz) is a 2D membrane on a cavity — the stock
   string preset's harmonic 1D string modes do NOT model the Helmholtz
   body resonance, so a custom `STEEL_ACOUSTIC_GUITAR_MODES` would add
   the body "boom" mode at ~110 Hz (A2-body coupling). Karplus-Strong is
   the better recommendation because it models the string-body coupling
   through the waveguide loop.

## Production

- **Reverb**: room/small hall 1.2–1.8 s — steel-string rhythm needs clarity;
  long reverb washes out the percussive attack and the rhythmic groove.
  Shorter than nylon (2.0–2.5 s) because steel is naturally brighter and
  more sustained.
- **EQ**: 
  - Cut 200–400 Hz (body boxiness, "honk" region) — the steel-string's main
    mud zone; ~3 dB cut with a peaking filter preserves the warm body
  - Boost 3–5 kHz (string brightness, pick attack, presence) — ~2–3 dB
    peaking boost; this is the steel-string's identity band
  - Shelf 8–10 kHz (air, sparkle) — gentle ~1.5 dB shelf; steel has natural
    energy here, too much sounds brittle
- **Delay**: optional dotted-8th at low mix for fingerstyle ballads; avoid on
  rhythm strumming (muddies the percussive groove)
- **Pan**: center for solo; ±0.2–0.3 for double-tracked rhythm (stereo pair);
  ±0.1 for strumming in a band mix

## Verification

- GM26 → stem `trackXX_Acoustic_Guitar_steel.wav` (label matches pipeline
  GM_PROGRAMS[25], no quirk; FluidR3 preset 25 = "Steel String Guitar" —
  internal SF2 name differs from pipeline label "Acoustic Guitar (steel)"
  only cosmetically)
- Zero-drift: rhythm units end flush at BAR (terminal landmark)
- Solo render only (no unison doubling — comb-filtering buzz)
- Spectral 4–8 kHz buzz well below 20% (bright but clean steel-string tone)

## Instrument.md companion

`steel_acoustic.py` — importable constants. Registered in
`instrument_registry.py` (2026-10-09) as `Guitar.steel_acoustic.steel_acoustic`
→ key `steel_acoustic`, constant `STEEL_ACOUSTIC`.