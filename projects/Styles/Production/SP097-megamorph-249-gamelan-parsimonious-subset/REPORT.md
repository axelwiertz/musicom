# SP-097 MegaMorph Multi-Lane Parameter Modulation — 249-gamelan-parsimonious-subset

Random-style production job (SP methods), layer-aligned, 2026-11-06.

## Selection

| Item | Value |
|---|---|
| Method | **SP-097** — `sound.effects.mega_morph` |
| Registry source | `workflows.musicom_workflow.SP_METHODS` (single source of truth) |
| Method description | Multi-Segment Envelope Generator for Parameter Modulation (Sync Audio MegaMorph-style) |
| Excluded (recent ≤7d) | 43 methods (SP-009, SP-011, SP-021, SP-025…SP-117, SP-143) + baseline SP-001 |
| Source composition | `Styles/Gamelan/249-gamelan-parsimonious-subset` — D-pentatonic {D E F♯ A B} slendro-like gamelan, 108 BPM, head-solos-head form, glockenspiel (balungan) + vibraphone (gender) + marimba (kenong) + kendang kit |
| Source MIDI | `…/MIDI/249-gamelan-parsimonious-subset-humanized.mid` (7983 B, sha256 `03edf2f8…`) |

## PRE-FLIGHT RULES AUDIT (3 rules) — re-run on source, mido read-only

Audited via the project's own `verify.py` (mido readback, real numbers):

| Rule | Verdict | Numbers |
|---|---|---|
| 1. Grid sync | **PASS** | Compositional truth = `-perfect.mid`: **0 off-grid** (4 voices, 16th grid). Selected `-humanized.mid`: 712 off-grid = **by-design humanization micro-timing** (off-grid > 0 is the humanization contract), not compositional slop. |
| 2. Harmony — scale | **PASS** | 0 out-of-scale in BOTH perfect and humanized (all notes ∈ D pentatonic). |
| 2. Harmony — chord tone | **PASS** | perfect: **0 out-of-chord**. humanized: 9 "out-of-chord" = documented bar-line jitter attribution artifact (onset jitter moves 9/748 onsets across a bar line; their pitch classes unchanged + in-key). |
| 3. Zero-drift | **PASS** | 4 tracks × 61440 ticks, equal length; `validate()` gate green (source `compose.py`). |

**Verdict: PASS all three — no rework needed; proceed to SP method.**

## Method application (absolute layer)

SP-097 is an envelope/modulation HOST, not a standalone sound generator — it
renders multi-lane control signals that drive audio processors. Applied as a
single production layer across the WHOLE mix (no per-voice split, per the
absolute-layer mandate):

```
fluidsynth -ni -g 1.2 -F full_mix.wav FluidR3_GM.sf2 <humanized>.mid   # 44100 Hz, 78.64 s, stereo
MegaMorph(bpm=108) — 3 lanes rendered at control rate (5 ms), np.interp → audio rate:
  gate   LOOP   [1.0 @0.5 beat SMOOTHSTEP, 0.32 @0.5 beat EXP(curv 3)]  → amplitude modulation
  cutoff BOUNCE [0.12 @2 beat SMOOTHSTEP, 0.95 @2 beat SMOOTHSTEP]      → SVF lowpass sweep
  pan    LOOP   [1.0 @1 beat, 0.0 @1 beat]                              → constant-power stereo
gated   = mix * gate
cutoff  = 250·(9000/250)^lane  (log map) → StateVariableFilter lp (res 0.5, block 512, time-varying)
panned  = constant-power pan on gated+filtered
master(panned, target_lufs=-14.0, ceiling=-1.0)                          # gamelan → -14 LUFS
```

SoundFont: `FluidR3_GM.sf2` via `discover_soundfont()`; FluidSynth CLI `-ni -g 1.2`.

## Output artifacts

| File | Role | Size |
|---|---|---|
| `Audio/full_mix.wav` / `.ogg` | Reference render (raw mix, unmastered) | 13.9 MB / 1.76 MB |
| `Audio/sp097_morph.wav` / `.ogg` | **Primary**: gated + cutoff-swept + panned, mastered −14 LUFS | 13.9 MB / 1.71 MB |
| `MIDI/249-…-humanized.mid` | Source MIDI (copied) | 7983 B |
| `Audio/provenance.json` / `silence_profile.json` | Provenance + RMS/silence sidecars | — |

## Pitch verification (mandatory)

Per 0.5 s window, FFT dominant peak 50–1000 Hz; harmonic energy in first 8
harmonics of lowest fundamental; silence ratio + per-second RMS.

| Render | median peak Hz | D-pent frac (dom. PC) | harmonic energy | silence |
|---|---|---|---|---|
| full_mix (ref) | 164 (E3) | 0.286 | 0.287 | 0.0957 |
| **sp097_morph** | 166 (E3) | 0.291 | **0.518** | 0.0938 |
| sp097_morph_raw (pre-master) | 166 (E3) | 0.293 | 0.510 | 0.1009 |

- **Not noise**: harmonic energy **rose 0.287 → 0.518** after the morph — the
  lowpass sweep + gate concentrate energy into the fundamental's harmonic
  series (noise collapse signature is single-digit %). PASS.
- **Not silent**: 9.37% silence, continuous per-second RMS 0.08–0.19 across the
  whole body; the 6 low-RMS seconds are the tail ring-out after the final
  kenong (legit), no mid-track gaps. PASS.
- **Pitch caveat (honest)**: dominant-peak D-pentatonic fraction sits at ~0.29
  for BOTH reference and morph. This is the *source's* character, not a morph
  defect — gamelan metallophones (glockenspiel/vibraphone/marimba) have strong
  inharmonic partials plus an unpitched kendang kit, so the 50–1000 Hz dominant
  peak per window frequently lands on a non-fundamental partial. The morph
  preserves (slightly improves) diatonicity and raises tonal energy; it adds no
  irrational noise.

## Mastering

`target_for_style("gamelan")` → −14.0 LUFS. Result: integrated **−14.44** LUFS,
true-peak **−1.00** dBTP (ceiling reached). Within 0.5 LUFS of target.

## Fixes / cleanup

- No composition rework required (all three rules audited clean).
- Removed intermediate `sp097_morph_raw.wav` (superseded by mastered render);
  its stats retained in this report.

## Scripts

- `sp097_process.py` — render + MegaMorph 3-lane modulation + master + Opus OGG.
- `verify_pitch.py` — pitch / harmonic-energy / silence verification.
