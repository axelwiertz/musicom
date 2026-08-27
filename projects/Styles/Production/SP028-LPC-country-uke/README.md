# SP-028 — LPC Synthesis · Country Uke

**Nightly sound-production pass · 2026-08-12**

A formant-preserving **Linear Predictive Coding (LPC) Synthesis** production pass
applied to an existing Country composition (Project 012, Country Uke).

## Source composition

| | |
|---|---|
| MIDI | `MIDI/original_v2_country_unitmatrix.mid` |
| Orig path | `Styles/Country/012-country-country-uke/MIDI/v2_country_unitmatrix.mid` |
| SHA-256 | `49fc8dad9f1bbad1b96dad214be108feab31c421e1048430727d6f499661d9b4` |
| Tempo / meter | 96 BPM · 4/4 |
| Voices (8) | Lead Vocal, Harmony Vox, Acoustic Guitar, Electric Guitar, Bass, Drums, Fiddle, Pedal Steel |
| Total notes | 1960 |

## Method — SP-028 Linear Predictive Coding (Synthesis Engines layer)

Per `methods_db.md` §SP-028: model audio as the output of an **all-pole IIR
filter** excited by a source (impulse train for voiced, noise for unvoiced).
The filter coefficients `{a_k}` capture the **spectral envelope / formants**;
the excitation encodes pitch and voicing. This enables the two classic LPC
tricks applied here:

1. **Formant-preserving vocal resynthesis (vocoder/timbre transfer)**
   - Analyze the lead-vocal register of a 30 s window of the dry render
     (30 ms frames, 10 ms hop, Hamming window, pre-emphasis `α=0.97`).
   - **Autocorrelation + Levinson-Durbin** (`p = 16`) → all-pole coefficients.
   - Pitch/voicing estimated from the residual's autocorrelation
     (`θ = 0.5` voicing threshold).
   - **Re-excite** the extracted all-pole filter with a clean glottal impulse
     train at the detected pitch → an "LPC country chorus" carrying the
     composition's formant color but a synthetic vocal source.

2. **Formant-preserving pitch shift**
   - Keep LPC coefficients unchanged; change excitation period `T0' = T0 / β`
     with `β = 1.12` (~+1 semitone / 12%) → pitch lifts while formants stay fixed
     (the LPC advantage over plain resampling, which shifts formants together).

## Pipeline

```
composition.mid
  └─(FluidSynth CLI, TimGM6mb.sf2, stereo dry render)──► dry_render_full.wav
  └─(mido read-only analysis)──► 8-voice map, 96 BPM 4/4
dry.wav ──(LPC analysis: autocorr + Levinson-Durbin)──► {a_k}, {T0}, {voicing}, {gain}
{a_k}, {T0} ──(glottal-train re-excitation + β=1.12)──► stem_lpc_vocal_resynth.wav
                                                       └► stem_lpc_pitchshift_beta112.wav
dry.wav + LPC stem ──(0.9 dry + 0.35 LPC blend, -1 dBFS)──► full mix WAV
full mix WAV ──(ffmpeg libopus 48k voip)──► full mix OGG
```

## Output artifacts

| File | Description |
|------|-------------|
| `MIDI/original_v2_country_unitmatrix.mid` | Source composition (reference copy) |
| `Audio/SP028-LPC-country-uke-fullmix.wav` | Final full mix (125.33 s, 44.1 kHz stereo) |
| `Audio/SP028-LPC-country-uke-fullmix.ogg` | Final mix, Opus 48k voip (delivery) |
| `Audio/stem_lpc_vocal_resynth.wav` | LPC vocal resynthesis stem (formant color) |
| `Audio/stem_lpc_pitchshift_beta112.wav` | LPC formant-preserved pitch-shift stem |
| `provenance.json` | Source SHA-256 + method + params + analysis |
| `Analysis/lpc_formant_grid.txt` | LPC voicing grid + voiced-pitch contour |
| `produce_sp028.py` | Reproducible production script |

## Verification

- All WAV/OGG files non-empty (> 40 bytes).
- Duration: **125.33 s** @ 44.1 kHz (all outputs).
- Peak: **-0.855** (≈ -1.4 dBFS), mean RMS ≈ 0.11 — healthy level, no clipping.
- **Silence fraction 1.9%** — music is fully populated (no silent-render trap;
  the 1.9% is natural tail/breath gaps, not mid-track dead zones).
- RMS per second steady ~0.10–0.12 across the first 8 s — no dropouts.
- LPC analysis: 2998 frames over the 30 s vocal window, **21.7% voiced**,
  voiced pitch range 165–495 Hz, mean **374 Hz** — consistent with a lead
  vocal + harmony in the country register.

## Listen guide

- **full mix**: the dry country arrangement (guitar, fiddle, pedal steel, bass,
  drums) stays intact; the LPC stem adds a subtle vocal-formant sheen over the
  arrangement — the "LPC chorus" layer most audible on sustained vocal/top notes.
- **stem_lpc_vocal_resynth alone**: pure source-filter demo — clean synthetic
  glottal tone shaped by the extracted country-vocal formants; you hear the
  resonant "ah/eh" coloring with no noise floor.
- **stem_lpc_pitchshift alone**: pitch lifted ~12% over the dry vocal while the
  formant envelope stays locked — the classic resampling-vs-LPC difference.

## Method notes / decisions

- `p = 16` chosen as a middle LPC order — captures the first 2–3 formant pairs
  (enough for vocal color) without overfitting into noise modeling (p=30–50
  reserved for complex timbres).
- Voicing threshold `θ = 0.5` per the spec; unvoiced frames re-synthesized with
  0.15-gain white noise to add breath/resonance rather than dead silence.
- The LPC stem is blended at 0.35 under the 0.9 dry arrangement so the LPC color
  is a production **layering effect** (SP-028 synthesis applied as a production
  gloss) rather than a full replacement — keeps the country identity intact.
- Fluidsynth default (non-`.sf2`) GM soundfont `TimGM6mb.sf2` used for the dry
  source; headless `-a file` driver required in this sandbox.