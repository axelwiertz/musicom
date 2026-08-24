# Music-Tech Surveillance Findings

Replicability analyses from the Hermes agent's music-tech surveillance cron
(job e2760579d2c8, runs Mon/Thu). Distilled verdicts for musicom adoption.

## 2026-08-24 Scan

| Item | Technique | Verdict | Musicom path |
|------|-----------|---------|--------------|
| Minimal Audio Lucid (granular FX) | Real-time granulation + scale-lock (grain pitch quantized to user key/scale) + tempo-synced grain scheduling + stretch/scrub modes + harmonic grain delay (scale-locked shimmer/arp taps) | YES | **DONE** — sound/effects/scale_locked_granular.py (350-preset library, Animator X-Y pad, multi-mode grain filter/imager = proprietary, not replicated) |
| Rapid Flow miniGRID (sequencer) | 4-lane MIDI step sequencer with per-lane ±64 ms micro time shift (0.02 ms fine), 32 steps/lane, per-lane mute/solo + 7 vintage shuffle styles (TR-909, Tanzbar, MPC60, SP-12, MPC3000, DMX, LM-1) | YES | **DONE** — sound/generators/micro_timing_seq.py (DAW transport lock / plugin UI = host concern, not replicated) |
| Parish Audio Parametric Compressor | Up to 10 overlapping parametric compressor bands (bell filters, no fixed crossovers), per-band threshold/ratio/attack/release/makeup + frequency/width, per-band detection source (band-limited / full-range / external sidechain) | YES | **DONE** — sound/effects/overlap_comp.py (interactive spectrum display = UI, not replicated) |
| Sound Radix Radical1 Solo (free additive monosynth) | Additive oscillator engine + filters + modulation; full Radical1 adds Route/Quantize modulators (already covered by sound/effects/quantize_mod.py) | PARTIAL | sound/synthesis/additive.py exists (SoundWave); Radical1's proprietary additive engine + preset library NOT replicated — no new code |
| Audio Modeling PolySWAM (physical-modeling orchestra) | SWAM physical modeling engine + proprietary voice-allocation distributing notes among virtual players (legato/staccato/portamento from performance, no keyswitches) | PARTIAL | sound/synthesis/bowed.py + voice_allocator.py cover components; SWAM's per-player phrasing engine is proprietary — no new code |
| Love Synthesizers First Love (hardware FM/wave-morphing synth) | Wave morphing + morphing envelopes + FM, 4-part multitimbral, live looping, riff sequencing, microtonal tuning | PARTIAL | sound/synthesis/phase_mod.py (FM) + west_coast.py (wavefolder) + polyrhythm.py (arps) cover pieces; hardware engine proprietary — no new code |
| Cubase 15 / Celemony Tonalic | Virtual session musician following the Chord Track; pattern 'sets' with transitions/endings (strum/pick/arpeggio/power-chord/melodic) | PARTIAL | Orchestration direction; needs recorded performance content + chord-track follower — future (see planned) |
| Yurt Rock Dr. Fill | Human-played drum fill sample library (no AI) | NO | Sample content, not algorithm |
| Harrison Flex-10 (interface) | Vintage console-style mic pres + HP/LP filters + inserts | NO | Analog hardware |
| KRK V Series Five (monitors) | Wireless control of monitor tuning | NO | Hardware/network |
| Audiocube Space | 3D panner (binaural/spatial) | PARTIAL | sound/synthesis/binaural.py covers binaural/Haas; 3D panner UI + HRTF set not replicated |

## 2026-08-20 Scan

| Item | Technique | Verdict | Musicom path |
|------|-----------|---------|--------------|
| Spectdrum (rhythmic spectral gate) | Multi-band split + per-band step sequencer (polyrhythmic lengths, velocity/accents/swing) + master normalize | YES | **DONE** — sound/effects/spectral_gate.py |
| Rithmatic (DX7 voice parser) | Packed 128-byte + expanded 155-byte DX7 voice parsing (op params, algorithm, feedback, name) | YES | **DONE** — sound/synthesis/dx7_voice.py |
| Synthesizers.com Q210 (complex noise) | White/pink/metallic noise + grainy processing + random gates | YES | **DONE** — sound/generators/complex_noise.py |
| Audio Damage AD-202 (MC-202 monosynth) | Saw/pulse/sub/noise VCO → 4-pole lowpass + resonance → ADSR → LFO → post-VCA color (saturation/drive/tilt EQ) | YES | **DONE** — sound/synthesis/mono_synth.py |
| Triton Tilt EQ | Tilt EQ rotating tonal balance around a pivot frequency | YES | **DONE** — sound/effects/tilt_eq.py |
| Liminal Space 2 (reverb) | Algorithmic reverb + gated/collapse decay envelopes + shimmer pitch-shift + LEXITONE decay shaping | PARTIAL | sound/effects/liminal_reverb.py (gated decay + shimmer + LEXITONE in; 4,636 profiled algorithms / per-tap DLFO modulation not replicated) |
| MathSynth (equation synth) | Equation → waveform evaluation engine with safe namespace | YES | **DONE** — sound/synthesis/equation_synth.py |
| Monochord (chord workstation) | Chord voicing from tonal sets + arpeggiation/strum/humanization MIDI output | PARTIAL | sound/synthesis/mono_synth.py + generators/ratchet_seq.py (chord triggers + 600 chord library NOT replicated; requires sample library + hand-voiced chord data) |

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
