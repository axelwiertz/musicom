# 317-factor-oracle-lounge

**Nightly composition job · 2026-11-21 · Method 067 Factor Oracle Guided Improvisation (FOGI).**

| Field | Value |
|---|---|
| Genre / Style | Lounge |
| Method | 067 — Factor Oracle Guided Improvisation (FOGI), **concrete** layer, Stochastic |
| Form | `intro-a-a-b-a` → `Intro·A·A·B·A`, bars `[4,8,8,8,8]` = **36 bars** |
| Key | F major (ionian) — `{F,G,A,Bb,C,D,E}` = `{5,7,9,10,0,2,4}` |
| Tempo / Meter | 90 BPM · 4/4 · 480 TPB (BAR = 1920) |
| Voices | Flute (73) lead · Rhodes (4) pad · Jazz Guitar (26) comp · Acoustic Bass (32) · Drums (ch9) |
| Seeds | raw `20261121` · humanize `52592` |

## Concept

A **Factor Oracle** (Allauzen–Crochemore–Raffinot 1999) is an automaton built
over a seed corpus — forward transitions continue the current motif, suffix
links point at the longest repeated context. Walking it forward emits an
infinite corpus-styled improvisation: forward steps continue a phrase,
suffix-link recombination jumps to a recurring motif (a "Trojan island"),
restart returns to the head (phrase breath). No training — the automaton IS
the model.

Here the 32-symbol degree corpus (`0=F .. 6=E`) is the melodic pitch DNA; the
walk emits the lead's 180-note degree stream over a bossa-lounge 8th-note gate.
The `Intro·A·A·B·A` form supplies the macro-structure; per-bar 7th-chord
regions (`I vi ii V` turnaround, `IV V iii vi ii V I V` bridge) supply the
harmonic grammar the chord-tone snap quantizes against.

## Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw FO walk, single Flute voice. 180 jittered
  events (off-grid onsets, float pitch + chromatic jitter), no harmony.
  Scale violations = 60 (expected — raw draft is pre-rules, deliberately
  imperfect).
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): STRICT chord discipline —
  every note snaps to its own bar's 7th-chord tone (in-scale AND in-chord),
  16th-grid snap, 5-voice Lounge texture.

## Files

- `MIDI/317-factor-oracle-lounge-{phase1,perfect,humanized}.mid` (+ provenance sidecars)
- `Audio/317-factor-oracle-lounge-{phase1,perfect,humanized}.ogg`
- `REPORT.md` (primary record) · `provenance.json` · `index.html` · `README.md`
- `Analysis/` — grid visualization, compose summary, verification, render report
- `compose.py` · `render.py` · `verify.py`

See `REPORT.md` for full audit numbers (grid, harmony, humanization, mastering).
