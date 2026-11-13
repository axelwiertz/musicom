---
type: instrument
family: Guitar
name: Guitar Harmonics
midi_program: 31
gms: "Guitar harmonics"
range_min: 40
range_max: 84
solo_range: [48, 76]
role: [lead, melody, ornament, texture, accent, countermelody]
synthesis: [modal, karplus-strong, phase-mod]
---

# Guitar Harmonics

The chiming voice of the guitar family: a string excited at a **node** so
that only one upper partial survives (natural harmonics at the 12th / 7th /
5th / 4th fret), or a fretted note excited by a pick harmonic (artificial /
pinch harmonic). The tone is near-sinusoidal, bell-like, an octave or more
above the written pitch, and it rings several times longer than a normally
plucked note.

Identity: **GM31 = Electric Guitar (harmonics)**, not a separate instrument —
it is the guitar played in harmonic mode. The KB's other guitar entries
(24/25 acoustic, 26 jazz, 27 clean, 28 muted, 29 overdriven, 30 distortion)
all produce the string's full harmonic series; this is the only one whose
fundamental partial is *removed by physics*.

## MIDI / GM

- **Program**: 31 (GM program numbers are 0-based; 31 = the 32nd entry,
  "Guitar Harmonics"). GM2 spec spelling in the pipeline: `"Guitar harmonics"`.
- **Channel**: melodic channel (0–9), polyphonic (chords of harmonics are
  idiomatic: 3rds/4ths/6ths and open-string dyads).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 31 =
  **"Guitar Harmonics"** (verified from the phdr chunk).
- **RenderPipeline stem label**: `GM_PROGRAMS[31] = "Guitar harmonics"` →
  stem file `trackXX_Guitar_harmonics.wav` (capitalisation differs from the
  SF2 name only — **no routing quirk**; `STEM_LABEL = "Guitar_harmonics"`
  matches the pipeline so stem lookups resolve).
- GM neighbors: 24 nylon / 25 steel / 26 jazz / 27 clean / 28 muted / 29
  overdriven / 30 distortion — 31 closes the guitar block.

### Transposition quirk (measured)

**The patch sounds ONE OCTAVE ABOVE the written note.** Sweep (2026-11-13):

| Written | Expected f0 | FluidR3 peak | Ratio |
|---|---|---|---|
| 60 (C4) | 261.6 Hz | 522.0 Hz | 2.00× |
| 67 (G4) | 392.0 Hz | 782.0 Hz | 1.99× |
| 72 (C5) | 523.3 Hz | 1044.0 Hz | 2.00× |

Control programs 25 (steel guitar) and 105 (banjo) sound at written pitch
(ratio 1.00×), so this is a **patch property, not a render-path bug**:
FluidR3 samples preset 31 with the harmonic already transposed. Composition
jobs must therefore **write an octave below the desired sounding pitch** —
which is exactly how a 12th-fret natural harmonic behaves on a real guitar
(the node halves the string, the pitch doubles). `TRANSPOSE_SEMITONES = 12`
in `guitar_harmonics.py` documents this.

## Range

All figures are **written pitch**; sounding pitch = written + 12.

| Zone | Written MIDI | Written pitch | Sounds | Register |
|---|---|---|---|---|
| Full range | 40–84 | E2–C6 | E3–C7 | GM patch span (patch silent ≥ 86) |
| Low | 40–47 | E2–B2 | E3–B3 | 12th-fret harmonics on wound bass strings — fullest, woodiest chime, longest ring |
| Mid (harmonic zone) | 48–64 | C3–E4 | C4–E5 | 7th/5th/4th-fret nodes on A/D/G strings — primary melody |
| High | 65–84 | F4–C6 | F5–C7 | artificial / pinch harmonics, high node positions — glassy, thin, very long ring |

Empirical FluidR3 sweep (RMS, written notes 18–96): audible at every note
from 18 to 85, **silence from 86 up** (RMS 0.0000 at 86/87/88/91/96). So the
patch never clips a composition written inside 40–84. The real 22-fret neck's
natural harmonics span sounding E3 (52) to about E6 (88) = written E2–E5
(40–76), which is the SOLO_RANGE; above that only artificial harmonics reach.

## Articulations

| Technique | Velocity | Duration factor | Description |
|---|---|---|---|
| harmonic_12 | 82–86 | 1.6× | 12th-fret node — octave harmonic, the default natural harmonic, fullest tone |
| harmonic_7 | 80–84 | 1.4× | 7th-fret node — octave+fifth harmonic |
| harmonic_5 | 76–80 | 1.4× | 5th-fret node — double-octave harmonic, thinner and brighter |
| artificial | 78–84 | 1.0× | fretted note + pick harmonic 12 frets higher — melody-capable, any pitch |
| pinch_squeal | 88–96 | 0.6× | high-gain pinch harmonic — short screaming chime (rock/metal accent) |
| harp_harmonic | 66–74 | 2.0× | cascading harmonic arpeggio / glissando, the "harp" texture |
| chime_double_stop | 70–78 | 1.2× | two harmonics together (3rds/4ths/6ths stay clean) |
| tap_harmonic | 55–65 | 0.4× | tapped harmonic, short bell-like blip |
| let_ring | 64–72 | 2.5× | struck then left alone, full symmetric ring |
| muted | 35–45 | 0.2× | palm-damped harmonic ghost |

Durations are deliberately long: a node-touched string has almost no path
for energy to leak into other partials, so harmonics ring **2–5 s** while
held, versus ~1 s for an open plucked note on the same string.

## Timbre DNA

- **Partial structure**: the node kills every partial that has a displacement
  maximum where the finger touches. A 12th-fret touch removes the
  fundamental and *all even* partials above it → the surviving spectrum is
  the **ODD series of the sounding pitch**: 1f, 3f, 5f, 7f. Measured on the
  FluidR3 solo render of written C4, the peaks sit at 2×, 6×, 10×, 14× of the
  written pitch = 1×, 3×, 5×, 7× of the sounding (octave-up) pitch —
  28% / 10% / 11% / 1% of band energy, with the even partials absent.
- **Attack**: soft to medium — the finger *touches*, it does not strike; the
  pick (artificial harmonics) adds a short bright tick, the pinch harmonic a
  hard squeal.
- **Decay**: extremely long, near-exponential with a very slow slope (the
  SF2 patch is looped and holds flat RMS while the note is down:
  0.38 → 0.45 → 0.41 rms/peak across 0.2 s–2.5 s windows).
- **Vibrato**: possible but rare before the 1990s; a wide slow vibrato on a
  harmonic is the "whale call" texture.
- **Character**: glass, ice, crystal, harp-like; hollow because the even
  partials are missing — closer to a clarinet's odd-harmonic spectrum than
  to any other guitar voice, but with the guitar's fast, bright attack.

## Role in Arrangement

- **Lead / melody** — the classic artificial-harmonic melody line, floating
  an octave above the rest of the arrangement.
- **Ornament / accent** — single 12th-fret chimes punctuating a phrase; the
  pinch squeal as a rock/metal accent.
- **Texture / atmosphere** — arpeggiated harmonic chords, let-ring cascades,
  the "ice intro" layer (ambient, post-rock, film underscore).
- **Countermelody** — answers a vocal or lead line from above, in the same
  register as a glockenspiel/celesta but with guitar attack.
- **NOT a bass voice** — the lowest available sound is E3, and the whole
  point of the timbre is that the fundamental is missing.
- **NOT a rhythm/chord bed** — 2–3 note harmonic chords only; the sound is
  too pure and too long for strummed harmony (four simultaneous harmonics
  smear into a cluster).

## Synthesis Engines (musicom)

1. **ModalSynth** (`sound/synthesis/modal.py`) — **primary**, impulse-excited
   resonator bank with a custom `GUITAR_HARMONICS_MODES` bank at the measured
   odd-harmonic ratios **1 : 3 : 5 : 7** of the sounding pitch, amplitudes
   1.00 / 0.42 / 0.18 / 0.08 and decay rates 0.35 / 0.60 / 0.95 / 1.30 — the
   **slowest decay rates in the struck/plucked set** (vibraphone 0.30–1.10,
   timpani 0.9–3.0, xylophone 9–20), because one surviving partial has
   nowhere to leak energy. The stock `'string'` preset is the closest bank
   but keeps the even partials the node removes.
2. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
   legitimate fallback (the string *is* plucked, unlike the struck bars):
   `loop_gain 0.9988` is the highest in the KB (harp 0.9985), `width 0.22`
   for a narrow glassy pulse, `noise_component 0.004` (a finger touch, not a
   pick scrape), `lowpass_hz 9000`.
3. **PhaseModSynth** — cheap chime: sine carrier, mod ratio 2.0 (keeps the
   spectrum odd-harmonic), depth 0.8, attack 0.002 s, release 0.60 s.

## Production

- **Reverb**: 2.0–3.0 s hall — the longest guitar tail in the KB (default
  2.6 s). Pull to ~1.2 s if the chime must sit inside a dense mix.
- **EQ**: 240 Hz −2 dB to remove the small body thump under the chime;
  +2 dB at 5 kHz for the 5f/7f glass band (the identity of the sound);
  +2 dB shelf at 10.5 kHz for shimmer above the steel guitar's 9 kHz shelf.
- **Pan**: −0.15 default; hard-L/R ±0.5 doubles give the classic wide
  harmonic shimmer (the doubled parts are *different* pitches/octaves, never
  unison copies — unison doubling of identical pitches comb-filters).
- **Layering rule (2026-09-01 lesson)**: never double this voice with
  another melodic patch on the SAME pitches; the near-pure tone beats
  audibly against a piano/harp unison. Layer an octave up/down instead.

## Verification

- Solo render, one voice, one track (no unison doubling).
- GM31 → stem `trackXX_Guitar_harmonics.wav` (pipeline label matches).
- FluidR3 preset 31 = "Guitar Harmonics" (verified from the phdr chunk).
- Empirical pitch sweep (written 18–96): audible 18–85, silent ≥ 86.
- Measured transposition: sounding = written + 12 (2.00× fundamental).
- Measured spectrum: odd partials only (1×, 3×, 5×, 7× of sounding pitch).
- Measured sustain: flat RMS envelope for the whole held note (looped patch).

## Instrument.md companion

`guitar_harmonics.py` — importable constants. Registered in
`instrument_registry.py` (2026-11-13) as
`Guitar.guitar_harmonics.guitar_harmonics` → key `guitar_harmonics`,
constant `GUITAR_HARMONICS`.
