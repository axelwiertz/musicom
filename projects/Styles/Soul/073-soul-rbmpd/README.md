# 073-soul-rbmpd — Soul / Method 048 RBMPD

**Style:** Soul (C minor) · **Method:** 048 Reflected Brownian Motion Pitch Diffusion
**BPM:** 92 · **Key:** C natural minor · **Bars:** 24 · **Sections:** Intro, Verse, Chorus, Verse2, Chorus2, Outro (4 bars each)

## Concept
Soul ballad-groove built from a single physical process: each voice is a particle doing
reflected Brownian motion in pitch space (Skorokhod reflection at corridor walls).
Onsets fire where |dP/dt| exceeds a section threshold; velocity follows a soft-knee
tanh compressor on |dP/dt|. Macro-form comes from the drift schedule:
Intro mu=0 (free wander), Verse mu=-0.15, Chorus mu=-0.35 (tonic pull),
Outro mu=-0.6 (homecoming).

## Two-Phase Pipeline
- **Phase 1** (`MIDI/073-soul-rbmpd-phase1.mid`): raw single-voice RBMPD draft.
  Unquantized continuous semitones, no harmony, no chord context. Audibly a
  wandering "flame-flicker" line with organic density shifts.
- **Phase 2** (`MIDI/073-soul-rbmpd.mid`): rules post-process. Every phase-1 event
  quantized to nearest chord tone of the bar's C-minor soul progression
  (i iv V III | i iv V VI ...), voice-leading leaps capped at 9 semitones, then a
  full soul texture: Lead (Pan Flute), Horn stabs on beats 2&/4&, Rhodes 3rd+7th comp,
  octave-pulse electric bass, backbeat drums (kick 1&3, snare 2&4, hat 8ths,
  claps+ride in choruses).

## Voices
Lead(75), Horns(61), Rhodes(4), Bass(33), Drums(ch9)

## Artifacts
- `MIDI/073-soul-rbmpd.mid` + `MIDI/073-soul-rbmpd-phase1.mid` (both with provenance sidecars)
- `Audio/073-soul-rbmpd.ogg` / `.wav` + phase1 renders
- `Analysis/grid_visualization.txt`, `Analysis/summary.json`
- `compose.py` (engine-only, preflight-clean)

## Verification
- Phase1 validate: OK · Phase2 validate: OK
- Silence check: 4.3% silence (mix), 3.7% (phase1) — no silent-WAV trap
- Preflight: exit 0 (compliant, no raw-MIDI)
- All artifacts > 40 bytes
