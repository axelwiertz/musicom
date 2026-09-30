# REPORT — 214-blues-antcolony

**Project:** 214-blues-antcolony
**Style:** Blues — 12-bar blues (two choruses, 24 bars) in E
**Method:** 041 Ant Colony Optimization Path Finding (ACOPF)
**Layer:** `concrete`
**Date:** 2026-09-30 (Nightly Autonomous Composition Job, ID 1fc3fd65d359)
**Seed:** 20260930
**Key:** E blues scale = E G A B♭ B D = pitch classes {2, 4, 7, 9, 10, 11} (tonic E4 = 64)
**BPM:** 100 · 4/4 · 480 TPB (bar = 1920, 16th = 120, 8th = 240, section = 7680, total = 46080)

---

## 1. Selection

| Field | Value |
|---|---|
| Style | **Blues** — random pick from the genre folders (excl. _Comparison/_Data_Patterns/Research/Poetry/Production/Percussion/Other + numbered/`Celtic `). Seed 20260930 first roll gave IndianClassical (a repeat of 212, last night), so a documented second roll (seed 20260941) landed on **Blues**. |
| Method | **041 Ant Colony Optimization Path Finding (ACOPF)** — `concrete` layer, Stochastic. Not used in the last 7 days. |
| Layer cadence | `concrete` (6-of-7 cadence). Last abstract composition job was 105 (2026-09-24, method 095 Contour Theory); abstract not yet due. |
| Recent-method exclusion | Excluded methods used in the last 7 days: {001, 010, 016, 018, 020, 025, 026, 031, 040, 048, 069, 075, 082, 095}. Random pick from the remaining concrete methods landed on **041**. |

## 2. Method essence (041 ACOPF — ant colony + blues)

A colony of **8 ants** traverses a pitch graph left-to-right across **192
eighth-note slots** (one slot = one melodic position). The graph nodes are the
25 chromatic MIDI pitches **52–76**. At each slot an ant picks a node by a
roulette wheel over:

```
desirability(node) = pheromone[slot][node]^α  ×  heuristic(node)^β
heuristic(node)    = smoothness (1/(1+|interval from prev|))  ×  register pull (to E4)
```

- A full traversal (a **tour**) is one candidate melody.
- Tour **fitness** = smoothness (small average interval) + register centering —
  **no scale/chord term** (kept out of Phase 1 on purpose).
- Pheromone is deposited on every (slot, node) of each tour proportional to
  fitness, then **evaporates** by (1−ρ). Over 60 iterations the colony's
  pheromone trail converges; the **best-ever tour** is the melodic contour.

The "pheromone trail" is literally the blues player's re-trodden lick — the
method's emergent line is the ant colony's consensus path, not a hand-drawn
contour.

| ACO parameter | Value |
|---|---|
| ants / iterations | 8 / 60 |
| α (pheromone) / β (heuristic) | 1.0 / 2.5 |
| ρ (evaporation) | 0.15 |
| node pool | 25 chromatic pitches (MIDI 52–76) |
| best fitness | 0.21749 |
| raw tour pitch range | [69, 76] (narrow plateau — see §9) |

## 3. Form, Key, Meter

| Field | Value |
|---|---|
| Form | 12-bar blues × 2 = **24 bars** (6 sections × 4 bars): `I7 / IV7-I7 / V7-IV7-I7-V7 / I7 solo / IV7-I7 solo / Turnaround` |
| Key | **E** (blues scale {E G A B♭ B D}) |
| Meter | 4/4, 100 BPM, straight "shuffle-lite" (swing accent on off-beat 8ths; all onsets on the 8th grid) |
| Progression | `I I I I / IV IV I I / V IV I V` — repeated (E blues: I=E, IV=A, V=B) |

Blues-scale harmony model (documented): each chord is a **tight subset of the
E-blues scale** anchored on its root, with no major 3rd — "blues sus-dominant"
voicings — so every chord tone stays inside the blues scale. This keeps the
harmony audit meaningful (separate out-of-scale vs out-of-chord) while both
pass at **0**.

| Chord | pcs | Notes | Root (bass) |
|---|---|---|---|
| I | {4, 11, 2, 7} | E B D G | E2 (40) |
| IV | {9, 4, 2, 7} | A E D G | A2 (45) |
| V | {11, 9, 2, 4} | B A D E | B2 (47) |

## 4. Voices & Instruments (registry source of truth)

| Voice | Instrument | GM Program | Channel | Role |
|---|---|---|---|---|
| Piano | Acoustic Grand Piano | 1 | 0 | Comp chords (block, beats 2 & 4) |
| Bass | Double Bass | 43 | 1 | Walking quarter-notes (root/top/root/mid) |
| Harmonica | Harmonica | 22 | 2 | ACO lead melody (blues solo, 8th-note phrasing) |
| Trumpet | Trumpet | 56 | 3 | Call-response (sustained off-beat 8ths) |
| Drums | Drum Kit | 0 (ch9) | 9 | Kick 1&3, snare 2&4, 8th hats + open hat |

All programs resolved via `instrument_registry.py` (source of truth), not the
10-entry `MidiInstrument` enum.

## 5. Two-Phase Architecture

### Phase 1 — Raw ACO Draft (`-phase1.mid`)
- Single voice (Raw_Lead, Harmonica).
- **Onsets** unquantized: 8th slot + micro-jitter (±18 ticks) OFF the 120/240 grid.
- **Pitch** unquantized: raw ACO best-tour nodes (chromatic, NO scale/chord snap).
- No harmony, no chord-tone quantization, no texture. `validate()` PASSED.

### Phase 2 — Musicom Rules Post-Processing (`.mid`)
- **Same ACO run** re-run with the same seed → identical raw contour, then:
  1. every onset snapped to the **8th grid** (240 ticks),
  2. every pitch snapped to its bar's **blues chord-tone set** (I/IV/V subset of the blues scale).
- Full 5-voice blues band added. `validate()` PASSED.

## 6. Verification (real numbers)

### Grid audit (every voice vs 16th/8th grid) — **0 OFF-GRID**

| Track | Onsets | off_16th | off_8th | Verdict |
|---|---|---|---|---|
| Piano | 192 | **0** | 0 | 0 off-grid |
| Bass | 96 | **0** | 0 | 0 off-grid |
| Harmonica | 192 | **0** | 0 | 0 off-grid |
| Trumpet | 36 | **0** | 0 | 0 off-grid |
| Drums (ch9) | 312 | **0** | 0 | 0 off-grid |

All **828** onsets snap to the 8th grid (therefore also the 16th grid). No 16th
syncopation was used in this pass — the "shuffle" is expressed as velocity
accent on the off-beat 8ths rather than dotted/triplet subdivisions, keeping
the grid audit fully clean.

### Harmony audit (pitched voices vs E blues scale + bar chord) — **0 OUT-OF-KEY**

| Track | Notes | out_of_scale | out_of_chord | Verdict |
|---|---|---|---|---|
| Piano | 192 | **0** | **0** | pass |
| Bass | 96 | **0** | **0** | pass |
| Harmonica | 192 | **0** | **0** | pass |
| Trumpet | 36 | **0** | **0** | pass |

All **516** pitched notes are in the E blues scale AND in their bar's chord set.
The blunt harmonic tension (major-3rd vs blues b3) is avoided by construction
via the blues sus-dominant voicings (§3).

### Audio profile (FluidSynth + FluidR3_GM.sf2 → WAV → Opus OGG)

| Phase | Duration | Silence | Peak | Tonal ratio | Verdict |
|---|---|---|---|---|---|
| Phase 2 | 62.47 s | 7.68% | 0.5834 | 99.19% | healthy (silence = reverb tail) |
| Phase 1 | 59.67 s | 8.72% | 0.2694 | 100% | raw sparse harmonica stream (expected) |

- Mid-track RMS is continuous (~0.07–0.12 across the body); the only near-zero
  RMS seconds are the final ~4 s reverb/release tail. No mid-track dead zones.
- FFT tonal content 50–1000 Hz ≥ 99% in both phases → **not noise**.
- Phase 1 vs phase 2 contrast is *texture* (1 voice vs 5) and *harmonicity*
  (chromatic wander vs blues-chord-locked), exactly as intended.

## 7. Zero-drift status

`UnitMatrixComposer.validate()` PASSED for **both** phases. All 5 tracks equal
length (46080 ticks), terminal landmark `MusicEvent(0,0,SECTION_TICKS-1,SECTION_TICKS)`
per section per voice, chronological sort enforced by the engine. No raw-mido
authoring (mido used only for read/verify in render_audio.py), no sys.path hack
beyond the sanctioned instrument-registry path.

## 8. Files

| Path | Size | Description |
|---|---|---|
| MIDI/214-blues-antcolony.mid | 6,893 B | Phase 2 rules composition (DAW-editable) |
| MIDI/214-blues-antcolony-phase1.mid | 1,751 B | Phase 1 raw ACO draft |
| Audio/214-blues-antcolony.ogg | 1,246,508 B | Phase 2 Opus render |
| Audio/214-blues-antcolony-phase1.ogg | 1,279,964 B | Phase 1 Opus render |
| Audio/*.wav | ~10.5 MB each | Raw PCM (pre-compression) |
| Analysis/grid_visualization.txt | 3,688 B | High-contrast timeline |
| Analysis/summary.json | 3,276 B | Full audit numbers |
| compose.py / render_audio.py | 19,157 / 6,844 B | Generators |
| provenance.json per artifact | — | write_provenance sidecars |

## 9. Fixes / notes

1. **Style re-roll**: first random draw (seed 20260930) returned IndianClassical,
   identical to last night's 212. A single documented re-roll (seed 20260941)
   landed on **Blues** — remaining honest to "random style" while avoiding a
   two-night same-genre streak (the 212 report's own convention).
2. **Narrow raw ACO range [69, 76]**: the smoothness heuristic (β=2.5) + register
   pull converged the colony onto a tight plateau. This is a *legitimate* ACO
   convergence (not a bug) and it is the raw draft's character; Phase 2's
   chord-tone snap then maps that plateau across the changing I/IV/V chord sets,
   so the harmonica still articulates the blues changes. A future seed changing
   β down (or adding a small per-slot pitch-range envelope) would widen the
   contour.
3. **Blues harmony honesty**: strict dominant-7th chords (E7/A7/B7) would place
   the major 3rd (G♯/C♯/D♯) *outside* the blues scale, breaking the 0-out-of-scale
   gate. Using "blues sus-dominant" voicings (root/5th/b3-or-4th/b7) keeps the
   whole texture inside the blues scale — documented, musically standard for a
   modal blues treatment.

## 10. What to listen for

- **The walking bass** (root-top-root-mid quarter-notes) never stops — it is the
  harmonic floor the horns float on.
- **The 12-bar changes**: I → IV at bar 5, the V-IV-I-V turnaround at bar 9–12 —
  the harmonica's snapped notes re-voice onto each chord's tones.
- **The backbeat** (snare on 2 & 4, kick on 1 & 3) with the swing accent on the
  off-beat hi-hats — the straight "shuffle-lite" feel.
- **Call-response**: the trumpet answers on the off-beat 8ths, denser in the solo
  chorus (sections 3–5).
- **The turnaround** (final 4 bars): the open hi-hat on "and of 4" + the V pedal
  that pulls home to the I7.