# 103-japanese-kojo-koto — Japanese × Method 019 (L-System Algorithmic Composition)

**Style:** Japanese (koto + shakuhachi + shamisen + taiko, Jo-Ha-Kyu form)
**Method:** 019 L-System Algorithmic Composition (dragon-curve / paperfolding grammar)
**Layer:** `concrete`
**Date:** 2026-09-23 (Nightly Autonomous Composition Job)
**Key:** A hirajoshi pentatonic (A Bb D E G) · **BPM:** 80 · **Meter:** 4/4 · **TPB:** 480
**Form:** Jo | Ha1 | Ha2 | Kyu1 | Kyu2 | Jo_Coda (6 sections × 4 bars = 24 bars)
**Duration:** ~75.3 s (46,080 ticks)
**Project dir:** `/opt/data/repos/musicom/projects/Styles/Japanese/103-japanese-kojo-koto`

---

## Concept

A meditative Japanese piece built on a self-similar **L-System dragon-curve**
fractal melody. The grammar `A → A+B, B → A-B` with `+`/`-` as ±2-semitone
steps generates a balanced, bounded contour (255 deltas at 8 iterations).

**Two-phase architecture:**
1. **Phase 1 (raw):** single Koto walks the fractal — unquantized micro-rhythm,
   no scale/chord snapping (whole-tone stepwise contour preserved).
2. **Phase 2 (rules):** grid quantization (16th/8th), A-hirajoshi diatonic +
   per-bar palette (chord-tone) snapping, full 5-voice Japanese arrangement.

The **Jo-Ha-Kyu** acceleration arc drives density: Jo (sparse quarter-notes) →
Ha (eighth-notes, flute enters) → Kyu (full 16th runs) → Jo_Coda (resolve to tonic drone).

---

## Audio & MIDI Artifacts

- **Phase 2 (master arrangement):**
  - MIDI: `MIDI/103-japanese-kojo-koto.mid` (5,089 B)
  - WAV: `Audio/103-japanese-kojo-koto.wav` (13.3 MB)
  - OGG: `Audio/103-japanese-kojo-koto.ogg` (1.5 MB)
- **Phase 1 (raw L-system draft):**
  - MIDI: `MIDI/103-japanese-kojo-koto-phase1.mid` (1,699 B)
  - WAV: `Audio/103-japanese-kojo-koto-phase1.wav` (13.3 MB)
  - OGG: `Audio/103-japanese-kojo-koto-phase1.ogg` (1.6 MB)

---

## Verification & Audit Highlights

- `validate()`: **PASS** (zero-drift, all 5 voices = 46,080 ticks).
- 16th-Grid Audit: **0 / 556 notes off-grid** (100% on 120-tick grid).
- Harmony Audit: **0 out-of-scale, 0 out-of-chord**.
- Phase 1 Timing Fingerprint: **190 / 192 notes off-grid (99.0% raw)**.
- Audio: **6.45% silence, 100% tonal frames** (50–1000 Hz).

Full detail in `REPORT.md`.
