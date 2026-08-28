# SP-017 — Modified FM (Feedback FM & Phase Modulation) × 072-world-melisma

Production pass (cron, 2026-08-28) applying **SP-017 Modified FM** to the World composition
**072-world-melisma** (D Dorian, 120 BPM file tempo, 20 bars, 5 sections).

Feedback-FM core: carrier phase-modulated by a self-feedback modulator — dynamic harmonic
timbres from breathy lead flutes (β 0.15) to brassy saw-toothed bass (β 0.60), with chaotic
feedback-noise percussion (β > 1.6).

- **Pitch verification: PASS** — 80/80 frames, median 110 Hz, 78/80 note-match, harmonic energy 25% (lowest f0).
- **Silence: 1.9%** — no mid-track gaps.

Full details: [REPORT.md](REPORT.md) · [render_sp017.py](render_sp017.py) · [provenance.json](provenance.json)

## Artifacts
- Audio: [WAV](Audio/SP017-feedback-fm-world-melisma.wav) · [OGG](Audio/SP017-feedback-fm-world-melisma.ogg)
- Stems: `Audio/stems/` (lead, counter, pad, bass, percussion)
- MIDI: [source copy](MIDI/SP017-feedback-fm-world-melisma.mid)
- Analysis: [grid](Analysis/grid_visualization.txt) · [stats](Analysis/render_stats.json)
