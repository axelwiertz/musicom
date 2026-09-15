# 096-trap-skeleton-seoul — Trap x Method 001 (Skeleton-First Refinement)

**Date:** 2026-09-15 (nightly autonomous composition cron)
**Style:** Trap — dark half-time (140 BPM, felt ~70, C phrygian)
**Layer:** `concrete` (6-of-7 concrete cadence; last abstract runs 085/087/089/090)
**Method:** **001 Skeleton-First Refinement** — implementation
`generators.base.FunctionGenerator` (registry-confirmed) driving a fixed
section bar-plan + density skeleton, realized through the musicom rules layer
**Seed:** 20260915
**Key:** C phrygian (C Db Eb F G Ab Bb) · **BPM:** 140 · 4/4 · 480 TPB
(bar = 1920, 8th = 240, 16th = 120)
**Form:** 6 sections x 4 bars = 24 bars — Intro | VerseA | HookB |
Bridge | HookB2 | Outro (section = 7680 ticks, total = 46080 ticks)
**Project dir:** `/opt/data/repos/musicom/projects/Styles/Trap/096-trap-skeleton-seoul`
(symlink alias `/opt/data/projects/Styles/Trap/096-trap-skeleton-seoul`)

---

## 1. Report contract — headline results

| Gate | Result |
|---|---|
| `validate()` phase 1 (raw) | **True / OK** |
| `validate()` phase 2 (rules) | **True / OK** |
| Grid audit phase 2 (16th = 120 @ 480 TPB) | **0 off-grid / 891 notes** (8th off-grid 11/891 = legit 16ths) |
| Grid audit phase 1 (raw fingerprint) | 117 off-grid / 121 notes (by design) |
| Harmony audit (scale + chord tones, all pitched voices) | **0 out-of-scale, 0 out-of-chord** |
| Range audit (instrument registry) | **PASS** (all 5 pitched voices in range) |
| Zero-drift (all tracks end at same tick) | **PASS** — max_end = 46080 ticks both phases |
| Phase-1 pitch ground truth (known MIDI notes) | **PASS 121/121** fundamentals present, 121/121 harmonic ratio > 0.30 |
| Phase-2 tonal check (polyphonic mix) | **CHECK** — 83/83 autocorr frames pitched, chroma top-3 in key 81.9 %, full-band peak test 48.2 % on-note (bass + hats dominate argmax, same band-split class effect as 095) |
| Silence / RMS | **PASS** — 7.05 % total silence, only tail secs 42-44, peak 0.8547 |
| Voice-leading (classical, 808 + bell) | 5 flags pre-fix -> **0 after fix** |
| Preflight compliance | **COMPLIANT** (engine only, mido READ-only in analysis) |

Primary record: this file. Machine-readable mirrors: `Analysis/audit.json`,
`Analysis/summary.json`, `Analysis/tonal_check.json`,
`Analysis/render_stats.json`, `Analysis/render_info.json`,
`Analysis/concept.json`.

---

## 2. Selection (auditable)

- **Style pool:** 45 genre folders under `projects/Styles/` (excluding
  `_Comparison`, `_Data_Patterns`, `Research`, `Poetry`, `Production`,
  `Percussion`, `Other`, `016-genre-pattern-dataset`, `Celtic `). Recent
  styles excluded (Celtic, Baroque, Disco, Rock, African, Klezmer);
  `random.seed(20260915)` drew **Trap**.
- **Method pool:** cron-ready registry code minus the last-7-day methods
  (`003` 091, `018` 092, `012` 093, `010` 094, `079` 095, `ABS-002`
  089/090, `002` 086, `045` 088) leaves `001, 023, 040, ABS-001/003/004/
  005, HC-012`; concrete-night filter leaves `001, 023, 040, HC-012`;
  seed drew **001** (concrete night).
- **Layer cadence:** 6-of-7 concrete. Most recent abstract runs 085/087/089/
  090; 091/092/093/094/095 all concrete, so tonight is **concrete**.

Selection record: `projects/Research/selection/night_2026-09-15.json`.

---

## 3. Method mechanics (Method 001, concrete)

Method 001 *Skeleton-First Refinement* = form-first drafting: a
deterministic structural skeleton (section bar-plan + per-section harmonic
skeleton + per-section density map) is fixed BEFORE any notes exist;
micro-variation (ornament, pickup, counter-shadow) is added only inside
the skeleton afterwards. The repo implementation is
`generators.base.FunctionGenerator`:

| Step | Call |
|---|---|
| Skeleton build | `FunctionGenerator(function=skeleton_plan)` returns the 6-row section plan (section / bars / degrees / density) |
| Skeleton assert | rows == NAMES, degrees == PROG_DEG slices (plan integrity proven in stdout) |
| Realization | skeleton slots filled with phrygian motif + chord-tone rules (phase 2) |

Per-section density skeleton (the method-001 artifact):

| Section | hat | lead | drums | bass |
|---|---|---|---|---|
| Intro | sparse8 | half | lite | long |
| VerseA | 16 | full | half | half |
| HookB | 16roll | full | full | full |
| Bridge | sparse8 | half | lite | long |
| HookB2 | 16roll | full | full | full |
| Outro | sparse8 | half | lite | long |

---

## 4. Two-phase architecture

### Phase 1 — raw generative draft (`MIDI/096-trap-skeleton-seoul-phase1.mid`, 1162 B)

Single voice (`LeadRaw`, GM 12 marimba), **no mode, no harmony**. The
method's pre-rules material:

- Rhythm = 8th-slot walk at a **fractional 311-tick unit** (NOT a 120/240
  multiple) + 18 % dropout rests -> off-grid by construction.
- Pitch = unquantized chromatic random walk from C5 (`P1_STEPS` + 0.9*N(0,1)
  drift, clamped 55-96) — no scale snap, no chord context.
- Per-section densities/counts `P1_N/P1_C` so the draft breathes Intro->Outro.

### Phase 2 — rules post-process (`MIDI/096-trap-skeleton-seoul.mid`, 7536 B)

1. 16th-grid lock (078 mandatory rule): all onsets on the 120-grid.
2. C-phrygian scale snap -> bar chord-tone quantize per bar through the
   canonical `Scale7ChordDegree.get_diatonic_note` (no `% 7` wrappers).
3. Bell contour in scale-degree steps `MOTIF_STEPS =
   [0, 1, 1, -1, 0, -2, 1, 0, 2, -1, -1, 0]`, seeded from the phase-1
   per-section mean (draft steers register, rules own pitch).
4. Violin counter: contrary-ish shadow a third-ish below, chord-locked.
5. Leap cap (> 10 st -> nearest chord tone) + overlap clamp per voice.
6. Voice-leading check/correction (rules.voice_leading, classical) on outer
   voices (808 root + bell lead): 5 flags -> 5 fixes -> 0 remaining.
7. Full 6-voice trap texture (see section 6).

---

## 5. Progression (24 bars, 0-based phrygian degrees)

```
Intro   i   i   bII i    | VerseA i   bII bvii bII
HookB   bvii bII i   i   | Bridge bVII iv  bII bII
HookB2  bvii bII i   i   | Outro  i   bII i   i
```

Bar labels:

```
C-i C-i Db-bII C-i | C-i Db-bII Bb-bvii Db-bII |
Bb-bvii Db-bII C-i C-i | Bb-bVII F-iv Db-bII Db-bII |
Bb-bvii Db-bII C-i C-i | C-i Db-bII C-i C-i
```

All diatonic to C phrygian; outro closes bII -> i (phrygian half-cadence
weight into the tonic).

---

## 6. Voices (instrument registry, source of truth)

| Voice | Instrument | GM | Ch | Register | Role |
|---|---|---|---|---|---|
| BellLead | Marimba | 12 | 0 | 65-77 (range 45-96) | phrygian bell motif, chord-locked |
| ViolinCtr | Violin | 40 | 1 | 63-73 (range 55-103) | counter shadow, third-ish below |
| PianoStab | Piano | 1 | 2 | 48-58 (range 21-108) | dark quarter-note triad stabs |
| Sub808 | Double Bass | 43 | 4 | 34-44 (range 28-74) | half-time 808 (longs + fills) |
| BrassStab | Trumpet | 56 | 5 | 60-80 (range 54-86) | offbeat 8th horn stabs |
| Drums | Drum Kit | 0 | 9 | kit pcs | half-time kit: kick 1 + 720 pickup, snare on 3, section hats |

Drum details: kick on beat 1 + 8th pickup at 720 (half sections: beat 1
only); snare on beat 3 (960) every bar (half-time backbeat); hats follow
the skeleton (sparse 8ths / 16ths / 16ths + on-grid Hook pickup at
BAR-120); crash on section-opening downbeats (Intro/HookB/Bridge/Outro).

---

## 7. Grid audit (mandatory, per voice)

```
BellLead   prog= 12 ch=0 notes= 120 off16=0 off8=0 end=46080
ViolinCtr  prog= 40 ch=1 notes= 120 off16=0 off8=0 end=46080
PianoStab  prog=  1 ch=2 notes= 288 off16=0 off8=0 end=46080
Sub808     prog= 43 ch=4 notes=  48 off16=0 off8=0 end=46080
BrassStab  prog= 56 ch=5 notes=  99 off16=0 off8=3 end=46080
Drums      prog=  0 ch=9 notes= 216 off16=0 off8=8 end=46080
```

Phase-2 total: **0 off-16th / 891 notes**. The 11 off-8th are legit 16ths
(BAR-120 Hook pickup, brass tail pickup) — same reporting convention as 095.
Phase-1 fingerprint: 117 off-16th / 121 notes (raw, by design).

Fix applied during the run: first audit showed 24 off-16th (32nd-tick hat
rolls at 60/30 ticks + 840-tick kick + Hook pickup). Fixed by moving the
kick pickup to the on-grid 8th at 720, replacing 32nd rolls with a single
on-grid 16th pickup (BAR-120), and re-exporting — second audit 0 off-16th.

---

## 8. Harmony audit (mandatory, per pitched voice)

```
BellLead   notes= 120 out_scale=0 out_chord=0
ViolinCtr  notes= 120 out_scale=0 out_chord=0
PianoStab  notes= 288 out_scale=0 out_chord=0
Sub808     notes=  48 out_scale=0 out_chord=0
BrassStab  notes=  99 out_scale=0 out_chord=0
```

**0 out-of-scale, 0 out-of-chord** — every pitched voice chord-quantized
per bar (078 class-bug patch honored: no voice holds non-chord tones).

---

## 9. Range + zero-drift

Range (registry `in_range`): BellLead 65-77 in 45-96 PASS; ViolinCtr
63-73 in 55-103 PASS; PianoStab 48-58 in 21-108 PASS; Sub808 34-44 in
28-74 PASS; BrassStab 60-80 in 54-86 PASS. Drums skipped (channel 9).

Zero-drift: all 6 voice tracks end at 46080 ticks (24 bars x 1920);
`validate()` True on both phases; terminal landmark padding per cell.

---

## 10. Render + verification numbers

- Engine: FluidSynth CLI (`-ni -g 1.0 -F`), FluidR3_GM.sf2, peak-normalized
  to 0.89, Opus OGG (`libopus voip 48k`).
- Phase 2: WAV 7905102 B, OGG 295856 B, peak 0.8547, silence 7.05 %,
  silent secs [42, 43, 44] (post-music DAW tail only), duration 44.81 s.
- Phase 1: WAV 7711054 B, OGG 374648 B, peak 0.888, silence 8.51 %,
  silent secs [42, 43] (tail only), duration 43.71 s.
- Per-second RMS (phase 2): musicband 0.117-0.167 every second 0-41, tail
  0.036 -> 0.000 — no mid-track gaps.
- Tonal phase 1: 121/121 fundamentals present, 121/121 harmonic ratio
  > 0.30 -> PASS (synthesis path verified tonal, not noise).
- Tonal phase 2: 83/83 autocorr frames pitched, chroma top-3 in key
  81.9 %, median harmonic ratio 0.159 (full-band peak test 48.2 %
  on-note: expected — sub-808 + hats dominate the argmax; same
  band-split class effect documented on 095).
- File sizes: phase-1 MID 1162 B, phase-2 MID 7536 B (all > 40 B).

---

## 11. Files

```
MIDI/096-trap-skeleton-seoul-phase1.mid (+ .provenance.json)
MIDI/096-trap-skeleton-seoul.mid (+ .provenance.json)
Audio/096-trap-skeleton-seoul.wav / .ogg
Audio/096-trap-skeleton-seoul-phase1.wav / .ogg
Analysis/grid_visualization.txt Analysis/matrix_grid.txt Analysis/audit.json
Analysis/summary.json Analysis/tonal_check.json Analysis/render_stats.json
Analysis/render_info.json Analysis/concept.json
Scripts/compose.py Scripts/audit.py Scripts/render_audio.py
Scripts/audio_stats.py Scripts/tonal_check.py Scripts/summarize.py
README.md REPORT.md
```

---

## 12. Fixes applied this run

1. Hat 32nd-rolls (60/30-tick) + 840-tick kick + BAR-30/60/90 pickup all
   off the 120-grid -> moved kick to on-grid 720, rolls to single on-grid
   16th pickup (BAR-120); re-export + re-audit -> 0 off-16th.
2. Audit INTRO label bug (`(0, 2)` piano key): piano (GM 1, ch 2) reported
   as UNKNOWN PROG `track3` -> fixed key to `(1, 2)`; all voices named.
3. VL 5 parallel/hidden flags (bass + bell) -> 5 chord-tone fixes, re-check 0.
4. `tonal_check.py` typo (`n Pitched`) -> fixed before first run.
5. Preflight: COMPLIANT, exit 0 (mido READ-only in analysis scripts with
   `# READING ONLY (analysis)` marker + compliant musicom imports).

---

## 13. Selection record

```json
{
  "run_date": "2026-09-15",
  "seed": 20260915,
  "style_pool_n": 45,
  "style_eligible_n": 39,
  "style": "Trap",
  "layer": "concrete",
  "cadence": "concrete (prior abstract runs 085/087/089/090; 091/092/093/094/095 concrete)",
  "candidate_pool": [
    "001",
    "023",
    "040",
    "ABS-001",
    "ABS-003",
    "ABS-004",
    "ABS-005",
    "HC-012"
  ],
  "excluded_recent": [
    "003",
    "010",
    "012",
    "018",
    "079",
    "ABS-002"
  ],
  "method": "001"
}
```

**Next variables:** 808 glide sculpt, bell octave pops in Hooks, counter
call-response bars, hi-hat velocity swing humanization.
