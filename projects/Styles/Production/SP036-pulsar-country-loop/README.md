# SP-036 — Pulsar Synthesis · Country Loop (001-country-loop-seamless)

**Production pass:** SP-036 — Pulsar Synthesis (Curtis Roads, *Microsound* 2001)
applied to `001-country-loop-seamless` (Country, G major, 120 BPM, 16 bars, seamless loop).

| | |
|---|---|
| Source | `/opt/data/projects/Styles/Country/001-country-loop-seamless/MIDI/loop.mid` |
| Method | **SP-036 Pulsar Synthesis** — pulsaret trains at pulse rate f_p (pitch) decoupled from carrier/formant frequency f_f (spectrum) |
| Renderer | `render_sp036.py` |
| Output | `Audio/SP036-pulsar-country-loop.wav` + `.ogg` + per-voice stems |

## Method applied (SP-036)

Pulsar synthesis emits a strictly periodic train of *pulsarets* — short carrier
bursts windowed by a grain envelope. Pulse rate `f_p` sets perceived pitch;
carrier frequency `f_f` sets the spectral formant center. Because `f_p` and
`f_f` are independent, a stable pitch can carry freely-sweeping spectral color —
vowel-like timbres, pitched noise, granular textures.

Per-voice pulsar roles (methods_db SP-036 section 6):

| Voice (GM) | f_p | carrier | f_f | duty | envelope | gain |
|---|---|---|---|---|---|---|
| Lead — Violin (40) | MIDI pitch | sine | 3× f_p | 0.50 | Hann | 0.55 |
| Chords — Ac. Guitar (24) | MIDI pitch | saw | 2× f_p | 0.42 | Gaussian | 0.20/note (5-note strums) |
| Bass — Ac. Bass (32) | MIDI pitch | saw | 1× f_p | 0.90 | linear decay | 0.50 |
| Percussion (ch10) | sub-audio 4.3–6.0 Hz | noise | 2400 Hz color | 0.50 | linear decay | 0.42 |

Integer formant ratio `r = f_f/f_p` (lead 3, chords 2, bass 1) → clean resonant
tones; sub-audio pulse rates for drums → rhythmic ticking, not pitch.

## Implementation notes (pitfalls applied)

- **Continuous carrier phase accumulation** across pulsarets (pitfall 10) — no zipper noise on formant sweeps
- **Zero-aligned pulsaret phase** (pitfall 8) — stable formant centering
- **Duty ≤ 1 enforced** (pitfall 3) — no pulsaret overlap/alias
- **Hann/Gaussian/decay envelopes** (pitfalls 2, 5) — low sidelobes, no clicks
- **DC removal per voice** (pitfall 4) + 20 Hz highpass / 16 kHz lowpass (Butterworth, scipy)
- Per-note ADSR (15 ms attack / 90 ms release), velocity-scaled, peak-normalized 0.89
- Seeded RNG (20260826) for reproducible noise carriers

## Verification (SP-035 lesson applied)

| Check | Result |
|---|---|
| Events parsed / synthesized | 333 / 333 |
| Duration | 63.75 s |
| Silence ratio | 61.9 % (tail = drums-only loop bed, source-faithful) |
| RMS per second | 0.12–0.14 s 0–16 (full arrangement), ~0.034 s 16–63 (drum bed) |
| FFT pitch frames (50–1000 Hz) | 126 detected, median 86 Hz (bass register dominates dense mix) |
| **Lead F0 harmonic-sum** | MIDI 67/69/71 = G4/A4/B4 ✓ (violin melody exact) |
| **Bass F0 harmonic-sum** | MIDI 36–47 = G2–B2 ✓ (walking bass exact) |
| Harmonic energy @ single f0 | 17–25 % (dense 4-voice mix; SP-035 30% rule was for pure chorale) |

The naive FFT-dominant-peak check reads the 2nd harmonic of the lead in sparse
windows (saw/decay carriers are harmonic-rich) — harmonic-sum F0 search confirms
pitch accuracy. Stems: lead RMS 0.22 in the arrangement section (clearly
audible above chords 0.13 / bass 0.22 / perc 0.08).

## Structure note (source-faithful)

The source composition writes **8 bars of full arrangement** (violin arpeggios
over I–IV–V–I in G, 5-note guitar strums, walking bass, country backbeat) then
the **drum groove continues as a seamless loop bed** to ~64 s. The RMS drop at
16 s is the arrangement ending while the loop bed continues — intentional per
the project README ("Seamless end → start").

## Files

```
SP036-pulsar-country-loop/
├── render_sp036.py
├── provenance.json
├── MIDI/SP036-pulsar-country-loop.mid        (source copy)
├── Audio/
│   ├── SP036-pulsar-country-loop.wav         (full mix, 5.6 MB)
│   ├── SP036-pulsar-country-loop.ogg         (Opus 128k, 728 KB)
│   └── stems/
│       ├── stem_lead.wav
│       ├── stem_chords.wav
│       ├── stem_bass.wav
│       └── stem_percussion.wav
└── Analysis/
    ├── render_stats.json
    └── grid_visualization.txt
```

## Next steps

- SP-036 formant **sweep** on the lead (`f_f(t)` glide) for vowel-like country-fiddle color
- SP-034 HOA / SP-021 binaural spatialization of the stem stack
- Humanization (SP-006) on the drum pulsar onsets
