# 310 — Country Road Rework (redesign of 012-country-country-uke)

## Decision: REDESIGN (audit failed 5 of 6 standards)

Source `012-country-country-uke` (Country-pop road song, G major, 96 BPM, 48 bars)
was audited against current engine standards and **failed**:

| Standard | Result |
|---|---|
| 1. Engine (UnitMatrixComposer), not hand-rolled | FAIL — `Scripts/generate_v2.py` authors MIDI with raw `mido.MidiTrack()/note_on/.save()` |
| 2. Zero-drift | FAIL — 8 distinct voice-track lengths `{91680..92400}` |
| 3. Rhythm-grid sync | FAIL — 192 off-grid pitched onsets of 1608 |
| 4. Track count >= 4 | PASS — 8 voices |
| 5. Two-phase artifacts | FAIL — no `-phase1.mid` |
| 6. provenance.json + index.html | FAIL — index.html yes, provenance.json missing |

Rebuilt from scratch through the canonical `UnitMatrixComposer` workflow,
preserving the musical identity (genre/key/tempo/progression/instrumentation).

## Identity preserved from source

- Genre: Country (Country-pop road song), key G major, 96 BPM, 4/4
- Core progression: G–D–Em–C (I–V–vi–IV)
- 8 voices: Lead Vocal(53), Harmony Vox(52), Acoustic Guitar(24),
  Electric Guitar(29), Bass(33), Drums(ch9), Fiddle(40), Pedal Steel(48)

## What changed (new piece)

- **Longer**: 68 bars (source 48) across 10 sections (source 8).
  Intro 4 · Verse 1 8 · Pre-Chorus 4 · Chorus 1 8 · Verse 2 8 · Chorus 2 8 ·
  Bridge 8 · Solo 8 · Final Chorus 8 · Outro 4.
- **Per-section harmonic regions**: each section owns its own progression
  (Intro G-D-Em-C; Verse/Chorus G-D-Em-C-G-D-C-D; Pre-Chorus C-D-Em-D;
  Bridge Em-C-G-D-Em-C-**Am**-D [relative-minor shift + ii]; Solo G-Em-C-D x2;
  Outro G-C-G-G). No section defaults to bar-0 tonic.

## Variation techniques (7)

1. **Inversion** — Verse 2 inverts the Verse 1 lead contour around G4 (67),
   re-quantized to chord tones.
2. **Register shift** — Pre-Chorus quantization window raised (+4/+5 semitones);
   Final Chorus raised +12 (one octave).
3. **Retrograde** — Outro uses the descending motif D5-B4-A4-G4 (5-3-2-1),
   the reversal of the intro's 1-2-3-5 rise.
4. **Mode shift** — Bridge emphasizes relative minor (Em) and adds Am (ii),
   low register, sustained fiddle texture.
5. **Augmentation** — Solo: fiddle takes the lead with durations doubled
   (half speed).
6. **Density rise + counterline** — Chorus 2: 16th-note electric arpeggios,
   open hi-hat, fiddle off-beat counterline.
7. **Diminution** — Outro: pedal-steel durations shortened with velocity taper.

## Two-phase architecture

- **Phase 1** (`-phase1.mid`): seeded random-walk `pitch_index` in [0,1] +
  unquantized rhythm, single voice. Raw by design (off-grid + off-scale).
- **Phase 2** (`-perfect.mid` / `-humanized.mid`): musicom rules — per-bar
  chord-tone quantization (floor `t // BAR` attribution), rhythm-grid snap to
  16th (120 ticks), `(start_tick, pitch)` dedup keeping longest, register
  enforcement, per-section harmonic regions.

## Dual-version export (humanization)

- Style profile `country` (timing_sigma 9 ms, velocity_sigma 6.5, phrase_corr
  0.5, layback 2 ms) + per-voice instrument DNA (drums anchor 2 ms/0 layback,
  bass lays back 8 ms, choir/steel velocity +6-8).
- `hz_seed = 2163656159` (md5 of style+key+bpm+bars+seed).
- Perfect = grid-locked (off-grid 0). Humanized = jitter applied (off-grid > 0).

## Verification (read-only mido)

| artifact | tracks | len (ticks) | zero-drift | off-grid | scale viol | chord viol (floor) | chord viol (grid) |
|---|---|---|---|---|---|---|---|
| phase1 | 1 | 130560 | true | 405 | 209 | 319 | — |
| perfect | 8 | 130560 | true | **0** | **0** | **0** | **0** |
| humanized | 8 | 130560 | true | 1873 | **0** | 78* | **0** |

`*` 78 floor-attributed chord violations in the humanized layer are bar-line
jitter artifacts: the humanizer shifts onsets up to ~18 ticks, and notes
originally on beat 1 can cross into the previous bar under `t // 1920`. Pitch
is untouched (scale violations 0); grid-attributed (`round(t/120)*120//1920`)
count is 0, proving the intended-bar chord membership is exact.

## Files

- MIDI: `310-country-road-rework-phase1.mid`,
  `310-country-road-rework-perfect.mid`, `310-country-road-rework-humanized.mid`
  (+ `.provenance.json` sidecars)
- Audio: `Audio/310-country-road-rework-{phase1,perfect,humanized}.ogg` (+ .wav)
- Analysis: `grid_visualization.txt`, `grid_visualization_phase1.txt`,
  `compose_meta.json`, `verification.json`, `render_stats.json`

## Render + mastering (FluidSynth → `master()` → Opus OGG)

| artifact | target LUFS | integrated LUFS | true peak | silence |
|---|---|---|---|---|
| phase1 | -14 | -14.01 | -1.0 dBTP | 1.86% |
| perfect | -14 | -14.00 | -1.0 dBTP | 1.80% |
| humanized | -14 | -14.01 | -1.0 dBTP | 1.83% |

SoundFont FluidR3_GM.sf2; rendered at 22050 Hz to keep `master()`'s 4x
true-peak oversample under the ~1.7 GB cgroup memory ceiling.

