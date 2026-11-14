# 302 — Techno Tendency Mask

Techno / **Method 023 Tendency Masking Stochastic Bounds (TM-SB)** — concrete layer.

A stochastic pitch walk whose every step is bounded by a dynamic tendency mask:
a per-section lower/upper frequency envelope that opens and closes like a filter
sweep. The mask is the musical idea — Intro opens, Break collapses to a narrow
mid band (breakdown), Drop throws the band wide open, Outro closes it back down.

**A natural minor · 128 BPM · 4/4 · 24 bars** (Intro 4 · Break 8 · Drop 8 · Outro 4)

## Instrumentation (musicom instrument registry)

| Voice | Instrument | GM Program | Role |
|---|---|---|---|
| Lead | Singing Saw | 81 | tendency-masked stochastic contour (saw lead) |
| Bass | Synth Bass 1 | 38 | driving offbeat 8th pump (Drop), root/fifth elsewhere |
| Pad | Synth Pad | 88 | breakdown pad (Break/Intro/Outro, silent in Drop) |
| Stab | Synth Brass 1 | 62 | offbeat rave stab (Drop only) |
| Drums | Drum Kit | ch9 | 4-on-floor kick, offbeat open hat, clap, 16th closed hat |

## Tendency mask (Method 023)

Band `[lo(t), hi(t)]` interpolates linearly across each section (`p = t/span`):

| Section | lo start→end | hi start→end | band width start→end | Gesture |
|---|---|---|---|---|
| Intro  | 45→43 | 60→74 | 29→17 (wide top) | opening |
| Break  | 48→50 | 58→66 | 18→8  | narrow breakdown |
| Drop   | 57→62 | 84→96 | 39→22 | wide open, peak energy |
| Outro  | 62→55 | 96→68 | 6→41  | closing / collapse |

## Harmony — i · VI · VII (Am · F · G)

| Section | Progression |
|---|---|
| Intro  | Am Am Am Am |
| Break  | Am ×8 |
| Drop   | Am Am F G Am Am F G |
| Outro  | Am Am Am Am |

## Files

- `MIDI/302-techno-tendency-mask-phase1.mid` — raw unquantized draft (187 off-grid)
- `MIDI/302-techno-tendency-mask-perfect.mid` — grid-locked (0 off-grid)
- `MIDI/302-techno-tendency-mask-humanized.mid` — style/instrument humanized (>0 off-grid)
- `Audio/*.ogg` — mastered listening renders (−10 LUFS, −1 dBTP)
- `compose.py` / `render_audio.py` / `verify.py` — build, render, audit
- `REPORT.md` — full record

## Verification

- **Zero-drift** ✓ (all 6 tracks = 46080 ticks)
- **Grid audit** (perfect): 0 off-grid on every pitched voice
- **Harmony audit**: 0 untagged out-of-scale, 0 non-resolving, 0 strong violations
- **Humanization**: seeded (`263394771`), drums anchor 2 ms, bass lays back 8 ms, lead tight 2 ms
