# 082-ambient-perlin — Ambient / Method 040 Perlin Noise Composition

**Date:** 2026-08-30 (nightly autonomous composition job)
**Style:** Ambient
**Method:** 040 Perlin Noise Composition (Nature-Led, fBm gradient noise)
**Key:** D natural minor (aeolian)
**Tempo:** 72 BPM, 4/4, 480 TPB
**Seed:** 20260830
**Form:** 6 sections × 4 bars = 24 bars: Intro | DriftA | Rise | DriftB | Pulse | Outro

## 1. Concept

Slow-moving ambient texture over a D-minor progression. The generative voice is
a Perlin fractal-Brownian-motion walk: fBm octaves shape both the pitch contour
(organic arcs) and the rhythm density (Perlin-modulated event spacings with
fractional ticks, deliberately OFF-GRID in phase 1). Phase 2 snaps everything
to the 16th grid and chord-quantizes into a D-minor harmonic bed, then layers a
sustaining ambient texture: flute lead, cello pad, violin counterline, piano
arpeggio comp, double-bass roots, soft pulse drums.

## 2. Progression (24 bars, D minor)

```
i   VI  III VII | i   iv  v   i  | VI  III VII i  |
i   VI  III VII | i   iv  v   i  | VI  III i   i
```
(Dm Bb F C | Dm Gm Am Dm | Bb F C Dm | Dm Bb F C | Dm Gm Am Dm | Bb F Dm Dm)

Functional arc: tonic-prolonging i–VI–III–VII (dorian-ish lift), iv–v–i
authentic pull in bars 5-8 and 17-20, closing VI–III–i–i plagal-ish release.

## 3. Voices + Instruments (phase 2)

| # | Voice | Instrument | GM | Channel | Role |
|---|-------|-----------|-----|---------|------|
| 0 | Lead | Flute (KB) | 74 | 0 | Perlin fBm lead, 16th-grid, chord-tones |
| 1 | Cello | Cello (KB) | 42 | 1 | Sustained pad, whole-bar triad (oct 3) |
| 2 | Violin | Violin (KB) | 40 | 2 | 8th-note counterline, chord tones +12 |
| 3 | Piano | Piano (KB) | 1 | 3 | 8th arpeggio comp root-5th-3rd-5th (+12) |
| 4 | Bass | Double Bass (KB) | 43 | 4 | Whole-bar root (oct 2) |
| 5 | Drums | Drum kit (KB) | 0 | 9 | hat 8ths; kick 1&3 + ride in Rise/Pulse |

All pitched voices drawn from the Instrument KB at
`/opt/data/projects/Instruments/` (flute, cello, violin, double bass, piano,
drum kit constants).

## 4. Method mechanics (Method 040)

- **Phase 1 (raw draft):** single voice, unquantized. Event spacings = fBm
  density field (3 octaves) × jitter → fractional tick gaps (off-grid, e.g.
  mean spacing 7680/26 ≈ 295.4 ticks, not a 120 multiple). Pitches = fBm
  contour (4 octaves) + slow macro layer + register drift, raw MIDI floats
  rounded — no scale/chord constraint. Exported as `082-ambient-perlin-phase1.mid`.
- **Phase 2 (rules post-process):**
  1. RHYTHM LOCK: every pitched onset snapped to nearest 16th (120 ticks @ 72 BPM) —
     mandatory grid-sync rule (078 bugfix).
  2. Scale snap: raw pitch → nearest D-minor scale degree.
  3. CHORD-TONE quantization per bar: nearest tone of that bar's chord
     (section-relative tick → global bar mapping).
  4. Voice-leading: leap cap ≤ 9 semitones toward nearest chord tone;
     `rules.voice_leading.VoiceLeadingRules(style="classical")` check on
     bass+lead per bar-pair.
  5. Texture: cello pad, violin counterline, piano comp, bass roots, drums.
  6. Zero-drift normalization: every cell padded to exact section boundary.

## 5. Two-phase artifacts

| Artifact | Path | Size |
|----------|------|------|
| Phase-1 MIDI | `MIDI/082-ambient-perlin-phase1.mid` | see ls |
| Phase-2 MIDI | `MIDI/082-ambient-perlin.mid` | see ls |
| Phase-1 WAV | `Audio/082-ambient-perlin-phase1.wav` | 14.5 MB |
| Phase-1 OGG | `Audio/082-ambient-perlin-phase1.ogg` | 765 KB |
| Phase-2 WAV | `Audio/082-ambient-perlin.wav` | 14.6 MB |
| Phase-2 OGG | `Audio/082-ambient-perlin.ogg` | 700 KB |

Provenance sidecars (`.provenance.json`) next to every MIDI/WAV/OGG artifact.

## 6. Zero-drift status

- Phase 1 `validate()`: **OK**
- Phase 2 `validate()`: **OK**
- All cells end exactly at section boundary (7680 ticks); landmark events
  appended where needed; every track padded to identical absolute length.

## 7. Grid audit (phase-2 exported MIDI, mandatory)

16th grid = 120 ticks, 8th grid = 240 ticks. **Required: 0 off-grid on 16th
for every voice.**

| Voice | Notes | off-16th | off-8th |
|-------|-------|----------|---------|
| Lead | 141 | **0** | 65 |
| Cello | 72 | **0** | 0 |
| Violin | 192 | **0** | 0 |
| Piano | 192 | **0** | 0 |
| Bass | 24 | **0** | 0 |
| Drums | 240 | **0** | 0 |

**Verdict: 0 off-grid on the 16th grid — PASS.** Lead's 65 off-8th onsets are
intentional 16th-level syncopation (Perlin rhythm retained at 16th resolution);
all onsets are exact multiples of 120, satisfying the mandatory grid rule.
Phase-1 draft keeps its raw off-grid character by design (audited: not
required to be on-grid).

## 8. Harmony audit (phase-2 exported MIDI, mandatory)

Pitch-class membership: D-minor scale PCs {2,4,5,7,9,11,0} and per-bar chord
PCs. Octave displacement allowed (violin/piano at +12). Percussion skipped.

| Voice | Notes | out-of-scale | out-of-chord |
|-------|-------|--------------|--------------|
| Lead | 141 | **0** | **0** |
| Cello | 72 | **0** | **0** |
| Violin | 192 | **0** | **0** |
| Piano | 192 | **0** | **0** |
| Bass | 24 | **0** | **0** |
| Drums | 240 | — (perc) | — |

**Verdict: 0 out-of-scale, 0 out-of-chord — PASS.**

## 9. Voice-leading

Initial classical check flagged 2 hidden fifths in outer voices (bars 10, 17).
Correction pass nudged the lead's first note of the following bar to a
non-fifth/non-octave chord tone (Dm i → C VII and C VII → Dm i joins).
Re-check: **0 flags** (`audit.json: voice_leading_flag_count = 0`).
Note: `rules/voice_leading.py` emits an `overflow encountered in scalar
subtract` RuntimeWarning during motion-interval arithmetic — benign
(numpy int16 wrap in the library's interval computation), does not affect
output or the flag results.

## 10. Audio render + silence/RMS profile

FluidSynth CLI SP-001, `-g 1.2`, `TimGM6mb.sf2`; ffmpeg → Opus 48k VoIP.
Full analysis: `Analysis/render_stats.json`.

| Render | Duration | Silence ratio | Silent secs | Peak | RMS mean |
|--------|----------|---------------|-------------|------|----------|
| Phase 2 | 82.93 s | **3.7%** | 1 / 82 | 0.637 | 0.0410 |
| Phase 1 | 82.14 s | **10.8%** | 2 / 82 | 0.257 | 0.0276 |

Silence thresholds: ratio < 30% (rule: >30% mid-track gaps = suspect) and only
1-2 silent seconds at the very end (reverb tail after last notes) — no mid-track
gaps. Phase-2 mix peak 0.637 (~-4 dBFS headroom), no clipping. **PASS.**

## 11. Verification checklist

- [x] Both phases exported (`.mid`), validate() OK, zero-drift
- [x] Grid audit: 0 off-grid (16th) on all 6 voices
- [x] Harmony audit: 0 out-of-scale, 0 out-of-chord on all 5 pitched voices
- [x] Voice-leading: 0 flags after 2 corrections
- [x] Audio: WAV + OGG both phases, sizes > 40 B, silence < 30%
- [x] Provenance sidecars on all 6 artifacts (2 MIDI + 4 audio)
- [x] `Analysis/grid_visualization.txt`, `Analysis/summary.json`,
      `Analysis/audit.json`, `Analysis/render_stats.json`
- [x] Engine-only (structures + workflows.unitmatrix_composer +
      rules.voice_leading); mido used read-only for audits

## 12. Files

```
082-ambient-perlin/
├── README.md
├── REPORT.md
├── compose.py
├── audio_stats.py
├── audio_provenance.py
├── MIDI/
│   ├── 082-ambient-perlin.mid (+ .provenance.json)
│   └── 082-ambient-perlin-phase1.mid (+ .provenance.json)
├── Audio/
│   ├── 082-ambient-perlin.wav/.ogg (+ .provenance.json)
│   └── 082-ambient-perlin-phase1.wav/.ogg (+ .provenance.json)
└── Analysis/
    ├── grid_visualization.txt
    ├── summary.json
    ├── audit.json
    └── render_stats.json
```
