# REPORT — 210-rbncc-west-african-polyrhythm

**Project:** 210-rbncc-west-african-polyrhythm
**Style:** West African Polyrhythms (Ewe/Ghana timeline ensemble — gankogui double bell, kalimba/kora lead, balafon counter, dunun bass, djembe/shaker drums)
**Method:** 082 Random Boolean Network Criticality Composition (RBNCC)
**Layer:** `concrete`
**Date:** 2026-09-28 (Nightly Autonomous Composition Job, ID 1fc3fd65d359)
**Seed:** 20260928
**Key:** G major = G A B C D E F# = pitch classes {7, 9, 11, 0, 2, 4, 6}
**BPM:** 112 · 4/4 · 480 TPB (bar = 1920, 16th = 120, 8th = 240)

---

## 1. Selection

| Field | Value |
|---|---|
| Style | **West African Polyrhythms** — random pick from `/opt/data/repos/musicom/projects/Styles/` genre folders (excl. _Comparison/_Data_Patterns/Research/Poetry/Production/Percussion/Other + numbered/`Celtic `), seed 20260928. |
| Method | **082 Random Boolean Network Criticality Composition (RBNCC)** — `concrete` layer, Nature-Led. Not used in the last 7 days. |
| Layer cadence | `concrete` (6-of-7 cadence). Last abstract composition job was 105 (2026-09-24, method 095 Contour Theory); abstract not yet due. |
| Recent-method exclusion | Excluded methods used in the last 7 days: {001, 010, 016, 019, 025, 026, 040, 048, 069, 075}. Random pick from the remaining 83 concrete methods landed on **082**. |

## 2. Method essence (082 RBNCC — Kauffman random Boolean network at criticality)

A synchronous random Boolean network — N=16 nodes, each with K=2 distinct
inputs and a random Boolean truth table (each output bit = 1 with bias p=0.5).
With p=0.5, the critical connectivity is Kc = 1/[2p(1-p)] = 2, so this network
sits exactly at the **edge of chaos**. The deterministic state trajectory falls
into an **attractor cycle**; the pre-attractor **transient** is
connective/tension material; **frozen** nodes (bits that never flip across the
cycle) form the harmonic scaffold; **unstable** nodes are melodic figuration.

| RBN parameter | Value |
|---|---|
| N (nodes) | 16 |
| K (inputs/node) | 2 (critical: Kc = 1/[2·0.5·0.5] = 2) |
| Output bias p | 0.5 |
| Wiring seed / init seed | 20260928 / 20260935 (init = SEED+7) |
| Transient length | **1** state |
| Attractor cycle length | **12** states |
| Frozen nodes | **[5]** (1 frozen node = harmonic anchor; 15 unstable = figuration) |

**Why 12 matters musically:** a 12-state cycle cycled against the 16-sixteenth
bar is a **3:4 cross-rhythm**. The lead pitch contour (and balafon counter)
repeat every 12 sixteenths = 3 beats, while the bar is 4 beats — so the melodic
phase drifts one beat per cycle against the duple groove. This is the signature
West African polyrhythm, produced *by the method*, not imposed by hand.

Bit-field decode (16-bit state, bit 0 = LSB):

| bits | field | musical use |
|---|---|---|
| 0..3 | lead_deg (0-15) | lead pitch index; `>= 12` = rest (25% rests) |
| 4..5 | lead_art | articulation tag (method fidelity, not gated) |
| 6..8 | lead_vel (0-7) | velocity = 56 + 7·vel (56..105) |
| 9..11 | bal_deg (0-7) | balafon counter pitch index |
| 12..13 | bal_gate (0-3) | balafon fire gate (`==1` → fire, 25%) |
| 14..15 | shake (0-3) | shaker density (`==3` → extra RBN shaker hit) |

## 3. Form, Key, Meter

| Field | Value |
|---|---|
| Form | Intro → Verse → Chorus → Verse2 → Chorus2 → Break → Chorus3 → Outro (8 sections × 4 bars = **32 bars**) |
| Key | **G major** |
| Meter | 4/4, 112 BPM |
| Grid | 480 TPB → 16th = 120, 8th = 240, bar = 1920, section = 7680, total = 61440 ticks (~68.6 s + tail) |
| Progression | **I–IV–V–I** (Verse: G–C–D–G) · **I–vi–IV–V** (Chorus: G–Em–C–D) · **vi–IV–I–V** (Break: Em–C–G–D, darker turn) · Intro/Outro pedal G |

## 4. Voices & Instruments (registry source of truth)

| Voice | Instrument | GM Program | Channel | Role |
|---|---|---|---|---|
| Gankogui | Marimba | 12 | 0 | Two-pitch timeline bell (low = chord root, high = chord 5th), 5-stroke 3-2 clave |
| LeadKora | Kalimba | 108 | 1 | RBN attractor melody (12-step cycle → 3:4 polyrhythm), chord-tone snapped |
| BassDunun | Double Bass | 43 | 2 | Root pulse, 3+3+2 syncopation (16th steps 0/6/10) |
| Balafon | Xylophone | 13 | 3 | RBN interlocking counter (bal_gate==1), chord-tone snapped |
| Drums | Drum Kit | 0 (ch9) | 9 | Dunun kick (36), djembe slap (38), shaker (42, 8ths + RBN) |

All instrument programs resolved via `instrument_registry.py` (source of truth),
not the 10-entry `MidiInstrument` enum.

## 5. Two-Phase Architecture

### Phase 1 — Raw RBN Draft (`-phase1.mid`)
- Single voice (Raw_Lead, Kalimba).
- **Onsets** unquantized: 16th slot + micro-jitter (±18 ticks) OFF the 120/240 grid.
- **Pitch** unquantized: raw chromatic (`48 + lead_deg*3`), NOT snapped to key/chord.
- No harmony, no chord-tone quantization, no texture. `validate()` PASSED.

### Phase 2 — Musicom Rules Post-Processing (`.mid`)
- **Same RBN** re-run with the same seed → identical raw material, then:
  1. every onset snapped to the **16th grid** (120 ticks),
  2. every pitch snapped to its **bar's chord tones** (G major).
- Full 5-voice polyrhythmic texture added. `validate()` PASSED.

## 6. Verification (real numbers)

### Grid audit (every voice vs 16th/8th grid) — **0 OFF-GRID**

| Track | Onsets | off_16th | off_8th | Verdict |
|---|---|---|---|---|
| Gankogui | 176 | **0** | 32 | 0 off-grid (32 are legit 16th bell syncopation) |
| LeadKora | 384 | **0** | 171 | 0 off-grid (171 legit 16th syncopation) |
| BassDunun | 96 | **0** | 0 | 0 off-grid |
| Balafon | 128 | **0** | 43 | 0 off-grid (43 legit 16th syncopation) |
| Drums (ch9) | 544 | **0** | 128 | 0 off-grid |

All **1328** onsets snap to the 16th grid. The off-8th counts are deliberate
16th-note syncopations (bell/clave off-beats, shaker 16ths), on-grid at 16th
resolution.

### Harmony audit (pitched voices vs key + bar chord) — **0 OUT-OF-KEY**

| Track | Notes | out_of_scale | out_of_chord | Verdict |
|---|---|---|---|---|
| Gankogui | 176 | **0** | **0** | pass |
| LeadKora | 384 | **0** | **0** | pass |
| BassDunun | 96 | **0** | **0** | pass |
| Balafon | 128 | **0** | **0** | pass |

All **784** pitched notes are chord tones of their bar (hence in G major).

### Audio profile (FluidSynth + FluidR3_GM.sf2 → WAV → Opus OGG)

| Phase | Duration | Silence | Peak | Tonal ratio | Verdict |
|---|---|---|---|---|---|
| Phase 2 | 74.53 s | 8.35% | 0.8466 | 97.99% | healthy (silence = tail + sparse intro/outro) |
| Phase 1 | 74.50 s | 9.23% | 0.434 | 98.65% | raw dense chromatic stream (expected) |

- Phase 2: 8.35% silence is the FluidSynth reverb/release tail + the sparse
  Intro/Outro pedal bars. No mid-track dead zones.
- Phase 1: dense single-voice chromatic stream (384 notes ≈ 75% density), so
  silence is low; the contrast vs phase 2 is *harmonic* (chromatic vs
  chord-locked), not density.
- FFT tonal content 50–1000 Hz ≥ 98% in both phases → **not noise**.

## 7. Zero-drift status

`UnitMatrixComposer.validate()` PASSED for **both** phases. All tracks equal
length (61440 ticks), terminal landmark `MusicEvent(0,0,SECTION_TICKS-1,SECTION_TICKS)`
per section, chronological sort enforced by the engine. Preflight compliance
check: **COMPLIANT** (exit 0 — no raw-mido authoring, no sys.path hack).

## 8. Files

| Path | Size | Description |
|---|---|---|
| MIDI/210-rbncc-west-african-polyrhythm.mid | 11,118 B | Phase 2 rules composition (DAW-editable) |
| MIDI/210-rbncc-west-african-polyrhythm-phase1.mid | 3,044 B | Phase 1 raw RBN draft |
| Audio/210-rbncc-west-african-polyrhythm.ogg | 1,407,772 B | Phase 2 Opus render |
| Audio/210-rbncc-west-african-polyrhythm-phase1.ogg | 1,533,193 B | Phase 1 Opus render |
| Audio/*.wav | ~13 MB each | Raw PCM (pre-compression) |
| Analysis/grid_visualization.txt | 4,679 B | High-contrast timeline |
| Analysis/summary.json | 3,713 B | Full audit numbers |
| compose.py / render_audio.py | 20,236 / 7,578 B | Generators |
| provenance.json per artifact | — | write_provenance sidecars |

## 9. Fixes applied

None required — first-pass validation, grid audit, and harmony audit all green.
No rhythm-grid drift (078-class bug avoided by construction: all phase-2 onsets
computed as `bar_start + step*GRID16`, never `SECTION_TICKS // n_events`).
Diatonic pitch routing uses chord-tone snapping against the explicit
`CHORD_PCS` dict (no custom `% 7` wrappers).

## 10. What to listen for

- **The 3:4 polyrhythm**: the kalimba lead (12-step RBN cycle) drifts against
  the 4-beat bar — count 4 on the bell/bass and feel the lead "phase" one beat
  every cycle. This is the method's critical-cycle gift.
- **Gankogui bell**: the stable 3-2 clave timeline (two pitches) is the
  "frozen-node harmonic scaffold" made audible — it never changes while the
  lead figuration (unstable nodes) swirls around it.
- **Interlocking hocket**: lead (75% density) and balafon (25%) interlock on the
  16th grid — the classic West African call-and-response fill.
- **Break turn**: the progression dips to Em–C–G–D (vi–IV–I–V) before the final
  chorus for a darker lift.
- Tension/release lives in the V→I cadence (D→G) landing at each section's bar 4.
