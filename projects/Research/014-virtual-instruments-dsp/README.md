# 014 — Virtual Instruments DSP Research

**Repo:** musicom-agent/music-projects  
**Status:** Active daily research  
**Focus:** Physical/subtractive synthesis of acoustic instruments via DSP

## Inventory

| Instrument | Date | Src | Audio | MIDI |
|------------|------|-----|-------|------|
| Steel Guitar (lap steel, pitch bend) | 2026-06-24 | ✅ | ✅ | ✅ |
| Resonant Steel Plate (steel) | 2026-06-23 | ✅ | ✅ | ✅ |
| Glass Armonica | 2026-06-22 | ✅ | ✅ | ✅ |
| Resonant Plate (aluminum) | 2026-06-21 | ✅ | ✅ | ✅ |

## Structure

- `Src/` — Python DSP scripts (SciPy/NumPy/Soundfile)
- `Audio/` — WAV (44.1kHz/16-bit), OGG, Opus renders
- `MIDI/` — Paired MIDI exports
- `Analysis/` — Spectral reports, peak validations
- `Notes/` — Design notes and research direction

## Next Research Direction

Electric piano / Rhodes — tine + tonebar mechanical model with magnetic pickup.