# 318-sinterklaaslied

A Dutch **Sinterklaas liedje** composed through the musicom engine as the
worked example for the newly registered `sinterklaas` style.

- **Style**: `sinterklaas` (registered 2026-11-22) — see `Notes/style-spec.md`
- **Key/tempo/meter**: C major · 112 BPM · 4/4 march
- **Form**: Intro(4) → Verse(8) → Refrain(8) → Verse(8) → Outro(4) = 32 bars
- **Palette**: recorder (melody) · celesta (pad) · tuba (oom-pah bass) ·
  glockenspiel (bell arp) · light march kit

## Files

| Path | What |
|---|---|
| `compose.py` | engine-only composition + dual export (perfect + humanized) |
| `render.py` | FluidSynth → master(−16 LUFS) → Opus OGG |
| `verify.py` | zero-drift / off-grid / out-of-scale / range / spectral audit |
| `MIDI/*.mid` | `-perfect` (grid-locked) + `-humanized` |
| `Audio/*.ogg` | mastered listening renders |
| `Analysis/*.json` | verification + render report |
| `Notes/style-spec.md` | the Sinterklaas liedje DNA analysis |

## Verification summary

- **zero-drift**: all 5 tracks padded to 61440 ticks (32 × 1920) ✓
- **off-grid**: perfect = 0 · humanized = 550/901 (audible humanization) ✓
- **out-of-scale**: 0 (all diatonic to C major) ✓
- **melody range**: B4–A5 (children-singable) ✓
