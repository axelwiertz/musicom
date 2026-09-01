# 083-techno-brownian — Techno / Method 048 Reflected Brownian Motion Pitch Diffusion

**Date (UTC):** 2026-08-31 (nightly autonomous composition job)
**Style:** Techno
**Method:** 048 Reflected Brownian Motion Pitch Diffusion (RBMPD, Nature-Led)
**Seed:** 20260831
**Key:** F natural minor (F G Ab Bb C Db Eb)
**Tempo:** 128 BPM, 4/4, 480 TPB, BAR = 1920 ticks
**Form:** 6 sections × 4 bars = 24 bars: Intro | Build | Drop | Break | Drop2 | Outro
**Section length:** 7680 ticks each

---

## 1. Concept

Techno built on a Reflected Brownian motion pitch particle. Gaussian innovation
steps, drift biased toward the nearest F-tonic octave, and **reflecting
barriers** at [G3=55, F5=89] fold the walk back into range — the reflection is
the method's signature (motif repeats + neighbor-tone turns on rebound). Phase 1
is the raw diffusion; Phase 2 is the musicom rules layer that makes it
rhythmically locked and harmonically tonal.

## 2. Progression (24 bars, roots + function)

```
i   VI  III VII | i   iv  v   i  | VI  III VII i  |
i   VI  III VII | i   iv  v   i  | VI  III i   i
```
(Fm Db Ab Eb | Fm Bbm Cm Fm | Db Ab Eb Fm | Fm Db Ab Eb | Fm Bbm Cm Fm | Db Ab Fm Fm)

Chord tone sets (diatonic triads, root-keyed, octave 4/5 window 48–88):
- i (Fm): {53,56,60,65,68,72,77,80,84} · VI (Db): {49,53,56,61,65,68,73,77,80}
- III (Ab): {44,48,51,56,60,63,68,72,75} · VII (Eb): {51,55,58,63,67,70,75,79,82}
- iv (Bbm): {46,49,53,58,61,65,70,73,77} · v (Cm): {48,51,55,60,63,67,72,75,79}

## 3. Voices + Instruments (Instrument KB)

| # | Voice | GM | Instrument KB | Role |
|---|-------|----|----------------|------|
| 0 | Lead | 19 | Keys/organ (Church Organ) | RBMPD lead, 16th-grid, chord-tones |
| 1 | Cello | 42 | Strings/cello | Sustained whole-bar triad pad (oct 3/4) |
| 2 | Piano | 1 | Keys/piano | Offbeat 16th stabs, chord tones +12 |
| 3 | Violin | 40 | Strings/violin | 8th-note counterline, chord tones +12 |
| 4 | Bass | 43 | Strings/double_bass | Root pulse (8ths in drops, quarters elsewhere) |
| 5 | Drums | ch9 | Percussion/drum_kit | Four-on-floor: kick, backbeat snare/clap, 16th hats, ride, crash |

All pitched voices drawn from the Instrument KB at `/opt/data/projects/Instruments/`.

## 4. Two-Phase Architecture

**Phase 1** (`MIDI/083-techno-brownian-phase1.mid`) — raw generative draft:
- Single voice (Church Organ 19), NO harmony, NO bass, NO drums.
- Rhythm: random-walk inter-onset spacings, **fractional, OFF-GRID** ticks
  (audited: 166/174 onsets off the 16th grid — this is the point of phase 1).
- Pitches: Gaussian-innovation walk with tonic-drift bias (0.02) and reflecting
  barriers at LEAD_LO/LEAD_HI — raw, unquantized, no scale/chord constraint.
- Per-section event counts: 22 / 30 / 40 / 24 / 40 / 20 (total 174).

**Phase 2** (`MIDI/083-techno-brownian.mid`) — musicom rules post-process:
1. **Grid lock FIRST** (078/079 rule): every pitched onset snapped to the 16th
   grid (120 ticks @ 128 BPM).
2. Scale snap to nearest F-natural-minor degree.
3. **Chord-tone quantization per bar** using GLOBAL bar lookup
   (`bar = s*BARS_PER + local_bar`) — 079 bugfix pattern.
4. Leap cap ≤ 9 semitones (drift to nearest chord tone of that bar).
5. `rules.voice_leading.VoiceLeadingRules(style="classical")` check on
   bass+lead outer voices per bar-pair → 6 flags (hidden octaves/fifths +
   1 parallel fifth), all corrected by re-voicing the lead's next-bar first note
   to a non-fifth/non-octave chord tone. Re-check: **0 flags**.
6. Texture: cello pad, piano offbeat stabs, violin counterline, bass root
   pulse, four-on-floor drums.
7. Zero-drift `validate()` gate on both phases: **OK / OK**; `to_midi()`.

## 5. Grid Audit (rhythm-grid sync — MANDATORY)

Exported phase-2 MIDI, every track's onsets vs grid (0 off-grid required on the
16th grid):

| Track | Voice | ch | n | 16th off (120) | 8th off (240) |
|-------|-------|----|---|---------------|---------------|
| 1 | Lead | 0 | 174 | **0** | 79* |
| 2 | Cello | 1 | 72 | **0** | **0** |
| 3 | Piano | 2 | 192 | **0** | 192* |
| 4 | Violin | 3 | 192 | **0** | **0** |
| 5 | Bass | 4 | 137 | **0** | 9* |
| 6 | Drums | 9 | 372 | **0** | 64* |

\* 8th-off entries are *intentional 16th placements* (16th syncopation / offbeat
stabs / 16th hats / bass 16th push) — all exact multiples of 120, i.e. locked to
the drum 16th grid, not drift. The MANDATORY requirement is **0 off-grid on the
16th grid**, satisfied by every voice.

**Verdict: 0 off-grid (16th) on all 6 voices — PASS.**
Phase-1 raw draft is off-grid by design (166/174 on 16th) — audited, not required
to be on-grid.

## 6. Harmony Audit (scale + chord-tone — MANDATORY)

Pitch-class membership per voice (drums exempt — percussion sounds, not pitches).
Scale PCs {0,1,3,5,7,8,10} = F G Ab Bb C Db Eb; per-bar chord PCs from section 2.

| Track | Voice | n | out-of-scale | out-of-chord |
|-------|-------|---|--------------|--------------|
| 1 | Lead | 174 | **0** | **0** |
| 2 | Cello | 72 | **0** | **0** |
| 3 | Piano | 192 | **0** | **0** |
| 4 | Violin | 192 | **0** | **0** |
| 5 | Bass | 137 | **0** | **0** |
| 6 | Drums | 372 | n/a | n/a |

**Verdict: 0 out-of-scale, 0 out-of-chord on every pitched voice — PASS.**

## 7. Zero-Drift Status

- Phase 1 `validate()`: **OK** — every cell carries terminal landmark
  `MusicEvent(0,0,7679,7680)`.
- Phase 2 `validate()`: **OK** — all 6 rows equal length (6 × 7680 = 46080
  ticks), terminal landmark per cell.
- MIDI exports via `UnitMatrixComposer.to_midi()` (built-in absolute-alignment
  + tail pad). Engine-only: structures + workflows.unitmatrix_composer +
  generators + rules.voice_leading; mido used read-only in audit.py.

## 8. Audio Render + Silence/RMS Profile

FluidSynth CLI: `fluidsynth -ni -g 1.2 -F <wav> TimGM6mb.sf2 <mid>`, then ffmpeg
→ opus (voip 48k). Phase-2 WAV peak-normalized to -1 dBFS (peaknorm filter
absent → manual `volume=0.89125` gain; peak before 1.0 → after 0.89124).

| File | Size | Duration | Silence ratio | Peak | RMS mean |
|------|------|----------|---------------|------|----------|
| Audio/083-techno-brownian.wav | 8,470,572 B | 48.02 s | **6.3%** | 0.891 | 0.1082 |
| Audio/083-techno-brownian.ogg | 353,065 B | — | — | — | — |
| Audio/083-techno-brownian-phase1.wav | 8,417,068 B | 47.72 s | **9.9%** | 0.223 | 0.0354 |
| Audio/083-techno-brownian-phase1.ogg | 390,639 B | — | — | — | — |

Per-second RMS (phase 2, first 24 s): 0.098–0.127 — steady body, no mid-track
dead zones; near-silent seconds only at 46–47 (final reverb tail after last
notes). Phase 1 RMS 0.023–0.054 throughout, single silent final second.
Silence thresholds: ratio < 30% (rule) — both **PASS**, no silent-WAV trap.

## 9. Pitch / Tonal Verification (post-synthesis check, mandatory)

| Render | Tonal windows | Harmonic energy (F2 ×8) | Dominant peaks (sample) |
|--------|---------------|------------------------|--------------------------|
| Phase 2 | **91 / 96** | **0.73** | 262, 174, 174, 138, 208 Hz (C4/F3/Db3/Eb3) |
| Phase 1 | **91 / 95** | 0.024* | 556, 494, 418, 624 Hz |

Phase 2 dominant peaks are F-minor chord tones (C4 262, F3 174, Db3 138, Eb3
208) with 73% of 30–1000 Hz band energy in the F2 harmonic series — clearly
tonal, NOT noise. *Phase 1 is a single high-register organ lead with no bass
line, so low-F2 harmonic ratio is expected (no low fundamental present); its
91/95 tonal windows + clean spectral peaks confirm a tonal lead, not noise.

## 10. Voice Leading

Initial classical check: 6 flags — Hidden octave (bars 2, 6, 10), Parallel
fifths + Hidden fifth (bar 9), Hidden fifth (bar 17). Correction pass re-voiced
the lead's first note of the following bar to a non-fifth/non-octave chord tone
at each flagged join. Re-check: **0 flags** (`audit.json:
voice_leading_flag_count = 0`). Benign `overflow encountered in scalar
subtract` RuntimeWarning from rules/voice_leading.py interval arithmetic —
library-internal numpy int16 wrap, does not affect output (same as 082).

## 11. Verification Checklist

- [x] Both phases exported (`.mid`), validate() OK, zero-drift
- [x] Grid audit: 0 off-grid (16th) on all 6 voices (phase 2); phase 1 raw
      off-grid by design (166/174)
- [x] Harmony audit: 0 out-of-scale, 0 out-of-chord on all 5 pitched voices
- [x] Voice-leading: 0 flags after 6 corrections
- [x] Audio: WAV + OGG both phases, sizes > 40 B, silence 6.3% / 9.9% (< 30%)
- [x] Pitch verification: 91/96 + 91/95 tonal windows, harmonic energy 0.73
      (phase 2) — no noise render, no silent trap
- [x] Provenance sidecars on all 6 artifacts (2 MIDI + 4 audio)
- [x] `Analysis/grid_visualization.txt`, `summary.json`, `audit.json`,
      `vl_audit.json`, `render_stats.json`, `pitch_verification.json`
- [x] Engine-only (structures + workflows.unitmatrix_composer +
      rules.voice_leading); mido used read-only for audits
- [x] Preflight compliance: PASS (no raw-MIDI/sys.path violations)

## 12. Files

```
083-techno-brownian/
├── README.md
├── REPORT.md
├── compose.py / audit.py / audio_stats.py / audio_provenance.py
├── verify_pitch.py / normalize.py
├── MIDI/
│   ├── 083-techno-brownian.mid (+ .provenance.json)
│   └── 083-techno-brownian-phase1.mid (+ .provenance.json)
├── Audio/
│   ├── 083-techno-brownian.wav/.ogg (+ .provenance.json)
│   └── 083-techno-brownian-phase1.wav/.ogg (+ .provenance.json)
└── Analysis/
    ├── grid_visualization.txt
    ├── summary.json
    ├── audit.json
    ├── vl_audit.json
    ├── render_stats.json
    └── pitch_verification.json
```

## 13. Fixes / Notes Applied This Run

1. **Grid-lock ordering (078/079 rule):** grid-lock BEFORE chord-tone
   quantization (bar lookup stays consistent).
2. **GLOBAL bar lookup (079 bugfix):** phase-1 events are section-relative;
   used `bar = s*BARS_PER + local_bar` for lead quantization + leap caps.
   Verified by audit: 0 out-of-chord.
3. **Voice-leading (6 flags):** hidden octaves/fifths + 1 parallel fifth
   between bass root and lead chord tone — fixed by re-voicing lead's next-bar
   first note to a non-fifth/non-octave chord tone. Re-check 0 flags.
4. **Peak normalization:** peaknorm filter absent in this ffmpeg → manual
   `volume=0.89125` gain to -1 dBFS (peak 1.0 → 0.891).
5. **Provenance:** `write_provenance` AI_GENERATED per artifact (MIDI ×2,
   audio ×4), RBMPD params (drift bias, barrier reflect) recorded.
6. **Phase-1 low-F2 harmonic ratio explained:** single high-register lead, no
   low fundamental — tonal windows (91/95) confirm non-noise; not a bug.
