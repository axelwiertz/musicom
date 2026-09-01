# 083-techno-brownian — Techno / Method 048 Reflected Brownian Motion Pitch Diffusion

**Style:** Techno · **Method:** 048 Reflected Brownian Motion Pitch Diffusion (RBMPD, Nature-Led)
**Key:** F natural minor · **BPM:** 128 · **Bars:** 24 · **Sections:** Intro / Build / Drop / Break / Drop2 / Outro (4 bars each)

## Concept

A four-on-the-floor techno piece whose generative DNA is **Reflected Brownian
motion**: a pitch particle walks with Gaussian innovations, biased by drift
toward the nearest F tonic, and bounces off reflecting barriers at the organ
lead's register edges. The reflections are the signature — they *fold* the walk
back into range, producing the motif repeats and neighbor-tone turns that give
RBMPD its character. Phase 1 keeps the raw diffusion (off-grid fractional
rhythm, unquantized pitches, no harmony). Phase 2 is the musicom rules layer:
16th-grid lock, scale snap, per-bar chord-tone quantization, voice-leading
correction, then a full techno texture.

## Two-Phase Pipeline

- **Phase 1** (`MIDI/083-techno-brownian-phase1.mid`): raw single-voice
  Reflected-Brownian draft (Church Organ 19). Random-walk inter-onset spacings
  are deliberately OFF-GRID (fractional ticks); pitches unquantized with tonic
  drift + barrier reflection. No harmony, no bass, no drums. Audibly a floating
  diffusing line that keeps folding back into the F-minor register.
- **Phase 2** (`MIDI/083-techno-brownian.mid`): rules post-process.
  1. **Grid lock FIRST** (078/079 rule): every onset snapped to 16th (120 @ 128 BPM).
  2. Scale snap to F natural minor, then **chord-tone quantization per bar**
     using GLOBAL bar lookup (`bar = s*BARS_PER + local_bar`).
  3. Leap cap ≤ 9 semitones, drift to nearest chord tone.
  4. `rules.voice_leading.VoiceLeadingRules(style="classical")` — 6 flags
     (hidden octaves/fifths), all fixed by re-voicing the lead to a non-fifth/
     non-octave chord tone of the next bar. Re-check: **0 flags**.
  5. Texture: organ lead, cello pad, piano offbeat stabs, violin counterline,
     double-bass root pulse, four-on-floor drums.
  6. Zero-drift `validate()` gate on both phases: **OK / OK**, then `to_midi()`.

## Voices + Instruments (Instrument KB)

| # | Voice | Instrument | GM | Channel | Role |
|---|-------|-----------|-----|---------|------|
| 0 | Lead | Church Organ (KB) | 19 | 0 | RBMPD lead, 16th-grid, chord-tones |
| 1 | Cello | Cello (KB) | 42 | 1 | Sustained whole-bar triad pad |
| 2 | Piano | Piano (KB) | 1 | 2 | Offbeat 16th stabs (chord tones +12) |
| 3 | Violin | Violin (KB) | 40 | 3 | 8th-note counterline, chord tones +12 |
| 4 | Bass | Double Bass (KB) | 43 | 4 | Root pulse (8ths in drops, quarters elsewhere) |
| 5 | Drums | Drum kit (KB) | 0 | 9 | Four-on-floor: kick, backbeat snare/clap, 16th hats, ride, crash |

## Progression (24 bars, F natural minor)

```
i   VI  III VII | i   iv  v   i  | VI  III VII i  |
i   VI  III VII | i   iv  v   i  | VI  III i   i
```
(Fm Db Ab Eb | Fm Bbm Cm Fm | Db Ab Eb Fm | Fm Db Ab Eb | Fm Bbm Cm Fm | Db Ab Fm Fm)

Functional arc: tonic-prolonging i–VI–III–VII (modal lift) x2, iv–v–i authentic
pull mid-piece, closing VI–III–i–i plagal release. Drop sections (2 & 4) sit on
the modal-loop bars with the full four-on-floor drive.

## Files

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
