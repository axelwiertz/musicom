# REPORT — 098-funk-som

**Project:** 098-funk-som  
**Style:** Funk  
**Method:** 075 Self-Organizing Map Composition (SOM-C)  
**Layer:** `concrete`  
**Date:** 2026-09-19 (Nightly Autonomous Composition Job)  
**Seed:** 20260919  
**Key:** F minor (Aeolian / Pentatonic) · **BPM:** 104 · 4/4 · 480 TPB (Bar = 1920 ticks, 16th = 120 ticks, 8th = 240 ticks)  
**Form:** 6 sections × 4 bars = 24 bars (Intro | Verse | Chorus | Bridge | Chorus2 | Outro) = 46,080 ticks (~58.0 s)  
**Project Dir:** `/opt/data/repos/musicom/projects/Styles/Funk/098-funk-som`  

---

## 1. Headline Results & Compliance Summary

| Verification Gate | Required Standard | Result | Status |
|---|---|---|---|
| `validate()` Phase 1 (Raw) | `True` (Zero-drift) | `True` (46,080 ticks) | **PASS** |
| `validate()` Phase 2 (Rules) | `True` (Zero-drift) | `True` (46,080 ticks) | **PASS** |
| 16th-Grid Audit (Phase 2) | 0 off-grid onsets | **0 / 1128 notes** | **PASS** |
| Harmony Scale Audit (Phase 2) | 0 out-of-scale notes | **0 / 1128 notes** | **PASS** |
| Harmony Chord Audit (Phase 2) | 0 out-of-chord notes | **0 / 1128 notes** | **PASS** |
| Raw Timing Fingerprint (Phase 1) | Unquantized raw drift | 177 off-grid / 184 notes | **PASS** |
| Silence Profile (Phase 2) | Mid-track gaps < 30% | 5.24% (tail only, sec 56) | **PASS** |
| Silence Profile (Phase 1) | Mid-track gaps < 30% | 7.24% (tail only, sec 56) | **PASS** |
| FFT Tonal Detection (50–1000 Hz) | Sustained tonal peaks | Phase 2: 113/115; Phase 1: 112/114 | **PASS** |
| Preflight Engine Compliance | Exit 0 (no raw mido authoring) | `preflight_check.py` clean | **PASS** |

---

## 2. Methodology & Layer Details

- **Layer Cadence:** Concrete layer. (Recent cadence: 091-096 concrete, 097 abstract, tonight continues concrete progression with Method 075).
- **Paradigm:** Stochastic / Learned Topology.
- **SOM Structure:** 4×4 toroidal lattice of 3-dimensional prototypes (`pitch_norm`, `duration_norm`, `velocity_norm`).
- **Corpus Training:** Trained for 100 epochs with exponential learning rate and Gaussian neighborhood decay on 8 canonical funk atoms (syncopated slap, 16th pop, horn punch, blue note stab, etc.).
- **Trajectory Walking:** 2D Markov walk over the 16 toroidal nodes guided by transition similarity kernel $P(j \to j') \propto \exp(-\beta \|w_j - w_{j'}\|^2 - \gamma d_T(j', R_s))$ towards section waypoints.

---

## 3. Harmonic Framework & Form

**Progression (24 bars, 1 bar per root):**
- **Intro (bars 0–3):** `i - i - iv - v` (`Fm - Fm - Bbm - Cm`)
- **Verse (bars 4–7):** `i - VI - iv - v` (`Fm - Db - Bbm - Cm`)
- **Chorus (bars 8–11):** `i - III - VII - iv` (`Fm - Ab - Eb - Bbm`)
- **Bridge (bars 12–15):** `VI - VII - i - v` (`Db - Eb - Fm - Cm`)
- **Chorus2 (bars 16–19):** `i - III - VII - iv` (`Fm - Ab - Eb - Bbm`)
- **Outro (bars 20–23):** `i - VI - v - i` (`Fm - Db - Cm - Fm`)

---

## 4. Instrumentation & Roles (Instrument Registry)

All voices configured using `/opt/data/repos/musicom/projects/Instruments/instrument_registry.py`:
1. **Lead (Trumpet, GM 56, ch 0):** Melodic line from quantized SOM walk; 184 notes.
2. **Sax (Tenor Saxophone, GM 65, ch 1):** Punchy offbeat counterlines on beats 2.5 and 4.5; 32 notes.
3. **Piano (Acoustic Grand Piano, GM 1, ch 2):** Syncopated funk comping (beat 1, "and" of 2, beat 4); 216 notes.
4. **Bass (Double Bass, GM 43, ch 3):** Slap/pop funk groove with root octaves and syncopated pushes; 144 notes.
5. **Drums (Drum Kit, ch 9):** Tight 16th funk hi-hats, ghost-snare patterns, and syncopated kick groove; 552 notes.

---

## 5. Detailed Audit Logs

### Phase 2 Detailed Voice Breakdown
```
Track 1 (Lead, ch0, prg56):  184 notes | off16=0 | oos=0 | ooc=0
Track 2 (Sax, ch1, prg65):    32 notes | off16=0 | oos=0 | ooc=0
Track 3 (Piano, ch2, prg1):  216 notes | off16=0 | oos=0 | ooc=0
Track 4 (Bass, ch3, prg43):  144 notes | off16=0 | oos=0 | ooc=0
Track 5 (Drums, ch9, prg0):  552 notes | off16=0 | oos=0 | ooc=0
-----------------------------------------------------------------
TOTAL:                      1128 notes | off16=0 | oos=0 | ooc=0
```

### Phase 1 Raw Draft Breakdown
```
Track 1 (LeadRaw, ch0, prg56): 184 notes | off16=177 (unquantized continuous timing)
```

---

## 6. Audio Rendering & Spectral Metrics

Generated via `workflows.musicom_workflow.produce(method="SP-001")`:
- **Phase 2 Full Mix:**
  - WAV: `Audio/098-funk-som.wav` (10,223,404 bytes, 57.96s)
  - OGG: `Audio/098-funk-som.ogg` (432,328 bytes)
  - Peak: `0.9405`
  - RMS Mean: `0.10505`
  - Silence Ratio: `5.24%` (tail padding only)
  - Tonal Windows: `113/115`
- **Phase 1 Raw Draft:**
  - WAV: `Audio/098-funk-som-phase1.wav` (10,123,052 bytes, 57.39s)
  - OGG: `Audio/098-funk-som-phase1.ogg` (514,572 bytes)
  - Peak: `0.4696`
  - RMS Mean: `0.07093`
  - Silence Ratio: `7.24%` (tail padding only)
  - Tonal Windows: `112/114`

---

## 7. Artifacts List

- `/opt/data/repos/musicom/projects/Styles/Funk/098-funk-som/MIDI/098-funk-som.mid`
- `/opt/data/repos/musicom/projects/Styles/Funk/098-funk-som/MIDI/098-funk-som-phase1.mid`
- `/opt/data/repos/musicom/projects/Styles/Funk/098-funk-som/MIDI/098-funk-som.mid.provenance.json`
- `/opt/data/repos/musicom/projects/Styles/Funk/098-funk-som/MIDI/098-funk-som-phase1.mid.provenance.json`
- `/opt/data/repos/musicom/projects/Styles/Funk/098-funk-som/Audio/098-funk-som.wav`
- `/opt/data/repos/musicom/projects/Styles/Funk/098-funk-som/Audio/098-funk-som.ogg`
- `/opt/data/repos/musicom/projects/Styles/Funk/098-funk-som/Audio/098-funk-som-phase1.wav`
- `/opt/data/repos/musicom/projects/Styles/Funk/098-funk-som/Audio/098-funk-som-phase1.ogg`
- `/opt/data/repos/musicom/projects/Styles/Funk/098-funk-som/Analysis/grid_visualization.txt`
- `/opt/data/repos/musicom/projects/Styles/Funk/098-funk-som/Analysis/audit.json`
- `/opt/data/repos/musicom/projects/Styles/Funk/098-funk-som/Analysis/render_stats.json`
- `/opt/data/repos/musicom/projects/Styles/Funk/098-funk-som/README.md`
- `/opt/data/repos/musicom/projects/Styles/Funk/098-funk-som/REPORT.md`
