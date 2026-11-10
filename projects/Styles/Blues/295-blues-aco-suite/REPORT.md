# 295-blues-aco-suite — Report

## Source & Audit

- **Source**: `Blues/233-blues-aco-rework` (chosen at random, one existing composition).
- **Genre**: Blues (E blues scale `{2,4,7,9,10,11}`), 100 BPM, 4/4, Method 041 ACOPF.
- **Audit result**: **ALL 6 standards PASS**.
  - engine: `UnitMatrixComposer` (pass)
  - zero-drift: 5 voice tracks all len 61440 ticks (pass)
  - rhythm-grid: 0 off-grid pitched onsets (pass)
  - track setup: 5 voices (pass)
  - two-phase: `-phase1.mid` present (pass)
  - provenance.json + index.html present (pass)
- **Decision**: **EXTEND** (compliant source → keep identity as DNA seed).
  - Gap noted but not an audit fail: source shipped a single phase-2 MIDI with
    **no humanization / no dual-version export**. This rework adds the
    current-standard `-perfect` / `-humanized` dual-version layer.

## What Changed (longer + more varied)

| | source | rework |
|---|---|---|
| sections | 8 | **10** |
| bars | 32 | **40** |
| variation techniques | 6 | **8** |
| dual-version export | no | **yes** (`-perfect` + `-humanized`) |
| humanization | none | **blues profile, seeded** |

New section map:
`Intro → Verse1 → Verse2 → Verse3 → Chorus → Solo1 → Solo2 → ShoutChorus → Bridge → Outro`

## Variation Techniques (where applied)

1. **augmentation** — Intro (half-speed sparse lead, double duration).
2. **diminution** — Verse3 (16th-note pickup ghosts on alternating 8ths).
3. **register shift (+12)** — Solo1 (lead one octave up).
4. **transposition (+7)** — Solo2 (up a perfect fifth).
5. **transposition (+5)** — ShoutChorus (up a perfect fourth) + density rise.
6. **inversion** — Bridge (mirror around tonic E4).
7. **retrograde** — Outro (section contour reversed).
8. **density rise + thinning** — Chorus (full band) vs Outro (quarter-note feel).

## Two-Phase Architecture

- **Phase 1** (`-phase1.mid`): raw ACO best-tour — 320 chromatic pitches, unquantized
  micro-jitter timing, single voice. `validate()` gate passed. (off-grid = 289, raw by design.)
- **Phase 2** (`-perfect.mid`): musicom rules — chord-tone quantization per bar,
  rhythm-grid snap to 8th/16th, register enforcement, 5-voice band.
  - per-section harmonic regions: each section its own short I–IV–V blues cycle;
    section root taken from the section **midpoint degree** (never bar-0 tonic).
  - section midpoint degrees: `[IV, I, IV, IV, IV, IV, I, V, V, V]` — tonic variety
    guaranteed (no all-degree-i bug).

## Humanization (dual-version)

- Style profile `blues`: timing sigma 10 ms, velocity sigma 7, layback 3 ms,
  phrase correlation 0.55. Instrument DNA tunes roles (drums anchor 2 ms/0 layback,
  bass lays back 8 ms).
- `export_dual` (seed 20261110): validate + export `-perfect`, humanize in place,
  re-validate + export `-humanized`.
- Per-voice shift stats recorded in `provenance.json`.

## Verification (real numbers)

| check | perfect | humanized | phase1 |
|---|---|---|---|
| voice tracks | 5 | 5 | 1 |
| zero-drift (all len 76800) | ✓ | ✓ | ✓ |
| pitched off-grid | **0** | **817** (>0, jitter ran) | 289 (raw) |
| scale violations | **0** | **0** | 146 (raw) |
| chord violations | **0** | 4* | 189 (raw) |

\* The 4 humanized "chord violations" are bar-line jitter artifacts, not harmonic
errors: each is a V/IV-chord **downbeat** harmonica note jittered ≤7 ticks early
across a bar boundary, so it buckets into the previous bar. All are scale-clean
(pc in `{2,4,7,9,10,11}`) and correct chord tones in their true bar. Perfect layer
is 0, as required.

## Artifacts

- `MIDI/295-blues-aco-suite-phase1.mid`
- `MIDI/295-blues-aco-suite-perfect.mid`
- `MIDI/295-blues-aco-suite-humanized.mid`
- `Audio/295-blues-aco-suite-perfect.ogg`
- `Audio/295-blues-aco-suite-humanized.ogg`