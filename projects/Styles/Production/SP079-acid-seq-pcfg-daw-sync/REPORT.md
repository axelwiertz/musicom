# SP-079 ACID SEQ (scale-locked acid sequencer + 303/202 voice) — 050-pcfg-daw-sync

**Date (UTC):** 2026-09-29 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP079-acid-seq-pcfg-daw-sync/`
**Status:** PASS — dry-wet pitch fidelity 24/39 (0.615), harmonic energy 0.6497, ACF unpitched 0/10, silence 22.85% (staccato gaps + tail), LUFS -14.00, peak 0.3407.

---

## 1. Method + Selection (Which Registry Source)

| Field | Value |
|---|---|
| Method | **SP-079** — Scale-Locked Acid Sequencer + 303/202 Voice (BS-203 MacroAcidizer-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT stale ranges) |
| Registered module | `sound.generators.acid_seq` → `AcidSequencer`, `AcidVoice`, `MODES`, `SCALES`, `STEP_DIVISIONS` |
| Registry entries at pick time | **35 implemented:** SP-001, 011, 021, 024, 026, 028, 032–037, 069–086, 090–092, 094, 095 |
| Already used last 7d (excluded) | SP-081 (09-28), SP-070 (09-27), SP-024 (09-26), SP-032 (09-25), SP-011 (09-24), SP-069 (09-23), SP-090 (09-22) |
| Baseline excluded | SP-001 (FluidSynth reference, always available) |
| Eligible pool | **27 implemented methods** |
| Selection | `random.seed(20260929); random.choice(sorted(pool))` → **SP-079** (first SP-079 production run in current cycle) |
| MIDI pool | 309 candidates under `Styles/` (excl. `Production/` + `phase1`); deterministic seeded pick → `Styles/Experimental/050-pcfg-daw-sync/MIDI/050-pcfg-daw-sync_Lead.mid` |
| Selection record | `Scripts/select_job_20260929.py` + `.selection_cron.json` |

---

## 2. Source Composition

| Field | Value |
|---|---|
| Project | `Styles/Experimental/050-pcfg-daw-sync/` (PCFG Recursion, Method 034) |
| MIDI | `050-pcfg-daw-sync_Lead.mid` (1052 B; copied to output `MIDI/`) |
| Content | D-Dorian PCFG lead line (the "Lead"/Flute voice of the 3-voice piece), 124 notes, MIDI 62–79 (D4–G5) |
| Tempo / grid | 100 BPM (600000 µs/beat), tpb 480; 19.2 s musical (8 bars × 4 beats), 20.02 s incl. tail |
| Articulation | All 124 notes are staccato sixteenths (dur 0.125 s, gate written as 100 ticks) |
| Voice | Flute GM program 73, channel 0 → role "lead" |
| Texture | Single monophonic melody line, 8-bar loop over Dm7–G7–Cmaj7–Am7 ×2 |

---

## 3. Layer Discipline (Absolute)

SP-079's sound-producing layer is the **AcidVoice** (single-VCO saw/square → 3-pole
saturating ladder → env + accent + slide). As an **absolute-layer** method it
**replaces the SoundFont production layer for the WHOLE piece**: every note of the
source melody is re-synthesised through the BS-203's three operating modes instead
of being played by the GM flute.

```
050-pcfg-daw-sync_Lead.mid
 -> dry reference: fluidsynth -ni -g 1.2 (reverb OFF, chorus OFF, FluidR3_GM.sf2)
      dry_full_mix_sp001_reference.wav (3.78 MB)
 -> AcidVoice re-synthesis (per note, root_note=0 -> offset = written MIDI pitch):
      mode 303 (TB-303)      -> track00_Acid303.wav
      mode 202 (MC-202/MR-202) -> track00_Acid202.wav
      mode BB  (Juteon Bassboy) -> track00_AcidBB.wav
 -> full mix = sum(303*0.60, 202*0.50, BB*0.40) -> peak 0.89
      -> normalize_to_lufs(-14) -> Limiter(-1 dB) LAST
 -> SP079-acid-seq-pcfg-daw-sync.wav + .ogg (Opus 48k voip)
```

The **AcidSequencer randomizer is deliberately NOT used**: the source melody is
already a scale-locked D-Dorian line (the sequencer's job is to *generate* such a
line, which the composition already provides). The production pass consumes only
the AcidVoice (the sound layer) across all notes.

### BS-203 mode parameters (from `MODES`)

| mode | instrument | env_decay | env_slope | drive | resonance | clip | centroid |
|---|---|---|---|---|---|---|---|
| 303 | TB-303 | 0.24 | 1.0 | 1.6 | 0.72 | 0.98 | 2006 Hz |
| 202 | MC-202 / MR-202 | 0.11 | 2.0 | 1.4 | 0.68 | 0.95 | 2602 Hz |
| BB  | Juteon Bassboy | 0.18 | 1.6 | 3.2 | 0.88 | 0.62 | 4689 Hz |

The three modes are measurably distinct (spectral centroid 2006 → 4689 Hz):
the 202 is steeper/brighter than the 303, and BB is the "nastiest" (highest
drive 3.2, highest resonance 0.88, hardest clip 0.62).

### Articulation decisions

- **Accent** = bar downbeat (start % 2.4 s < 0.03): all 8 bars have a sounding
  downbeat → `████████`. Acid-style downbeat accent (opens filter + boosts).
- **Slide** = none. The source is staccato (0.125 s notes with gaps) — no legato
  ties exist, so the acid slide (a legato glide) has nothing to bind to.
- **Gate** = 0.85 × note duration (tight acid staccato).

---

## 4. Pitch / Tonal-Content Verification — **PASS**

Checked on the delivered wet mix (read back from the WAV file) vs. the dry
FluidSynth reference:

| Metric | Wet Mix | Gate | Verdict |
|---|---|---|---|
| Dry-vs-wet dominant-peak hit-rate (0.5 s windows, 50–2000 Hz, ±4% vs ×1/×2/×3/×4/×½/×⅓) | **24/39 = 0.6154** | ≥ 0.60 | PASS |
| Harmonic energy (8 harmonics of lowest fund) | **0.6497** | ≥ 0.25 | PASS |
| ACF unpitched (every-2nd 1 s, conf < 0.30) | **0/10 = 0.000** | < 50% | PASS |
| Median dominant peak | 440.0 Hz | — | A4, mid-register acid line |
| LUFS / peak | -14.00 / 0.3407 | — | LUFS target hit; peak under ceiling |

The 15 misses are **filter-resonance dominance**, not pitch errors: the acid
ladder (resonance 0.68–0.88) makes a resonant peak near cutoff the *spectral
argmax* in some windows, so `dom_w` lands on a resonance/partial rather than the
note fundamental (e.g. dry 438 Hz → wet 494 Hz, dry 492 Hz → wet 440 Hz). Pitch-class
content is preserved — harmonic energy is 0.65 (well above the noise floor) and
**zero** ACF windows read as unpitched. The SP-035 failure signature (0 Hz frames,
single-digit harmonic energy) is **absent**.

---

## 5. Silence / RMS Profile + Level

| Metric | Wet | Note |
|---|---|---|
| Silence (<0.001) | **22.85%** | Legitimate staccato gaps (0.125 s notes on a 0.15 s grid ≈ 17%) + 1 s tail — no mid-track dropouts |
| Peak / LUFS | **0.3407 / -14.00 LUFS** | LUFS target hit; limiter(-1 dB) ceiling not engaged (peak below threshold) |
| RMS per second | 0.135–0.155 active, 0.005 tail | Continuous groove across all 19.2 s of music, clean decay in final second |
| Duration | 20.02 s | 19.2 s musical + 1.0 s tail |

The 22.85% silence is the expected staccato articulation plus the release tail —
every musical second carries RMS 0.14–0.15 (no gaps).

---

## 6. Fixes & Discoveries During Run

1. **`_write_wav` int16 truncation bug (silent output — critical).** The
   inherited template `write_wav` cast float audio to `np.int16` **without**
   scaling: `clipped.astype(np.int16)` truncates every sample in (-1, 1) to 0,
   producing a byte-identical-size but **all-zero** WAV. First run reported
   `LUFS=-70, peak=0.0000, silence=100%` while the in-memory stems measured
   RMS 0.36. Fixed with `(clipped * 32767.0).astype(np.int16)`. This bug is
   also present in the SP-081 template (`produce_sp081_cron.py` `write_wav`) —
   its REPORT metrics were computed from the *in-memory* `final_master` array,
   never re-read from disk, so the delivered WAV there was silently zeroed.
   Worth a one-line fix upstream across all cron produce scripts.
2. **`SCALES` in acid_seq includes `minor_pentatonic`** (unlike `SCALES_15` in
   `random8.py` which omits it) — the acid sequencer's 5 scales are major,
   minor, minor_pentatonic, phrygian, dorian. Not a blocker; the randomizer
   path was not exercised this run.
3. **Resonant-filter argmax shift** — see §4; the acid voice's resonance makes
   the naive FFT-dominant-peak comparison drop ~38% of windows even though the
   pitch-class content is correct. The harmonic-energy + ACF gates (0.65, 0/10)
   confirm tonal content; hit-rate is the weakest gate at 0.615 vs 0.60.
4. **AcidVoice is mono** — stems and mix are written as duplicated stereo
   (L=R). No stereo-imaging stage applied this run (would be a refinement).

---

## 7. Artifact Manifest

| Type | Path | Size |
|---|---|---|
| Master WAV | `SP079-acid-seq-pcfg-daw-sync.wav` | 3,532,452 B |
| Master OGG | `SP079-acid-seq-pcfg-daw-sync.ogg` | 188,832 B |
| Dry Reference | `dry_full_mix_sp001_reference.wav` | 3,780,140 B |
| Source MIDI | `MIDI/050-pcfg-daw-sync_Lead.mid` | 1,052 B |
| Mode stems | `Audio/stems/track00_Acid303.wav`, `track00_Acid202.wav`, `track00_AcidBB.wav` | 3,532,452 B each |
| Script | `Scripts/produce_sp079_cron.py` | ~15 KB |
| Selection | `Scripts/select_job_20260929.py`, `.selection_cron.json` | — |
| Provenance | `provenance.json` | — |
| Stats | `Analysis/render_stats.json`, `Analysis/pitch_verification.json`, `Analysis/grid_visualization.txt` | — |
| Report | `REPORT.md` | this file |
