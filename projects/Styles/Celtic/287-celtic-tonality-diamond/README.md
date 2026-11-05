# 287 — Celtic Tonality Diamond

**Celtic composition · Method 131 TDRPC (Tonality Diamond Ratio-Pool Composition)**

A Celtic reel built from Harry Partch's 7-limit tonality diamond: the pitch pool
is the 13 just-intonation ratios of D(7), the harmonic progression is an
identity walk (D → G → C → Am) with common-tone retention, and the tension arc
follows the Tenney-height curve. The diamond's signature tone — the 7/4 harmonic
seventh — is the Mixolydian b7 that gives Celtic melody its distinctive colour.

## Headline

| | |
|---|---|
| Style | Celtic |
| Method | 131 — Tonality Diamond Ratio-Pool Composition (TDRPC) |
| Layer | **abstract** (weekly cadence) |
| Form | intro–verse–chorus–verse–chorus–outro (6 sections, 40 bars) |
| Key | D Mixolydian (D E F# G A B C) |
| Tempo | 112 BPM (reel) |
| Instruments | Fiddle, Flute, Steel Guitar, Acoustic Bass, Drum Kit |

## Files

- `MIDI/287-celtic-tonality-diamond-phase1.mid` — raw diamond walk (single voice, off-grid)
- `MIDI/287-celtic-tonality-diamond-perfect.mid` — grid-locked rules layer
- `MIDI/287-celtic-tonality-diamond-humanized.mid` — humanized twin
- `Audio/*.ogg` — mastered Opus renders (all three versions)
- `Analysis/grid_visualization.txt`, `Analysis/summary.json`, `Analysis/render_stats.json`
- `REPORT.md` — full record

## The two-phase architecture

**Phase 1 (abstract → raw):** a height-directed random walk over the 13 ratios of
D(7), each mapped to nearest 12-TET with cents deviation recorded in provenance.
Onsets jittered off-grid. Single voice, no harmony.

**Phase 2 (musicom rules):** tiered pitch discipline (strong beats snap scale+chord,
weak beats snap scale), 16th-grid lock, voice-leading cap, full 5-voice Celtic
texture, dual-version export (perfect + humanized).

See `REPORT.md` for the full audit trail and `provenance.json` for the diamond data.
