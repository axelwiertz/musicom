# 090 — Celtic Subset Walk

**Style**: Celtic · **Method**: ABS-002 Subset Walker (ABSTRACT layer) +
ABS-001 tension-curve steering + method-006 cadence close
**Key**: D minor · **BPM**: 108 · **Form**: Intro / Verse / Chorus / Break /
Chorus2 / Outro (24 bars)

## What this is

The weekly abstract-layer composition. A 12TET subset network walk
(`rules/subset_network.py`) over D-minor diatonic anchors produces the entire
harmonic universe; a tension curve (calm → rise → chorus peak → settle →
resolve) steers the walk; a forced A7 → Dm cadence closes the piece.

Phase 1 is the RAW abstract draft: a single bagpipe voice whose pitch classes
are sampled from the current walked subset at every 8th slot — you literally
hear the walk as harmony colour, with fractional jittered onsets (the raw
fingerprint). Phase 2 realizes it: 16th-grid lock, scale + chord-tone
quantize, voice-leading correction, and a full Celtic texture.

## Progression (24 bars)

```
i  III i  v  i  III | i7 IIImaj7 i7 IIImaj7 V7 bVII7 |
vii° V7 IIImaj7 V7 vii° bVII7 | i III i v V7 i
Dm F  Dm Am Dm F    | Dm7 Fmaj7 Dm7 Fmaj7 A7 G7 |
C#dim A7 Fmaj7 A7 C#dim G7 | Dm F Dm Am A7 Dm
```

## Voices

Violin (lead) · Flute (counterline) · Cello (pad) · Piano (harp rolls) ·
Double Bass (roots) · Drum Kit — all from `instrument_registry`.

## Verification

- Grid audit: **0 / 1167** notes off the 16th grid (all 6 voices)
- Harmony audit: **0** out-of-scale, **0** out-of-chord
- Zero-drift: both phases pass `validate()`; all tracks 46080 ticks
- Voice-leading: 9 flags → fixed → 0 flags
- Audio: 56.02 s, silence 4.72%, tonal 109/112 windows — healthy

## Files

| Path | Artifact |
|---|---|
| `MIDI/090-celtic-subset-walk-phase1.mid` | raw abstract-layer draft |
| `MIDI/090-celtic-subset-walk.mid` | phase-2 arrangement |
| `Audio/090-celtic-subset-walk.ogg` | full-mix render |
| `Audio/090-celtic-subset-walk-phase1.ogg` | phase-1 render |
| `Analysis/grid_visualization.txt` | density grid |
| `Analysis/audit.json` | grid + harmony audit |
| `REPORT.md` | full report |

Reproduce: `compose.py` → `audit.py` → `render_audio.py` → `audio_stats.py`.
