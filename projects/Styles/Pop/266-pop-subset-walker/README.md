# 266 — Pop Subset Walker (abstract + concrete)

**Axis combo** (from `COMPOSITION_DESIGN_SPACE.md`, user pick "abstract+concrete ABS-002 walker, pop"):

| axis | pick |
|---|---|
| layer path | **abstract + concrete** |
| paradigm | ABS (tonal) — ABS-002 Subset Walker |
| lead | 1 (flute) |
| percussion | full kit (pop backbeat) |
| harmonization | piano pad + clarinet 16th arp |
| voices | 5 = Flute · Piano · Double Bass · Clarinet · Drums |
| form | intro-verse-chorus-bridge-chorus2-outro (24 bar) |
| humanization | pop (4 ms σ) |

## The abstract layer (ABS-002)

`PatternNetwork.walk()` over a pool of C-major diatonic anchors (6 triads +
5 seventh chords + V7), steered by a tension curve (intro low → chorus peak →
bridge settle → resolve), closed by a forced **V7→I cadence** (G7 → C). One
walked subset per bar **is** the harmony — the walk is the score's skeleton,
not a functional progression.

**Walked progression:** `I ii I IV I Imaj7 I ii | ii7 iii7 ii7 IVmaj7 | ii7 vi7
iii7 ii7 | IVmaj7 vi7 iii7 ii7 | IV iii V7 I`

## The concrete layer

The walked subset is realized into notes: lead (flute) samples the subset's
pitch classes, piano pads the root-position triad, bass pulses the root,
clarinet arpeggiates 16ths, drums lock the backbeat. Scale-snap + chord-quantize
keep every voice in-key **and** in-chord.

## Files

- `MIDI/*-phase1.mid` — raw subset-walk draft (off-grid)
- `MIDI/*-perfect.mid` — grid-locked rules-processed
- `MIDI/*-humanized.mid` — pop-profile jitter
- `Audio/*.ogg` / `*.wav` — mastered −9 LUFS (pop target)

## Verify (real numbers)

Zero-drift 46080 × 5 voices · perfect off-grid **0** · humanized off-grid
**647** · harmony 0/0/0 all voices · phase-1 pc-in-subset **99.2%** ·
walk valid (tonic → V7→I). See `Analysis/verify.json`.
