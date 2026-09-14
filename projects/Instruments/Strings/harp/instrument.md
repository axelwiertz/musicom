---
type: instrument
family: Strings
name: Harp
midi_program: 46
gms: "Orchestral Harp"
range_min: 24
range_max: 103
solo_range: [24, 103]   # full 47-string concert-grand span
role: [harmony, arpeggio, glissando, melody, countermelody, accent]
synthesis: [karplus, modal, phase_mod]
---

# Harp

## MIDI / GM

- **Program**: 46 (GM1 Orchestral Harp — GM program numbers are 0-based; 46
  is the 47th entry, "Orchestral Harp", part of the strings block 40–47).
  NOT in `structures/instrument.py` `MidiInstrument` enum (10 only) — use
  raw `program=46` in `add_voice`.
- **Channel**: any melodic channel (0-9) — the harp is PITCHED; channel 9
  would trigger the drum-kit map and the program-0 fallback stem label
  `Acoustic_Grand_Piano` (ch9/pgm0 quirk).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 46 =
  "Harp" (phdr-verified — SF2 spells it "Harp", NOT "Orchestral Harp";
  cosmetic label difference only, no routing impact).
- **Pipeline stem label**: `GM_PROGRAMS[46]` = "Orchestral Harp" → disk stem
  `trackXX_Orchestral_Harp.wav` — matches exactly, **no quirk** (contrast
  GM74 Flute → `Recorder`, GM109 → `Bag_pipe`).

## Identity

The modern concert harp is the **47-string double-action pedal harp** — a
triangular frame (column, curved neck, soundboard body) carrying **47
strings** (lowest ~1.4 m wire-wound, then gut, then nylon trebles) played by
**eight fingertips** with the pads (not nails) in classical technique.
Sebastién Érard's **double-action pedal mechanism** (1810, still the
standard) is the defining invention: **seven pedals** (D C B — left foot;
E F G A — right foot), each with **three positions** (flat / natural /
sharp), each position retuning **every string of one pitch class across
all 47 strings at once** (the double action adds two semitone steps).

Consequences for composition:

- The harp is **diatonic per pedal setting** — a single string cannot sound
  a chromatic neighbour; accidentals require pedal moves (~a beat of
  writing time) or an **enharmonic re-spelling** (press the D pedal to
  sharp → every D# string is retuned, Cb and B become playable as separate
  pitches).
- **No dampers** — every string rings until hand-damped; the natural
  texture is rings, arpeggios and glissandi, not dry staccato.
- **Glissando is idiomatic and cheap** — a drag across 20+ strings of the
  current diatonic row is the instrument's signature sound.

It is the only plucked member of the classical strings block, the standard
orchestral colour (Debussy *Danses sacrée et profane*, Ravel's *Introduction
and Allegro*, Tchaikovsky waltzes, Berlioz), a jazz voicing instrument
(Alice Coltrane, Dorothy Ashby), and a foundational film-score texture.

## Range

47 strings, sounding pitch. **Non-transposing, written at concert pitch**
(grand staff; bass clef hands play low, treble clef hands high).

| Zone | MIDI | Pitches | Strings | Register |
|---|---|---|---|---|
| Full range | 24–103 | C1–G7 | 1–47 | concert grand (widest in the orchestra after piano) |
| Sweet spot | 55–88 | G3–E6 | ~22–38 | richest gut/nylon; main melody + arpeggio zone |
| Low | 24–47 | C1–B2 | 47–34 | wire-wound bass: dark, huge, rings 6–10 s |
| Mid | 48–71 | C3–B4 | ~33–22 | gut: principal melodic + arpeggio register |
| High | 72–103 | C5–G7 | ~21–1 | nylon treble: bright, fast decay, gliss sparkle |

The 47-string grand is the orchestral standard; smaller lever (folk/Celtic)
harps span ~34 strings (C3–A6, 48–93). Chords of **4 notes per hand, both
hands = 8 simultaneous pitches** are physically idiomatic (contrast koto's
stacked 4ths or the piano's thirds clusters): harp voicings typically space
in **open 4ths/5ths/octaves** with the hands an octave apart ("harp
spread").

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Pluck (apoyando) | 75–95 | full decay, ring 2–8 s | fingertip pad, round attack, full string |
| Nail / plectrum | 85–105 | 0.9×, faster decay | bright ping, Celtic/folk tone |
| Arpeggio (rolled) | 60–80 | 30–60 ms/string | low→high ripple, the default harp chord |
| Glissando | 70–90 | 0.5–2 s sweep | thumb-drag up or down the diatonic row |
| Bisbigliando | 55–70 | sustained trill | whisper tremolo between enharmonic unisons |
| Harmonic | 50–70 | 0.6× | palm node, flute-like octave bell tone |
| Étouffée (damp) | 40–60 | very short | palm-choked, dry percussive stop |
| Près de la table | 50–70 | 0.8× | near soundboard — dark, covered, intimate |
| Flat fermata | 55–75 | medium | flat hand stops ring — buzzing slap decay |
| Sonoro / harmonics gliss | 60–80 | gliss of harmonics | crystalline high chime cascade |

## Timbre DNA

- **Harmonic content**: near-harmonic string stack with real slight
  inharmonicity (thicker bass winding = progressively flatter upper
  partials); fundamental dominates through the mid band
- **Attack**: 2–8 ms fingertip pluck — soft round onset (softer than a
  guitar pick, rounder than a koto tsume)
- **Decay**: the longest ring of any plucked instrument — 6–10 s on the
  wire bass, 3–5 s gut, 2–3 s nylon; **no dampers exist** (the harpist
  damps by hand, so scores mostly let strings ring)
- **Release**: natural string decay; hand damping is an explicit technique
- **Vibrato**: none (no mechanism); expression comes from dynamics,
  arpeggio timing and pedal effects
- **Character**: lush, bell-warm, wide-spectrum "plucked strings in air" —
  the classical halo instrument; the gliss is a cascading water-wall

## Role in Arrangement

- Arpeggiated harmony pads (the classic harp backdrop under strings/winds)
- Glissando transitions + accents (up-gliss into a downbeat, out of a
  fermata)
- Melody in the mid register (gentle, folkish or lyrical solo lines)
- Countermelody filigree above sustained strings
- Cadential arpeggio flourishes (rising runs into cadences)
- NOT a bass foundation (wire strings are available but muddy fast in a
  mix; cello/double bass own the low register) and NOT a rhythmic strum
  voice (that's guitar/banjo)

## Synthesis Engines (musicom)

1. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
   **primary**. Plucked waveguide = the exact physical model (direct-plucked
   string, no bow, no bar). `loop_gain` **0.9985** — the HIGHEST of the
   plucked set (sitar 0.9975, koto 0.9970, banjo 0.9960) because harp
   strings are the longest and least-damped; `width` 0.55 for the wide
   47-string stereo image.
2. **ModalSynth** (`sound/synthesis/modal.py`) preset `'string'` — harmonic
   stack with moderate decay; the "clean harp" fallback. Custom
   `HARP_MODES` bank (near-harmonic, low decay rates 0.22–1.20) gives the
   true multi-second gut ring.
3. **PhaseModSynth** — cheap harp: sine carrier, mod ratio 2.0, depth 1.3,
   attack 0.003, release 1.8. Twangy, less lush.

## Production

- **Reverb**: hall 2.0–2.5 s — the harp is THE concert-hall instrument;
  a long tail sells the air around the ring (longest of the plucked set;
  compare koto room 1.0–1.5 s)
- **EQ**: cut ~250 Hz soundboard boom on the big resonant box; boost
  ~3.5 kHz for fingertip attack clarity; 10 kHz high shelf for treble
  shimmer and gliss sparkle (harp recordings are air-forward)
- **Delay**: not idiomatic; the long natural ring IS the delay
- **Pan**: center solo; ~0.3 right in classical orchestra seating
  (audience view) — the standard orchestral placement

## Verification

- GM46 → stem `trackXX_Orchestral_Harp.wav` (label matches, no quirk)
- FluidR3 preset 46 = "Harp" (verified from phdr chunk — one-word label vs
  the pipeline's "Orchestral Harp"; cosmetic only)
- Solo render passes 4–8 kHz spectral gate (round pluck, no comb buzz)
- Zero-drift: plucked units end flush at BAR (terminal landmark)
- **Treble rolloff quirk** (measured FluidR3 sweep, notes 12–108, 12/12
  audible, no gaps): the patch rolls off smoothly toward the treble —
  bass strings ~0.024 rms, top octave (≥ C6=84) ~0.0024–0.0037 (≈10×
  quieter, matching a real harp's thin nylon trebles). Composition jobs
  should use higher velocities (or doubled octaves) for melody above C6.

## Instrument.md companion

`harp.py` — importable constants. Registered in `instrument_registry.py`
(2026-09-14) as `Strings.harp.harp` → key `harp`, constant `HARP`.
