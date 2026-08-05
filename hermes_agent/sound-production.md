# Sound Production Knowledge Base

Operational guide for Hermes agent sound production on the musicom engine.

## Package Layout (sound/)

```
sound/
├── synthesis/    create audio from scratch
│   ├── modal.py      ResonatorBank, ModalSynth (presets: marimba/bell/drum/string/plate/tube)
│   ├── granular.py   AperiodicGranulator (SP-013 stochastic grains)
│   ├── phase_mod.py  PhaseModSynth, FDSSynth (wavetable PM)
│   ├── vocal.py      FormantVocalGuide (vowel synthesis)
│   └── additive.py   SoundWave (sine + overtones + ADSR + FFT)
├── effects/      transform audio
│   ├── reverb.py     AlgorithmicReverb (Schroeder 8-comb + 4-allpass), Freeverb
│   ├── filter.py     StateVariableFilter, BiquadFilter (RBJ), SubtractiveVoice
│   └── mastering.py  LUFSMeter, DynamicEQ, StereoImager, Limiter, MasteringChain
├── analysis/     extract info
│   ├── pitch.py      PitchDetector (librosa pyin)
│   ├── rhythm.py     BeatTracker, OnsetDetector
│   └── chroma.py     ChromaExtractor (chord recognition)
├── render/       symbolic → audio
│   ├── fluidsynth.py FluidSynthRenderer (CLI wrapper)
│   ├── vst.py        VSTRenderer (DawDreamer, needs py3.11 env)
│   └── pipeline.py   RenderPipeline (MIDI→WAV→OGG + render_stems)
├── generators/   event_core.py — generative pattern engines
├── sync/         clock.py — DAWClockBridge (MIDI clock/MTC)
└── utils/        pitch.py, io.py (read_wav/write_wav), envelope.py (ADSR)
```

## Render Chain

```bash
PY=/opt/data/micromamba/envs/musicom/bin
$PY/fluidsynth -ni -g 1.2 -F out.wav TimGM6mb.sf2 out.mid
ffmpeg -y -i out.wav out.ogg
```

## Stem Rendering (per-track WAVs)

Every production renders BOTH full mix and individual track stems:

```python
from sound.render import RenderPipeline

pipeline = RenderPipeline(
    fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
    soundfont_path="TimGM6mb.sf2"
)
pipeline.render_to_wav("composition.mid", "output/full_mix.wav")
stems = pipeline.render_stems("composition.mid", "output/stems/", format="wav")
# → {"track00_Flute": ".../track00_Flute.wav", ...}
```

## Mastering Chain (from MusicTech/Mastering-The-Mix workflow)

Order: resonance removal → stereo image → tone/punch/loudness → QC

1. **DynamicEQ** — tame resonances (boxy 300-500Hz, harsh 2-5kHz).
   Max 4-8 nodes. Avoid cuts below 250Hz (fix in mix instead).
2. **StereoImager** — mono below 100Hz always; 100-250Hz small width;
   widen highs for air/cymbals/reverb. Always mono-check.
3. **Limiter** — ceiling -1.0 to -0.1 dB, lookahead + release
4. **normalize_to_lufs** — targets: Spotify -14, Apple Music -16, YouTube -14

```python
from sound.effects import LUFSMeter, DynamicEQ, StereoImager, Limiter, normalize_to_lufs
```

## Preparation Rules (before mastering)

- Headroom: -3 to -6dB on mix bus
- No limiters on mix output — preserve transients
- Export 24-bit/44.1kHz, no dithering, gap at start/end for tails

## DSP Notes

- Reverb/filter per-sample Python loops (feedback dependencies) — offline only, not real-time
- Phase modulation depth is in RADIANS: `phase_offset = mod_signal * mod_depth / (2π)`
- SVF filter: `f = 2*sin(π*cutoff/sample_rate)`, `q = 1 - resonance`
- VSTRenderer needs the py3.11 env (dawdreamer)
