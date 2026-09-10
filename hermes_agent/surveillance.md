# Music-Tech Surveillance Findings

Replicability analyses from the Hermes agent's music-tech surveillance cron
(job e2760579d2c8, runs Mon/Thu). Distilled verdicts for musicom adoption.

> **SP-ID note (2026-09-10):** `docs/methods.md` (the absolute-layer catalog)
> already occupies **SP-038 … SP-068**. Tracking doc `methods-registry.md` and
> `SP_METHODS` had a lower max (SP-037), which under-counts the true next free
> ID. As of 2026-09-10 the ID space is unified: **next free SP-ID = global max
> across `SP_METHODS` ∪ `methods-registry.md` ∪ `docs/methods.md`, +1**
> (= **SP-069** at this scan).

## 2026-09-10 Scan

| Item | Technique | Verdict | Musicom path |
|------|-----------|---------|--------------|
| Teaching Machines FuzzBillion (SoS Sept 2026) | 11 numerical switches (10 positions each) selecting discrete diode/amplifier elements (germanium, silicon, LED, transformer, JFET, tube, CMOS, op-amp) in series + gain knob → 10^11 circuit variations; switchable instrument/line-level I/O | YES | **DONE** — sound/effects/topology_distortion.py (SP-069: `FuzzBillion`, 10 nonlinear element transfer functions incl. exact antiparallel-diode `Vk·asinh(x/Vk)` with 0.30/0.65/1.80 V knees, 11-stage serial chain, `circuit_count()==10**11`, spectral-centroid element profiling, inst/line I/O trims); hardware enclosure/measured component selection not replicated |
| ZERO9 Fusion Filter (MusicTech 2026-09-08) | Five different filter characters in one workflow, filtered *between* engines via morph while sharing one amount/resonance/mix control set | YES | **DONE** — sound/effects/morph_filter.py (SP-070: `FusionFilter`, five real topologies — saturating 4-pole ladder, asymmetric diode ladder, ZDF/trapezoidal SVF, resonant damped comb, folded "scream" ladder — equal-power continuous morph across all five, shared cutoff/res/drive/mix, self-oscillation-stable); plug-in UI/coefficient tables not replicated |
| ZERO9 Severed Space / Eccentric Echo / Fractured Frequency / Crushing Compressor (MusicTech 2026-09-08) | Gated reverb with onset-triggered closure + spectral declashing + analogue movement; dual delay engines (continuous + granular) feeding each other with serial/parallel routing, echo, splice, pitch; four-stage tempo-locked glitch chain; 4-band upward+downward parallel compression | YES | **DONE** — sound/effects/severance.py (SP-071: `GatedReverb` (comb+allpass tail, onset gate env, `spectral_declash` STFT per-bin magnitude limiter, LFO movement), `DualEngineDelay` (interpolated continuous line + windowed granular grains, serial/parallel coupling, per-engine pitch + splice hop, feedback), `RhythmicGlitchChain` (4 tempo-locked stages gated by 16th patterns), `ParallelBandCompressor` (complementary 4-band split, per-band upward lift + downward squash, parallel mix)); plug-in UIs/parameter curves not replicated |
| Crow Hill Brackish Pads (SoS Sept 2026, 5/5) | Three sampled partials per patch (Basic / Complex / dedicated stochastic "Critters" partial) balanced by sliders; unstable pitch-wobble + microtonal shift identity; four Pump Triggers bound to envelopes + compressor; Cassette lo-fi wear and Splosh reverb | YES | **DONE** — sound/synthesis/critter_pad.py (SP-072: `PadPartialBank` 3-layer balance, `Partial` detuned-wave layer with random-walk pitch wobble, `Critters` Poisson-triggered detuned clusters with `MICROTONAL_SETS` quarter/eighth-tone + drift, `pump_envelope` 4 shapes, `cassette` (wow/flutter + head-loss LPF + hiss + asymmetric squash), `splosh` (sparse early reflections + short comb tail)); 1.25 GB sampled patch sets not replicated |
| Muro Box N40 — MIDI music box, "Sublime" twin-comb edition (Synthtopia 2026-09-08) | Steel-tine music box with pickup + audio out; the flagship edition fits **two combs detuned by 14 cents** for chorus; chromatic notes over an expanded range | YES | **DONE** — sound/synthesis/music_box.py (SP-073: `MusicBoxComb` modal tine bank with the free-free bar ratios (1, 6.2669, 17.547, 34.3863), per-mode decay, pluck click, magnetic-pickup colouration; `TwinCombMusicBox` two combs with independent `detune_cents` (default `DEFAULT_DETUNE_CENTS=14.0`), per-note tuning jitter, mechanics noise, stereo comb placement, chromatic `midi_to_freq` map, `render_melody`); brass/acacia build + pin-drum mechanism + action latency not replicated |
| Erica Synths Bullfrog Drums (SoS Sept 2026) | Eight channels — seven identical sample tracks (pitch, decay, start, end, loop point, DJ-style LP/HP filter, resonance, overdrive, pan) plus one **CV sequencing** channel; X0X-style 64-step sequencer; kits and patterns loaded separately; user-replaceable samples | YES | **DONE** — sound/generators/drum_machine.py (SP-074: `SampleChannel` full Bullfrog parameter set with trim/loop/resample/filter/overdrive/pan/stereo, `CVChannel` emitting normalised → volt → pitch sequences for an external synth, `X0X_STEPS=64` 64-step grid with swing, per-step velocity and flam/ratchet, `Kit` kit/pattern split, `synthesize_drum_samples` factory kit, `pattern_to_midi_events` export); enclosure, USB sample drive and built-in mic not replicated |
| XILS-lab MemoryTone (Synthtopia/SoS 2026-09-09) | Software recreation of the 1982 Memorymoog, claims to model **interactions** between oscillators, voice variation, mixer-level-dependent drive and filter behaviour; 3 osc/voice + 24 dB ladder + osc-3 LF mode | PARTIAL (no new code) | Covered by sound/synthesis/memorymoog_synth.py (SP-…, Memorymode 2 scan 2026-08-31): 3-osc stack, whole-tone detune, 4-pole saturating ladder. MemoryTone's per-voice interaction/drift modelling and MPE per-note brightness = incremental refinement, not a new method; arpeggiator + 6 FX + preset manager are UI/content |
| Yamaha TX7 Patch Editor & Librarian (Synthtopia 2026-09-06) | Browser tool: reads TX7 voices, saves full libraries, loads DX7 SysEx banks, visual 6-operator FM editing, per-sound send | PARTIAL (no new code) | DX7 SysEx parsing already **DONE** — sound/synthesis/dx7_voice.py (`parse_dx7_packed/expanded`). Web MIDI transport + browser UI = host/hardware concern |
| Vintage Emulator Studio (VES) (Synthtopia 2026-09-06) | Free open-source host that runs MAME **machine emulations** of vintage synths/samplers/drum machines — reproduces original firmware execution, device logic and peripherals rather than re-creating the DSP; ROMs supplied separately | NO | Full-system machine emulation + user-supplied ROMs + GUI host; not a sound-production method (and cannot be replicated without the ROM content) |
| ZERO9 Cosmic Chorus (MusicTech 2026-09-08) | Two fixed chorus voicings, free vibrato, extra LFOs, tempo-synced undulation | PARTIAL (no new code) | Covered by sound/effects/bbd_chorus.py (SP-034) and sound/effects/tape_delay.py (multitap chorus/vibrato + fractional-delay modulation) — no new DSP class |
| ZERO9 Reactive Reverb (MusicTech 2026-09-08) | Input-reactive algorithm that reshapes itself from the source material | PARTIAL | Envelope-following reverb is covered structurally by `GatedReverb` (SP-071, onset-triggered closure) + sound/effects/fdn_reverb.py; the proprietary "reactive" mapping curve was not faked |
| TONE3000 free NAM plugin (MusicTech 2026-09-08) | Zero-cost plugin for browsing/loading thousands of Neural Amp Modeler captures + IRs with chain configuration | PARTIAL | Neural amp capture inference needs trained NAM models + a real-time/IR convolution host; closest existing module is sound/effects/production_chain.py (IR/convolve stages). Model inference stack not replicated — no new code |
| MixWave Spiritbox: Courtney LaPlante (MusicTech 2026-09-08) | All-in-one vocal chain: pitch + **formant** processing, distortion, compression, modulation width, 3-algorithm reverb, multi-mode delay, line-amp colour, freely reorderable chain | PARTIAL | Every module exists (sound/synthesis/formant_voice.py SP-036, sound/effects/filter.py, multiband.py, reverb.py, tape_delay.py, production_chain.py for reordering) — this is an artist-preset pack, not a new method; no new code |
| Cradle State Machine "Alt Textures" / Sauceware Audio Scorch 2 (MusicTech/SoS) | Alt Textures = multisampled texture library; Scorch 2 = dual-source sample instrument with a central Chaos knob modulating nearly every parameter, Bite/Space/Motion macros, sampler page (LP/HP series-or-parallel, ADSR, unison), tape echo + 3 reverbs + wow/flutter, 3-track scale-snapped MIDI generator, curated-source Randomize | PARTIAL | Scorch 2's *base sound* is curated multi-synth sample content (Oberheim TEO-5/OB-X, Memorymoog, Moog One, Trigon-6, Prophet-10, Juno 106, Rhodes Chroma) — content, not algorithm. The **Chaos macro** (one knob → many destinations) and **scale-snapped 3-track melody/chord/bass generator** are algorithmic and could be a future module; today they're approximated by sound/modular/math_mod.py (mod routing) + sound/synthesis/scale_quantizer.py, so no new code this scan |
| Soundcraft Signature Plus series (MusicTech) | Analogue mixing consoles (12/16/22/30) with signature sound + USB interface | NO | Analogue console hardware |
| Tracktion Waveform 14 Pro / Logic Pro 12.3 (MusicTech) | DAW releases: Live Loops non-linear pattern sequencing, Session Players performance generation, stem separation, AI assistant (API key) | PARTIAL (DAW-level) | Stem separation + performance generation concept overlaps the planned `sound/transcription/separation.py` (demucs) and workflows/ paradigm selection; DAW hosts are out of scope for the absolute layer — no new code |
| Korg Nu:Tekt NTS-4 / Sony WH-1000XM4C trio / Denon Prime 4 G2 / Soundcraft mixers / AlphaTheta XDJ-AN / Sennheiser Momentum 5 / Novation FLkey 37 / Palmer Orbit 11 / HeadRush FRFR Cabs / Warm Audio Jude / DPA 6388 / TELEGRAPHER monitors / Julian Michael Plugin Station / Arvital Audio AudioRoute / Blackbox HG-Q / SSL Odyssey / Celemony Tonalic bass / Crow Hill… hardware+utility | Mixers, headphones, DJ systems, mics, monitors, plug-in managers, system-audio capture, valve EQ, digitally controlled analogue console, session-musician content, plugin-management utility | NO | Hardware, hosting/utility software, or licensed content — not replicable DSP |

## 2026-09-07 Scan

| Item | Technique | Verdict | Musicom path |
|------|-----------|---------|--------------|
| klattsch (retro vocal synthesizer, Synthtopia 09-03) | 1980 Klatt formant-synthesis design: chain of oscillators + noise + resonators, no samples, per-phone editable parameters, text/piano-roll input with hand-drawn pitch curves, multi-voice layering | YES | **DONE** — sound/synthesis/formant_voice.py (SP-036: `FormantVoiceSynth`, 40+ phone inventory incl. Japanese kana vowels, text_to_phones front end, per-phone pitch curve + vibrato) |
| Penteo 8 (upmix/downmix v8, SoS 09-03) | Synthesized LFE Sub-Harmonic Generator across three independently mute-able/link-able frequency bands; plus phaseless-decorrelation upmix, 62-format ITU downmix | PARTIAL | Sub-harmonic core **DONE** — sound/effects/subharmonic.py (SP-037: pitch-tracked 3-band sub-octave synthesis, envelope-followed, add-fifth/sub-sub modes); full upmix decorrelation suite + ITU downmix = proprietary, not replicated |
| Groove Synthesis 3rd Wave OS 2.0a (SoS 08-25) | Shimmer Verb + Make Waves third "Spectral" wavetable mode (frequency-domain slice picking for wandering-pitch sources); MIDI CC/SysEx expansion | YES (partial new) | Shimmer + Make Waves Spectral already **DONE** 09-03 (sound/effects/shimmer_reverb.py, sound/synthesis/spectral_wavetable.py) — no new code (repeat of 08-27/09-03 finding) |
| Arturia Pure SUB (MusicTech, ~08-28) | Sub/harmonics/texture three-way split bass synth, 40+ filter modes, Sub Processor distortion chain, 12-slot FX rack, preset randomiser + resampler | PARTIAL | Covered by sound/synthesis/mono_synth.py (sub osc + ladder + drive) + sound/effects/production_chain.py — no new code (repeat of 09-03 finding) |
| Dreamtonics Instrument X (MusicTech + Synthtopia 08-31) | Neural Acoustics Modeling: notation → soundwaves via neural nets, breath/bow-friction dynamics, 3D Sound-Field Control (spot/Decca Tree/ambient mics) | PARTIAL | Proprietary neural nets + multi-channel IR captures; voice_allocator.py + bowed.py approximate routing — no new code (repeat of 08-27/08-31/09-03 finding) |
| Akai S900 SuperOS v4.0 (Synthtopia 09-03) | Custom firmware: S950/S1000 features, new MIDI control, TIMESTRETCH, real-time filter modulation | PARTIAL | Time-stretch covered by sound/effects/phase_vocoder.py; per-note filter modulation ≈ sound/synthesis/voice_allocator.py mod matrix; firmware + sample playback engine = hardware, not replicated — no new code |
| BS-203 MacroAcidizer (SoS 09-06) | TB-303/MC-202 emulation (3 modes: 303, 202, Bassboy) + scale-locked Acid Sequencer with randomize + saturation/delay/reverb FX | PARTIAL | 303-style voice covered by sound/synthesis/mono_synth.py; MC-202-style AD-202 already in sound/synthesis (mono_synth); scale-locked random sequencer ≈ sound/generators/param_lock_seq.py + scale_quantizer.py — no new code |
| Electric Cow EC909 (Synthtopia 09-04) | 1998 Atari ST virtual TR-909 + TB-303: PCM 909 drums (editable pitch/attack) + 303 synth in one, pattern → MIDI/AIFF export | PARTIAL | 909 drum synthesis covered by sound/synthesis/drum_synth_606.py family + ratchet_seq.py; PCM sample playback + 1998 Atari UI = not replicated — no new code |
| Elektron Tonverk OS 1.40 (Synthtopia 09-03) | OS update in-depth demo: per-track mod routing, Overbridge multitrack streaming | NO | DAW/host integration (repeat of 09-03 finding); per-track mod routing ≈ voice_allocator.py — no new code |
| Korg Prologue Elixir user oscillators (Synthtopia 09-03) | 3 custom multi-engine osc + 5 wavetable osc: DXOSC FM (25 algos, mod gen with 24 LFO shapes), TZFM dual-waveform (90 shapes, ringmod/bitcrush, A↔B FM), STEPr (per-note waveform stepping) | PARTIAL | FM covered by sound/synthesis/phase_mod.py; dual-waveform morph + bitcrush ≈ sound/synthesis/supersaw_swarm.py harmony + equation_synth.py; STEPr per-note stepping is a sequencing idea ≈ param_lock_seq.py — no new code |
| SOMA Enigma (SoS 08-26) | Metal-object proximity scanner (0-20 mm) controls freeform sonic landscape; any metal object = control surface | NO | Hardware sensor instrument (repeat of 08-27 finding) — not replicable DSP |
| LeWitt Space Replicator Free (SoS 09-02) | Headphone virtual mixing room: 800+ headphone compensation profiles + room/consumer-speaker/earbud emulation | NO | Proprietary measured IR/compensation dataset (repeat of 09-03 finding) |
| e-instruments Velvet Guitars Fragment (SoS 09-04) | Free Kontakt baritone-guitar instrument: sustains/mutes/dead notes/legato + 2 vintage amps + spring reverb + 60s tremolo | NO | Sample-library content, not algorithm |
| Audacity 4 (MusicTech, ~09-05) | DAW refresh: overlapping/non-destructive clips, ripple editing, redesigned effects, real-time VST3/AU/LV2 hosting, Workspaces | NO | Host/DAW architecture, not replicable DSP |
| HeadRush FRFR Cab Series / Sony ULT Tower / Denon Prime 4 G2 / Polyend Keys / HEDD CTRL / IK Tonex Board / Keeley Tube Drive / Reason Free | Speakers/controllers/consoles/pedals | NO | Hardware / host / content (Polyend Keys + Reason Free repeat of 08-31 finding) |

## 2026-09-03 Scan

| Item | Technique | Verdict | Musicom path |
|------|-----------|---------|--------------|
| Native Instruments SuperStarSaw (A.G. Cook supersaw synth, MusicTech review) | Two independent "swarms" of 16 detuned saw oscillators (alternating detune ladder scaled by Spread); per-oscillator stereo pan + amplitude drift; harmony engine quantizing every oscillator pitch to a scale (incl. Super Locrian, Dorian #4, Hirajoshi) or a chord shape — wide spread over quantized pitches forms tense tone clusters; 2×2 XY Morph pad bilinearly blending four parameter snapshots | YES | **DONE** — sound/synthesis/supersaw_swarm.py (235-preset library, oscillator-distribution visualizer, unconstrained randomize = UI/content, not replicated) |
| UVI Thorus XT (chorus, SoS 2026-08-31) | Analogue-modelled BBD chorus engine: bucket-brigade clocked delay with per-voice LFO phase/rate variation, hiss injection, alias filtering (pre/post lowpass around the clock), compander encode/decode (expand-before-delay / inverse-gain-after, "pumping" on mismatch), morphable 1..8-voice shared architecture, clock-rate control | YES | **DONE** — sound/effects/bbd_chorus.py (pristine digital chorus engine + iLok = not replicated; clean multitap delay already in sound/effects/tape_delay.py) |
| Groove Synthesis 3rd Wave Shimmer Verb (OS 2.0a, SoS 2026-08-25) | Shimmer reverb with pitch shift in fractions of a semitone across ±2 octaves in the feedback loop: SOLA (resample + overlap-add) length-preserving pitch shifter on the recirculated tail, comb+allpass tank with energy-normalized recirculation so loop gain is exactly rev-time controlled, mod-matrix-style destinations (rev time / pitch amount / filter cutoff) + slow LFO wobble on live shift cents | YES | **DONE** — sound/effects/shimmer_reverb.py (Super Plate processor, hardware mod-matrix UI/SysEx, LP/HP dual cutoff = not replicated) |
| Arturia Pure SUB (sub-bass synth, MusicTech 09-03) | Dedicated sub-bass synth: sub/harmonics/texture split, 40+ filter modes, Sub Processor bass distortion chain, MPE/velocity | PARTIAL | Covered by sound/synthesis/mono_synth.py (sub osc + ladder + drive); 40 filter modes + preset randomiser/resampler = proprietary UI — no new code |
| Core Sampler (AAX sampler for Pro Tools, MusicTech 09-03) | One-shot sampler: drag audio, edit waveform, envelope/gain/fade/filter/pitch/velocity shaping, play from MIDI | PARTIAL | Covered by sound/generators/sample_slicer.py (oneshot play modes + pitch); AAX hosting + waveform editor UI = not replicable — no new code |
| Dreamtonics Instrument X (neural orchestra, SoS/Synthtopia 08-31) | Neural Acoustics: translates notation to soundwaves, articulation stack (col legno, mutes...), Dynamics Lane morphing timbre, AI performance retakes | PARTIAL | Proprietary neural nets; existing voice_allocator.py + bowed.py approximate routing — no new code (repeat of 08-27/08-31 finding) |
| Cherry Audio Memorymode 2 / Korg Volca hj firmware / Polyend Keys / Reason Free / Elektron Tonverk OS / IK Maestosa Strings | Already analyzed 08-27..08-31; Memorymode 2 & Volca Drum DSP already replicated | — | See 2026-08-31 and 2026-08-27 scan tables |
| Roland Aira firmware switcher (Synthtopia 09-01) | Experimental tool swapping firmware between Scooper/Demora/Torcido/Bitrazer (1-byte difference); AI-assisted reverse engineering | NO | Firmware bit-twiddling for specific hardware; no general DSP |
| Korg MS2000 Editor Librarian (Synthtopia 08-31) | Free browser Web MIDI patch editor/librarian for MS2000: SysEx bank load/save, program edit, randomisation | NO | Hardware SysEx librarian (Web MIDI + device-specific SysEx); not replicable DSP |
| LeWitt Space Replicator Free (SoS 09-02) | Headphone virtual mixing room: 800+ headphone compensation profiles + room/consumer-speaker/earbud emulation IRs | NO | Proprietary measured IR/compensation dataset — no new code |
| SOMA Enigma / Cradle Alt Textures / SuperStarSaw sample content | Hardware metal-scanner instrument / curated sample library content | NO | Not replicable DSP |

## 2026-08-31 Scan

| Item | Technique | Verdict | Musicom path |
|------|-----------|---------|--------------|
| Asterism (free WebAudio drum machine) | Param-lock step sequencing: per-step overrides of track base params (pitch/decay/cutoff/velocity), ratcheting (sub-division bursts), randomization with per-param freeze/unlock | YES | **DONE** — sound/generators/param_lock_seq.py (WebAudio engine + browser UI + pattern chains = host concerns, not replicated) |
| Cherry Audio Memorymode 2 (Memorymoog soft-synth) | Stacked 3-osc-per-voice analog voice with whole-tone detune cluster (osc locked ± major 2nd = 200 cents), per-osc saw/pulse/triangle mix, 4-pole lowpass + resonance, 3/6/9-voice doubling (voice-count thickening) | YES | **DONE** — sound/synthesis/memorymoog_synth.py (Curtis CEM3340 filter curve, LFO/S&H mod matrix, arpeggiator, preset library = not replicated) |
| Bitwig Studio 6.1 Sampler | Auto tempo (envelope autocorrelation → BPM) + auto pitch (waveform autocorrelation → fundamental) detection, spectral-flux onset detection → auto-slicing, play modes (oneshot/loop/reverse/pingpong) + per-slice rate (pitch), pad-style slice grid | YES | **DONE** — sound/generators/sample_slicer.py (phase-vocoder time-stretch warping, multisample editor, granular modes = proprietary, not replicated) |
| Arturia Pure Sub (sub-bass synth) | Sine/saw/square osc + sub-osc + lowpass + drive/saturation for hard-hitting modern bass | PARTIAL | Covered by sound/synthesis/mono_synth.py (sub osc + ladder filter + drive) — no new code |
| Ravine DSP Inter::State (chain host) | Plugin chain hosting with macro/parameter mapping across devices | PARTIAL | Covered by sound/modular/graph.py + sound/effects/production_chain.py — no new code |
| Dreamtonics Instrument X (physical-modeling orchestra) | Neural Acoustics physical modeling of orchestral strings/woodwinds/brass; articulation by pitch/length (no keyswitches) | PARTIAL | Proprietary neural nets (see 08-27 note); voice_allocator.py + bowed.py approximate routing — no new code |
| CEDAR Voxis (voice isolation) | Sub-10ms low-latency voice isolation for live use | PARTIAL | Proprietary ML voice isolation; needs demucs-style source-separation models — no new code |
| StemDeck (open-source stem separator) | ML stem separation (vocals/drums/bass/piano/guitar) via open-source models | PARTIAL | Needs trained separation models (demucs etc.) — no new code; see planned sound/transcription/separation.py |
| Love Synths First Love (FM synth, pre-order) | User-friendly FM architecture; wave morphing + FM + microtonal tuning | PARTIAL | FM covered by sound/synthesis/phase_mod.py + west_coast.py — hardware engine + UI not replicated |
| IK Multimedia Sinphonica Maestosa Strings | Italian orchestral virtual instrument (sample-based strings) | NO | Sample-library content, not algorithm |
| Reason Studios Reason Free | Free Reason Rack + 15 bundled instruments | NO | Content/business model, not DSP |
| SSL O-Series V2.0 / Elektron Tonverk OS update | Console software / Overbridge multitrack streaming + per-track mod routing | NO | DAW/host integration, not replicable DSP (Tonverk's per-track modulation routing ≈ existing sound/synthesis/voice_allocator.py + math_mod.py) |
| Polyend Keys / Patternflow / Interaktiv Tap | QWERTY music keyboard / OSC light synth controller / iPad Traktor surface | NO | Hardware/controller surfaces |

## 2026-08-27 Scan

| Item | Technique | Verdict | Musicom path |
|------|-----------|---------|--------------|
| Korg Volca Drum alt firmware "hj Firmware" (trig conditions) | Elektron-style trig conditions (A-B, first, last, every-N, FILL, discrete 50/62/75/87% probs), negative accent → ghost notes, negative swing, SLICE sub-step patterns | YES | **DONE** — sound/generators/trig_cond_seq.py (FUNC+knob editing / TOUCH FX pads = hardware UI, not replicated) |
| AudioKit Pro Super 606 (synth drum machine) | 606-style drum synthesis engine: pitch-swept sine kick (+XL mode), tonal body + bandpassed-noise snare, pitch-swept toms, multi-burst noise clap, XOR'd square+noise metallic hats; 606 sequencing: flams (9 types + ahead-of-beat), ratchets, ghost notes, swing | YES | **DONE** — sound/synthesis/drum_synth_606.py (AUv3/Ableton Link/MIDI import/WAV export = host concerns; Magic Pattern Generator/Smart Fills heuristics not replicated) |
| Groove Synthesis 3rd Wave OS 2.0a (Make Waves Spectral mode) | Spectral wavetable extraction: STFT the source, score frames by harmonic cleanness, pick best slices spread across the file, phase-align cycles → wavetable; plus fractional-semitone Shimmer reverb | YES | **DONE** — sound/synthesis/spectral_wavetable.py (hardware UI + Pitch-On/Pitch-Off modes not replicated; shimmer already in sound/effects/liminal_reverb.py) |
| Hot Shower Audio bathROOMs (free reverb) | Small-room reverb: early-reflection tapped delays (position/surface), independent slap feedback loop, wash balance vs Schroeder diffuse tail, temp tilt (bright/warm) | YES | **DONE** — sound/effects/room_reverb.py (5 modeled bathroom IRs + sidechain ducker + A/B UI not replicated) |
| Liminal Space 2 (reverb, v2 release) | 4,636 profiled algorithms, gated/collapse decays, shimmer, per-tap DLFO, LEXITONE shaping | PARTIAL | sound/effects/liminal_reverb.py (already covers gated decay + shimmer + LEXITONE; algorithm library + DLFO need parameter-scan framework) — no new code |
| Dreamtonics Instrument X (physical-modeling orchestra) | Neural Acoustics Modeling platform; articulation switching by pitch/length (no keyswitches); scoring-stage response captured via dodecahedral speaker array; Dynamics Lane auto-mapping | PARTIAL | Needs proprietary neural nets + multi-channel IR captures — no new code (see planned) |
| SOMA Laboratory Enigma (hardware) | Metal-object proximity scanner (0–20 mm) controls sonic landscape; object shape/size/type → sound | NO | Hardware sensor + proprietary mapping; no replicable DSP |
| Groove Synthesis 3rd Wave Shimmer Verb | Fractional-semitone pitch shift (−1..+2 oct) in reverb feedback, mod-matrix routable Rev Time/Pitch/Cutoff | PARTIAL | Covered by sound/effects/liminal_reverb.py shimmer; fractional detune + mod-matrix routing could extend it — no new code |

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
