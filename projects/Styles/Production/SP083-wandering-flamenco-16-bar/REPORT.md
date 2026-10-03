# SP-083 WANDERING ENGINE + PORTAL + DRIFT CLOUDS — 023-flamenco-16-bar

**Date (UTC):** 2026-10-03 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP083-wandering-flamenco-16-bar/`
**Status:** PASS — pitch hit 48/48 (1.0000), harmonic energy 0.4327, ACF 0/13 unpitched, silence 11.44%, LUFS -14.30, peak 0.8913.

---

## 1. Method + Selection (Which Registry Source)

| Field | Value |
|---|---|
| Method | **SP-083** — Non-LFO Wandering Engine + Portal + Drift Clouds Voice (Sound Dust-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT stale ranges) |
| Registered module | `sound.modular.wandering` → `WanderingEngine`, `Portal`, `ModRoute`, `DriftCloudsVoice`, `DEFAULT_DESTINATIONS` |
| Registry entries at pick time | **38 implemented:** SP-001, 011, 021, 024, 026, 028, 032–037, 069–086, 090–092, 094–098 |
| Already used last 7d (excluded) | SP-024, SP-070, SP-072, SP-075, SP-079, SP-081, SP-086 |
| Baseline excluded | SP-001 (FluidSynth reference, always available) |
| Eligible pool | **30 implemented methods** |
| Selection | `random.seed(20261003); random.choice(sorted(pool))` → **SP-083** (first SP-083 production run; adapter not wired in `produce()` → module API called directly) |
| MIDI pool | 317 candidates under `Styles/` (excl. `Production/` + `phase1`); deterministic seeded pick → `Styles/Flamenco/023-flamenco-16-bar/MIDI/flamenco_v2.mid` |
| Selection record | `Scripts/select_job_20261003.py` + `.selection_cron.json` |

---

## 2. Source Composition

| Field | Value |
|---|---|
| Project | `Styles/Flamenco/023-flamenco-16-bar/` (Flamenco 16-bar study, project 023) |
| MIDI | `flamenco_v2.mid` (copied to output root; source 3.1 KB) |
| Content | **E Phrygian** flamenco: track1 melody nylon-guitar (GM24, ch0) E4–C5 = 52 notes; track2 harmony/bass nylon-guitar (GM24, ch0) E2–A4 = 64 notes; track3 ch9 percussion "palo" accent (note 72) = 48 hits |
| Tempo / grid | 120 BPM (500000 µs/beat), source tpb **10080** (= 480 × 21), 3/4 meter, ~12.5 bars |
| Cadence | Andalusian: Am–G–F–E (README) |
| Why this source | A 27.6 s monophonic-lead + chordal-accompaniment piece is the ideal carrier for a *modulation* layer — SP-083 writes no new notes, it re-sculpts the rendered tone/pan/level with a non-LFO wander |

---

## 3. Layer Discipline (Absolute)

SP-083 is a **modulation/effect layer**, not a synthesizer. Its content layer is the **non-LFO Wandering Engine + surprised Portal matrix**, applied to the **whole** rendered flamenco piece via a Cloud/Shadow two-band split (the "Drift Clouds" two-partial concept). FluidSynth GM render is the acoustic carrier only (the SP-001 reference), not a competing production layer.

```
flamenco_v2.mid
 -> FluidSynth dry render (SP-001 reference, reverb/chorus OFF)
 -> Cloud band = SVF highpass 350 Hz (melody + guitar highs)
    Shadow band = SVF lowpass 350 Hz (bass + harmony body)
 -> SP-083 machinery:
    WanderingEngine(rate=0.35, wobble=0.5, stall_prob=0.30, stall_len=0.8, slew=0.5)
      -> non-LFO "wonky" CV that ebbs/flows/slews/near-halts (no fixed frequency)
    WanderingEngine #2 (rate=0.18) -> independent pan wander
    Portal(routes: drift->filter_cutoff 0.40, drift->pan 0.35,
            drift->volume 0.20, portal->eq_tilt 0.15)
      -> surprise(0.4) at 4/8/12/16/20 s re-routes 2 routes each ("happy drunk")
    DriftCloudsVoice(mod_wheel=0.60) -> Cloud/Shadow layer balance 0.60/0.40
 -> block-wise (4096 smp) modulation:
    cloud SVF lp cutoff = 1500 + 6500·cv Hz (bright<->dark)
    shadow SVF lp cutoff = 180 + 900·(1-cv) Hz (complementary)
    level = 0.72 + 0.28·cv (ebb/near-halt)
    pan = (cv2 - 0.5)·0.7 + portal pan offset
 -> stereo mix -> peak 0.89 -> normalize_to_lufs(-14) -> Limiter(-1 dB) LAST
 -> SP083-wandering-flamenco-16-bar.wav + .ogg (Opus 48k voip)
 -> stems: dry (source tracks) + wet (cloud_band/shadow_band)
```

### SP-083 parameters

| Field | Value |
|---|---|
| seed | `20261003` (deterministic) |
| Cloud/Shadow band split | 350 Hz |
| mod wheel (layer balance) | 0.60 (Cloud-dominant, "the meat and potatoes") |
| WanderingEngine (drift) | rate 0.35, wobble 0.5, roughness 0.03, stall_probability 0.30, stall_length 0.8 s, slew 0.5 |
| WanderingEngine (pan) | rate 0.18, wobble 0.35, roughness 0.02, stall_probability 0.25, stall_length 1.0 s, slew 0.6 |
| Portal routes | drift→filter_cutoff 0.40, drift→pan 0.35, drift→volume 0.20, portal→eq_tilt 0.15 |
| Portal surprise | amount 0.4 at 4, 8, 12, 16, 20 s (2 routes touched each) |
| Filter | cloud SVF lp 1500+6500·cv Hz; shadow SVF lp 180+900·(1−cv) Hz |
| Level | 0.72 + 0.28·cv (ebb / near-halt) |
| Pan | (cv2−0.5)·0.7 + portal pan offset (equal-power) |

### Non-LFO proof

The WanderingEngine is not an LFO: it has no fixed frequency. Measured over the full 27.6 s render, the wander CV spans 0.014…0.961 (mean 0.519) and its **stall fraction (near-halt share) = 0.0185** — the documented "often reaching a near halt before starting back up again". The Portal re-routed itself 5 times during the piece (2 routes each), matching "a happy drunk in control of your parameters".

---

## 4. Pitch / Tonal-Content Verification — **PASS**

Checked on the delivered wet mix (read back from WAV) vs. active MIDI pitches (116 pitched guitar notes; ch9 percussion excluded):

| Metric | Wet Mix | Gate | Verdict |
|---|---|---|---|
| Mix FFT hit (0.5 s windows, 50–2000 Hz, ±4% vs fund ×1/×2/×3//2) | **48/48 = 1.0000** | ≥ 0.60 | PASS |
| Harmonic energy (7 harmonics of lowest fund) | **0.4327** | ≥ 0.30 | PASS |
| ACF unpitched (every-2nd 1 s, conf < 0.30) | **0/13 = 0.000** | < 50% | PASS |
| Lowest MIDI notes seen | 40 (E2), 41 (F2), 43 (G2), 45 (A2) — harmony roots | — | Sane |
| Median dominant peak | (recorded in pitch_verification.json) | — | Clean |

The SP-035 failure signature (0 Hz frames + broadband noise) is **absent**. Every 0.5 s window carries a tonal peak matching an active MIDI fundamental or its octave, and zero windows read as unpitched. The wandering lowpass darkens but never removes fundamentals, so tonal content survives the modulation.

---

## 5. Silence / RMS Profile + Level

| Metric | Wet | Dry (source) | Note |
|---|---|---|---|
| Silence (<0.001) | **11.44%** | 11.48% | Matches source rests; modulation adds no dropout |
| Peak / LUFS | **0.8913 / -14.30 LUFS** | — | Limiter(-1 dBFS) applied last |
| Duration | 27.59 s | 27.59 s | — |
| RMS profile | recorded in render_stats.json | — | continuous pluck + ebb/flow level |

Silence is essentially identical to the dry source (11.44% vs 11.48%), proving the SP-083 level modulation (0.72–1.0×) never gates the signal to silence — no mid-track dropout.

---

## 6. Fixes & Discoveries During Run

- **None required.** The source tpb=10080 did *not* need rescaling because SP-083 writes no MIDI — FluidSynth renders the source file directly and the modulation layer operates on audio only (unlike SP-086, which had to rescale ticks to feed `UnitMatrixComposer`).
- Confirmed SP-083's adapter is **not wired** in `workflows.musicom_workflow.produce()` (raises `NotImplementedError`), so the module API (`WanderingEngine`/`Portal`/`DriftCloudsVoice`) was called directly, per the module docstring.
- `sound.effects.filter.StateVariableFilter` keeps internal state across `process()` calls, enabling a continuous time-varying wandering cutoff when applied block-wise (4096 samples).

---

## 7. Artifacts

| Artifact | Path | Size |
|---|---|---|
| Wet mix WAV | `SP083-wandering-flamenco-16-bar.wav` | 4,866,348 B (27.59 s) |
| Wet mix OGG (Opus 48k voip) | `SP083-wandering-flamenco-16-bar.ogg` | 211,392 B |
| Dry reference mix (SP-001, source) | `dry_full_mix_sp001_reference.wav` | 4,866,348 B |
| Source MIDI (copy) | `flamenco_v2.mid` | 3.1 KB |
| Dry stems (source) | `Audio/stems_dry/track00_Acoustic_Guitar_nylon.wav`, `track01_Acoustic_Guitar_nylon.wav`, `track02_Drums.wav` | — |
| Wet stems (Drift Clouds bands) | `Audio/stems_wet/cloud_band.wav`, `Audio/stems_wet/shadow_band.wav` | — |
| Renderer script | `Scripts/produce_sp083_cron.py` | 19,161 B |
| Selection script | `Scripts/select_job_20261003.py` + `.selection_cron.json` | — |
| Verification JSON + grid | `Analysis/pitch_verification.json`, `Analysis/render_stats.json`, `Analysis/grid_visualization.txt` | — |
| Provenance | `provenance.json` | — |
| Report | `REPORT.md` | this file |

---

## 8. Quality gate

- Wet WAV + OGG exist (4,866,348 B / 211,392 B, non-empty). ✅
- Pitch verification PASS (48/48 hit, he 0.4327, ACF 0/13). ✅
- Silence ratio 11.44% (matches source, no mid-track gaps). ✅
- Stems generated (dry source tracks + cloud/shadow wet bands). ✅
- Project follows numbered production naming (`Production/SP083-wandering-flamenco-16-bar`). ✅
- Provenance + selection record + REPORT written. ✅
