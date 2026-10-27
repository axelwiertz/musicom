# SP-109 Tape-Stop / Turntable-Stop — production report

- **Date**: 2026-10-27
- **Job**: random-style production (SP), layer-aligned
- **Method**: SP-109 (`sound.effects.tape_stop`) — TapeStop processor, classic
  mode (rate-ramp resample: pitch AND time drop together, the vinyl/turntable
  stop sound). Cableguys TimeStop-style offline render.
- **Layer**: ABSOLUTE (whole rendered mix processed as one layer; the effect is
  applied as a tape-stop OUTRO over the final 2.5s).

## Selection
- **Registry source**: `workflows.musicom_workflow.SP_METHODS` (69 registered;
  60 in pool after excluding recent-7-day SP-078, SP-090, SP-094, SP-095, SP-101, SP-108, SP-111, SP-119 and
  baseline SP-001).
- **Source composition**: `Styles/Country/038-steel-guitar-demo/MIDI/country_ensemble_16bar.mid`
  (G major country ensemble, 120 BPM, 480 TPB, 16 bars, 2 voices — acoustic
  bass prog 32 + steel acoustic guitar prog 25).

## Pre-flight audit (3 rules) — **FAIL on source, REWORKED before production**

| rule | before (source) | after (rework) |
|---|---|---|
| Grid sync (16th = 120 ticks) | **FAIL** off-grid = 448 | **PASS** off-grid = 0 |
| Harmony (G major scale + chord tones) | out-of-scale = 0, out-of-chord = **105** | out-of-scale = 0, out-of-chord = 0 |
| Zero-drift (equal track ends) | **FAIL** ends = [30480, 34330] | **PASS** ends = [30720] |

The source is an early (June 24) ensemble whose steel-guitar strums are
rolled-chord grace notes (onsets at ~10-30 tick offsets -> 448 off-grid) with
105 non-chord passing/colour tones, and whose two tracks end at different
ticks (30480 vs 34330). It was rebuilt with `UnitMatrixComposer` as a clean
16-bar G major country ensemble faithful to the original DNA: bass
root-5th-root-5th quarter notes over the I-I-I-I IV-IV I-I V-V IV-IV I-I-I-I
progression, steel guitar downbeat strums + 8th-note 5th "chicks". All onsets
grid-locked, all notes chord tones in G major, both tracks end at 30720 ticks
(`validate()` PASS). Raw character preserved in `MIDI/reworked-phase1.mid`.

## SP-109 absolute layer (classic tape-stop outro)
- Carrier: FluidSynth (FluidR3_GM) full-mix render of the reworked MIDI, dry
  (`-R 0 -C 0 -g 1.2`), 44100 Hz.
- Effect: `TapeStop(mode="classic", stop_time_sec=2.5, gain_comp=True)` on
  the final 2.5 s of the mix (the last phrase). Playback rate ramps 1.0 →
  ~0 (exponential), so the piece ends as if a turntable was stopped — pitch and
  time falling together. The preceding body is untouched.
- Mastered to -14 LUFS (country target), −1 dBTP ceiling.

## Verification
- **Pitch**: dominant-peak-in-key hit rate = 1.0000 (66
  windows; the tape-stop outro deliberately detunes the last ~2.5 s, which
  is the desired effect) → **PASS**
- **Harmonic energy (8 harmonics of dominant)**: final 0.7619 vs dry
  0.7620 (retention 1.000)
- **Silence**: 15.09%
- **RMS**: 0.1366
- **LUFS**: -14.00  **true peak**: 0.7445

## Files
- `/opt/data/repos/musicom/projects/Styles/Production/SP109-tape-stop-038-steel-guitar-demo/SP109-tape-stop-038-steel-guitar-demo.wav` (6806060 bytes)
- `/opt/data/repos/musicom/projects/Styles/Production/SP109-tape-stop-038-steel-guitar-demo/SP109-tape-stop-038-steel-guitar-demo.ogg` (251605 bytes)
- `/opt/data/repos/musicom/projects/Styles/Production/SP109-tape-stop-038-steel-guitar-demo/SP109_tape_stop_raw.wav` (tape-stop applied, pre-master)
- `/opt/data/repos/musicom/projects/Styles/Production/SP109-tape-stop-038-steel-guitar-demo/dry_full_mix_reworked_reference.wav` (dry reworked source reference, pre-production)
- `MIDI/source_original.mid` (original source)
- `MIDI/reworked.mid` (clean grid-locked rework)
- `MIDI/reworked-phase1.mid` (raw phase-1 character sidecar)
- `Audio/stems/` (2 dry per-instrument stems, pre-effect)
- `provenance.json`, `Analysis/render_stats.json`

## Notes
- SP-109 is a transition/outro effect, not a continuous processor. Applying it
  across the whole track would slow the entire piece from bar 1 (unmusical);
  the idiomatic use — and the one applied here — is a wind-down over the final
  phrase. `modern` (granular pitch-only drop, time-locked) and `loop`
  (capture+retrigger stutter) modes remain available in the module.
- The composition was brought to rule-clean state before any sound change, per
  the pre-flight gate: 448 off-grid + 105 out-of-chord + zero-drift fail →
  all three to 0.
