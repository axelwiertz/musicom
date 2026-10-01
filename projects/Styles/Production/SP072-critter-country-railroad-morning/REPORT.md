# SP-072 CRITTER PAD (Brackish Pads three-partial + stochastic microtonal Critters) — Country Railroad Morning / 041-country-railroad-morning

**Date (UTC):** 2026-10-01 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP072-critter-country-railroad-morning/`
**Status:** PASS — mix FFT 36/41 (0.878), harmonic energy 0.360, ACF 1/11 unpitched, silence 1.79%, LUFS -14.00, peak 0.8913.

---

## 1. Method + selection (which registry source)

| Field | Value |
|---|---|
| Method | **SP-072** — Three-Partial Pad Bank with Stochastic Microtonal Critters Layer (Brackish Pads-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT stale `SP-001..SP-035` range) |
| Registered module | `sound.synthesis.critter_pad` → `PadPartialBank`, `Partial`, `Critters`, `cassette`, `splosh`, `pump_envelope` |
| Registry entries at pick time | **38 implemented** (SP-001..SP-098, sparse) |
| Already used last 7d (excluded) | SP-011, SP-024, SP-032, SP-070, SP-075, SP-079, SP-081 |
| Baseline excluded | SP-001 |
| Eligible pool | **30** methods |
| Selection | `random.Random(20261001).choice(pool)` → **SP-072** (prior SP-072 run 2026-09-16; >7 days back, so eligible again) |
| MIDI pool | 313 candidates under `Styles/` (excl. `phase1` + `Production`); deterministic seeded pick → `Country/041-country-railroad-morning/MIDI/041-country-railroad-morning-v1.mid` |
| Selection record | `Production/.selection_cron.json` (rewritten this run) + `Production/select_job_20261001.py` |

## 2. Source composition

| Field | Value |
|---|---|
| Project | `Styles/Country/041-country-railroad-morning/` |
| MIDI | `MIDI/041-country-railroad-morning-v1.mid` (copied to output `MIDI/`; 6 tracks incl. tempo meta) |
| Tempo / grid | 106 BPM (566038 us/beat), 4/4, tpb **480**; 20.38 s music (last_tick 17280) |
| Voices | Lead **Electric Guitar (jazz)** prog26 ch0, 16 notes E4–D5 (64–74) · Harmony **Acoustic Guitar (nylon)** prog24 ch1, 8 notes G3–D4 (55–62) · Bass **Electric Bass (finger)** prog33 ch2, 8 notes G2–C3 (43–48) · **Drums** ch9, 96 notes 36–42 (kick/snare/hat) · Guitar **Acoustic Guitar (steel)** prog25 ch3, 32 notes B3–D4 (59–62) |
| Texture | 160 total notes; drums 96 notes = dense backbeat grid; guitar/harmony chord strums; lead melodic hook |
| Why this source | Country piece with a full rhythm section (drums + bass + guitar strums) is a good stress test for an absolute-layer pad: every role — including channel-9 percussion — must go through the pad without turning to mush |

Grid (`Analysis/grid_visualization.txt`, sanctioned `visualization/grid.py`): Lead 33%, Harmony 89%, Bass 89%, Drums 89%, Guitar 78% density.

## 3. Layer discipline (absolute)

SP-072 is an **absolute-layer synthesis method**: the `PadPartialBank` replaces the production layer for **ALL voices**, including channel-9 percussion. Nothing rides the GM kit in the wet mix — the kit appears only in the SP-001 reference render and the dry stems.

```
041-country-railroad-morning-v1.mid
 -> per-note PadPartialBank.render_note (per-voice profiles below, 0.40 s tail)
      + outer half-cosine envelope + velocity gain at call site + const-power pan
      -> voice bus sum -> cassette(0.30 blend) + splosh(0.20)
      -> peak-norm 0.89 -> normalize_to_lufs(-14) -> Limiter(-1 dB) LAST
      -> SP072-critter-country-railroad-morning.wav (21.25 s stereo) + .ogg (Opus 48k voip)
 -> dry reference: fluidsynth -ni -g 1.2 (reverb OFF, chorus OFF, FluidR3_GM.sf2)
      dry_full_mix_sp001_reference.wav 21.25 s
 -> dry stems (RenderPipeline.render_stems, FX off)
 -> wet stems (same pad synth, peak 0.89)
```

### Voice profiles (measurement-driven)

| Voice | GM | basic atk/rel | complex atk/rel | wobble b/c | Critters density / set / drift | balance b/c/cr | gain | pan |
|---|---|---|---|---|---|---|---|---|
| Lead (jazz gtr hook) | 26 | 0.10 / 0.35 s | 0.15 / 0.45 s | 5 / 12 c | 2.2/s, quarter-tone (±50 c), 24 c | 0.70 / 0.50 / 0.50 | 1.00 | -0.22 |
| Harmony (nylon bed) | 24 | 0.20 / 0.60 s | 0.35 / 0.90 s | 4 / 9 c | 1.3/s, eighth-tone (±25 c), 16 c | 0.75 / 0.45 / 0.30 | 0.80 | +0.18 |
| Bass (finger bass) | 33 | 0.04 / 0.30 s | 0.08 / 0.40 s | 3 / 7 c | 1.0/s, just-ish, 14 c | 0.80 / 0.40 / 0.30 | 0.90 | 0.00 |
| **Drums (ch9)** | — | 0.003 / 0.09 s | 0.005 / 0.14 s | 2 / 4 c | 4.0/s, chromatic-drift, 40 c | 0.55 / 0.40 / 0.45 | 0.65 | 0.00 |
| Guitar (steel strum) | 25 | 0.02 / 0.25 s | 0.04 / 0.35 s | 4 / 9 c | 1.8/s, eighth-tone (±25 c), 20 c | 0.70 / 0.50 / 0.45 | 0.85 | +0.15 |

Drums get a **percussive-adapted pad profile**: near-instant attack (3–5 ms), short release, and high noise partials (0.22 / 0.15) so each hit reads as a short noise-burst rather than a sustained pad. This is the first SP-072 run with a percussion track; the absolute-layer rule is honoured literally — the kit goes through the pad — while the envelope is tuned so the backbeat stays articulate.

## 4. Pitch / tonal-content verification — **PASS**

Mandatory for every synthesis method: size asserts and silence ratios do **not** catch noise (SP-035 GENDYN shipped broadband noise past both). Three checks, all on the **delivered files**:

| Metric | Wet mix | Gate | Verdict |
|---|---|---|---|
| Mix FFT hit (0.5 s windows, 50–2000 Hz, ±4% vs fund ×1/×2/×3//2) | **36/41 = 0.878** | ≥ 0.60 | PASS |
| Median harmonic energy (8 harmonics of lowest fund) | **0.360** | ≥ 0.30 (noise = single digits) | PASS |
| ACF unpitched (every-2nd 1 s, conf<0.30) | **1/11 = 0.091** | < 50% | PASS |
| Misses (5) | t=1.5 dom 66 Hz vs {38,42}; t=2.0 dom 74 vs {42,43,55,59,67}; t=6.0 dom 64 vs {42,43,59,60,62,67}; t=9.5 dom 66 vs {38,42,45,55,59,62}; t=10.5 dom 66 vs {42,45,55,62} — all land in the drum/bass low register (dominant peak 64–74 Hz = kick/snare/tom detuned partials under pad wobble), not noise | — | explained |
| Lowest notes seen | MIDI 36/38/42/43 — kick, snare, hat, bass G2 — the source registers | — | sane |
| Median dominant peak | 98 Hz ≈ low G2/bass + drum register | — | sane |

The SP-035 failure signature (0 Hz frames + ~4% harmonic energy) is **absent**.

Full JSON: `Analysis/pitch_verification.json`.

## 5. Silence / RMS profile + level

| Metric | Wet | Dry (SP-001 ref) | Note |
|---|---|---|---|
| Silence (<0.001) | **1.79%** | 17.37% | wet far denser — pad tails + splosh fill interstices |
| Peak / LUFS | 0.8913 / **-14.00** | — | limiter last |
| RMS/s wet | 0.078–0.213, median ~0.16 | — | no dead zones; min is final 0.87 s tail (0.0013) |
| RMS/s shape | rises s2+, peaks s4–8 (full band), decays s19+ to tail | peaks s3–5, tails s20+ | **loci broadly match dry** — arrangement breathing, not production gaps |

Per-second tables: `Analysis/render_stats.json`. Zero mid-track gaps; the only sub-0.01-RMS window is the final tail second.

## 6. Fixes / decisions applied during this run

1. **First SP-072 run with percussion (ch9).** Stock pad envelopes (1.2–1.8 s attack) would smear the 96-hit backbeat into mush. Fix: dedicated drum profile — basic/complex attack 3/5 ms, release 0.09/0.14 s, noise partials 0.22/0.15 — so hits read as short pitched-noise bursts. Absolute-layer rule preserved (kit still renders through `PadPartialBank`).
2. **`render_note()` peak-normalizes every note to 0.8**, erasing dynamics (SP-073 lesson). Fix: explicit `clip((vel/90)**1.5, 0.22, 1.30)` gain at the call site.
3. **Velocity spread across 5 roles.** Five distinct profiles (not one size) keep the lead hook, chord bed, bass, and strums separable after the absolute pad transform.
4. **Stem label for drums.** Program-less ch9 track must not fall back to GM index 0 ("Acoustic_Grand_Piano"); added `perc` flag → stem labelled `track03_Drums` (dry + `_CRITTER` wet).

## 7. Artifacts

| Artifact | Path | Size |
|---|---|---|
| Full mix WAV | `SP072-critter-country-railroad-morning.wav` (21.25 s, 44.1 kHz stereo) | 3,747,716 B |
| Full mix OGG (Opus 48k voip) | `SP072-critter-country-railroad-morning.ogg` | 114,915 B |
| Dry reference mix (SP-001, FX-off) | `dry_full_mix_sp001_reference.wav` (21.25 s) | 4,084,780 B |
| Source MIDI (copy) | `MIDI/041-country-railroad-morning-v1.mid` | — |
| Dry stems | `Audio/stems_dry/track00_Electric_Guitar_jazz.wav` (1,965,356 B) · `track01_Acoustic_Guitar_nylon.wav` (4,084,780 B) · `track02_Electric_Bass_finger.wav` (3,983,660 B) · `track03_Drums.wav` (3,624,492 B) · `track04_Acoustic_Guitar_steel.wav` (4,007,468 B) | — |
| Wet stems (peak 0.89) | `Audio/stems_wet/track00_Electric_Guitar_jazz_CRITTER.wav` … `track04_Acoustic_Guitar_steel_CRITTER.wav` (21.25 s each) | 3,747,716 B each |
| Renderer | `Scripts/produce_sp072_cron.py` | — |
| Verification JSON + grid | `Analysis/pitch_verification.json`, `Analysis/render_stats.json`, `Analysis/grid_visualization.txt` | — |
| Selection records | `Production/.selection_cron.json`, `Production/select_job_20261001.py` | — |
| Provenance | `provenance.json` | — |
| Report | `REPORT.md` | this file |

WAVs git-ignored by policy; OGG + MIDI + JSON + REPORT tracked.

## 8. Listen for

- The lead jazz-guitar hook now breathes through a Mellotron-like wobble: quarter-tone Critters clusters bloom behind the 16 melodic notes, most audible when the nylon harmony swells (s4–8).
- The backbeat is a percussive Critters scatter — short pitched-noise bursts with chromatic-drift clusters, not a GM kit. Compare `dry_full_mix_sp001_reference.wav` (clean GM country band) vs wet: same railroad-morning DNA, haunted-tape double.
- Bass sits tight (0.04 s attack) with just-ish microtonal drift — a low, slightly-unstable pedal under the strums.
- Cassette wear (0.30 blend) + splosh (0.20) sit low so strum transients stay readable.

## 9. Quality gate

- [x] MIDI present for the audio render (`MIDI/041-country-railroad-morning-v1.mid`)
- [x] OGG non-empty (114,915 B) and playable-length (21.25 s)
- [x] Pitch verification run and reported (PASS: FFT 36/41, harm 0.360, ACF 1/11)
- [x] Silence ratio + per-second RMS measured; loci match dry, no production gaps
- [x] Full mix WAV + per-track stems (dry AND wet/critter)
- [x] `provenance.json` per artifact set
- [x] Grid visualization written before trusting timing (sanctioned visualizer)
- [x] Output under `projects/Styles/Production/<method>-<project>/`
- [x] No hardcoded soundfont (`discover_soundfont` → FluidR3_GM.sf2)
- [x] Registry source is the implemented `SP_METHODS` dict, not a stale range or spec-only DB
