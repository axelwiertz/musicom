---
type: instrument
family: Guitar
name: Acoustic Guitar
midi_program: 25
gms: "Acoustic Guitar (nylon)"
range_min: 40
range_max: 84
solo_range: [48, 76]
role: [harmony, rhythm, strum, arpeggio, accompaniment]
synthesis: [modal, additive, karplus-strong]
---

# Acoustic Guitar

## MIDI / GM

- **Program**: 25 (GM1 Acoustic Guitar nylon); steel = 26 (GM2, not in MidiInstrument enum)
- **Channel**: any channel; polyphonic (6 strings)
- **FluidSynth**: TimGM6mb.sf2 renders GM25 → nylon guitar

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 40–84 | E2–C6 (standard tuning, 6 strings) |
| Bass strings | 40–47 | E2–B2 | low E, A, D strings |
| Middle | 48–59 | E3–B3 | G, B strings |
| High | 60–84 | E4–C6 | high E string + frets |

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Strum (full chord) | 60–85 | 1/8–1/2 | multiple strings, pluck |
| Arpeggio (fingerpick) | 55–75 | 1/8–1/4 | individual strings |
| Pizzicato (muted) | 40–55 | short | palm-muted, damped |
| Hammer-on/pull-off | 65–80 | legato slur | smooth connection |
| Slide | — | gliss | portamento between frets |
| Percussive strum | 70–90 | very short | attack noise + chord |

## Timbre DNA

- **Harmonic content**: fundamental + decaying harmonics; string body resonance
- **Attack**: 1–10 ms (pick/plectrum) — percussive but softer than piano
- **Decay**: exponential, 2–8 s (nylon longer sustain)
- **Release**: natural decay (no sustain control)
- **Noise**: pick scrape, fret buzz
- **Character**: warm, woody, organic

## Role in Arrangement

- Rhythm (strummed chords, 8th/16th patterns)
- Harmony (fingerpicked arpeggios)
- Accompaniment (folk, pop, singer-songwriter)
- NOT lead in loud mixes (lacks projection)

## Synthesis Engines (musicom)

1. **ModalSynth** preset `string` (decay 4–5) — closest physical model
2. **Additive** — plucked string approximation: decaying harmonic stack
3. **Karplus-Strong** — if implemented; decays <1s, fine for plucked

## Production

- **Reverb**: room 0.5–1.0 s (intimate)
- **EQ**: presence 2–5 kHz; cut 200–300 Hz mud; high shelf for sparkle
- **Compression**: gentle 2:1 for consistent strumming
- **Pan**: slight L/R for double-tracked guitars

## Verification

- GM25 renders as `trackXX_Acoustic_Guitar_nylon.wav` in RenderPipeline stems
- Pluck check: fast attack + exponential decay, no sustain plateau
