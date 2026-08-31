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
# NEW (recommended): uniform Instrument objects via the registry
from instrument_registry import VIOLIN, PIANO, TRUMPET, by_name, by_program

composer.add_voice("Violin", program=VIOLIN.midi_program, channel=0)
inst = by_name("flute")          # → FLUTE
inst = by_program(56)            # → TRUMPET (GM 56)
inst.in_sweet_spot(72)           # True if 72 is in the melodic sweet spot
```

```python
# LEGACY (still works): raw constants from the per-instrument modules
from Strings.violin.violin import MIDI_PROGRAM, SWEET_SPOT
from Keys.piano.piano import midi_to_freq
from Percussion.drum_kit.drum_kit import KIT, beat_pattern
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
│   ├── bassoon/
│   └── saxophone/
├── Keys/
│   ├── piano/
│   └── organ/
├── Guitar/
│   └── acoustic/
└── Percussion/
    └── drum_kit/
```

Current instruments (17): Violin, Viola, Cello, Double Bass, Piano, Church
Organ, Trumpet, Trombone, French Horn, Tuba, Flute, Oboe, Clarinet, Bassoon,
Alto Saxophone, Acoustic Guitar, Drum Kit.

## Musicom Integration

Instrument definitions feed into:
1. **UnitMatrixComposer** — program selection, range constraints (`VIOLIN.midi_program`)
2. **Synthesis engines** — BowedString, ModalSynth, PhaseModSynth presets
3. **Arrangement rules** — register zones, role assignments (`orchestrator.py`)
4. **Production chains** — per-instrument DSP (reverb, EQ, compression)

## Registry

Auto-generated — run `python instrument_registry.py` to regenerate:
```bash
cd /opt/data/projects/Instruments && /opt/data/micromamba/envs/musicom/bin/python instrument_registry.py
```
The canonical table lives in `registry.md` (kept in sync manually) and
`instrument_registry.registry_table()` (generated from code).

## Status

- [x] Registry + Instrument objects (16 instruments loaded, lookup by name/program)
- [x] Trumpet program corrected to GM 56 (was 57 = Trombone)
- [x] String delay formula corrected (`D = sr/freq`, not `sr/(2*freq)`)
- [x] Orchestrator (role → instrument mapping)
- [x] Oboe, Bassoon, Saxophone (woodwind family complete)
- [x] Church Organ (keys family, GM19, additive engine — 2026-08-31)
- [ ] Synth Pad, Harpsichord, Electric Guitar (listed in roadmap)
- [ ] Drum Kit expansion beyond GM mapping
