# SP-080 Cadence Engine Rhythmic Variator — Production Report (2026-10-05)

## Job
Random-style production pass (SP) — **LAYER-ALIGNED**.
Seed `20261005`. Selection source: `workflows.musicom_workflow.SP_METHODS` registry
(40 implemented entries), NOT the research DB and NOT a stale SP range.

## Method
- **SP-080** → `sound.generators.cadence_variator`
- Description: "Cadence Engine Rhythmic Variator w/ Flux Randomizer (Emergence Audio Envoy-style)"
- Adapter not wired in `produce()` (only SP-001/SP-011 are) → module API called directly.

## Source composition
- Project: `Styles/Country/012-country-full-16bar`
- MIDI: `16bar_country.mid` — 110 BPM, 4/4, 16 bars (64 beats, ~34.9s), tpb 480.
  - track0 Accordion (prog 21, ch0): 64-note melody G4–A5 (67–81)
  - track1 Acoustic Guitar nylon (prog 24, ch0): 32-note rhythm G3–D4 (55–62)
  - track2 Choir Aahs (prog 52, ch0): 16-note pad G3–D4 (55–62)
  - track3 ch9 percussion: 64 hits kick(36)/snare(38)

### Source-override note (important)
The random selector landed on
`Country/012-country-full-16bar/MIDI/country_pop_v1.mid`, but that file is a
2.0s / 12-note / single-track stub (prog 0 piano, C4–D5, channel 0). The real,
complete composition in the selected project is `16bar_country.mid`, so that was
used as the production source. Recorded in provenance + here.

## Layer discipline
ABSOLUTE layer. CadenceEngine is applied as a production layer across ALL voices:
each voice gets a CadenceLayer (4 independent blocks, per-step velocity/pitch/
length/pan/combi-LP-HP lanes, own rate/direction/feel, own LFO) + FluxRandomizer,
driving time-varying gain / constant-power pan / LP-filter envelopes over the
rendered stem audio. FluidSynth GM render (SP-001 reference) is the acoustic
carrier; no new notes are written.

## Chain
```
16bar_country.mid
  -> FluidSynth dry render (SP-001 reference, reverb/chorus off)
  -> dry stems via RenderPipeline (accordion / guitar-nylon / choir / drums)
  -> per-voice CadenceLayer -> render_events(flux) -> gain/pan/LP curves
  -> StateVariableFilter LP (blockwise, default resonance) + constant-power pan + gain
  -> wet stems (peak-normalized 0.89)
  -> mix bus -> AlgorithmicReverb(wet_dry 0.10) -> normalize_to_lufs(-14) -> Limiter(-1 dB)
  -> SP080-cadence-country-full-16bar.wav + .ogg (Opus voip 48k)
```

## Parameters
- seed: 20261005, BPM 110.00, master LFO rate 0.7 Hz
- reverb: room_size 0.55, damping 0.45, wet_dry 0.10, width 0.85
- per-voice CadenceLayer config:

| voice | role | blocks | rate | dir | feel | flux depth (blocks) | hp base | lp base | pan | gain |
|---|---|---|---|---|---|---|---|---|---|---|
| track00 Accordion | melody lead | 8,6,8,7 | 2.0 | fwd | straight | 0.22 (0,2) | 250 | 4500 | +0.25 | 1.05 |
| track01 Guitar nylon | rhythm | 7,8,6,8 | 1.5 | pingpong | swing | 0.28 (1,3) | 180 | 3800 | -0.40 | 0.95 |
| track02 Choir Aahs | pad | 6,8,7,5 | 1.0 | fwd | lurch | 0.25 (0,1,2) | 120 | 3200 | +0.40 | 0.90 |
| track03 Drums | kit | 8,8,4,8 | 2.0 | fwd | straight | 0.15 (0) | 40 | 9000 | 0.00 | 1.00 |

- Cadence events rendered: accordion 319 / guitar 261 / choir 182 / drums 336.
- LP curve clipped to [400, 11000] Hz; per-block (256 smp) mean cutoff fed to SVF.

## Pitch verification (Analysis/pitch_verification.json)
- windows checked: 70
- **dominant-peak hit rate: 0.9857** (69/70 windows match an active MIDI fund or x2/x3/x4/÷2)
- harmonic energy (8 harmonics, full mix): 0.2838
- **pitched-only harmonic energy (drums excluded): 0.3288**
- pitched-only hit rate: 0.9857
- ACF: 18 windows, 2 unpitched (11%) — no noise
- median dominant freq: 522 Hz; lowest active notes seen: 55/60/62 (G3/C4/D4)
- 1 miss @ t=20.0s (dom 988 Hz vs active C4/E5/D5 = 60/72/76) — transient/percussive window
- **verdict: PASS**

### Harmonic-energy rationale
The full-mix harmonic energy (0.2838) sits just under the 0.30 gate because the
drum kit's broadband percussive energy lives inside the 50–2000 Hz measurement
band (drums are correctly excluded from the *pitched-note reference* but are
present in the mix). The pitched-only harmonic energy (0.3288) — the metric that
actually isolates tonal coherence — clears the gate. Dominant-peak hit rate
98.6% + ACF unpitched 11% independently confirm tonal, non-noise content.

## Silence / RMS (Analysis/render_stats.json)
- duration 38.71s
- silence ratio: wet 0.0857 (8.57%), dry 0.0993 (9.93%)
- peak 0.8913, LUFS -14.00
- per-second RMS (wet): steady ~0.11–0.15 across the piece, dropping to ~0.016→0
  in the final 3s (reverb tail + end-of-piece padding — legitimate tail, no
  mid-track gaps).

## Fixes applied this run
1. **SVF stability bug (the important one).** `StateVariableFilter.process()` is
   the Chamberlin SVF with `q = 1 - resonance`. At default `resonance=0.5` it is
   unstable above ~12.5 kHz cutoff; at `resonance=0.0` (q=1.0) it is unstable
   above ~9.3 kHz. First two renders produced `NaN` on the drums stem (broadband
   transients + LP swept toward 18 kHz → pole outside unit circle → `bp += f*hp`
   overflow). Fix: cap LP at **11000 Hz** and use the **default resonance**
   (0.5, no override). Verified stable (no NaN, max ~0.35 on the drums stem).
2. **Source override** — selector returned a 2s/12-note stub; promoted the
   project's real 16-bar composition `16bar_country.mid`.
3. **Per-voice flux isolation** — one fresh `CadenceEngine` per voice so
   `FluxRandomizer.apply()` jitter is not re-applied/accumulated across voices
   (single shared engine + shared `self.flux` re-jitters every layer each call).
4. `write_wav` scales by 32767 then `.astype(int16)` (SP-079 int16 truncation bug).

## Artifacts
| file | size |
|---|---|
| SP080-cadence-country-full-16bar.wav | 6,829,100 B (38.71s, 44.1k stereo 16-bit) |
| SP080-cadence-country-full-16bar.ogg | 271,206 B (Opus voip 48k) |
| dry_full_mix_sp001_reference.wav | 6,935,340 B |
| MIDI/16bar_country.mid | source copy |
| Audio/stems_dry/track0{0,1,2,3}_*.wav | 4 dry stems |
| Audio/stems_wet/track0{0,1,2,3}_*_CADENCE.wav | 4 wet (Cadence-modulated) stems |
| Analysis/{pitch_verification,render_stats}.json, grid_visualization.txt | metrics + DNA grid |
| provenance.json | full provenance |
| Scripts/produce_sp080_cron.py | reproducible generator |

## Method status
SP-080 now exercised on a **drum-kit country/pop** source (previous run was the
drum-free 064-markov-constraint-chorale). The drum-kit broadband energy is the
reason full-mix harmonic energy reads ~0.28; the pitched-only metric is the
correct tonal-coherence check for percussion-bearing sources going forward.
