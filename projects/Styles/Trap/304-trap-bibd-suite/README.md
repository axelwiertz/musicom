# 304-trap-bibd-suite

Trap / **Method 132 — Balanced Incomplete Block Design Composition (BIBDC)** (Rules-Based, concrete layer).

## Concept

The ensemble schedule *is* the composition. A balanced incomplete block design
**BIBD(v=4, k=3, λ=2, b=4, r=3)** over the four pitched voices — each of the four
strophic verses is one block (3 voices active, one rotating tacet):

| Verse | Active voices | Tacet | Role |
|---|---|---|---|
| Verse1 | Lead · Pluck · Pad | Bass | atmospheric (no 808) |
| Verse2 | Lead · Pluck · Bass | Pad | 808 enters |
| Verse3 | Lead · Pad · Bass | Pluck | fullest (lead octave-up) |
| Verse4 | Pluck · Pad · Bass | Lead | outro texture |

Every voice plays exactly r=3 verses; every voice-pair co-occurs in exactly λ=2
verses. Pair-novelty (new pairs per verse) = **3 → 2 → 1 → 0** — a provable
monotone-decreasing tension curve.

## Musical DNA

- **Key**: E natural minor `{E F# G A B C D}` · **BPM** 140 · 4/4 · 480 TPB
- **Form**: strophic — 4 × 8 bars = 32 bars = 61,440 ticks (~54.9 s)
- **Harmony**: i · VI · III · VII loop (Em · C · G · D), 2× per verse
- **Voices**: Kalimba lead · Music-box pluck · Warm-pad chords · 808 synth-bass · half-time trap kit

## Files

- `MIDI/304-trap-bibd-suite-phase1.mid` — raw single-voice walk (pre-rules)
- `MIDI/304-trap-bibd-suite-perfect.mid` — grid-locked concrete layer
- `MIDI/304-trap-bibd-suite-humanized.mid` — style humanized twin
- `Audio/304-trap-bibd-suite-{perfect,humanized,phase1}.{wav,ogg}` — mastered renders
- `REPORT.md` — full report
- `Analysis/` — grid visualization, manifest, verification
