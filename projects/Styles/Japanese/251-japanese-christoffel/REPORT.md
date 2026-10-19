# REPORT — 251 Japanese Christoffel Word

**Date**: 2026-10-18 (nightly autonomous composition job)
**Project**: `Styles/Japanese/251-japanese-christoffel/`

## Selection

| Field | Value |
|---|---|
| Project number | **251** |
| Style | **Japanese** (koto / shakuhachi / shamisen / taiko) |
| Method | **069 Christoffel Word Combinatorial Composition (CWCC)** |
| Layer | **concrete** (Rules-Based, Grid-Locked, O(N)) |
| Form | **rondo (A-B-A-C-A)** — 5 sections × 4 bars = 20 bars |
| Key | **E yo pentatonic** {4,6,8,11,1} = E F# G# B C# (major pentatonic) |
| Tempo | 88 BPM, 4/4, 480 TPB, BAR = 1920 |
| Selection seed | 251 (style random over 44 candidates; method excluded last-7-days set) |

## Method mechanics (concrete → engine)

Christoffel words = *balanced binary words*. The method drives four dimensions
from one word family:

1. **Scale (height)** — step word `C(3,2) = aabab` over {whole-step=2,
   minor-3rd=3} semitones → step pattern (2,2,3,2,3) → E yo pentatonic.
   (`christoffel()` = floor-difference construction; C(5,2)=aaabaab is the
   Lydian diatonic analog.)
2. **Rhythm (time)** — Euclidean rhythms ARE Christoffel words over
   {onset,rest}. Koto = `C(5,3)` → E(5,8) mask `11011010`; Shamisen =
   `C(3,5)` → E(3,8) tresillo `10100100`.
3. **Form (Sturmian)** — the rondo A-B-A-C-A recurrence mirrors the
   Fibonacci/Sturmian substitution A→AB (A self-repeats as a recurrent block).
4. **Harmony (duality)** — the dual word `C(2,3) = babaa` (a↔b swap) is the
   "dark twin" of the home scale; its pattern schedules the episode chords
   (C#m / B / F#sus2) — all still subsets of the home pentatonic.

## Voices & instruments (registry, source of truth)

| Voice | Program | Channel | Pitched | Role |
|---|---|---|---|---|
| Koto | 107 | 0 | yes | lead melody (Christoffel-contour chord-tone arpeggio) |
| Shakuhachi | 77 | 1 | yes | sustained counterline (root + upper chord tone) |
| Shamisen | 106 | 2 | yes | tresillo rhythmic plucks |
| Taiko | 116 | 3 | no | percussion anchor (climax 8th interlock) |

## Chord progression (per bar)

```
A1 (0-3)   I  E major    {4,8,11}
B  (4-5)   vi C# minor   {1,4,6}
B  (6-7)   V  B sus      {11,1,4}
A2 (8-11)  I  E major    {4,8,11}
C  (12-13) ii F# sus2    {6,8,11}   (tense)
C  (14-15) V  B sus      {11,1,4}   (turn -> resolve)
A3 (16-19) I  E major    {4,8,11}
```

## Grid audit (perfect / pre-humanization — inline)

| Voice | notes | off16 | off8 | out_scale | out_chord |
|---|---|---|---|---|---|
| Koto | 100 | 0 | 0 | 0 | 0 |
| Shakuhachi | 40 | 0 | 0 | 0 | 0 |
| Shamisen | 60 | 0 | 0 | 0 | 0 |
| Taiko | 72 | 0 | 0 | 0 | 0 |

## Readback audit (final exported MIDIs, mido read-only)

| Artifact | size | onsets | pitched | off16 | off8 | out_scale | out_chord | zero-drift |
|---|---|---|---|---|---|---|---|---|
| phase1 | 1157 B | 120 | 120 | 119 | 120 | 0 | 41 | True (38400) |
| perfect | 2649 B | 272 | 200 | **0** | **0** | **0** | **0** | True (38400) |
| humanized | 2643 B | 272 | 200 | **225** | 225 | 0 | 2 | True (38400) |

- **perfect** = 0 off-grid (compositional truth), 0 out-of-scale, 0 out-of-chord. ✓
- **humanized** = 225 off-grid (>0 → humanizer ran), 0 out-of-scale; 2
  out-of-chord are two onsets micro-shifted across a *bar* boundary by
  humanization timing (still in-scale; musically negligible).
- **phase1** = off-grid by design (raw stochastic walk; out_chord=41 is
  expected — no harmony in phase 1).

## Humanization (seed 251, style-derived, per-instrument DNA)

| Voice | seed | timing_sigma_ms | vel_sigma | layback_ms | mean_shift(t) | max_shift(t) | vel_delta |
|---|---|---|---|---|---|---|---|
| Koto | 25351 | 8.0 | 6.0 | 1.0 | 3.82 | 12 | 4.63 |
| Shakuhachi | 25352 | 8.0 | 6.0 | 1.0 | 3.00 | 9 | 5.10 |
| Shamisen | 25353 | 8.0 | 6.0 | 1.0 | 3.88 | 16 | 5.27 |
| Taiko | 25354 | 2.0 | 4.0 | 0.0 | 0.72 | 3 | 2.96 |

Taiko anchors the grid (2 ms sigma, 0.72t mean shift — tightest); the three
World-family plucked/wind voices sit looser (8 ms, ~3-4t). Per-voice child
seed = `251*101 + row` (25351..25354).

## Render + master (FluidSynth → master() → Opus OGG)

SoundFont: `FluidR3_GM.sf2` (via `discover_soundfont()` / `$MUSICOM_SOUNDFONT`).
Target: `target_for_style("japanese")` = **−14.0 LUFS** (fallback — "japanese"
not in the genre map; traditional ensemble sits naturally quieter).

| Artifact | integrated LUFS | true peak | silence ratio | duration | wav | ogg |
|---|---|---|---|---|---|---|
| phase1 | −15.54 | −1.0 dBTP | 7.1% | 58.11 s | 10.25 MB | 555 KB |
| perfect | −14.28 | −1.0 dBTP | 6.3% | 57.88 s | 10.21 MB | 494 KB |
| humanized | −14.25 | −1.0 dBTP | 6.3% | 57.87 s | 10.21 MB | 494 KB |

Per-second RMS is steady ~0.10–0.21 through the music (53 s), dropping only at
the final reverb tail (last ~3 s) — **no mid-track gaps**. Silence ratio
6–7% is tail padding, not dead air.

## Fixes applied during this run

1. **Section-split absolute offset bug** — `split_abs_to_section` used
   `start = s * BAR` (section index × one bar) instead of
   `start = SECTION_START_BARS[s] * BAR`. Caught by readback: perfect showed
   out_chord=64 (notes shifted +3 bars into wrong sections). Fixed → out_chord 0.
2. **Registry constant name** — shakuhachi is exported as `SHAKUCHACHI`
   (upstream typo in `instrument_registry.py`), not `SHAKUHACHI`. Import fixed.

## File map

- `MIDI/251-japanese-christoffel-{phase1,perfect,humanized}.mid` (+ provenance sidecars)
- `Audio/251-japanese-christoffel-{phase1,perfect,humanized}.{wav,ogg}` (+ provenance)
- `Analysis/{summary,readback,render_stats}.json`, `grid_visualization.txt`
- `README.md`, `index.html` (VoltAgent dashboard), `compose.py`, `render.py`, `verify.py`

**Status**: COMPLETE — zero-drift ✓, grid 0 off-grid (perfect) ✓, harmony 0
out-of-key/out-of-chord (perfect) ✓, humanizer verified (225 off-grid) ✓,
mastered to −14 LUFS / −1 dBTP ✓.
