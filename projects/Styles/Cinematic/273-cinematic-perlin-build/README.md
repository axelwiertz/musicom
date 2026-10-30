# 273 — Cinematic Perlin Build

Nightly composition job · 2026-10-29 · **Method 040 — Perlin Noise
Composition (PNC)** · layer **concrete** · paradigm Nature-Led.

| Field | Value |
|---|---|
| Genre | Cinematic |
| Method | 040 Perlin Noise Composition (1D gradient-noise fBm: pitch contour + activity density) |
| Layer | **concrete** (emits raw float-pitch/off-grid events → feeds `generators/` + rules) |
| Form | **cinematic-build** (Intro 4 / Build 8 / Rise 8 / Peak 8 / Resolve 4 = 32 bars) |
| Key / Tempo / Meter | D Minor (aeolian) · 76 BPM · 4/4 (480 TPB) |
| Band | Lead (Violin 40) · Counter (Flute 73) · Pad (String Ensemble 48) · Bass (Cello 42) · Drums (ch9) |
| Humanization | style **cinematic** (timing σ 7 ms, phrase_corr 0.6) + per-instrument DNA · seed 34304 |

## Two-phase architecture

- **Phase 1 (`-phase1.mid`)** — raw Perlin draft: a 4-octave fractal-Brownian
  gradient-noise field drives a smooth pitch contour; a second,
  higher-frequency noise field drives onset density and velocity. A per-section
  tension ramp (0.15 → 0.90) lowers the onset threshold so the piece densifies
  toward the Peak. Raw events keep float pitch and jittered (±12%) off-grid
  onsets. Single voice, no harmony.
- **Phase 2 (`-perfect.mid`)** — rules post-process: weight-aware tiered
  quantize (strong = scale **and** chord, weak = scale), 16th grid snap, dedup,
  voice-leading, 2 tagged chromatic approach ornaments on the lead, 5-voice
  arrangement (register ramp per section: lead climbs Intro → Peak).
- **Phase 2 (`-humanized.mid`)** — `export_dual`: humanize in place (cinematic
  profile + instrument DNA), re-validate, export.

## Artifacts

- MIDI: `MIDI/273-cinematic-perlin-build-{phase1,perfect,humanized}.mid`
- Audio: `Audio/273-cinematic-perlin-build-{phase1,perfect,humanized}.ogg` (+ WAV)
- Analysis: `Analysis/{grid_visualization,grid_visualization_phase1}.txt`,
  `Analysis/{pitch_audit,verify_report,render_report,compose_summary}.json`
- Report: `REPORT.md` · Dashboard: `index.html`

## Regenerate

```bash
cd /opt/data/projects/Styles/Cinematic/273-cinematic-perlin-build
$MUSICOM_PYTHON compose.py    # MIDI (phase1 + perfect + humanized)
$MUSICOM_PYTHON render.py     # WAV + OGG (mastered to -14 LUFS)
$MUSICOM_PYTHON verify.py     # read-only audit (grid + zero-drift + harmony)
```