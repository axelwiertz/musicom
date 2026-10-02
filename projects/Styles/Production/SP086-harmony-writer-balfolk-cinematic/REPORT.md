# SP-086 HARMONY WRITER (Rule-Based Melody Harmony Writer w/ Voice Leading) — 014-balfolk-cinematic

**Date (UTC):** 2026-10-02 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP086-harmony-writer-balfolk-cinematic/`
**Status:** PASS — pitch hit 96/96 (1.0000), harmonic energy 0.3466, ACF 0/25 unpitched, silence 5.45%, LUFS -14.00, peak 0.6509.

---

## 1. Method + Selection (Which Registry Source)

| Field | Value |
|---|---|
| Method | **SP-086** — Rule-Based Melody Harmony Writer w/ Voice Leading (HarmonyKeen-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT stale ranges) |
| Registered module | `sound.generators.harmony_writer` → `HarmonyWriter`, `melody_to_events`/`events_to_midi`, `diatonic_triads`, `key_scale` |
| Registry entries at pick time | **38 implemented:** SP-001, 011, 021, 024, 026, 028, 032–037, 069–086, 090–092, 094–098 |
| Already used last 7d (excluded) | SP-024, SP-032, SP-070, SP-072, SP-075, SP-079, SP-081 |
| Baseline excluded | SP-001 (FluidSynth reference, always available) |
| Eligible pool | **30 implemented methods** |
| Selection | `random.seed(20261002); random.choice(sorted(pool))` → **SP-086** (first SP-086 production run; module registered 2026-09-17 scan, never produced until tonight) |
| MIDI pool | 315 candidates under `Styles/` (excl. `Production/` + `phase1`); deterministic seeded pick → `Styles/Balfolk/014-balfolk-cinematic/MIDI/balfolk_cinematic_v1.mid` |
| Selection record | `Scripts/select_job_20261002.py` + `.selection_cron.json` |

---

## 2. Source Composition

| Field | Value |
|---|---|
| Project | `Styles/Balfolk/014-balfolk-cinematic/` (Balfolk-Cinematic Hybrid, project 014) |
| MIDI | `balfolk_cinematic_v1.mid` (copied to output `MIDI/`; 5148 B harmonized, source 3.1 KB) |
| Content | **D-Dorian** Balfolk jig melody: Violin (GM40, ch0), 112 notes, pitches D4–A4 (D E F G A = dorian pentachord); String Ensemble (GM48, ch1) D2 pedal drone |
| Tempo / grid | 120 BPM (500000 µs/beat), source tpb **10080** (= 480 × 21); 96 beats = 24 bars |
| Rhythm | 96 eighth notes (0.5 beat) + 16 held notes (3.0 beat); no gaps; 48.0 s musical |
| Mode | D Dorian (per `src/regen.py`: `MusicPitchClassSet("Dorian", rotation=1, initial=2)`) |
| Why this source | A monophonic folk melody over a pedal is the exact input HarmonyKeen's HarmonyWriter is designed for ("you give it a monophonic MIDI melody and it writes harmony parts around it") |

---

## 3. Layer Discipline (Absolute)

SP-086's content layer is the **HarmonyWriter** — it writes SATB harmony voices around the whole monophonic melody, **replacing the source arrangement** (the original violin melody + D2 drone). GM rendering via FluidSynth is the acoustic realisation only (the SP-001 reference), not a competing production layer.

```
balfolk_cinematic_v1.mid
 -> melody extract (mido read-only; ticks rescaled 10080 -> 480, /21 exact)
 -> HarmonyWriter(key="C", style=5, seed=20261002).harmonize()
    voices: soprano (=melody), alto, tenor, bass, bass2 (bass - octave)
 -> harmonized MIDI via UnitMatrixComposer (zero-drift validate gate PASS)
    soprano->Violin 40   alto->Viola 41   tenor->Cello 42
    bass->Contrabass 43  bass2->Tuba 58
 -> fluidsynth -ni -g 1.2 (reverb OFF, chorus OFF, FluidR3_GM.sf2)
    dry_full_mix_sp001_reference.wav (source)  +  SP086-...wav (harmonized)
 -> peak 0.89 -> normalize_to_lufs(-14) -> Limiter(-1 dB) LAST
 -> SP086-harmony-writer-balfolk-cinematic.wav + .ogg (Opus 48k voip)
 -> stems: dry (source) + harmony (harmonized) via RenderPipeline.render_stems
```

### Harmony parameters

| Field | Value |
|---|---|
| key | `C` — HarmonyWriter is **Ionian-only**; D Dorian's parent major is C, so the melody tonic D lands on the **ii** chord (Dm) |
| style | `5` — SATB + bass octave doubling (fuller/cinematic arrangement; matches the source's "epic finale" intent) |
| seed | `20261002` (deterministic; same melody+settings → same output) |

### Voice map (SATB + bass doubling)

| Voice | GM program | Channel | Role |
|---|---|---|---|
| soprano | 40 Violin | 0 | melody (D4–A4) |
| alto | 41 Viola | 1 | chord tone below melody (55–57) |
| tenor | 42 Cello | 2 | chord tone (52–57) |
| bass | 43 Contrabass | 3 | chord root nearest-below (50–57) |
| bass2 | 58 Tuba | 4 | bass − octave (38–45, D2–A2) |

The bass/bass2 voices replace the source's static D2 drone with a harmonically-correct, voice-led bass line (roots follow the chord progression instead of a single pedal).

### Chord progression (first 24 of 112, per-note harmonic analysis)

`ii iii IV V vi iii` repeating → in D Dorian: **Dm — Em — F — G — Am — Em**.

This is the canonical Dorian i–ii–III–IV–v oscillation the melody implies (each melody note D/E/F/G/A is the root of its triad: D→Dm, E→Em, F→F, G→G, A→Am).

---

## 4. Pitch / Tonal-Content Verification — **PASS**

Checked on the delivered harmonized mix (read back from WAV) vs. active MIDI pitches (melody + all harmony voices):

| Metric | Harmonized Mix | Gate | Verdict |
|---|---|---|---|
| Mix FFT hit (0.5 s windows, 50–2000 Hz, ±4% vs fund ×1/×2/×3//2) | **96/96 = 1.0000** | ≥ 0.60 | PASS |
| Harmonic energy (7 harmonics of lowest fund) | **0.3466** | ≥ 0.30 | PASS |
| ACF unpitched (every-2nd 1 s, conf < 0.30) | **0/25 = 0.000** | < 50% | PASS |
| Lowest MIDI notes seen | 38 (D2), 41 (F2), 43 (G2), 45 (A2) — bass2 roots | — | Sane |
| Median dominant peak | 493.9 Hz (B4) | — | Clean |

The SP-035 failure signature (0 Hz frames + broadband noise) is **absent**. Every 0.5 s window of the 48 s piece carries a tonal peak that matches an active MIDI fundamental (or its octave), and zero windows read as unpitched.

---

## 5. Silence / RMS Profile + Level

| Metric | Harmonized | Dry (source) | Note |
|---|---|---|---|
| Silence (<0.001) | **5.45%** | 6.82% | Dense 5-voice SATB; no mid-track dropouts |
| Peak / LUFS | **0.6509 / -14.00 LUFS** | — | Limiter(-1 dBFS) applied last |
| Duration | 50.75 s | 51.75 s | 48.0 s musical + tail |
| RMS profile | ~0.04–0.14 active | — | Continuous 5-part texture across all 48 s |

---

## 6. Fixes & Discoveries During Run (critical)

1. **Engine bug — `diatonic_triads` root ordering (musically wrong harmony).** The module built triads as `sorted({pc...})`, so the pitch-class set lost its (root, third, fifth) order. For IV/V/vi/vii° the root pitch-class is not the numeric minimum (e.g. F major = (5,9,0) → sorted (0,5,9) misidentifies C as the "root"). `choose_chords` (scores pc==pcs[0] as root) and the bass voice (uses pcs[0] as root) both then targeted the wrong note — the D-Dorian melody collapsed to a degenerate `ii iii ii iii…` alternation instead of `ii iii IV V vi iii`. **Fix:** `diatonic_triads` now returns chord tones in (root, third, fifth) order transposed to the key root (the already-present `qualities` table, previously dead code). Verified: module `demo()` still passes (now emits a correct `I vii V vi IV iii ii I` descent), and no test pins the old behavior (`tests/` has no harmony_writer reference).

2. **Source tpb=10080 (480×21) breaks UnitMatrixComposer's 480-tpb model — silent 16-bit tick truncation.** First render wrote 112 notes compressed into 65520 ticks (6.0 s) with scrambled/overlapping notes — the engine's 480-tpb internal grid can't hold 10080-tpb absolute ticks. **Fix:** rescale all melody ticks `/21` (exact integer) to standard 480 tpb before composing; assert the written MIDI's last tick == section length (46080) to catch any truncation.

3. **`write_wav` int16 scaling (SP-079 silent-output bug).** Wrote `(audio * 32767.0).astype(np.int16)` — raw `astype(np.int16)` would zero every sample in (−1, 1).

---

## 7. Artifacts

| Artifact | Path | Size |
|---|---|---|
| Harmonized mix WAV | `SP086-harmony-writer-balfolk-cinematic.wav` | 8,952,876 B (50.75 s) |
| Harmonized mix OGG (Opus 48k voip) | `SP086-harmony-writer-balfolk-cinematic.ogg` | 318,623 B |
| Dry reference mix (SP-001, source) | `dry_full_mix_sp001_reference.wav` | 9,128,748 B |
| Harmonized MIDI (SP-086 output) | `MIDI/balfolk_cinematic_v1_harmonized.mid` | 5,148 B |
| Source MIDI (copy) | `MIDI/balfolk_cinematic_v1.mid` | 3,116 B |
| Dry stems (source) | `Audio/stems_dry/track00_Violin.wav`, `track01_String_Ensemble_1.wav` | — |
| Harmony stems (harmonized) | `Audio/stems_harmony/track00_Violin..track04_Tuba.wav` | — |
| Renderer script | `Scripts/produce_sp086_cron.py` | 17,864 B |
| Selection script | `Scripts/select_job_20261002.py` + `.selection_cron.json` | — |
| Verification JSON + grid | `Analysis/pitch_verification.json`, `Analysis/render_stats.json`, `Analysis/grid_visualization.txt` | — |
| Provenance | `provenance.json` | — |
| Report | `REPORT.md` | this file |

---

## 8. Quality gate

- Harmonized MIDI exists (5148 B, zero-drift validate() PASS, tpb 480, full 46080-tick span). ✅
- OGG plays / non-empty (318,623 B). ✅
- Pitch verification PASS (96/96 hit, he 0.3466, ACF 0/25). ✅
- Silence ratio 5.45% (no mid-track gaps). ✅
- Project follows numbered production naming (`Production/SP086-...`). ✅
- Engine bug fix committed with the project (`sound/generators/harmony_writer.py`). ✅
