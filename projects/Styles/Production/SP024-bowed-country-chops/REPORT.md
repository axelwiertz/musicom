# SP-024 — Bowed String Physical Modeling → "bowed country chops"

**Job:** random-style production (SP methods), LAYER-ALIGNED cron
**Date:** 2026-09-10
**Output project:** `/opt/data/repos/musicom/projects/Styles/Production/SP024-bowed-country-chops/`

---

## 1. Selection

| Item | Value |
|---|---|
| Method registry (single source of truth) | `workflows.musicom_workflow.SP_METHODS` |
| Registry size | 18 implemented methods |
| Seed | `20260910` (date-derived, reproducible) |
| Pool after 7-day exclusion | `SP-021, SP-024, SP-069, SP-070, SP-071, SP-072, SP-073, SP-074` |
| **Chosen method** | **SP-024** → `sound.synthesis.bowed` (Bowed String Physical Modeling) |
| **Source composition** | `projects/Styles/Country/001-country-loop-seamless/MIDI/loop.mid` |
| Source provenance | Country, G major, 120 BPM, 16-bar seamless loop, 4 tracks, 333 notes |
| Layer discipline | **absolute** — SP-024 replaces the production layer for ALL voices |

Excluded in the last 7 days (per `.selection.txt`): SP-001, SP-011, SP-026, SP-028,
SP-032, SP-033, SP-034, SP-035, SP-036, SP-037.

## 2. Method

`sound.synthesis.bowed.BowedString` — friction-induced digital waveguide.
The string is split into two bidirectional delay-line segments (neck + bridge) at
the bowing point; a Newton-Raphson solver (4 iterations) resolves an exponential
sliding-friction law per sample, producing Helmholtz stick-slip motion.

Call surface used (module API directly, no `produce()` adapter for this method):

```python
from sound.synthesis.bowed import BowedString
bs = BowedString(sample_rate=44100)
audio = bs.render(freq=..., duration=..., bow_velocity=<envelope>,
                  bow_force=..., bow_position=..., friction_decay=...,
                  noise_level=...)
```

## 3. Voice mapping (whole piece re-rendered as bowed strings)

| Track | Source name | GM prog | Bowed role | Register | Params |
|---|---|---|---|---|---|
| 1 | Violin | 40 | violin (motif/fiddle) | 67–79 | bow pos 0.17, vel 0.26, force 1.2, decay 5.0, rosin 0.010 |
| 2 | Acoustic Guitar | 24 | viola (harmony chops) | 43–66 | bow pos 0.15, vel 0.19, force 1.5, decay 5.5, rosin 0.014 |
| 3 | Acoustic Bass | 32 | bass (walking line) | 36–47 | bow pos 0.10, vel 0.13, force 2.2, decay 5.0, rosin 0.010 |
| 4 | Percussion | ch 3 | **bowed chop** (kick/snare/hat) | 36/38/42 | see §4 |

Stereo: bass static pan 0.44; viola harmony alternates 0.62/0.38; violin lead
drifts −0.40…+0.40 across the phrase. Bus: soft-knee saturation (thresh 0.85,
slope 0.30), peak-normalized to −1 dBFS (measured 0.8473).

## 4. Percussion: bowed "chop" adaptation

All 128 drum hits were re-synthesized as short, high-force, near-bridge bow
strokes (no samples). The raw waveguide output is peak-normalized per note, so
gain is set by an explicit **target RMS** per class, then class-filtered
(cascaded one-pole filters, numpy only):

| GM note | Class | Body | Filter | Noise layer | target RMS | measured centroid |
|---|---|---|---|---|---|---|
| 36 | kick | 65.4 Hz, 200 ms, force 5.2 | LP 300 Hz × 2 | — | 0.060 | **332.8 Hz** |
| 38 | snare | 190 Hz, 150 ms, force 4.4 | LP 4000 Hz × 1 | 1200–7000 Hz, LP 7000 | 0.050 / 0.035 | **4607.8 Hz** |
| 42 | hat | 1700 Hz, 70 ms, force 3.0 | HP 5000 Hz × 2 | 6000–13000 Hz | 0.010 / 0.008 | **9700.7 Hz** |

Texture ordering **kick < snare < hat** verified → `perc_texture_ok: true`.

## 5. Verification (pitch, not just size/silence)

Mandatory for synthesis methods — a size assert and a silence ratio do NOT catch
noise.

**Per-note pitch detection (two-stage: autocorrelation, then FFT dominance in a
±25 % band around the expected fundamental):**

```
per-note pitch tally: 141/141 (100.0%)
  track 1 violin:  61/61 (100.0%)
  track 2 viola:   16/16 (100.0%)   [simultaneous onsets → chord-member test]
  track 3 bass:    64/64 (100.0%)
  track 4 perc:    verified separately (transient, no stable f0) → §4
```

**Harmonic energy in the first 8 harmonics of the lowest fundamental per voice**
(gate: ≥ 30 %; a noise render scores single digits):

| Voice | Lowest MIDI | f0 | Fundamental present | 8-harmonic energy |
|---|---|---|---|---|
| Violin | 67 | 392.0 Hz | yes | **30.6 %** |
| Guitar (viola role) | 43 | 98.0 Hz | yes | **37.3 %** |
| Bass | 36 | 65.4 Hz | yes | **72.3 %** |

All three pass the ≥ 30 % harmonic-energy gate. Note that for bowed strings the
STRONGEST spectral peak can sit on a harmonic (bridge LPF boosts upper partials),
so verification checks fundamental **presence** + harmonic ratio instead of
naive argmax pitch.

**Silence / RMS:**

| Metric | Value |
|---|---|
| Full-mix silence ratio | 62.9 % ← see source defect below |
| **Core (first 17 s) silence ratio** | **3.3 %** |
| Core per-second RMS | 0.26, 0.29, 0.26, 0.29, 0.30, 0.26, 0.29, 0.26, 0.26, 0.30, 0.26, 0.29, 0.30, 0.26, 0.28, 0.25, 0.01 |
| Peak | 0.8473 (−1.4 dBFS) |

No mid-track gaps: RMS is flat ~0.26–0.30 across the core; only the final
second decays (release tail). The percussion-only tail runs at ~0.010 RMS,
which is audible but far below the core.

### ⚠️ Source defect discovered

`loop.mid` **does not have equal-length tracks** despite being called a seamless
loop: Violin/Guitar/Bass end at ~15.5–16.5 s (16 bars), but the percussion track
keeps repeating **to 63.25 s** (128 hits = 64 bars of kick/snare/hat). The
64-second full render is therefore faithful to the source, but 47 s of it is a
percussion-only tail — that is the entire reason the naive full-mix silence ratio
reads 62.9 %. A trimmed **core mix** is exported so the bowed arrangement can be
judged directly. This matches the known `validate()` "track length mismatch"
failure class.

## 6. Fixes applied during this pass

1. **Verification window vs hit length** — the 0.25 s per-note analysis window
   overran 50–160 ms percussive hits, returning 0 Hz for all 64 perc hits.
   Percussive classes are now verified by spectral signature instead of f0.
2. **Noise-band gain bug** — `band_noise` peak-normalizes internally, so the
   original dB gain offsets were meaningless and all classes collapsed to a
   ~8.5 kHz harsh centroid. Replaced with explicit per-class target RMS.
3. **Coincident-hit contamination** — kick+snare+hat land together on beats, so
   per-class centroid measured on the summed percussion stem reflected the mix
   (kick read 7813 Hz). Class buses are now built and measured **isolated**;
   kick now reads 333 Hz.
4. **Silence-ratio dilution** — full-mix silence is reported alongside a 17 s
   core metric so the source's percussion tail does not masquerade as dead render.
5. **Grid visualization truncation** — the 16th-note grid now shows the musical
   core (136 cells) instead of 500+ cells of tail.

## 7. Artifacts

| File | Size |
|---|---|
| `Audio/SP024-bowed-country-chops.wav` | 11 510 144 B (64-bit float source, 65 s stereo) |
| `Audio/SP024-bowed-country-chops.ogg` | 210 093 B (Opus, voip 48 kbps) |
| `Audio/SP024-bowed-country-chops-core16s.wav` | 2 998 844 B (17 s musical core) |
| `Audio/SP024-bowed-country-chops-core16s.ogg` | 102 112 B |
| `Audio/stems/track01_Violin.wav` … `track04_Percussion.wav` | 4 × 11 510 144 B, time-aligned |
| `MIDI/loop.mid` | 3 139 B (source copy) |
| `Analysis/render_info.json` | full parameter + verification record |
| `Analysis/grid_visualization.txt` | 16th-note onset grid |
| `produce_sp024_country.py` | reproducible generator |
| `provenance.json` | artifact provenance sidecar |

WAVs are gitignored (renderable from MIDI); OGG is tracked per user decision
2026-08-27.

## 8. Listening notes

- **Violin** — the source's fiddle line becomes a real bowed string: bow attack
  transients, Helmholtz plateaus, phrase drift left→right.
- **Guitar → viola** — the 1-second strummed comping becomes sustained bowed
  chords; the alternation 0.62/0.38 gives a gentle width without reverb.
- **Bass** — the walking line now has bow noise and a strong low fundamental
  (72 % harmonic energy), the most "instrument-like" of the three.
- **Percussion → bowed chop** — nothing on this piece is a sample or a GM drum
  anymore. Every hit is a short friction burst; kick is a low-filtered body,
  snare adds band-limited rosin noise, hat is a high-passed scrape.
- The full render is faithful to the source; listen to the **core16s** pair for
  the 16-bar arrangement and the full files for the percussion-loop tail.
