# REPORT — 100-balkan-christoffel

**Project:** 100-balkan-christoffel  
**Style:** Balkan (Bulgarian Kopanitsa Dance in 11/8)  
**Method:** 069 Christoffel Word Combinatorial Composition (CWCC)  
**Layer:** `concrete`  
**Date:** 2026-09-21 (Nightly Autonomous Composition Job)  
**Seed:** 20260921  
**Key:** D Dorian / Folk Minor · **BPM:** 160 · **Meter:** 11/8 (2+2+3+2+2 subdivision) · **TPB:** 480  
**Ticks per Bar:** 11 sixteenths × 120 ticks = 1320 ticks  
**Form:** 6 sections × 4 bars = 24 bars (Intro | Tema_A | Tema_B | Razvivka | Tema_A_Var | Zavurshek) = 31,680 ticks (~34.75 s)  
**Project Dir:** `/opt/data/repos/musicom/projects/Styles/Balkan/100-balkan-christoffel`  

---

## 1. Headline Results & Compliance Summary

| Verification Gate | Required Standard | Result | Status |
|---|---|---|---|
| `validate()` Phase 1 (Raw) | `True` (Zero-drift) | `True` (31,680 ticks) | **PASS** |
| `validate()` Phase 2 (Rules) | `True` (Zero-drift) | `True` (31,680 ticks) | **PASS** |
| 16th-Grid Audit (Phase 2) | 0 off-grid onsets | **0 / 1032 notes** (100% on 120-tick grid) | **PASS** |
| Harmony Scale Audit (Phase 2) | 0 out-of-scale notes | **0 / 1032 notes** | **PASS** |
| Harmony Chord Audit (Phase 2) | 0 out-of-chord notes | **0 / 1032 notes** | **PASS** |
| Raw Timing Fingerprint (Phase 1) | Unquantized raw drift | 134 off-grid / 141 notes | **PASS** |
| Silence Profile (Phase 2) | Mid-track gaps < 30% | 24.01% (natural release tail at end) | **PASS** |
| Silence Profile (Phase 1) | Mid-track gaps < 30% | 7.51% | **PASS** |
| FFT Tonal Detection (50–1000 Hz) | Sustained tonal peaks | Phase 2: 66/69 frames (95.65%); Phase 1: 53/53 (100%) | **PASS** |
| Preflight Engine Compliance | Exit 0 (no raw mido authoring) | `preflight_check.py` clean | **PASS** |

---

## 2. Methodology & Layer Details

- **Layer Cadence:** Concrete layer.
- **Method:** 069 Christoffel Word Combinatorial Composition (CWCC).
- **Theoretical Basis:**
  - Lower Christoffel words $C(p, q)$ over $\{a, b\}$ with $\gcd(p, q) = 1$ and $n = p + q$:
    $$w_k = b \iff \lfloor(k+1)q/n\rfloor > \lfloor kq/n\rfloor$$
  - Master Word $C(5, 2) = \text{`aaabaab'}$ defines the balanced step-pattern whose cyclic conjugates generate the diatonic modes (Carey & Clampitt well-formed scales, Clough-Douthett maximal evenness).
  - Sturmian morphisms $G: (a \mapsto a, b \mapsto ab)$ and $D: (a \mapsto ba, b \mapsto b)$ expand motifs across recursive hierarchical levels.
  - Kopanitsa 11/8 Asymmetric Rhythmic Christoffel Binding: 11 pulses structured as $2+2+3+2+2$ (short, short, long, short, short). In 16th resolution ($16\text{th} = 120$ ticks), beat onsets sit at ticks $0, 240, 480, 840, 1080$. Every melodic and percussive hit aligns strictly to the 120-tick grid.

---

## 3. Harmonic Framework & Form

Key: **D Dorian** (pitch classes: D=2, E=4, F=5, G=7, A=9, B=11, C=0) with Folk Bb borrowing in Zavurshek.
Form: 6 sections × 4 bars = 24 bars.

- **Intro (bars 0–3):** `Dm - Dm - C - Dm`
- **Tema A (bars 4–7):** `Dm - C - G - Dm`
- **Tema B (bars 8–11):** `F - C - Dm - Am`
- **Razvivka (bars 12–15):** `G - F - C - Dm`
- **Tema A Var (bars 16–19):** `Dm - C - G - Dm`
- **Zavurshek (bars 20–23):** `Bb - C - Dm - Dm`

Every bar's pitches are mapped strictly to the triad chord tones, guaranteeing 0 harmonic violations.

---

## 4. Instrumentation & Roles (Instrument Registry)

All voices configured from `/opt/data/repos/musicom/projects/Instruments/instrument_registry.py`:
1. **Lead (Clarinet, GM 71, ch 0):** Virtuosic 16th Kopanitsa runs generated from $C(5, 2)$ Christoffel word steps; 240 notes.
2. **Fiddle / Countermelody (Violin, GM 40, ch 1):** Sustained 5-beat asymmetric contour using rotated Christoffel words; 120 notes.
3. **Tambura / Comping (Acoustic Guitar, GM 25, ch 2):** Offbeat rhythmic stabs on beats 2, 3, and 5; 216 notes.
4. **Bass (Double Bass, GM 43, ch 3):** Root-fifth dance pattern locking into the 11/8 dance groove; 96 notes.
5. **Percussion (Drum Kit / Tupan, ch 9):** Heavy kick on beats 1 and 3 (the long beat!), crisp snare backbeats on beats 2, 4, and 5, riding 16th hi-hat; 360 notes.

---

## 5. Detailed Audit Logs

### Phase 2 Detailed Voice Breakdown
```
Track 1 (Clarinet, ch0, prg71): 240 notes | off16=0 | oos=0 | ooc=0 | tick_len=31680
Track 2 (Fiddle,   ch1, prg40): 120 notes | off16=0 | oos=0 | ooc=0 | tick_len=31680
Track 3 (Tambura,  ch2, prg25): 216 notes | off16=0 | oos=0 | ooc=0 | tick_len=31680
Track 4 (Bass,     ch3, prg43):  96 notes | off16=0 | oos=0 | ooc=0 | tick_len=31680
Track 5 (Drums,    ch9, prg0):  360 notes | off16=0 | oos=0 | ooc=0 | tick_len=31680
Total: 1032 notes | 0 off-grid | 0 out-of-scale | 0 out-of-chord
```

### Phase 1 Raw Draft (Clarinet)
```
Track 1 (Raw_Clarinet, ch0): 141 notes | off-grid=134/141 | tick_len=31680
```

---

## 6. Audio Renders & RMS Profile

- **SoundFont:** `FluidR3_GM.sf2` (141 MB) auto-resolved via `discover_soundfont()`.
- **Phase 2 Audio:**
  - WAV: `Audio/100-balkan-christoffel.wav` (6,130,732 bytes)
  - OGG: `Audio/100-balkan-christoffel.ogg` (586,404 bytes)
  - Duration: 34.75 s
  - Silence ratio: 24.01% (clean sustained decay, no mid-track dropouts)
  - FFT tonal detection: 66/69 frames (95.65% tonal content in 50–1000 Hz)
- **Phase 1 Audio:**
  - WAV: `Audio/100-balkan-christoffel-phase1.wav` (4,719,404 bytes)
  - OGG: `Audio/100-balkan-christoffel-phase1.ogg` (606,511 bytes)
  - Duration: 26.75 s

---

## 7. Artifact Manifest

- `compose.py` — two-phase composition script (engine-only, preflight clean)
- `audit.py` — verification script for grid & harmony audits
- `render_audio.py` — FluidSynth rendering & audio stats pipeline
- `gen_grid.py` — grid visualizer
- `MIDI/100-balkan-christoffel.mid` (8,412 bytes) + provenance
- `MIDI/100-balkan-christoffel-phase1.mid` (1,342 bytes) + provenance
- `Audio/100-balkan-christoffel.wav` (6.1 MB)
- `Audio/100-balkan-christoffel.ogg` (586 KB)
- `Audio/100-balkan-christoffel-phase1.wav` (4.7 MB)
- `Audio/100-balkan-christoffel-phase1.ogg` (606 KB)
- `Analysis/audit.json`
- `Analysis/render_stats.json`
- `Analysis/grid_visualization.txt`
- `README.md`
- `REPORT.md`
