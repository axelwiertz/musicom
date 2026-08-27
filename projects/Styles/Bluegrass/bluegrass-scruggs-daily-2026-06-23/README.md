# Daily Pattern Composition: Bluegrass (Scruggs-Style Breakdown)

**Date:** 2026-06-23  
**Genre:** Bluegrass / Appalachian / Scruggs-Style Bluegrass Breakdown  
**Framework:** Musicom UnitMatrix  
**BPM:** 140 (cut time / 2/2)  
**Key:** G Major (Mixolydian flavor with flat-7)  
**Meter:** 2/2 (cut time)  
**Length:** 2 bars (4 half-note beats)

---

## UnitMatrix Structure

| Row | Instrument | MIDI Program | Role |
|-----|-----------|-------------|------|
| 1 | Banjo (Scruggs Forward Roll) | 105 (Banjo) | Continuous 8th-note forward roll — G major pentatonic pattern with thumb-index-middle cycle |
| 2 | Fiddle | 40 (Violin) | Melodic line with open-string drones, slides, and Mixolydian flat-7 (F natural) color |
| 3 | Mandolin (Chop) | 104 (Mandolin) | Muted chord chops on backbeats (2 & 4 — positions 1.5 and 3.5 in cut time) |
| 4 | Guitar (Bass Runs) | 25 (Acoustic Guitar) | Walking bass runs with scalar passing tones between chord changes |
| 5 | Upright Bass | 34 (Acoustic Bass) | Two-beat feel: root on beat 1, fifth on beat 3 (half-note pulse) |

## Metrical Gravity Profile

Cut-time feel across 2 bars (8 eighth-note positions per bar, 16 total):

```
eighth:  1   2   3   4   |   1   2   3   4
           (cut time: each = half-note beat)
gravity: 1.0 0.2 0.8 0.2 |   0.7 0.3 0.6 0.2
```

- **Beat 1 (eighth pos 0, 8)**: Strongest half-note downbeat — banjo thumb accented, bass root, fiddle entrance
- **Beat 2 (eighth pos 2, 10)**: Secondary half-note pulse — banjo thumb accent, bass fifth, mandolin chop rest
- **Backbeats (eighth pos 1.5, 3.5, 5.5, 7.5)**: Mandolin chop punctuation — the defining bluegrass backbeat
- **Banjo roll**: Continuous 8th notes throughout with thumb-index-middle cycle creating forward drive

## Rhythm Pattern: Scruggs Forward Roll

```
8th-note: 1   &   2   &   3   &   4   &  |  1   &   2   &   3   &   4   &
Banjo:    X   x   .   X   x   .   X   x  |  X   x   .   X   x   .   X   x
           (thumb-index-middle-thumb-index-middle-thumb-index cycle)
G-chord:  G   D   B   G   D   B   G   C  |  A   E   D   A   E   D   G   B

Mandolin: .   X   .   X   .   X   .   X  |  .   X   .   X   .   X   .   X
           (chops on backbeats 2 & 4 — G on bar 1, D7 on bar 2)

Bass:     G . . . . . . D | D . . . G . D .
           (root on 1, fifth on 3 — half-note two-beat feel)
```

The characteristic Scruggs "drive" comes from the continuous eighth-note forward roll — thumb (accent) on each half-note beat, index and middle filling the subdivision. The mandolin chop on backbeats creates the signature bluegrass rhythmic punctuation.

## Harmonic Framework

- **G Major / Mixolydian**: G A B C D E F G (flat-7 F natural is the characteristic bluegrass inflection)
- **Harmony**: G (I) | D7 (V7) | D7 (V7) | G (I)
- **Bass movement**: G2–D2–G2 / D2–D3 / G2–D2 (two-beat root-fifth pattern)
- **Guitar walk**: G3–A3–B3–C4–D4–B3–G3–A3 / D4–C#4–D4–C4–B3–A3–G3–A3–B3–G3

## Metrical Gravity Analysis

The bluegrass cut-time feel distributes weight primarily on the two half-note pulses (beats 1 and 3), with the mandolin chop creating a backbeat counter-rhythm on beats 2 and 4. Unlike swung genres, bluegrass uses **straight eighth notes** throughout — the drive comes from relentless forward motion of the banjo roll, not from swing feel.

The characteristic bluegrass "high lonesome" quality comes from:
1. Open-string drone resonance (banjo 5th string, fiddle open strings)
2. Mixolydian flat-7 (F natural) creating a modal, Appalachian tonality
3. Backbeat mandolin chops providing rhythmic anchor against continuous banjo roll

## Files

- `composition.mid` — Standard MIDI file (meta + 5 instrument tracks)
- `composition.ogg` — OGG Vorbis audio render (FluidSynth, FluidR3_GM SoundFont)
- `generate.py` — Generate script (UnitMatrix framework)
- `README.md` — This file
- `verify.py` — MIDI verification utility