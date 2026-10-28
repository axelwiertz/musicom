# 271 — Funk SNN Spiking

Nightly composition job · 2026-10-28 · **Method 109 — Spiking Neural Network
Composition (SNN-C)** · layer **concrete** · paradigm Nature-Led.

| Field | Value |
|---|---|
| Genre | Funk |
| Method | 109 SNN-C (Izhikevich spiking network, theta-gamma clock, STDP decode) |
| Layer | **concrete** (emits raw events → feeds `generators/` + rules) |
| Form | **rondo A–B–A–C–A** (4 bars × 5 = 20 bars) |
| Key / Tempo / Meter | F Major · 105 BPM · 4/4 (480 TPB) |
| Band | Lead (Clavinet 7) · Guitar (Clean Electric 27) · Brass (Brass Section 61) · Bass (Electric Bass 33) · Drums (ch9) |
| Humanization | style **funk** (timing σ 4 ms) + per-instrument DNA · seed 38252 |

## Two-phase architecture

- **Phase 1 (`-phase1.mid`)** — raw SNN draft: 12 tonotopic pitch-class columns
  of Izhikevich RS neurons, driven by a thalamic theta (bar) + gamma (16th)
  clock, a prefrontal F-major scale bias, and an insula tension envelope
  (HOME → LIFT → HOME → TENSE → TURN across the 5 rondo sections). Spike
  trains decoded by population rate (softmax winner) → 302 raw events with
  float pitch, off-grid onsets, rate velocities. Single voice, no harmony.
- **Phase 2 (`-perfect.mid`)** — rules post-process: weight-aware tiered
  quantize (strong = scale **and** chord, weak = scale), 16th grid snap,
  dedup, funk phrasing-thinning (rests), voice-leading, 4 tagged chromatic
  approach ornaments, 5-voice arrangement.
- **Phase 2 (`-humanized.mid`)** — `export_dual`: humanize in place (funk
  profile + instrument DNA), re-validate, export.

## Artifacts

- MIDI: `MIDI/271-funk-snn-spiking-{phase1,perfect,humanized}.mid`
- Audio: `Audio/271-funk-snn-spiking-{phase1,perfect,humanized}.ogg` (+ WAV)
- Analysis: `Analysis/{grid_visualization,grid_visualization_phase1}.txt`,
  `Analysis/{pitch_audit,verify_report,render_report,compose_summary}.json`
- Report: `REPORT.md` · Dashboard: `index.html`

## Regenerate

```bash
cd /opt/data/projects/Styles/Funk/271-funk-snn-spiking
$MUSICOM_PYTHON compose.py    # MIDI (phase1 + perfect + humanized)
$MUSICOM_PYTHON render.py     # WAV + OGG (mastered to -13 LUFS)
$MUSICOM_PYTHON verify.py     # read-only audit (grid + zero-drift + harmony)
```
