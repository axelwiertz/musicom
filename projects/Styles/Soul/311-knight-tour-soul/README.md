# 311-knight-tour-soul — Soul via Knight's Tour Composition (method 126)

Nightly composition job · 2026-11-18 · **Soul** · **Method 126 Knight's Tour
Composition (KTC)** (Rules-Based, concrete layer) · **verse-chorus** · **F major**
· 96 BPM · 40 bars.

A knight's tour (Hamiltonian path on the knight graph) walks an 8×n board whose
**rows are F-major scale degrees** and **columns are time-slot classes** — each
cell visited exactly once, so each of the 8 scale degrees is visited exactly n
times (2D aggregate). The tour order is the melody: knight moves of |Δrow|=1/2
scale steps produce a stepwise, singable soul line; the knight signature
|Δr|·|Δc|=2 anti-correlates melodic leap with short duration and step with long
duration. The **board-transpose of the tour** (columns → pitch) is the dual
voice — the Choir backing vox counter-line in the choruses.

## Files

- `MIDI/311-knight-tour-soul-phase1.mid` — raw knight-tour draft (single voice, unquantized)
- `MIDI/311-knight-tour-soul-perfect.mid` — phase-2 rules, grid-locked
- `MIDI/311-knight-tour-soul-humanized.mid` — phase-2 + style/inst humanization
- `Audio/*-{perfect,humanized,phase1}.ogg` — mastered Opus renders
- `Analysis/` — grid visualization, verification, render stats, compose summary
- `REPORT.md` — full method + audit record

## Texture (5 voices)

| Voice | Instrument | Program | Role |
|---|---|---|---|
| Lead | Tenor Sax | 66 | Knight's-tour melody |
| Rhodes | Electric Piano 1 | 4 | Comp chords (voice-led triads) |
| Bass | Electric Bass (finger) | 33 | Root/fifth soul line |
| Vox | Choir Aahs | 53 | Transpose-tour counter (chorus) / pad |
| Drums | Drum Kit | ch 9 | Backbeat (kick 1&3, snare 2&4, 8th hats) |

## Harmony

F major — I vi IV V soul cycle, per-section regions:
Intro F–Bb–F–C · Verse F–Dm–Bb–C–F–Dm–Gm–C · Chorus F–Dm–Bb–C–F–Bb–C–F ·
Verse2 = Verse · Chorus2 = Chorus · Outro F–Bb–C–F.

## Verify

```
/opt/data/micromamba/envs/musicom/bin/python verify.py   # -> VERIFY_OK
/opt/data/micromamba/envs/musicom/bin/python render.py   # -> RENDER_OK
```
