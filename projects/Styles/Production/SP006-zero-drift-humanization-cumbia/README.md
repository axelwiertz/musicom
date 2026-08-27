# SP-006 Zero-Drift Humanization — Production Pass (Cumbia)

**Job:** Autonomous daily production pipeline
**Run type:** Random composition × random sound-production method
**Date:** 2026-08-25

## Selection (this run)

| Item | Value |
|------|-------|
| Source composition | **cumbia-daily-2026-06-22** (Latin / Colombian Cumbia) |
| Source MIDI | `/opt/data/projects/Styles/Latin/cumbia-daily-2026-06-22/composition.mid` |
| Production method | **SP-006 — Zero-Drift Humanization** |

## Source analysis

A 2-bar **cumbia groove**, D Dorian, 100 BPM, 2/4 meter (1920 ticks at 480 tpb),
5 voices: bombo (root-fifth bass), llamador (steady 8th-note pulse), alegre
(syncopated off-beat conga accents), maraca (16th-note shaker), accordion
(D Dorian melodic hook).

Grid (high-contrast, 120 ticks/char = 16th-note cells, this run's humanized MIDI):

```
Bombo Bass      : ███████░███░███░███░███████████░███░███████░███░███░███████████░  (Density: 84%)
Llamador        : ░░█░░░█░░░█░░░█░░░█░░░█░░░█░░░█░░░█░░█░░░░█░░█░░░░█░░█░░░░█░░█░░  (Density: 25%)
Alegre          : ░█░█░█░█░█░█░██░░█░██░█░░██░█░░█░██░█░█░█░█░█░█░░█░█░█░██░█░█░░█  (Density: 50%)
Maraca          : █░█░████░█░████░█░██████░████░███████░████░███████████░█░██░█░██  (Density: 78%)
Accordion       : █░█░█░███░█░██░███░██░████░████░██░██████░█░███░█░████░██░█████░  (Density: 72%)
```

Bombo's 84% density is faithful to the source: it plays continuous 8th notes
with only short 48-tick gaps at the off-beat eighths (layered double-strikes
vel 100/65 and 85/60, per the source README's "varied velocity" bombo line).

## Method applied (SP-006)

"Zero-Drift Humanization": per-voice Gaussian micro-timing jitter + velocity
spread applied over a perfectly quantized groove, with strict absolute-track
alignment preserved (validate() zero-drift gate + readback check).

### Design decisions

| Parameter | Value | Why |
|-----------|-------|-----|
| Source loop | 2-bar groove × 4 repetitions | Listenable 9.6 s artifact; the source is a 2.4 s loop |
| Per-rep re-roll | same seeded RNG stream | Humanization is audible as *variation* across repeats, not a fixed offset |
| Bombo sigma_t / vel | 2 ticks / ±8 | Drummer keeps the downbeat, accents breathe |
| Llamador sigma_t / vel | 1.5 ticks / ±5 | Metronomic backbone, subtly alive |
| Alegre sigma_t / vel | 3 ticks / ±10 | Syncopated accents need the most push-pull |
| Maraca sigma_t / vel | 2 ticks / ±6 | Continuous shaker lift |
| Accordion sigma_t / vel | 5 ticks / ±7, dur ×0.97 | Lead rubato; slight shortening avoids mushy tails |
| Clamping | `start = max(prev_start, grid + jitter)` | No negative deltas / backtracking (mido-safe); preserves overlapping layered strikes |
| Seed | 260825 | Reproducible run |
| Instrumentation | Bombo → program 34 (Acoustic Bass) | Source README documents bombo as acoustic bass; source MIDI omits program changes, restored here |

### Transcription notes (bugs fixed during this run)

- **Velocity-layered double strikes**: bombo and maraca play overlapping
  same-pitch `note_on` pairs (vel 100+65 etc.). A naive note-dict parser
  collapsed them (bombo density 33% → wrong). Fixed with a per-pitch FIFO
  stack: `note_off` pops the oldest layer, preserving both layers and the
  full rhythmic density (84%).
- **Overlap vs ordering clamp**: the first forward-clamp used the prior
  note *end* (serialized overlapping strikes, mean shift 170 ticks).
  Clamping against prior note *start* preserves overlaps and keeps jitter
  in the intended ±1.5–3.5 ms band.

## Verification results

| Check | Result |
|-------|--------|
| `composer.validate()` zero-drift gate | **True OK** |
| MIDI readback track lengths | `[7680, 7680, 7680, 7680, 7680]` — all equal ✓ |
| Full mix duration / peak | 14.36 s / 0.81 (peak-normalized to 0.89 pre-OGG) |
| Full mix silence ratio | 29.8% — all in the reverb tail (sec 0–9 RMS 0.10–0.17, sec 10 = 0.001, sec 11–14 = 0) |
| Stems | 5 WAVs, silence 14–50% (per-instrument reverb tails; no mid-track gaps) |
| WAV size guard | mix 2.5 MB, stems < 1 MB each — no FluidSynth bloat |

### Humanization DNA (mean absolute shift, ticks)

| Voice | mean | max | n notes (4 loops) |
|-------|------|-----|-----|
| Bombo | 1.47 | 4 | 32 |
| Llamador | 0.94 | 3 | 16 |
| Alegre | 2.62 | 7 | 32 |
| Maraca | 1.52 | 5 | 64 |
| Accordion | 3.43 | 11 | 44 |

All shifts < 12 ticks ≈ < 10 ms — imperceptible as timing, perceptible as
groove. Velocity was re-rolled ±5–10 around the source values each repeat.

## Files

```
MIDI/SP006-cumbia-zero-drift-humanized.mid   (editable, 5 voices, 7680 ticks)
Audio/SP006-cumbia-zero-drift-humanized.wav  (full mix, peak 0.89)
Audio/SP006-cumbia-zero-drift-humanized.ogg  (Opus 48k, Telegram-playable)
Audio/stems/track00_Electric_Bass_pick.wav   (bombo → program 34)
Audio/stems/track01_Acoustic_Grand_Piano.wav (llamador nuclei → GM piano map)
Audio/stems/track02_Acoustic_Grand_Piano.wav (alegre → GM piano map)
Audio/stems/track03_Acoustic_Grand_Piano.wav (maraca → GM piano map)
Audio/stems/track04_Harmonica.wav            (accordion → GM harmonica map)
Analysis/grid_visualization.txt
Analysis/humanization_dna.json
Analysis/render_stats.json
produce_sp006.py                             (this run's generator)
provenance.json
```

**Note on stem labels**: `RenderPipeline` derives stem names from GM program
names; percussion-channel voices (ch 9, no program change) default to
"Acoustic Grand Piano" and program 22 renders as "Harmonica" in this
SoundFont's map — labels are GM quirks, not instrumentation changes.
Percussion pitch classes (45/63/70) are preserved 1:1 from the source.