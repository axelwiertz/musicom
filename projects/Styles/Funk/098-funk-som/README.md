# 098 - Funk Style, Method 075 Self-Organizing Map Composition (SOM-C)

**Status:** Complete (2026-09-19)
**Style:** Funk
**Method:** 075 Self-Organizing Map Composition (SOM-C)
**Layer:** `concrete`
**Key:** F minor (Aeolian / Pentatonic) · **BPM:** 104 · 4/4 · 480 TPB
**Form:** 6 sections × 4 bars = 24 bars (Intro | Verse | Chorus | Bridge | Chorus2 | Outro) = 46,080 ticks (~58s)

---

## Method Summary

Method 075 (SOM-C) uses a Kohonen Self-Organizing Map trained on prototypical funk melodic and rhythmic gesture vectors `[pitch_norm, duration_norm, velocity_norm]`. A 2D toroidal Markov walker navigates the 4×4 prototype lattice with thermal noise and section-level attractor waypoints.

### Two-Phase Architecture
- **Phase 1 (`098-funk-som-phase1.mid`)**: Raw generative draft from the SOM walker. Continuous floating-point pitch and unquantized inter-onset intervals (177/184 onsets off 16th-grid by design). Single voice (Lead Trumpet), no accompaniment, zero-drift validated.
- **Phase 2 (`098-funk-som.mid`)**: Musicom rules post-processing:
  1. Mandatory 16th-grid quantization (120 ticks @ 480 TPB) → **0 off-grid**.
  2. Harmonic quantization to bar chord tones and F minor scale → **0 out-of-scale, 0 out-of-chord**.
  3. Voice-leading leap cap ($\le 9$ semitones).
  4. 5-voice arrangement: Lead Trumpet, Tenor Sax, Piano comping, Double Bass funk groove, Drum Kit (ch9).
  5. Zero-drift validated across all 5 tracks.

---

## Verification & Audits

- **Zero-Drift Gate:** PASS (`validate()` returned `True` for both phases; exact track length 46,080 ticks).
- **16th-Grid Audit (120 ticks):**
  - Phase 2: **0 off-grid / 1128 notes** (0 off-grid across all voices).
  - Phase 1: 177 off-grid / 184 notes (authentic generative fingerprint).
- **Harmony Audit:**
  - Out-of-scale: **0 / 1128 notes** (0 violations).
  - Out-of-chord: **0 / 1128 notes** (0 violations).
- **Audio Rendering & Silence Profile:**
  - Phase 2 Mix: 57.96s, Peak 0.9405, RMS 0.1051, Silence ratio 5.24% (tail only). Tonal windows: 113/115.
  - Phase 1 Mix: 57.39s, Peak 0.4696, RMS 0.0709, Silence ratio 7.24% (tail only). Tonal windows: 112/114.
- **Preflight Compliance:** COMPLIANT (`exit 0`).

---

## Artifacts

- `MIDI/098-funk-som.mid` (Phase 2 full arrangement) + `.provenance.json`
- `MIDI/098-funk-som-phase1.mid` (Phase 1 raw SOM draft) + `.provenance.json`
- `Audio/098-funk-som.wav` (10.2 MB) + `.ogg` (432 KB)
- `Audio/098-funk-som-phase1.wav` (10.1 MB) + `.ogg` (515 KB)
- `Analysis/grid_visualization.txt`, `Analysis/audit.json`, `Analysis/render_stats.json`
- `REPORT.md`
