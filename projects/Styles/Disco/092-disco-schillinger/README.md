# 092-disco-schillinger

**Style:** Disco · **Layer:** concrete · **Method:** 018 Schillinger System of
Musical Design (`generators.schillinger`, resultant of generators a=7, b=4)
**Key:** Eb major · **BPM:** 118 · 4/4 · 480 TPB
**Form:** 6 sections × 4 bars = 24 bars — Intro | Verse | Chorus | Break |
Chorus2 | Outro (46080 ticks)
**Seed:** 20260910 — nightly autonomous composition cron, 2026-09-10

---

## Concept

A disco piece whose **rhythm** is pure Schillinger arithmetic: two periodic
generators (every 7th pulse, every 4th pulse) interfere over 28 pulses to give
the resultant `[4,3,1,4,2,2,4,1,3,4]`, and pitch comes from a coordinate-axis
sine projection. That is the **phase-1** draft — one raw trumpet voice, off the
grid, in no key.

The **phase-2** artifact is the musicom rules layer: 16th-grid lock, Eb-major
scale snap, chord-tone quantization per bar, voice-leading check/correction,
then a full seven-voice disco texture (trumpet hook, sax answer, piano stabs,
organ pad, 16th guitar chank, octave-pulse bass, four-on-the-floor kit).

The point: the Schillinger resultant knows nothing about disco. Every disco
marker you hear — the kick lock, the octave bass, the offbeat chank — is
assigned by the rules layer.

## Files

```
MIDI/     092-disco-schillinger.mid            (rules-processed, 7 voices)
          092-disco-schillinger-phase1.mid     (raw Schillinger draft, 1 voice)
Audio/    092-disco-schillinger.ogg            (Opus 48k — listen here)
          092-disco-schillinger-phase1.ogg     (raw draft A/B)
Analysis/ audit.json  summary.json  concept.json
          grid_visualization.txt  matrix_grid.txt
          render_stats.json  verify.json  tonal_check.json
REPORT.md full record: method, progression, audits, numbers, fixes
```

## Verification (all PASS)

| Check | Result |
|---|---|
| zero-drift (both phases) | PASS — all tracks end at 46080 |
| grid audit, 16th (120) | PASS — 0 / 1237 off-grid |
| harmony audit | PASS — 0 out-of-key, 0 out-of-chord |
| instrument ranges (7 voices) | PASS — all in range |
| silence ratio / RMS | PASS — 8.2 % silence (post-tail only) |
| tonal content (note-energy ratio) | PASS — 0.593 |
| preflight compliance | ✅ exit 0 |

## Listen

Start with `Audio/092-disco-schillinger.ogg`, then A/B against
`Audio/092-disco-schillinger-phase1.ogg` to hear exactly what the rules layer
adds to the raw Schillinger arithmetic.

Full detail: [`REPORT.md`](REPORT.md).
