---
type: instrument
family: Woodwind
name: Clarinet
midi_program: 71
gms: "Clarinet"
range_min: 52
range_max: 96
solo_range: [60, 84]    # E3-C7 playable, solo sweet spot C4-C6
role: [lead, countermelody, harmony, accent]
synthesis: [phase_mod, additive, modal]
---

# Clarinet

## MIDI / GM

- **Program**: 71 (GM1 Clarinet)
- **Channel**: any melodic channel (0-9); solo instrument
- **FluidSynth**: TimGM6mb.sf2 renders GM71 → Clarinet (no quirk; stem label matches)

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 52–96 | E3–C7 | Bb clarinet, sounding pitch |
| Sweet spot | 65–83 | F4–B5 | clarion register, warm singing, projects well |
| Low (chalumeau) | 52–66 | E3–G#4 | dark, woody, breathy, quiet |
| Mid (throat+clarion) | 67–83 | G4–B5 | most characteristic, flexible dynamics |
| High (altissimo) | 84–96 | C6–C7 | piercing, bright, harder to control |

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Legato | 70–90 | full note | smooth, reed-driven, near-flute legato |
| Tenuto | 60–75 | ~0.9 note | slight separation, singing |
| Staccato | 55–70 | 1/8–1/4 note | short, crisp, tongue stop |
| Accent/marcato | 85–100 | full note, strong onset | emphasized reed attack |
| Flutter-tongue | 60–75 | full note | airy, buzzing, rough |
| Glissando | 65–80 | smear between notes | Rhapsody-style rise, rare |

## Timbre DNA

- **Harmonic content**: strong odd harmonics (cylindrical bore, closed at one end) — fundamental + 3rd/5th prominent; clarion register jumps an octave+twelfth
- **Attack**: 30–80 ms (reed onset) — softest onset of woodwinds, no clicks
- **Decay**: sustained (breath-driven, no natural decay)
- **Release**: 50–120 ms (tongue stop / breath lift)
- **Noise component**: breath hiss (low level, throughout), key clack (transient, rare in synth)
- **Vibrato**: not native (single reed) — 0 or slight 4–5 Hz for effect; airy tremolo possible

## Role in Arrangement

- Lead melody (clarion sweet spot F4-B5)
- Countermelody (against flute or strings)
- Harmony (doubling 3rds/6ths, woodwind section blend)
- Accent/ornament (fast passage work, altissimo effects)
- NOT bass (low register too quiet/breathy)
- NOT rhythm (sustained melodic voice)

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — best match
   - Saw carrier + mod → odd-harmonic reed spectrum
   - `freq = midi_to_freq(pitch)`; attack 0.05 s, release 0.10 s
2. **Additive** (`sound/synthesis/additive.py`) — odd partials 1:3:5, slow attack for legato
3. **ModalSynth** (`sound/synthesis/modal.py`) — short pluck/attack for staccato effects

## Production

- **Reverb**: hall/room, 1.2–2 s tail (solo); keep articulation clarity
- **EQ**: cut 400–500 Hz nasality; boost ~3 kHz reed sparkle; high shelf for air
- **Delay**: none for classical legato; dotted 8th echo for pop/jazz lines
- **Pan**: center (solo) or slight off-center in section

## Verification

- GM71 renders as `trackXX_Clarinet.wav` in RenderPipeline stems (label matches, no quirk)
- PhaseModSynth: check odd-harmonic spectrum (fundamental + 3rd/5th prominent)
