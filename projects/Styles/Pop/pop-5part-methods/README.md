# Pop 5-Part — Framework + Per-Section Method Variation

Pop composition, standard form: **Intro → Verse → Chorus → Bridge → Outro**.

## Phase 1 — Composition (framework + method variation)

**Framework (Method 001 Skeleton-First):** C major, 120 BPM, 4/4, progression
I-V-vi-IV family, 5 voices (Melody / Pad / Bass / Arp / Drums).

Each SECTION uses a DIFFERENT generative method but stays inside the same
framework (same key, same progression family, same voice roles, same density):

| Section | Bars | Composition method |
|---|---|---|
| Intro | 4 | Tendency Masking (023) — sparse half-note melody, no drums first 2 bars |
| Verse | 8 | Markov (002) melody + Euclidean (011) drums + tendency bass |
| Chorus | 8 | DPSM phase-shift (026) 16th arp + inversion-heavy chords (lift) |
| Bridge | 4 | Isorhythmic talea-color (032) melody + sustained pad |
| Outro | 4 | Schillinger resultant (018) rhythm + progressive dropout |

## Phase 2 — Production (per-voice + per-section methods)

**Per-voice production** (5 distinct DSP methods on rendered stems):

| Voice | Production method |
|---|---|
| Melody | Echo (280 ms delay) |
| Pad | FDN reverb (space) |
| Bass | Biquad lowpass 400 Hz (warm) |
| Arp | StereoImager widen + highshelf (air) |
| Drums | Multiband compressor (punch) |

**Per-section production** (5 distinct treatments on the mixed bus):

| Section | Treatment |
|---|---|
| Intro | lowpass 1200 Hz (muffled build-in) |
| Verse | dry (clean) |
| Chorus | StereoImager widen + highshelf (lift) |
| Bridge | FDN reverb wash |
| Outro | lowpass 800 Hz + fade-out |

**Master:** LUFS −14, limiter −1 dB.

**Rhythm alignment:** percussion locked to the 16th-note grid. Verified via
`verify_rhythm.py` — kick beats 1-2-3-4, snare beats 2&4, hat 8th notes; zero
off-grid onsets. NOTE: `EuclideanCore` Bjorklund bucket phase-shifts downbeats
(kick lands on the "and"), so beat-aligned explicit patterns are used instead.

## Files

- `MIDI/pop_5part_methods.mid` — editable DAW file (zero-drift validated)
- `Audio/pop_5part_methods.wav` — full mix
- `Audio/pop_5part_methods.ogg` — Opus (Telegram)
- `Audio/stems/` — per-voice WAV stems
- `Analysis/grid_visualization.txt` — high-contrast density grid

## Verify

```bash
/opt/data/micromamba/envs/musicom/bin/python compose.py   # Phase 1
/opt/data/micromamba/envs/musicom/bin/python produce.py  # Phase 2
```
