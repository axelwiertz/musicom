# REPORT — SP-157 Whole-Tone Filter Bank × 247-metal-fourier-spectrum

**Job:** random-style production (SP) — layer-aligned (2026-11-19)
**Method:** SP-157 — 48-Band Whole-Tone Filter Bank (AudioThing/Hainbach "Seconds"-style)
**Source composition:** `Metal/247-metal-fourier-spectrum` (Method 113 Pitch-Class Fourier Spectrum Composition)
**Seed:** 20261119

---

## 1. Selection

| Field | Value |
|---|---|
| Registry source | `workflows.musicom_workflow.SP_METHODS` (104 implemented entries) |
| Method | **SP-157** → `sound.effects.whole_tone_filterbank` |
| Source MIDI | `Styles/Metal/247-metal-fourier-spectrum/MIDI/247-metal-fourier-spectrum.mid` |
| Candidates | 470 `.mid` scanned → 365 well-formed → 364 meaningful (≥3 pitch classes) |
| Recent excluded (≤7 d) | SP-075, SP-084, SP-100, SP-107, SP-115, SP-146, SP-154 |
| Already-on-source | — (none) |
| Baseline excluded | SP-001 |
| Pool size | 96 |

## 2. Source composition

| Field | Value |
|---|---|
| Style / key | Metal — **E minor** (tonic pc 4) |
| Method of origin | 113 Pitch-Class Fourier Spectrum Composition (PCFSC), layer abstract |
| BPM / meter / TPB | 140 · 4/4 · 480 TPB (16th = 120, 8th = 240, bar = 1920) |
| Length | 32 bars (head-solos-head: Head1·Solo1·Solo2·Head2, 8 bars each), ~54.9 s |
| Voices | Lead (Overdriven Guitar 29, ch0, 448 n), Rhythm (29, ch1, 1152 n), Bass (Electric Bass 33, ch2, 384 n), Drums (ch9, 676 n) |
| Section pools | Head1/Head2 E natural minor {0,2,4,6,7,9,11}; Solo1 E harmonic minor {0,3,4,6,7,9,11}; Solo2 E half-whole octatonic {1,2,4,5,7,8,10,11} |
| Chord path | Em·Em·C·G·D·C·D·Em ‖ Em·Am·B·Em·C·F♯dim·B·Em ‖ Em·Edim7·Fdim7·Em·Edim7·Bdim·Fdim7·Em ‖ Em·Em·C·G·D·C·D·Em |

## 3. Pre-flight — RULES ADHERENCE GATE

| Rule | Before (source .mid) | After (rework) |
|---|---|---|
| 1. Grid sync (16th = 120) | **FAIL — 1826 off-grid** (humanized micro-timing) | **PASS — 0 off-grid** |
| 2. Harmony (in-scale + chord-tone) | PASS — 0 out-of-scale, 0 out-of-chord | **PASS — 0 / 0** |
| 3. Zero-drift (all tracks 61440) | PASS — 4 tracks equal | **PASS — 4 tracks = 61440** |

**Verdict: FAIL (rule 1) → rework required.** The source `.mid` is the
composition job's always-on **humanized** export — micro-timing puts 1826/1984
pitched onsets off-grid. Harmony and zero-drift were already clean.

**Rework (two-phase discipline):** de-humanized the source by snapping every
`note_on` onset to the nearest 16th grid (`round(start/120)*120`), preserving
per-note durations and the pitch-0 terminal landmark. Humanization shifted each
onset ≤20 ticks from its grid position, so `round/120` recovers the exact
pre-humanization grid. Re-audit: **0 off-grid / 0 out-of-scale / 0 out-of-chord
/ zero-drift**. Raw phase-1 draft preserved as `-phase1.mid` sidecar; original
humanized export preserved as `-humanized.mid` sidecar.

## 4. SP-157 method — 48-Band Whole-Tone Filter Bank

**Layer: ABSOLUTE** — one resonant 48-band whole-tone bank applied across the
whole dry mix. The bank spans 8 octaves (40 Hz → 9.12 kHz), 48 RBJ bandpass
bands spaced in whole-tone steps (ratio 2^(2/12) ≈ 1.1225).

| Param | Value |
|---|---|
| bands / f0 / f_last | 48 · 40.0 Hz · 9122.8 Hz (span 7.83 octaves) |
| resonance | 0.25 (Q ≈ 4.35 · 2.5 ≈ 10.9 per band, self-resonant "ping" colour) |
| gain profile | **spectral freeze** of the dry mix (FFT band-energy profile) + 0.15 floor |
| strong bands | 13 (bands > 0.5 gain after freeze) |
| pan spread | 0.40 (odd/even band alternating stereo width) |
| ring mod | **0.0** (OFF — per-band ring mod adds inharmonic sidebands that would break pitch verification) |

Pipeline: reworked MIDI → dry FluidSynth (`-R 0 -C 0 -g 1.2`, FX off) →
SP-157 whole-tone bank (freeze-gain + resonance + odd/even pan) → `master()`
(target −14.0 LUFS, −1 dBTP ceiling) → WAV + Opus OGG → pitch/silence/RMS
verification → provenance + this report.

## 5. Verification (pitch mandatory check)

| Metric | Value |
|---|---|
| Pitch hit rate (0.5 s windows vs per-section pool) | **0.8273** (wet) · 0.8455 (dry) — 108 valid windows |
| Mean harmonic energy (8 harmonics of dominant peak) | **0.2813** wet · 0.1877 dry |
| Harmonic-energy retention vs dry | **1.499** (≥ 0.40 threshold) — bank *boosts* harmonic energy |
| **Pitch verdict** | **PASS** — tonal, not noise; resonant bank concentrates energy on harmonics |
| Integrated LUFS | −14.00 (target −14.0) |
| True peak | −1.93 dBTP (ceiling −1.0 — legit below ceiling for a −14 LUFS dynamic piece) |
| Peak (sample) | 0.8006 |
| Silence ratio | **5.17%** (trailing decay after final note; no mid-track gaps) |
| RMS | 0.1475 (per-second RMS map continuous 0–55 s, then clean tail decay) |

Note: dry harmonic energy 0.19 is expected for a dense metal mix (the metric
sums 8 harmonic bands of a single dominant peak against the full-mix energy);
the wet/dry retention ratio 1.499 is the meaningful signal — the whole-tone
bank preserves and sharpens tonal content, it does not add noise.

## 6. Artifacts

| File | Size |
|---|---|
| `SP157-whole-tone-filterbank-247-metal-fourier-spectrum.wav` | 10,118,188 B (57.3 s, 44.1 kHz stereo) |
| `SP157-whole-tone-filterbank-247-metal-fourier-spectrum.ogg` | 354,865 B (Opus 48k voip) |
| `dry_full_mix_sp001_reference.wav` | 10,118,188 B (dry reference) |
| `MIDI/247-metal-fourier-spectrum.mid` | 19,495 B (reworked — grid-quantized, clean) |
| `MIDI/247-metal-fourier-spectrum-humanized.mid` | 19,431 B (original humanized source) |
| `MIDI/247-metal-fourier-spectrum-phase1.mid` | 2,247 B (raw phase-1 draft) |
| `Analysis/preflight.json`, `Analysis/render_stats.json`, `provenance.json` | — |

## 7. Notes

- **Pre-flight caught a real rule-1 failure**: the composition job ships a
  humanized MIDI, so the production gate's grid-sync rule legitimately fails on
  it. De-humanization (round/120 snap) recovered the perfect grid without
  touching harmony (already 0/0) or zero-drift.
- **Ring mod deliberately OFF**: per-band ring mod would generate inharmonic
  sidebands and mask the fundamental (failing the pitch check). The freeze +
  resonance + pan-spread combination still exercises the bank's signature
  spectral features.
- `master()` true-peak is a ceiling, not a target: −14 LUFS metal legitimately
  lands at −1.93 dBTP. Correct behaviour, not fixed.
- Wall clock: dry render 1.2 s + SP-157 11.1 s + master ~140 s = **160.5 s**
  total (master LUFS metering dominates, as usual).
- File sizes all `> 40 B` (no empty-output trap); OGG `> 10 KB`.
