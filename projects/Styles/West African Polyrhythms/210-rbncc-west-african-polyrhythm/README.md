# 210-rbncc-west-african-polyrhythm

West African Polyrhythms composition using **Method 082 — Random Boolean
Network Criticality Composition (RBNCC)**.

- **Style:** West African Polyrhythms (gankogui bell, kalimba lead, balafon
  counter, dunun bass, djembe/shaker drums)
- **Method:** 082 RBNCC (Kauffman RBN at the edge of chaos), `concrete` layer
- **Key:** G major · **BPM:** 112 · 4/4 · 32 bars (8 sections)
- **Seed:** 20260928 · transient=1, cycle=12, frozen=[5]

The 12-step RBN attractor cycle against the 16-sixteenth bar produces a
**3:4 cross-rhythm** — the method's signature, not a hand-imposed pattern.

## Files

| Path | Purpose |
|---|---|
| `MIDI/*.mid` | Phase 2 rules composition + Phase 1 raw draft |
| `Audio/*.ogg` | Opus renders (phase 1 + 2) |
| `Audio/*.wav` | Raw PCM (pre-compression) |
| `Analysis/` | grid_visualization.txt + summary.json |
| `REPORT.md` | Full method/verification report |

## Verification

- Grid audit: **0 off-grid** (1328 onsets, all on the 16th grid).
- Harmony audit: **0 out-of-key / 0 out-of-chord** (784 pitched notes).
- Zero-drift: `validate()` PASSED both phases; preflight COMPLIANT.

See `REPORT.md` for the full breakdown.
