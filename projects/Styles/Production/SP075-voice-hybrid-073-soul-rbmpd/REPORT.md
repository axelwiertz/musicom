# SP-075 Voice-Like Instrument Hybrid Render — 073-soul-rbmpd

**Job:** random-style production (SP methods) — LAYER-ALIGNED
**Date (UTC):** 2026-11-15  **Seed:** 20261115
**Status:** PASS — FFT hit 1.0000, harmonic energy 0.9834 (≥ 0.25), ACF
unpitched 0/32, silence 1.10%, LUFS −13.00, true peak −1.78 dBTP,
zero-drift clean after rework.

---

## 1. Method + selection (which registry source)

| Field | Value |
|---|---|
| Method | **SP-075** — Voice-Like Instrument Hybrid Render (synthesized voice tracks + SoundFont backing) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT a stale `SP-001..SP-035` range) |
| Registered module | `sound.render.hybrid` → `render_hybrid`, `parse_tracks`, `voice_track_indices` |
| Voice-like engine | `sound.synthesis.voice_like` → `VoiceLikeInstrument("talkbox")` (formant voice) |
| Registry entries at pick time | 93 implemented |
| Recent excluded (7d) | SP-069, SP-084, SP-100, SP-113, SP-119, SP-138, SP-154 |
| Already on source | (none) |
| Baseline excluded | SP-001 |
| Eligible pool | 85 methods |

Selection record: `Production/select_job_20261115.py`,
`Production/.selection_cron.json`. Well-formed filter: **351 / 456**
candidate MIDIs passed; 350 with ≥3 pitch classes. Random pick (seed
20261115) landed on `Soul/073-soul-rbmpd/MIDI/073-soul-rbmpd.mid` + SP-075.

## 2. Source composition

| Field | Value |
|---|---|
| Project | `Styles/Soul/073-soul-rbmpd/` |
| MIDI | `MIDI/073-soul-rbmpd.mid` |
| Genre / key | Soul (Method 048 RBMPD — Reflected Brownian Motion Pitch Diffusion); **C natural minor** (pcs `{0,2,3,5,7,8,10}`) |
| Tempo | 92.00 BPM, 480 tpb, 4/4, type-1 |
| Length | 62.61 s = 24 bars (6 sections × 4) = 46080 ticks |
| Voices | Lead (75 Pan Flute, ch0) · Horns (61 Brass, ch1) · Rhodes (4 E.Piano, ch2) · Bass (33 E.Bass, ch3) · Drums (ch9) |
| Progression | i iv V III \| i iv V VI \| i V i VI \| i iv V i \| i iv V III \| i V iv i |

## 3. Layer discipline (absolute)

SP-075 is an **absolute-layer** production method: the whole piece is
re-realized through it. The Lead (the "singer") has no GM soundfont
equivalent, so it becomes a **talkbox** (formant voice, Peter Frampton-style
soul); Horns / Rhodes / Bass / Drums stay on the FluidSynth soundfont as the
backing band.

```
C natural minor, 92 BPM, 480 tpb, 24 bars (46080 ticks)
 -> Lead   -> talkbox (voice_like synthesis)     ch0
 -> Horns  -> FluidSynth (Brass Section 61)      ch1
 -> Rhodes -> FluidSynth (Electric Piano 4)      ch2
 -> Bass   -> FluidSynth (Electric Bass 33)      ch3
 -> Drums  -> FluidSynth (GM kit)                ch9
 -> voice_instruments = ["talkbox", None, None, None, None]
 -> render_hybrid -> mono -> master(-13 LUFS, -1 dBTP) -> WAV + Opus OGG
```

## 4. PRE-FLIGHT AUDIT (3-rule gate) + rework

The source **FAILED two of three rules**; it was reworked (two-phase,
engine-only) before the SP method was applied.

| Rule | Source (before) | After rework | Verdict |
|---|---|---|---|
| Grid sync (16th = 120 ticks) | **27003 off-grid** (all Lead) | **0** | PASS (fixed) |
| Harmony — in scale (C nat. minor) | 0 out-of-scale | **0** | PASS |
| Harmony — chord tone of bar | **4766 out-of-chord** (all Lead) | **0** | PASS (fixed) |
| Zero-drift (note tracks equal) | [46080] | **[46080]** | PASS |

**Root causes (both in the Lead voice only):**
1. **Grid** — the Lead is the raw RBMPD brownian line: onsets fired at
   **1-tick resolution** (`start_tick = int(tick)` on every diffusion step
   where `|dP/dt|` exceeded threshold). 27239 notes, ~1.7-tick spacing —
   never grid-quantized in the composition pass.
2. **Chord** — the composition's lead quantization indexed the **global**
   24-bar progression with a **section-local** bar index
   (`bar = start_tick // BAR` inside each 4-bar section → always 0..3 → the
   Intro's i-iv-V-III). Sections 2/3/5 were therefore chord-quantized against
   the wrong bars.

**Rework (two-phase, musicom engine only — no raw mido writing):**
1. Lead onset snapped to nearest **16th grid cell** (120 ticks); per-cell
   collisions merged keeping the highest-velocity note (dynamic peaks define
   the melodic contour). 27239 → **385** notes.
2. Each merged lead pitch **chord-tone quantized** against the **correct
   global per-bar chord** (register-preserving, nearest semitone).
3. Horns/Rhodes/Bass/Drums already clean → preserved exactly.
4. Re-exported via `UnitMatrixComposer` with a passing `validate()`
   zero-drift gate; original raw kept as `MIDI/073-soul-rbmpd-phase1.mid`.

After-rework audit (recorded in `MIDI/rework_audit.json`): off-grid 0,
out-of-scale 0, out-of-chord 0, zero-drift true.

## 5. Parameters

| Param | Value |
|---|---|
| engine | `talkbox` formant voice (Klatt-style vocal tract) |
| vowels | `a o e a u o` (6-vowel "singing" cycle, per-note articulation) |
| voice_gain / backing_gain | 1.0 / 1.0 |
| seed | 20261115 (per-track voice seed = seed + idx·7919) |
| bpm | 92.0 (read from MIDI tempo map) |
| sr | 44100 |
| target LUFS / ceiling | −13.0 (`target_for_style("Soul")`) / −1.0 dBTP |
| available voice-like instruments | vox_humana, kazoo, jaw_harp, didgeridoo, singing_saw, talkbox |

## 6. Render + master

| Stage | Value |
|---|---|
| Dry reference | FluidSynth `-ni -g 1.2 -r 44100 -o synth.reverb.active=no -o synth.chorus.active=no`, FluidR3_GM.sf2 |
| Hybrid | `render_hybrid` (talkbox lead synth + FluidSynth backing) |
| Master | `master(target_lufs=-13.0, ceiling_db=-1.0, sample_rate=44100)` |
| Integrated LUFS | **−13.00** |
| True peak | **−1.78 dBTP** (below −1 ceiling — correct; master is a ceiling, not a target) |
| Peak | 0.8145 |

## 7. Verification (pitch + silence + RMS + ACF)

| Metric | Value | Verdict |
|---|---|---|
| MIDI-note hit rate (0.5 s windows, 50–1000 Hz, vs expected note freqs ±4%) | **1.0000** (126 windows) | PASS (≥ 0.60) |
| Harmonic energy (first 8 harmonics of expected notes) | **0.9834** | PASS (≥ 0.25) |
| ACF unpitched windows | **0 / 32** | PASS (< 0.50) |
| Silence ratio (`|mono| < 0.001`) | **1.10 %** | tail/decay only |
| Zero-drift | [46080] × 5 tracks | PASS |

Harmonic energy 0.9834 ≫ 0.25 confirms the render is **tonal, not noise**
(the 2026-08-24 GENDYN failure mode). Pitch verification is against the
expected MIDI note frequencies (SP-075 replaces timbre, so a dry-vs-wet
spectral match is meaningless).

## 8. Fixes applied

1. **Grid-quantize the Lead** — snapped 27239 one-tick-resolution onsets to
   the 16th grid, merged per-cell (385 notes). Preserves the continuous-motion
   soul character at a musically idiomatic resolution.
2. **Chord-tone re-quantize the Lead** — snapped every merged lead pitch to
   the correct global per-bar chord (the composition's section-local bar
   indexing had quantized sections 2/3/5 against the Intro's chords).
3. **Zero-drift re-export** — re-built via `UnitMatrixComposer` +
   `validate()` gate; original raw kept as phase1 sidecar.

## 9. Artifacts

| File | Size | Role |
|---|---|---|
| `MIDI/073-soul-rbmpd.mid` | 8700 B | reworked (gate-clean) |
| `MIDI/073-soul-rbmpd-phase1.mid` | 206184 B | original raw sidecar |
| `MIDI/rework_audit.json` | — | before/after audit numbers |
| `SP075-voice-hybrid-073-soul-rbmpd.wav` | 11.2 MB | mastered full mix |
| `SP075-voice-hybrid-073-soul-rbmpd.ogg` | 446 KB | Opus 48k voip (Telegram) |
| `dry_full_mix_sp001_reference.wav` | 10.9 MB | dry FluidSynth reference |
| `Audio/stems_dry/track00_Pan_Flute.wav` … `track04_Drums.wav` | — | 5 dry per-track stems |
| `Audio/stems_wet/track00_Lead_talkbox.wav` | — | wet talkbox lead stem |
| `Audio/stems_wet/track_backing_fluidsynth.wav` | — | wet backing stem |
| `Analysis/render_stats.json` | — | LUFS/peak/silence/RMS/pitch |
| `Analysis/pitch_verification.json` | — | hit rate / harmonic energy / ACF |
| `Analysis/grid_visualization.txt` | — | track→engine→instrument map |
| `Scripts/produce_sp075_cron.py` | — | reproducible producer |
| `provenance.json` | — | full provenance sidecar |

---

*Report is the primary record. Chat summary is a short caveman digest.*
