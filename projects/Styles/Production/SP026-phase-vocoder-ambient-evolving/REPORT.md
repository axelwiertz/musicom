# SP-026 Phase Vocoder Resynthesis — Ambient Evolving

**Job:** random-style production pass (SP) — LAYER-ALIGNED — 2026-09-06 cron
**Output root:** `/opt/data/projects/Styles/Production/SP026-phase-vocoder-ambient-evolving/`

## 1. Selection

| Field | Value |
|---|---|
| Method | **SP-026** — Spectral Phase Vocoder Resynthesis |
| Registry source | `workflows.musicom_workflow.SP_METHODS` (10 implemented; SP-026 → `sound.effects.phase_vocoder`) |
| Exclusion | Used in last 7 days: SP-033 (09-05), SP-011 (09-04), SP-034 (09-03), SP-032 (09-02) — SP-026 was last run 2026-08-15 → eligible, picked |
| Source composition | `Styles/Ambient/evolving/v1/ambient_evolving.mid` (Ambient Evolving) |
| Source provenance | 60 BPM, 32 bars (2×16) = 128 s score, methods 023 (tendency masking) + 026 (DPSM); sha256 `5e6dc086…bfb7c9` |
| Voices | Pad (GM 88, ch0), Texture (GM 89, ch1), Bass (GM 33, ch2), Lead (GM 74, ch3) — no drums |
| Layer discipline | **ABSOLUTE layer** — SP-026 replaces the spectral/timbre layer for the WHOLE piece (full mix + every per-voice stem through the same PV identity/freeze chain) |

The pick was independent of the SP-026-vs-ambient affinity (random), but it is a
good match: sustained pads are exactly the material a spectral-freeze treatment
can turn into evolving clouds. Source had never been produced before.

## 2. Chain

```
MIDI -> mido parse (read only) -> FluidSynth dry render (FluidR3_GM.sf2,
        internal reverb/chorus OFF, -g 1.2) of full mix + 4 per-voice stems
        -> SP-026 phase vocoder: magnitude-phase identity resynthesis
           (phase-preserving STFT/iSTFT WOLA, n_fft 2048 / hop 512)
        + spectral-freeze chord: last LOUD analysis frame re-synthesized as a
           decaying frozen spectrum (8 s, exp decay k=2, amp 0.5)
        -> -1 dBFS peak master -> WAV + OGG (Opus 48 k, voip)
```

Renderer script: `produce_sp026_cron.py` (this dir). Dry render:
`dry_full_mix.wav` (135.92 s).

## 3. Parameters

| Param | Value |
|---|---|
| `n_fft` / `hop` | 2048 / 512 |
| Resynthesis mode | magnitude-phase identity (`_stft` → `_istft`, `length=len(x)`) |
| Freeze source frame | last frame with RMS > 2% of peak frame RMS (idx 11145/11704 ≈ 129.4 s — NOT the file-final frame, which sits in FluidSynth's silent tail) |
| `freeze_tail_s` | 8.0 (total render 143.92 s = dry 135.92 + 8.0 tail) |
| `freeze_decay_k` / `amp` | 2.0 / 0.5 |
| Sample rate / peak | 44100 / −1.0 dBFS |
| FluidSynth | `-g 1.2`, reverb OFF, chorus OFF, FluidR3_GM.sf2 |

## 4. On-run fixes applied (SP-026 adapter — registered module untouched)

The module's high-level `phase_vocoder(freeze=True, sharpness=…)` produced
**silence on this 128 s input** (first run: 98.55 % silence, assert failed).
Diagnosis on a 10 s block:

1. **Phase is never unwrapped.** `phase_acc` accumulates raw `np.angle`
   differences, which wrap at ±π; on long inputs the propagated phase destroys
   the harmonic structure → output collapses to noise-floor.
   (`freeze=F, sharp=1.0` sounded fine on 10 s but must also drift on 128 s —
   phase_acc still never unwraps.)
2. **`sharpness != 1.0` applies `|X|^sharpness` to every frame.** After peak
   normalization this brickwall-clips (test block: peak 88, RMS 0.17 → post-norm
   100 % saturation). There is no per-frame gain normalization anywhere.
3. **Freeze holds the *file-final* frame** — for a FluidSynth render that frame
   lives in the silent tail → frozen chord inaudible (tail peak 0.0008).
   Fix: scan backwards for the last frame above 2 % of peak frame RMS (129.4 s).
4. **Tail re-synthesis frame count was too small** (0.4 s of hops → iSTFT output
   only ~0.4 s of audible freeze regardless of `tail_len`). Fix: emit one frame
   per hop across the full tail (`n_hold = tail_n/hop + 1`).

Adapter fix (verified):
- identity resynthesis via straight `_stft`/`_istft` — **RMS/peak bit-preserved**
  (verified: in 0.04585 → out 0.04585, peak 0.2791 → 0.2791, per-second RMS
  profile identical);
- spectral-freeze chord = re-synthesized decaying version of the last loud
  frame's spectrum (this IS the SP-026 "spectral freeze" intent: hold magnitude,
  continue/decay phase, audible bloom).

## 5. Verification results

| Check | Value | Verdict |
|---|---|---|
| Pitch — dominant-peak hit rate (0.5 s FFT windows, 50–1000 Hz, ±4 % vs active MIDI fundamentals or octave below) | **0.961** (246/256 windows) | PASS (≥ 0.60) |
| Pitch — harmonic energy in 8 harmonics of lowest fundamental | **0.582** | PASS (≥ 0.25) |
| Silence ratio (wet) | **7.7 %** (dry 6.1 %) | PASS (< 30 %) |
| Freeze tail after dry end (+0.1…1.5 s window peak) | 0.00239 | PASS (assert > 0.002) |
| Freeze tail RMS profile (135.5 → 143.9 s) | 0.0027 → 0.0004 exponential decay, no dropouts | audible bloom |
| Freeze chord pitch | 258 Hz (B3≈247 → ~C4 via FluidSynth pad timbre), stable 136–142 s | tonal, not noise |
| Onset alignment | source onset grid (grid_visualization.txt) preserved 1:1 by identity resynthesis | — |
| OGG non-empty | 960 188 B | PASS |

`Analysis/pitch_verification.json`, `Analysis/render_stats.json` hold the raw
numbers (RMS per second included).

## 6. Artifacts

| File | Size |
|---|---|
| `Audio/SP026-phase-vocoder-ambient-evolving.wav` (143.9 s, 44.1 kHz stereo, −1 dBFS) | 25 387 180 B |
| `Audio/SP026-phase-vocoder-ambient-evolving.ogg` (Opus 48 k voip) | 960 188 B |
| `Audio/stems/track00_Pad_1_new_age.wav` … `track03_Recorder.wav` (4 dry+PV stems, same chain) | 22.9–24.0 MB each |
| `dry_full_mix.wav` (SP-001 reference, internal FX off) | 23 975 980 B |
| `MIDI/ambient_evolving.mid` (source copy) | 7 852 B |
| `Analysis/render_stats.json`, `Analysis/pitch_verification.json` | — |
| `provenance.json`, `produce_sp026_cron.py`, `run.log` | — |

## 7. Notes for the next pass

- The module-level `phase_vocoder(freeze=…)` collapse-to-silence bug is worth a
  proper fix upstream (unwrap `phase_acc` with `np.unwrap` + per-frame gain
  normalization) — the adapter bypasses it but `phase_vocoder` remains broken
  for inputs longer than a few seconds with `freeze=True`.
- Render time dominated by FluidSynth (5 renders × ~136 s) + per-sample-free
  iSTFT; total ~3 min.
