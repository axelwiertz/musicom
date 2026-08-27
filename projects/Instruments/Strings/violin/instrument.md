---
type: instrument
family: Strings
name: Violin
midi_program: 40
gms: "Violin"
range_min: 55
range_max: 103
solo_range: [67, 96]    # G3-E7 playable, melodic sweet spot D4-B5
role: [lead, countermelody, accent]
synthesis: [bowed, additive, modal]
---

# Violin

## MIDI / GM

- **Program**: 40 (GM1 Violin)
- **Channel**: any melodic channel (0-9); solo instrument
- **FluidSynth**: TimGM6mb.sf2 renders GM40 → solo violin with portamento cap

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 55–103 | G3–E7 | concert violin range |
| Sweet spot | 67–96 | G4–B5 | melodic focus, projects well |
| Low | 55–66 | G3–F#4 | dark, stringy, lacks projection |
| High | 97–103 | C6–E7 | piercing, fragile |

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Sustained (legato) | 70–90 | full note | smooth, steady bow |
| Staccato | 60–75 | 1/8–1/4 note | short, crisp, separated |
| Spiccato | 55–70 | very short | bouncing bow |
| Tremolo | 65–80 | 16th repetitions | rapid bow changes |
| Pizzicato | 50–65 | short | plucked, no bow |
| Accent/marcato | 85–100 | full note, strong attack | emphasized onset |
| Harmonics (natural) | 40–50 | sustained | airy, bell-like |
| Glissando | — | portamento between notes | slide (MIDI: bend) |

## Timbre DNA

- **Harmonic content**: strong fundamental + prominent 2nd/3rd harmonics, rich overtones up to 8+
- **Attack**: 10–30 ms (bow contact) — smooth, no clicks
- **Decay**: sustained (bow-driven, no natural decay while bowed)
- **Release**: 50–150 ms (bow lift)
- **Noise component**: bow scratch (transient, at attack)
- **Vibrato**: natural 5–7 Hz, ±0.2–0.5 semitone (pitch bend or synthesis param)

## Role in Arrangement

- Lead melody (sweet spot G4-B5)
- Countermelody (2nd violin/other voice)
- Accent/ornament (high register)
- NOT bass (no low register)
- NOT rhythm (sustained melodic voice)

## Synthesis Engines (musicom)

1. **BowedString** (`sound/synthesis/bowed.py`) — physical waveguide, best match
   - Fundamental present, bridge LPF (verify spectral, not argmax)
   - Use `freq = midi_to_freq(pitch)`; fix octave via `D = sr/(2*freq)`
2. **ModalSynth** preset `string` (`sound/synthesis/modal.py`) — pluck/attack, okay for pizzicato
3. **PhaseModSynth** — additive harmonics for synthetic string pad texture

## Production

- **Reverb**: hall/room, 1.5–3 s tail (solo); plate for pop
- **EQ**: high shelf boost above 4 kHz for air; cut 200–400 Hz boxiness
- **Delay**: none for legato; dotted 8th echo for pop lead lines
- **Pan**: center (solo) or wide (section)

## Verification (pop 5-part project)

- GM40 renders as `trackXX_Violin.wav` in RenderPipeline stems
- Bowed string: check fundamental PRESENT in spectrum (not global argmax — bridge LPF boosts harmonics)
