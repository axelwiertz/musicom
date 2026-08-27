# SP-011 Karplus-Strong String Synthesis — Production Pass

**Job:** Autonomous daily production pipeline (`9a2813f77dac`)
**Run type:** Random composition × random sound-production method
**Date:** 2026-08-09

## Selection (this run)

| Item | Value |
|------|-------|
| Source composition | **057-Cellular Chorale** (Experimental / Cellular Automata, project 057) |
| Source MIDI | `/opt/data/projects/Styles/Experimental/057-cellular-chorale/MIDI/057-cellular-chorale.mid` |
| Production method | **SP-011 — Karplus-Strong String Synthesis** |

## Source analysis

A **4-voice chorale**, 96 BPM, 20 s, generated from a Cellular Automata evolution
(method 021). Every voice plays 8 whole notes (2.5 s each), one per CA generation:

| Voice | Program | MIDI range | Role in chorale |
|-------|---------|-----------|-----------------|
| Track 1 | 74 (Flute) | D#4 (63) – D5 (74) | Soprano line |
| Track 2 | 74 (Flute) | G3 (55) – F#4 (66) | Alto line |
| Track 3 | 74 (Flute) | D3 (50) – C#4 (61) | Tenor line |
| Track 4 | 33 (Electric Bass) | A2 (45) – F#3 (54) | Bass line |

Chorale DNA grid (█ = onset, one column = one 2.5 s whole-note cell):

```
          c0    c1    c2    c3    c4    c5    c6    c7
V1 (P74)   █    █    █    █    █    █    █    █
V2 (P74)   █    █    █    █    █    █    █    █
V3 (P74)   █    █    █    █    █    █    █    █
V4 (P33)   █    █    █    █    █    █    █    █
```

Pitch classes per cell (C-major-adjacent field, tonic gravity on C/A):

```
V1 (P74): D#  C  A#  D  A#  D  F  D#
V2 (P74):  B  B  F#  E  E  F#  B  G
V3 (P74):  D  B  G  C#  E  C#  G  D
V4 (P33):  C  E  D  F#  C  D  C  A
```

## Method applied (SP-011)

Signal flow per note: **noise-burst excitation → delay-line loop → moving-average
loop filter → velocity-scaled gain → panned mix bus**.

The classic Karplus-Strong plucked string:

```
y[n] = x[n] + loop_gain · ½ · ( y[n−N] + y[n−N−1] )
N    = round( sr / f0 )          # delay line length = one full period
x    = 2-sample noise burst     # the "pick" transient
```

### Design decisions

| Parameter | Value | Why |
|-----------|-------|-----|
| Delay length | `N = sr/f0` (full cycle) | Classic KS is a *single* delay loop with no sign inversion — full period is correct. (The skill's octave-drop warning applies to *fixed-end* bidirectional waveguides with two sign inversions, not this loop.) |
| Excitation | 2-sample uniform noise, scaled by velocity | Closest to a real pick transient; velocity 100 → full burst |
| Loop filter | 2-point moving average | The canonical KS low-pass; damps high frequencies per round-trip |
| Loop gain | 0.996 + tilt 0.994–0.997 | Controls decay time (~1–2 s audible ring); spectral tilt makes high strings brighter, low strings darker |
| Bass voice | loop gain 0.997, −6 dB | Longer sustain, darker — electric-bass register |
| Pan | static per voice; lead drifts −0.55→+0.55 across the 8 cells | The chorale's CA "motion" becomes a slow spatial gesture; bass centered |
| Bus | soft-knee saturation, peak −1 dBFS | Glue + headroom; no clipping |

### What to listen for

1. **The pick transient** — every whole note starts with a soft noise "pluck", the
   signature KS attack. The chorale's flutes become a **plucked string choir**.
2. **Pitch-tracking decay** — each string rings ~1–2 s with a slightly bright
   attack that darkens as the loop filter eats highs. Low strings (bass) ring
   longer and darker.
3. **Spatial motion** — the soprano line drifts slowly from left to right across
   the 8 cells while the bass stays centered: the CA field evolution made audible
   as movement.
4. **Dissonance by design** — cells c1 (B/D/B/E), c3 (D/E/C#/F#), c6 (F/B/G/C)
   keep their sharp cluster character; the plucked timbre makes each chord's
   beating audible instead of blending it into a pad.

### Files

| Path | Description |
|------|-------------|
| `MIDI/057-cellular-chorale.mid` | Source composition (copy) |
| `Audio/SP011-cellular-chorale-karplus-strong.wav` | Full mix, 16-bit stereo, 23.0 s (incl. 3 s tail) |
| `Audio/SP011-cellular-chorale-karplus-strong.ogg` | Opus 48 kbps voip — Telegram-playable |
| `Analysis/chorale_dna.json` / `chorale_dna_grid.txt` | Chorale DNA (8 cells × 4 voices) |
| `Analysis/render_info.json` | Full synthesis parameter record |
| `produce_sp011.py` | The renderer (pure numpy, reproducible) |
| `provenance.json` | Job / source / method / verification record |

### Verification (real tool output)

- Spectral check: **PASS** — FFT peak-picking finds the expected fundamental for
  7/7 tested notes in their 2.5 s cell windows (C2→130.8 found 130.5, B3→246.9
  found 246.0, D5→587.3 found 587.5, etc.).
- Sanity check: **PASS** — peak 0.696, 0 clipped samples, RMS profile follows the
  8 chorale cells, no click artifacts (11 frames > 0.25 delta, all at pluck
  transients — expected).
- `ffprobe`: OGG = Opus 48 kHz stereo, 23.0 s; WAV = PCM s16 44.1 kHz stereo.

### Notes / next moves

- A natural follow-up is **SP-024 (Bowed String)** on the same chorale — the
  friction model turns the plucks into sustained bows, changing only the
  excitation, keeping the identical delay-line core. A/B comparison would isolate
  excitation vs. loop-filter contribution.
- The lead pan drift (cell→cell) is a tasteful default; a full circle
  (0→2π over 8 cells) would make the motion more obvious.
- Loop gain could be parameterized per-cell to trace the CA density curve.
