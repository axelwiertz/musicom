# 285-flamenco-boids-falseta — Composition Report

**Nightly composition job (ID 1fc3fd65d359) · 2026-11-04**

## 1. Selection (LAYERED METHODOLOGY)

| Attribute | Value |
|---|---|
| Style | **Flamenco** |
| Method | **031 — Boids Swarm Flocking (Reynolds separation/alignment/cohesion)** |
| Layer | **concrete** (Nature-Led) — emits raw `MusicEvent`s straight into the two-phase pipeline; no abstract design stage |
| Paradigm | Nature-Led · Continuous/Fluid · Meso/Agent-state |
| Form | **intro-falseta-letra-falseta-cierre** (5 sections, 4+8+8+8+4 = **32 bars**) |

Method 031 drawn from the **concrete** pool (97 candidates), excluding the abstract
layer `{95,99,104,113,127,131,133}`, impractical AI-driven methods, and methods used
in the last 7 days `{18,21,69,11,98,38,36,25}`. Cadence this night = concrete (~6/7).

## 2. Musical DNA

| Attribute | Value |
|---|---|
| Key / mode | **E natural Phrygian ("por arriba")** — E F G A B C D (PC set ≡ C major) |
| Tempo | 100 BPM, 4/4, TPB 480, BAR 1920 |
| Harmonic plan | **Andalusian cadence** Am → G → F → Em (descending bass A-G-F-E), fully diatonic to E Phrygian |
| Form | Intro (4) → Falseta1 (8) → Letra (8) → Falseta2 (8) → Cierre (4) |
| Per-section cadence rotation | Intro `[Am G F Em]` · Falseta1 `[G F Em Am]` · Letra `[F Em Am G]` · Falseta2 `[Em Am G F]` · Cierre `[Am G F Em]` |
| Section midpoint roots | G · F · Em · Am · G (varied — no bar-0 tonic monotony) |

**Voices** (registry is source of truth):

| Voice | Instrument | GM prog | Channel | Role |
|---|---|---|---|---|
| Falseta | acoustic_guitar (nylon) | 24 | 0 | Boids-derived lead melody |
| Rasgueado | steel_acoustic | 25 | 1 | Rolling 8th-note chord strum |
| Bass | acoustic_bass | 32 | 2 | Andalusian root/fifth walk |
| Violin | violin | 40 | 3 | Sustained counterline + cierre tonic pedal |
| Drums | drum_kit | 0 | 9 | Palmas (claps 39) + cajón (kick 36 / snare 38) |

## 3. Two-phase architecture

**Phase 1 — raw Boids draft** (`-phase1.mid`, single voice):
A faithful Reynolds flocking simulation in (time-phase, pitch) space — separation
(push apart close neighbours), alignment (match neighbour velocity), cohesion (move
to local centroid) — plus a tonic-centre bias and damping. The flock **centroid**
pitch is sampled at checkpoints → the emergent single-voice melody. Onsets + durations
are intentionally raw (jittered, off-grid); pitch is unquantized. 5 per-section flocks
(Intro sparse n=10, Falseta1 n=16, Letra n=12, Falseta2 n=20 dense/high, Cierre n=8).

**Phase 2 — musicom rules post-process** (tiered pitch discipline):
1. Grid-lock onsets to 16th (120 ticks).
2. `classify_weight` (strong-grid beats 1&3 = ticks 0/960) → `tiered_quantize`:
   **strong → scale THEN chord** (hard in-scale AND in-chord); **weak → scale only**.
3. Voice-leading leap cap ≤ 9 semitones.
4. Dedup collisions.
5. Full 5-voice Flamenco texture (rasgueado strum, bass, violin counter, palmas/cajón).
6. Zero-drift normalize (terminal landmark per section).

## 4. Audits (perfect layer — pre-humanization)

### Rhythm-grid (per voice)

| Voice | onsets | off-16th | off-8th |
|---|---|---|---|
| Falseta | 140 | **0** | 71 (16th notes) |
| Rasgueado | 256 | **0** | 0 |
| Bass | 128 | **0** | 0 |
| Violin | 52 | **0** | 0 |
| Drums | 257 | **0** | 0 |

**Verdict: 0 off-grid (16th) across all voices.** ✓

### Harmony (tiered, `workflows.pitch_audit.audit_voice`)

| Voice | total | strong_ok | weak_in_scale | untagged_out_of_scale | tagged_non_resolving | strong_violations |
|---|---|---|---|---|---|---|
| Falseta | 140 | 30 | 110 | **0** | **0** | **0** |
| Rasgueado | 256 | 64 | 192 | **0** | **0** | **0** |
| Bass | 128 | 64 | 64 | **0** | **0** | **0** |
| Violin | 52 | 52 | 0 | **0** | **0** | **0** |

**Verdict: 0 un-tagged / 0 non-resolving / 0 strong violations — all voices pass.**
No chromatic ornaments were needed: the Andalusian cadence is fully diatonic to the
modal key, so the lead stayed chromatic-free by construction (ornament path unused but
available via `rules.ornament`).

## 5. Humanization + dual-version export

Canonical `workflows.humanize.export_dual` (validates + exports perfect FIRST, then
humanizes in place, re-validates, exports humanized — zero-drift gate on BOTH).
Style profile **flamenco**: timing 8 ms, velocity 6, layback 2 ms, phrase_corr 0.45.
Per-voice instrument DNA from the registry; melodic voices keep `None` timing/layback
so the style value wins; bass lays back 8 ms; drums anchor 2 ms / 0 layback.

Seed: `hz_seed = 20261104` (per-voice child seed = `seed*101+row`).

| Voice | timing_sigma_ms | vel_sigma | layback_ms | mean_abs_shift_ticks | max_abs_shift_ticks | mean_abs_vel_delta |
|---|---|---|---|---|---|---|
| Falseta | 8.0 | 6.0 | 2.0 | 4.607 | 13 | 5.10 |
| Rasgueado | 8.0 | 6.0 | 2.0 | 4.445 | 17 | 4.84 |
| Bass | 5.0 | 4.0 | 8.0 | 6.461 | 15 | 3.46 |
| Violin | 8.0 | 6.0 | 2.0 | 3.461 | 12 | 5.75 |
| Drums | 2.0 | 4.0 | 0.0 | 0.957 | 4 | 3.07 |

Drums are tightest (0.957 ticks mean shift), bass lays back — the expected role
hierarchy is preserved.

**Dual-version off-grid proof** (post-humanization): total off-16th = **702**
(Falseta 134, Rasgueado 237, Bass 127, Violin 43, Drums 161) — the humanizer ran.
The perfect layer stays 0 off-grid (compositional truth).

## 6. Zero-drift

| File | tracks | track length (ticks) | zero-drift |
|---|---|---|---|
| phase1 | 1 | 61440 (32 bars × 1920) | ✓ |
| perfect | 5 | 61440 × 5 | ✓ |
| humanized | 5 | 61440 × 5 | ✓ |

All rows equal length; `validate()` returned OK for both phases.

## 7. Rendering & mastering

FluidSynth (`FluidR3_GM.sf2`) → WAV → `master()` to genre target → Opus OGG.
Genre loudness target for flamenco = **−14 LUFS** (`target_for_style`), −1 dBTP ceiling.

| Version | duration | silence | RMS mean (per-sec) | LUFS (measured) | dBTP | WAV | OGG |
|---|---|---|---|---|---|---|---|
| phase1 | 80.11 s | 10.7% | 0.033 | **−14.38** | **−1.0** | 14.1 MB | 722 KB |
| perfect | 87.03 s | 10.6% | 0.103 | **−14.11** | **−1.0** | 15.4 MB | 623 KB |
| humanized | 87.03 s | 10.5% | 0.104 | **−14.04** | **−1.0** | 15.4 MB | 627 KB |

All three sit at the −14 LUFS flamenco target (within ±0.4 LUFS) with true peak at the
−1 dBTP ceiling. ~10% silence is the post-music reverb tail (not mid-track gaps).

## 8. Files

- `MIDI/285-flamenco-boids-falseta-phase1.mid` (+ `.provenance.json`)
- `MIDI/285-flamenco-boids-falseta-perfect.mid` (+ `.provenance.json`)
- `MIDI/285-flamenco-boids-falseta-humanized.mid` (+ `.provenance.json`)
- `Audio/285-flamenco-boids-falseta-{phase1,perfect,humanized}.{wav,ogg}`
- `Analysis/grid_visualization.txt`, `Analysis/summary.json`, `Analysis/render_stats.json`
- `provenance.json` (root), `README.md`, `index.html` (dashboard), `REPORT.md`

## 9. Fixes applied during this run

- `ScaleQuantizer` rejects `"phrygian"` (its `_SCALES` list is
  major/minor/pentatonic/chromatic/dorian/mixolydian). E natural Phrygian shares its
  pitch-class set with C major, so the quantizer was pointed at `root=60, scale="major"`
  — same PC set, tonic stays E. No musical compromise.

## 10. What to listen for

- The **Falseta** line is the flock's emergent centroid — cohesion keeps it flowing,
  alignment gives momentum, separation produces the occasional leap; every strong beat
  lands on a chord tone, every weak beat on a scale tone.
- The **Andalusian cadence** (Am→G→F→Em, bass A-G-F-E) is the harmonic DNA — the
  descending bass is the signature Flamenco pull.
- The **palmas** (claps) + **cajón** (kick/snare) lock the compás; the rasgueado
  strum rolls on 8ths.
- A/B the `-perfect` vs `-humanized`: perfect is machine-locked, humanized carries
  8 ms flamenco timing slop + bass layback — same notes, different groove.
