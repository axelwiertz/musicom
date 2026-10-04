# 220-funk-contour-groove

**Funk × Contour Theory Composition (CTC)** — nightly autonomous composition.

- **Style:** Funk
- **Method:** 095 Contour Theory Composition (CTC) — `abstract` layer
- **Key:** E minor pentatonic (E G A B D) — pc {4,7,9,11,2}
- **Tempo:** 100 BPM · 4/4 · 480 TPB
- **Form:** Intro → Theme → Variation → Development → Climax → Outro (6 × 4 = 24 bars)
- **Voices:** Trumpet (lead) · Tenor Sax (stabs) · Clavinet (comp) · Contrabass (bass) · Drums (ch9)

## Concept

Melodic DNA is the **shape** of the line, not its notes. Abstract contour
prototypes (CSeg rank sequences + CAS up/down strings) are transformed under
the dihedral group {I, R, RI}, then concretized into the E-minor-pentatonic and
quantized to per-bar chord-tone palettes. Phase 1 keeps the raw whole-tone
off-grid draft; Phase 2 applies the funk grammar.

## Files

- `MIDI/220-funk-contour-groove.mid` (phase 2, rules) + `-phase1.mid` (raw)
- `Audio/220-funk-contour-groove.ogg` (Opus, listen) + `.wav` + `-phase1.*`
- `Analysis/` — grid visualization, summary, audit, render stats
- `REPORT.md` — full method + verification record

## Verification (all PASS)

- Zero-drift: 5 tracks = 46080 ticks, `validate()` PASS both phases
- Grid: **0** off-16th onsets
- Harmony: **0** out-of-scale, **0** out-of-chord (496 pitched onsets)
- Audio: silence 5.7%, peak 0.767, tonal 100%
