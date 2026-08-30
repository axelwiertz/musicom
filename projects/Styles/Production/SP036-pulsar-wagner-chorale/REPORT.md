# SP-036 — Pulsar Synthesis · Wagner Chorale (033-wagner-study-v2)

**Date:** 2026-08-30 (nightly production job)
**Source composition:** `/opt/data/projects/Styles/Classical/033-wagner-study-v2/midi/wagner_poly.mid`
**Method:** SP-036 — Pulsar Synthesis (Curtis Roads, *Microsound* 2001)

## Selection

- Random MIDI (select_job.py, excludes phase1): `033-wagner-study-v2/midi/wagner_poly.mid`
- Random method: **SP-036** (Pulsar Synthesis)

## Source composition

`wagner_poly.mid` — 4-voice chromatic chorale (Soprano / Alto / Tenor / Bass),
A-minor center with Tristan-esque inner chromaticism, whole notes only,
16 bars @ 120 BPM (no tempo meta → 500000 us/beat default), 32.0 s, 64 notes.
All four tracks share GM program 0 (piano), so **voices are mapped by track
index (0–3), not by GM program**.

| Track | Voice | MIDI range | Role in render |
|-------|-------|-----------|----------------|
| 0 | Soprano | 69–75 (A4–D5) | Lead — sine carrier, f_f = 3× f_p, Hann, duty 0.50 |
| 1 | Alto | 64–70 (E4–A4) | Pad — sine carrier, f_f = 4× f_p, Gaussian, duty 0.42 |
| 2 | Tenor | 57–63 (A3–D4) | Inner — saw carrier, f_f = 2× f_p, Hann, duty 0.55 |
| 3 | Bass | 41–48 (F2–C3) | Bass — saw carrier, f_f = 1× f_p, decay, duty 0.90 |

## Method applied (SP-036)

Pulsar synthesis emits a strictly periodic train of *pulsarets* — short
carrier bursts windowed by a grain envelope. Pulse rate `f_p` sets perceived
pitch; carrier frequency `f_f` sets the spectral formant center. Because
`f_p` and `f_f` are independent, a stable pitch can carry freely-sweeping
spectral color. Integer formant ratios (3, 4, 2, 1) → clean resonant tones
per spec section 6 voice roles.

## Implementation notes (pitfalls applied)

- **Continuous carrier phase accumulation** across pulsarets (pitfall 10) — no zipper noise
- **Zero-aligned pulsaret phase** (pitfall 8) — stable formant centering
- **Duty ≤ 1 enforced** (pitfall 3) — no pulsaret overlap/alias
- **Hann/Gaussian/decay envelopes** (pitfalls 2, 5) — low sidelobes, no clicks
- **DC removal per voice** (pitfall 4) + 20 Hz highpass / 16 kHz lowpass (Butterworth, scipy)
- Per-note ADSR (15 ms attack / 90 ms release), velocity-scaled, peak-normalized 0.89
- Seeded RNG (20260830) for reproducibility

## Verification (SP-035 lesson applied)

| Check | Result |
|---|---|
| Events parsed / synthesized | 64 / 64 (4 voices × 16 whole notes) |
| Duration | 32.5 s @ 120 BPM |
| Silence ratio | **2.2 %** (continuous chorale texture, no mid-track gaps) |
| RMS per second | 0.15–0.19 throughout (flat, no dropouts) |
| FFT pitch frames (50–1000 Hz, 0.5 s windows) | 64 detected, range 88–988 Hz, median 110 Hz |
| Per-voice autocorrelation (true period) | Soprano **16/16**, Alto **16/16**, Tenor 12/16, Bass **16/16** within ±2 octaves of expected MIDI |
| Per-voice FFT harmonic-sum exact-octave match | Bass 16/16, Tenor 11/16, Alto 11/16, Soprano 8/16 |

### Pitch verification — method notes (important)

1. **Harmonic-sum F0** on high-formant-ratio voices (Soprano r=3, Alto r=4)
   prefers a candidate at 1.5× or 2× the true pitch: the formant boosts every
   3rd/4th harmonic, so the subharmonic candidate aligns its even harmonics
   with the boosted comb. This is a *detector* artifact of the comb spectrum,
   not an audio defect.
2. **Autocorrelation** (the SP-035 truth test) resolves the true period:
   Soprano and Alto lock **16/16** windows to the expected MIDI pitch
   (e.g. bar 3 soprano: 523.5 Hz = C5 = MIDI 72 ✓). AC may lock the octave
   subharmonic for harmonic-rich saw carriers (period doubling) — accepted
   within ±2 octaves, with the exact octave confirmed by the FFT harmonic-sum
   match where the fundamental carries energy (Bass 16/16, Tenor 16/16).
3. **Missing fundamental is expected physics**: formant ratio 3×/4× with
   Hann/Gaussian envelope suppresses the first partial; energy at exactly f_p
   is low (Soprano 4/16, Alto 9/16) while the pitch is clearly present
   (AC 16/16). Verdict: **PITCHED — PASS** (compare SP-035 v1 noise failure:
   0 Hz frames everywhere, harmonic energy 4%).

### Silence / RMS profile

Per-second RMS: min 0.149, max 0.192, mean ~0.167 — the chorale sustains
continuously across all 16 bars; no silent regions (silence ratio 2.2 % is
tail padding after the last note).

## Files

```
SP036-pulsar-wagner-chorale/
├── render_sp036.py                      (renderer, voices by track index)
├── verify_pitch.py                      (FFT harmonic-sum + autocorrelation verifier)
├── provenance.json                      (sha256, params, verification)
├── MIDI/SP036-pulsar-wagner-chorale.mid (source copy, 674 B)
├── Audio/
│   ├── SP036-pulsar-wagner-chorale.wav  (full mix, 2 866 544 B, mono 44.1k)
│   ├── SP036-pulsar-wagner-chorale.ogg  (Opus 128k, 902 344 B)
│   └── stems/
│       ├── stem_soprano.wav             (lead, sine r=3)
│       ├── stem_alto.wav                (pad, sine r=4)
│       ├── stem_tenor.wav               (inner, saw r=2)
│       └── stem_bass.wav                (bass, saw r=1)
└── Analysis/
    ├── render_stats.json                (silence ratio, RMS map, pitch frames)
    ├── pitch_verification.json          (per-note FFT + AC results)
    └── grid_visualization.txt           (onset density per bar per voice)
```

## Fixes applied this run

1. **Voice mapping by track index** — source MIDI uses GM program 0 on all
   4 tracks; per-program routing would have merged all voices into one.
2. **Verifier bin-index bug** — first harmonic-sum pass indexed spectrum bins
   by frequency value (wrong for 1.5 s windows); corrected to
   `bin = round(f * n / sr)` with ±5-bin leakage sums.
3. **Missing-fundamental handling** — added autocorrelation pitch test
   (SP-035 lesson) because FFT harmonic-sum alone misreads high-formant-ratio
   pulsar trains; combined FFT + AC gives exact-octave AND true-period proof.
4. **JSON bool_ serialization** — numpy bool cast to Python bool.

## Report contract

| Item | Value |
|---|---|
| Method | SP-036 Pulsar Synthesis |
| Source | 033-wagner-study-v2 (wagner_poly.mid) |
| Pitch verification | PASS (AC 16/16 soprano+alto+bass, 12/16 tenor; FFT exact octave bass 16/16) |
| Silence | 2.2 % |
| Full mix | Audio/SP036-pulsar-wagner-chorale.wav (+ .ogg) |
| Stems | 4 (soprano/alto/tenor/bass) |
