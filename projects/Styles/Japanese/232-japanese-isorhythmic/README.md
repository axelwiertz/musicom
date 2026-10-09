# 232-japanese-isorhythmic

**Japanese × Method 032 Isorhythmic Talea-Color Mapping** (concrete, Rules-Based).

A D Phrygian study built on the medieval isorhythmic technique: a fixed 7-note
pitch COLOR (`D Eb G A C A G`, the Japanese *in-sen* pentatonic) and a fixed
5-duration TALEA (quarter, eighth, quarter, eighth, quarter) with
`gcd(7,5)=1`, so the melody perpetually shifts against the bar grid
(35-note = 7-bar cycle).

Ensemble (from instrument registry): Koto (107, lead), Shakuhachi (77,
counterline), Shamisen (106, arpeggio), Taiko (116, DON), GM drums (ch9).

16 bars · 76 BPM · two-phase (raw isorhythmic draft → musicom rules).

## Listen

- `Audio/232-japanese-isorhythmic.ogg` — rules-processed ensemble (phase 2)
- `Audio/232-japanese-isorhythmic-phase1.ogg` — raw color×talea draft (phase 1)

## Files

- `MIDI/*.mid` — phase 1 + phase 2 MIDI (+ provenance sidecars)
- `Audio/*.ogg` — Opus renders
- `Analysis/` — grid visualization, summary.json (audits), render stats
- `compose.py` / `verify.py` / `render.py` — generator, audit, render

Full record: `REPORT.md`.
