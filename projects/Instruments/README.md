# Instruments Reference — Musicom-Compatible Format

Structured instrument definitions for use in musicom compositions.

## Purpose

Each instrument folder contains a `instrument.md` reference file with:
- MIDI program mapping (GM numbers)
- Pitch range (MIDI min/max, register zones)
- Articulation catalog (sustain, staccato, special techniques)
- Timbre DNA (harmonic content, ADSR characteristics)
- Arrangement roles (bass, lead, pad, accent)
- Synthesis engine recommendations (which musicom engine to use)
- FluidSynth/SF2 behavior notes

## Usage in Compositions

```python
from projects.Instruments.Strings.violin import VIOLIN

# Use in UnitMatrixComposer
composer.add_voice("Violin", program=VIOLIN.midi_program, channel=0)

# Use in synthesis
from sound.synthesis import BowedString
bow = BowedString(sample_rate=44100)
audio = bow.render_note(freq=440.0, duration=1.0)
```

## Structure

```
Instruments/
├── Strings/
│   ├── violin/
│   │   ├── instrument.md
│   │   └── violin.py (Python constants)
│   ├── viola/
│   ├── cello/
│   └── double_bass/
├── Brass/
│   ├── trumpet/
│   ├── trombone/
│   ├── french_horn/
│   └── tuba/
├── Woodwind/
│   ├── flute/
│   ├── clarinet/
│   ├── oboe/
│   └── bassoon/
├── Keys/
│   ├── piano/
│   ├── organ/
│   └── synth_pad/
├── Guitar/
│   ├── acoustic/
│   └── electric/
└── Percussion/
    └── drum_kit/
```

## Musicom Integration

Instrument definitions feed into:
1. **UnitMatrixComposer** — program selection, range constraints
2. **Synthesis engines** — BowedString, ModalSynth, PhaseModSynth presets
3. **Arrangement rules** — register zones, role assignments
4. **Production chains** — per-instrument DSP (reverb, EQ, compression)

## Status

- [x] Structure created
- [ ] Violin (Strings)
- [ ] Piano (Keys)
- [ ] Trumpet (Brass)
- [ ] Flute (Woodwind)
- [ ] Acoustic Guitar
- [ ] Drum Kit (expand beyond GM mapping)
