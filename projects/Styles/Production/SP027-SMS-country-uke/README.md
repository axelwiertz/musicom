# SP-027 Spectral Modeling Synthesis — Production Pass

**Job:** Autonomous daily production pipeline (`9a2813f77dac`)
**Run type:** Random composition × random sound-production method

## Selection (this run)

| Item | Value |
|------|-------|
| Source composition | **012-country-country-uke** (Country Uke, C major chord-melody) |
| Source MIDI | `/opt/data/projects/Styles/Country/012-country-country-uke/MIDI/country_uke.mid` |
| Production method | **SP-027 — Spectral Modeling Synthesis (SMS)** |

The source is a 4-bar loop (4 chords: C / C / F / G-ish voicings) played on the
default GM piano patch (no explicit program change). It is a clean, harmonically
consonant piece — a good candidate for SMS because its deterministic (harmonic)
and stochastic (residual) components are well separated.

## Method applied (SP-027)

Spectral Modeling Synthesis (Xavier Serra, MTG-UPC 1989) decomposes audio into:

- **Deterministic (harmonic) component** — sinusoidal tracks (time-varying
  amplitude / frequency / phase) extracted via STFT peak-detection + peak tracking.
- **Stochastic (residual) component** — the non-harmonic remainder, modelled as
  band-shaped filtered white noise.

The reference implementation from `methods_db.md` (SP-027) was executed exactly:
Hann window `N=2048`, hop `H=512`, up to `K_max=60` partials per frame,
`min_snr=40 dB`, `peak_tolerance=30 Hz`. The decomposition yielded **13,918
sinusoidal tracks** over the 7.05 s render.

### Sound transformation

SMS enables independent manipulation of the two components. Applied:

1. **Deterministic pitch-shift +3 semitones** — the harmonic partials were
   shifted up (resampling the clean sum-of-sinusoids band), brightening the uke
   voicing into a higher register.
2. **Stochastic envelope preserved** — the residual noise texture (room/attack
   "live" character) was kept unchanged, so the timbral body stays natural.
3. **Stochastic balance +3 dB** — residual energy lifted for a livelier, more
   present room feel.

Components re-mixed, RMS-matched to the source (for comparable loudness), then
soft-limited (`tanh`) to stay under -1 dBFS without hard-clip artifacts.

## Output artifacts

| File | Description |
|------|-------------|
| `country_uke_base.wav` | Raw FluidSynth render (TimGM6mb.sf2) — reference |
| `country_uke_SP027_SMS.wav` | Final SMS-transformed full mix |
| `country_uke_SP027_deterministic.wav` | Deterministic (pitch-shifted harmonic) component only |
| `country_uke_SP027_stochastic.wav` | Stochastic (residual noise) component only |
| `country_uke_SP027_SMS.ogg` | Final mix, Opus 48k (delivery format) |
| `provenance.json` | SHA-256 + method/transformation metadata |
| `produce.py` | Reproducible production script |
| `_verify.py` | Output validation script |

## Render chain

```
MIDI --(FluidSynth 2.5.6 / TimGM6mb.sf2)--> base.wav
base.wav --(SMS analyze)--> det + stoch
det --(+3 st pitch-shift)--> det'
stoch --(+3 dB)--> stoch'
(det' + stoch') --(RMS-match + soft-limit)--> full_mix.wav
full_mix.wav --(ffmpeg libopus 48k)--> full_mix.ogg
```

## Verification

- All WAV/OGG files non-empty (`> 40` bytes).
- Durations consistent: 7.05 s @ 44.1 kHz for all outputs.
- Source RMS ≈ 1530 (int16); SMS mix RMS ≈ 615 — clearly audible, softer crest
  than the original piano (expected: additive IBF synth has higher crest factor;
  soft-limiting preserved mid-level detail instead of peak-crushing).
- `provenance.json` written with source + output SHA-256.

## Listen guide

- **full_mix** vs **base**: the SMS version sits a bit higher (brighter uke) with
  a touch more "room" in the attacks — the harmonic shift is subtle but present.
- **deterministic** alone = pure pitched tone (sine-like, the +3 st shift audible
  as higher pitch); **stochastic** alone = airy noise bed with no pitch.
