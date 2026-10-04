# SP-021 BINAURAL HRTF SPATIALIZATION — 001-ragtime-maple-leaf

**Date (UTC):** 2026-10-04 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP021-binaural-ragtime-maple-leaf/`
**Status:** PASS — pitch hit 64/64 (1.0000), harmonic energy 0.3155, ACF 3/17 unpitched, silence 4.34%, LUFS -14.29, peak 0.8913.

---

## 1. Method + Selection (Which Registry Source)

| Field | Value |
|---|---|
| Method | **SP-021** — Binaural HRTF Spatialization |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT stale ranges) |
| Registered module | `sound.synthesis.binaural` (provides `HaasDelay`, `BinauralSynth`); adapter not wired in `produce()` → per-voice Woodworth-Schlosberg spatializer implemented directly per the module concept |
| Registry entries at pick time | **38 implemented:** SP-001, 011, 021, 024, 026, 028, 032–037, 069–086, 090–092, 094–098 |
| Already used last 7d (excluded) | SP-070, SP-072, SP-075, SP-079, SP-081, SP-083, SP-086 |
| Baseline excluded | SP-001 (FluidSynth reference, always available) |
| Eligible pool | **30 implemented methods** |
| Selection | `random.seed(20261004); random.choice(sorted(pool))` → **SP-021** |
| MIDI pool | 320 candidates under `Styles/` (excl. `Production/` + `phase1`); deterministic seeded pick → `Styles/Ragtime/001-ragtime-maple-leaf/MIDI/ragtime-maple-leaf.mid` |
| Selection record | `Scripts/select_job_20261004.py` + `.selection_cron.json` |

---

## 2. Source Composition

| Field | Value |
|---|---|
| Project | `Styles/Ragtime/001-ragtime-maple-leaf/` (ragtime boom-chick study, project 001) |
| MIDI | `ragtime-maple-leaf.mid` (copied to output root; source 6.0 KB) |
| Content | **C major** ragtime, 120 BPM, 4/4, 16 bars (30720 ticks = 480 tpb × 64 beats): track1 `PianoLH` (ch0, GM1) boom-chick bass root F1–G3 + chord stabs = 164 note events; track2 `PianoRH` (ch1, GM1) ragged syncopated melody C4–C5 = 64 events; track3 `Banjo` (ch2, GM105) 16th-note counter-rolls C4–D5 = 256 events. **484 pitched note events total**, no channel-9 percussion. |
| Cadence | I (C) → IV (F) → V (G) → C, boom-chick left hand |
| Why this source | A three-voice texture (bass anchor + lead melody + plucked counter-roll) is the ideal carrier for a *spatialization* layer — SP-021 writes no new notes, it positions each voice in a binaural soundstage with inter-aural time/level differences |

---

## 3. Layer Discipline (Absolute)

SP-021 is a **spatialization layer**, not a synthesizer. Its content layer is the **Woodworth-Schlosberg binaural model** applied to the **whole** rendered ragtime piece: each of the 3 voices is rendered mono via FluidSynth (the SP-001 acoustic carrier), then positioned with a unique azimuth + distance and summed to a stereo binaural image. No new notes are written; only inter-aural time/level/spectral cues are sculpted.

```
ragtime-maple-leaf.mid
 -> split into 3 per-voice MIDI (tempo track + channel-remapped data track)
 -> FluidSynth mono render per voice (reverb/chorus OFF; SP-001 reference carrier)
 -> SP-021 Woodworth-Schlosberg per voice:
      ITD:  tau = (head_radius/c) * (sin|az| + |az|), head_radius=0.0875 m, c=343 m/s
            -> fractional sample delay on the ear toward the source
      ILD:  head-shadow lowpass fc = 1000 + 19000*((1+cos az)/2)^2 Hz on the far ear
      dist: attenuation 1/distance (ref 1.0 m)
 -> stereo sum -> peak 0.89 -> normalize_to_lufs(-14) -> Limiter(-1 dB) LAST
 -> SP021-binaural-ragtime-maple-leaf.wav + .ogg (Opus 48k voip)
 -> stems: per-voice mono (source) + per-voice binaural stereo
 -> pitch verification + silence/RMS on the wet mix
```

### SP-021 parameters

| Field | Value |
|---|---|
| seed | `20261004` (deterministic selection) |
| head radius | 0.0875 m |
| speed of sound | 343.0 m/s |
| ILD filter | first-order lowpass, fc 1000–20000 Hz, exponent p=2.0 |
| PianoLH | azimuth 0.0 rad (0.0°, center), distance 1.30 m — boom-chick bass/chord anchor |
| PianoRH | azimuth +0.55 rad (+31.5°, right-front), distance 1.00 m — ragged lead melody |
| Banjo | azimuth -0.65 rad (-37.2°, left), distance 1.10 m — 16th counter-rolls |

### Binaural proof

The three voices resolve to a wide, stable soundstage: PianoLH dead-center (ITD=0 at az 0), PianoRH right (right-ear delay 0 + far-ear lowpass on left), Banjo left (left-ear delay 0 + far-ear lowpass on right). Per-voice L/R peak pairs confirm symmetry (center voice L≈R 0.769/0.769; offset voices carry head-shadow attenuation on the far ear).

---

## 4. Pitch / Tonal-Content Verification — **PASS**

Checked on the delivered wet mix (read back from WAV) vs. active MIDI pitches (484 pitched notes):

| Metric | Wet Mix | Gate | Verdict |
|---|---|---|---|
| Mix FFT hit (0.5 s windows, 50–2000 Hz, ±4% vs fund ×1/×2/×3//2) | **64/64 = 1.0000** | ≥ 0.60 | PASS |
| Harmonic energy (8 harmonics of lowest fund) | **0.3155** | ≥ 0.30 | PASS |
| ACF unpitched (every-2nd 1 s, conf < 0.30) | **3/17 = 0.176** | < 50% | PASS |
| Lowest MIDI notes seen | 29 (F1), 31 (G1), 36 (C2) — bass roots | — | Sane |

The SP-035 failure signature (0 Hz frames + broadband noise) is **absent**. Every 0.5 s window carries a tonal peak matching an active MIDI fundamental or its octave. The binaural model (fractional delay + far-ear lowpass) is linear and does not remove fundamentals, so tonal content survives the spatialization.

---

## 5. Silence / RMS Profile + Level

| Metric | Wet | Dry (source) | Note |
|---|---|---|---|
| Silence (<0.001) | **4.34%** | 5.97% | Busy ragtime; continuous piano + banjo, no mid-track gaps |
| Peak / LUFS | **0.8913 / -14.29 LUFS** | — | Limiter(-1 dBFS) applied last |
| Duration | 34.71 s | 43.92 s (dry tail) | — |
| RMS profile | recorded in render_stats.json | — | steady pluck texture |

Silence is *lower* than the dry source (4.34% vs 5.97%) because the three spatially-summed voices overlap more continuously than the dry reference; no mid-track dropout. The dry full-mix renders 43.92 s because the source MIDI's fluidsynth tail is long; the wet mix is trimmed to the 34.71 s common voice length (32 s music + 2.7 s release), which captures every pitched note (all end ≤ 32 s).

---

## 6. Fixes & Discoveries During Run

- **None required.** The source tpb=480 did not need rescaling — SP-021 writes no MIDI, it renders the source (and per-voice splits) and operates on audio only.
- Confirmed SP-021's adapter is **not wired** in `workflows.musicom_workflow.produce()`, so the Woodworth-Schlosberg model was implemented directly in the cron script (per the SP-021 concept: ITD fractional delay + ILD head-shadow lowpass).
- Because each voice uses a **constant** azimuth, the spatializer reduces to constant fractional delay + constant first-order lowpass (vectorized via `scipy.signal.lfilter`), rather than the per-sample loop of earlier SP-021 runs — faster and numerically identical.
- Source `PianoLH` track has one un-terminated note (note 36 at tick 30720, no note_off); it decays inaudibly and does not affect pitch/silence metrics.

---

## 7. Artifacts

| Artifact | Path | Size |
|---|---|---|
| Wet mix WAV | `SP021-binaural-ragtime-maple-leaf.wav` | 6,123,564 B (34.71 s) |
| Wet mix OGG (Opus 48k voip) | `SP021-binaural-ragtime-maple-leaf.ogg` | 238,000 B |
| Dry reference mix (SP-001, source) | `dry_full_mix_sp001_reference.wav` | 7,747,116 B |
| Source MIDI (copy) | `ragtime-maple-leaf.mid` | 6,035 B |
| Per-voice split MIDI | `MIDI/voice_pianolh.mid`, `voice_pianorh.mid`, `voice_banjo.mid` | 3.4/0.6/2.1 KB |
| Mono stems (source) | `Audio/stems_mono/pianolh_mono.wav`, `pianorh_mono.wav`, `banjo_mono.wav` | 6.1/6.1/7.7 MB |
| Binaural stems (per voice) | `Audio/stems_binaural/{pianolh,pianorh,banjo}_binaural.wav` | 6.1 MB each |
| Renderer script | `Scripts/produce_sp021_cron.py` | 17,935 B |
| Selection script | `Scripts/select_job_20261004.py` + `.selection_cron.json` | — |
| Verification JSON + grid | `Analysis/pitch_verification.json`, `Analysis/render_stats.json`, `Analysis/grid_visualization.txt` | — |
| Provenance | `provenance.json` | — |
| Report | `REPORT.md` | this file |

---

## 8. Quality gate

- Wet WAV + OGG exist (6,123,564 B / 238,000 B, non-empty). ✅
- Pitch verification PASS (64/64 hit, he 0.3155, ACF 3/17). ✅
- Silence ratio 4.34% (no mid-track gaps). ✅
- Stems generated (per-voice mono + per-voice binaural). ✅
- Project follows numbered production naming (`Production/SP021-binaural-ragtime-maple-leaf`). ✅
- Provenance + selection record + REPORT written. ✅
