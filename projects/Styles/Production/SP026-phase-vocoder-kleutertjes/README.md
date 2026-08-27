# SP-026 — Spectral Phase Vocoder Resynthesis (Drie Kleine Kleutertjes)

Production pass: **SP-026 Spectral Phase Vocoder Resynthesis** applied to
**`variation_intro_verse.mid`** (Folk nursery rhyme "Drie Kleine Kleutertjes",
120 BPM, 85s).

| Field | Value |
|---|---|
| Method ID | SP-026 |
| Method | Spectral Phase Vocoder Resynthesis |
| Layer | Post-Processing / DSP |
| Target | Time-Stretched / Pitch-Shifted / Frozen Timbres |
| Source composition | `/opt/data/projects/Styles/Folk/001-folk-drie-kleine-kleutertjes/midi/variation_intro_verse.mid` |
| Source tempo | 120.0 BPM |
| Source duration | 85.0 s (GM render) |
| Source tracks | 1 track, 126 notes, pitch 48-65 (C3-F4), piano-ish GM |
| Render | `Audio/mix_spectral.wav` + `Audio/mix_spectral.ogg` (Opus) |
| Mastering | musicom `ProductionChain`: butter LP(12kHz) + StereoImager(1.2) + LUFS(-16) + Limiter(-1.0 dB) |

## What was done

The MIDI was rendered to a reference WAV with FluidSynth GM
(TimGM6mb.sf2). That audio was then pushed through the **SP-026 spectral
phase vocoder** — a full STFT analysis-modification-resynthesis pipeline:

1. **STFT analysis** — Hann window, N=2048, 75% overlap. Magnitude and
   phase captured per frame.
2. **Phase unwrapping → instantaneous frequency** — the phase increment
   between frames is unwrapped and converted to a true per-bin frequency
   (Flanagan/Schafer). This is what keeps the resynthesis phase-coherent.
3. **Time-stretch α = 1.2** — synthesis hop `H_s = α·H_a`; output phases
   are accumulated from the instantaneous frequencies, magnitudes are
   linearly interpolated. The nursery rhyme slows from 120 to an effective
   100 BPM — a dreamier lullaby pace.
4. **Spectral freeze tail** — the last sounding note's spectrum (final
   chord frame, auto-detected as the last frame above 5% max energy) is
   frozen: magnitude held constant, phase propagation continued, with an
   exponential decay over ~6 s. The piece ends in an ethereal pad instead
   of a hard stop.
5. **ISTFT WOLA resynthesis** — weighted overlap-add with squared-window
   normalization (denominator floored at 1e-4 to keep window edges clean).

### Layers

| Layer | Source | Treatment |
|---|---|---|
| GM source | FluidSynth TimGM6mb.sf2 | untouched reference (stems/gm_source.wav) |
| Stretched melody | SP-026 pass 1 | phase-vocoder time-stretch α=1.2 (stems/stretched.wav) |
| Freeze pad | SP-026 pass 2 | spectral freeze of final chord, 6 s decay (stems/freeze_pad.wav) |
| Mix | — | stretch + pad, 0.5 s crossfade, then mastering chain |

### SP-026 implementation notes (methods_db.md deviations)

The db reference code contained two bugs that were fixed for this render:

1. **Frame-count bug**: reference computes `n_frames_synthesis =
   ceil(n_frames_analysis / α)`, which cancels the stretch (output ≈ input
   length). Fixed: one synthesis frame per analysis frame with the
   stretched synthesis hop — output = α × input.
2. **Unit bug in instantaneous frequency**: reference code computes
   `omega = k·(2π/N)·H_a + wrap(dev)/H_a` (mixed units), which over-advances
   synthesis phase by factor H_a and cancels the output to silence. The
   methods_db *description* formula `ω̂ = k·(2π/N) + wrap(dev)/H_a`
   (radians/sample) is correct and was used instead.

Plus a robustness fix: WOLA normalization divides by `window_sum` which
collapses to ~1e-8 at signal edges; dividing numerical residue there
created a 162× peak spike that crushed the whole mix under normalization.
Denominator floor of 1e-4 fixes it.

## Verification

- pitch integrity: dominant spectral peak 260.8 Hz ≈ C4 (melody's home
  note) — phase vocoder preserved pitch under stretch
- stretch: 85.0 s → 101.9 s (α=1.2, +20%)
- freeze tail: 6.0 s, RMS 0.06-0.08 (audible, not silent)
- mastered: peak 0.891, RMS 0.136, 396/429 250ms-envelope windows active
- silence check: mastered 9.7% silence (legit phrase gaps + tail)

## Files

```
SP026-phase-vocoder-kleutertjes/
├── README.md
├── produce_sp026.py          # full production script (engine + pipeline)
├── MIDI/
│   └── original.mid          # source composition (DAW artifact)
├── Audio/
│   ├── mix_spectral.wav      # final stereo mix (mastered)
│   ├── mix_spectral.ogg      # Opus render (Telegram playback)
│   └── stems/
│       ├── gm_source.wav     # FluidSynth GM reference
│       ├── stretched.wav     # SP-026 time-stretch pass
│       ├── freeze_pad.wav    # SP-026 spectral-freeze tail
│       └── mix_raw.wav       # pre-master mix
└── Analysis/
    ├── provenance.json
    └── grid_visualization.txt
```

## Listen

- Original: `/opt/data/projects/Styles/Folk/001-folk-drie-kleine-kleutertjes/audio/variation_intro_verse.ogg`
- SP-026 render: `Audio/mix_spectral.ogg`
