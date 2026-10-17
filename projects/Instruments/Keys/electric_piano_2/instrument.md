---
type: instrument
family: Keys
name: Electric Piano 2
midi_program: 5
gms: "Electric Piano 2"
range_min: 36
range_max: 96
solo_range: [48, 84]
role: [harmony, melody, bass, accent, color]
synthesis: [phase_mod, karplus, modal]
---

# Electric Piano 2 (DX7 FM Piano)

## MIDI / GM

- **Program**: 5 (GM1 "Electric Piano 2" — the Yamaha DX7 FM electric piano
  preset; GM program numbers are 0-based, so 5 is the 6th entry, "Electric
  Piano 2"). NOT in `structures/instrument.py` `MidiInstrument` enum (10 only)
  — use raw `program=5` in `add_voice`.
- **Channel**: any melodic channel (0-9). Channel 9 with program 5 would trigger
  the drum-kit map and the `Acoustic_Grand_Piano` program-0 fallback label (ch9
  quirk).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 5 =
  "Electric Piano 2" (phdr-verified — labels match exactly, no routing impact).
- **Pipeline stem label**: `GM_PROGRAMS[5]` = "Electric Piano 2" → disk stem
  `trackXX_Electric_Piano_2.wav` — labels match exactly, **no quirk**.

## Identity

Electric Piano 2 in the GM specification is historically the **Yamaha DX7**
digital synthesizer's iconic "E. Piano 1" preset (a 2-operator FM algorithm
with a fast percussive attack and bright bell-like tone). Unlike the Rhodes
(GM4) which is an electromechanical tine piano, the DX7 is a purely digital
**FM synthesis** instrument, producing its tone by modulating the frequency
of one sine-wave oscillator with another.

The defining elements:

- **FM synthesis core**: two sine-wave operators — a carrier (which we hear)
  and a modulator (which shapes the carrier's harmonic spectrum). The ratio
  of modulator frequency to carrier frequency determines the harmonic
  content (small integer ratios = bell-like; large non-integer ratios =
  metallic/clangorous). The DX7 "E. Piano 1" uses algorithm 1 with a ratio
  of ~2.94-3.1× (the exact number varies between factory banks).
- **Percussive attack**: the FM operator envelopes have a near-instant
  attack (rate ~80 on the DX7 envelope generator) — the sound starts at its
  brightest, then quickly decays to a softer sustain. This is the "bell
  strike" character: a bright, shimmering, percussive onset that decays
  into a purer tone.
- **No pickup, no amp**: unlike the Rhodes, the DX7 signal is a pure
  electrical sine-wave output — no magnetic pickup, no tube amp coloration,
  no speaker breakup. The sound is pristine, glassy, and clean until
  processed through effects.
- **Digital reverb**: the DX7 was famous for its built-in digital effects
  (especially the Lexicon-derived hall reverb). The "DX7 sound" is
  inseparable from a long shimmering reverb tail.

Consequences for composition:

- **Bright, cutting tone**: the DX7 electric piano is the BRIGHTEST of the
  electric piano family (GM4 Rhodes is warm/woody, GM5 DX7 is bright/glassy).
  It cuts through a mix better than any other keyboard patch — use it for
  melodic hooks and rhythmic stabs that need to be heard.
- **Wider dynamic range than Rhodes**: the DX7 responds more linearly to
  MIDI velocity than the Rhodes (no pickup compression). Velocity 40 and 120
  differ significantly in brightness AND loudness — phrase with velocity as
  on a real acoustic piano.
- **The "DX7 bell" is iconic**: the specific timbre (bright, percussive, with
  a slight metallic ring at high velocities) was used on countless 1980s
  records (Phil Collins, Whitney Houston, Toto, Genesis). It is instantly
  recognizable.
- **Limited release control**: the DX7 has no damper pedal response like an
  acoustic piano — notes ring for their programmed duration. The release is
  controlled by the operator envelope, not by physical dampers.
- **Line + harmony voice**: fully polyphonic (16-voice DX7 can play 16 notes
  simultaneously). Works as a harmonic pad, a comping chord voice, a melody
  lead, and a bass voice (in the low register).

## Range

| Zone | MIDI | Pitches | Keys | Register |
|---|---|---|---|---|
| Full range | 36–96 | E1–C7 | ~25–61 | GM patch span (DX7 keyboard 61 keys C3-C7) |
| Sweet spot | 53–79 | F3–G5 | ~18–44 | primary bell register, the iconic DX7 tone |
| Low | 36–47 | E1–B2 | 1–12 | dark, thuddy fundamental — bass zone (C1-C4 on 61-key) |
| Mid-low | 48–59 | C3–B3 | 13–24 | warm bell register, chord comping |
| Mid | 60–79 | C4–G5 | 25–44 | bright bell register — the DX7 signature zone |
| High | 80–96 | G#5–C7 | 45–61/61 | thin tinkly top, metallic sheen — use for sparkle |

The DX7 standard 61-note keyboard covers C3–C7 (48–96). The GM patch
(program 5) extends across the full GM span (36–96 in our range), and
FluidR3 preset 5 is a decent sampled DX7 patch.

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Legato (pedal) | 40–55 | full sustain, 1–3 s ring | mellow, soft fundamental, "water" |
| Touch (finger) | 55–72 | full sustain | neutral bell tone, clear attack |
| Accent | 80–95 | full, with bite | mid-velocity bell strike, signature DX7 |
| Hard accent | 100–115 | full, metallic ring | high velocity, bright metallic clang |
| Staccato | 65–78 | 0.2–0.25× | damped short, crisp pop/funk chop |
| Bell | 90–105 | 0.9× sustained | the iconic DX7 bell strike — brightest, most percussive |
| Tremolo (amp) | 50–65 | sustained | amplitude modulation 4-7 Hz |
| Comping chop | 72–82 | 0.45× | rhythmic chord stab, 80s pop/funk |

## Timbre DNA

- **Harmonic content**: fundamental + strong upper partials at ratios close
  to 2×, 3×, 4× of the fundamental, shaped by the FM modulation index. The
  brightness increases with velocity (higher modulation index = more
  harmonics). The signature DX7 sound has a prominent 3rd and 4th partial
  giving it a crystal-like "glass" character.
- **Attack**: ~1-5 ms — near-instant FM operator attack. The sound starts at
  its brightest and decays inward, unlike a Rhodes (where the tine starts
  bright and decays naturally) or a piano (where the hammer leaves the
  string at the moment of strike).
- **Decay**: FM decay is exponential and FAST — the bright harmonics die
  away quickly (0.3-1.0 s), leaving a softer fundamental sustain (1-3 s).
  Total tail is ~2-3 s vs a Rhodes ~2-6 s and a piano ~10 s.
- **Release**: the DX7 note stops instantly when Note Off is received (no
  physical dampers). Release is controlled by the operator envelopes (EG
  rate 4), which can be programmed for quick cutoff (~50 ms) or a slow fade
  (~500 ms).
- **Vibrato**: the DX7 has an LFO for pitch vibrato (rate ~5 Hz, depth
  ~0.5). Unlike the Rhodes, the natural DX7 has pitch vibrato, not
  amplitude tremolo. Use both pitch LFO (vibrato) and amplitude LFO
  (tremolo) for authentic 80s string/pad layering.
- **Character**: bright, percussive, glassy, digital — the coldest of the
  electric piano family; blends with warm analog sounds (Rhodes, analog
  synth pads) for the classic 80s "FM + analog" stereo layer. Without
  effects it sounds sterile; with hall reverb and chorus it transforms into
  the iconic shimmer.

## Role in Arrangement

- **Melody/hook**: bright cutting single-note lines in the mid register
  (60-79) — the DX7 bell cuts through a full mix; ideal for melodic hooks
  and signature riffs (Phil Collins "One More Night", Toto "Africa" chords).
- **Harmony/comping**: chordal pad/comping in the mid register — the classic
  80s "DX7 chord wash" with long hall reverb (sustain pedal down, soft
  velocity, chords ringing for 2-3 seconds).
- **Accent/percussive stab**: the DX7's fast attack makes it perfect for
  rhythmic chord stabs and punctuation (the iconic "One More Night" synth
  brass stab, Whitney Houston "I Wanna Dance With Somebody" intro chords).
- **Bass**: left-hand bass in the low zone (36-47) — the DX7 bass is less
  warm than a Rhodes or an acoustic piano; use for bright punchy synth bass
  lines but NOT for sub-bass foundations.
- **Color/sparkle**: high register (80-96) for bell-like accent notes,
  sparkly arpeggios, and glittering top-line tracer.

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — **primary**. The DX7
   IS an FM synthesizer — this is the exact synthesis model. Use a sine
   carrier + sine modulator, mod_freq_ratio **3.1** (the classic DX7 "E. Piano
   1" ratio — 3.0 is a pure 3rd partial, slightly detuned for the bell
   signature), mod_depth **2.8** (moderate-high for the bell clang without
   nasal foldover), attack 0.003 s (near-instant), release 1.2 s. For the
   warm "DX7 pad" tone, reduce mod_depth to ~1.5-2.0 and add chorus.

2. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) — the
   FM bell is a struck metallic sound — waveguide model with loop_gain
   **0.9960** (between clavi 0.9960 and rhodes 0.9965; shorter than a guitar
   or harp string). Low-pass filter at ~4000 Hz for the bright bell top, and
   minimal noise_component (0.01) — FM synthesis is clean with no mechanical
   noise.

3. **ModalSynth** (`sound/synthesis/modal.py`) — stock `'bell'` preset for
   the metallic percussive character. A custom bank at ratios 1:2.5:4.7:7.3
   (the inharmonic FM bell stretch) with fast decay rates (3-8) models the
   DX7 bell character.

## Production

- **Reverb**: hall 1.5–2.5 s with 30-60 ms pre-delay — the DX7 sound IS
  drenched in digital hall reverb (Lexicon 224/480L / Yamaha SPX90). The
  shimmering chord wash requires at least 2.0 s reverb tail. For pop
  comping, use a shorter room plate 1.2-1.5 s.
- **Chorus**: a stereo chorus (rate ~0.4 Hz, depth ~50%) is the second-most
  important effect — the iconic "DX7 stereo chorus" widens the mono FM
  signal into a lush stereo layer. The chorus was built into the DX7 itself
  (internal stereo chorus).
- **EQ**: cut ~400 Hz (body boxiness); boost ~3.2 kHz for the bright bell
  articulation; high shelf 9 kHz for shimmer air. The DX7 has a lot of
  energy at 3-6 kHz — use this for cutting through a dense mix. A high-pass
  filter at 150 Hz keeps the bass clear.
- **Compression**: the DX7 needs LESS compression than the Rhodes (its
  dynamic range is already wide and linear). A gentle 2:1 opto compressor
  smooths peaks for a pop mix; for ambient pad, use a slow opto (LA-2A)
  for the natural sustain bloom.
- **Delay**: dotted 8th or 1/4-note delay (120-200 ms) for solo lines;
  ambient 1/4-note with feedback for pad atmospheres (the classic 80s
  gated delay).
- **Stereo layering**: the most famous DX7 sound in pop is a DUAL-layer of
  the DX7 (panned left) + Rhodes (panned right) in stereo, or DX7 +
  analog pad. The DX7 provides the cutting bell attack; the warm analog
  pad provides the body.
- **Pan**: center for solo; in 80s stereo the DX7 sits centre-left
  (-0.2) for the classic "stereo piano" spread with Rhodes on the right.
- **FluidSynth note**: FluidR3 preset 5 is a decent DX7 sample. For the
  authentic FM bell + shimmer, use the PhaseModSynth engine (the exact
  synthesis model).

## Verification

- GM5 → stem `trackXX_Electric_Piano_2.wav` (label = "Electric Piano 2",
  no quirk — GM_PROGRAMS index 5 = "Electric Piano 2")
- FluidR3 preset 5 = "Electric Piano 2" (phdr-verified — exact match)
- Solo render passes 4–8 kHz spectral gate (FM bell, no comb buzz)
- Zero-drift: struck/piano-style units end flush at BAR (terminal landmark)
- **FM bell quirk**: the DX7 signature is a VERY bright attack with a fast
  decay — the top partials (>5 kHz) are prominent in the first 200 ms then
  vanish. Do NOT use the spectral-buzz gate (4-8 kHz) in the first 100 ms
  as a rejection criterion — the natural FM bell has 4-8 kHz energy at
  onset by design.
- **Empirical FluidR3 pitch sweep** (RMS, notes 36–96): preset 5 audible
  across full span, no gaps — SF2 never clips a composition.

## Instrument.md companion

`electric_piano_2.py` — importable constants. Registered in
`instrument_registry.py` (2026-10-17) as `Keys.electric_piano_2.electric_piano_2`
→ key `electric_piano_2`, constant `ELECTRIC_PIANO_2`.