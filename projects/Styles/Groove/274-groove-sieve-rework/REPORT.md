# REPORT — 274-groove-sieve-rework

**Project:** 274-groove-sieve-rework · **Date:** 2026-10-30 · **Job:** nightly rework cron

## 1. Source selection + audit

| Field | Value |
|---|---|
| Chosen source | `Styles/Groove/080-groove-sieve` (age 62.1 d, mtime 2026-08-28) |
| Genre | Groove |
| Primary MIDI | `MIDI/080-groove-sieve.mid` |
| Audit | **REDESIGN REQUIRED** — 1 standard failed |

**Standards:**

| Standard | Result |
|---|---|
| engine (UnitMatrixComposer, no raw mido) | ✅ PASS |
| zero-drift (5 voice tracks equal 46080 ticks) | ✅ PASS |
| rhythm-grid (0 off-grid pitched onsets) | ✅ PASS |
| track-setup (6 tracks, ch9 drums) | ✅ PASS |
| two-phase artifacts (`-phase1.mid` present) | ✅ PASS |
| provenance.json + index.html | ❌ FAIL — no `index.html` dashboard (only `.mid.provenance.json` sidecars) |

Detailed audit: `../080-groove-sieve/Analysis/rework_audit.json`.

## 2. Preserved musical identity (DNA)

- Key **G natural minor** (G A Bb C D Eb F; pcs `{7,9,10,0,2,3,5}`)
- **Xenakis Sieve** (Method 025): C = A (mod 8, res {0,2,5}) ∩ B (mod 7, res {0,1,4}),
  period lcm(8,7) = 56, offsets `[0,8,18,21,29,32,42,50,53]`
- Tempo **110 BPM** 4/4 · 480 TPB (bar 1920)
- Voices: Lead (Soprano Sax 65), Horns (Brass 61), Rhodes (EP 4), Bass (EB 33), Drums (ch9)

## 3. What changed (redesign, from scratch via canonical engine)

- Rebuilt through `UnitMatrixComposer` (flat `structures`/`workflows` imports).
- **Longer**: 32 bars / 8 sections (source was 24 bars / 6 sections).
- **Per-section harmonic regions** — each section its own progression; section
  roots differ (i / III / iv / VI), no bar-0 tonic collapse.
- Added a 6th voice **Counter** (String Ensemble 48) in chorus sections only.

## 4. Form (32 bars / 8 sections)

| Section | Bars | Progression | Variation technique |
|---|---|---|---|
| Intro | 4 | i — VII — i — VII | sieve exposed, sparse |
| VerseA | 4 | i — III — iv — v | core sieve motif |
| VerseB | 4 | i — iv — v — VI | **transposition +12** |
| Chorus | 4 | III — VII — i — iv | **counterline + density rise** |
| Bridge | 4 | VI — III — VII — v | **inversion** (sieve offsets negated) |
| VerseC | 4 | i — III — iv — v | **retrograde** (offset sequence reversed) |
| Chorus2 | 4 | III — VII — i — iv | transposition + densest |
| Outro | 4 | i — VI — VII — i | **augmentation** (onset step ×2) |

## 5. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw sieve walk, single voice (LeadRaw 65),
  off-grid onsets, unquantized chromatic wander around sieve offsets, no harmony.
  Own `UnitMatrixComposer` + `validate()` gate (PASS). 252 raw events.
- **Phase 2** (`-perfect.mid`): grid snap (16th) → scale quantize →
  chord-tone quantize **per bar** (`t // BAR`) → voice-leading (leap cap 9) →
  range-restricted (48–84) → 6-voice arrangement. `validate()` PASS.
- **Dual-version**: `export_dual` → `-perfect.mid` (grid-locked) +
  `-humanized.mid` (style groove + per-instrument DNA, seeded hz 62194).

## 6. Verification (read-only mido audit)

| Check | phase1 (raw) | perfect | humanized |
|---|---|---|---|
| File size > 40 B | 2316 ✓ | 8971 ✓ | 8969 ✓ |
| Zero-drift | 1 × 61440 ✓ | 6 × 61440 ✓ | 6 × 61440 ✓ |
| Pitched onsets | 252 | 652 | 652 |
| Off-grid pitched onsets | 243/252 (raw) | **0/652 ✓** | 570/652 (>0, jitter ran) |
| Scale violations | 36 (raw) | **0 ✓** | **0 ✓** |
| Chord violations (t//BAR) | 176 (raw) | **0 ✓** | 18 (bar-boundary jitter ≤5 t) |

Humanized chord "violations" (18) are onset-jitter artifacts: every note is
in-scale and a valid chord tone of its **source** bar; its onset jittered 1–5
ticks across a bar line, so strict `t//BAR` attribution lands on the neighbor
bar's chord. Perfect layer (compositional truth) is 0 / 0 / 0.

## 7. Humanization (style groove + per-instrument DNA, seed 62194)

Style groove profile: timing σ 3.0 ms, velocity σ 5.0, phrase_corr 0.15, layback 1.0 ms.

| Voice | mean|Δshift| (ticks) | max|Δshift| | mean vel Δ |
|---|---|---|---|---|
| Lead | 1.86 | 7 | 5.68 |
| Horns | 2.00 | 8 | 5.69 |
| Rhodes | 1.98 | 8 | 4.44 |
| Bass | 7.38 | 15 | 2.65 |
| Counter | 2.38 | 6 | 4.13 |
| Drums | 1.22 | 5 | 3.24 |

Drums tightest (anchors grid), bass lays back (+8 ms DNA). Zero-drift readback intact.

## 8. Render + master (FluidSynth → master() → Opus OGG)

Soundfont `FluidR3_GM.sf2` (via `discover_soundfont()`). Master to
`target_for_style("groove")` = **−14 LUFS**, ceiling **−1 dBTP**.

| Version | LUFS | true peak | silence ratio |
|---|---|---|---|
| phase1 | −15.22 | −1.0 | 43.5 % (single sparse voice — expected) |
| perfect | −14.00 | −1.0 | 3.4 % |
| humanized | −14.00 | −1.0 | 3.6 % |

Perfect + humanized hit the −14 LUFS target at the −1 dBTP ceiling; silence
< 30 % (healthy). Phase-1 silence is the raw single-voice draft (no rhythm
section) — expected.

## 9. Fix applied during this job

**Range-clamp pitch-class mutation bug**: the lead's post-quantization clamp
`min(84, chord_tone)` could change a chord tone (e.g. Bb5=94 → C5=84) and
silently break chord compliance (109 chord violations in the first perfect
export). Fixed by making `nearest_in_pcs` range-restricted (search only within
[48,84]) so no post-clamp is ever needed — perfect layer is now 0 chord
violations.

## 10. Files

```
/opt/data/projects/Styles/Groove/274-groove-sieve-rework/
├── README.md, REPORT.md, index.html, composition_meta.json
├── compose.py, verify.py, render.py
├── MIDI/   274-groove-sieve-rework-{phase1,perfect,humanized}.mid (+ provenance.json)
├── Audio/  274-groove-sieve-rework-{phase1,perfect,humanized}.ogg + .wav
└── Analysis/ grid_visualization{,_phase1}.txt, verify.json, render_report.json
```
