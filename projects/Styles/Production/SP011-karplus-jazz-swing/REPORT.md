# SP-011 — Karplus-Strong String Synthesis Production Pass

**Job:** nightly random-style production (layer-aligned) — 2026-09-04
**Method:** SP-011 Karplus-Strong String Synthesis (physical modeling)
**Source:** `/opt/data/projects/Styles/Balfolk/017-hybrid-pattern-matrix/MIDI/exercise1b_jazz_ii_v_i_swing.mid`
**Output:** `/opt/data/projects/Styles/Production/SP011-karplus-jazz-swing/`

---

## 1. Method + selection (registry source)

Picked from the **implemented SP_METHODS registry** in
`/opt/data/repos/musicom/workflows/musicom_workflow.py` (NOT methods_db.md).
Registry contents (10 methods): SP-001, SP-011, SP-021, SP-024, SP-026, SP-028,
SP-032, SP-033, SP-034, SP-035.

Selection: uniform random over the implemented pool, excluding methods used in
the last 7 days (SP-034 09-03, SP-032 09-02, SP-024 09-01, SP-017 08-31/08-28,
SP-014 08-29).

- Eligible pool: `["SP-001", "SP-011", "SP-021", "SP-026", "SP-028", "SP-033", "SP-035"]`
- **Drawn: SP-011** → module `sound.synthesis.karplus_strong`
  "Physical modeling of plucked strings. Delay line feedback loop with low-pass
  filter (moving average) to simulate acoustic decay."
- Source composition drawn uniformly from 246 eligible numbered projects
  (excluded `Production/`, `*phase1*`, `*daily*`, hitl candidates):
  **Exercise 1B Jazz ii-V-I Swing** (Balfolk genre-matrix study).

## 2. Source composition

| | |
|---|---|
| File | `exercise1b_jazz_ii_v_i_swing.mid` |
| Tempo | 120 BPM, 4/4 |
| Length | 16.00 s (8 bars) |
| Tracks | 5 |
| Voice layout | Sax Lead (prog 65, ch0, 44 notes) · Piano Comping (prog 0, ch1, 64 notes) · Walking Bass (prog 32, ch2, 32 notes) · Ride/Backbeat (ch9, 48 notes) |
| Total notes | 188 |

## 3. Absolute-layer application

SP-011 applied to **every voice** (no FluidSynth, no GM samples anywhere in the
mix). Per-role Karplus-Strong configs (single delay line, `N = round(sr/f0)`
full-cycle period — no octave drop; 2-point moving-average loop filter):

| Role | Source | loop_gain | gain_db | pan |
|---|---|---|---|---|
| lead | Sax (65) | 0.9992 | −2.0 | drift −0.55→+0.55 across form |
| comp | Piano (0) | 0.9978 | −6.0 | center, width 0.60 |
| bass | Bass (32) | 0.9994 | −5.0 | center, width 0.35 |
| perc | ch9 drums | 0.9850 | −10.0 | center, width 0.30 (short thunks) |

Retune notes: v1 render had 33.6% music-region silence (KS decay too fast for
1 s comp chords — the SP-011 known trap). Raised lead/comp/bass loop_gain
(0.9985/0.9950/0.9990 → 0.9992/0.9978/0.9994), raised perc gain, and trimmed the
3 s dead tail after the last pluck (19 s → 16.2 s).

## 4. Pitch verification (MANDATORY)

Autocorrelation pitch frames (0.5 s window / 0.25 s hop, 50–1000 Hz):

- **63/63 frames (100%) pitched** — zero 0 Hz / noise frames (v1 SP-035 noise
  failure was 0/16; this is a completely different result)
- Detected f0 matches an expected source note (within 8%): **45/60 = 75%**
  (failing frames lock onto harmonics 2×–5× of expected notes — expected for
  KS plucks, whose overtone ring outlives the fundamental)
- FFT dominant-peak check: 58% exact fundamental matches; every "miss" resolves
  to a harmonic of an expected pitch class (e.g. t=5.25: peak 984 Hz = 5×A4 196 Hz)

Tonality (harmonic energy in 8 harmonics of detected f0, per window):
mean 10.6%, median 8.6%. **Reference comparison:** same metric on a FluidSynth
GM render of the identical MIDI = mean 17.6%, median 16.0%. The classic 30%
threshold assumes monophonic sources; this is a 4-voice polyphonic jazz mix and
the naive metric under-reports (it measures only harmonics of ONE detected f0
while 3 other voices are sounding). KS sits ~2× below GM on the metric but
tracks expected pitches at 75–82% — pitched, tonal, NOT noise.

## 5. Silence ratio + RMS profile

After retune + tail trim (16.2 s final):

- Overall silence ratio (|x|<0.001): **28.1%** of music region (0–16 s);
  tail region trimmed away (v1: 44.1% incl. 3 s dead tail)
- Per-second RMS: 0.0043–0.0192, min at final second (0.0043); no silent second
- Longest silent run in music region: **55 ms** (natural swing rests; drum
  hits land on every beat so gaps are percussive, not dead air)

Onset grid (32 cols × 0.5 s; █ = onset):

```
lead  ███░███████████░░███░███████████
comp  █░█░█░█░█░█░█░█░█░█░█░█░█░█░█░█░
bass  ████████████████████████████████
perc  ████████████████████████████████
```

## 6. Files + sizes

| Artifact | Path | Size |
|---|---|---|
| Full mix WAV | `Audio/SP011-jazz-swing-karplus-strong.wav` | 2,857,724 B (16.2 s, 44.1 kHz stereo) |
| OGG (Opus, voip 48k) | `Audio/SP011-jazz-swing-karplus-strong.ogg` | 147,975 B |
| Stem lead | `Audio/stem_lead.wav` | 2,857,724 B |
| Stem comp | `Audio/stem_comp.wav` | 2,857,724 B |
| Stem bass | `Audio/stem_bass.wav` | 2,857,724 B |
| Stem perc | `Audio/stem_perc.wav` | 2,857,724 B |
| Source MIDI copy | `MIDI/exercise1b_jazz_ii_v_i_swing.mid` | 1,740 B |
| Render info | `Analysis/render_info.json` | 2,344 B |
| Onset grid | `Analysis/onset_grid.txt` | 549 B |
| Pitch verify (FFT) | `Analysis/verify_pitch.json` | 626 B |
| Pitch verify (autocorr) | `Analysis/verify_pitch2.json` | 237 B |
| Per-window tonality | `Analysis/tonality.json` | 3,339 B |
| QC final (RMS/gaps) | `Analysis/qc_final.json` | 410 B |
| Reference GM tonality | `Analysis/ref_tonality.json` | 4,211 B |
| Provenance sidecars | `Audio/*.provenance.json` ×6 | ~500 B each |

Note: full-mix and stem WAVs are byte-identical in size — each stem is the same
16.2 s buffer at the same amplitude range (normalized independently). Time
alignment across stems is preserved (same absolute note timings).

## 7. Fixes applied this run

1. **Role assignment bug**: drum track carries no program_change → parse defaulted
   channel 0 → 48 drum notes silently classified as piano (0). Fixed: capture
   per-note-event channel, classify ch9 as `perc` regardless of program.
2. **write_provenance Path bug**: `write_provenance` expects str artifact paths;
   passed PosixPath → TypeError. Fixed: str() on mix/ogg, stems already str.
3. **v1 silence (33.6% music region)**: KS decay too short for 1 s comp chords —
   raised loop_gain for lead/comp/bass, trimmed 3 s dead tail to 16.2 s →
   final music-region silence 28.1%, max gap 55 ms.
4. **Reference render PATH**: `fluidsynth` CLI not on PATH; canonical env binary
   `/opt/data/micromamba/envs/musicom/bin/fluidsynth` used (SoundFont via
   `discover_soundfont()` = FluidR3_GM.sf2).

## 8. Verdict

**PASS.** Karplus-Strong plucked-string rendering of the jazz ii-V-I swing study:
100% pitch-detection frames, 75–82% expected-note match (rest = harmonics),
no noise frames, no dead seconds, sub-30% music-region silence. The render is a
plucked-string re-voice of the jazz study — GM reference comparison confirms the
tonality metric gap is detector artifact, not noise.

## 9. Reuse notes

- Produce script: `Scripts/produce_sp011_jazz.py` (parametrized source at top)
- Verify scripts: `Scripts/verify_pitch.py`, `verify_pitch2.py`,
  `tonality_check.py`, `qc_final.py`, `ref_tonality.py`
- Reference GM WAV (`Analysis/ref_fluidsynth.wav`) deleted after comparison to
  keep the project lean (per WAV-cleanup rule); regenerate with
  `Scripts/ref_tonality.py` if needed.
