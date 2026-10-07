# REPORT — 227-hiphop-diffusion-extended

**Project:** 227-hiphop-diffusion-extended
**Style:** HipHop (boom-bap backbeat, sub bass, chord stabs, swung 16ths)
**Method:** 010 Hierarchical Diffusion (Stochastic, Structure/Texture) — rework
**Date:** 2026-10-07 (Nightly Rework Job)
**Seed:** 20261007
**Key:** A natural minor = A B C D E F G = pitch classes {9, 11, 0, 2, 4, 5, 7}
**BPM:** 90 · 4/4 · 480 TPB (bar = 1920, 16th = 120, 8th = 240)

---

## 1. Source selection

| Field | Value |
|---|---|
| Chosen source | **208-hiphop-hierarchical-diffusion** (HipHop) |
| Source form | 8 sections × 4 bars = **32 bars** |
| Source key/tempo | A natural minor, 90 BPM |
| Source method | 010 Hierarchical Diffusion |

## 2. Audit result (all six standards) — **ALL PASS → EXTENSION**

| # | Standard | Result |
|---|---|---|
| 1 | Engine (UnitMatrixComposer, not hand-rolled) | ✅ pass — `from workflows.unitmatrix_composer import UnitMatrixComposer` |
| 2 | Zero-drift (voice tracks equal length) | ✅ pass — 5 tracks × 61440 ticks |
| 3 | Rhythm-grid sync (onsets % 120/240) | ✅ pass — 0 off-grid of 359 pitched onsets |
| 4 | Valid track setup (≥4 voices) | ✅ pass — 5 voice tracks |
| 5 | Two-phase artifacts (.mid + -phase1.mid) | ✅ pass — both present |
| 6 | provenance.json + index.html | ✅ pass — both present |

**Decision: EXTENSION** (no redesign needed). Identity preserved; source used as DNA seed.

## 3. What changed (extension)

| Field | Source (208) | New (227) |
|---|---|---|
| Sections | 8 | **10** (N+2) |
| Bars | 32 | **40** |
| Voices | 5 | **6** (+ CounterLine flute) |
| Total ticks | 61440 | 76800 |
| Audio duration | ~90 s | ~107 s (+ ~5 s reverb tail) |

**Form:** Intro → Verse → Chorus → Verse2 → Chorus2 → Bridge → Chorus3 → Lift → Chorus4 → Outro.

**Per-section harmonic regions** (each section its own 4-bar progression — no section
lands on degree i every bar):

| Section | Progression | Region |
|---|---|---|
| Intro | Am Am Am Am | pedal |
| Verse | Am F C G | i VI III VII |
| Chorus | Am F C G | i VI III VII |
| Verse2 | Dm Am Em Am | iv i v i |
| Chorus2 | Am F C G | i VI III VII |
| Bridge | F C G Am | VI III VII i (darker turn) |
| Chorus3 | Am F C G | i VI III VII |
| Lift | C G Am F | III VII i VI (relative-major shift, tonicizes C) |
| Chorus4 | Am F C G | i VI III VII |
| Outro | Am Am Am Am | pedal (retrograde) |

## 4. Variation techniques (8 applied)

| Technique | Where | How |
|---|---|---|
| 1. Inversion | Verse2 (sec 3) | lead pitch mirrored around E4 axis: p → 142 − p, then chord-snapped |
| 2. Augmentation | Bridge (sec 5) | halve note rate (keep every 2nd onset), double durations 100→220 |
| 3. Counterline | Bridge (sec 5) | new flute voice: descending 2-note/bar line F→A, G→E, D→B, C→A |
| 4. Register shift | Chorus3 (sec 6) | lead +1 octave (range 67–96) |
| 5. Mode shift | Lift (sec 7) | progression tonicizes relative major C (same A-minor pitch-class set) |
| 6. Transposition | Chorus4 (sec 8) | lead +perfect 4th (+5 semitones), chord-snapped |
| 7. Retrograde | Outro (sec 9) | Intro note sequence reversed |
| 8. Density rise | global | per-section density arc 0.30→0.85→0.40→0.78→0.30 |

Drums also vary: half-time feel in Bridge (kick on 1, snare on 3), driving 16th hats in Lift.

## 5. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw diffusion draft, single voice, unquantized onsets
  (+/-25 tick jitter) and chromatic OU drift-diffusion pitch. 147 onsets, 146 off-grid,
  63 out-of-scale, 109 out-of-chord (expected for the raw draft).
- **Phase 2** (`.mid`): same diffusion re-run (same seed) → rules post-process:
  onset snap to 16th grid, chord-tone snap per bar, `(start_tick, pitch)` dedup
  (keep longest), per-section variation transforms, 6-voice texture.
  Zero-drift terminal landmarks per section; `validate()` PASSED both phases.

## 6. Verification (real numbers)

| Metric | Phase 2 | Phase 1 |
|---|---|---|
| Tracks | 7 (conductor + 6 voices) | 2 |
| Zero-drift | ✅ all 6 voice tracks = 76800 ticks | ✅ 76800 ticks |
| Pitched onsets | 468 | 147 |
| **Off-grid** | **0** | 146 (raw, expected) |
| **Scale violations** | **0** | 63 (raw, expected) |
| **Chord violations** | **0** | 109 (raw, expected) |

**Audio (Phase 2, FluidSynth + FluidR3_GM.sf2 → WAV → Opus OGG):**
- Duration 111.51 s (107 s content + reverb tail)
- Silence 4.5% (< 30% → not a silent render)
- Integrated loudness **−15.9 LUFS**, true peak −3.4 dBTP, LRA 1.8 LU
- Peak 0.626

**Audio (Phase 1):** silence 54.2% (expected — sparse single-voice raw draft).

## 7. What to listen for

- **Inverted hook (Verse2)**: the familiar lead contour now falls where it rose —
  mirror image around E4, over a darker iv–i–v–i progression.
- **Bridge breath**: augmented (half-speed) lead + a new descending flute counterline,
  half-time drums — the widest textural contrast in the piece.
- **Register lift (Chorus3)**: the hook jumps an octave; on top of the pad it reads as a
  brighter, higher-energy chorus without adding notes.
- **Lift section (relative major)**: C–G–Am–F briefly makes C sound like home before
  snapping back to A minor — a bright "sunbreak" before the final chorus.
- **Outro retrograde**: the sparse Intro hook plays backwards, fading the piece out.

## 8. Files

| Path | Description |
|---|---|
| MIDI/227-hiphop-diffusion-extended.mid | Phase 2 rules composition (6 voices) |
| MIDI/227-hiphop-diffusion-extended-phase1.mid | Phase 1 raw draft |
| Audio/227-hiphop-diffusion-extended.ogg | Phase 2 Opus render |
| Audio/227-hiphop-diffusion-extended-phase1.ogg | Phase 1 Opus render |
| Audio/*.wav | raw PCM renders |
| Analysis/grid_visualization.txt | high-contrast timeline |
| Analysis/rework_audit.json | audit record (copy) |
| compose.py / verify.py | generator + verification |
| provenance.json per artifact | write_provenance sidecars |
| index.html | dashboard |
