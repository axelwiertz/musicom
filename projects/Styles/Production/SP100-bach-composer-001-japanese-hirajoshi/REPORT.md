# SP-100 B.A.C.H. Composition Generator — 001-japanese-hirajoshi

**Job:** random-style production (SP methods) — LAYER-ALIGNED
**Date (UTC):** 2026-11-14  **Seed:** 20261114
**Status:** PASS — FFT hit 1.000, harmonic energy 0.685 (≥ 0.30), silence 8.93%
(all in tail/decay), LUFS −14.00, true peak −3.96 dBTP, zero-drift clean.

---

## 1. Method + selection (which registry source)

| Field | Value |
|---|---|
| Method | **SP-100** — B.A.C.H. Composition Generator: 11 algorithmic composition engines (FUGUE/CANON/PROBA/TINTINNABULI/MINIMAL/CELLULAR/TREE/MOTIF/HYBRID/GROOVE/GROOVE_MIX), Kaona B.A.C.H.-style |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT a stale `SP-001..SP-035` range) |
| Registered module | `sound.generators.bach_composer` → `tintinnabuli`, `canon`, `fugue`, `proba`, `minimal_music`, `cellular_melody`, `tree_melody`, `motif_chain`, `hybrid`, `groove`, `groove_mix`, `compose_with` |
| Engine used | **TINTINNABULI** (Arvo Pärt-style) |
| Registry entries at pick time | 100+ implemented |
| Recent excluded (7d) | SP-069, SP-084, SP-113, SP-119, SP-138, SP-146, SP-154 |
| Already on this source | SP-105 |
| Baseline excluded | SP-001 |
| Eligible pool | 84 methods |

Selection record: `Production/.selection_cron.json`,
`Production/select_job_20261114.py`. Well-formed filter: **347 / 452**
candidate MIDIs passed (normal tpb, sane note lengths, ≥2 note tracks or a
program change, 2–600 s length); 346 with ≥3 pitch classes.

## 2. Source composition

| Field | Value |
|---|---|
| Project | `Styles/Japanese/001-japanese-hirajoshi/` |
| MIDI | `MIDI/japanese-hirajoshi.mid` |
| Genre / key | Japanese hōgaku; **D hirajoshi** (D-Eb-G-Ab-C, pcs `{0,2,3,7,8}`) |
| Tempo | 70.00 BPM, 480 tpb, 4/4, type-1 |
| Length | 54.86 s = 16 bars = 30720 ticks |
| Voices | track1 koto (prog 108 ch0, 20 notes) · track2 shakuhachi (prog 75 ch1, 48 notes) · track3 shamisen ostinato (prog 106 ch2, 128 notes) · track4 taiko (ch9, 16 hits) |

## 3. Layer discipline (absolute — generator re-composes the whole piece)

SP-100 is a **generator** method: it produces note events, not a timbral
effect. Applied as an **absolute layer**, the B.A.C.H. engine re-composes the
whole piece in the source's key (D hirajoshi) and tempo (70 BPM); no source
MIDI notes survive — only its key/tempo/genre context is inherited (same
convention as the SP-098 fractal-seq generator run).

```
D hirajoshi, 70 BPM, 480 tpb, 16 bars (30720 ticks)
 -> TINTINNABULI engine (Pärt-style)
 -> melody            Shakuhachi(77)      ch0   (D hirajoshi, 62–75)
 -> tintinnabular alt Koto(107)           ch1   (D/G/C quartal, 50–79)
 -> tintinnabular hi  StringEnsemble2(49) ch2   (D/G/C octave-up)
 -> tintinnabular low Contrabass(43)      ch3   (D/G/C bass, 26–50)
 -> UnitMatrixComposer (validate() = zero-drift gate) -> to_midi
 -> FluidSynth GM render (FluidR3_GM.sf2) + RenderPipeline stems
 -> master(target_lufs=-14, ceiling -1 dBTP)
 -> SP100-bach-composer-001-japanese-hirajoshi.wav + .ogg (Opus 48k voip)
```

The tintinnabuli triad is the **quartal stack (0, 5, 10) = D-G-C**, every tone
a member of D hirajoshi (pcs `{2,7,0}`) — no foreign triadic third (hirajoshi
has no major/minor third), so the tintinnabular voices stay strictly in-key.
The result is a static, bell-like "ma" texture idiomatic to the Japanese
source (gagaku-style tonic drone + ringing scale-tone bells).

## 4. Parameters

| Param | Value | Logic |
|---|---|---|
| engine | `tintinnabuli` | melodic voice + voices drawn from a scale-tone triad |
| melody | 30 notes, 16 bars, total 30720 ticks | 4 phrases × 4 bars; hirajoshi pcs `{0,2,3,7,8}`; durations 480/960/1920 ticks (all on the 16th grid) |
| triad | `(0, 5, 10)` = D-G-C | quartal; all hirajoshi tones |
| root_pitch | 62 (alto), 74 (high), 38 (bass) | three register transpositions of the SAME melody (0, +12, −24 semitones) |
| num_voices | 4 total | 1 melody + 3 tintinnabular |
| octave-jump prob | 0.15 (engine default) | occasional ±12 tintinnabular displacement |
| bpm | 70.0 | inherited from source |
| total_ticks | 30720 (16 bars) | matches source length |

## 5. Two-phase architecture (mandatory for generative methods)

- **Phase 1 (raw generative draft):** raw `tintinnabuli` output — includes the
  engine's occasional ±octave tintinnabular jumps (15% per note), i.e. the
  un-smoothed algorithmic character. Exported as
  `MIDI/001-japanese-hirajoshi-phase1.mid` (validate() gate passes; provenance
  `phase=1`).
- **Phase 2 (musicom rules post-processing):** voice-leading octave smoothing —
  any same-voice leap > 12 semitones is folded back within an octave
  (octave folding preserves pitch class, so it cannot introduce out-of-scale
  notes). Result exported as `MIDI/001-japanese-hirajoshi.mid` (validate()
  gate passes; provenance `phase=2`).

Because the engine's pitch material is constrained to the hirajoshi scale and
its triad to scale tones, the Phase-2 chord-tone/voice-leading rules needed
**0 corrective pitch changes** beyond the octave-fold smoothing — the input
was already in-key and on-grid by construction.

## 6. PRE-FLIGHT AUDIT (3-rule gate)

**Source MIDI (informational — generator method does not preserve its notes):**

| Rule | Count | Note |
|---|---|---|
| Grid sync (16th = 120 ticks) | 0 off-grid | clean |
| Harmony — in scale (D hirajoshi) | **4 out-of-scale** | 4 shakuhachi C#6 leading-tone ornaments (pc 1 ∉ `{0,2,3,7,8}`) in the SOURCE |
| Harmony — chord tone | 0 out-of-chord | clean |
| Zero-drift (note tracks equal) | [30720] | PASS |

The 4 out-of-scale source notes are chromatic shakuhachi ornaments. Because
SP-100 is a **generator**, the source notes do not survive (only key/tempo
context is inherited), so no source rework was required — the gate applies to
the *generated* composition instead:

**Generated final MIDI (gate — MUST be clean):**

| Rule | Count (phase1) | Count (final) | Verdict |
|---|---|---|---|
| Grid sync (16th = 120 ticks) | 0 | **0** | PASS |
| Harmony — in scale (D hirajoshi) | 0 | **0** | PASS |
| Harmony — chord tone (hirajoshi region) | 0 | **0** | PASS |
| Zero-drift (note tracks equal) | [30720] | **[30720]** | PASS |

Final: 120 notes (4 × 30), all in D hirajoshi, all on the 16th grid, all
tracks exactly 30720 ticks.

## 7. Render + master

| Stage | Value |
|---|---|
| Carrier | FluidSynth CLI `-ni -R 0 -C 0 -g 1.2 -F`, FluidR3_GM.sf2 (dry, FX off) |
| Master | `master(target_lufs=-14.0, ceiling_db=-1.0, sample_rate=44100)` |
| Target LUFS | `target_for_style("Japanese")` → −14.0 (fallback, style not in GENRE_LUFS) |
| Integrated LUFS | **−14.00** |
| True peak | **−3.96 dBTP** (below −1 ceiling; correct — master is a ceiling, not a target) |
| Peak | 0.634 |
| RMS | 0.1246 |

## 8. Verification (pitch + silence + RMS)

| Metric | Final | Dry ref | Verdict |
|---|---|---|---|
| FFT dominant-pc hit rate (0.5 s windows, 50–1000 Hz, vs hirajoshi pcs) | **1.000** (valid windows 110) | 1.000 | PASS |
| Mean harmonic energy (first 8 harmonics of lowest fundamental) | **0.685** | 0.689 | PASS (≥ 0.30) |
| Harmonic-energy retention (final/dry) | 0.996 | — | PASS |
| Silence ratio (`|mono| < 0.001`) | **8.93 %** | — | tail/decay only |
| Zero-drift | [30720] × 4 tracks | — | PASS |

Harmonic energy 0.685 ≫ 0.30 confirms the render is **tonal, not noise**
(the 2026-08-24 GENDYN failure mode: broadband noise = single-digit harmonic
energy). Silence is confined to the release tail after the final note.

## 9. Fixes applied

1. **Voice-leading octave smoothing (Phase 2)** — folded same-voice tintinnabular
   octave jumps back within an octave (octave-folding preserves pitch class,
   0 out-of-scale introduced). This is the only rules correction; the
   generated material was otherwise already in-key/on-grid.

## 10. Artifacts

| File | Size | Role |
|---|---|---|
| `MIDI/001-japanese-hirajoshi.mid` | 1173 B | final (phase-2, rules-processed) |
| `MIDI/001-japanese-hirajoshi-phase1.mid` | 1173 B | raw generative draft (pre voice-leading) |
| `Audio/SP100-bach-composer-001-japanese-hirajoshi.wav` | 10.9 MB | mastered full mix |
| `Audio/SP100-bach-composer-001-japanese-hirajoshi.ogg` | 435 KB | Opus 48k voip (Telegram) |
| `Audio/dry_full_mix_sp001_reference.wav` | 10.9 MB | dry FluidSynth reference |
| `Audio/stems/track00_Shakuhachi.wav` | 10.1 MB | stem |
| `Audio/stems/track01_Koto.wav` | 10.3 MB | stem |
| `Audio/stems/track02_String_Ensemble_2.wav` | 10.9 MB | stem |
| `Audio/stems/track03_Contrabass.wav` | 10.1 MB | stem |
| `Analysis/render_stats.json` | 1177 B | LUFS/peak/silence/RMS/pitch |
| `Scripts/produce_sp100_cron.py` | 18.4 KB | reproducible producer |
| `provenance.json` | 3023 B | full provenance sidecar |

---

*Report is the primary record. Chat summary is a 6-line caveman digest.*
