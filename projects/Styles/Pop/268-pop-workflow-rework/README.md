# 268-pop-workflow-rework

Rework of `Styles/Pop/workflow-demo` (nightly rework job 2026-10-26).

- **Genre:** Pop · **Key:** C major · **Tempo:** 120 BPM · **Form:** 8 sections / 32 bars
- **Pipeline:** two-phase `UnitMatrixComposer` (raw generative draft → musicom rules)

## Files
- `MIDI/268-pop-workflow-rework-phase1.mid` — raw generative draft (pre-rules, single voice)
- `MIDI/268-pop-workflow-rework-perfect.mid` — grid-locked rules layer
- `MIDI/268-pop-workflow-rework-humanized.mid` — humanized (style + instrument DNA)
- `Audio/268-pop-workflow-rework-{perfect,humanized}.ogg` — mastered Opus renders
- `Analysis/grid_visualization.txt`, `Analysis/rework_audit.json`, `Analysis/render_report.json`
- `REPORT.md` — full audit + variation + verification detail

## Verification (read-only mido)
- Zero-drift: 5 voice tracks × 61440 ticks (32 bars) — equal
- Off-grid: perfect 0 · humanized > 0
- Scale violations: 0 · Chord violations: 0 (perfect layer)
