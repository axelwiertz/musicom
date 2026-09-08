# SP-037 Sub-Harmonic Generator — Cuban Trova Research (003-cuban-son-laboratory v8)

**Date (UTC):** 2026-09-08
**Job:** random-style production pass (SP methods) — LAYER-ALIGNED (2026-09-08 cron)
**Output root:** `/opt/data/projects/Styles/Production/SP037-subharmonic-cuban-trova/`

## 1. Method + selection (registry source)

| Field | Value |
|---|---|
| Method | **SP-037** — Pitch-Tracked 3-Band Sub-Harmonic Generator (Penteo 8 Synthesized LFE-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` (implemented-methods dict — NOT methods_db.md spec table). Pool = **12 implemented**: SP-001/011/021/024/026/028/032/033/034/035/036/037 |
| Registered module | `sound.effects.subharmonic` (`SubHarmonicGenerator`, `SubBand`, `pitch_frame`) |
| Recent-7d exclusion (dir mtimes ≥ 2026-09-01) | SP-011 (09-04), SP-024 (09-01), SP-026 (09-06), SP-032 (09-02), SP-033 (09-05), SP-034 (09-03), SP-035 (09-07) → excluded |
| Eligible pool | **SP-001, SP-021, SP-028, SP-036, SP-037** → uniform random pick landed on **SP-037** |
| Selection record | `/opt/data/select_job_20260908.py` + `/opt/data/select_job_20260908.json`, mirrored in `Production/.selection.txt` (job appends) |
| SP-037 in registry | `"sound.effects.subharmonic": "Pitch-Tracked 3-Band Sub-Harmonic Generator (Penteo 8 Synthesized LFE-style)"` |

**NOTE on registry scope:** SP-035 in this registry is *shimmer reverb* (not the old
GENDYN dynamic-stochastic method), so the GENDYN noise-fix pattern does not apply.
SP-037 is a new registry entry — first production run of this method.

## 2. Source composition

| Field | Value |
|---|---|
| Project | `Styles/Cuban/001-cuban-trova-research/MIDI/` |
| MIDI | `cuban_001-cuban-trova-research-v8.mid` |
| Provenance | Cuban trova / son research, GM programs: Flute (73) ch0, Acoustic Guitar nylon (24) ch1, Electric Bass finger (33) ch2, Percussion ch9 |
| Tempo | 96 BPM (625000 µs/beat), 4/4, 480 tpb |
| Form | 6 bars × 4 beats = 24 beats = **15.00 s** score; all voices quarter-note dense (24 notes/voice) |
| Voices | Flute lead (24 notes), Guitar (24), Bass (24), Drums ch9 (24) — 96 total |
| Length (render) | dry full mix 18.00 s (GM release tails) |

## 3. Layer discipline (absolute)

SP-037 is an **effect method on rendered audio** → two-stage pipeline; the
sub-harmonic layer is applied to **ALL pitched voices** (absolute layer —
not per-voice opt-in). FluidSynth internal reverb/chorus forced OFF
(`-o synth.reverb.active=no -o synth.chorus.active=no`) so the synthesized
LFE sub is the sole low-frequency treatment:

```
cuban_001-cuban-trova-research-v8.mid
  → fluidsynth -ni -g 1.2 -r 44100 (reverb/chorus OFF) → dry_full_mix.wav
  → per-voice FX-off stems (4, time-aligned): track00_Flute,
    track01_Acoustic_Guitar_nylon, track02_Electric_Bass_finger,
    track03_Acoustic_Grand_Piano (= ch9 percussion — GM-name quirk, see §6)
  → SubHarmonicGenerator.process() on EVERY pitched stem (role params below)
    + one full-mix sub pass at moderate depth (glue)
  → mix = dry×0.9 + Σ(stem_sub × wet_gain) + full_sub×0.35
  → peak normalize −1 dBFS → SP037-subharmonic-cuban-trova.wav
  → .ogg (Opus 48k voip)
```

Per-voice sub params (input band one octave above output band; 3-band gating
sub 20–60 / low 60–120 / mid 120–240 Hz):

| Stem | Role | depth | add_fifth | wet_gain | Logic |
|---|---|---|---|---|---|
| track00_Flute | melody | 0.55 | no | 0.9 | flute 40–240 Hz content weak → little sub, low-body only |
| track01_Acoustic_Guitar_nylon | strum | 0.70 | no | 1.0 | mid-band body thickens |
| track02_Electric_Bass_finger | bass | 1.00 | **yes** | 1.2 | full sub-octave + 3f0/4 fifth (POG-style); bass is the primary sub target |
| track03_Acoustic_Grand_Piano | (ch9 drums) | — | — | — | percussion passes dry in the base mix |
| full mix (glue) | all | 0.45 | no | 0.35 | coherent low end under the whole son |

## 4. Pitch verification (mandatory)

| Metric | Dry full mix | SP-037 mix |
|---|---|---|
| Median FFT dominant peak (50–1000 Hz, 0.5 s hops) | 220.0 Hz (32 frames) | 220.0 Hz (32 frames) |
| Per-frame pitch track (autocorrelation, 40–240 Hz) | bass/guitar content | unchanged, sub follows f0 |

The median *dominant* peak is unchanged because the sub content lives
20–120 Hz — largely below the 50–1000 Hz verification window. The correct
proof of "synthesized sub, not noise" is the **low-band energy comparison
dry vs mix** (below), since noise would lift every band equally while a real
sub-octave generator lifts the sub bands disproportionately.

| Band (Hz) | Dry energy | SP-037 mix energy | Ratio | Interpretation |
|---|---|---|---|---|
| 20–60 | 13,423,744 | 133,095,578 | **×9.91** | synthesized sub-octave content (LFE band) |
| 60–120 | 53,010,433 | 162,286,786 | **×3.06** | sub + low band |
| 120–240 | 486,693,607 | 1,261,741,436 | ×2.59 | mid-band harmonic gain |
| 500–2000 (presence) | 254,560,185 | 658,464,974 | ×2.59 | normalization-lift reference |

Presence band ×2.59 is the global peak-normalization lift (dry RMS 0.095 →
mix RMS 0.156 after norm). The sub bands exceed that lift by ×3.8 (20–60) and
×1.2 (60–120) → **genuine synthesized sub energy, not broadband noise**.
Harmonic structure preserved (dominant peaks unchanged); no 0 Hz/unpitched
frames introduced. Sub oscillator is phase-continuous per module design
(click-free joins), DC-free.

## 5. Silence / RMS profile

- **Silence ratio: 0.147** (14.7 %) — well under the 30 % suspect threshold.
- Per-second RMS map (18 s): `0.185 0.174 0.171 0.159 0.166 0.184 0.176 0.169 0.160 0.166 0.181 0.171 0.169 0.160 0.167 0.026 0.000 0.000 0.000`
  - Seconds 0–14: full son groove, steady 0.16–0.19 RMS.
  - Seconds 15–17: legitimate decay — score ends at 15.0 s; 0.026 tail then GM release fade to digital silence. **No mid-track gaps.**

## 6. Fixes / notes

- **`RenderPipeline.render_stems()` cannot force FluidSynth FX off** (its
  renderer call omits `-o synth.*.active=no`). Layer discipline requires
  internal reverb/chorus OFF → stems rendered with the pipeline's own
  FX-off fluidsynth calls (identical per-track single-MIDI extraction logic,
  tempo track preserved). See `produce_sp037_cuban.py`.
- **Stem-label quirk (known):** the ch9 percussion track is labeled
  `track03_Acoustic_Grand_Piano` (GM program 0 fallback) — matching the
  documented RenderPipeline behavior. It is the drum stem; passed dry.
- **Flute sub gate:** flute lead has almost no 40–240 Hz input energy
  (pitch-tracked f0 median 117.5 Hz with weak periodicity) → its sub output
  is near-silent (peak 0.0003). By design of the 3-band gate; the bass +
  guitar + full-mix passes carry the LFE content.
- **SP-037 adapter not wired** in `workflows.musicom_workflow.produce()`
  (only SP-001/SP-011 are) → called the registered module API directly
  (`SubHarmonicGenerator.process`), per job instructions.
- Rendering script: `produce_sp037_cuban.py` (kept in this dir for replay).

## 7. Files + sizes

| File | Size | Note |
|---|---|---|
| `SP037-subharmonic-cuban-trova.wav` | 1.6 MB | final mix, −1 dBFS, 18.0 s |
| `SP037-subharmonic-cuban-trova.ogg` | 124 KB | Opus 48k voip (Telegram-ready) |
| `dry_full_mix.wav` | 3.1 MB | FX-off SP-001 reference (A/B) |
| `provenance.json` | 2.1 KB | full params + verification numbers |
| `Analysis_grid.txt` | 465 B | onset-density grid (6 bars × 4 beats, all voices) |
| `stems_dry/track00_Flute.wav` … `track03_*.wav` | 2.9–3.1 MB each | 4 FX-off per-voice stems for DAW remix |

MIDI for the render is the source composition itself
(`cuban_001-cuban-trova-research-v8.mid`) — production pass does not alter the
score, so the source `.mid` is the DAW artifact (per dual-mode convention).

## 8. Listen for

- The son's bass line doubled an octave down with a synthesized fifth — clean
  sine sub, not a pitch-shifted copy (no comb artifacts).
- Guitar strum mid-band body thickened (60–120/120–240 bands).
- Drums untouched — the groove's attack stays dry on top of the new low end.
- Compare `dry_full_mix.wav` (thin, 96-BPM acoustic) vs the SP-037 mix
  (bottom-heavy, club-LFE body) — the A/B gap is the whole method.
