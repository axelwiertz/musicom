# 219-japanese-kojo-koto-rework

Japanese-style algorithmic composition — extended Jo-Ha-Kyu rework of
`103-japanese-kojo-koto`. A hirajoshi pentatonic, L-System dragon-curve fractal,
32 bars across 8 sections with 6 variation techniques.

- **Key:** A hirajoshi pentatonic (A Bb D E G)
- **BPM:** 80 · 4/4 · 480 TPB
- **Method:** 019 L-System (dragon-curve)
- **Form:** Jo · Ha1 · Ha2 · Bridge · Kyu1 · Kyu2 · Interlude · Jo_Coda (8×4 = 32 bars)
- **Voices:** Koto, Shakuhachi, Shamisen, KotoBass, Taiko

## Files

- `MIDI/219-japanese-kojo-koto-rework.mid` — Phase 2 (rules-processed, 5 voices)
- `MIDI/219-japanese-kojo-koto-rework-phase1.mid` — Phase 1 (raw L-system draft)
- `Audio/219-japanese-kojo-koto-rework.ogg` — Opus render
- `Audio/219-japanese-kojo-koto-rework.wav` — FluidSynth render
- `Analysis/grid_visualization.txt` — timeline grid
- `Analysis/rework_verify.json` — read-only audit numbers
- `index.html` — dashboard

## Variation techniques

1. Augmentation (Jo — quarter-note lead)
2. Inversion (Ha2 — negated deltas)
3. Method change (Bridge — pentatonic arpeggio)
4. Retrograde + diminution (Kyu1 — reversed deltas, 16ths)
5. Register shift (Kyu2 — lead 74–90, octave lift)
6. Canon counterline (Interlude — shamisen echo)

See `REPORT.md` for the full audit + verification numbers.
