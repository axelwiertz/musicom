# REPORT — 228-balkan-spectral

Autonomous nightly composition job · 2026-10-07 · job `1fc3fd65d359`

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Style | **Balkan** (random from `Styles/` genre folders, excl. _Comparison/_Data_Patterns/Research/Poetry/Production/Percussion/Other + numbered dirs + `Celtic ` dup) |
| Method | **051 — Spectral Graph Laplacian Mapping (SGLM)** (Rules-Based, eigenvalue-guided, O(n³) / sparse O(nk)) |
| Layer | **concrete** |
| Seed | 20261007 (date-seeded RNG) |
| Layer roll | `rng.random()` = **0.2284** ≥ 1/7 → *concrete* (the ~6-of-7 cadence) |
| Excluded (last 7d) | methods used 2026-09-30 → 10-06: **007, 019, 025, 041, 050, 094, 095, 217** |
| Candidate pool | 93 concrete methods after exclusion |

The date-seeded roll landed concrete (0.2284), as expected by the 6-of-7 cadence.

## 2. Method essence (051 SGLM)

Build a 7-node graph over the G-Dorian scale degrees with edges weighted by a
**Gaussian consonance affinity on the circle-of-fifths cycle** (w = exp(−d²/2σ²),
d = fifths-cycle distance). Compute the eigendecomposition of the graph
Laplacian L = D − A:

- **Fiedler vector v₁** (2nd-smallest eigenvector) sorts scale degrees into a
  smooth *spectral scale* → drives the **lead melody contour**.
- **2nd eigenvector v₂** is the **counter-axis** → drives the violin counterline.
- **Algebraic connectivity λ₁** = continuous **harmonic-tension scalar** (Cheeger
  bound) → sets section function HOME/TURN/TENSE and note density.
- **Eigenvalue gap Δ = λ₂ − λ₁** = structural separation between hierarchical
  levels.

Per-section edge re-weighting (connectivity scale) morphs the spectrum.
A `tonic_boost` on tonic-incident edges breaks the cycle's circulant degeneracy
(pitfall 3) and anchors the tonic as the spectral centre (pitfall 4).

## 3. Musical parameters

| Field | Value |
|---|---|
| Key | **G Dorian** — G A Bb C D E F → pc `{0,2,4,5,7,9,10}`, tonic G |
| Tempo | 132 BPM |
| Meter | **7/8 (dajčovo 2+2+3)** · 480 TPB · GRID8 = 240 · GRID16 = 120 · BAR = 1680 |
| Form | 6 sections × 4 bars = **24 bars** (Intro → VerseA → LiftA → VerseB → Dance → Coda) |
| Total | 40320 ticks · ~40.8 s |

## 4. Two-phase architecture

**Phase 1 (raw draft, single voice):** one clarinet walks the HOME-graph Fiedler
ordering end-to-end with **unquantized pitch** (register drift + ±1.5-semitone
micro-jitter), **off-grid onsets** (±30-tick jitter), and eigenvalue-gap density.
No scale/chord snapping. Exported as `-phase1.mid`, own `validate()` gate PASS.

**Phase 2 (musicom rules):** **8th-grid snap (240 ticks)** → per-bar chord-tone
quantization (each bar's chord = a spectral cluster of the section graph) →
per-voice register clamp → full 4-voice texture. Exported as `.mid`,
`validate()` gate PASS.

## 5. Voices & instruments (from registry)

| Voice | Instrument | Program | Channel | Register (G Dorian ladder) |
|---|---|---|---|---|
| Bass | Double Bass | 43 | 0 | G2 A2 Bb2 C3 D3 E3 F3 (43–53) |
| Accordion | Accordion | 21 | 1 | G3 A3 Bb3 C4 D4 E4 F4 (55–65) |
| Clarinet | Clarinet | 71 | 2 | G4 A4 Bb4 C5 D5 E5 F5 (67–77) |
| Violin | Violin | 40 | 3 | G4 A4 Bb4 C5 D5 E5 F5 (67–77) |

Bass and accordion interlock on the dajčovo 2+2+3 grid (bass on group starts
p=0,2,4 + fifth on p=6; accordion chord stabs on offbeats p=1,3,5). Clarinet
walks the Fiedler ordering; violin walks the 2nd-eigenvector counter-axis.

## 6. Progression + spectra (G Dorian, 24 bars)

| Section | Function | λ₁ (connectivity) | Δ=λ₂−λ₁ | Lead density | Chords |
|---|---|---|---|---|---|
| Intro | HOME | 2.9227 | 0.3554 | 7 | i i i i |
| VerseA | HOME | 2.9227 | 0.3554 | 7 | i VII IV i |
| LiftA | TURN | 2.1509 | 0.2488 | 6 | IV v VII v |
| VerseB | TENSE | 1.5077 | 0.1599 | 5 | i III VII IV |
| Dance | TURN | 2.1509 | 0.2488 | 6 | IV VII i v |
| Coda | HOME | 2.9227 | 0.3554 | 7 | i VII IV i |

Chord spellings (G Dorian): i=Gm(G Bb D), II=Am, III=Bb, IV=C, v=Dm, vi°=Edim,
VII=F. The progression is the characteristic Dorian i–VII–IV turnaround with the
bright major IV (raised 6th) that defines the Balkan Dorian sound. Higher λ₁
(HOME) → denser, more connected melodic flow; lower λ₁ (TENSE) → sparser,
syncopated, ambiguous centre (exactly the SGLM tension mapping).

## 7. GRID audit (phase-2 MIDI read-back via mido, 16th = 120 / 8th = 240)

| Track | Notes | off-16th | off-8th | out-of-key | out-of-chord |
|---|---|---|---|---|---|
| Bass (ch0) | 96 | **0** | **0** | **0** | **0** |
| Accordion (ch1) | 216 | **0** | **0** | **0** | **0** |
| Clarinet (ch2) | 152 | **0** | **0** | **0** | **0** |
| Violin (ch3) | 68 | **0** | **0** | **0** | **0** |
| **TOTAL** | **532** | **0** | **0** | **0** | **0** |

**Verdict: PASS.** Every one of the 532 onsets sits exactly on the 8th grid
(multiple of 240, hence also the 16th grid). The project-078 drift bug class
(onsets at non-grid ticks like 295) is entirely absent.

## 8. HARMONY audit (every pitched note vs key scale and bar chord)

| Track | out-of-key (pc ∉ {0,2,4,5,7,9,10}) | out-of-chord (pc ∉ bar chord) |
|---|---|---|
| Bass | 0 | 0 |
| Accordion | 0 | 0 |
| Clarinet | 0 | 0 |
| Violin | 0 | 0 |
| **TOTAL** | **0** | **0** |

**Verdict: PASS.** Every one of the 532 pitched notes is a G-Dorian scale tone
AND a chord tone of its bar's chord (no project-078-style foreign-key line).

## 9. Voice-leading check (outer voices Bass + Clarinet, classical)

7 flags out of 23 bar transitions (parallel/hidden perfect intervals). Inherent
to the modal i–VII–IV turnaround (outer voices step by the same interval into
fifths/octaves while the accordion holds common tones). Reported
as-informational; the hard gates are grid + harmony (both 0). No forced
correction applied — moving a voice would break the spectral chord mapping.

## 10. Zero-drift status

| Phase | validate() | Result |
|---|---|---|
| Phase 1 (`-phase1.mid`) | `UnitMatrixComposer.validate()` | **PASS** (single voice, terminal pad) |
| Phase 2 (`.mid`) | `UnitMatrixComposer.validate()` | **PASS** (4 tracks, every cell lands on the 6720-tick section boundary) |

All cells end exactly at the section boundary (terminal landmark
`MusicEvent(0,0,SECTION_TICKS-1,SECTION_TICKS)` applied via `_pad`).

## 11. Render profile (FluidSynth FluidR3_GM → WAV → Opus OGG)

| Metric | Phase 1 | Phase 2 |
|---|---|---|
| Duration | 40.20 s | 40.77 s |
| Peak | 0.462 | 0.420 |
| Silence ratio | **4.11 %** | **6.28 %** |
| RMS mean | 0.0958 | 0.0731 |
| RMS max | 0.1196 | 0.0886 |
| Mid-track silent windows (1 s) | 0 | 0 |
| SoundFont | FluidR3_GM.sf2 | FluidR3_GM.sf2 |

Both renders healthy: no mid-track gaps (silence is only note-release + tail),
no clipping (peak < 0.5), continuous RMS. Pitch fidelity is inherent to
FluidSynth MIDI→soundfont rendering; tonal content is additionally guaranteed
by the §7–§8 audits. No custom synthesis engine used, so no FFT/autocorrelation
pitch test required.

## 12. Files

| Path | Size | Note |
|---|---|---|
| `MIDI/228-balkan-spectral-phase1.mid` | 1340 B | raw draft (single voice, off-grid) |
| `MIDI/228-balkan-spectral.mid` | 4686 B | rules-processed 4-voice |
| `MIDI/*.mid.provenance.json` (×2) | — | provenance sidecars (phase flag) |
| `Audio/228-balkan-spectral-phase1.ogg` | 378542 B | Opus 48k voip |
| `Audio/228-balkan-spectral.ogg` | 295198 B | Opus 48k voip |
| `Audio/*.wav` (×2) | ~7.1 MB | FluidSynth 16-bit stereo |
| `Analysis/grid_visualization.txt` | 2777 B | high-contrast timeline |
| `Analysis/summary.json` | 5415 B | selection + progression + spectra + audits |
| `Analysis/render_stats.json` | 716 B | silence/RMS profile |

## 13. Fixes applied this run

1. **Degenerate eigenvalue (gap = 0) on the symmetric fifths cycle:** the pure
   circulant affinity graph produced λ₁ = λ₂ (cos/sin eigenpair degeneracy,
   pitfall 3), making the Fiedler ordering ambiguous. Fixed by a `tonic_boost`
   on tonic-incident edges, which breaks the cycle symmetry and anchors the
   tonic as the spectral centre → λ₁ = 2.92 vs λ₂ = 3.28, distinct Fiedler/v₂
   axes (pitfall 4).
2. **Section-cell length overflow (track mismatch 50340 vs 40320):** the first
   melody pass placed onsets across 28 sixteenth slots but a 7/8 bar holds only
   14. Fixed by spreading onsets across the 7 **eighth** slots (8th-grid
   locked), which also drove `off-8th` from 144 → **0** (both grids clean).

## 14. Verification summary

```
grid 16th off-grid : 0 / 532   (PASS)
grid 8th  off-grid : 0 / 532   (PASS)
out-of-key          : 0 / 532   (PASS)
out-of-chord        : 0 / 532   (PASS)
zero-drift (both)   : PASS
silence (phase2)    : 6.28 %    (healthy, no mid-track gaps)
preflight           : COMPLIANT (exit 0)
```
