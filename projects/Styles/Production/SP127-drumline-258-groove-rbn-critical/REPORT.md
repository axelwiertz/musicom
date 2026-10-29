# SP-127 drumline (Ten-Model Drum Synthesizer + Funk Humaniser) - production report

- **Date (UTC):** 2026-10-29 (nightly autonomous production job)
- **Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP127-drumline-258-groove-rbn-critical/`
- **Status:** PASS - pitched-carrier pitch verify 110/110 (hit 1.000), harmonic energy 0.379, silence 0.96 %, LUFS -14.00, peak 0.7715.

---

## 1. Method + selection (registry source)

| Field | Value |
|---|---|
| Method | **SP-127** - Ten-Model Drum Synthesizer + Funk Humaniser (Teenage Engineering OP-XY drumline-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` - the **implemented** dict (NOT `methods_db.md` spec-only, NOT a stale `SP-001..SP-035` range) |
| Registered module | `sound.generators.drumline` -> `Drumline`, `DynamicFilter`, `MODELS` (10 models: kick / snare / rim / hat_closed / hat_open / conga_low / conga_high / shaker / clap / tom) |
| Registry entries at pick time | 72 implemented (SP-001 ... SP-134) |
| Already used last 7d (excluded) | SP-078, SP-094, SP-095, SP-101, SP-109, SP-119 |
| Baseline excluded | SP-001 |
| Already on this source | (none) |
| Eligible pool | 65 methods |

Selection record: `Production/.selection_cron.json`, `Production/select_job_20261029.py`.

Well-formed filter: 285 / 397 candidate MIDIs passed (normal tpb, sane note
lengths, >=2 note tracks or a program change, 2-600 s length). 284 meaningful
(>=3 distinct pitch classes).

## 2. Source composition

| Field | Value |
|---|---|
| Project | `Styles/Groove/258-groove-rbn-critical/` |
| Genre / key | Groove (funk-style 16th); **A natural minor** (pcs `{9,11,0,2,4,5,7}`) |
| Method of origin | 082 RBNCC (random Boolean network criticality, two-phase) |
| Tempo | 104.00 BPM, 480 tpb, type-1, 4/4 |
| Length | 55.38 s = 24 bars x 1920 ticks = 46080 ticks |
| Form | aba (A1 8 | B 8 | A2 8) |
| Voices | Clavi prog7 ch0 (138 notes, RBN lead) / Rhodes prog4 ch1 (192, off-beat comp) / Bass prog33 ch2 (96, groove) / Pad prog88 ch3 (32, B-section sustain) / Drums ch9 (512 hits: kick36 x72, snare38 x48, closed-hat42 x384, open-hat46 x8) |
| Chord plan | A1: i7 i7 VI7 VII7 | B: III7 VI7 iv7 v7 | A2: i7 i7 VI7 VII7 (all diatonic 7th chords: Am7 Fmaj7 G7 Cmaj7 Dm7 Em7) |

The selector's literal pick was the `-humanized.mid` twin; the production pass
uses its grid-locked `-perfect.mid` twin (the compositional truth), since the
humanized variant deliberately carries micro-timing jitter (see pre-flight).

## 3. Pre-flight rules-adherence gate - PASS on the perfect twin (no rework needed)

The source follows a **tiered** harmony discipline (its documented design):
strong beats (1 & 3) = in-scale AND in-chord; weak beats = in-scale (passing
tones allowed). The audit below honours that discipline (weak-beat in-scale
notes are counted as passing tones, not violations).

| Rule | humanized (selector pick) | perfect (production source) | verdict |
|---|---|---|---|
| 1. Grid sync (16th = 120 ticks) | 408 off-grid | **0 off-grid** | PASS |
| 2a. Harmony - in-scale | 0 out-of-scale | **0 out-of-scale** | PASS |
| 2b. Harmony - strong-beat chord tone | 0 strong violations | **0 strong violations** | PASS |
| 2c. weak-beat scale-only (passing tones) | 58 (allowed) | 57 (allowed) | PASS |
| 3. Zero-drift (equal track ends) | all 46080 | **all 46080** | PASS |

The 408 off-grid onsets in the humanized twin are the humanizer's intended
micro-timing jitter (max +-15 ticks); its grid-locked `-perfect.mid` twin is
0 off-grid, so the production pass uses `-perfect.mid` directly - no rework
required (the "rework" already exists as the dual-export twin). The 57
weak-beat scale-only notes are idiomatic passing tones, not out-of-key crud
(0 out-of-scale, 0 strong-beat chord violations).

## 4. Layer discipline (absolute - drum layer re-synthesised by drumline)

SP-127 is a **drum-only** synthesizer (10 unpitched percussion models - no
pitched/melodic models). Applied as an **absolute layer** on the drum/
percussion layer: all 512 of the source's GM drum hits are discarded and the
kit is re-synthesised from scratch by the 10 drumline models with the "funk"
humaniser. The A-minor harmonic/melodic layer (clavi / rhodes / bass / pad)
is carried by the FluidSynth SP-001 render of the pitched voices only (ch9
stripped) - the same carrier convention the SP-074 drum-machine pass used for
key/genre context.

```
A natural minor, 104 BPM, 480 tpb, 24 bars (46080 ticks)
 -> drumline 10 models (absolute drum layer, funk=0.35):
      kick 72 / snare 48 / hat_closed 384 / hat_open 8   (from source ch9, note->model)
      clap layered on 2&4 backbeat / shaker 8ths /
      conga_low "and of 2" / conga_high "and of 3" /
      rim "and of 4" ghost pickup / tom section-boundary fills (7/15/23)
 -> DynamicFilter (HPF 25 Hz + LPF 14 kHz + comp 0.45 + drive 0.12) glue on drum bus
 -> pitched carrier: ch9-stripped MIDI -> fluidsynth -ni -R0 -C0 -g1.2 (FluidR3_GM.sf2)
 -> mix: pitched bus x1.0 + drum bus x0.85 -> master(target -14 LUFS, -1 dBTP) LAST
 -> SP127-drumline-258-groove-rbn-critical.wav + .ogg (Opus 48k voip)
```

## 5. Parameters (full)

| param | value |
|---|---|
| sample_rate | 44100 |
| bpm / ppqn / meter | 104 / 480 / 4/4 |
| bars / ticks | 24 / 46080 |
| funk | 0.35 |
| dynamic filter | hp 25, lp 14000, comp 0.45, drive 0.12 |
| per-model (tone/decay/pitch/snap) | kick .55/.45/.30/.60 - snare .50/.40/.50/.70 - hat_closed .60/.30/.50/.60 - hat_open .60/.70/.50/.50 - clap .50/.40/.50/.60 - shaker .60/.50/.50/.40 - rim .50/.40/.60/.60 - conga_low .50/.50/.40/.50 - conga_high .50/.50/.60/.50 - tom .50/.50/.50/.50 |
| carrier | FluidSynth SP-001, FluidR3_GM.sf2, dry (-R 0 -C 0 -g 1.2) |
| master | target -14.0 LUFS (Groove), ceiling -1.0 dBTP |

## 6. Verification (all real numbers)

| check | value | verdict |
|---|---|---|
| Pitched-carrier pitch (FFT dom peak 50-1000 Hz vs A-minor pcs) | 110/110 windows (hit 1.000), mean harmonic energy 0.379 | **PASS** (>=0.60 hit, >=0.30 HE) |
| Silence ratio | 0.96 % (tail only) | PASS |
| RMS (whole) | 0.1517 | PASS |
| LUFS / true peak | -14.00 LUFS / -2.25 dBTP (ceiling, not target - dynamic kit) | PASS |
| Peak | 0.7715 | PASS |
| Drum envelope grid | closed-hat stem onset autocorr dominant period 580 ms ~= quarter-note accent cycle (16th = 144.2 ms not the dominant peak in this dense mixed kit) | NOTE |
| Zero-drift (source) | all 6 tracks 46080 | PASS |

Pitch verification is on the pitched carrier (FluidSynth A-minor texture) - the
only pitched content in this pass; the drumline layer is unpitched percussion,
verified for rhythm/spectral sanity (0.96 % silence, no clipping, real onsets
per-stem) rather than harmonic energy.

## 7. Files

| file | size (bytes) |
|---|---|
| SP127-drumline-258-groove-rbn-critical.wav | 9769868 |
| SP127-drumline-258-groove-rbn-critical.ogg | 361969 |
| pitched_carrier_sp001.wav | 10137900 |
| dry_full_mix_sp001_reference.wav | 10223404 |
| MIDI/source_perfect.mid | 7557 |
| MIDI/source_humanized.mid | 7350 |
| MIDI/pitched_carrier.mid | 3702 |
| Audio/stems/drum_{kick,snare,rim,hat_closed,hat_open,conga_low,conga_high,shaker,clap,tom}.wav | 10 x 9769868 |
| Audio/stems/track{00_Clavi,01_Electric_Piano_1,02_Electric_Bass_finger,03_Pad_1_new_age}.wav | 4 pitched stems |
| Analysis/render_stats.json | - |
| provenance.json | - |

Pitched stem labels use GM program names (not `add_voice` names): Clavi /
Electric_Piano_1 / Electric_Bass_finger / Pad_1_new_age (verified against the
per-voice-per-section stem-label table).

## 8. Fixes applied

- **Pre-flight**: no composition rework needed. The selector's humanized pick
  fails rule 1 by design (408 off-grid = humanizer micro-timing); its
  grid-locked `-perfect.mid` twin (the dual-export contract) passes 0/0/0 and
  was used as the production source.
- **Audit discipline**: the initial naive "every note must be a chord tone"
  audit reported 57 "out-of-chord" notes; these are the source's documented
  weak-beat in-scale passing tones (0 strong-beat chord violations, 0
  out-of-scale), so the audit was corrected to the source's tiered discipline
  (strong beats in-chord, weak beats in-scale).

## 9. Chat summary (short)

SP-127 drumline on Groove/258-groove-rbn-critical (A-minor funk, 104 BPM).
Pre-flight PASS (perfect twin 0 off-grid / 0 out-scale / 0 strong-out-chord,
zero-drift). 10-model drum synth (funk 0.35) replaces the drum layer absolutely;
A-minor texture carried by FluidSynth. Pitch verify PASS (1.000 / HE 0.379),
silence 0.96 %, LUFS -14.00. Full record above.
