# REPORT — 273-cinematic-perlin-build

**Project:** 273-cinematic-perlin-build · **Date:** 2026-10-29 · **Job:** nightly composition cron

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Style | **Cinematic** (random from `/opt/data/projects/Styles/` genre folders) |
| Method | **040 — Perlin Noise Composition (PNC)** |
| Layer | **concrete** (emits raw float-pitch/off-grid events → feeds `generators/` + rules) |
| Paradigm | Nature-Led |
| Form | **cinematic-build** (Intro 4 / Build 8 / Rise 8 / Peak 8 / Resolve 4 = 32 bars) |
| Key / Mode | **D minor** (aeolian: D E F G A B♭ C) |
| Tempo / Meter | 76 BPM · 4/4 · 480 TPB (bar 1920, 8th 240, 16th 120) |
| Seed | raw 928473 · humanize 34304 |

Method was **not** in the last-7-days exclusion set (recent nights used 001, 002,
082, 091, 095, 109, 121). ~6/7 concrete night — this night landed on the
concrete branch.

## 2. Method — Perlin Noise Composition (fBm gradient noise)

Phase-1 generative core is a faithful implementation of Method 040:

- **1D Perlin gradient noise** (Ken Perlin, 1985): permutation table +
  gradient + smoothstep fade (`t³·(6t²−15t+10)`), 512-entry doubled
  permutation (seeded by `raw_seed+1` / `raw_seed+2`).
- **4-octave fractal Brownian motion** (fBm): lacunarity 2.0, gain 0.5,
  amplitude-normalized → bounded smooth field ≈ [−1, 1].
- **Pitch field** (`fbm @ 0.40 Hz`): slow, ~2.5 s feature scale → a flowing
  melodic contour. Mapped `pitch = octave_base + field·6` semitones.
- **Activity field** (`fbm @ 1.60 Hz + phase offset`): higher-frequency noise
  → onset density + velocity. Onset fires when `activity > threshold`, with
  `threshold = 0.15 − 0.40·tension` — the per-section tension ramp densifies
  the texture toward the Peak.
- **Decode**: 16th-note stepping with ±12% onset jitter (off-grid) → **328 raw
  events** (float pitch, off-grid, activity-scaled velocity).

## 3. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw Perlin decode, single voice (Lead), no
  harmony, unquantized. Own `UnitMatrixComposer` + own `validate()` gate
  (passed). 1 track × 61440 ticks.
- **Phase 2** (`-perfect.mid`): weight-aware **tiered pitch discipline** —
  `classify_weight` (strong = beats 1 & 3) → `tiered_quantize` (strong =
  scale **and** chord, weak = scale) → 16th grid snap → dedup → voice-leading
  → **2 tagged chromatic approach ornaments** → 5-voice arrangement with a
  per-section lead register ramp (55 → 60 → 64 → 67 → 60).
- **Phase 2** (`-humanized.mid`): `export_dual` — validate + export perfect,
  humanize in place, re-validate, export (zero-drift gate on both).

## 4. Form & progression (cinematic-build, 32 bars)

| Section | Bars | Progression | Tension | Lead octave |
|---|---|---|---|---|
| Intro | 0–3 | Dm · Dm · B♭ · C | 0.15 | 55 |
| Build | 4–11 | Dm · B♭ · F · C · Dm · B♭ · F · C | 0.40 | 60 |
| Rise | 12–19 | B♭ · C · Dm · Am · Gm · C · Dm · Am | 0.65 | 64 |
| Peak | 20–27 | Dm · B♭ · F · C · Dm · B♭ · F · C | 0.90 | 67 |
| Resolve | 28–31 | Dm · B♭ · C · Dm | 0.35 | 60 |

The register ramp + density ramp realize the cinematic build; the Resolve
section closes on a plagal-ish B♭ → C → Dm cadence to the tonic.

## 5. Voices (instrument registry — source of truth)

| Voice | Instrument | Program | Notes |
|---|---|---|---|
| Lead | Violin | 40 | Perlin contour melody + 2 tagged ornaments |
| Counter | Flute | 73 | octave-up half-density echo (chord tones) |
| Pad | String Ensemble | 48 | sustained root-position triads per bar |
| Bass | Cello | 42 | low root pedal + fifth on beat 3 |
| Drums | Drum Kit | ch9 | soft kick, cymbal section accents, Peak toms |

## 6. Tiered harmony audit (workflows.pitch_audit.audit_voice)

Every pitched note must be in-scale AND (strong) in-chord, OR a tagged
ornament resolving by step. All voices: **0 untagged out-of-scale · 0
non-resolving · 0 strong violations → PASS.**

| Voice | audible | strong_ok | weak_in_scale | tagged | resolving | non-resolving | untagged_out | strong_viol | PASS |
|---|---|---|---|---|---|---|---|---|---|
| Lead | 330 | 39 | 289 | **2** | **2** | 0 | 0 | 0 | ✓ |
| Counter | 164 | 18 | 146 | 0 | 0 | 0 | 0 | 0 | ✓ |
| Pad | 96 | 96 | 0 | 0 | 0 | 0 | 0 | 0 | ✓ |
| Bass | 64 | 64 | 0 | 0 | 0 | 0 | 0 | 0 | ✓ |

## 7. Grid audit (read-only mido readback)

| Check | phase1 (raw) | perfect | humanized |
|---|---|---|---|
| File size > 40 B | 462 B ✓ | 5892 B ✓ | 5812 B ✓ |
| Zero-drift | 1 × 61440 ✓ | 5 × 61440 ✓ | 5 × 61440 ✓ |
| Pitched onsets | 50 | 654 | 654 |
| Off-grid pitched onsets | 48/50 (raw) | **0/654 ✓** | 576/654 (>0, jitter ran) |
| Strong chord violations | 0 | **0 ✓** | **0 ✓** |
| Weak out-of-scale (tagged ornaments) | 13 (raw chroma) | 2 (tagged) | 2 (tagged) |

Perfect = 0 off-grid (grid-locked); humanized > 0 off-grid proves the
humanizer ran.

## 8. Humanization (style cinematic + per-instrument DNA, seed 34304)

Style cinematic profile: timing σ 7.0 ms, velocity σ 6.0, phrase_corr 0.6,
layback 1.0 ms (loose, organic — the film-score feel). Per-voice override
tunes role DNA: bass lays back 8 ms, drums anchor 2 ms.

| Voice | mean abs shift (ticks) | max shift | mean vel Δ | timing σ (ticks) |
|---|---|---|---|---|
| Lead | 3.139 | 11 | 4.84 | 4.256 |
| Counter | 2.976 | 11 | 5.57 | 4.256 |
| Pad | 2.865 | 11 | 3.41 | 4.256 |
| Bass | 5.359 | 12 | 3.97 | 3.648 |
| Drums | 0.838 | 4 | 2.52 | 1.216 |

Drums tightest (anchors grid), bass lays back (+8 ms DNA), lead loose — as
expected. Zero-drift readback intact on the humanized export.

## 9. Render + master (FluidSynth → master() → Opus OGG)

Soundfont: FluidR3_GM.sf2 (via `discover_soundfont()`). Master to
`target_for_style("cinematic")` = **−14 LUFS** (fallback; cinematic is not in
the GENRE_LUFS map), ceiling **−1 dBTP**.

| Version | target LUFS | measured LUFS | true peak dBTP | silence ratio | rms mean/max |
|---|---|---|---|---|---|
| phase1 (raw) | −14 | −14.89 | −1.0 | 78.5 % (single sparse voice) | 0.027 / 0.169 |
| perfect | −14 | −14.00 | −1.3 | 3.95 % | 0.124 / 0.177 |
| humanized | −14 | −14.00 | −1.55 | 4.02 % | 0.125 / 0.192 |

Perfect + humanized hit the −14 LUFS target with true peak at/below the −1
dBTP ceiling. Phase-1 silence is expected (raw single-voice draft, no rhythm
section); its RMS max 0.169 confirms audible content.

## 10. Files

```
/opt/data/projects/Styles/Cinematic/273-cinematic-perlin-build/
├── README.md, REPORT.md, index.html
├── compose.py, render.py, verify.py
├── MIDI/   273-cinematic-perlin-build-{phase1,perfect,humanized}.mid  (+ provenance.json sidecars)
├── Audio/  273-cinematic-perlin-build-{phase1,perfect,humanized}.wav + .ogg
└── Analysis/ grid_visualization{, _phase1}.txt, pitch_audit.json,
             verify_report.json, render_report.json, compose_summary.json
```

## 11. Notes / none of the known pitfalls were hit

- No minor-key degree-root collapse (per-section short progressions, midpoint
  used, and `diatonic()` routes through `Scale7ChordDegree.get_diatonic_note`
  — no `% 7` wrapper).
- No negative-delta humanization (forward-clamp invariant in `export_dual`).
- Voice names unique (cinematic-build sections are already distinct: Intro /
  Build / Rise / Peak / Resolve), so no section-name collision.
- Phase-1 raw pitch is genuinely unquantized (13 off-scale chroma notes in the
  50-note raw draft), while phase-2 snaps every note in-scale/in-chord.