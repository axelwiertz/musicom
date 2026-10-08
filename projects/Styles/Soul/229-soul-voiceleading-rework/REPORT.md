# 229 · Soul Voice-Leading Rework

**Rework of** `078-soul-voiceleading` (Soul, F natural minor, Method 007 Voice-Leading Graph Search).

## Source audit (078-soul-voiceleading)

| Standard | Result |
|---|---|
| 1 Engine (UnitMatrixComposer) | PASS |
| 2 Zero-drift | PASS (6 tracks × 46080) |
| 3 Rhythm-grid sync | **FAIL** — 32 off-grid onsets (violin 480+k·180) |
| 4 Track setup (≥4) | PASS (6) |
| 5 Two-phase artifacts | PASS |
| 6 provenance.json + index.html | **FAIL** — both missing |

Extra: 30 lead notes chord-quantized against pre-snap bar → post-snap bar mismatch.
`redesign_required = true`.

## What changed

- **Longer**: 24 → **32 bars** (8 sections: Intro, Verse, Chorus, Verse2, Chorus2, Bridge, Chorus3, Outro).
- **On-grid**: every pitched onset snapped to 120/240 tick grid (`off_grid = 0`).
- **Chord attribution fixed**: pitch quantized using `floor(final_onset // BAR)` after grid snap (`chord_viol = 0`).
- **Register fold, not clamp**: octave-fold chord tones into range (clamp pushed tones out of chord).
- **Diatonic chords only**: dropped the mislabeled "C major V" — uses natural-minor v(Cm), ii(Gdim), VII(Eb) — all in F natural minor (`scale_viol = 0`).
- **Sidecars**: provenance.json (top-level) + index.html dashboard now present.

## Variation techniques (5)

1. **Inversion** — Intro lead = diatonic inversion of the hook around F4.
2. **Method change** — Verse/Outro lead from tonal-network walk; Chorus lead from pentatonic hook.
3. **Register shift** — Verse2 lead = verse walk +1 octave.
4. **Transposition** — Chorus2 lead = hook diatonic-transposed +2 scale steps.
5. **Retrograde** — Bridge lead + violin counterline = retrograde of the hook/line.
6. **Density rise** — drum/horn density curve 0.3→1.0→0.4 across sections.

## Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw tonal-network graph walk — single voice, unquantized chromatic, off-grid onsets (slot 295.4). No harmony.
- **Phase 2** (`.mid`): rules post-process — grid snap → chord-tone quantization (floor bar attribution) → voice-leading check → register fold → full soul texture.

## Verification (real read-only mido numbers)

| Check | Value |
|---|---|
| Phase-2 tracks | 6 voice tracks, length 61440 (zero-drift) |
| Pitched onsets | 708 |
| Off-grid | **0** |
| Scale violations (non-ch9) | **0** |
| Chord violations (non-ch9) | **0** |
| Audio silence ratio | 3.6% (peak 0.889, ~ -15.5 dBFS) |

## Files

- `MIDI/229-soul-voiceleading-rework.mid` — phase 2 (full mix)
- `MIDI/229-soul-voiceleading-rework-phase1.mid` — phase 1 (raw draft)
- `Audio/229-soul-voiceleading-rework.ogg` — Opus render
- `Audio/229-soul-voiceleading-rework.wav` — FluidSynth render
- `Analysis/grid_visualization.txt`, `Analysis/verify.json`, `Analysis/summary.json`
- `index.html`, `README.md`, `provenance.json`
