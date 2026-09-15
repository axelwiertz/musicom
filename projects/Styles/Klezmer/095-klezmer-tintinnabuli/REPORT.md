# 095-klezmer-tintinnabuli — Klezmer x Method 079 (Tintinnabuli Composition)

**Date:** 2026-09-14 (nightly autonomous composition cron)
**Style:** Klezmer — freylekhs wedding-dance (124 BPM, D harmonic minor)
**Layer:** `concrete` (6-of-7 concrete cadence; last abstract runs 085/087/089/090)
**Method:** **079 Tintinnabuli Composition (TINC)** — implementation
`generators.tintinnabuli.TintinnabuliGenerator` (registry-confirmed) + ABS-003
Z-variation bridge color (`rules.patterns.z_pair_catalogue`)
**Seed:** 20260914
**Key:** D harmonic minor (D E F G A Bb C#) · **BPM:** 124 · 4/4 · 480 TPB
(bar = 1920, 8th = 240, 16th = 120)
**Form:** 6 sections x 4 bars = 24 bars — Intro | FreylekhsA | FreylekhsB |
Bridge | FreylekhsA2 | Outro (section = 7680 ticks, total = 46080 ticks)
**Project dir:** `/opt/data/repos/musicom/projects/Styles/Klezmer/095-klezmer-tintinnabuli`
(symlink alias `/opt/data/projects/Styles/Klezmer/095-klezmer-tintinnabuli`)

---

## 1. Report contract — headline results

| Gate | Result |
|---|---|
| `validate()` phase 1 (raw) | **True / OK** |
| `validate()` phase 2 (rules) | **True / OK** |
| Grid audit phase 2 (16th = 120 @ 480 TPB) | **0 off-grid / 1095 notes** (8th off-grid 3/1095 = legit 16ths) |
| Grid audit phase 1 (raw fingerprint) | 131 off-grid / 138 notes (by design) |
| Harmony audit (scale + chord tones, all pitched voices) | **0 out-of-scale, 0 out-of-chord** |
| Range audit (instrument registry) | **PASS** (all 5 pitched voices in range) |
| Zero-drift (all tracks end at same tick) | **PASS** — max_end = 46080 ticks both phases |
| Phase-1 pitch ground truth (known MIDI notes) | **PASS 138/138** fundamentals present, 137/138 harmonic ratio > 0.30 |
| Phase-2 tonal check (polyphonic mix) | **CHECK** — 90/94 autocorr frames pitched, median f0 169.7 Hz; full-band peak test not applicable (bass + hats dominate argmax, verified by band-split diag) |
| Silence / RMS | **PASS** — 5.69% total silence, only tail secs 47-49, peak 0.8868 |
| Voice-leading (classical, bass + violin M) | 5 flags pre-fix -> **0 after fix** |

Primary record: this file. Machine-readable mirrors: `Analysis/audit.json`,
`Analysis/summary.json`, `Analysis/tonal_check.json`,
`Analysis/render_stats.json`, `Analysis/render_info.json`,
`Analysis/concept.json`.

---

## 2. Selection (auditable)

- **Style pool:** 47 genre folders under `projects/Styles/` (excluding
  `_Comparison`, `_Data_Patterns`, `Research`, `Poetry`, `Production`,
  `Percussion`, `Other`). Recent styles excluded (African, Rock, Disco,
  Baroque, Celtic, Electronic); `random.seed(20260914)` drew **Klezmer**.
  (016-genre-pattern-dataset included in pool listing but never drawn; it is
  a data asset, not a genre.)
- **Method pool:** `workflows.selector.select_for_cron()` = headless +
  deterministic methods that HAVE registry code: `001, 010, 012, 018, 023,
  040, 079, ABS-001..005, HC-012`. Excluding the last-7-day methods (`002`
  086, `003` 091, `018` 092, `045` 088, `010` 094, `012` 093) leaves `001,
  023, 040, 079, ABS-001..005, HC-012`; seed drew **079** (concrete night).
- **Layer cadence:** 6-of-7 concrete. Most recent abstract runs 085/087/089/
  090; 091/092/093/094 all concrete, so tonight is **concrete**.

Selection record: `Analysis/../Research/selection/night_2026-09-14.json`
(written below, section 13).

---

## 3. Method mechanics (Method 079, concrete + ABS-003 color)

Method 079 *Tintinnabuli Composition* = Arvo Part's two-voice procedure:
a stepwise **M-voice** (melodic, moves within a mode) shadowed note-by-note by
a **T-voice** that only ever uses tones of ONE fixed tonic triad. Every dyad
contains a triad tone -> constant consonance, no functional harmony.
The repo implementation is `generators.tintinnabuli.TintinnabuliGenerator`:

- `m_voice(unit)` snaps each pitch to the nearest D-harmonic-minor degree.
- `t_voice(pitches, position, ...)` picks the nearest tonic-triad tone per
  M-note (position selects which near triad tone).
- `isorhythmize(color, talea)` maps a pitch color onto a repeating duration
  talea (both cycle; LCM = full period).

This piece wires the engine calls directly (not a reimplementation):

| Step | Call |
|---|---|
| M conform | `TINC.m_voice(m_unit)` on every section (D harmonic minor) |
| T shadow | `TINC.t_voice(m_pitches, position=T_POS[s], ...)` per section |
| Isorhythm | talea `[1, 0.5, 0.5, 1, 0.5, 1]` beats -> onsets `[0, 480, 720, 960, 1440, 1680]` (all % 120 == 0) |
| Parity | TINC m_voice vs rules M: **144/144 within 2 semitones** |

**ABS-003 Z-variation** (abstract color inside a concrete night): the Bridge
carries a hexachord Z-pair texture from `rules.patterns.z_pair_catalogue(6)`:
`z_6-Z50 {0,1,4,6,7,9} T=19.00` <-> `z_6-Z29 {0,2,3,6,7,9} T=19.00` —
same tension, different notes (documented in concept.json; the freylekhs
texture keeps bar chord tones, so the pair acts as color, not as harmony).

T-voice position cycle per section: `[0, 1, 0, 2, 0, 1]` (Part-style
nearest-above with slow outward drift in the Bridge).

---

## 4. Two-phase architecture

### Phase 1 — raw generative draft (`MIDI/095-klezmer-tintinnabuli-phase1.mid`, 1301 B)

Single voice (`LeadRaw`, GM 40 violin), **no mode, no triad, no harmony**.
The method's pre-rules material:

- Rhythm = 8th-slot walk at a **fractional 317-tick unit** (NOT a 120/240
  multiple), jittered +-6% per onset -> off-grid by construction.
- Pitch = unquantized chromatic random walk from D5 (`P1_STEPS` + 0.9*N(0,1)
  drift, clamped 55-96) — no scale snap, no chord context.
- Per-section densities/counts `P1_N/P1_C` so the draft breathes Intro->Outro.

### Phase 2 — rules post-process (`MIDI/095-klezmer-tintinnabuli.mid`, 9356 B)

1. 16th-grid lock (078 mandatory rule): talea onsets all on the 120-grid.
2. D-harmonic-minor scale snap -> M chord-tone quantize per bar through the
   canonical `Scale7ChordDegree.get_diatonic_note` (no `% 7` wrappers).
3. T-voice from the ENGINE `t_voice`, folded into the clarinet register with
   triad priority (nearest D-F-A tone within 4 st, else nearest bar chord
   tone) -> audit invariant: T = tonic-triad pc OR bar chord tone.
4. Bass offbeats chord-quantized (root-anchored fifth color) — patches the
   project-078 class bug (no voice holds non-chord tones).
5. Voice-leading check/correction (rules.voice_leading, classical) on outer
   voices -> 5 flags fixed -> re-check 0.
6. Full 6-voice klezmer texture (below).

---

## 5. Progression (24 bars, 0-based degrees in D harmonic minor)

```
Intro       i  VII VII i    = Dm · C#dim · C#dim · Dm
FreylekhsA  i  VII VI  VII  = Dm · C#dim · Bb · C#dim
FreylekhsB  VI VII i   i    = Bb · C#dim · Dm · Dm
Bridge      iv VI  VII VII  = Gm · Bb · C#dim · C#dim
FreylekhsA2 i  VII VI  VII  = Dm · C#dim · Bb · C#dim
Outro       i  VII i   i    = Dm · C#dim · Dm · Dm
```

Degree roots via `Scale7ChordDegree.get_diatonic_note(62, HMINOR, degree)`.
Labels: Di / C#VII / BbVI / Giv (see `Analysis/concept.json` progression).

---

## 6. Voices & instruments (registry source of truth)

| Row | Voice | Instrument (registry) | GM | Ch | Notes | Register used |
|---|---|---|---|---|---|---|
| 0 | ViolinM | Violin | 40 | 0 | 144 | 65-91 (range 55-103, sweet 67-96) |
| 1 | ClarinetT | Clarinet | 71 | 1 | 144 | 62-69 (range 52-96) |
| 2 | Trumpet | Trumpet | 56 | 2 | 99 | 67-82 (range 54-86) |
| 3 | Dulcimer | Dulcimer | 15 | 3 | 192 | 58-69 (range 48-96) |
| 4 | Bass | Double Bass | 43 | 4 | 192 | 34-50 (range 28-74) |
| 5 | Drums | Drum Kit | 0 | 9 | 324 | kit map (kick 36, snare 38, hats 42, crash 49) |

Roles: violin M (talea lead) / clarinet T (triad shadow) / trumpet offbeat
calls + pushes / dulcimer quarter-note root+fifth chops / bass oom-pah 8ths
(root quarters + chord-tone offbeats) / drums freylekhs oom-pah (kick 1&3,
snare 2&4 + offbeat pah ghosts in A/B sections, 8th hats, section crashes).

---

## 7. Verification (real numbers)

### Grid audit (phase-2 MIDI, mido read-only) — **PASS**

```
16th off-grid: 0/1095        (8th off-grid 3/1095 = legit 16ths: trumpet pushes)
  ViolinM    ch=0 notes=144 off16=0 off8=  0 end=46080
  ClarinetT  ch=1 notes=144 off16=0 off8=  0 end=46080
  Trumpet    ch=2 notes= 99 off16=0 off8=  3 end=46080
  Dulcimer   ch=3 notes=192 off16=0 off8=  0 end=46080
  Bass       ch=4 notes=192 off16=0 off8=  0 end=46080
  Drums      ch=9 notes=324 off16=0 off8=  0 end=46080
```

Phase-1 fingerprint: 131/138 off-grid (raw draft NOT grid-locked, by design).

### Harmony audit (phase-2, canonical degree table) — **PASS**

```
  ViolinM    out_of_scale=0 out_of_chord=0
  ClarinetT  out_of_scale=0 out_of_chord=0   (T = triad pc OR bar chord tone)
  Trumpet    out_of_scale=0 out_of_chord=0
  Dulcimer   out_of_scale=0 out_of_chord=0
  Bass       out_of_scale=0 out_of_chord=0
```

Audit scale = D harmonic minor pcs {2,4,5,7,9,10,1}; bar attribution by
`st // BAR` (floor, matches compose). T-voice exception is method-079's Part
rule, stated in code and in `Scripts/audit.py`.

### Range audit — **PASS** (all 5 pitched voices inside registry ranges)

### Zero-drift — **PASS** (max_end 46080 all tracks, both phases)

### Voice-leading — 5 flags (parallel/hidden, classical) -> 5 fixes ->
re-check **0 remaining**.

### TINC engine parity — 144/144 M-notes within 2 st of `m_voice` output.

---

## 8. Audio (SP-001 FluidSynth, discover_soundfont -> FluidR3_GM.sf2)

- Full mix: 49.29 s, peak 0.8868 (normalized to 0.89 ~ -1 dBFS), **silence
  5.69%** (< 30% PASS). Only silent seconds 47-49 = legit tail decay after
  the final Dm; **no mid-track gaps** (per-second RMS 0.096-0.136 throughout).
- Phase-1 render: 48.45 s, peak 0.8114, silence 5.88% (single violin draft,
  audible throughout).
- WAV sizes sane (8.69 MB / 8.55 MB — no FluidSynth blowup); OGG 348 kB /
  391 kB (Opus voip 48k).
- All artifacts size > 40 B asserted; provenance.json sidecars written.

### Pitch verification (synthesis checked for PITCH, not just size/silence)

- Phase-1 ground truth (single violin, known MIDI): **138/138 fundamentals
  present, 137/138 harmonic ratio > 0.30** -> PASS.
- Phase-2 polyphonic mix: 90/94 autocorr frames pitched (median f0 169.7 Hz).
  The naive full-band argmax test reads CHECK (peak median 97 Hz = bass root
  zone; melody-band argmax locks onto 442 Hz violin overtones in several
  windows) — EXPECTED for a bass-heavy freylekhs mix, not a synth defect.
  Band-split diag: bass band median 74 Hz (D2), melody band shows 442/74/68
  Hz mixture, hats band ~2.1 kHz. Phase-1 ground truth is the binding pitch
  proof; phase-2 numbers reported raw, no tuning.

---

## 9. Bugs found & fixed during completion

1. **Harmony audit FAIL (72 clarinet-T + 40 bass off-chord)**: first build
   locked violin/trumpet/dulcimer to chord tones but let the T-voice hold
   pure tonic-triad tones over foreign bars and gave the bass raw fifth
   offbeats (`root+7` unquantized) — the project-078 class bug (56/96
   out-of-scale counterline in F-minor Soul). Fixed by (a) T triad-priority
   fold (nearest D-F-A within 4 st, else bar chord tone) + explicit Part-rule
   audit exception, (b) bass offbeats chord-quantized root-anchored.
   Re-audit: 0 out-of-scale, 0 out-of-chord.
2. **Voice-leading runtime warnings**: `check_parallel_motion` overflow
   RuntimeWarnings (numpy scalar subtract, same as 090) — harmless; flags
   correctly detected and fixed.
3. **TALEA bar-fill check**: talea `[1,.5,.5,1,.5,1]` sums to 4.5 beats, so
   `talea_onsets` walks the cycle across the barline (LCM period) rather
   than looping per bar — asserted on-grid (all % 120 == 0), 6 onsets/bar.

---

## 10. Method rationale (why 079 + Klezmer)

TINC's static-triad consonance is the inverse of klezmer's usual functional
freylekhs drive — that friction IS the study: the violin still dances the
i-VII-VI-VII freylekhs progression bar by bar, but the clarinet refuses to
leave D-F-A, so every bar recolors the same shadow (consonant over i,
aching minor-9th rubs over VII). The talea gives the freylekhs lilt without
copying a folk groove literally, and the Z-pair documents that same-tension
reharmonization exists inside the concrete night without breaking the audit.

---

## 11. Files

```
MIDI/095-klezmer-tintinnabuli-phase1.mid   (1301 B, raw phase-1 draft)
MIDI/095-klezmer-tintinnabuli.mid          (9356 B, phase-2 arrangement)
Audio/095-klezmer-tintinnabuli.wav/.ogg    (full mix, SP-001)
Audio/095-klezmer-tintinnabuli-phase1.wav/.ogg (phase-1 render)
Analysis/grid_visualization.txt            (8th-slot density grid)
Analysis/matrix_grid.txt                   (canonical UnitMatrix render)
Analysis/summary.json                      (project summary)
Analysis/audit.json                        (grid+harmony+range+drift: PASS)
Analysis/tonal_check.json                  (pitch verification)
Analysis/render_stats.json                 (silence/RMS/peak)
Analysis/render_info.json                  (FluidSynth normalization record)
Analysis/concept.json                      (method/seed/progression)
Scripts/compose.py | audit.py | render_audio.py | audio_stats.py
      | tonal_check.py | summarize.py
```

Rhythm DNA (8th-slot grid, `.` rest `+` 1-2 `#` 3+; 24 bars):

```
ViolinM     6 onsets/bar (talea 1 .5 .5 1 .5 1)
ClarinetT   6 onsets/bar (T shadows M 1:1)
Trumpet     4-5 onsets/bar (offbeat calls + pushes)
Dulcimer    8 onsets/bar (quarter dyads x2 notes)
Bass        8 onsets/bar (oom-pah 8ths)
Drums       10-17 onsets/bar (A/B sections densest)
```

---

## 12. Reproduce

```bash
/opt/data/micromamba/envs/musicom/bin/python \
  /opt/data/repos/musicom/projects/Styles/Klezmer/095-klezmer-tintinnabuli/Scripts/compose.py
/opt/data/micromamba/envs/musicom/bin/python \
  /opt/data/repos/musicom/projects/Styles/Klezmer/095-klezmer-tintinnabuli/Scripts/audit.py
/opt/data/micromamba/envs/musicom/bin/python \
  /opt/data/repos/musicom/projects/Styles/Klezmer/095-klezmer-tintinnabuli/Scripts/render_audio.py
/opt/data/micromamba/envs/musicom/bin/python \
  /opt/data/repos/musicom/projects/Styles/Klezmer/095-klezmer-tintinnabuli/Scripts/audio_stats.py
/opt/data/micromamba/envs/musicom/bin/python \
  /opt/data/repos/musicom/projects/Styles/Klezmer/095-klezmer-tintinnabuli/Scripts/tonal_check.py
/opt/data/micromamba/envs/musicom/bin/python \
  /opt/data/repos/musicom/projects/Styles/Klezmer/095-klezmer-tintinnabuli/Scripts/summarize.py
```

---

## 13. Selection record

```json
{
  "run_date": "2026-09-14",
  "seed": 20260914,
  "style": "Klezmer",
  "method": "079",
  "layer": "concrete",
  "cadence": "concrete (prior abstract runs 085/087/089/090; 091/092/093/094 concrete)",
  "excluded_recent": ["002", "003", "018", "045", "010", "012"],
  "candidate_pool": ["001", "023", "040", "079", "ABS-001", "ABS-002", "ABS-003", "ABS-004", "ABS-005", "HC-012"]
}
```
