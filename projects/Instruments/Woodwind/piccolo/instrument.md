---
type: instrument
family: Woodwind
name: Piccolo
midi_program: 72
gms: "Piccolo"
range_min: 72
range_max: 108
solo_range: [79, 101]
role: [lead, melody, ornament, accent, countermelody]
synthesis: [phase_mod, air_pipe, additive]
---

# Piccolo

The orchestral piccolo (octave flute), the highest-pitched voice of the standard symphony orchestra woodwind section. Half the length of the concert Western concert flute, pitched exactly one octave higher.

## MIDI / GM

- **Program**: 72 (GM1 Piccolo, 0-indexed GM 72 / 1-indexed GM #73)
- **Channel**: Melodic channel (0–8, 10–15)
- **RenderPipeline stem label**: `trackXX_Piccolo.wav` ✓ (GM_PROGRAMS[72] = "Piccolo", FluidR3 preset 72 = "Piccolo" — exact match, no quirk)
- **SoundFont (FluidR3_GM.sf2)**: Preset 72 "Piccolo" provides crisp high woodwind embouchure chiff with clean sustain and natural vibrato up to C8.

## Range

The piccolo sounds one octave higher than written in standard orchestral sheet music (transposing octave aerophone). In MIDI and musicom compositions, concert sounding pitch is used directly:

| Zone | MIDI | Pitches | Character & Register |
|---|---|---|---|
| Full range | 72–108 | C5–C8 | Full playable & soundfont compass |
| Low | 72–79 | C5–G5 | Quiet, breathy, dark, easily covered; hollow tone |
| Middle | 80–91 | Ab5–G6 | Clear, lyrical, singing, primary expressive melodic zone |
| High | 92–101 | Ab6–F7 | Brilliant, piercing, cuts effortlessly through full orchestral tutti |
| Altissimo | 102–108 | F#7–C8 | Shrill, screaming, military marches, storm effects, high shrieks |

- **Sweet Spot**: 84–96 (C6–C7, ~1046 Hz – ~2093 Hz) — bright, projecting, agile, melodic brilliance without excessive shrillness.

## Articulations

| Technique | Velocity | Duration | Character |
|---|---|---|---|
| Legato | 65–80 | 1.0 | Fluid, seamless woodwind singing lines |
| Staccato | 60–75 | 0.25 | Pointed, needle-sharp, crisp double/triple tonguing |
| Accent | 90–105 | 0.85 | Piercing sforzando attack, instantaneous transient spike |
| Flutter tongue | 65–80 | 1.0 | Rapid rolling 'frullato' throat/tongue flutter |
| Breath tone | 45–55 | 0.9 | Airy whisper in the lower register |
| Trill | 65–75 | 0.5 | Rapid alternation, sparkling avian ornamentation |

## Timbre DNA

- **Harmonic spectrum**: Dominated by the fundamental and second harmonic, with subtle high-order chiff noise generated at the embouchure hole lip. The high fundamental frequency (>1 kHz) leaves wide inter-harmonic spacing, giving a clean, luminous spectral footprint.
- **Envelope**: Fast attack (30–50 ms), instantaneous breath response due to the short 32 cm acoustic air column (half the acoustic inertia of a standard C flute).
- **Vibrato**: High-register diaphragm/throat vibrato (5.5–6.5 Hz) with moderate pitch deviation.

## Role in Arrangement

- **Lead / Melody**: Top-line melody doubling the 1st violins or concert flutes an octave higher to add sheen and radiance.
- **Ornamentation**: Bird calls (Rossini, Beethoven Pastoral, Saint-Saëns Carnival), high arpeggio runs, trills, mordents.
- **Accent / Climax**: High sforzandi and military accents that puncture thick brass and percussion textures.
- **Countermelody**: Rapid descant counter-lines woven high above brass and string themes.

## Synthesis Engines (musicom)

1. **PhaseModSynth (`phase_mod`)**:
   - Carrier: sine, Modulator: sine
   - Mod ratio: 1.0, Mod depth: 1.2
   - Fast attack (0.04 s), short release (0.10 s)
   - Accurately generates the sweet, focused flue pipe tone without artificial harshness.

2. **AirPipe (`air_pipe`)**:
   - Cylindrical open pipe aerophone physical model (`stopped=False`).
   - `length_scale=0.5` (half length of concert flute).
   - Higher jet pressure (`pressure=0.65`) modeling narrow bore overblowing.

3. **AdditiveSynth (`additive`)**:
   - Dominant f0 (1.0), gentle 2nd harmonic (0.35), weak 3rd harmonic (0.12), plus 8 kHz+ high shelf air noise.

## Production Defaults

- **Reverb Tail**: 2.2 s (room/hall reverb allows sparkling piccolo transients to float cleanly above rhythm sections).
- **EQ**:
  - Body: +2.0 dB at 1.2 kHz (adds roundness and weight to mid-register notes).
  - Presence: +3.0 dB at 3.5 kHz (bite and articulation definition).
  - Air: +2.0 dB shelf at 10 kHz (embouchure chiff and air shimmer).
  - High-pass: sharp 18 dB/oct rolloff below 450 Hz to eliminate rumble/stage noise.
- **Pan**: +0.15 (standard orchestral woodwind layout, positioned just to the right of concert flutes).

## FluidSynth & Pipeline Behavior

- **GM Program**: 72
- **RenderPipeline Stem**: `trackXX_Piccolo.wav` (pipeline `GM_PROGRAMS[72] == "Piccolo"`).
- **FluidR3_GM.sf2**: Preset 72 is named `"Piccolo"` with full velocity and pitch range verified (audible across C5–C8, RMS 0.048–0.103 with zero dropouts).
