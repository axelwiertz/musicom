---
type: instrument
family: Woodwind
name: Flute
midi_program: 74
gms: "Flute"
range_min: 60
range_max: 96
solo_range: [67, 91]
role: [lead, countermelody, ornament, pad-ish]
synthesis: [additive, phase_mod, noise+filter]
---

# Flute

## MIDI / GM

- **Program**: 74 (GM1 Flute)
- **Channel**: melodic channel; monophonic, breathy
- **FluidSynth**: TimGM6mb.sf2 renders GM74 → flute. NOTE: RenderPipeline stems
  label program 74 as **Recorder** (GM list mismatch — see pop 5-part project)

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 60–96 | C4–C7 | concert flute |
| Low | 60–66 | C4–F#4 | warm, breathy, soft |
| Middle | 67–83 | G4–B5 | primary melodic register |
| High | 84–96 | C6–C7 | bright, piercing |

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Legato | 65–85 | full | smooth, connected |
| Staccato | 55–70 | 1/8–1/4 | light, crisp (tongued) |
| Flutter tongue | 60–75 | sustained | rolling effect |
| Breath tone | 40–55 | sustained | airy, soft |
| Accent | 85–100 | full | emphasized |
| Tremolo (trill) | 60–75 | fast alternation | ornament |

## Timbre DNA

- **Harmonic content**: fundamental strong, weak 2nd harmonic, stronger 3rd;
  breathy noise component above 8 kHz
- **Attack**: 30–80 ms (breath onset) — soft, non-percussive
- **Decay**: sustained (breath-driven)
- **Release**: 50–150 ms
- **Vibrato**: natural 5–6 Hz, moderate depth
- **Character**: airy, transparent, can be soft or piercing

## Role in Arrangement

- Lead melody (middle register)
- Countermelody (2nd flute / oboe pairing)
- Ornamentation (high register trills, runs)
- Pad-ish sustained tones (soft dynamics, low register)

## Synthesis Engines (musicom)

1. **PhaseModSynth** — flute-ish: carrier sine, mod ratio 1.0, depth 1–2,
   attack 0.05–0.1 (soft breath), release 0.1–0.2
2. **Additive** — sine + small 3rd harmonic + noise floor
3. **BowedString** — not ideal; use only for airy sustained approximation

## Production

- **Reverb**: hall 1.5–2.5 s (flute loves space)
- **EQ**: high shelf 8 kHz for breathiness; cut 300–500 Hz mud
- **Delay**: subtle dotted 8th for pop
- **Pan**: center or wide in pads

## Verification

- GM74 renders as `trackXX_Recorder.wav` in RenderPipeline stems (name quirk)
- Airy check: noise energy above 8 kHz present (breath component)
