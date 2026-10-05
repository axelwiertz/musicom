# 224-blues-otvl — Blues × Method 050 (Optimal Transport Voice Leading)

Autonomous nightly composition job — 2026-10-05. Project number **224**.

---

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Style | **Blues** (random from `Styles/` genre folders, date-seeded RNG 20261005) |
| Method | **050 — Optimal Transport Voice Leading (OTVL)** |
| Layer | **concrete** |
| Layer roll | `rng.random()` = **0.339268** > 1/7 → concrete pool (correct cadence; last abstract job = 221 on 2026-10-04) |
| Excluded (last 7 d) | methods used 2026-09-28 → 10-05: `{001,002,007,010,012,016,018,019,020,025,026,031,032,040,041,048,069,075,082,095}` |
| Concrete pool | 83 methods → pick index 33 → **050 OTVL** |

Method 050 essence (from `methods_db.md`): solves voice leading as an
**optimal-transport** problem — minimum-cost redistribution of pitch masses
between successive chords via Wasserstein distance. Transport plan = voice
assignment; plan entropy = texture; $W_p$ = continuous harmonic tension.

## 2. Composition brief

| Field | Value |
|---|---|
| Title | "Blues Transport" (working) |
| Genre / subgenre | Blues · 12-bar dominant blues |
| Key | **E blues** (12-bar dominant-blues tonality) |
| Tempo / meter | 100 BPM, 4/4, 480 TPB → `BAR = 1920` ticks |
| Form | **6 sections × 4 bars = 24 bars = 2 × 12-bar blues** |
| Emotional target | Gritty, swinging, transport-driven voice-leading smoothness under raw blues color |

### Blues tonality (E)
The 12-bar dominant blues requires I7/IV7/V7 dominant-seventh chords whose
chord tones (notably the major 3rd of the I and the subdominant's leading tones)
are chromatic to any single 7-note scale. The key is therefore declared as the
**union of the three dominant-7th chord tones plus the blue 3rd and flat 5th**:

```
KEY_PCS = {1, 2, 3, 4, 6, 7, 8, 9, 10, 11}
        = {C#, D, D#, E, F#, G, G#, A, Bb, B}
excluded: C (0), F (5)   -- the notes most foreign to the E-A-B dominant frame
```

### Chords (dominant 7th + blue notes; each ⊆ KEY_PCS)

| Degree | Chord | Pitch-class set | Root (bass) |
|---|---|---|---|
| 0 | I7 = E7 | {E, G, G#, A, Bb, B, D} = {4,8,11,2,7,10} | E2 = 40 |
| 1 | IV7 = A7 | {A, C#, Eb, E, G} = {9,1,3,4,7} | A2 = 45 |
| 2 | V7 = B7 | {B, D, D#, F#, A} = {11,2,3,6,9} | B2 = 47 |

### 12-bar progression (×2)

```
Bar:  1  2  3  4 | 5  6  7  8 | 9  10 11 12
      I  I  I  I | IV IV I  I | V  IV I  I    (E7 / A7 / B7)
```

## 3. Two-phase architecture

### Phase 1 — raw OTVL draft (`224-blues-otvl-phase1.mid`, 1768 B)
Single voice (harmonica, ch 0). The lead is an **optimal-transport walk**:

- Each bar's chord is a 4-note **mass** (close voicing of chord tones).
- Between bars, a **monotone (1D-optimal) transport** redistributes the mass:
  each mass point moves to the positionally-matched point of the next chord
  (min $\sum|\Delta|$ = the Wasserstein cost). The lead follows the **top mass
  point** → smooth voice leading.
- Transport cost drives articulation: higher $W$ = shorter, louder attacks.
- **Off-grid by construction** (micro-timing jitter) + **chromatic** micro-jitter
  (pre-rules, no chord/scale quantization).

Raw fingerprint: **177 / 192 onsets off-grid** (by design — this is the point
of phase 1). Zero-drift landmark holds; `validate()` passes.

### Phase 2 — musicom rules post-process (`224-blues-otvl.mid`, 8956 B)

| Rule | Applied |
|---|---|
| 16th-grid snap (120 ticks) | ✅ all pitched onsets on 8th/16th grid |
| Per-bar chord-tone quantization | ✅ nearest chord tone per bar (blue notes are chord tones) |
| Register clamp | ✅ lead 58–90, comp 45–79, bass 36–52 |
| Full texture | ✅ 5 voices |
| Voice-leading check | ✅ `VoiceLeadingRules(style="classical")` on bass+lead outer voices |
| Zero-drift normalization | ✅ `validate()` passes, all 5 tracks × 46080 |

**Voice-leading flags: 3** (parallel/hidden fifths between the walking bass
root and the harmonica lead top note at the I→IV→V bar boundaries). **Left
uncorrected by design** — parallel perfect intervals between a root-driven
walking bass and a harmony-following lead are idiomatic to blues (the genre's
open-fifth / power-chord vocabulary); the classical parallel-fifths prohibition
does not apply to a 12-bar dominant blues. (Documented, not silently dropped.)

## 4. Voices & instruments (from `instrument_registry.py`)

| Voice | Instrument (registry) | GM program | Channel | Notes |
|---|---|---|---|---|
| Lead | HARMONICA | 22 | 0 | OTVL-transported melody, blue-note color |
| Piano | PIANO | 0 | 1 | offbeat 8th-note chord stabs (root+3rd+7th) |
| Guitar | ACOUSTIC_GUITAR | 25 | 2 | root+fifth chank on every 8th (straight) |
| Bass | DOUBLE_BASS | 32 | 3 | root-anchored quarter-note walk (root→blue3rd→5th→approach) |
| Drums | DRUM_KIT | — | 9 | kick 1+3, snare 2+4 backbeat, hat 8ths, crash on chorus-2 downbeats |

## 5. Verification (read-only `mido` audit)

### Phase 2 (rules-processed)

| Gate | Result |
|---|---|
| File size > 40 B | 8956 ✓ |
| Zero-drift (voice tracks equal length) | **5 × 46080 ✓** |
| Total notes | 1068 (768 pitched + 300 drums) |
| **Off-grid (16th)** | **0** ✓ |
| **Off-grid (8th)** | **0** ✓ |
| **Scale violations** (pc ∉ KEY_PCS) | **0** ✓ |
| **Chord violations** (pc ∉ bar chord) | **0** ✓ |

Per-voice grid + harmony audit:

| Track | Channel | Notes | off16 | off8 | out-of-scale | out-of-chord |
|---|---|---|---|---|---|---|
| Lead (harmonica) | 0 | 192 | 0 | 0 | 0 | 0 |
| Piano | 1 | 96 | 0 | 0 | 0 | 0 |
| Guitar | 2 | 384 | 0 | 0 | 0 | 0 |
| Bass | 3 | 96 | 0 | 0 | 0 | 0 |
| Drums | 9 | 300 | 0 | 0 | — (unpitched) | — (unpitched) |

### Phase 1 (raw)

| Gate | Result |
|---|---|
| File size > 40 B | 1768 ✓ |
| Zero-drift | 1 × 46080 ✓ |
| Notes | 192 |
| Off-grid (16th/8th) | **177** (raw fingerprint — by design) |

## 6. Audio render (SP-001 FluidSynth + FluidR3_GM.sf2 → Opus)

- `Audio/224-blues-otvl.wav` — 12.1 MB, 44.1 kHz stereo, **68.68 s**, peak **0.8732**
  (normalized: `peaknorm` unavailable → `volume=1.07`).
- `Audio/224-blues-otvl.ogg` — 488 KB, Opus 48 kbps voip.
- **Silence:** 14.3 % total (reverb/release tail). Music body (first ~58 s) has
  **zero silent seconds**; per-second RMS ≈ 0.12–0.15. The 9 near-zero seconds
  are the **release tail** after the final cadence — **no mid-track gaps** (not
  the silent-render trap).
- **FFT tonal check** (FluidSynth GM render — pitch is guaranteed by MIDI note
  numbers, verified at source by the 0/0 scale/chord audit): dominant frames
  `{330 (E4), 164 (E3), 98–104 (G2/G#2 walk), 494 (B4)}` Hz — all harmonics of
  the E-blues frame. No broadband noise.

## 7. Files

```
224-blues-otvl/
├── compose.py                  # canonical UnitMatrixComposer two-phase workflow
├── render_audio.py             # FluidSynth -> WAV -> normalize -> OGG + analysis
├── MIDI/   224-blues-otvl.mid            (+ .provenance.json, phase 2)
│           224-blues-otvl-phase1.mid     (+ .provenance.json, phase 1)
├── Audio/  224-blues-otvl.wav  (12.1 MB)
│           224-blues-otvl.ogg  (488 KB, Opus)
├── Analysis/ grid_visualization.txt · summary.json · verify.json · render_stats.json
├── Scripts/  verify.py         # read-only mido audit (grid + scale + chord)
├── README.md
├── REPORT.md
└── index.html                  # VoltAgent dashboard
```

Rerun: `$MUSICOM_PYTHON compose.py` (env `musicom`).

## 8. Fixes applied during this job

1. **Root-anchored bass walk** (initial version): the walking bass originally
   took the *lowest* chord tone in range (D2, the b7 of E7) as its first beat,
   producing a sub-root 74 Hz anchor. Fixed to anchor on `DEG_ROOT` and walk
   `root → blue-3rd/3rd → 5th/blue-5th → approach` within `root..root+12`.
2. **Master normalization**: `peaknorm` filter unavailable in this ffmpeg →
   fell back to `volume=1.07` (peak 0.83 → 0.87, safely under 0 dBFS).
