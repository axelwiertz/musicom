# REPORT — 271-funk-snn-spiking

**Project:** 271-funk-snn-spiking · **Date:** 2026-10-28 · **Job:** nightly composition cron

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Style | **Funk** (random from `/opt/data/projects/Styles/` genre folders) |
| Method | **109 — Spiking Neural Network Composition (SNN-C)** |
| Layer | **concrete** (emits raw events → feeds `generators/` + rules) |
| Paradigm | Nature-Led |
| Form | **rondo A–B–A–C–A** (picked via `pick_form(style)`, `form_to_sections`) |
| Key / Mode | **F major** (ionian) |
| Tempo / Meter | 105 BPM · 4/4 · 480 TPB (bar 1920, 8th 240, 16th 120) |
| Seed | raw 2034316830 · humanize 38252 |

Method was **not** in the last-7-days exclusion set (001, 002, 023, 028, 043,
051, 053, 065, 075, 082, 091, 095, 098, 104, 111, 113, 121). ~6/7 concrete
night — this night landed on the concrete branch.

## 2. Method — SNN-C (spiking neural network)

Phase-1 generative core is a faithful implementation of Method 109:

- **12 tonotopic pitch-class columns** (pc 0–11), 8 Izhikevich **regular-spiking**
  neurons each (a=0.02, b=0.2, c=−65, d=8), Euler dt=0.5 ms, ~91 k steps.
- **Thalamic theta–gamma clock**: theta = bar-period oscillator, gamma =
  16th-note oscillator, gamma gated by theta (metric binding / strong beats).
- **Prefrontal mode bias**: F-major scale tones get base drive 6.0, chromatic
  columns 3.2 (mode knowledge).
- **Insula tension envelope** per section: HOME 0.25 → LIFT 0.55 → HOME 0.25 →
  TENSE 0.85 → TURN 0.40; tension boosts chromatic columns (chromatic drive
  peaks in the C section).
- **Decode**: 16th-note windows (jittered ±12 % → off-grid onsets), population
  rate per column, softmax-argmax winner → float pitch, winner-rate velocity,
  ISI duration. → **302 raw events** (float pitch, off-grid, rate velocity).

## 3. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw SNN decode, single voice (Lead), no
  harmony, unquantized. Own `UnitMatrixComposer` + own `validate()` gate
  (passed). 1 track × 38400 ticks.
- **Phase 2** (`-perfect.mid`): weight-aware **tiered pitch discipline** —
  `classify_weight` (strong = beats 1 & 3) → `tiered_quantize` (strong =
  scale **and** chord, weak = scale) → 16th grid snap → dedup → funk
  phrasing-thinning (rests) → voice-leading → **4 tagged chromatic approach
  ornaments** → 5-voice arrangement.
- **Phase 2** (`-humanized.mid`): `export_dual` — validate + export perfect,
  humanize in place, re-validate, export (zero-drift gate on both).

## 4. Form & progression (rondo, 20 bars)

| Section | Bars | Progression | Midpoint root | Insula | Lead octave |
|---|---|---|---|---|---|
| A1 (refrain) | 0–3 | F · Bb · Dm · C | Bb | HOME 0.25 | 60 |
| B | 4–7 | Dm · C · Bb · C | C | LIFT 0.55 | 72 |
| A2 (refrain) | 8–11 | F · Bb · Dm · C | Bb | HOME 0.25 | 60 |
| C | 12–15 | Dm · Gm · C · F | C | TENSE 0.85 | 60 |
| A3 (refrain) | 16–19 | F · Bb · Dm · C | Bb | TURN 0.40 | 60 |

A-refrain identity returns three times (rondo); B lifts the register an
octave; C pushes chromatic drive through a ii–V–I turnaround.

## 5. Voices (instrument registry — source of truth)

| Voice | Instrument | Program | Notes |
|---|---|---|---|
| Lead | Clavinet | 7 | SNN melody + 4 tagged ornaments |
| Guitar | Clean Electric | 27 | 16th "chicken-scratch" comp |
| Brass | Brass Section | 61 | syncopated stabs ('and' of 2 / 4) |
| Bass | Electric Bass | 33 | 16th syncopated funk line |
| Drums | Drum Kit | ch9 | syncopated kick + backbeat + 16th hats |

## 6. Tiered harmony audit (workflows.pitch_audit.audit_voice)

Every pitched note must be in-scale AND (strong) in-chord, OR a tagged
ornament resolving by step. All voices: **0 untagged out-of-scale · 0
non-resolving · 0 strong violations → PASS.**

| Voice | audible | strong_ok | weak_in_scale | tagged | resolving | non-resolving | untagged_out | strong_viol | PASS |
|---|---|---|---|---|---|---|---|---|---|
| Lead | 255 | 39 | 212 | **4** | **4** | 0 | 0 | 0 | ✓ |
| Guitar | 360 | 0 | 360 | 0 | 0 | 0 | 0 | 0 | ✓ |
| Brass | 120 | 0 | 120 | 0 | 0 | 0 | 0 | 0 | ✓ |
| Bass | 180 | 40 | 140 | 0 | 0 | 0 | 0 | 0 | ✓ |

## 7. Grid audit (read-only mido readback)

| Check | phase1 (raw) | perfect | humanized |
|---|---|---|---|
| File size > 40 B | 544 B ✓ | 10319 B ✓ | 10142 B ✓ |
| Zero-drift | 1 × 38400 ✓ | 5 × 38400 ✓ | 5 × 38400 ✓ |
| Pitched onsets | 59 | 915 | 915 |
| Off-grid pitched onsets | 56/59 (raw) | **0/915 ✓** | 849/915 (>0, jitter ran) |
| Strong chord violations | 0 | **0 ✓** | **0 ✓** |
| Weak out-of-scale (tagged ornaments) | 2 (raw chroma) | 4 (tagged) | 4 (tagged) |

Perfect = 0 off-grid (grid-locked); humanized > 0 off-grid proves the
humanizer ran.

## 8. Humanization (style funk + per-instrument DNA, seed 38252)

Style funk profile: timing σ 4.0 ms, velocity σ 6.0, phrase_corr 0.25,
layback 2.0 ms.

| Voice | mean abs shift (ticks) | max shift | mean vel Δ | timing σ (ticks) |
|---|---|---|---|---|
| Lead | 2.592 | 8 | 4.06 | 3.36 |
| Guitar | 3.186 | 10 | 4.86 | 3.36 |
| Brass | 3.367 | 8 | 6.58 | 3.36 |
| Bass | 6.950 | 17 | 3.11 | 4.20 |
| Drums | 1.113 | 4 | 3.17 | 1.68 |

Drums tightest (anchors grid), bass lays back (+8 ms DNA), lead loose — as
expected. Zero-drift readback intact on the humanized export.

## 9. Render + master (FluidSynth → master() → Opus OGG)

Soundfont: FluidR3_GM.sf2 (via `discover_soundfont()`). Master to
`target_for_style("funk")` = **−13 LUFS**, ceiling **−1 dBTP**.

| Version | target LUFS | measured LUFS | true peak dBTP | silence ratio | rms mean/max |
|---|---|---|---|---|---|
| phase1 (raw) | −13 | −13.00 | −4.6 | 79.4 % (single sparse voice) | 0.034 / 0.178 |
| perfect | −13 | −13.00 | −1.0 | 4.87 % | 0.159 / 0.184 |
| humanized | −13 | −13.01 | −1.0 | 4.97 % | 0.159 / 0.186 |

Perfect + humanized hit the funk loudness target with true peak at the −1 dBTP
ceiling. Phase-1 silence is expected (raw single-voice draft, no rhythm
section); its RMS max 0.178 confirms audible content.

## 10. Files

```
/opt/data/projects/Styles/Funk/271-funk-snn-spiking/
├── README.md, REPORT.md, index.html
├── compose.py, render.py, verify.py
├── MIDI/   271-funk-snn-spiking-{phase1,perfect,humanized}.mid  (+ provenance.json sidecars)
├── Audio/  271-funk-snn-spiking-{phase1,perfect,humanized}.wav + .ogg
└── Analysis/ grid_visualization{, _phase1}.txt, pitch_audit.json,
             verify_report.json, render_report.json, compose_summary.json
```

## 11. Fixes applied during this job

1. **KEY_PCS missing Bb** — F-major pitch-class set omitted pc 10 (Bb); the
   scale quantizer was correct but the audit scale-set wrongly flagged every
   Bb as out-of-scale. Fixed to {5,7,9,10,0,2,4}.
2. **Duplicate section names** — the composer keys sections by name
   (`fill_voice_section` → `next(...)`), so the three rondo "A" sections
   collided and the piece collapsed to 12 bars. Fixed with unique internal
   names A1/A2/A3 (musical form still rondo A–B–A–C–A).
3. **SNN decode onset criterion** — corrected to winner-column rate (not total
   spikes) per the method's θ_onset definition; added funk phrasing-thinning
   so the melody has rests (and room for the tagged ornaments).
4. **verify.py track-name key collision** — empty track names overwrote the
   per-voice dict; switched to a per-track list + aggregate.
5. **preflight compliance** — verify.py (read-only mido audit) now carries the
   `# READING ONLY (analysis)` marker + musicom structures import.
