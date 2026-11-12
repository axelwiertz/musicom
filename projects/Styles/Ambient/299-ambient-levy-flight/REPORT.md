# 299 — Ambient Lévy Flight

## Summary

| Field | Value |
|---|---|
| Project | 299-ambient-levy-flight |
| Style | Ambient |
| Method | 053 Lévy Flight Composition (LFC) |
| Paradigm | Stochastic |
| **Layer** | **concrete** |
| Form | through-composed (S1…S6, 4 bars each = 24 bars) |
| Key | A natural minor `{0,2,4,5,7,9,11}` |
| Tempo | 72 BPM, 4/4 |
| Length | 24 bars ≈ 80 s + tail |
| Seed | 20261111 · humanize seed 263394742 · form seed 202611117 |

## Concept

A single melodic voice performs a **Lévy flight** in pitch space. Step lengths
are Pareto-distributed (`mag = (1−U)^(−1/α)`): most steps are tiny (1–2
semitones → conjunct motif cells), a few are enormous (register flights,
clipped at 36…96). The **tail index α** is the compositional dial, and a
per-section α schedule drives the macro-form:

| Section | α | Character | Phase-1 mean pitch | Phase-1 max leap |
|---|---|---|---|---|
| S1 | 1.3 | heavy tail, sparse register-shattering jumps | 90.66 | 28 |
| S2 | 1.6 | moderate | 63.94 | 4 |
| S3 | 1.9 | light tail, dense motif clusters | 64.44 | 10 |
| S4 | 1.4 | re-enter heavy tail (climax shatter) | 57.34 | 9 |
| S5 | 2.0 | near-Gaussian conjunct | 53.28 | 13 |
| S6 | 2.5 | settle, cluster toward tonic | 57.78 | 4 |

## Harmony — i–VI–III–VII (A natural minor)

Am — F — C — G, repeated per section (Resolve-style cadence not needed in
through-composed form). Bass roots: Am=A2(45), F=F2(41), C=C2(36), G=G2(43).

## Voices (instrument registry)

| Voice | Instrument | Program | Channel | Role |
|---|---|---|---|---|
| Lead | Flute | 73 | 0 | Lévy contour (tiered snap) |
| Pad | Warm Pad | 89 | 1 | sustained triad |
| Bass | Synth Bass 1 | 38 | 2 | root/fifth |
| Arp | Vibraphone | 11 | 3 | sparse 8th arpeggio |
| Drums | Drum Kit | ch9 | 9 | soft ambient kick + airy tick |

## Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw single-voice Lévy walk, unquantized pitch,
  off-grid onset jitter, no harmony. **189 / 192 onsets off the 16th grid** —
  deliberately unquantized (that is the raw character).
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): grid-lock to 8th grid →
  tiered snap (strong beat → chord tone, weak → A-minor scale tone) → full
  texture → zero-drift landmark → `validate()` → `export_dual`.

## Grid audit (pre-humanization, perfect)

Every pitched voice: **0 off-grid** on both 16th (120) and 8th (240).

| Voice | 16th off-grid | 8th off-grid |
|---|---|---|
| Lead | 0/191 | 0/191 |
| Bass | 0/48 | 0/48 |
| Pad | 0/144 | 0/144 |
| Arp | 0/128 | 0/128 |

## Harmony audit (tiered pitch discipline, `audit_voice`)

All voices PASS — 0 untagged-out-of-scale, 0 non-resolving ornaments,
0 strong violations. Lead carries no tagged chromatic here (pure diatonic
A-minor contour is musically apt for ambient).

| Voice | total | strong_ok | weak_in_scale | untagged_out | non_resolving | strong_viol |
|---|---|---|---|---|---|---|
| Lead | 191 | 48 | 143 | 0 | 0 | 0 |
| Bass | 48 | 48 | 0 | 0 | 0 | 0 |
| Pad | 144 | 144 | 0 | 0 | 0 | 0 |
| Arp | 128 | 48 | 80 | 0 | 0 | 0 |

## Humanization (style-derived, seeded)

Style `ambient`, seed `263394742`. Per-voice profile + instrument DNA,
recorded in provenance. Drums tightest (2 ms), bass lays back (+8 ms), lead
loosest. `mean/max` absolute shift in ticks + velocity delta:

| Voice | timing σ (ms) | layback | mean shift (ticks) | max shift | vel δ |
|---|---|---|---|---|---|
| Lead | 6.0 | 0 | 2.70 | 9 | 4.98 |
| Pad | 6.0 | 0 | 1.77 | 6 | 2.98 |
| Bass | 5.0 | +8 | 5.40 | 12 | 3.47 |
| Arp | 6.0 | 0 | 2.85 | 9 | 4.23 |
| Drums | 2.0 | 0 | 0.82 | 3 | 3.04 |

Post-export readback (mido, read-only): **perfect = 0 off-grid / 631 note-ons;
humanized = 524 off-grid (>0, humanizer ran)**. All 5 voice tracks = 46080
ticks (zero-drift).

## Rendering + mastering

FluidSynth (FluidR3_GM, `-R no -C no`) → WAV → `master()` → Opus OGG, for all
three artifacts (`-perfect`, `-humanized`, `-phase1`). Target = ambient
`target_for_style("ambient")` = **−18 LUFS**, ceiling −1 dBTP.

| Artifact | target LUFS | measured LUFS | true peak | silence |
|---|---|---|---|---|
| perfect | −18 | −18.0 | −5.46 dB | 5.14% |
| humanized | −18 | −18.0 | −5.86 dB | 5.02% |
| phase1 | −18 | −18.0 | −3.09 dB | 4.54% |

All three hit the −18 LUFS target exactly; true peaks sit well under the −1 dBTP
ceiling (correct — quiet material is not pushed up); silence ratios ~5% with no
mid-track gaps.

## Files

```
299-ambient-levy-flight/
├── compose.py                       # engine-only two-phase generator
├── render_audio.py                  # FluidSynth + master + OGG
├── verify.py                        # mido read-only zero-drift/grid audit
├── README.md / REPORT.md / index.html
├── MIDI/  299-…-phase1.mid / -perfect.mid / -humanized.mid (+ provenance)
├── Audio/ 299-…-perfect.ogg / -humanized.ogg / -phase1.ogg (+ .wav, stats)
└── Analysis/ grid_visualization.txt / manifest.json / readback.json
```

## Fixes applied

- `verify.py` zero-drift check initially failed against the tempo meta track
  (length 0 by design); corrected to compare note-carrying tracks only.

## Layer: concrete

Method 053 (Lévy Flight Composition) is a **concrete** method — implemented
directly in engine code (numpy Pareto step sampling) without an abstract
interpretation step.