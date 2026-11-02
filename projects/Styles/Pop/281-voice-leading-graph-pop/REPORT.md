# REPORT — 281-voice-leading-graph-pop

**Nightly composition job · 2026-11-02 · Method 011 Voice-Leading Graph Search (VLG)**

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Seed | 20261102 (nightly date) |
| Style | **Pop** (random draw from `/opt/data/projects/Styles/` genre dirs) |
| Method | **011 — Voice-Leading Graph Search (VLG)** |
| Layer | **concrete** (Rules-Based) — emits raw `MusicEvent`s straight into the graph-walk → two-phase pipeline; no abstract design stage |
| Paradigm | Rules-Based · Grid-Locked · Local/Path memory |
| Form | **intro-verse-chorus-bridge-outro** (4/8/8/4/4 = 28 bars) via `pick_form("pop")` → `form_to_sections` |
| Key | C major (ionian) — TONIC_PC 0, KEY_PCS {0,2,4,5,7,9,11} |
| Tempo | 118 BPM · 480 TPB · BAR = 1920 ticks |

Method 011 was drawn from the **concrete** pool (89 candidates), excluding the
last-7-days set `{1,2,23,25,28,36,38,40,43,91,95,98,104,109,111,113,117,121}`
plus abstract `{95,99,104,113,127,131}` and impractical AI-driven methods. This
is a concrete night (~6/7 cadence).

## 2. Method — Voice-Leading Graph Search (Neo-Riemannian, diatonic)

The compositional engine is a graph over the seven C-major triads whose edges are
voice-leading-preserving transformations, all in-key:

- **R** (relative): I↔vi, IV↔ii, V↔iii
- **L** (leading-tone exchange): I↔iii, IV↔vi, V↔vii°
- **plagal** IV→I, **authentic** V→I, **subdominant** I→IV, **deceptive** V→vi

Adjacency `VOICE_LEAD_GRAPH`:
`1→{6,3,4,5} 2→{5,4} 3→{6,4,1} 4→{2,1,5} 5→{1,3,6} 6→{4,2,5,1} 7→{1}`

A **weighted graph walk** (seeded `random.Random(20261102)`) generates the chord
sequence, biased by BFS distance toward each section's cadence anchor (target
degree forced on the final bar):

| Section | bars | anchor | generated progression |
|---|---|---|---|
| Intro | 4 | 1 → 5 | C · Em · C · G |
| Verse | 8 | 1 → 4 | C · Em · C · Am · F · G · C · F |
| Chorus | 8 | 4 → 1 | F · G · Am · G · Am · G · Am · C |
| Bridge | 4 | 6 → 5 | Am · G · Am · G |
| Outro | 4 | 4 → 1 | F · C · G · C |

The **voice-leading line** is the minimal-movement voice note between each
consecutive triad pair (computed from root-position voicings around C4), plus a
4-note triad arpeggio. This line *is* the raw melodic material.

## 3. Two-phase architecture

### Phase 1 — raw generative draft
Single voice (Piano), **no harmony**, **no quantize**. Per bar: voice-leading
note + arpeggio (root, 3rd, 5th, octave, 3rd) at rough 8th/16th slots with
±40-tick off-grid jitter and ±1-semitone chromatic jitter, velocity shaped by
phrase position. → `-phase1.mid`, own `validate()` gate (passed), provenance
`phase=1 quantized=false`.

- 168 raw events · mido readback: 166/168 off-grid (raw), 56 out-of-scale
  (unquantized float pitch — expected), 0 strong violations.

### Phase 2 — musicom rules post-process
1. **tiered pitch discipline** — `classify_weight` (strong on beats 1&3) →
   `ScaleQuantizer(root=60, scale="major").tiered_quantize` (strong = scale+chord,
   weak = scale), clamped to [48, 88].
2. **16th grid snap** (`GRID=120`), **dedup** on (start, pitch).
3. **voice-leading check** — break parallel perfect 5ths/octaves on adjacent onsets.
4. **tagged chromatic approach ornaments** on strong notes (lead only; lower
   chromatic neighbor, `.ornament="approach"`, `.resolve_pitch=target`).
5. Full 5-voice pop texture (all grid-locked, in-chord).

Voices + instruments (from `projects/Instruments/instrument_registry.py`):

| Voice | Instrument | GM program | channel | humanize_dna (timing/vel/layback/dur) |
|---|---|---|---|---|
| Lead | Piano | 1 | 0 | (None, 5.0, None, 0.015) |
| Harmony | Rhodes (Electric Piano 1) | 4 | 1 | (None, 5.0, None, 0.015) |
| Pad | Synth Pad (new age) | 88 | 2 | (None, 4.0, None, 0.01) |
| Bass | Electric Bass (finger) | 33 | 3 | (5.0, 4.0, 8.0, 0.01) |
| Drums | Drum Kit | ch9 | 9 | (2.0, 4.0, 0.0, 0.008) |

## 4. Grid audit (mido readback, all voices)

| layer | pitched | off-grid 16th | off-grid 8th | out-of-scale* | strong viol |
|---|---|---|---|---|---|
| phase1 | 168 | 166 | 166 | 56 | 0 |
| **perfect** | 663 | **0** | 19 | 19 | 0 |
| **humanized** | 663 | 624 | 626 | 19 | 0 |

\* the 19 out-of-scale notes in the mido readback are exactly the 19 **tagged**
chromatic approach ornaments on the Lead — the mido readback cannot see the
ornament tags; the authoritative tiered audit below counts them as *tagged* and
resolving. Perfect layer = 0 off-grid (compositional truth); humanized = 624
off-grid (proves the humanizer ran). off-grid-8th = 19 (the ornaments sit on
16th offbeats; the melody legitimately uses 16th-note subdivisions).

## 5. Tiered pitch-discipline audit (`workflows.pitch_audit.audit_voice`)

| voice | audible | strong_ok | weak_in_scale | tagged | resolving | non-resolving | untagged_out | strong_viol | passes |
|---|---|---|---|---|---|---|---|---|---|
| Lead | 187 | 56 | 112 | 19 | 19 | 0 | **0** | **0** | ✅ |
| Harmony | 168 | 168 | 0 | 0 | 0 | 0 | **0** | **0** | ✅ |
| Pad | 84 | 84 | 0 | 0 | 0 | 0 | **0** | **0** | ✅ |
| Bass | 224 | 56 | 168 | 0 | 0 | 0 | **0** | **0** | ✅ |

**all_pass = true** — 0 un-tagged out-of-scale, 0 non-resolving ornaments,
0 strong violations. Only the Lead carries chromatic ornaments (allowed);
Harmony/Pad/Bass are chromatic-free.

## 6. Humanization (style pop + per-instrument DNA, seeded)

- **hz_seed = 87653** (md5 of project name).
- style profile `profile_for_style("pop")`:
  timing_sigma_ms 4.0 · velocity_sigma 5.0 · layback_ms 2.0 · phrase_corr 0.25.
- Per-voice resolved profile + measured shift (1 tick = 1.059 ms @118 BPM):

| voice | timing_ms | vel_sigma | layback_ms | mean_abs_shift (ticks/ms) | max_shift | vel_delta |
|---|---|---|---|---|---|---|
| Lead (Piano) | 4.0 | 5.0 | 2.0 | 2.82 / 2.99 | 11 | 4.43 |
| Harmony (Rhodes) | 4.0 | 5.0 | 2.0 | 3.07 / 3.25 | 9 | 4.00 |
| Pad (Synth Pad) | 4.0 | 4.0 | 2.0 | 4.06 / 4.30 | 10 | 2.93 |
| Bass (Elec Bass) | 5.0 | 4.0 | 8.0 | 7.32 / 7.75 | 16 | 3.26 |
| Drums | 2.0 | 4.0 | 0.0 | 1.20 / 1.27 | 5 | 3.33 |

Drums anchor tightest (1.27 ms), bass lays back (~7.75 ms), lead breathes —
all within profile bounds. Forward-clamped, boundary-clamped, terminal landmark
pinned → `validate()` still passes on the humanized export.

## 7. Zero-drift

Both phase-1 (1 voice) and phase-2 (5 voices) export with all note-track lengths
identical:

- phase1: `[53760]` ✓
- perfect: `[53760, 53760, 53760, 53760, 53760]` ✓
- humanized: `[53760, 53760, 53760, 53760, 53760]` ✓

`validate()` passed for both phases and both dual-version exports.

## 8. Render + mastering

SoundFont `discover_soundfont()` → `FluidR3_GM.sf2`; FluidSynth `-ni -g 1.2 -R no -C no`.
All three MIDIs rendered → mastered to **target_for_style("pop") = −9.0 LUFS**
(`master()`: high-pass 30 Hz → glue → mono-safe stereo → LUFS normalize → −1 dBTP
limit) → Opus OGG (`libopus`, voip, 48k).

| render | LUFS | true-peak dBTP | silence ratio | RMS mean/max | wav bytes | ogg bytes |
|---|---|---|---|---|---|---|
| phase1 | −10.57 | −1.00 | 0.207 | 0.140 / 0.231 | 10,420,780 | 556,509 |
| perfect | −10.36 | −1.00 | 0.101 | 0.198 / 0.244 | 11,320,620 | 433,980 |
| humanized | −10.11 | −1.00 | 0.099 | 0.204 / 0.263 | 11,320,876 | 436,607 |

All three hit the −1.0 dBTP ceiling exactly; integrated LUFS lands ~1.1–1.6 dB
under the −9 target because the true-peak limiter is binding on this transient
pop texture (LUFS-normalize to −9 first, then TP-limit to −1 pulls loudness
down). Same behavior as prior nightly renders (e.g. 279 techno: target −10,
measured −10.86). Silence ratios healthy (no mid-track gaps — the 0.207 on the
sparse single-voice phase1 is inter-phrase space, not a defect).

## 9. Files

| file | bytes |
|---|---|
| MIDI/281-voice-leading-graph-pop-phase1.mid | 1,592 |
| MIDI/281-voice-leading-graph-pop-perfect.mid | 8,300 |
| MIDI/281-voice-leading-graph-pop-humanized.mid | 8,289 |
| Audio/281-voice-leading-graph-pop-phase1.ogg | 556,509 |
| Audio/281-voice-leading-graph-pop-perfect.ogg | 433,980 |
| Audio/281-voice-leading-graph-pop-humanized.ogg | 436,607 |

Provenance sidecars (`.provenance.json`) written per artifact; grid visualizations
in `Analysis/grid_visualization{,_phase1}.txt`; `Analysis/pitch_audit.json`,
`Analysis/verify_report.json`, `Analysis/compose_summary.json`.

## 10. Fixes applied

None required. Perfect layer hit 0 off-grid, tiered audit all-pass, zero-drift
on the first run. Selection honored the concrete-method cadence and the random
form draw (not verse-chorus).
