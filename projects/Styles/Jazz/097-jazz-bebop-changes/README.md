# 097 — Jazz Bebop Changes

**Style**: Jazz (bebop head) · **Method**: ABS-002 Subset Walker (ABSTRACT layer) +
ABS-001 tension-curve steering + method-006 cadence close (forced V7 → I)
**Key**: G major · **BPM**: 132 · **Form**: Intro / Head / Solo / Bridge /
Head2 / Outro (24 bars)

## What this is

The weekly abstract-layer composition. A 12TET subset network walk
(`rules/subset_network.py`) over G-major diatonic seventh anchors produces the entire
harmonic universe; a tension curve (head sway → solo rise → bridge peak →
head return → outro resolve) steers the walk; a forced D7 → G cadence closes the piece.

Phase 1 is the RAW abstract draft: a single trumpet voice whose pitch classes
are sampled from the current walked anchor tetrad (+30% chromatic-approach
bebop color) at every swing-8th slot — you literally hear the walk as harmony
colour, with fractional jittered onsets (the raw fingerprint). Phase 2 realizes it:
16th-grid lock, subset realization + chord-tone quantize, voice-leading correction,
and a full bebop texture.

## Progression (24 bars)

```
I  IV I  IV ii iii | IV I ii I iii IV | IV7 vi7 IV7 I7 |
vi7 ii7 vi7 IV7 ii7 | IV V7 I
G  C  G  C  Am Bm   | C  G  Am G  Bm C  | Cmaj7 Em7 Cmaj7 Gmaj7 |
Em7 Am7 Em7 Cmaj7 Am7 | C D7 G
```

## Voices

Trumpet (lead, GM 56) · Trombone (counterline, GM 57) · Piano (comping, GM 1) ·
Double Bass (walking, GM 43) · Drum Kit (ch9, spang-a-lang ride) — all from `instrument_registry`.

## Verification

- Grid audit: **0 / 713** notes off the 16th grid (all 5 voices)
- Harmony audit: **0** out-of-scale, **0** out-of-chord
- Zero-drift: both phases pass `validate()`; all tracks 46080 ticks
- Voice-leading: 3 flags → fixed → 0 flags
- Audio: 47.77 s, silence 8.78%, tonal 90/95 windows — healthy

## Files

| Path | Artifact |
|---|---|
| `MIDI/097-jazz-bebop-changes-phase1.mid` | raw abstract-layer draft |
| `MIDI/097-jazz-bebop-changes.mid` | phase-2 arrangement |
| `Audio/097-jazz-bebop-changes.ogg` | full-mix render |
| `Audio/097-jazz-bebop-changes-phase1.ogg` | phase-1 render |
| `Analysis/grid_visualization.txt` | density grid |
| `Analysis/audit.json` | grid + harmony audit |
| `REPORT.md` | full report |

Reproduce: `compose.py` → `audit.py` → `render_audio.py` → `audio_stats.py`.
