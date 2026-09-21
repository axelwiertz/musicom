---
type: instrument
family: Keys
name: Celesta
midi_program: 8
gms: "Celesta"
range_min: 48
range_max: 108
solo_range: [60, 96]
role: [lead, melody, ornament, arpeggio, countermelody, accent]
synthesis: [modal, karplus, phase_mod]
---

# Celesta

The orchestral celesta (keyboard metallophone), patented in 1886 by Auguste Mustel in Paris. It consists of a piano-like keyboard action where felt-covered hammers strike tuned steel plates suspended over wooden resonator boxes, producing a tone of celestial purity, warmth, and ethereal delicacy. Made famous by Pyotr Ilyich Tchaikovsky in the *Dance of the Sugar Plum Fairy* from *The Nutcracker* (1892).

## MIDI / GM

- **Program**: 8 (GM1 Celesta, 0-indexed GM 8 / 1-indexed GM #9)
- **Channel**: Melodic channel (0–8, 10–15)
- **RenderPipeline stem label**: `trackXX_Celesta.wav` ✓ (GM_PROGRAMS[8] = "Celesta", FluidR3 preset 8 = "Celesta" — exact match, no quirk)
- **SoundFont (FluidR3_GM.sf2)**: Preset 8 "Celesta" provides warm, round bell-chime tones across C3–C8 with natural room acoustics and decay.

## Range

In standard orchestral notation, the celesta is written one octave lower than it sounds (sounding 8va alta, transposing keyboard). In musicom compositions and MIDI files, sounding concert pitch is used directly:

| Zone | MIDI | Pitches | Character & Register |
|---|---|---|---|
| Full range | 48–108 | C3–C8 | Full 5-octave modern concert instrument |
| Low | 48–59 | C3–B3 | Dark, bell-like, resonant steel hum coupled to box |
| Mid-Low | 60–71 | C4–B4 | Mellow, warm, round chime |
| Mid-High | 72–83 | C5–B5 | Sweet, singing crystalline tone (*Sugar Plum Fairy* core) |
| High | 84–95 | C6–B6 | Sparkling, brilliant, ethereal chime |
| Altissimo | 96–108 | C7–C8 | Delicate, pinprick silver droplets |

- **Sweet Spot**: 72–96 (C5–C7, ~523 Hz – ~2093 Hz) — purest celestial chime, optimal balance between wooden resonator body and steel plate brilliance.
- **Solo Range**: 60–96 (C4–C7) — full expressive melodic and arpeggio range.

## Articulations

| Technique | Velocity | Duration | Character |
|---|---|---|---|
| Normale | 75–85 | 1.0 | Standard felt hammer stroke with natural decay |
| Staccatissimo | 70–80 | 0.3 | Pointillistic, sparkling staccato drop |
| Legato | 65–75 | 1.1 | Flowing melodic or arpeggio phrasing, pedal sustained |
| Accent | 90–105 | 0.9 | Brilliant sforzato chime highlighting key melodic turns |
| Pianissimo | 45–55 | 1.0 | Ethereal, mysterious whisper chime |
| Arpeggio | 68–78 | 0.85 | Fluid rolled chord across multiple octaves |

## Timbre DNA

- **Harmonic spectrum**: The steel plates have inharmonic flexural modes (~1.0, ~2.76, ~5.40, ~8.90), but the wooden hollow box resonator beneath each plate amplifies the fundamental and dampens high clatter, producing a sound far warmer, rounder, and less piercing than the orchestral glockenspiel (which has no resonators and is struck with metal/hard plastic mallets).
- **Attack transient**: Soft felt hammer strike gives a subtle, cushioned onset without harsh transient click.
- **Envelope**: Instant strike followed by exponential decay (~1.2–2.5 s depending on register and damper pedal engagement).

## Role in Arrangement

- **Lead / Melody**: Fragile, magical top-line melody (*Nutcracker*, John Williams' *Hedwig's Theme* from *Harry Potter*).
- **Arpeggio / Arabesque**: Cascading broken chords weaving shimmering filigree around woodwinds and strings.
- **Ornamentation**: Shimmering grace notes, mordents, trills, and high ostinatos.
- **Accent**: Sparkling punctuation marking harmonic arrivals or cadence resolutions.
- **Countermelody**: Delicate descant voice floating above slower string themes.

## Synthesis Engines (musicom)

1. **ModalSynth (`modal`)**:
   - Primary physical modeling engine. Impulse-excited resonator bank (`sound/synthesis/modal.py`).
   - Built-in stock preset: `'bell'` provides inharmonic metallic partials.
   - Custom mode bank: `CELESTA_MODES` (ratios 1.0, 2.76, 5.40, 8.90 with decay rates 3.2, 4.8, 6.5, 8.5) captures the hollow wooden resonator coupling and softened steel plate modes.

2. **Karplus-Strong (`karplus`)**:
   - High loop gain (`loop_gain: 0.9970`) provides realistic bell-chime resonance decay (~1.5 s).
   - Stereo width 0.40 models keyboard spread.

3. **PhaseModSynth (`phase_mod`)**:
   - Soft FM bell chime: sine carrier + sine modulator at ratio 2.76, modest depth 1.1, fast attack (3 ms), decay 1.2 s.

## Production Defaults

- **Reverb Tail**: 2.4 s (celesta blooms in rich, warm hall acoustics; short reverb sounds dry and toy-like).
- **EQ**:
  - Body: +1.5 dB at 500 Hz (resonator box body and fullness).
  - Presence: +1.8 dB at 4000 Hz (felt hammer stroke definition).
  - Air: +2.2 dB at 11000 Hz (silver shimmer and sparkle).
- **Pan**: +0.25 (orchestral stage placement: slightly right of center, near percussion/harp).

## FluidSynth & Pipeline Behavior

- **GM Program**: 8
- **RenderPipeline Stem**: `trackXX_Celesta.wav` (pipeline `GM_PROGRAMS[8] == "Celesta"`).
- **FluidR3_GM.sf2**: Preset 8 is `"Celesta"`, fully responsive from C3 to C8 (RMS 0.063–0.113 across full compass, no dropouts or velocity jumps).
