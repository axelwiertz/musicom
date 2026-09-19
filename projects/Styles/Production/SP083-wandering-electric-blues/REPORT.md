# SP-083 WANDERING (Non-LFO Wandering Engine + Portal + Drift Clouds Voice) — 039-electric-blues

**Date (UTC):** 2026-09-19 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP083-wandering-electric-blues/`
**Status:** PASS — mix FFT 116/120 (0.9667), harmonic energy 0.3071, ACF 0/31 unpitched, silence 4.12%, LUFS -14.00, peak 0.8913.

---

## 1. Method + Selection (Which Registry Source)

| Field | Value |
|---|---|
| Method | **SP-083** — Non-LFO Wandering Engine + Portal + Drift Clouds Voice (Sound Dust-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT stale ranges) |
| Registered module | `sound.modular.wandering` → `WanderingEngine`, `Portal`, `DriftCloudsVoice` |
| Registry entries at pick time | **30 implemented:** SP-001, 011, 021, 024, 026, 028, 032–037, 069–086 |
| Already used last 7d (excluded) | SP-084 (09-17), SP-072 (09-16), SP-074 (09-15), SP-036 (09-14), SP-021 (09-14), SP-073 (09-13), SP-071 (09-12) |
| Eligible pool | **23 implemented methods** |
| Selection | `random.Random(20260919).choice(pool)` → **SP-083** (first SP-083 production run; module registered 2026-09-17 scan, never produced until tonight) |
| MIDI pool | 292 candidates under `Styles/` (excl. `phase1` + `Production`), 285 usable (>40 B); deterministic seeded pick → `Blues/039-electric-blues/daily-2026-06-27_blues_039-electric-blues-unitmatrix.mid` |
| Selection record | `Analysis/select_20260919.json` and `.selection_cron.json` |

---

## 2. Source Composition

| Field | Value |
|---|---|
| Project | `Styles/Blues/039-electric-blues/` (Electric Blues, UnitMatrix structure) |
| MIDI | `daily-2026-06-27_blues_039-electric-blues-unitmatrix.mid` (copied to output `MIDI/`; 4514 B) |
| Tempo / grid | 80 BPM (750000 µs/beat), tpb 480; 60.00 s music, 38400 ticks (20 bars) |
| Form | Intro 2 \| Verse1 4 \| Verse2 4 \| Chorus 4 \| Solo 4 \| Outro 2 = 20 bars, A minor / blues hexatonic |
| Voices | Lead Guitar GM30 ch0 (**224 notes**, MIDI 52–71, power chug & solos) · Bass GM33 ch0 (**40 notes**, MIDI 45–59, 12-bar blues roots) · Drums ch9 (**288 notes**, kick/snare/hat 36–42) |
| Texture | Driving 80 BPM power chug blues rhythm with soaring solo lines and steady backbeat |
| Why this source | Perfect test bed for the Sound Dust Drift Clouds architecture: rich guitar harmonics and steady bass line can be transformed via wonky wander modulation, filter sweeps, and layer balance shifts without sacrificing blues drive |

Grid (`Analysis/grid_visualization.txt`, 1920 ticks/char): All 3 voices 100% density across all 20 measures.

---

## 3. Layer Discipline (Absolute)

SP-083 is an **absolute-layer modulation and dual-partial voice synthesis method**: `DriftCloudsVoice` (Cloud / Shadow dual partial balance driven by `WanderingEngine` and `Portal` randomized matrix) processes all stems across the entire composition.

```
daily-2026-06-27_blues_039-electric-blues-unitmatrix.mid
 -> dry reference: fluidsynth -ni -g 1.2 (reverb OFF, chorus OFF, FluidR3_GM.sf2)
      dry_full_mix_sp001_reference.wav (10.99 MB)
 -> dry stems (RenderPipeline extraction, FX off):
      track00_Overdriven_Guitar / track01_Electric_Bass_finger / track02_Drums
 -> SP-083 Wandering Engine + DriftCloudsVoice:
      Cloud (dry) + Shadow (time-slipped micro-layer) ->
      WanderingEngine (nested 4-timescale speed walk, ebb/flow stalls) ->
      Portal (surprise-mutated routes to filter_cutoff, pan, eq_tilt) ->
      per-stem peak-norm 0.89 -> trackXX_*_WANDERING.wav
 -> master bus sum -> peak-norm 0.89 -> normalize_to_lufs(-14) -> Limiter(-1 dB) LAST
 -> SP083-wandering-electric-blues.wav + .ogg (Opus 48k voip)
```

### Voice Profiles (Wandering / Portal Design)

| Voice | GM / Ch | Cloud Drift | Shadow Drift | Mod Wheel | Delay Shift | Routes & Surprise |
|---|---|---|---|---|---|---|
| Lead Guitar | GM30 (Overdriven Guitar) | 1.00 | 0.40 | 0.65 | 180 smp | drift→filter (0.45), drift→pan (0.50), portal→eq_tilt (0.30); surprise=0.30 |
| Bass | GM33 (Electric Bass finger) | 0.50 | 0.20 | 0.50 | 300 smp | drift→filter (0.25), drift→pan (0.15); surprise=0.10 |
| Drums | GM Perc (Channel 9) | 0.60 | 0.25 | 0.70 | 80 smp | drift→pan (0.35), drift→filter (0.20); surprise=0.20 |

---

## 4. Pitch / Tonal-Content Verification — **PASS**

Checked on delivered wet mix audio:

| Metric | Wet Mix | Gate | Verdict |
|---|---|---|---|
| Mix FFT hit (0.5 s windows, 50–2000 Hz, ±4% vs fund ×1/×2/×3/×4//2) | **116/120 = 0.9667** | ≥ 0.60 | PASS |
| Median harmonic energy (8 harmonics of lowest fund) | **0.3071** | ≥ 0.30 | PASS |
| ACF unpitched (every-2nd 1 s, conf<0.30) | **0/31 = 0.000** | < 50% | PASS |
| Lowest MIDI notes seen | 45 (A2), 48, 50, 52, 55, 57 — blues bass roots | — | Sane |
| Median dominant peak | 110.0 Hz (A2 fundamental) | — | Clean |

The SP-035 failure signature (0 Hz frames + broadband noise) is **absent**.

---

## 5. Silence / RMS Profile + Level

| Metric | Wet | Note |
|---|---|---|
| Silence (<0.001) | **4.12%** | Tight blues rhythm, smooth intro/outro tails |
| Peak / LUFS | **0.8913 / -14.00 LUFS** | Limiter(-1 dBFS) applied last |
| RMS profile | ~0.15–0.24 active, no mid-track dropouts | Continuous groove across all 20 bars |

---

## 6. Fixes & Discoveries During Run

1. **Stem Alignment & Time Sync**: MIDI tracks rendered with different tail lengths by FluidSynth CLI. Padded all stem arrays to the exact maximum frame length (2,749,248 samples = 62.34 s) before summing to ensure zero timing drift.
2. **Channel 9 GM Drums Extraction**: Standardized drum stem naming using `track02_Drums` rather than acoustic grand piano mislabel.
3. **Portal Modulation Matrix Invariants**: Ensured route parameters stay clipped within [0, 1] after `surprise()` mutations, maintaining stable filter cutoffs and pan ranges.

---

## 7. Artifacts

| Artifact | Path | Size |
|---|---|---|
| Full mix WAV | `SP083-wandering-electric-blues.wav` | 10,997,036 B |
| Full mix OGG (Opus 48k voip) | `SP083-wandering-electric-blues.ogg` | 473,766 B |
| Dry reference mix (SP-001) | `dry_full_mix_sp001_reference.wav` | 10,997,036 B |
| Source MIDI (copy) | `MIDI/daily-2026-06-27_blues_039-electric-blues-unitmatrix.mid` | 4,514 B |
| Dry stems | `Audio/stems_dry/track00..02.wav` | ~10.9 MB each |
| Wet stems (peak 0.89) | `Audio/stems_wet/track00..02_WANDERING.wav` | 10,997,036 B each |
| Renderer script | `Scripts/produce_sp083_cron.py` | 12,521 B |
| Verification JSON + grid | `Analysis/pitch_verification.json`, `Analysis/render_stats.json`, `Analysis/grid_visualization.txt` | — |
