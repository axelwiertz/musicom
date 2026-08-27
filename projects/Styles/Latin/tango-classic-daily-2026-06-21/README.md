# Daily Pattern Composition: Classic Tango

**Date:** 2026-06-21  
**Genre:** Latin / Tango (Classic)  
**Framework:** Musicom UnitMatrix  
**BPM:** 128  
**Key:** A Harmonic Minor  
**Meter:** 4/4  
**Length:** 2 bars

---

## UnitMatrix Structure

| Row | Instrument | MIDI Program | Role |
|-----|-----------|-------------|------|
| 1 | Double Bass | 43 (Acoustic Bass) | Marcato quarter-note pulse, roots & fifths |
| 2 | Piano | 1 (Acoustic Grand) | Chordal punctuation on 3-3-2 syncopation |
| 3 | Bandoneon | 23 (Harmonica surrogate) | Dramatic melody w/ chromatic passing tones |
| 4 | Percussion | Channel 9 | Side stick (marcato), kick (downbeats), hi-hat (eighth-note pulse) |

## Metrical Gravity Profile

Gravity values across 8 eighth-notes per bar:

```
eighth:  1   2   3   4   5   6   7   8
gravity: 1.0 0.3 0.5 0.9 0.4 0.9 0.3 0.8
```

- **Beat 1**: Strongest downbeat (bass + kick + stick + piano)
- **Beat 4** (3rd eighth): 3-3-2 group accent (second group start)
- **Beat 6** (5th eighth): 3-3-2 group accent (third group start)
- **Beat 8** (7th eighth): Anticipatory, leading into next bar

## Rhythm Pattern: 3-3-2 Syncopation

The signature tango 3-3-2 rhythm patterns piano and side-stick hits:

```
| X . . | X . . | X . |  (eighth-note grid: accented at 0, 3, 6)
```

Repeated twice across the 2-bar phrase (accents at beats 0, 1.5, 3, 4, 5.5, 7).

## Harmonic Progression

- **A section**: Am7 (A-C-E-G) — tonic vamp
- Characteristic tango dynamics: strong marcato attacks, sharp releases, dramatic leaps

## Files

- `composition.mid` — Standard MIDI file (4 tracks + meta)
- `composition.ogg` — OGG Vorbis audio render (FluidSynth, FluidR3_GM SoundFont)
- `src/generate.py` — Python generator script using mido + fluidsynth