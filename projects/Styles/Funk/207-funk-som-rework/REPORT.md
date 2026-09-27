# REPORT — 207-funk-som-rework

**Rework of:** 098-funk-som (Nightly Rework Agent Job)
**Style:** Funk · **Key:** F minor (Aeolian) · **BPM:** 104 · 4/4 · 480 TPB (BAR = 1920)
**Form:** 8 sections × 4 bars = 32 bars = 61,440 ticks (~76.4 s)
**Method:** 075 SOM-C (Self-Organizing Map) + musicom rules (two-phase)
**Seed:** 20260927

---

## 1. Source Identity (preserved)

| Attribute | Source 098-funk-som | This rework |
|---|---|---|
| Genre | Funk | Funk |
| Key | F minor | F minor |
| Tempo | 104 BPM | 104 BPM |
| Method | SOM-C | SOM-C (re-seeded) |
| Voices | Trumpet, Sax, Piano, Bass, Drums | Trumpet, Tenor Sax, Piano, Contrabass, Drums |

## 2. Audit Result (Step 2)

| Standard | Source 098 | Verdict |
|---|---|---|
| 1. Engine (UnitMatrixComposer, no raw mido author) | PASS | — |
| 2. Zero-drift (all voice tracks equal length) | PASS (5×46080) | — |
| 3. Rhythm-grid sync (0 off-grid pitched onsets) | PASS (0/576) | — |
| 4. ≥4 voice tracks | PASS (5) | — |
| 5. Two-phase artifacts (`-phase1.mid` present) | PASS | — |
| 6. `provenance.json` + `index.html` | **MISSING** | **FAIL** |

**Decision: REDESIGN** — rebuild via canonical `UnitMatrixComposer`, preserving identity only. `standard_failures = ["std6_provenance.json", "std6_index.html"]`.

## 3. What Changed

- **Longer form:** 6 sections → 8 sections (Intro, Verse, Chorus, Bridge, Verse2, Chorus2, Solo, Outro); 24 → 32 bars.
- **Sidecars fixed:** project-root `provenance.json` + `index.html` (VoltAgent dashboard) now present.
- **Tenor Sax program corrected** 65 → 66 (actual GM Tenor Sax).
- **Per-section harmonic regions** (bar-0 tonic bug fix): each section starts on a different degree, section roots derived from the MIDPOINT bar.

## 4. Variation Techniques (6 applied)

| Technique | Where | Effect |
|---|---|---|
| Transposition +5 (perfect 4th) | Chorus | Lead contour lifted a 4th |
| Retrograde | Bridge | Pitch sequence reversed |
| Inversion (axis F4) | Chorus2 | Contour mirrored |
| Register shift +12 (octave) | Verse2 | Lead up an octave |
| Diminution ×0.5 | Solo | Note values halved (staccato) |
| Augmentation ×2.0 | Outro | Note values doubled (legato) |

## 5. Per-Section Harmonic Regions

Section roots taken from MIDPOINT bar (never bar 0). Full 32-bar root map printed in `Analysis/rework_verify.json` and dashboard.

- Intro (bars 0–3): `i i iv v` → Fm Fm Bbm Cm
- Verse (4–7): `i VI iv VII` → Fm Db Bbm Eb
- Chorus (8–11): `III VII i iv` → Ab Eb Fm Bbm
- Bridge (12–15): `VI VII III VII` → Db Eb Ab Eb
- Verse2 (16–19): `iv i VI v` → Bbm Fm Db Cm
- Chorus2 (20–23): `VII III VI i` → Eb Ab Db Fm
- Solo (24–27): `i iv III v` → Fm Bbm Ab Cm
- Outro (28–31): `i VI v i` → Fm Db Cm Fm

**Section midpoint roots:** F, Db, Eb, Eb, F, Ab, Bb, Db (6/8 non-tonic → bar-0 tonic bug avoided).

## 6. Verification (real numbers)

| Check | Result |
|---|---|
| MIDI size | phase2 11,232 B · phase1 1,872 B (both > 40) |
| Zero-drift | **5 voice tracks len 61,440** |
| Off-grid pitched onsets | **0 / 704** |
| Scale violations (pc ∉ F minor) | **0** |
| Chord violations (bar `t//BAR`) | **0** |
| Audio | 76.42 s · peak 0.865 · RMS 0.101 · **silence 4.50%** |

## 7. Artifacts

- `MIDI/207-funk-som-rework.mid` (+ `.provenance.json`)
- `MIDI/207-funk-som-rework-phase1.mid` (+ `.provenance.json`)
- `Audio/207-funk-som-rework.wav`
- `Audio/207-funk-som-rework.ogg`
- `Analysis/grid_visualization.txt`
- `Analysis/rework_verify.json`
- `provenance.json` (project root — std6 fix)
- `index.html` (VoltAgent dashboard — std6 fix)
