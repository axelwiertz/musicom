---
type: instrument
family: Brass
name: Trumpet
midi_program: 57
gms: "Trumpet"
range_min: 54
range_max: 86
solo_range: [60, 84]
role: [lead, accent, fanfare, countermelody]
synthesis: [phase_mod, subtractive, additive]
---

# Trumpet

## MIDI / GM

- **Program**: 57 (GM1 Trumpet)
- **Channel**: melodic channel; monophonic instrument (one note at a time)
- **FluidSynth**: TimGM6mb.sf2 renders GM57 → trumpet

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 54–86 | F#3–D6 | practical trumpet range |
| Low | 54–65 | F#3–F4 | dark, less projection |
| Middle | 66–79 | F#4–G5 | main playing register, bright |
| High | 80–86 | G#5–D6 | lead, piercing, powerful |

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Sustained | 75–95 | full | even tone |
| Staccato | 60–75 | 1/8–1/4 | crisp articulation |
| Marcato | 90–105 | full, accented | emphasized onset |
| Sforzando | 100–115 | strong attack, decay | dramatic accent |
| Muted | 50–70 | any | nasal, softer (GM: no mute) |
| Fall (drop) | — | end of note | gliss down (bend) |
| Rip (attack) | — | very fast attack | rapid slide up |

## Timbre DNA

- **Harmonic content**: odd harmonics strong (2, 3, 4 prominent); bright, brassy
- **Attack**: 10–40 ms (lip/valve)
- **Decay**: sustained while blown
- **Release**: 30–80 ms
- **Vibrato**: lip vibrato 5–6 Hz
- **Character**: can sound aggressive (fanfare) or smooth (lyrical)

## Role in Arrangement

- Lead melody (middle-high register)
- Accent/hits (fanfare figures, stabs)
- Countermelody (2nd trumpet)
- NOT bass, NOT pad (sustained chord tones possible but exhausting)

## Synthesis Engines (musicom)

1. **PhaseModSynth** — FM brass: carrier saw/square, mod ratio 1.0–2.0,
   mod_depth 3–5, fast attack 0.01–0.03, medium release 0.05–0.15
2. **SubtractiveVoice** — saw + lowpass 2000–4000 Hz, resonance 0.3–0.5
3. **Additive** (SoundWave) — odd-harmonic stack (0.5, 0.3, 0.2, 0.1...)

## Production

- **Reverb**: room/small hall 0.8–1.5 s (avoid drowning)
- **EQ**: presence 3–5 kHz; cut 500 Hz mud
- **Compression**: moderate 3:1 for consistency
- **Delay**: none (dry lead) or subtle

## Verification

- GM57 renders as `trackXX_Trumpet.wav` in RenderPipeline stems
- FM brass: check harmonic energy ≥ 30% above fundamental (brightness test)
