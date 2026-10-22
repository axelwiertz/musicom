# 255-blues-vuza-hocket

**Vuza Tiling Canon Composition (Method 111) — Blues**

A 12-bar blues in E major whose rhythmic engine is a **Vuza tiling canon**
(`A ⊕ B = ℤ₇₂`): a 12-onset rhythmic motif is played verbatim by 6 entry
voices at offsets that tile the cyclic group exactly once. The result is a
**perfect hocket** — all 72 eighth-note slots are struck exactly once, zero
collisions, zero gaps — a gapless, collision-free interlocking stream across
six timbres.

| | |
|---|---|
| Style | Blues |
| Method | 111 Vuza Tiling Canon Composition (VTCC) — **concrete**, Rules-Based, Grid-Locked |
| Form | blues-12 (12 bars) |
| Key | E major (ionian) — E F♯ G♯ A B C♯ D♯ |
| Tempo | 112 BPM, 4/4, 480 TPB (bar = 1920, 8th = 240, 16th = 120) |
| Progression | I I I I · IV IV · I I · V · IV · I V |

## The canon (n = 72, aperiodic = true Vuza / RCMC)

```
motif A  = {0, 1, 5, 6, 12, 25, 29, 36, 42, 48, 49, 53}   (12 onsets)
entries B = {0, 8, 16, 18, 26, 34}                         (6 voices)
A ⊕ B = ℤ₇₂  (verified: tiles, both factors aperiodic)
```

Each entry voice plays the 12-onset motif shifted by its offset; the 72 onsets
span 9 bars of eighth notes without a single collision. The last 3 bars are the
blues turnaround, where the hocket clears into a held V–IV–I triad.

## Voices (9)

| Voice | Instrument | GM program | Channel | Role |
|---|---|---|---|---|
| Lead | Harmonica | 22 | 0 | chord-tone arpeggio melody |
| E0 | Clean Electric Guitar | 27 | 1 | hocket entry 0 |
| E1 | Electric Piano 2 | 5 | 2 | hocket entry 1 |
| E2 | Drawbar Organ | 16 | 3 | hocket entry 2 |
| E3 | Vibraphone | 11 | 4 | hocket entry 3 |
| E4 | Steel Acoustic Guitar | 25 | 5 | hocket entry 4 |
| E5 | Marimba | 12 | 6 | hocket entry 5 |
| Bass | Electric Bass | 33 | 7 | walking bass (quarter grid) |
| Drums | Drum Kit | — | 9 | shuffle backbeat |

## Two-phase architecture

- **Phase 1** (`-phase1.mid`): the raw 72-onset hocket flattened to one voice,
  scale-mapped pitch (NOT chord-tone quantized), eighth-note slots. No harmony.
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): the hocket split over 6 entry
  voices, chord-tone quantized per bar against the I–IV–V progression, 8th/16th
  grid snap, harmonica lead + walking bass + shuffle drums, voice-leading
  optimization, zero-drift gate. Dual-version export (grid-locked perfect +
  seeded humanized).

## Verification (real numbers)

- **Grid**: perfect = **0 off-grid** (all voices on 16th/8th grid); humanized > 0
  (humanizer ran). Drums' swung hi-hat lands on the 16th grid (`off8` = expected).
- **Harmony**: **0 out-of-scale**, **0 out-of-chord** across all 8 pitched voices.
- **Zero-drift**: all 9 tracks equal length (23040 ticks).
- **Humanization**: seed 25756; drums tightest (mean 1.28t), bass lays back
  (mean 8.08t).

## Files

- `MIDI/255-blues-vuza-hocket-phase1.mid` — raw draft (pre-rules)
- `MIDI/255-blues-vuza-hocket-perfect.mid` — grid-locked concrete layer
- `MIDI/255-blues-vuza-hocket-humanized.mid` — seeded humanized twin
- `Audio/255-blues-vuza-hocket-{phase1,perfect,humanized}.ogg` — mastered Opus
- `Analysis/summary.json`, `Analysis/grid_visualization.txt`
- `REPORT.md` — full record

See `REPORT.md` for the complete technical record.