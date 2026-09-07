# Sound Production Methods Registry

Catalog of researched sound production methods (SP-xxx). The Hermes agent's
production pipeline picks from this registry. Keep one entry per method;
update status when implementation lands in `sound/`.

Status: `implemented` = in sound/ package · `partial` = some pieces exist · `research` = documented only

## Synthesis Engines

| ID | Method | Status | Location |
|----|--------|--------|----------|
| SP-010 | FM Synthesizer Voicing | partial | sound/synthesis/phase_mod.py |
| SP-013 | Aperiodic Granular Synthesis | implemented | sound/synthesis/granular.py |
| SP-022 | Wave Terrain Synthesis (WTS) | research | — (2D terrain scan) |
| SP-032 | FDTD Physical Modeling | research | — (see methods KB; distinct from SP-003) |
| SP-003 | Modal Physical Modeling (Plate/Bar) | implemented | sound/synthesis/modal.py |
| SP-024 | Bowed String Physical Modeling (Friction Waveguide) | implemented | sound/synthesis/bowed.py |
| — | Mass-Spring Physical Modeling (ANUKARI-style) | implemented | sound/synthesis/mass_spring.py |
| — | Modular Node-Graph DSP (SynthEdit-style) | implemented | sound/modular/graph.py |
| — | Math Modulators + 24-step Sequencer (Altitude-style) | implemented | sound/modular/math_mod.py |
| — | Digital Chaos CV (Sofia2 / Leibniz-style) | implemented | sound/modular/chaos_cv.py |
| — | JSON Patch Loader/Builder (Karst-style) | implemented | sound/modular/patch_loader.py |
| — | Scale Quantizer + Probability Engine (Synterra-style) | implemented | sound/synthesis/scale_quantizer.py |
| — | Voice Allocator + Modulation Matrix (ECHON-6-style) | implemented | sound/synthesis/voice_allocator.py |
| — | Polyrhythmic Arpeggiator (Memory-V-style) | implemented | sound/synthesis/polyrhythm.py |
| — | Binaural / Haas / Play Modes (DMNO-style) | implemented | sound/synthesis/binaural.py |
| — | West Coast Wavefolder + LPG (Obsidian-style) | implemented | sound/synthesis/west_coast.py |
| — | FDN Reverb (Rev-Ocean-style) | implemented | sound/effects/fdn_reverb.py |
| — | Multiband Compressor + Synth (Rumble-style) | implemented | sound/effects/multiband.py |
| — | Quantize Modulators + Routing (Radical1-style) | implemented | sound/effects/quantize_mod.py |
| — | Dice Variation + Param Scopes (Karst-style) | implemented | sound/generators/dice.py |
| — | Microtonal MIDI Export (KHÔRA-style) | implemented | sound/utils/midi.py |
| — | Just Intonation / Microtonal (KHÔRA-style) | implemented | sound/tuning/just_intonation.py |
| — | Polyphonic Multi-Engine (Astrolab-style) | implemented | sound/synthesis/polysynth.py |
| SP-004 | Formant Vocal Synthesis | implemented | sound/synthesis/vocal.py |
| — | Additive Synthesis (SoundWave) | implemented | sound/synthesis/additive.py |
| — | Mono Subtractive Synth (AD-202 / MC-202-style) | implemented | sound/synthesis/mono_synth.py |
| — | DX7 Voice Format Parser (Rithmatic-style) | implemented | sound/synthesis/dx7_voice.py |
| — | Equation→Waveform Synthesis (MathSynth-style) | implemented | sound/synthesis/equation_synth.py |
| — | Stacked-Oscillator Memorymoog-Style Voice (Memorymode 2-style) | implemented | sound/synthesis/memorymoog_synth.py |
| SP-033 | Detuned Saw Swarm + Harmony Engine + Morph Pad (SuperStarSaw-style) | implemented | sound/synthesis/supersaw_swarm.py |
| — | Scale/Chord-Pitch Quantizer (SuperStarSaw harmony engine) | implemented | sound/synthesis/supersaw_swarm.py (SCALES/CHORDS + quantize) |

## Interval-Based Composition (NEW)

| Method | Status | Location |
|--------|--------|----------|
| Forte Interval-Class Vectors (Set Theory) | implemented | structures/intervals.py |
| Hindemith Series 2 Harmonic Fluctuation | implemented | structures/intervals.py |
| Bartók Interval Expansion/Contraction | implemented | structures/intervals.py |
| Delta Encoding (Transposition-Invariant) | implemented | structures/intervals.py |
| Interval Markov Chain | implemented | generators/interval_chain.py |
| Interval L-System (Fractal Melodies) | implemented | generators/interval_lsystem.py |
| Just-Intonation Ratio Lattice | implemented | sound/tuning/ratio_lattice.py |

## Post-Processing / DSP

| ID | Method | Status | Location |
|----|--------|--------|----------|
| SP-001 | Multi-timbral SoundFont (SF2) | implemented | sound/render/fluidsynth.py |
| SP-002 | VST3 Polyphonic Stacking | implemented | sound/render/vst.py |
| SP-005 | Headless DAW/MTC Sync | implemented | sound/sync/clock.py |
| SP-006 | Zero-Drift Humanization | implemented | workflows/unitmatrix_composer.py |
| SP-007 | Spectral Masking EQ | partial | sound/effects/filter.py (DynamicEQ) |
| SP-008 | Dynamic Range Compression (DRC) | partial | sound/effects/mastering.py (Limiter) |
| SP-009 | Convolutive Reverberation | implemented | sound/effects/reverb.py (algorithmic) |
| SP-021 | Binaural Woodworth-Schlosberg Spatialization | research | — (HRTF ITD/ILD) |
| — | Vowel Filter Bank (Vowel-Blender-style) | implemented | sound/effects/vowel_filter.py |
| — | Tape Delay / Sample Player / Drum Machine (VST-Classics-style) | implemented | sound/effects/tape_delay.py |
| — | Rhythmic Spectral Gate (Spectdrum-style) | implemented | sound/effects/spectral_gate.py |
| — | Tilt EQ (Triton Tilt EQ-style) | implemented | sound/effects/tilt_eq.py |
| — | Gated-Decay Reverb + Shimmer (Liminal Space 2-style) | partial | sound/effects/liminal_reverb.py |
| — | Scale-Locked Granular FX (Lucid-style) | implemented | sound/effects/scale_locked_granular.py |
| SP-034 | BBD Chorus Ensemble (Thorus XT-style) | implemented | sound/effects/bbd_chorus.py |
| SP-035 | Fractional-Pitch Shimmer Reverb (3rd Wave Shimmer Verb-style) | implemented | sound/effects/shimmer_reverb.py |
| — | Overlapping-Band Parametric Compressor (Parish Audio-style) | implemented | sound/effects/overlap_comp.py |
| — | Micro-Timing Shift Sequencer (miniGRID-style) | implemented | sound/generators/micro_timing_seq.py |
| — | Trig-Condition Sequencer (Volca Drum alt-firmware-style) | implemented | sound/generators/trig_cond_seq.py |
| — | 606-Style Drum Synthesis Engine (Super 606-style) | implemented | sound/synthesis/drum_synth_606.py |
| — | Spectral Wavetable Extraction (3rd Wave Make Waves-style) | implemented | sound/synthesis/spectral_wavetable.py |
| — | Room Reverb with Slap/Wash/Tilt (bathROOMs-style) | implemented | sound/effects/room_reverb.py |
| — | Param-Lock Sequencer with Ratchet+Randomize (Asterism-style) | implemented | sound/generators/param_lock_seq.py |
| — | Auto Tempo/Pitch Detection + Sample Slicer (Bitwig 6.1 Sampler-style) | implemented | sound/generators/sample_slicer.py |

| SP-036 | Klatt-Cascade Formant Voice / Speech Synthesis (klattsch-style) | implemented | sound/synthesis/formant_voice.py |
| SP-037 | Pitch-Tracked 3-Band Sub-Harmonic Generator (Penteo 8 Synthesized LFE-style) | implemented | sound/effects/subharmonic.py |

## Mastering (from MusicTech workflow)

| Method | Status | Location |
|--------|--------|----------|
| LUFS Metering (ITU-R BS.1770-4) | implemented | sound/effects/mastering.py |
| Dynamic EQ (resonance control) | implemented | sound/effects/mastering.py |
| Stereo Imaging (mono-safe) | implemented | sound/effects/mastering.py |
| Peak Limiter | implemented | sound/effects/mastering.py |

## Generative Event Cores (Karst-style)

| Core | Status | Location |
|------|--------|----------|
| MarkovCore | implemented | sound/generators/event_core.py |
| StochasticCore (tendency mask) | implemented | sound/generators/event_core.py |
| EuclideanCore (Bjorklund) | implemented | sound/generators/event_core.py |
| LSystemCore | implemented | sound/generators/event_core.py |
| WeightedRandomCore | implemented | sound/generators/event_core.py |
| — | Ratchet Sequencer (SuperOS-808-style) | implemented | sound/generators/ratchet_seq.py |
| — | Complex Noise Generator (Q210-style) | implemented | sound/generators/complex_noise.py |
| — | Trig-Condition Sequencer (Volca Drum alt-firmware-style) | implemented | sound/generators/trig_cond_seq.py |

## Planned (from surveillance, see surveillance.md)

| Method | Priority | Notes |
|--------|----------|-------|
| Spectral processing (STFT + demucs) | medium | effects/spectral.py planned |
| Mass-spring physical modeling | low | synthesis/physical.py, JAX optional |
| Guitar Pro / tab export | future | transcription pipeline |
| Flat.io integration | future | integrations/flat_io.py |
| Liminal Space 2 full algorithm library | low | liminal_reverb.py has gated decay + shimmer; 4,636 profiled algorithms + per-tap DLFO need parameter-scan framework |
| Monochord chord library / strum | low | chord voicing engine needs hand-voiced chord data or algorithmic voicing generator |
| Instrument X neural orchestral modeling | low | proprietary neural nets + dodecahedral IR captures; articulation-by-pitch/length routing could be approximated with voice_allocator + bowed.py |
