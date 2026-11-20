# 315-de-bruijn-groove-blues

**Groove · De Bruijn Universal Cycle (DBUC) · 12-bar blues · E minor · 104 BPM**

Nightly composition job (2026-11-20). Method 077 — De Bruijn Universal Cycle
Composition (concrete, Rules-Based). Form: blues-12.

## Concept

A funky 12-bar blues whose melodic DNA is a de Bruijn sequence. A de Bruijn
cycle `B(k,n)` is a cyclic word of length `n^k` whose every length-`n` window
over a `k`-symbol alphabet appears exactly once — an exhaustive, non-repeating
contour generator.

- **Pitch DNA**: `B(7,2)` → 49 symbols over the 7 diatonic degrees of E minor.
  Every ordered degree pair appears exactly once.
- **Rhythm DNA**: `B(2,3)` → 8 binary symbols (`00010111`), the onset gate
  (1 = hit, 0 = rest), period = one bar.
- The lead walks the pitch cycle across the 8th-note grid, gated by the rhythm
  cycle, then snaps to chord tones under the 12-bar blues progression.

## Voices

| Voice | Instrument | GM | Channel | Role |
|---|---|---|---|---|
| Lead | Clavinet | 7 | 0 | de Bruijn melody |
| Guitar | Muted Guitar | 28 | 1 | funk 16th comp |
| Rhodes | Rhodes | 4 | 2 | backbeat stabs |
| Bass | Electric Bass | 33 | 3 | root/octave funk line |
| Drums | Drum Kit | — | 9 | backbeat groove |

## Progression (12-bar blues, E natural minor)

`Em Em Em Em | Am Am Em Em | Bm Am Em Bm`

## Files

- `MIDI/315-de-bruijn-groove-blues-{phase1,perfect,humanized}.mid` (+ provenance)
- `Audio/315-de-bruijn-groove-blues-{phase1,perfect,humanized}.ogg`
- `REPORT.md` — full composition report
- `provenance.json` · `index.html` · `Analysis/` (grid viz, audits, summary)
- `compose.py` · `render.py` · `verify.py`

See `REPORT.md` for the full two-phase architecture, audits, and loudness data.
