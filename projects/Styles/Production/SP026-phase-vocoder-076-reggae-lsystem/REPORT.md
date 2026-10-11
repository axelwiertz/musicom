# SP-026 Spectral Phase Vocoder Resynthesis — Reggae / 076-reggae-lsystem

**Date (UTC):** 2026-10-11 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP026-phase-vocoder-076-reggae-lsystem/`
**Status:** PASS — FFT 123/144 (hit 0.854), harmonic energy 0.455, ACF unpitched 0/36, silence 7.70%, LUFS −14.01, peak 0.8913.

---

## 1. Method + selection (which registry source)

| Field | Value |
|---|---|
| Method | **SP-026** — Spectral Phase Vocoder Resynthesis (Flanagan STFT phase-propagation time-stretch + harmonic sharpening) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT a stale `SP-001..SP-035` range) |
| Registered module | `sound.effects.phase_vocoder` → `phase_vocoder`, `time_stretch`, `spectral_freeze`, `spectral_sharpen` |
| Registry entries at pick time | **42 implemented** (SP-001 … SP-102) |
| Already used last 7d (excluded) | SP-021, SP-069, SP-080, SP-085, SP-091, SP-092, SP-098 |
| Baseline excluded | SP-001 |
| Already on this source | (none) |
| Eligible pool | 34 methods |

Selection record: `Production/.selection_cron.json`, `Analysis/select_20261011.json`,
`Production/select_job_20261011.py`.

Well-formed filter: **225 / 334** candidate MIDIs passed (normal tpb, sane note
lengths, ≥2 note tracks or a program change, 2–600 s length).

## 2. Source composition

| Field | Value |
|---|---|
| Project | `Styles/Reggae/076-reggae-lsystem/` |
| MIDI | `MIDI/076-reggae-lsystem.mid` (6422 B, copied to `MIDI/` for provenance) |
| Genre / key | Reggae (one-drop); A natural minor (pcs `{0,4,7,9,11}` — Am skank + Am/G/C bass walk) |
| Tempo | 96.00 BPM (625000 µs/beat), 480 tpb, type-1 |
| Length | 60.0 s = 24 bars × 1920 ticks = 46080 ticks |
| Voices | Percussive Organ prog17 ch0 (120 notes, Am skank) · Electric Guitar (clean) prog27 ch1 (240 notes) · Electric Bass (finger) prog33 ch2 (144 notes, Am/G/C walk) · GM drums ch9 (272 hits) |
| Source PCS (non-drum) | `[0, 4, 7, 9, 11]` — fully diatonic to A minor / C major |

## 3. Pre-flight rules-adherence gate — PASS (all three)

| Rule | Result | Evidence |
|---|---|---|
| 1. Grid sync (onsets on 8th/16th grid) | **PASS** | 0 off-grid onsets across all pitched voices (all on 120-tick 16th grid) |
| 2. Harmony (in-key AND chord-tone) | **PASS** | 0 out-of-scale notes; every non-drum note ∈ A natural minor; chord plan Am–G–C (i–VII–III) with diatonic 7th/9th extensions |
| 3. Zero-drift (equal track length) | **PASS** | all 4 note tracks end at exactly 46080 ticks |

**No rework needed** — the source is a clean rules-adherent composition. SP-026
applied directly (absolute layer). Note: track 4 runs on **channel 9** (GM drum
kit), so its program-0 marker is irrelevant — the `[0,2,6,10]` pitch-class
set it emits is the drum map (36=kick, 38=snare, 42=closed-hat, 46=open-hat),
NOT a chromatic piano line. Drums are correctly excluded from the harmony rule.

## 4. Layer discipline (absolute — phase vocoder re-synthesizes the whole mix)

SP-026 is an **absolute-layer** spectral method: the phase vocoder re-synthesizes
the **whole** mixed signal (all 4 voices together), replacing the time layer with
a Flanagan STFT phase-propagation time-stretch and re-emphasising the spectrum by
`|X|^1.12`. Pitch is preserved (phase continuity across frames); only time and
spectral tilt change. FluidSynth GM (SP-001) is the acoustic carrier (dry
reference rendered first, FX off).

```
076-reggae-lsystem.mid
 -> dry reference: fluidsynth -ni -R 0 -C 0 -g 1.2 (reverb OFF, chorus OFF, FluidR3_GM.sf2)
      dry_full_mix_sp001_reference.wav (65.02 s incl. release tail)
 -> dry stems (RenderPipeline, FX off): 4 stems (Percussive_Organ / Electric_Guitar_clean / Electric_Bass_finger / Drums)
 -> SP-026 absolute phase vocoder (same params on full mix + each stem):
      alpha=1.2 (time-stretch), sharpness=1.12, freeze=False, n_fft=2048, hop=512
      wet mix 77.97 s (65.02 x 1.2)
 -> normalize_to_lufs(-14) -> Limiter(-1 dBFS) LAST
 -> SP026-phase-vocoder-076-reggae-lsystem.wav + .ogg (Opus 48k voip)
```

## 5. Parameters

| Param | Value | Logic |
|---|---|---|
| alpha | 1.2 | Flanagan time-stretch: synthesis hop 614 = 512×1.2 → 20% slower/longer (dub-style smear) |
| sharpness | 1.12 | `mag = mag^1.12` spectral emphasis for harmonic clarity |
| freeze | **False** | disabled — see §7 fix #1 |
| n_fft / hop | 2048 / 512 | standard STFT frame |
| Key / scale | A natural minor | preserved by phase continuity |
| Master | `normalize_to_lufs(−14)` → `Limiter(−1 dB)` | measured **−14.01 LUFS**, peak 0.8913 |
| SoundFont | `discover_soundfont()` → FluidR3_GM.sf2 | ONE-ENV contract, never hardcoded |

## 6. Pitch / tonal-content verification — **PASS**

Time-stretch is linear, so source note times were mapped by ×1.2 for the wet
comparison. Checks on the delivered WAV:

| Metric | Wet mix | Gate | Verdict |
|---|---|---|---|
| FFT hit rate (0.5 s windows, dominant peak vs active MIDI note ×1/2/3/4/½/⅓, ±4%) | **123/144 = 0.854** | ≥ 0.60 | PASS |
| Mean harmonic energy (8 harmonics of dominant peak) | **0.4553** | ≥ 0.25 | PASS |
| ACF unpitched windows | **0 / 36** | < 0.50 | PASS (no broadband noise) |
| Median dominant frequency | 438.0 Hz (A4) | — | tonic A dominates the mix, as expected |

The SP-035 failure signature (0 Hz frames + single-digit harmonic energy +
broadband ACF) is **absent**. Harmonic energy 0.455 confirms the phase vocoder
preserved tonal content through re-synthesis — no smearing into noise.

Full JSON: `Analysis/pitch_verification.json`, `Analysis/render_stats.json`.

## 7. Fixes & discoveries during run

1. **`freeze=True` is broken (decay-tail off-by-semantics).** The module's freeze
   branch applies its exponential-decay envelope to `y[tail_len*sr:]`, i.e. from
   **2 s to the end** of the output. For a 60 s source that would suppress ~97% of
   the audio. Verified empirically before the run: a steady 4 s chord (440+554+659 Hz)
   rendered through `phase_vocoder(..., freeze=True)` had RMS fall 0.54 → 0.36 →
   0.19 → 0.03 across its first four seconds (constant input, so it must stay flat).
   Fix: **freeze=False**, using the pure Flanagan time-stretch + `|X|^1.12` sharpen
   path, which is well-defined and pitch-preserving. Reported as a module bug for
   `musicom-engine-maintenance`.
2. **Channel-9 drum track misread risk.** Track 4 carries `program 0` on channel 9;
   a naive pitch-class audit flags it as a "chromatic piano line" (`{0,2,6,10}` =
   C, D, F♯, A♯). It is in fact the GM drum kit (36/38/42/46). Drums are excluded
   from the harmony rule on channel identity, not program number.

## 8. Silence / RMS profile

| Metric | Value | Note |
|---|---|---|
| Silence (<0.001) | **7.70%** | all in the stretched tail; no mid-track gaps |
| RMS | 0.1449 | — |
| Peak / LUFS | 0.8913 / −14.01 | mastered |
| Wet duration | 77.97 s | 65.02 s dry × 1.2 |

Only 7.70% silence confirms the time-stretch closed the source's sparse moments
rather than adding dead air; the reggae one-drop groove reads continuous.

## 9. Artifacts

| Type | Path | Size |
|---|---|---|
| Master WAV | `SP026-phase-vocoder-076-reggae-lsystem.wav` (77.97 s, 44.1 kHz stereo) | 13,754,468 B |
| Master OGG | `SP026-phase-vocoder-076-reggae-lsystem.ogg` (Opus 48k voip) | 594,965 B |
| Dry reference | `dry_full_mix_sp001_reference.wav` | 11,468,844 B |
| Source MIDI (copy) | `MIDI/076-reggae-lsystem.mid` | 6,422 B |
| Dry stems | `Audio/stems_dry/track0{0,1,2,3}_*.wav` (4) | ~10.9–11.5 MB each |
| Wet stems | `Audio/stems_wet/track0{0,1,2,3}_*_PV.wav` (4) | ~13.1–13.8 MB each |
| Renderer | `Scripts/produce_sp026_cron.py` | — |
| Verification JSON | `Analysis/pitch_verification.json`, `Analysis/render_stats.json` | — |
| Onset DNA grid | `Analysis/grid_visualization.txt` | — |
| Selection JSON | `Analysis/select_20261011.json` | — |
| Provenance | `provenance.json` | — |
| Report | `REPORT.md` | this file |

WAVs git-ignored by policy; OGG + MIDI + JSON + REPORT tracked.

## 10. Quality gate

- [x] MIDI present for the audio render (`MIDI/076-reggae-lsystem.mid`)
- [x] OGG non-empty (≈581 KB) and playable-length (77.97 s)
- [x] Pitch verification run and reported (PASS: FFT 0.854, HE 0.455, ACF 0/36)
- [x] Silence ratio + RMS measured; 7.70% silence all in tail, no mid-track gaps
- [x] Full mix WAV + per-track stems (RenderPipeline)
- [x] `provenance.json` per artifact set (incl. freeze-bug fix record)
- [x] Output under `projects/Styles/Production/<method>-<project>/`
- [x] No hardcoded soundfont (`discover_soundfont` → FluidR3_GM.sf2)
- [x] Pre-flight three-rule gate audited and PASS (0 off-grid / 0 out-of-scale / zero-drift)
