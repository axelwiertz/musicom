# 101-folk-sieve — Folk × Method 025 (Xenakis Sieve Theory)

**Project:** 101-folk-sieve  
**Style:** Folk (Dorian Reel / Morris Folk Dance)  
**Method:** 025 Xenakis Sieve Theory (Modular Congruence & Residual Sieve Intersections)  
**Layer:** `concrete`  
**Date:** 2026-09-22 (Nightly Autonomous Composition Job)  
**Key:** D Dorian · **BPM:** 116 · **Meter:** 4/4 · **TPB:** 480  
**Form:** 6 sections × 4 bars = 24 bars (Intro | Theme_A | Theme_B | Breakdown | Theme_A_Var | Outro)  
**Duration:** ~59.6 s (46,080 ticks)  
**Project Dir:** `/opt/data/repos/musicom/projects/Styles/Folk/101-folk-sieve`

---

## Concept & Architectural Overview

This project composes a traditional English/Celtic-influenced Folk Reel using **Method 025 (Xenakis Sieve Theory)** under the mandatory two-phase architecture:

1. **Phase 1 (Raw Sieve Walk):** A single-voice generative draft on Fiddle. Pitches and timings are generated through modular congruence sieve residual classes without harmonic constraints or time grid locking. Micro-timing fluctuations create an unquantized acoustic feel.
2. **Phase 2 (Musicom Rules Post-Processing):** Rhythmic quantization to the strict 16th grid (120 ticks @ 116 BPM), diatonic D Dorian mapping, and bar-by-bar chord-tone snapping. Full folk dance arrangement:
   - **Lead Fiddle:** Virtuosic 16th-note reel runs driven by Xenakis pitch and rhythm sieves.
   - **Tin Whistle / Flute:** Lyrical sustained countermelodies.
   - **Acoustic Guitar:** Traditional rhythmic strumming (boom-chick reel pattern).
   - **Double Bass:** Root-fifth dance foundation.
   - **Bodhrán / Drum Kit:** Deep percussion pulses and sieve-accented syncopations.

---

## Audio & MIDI Artifacts

- **Phase 2 (Master Arrangement):**
  - MIDI: `MIDI/101-folk-sieve.mid` (9,886 bytes)
  - WAV: `Audio/101-folk-sieve.wav` (10,520,620 bytes)
  - OGG: `Audio/101-folk-sieve.ogg` (1,039,157 bytes)
- **Phase 1 (Raw Sieve Draft):**
  - MIDI: `MIDI/101-folk-sieve-phase1.mid` (1,700 bytes)
  - WAV: `Audio/101-folk-sieve-phase1.wav` (9,188,652 bytes)
  - OGG: `Audio/101-folk-sieve-phase1.ogg` (963,256 bytes)

---

## Verification & Audit Highlights

- `validate()`: **PASS** (Zero-drift verified across all 5 voices, 46,080 ticks).
- 16th-Grid Audit: **0 / 1240 notes off-grid (100% on 120-tick grid)**.
- Harmony Audit: **0 out-of-scale, 0 out-of-chord**.
- Phase 1 Timing Fingerprint: **191 / 192 notes off-grid (99.5% raw unquantized)**.
- Audio Analysis: **15.94% silence ratio, 97.48% tonal frames in 50–1000 Hz**.
- Preflight: **Exit 0 (no raw mido authoring, clean musicom engine)**.
