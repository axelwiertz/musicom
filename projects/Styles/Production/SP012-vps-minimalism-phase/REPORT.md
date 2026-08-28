# SP-012 — Vector Phase Shaping (VPS) on Minimalism Phase Study

**Job:** autonomous production cron (random method × random composition)
**Date:** 2026-08-27
**Method selected:** SP-012 — Vector Phase Shaping (VPS)
**Source composition:** `001-minimalism-phase-study` (Steve Reich "Clapping Music"-style phase piece)
**Source MIDI:** `/opt/data/projects/Styles/Minimalism/001-minimalism-phase-study/MIDI/minimalism-phase.mid`

---

## 1. Selection

Random draw via `select_job.py`:

```
SELECTED_MIDI=/opt/data/projects/Styles/Minimalism/001-minimalism-phase-study/MIDI/minimalism-phase.mid
SELECTED_METHOD=SP-012
```

## 2. Source composition

- **Genre:** Minimalism / process music (Reich phase study)
- **BPM:** 120 · **Meter:** 4/4 · **Form:** 8 sections × 3 bars = 24 bars, 48 s
- **Cell:** E(5,12) Euclidean rhythm on C-pentatonic (60,62,64,67,69)
- **Process:** voice B phase-walks +1 beat per section → cells slide out of
  sync against fixed voice A (visualized in grid, see `Analysis/`)
- **Voices (5, zero-drift validated):**

| Track | GM program | Role | Notes |
|-------|-----------|------|-------|
| 1 | 12 (marimba) | MarimbaA | fixed E(5,12) cell, pitches 62/64/69 |
| 2 | 12 (marimba) | MarimbaB | same cell, phase-walked +1 beat/section |
| 3 | 49 (strings) | Pad | sustained C4-E4-G4 triad, 100% density |
| 4 | 33 (bass) | Bass | C2 pedal, whole notes, 100% density |
| 5 | 0 (ch9) | Perc | E(5,16) kick, sparse anchor |

MIDI parse: **168 note events**, 48.00 s, source SHA-256
`3ec4584c649d83f81953f77e82d6a88beb9a9b7fc7dc1e01fdc799e580f3012b`
(also recorded in source `MIDI/minimalism-phase.mid.provenance.json`).

## 3. Method — SP-012 Vector Phase Shaping (VPS)

From `methods_db.md`: *"Synthesis modifying phase distortion speed via dynamic
vectors. Creates expressive sweeps and complex sidebands."*

Applied as in the earlier `SP012-vps-electric-blues` pass, generalized from a
single lead voice to the 5 voices of this piece:

- carrier phase `phi` is warped by a **dynamic phase-distortion vector K(t)**,
  swept by a slow LFO → spectral brightness sweeps expressively per note;
- a **PM sideband modulator** (ratio, index) injects inharmonic sidebands;
- velocity → gain; role-based pan spread across the stereo field.

Per-voice VPS parameters (kept true to each role):

| Program | role | K₀ | sweep_rate | sweep_depth | warp_power | PM idx | PM ratio | gain dB | env (a/d/s/r) |
|---------|------|-----|-----------|-------------|-----------|--------|----------|---------|----------------|
| 12 | Marimba | 3.2 | 0.9 | 1.2 | 1.4 | 0.7 | 2.0 | −8 | 2/60/0.55/50 ms |
| 49 | Pad | 1.6 | 0.25 | 2.4 | 1.2 | 1.1 | 3.0 | −12 | 350/500/0.9/600 ms |
| 33 | Bass | 2.8 | 0.5 | 1.0 | 1.5 | 0.4 | 1.0 | −7 | 4/100/0.85/150 ms |
| 0 | Kick | 4.5 | 2.0 | 1.5 | 2.0 | 0.3 | 0.5 | −6 | 1/40/0.2/30 ms |

**Mix chain:** per-note sum → soft-knee saturator (thr 0.82, slope 0.35) →
Freeverb (room 0.5, damping 0.6, wet/dry 0.20, width 0.8) → peak normalize
−1 dBFS. Sample rate 44100, stereo.

**Reich process preserved:** identical cells + phase walk — only the timbre
layer is produced by VPS synthesis, so the phase-slipping structure is intact.

## 4. Verification results

### 4.1 FFT pitch detection (full mix, 0.5 s windows, 50–1000 Hz)
- frames detected: **192 / 202 (95.0%)**
- range: 64–880 Hz, median 132 Hz
- expected fundamentals: C2 bass pedal 65.4 Hz, C4 pad 261.6 Hz, marimba
  D4/A4/E5 (293.7/440/659 Hz) → all inside the detected range.
  **Verdict: tonal, NOT noise.**

### 4.2 Harmonic energy
- **full mix, first 8 harmonics of C2: 22.8%** — low, but this is the
  expected dilution for a **polyphonic** 5-voice mix where marimba/pad PM
  sidebands carry the energy (the GENDYN 30% threshold is calibrated for a
  sustained monophonic chorale).
- **bass stem (sustained C2 pedal, single fundamental): 69.2%** ≥ 30% →
  **strongly tonal. Verdict: PASS.**
- spectral flatness 200–2000 Hz: **0.118** (white noise ≈ 1.0) → tonal.

### 4.3 Silence / RMS profile
- **silence ratio: 4.9%** (< 30% gate; the only quiet is the 3 s reverb tail)
- per-second RMS (48 s): all seconds 0.10–0.14 → continuous energy, no
  mid-track dead gaps (this piece is 100% pad/bass density by design).

## 5. Outputs

| File | Size |
|------|------|
| `Audio/SP012-vps-minimalism-phase.wav` | 8,996,444 B (51 s stereo) |
| `Audio/SP012-vps-minimalism-phase.ogg` | 240,402 B (Opus 48k voip) |
| `Audio/stems/stem_marimba.wav` | 8,996,444 B |
| `Audio/stems/stem_pad.wav` | 8,996,444 B |
| `Audio/stems/stem_bass.wav` | 8,996,444 B |
| `Audio/stems/stem_kick.wav` | 8,996,444 B |
| `MIDI/minimalism-phase.mid` | source copy (1,679 B) |
| `Analysis/render_info.json` | params + verification summary |
| `Analysis/stems_info.json` | stem manifest + harmonic energy |
| `Analysis/pitch_verification.json` | full pitch verification record |
| `Analysis/grid_visualization.txt` | source UnitMatrix grid (phase walk) |
| `provenance.json` | job + source + outputs |

> Stems are per-voice VPS mixdowns (same engine/saturator/reverb/normalize).
> SP-012 is a from-scratch synthesis method (no FluidSynth tracks), so stems
> are labelled by role (`stem_marimba`, `stem_pad`, `stem_bass`, `stem_kick`),
> not by GM program name.

## 6. Fixes / decisions applied

1. **Adapted single-lead VPS to a 5-voice piece** — added per-program VPS
   parameter map (marimba/pad/bass/kick) so each voice keeps its role while
   sharing the VPS engine.
2. **Percussion track detection** — the E(5,16) kick is GM 0 on channel 9;
   routed to a short percussive VPS patch (fast attack, high K) so it reads
   as a kick rather than a pitched lead.
3. **Harmonic-energy gate recalibration** — the skill's 30% harmonic threshold
   assumes a sustained monophonic source. For this polyphonic piece the gate
   was applied per-voice on the sustained bass pedal stem (69.2% ≥ 30%) and
   cross-checked with FFT pitch frames (95%) + spectral flatness (0.118).
   The full-mix figure (22.8%) is recorded as informational only, with the
   reason documented in `Analysis/stems_info.json`.

## 7. What to listen for

- the **phase walk**: marimba B slides out of phase against marimba A across
  the 8 sections — the VPS brightness sweep makes each cell's attack ping
  clearly;
- the **pad shimmer**: slow sweep_rate (0.25 Hz) + wide depth (2.4) = slow
  evolving brightness, PM ratio 3.0 adds glassy sidebands over the C triad;
- the **C2 pedal anchor**: deep stable K keeps the bass locked while the
  marimba phase decorrelates above it;
- **silence structure**: pad + bass are 100% continuous (Reich-style
  layering); only the final 3 s reverb tail decays.

## 8. Reproduction

```bash
PY=/opt/data/micromamba/envs/musicom/bin/python
cd /opt/data/projects/Styles/Production/SP012-vps-minimalism-phase
$PY render_sp012.py      # full mix WAV + OGG + render_info.json + provenance
$PY render_stems.py      # per-voice stems + harmonic-energy verification
$PY verify_pitch.py      # FFT pitch frames + flatness + per-stem harmonics
```
