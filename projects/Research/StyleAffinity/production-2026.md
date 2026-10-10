---
name: production-2026
type: Reference
title: Modern Professional Sound — 2026 Production Methods
resource: https://github.com/axelwiertz/musicom
tags: [music, production, mastering, lufs, streaming, okf]
timestamp: 2026-10-10T12:00:00Z
---

# Modern Professional Sound — 2026 Production Methods

How to make musicom output sound professional under current (2026) production
practice. The synthesis layer is *complete* (SP-* methods); "professional" is
the mix/master glue on top. This doc pins the targets, the chain, and the
engine entry points.

## 1. Loudness targets (the real numbers)

Streaming normalization = **playback gain, not processing**. A master above
target gets turned down cleanly; there is no loudness win. Genre decides, not
the platform.

| Platform | Integrated LUFS | True peak | Boosts quiet masters |
|---|---|---|---|
| Spotify | -14 | -1 dBTP | Yes |
| Apple Music | -16 | -1 dBTP | Yes |
| Tidal / YouTube / Amazon | -14 | -1 dBTP | No |

### Genre → LUFS (baked into `GENRE_LUFS` in `sound/effects/mastering.py`)

| Class | Target | Examples |
|---|---|---|
| Loud-first | -8..-11 | pop -9 · hiphop/trap/drill/phonk -8/-9 · edm -9 · house/techno -10 · disco/rock/amapiano -11 |
| Balanced | -13..-14 | jazz -14 · blues -14 · soul/funk -13 · chanson -14 · country/reggae/latin -13/-14 |
| Dynamic | -16..-18 | ambient/classical/minimal -18 · folk/solo -16 |

## 2. What the top 2025 tracks actually measure

| Metric | Observed range | Meaning |
|---|---|---|
| Dynamic range | 3.3–7.1 DR | punchy (>5) beats squashed (≤4) |
| Max short-term | -3.3..-7 LUFS | loudest moments, not crushed |
| LRA | 3.7–10.4 LU | movement between sections |

#1 (Die With A Smile) = **7.1 DR / 10.4 LU** — dynamics win, not max
loudness. No universal EQ curve exists; match a reference in your style.

## 3. Codec-safe mastering chain

1. **High-pass 20–30 Hz** — inaudible sub wastes headroom, confuses AAC/Ogg.
2. **Corrective EQ** — balance, not color.
3. **Gentle compression** — 1–3 dB GR max (kills dynamics = fatigue).
4. **Stereo imaging** — mono sub (<100 Hz), widened highs (>3 kHz), mono-check.
5. **True-peak limit -1.0 dBTP** — inter-sample peaks the encoder creates.

Deliver the mix at **-3..-6 dBFS** peak headroom, 24-bit WAV/FLAC, no
master-bus limiter.

## 4. Engine entry points (unified master stage)

The DSP already lives in `sound/effects/mastering.py`
(`LUFSMeter`, `normalize_to_lufs`, `StereoImager`, `Limiter`, `DynamicEQ`,
`MasteringChain`) and `production_chain.py` (7-stage `ProductionChain`). The
**unified one-call stage** added 2026-10-10:

```python
from sound.effects.mastering import master, target_for_style

audio, report = master(
    audio,                                  # float32/64, mono or [n,2]
    target_lufs=target_for_style("pop"),    # -9.0 for pop
    ceiling_db=-1.0, hp_hz=30.0,
    sample_rate=44100,
)
# report: {"stages": [per-stage LUFS], "integrated_lufs", "true_peak_db"}
```

Chain order inside `master()`:
`high_pass → glue_compress → stereo_imager → normalize_to_lufs → true_peak_limit`

New primitives (all additive, deterministic, tested):
- `high_pass(audio, cutoff_hz=30)` — sub cleanup.
- `glue_compress(audio, threshold_db=-18, ratio=2)` — soft-knee bus glue.
- `true_peak_limit(audio, ceiling_db=-1, oversample=4)` — inter-sample peak
  limiter (4x oversampled envelope).
- `target_for_style(style)` / `LOUDNESS_TARGETS` / `GENRE_LUFS` — genre map.

### Bolt onto RenderPipeline

```python
from sound.render.pipeline import RenderPipeline
pipe = RenderPipeline(soundfont_path=SF)
pipe.render_to_wav(midi, out, master_bus=True, target_lufs=-14.0)  # default off
pipe.render_to_ogg(midi, out, master_bus=True, target_lufs=-14.0)
```

`master_bus` defaults `False` — zero behavior change for existing callers.

### Verified numbers (real pop render, 2026-10-10)

| Stage | Integrated LUFS |
|---|---|
| input (raw FluidSynth) | -15.54 |
| highpass | -15.55 |
| glue | -16.04 |
| stereo | -16.03 |
| lufs_norm (-14) | -14.00 |
| true_peak_limit | -14.00 |

Final: **-14.0 LUFS / -1.0 dBTP**. True-peak limiter pulled a 0.98-amplitude
997 Hz sine (sample peak -0.18 dBFS) to **-1.00 dBFS** (inter-sample aware).

## 5. 2026 tool landscape (context, not dependency)

- **AI-assisted** (human-led, AI-assisted is the standard): iZotope Ozone 12 /
  Neutron / RX 12; LANDR, eMastered, Cryo Mix, RoEx Automix for mastering.
- **Restoration-first**: RX repair before mix is mandatory, not optional.
- **Immersive/spatial** (Atmos) = fastest-growing skill; stereo still default.

## 6. Pitfalls

- **Loudness normalization is NOT a target.** Master for the music, check
  integrated LUFS + LRA at the end, manage true peak. Aiming for a number is
  missing the point — the platform normalizes to its own target regardless.
- **Over-compression is the #1 streaming mistake.** Heavy GR + low DR (≤4)
  sounds dense-but-fatiguing after normalization.
- **True peak is the one non-negotiable.** Keep ≤ -1 dBTP for codec safety.
- **Do not `TapeDelay` for echo** — it self-oscillates into full-scale noise
  (loop gain > 1.0). Use a manual overlay for delay.
