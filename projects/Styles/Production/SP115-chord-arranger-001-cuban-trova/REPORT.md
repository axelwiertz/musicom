# SP-115 Chord-Driven 3-Track Generative Arranger — 001-cuban-trova

**Job:** random-style production (SP methods) — LAYER-ALIGNED
**Date (UTC):** 2026-11-16  **Seed:** 20261116
**Status:** PASS — FFT hit 1.000, harmonic energy 0.595 (≥ 0.30), silence 7.51%
(all in tail/decay), LUFS −14.20, true peak −1.00 dBTP, zero-drift clean.

---

## 1. Method + selection (which registry source)

| Field | Value |
|---|---|
| Method | **SP-115** — Chord-Driven 3-Track Generative Arranger: input chords → chord/rhythm + arpeggiated melody + harmony-following bass tracks; ratchets/trills/swing/probability/accents/Euclidean muting; 8-macro + 16-step-lane modulation bus (Midicake UNA-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT a stale `SP-001..SP-035` range) |
| Registered module | `sound.generators.chord_arranger` → `ChordDrivenArranger` (`generate(chords, macros)`, `to_midi`) |
| Registry entries at pick time | 97 |
| Recent excluded (7d) | SP-069, SP-075, SP-084, SP-100, SP-113, SP-138, SP-154 |
| Already on this source | (none) |
| Baseline excluded | SP-001 |
| Eligible pool | 89 methods |

Selection record: `Production/.selection_cron.json`,
`Production/select_job_20261116.py`. Well-formed filter: **355 / 460**
candidate MIDIs passed (normal tpb, sane note lengths, ≥2 note tracks or a
program change, 2–600 s length); 354 with ≥3 pitch classes.

## 2. Source composition

| Field | Value |
|---|---|
| Project | `Styles/Cuban/001-cuban-trova-research/` |
| MIDI | `MIDI/cuban_seed.mid` |
| Genre / key | Cuban trova (Polo Montañez style); **C major** (pcs `{0,2,4,5,7,9,11}`) |
| Tempo | 92.00 BPM, 480 tpb, 4/4, type-1 |
| Length | 70.43 s = 27 bars = 51840 ticks |
| Voice | single track nylon guitar (prog 24 ch0), 96 notes, range B3–D5, 0% chromatic (pure C-major diatonic) |

## 3. Layer discipline (absolute — generator re-composes the whole piece)

SP-115 is a **generator** method: it produces note events, not a timbral
effect. Applied as an **absolute layer**, `ChordDrivenArranger` re-composes the
whole piece in the source's key (C major) and tempo (92 BPM); no source MIDI
notes survive — only its key/tempo/genre context is inherited (same convention
as the SP-098 fractal-seq and SP-100 B.A.C.H. generator runs).

```
C major trova melody (92 BPM, 27 bars)
 -> derive 27-bar chord progression from the melody's harmonic rhythm
    (downbeat + per-bar pitch content; son/trova/guajira I-IV-V + vi/ii + V7)
 -> ChordDrivenArranger(bpm=92, bars=27, seed=20261116)
 -> chord/rhythm  Acoustic Guitar nylon(24)  ch0   (block/strum/euclid/drone)
 -> arp melody    Flute(73)                  ch1   (up/down/updown/random)
 -> bass          Acoustic Bass(32)          ch2   (root/fifth + Euclid mute)
 -> UnitMatrixComposer (validate() = zero-drift gate) -> to_midi
 -> FluidSynth GM render (FluidR3_GM.sf2, FX off) + RenderPipeline stems
 -> master(target_lufs=-14, ceiling -1 dBTP)
 -> SP115-chord-arranger-001-cuban-trova.wav + .ogg (Opus 48k voip)
```

## 4. Parameters

| Param | Value | Logic |
|---|---|---|
| engine | `ChordDrivenArranger` | 16-step grid/bar (120 ticks), 3 coordinated tracks |
| chords | 27 × `(root, quality)` | C/G/G7/F/Am/Dm over 27 bars, all chord tones ⊂ C major |
| density | 0.60 | moderate strum/pulse density |
| probability | 0.70 | per-step play chance (melody/bass) |
| swing | 0.15 | subtle Latin swing (even-step delay) |
| accent | 0.50 | mid accent |
| ratchet | 0.30 | occasional 2–4 step subdivisions |
| octave | 0.0 | melody/bass stay in register |
| gate | 0.60 | note duration fraction |
| spread | 0.30 | light chord voicing inversion |
| bpm / bars / ticks | 92 / 27 / 51840 | inherited from source length |

Raw generation: **1015 events** (chord 507, melody 286, bass 222), all pitch
classes within C major.

## 5. Two-phase architecture (mandatory for generative methods)

- **Phase 1 (raw generative draft):** raw `ChordDrivenArranger` output — keeps
  the engine's swing + ratchet subdivisions (283 off-grid onsets, the UNA-style
  micro-rhythmic character). Exported as `MIDI/001-cuban-trova-phase1.mid`
  (zero-drift validate() gate passes; provenance `phase=1`).
- **Phase 2 (musicom rules post-processing):** grid quantize — snap every onset
  to the 16th grid (120 ticks). One melody note snapped across a bar boundary
  into a new chord region, so its pitch-class was no longer a chord tone →
  chord-tone corrected (pulled to nearest chord tone, minimal semitone move).
  Result exported as `MIDI/001-cuban-trova.mid` (validate() gate passes;
  provenance `phase=2`).

Because the arranger's pitch material is chord tones by construction (chord
track = chord tones, melody = arpeggio over chord tones, bass = root/fifth),
out-of-scale and out-of-chord were **0 in both phases**; the only Phase-2
correction was grid snapping + 1 boundary chord-tone pull.

## 6. PRE-FLIGHT AUDIT (3-rule gate)

**Source MIDI (informational — generator method does not preserve its notes):**

| Rule | Count | Note |
|---|---|---|
| Grid sync (16th = 120 ticks) | 0 off-grid | clean |
| Harmony — in scale (C major) | 0 out-of-scale | pure diatonic |
| Harmony — chord tone | 0 out-of-chord | clean |
| Zero-drift (note tracks equal) | [51840] | PASS |

The source melody is already clean (single monophonic line, 0% chromatic) — **no
source rework required**. The gate applies to the *generated* composition:

**Generated final MIDI (gate — MUST be clean):**

| Rule | Count (phase1) | Count (final) | Verdict |
|---|---|---|---|
| Grid sync (16th = 120 ticks) | 283 | **0** | PASS |
| Harmony — in scale (C major) | 0 | **0** | PASS |
| Harmony — chord tone (bar chord) | 0 | **0** | PASS |
| Zero-drift (note tracks equal) | [51840] | **[51840]** | PASS |

Final: 1015 notes (3 voices), all in C major, all onsets on the 16th grid, all
chord tones of their bar, all three tracks exactly 51840 ticks.

## 7. Render + master

| Stage | Value |
|---|---|
| Carrier | FluidSynth CLI `-ni -R 0 -C 0 -g 1.2 -F`, FluidR3_GM.sf2 (dry, FX off) |
| Master | `master(target_lufs=-14.0, ceiling_db=-1.0, sample_rate=44100)` |
| Target LUFS | `target_for_style("Cuban")` → −14.0 (fallback, style not in GENRE_LUFS) |
| Integrated LUFS | **−14.20** |
| True peak | **−1.00 dBTP** (at ceiling) |
| Peak | 0.8913 |
| RMS | 0.1506 |

## 8. Verification (pitch + silence + RMS)

| Metric | Final | Dry ref | Verdict |
|---|---|---|---|
| FFT dominant-pc hit rate (0.5 s windows, 50–1000 Hz, vs C-major pcs) | **1.000** (valid 142) | 1.000 | PASS |
| Mean harmonic energy (first 8 harmonics of lowest fundamental) | **0.5955** | 0.6008 | PASS (≥ 0.30) |
| Harmonic-energy retention (final/dry) | 0.991 | — | PASS |
| Silence ratio (`|mono| < 0.001`) | **7.51 %** | — | tail/decay only |
| Zero-drift | [51840] × 3 tracks | — | PASS |

Harmonic energy 0.5955 ≫ 0.30 confirms the render is **tonal, not noise** (the
2026-08-24 GENDYN failure mode: broadband noise = single-digit harmonic energy).
Per-second RMS profile: music 0–77 s (0.07–0.23 RMS), then 2 s of release tail
at 78–79 s; **no mid-track silence** (no 0.0 seconds inside the music span).

## 9. Fixes applied

1. **Grid quantize (Phase 2)** — snapped all 1015 onsets to the 16th grid
   (120 ticks), removing the engine's 283 off-grid swing/ratchet onsets for the
   final file (raw swing/ratchet character preserved in `-phase1.mid`).
2. **Chord-tone correction** — 1 melody note snapped across a bar boundary into
   a new chord region; pulled to the nearest chord tone (minimal semitone move).
   This is the only pitch change; out-of-scale stayed 0 (chord tones ⊂ C major).

## 10. Artifacts

| File | Size | Role |
|---|---|---|
| `SP115-chord-arranger-001-cuban-trova.ogg` | 540 798 B | Opus 48k voip (Telegram) |
| `SP115-chord-arranger-001-cuban-trova.wav` | 12 841 004 B | mastered full mix |
| `Audio/dry_full_mix_sp001_reference.wav` | 12 841 004 B | dry FluidSynth reference |
| `Audio/stems/track00_Acoustic_Guitar_nylon.wav` | 12 824 108 B | stem |
| `Audio/stems/track01_Flute.wav` | 12 841 004 B | stem |
| `Audio/stems/track02_Acoustic_Bass.wav` | 12 800 812 B | stem |
| `MIDI/001-cuban-trova.mid` | 7 417 B | final (phase-2, rules-processed) |
| `MIDI/001-cuban-trova-phase1.mid` | 7 513 B | raw generative draft (pre grid-snap) |
| `Analysis/render_stats.json` | 1 502 B | LUFS/peak/silence/RMS/pitch |
| `Scripts/produce_sp115_cron.py` | 20 046 B | reproducible producer |
| `Scripts/select_job_20261116.py` | — | selection record |
| `provenance.json` | 3 877 B | full provenance sidecar |

---

*Report is the primary record. Chat summary is a short caveman digest.*
