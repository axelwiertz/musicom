# Music-Tech Surveillance Findings

Replicability analyses from the Hermes agent's music-tech surveillance cron
(job e2760579d2c8, runs Mon/Thu). Distilled verdicts for musicom adoption.

## 2026-08-13 Scan

| Item | Technique | Verdict | Musicom path |
|------|-----------|---------|--------------|
| VAEMI Synterra | Scale quantizer + probability engine + MIDI scale mode | YES | **DONE** — sound/synthesis/scale_quantizer.py |
| KHÔRA (microtonal output) | Pitch bend + microtonal MIDI export | YES | **DONE** — sound/utils/midi.py |
| Karst (dice variation) | Dice variation + param scopes | YES | **DONE** — sound/generators/dice.py |
| Altitude | Math modulators + 24-step sequencer | YES | **DONE** — sound/modular/math_mod.py |
| Rev Ocean | FDN reverb (freeze + ducking) | YES | **DONE** — sound/effects/fdn_reverb.py |
| UVI Rumble | Multiband compressor + multiband synth | YES | **DONE** — sound/effects/multiband.py |
| ECHON 6 | Voice allocator + 9x32 mod matrix | YES | **DONE** — sound/synthesis/voice_allocator.py |
| Memory V | 4-part polyrhythmic arpeggiator | YES | **DONE** — sound/synthesis/polyrhythm.py |
| UDO DMNO | Binaural + Haas + play modes | YES | **DONE** — sound/synthesis/binaural.py |
| Obsidian | Wavefolder + lowpass gate (West Coast) | YES | **DONE** — sound/synthesis/west_coast.py |
| Radical1 | Quantize modulator + routing | YES | **DONE** — sound/effects/quantize_mod.py |
| Karst (patches) | JSON patch loader/builder | YES | **DONE** — sound/modular/patch_loader.py |

## 2026-08-17 Scan

| Item | Technique | Verdict | Musicom path |
|------|-----------|---------|--------------|
| SuperOS-808 (TR-808 replacement firmware) | Ratchet step sequencer: sub-division bursts, per-step probability + accent | YES | **DONE** — sound/generators/ratchet_seq.py |
| Digital chaos hardware (Sofia2 / Leibniz) | Iterated chaotic maps as CV (logistic/tent) | YES | **DONE** — sound/modular/chaos_cv.py |
| FDN reverb update (Rev-Ocean) | Freeze + ducking modes | PARTIAL | sound/effects/fdn_reverb.py (freeze exists; ducking pending) |
| Spectral/source separation | STFT + demucs | PARTIAL | effects/spectral.py planned (librosa + demucs) |

## 2026-08-03 Scan

| Item | Technique | Verdict | Musicom path |
|------|-----------|---------|--------------|
| Anukari | 3D mass-spring physical modeling | PARTIAL | synthesis/physical.py (JAX, long-term) |
| reFX Rippler | Modal synthesis, resonator banks | YES | **DONE** — sound/synthesis/modal.py |
| KARST | Generative event cores, algo sequencing | YES | **DONE** — sound/generators/event_core.py |
| MD-7 | Subtractive synth + sequencer | YES | **DONE** — sound/effects/filter.py (SubtractiveVoice) |
| SpectraLayers 13 | Spectral editing, ML separation | PARTIAL | effects/spectral.py (librosa + demucs, planned) |
| Waves Atlas Reverb | Algorithmic reverb (comb+allpass) | YES | **DONE** — sound/effects/reverb.py |
| Magical FDS Plug | Phase modulation, additive waveform | YES | **DONE** — sound/synthesis/phase_mod.py (FDSSynth) |
| Crow Hill Harmonic Piano | String harmonic extraction | APPROX | Bandpass on SF2 render |

## Mastering Guide (MusicTech / Mastering The Mix)

Key takeaways adopted into sound/effects/mastering.py:
- Mastering chain order: resonance removal → stereo image → tone/punch/loudness → QC
- Dynamic EQ > static EQ for resonances (only active when problem appears)
- Stereo rules: mono below 100Hz, widen highs, always mono-check
- Loudness targets: Spotify -14 LUFS, Apple Music -16 LUFS
- Level-match all A/B comparisons (loudness fools ears)
- Prep: -3 to -6dB headroom, no limiters on mix, 24-bit export, no dithering

## Audio-to-Tab / Notation (planned direction)

User-confirmed feature direction: accurate guitar/bass/piano/drum tabs from
audio, export as PDF / Guitar Pro / MIDI / MusicXML. Plus Flat.io integration.

Proposed architecture (not yet built):
```
sound/transcription/
├── separation.py   Demucs source separation
├── guitar.py       Guitar/bass → tab positions
├── piano.py        Piano → staff notation
├── drums.py        Drum classification → drum tab
└── export.py       Guitar Pro (.gp5), PDF via LilyPond
integrations/
└── flat_io.py      Flat.io REST API client
```

Existing foundation: sound/analysis/ (pitch/beat/onset/chroma), MIDI + MusicXML export.
