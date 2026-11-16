# 308-physarum-classical-rondo — REPORT

**Nightly composition job (ID 1fc3fd65d359) · 2026-11-16 · Method 035 (concrete layer)**

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Style | **Classical** (random from 47 style dirs, seeded 20261116) |
| Method | **035 — Physarum Polycephalum Transport Network Optimization (PPTNO)** (Nature-Led) |
| Layer | **concrete** (weekly abstract cadence not due — last abstract was 134 on 11-12) |
| Form | **rondo** → `A·B·A·C·A`, bars `[4,4,4,4,4]` = **20 bars** (from `pick_form("classical")` → rondo) |
| Seed | 20261116 · humanize seed **73893** |

Methods excluded (used last 7 days): 001, 007, 012, 015, 019, 023, 032, 041, 053, 069, 075, 120, 132, 134.

## 2. Musical DNA

| Field | Value |
|---|---|
| Key | G major (Ionian) = pc {0,2,4,6,7,9,11} |
| Tempo | 100 BPM · 4/4 · 480 TPB · BAR=1920 · 8th=240 |
| Length | 20 bars = 38,400 ticks (~48 s) |

**Physarum (method 035)** — slime-mold transport network, self-contained model:

```
food sources   = the current bar's chord tones (pitch-coordinate nodes) + tonic attractor (G5)
chemotaxis     = step toward nearest source + uniform exploration noise (width 7)
streaming      = move 0.35 of the distance toward the target
diffusion      = + N(0, 1.3) per slot
tube thickness = flux: revisited pitches accumulate weight -> velocity (60..95)
peristalsis    = contraction oscillation period 16 slots; dips below 0.30 -> REST
```

The agent starts at tonic G5 and forages 160 eighth-note slots; the deposited
flux path is the raw melodic line. 110 raw notes emitted (50 rests from
peristaltic dips).

**Voices (5, from instrument registry):**

| Voice | Instrument | Program | Channel | Role |
|---|---|---|---|---|
| Violin | Violin | 40 | 0 | Physarum path lead melody |
| Flute | Flute | 73 | 1 | canon (path −12, +1 beat, thinned 1/2) |
| Viola | Viola | 41 | 2 | inner harmony (3rd + 5th, sustained) |
| Cello | Cello | 42 | 3 | bass (root beat 1, fifth beat 3) |
| Piano | Piano | 1 | 4 | Alberti-style broken-chord continuo |

## 3. Progression (G major, rondo)

| Section | Bars | Degrees (chords) | Role |
|---|---|---|---|
| A | 0-3 | G D G C | tonic area (I V I IV) |
| B | 4-7 | D Em Am D | dominant excursion (V vi ii V) |
| A2 | 8-11 | G D G C | recap |
| C | 12-15 | Em Am D G | relative-minor contrast (vi ii V I) |
| A3 | 16-19 | G D G G | authentic cadence (I V I I) |

Voice-leading on the pad triads (viola/piano/cello share the voice-led triad):
**0 corrections** needed. Section midpoint chords used (no bar-0 tonic collapse).

## 4. Two-phase architecture

- **Phase 1** (`-phase1.mid`, 990 B): raw Physarum walk, single violin voice,
  unquantized float pitch (diffusion jitter) + off-grid onsets (±25 ticks),
  110 notes, own composer + validate() gate.
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): tiered quantization
  (`ScaleQuantizer.tiered_quantize` — strong beats → chord tones, weak beats →
  scale tones), 8th-grid snap + dedup, voice-leading on the pad triads, register
  enforcement (octave-preserving `to_register`, not clamp), 5-voice texture.

## 5. Dual-version + humanization (always-on, seeded)

`export_dual` → `-perfect.mid` (grid-locked) + `-humanized.mid` (style
classical + per-instrument DNA). `hz_seed = 73893`. Style profile = classical →
`STYLE_HUMANIZE_DEFAULT` (timing 7 ms = 5.6 ticks @ 100 BPM, vel σ 6, phrase
corr 0.40, layback 1 ms). Per-voice mean/max abs shift (ticks) + velocity delta:

| Voice | mean shift | max shift | vel Δ | notes |
|---|---|---|---|---|
| Violin | 4.90 | 14 | 5.26 | 110 |
| Flute | 4.24 | 13 | 6.42 | 55 |
| Viola | 4.05 | 8 | 4.45 | 40 |
| Cello | 3.85 | 10 | 4.45 | 40 |
| Piano | 3.98 | 12 | 3.74 | 80 |

All voices ~4-5 ticks of timing slop (organic, no drum anchor needed — the
string continuo carries the grid). Zero-drift safe (forward-clamp +
boundary-clamp, terminal landmark pinned).

## 6. Verification (real numbers, read-only mido + `audit_voice`)

| Metric | phase1 | perfect | humanized |
|---|---|---|---|
| voice tracks | 1 | 5 | 5 |
| track length (ticks) | 38400 | 38400 | 38400 |
| zero-drift | ✓ | ✓ | ✓ |
| pitched onsets | 110 | 325 | 325 |
| off-grid (16th=120) | 95 (raw) | **0** | **292** (jitter) |
| off-grid (8th=240) | 95 | **0** | 292 |
| untagged out-of-scale | 33 (raw) | **0** | **0** |
| tagged non-resolving | 0 | 0 | 0 |
| strong-beat violations | 7 (raw) | **0** | **0** |

All 5 pitched voices pass the tiered pitch discipline: **0 untagged / 0
non-resolving / 0 strong violations**. Lead/counter kept chromatic-free (no
tagged ornaments needed for this diatonic rondo). Phase-1 raw violations are
expected (unquantized draft, pre-rules). Humanized off-grid 292/325 proves the
humanizer ran; pitch stays 100% in-scale/in-chord.

## 7. Audio (mastered to −18 LUFS, −1 dBTP ceiling)

`target_for_style("classical")` = **−18.0**. SoundFont = FluidR3_GM.sf2.

| Version | LUFS | true-peak | silence | RMS mean | OGG |
|---|---|---|---|---|---|
| phase1 | −18.07 | −1.63 | 33.1% | 0.053 | 353 KB |
| perfect | −18.00 | −5.63 | 6.0% | 0.069 | 339 KB |
| humanized | −18.00 | −5.90 | 6.0% | 0.069 | 344 KB |

Perfect/humanized silence 6.0% (healthy, no mid-track gaps). Phase-1 silence
33% is the expected sparse monophonic raw draft (peristaltic rests between
notes) — not a gap bug. True-peaks −5.6/−5.9 dB sit below the −1 ceiling
(ceiling, not target — a dynamic classical texture legitimately peaks below it).

## 8. Fixes applied during build (audit-driven)

1. **Register-clamp broke chord membership (the 306-class bug)**: viola/cello/
   piano chord tones were clamped to a register boundary (`max(lo, min(hi, p))`),
   turning e.g. a B4 chord tone into A4 (69, pc 9) or G3 (55, pc 7) — out-of-chord
   on strong beats (22 viola + 14 cello violations caught by `audit_voice`).
   Replaced every clamp with `to_register(p, lo, hi)` (octave-shift preserving
   pitch class). Re-verified: 0 strong violations across all voices.
2. **Flute canon bar-seam chord mismatch**: the +1-beat canon could offset a
   note into the next bar; the chord snap originally used the *pre-offset* bar.
   Now the snap uses `st_glob // BAR` (the shifted bar) so a canon note landing
   on beat 1 of the next bar is quantized to that bar's chord.
3. B-section progression tightened from `D Em Bm D` to `D Em Am D` (cleaner
   ii–V prep before the recap).

## 9. Artifacts

| File | Role |
|---|---|
| `MIDI/308-physarum-classical-rondo-phase1.mid` (990 B) | raw Physarum draft |
| `MIDI/308-physarum-classical-rondo-perfect.mid` (3000 B) | grid-locked phase 2 |
| `MIDI/308-physarum-classical-rondo-humanized.mid` (3004 B) | humanized phase 2 |
| `Audio/*-perfect.ogg` / `*-humanized.ogg` / `*-phase1.ogg` | mastered Opus renders |
| `Analysis/grid_visualization.txt` (+phase1) | rhythm DNA grids |
| `Analysis/compose_summary.json` / `verification.json` / `render_report.json` | metrics |
| provenance sidecars (`.mid.provenance.json`) | per MIDI artifact |
| `index.html` | dashboard (VoltAgent styling) |
| `compose.py` / `render.py` / `verify.py` / `build_dashboard.py` | generators |
