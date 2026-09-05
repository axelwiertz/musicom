# SP-033 Supersaw Swarm — Bossa Nova Gentle (bossa_nova_gentle.mid)

**Date:** 2026-09-05 (random-style nightly production pass)
**Job:** `random-style production job (SP methods) — LAYER-ALIGNED (2026-09-05)`

## Selection

| Item | Value |
|---|---|
| Production method | **SP-033 — Detuned Saw Swarm + Scale/Chord Quantize + Morph Pad** |
| Registry source | `workflows.musicom_workflow.SP_METHODS` (10 implemented entries; NOT methods_db.md spec-only range). Registered module `sound.synthesis.supersaw_swarm` (`SupersawSwarm`, NI SuperStarSaw-style: two independent 16-osc detuned-saw swarms + harmony quantizer + morph pad). |
| Source composition | `/opt/data/projects/Styles/BossaNova/gentle/v1/bossa_nova_gentle.mid` |
| Composition style | Bossa-nova gentle loop, 100 BPM, 32 bars (2×16: sections A/B) = **76.9 s**. 4 voices: nylon guitar (prog 25, ch0, 768 notes), electric bass (33, ch1, 160), flute (74, ch2, 128), drums (ch9, GM). Source methods 011 (Euclidean rhythm) + 002 (Markov) + 026. |
| Layer discipline | **Absolute layer**: supersaw swarm replaces the timbre layer for ALL pitched voices — every pitched MIDI note (544 across guitar/bass/flute) is synthesized by `SupersawSwarm.render_note()`; percussion rides the GM kit (FluidSynth, internal reverb/chorus OFF) as the rhythmic anchor. Per-voice stems shipped for DAW remix. |
| Method pool | Registry = SP-001/011/021/024/026/028/032/033/034/035. Last-7-day exclusion (dir mtimes ≥ 2026-08-29): SP-001, SP-011, SP-021, SP-024, SP-026, SP-028, SP-032, SP-034, SP-035 → available **SP-033** (only method not run in the last 7 days) → deterministic pick. |
| Selection script | `/opt/data/select_job_20260905.py` → result `/opt/data/select_job_20260905.json`, mirror in `Production/.selection.txt`. 218 phase-2 candidates (phase-1 rules drafts excluded); random source pick landed on BossaNova gentle. |

## Pipeline

```
bossa_nova_gentle.mid (76.9 s, 544 pitched notes + drums)
  → mido parse (reading only) → per-note SupersawSwarm.render_note()
     voice-role parameterized (see table) → additive stereo mix (0.25 s
     attack / 0.40 s release note envelopes, velocity-scaled)
  → global 0.05 s fades → loudness normalize (RMS −20 dBFS) → −1 dBFS peak
  → SP033-supersaw-bossa-gentle.wav → .ogg (Opus 48k voip)
  + 3 per-voice stems (same synth, per-voice buses, −1.5 dBFS)
  + SP-001 FluidSynth reference render (FX off) for A/B comparison
```

- SoundFont: `discover_soundfont()` → **FluidR3_GM.sf2** (not the TimGM6mb fallback) — used for the drum kit + the SP-001 reference render only.
- The SP-033 adapter is NOT wired in `workflows.musicom_workflow.produce()` (only SP-001/SP-011 are) → called the registered module API directly (`SupersawSwarm.render_note`), per job instructions.

## Parameters

### Voice-role supersaw map

| Voice | spread_cents | drift | harmony | harmony_root | swarm2 | brightness | bus gain | musical logic |
|---|---|---|---|---|---|---|---|---|
| Bass (33, ch1) | 6.0 | 0.08 | — (pure detune) | — | off (1 swarm) | 0.55 | 1.00 | narrow stack keeps low end tight; no 5th-above swarm to avoid muddy sub beat; dimmer tilt tames aliasing on A1 |
| Guitar (25, ch0) | 14.0 | 0.15 | `major` | (pitch−60) mod 12 | on | 0.85 | 0.55 | C-major chord tones: 14¢ spread lands the whole 16-osc swarm on the chord, classic analog pad; 2nd swarm adds movement |
| Flute lead (74, ch2) | 30.0 | 0.35 | `major` | (pitch−60) mod 12 | on | 0.95 | 0.60 | wide drift = singing "breath"; harmony quantize keeps the 128-note C-major melody inside the scale; brightest voice |

Sizing choice: bossa gentle needs a warm analog-pad wash, not aggressive
supersaw — moderate spreads (6–30 ¢), harmony locked to the source's C-major
collection, per-oscillator drift for the "breathing" chorus life, and the GM
kit (shaker + rimstick + kick) left dry so the bossa groove stays readable
through the sustained swarm bed. Source chord roots: C (60), B (59), C, C —
bass (35/36 = C1/B0) alternates root only, so harmony_root is computed from
the played pitch class, keeping every oscillator inside the source scale.

## Checks & verification

| Check | Result | Verdict |
|---|---|---|
| Silence ratio (full mix) | **0.0549 (5.5 %)** | PASS — no mid-track gaps (only inter-note space + final tail) |
| SP-001 reference silence | 0.0652 (6.5 %), 82.25 s (GM tails) | PASS |
| RMS profile | per-second RMS min 0.026 (≈ −31.7 dBFS) at bar 0 (fade-in region), max 0.24; sustained 0.08–0.22 across the piece | PASS — no dead zones |
| WAV / OGG size | 13 565 200 B / 712 176 B | PASS — non-empty, sane |
| **Pitch verification** | dominant-peak hit rate **1.000** (153/153 windows), harmonic energy (8 harmonics of lowest fund) mean **0.503** | **PASS** |

Pitch method: FFT dominant peak per 0.5 s window in the 40–2000 Hz band,
±4 % tolerance vs every active MIDI fundamental OR its 2nd/3rd harmonic.
Supersaw stacks place most spectral energy on harmonics (16 detuned saws),
so harmonic-ladder tolerance is required; octave-sub tolerance was removed
because the bass A1 (55 Hz) sits inside the band — a sub-octave match would
mask octave errors. **153/153 windows hit** — every window's dominant peak
matches an active note (fundamental, 2nd, or 3rd partial); harmonic energy
0.503 ≥ 0.30 threshold confirms tonal content (a noise pass scores single
digits). Lowest active notes across the piece: MIDI 35 (B0) and 36 (C1) —
both detected. Full JSON: `Analysis/pitch_verification.json`,
`Analysis/render_stats.json`.

## Artifacts

| Artifact | Path | Size |
|---|---|---|
| Full mix WAV | `Audio/SP033-supersaw-bossa-gentle.wav` | 13 565 200 B (76.90 s) |
| Full mix OGG | `Audio/SP033-supersaw-bossa-gentle.ogg` | 712 176 B (76.91 s, Opus 48k) |
| SP-001 reference (A/B) | `dry_full_mix_sp001_reference.wav` | ~14 MB (82.25 s incl. GM tails) |
| Source MIDI (copy) | `MIDI/bossa_nova_gentle.mid` | 11 597 B |
| Provenance | `provenance.json` | — |
| Report | `REPORT.md` | — |

Stems (per-voice buses from the same supersaw synth, time-aligned):

| Stem | Path | Size |
|---|---|---|
| Nylon guitar (25) | `Audio/stems/track00_Acoustic_Guitar_nylon.wav` | 13 565 200 B |
| Bass (33) | `Audio/stems/track01_Electric_Bass_finger.wav` | 13 565 200 B |
| Flute (74 → GM stem-name quirk) | `Audio/stems/track02_Recorder.wav` | 13 565 200 B |

Note: stems are full-length (76.9 s) per the time-aligned stem convention;
each stem is peak-normalized to −1.5 dBFS relative to its own bus. Drum bus
is not shipped as a separate stem (GM kit, present in the SP-001 reference).

## Notes & fixes applied

1. **Method pool math**: only SP-033 was available after the 7-day exclusion
   (9 of 10 methods ran 2026-08-29..09-04) — pick was deterministic, no
   `random.choice` needed. Registry-based selection JSON +
   `Production/.selection.txt` updated.
2. **First run bug**: `parse_notes` collected every non-track-0 track, and the
   drum track's note-ons fell through to a `KeyError: 4` (no synth for the
   percussion track). Fixed by filtering parsed notes to the three synth
   voices (`e['track'] in synths`) before rendering — drums intentionally
   excluded from the swarm layer.
3. **Stem naming quirk** (documented in the skill): GM program 74 renders its
   GM name as `Recorder` (SF2 instrument-name mapping), so the flute stem is
   `track02_Recorder.wav` — GM-name convention, not a bug.
4. **Full-note render**: sustain is the full MIDI note duration (end−start);
   chord changes overlap (guitar 8ths are ~1 beat at 100 BPM), so the swarm
   bed is continuous — no Karplus-style decay gaps (SP-011 silent-render
   lesson). Attack/release envelopes (0.25 s / 0.40 s) prevent clicks between
   adjacent notes and give the pad a soft analog swell.
5. **Loudness**: raw additive mix of 32 detuned saws per note hits ~0.3–0.5
   peak per note; the full mix was RMS-normalized to −20 dBFS then peak-capped
   at −1 dBFS (16-bit headroom). Resulting per-second RMS 0.08–0.22.
6. **Runtime**: 544 rendered notes over a 76.9 s score — vectorized per-osc
   saw synthesis is ~45× realtime per note; whole pass incl. FluidSynth
   reference finished well inside the job budget. No timing drift possible
   (event times are absolute seconds derived from the MIDI tick map).
7. Precedent: SP-034 BBD pass (2026-09-03) and SP-032 FDN pass (2026-09-02) —
   same absolute-layer structure (FX-off dry capture, per-voice stems,
   verification gate). SP-033 differs by being a *synthesis* method: the
   pitched layer is not a dry capture processed by an effect but is rebuilt
   note-by-note by the registered synth module, which is the correct
   layer-aligned application for a timbre-replacement method.
