# 298 — Lounge Bossa Cocktail

Lounge / bossa-cocktail composition. Smooth, downtempo, cocktail-hour vibe.

**F major · 92 BPM · 4/4 · 40 bars** (2:05 at 92 BPM + tail)

## Instrumentation

| Voice | Instrument | Program | Role |
|---|---|---|---|
| Flute | Flute | 73 | melody (bossa-syncopated lead) |
| Rhodes | Electric Piano 1 | 4 | harmony (sustained 7th chords) |
| Bass | Double Bass | 43 | bossa root/fifth |
| Guitar | Nylon Acoustic | 24 | batida comp (rolled strums) |
| Drums | Drum Kit | ch9 | soft kit (kick 1&3, cross-stick 2&4, airy ride) |

## Harmony — ii–V–I + iii–vi–ii–V turnaround (7th chords)

| Section | Bars | Progression |
|---|---|---|
| Intro | 4 | Fmaj7 — Gm7 — C7 — Fmaj7 |
| A ×3 | 8 | Fmaj7 Fmaj7 Gm7 C7 Am7 **D7** Gm7 C7 |
| B | 8 | Bbmaj7 Bbmaj7 Am7 D7 Gm7 C7 Fmaj7 Fmaj7 |
| Outro | 4 | Fmaj7 — Gm7 — C7 — Fmaj7 |

D7 is the **secondary dominant** (V/V → Gm7) — its chromatic third (F♯) is the
only non-diatonic note (intentional jazz colour, 20 notes across 4 D7 bars).

## Files

- `MIDI/298-lounge-bossa-cocktail-perfect.mid` — grid-locked (0 jitter)
- `MIDI/298-lounge-bossa-cocktail-humanized.mid` — style/instrument humanized
- `Audio/*.ogg` — mastered listening renders (−14 LUFS)
- `compose.py` / `render.py` / `verify.py` — build, render, audit

## Verification

- **Zero-drift** ✓ (all 5 voice tracks equal length)
- **Harmonic audit** (grid-locked): 0 out-of-key except the 20 intentional F♯
  (D7 3rd); 4 diatonic passing tones (melody motion), 0 wrong notes.
- **Humanization**: flute σ 7 ms / bass +8 ms layback / drum anchor σ 2 ms
  (max shift 3 ticks) — groove stays locked.