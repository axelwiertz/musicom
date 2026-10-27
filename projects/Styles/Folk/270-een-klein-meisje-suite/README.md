# 270 — Een Klein Meisje Suite

Dutch Folk / Child Folk (Kleuterlied nursery) extension of
`Folk/239-een-klein-meisje-rework`. Source passed all 6 core engine standards,
so this is an identity-preserving **extension** (not a redesign) that also
closes the pre-2026-10-17 gap: the source shipped a single grid-locked MIDI,
this rebuild ships the full dual-version (perfect + humanized) contract.

Identity preserved: G Major, 105 BPM, 4/4, I-arpeggio nursery motif
(1-3-5-5-3-1 + neighbor 2-3), Markov interval walk over scale degrees,
5-voice band (Lead=Choir Aahs, Counter=Violin, Harmony=Steel Guitar,
Bass, Drums ch9). Form extended 24 → 32 bars (6 → 8 sections) with 7
variation techniques.

- **MIDI (phase 1, raw):** `MIDI/270-een-klein-meisje-suite-phase1.mid`
- **MIDI (phase 2, perfect):** `MIDI/270-een-klein-meisje-suite-perfect.mid`
- **MIDI (phase 2, humanized):** `MIDI/270-een-klein-meisje-suite-humanized.mid`
- **Audio:** `Audio/270-een-klein-meisje-suite-perfect.ogg`,
  `Audio/270-een-klein-meisje-suite-humanized.ogg`
- **Dashboard:** `index.html`
- **Report:** `REPORT.md`

Regenerate: `$MUSICOM_PYTHON compose.py` then `$MUSICOM_PYTHON render.py`.
