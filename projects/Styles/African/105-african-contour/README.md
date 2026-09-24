# 105-african-contour

African polyrhythmic composition using **Method 095 — Contour Theory
Composition (CTC)**, the first numeric **abstract-layer** method in the Musicom
methods database.

## Concept

- **Style:** African (kalimba + flute call/response + marimba bell interlock + djembe)
- **Method:** 095 CTC (abstract layer) — melodies designed as contour *shapes*
  (CSeg rank sequences + CAS direction strings), transformed under I/R/RI,
  then realized onto the C-major pentatonic.
- **Key:** C major pentatonic (C D E G A) · **BPM:** 112 · 4/4 · 480 TPB
- **Form:** Intro | Theme | Variation | Development | Climax | Outro (6 × 4 = 24 bars)

## Two-phase architecture

1. **Phase 1** (`MIDI/...-phase1.mid`) — raw abstract draft: single Kalimba
   voice, whole-tone contour, off-grid timing, no harmony.
2. **Phase 2** (`MIDI/....mid`) — musicom rules post-process: 16th-grid lock,
   pentatonic + per-bar palette quantize, full 5-voice African texture.

## Files

- `MIDI/` — editable DAW files (both phases) + provenance sidecars
- `Audio/` — FluidSynth WAV + Opus OGG renders (both phases)
- `Analysis/` — grid visualization, contour summary, audit, render stats
- `compose.py` — generates both phases via `UnitMatrixComposer`
- `verify.py` — mido read-only audit (zero-drift / grid / scale / chord)
- `render_audio.py` — FluidSynth CLI → WAV → OGG + silence/RMS/tonal analysis

## Verification (summary)

- Zero-drift: 5 tracks × 46080 ticks (equal length) — **PASS**
- 16th-grid off-grid (Phase 2): **0 / 856**
- Out-of-scale (Phase 2): **0 / 424** · Out-of-chord: **0 / 424**
- Phase-1 raw fingerprint: 159/160 off-grid

See `REPORT.md` for the full record.
