# 096-trap-skeleton-seoul

Dark half-time trap study: C phrygian bell motif over 808 sub, piano
chord stabs, brass hits, and a half-time trap kit (kick on 1 + 8th
pickup, snare on beat 3, section-density hats).

- Method: 001 Skeleton-First Refinement (concrete) via
  `generators.base.FunctionGenerator` skeleton + musicom rules layer
- Key: C phrygian (C Db Eb F G Ab Bb) - 140 BPM, 4/4, half-time feel
- Form: 6 sections x 4 bars = 24 bars -
  Intro | VerseA | HookB | Bridge | HookB2 | Outro
- Progression (24 bars): i i bII i | i bII bvii bII | bvii bII i i |
  bVII iv bII bII | bvii bII i i | i bII i i

## Files

- `MIDI/096-trap-skeleton-seoul-phase1.mid` - raw generative draft
  (single marimba voice, fractional-tick walk, no harmony)
- `MIDI/096-trap-skeleton-seoul.mid` - rules-processed full texture
- `Audio/096-trap-skeleton-seoul.ogg` - FluidSynth render (Opus)
- `Audio/096-trap-skeleton-seoul-phase1.ogg` - phase-1 render (Opus)
- `Analysis/` - grid_visualization.txt, audit.json, summary.json,
  tonal_check.json, render_stats.json, render_info.json, concept.json,
  matrix_grid.txt
- `Scripts/` - compose.py, audit.py, render_audio.py, audio_stats.py,
  tonal_check.py, summarize.py
- `REPORT.md` - full record (primary)

## DNA

- Pitch DNA: phrygian bell contour in scale-degree steps
  `[0, 1, 1, -1, 0, -2, 1, 0, 2, -1, -1, 0]`, chord-locked per bar
  through `Scale7ChordDegree.get_diatonic_note` (no % 7 wrappers).
- Rhythm DNA: section density skeleton (method-001 structure-first) -
  Intro/Bridge/Outro sparse 8ths, VerseA 16ths, Hooks 16ths + on-grid
  pickup; drums half-time (snare on 3).
- Harmony DNA: i - bII - bvii - bVII - iv phrygian skeleton, V-i style
  half-time weight, perfect-cadence close (bII -> i outro).
- Voice DNA: marimba bell lead, violin counter, piano stabs,
  double-bass 808 sub, trumpet brass stabs, trap kit.
- Structure DNA: skeleton fixed first (bar-plan + densities), ornament
  only inside it - Intro sparse, Hooks dense, Bridge drop, Outro strip.

## Listen for

- The bII (Db) rub against the C root - the phrygian signature.
- Half-time weight: snare lands on 3, not 2 and 4.
- Hook lift: hats double and the bell goes full 16ths.
- Bridge drop: everything strips back to long 808s.
