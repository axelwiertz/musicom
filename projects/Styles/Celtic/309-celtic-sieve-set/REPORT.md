# 309-celtic-sieve-set — REPORT

**Nightly composition job (ID 1fc3fd65d359) · 2026-11-17 · Method 025 (concrete layer)**

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Style | **Celtic** (random from 48 style dirs, seeded 20261117) |
| Method | **025 — Xenakis Sieve Theory** (Rules-Based) |
| Layer | **concrete** (weekly abstract cadence not due — last abstract was 134 on 11-12) |
| Form | **through-composed** → `S1·S2·S3·S4·S5·S6`, bars `[4,4,4,4,4,4]` = **24 bars** (from `pick_form("celtic")`) |
| Seed | 20261117 · humanize seed **69180** |

Form note: `pick_form("celtic")` first drew the ~1/7 **loop** option; re-rolled
non-loop (loop_prob=0, seed 202611172) → **through-composed**, so the piece is a
6-phrase variation chain rather than a single loop.

Methods excluded (used last 7 days): 001, 007, 012, 015, 019, 023, 032, 035, 041, 053, 069, 075, 120, 132, 134.

Method pool: concrete non-AI candidates, excluding the abstract layer
{95,99,104,113,127,131,133,134,139,143}, the AI-Driven set, and the
last-7-days set → 99 candidates; **025** drawn.

## 2. Musical DNA

| Field | Value |
|---|---|
| Key | D Mixolydian = pc {0,2,4,6,7,9,11} |
| Tempo | 120 BPM · 4/4 · 480 TPB · BAR=1920 · 8th=240 · 16th=120 |
| Length | 24 bars = 46,080 ticks (~48 s) |

**Xenakis Sieve (method 025)** — a sieve is a modular congruence `x ≡ r (mod m)`.
The pitch sieve = a union of residues over the chromatic pitch space (builds the
pitch pool); the rhythm sieve = a union of residues over the 16th-step grid
(builds the onset pattern). Each section uses a distinct sieve pair — a
"sieve set" (tune-set of sieve variations).

| Section | pitch sieve | pitch-class pool | rhythm sieve (16ths) | dir |
|---|---|---|---|---|
| S1 | 4 @ {0,2} | {0,2,4,6,8,10} whole-tone | 4 @ {0,3} | ↑ |
| S2 | 3 @ {0,1} | {0,1,3,4,6,7,9,10} | 3 @ {0,2} | ↓ |
| S3 | 5 @ {0,2} | {0,2,5,7,10} pentatonic | 5 @ {0,2} | ↑ |
| S4 | 4 @ {1,3} | {1,3,5,7,9,11} | 4 @ {1,2} | ↑ |
| S5 | 3 @ {0,2} | {0,2,3,5,6,8,9,11} | 3 @ {0} | ↓ |
| S6 | 7 @ {0,4} | {0,4,7,11} quartal | 4 @ {0,3} | ↑ |

**Voices (5, from instrument registry):**

| Voice | Instrument | Program | Channel | Role |
|---|---|---|---|---|
| Violin | Violin | 40 | 0 | fiddle lead = sieve walk |
| Flute | Flute | 73 | 1 | canon (path −12, +1 beat, thinned 1/2) |
| Bagpipe | Bagpipe | 109 | 2 | regulator-style sustained chord root+fifth |
| Harp | Harp | 46 | 3 | broken-chord ripple (r f th oct th f r f on 8ths) |
| DoubleBass | Double Bass | 43 | 4 | bass (root beat 1, fifth beat 3) |

## 3. Progression (D Mixolydian, through-composed)

| Section | Bars | Degrees (chords) | Role |
|---|---|---|---|
| S1 | 0-3 | D D G D | tonic area (I I IV I) |
| S2 | 4-7 | G D Am D | lift to IV, minor-v cadence |
| S3 | 8-11 | Em D G Am | ii motion |
| S4 | 12-15 | Bm G D Am | vi → IV |
| S5 | 16-19 | G Em Bm Am | sequential chain |
| S6 | 20-23 | D G Am D | closing cadence |

Voice-leading on the pad triads (bagpipe/harp/bass share the voice-led triad):
**0 corrections** needed. Section midpoint chords used (no bar-0 tonic collapse).

## 4. Two-phase architecture

- **Phase 1** (`-phase1.mid`, 1560 B): raw sieve walk, single violin voice,
  unquantized float pitch (sieve pc + jitter) + off-grid onsets (±25 ticks),
  187 notes, own composer + validate() gate.
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): tiered quantization
  (`ScaleQuantizer.tiered_quantize` — strong beats → chord tones, weak beats →
  scale tones), 8th-grid snap, voice-leading on the pad triads, register
  enforcement (octave-preserving `to_register`, not clamp), 5-voice Celtic
  texture.

## 5. Dual-version + humanization (always-on, seeded)

`export_dual` → `-perfect.mid` (grid-locked) + `-humanized.mid` (style celtic +
per-instrument DNA). `hz_seed = 69180`. Style profile = celtic →
`STYLE_HUMANIZE_DEFAULT` (timing 7 ms = 6.72 ticks @ 120 BPM, vel σ 6, phrase
corr 0.40, layback 1 ms). Per-voice mean/max abs shift (ticks) + velocity delta:

| Voice | mean shift | max shift | vel Δ | notes |
|---|---|---|---|---|
| Violin | 4.22 | 14 | 5.17 | 170 |
| Flute | 4.24 | 16 | 5.48 | 87 |
| Bagpipe | 4.85 | 13 | 5.29 | 48 |
| Harp | 4.66 | 20 | 5.02 | 192 |
| DoubleBass | 9.06 | 24 | 4.98 | 48 |

DoubleBass lays back as designed (instrument DNA timing 10 ms / layback 8 ms →
9.6-tick σ, mean shift 9.06 vs ~4-5 for the others). Zero-drift safe
(forward-clamp + boundary-clamp, terminal landmark pinned).

## 6. Verification (real numbers, read-only mido + `audit_voice`)

| Metric | phase1 | perfect | humanized |
|---|---|---|---|
| voice tracks | 1 | 5 | 5 |
| track length (ticks) | 46080 | 46080 | 46080 |
| zero-drift | ✓ | ✓ | ✓ |
| pitched onsets | 187 | 545 | 545 |
| off-grid (16th=120) | 182 (raw) | **0** | **487** (jitter) |
| off-grid (8th=240) | 184 (raw) | **0** | 487 |
| untagged out-of-scale | 67 (raw) | **0** | **0** |
| tagged non-resolving | 0 | 0 | 0 |
| strong-beat violations | 0 | **0** | **0** |

All 5 pitched voices pass the tiered pitch discipline: **0 untagged / 0
non-resolving / 0 strong violations**. Lead/counter kept chromatic-free (no
tagged ornaments needed). Phase-1 raw violations (67 out-of-scale, 182 off-grid)
are expected — the sieve emits whole-tone/octatonic/chromatic pools that Phase 2
disciplines to D Mixolydian + chord tones. Humanized off-grid 487/545 proves the
humanizer ran; pitch stays 100% in-scale/in-chord.

## 7. Audio (mastered)

`target_for_style("celtic")` = **−14.0** (no genre-map entry → fallback;
folk-adjacent would be −16). SoundFont = FluidR3_GM.sf2 (`discover_soundfont`).

| Version | LUFS | true-peak | silence | RMS mean | OGG | WAV (git-ignored) |
|---|---|---|---|---|---|---|
| phase1 | −14.04 | −1.00 dBTP | 6.0% | 0.108 | 394 KB | 8.9 MB |
| perfect | −14.00 | −2.23 dBTP | 15.4% | 0.108 | 424 KB | 10.5 MB |
| humanized | −14.00 | −1.02 dBTP | 15.8% | 0.108 | 428 KB | 10.5 MB |

Silence = release/reverb tail, not mid-track gaps: per-second RMS is healthy
0.12–0.14 through seconds 0–48 (the music), then the bagpipe/bass release decays
through seconds 49–58 (tail). Perfect true-peak −2.23 dBTP sits below the −1
ceiling — correct (true-peak limit is a ceiling, not a target; the dynamic
fiddle line peaks lower). MIDI sizes: phase1 1560 B, perfect 4924 B, humanized
4903 B.

## 8. Files

| Artifact | Path |
|---|---|
| Phase-1 MIDI | `MIDI/309-celtic-sieve-set-phase1.mid` |
| Perfect MIDI | `MIDI/309-celtic-sieve-set-perfect.mid` |
| Humanized MIDI | `MIDI/309-celtic-sieve-set-humanized.mid` |
| Mastered OGGs | `Audio/309-celtic-sieve-set-{phase1,perfect,humanized}.ogg` |
| Grid viz | `Analysis/grid_visualization.txt` (+ `_phase1.txt`) |
| Compose summary | `Analysis/compose_summary.json` |
| Verification | `Analysis/verification.json` |
| Render report | `Analysis/render_report.json` |
| Provenance | `MIDI/*.provenance.json` (3 sidecars) |
| Dashboard | `index.html` |
| This report | `REPORT.md` |

## 9. Fixes applied this run

1. **Snapped-bar chord context** — the violin lead originally computed its
   chord degree from the RAW onset tick, but onsets are then snapped to the 8th
   grid; a note near a bar seam could snap into the next bar and carry the wrong
   chord's tones → strong-beat violations. Fixed: derive the bar/degree from the
   SNAPPED tick (`bar = st_glob // BAR`).
2. **Phase-1 negative-seam clamp** — negative jitter at a section seam produced a
   negative section-relative `start_tick`, which wraps in the MusicUnit uint16
   storage to ~65515 and emitted two stray notes at ticks 80875/103917 (track
   overshot to 103917). Fixed: clamp `st = max(0, tick_abs - s0)`. Track now
   ends exactly at 46080.
