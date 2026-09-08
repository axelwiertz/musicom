# Project 013: Vocal Research Objectives

## Tonight's Goals (2026-05-30)

- [x] Research and document consonant spectral signatures for vocal synthesis: **S, SH, T, P**.
- [x] Build Python prototype: `/opt/data/projects/013-vocal-research/Prototypes/consonant_synth.py`.
- [x] Generate filtered-noise consonant bursts: `s_test.wav`, `sh_test.wav`.
- [x] Combine preceding **S** with vowel **A** and save `/opt/data/projects/013-vocal-research/Prototypes/sa_test.wav`.
- [x] Update objectives with findings.
- [x] Create progress summary.

## Consonant Spectral Signatures

### /s/ — alveolar sibilant

- Source: turbulent white noise at narrow front-groove constriction.
- Main spectral shape: high-frequency hiss.
- Useful synthesis band: high-pass above ~5 kHz.
- Strong energy: commonly ~5–11 kHz, often with bright peak around 7–9 kHz.
- Envelope: soft attack/release for sustained sung syllables; ~35–50 ms attack, ~45–50 ms release.
- Prototype choice: white noise → 5 kHz high-pass → mild 7.5 kHz resonance → linear attack/release.

### /ʃ/ "SH" — postalveolar sibilant

- Source: turbulent noise from wider/posterior constriction than /s/.
- Main spectral shape: darker, lower hiss than /s/.
- Useful synthesis band: broad band-pass ~2–7 kHz.
- Strong energy: commonly ~2.5–6 kHz, broad peak near 3–4.5 kHz.
- Envelope: similar to /s/, often slightly longer/smoother.
- Prototype choice: white noise → 2–7 kHz band-pass → broad 3 kHz and 4.5 kHz resonances → linear attack/release.

### /t/ — voiceless alveolar plosive

- Source: stop closure, pressure release burst, possible short aspiration.
- Main spectral shape: short broadband burst with high-frequency emphasis.
- Useful synthesis band: high-pass above ~3 kHz for release burst.
- Duration: short, ~20–60 ms total burst/noise, fast attack, ~40 ms decay.
- Prototype note: not implemented tonight in prototype, but signature ready.

### /p/ — voiceless bilabial plosive

- Source: lip closure release plus low-frequency pressure transient.
- Main spectral shape: low-frequency thud plus muted broadband/noise burst.
- Useful synthesis components:
  - thud below ~200 Hz,
  - short damped noise burst, less high-frequency than /t/.
- Duration: ~40–80 ms, near-instant attack, quick decay.
- Prototype note: not implemented tonight in prototype, but signature ready.

## Prototype Output

Script:

- `/opt/data/projects/013-vocal-research/Prototypes/consonant_synth.py`

Generated files:

- `/opt/data/projects/013-vocal-research/Prototypes/s_test.wav`
  - mono, 44.1 kHz, 0.180 s
  - measured whole-file spectral centroid: ~12.4 kHz
- `/opt/data/projects/013-vocal-research/Prototypes/sh_test.wav`
  - mono, 44.1 kHz, 0.220 s
  - measured whole-file spectral centroid: ~4.6 kHz
- `/opt/data/projects/013-vocal-research/Prototypes/sa_test.wav`
  - mono, 44.1 kHz, 0.708 s
  - 170 ms /s/ crossfaded by 12 ms into 550 ms sung /a/
  - vowel /a/ uses formants F1=730 Hz, F2=1090 Hz, F3=2440 Hz with 5.5 Hz vibrato at 1.2% depth.

## Implementation Notes

- Used SciPy Butterworth SOS filters for stable noise shaping.
- Used `scipy.signal.iirpeak` for spectral emphasis and vowel formants.
- Used standard-library `wave` writer for 16-bit PCM output.
- Added `/opt/data/.local/lib/python3.13/site-packages` to `sys.path` before SciPy import, matching skill environment note.
- Seeded RNG for reproducible consonant bursts.

## Cron Verification (2026-05-31 03:00)

- Re-ran `/opt/data/projects/013-vocal-research/Prototypes/consonant_synth.py` successfully.
- Confirmed regenerated outputs:
  - `s_test.wav`: mono, 44.1 kHz, 16-bit PCM, 0.180 s, centroid ~12.4 kHz.
  - `sh_test.wav`: mono, 44.1 kHz, 16-bit PCM, 0.220 s, centroid ~4.6 kHz.
  - `sa_test.wav`: mono, 44.1 kHz, 16-bit PCM, 0.708 s.
- Current /s/ and /ʃ/ models meet target contrast: /s/ bright high-frequency hiss; /ʃ/ lower, darker, broader hush.
- The /sa/ join uses 12 ms consonant-vowel overlap; onset is simple but usable for next coarticulation tests.

## Future Work

- Add /t/ and /p/ implementations to `consonant_synth.py`.
- Add spectrogram/FFT plots for visual validation.
- Add consonant-to-vowel coarticulation: formant fade-in, aspiration, and slight F0 onset delay.
- Test other syllables: `sha`, `ta`, `pa`, `sa-re`, `some`, `where`.
- Improve /sa/ realism with short aspiration tail and vowel amplitude ramp delayed ~15–25 ms after /s/ release.
