# SP-119 Spectral Resonance Suppressor — 241-soul-voiceleading-graph-rework

Random-style production job (SP methods), layer-aligned, 2026-11-08.

## Selection

| Item | Value |
|---|---|
| Method | **SP-119** — `sound.effects.spectral_resonance_suppressor` |
| Registry source | `workflows.musicom_workflow.SP_METHODS` (single source of truth, 84 registered) |
| Method description | STFT de-resonator (Newfangled Audio Fixate:Midrange-style): per-frame magnitude vs local median baseline → flag excess peaks → raised-cosine notch → freq+frame smoothing → overlap-add resynthesis; midrange band focus |
| Excluded | recent ≤7d (44 methods) + baseline SP-001; pool = 42 |
| Source composition | `Styles/Soul/241-soul-voiceleading-graph-rework` — D minor (aeolian), 92 BPM, 32 bars / 8 sections, TenorSax(66)/Rhodes(4)/Violin(41)/Guitar(25)/Bass(33)/Drums(ch9) |
| Source MIDI | `…/MIDI/241-soul-voiceleading-graph-rework.mid` (13278 B) |

## PRE-FLIGHT RULES AUDIT (3 rules) — re-run independently (mido read-only)

| Rule | Verdict | Numbers |
|---|---|---|
| 1. Grid sync (16th = 120 ticks) | **PASS** | 0 off-grid (1318 pitched onsets) |
| 2. Harmony — scale (D aeolian {2,4,5,7,9,10,0}) | **PASS** | 0 out-of-scale |
| 2. Harmony — chord tone (per-bar triad) | **PASS** | 0 out-of-chord |
| 3. Zero-drift | **PASS** | 6 note tracks × 61440 ticks, equal length (track 0 = conductor/meta) |

**Verdict: PASS all three — no rework needed; proceed to SP method.**

## Method application (absolute layer)

SP-119 is a corrective mix tool (Soothe/Gullfoss/Curves-Equator family), not a
generator. Applied as a single production layer across the WHOLE mix (per the
absolute-layer mandate — no per-voice split):

```
fluidsynth -ni -g 1.2 -F full_mix.wav FluidR3_GM.sf2 <source>.mid   # 44100 Hz, 89.12 s, stereo
SpectralResonanceSuppressor(sample_rate=44100).process(channel,
    amount=0.7, threshold_db=5.0, width_bins=24,
    min_freq=200, max_freq=6000, attack=0.05, release=0.3)           # per channel (L, R)
master(suppressed, target_lufs=-13.0, ceiling_db=-1.0)               # soul target
```

SoundFont `FluidR3_GM.sf2` via `discover_soundfont()`; FluidSynth CLI `-ni -g 1.2`.

## Key finding — clean source, no non-musical resonances to tame (consistent with prior SP-119)

This is the **second** SP-119 production pass; the first (2026-10-25,
`081-funk-schillinger`) reached the same conclusion. A FluidSynth GM render is
spectrally smooth: its midrange peaks are in-key sustained musical tones
(sax/Rhodes/violin fundamentals and harmonics), not pathological ring/mud. A
Fixate:Midrange-style de-resonator compares each bin to its *local* median
baseline, so these broad musical tones sit above the baseline but ARE the
signal — the method correctly declines to eat them.

| Metric | Before | After |
|---|---|---|
| Midrange crest factor (dB) | 50.73 | 50.66 (−0.07) |
| Waveform RMS Δ | — | 0.0119 (1.2%) |
| Waveform max |Δ| | — | 0.0819 |

The tool works hard when there IS ring to fix: the module's own `demo()`
injects a 1500 Hz resonance and shows **96% suppression** (ratio 0.0416).
Here there is no such resonance, so the honest outcome is a near-transparent
pass that measurably preserves musical content (below).

## Pitch verification (mandatory)

Per 0.5 s window, FFT dominant peak 50–1000 Hz; harmonic energy in first 8
harmonics of the lowest fundamental; D-aeolian pitch-class fraction; silence.

| Render | median peak Hz | D-aeol frac | harmonic energy | silence |
|---|---|---|---|---|
| full_mix (ref) | 294.0 (D4) | 0.553 | 0.383 | 0.0602 |
| **sp119_suppressed** | 294.0 (D4) | **0.559** | 0.381 | 0.0595 |

- **Not noise**: harmonic energy ≈ 0.38, far above the single-digit % noise
  signature. Dominant peak D4 (294 Hz) = tonic. PASS.
- **Content preserved**: diatonic fraction *rose* 0.553 → 0.559 and harmonic
  energy held (0.383 → 0.381, retention 0.995) — the de-resonator ate nothing
  musical.
- **Not silent**: 5.95% silence; the 5 low-RMS seconds are the tail ring-out
  after the final chord (legit), no mid-track gaps. PASS.

## Mastering

`target_for_style("soul")` → −13.0 LUFS. Result: integrated **−13.0** LUFS,
true-peak **−1.00** dBTP (ceiling reached).

## Fixes / cleanup

- No composition rework (all three rules audited clean on the source).
- Removed the intermediate `sp119_suppressed_raw.wav` (had been written
  normalize=True, making it a misleading raw comparison); clean in-memory
  pre-master metrics retained in provenance instead.

## Output artifacts

| File | Role | Size |
|---|---|---|
| `Audio/full_mix.wav` / `.ogg` | Reference render (raw mix, unmastered) | 15.7 MB / 1.64 MB |
| `Audio/sp119_suppressed.wav` / `.ogg` | **Primary**: SP-119 de-resonated + mastered −13 LUFS | 15.7 MB / 1.63 MB |
| `MIDI/241-…-rework.mid` | Source MIDI (copied) | 13278 B |
| `Audio/provenance.json`, `silence_profile.json` | Provenance + silence sidecars | — |
| `Analysis/pitch_verification.json` | Pitch / harmonic-energy / silence verification | — |

## Scripts

- `sp119_process.py` — render + SP-119 per-channel + master + Opus OGG + sidecars.
- `verify_pitch.py` — pitch / harmonic-energy / silence verification.
- `analyze_resonance.py` — narrowband excess-over-median reduction check.

## Notes

- SP-119 is a mix "problem-solver": on a spectrally-clean GM render it
  legitimately finds little to suppress. The correct, honest report is
  "no non-musical resonances present" — not a defect of the method (proven by
  the 96%-suppression demo on a synthetic resonance).
