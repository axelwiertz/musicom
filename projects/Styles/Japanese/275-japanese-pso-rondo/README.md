# 275 — Japanese PSO Rondo

Nightly composition job · 2026-10-30 · **Method 117 — Particle Swarm
Optimization Composition (PSOC)** · layer **concrete** · paradigm Stochastic.

| Field | Value |
|---|---|
| Genre | Japanese (traditional ensemble) |
| Method | 117 Particle Swarm Optimization Composition (swarm-optimized continuous pitch×onset×velocity lead) |
| Layer | **concrete** (emits raw float-pitch/off-grid events → feeds `generators/` + rules) |
| Form | **rondo** (A1 4 / B 4 / A2 4 / C 4 / A3 4 = 20 bars) |
| Key / Tempo / Meter | A Yo Pentatonic (major pentatonic: A B C# E F#) · 78 BPM · 4/4 (480 TPB) |
| Band | Lead (Koto 107) · Counter (Shakuhachi 77) · Harmony (Shamisen 106) · Bass (Koto low 107) · Drums (ch9) |
| Humanization | style **japanese** + per-instrument DNA · seed 84037 |

## Two-phase architecture

- **Phase 1 (`-phase1.mid`)** — raw PSO draft: 40 particles × 90 iterations
  search a continuous (pitch × onset × velocity) space for a lead melody whose
  fitness rewards scale proximity, stepwise motion, and 8th-grid metric
  alignment. The global-best particle is decoded with RAW float pitch (rounded,
  NOT snapped) and off-grid onsets. Single voice, no harmony.
- **Phase 2 (`-perfect.mid`)** — rules post-process: weight-aware tiered
  quantize (strong = scale **and** chord, weak = scale), 16th grid snap, dedup,
  voice-leading, 3 tagged chromatic approach ornaments on the lead, 5-voice
  Japanese arrangement.
- **Phase 2 (`-humanized.mid`)** — `export_dual`: humanize in place (japanese
  profile + instrument DNA), re-validate, export.

## Scale / harmony (A yo pentatonic)

- Scale pcs {A, B, C#, E, F#} = {9, 11, 1, 4, 6}, intervals [0, 2, 4, 7, 9].
- Open / suspended sonorities per degree: A(maj), B(sus), C#(sus), E(sus), F#(sus).
- Rondo progression (per bar): A1 `I I V I` · B `iii V iii IV` · A2 `I I V I` ·
  C `V IV V iii` · A3 `I IV V I`.

## Artifacts

- MIDI: `MIDI/275-japanese-pso-rondo-{phase1,perfect,humanized}.mid`
- Audio: `Audio/275-japanese-pso-rondo-{phase1,perfect,humanized}.ogg` (+ WAV)
- Analysis: `Analysis/{grid_visualization,grid_visualization_phase1}.txt`,
  `Analysis/{pitch_audit,verify_report,render_report,compose_summary}.json`
- Report: `REPORT.md` · Dashboard: `index.html`

## Regenerate

```bash
cd /opt/data/projects/Styles/Japanese/275-japanese-pso-rondo
$MUSICOM_PYTHON compose.py    # MIDI (phase1 + perfect + humanized)
$MUSICOM_PYTHON render.py     # WAV + OGG (mastered)
$MUSICOM_PYTHON verify.py     # read-only audit (grid + zero-drift + harmony)
```
