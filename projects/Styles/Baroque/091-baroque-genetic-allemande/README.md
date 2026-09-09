# 091 — Baroque Genetic Allemande

Concrete-layer algorithmic composition: **Method 003 Genetic Genome
Selection** (raw draft) + **Method 011 TonalNetworkGenerator** walk
(harmony scaffold) + musicom rules post-processing.

- **Genre**: Baroque — allemande (medium-slow 4/4 court dance)
- **Key / tempo**: D aeolian (Dm) · 92 BPM
- **Form**: 24 bars — Intro | AllemandeA | AllemandeB | Lift | AllemandeA2 | Outro
- **Texture**: 7 voices — violin lead, oboe counterline, cello pad, piano
  continuo 16ths, viola inner voice, walking double bass, drums

## Files

- `MIDI/` — phase-1 raw genetic draft + phase-2 rules-processed MIDI (+
  provenance sidecars)
- `Audio/` — FluidSynth SP-001 renders (WAV + Telegram OGG) for both phases
- `Analysis/` — grid visualization, audit.json (grid/harmony/zero-drift),
  summary.json, render_stats.json (silence/RMS)
- `compose.py` — generator (engine-only, seed 20260909)
- `audit.py` — mido read-only verification
- `render_audio.py` / `render_audio_p1.py` — SP-001 render
- `audio_stats.py` — silence/RMS profile
- `REPORT.md` — full record (progression, audits, fixes)

## Verdicts

- Grid (16th): **0 off-grid** over 1221 onsets
- Harmony: **0 out-of-scale / 0 out-of-chord** over all pitched voices
- Zero-drift: PASS (both phases, all tracks end 46080)
- Silence: 4.1% (final tail only) — PASS

## Listening

- Phase 2 (full texture): `Audio/091-baroque-genetic-allemande.ogg`
- Phase 1 (raw genetic draft): `Audio/091-baroque-genetic-allemande-phase1.ogg`
  — compare to hear what the rules layer adds (grid, harmony, groove)