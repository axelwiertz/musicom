# 231 — Perlin Noise × LPC Rework

**Job:** autonomous nightly REWORK. **Source:** `Experimental/056-perlin-lpc`
(Method 040 Perlin Noise Composition, SP-028 LPC synthesis). **Decision:** redesign
(identity preserved; non-compliant parts rebuilt from scratch).
**Date:** 2026-10-09.

## Audit result (Step 2)

The source was audited against the six current standards:

| # | Standard | Result |
|---|----------|--------|
| 1 | Engine (`UnitMatrixComposer`) | ✅ pass |
| 2 | Zero-drift (equal track length) | ✅ pass (4 × 23040) |
| 3 | Rhythm-grid sync (onset %120/240) | ❌ **FAIL** (14 pitched onsets off-grid) |
| 4 | >=4 voice tracks | ✅ pass (4: Lead/Pad/Bass/Drums) |
| 5 | Two-phase artifacts (`-phase1.mid`) | ❌ **FAIL** (missing) |
| 6 | `provenance.json` + `index.html` | ❌ **FAIL** (index.html present; root provenance.json missing — only `*.mid.provenance.json` sidecars) |

`standard_failures = [grid-sync, two-phase, provenance]` → `redesign_required = true`.
The engine, zero-drift and track-setup standards were intact, but the rhythmic
drift and the missing phase-1/provenance artifacts required a from-scratch rebuild
of the generator (the old `compose.py` emitted Perlin onsets on raw 640-tick steps
that never land on the 120/240 grid).

## Source identity (extracted DNA)

- Genre: Experimental
- Key: D Dorian (D E F G A B C); BPM 80; 4/4 (480 tpb, 1920 ticks/bar)
- Method: 040 — Perlin noise fBm (seed 42) driving pitch contour, rhythm density, velocity
- Voices: Lead (Flute 74), Pad (String Ensemble 49), Bass (Electric Bass 33), Drums (ch9)
- Form: ABA' (3 × 4 bars = 12 bars); harmony D Dorian diatonic triads

## What changed (Step 4)

1. **Longer form** — 12 → **16 bars**, 3 → **8 sections**. Section map:
   Intro / VerseA / VerseA2 / VerseB / PreChorus / Chorus / Bridge / Outro (2 bars each).
2. **More variation (6 techniques)** — documented per section:
   - **Transposition** — VerseA2 +5 semitones, Chorus +12, Outro −12.
   - **Inversion** — VerseB (axis 67) and Bridge (axis 65) mirror the motif contour.
   - **Diminution** — PreChorus and Chorus halve durations (×0.5) → eighth/16th density.
   - **Augmentation** — Outro doubles durations (×2.0) → half-note breadth.
   - **Register shift** — Chorus lifts +12, Outro drops −12.
   - **Density rise** — Chorus adds 16th-note closed hi-hat on ch9.
3. **Per-section harmonic regions** — each section owns a short 2-bar Dorian
   progression; the **midpoint chord** drives the region so no section defaults to
   the bar-0 tonic bug. Midpoint degrees: `[VII, IV, III, v, IV, VII, v, i]`.
4. **Two-phase architecture** — Phase 1 = raw Perlin fBm draft (chromatic pitch
   60–76, unquantized durations, single voice, 64 events, 34 non-diatonic leaks
   preserved); Phase 2 = per-bar chord quantization, rhythm-grid snap, diatonic
   block harmony via `Scale7ChordDegree.get_diatonic_note()`, voice-leading
   optimization + correction, zero-drift gate.

## Verification (Step 6 — real numbers)

- Phase 2: 4 voice tracks, all length **30720** ticks (zero-drift PASS).
- Off-grid pitched onsets: **0**.
- Scale violations (pc ∉ D Dorian): **0**.
- Chord violations (note ∉ its own bar's triad): **0**.
- Parallel/hidden fifth violations: **0**.
- MIDI sizes: phase2 2251 B, phase1 685 B (both > 40 B).
- Phase 1 (raw) sanity: 62 off-grid, 39 non-diatonic, 52 off-chord — proves the
  draft was genuinely raw and the rules layer cleaned it.
- Audio: 55.59 s, silence ratio 10.9% (under the 30% trap), approx −18.8 dBFS.

## Artifacts

- `MIDI/231-perlin-lpc-rework.mid` — Phase 2 (rules, full 4-voice)
- `MIDI/231-perlin-lpc-rework-phase1.mid` — Phase 1 (raw, single voice)
- `Audio/231-perlin-lpc-rework.wav` — FluidSynth render (FluidR3_GM.sf2)
- `Audio/231-perlin-lpc-rework.ogg` — Opus (Telegram)
- `Analysis/grid_visualization.txt` — rhythm DNA
- `Analysis/rework_audit.json` — source audit (written to 056)
- `index.html` — VoltAgent dashboard
- `provenance.json` — root sidecar
