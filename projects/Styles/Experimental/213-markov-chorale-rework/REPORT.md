# 213 — Markov Chain Chorale Rework

**Job:** autonomous nightly REWORK. **Source:** `Experimental/066-markov-chain-chorale`
(Method 020 First-Order Markov Chain Sequencing). **Decision:** extension (identity preserved).
**Date:** 2026-09-30.

## Audit result (Step 2)

The source was audited against the six current standards:

| # | Standard | Result |
|---|----------|--------|
| 1 | Engine (`UnitMatrixComposer`) | ✅ pass |
| 2 | Zero-drift (equal track length) | ✅ pass (4 x 15360) |
| 3 | Rhythm-grid sync (onset %120/240) | ✅ pass (0 off-grid) |
| 4 | >=4 voice tracks | ✅ pass (4: SATB) |
| 5 | Two-phase artifacts (`-phase1.mid`) | ✅ pass |
| 6 | `provenance.json` + `index.html` | ❌ **FAIL** (only `.provenance.json` sidecars; no root provenance.json, no index.html) |

`standard_failures = ["provenance.json + index.html missing"]` →
`redesign_required = true` formally, but the only breach was the dashboard/sidecar pair.
The musical identity and engine compliance were intact, so this is a **preserving
extension**, not a from-scratch discard: same key, tempo, method, 4-part texture, and
stepwise-Markov pitch DNA are retained; the non-compliant deliverable gap is corrected.

## Source identity (extracted DNA)

- Genre: Experimental (chorale)
- Key: F major (ionian); BPM 92; 4/4 (480 tpb, 1920 ticks/bar)
- Method: 020 — first-order Markov chain over 12 pitch classes (neighbour-biased,
  chromatic escape states) + a second first-order chain over durations {1/8, 1/4}
- Voices: Soprano (Flute), Alto/Tenor (Strings), Bass
- Form: 4 sections × 2 bars = 8 bars; harmony I–vi–IV–V

## What changed (Step 4)

1. **Longer form** — 8 sections × 2 bars = **16 bars** (doubled; 8 → 16). Section map:
   Intro / VerseA / VerseA2 / PreChorus / Chorus / Chorus2 / Bridge / Outro.
2. **More variation (>=3 techniques)** — documented per section:
   - **Transposition** — VerseA2 +5 semitones, Chorus +12, Outro −12.
   - **Inversion** — Chorus2 (axis 69) and Bridge (axis 66) mirror the motif contour.
   - **Diminution** — PreChorus and Chorus halve durations (×0.5) → eighth/16th density.
   - **Augmentation** — Outro doubles durations (×2.0) → half-note breadth.
   - **Register shift** — Chorus lifts +12, Outro drops −12.
   - **Density rise** — Chorus adds 16th-note closed hi-hat on ch9.
3. **Per-section harmonic regions** — each section owns a short 2-bar progression; the
   **midpoint chord** (2nd bar) drives the region so no section defaults to the bar-0
   tonic bug. Midpoint degrees: `[IV, I, ii, V, V, IV, iii, I]`.
4. **Added ch9 drums** (5 voices: SATB + Drums) — backbeat (kick 1&3 / snare 2&4),
   quarter hi-hat, denser 16th hi-hat in Chorus.
5. **Two-phase architecture** — Phase 1 = raw chromatic Markov draft (single voice,
   94 events, 10 non-diatonic leaks preserved); Phase 2 = per-bar chord quantization,
   rhythm-grid snap, diatonic block harmony, voice-leading optimization + Phase 2c
   correction, zero-drift gate.

## Verification (Step 6 — real numbers)

- 5 voice tracks, all length **30720** ticks (zero-drift PASS).
- Off-grid pitched onsets: **0**.
- Scale violations (pc ∉ F major): **0**.
- Chord violations (note ∉ its own bar's triad): **0**.
- Parallel/hidden fifth violations: **0**.
- MIDI sizes: phase2 2459 B, phase1 912 B (both > 40 B).
- Audio: 48.93 s, silence ratio 11.7% (under the 30% trap), approx −17.4 dBFS.

## Artifacts

- `MIDI/213-markov-chorale-rework.mid` — Phase 2 (rules, full 5-voice)
- `MIDI/213-markov-chorale-rework-phase1.mid` — Phase 1 (raw, single voice)
- `Audio/213-markov-chorale-rework.wav` — FluidSynth render (FluidR3_GM.sf2)
- `Audio/213-markov-chorale-rework.ogg` — Opus (Telegram)
- `Analysis/grid_visualization.txt` — rhythm DNA
- `Analysis/rework_audit.json` — source audit (in 066)
- `index.html` — VoltAgent dashboard
- `provenance.json` — root sidecar