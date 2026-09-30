# REPORT — 212-indian-boids-yaman

**Project:** 212-indian-boids-yaman
**Style:** IndianClassical (Hindustani) — Raga Yaman (Kalyan thaat), alap → gat → jhala → alap form
**Method:** 031 Swarm Intelligence Flocking (Boids)
**Layer:** `concrete`
**Date:** 2026-09-29 (Nightly Autonomous Composition Job, ID 1fc3fd65d359)
**Seed:** 20260929
**Key:** Raga Yaman on C (Sa = C) = C D E F♯ G A B = pitch classes {0, 2, 4, 6, 7, 9, 11}
**BPM:** 90 · 4/4 · 480 TPB (bar = 1920, 16th = 120, 8th = 240)

---

## 1. Selection

| Field | Value |
|---|---|
| Style | **IndianClassical** — random pick from `/opt/data/repos/musicom/projects/Styles/` genre folders (excl. _Comparison/_Data_Patterns/Research/Poetry/Production/Percussion/Other + numbered/`Celtic `), seed 20260929 (first roll). |
| Method | **031 Swarm Intelligence Flocking (Boids)** — `concrete` layer, Nature-Led. Not used in the last 7 days. |
| Layer cadence | `concrete` (6-of-7 cadence). Last abstract composition job was 105 (2026-09-24, method 095 Contour Theory); abstract not yet due. |
| Recent-method exclusion | Excluded methods used in the last 7 days: {001, 010, 016, 018, 025, 026, 040, 048, 069, 075, 082, 095}. Random pick from the remaining concrete methods landed on **031**. |

## 2. Method essence (031 Boids — Reynolds flocking + tonal gravity)

N = 8 melodic "boids" move in **1D pitch space** (position = semitone, velocity =
melodic direction). Each step every boid feels three classic Reynolds forces plus
two raga-specific terms:

| Force | Weight | Musical meaning |
|---|---|---|
| **Separation** | 0.20 (radius 2 st) | avoid pitch-crowding → voice independence / ornament |
| **Alignment** | 0.05 | match neighbours' velocity → parallel melodic motion |
| **Cohesion** | 0.05 | steer to flock centroid → melodic coherence |
| **Leader attraction** | 0.25 | follow the virtual leader tracing the raga contour |
| **Sa gravity** | 0.02 | weak pull to the tonic (the raga's home) |

Velocity damping 0.78, max speed ±6 semitones/step.

The **virtual leader** walks the Yaman aroha → avaroha one scale step per quarter
note (`RAGA_PATH = [S R G M̄ P D N Ṡ Ṡ N D P M̄ G R S]`, dwell 4 steps = 1 quarter,
16 notes = 4 bars per cycle), with an octave drift: cycles 2–5 (gat/jhala) climb
an octave, cycles 6–7 return. The flock's emergent **centroid** is the melody;
its **spread** (std) drives velocity; the spread collapsing toward Sa is the
raga's "ma" (breath).

**Why Yaman + Boids pair well:** Yaman's serene, expansive character maps to a
slow flock gliding up the aroha; the separation force produces the micro-
fluctuation (meend-like) that a hand-drawn contour would lack. This seed
(20260929) yields a centroid that climbs C4 → C6 and returns, tracing all seven
Yaman notes — including the signature **tivra Ma (F♯)**, which separation keeps
audible as the flock momentarily spreads.

| Boid parameter | Value |
|---|---|
| N (boids) | 8 |
| Space | 1D pitch (semitones), time advances 1 step/16th |
| Leader path | Yaman aroha+avaroha, dwell 4 steps/note |
| Centroid range | **[56.2, 82.8]** semitones (26.6 st span, octave drift) |
| Spread mean | 1.11 st |
| Speed mean | 0.459 st/step |

## 3. Form, Key, Meter

| Field | Value |
|---|---|
| Form | Alap → Jod → Gat1 → Gat2 → Jhala → Gat1b → Alap2 → Outro (8 sections × 4 bars = **32 bars**) |
| Key | **Raga Yaman on C** (Sa = C, tivra Ma = F♯) |
| Meter | 4/4 (teental tala: 16 matra = 16 sixteenths), 90 BPM |
| Grid | 480 TPB → 16th = 120, 8th = 240, bar = 1920, section = 7680, total = 61440 ticks (~85.3 s + tail) |
| Progression | Monophonic raga — the Sa+Pa tanpura drone is the constant harmony; the melody traces the aroha/avaroha. Sparse sections (Alap/Alap2/Outro) restrict to Sa+Pa; melodic sections (Jod→Gat1b) open to the full Yaman scale. |

## 4. Voices & Instruments (registry source of truth)

| Voice | Instrument | GM Program | Channel | Role |
|---|---|---|---|---|
| Drone | Church Organ | 19 | 0 | Tanpura pedal: Sa octave (C2, C3) + Pa (G3), re-articulated per bar |
| LeadSitar | Sitar | 104 | 1 | Boid-centroid melody (aroha/avaroha), raga-harmonic snap, 16th-grid |
| Bansuri | Flute | 74 | 2 | Boid fifth-above interlock (off 16ths) in gat/jhala sections |
| Tabla | Drum Kit | 0 (ch9) | 9 | Teental theka: bayan (36) anchors + dayan (38) + tin (42) |

All instrument programs resolved via `instrument_registry.py` (source of truth),
not the 10-entry `MidiInstrument` enum.

## 5. Two-Phase Architecture

### Phase 1 — Raw Boid Draft (`-phase1.mid`)
- Single voice (Raw_Lead, Sitar).
- **Onsets** unquantized: 16th slot + micro-jitter (±18 ticks) OFF the 120/240 grid.
- **Pitch** unquantized: raw boid centroid rounded to nearest chromatic semitone, NOT snapped to raga/chord.
- No harmony, no chord-tone quantization, no texture. `validate()` PASSED.

### Phase 2 — Musicom Rules Post-Processing (`.mid`)
- **Same flock** re-run with the same seed → identical raw material, then:
  1. every onset snapped to the **16th grid** (120 ticks),
  2. every pitch snapped to its section's **raga-harmonic region** (full Yaman in melodic sections; Sa+Pa in Alap/Outro).
- Full 4-voice Hindustani texture added. `validate()` PASSED.

## 6. Verification (real numbers)

### Grid audit (every voice vs 16th/8th grid) — **0 OFF-GRID**

| Track | Onsets | off_16th | off_8th | Verdict |
|---|---|---|---|---|
| Drone | 96 | **0** | 0 | 0 off-grid |
| LeadSitar | 304 | **0** | 96 | 0 off-grid (96 legit 16th syncopation) |
| Bansuri | 160 | **0** | 160 | 0 off-grid (all off-beat 16ths) |
| Tabla (ch9) | 400 | **0** | 180 | 0 off-grid |

All **960** onsets snap to the 16th grid. Off-8th counts are deliberate 16th
syncopation (bansuri off-beats, tabla dayan strokes).

### Harmony audit (pitched voices vs raga + section region) — **0 OUT-OF-KEY**

| Track | Notes | out_of_scale | out_of_chord | Verdict |
|---|---|---|---|---|
| Drone | 96 | **0** | **0** | pass (Sa+Pa) |
| LeadSitar | 304 | **0** | **0** | pass (full Yaman: pcs {0,2,4,6,7,9,11}) |
| Bansuri | 160 | **0** | **0** | pass (full Yaman) |

All **560** pitched notes are in Raga Yaman (hence in their section region).
The lead and bansuri both traverse all seven pitch classes, including the
**tivra Ma (F♯, pc 6)** that defines Yaman.

### Audio profile (FluidSynth + FluidR3_GM.sf2 → WAV → Opus OGG)

| Phase | Duration | Silence | Peak | Tonal ratio | Verdict |
|---|---|---|---|---|---|
| Phase 2 | 92.52 s | 7.55% | 0.7872 | 98.38% | healthy (silence = tail + sparse alap/outro) |
| Phase 1 | 93.41 s | 11.34% | 0.1366 | 98.92% | raw sparse chromatic stream (expected) |

- Phase 2: 7.55% silence is the FluidSynth reverb/release tail + the sparse
  Alap/Outro drone sections. No mid-track dead zones.
- Phase 1: 11.34% silence, peak 0.137 — the single raw sitar voice decays; the
  contrast vs phase 2 is *texture* (1 voice vs 4) and *harmonicity* (chromatic
  vs raga-locked), not density.
- FFT tonal content 50–1000 Hz ≥ 98% in both phases → **not noise**.

## 7. Zero-drift status

`UnitMatrixComposer.validate()` PASSED for **both** phases. All tracks equal
length (61440 ticks), terminal landmark `MusicEvent(0,0,SECTION_TICKS-1,SECTION_TICKS)`
per section, chronological sort enforced by the engine. Preflight compliance
check: **COMPLIANT** (exit 0 — no raw-mido authoring, no sys.path hack beyond the
sanctioned instrument-registry path).

## 8. Files

| Path | Size | Description |
|---|---|---|
| MIDI/212-indian-boids-yaman.mid | 7,847 B | Phase 2 rules composition (DAW-editable) |
| MIDI/212-indian-boids-yaman-phase1.mid | 3,889 B | Phase 1 raw boid draft |
| Audio/212-indian-boids-yaman.ogg | 1,822,532 B | Phase 2 Opus render |
| Audio/212-indian-boids-yaman-phase1.ogg | 1,831,729 B | Phase 1 Opus render |
| Audio/*.wav | ~16 MB each | Raw PCM (pre-compression) |
| Analysis/grid_visualization.txt | 3,860 B | High-contrast timeline |
| Analysis/summary.json | 4,077 B | Full audit numbers |
| compose.py / render_audio.py | 19,011 / 7,264 B | Generators |
| provenance.json per artifact | — | write_provenance sidecars |

## 9. Fixes applied

Two iterations were needed:

1. **First pass** (monotonic aroha→climax→descent envelope + per-section chord
   subsets) produced a lead confined to 5 notes {C, D, G, A, B} — the monotonic
   contour never dwelled on Ga (E) or the signature tivra Ma (F♯), and the
   per-section chord subsets excluded them during the ascent. **Fix:** replaced
   the envelope with a note-dwell aroha/avaroha walk (leader steps one Yaman note
   per quarter note, octave drift for the gat/jhala), strengthened leader force
   (0.12 → 0.25) and lowered damping (0.85 → 0.78) so the flock tracks closely.
2. **Harmony model correction:** for a monophonic raga the Sa+Pa drone is
   consonant with the *entire* scale, so the melodic sections' "chord" = full
   Yaman (out-of-chord audit reduces to out-of-scale there, which is musically
   correct); only the sparse Alap/Outro sections restrict to {Sa, Pa}. This
   removed the false "out-of-chord" tension while keeping the audit meaningful.

No rhythm-grid drift (078-class bug avoided by construction: all phase-2 onsets
computed as `bar_start + step*GRID16`, never `SECTION_TICKS // n_events`).
Diatonic pitch routing uses nearest-chord-tone snapping against explicit pitch-class
sets (no custom `% 7` wrappers).

## 10. What to listen for

- **The tanpura drone** (organ Sa+Pa) never stops — it is the harmonic floor the
  whole raga floats on. Everything else is measured against it.
- **The aroha/avaroha**: the sitar lead climbs S→Ṡ in the alap/jod, dwells an
  octave up through the gat, peaks in the jhala (fast 16th runs + double-time
  tabla), then descends back to Sa in the alap2/outro.
- **The tivra Ma (F♯)**: Yaman's signature note — listen for the raised 4th that
  separates Yaman from the plain major scale, especially in Gat2/Jhala.
- **The bansuri interlock**: flute answers the sitar on the off-beats, a fifth
  above — the boid flock's separation made audible as a second voice.
- **Teental**: count 16 (4+4+4+4); the bayan bass lands on matras 1-5-9-13.
- **Tension/release**: the climax is the jhala (register + density peak); the
  release is the slow return to Sa, ending on the bare drone.
