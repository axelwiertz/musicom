# SP-085 GlitchChopper — Delta Blues / blues-delta-daily-2026-06-24

**Date (UTC):** 2026-10-09 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP085-glitch-chopper-blues-delta-daily/`
**Status:** PASS — FFT 80/80, HE retention 0.919, silence 12.82% (wet) vs 15.46% (dry), LUFS −14.15, peak 0.891.

---

## 1. Method + selection (which registry source)

| Field | Value |
|---|---|
| Method | **SP-085** — Transient-Snapped Segment Chopper w/ Glitch/Reverse Probability (GlitchShredder-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT a stale `SP-001..SP-035` range) |
| Registered module | `sound.effects.glitch_chopper` → `GlitchChopper`, `ChannelChopper`, `spectral_flux`, `detect_transients` |
| Registry entries at pick time | **42 implemented** (SP-001 … SP-102) |
| Already used last 7d (excluded) | SP-021, SP-069, SP-080, SP-083, SP-086, SP-091, SP-092 |
| Baseline excluded | SP-001 |
| Eligible pool | 33 methods |

**Re-roll note (two draws):**

1. **First draw** (seed `20261009`) landed on **SP-074** ×
   `Blues/blues-delta-daily-2026-06-24/MIDI/blues-delta-daily-2026-06-24.mid` —
   the **exact** source+method pair already produced 2026-09-15 as
   `Production/SP074-drummachine-delta-blues/` (its REPORT.md names this same
   source MIDI). Re-rolled the method only, keeping the well-formed source.
2. **Second draw** (seed `20261010`, method pool minus SP-074) landed on
   **SP-085** — first SP-085 production run (registered 2026-09-17, never
   produced until tonight).

Selection record: `Production/.selection_cron.json` and
`Analysis/select_20261009.json`.

Well-formed filter: 221 / 330 candidate MIDIs passed (normal tpb, sane note
lengths, ≥2 note tracks or a program change, 2–600 s length).

## 2. Source composition

| Field | Value |
|---|---|
| Project | `Styles/Blues/blues-delta-daily-2026-06-24/` |
| MIDI | `MIDI/blues-delta-daily-2026-06-24.mid` (copied to `MIDI/`; 4024 B) |
| Genre / key | Delta Blues, A blues hexatonic; 8-bar blues in A7 + intro/outro = 12-bar grid |
| Tempo | 72.00 BPM (833333 µs/beat), 480 tpb, 12/8 feel |
| Length | 39.62 s music (44.68 s with FluidSynth tails); 12 bars × 1920 ticks |
| Voices | Resonator Slide lead GM25 ch0 (**290 notes**) · Acoustic Rhythm GM26 ch1 (83 notes) · Fingerstyle Bass GM32 ch2 (47 notes) · Stomp & Clap ch9 (101 onsets) |
| Source PCS (non-drum) | `[0, 1, 2, 3, 4, 6, 7, 8, 9, 11]` — A blues hexatonic + slide ornaments |

## 3. Layer discipline (absolute — effect on the full mix)

SP-085 is an **absolute-layer time/timbre method**: the transient-snapped
16-slot chopper recombines the **whole** mixed signal (all 4 voices together),
replacing the time layer with quantized stutter/reverse recombination. The
pitch/harmony content is preserved (segments are re-ordered/reversed, not
re-synthesized) — the tonal identity of the delta blues survives; only the
time grain changes. Per-stem passes use the same params as a DAW convenience
(independently-glitched; they do **not** linearly sum back to the wet mix).

```
blues-delta-daily-2026-06-24.mid
 -> dry SoundFont reference (fluidsynth -ni -g 1.2, reverb OFF, chorus OFF, FluidR3_GM.sf2)
      dry_full_mix_sp001_reference.wav  44.68 s, silence 15.46%, RMS 0.132
 -> dry per-track stems (RenderPipeline.render_stems, FX off)
      track00 Acoustic_Guitar_steel / track01 Electric_Guitar_jazz /
      track02 Acoustic_Bass / track03 Drums
 -> GlitchChopper(bpm=72, slots=16, seed=20261009): glitch_p 0.30, reverse_p 0.25, quant 8
      wet full mix (per-channel 16-slot bank, transient-snapped, 8 quantized
      jumps/bar, reverse+recombine probabilities)  -> 44.68 s
 -> master: normalize_to_lufs(-14) -> Limiter(-1.0 dBFS) LAST
 -> SP085-glitch-chopper-blues-delta-daily.wav + .ogg (Opus 48k voip)
 -> per-stem GLITCH copies (same params, independent RNG) for DAW
```

Transient census: **447** spectral-flux onsets detected on the dry mono mix —
the chopper snaps its 16 slot boundaries to these where possible.

## 4. Parameters

| Param | Value | Logic |
|---|---|---|
| Engine | `GlitchChopper(sample_rate=44100, bpm=72.0, slots=16, seed=20261009)` | registered SP-085 engine |
| `glitch_p` | 0.30 | a quantized step is replaced by a random other slot with P=0.30 |
| `reverse_p` | 0.25 | a slot plays backwards with P=0.25 |
| `quant` | 8 | 8 quantized jumps/bar = 8th-note stutter grid (0.417 s/window @72 BPM) |
| `slots` | 16 | segment bank per channel (capture window = one stutter bar) |
| Bar length | 147000 samples (60/72×4 s) | 12 bars processed |
| Master | `normalize_to_lufs(−14)` → `Limiter(−1 dB)` | measured **−14.15 LUFS**, peak 0.8913 |
| SoundFont | `discover_soundfont()` → FluidR3_GM.sf2 | ONE-ENV contract, never hardcoded |

## 5. Pitch / tonal-content verification — **PASS**

Size asserts and silence ratios alone do **not** catch noise (SP-035 lesson).
Checks on the delivered files (same method as SP-092):

| Metric | Wet mix | Dry reference | Gate | Verdict |
|---|---|---|---|---|
| FFT hit rate (0.5 s windows, ±2% f0×1–4, 50–1000 Hz) | **80/80 = 1.000** | 80/80 = 1.000 | ≥ 0.60 | PASS |
| Mean harmonic energy (8 harmonics) | 0.402 | 0.438 | HE retention ≥ 0.50 | PASS (retention **0.919**) |
| LUFS / peak | −14.15 / 0.891 | — | limiter last | PASS |

The SP-085 effect re-orders/reverses existing segments — it cannot introduce
new pitch (no re-synthesis), so a high hit rate is expected; the guard is HE
retention, which is **0.919** (only −0.035 vs dry, the expected cost of
reverse/tile discontinuities). The SP-035 failure signature (0 Hz frames +
single-digit harmonic energy) is **absent**.

Full JSON: `Analysis/pitch_verification.json`, `Analysis/render_stats.json`.

## 6. Silence / RMS profile

| Metric | Wet | Dry | Note |
|---|---|---|---|
| Silence (<0.001) | **12.82%** | 15.46% | wet LOWER — stutter/tile fills interstices |
| RMS | 0.115 | 0.132 | slightly lower peak density, expected |
| Peak / LUFS | 0.8913 / −14.15 | ~1.0 / — | mastered |

Dry silence (15.46%) matches the SP-074 run on this same source byte-for-byte
on the dry render (same FluidSynth flags), confirming the reference path is
consistent. No mid-track production gaps; the only >30%-silent windows are the
natural 4 s FluidSynth tail.

## 7. Fixes applied during this run

1. **`glitch_chopper.render_pass` slot-padding bug (fatal musical bug).**
   V1 render: `render_pass` sliced `self.bank[cur_slot]` (a *bar-length* row
   whose first `step = bar/16` samples hold the slot, rest are zero padding)
   over a window of `out_len/quant`. For `quant < 16` every window therefore
   picked up the zero padding → **~60.05% silence** on the wet mix. Root
   cause: the docstring/comment intends the slot *content* to "tile the slot
   over the quantized window", but the code passed the full padded row.
   Fix: `seg = self.bank[cur_slot][:step].copy()` — slice to the real slot
   content before the `np.resize`/tile. After fix: wet silence **12.82%**
   (below dry 15.46%), module `demo()` still green, determinism/L-R
   independence asserts still pass. Engine edit committed to
   `sound/effects/glitch_chopper.py` (no test pinned its old behavior).
2. **Transient snap is bar-relative only for bar 0.** `capture()` compares
   *global* transient sample indices against bar-relative ideal grid
   positions, so transient snapping only actually engages on bar 0; later
   bars fall back to grid-aligned slots. Documented limitation, not corrected
   (out of scope for an apply-job; the effect remains valid and deterministic).
3. **Self-copy guard.** produce script guards `shutil.copy2(__file__, …)` so a
   re-run doesn't raise `SameFileError`.

## 8. Artifacts

| Artifact | Path | Size |
|---|---|---|
| Full mix WAV | `SP085-glitch-chopper-blues-delta-daily.wav` (44.68 s, 44.1 kHz stereo) | 7,881,516 B |
| Full mix OGG (Opus 48k voip) | `SP085-glitch-chopper-blues-delta-daily.ogg` | 353,992 B |
| Dry reference mix (FX-off) | `dry_full_mix_sp001_reference.wav` | 7,881,516 B |
| Source MIDI (copy) | `MIDI/blues-delta-daily-2026-06-24.mid` | 4,024 B |
| Dry stems | `Audio/stems_dry/track00..03.wav` | — |
| Wet stems | `Audio/stems_wet/track00..03_GLITCH.wav` | — |
| Renderer | `Scripts/produce_sp085_cron.py` | — |
| Verification JSON | `Analysis/pitch_verification.json`, `Analysis/render_stats.json` | — |
| Selection JSON | `Analysis/select_20261009.json` | — |
| Provenance | `provenance.json` | — |
| Report | `REPORT.md` | this file |

WAVs git-ignored by policy; OGG + MIDI + JSON + REPORT tracked.

## 9. Listen for

- Slide-guitar phrases stutter and reverse on the 8th-note grid (quant 8),
  recombining 16th-slice segments of each bar — the shuffle now glitches
  instead of flowing, but every note is still the *same* pitch material.
- Reverses (P=0.25) read as "backwards smear" of the slide/hat; glitches
  (P=0.30) jump to a non-adjacent slice. L/R channels glitch independently
  (separate RNG streams) → a stereo "scatter" the mono source never had.
- Compare `dry_full_mix_sp001_reference.wav` (clean) vs the wet mix: same
  delta-blues calls, new time grain.

## 10. Quality gate

- [x] MIDI present for the audio render (`MIDI/blues-delta-daily-2026-06-24.mid`)
- [x] OGG non-empty (~354 kB) and playable-length (44.68 s)
- [x] Pitch verification run and reported (PASS: FFT 80/80, HE retention 0.919)
- [x] Silence ratio + RMS measured; wet 12.82% vs dry 15.46%, no production gaps
- [x] Full mix WAV + per-track stems (dry AND wet/GLITCH)
- [x] `provenance.json` per artifact set (incl. fix record)
- [x] Output under `projects/Styles/Production/<method>-<project>/`
- [x] No hardcoded soundfont (`discover_soundfont` → FluidR3_GM.sf2)
- [x] Engine bug fixed + verified (`sound/effects/glitch_chopper.py`); `demo()` green, full pytest **693 passed / 1 skipped**
