# Sound Methods Overview — Comparison & Workflow Usage

Bridge document between the SP-xxx registry (`methods-registry.md`), the
surveillance findings (`surveillance.md`), and actual engine code in
`sound/`. Answers: *what transformation/creation method exists, what is it
comparable to, and how do I use it in a workflow?*

## 1. Method Comparison Table (creation + transformation)

| Method (file) | Class(es) | Category | Comparable to | Input → Output |
|---|---|---|---|---|
| `sound/synthesis/phase_mod.py` | PhaseModSynth, FDSSynth | synthesis | FM/DX7, FDS (NES) | freq+dur → WAV |
| `sound/synthesis/modal.py` | ResonatorBank, ModalSynth | physical modeling | AAS String Studio, physical vibraphone | mode params → WAV |
| `sound/synthesis/granular.py` | AperiodicGranulator | synthesis | granular, Clouds-style | grains → WAV cloud |
| `sound/synthesis/vocal.py` | FormantVocalGuide | synthesis | vocoder, formant synth | freq+vowel → WAV |
| `sound/synthesis/additive.py` | SoundWave | synthesis | additive, Hammond drawbars | sine+overtones → WAV |
| `sound/synthesis/bowed.py` | BowedString | physical modeling | bowed string, friction waveguide | note → WAV |
| `sound/synthesis/mass_spring.py` | MassSpringSystem | physical modeling | ANUKARI 3D mass-spring | bodies+springs → WAV |
| `sound/synthesis/west_coast.py` | Wavefolder, LowpassGate | waveshaping | Buchla West Coast, wavefolder | audio → folded audio |
| `sound/synthesis/binaural.py` | BinauralSynth, HaasDelay | spatial | binaural, Haas | mono → stereo/binaural |
| `sound/synthesis/polysynth.py` | Oscillator, EnvelopeGenerator | synthesis | virtual analog polysynth | note → WAV |
| `sound/synthesis/scale_quantizer.py` | ScaleQuantizer, ProbabilityEngine | pitch | Synterra, quantizer | value → scale pitch |
| `sound/synthesis/voice_allocator.py` | VoiceAllocator | voice mgmt | ECHON-6 mod matrix | voices → rendered mix |
| `sound/synthesis/polyrhythm.py` | PolyrhythmicArp | sequencing | Memory-V arp | notes+divisions → pattern |
| `sound/effects/filter.py` | StateVariableFilter, BiquadFilter | filter | SVF, RBJ biquad | audio → filtered audio |
| `sound/effects/reverb.py` | AlgorithmicReverb | reverb | Schroeder, Freeverb | audio → wet audio |
| `sound/effects/fdn_reverb.py` | FDN | reverb | Rev-Ocean, FDN | audio → FDN reverb |
| `sound/effects/vowel_filter.py` | VowelFilterBank | filter | vowel formant filter | audio → vowel-filtered |
| `sound/effects/tape_delay.py` | TapeDelay, SamplePlayer | delay/sampler | tape echo, drum machine | audio → delay/sample |
| `sound/effects/multiband.py` | MultibandCompressor | dynamics | UVI Rumble, multiband comp | audio → compressed |
| `sound/effects/quantize_mod.py` | QuantizeModulator, ModRouter | modulation | Radical1, quantize | values → quantized CV |
| `sound/effects/mastering.py` | LUFSMeter, DynamicEQ, Limiter | mastering | Ozone, Mastering-the-Mix | mix → mastered mix |
| `sound/effects/production_chain.py` | ProductionChain | chain | Ableton rack chain | audio → staged chain |
| `sound/modular/graph.py` | Node, OscNode, GainNode | modular | SynthEdit, VCV Rack | node graph → audio |
| `sound/modular/math_mod.py` | MathModulator, StepSequencer24 | modulation | Altitude | math expr → CV |
| `sound/modular/chaos_cv.py` | ChaosCV | modulation | Sofia2 / Leibniz | chaotic map → CV |
| `sound/modular/patch_loader.py` | PatchLoader, PatchBuilder | modular | Karst patches | JSON patch → graph |
| `sound/generators/event_core.py` | EventCore + Markov/Stochastic/Euclidean/LSystem/WeightedRandom cores | generative | KARST | params → event seq |
| `sound/generators/ratchet_seq.py` | RatchetSequencer | sequencing | SuperOS-808 | step+ratchet+prob+accent → events |
| `sound/generators/complex_noise.py` | ComplexNoise | synthesis (noise) | Q210 complex noise | noise type → white/pink/metallic/grainy/gate |
| `sound/generators/dice.py` | DiceVariation | variation | Karst dice | params → varied params |
| `sound/synthesis/mono_synth.py` | MonoSynth | synthesis | AD-202 / Roland MC-202 | osc+filter+env+lfo → mono WAV |
| `sound/synthesis/dx7_voice.py` | DX7Voice, DX7Operator, parse_dx7_packed/expanded | format parser | Rithmatic, DX7 | 128/155-byte voice → params dict |
| `sound/synthesis/equation_synth.py` | EquationSynth | synthesis | MathSynth | math expr (t,f,dur) → WAV |
| `sound/effects/spectral_gate.py` | SpectralGate | rhythmic spectral FX | Spectdrum | audio+patterns → gated audio |
| `sound/effects/tilt_eq.py` | TiltEQ | EQ | Triton Tilt EQ | audio+tilt → tilted audio |
| `sound/effects/liminal_reverb.py` | LiminalReverb | reverb | Liminal Space 2 | audio → gated/shimmer reverb |
| `sound/effects/scale_locked_granular.py` | ScaleLockedGranular | granular FX | Minimal Audio Lucid | audio → scale/tempo-locked grains + harmonic delay |
| `sound/effects/overlap_comp.py` | OverlapCompressor, CompBand | dynamics | Parish Audio Parametric Compressor | audio → overlapping-band compressed audio |
| `sound/generators/micro_timing_seq.py` | MicroTimingSequencer | sequencing | Rapid Flow miniGRID | lanes+shifts+shuffle → timed MIDI events |
| `sound/utils/midi.py` | MicrotonalExporter | export | KHÔRA microtonal | notes → pitch-bend MIDI |
| `sound/tuning/just_intonation.py` | JustIntonation | tuning | KHÔRA | ratio → freq/scale |
| `sound/sync/clock.py` | DAWClockBridge | sync | MTC/MIDI clock | bpm → clock pulses |
| `sound/render/fluidsynth.py` | FluidSynthRenderer | render | SF2 synth | MIDI → WAV |
| `sound/render/vst.py` | VSTRenderer | render | DAW VST3 | MIDI → VST audio |
| `sound/render/pipeline.py` | RenderPipeline | render | export chain | MIDI → WAV/OGG/stems |

## 2. Categories at a glance

| Category | Purpose | Key files |
|---|---|---|
| **synthesis/** | create audio from scratch | phase_mod, modal, granular, vocal, additive, bowed, mass_spring, polysynth, west_coast, mono_synth, dx7_voice, equation_synth |
| **effects/** | transform existing audio | filter, reverb, fdn_reverb, vowel_filter, tape_delay, multiband, quantize_mod, mastering, production_chain, spectral_gate, tilt_eq, liminal_reverb, scale_locked_granular, overlap_comp |
| **modular/** | node-graph DSP | graph, math_mod, patch_loader |
| **generators/** | generative event/pattern engines | event_core, dice, ratchet_seq, complex_noise, micro_timing_seq |
| **analysis/** | extract info from audio | pitch, rhythm, chroma |
| **render/** | symbolic → audio | fluidsynth, vst, pipeline |
| **tuning/** | microtonal / just intonation | just_intonation |
| **sync/** | DAW clock | clock |
| **utils/** | shared helpers | io, envelope, pitch, midi |

## 3. How to use in a workflow

### A. Full composition → sound pipeline (most common)
```python
# 1. compose (UnitMatrix)
composer = UnitMatrixComposer(bpm=120)
composer.create_matrix(num_voices=4, num_sections=4)
# ... add voices/sections/fill cells ...
ok, msg = composer.validate()          # zero-drift gate
composer.to_midi("out.mid")

# 2. render MIDI → WAV/OGG + stems
from sound.render import RenderPipeline
pipe = RenderPipeline(fluidsynth_bin=".../fluidsynth", soundfont_path="TimGM6mb.sf2")
pipe.render_to_wav("out.mid", "mix.wav")
pipe.render_to_ogg("out.mid", "mix.ogg")
stems = pipe.render_stems("out.mid", "stems/", format="wav")
```

### B. Transform a rendered mix (effects chain)
```python
from sound.effects import AlgorithmicReverb, BiquadFilter, TapeDelay, normalize_to_lufs
from sound.utils.io import read_wav, write_wav

audio, sr = read_wav("mix.wav")
wet = AlgorithmicReverb(sample_rate=sr).process(audio, size=0.7)
wet = BiquadFilter(sample_rate=sr).process(wet, cutoff=12000, mode="lowpass")
wet = TapeDelay(sample_rate=sr).process(wet, delay_seconds=0.28, feedback=0.3)
write_wav("mix_processed.wav", wet, sr)
```

### C. Synthesize from scratch (no MIDI)
```python
from sound.synthesis import PhaseModSynth, ModalSynth, FormantVocalGuide

pm = PhaseModSynth().render_note(freq=440.0, duration=1.0, mod_depth=2.0)   # FM tone
marimba = ModalSynth(preset="marimba").render_note(midi=72, duration=0.5)  # physical
voc = FormantVocalGuide().render_syllable(freq=330.0, dur=1.0, vowel="a")  # formant
```

### D. Generative events (pattern engines)
```python
from sound.generators.event_core import MarkovCore, EuclideanCore

mc = MarkovCore(transition_matrix={0: {0: 0.5, 1: 0.5}, 1: {0: 0.5, 1: 0.5}})
seq = mc.generate(steps=32, seed=42)              # probability-driven events
ec = EuclideanCore()
hits = ec.generate(steps=16, pulses=5)            # Euclidean rhythm
```

### E. Modular node graph
```python
from sound.modular.graph import Node, OscNode, GainNode, LfoNode

g = OscNode(freq=220.0, waveform="saw")
lfo = LfoNode(freq=0.5)
gain = GainNode(gain=0.5)
# connect and process n_samples
```

## 4. Replicability flow (surveillance → registry → code)

1. **Surveillance cron** (Mon/Thu) finds gear techniques → `hermes_agent/surveillance.md`
2. **Registry** `hermes_agent/methods-registry.md` tracks SP-xxx status
3. **Code lands** in `sound/` (see paths above)
4. **This overview** keeps the comparable + how-to-use view current

## 5. Pitfalls

- `sound/synthesis/granular.py` stochastic grains need a seed for determinism
- `sound/effects/*` per-sample Python loops are offline-only (not real-time)
- `VSTRenderer` requires the py3.11 env (dawdreamer); `FluidSynthRenderer` works everywhere
- Microtonal export uses pitch bends (2-semitone range default) — check `MicrotonalExporter(cents_range=...)`
- `production_chain.py` stages run in order; each stage's report has `summary_table()`
