# 314-abelian-sandpile-suite

**Method 036 — Abelian Sandpile Avalanche (ASAR)** · concrete · Nature-Led
Nightly rework of `277-abelian-sandpile-avalanche` (redesign + extension).

| Field | Value |
|---|---|
| Genre | Experimental |
| Key | D minor (aeolian) — pcs `{D,E,F,G,A,Bb,C}` |
| Tempo | 88 BPM · 4/4 · 480 TPB |
| Form | through-composed `S1..S8` (4 bars each = 32 bars) |
| Seed | raw `20261120` · humanize `66824` |
| Voices | Lead=Marimba · Counter=Celesta · Harmony=Piano · Pad=String Ensemble · Bass=Double Bass |

## Concept

Bak–Tang–Wiesenfeld abelian sandpile on a 14×256 lattice. A "composer's hand"
advances the drop site across register (density arc 3/5/7/11/7/9/5/3), and each
cell toppling is a note. Six variation techniques: transposition (+4 diatonic),
inversion (diatonic mirror), retrograde (section time-reversal), augmentation
(duration doubling + thinning), register shift, counterline variation.

- **Phase 1** — raw toppling stream (off-grid, chromatic jitter, single voice).
- **Phase 2** — strict chord discipline, 16th grid snap, dedup, voice-leading,
  5-voice texture. Dual-version export (-perfect / -humanized).

## Files

- `MIDI/` — `-phase1.mid`, `-perfect.mid`, `-humanized.mid` (+ provenance sidecars)
- `Audio/` — `-phase1.ogg`, `-perfect.ogg`, `-humanized.ogg` (mastered −14 LUFS)
- `Analysis/` — `grid_visualization*.txt`, `compose_summary.json`, `verify_report.json`, `render_report.json`
- `provenance.json` · `index.html` · `REPORT.md`
- `compose.py` / `render.py` / `verify.py`

Full details in `REPORT.md`.
