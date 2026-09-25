# REPORT — 203 Brownian Chorale Variations (rework of 062)

## 1. Source selected

- **Project:** `Experimental/062-brownian-chorale`
- **Genre:** Experimental
- **Primary MIDI:** `MIDI/062-brownian-chorale.mid`
- **Method:** 048 — Reflected Brownian Motion Pitch Diffusion (RBMPD)

## 2. Audit result

| Standard | Result |
|---|---|
| 1. Engine (UnitMatrixComposer) | PASS |
| 2. Zero-drift (4 voice tracks, 15360 ticks) | PASS |
| 3. Rhythm-grid sync (0 off-grid) | PASS |
| 4. Valid track setup (4 pitched voices) | PASS |
| 5. Two-phase artifacts | **FAIL** — phase1 MIDI missing |
| 6. provenance.json + index.html | **FAIL** — both missing |

→ `redesign_required = true`. Audit persisted to
`Experimental/062-brownian-chorale/Analysis/rework_audit.json`.

## 3. Decision

**Redesign.** Rebuilt from scratch through canonical `UnitMatrixComposer`,
preserving identity (C aeolian, 84 BPM, RBMPD method, 4-voice homophonic
chorale, modal cadence DNA). Non-compliant artifact gaps closed: both phase
MIDIs, project provenance.json, index.html now present.

## 4. New piece — longer + more varied

- **Form:** 16 bars (vs 8), 4 regions × 4 bars, 6 voice tracks (vs 4).
- **Length:** 30720 ticks = 48.1 s at 84 BPM.

### Variation techniques (5 applied)

1. **Harmonic rotation** (Verse): source i-VI-III-VII rotated to III-VII-i-VI —
   section starts off-tonic, never lands all sections on degree i.
2. **Register lift** (Verse): soprano chord-tone set shifted up, brighter top line.
3. **Augmentation** (Chorus): rhythm slowed to 8th-note grid (half speed),
   longer note durations.
4. **Retrograde** (Bridge): soprano contour reversed within the bar.
5. **Counterline + density rise** (Chorus/Bridge): added violin counterline
   voice + denser Bridge mask (threshold 0.55×) + ch9 drum pulse throughout.

### Per-section harmonic regions

| Region | Bars | Progression | Midpoint chord (root) |
|---|---|---|---|
| Intro | 1–4 | i VI III VII | VI |
| Verse | 5–8 | III VII i VI | VII |
| Chorus | 9–12 | iv VII VI III | VII |
| Bridge | 13–16 | v iv VII i | iv |

Each bar's chord quality derived from its own degree (diatonic stacked thirds);
root derivation uses region midpoint — avoids the bar-0 tonic bug.

## 5. Two-phase artifacts

- **Phase 1** (`-phase1.mid`): raw reflected-Brownian walk, unquantized pitch,
  single voice, own `validate()` gate (PASS).
- **Phase 2** (`.mid`): chord-tone quantization + classical voice leading
  (parallel 5th/8ve scan) + rhythm-grid snap + register enforcement.

## 6. Verification (read-only mido audit)

- phase-2: **6** voice tracks, all **30720** ticks (zero-drift PASS).
- off-grid pitched onsets: **0**.
- scale violations (phase-2): **0** (skip ch9).
- chord violations (phase-2): **0** (skip ch9).
- file sizes all > 40 B (phase2 2320 B, phase1 464 B, ogg 374655 B, wav 8490540 B).
- audio: silence ratio **6.1%** (< 30% flag), peak **0.957**, rough LUFS **−15.8 dB**.

## 7. Files

- `MIDI/203-brownian-chorale-variations.mid`
- `MIDI/203-brownian-chorale-variations-phase1.mid`
- `Audio/203-brownian-chorale-variations.ogg`
- `Audio/203-brownian-chorale-variations.wav`
- `Analysis/grid_visualization.txt`
- `index.html`, `README.md`, `provenance.json`
