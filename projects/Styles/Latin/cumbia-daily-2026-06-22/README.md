# Daily Pattern Composition: Colombian Cumbia

**Date:** 2026-06-22  
**Genre:** Latin / Colombian Cumbia  
**Framework:** Musicom UnitMatrix  
**BPM:** 100  
**Key:** D Dorian (D E F G A B C D)  
**Meter:** 2/4  
**Length:** 2 bars

---

## UnitMatrix Structure

| Row | Instrument | MIDI Program | Role |
|-----|-----------|-------------|------|
| 1 | Bombo (Bass) | 34 (Acoustic Bass) | Root-fifth bass line marking downbeats and off-beats |
| 2 | Llamador | 45 (Low Tom, ch.9) | Steady eighth-note pulse — the rhythmic backbone |
| 3 | Alegre | 63 (High Conga, ch.9) | Syncopated off-beat accents on & of each beat |
| 4 | Maraca | 70 (Maracas, ch.9) | Continuous 16th-note shuffle/shaker texture |
| 5 | Accordion | 22 (Accordion) | D Dorian melodic motif with characteristic cumbia phrasing |

## Metrical Gravity Profile

Gravity values across 8 eighth-notes (2 bars of 2/4):

```
eighth:  1    &    2    &    1    &    2    &
gravity: 1.0  0.6  0.8  0.7  1.0  0.6  0.8  0.7
```

- **Beat 1 (eighth 1, 5)**: Strongest downbeat — bass root, llamador, maraca all align
- **Beat 2 (eighth 3, 7)**: Secondary accent — bass off-beat, llamador pulse continues
- **Off-beats (& of 1, & of 2)**: Alegre syncopations drive the forward motion
- **Maraca**: Sustained 16th-note texture with slight accent on off-beat eighth positions (cumbia swing)

## Rhythm Pattern: Cumbia Clave Feel

```
Llamador: | X   X   X   X   X   X   X   X  |  (steady eighth notes)
Alegre:   | .   X   .   X   .   X   .   X  |  (off-beat accents)
Maraca:   | X X X X X X X X X X X X X X X X|  (continuous 16th notes)
Bombo:    | X   X   X   X   X   X   X   X  |  (root movement, varied velocity)
```

The characteristic cumbia "swing" comes from the alegre hitting the upbeats against the llamador's steady pulse, while the maraca fills the sixteenth-note grid with a slightly lifted feel on positions 2 and 6 of each 4-sixteenth group.

## Harmonic Framework

- **D Dorian mode**: D E F G A B C D
- **Harmony**: Dm7 (D-F-A-C) with G7 (G-B-D-F) passing implications
- **Bass movement**: D2–D2–D2–D2 / E2–E2–D2–D2 (root pedal with E passing tone in bar 2)

## Files

- `composition.mid` — Standard MIDI file (meta + 5 instrument tracks)
- `composition.ogg` — OGG Vorbis audio render (FluidSynth, FluidR3_GM SoundFont)
- `README.md` — This file
