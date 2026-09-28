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
| `sound/generators/trig_cond_seq.py` | TrigConditionSequencer | sequencing | Volca Drum alt firmware, Elektron trig conditions | steps+conditions+accents → gated events (pass-based) |
| `sound/synthesis/drum_synth_606.py` | DrumSynth606 | synthesis (drums) | AudioKit Super 606, Roland TR-606 | voice params → kick/snare/tom/clap/hat + flams/beat |
| `sound/synthesis/spectral_wavetable.py` | SpectralWavetableExtractor | synthesis (wavetable) | 3rd Wave Make Waves Spectral | audio → STFT-scored wavetable → oscillator |
| `sound/effects/room_reverb.py` | RoomReverb | reverb | bathROOMs, small-room reverb | audio+position/surface/slap/wash/temp → room audio |
| `sound/generators/param_lock_seq.py` | ParamLockSequencer | sequencing | Asterism, X0X param-lock | base params+locks+ratchet+randomize → (frac, params) hits |
| `sound/synthesis/memorymoog_synth.py` | MemorymoogVoice | synthesis | Memorymode 2, Memorymoog | freq+dur+detune-mode+doubling → WAV |
| `sound/synthesis/supersaw_swarm.py` | SupersawSwarm, SwarmSnapshot, MorphPad | synthesis | NI SuperStarSaw, JP-8000 supersaw | freq+dur+spread+harmony → stereo saw-swarm WAV (morphable via XY pad) |
| `sound/effects/bbd_chorus.py` | BBDChorus | effects (chorus) | UVI Thorus XT, Roland Dimension D / Juno chorus | audio+voices+rate+depth → BBD chorus wet mix (clocked, companded, per-voice variation) |
| `sound/effects/shimmer_reverb.py` | ShimmerVerb | effects (reverb) | 3rd Wave Shimmer Verb, shimmer reverbs | audio+pitch_cents+rev_time+pitch_amount → fractional-shift shimmer tail |
| `sound/generators/sample_slicer.py` | SampleSlicer, Slice, auto_tempo, auto_pitch | sampling | Bitwig 6.1 Sampler | audio → onsets/slices → played slices (oneshot/loop/reverse/pingpong) + BPM/pitch estimate |
| `sound/synthesis/formant_voice.py` | FormantVoiceSynth | synthesis (voice) | klattsch, Klatt 1980 cascade formant synth | phones/text+pitch curve → formant voice WAV (40+ phones incl. kana vowels, tts front end) |
| `sound/effects/subharmonic.py` | SubHarmonicGenerator, SubBand | effects (sub/LFE) | Penteo 8 Synthesized LFE, sub-harmonic pedals | audio → pitch-tracked 3-band sub-octave LFE signal (mute-able bands, add-fifth/sub-sub) |
| `sound/utils/midi.py` | MicrotonalExporter | export | KHÔRA microtonal | notes → pitch-bend MIDI |
| `sound/tuning/just_intonation.py` | JustIntonation | tuning | KHÔRA | ratio → freq/scale |
| `sound/effects/topology_distortion.py` | FuzzBillion, TopologyStage | effects (distortion) | Teaching Machines FuzzBillion | audio + 11-switch code (10^11 circuits) + gain → distorted audio |
| `sound/effects/morph_filter.py` | FusionFilter, filter_character | effects (filter) | ZERO9 Fusion Filter | audio + cutoff/res/position(0..4) → morphed five-character filtered audio |
| `sound/effects/severance.py` | GatedReverb, DualEngineDelay, RhythmicGlitchChain, ParallelBandCompressor, spectral_declash | effects (ZERO9 suite) | ZERO9 Severed Space / Eccentric Echo / Fractured Frequency / Crushing Compressor | audio + triggers/patterns → gated-reverb, dual-engine delay, glitch chain, 4-band up/down parallel compression |
| `sound/synthesis/critter_pad.py` | PadPartialBank, Partial, Critters | synthesis (pads) | Crow Hill Brackish Pads | partial balances + seed → wobbling microtonal pad with stochastic Critters layer, cassette + splosh |
| `sound/synthesis/music_box.py` | TwinCombMusicBox, MusicBoxComb | synthesis (modal, idiophone) | Muro Box N40 (Sublime twin comb) | midi note/melody + detune cents → inharmonic tine stereo audio (14-cent twin-comb chorus) |
| `sound/generators/drum_machine.py` | BullfrogDrums, SampleChannel, CVChannel, Kit | sequencing (drum machine) | Erica Synths Bullfrog Drums | 64-step X0X grid + velocity/swing/flam → stereo kit audio + CV/midi sequence |
| `sound/synthesis/lfsr_voice.py` | LFSRVoice, LFSR | synthesis (noise voice) | Noise Engineering AT Legio | midi note + bit depth → tuned maximal-LFSR noise voice (clock=f0·(2^b−1)) |
| `sound/synthesis/tzfm.py` | TZFMVoice, SteppedOscillator | synthesis (FM) | Korg Prologue Elixir TZFM/STEPr | note + depth/direction/ringmod/bitcrush → through-zero FM audio; per-note wave stepping |
| `sound/generators/polymetric_grid.py` | PolymetricGrid, Track, PerStepGraph | sequencing (polymetric) | Rapid Flow omniGRID | 16 tracks, per-track steps/resolution + 6 per-step graphs + shuffle → timed events/MIDI |
| `sound/generators/acid_seq.py` | AcidSequencer, AcidVoice | sequencing (acid) | BS-203 MacroAcidizer | scale-locked random pattern → 303/202-style rendered sequence audio |
|| `sound/generators/cadence_variator.py` | CadenceEngine, CadenceLayer, FluxRandomizer | sequencing (variation) | Emergence Audio Envoy Cadence Engine | 4-block lanes + flux randomizer + per-layer LFOs → rhythmic event streams |
|| `sound/generators/random_note_gen.py` | RandomNoteGenerator, NoteChanceSequencer | sequencing (generative) | NI Maschine 3.7 Random Note Gen + Note Event Chance | density+range+scale → MIDI note events; per-note prob re-roll each loop → active subset |
|| `sound/generators/euclidean_fill_seq.py` | EuclideanFillSequencer | sequencing (rhythm) | NI Maschine 3.7 Euclidean Sequencer | pulses+steps+fill_density+rotation → hit pattern w/ primary+fills → MIDI |
|| `sound/modular/random8.py` | Random8, RandomChannel | modular (random CV) | Befaco/Mylar Melodies RANDOM8 | 8 channels, 15 quantize scales, 8 styles → quantized random CV streams |
| `sound/synthesis/string_scales.py` | ArplusVoice, StringVoice | synthesis (strings) | Zlosynth Arplus | chord/scale pool + arpeggiation → plucked-string (KS) scale-quantized arps |
| `sound/modular/wandering.py` | WanderingEngine, Portal, DriftCloudsVoice | modular (drift) | Sound Dust Drift Clouds | nested non-LFO wander + Portal jumps → Cloud/Shadow layer balance drift |
| `sound/synthesis/air_pipe.py` | AirPipe, AirPipePatch | synthesis (physical, aerophone) | Modartt Airteq | pipe length + air pressure/mod → flue-pipe audio (open/stopped modes, overblow, MPE air) |
| `sound/effects/glitch_chopper.py` | GlitchChopper, ChannelChopper | effects (glitch) | GlitchShredder | stereo audio + bpm + glitch/reverse prob → transient-snapped 16-slot recombination |
| `sound/generators/harmony_writer.py` | HarmonyWriter | generators (harmony/arrangement) | HarmonyKeen | monophonic melody + key + style → rule-based harmony parts (phrase/cadence analysis, SATB voice-leading) |
| `sound/effects/orbit_sculptor.py` | OrbitalStereoSculptor, OrbitalBandProcessor, LinkwitzRiley4Crossover | effects (spatial/modulation) | SoundGhost Orbit | audio + 3-band LR4 crossover + per-band pan/width/gain modulators → sculpted stereo audio |
| `sound/effects/delta_sigma_saturator.py` | DeltaSigmaSaturator, DeltaSigmaStage, SlewLimiter, ReconstructionFilter | effects (distortion/saturation) | Mixland Grey Matter, PS1 DAC | audio + drive + strain + mode (clean/console/broken) → DAC-saturated audio |
| `sound/effects/multiband_saturator.py` | MultibandSaturator, BandConfig | effects (saturation/distortion) | Kreuzberg Audio Oberton | audio + 6 LR4-split bands + per-band algo (15 types) + M/S mode + global trim → saturated stereo audio |
| `sound/sync/clock.py` | DAWClockBridge | sync | MTC/MIDI clock | bpm → clock pulses |
| `sound/render/fluidsynth.py` | FluidSynthRenderer | render | SF2 synth | MIDI → WAV |
| `sound/render/vst.py` | VSTRenderer | render | DAW VST3 | MIDI → VST audio |
| `sound/render/pipeline.py` | RenderPipeline | render | export chain | MIDI → WAV/OGG/stems |

## 2. Categories at a glance

| Category | Purpose | Key files |
|---|---|---|
| **synthesis/** | create audio from scratch | phase_mod, modal, granular, vocal, additive, bowed, mass_spring, polysynth, west_coast, mono_synth, dx7_voice, equation_synth, drum_synth_606, spectral_wavetable, memorymoog_synth, supersaw_swarm, formant_voice |
| **effects/** | transform existing audio | filter, reverb, fdn_reverb, vowel_filter, tape_delay, multiband, quantize_mod, mastering, production_chain, spectral_gate, tilt_eq, liminal_reverb, scale_locked_granular, overlap_comp, room_reverb, bbd_chorus, shimmer_reverb, subharmonic |
| **modular/** | node-graph DSP | graph, math_mod, patch_loader |
| **generators/** | generative event/pattern engines | event_core, dice, ratchet_seq, complex_noise, micro_timing_seq, trig_cond_seq, param_lock_seq, sample_slicer |
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
