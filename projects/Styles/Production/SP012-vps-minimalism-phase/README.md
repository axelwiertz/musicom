# SP-012 — VPS Minimalism Phase

Vector Phase Shaping (SP-012) production pass on the **Minimalism Phase Study**
(Reich-style Clapping Music phase piece, 120 BPM, 8×3 bars, 5 voices).

## Artifacts

- `Audio/SP012-vps-minimalism-phase.ogg` — full mix (Opus 48k voip)
- `Audio/SP012-vps-minimalism-phase.wav` — full mix (51 s stereo)
- `Audio/stems/` — per-voice VPS mixdowns (marimba / pad / bass / kick)
- `MIDI/minimalism-phase.mid` — source MIDI copy
- `Analysis/` — render_info, stems_info, pitch_verification, grid
- `REPORT.md` — full production report (method, params, verification, fixes)

## Verification summary

- Silence ratio: **4.9%** (continuous pad/bass layers; only reverb tail quiet)
- FFT pitch frames: **192/202 (95%)** detected, 64–880 Hz, median 132 Hz
- Bass-stem harmonic energy (8 harm of C2): **69.2%** (≥ 30% → tonal, not noise)
- Spectral flatness: **0.118** (white noise ≈ 1.0)

Run: `render_sp012.py` (mix) · `render_stems.py` (stems + verify) ·
`verify_pitch.py` (FFT/spectral analysis).
