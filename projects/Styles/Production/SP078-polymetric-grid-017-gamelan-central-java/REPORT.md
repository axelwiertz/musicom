# SP-078 Polymetric Grid — production report

- **Date**: 2026-10-24
- **Job**: random-style production (SP), layer-aligned
- **Method**: SP-078 (`sound.generators.polymetric_grid`) — 16-track polymetric
  step sequencer w/ per-step graphs (Rapid Flow omniGRID-style). Independent
  step-count + resolution per track -> lanes re-phase over an LCM ensemble
  cycle; Bjorklund Euclidean pulses; per-step velocity/length/timing/probability/
  repeats graphs; eight shuffle modes; arpeggiator + scale quantisation.
- **Layer**: ABSOLUTE (whole-piece texture re-voicing; note material preserved
  as the source's D Slendro pentatonic, re-grooved by the polymetric grid).

## Selection
- **Registry source**: `workflows.musicom_workflow.SP_METHODS` (63 registered;
  55 in pool after excluding recent-7-day SP-090/092/095/101/105/108/111 and
  baseline SP-001).
- **Source composition**: `Styles/Gamelan/017-gamelan-central-java/MIDI/gamelan_live_render.mid`
  (D Slendro pentatonic gamelan, 80 BPM, 480 TPB, 8 x 16-beat gongan cycles,
  4 voices: Saron balungan / Peking elaboration / Colotomic pots / Gong Ageng;
  512 notes, all grid-locked).

## Pre-flight audit (3 rules) — zero-drift FAIL -> reworked, then PASS
The source is grid-clean (0 off-grid) and fully in D Slendro (0 out-of-scale /
0 out-of-chord), but the final Gong Ageng sustains 2 beats from beat 127 into
beat 129 -> note tracks end at [61440, 61920], violating equal-length
(zero-drift). **Rework**: boundary-clamp the whole source to the 128-beat seam
(61440 ticks) — the final gong note_off is truncated to the seam (the musicom
"no note crosses a section seam" convention). No onset touched.

| rule | before | after (reworked) |
|---|---|---|
| Grid sync (16th = 120 ticks) | **PASS** off-grid = 0 | **PASS** off-grid = 0 |
| Harmony (in D Slendro) | **PASS** out-of-scale = 0 | **PASS** out-of-scale = 0 |
| Zero-drift (equal track ends) | **FAIL** ends = [61440, 61920] | **PASS** ends = [61440] |

## SP-078 absolute layer (polymetric gamelan groove)
Six of the 16 available tracks, each with its own step-count + resolution so
their periods re-phase over the 96-beat render (2 full LCM re-phase cycles of
48 beats each):

| trk | role | steps | res | period | euclidean | pitch | program/ch |
|---|---|---|---|---|---|---|---|
| 1 | Gong Ageng | 16 | 1/4 | 16 beats | 1/16 (step 15) | D3 38 | 14 Tubular Bells / ch3 |
| 2 | Kenong | 16 | 1/4 | 16 beats | 4/16 rot 3 (3,7,11,15) | D4 50 | 12 Marimba / ch2 |
| 3 | Kempul | 16 | 1/4 | 16 beats | 3/16 (5,10,15) | A3 45 | 12 Marimba / ch2 |
| 4 | Kethuk | 16 | 1/4 | 16 beats | 8/16 (0,2,4,...14) | D4 50 | 12 Marimba / ch2 |
| 5 | Balungan | 12 | 1/8 | **6 beats** | 7/12 | Slendro contour | 12 Marimba / ch0 |
| 6 | Peking | 12 | 1/16 | **3 beats** | 9/12 | Slendro contour | 9 Glockenspiel / ch1 |

- **Polymetry**: tracks 5/6 run 6-beat and 3-beat periods against the 16-beat
  gongan, so the balungan and peking drift and re-phase across the piece
  (ensemble LCM = 48 beats; 96 beats = 2 full cycles).
- **Per-step graphs exercised**: note-length (gong 400% ring, kethuk 30% damp),
  probability (kethuk 88%, peking 92% — seeded thinning), repeats ratchet
  (kethuk beat 6 = 2), velocity via per-track gain.
- **Shuffle = straight, master micro-timing = 0** — deliberately disabled so
  the generated groove stays grid-locked (the composition 3-rule discipline
  requires 0 off-grid onsets; the method's pocket/shuffle controls would break
  that by design).
- **Scale quantisation**: the module's `SCALES` table is Western-only (no
  slendro), so the D Slendro pentatonic is applied manually via per-step
  `set_pitch` overrides (same quantised result).
- 463 generated notes, pitch classes [2, 4, 6, 9, 11] (all in D Slendro).
- Rendered through FluidSynth (FluidR3_GM) at 44100 Hz, mastered to −14 LUFS
  (unknown-genre default), −1 dBTP ceiling.

## Output audit (the generated groove, mirror of the 3 rules) — PASS
| rule | result |
|---|---|
| Grid sync (16th = 120 ticks) | **PASS** off-grid = 0 |
| Harmony (in D Slendro) | **PASS** out-of-scale = 0, out-of-chord = 0 |
| Zero-drift (equal track ends) | **PASS** 4 note tracks, end = 46080 ticks |

## Verification
- **Pitch**: dominant-peak-in-key hit rate = 1.0000 (153 windows) → **PASS**
- **Harmonic energy (8 harmonics of dominant)**: 0.4241 (dry reference 0.4239, retention 1.001)
- **Silence**: 17.10%
- **RMS**: 0.1363
- **LUFS**: -14.02  **true peak**: 0.8913

## Files
- `/opt/data/repos/musicom/projects/Styles/Production/SP078-polymetric-grid-017-gamelan-central-java/SP078-polymetric-grid-017-gamelan-central-java.wav` (16364332 bytes)
- `/opt/data/repos/musicom/projects/Styles/Production/SP078-polymetric-grid-017-gamelan-central-java/SP078-polymetric-grid-017-gamelan-central-java.ogg` (982924 bytes)
- `/opt/data/repos/musicom/projects/Styles/Production/SP078-polymetric-grid-017-gamelan-central-java/SP078_polymetric_raw.wav` (pre-master)
- `/opt/data/repos/musicom/projects/Styles/Production/SP078-polymetric-grid-017-gamelan-central-java/dry_full_mix_source_reference.wav` (dry source reference, pre-production)
- `MIDI/source_original.mid` (reference copy)
- `MIDI/source_reworked.mid` (boundary-clamped source)
- `MIDI/SP078-polymetric-gamelan.mid` (generated polymetric groove)
- `Audio/stems/` (4 per-voice stems)
- `provenance.json`, `Analysis/render_stats.json`

## Notes
- SP-078's headline is polymetry (independent length + resolution per track,
  long LCM re-phasing) plus Euclidean generation and the per-step graph lanes.
  The absolute-layer application re-voices the gamelan's 4-voice colotomic
  texture as a 6-lane polymetric grid: the colotomy (gong/kenong/kempul/kethuk)
  stays anchored on the 16-beat gongan while the balungan (6-beat) and peking
  (3-beat) lanes drift against it — the omniGRID "lanes re-phase over time"
  behaviour expressed with slendro pitch material.
