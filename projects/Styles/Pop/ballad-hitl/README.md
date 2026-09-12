# Pop Ballad — HITL Project

Human-in-the-loop evolution project for a dramatic pop ballad.

## Concept

- **Genre**: Pop ballad (minor-aeolian drama)
- **Key**: D (aeolian) — i–VI–III–VII harmonic regions
- **Tempo**: 72 BPM (slow ballad)
- **Form**: Intro(4) → Verse(8) → Chorus(8) → Bridge(4) → Outro(4) = 28 bars, ~93 s
- **Voices**: Lead (Flute), Pad (Piano), Bass (Double Bass), Arp (Clarinet), Drums (Drum Kit)

## Phase 1 — Composition (MIDI)

Framework via **Path C middle-out** (`workflows/paths.py`), then per-part
method swaps on the SAME framework + base patterns:

| Part | Bars | Comp method | Effect |
|---|---|---|---|
| Framework | all | 001 Skeleton-First + 012 Euclidean bass + 018 Schillinger density | spine |
| Intro | 0-4 | 001 skeleton | sparse held tones |
| Verse | 4-12 | 004 Prosodic Narrative | lyrical contour |
| Chorus | 12-20 | 011 Voice-Leading Graph | nearest-chord leaps, octave lift |
| Bridge | 20-24 | 023 Tendency Masking | tension walk, wide intervals |
| Outro | 24-28 | 013 Inversion/Retrograde | retrograde motif, resolve |

Per-section harmonic regions (ballad arc): Intro i-VI, Verse full aeolian
cycle, Chorus lift on III-VII-i-VI, Bridge peak on VII, Outro resolve to i.

Zero-drift validated (`validate()` gate), provenance sidecar, grid viz.

## Phase 2 — Production (Audio)

Different production method per VOICE (on stems) AND per SECTION (on bus):

| Voice (by role/index) | SP method |
|---|---|
| Lead | SP-032 FDN reverb wash (wet .3) |
| Pad | SP-020 SVF lowpass 4.5 kHz |
| Bass | SP-020 SVF lowpass 700 Hz (sub body) |
| Arp | SP-019 Chebyshev waveshape (drive 1.5) |
| Drums | SP-008 multiband compressor (punch) |

Stems route **by role and track index**, not by GM name — the palette
rotates per HITL round, so a name-based router stops matching.

| Section | SP method |
|---|---|
| Intro | SP-020 lowpass 1200 Hz (muffled build-in) |
| Verse | dry (lyric clarity) |
| Chorus | SP-021 stereo widen 1.35× |
| Bridge | SP-032 FDN wash (size .85, wet .4) |
| Outro | SP-020 lowpass 800 Hz + fade to 0 |

Master: `normalize_to_lufs(-14)` → `Limiter(-1 dB)` LAST.

## Verification

```
LUFS -14.01  peak 0.891  silence 3.2%
```

- MIDI: `MIDI/pop-ballad-hitl.mid` (3292 B, zero-drift)
- Audio: `Audio/pop-ballad-hitl.wav` (16.5 MB) + `.ogg` (670 KB)
- Stems: `Audio/stems/track*_*.wav`
- Grid: `Analysis/grid_phase1.txt`

## Phase 3 — HITL evolution rounds (human pick)

`Scripts/phase3_hitl.py` drives the engine's HITL machinery
(`workflows.hitl.record_pick`) over **this ballad's own framework** — the
generic `run_hitl_round` builds a plain I–V–vi–IV pop anchor, which would
discard the per-section regions and per-part methods from phase 1.

### Two rules that keep rounds from sounding identical

1. **Instrumentation rotates per round.** `PALETTES` defines four
   ballad-idiomatic line-ups; round *r* uses
   `PALETTE_ORDER[r % 4]`, so consecutive rounds are heard in fresh
   instrumentation instead of the same four tracks.

   | palette | Lead | Pad | Bass | Arp | Drums |
   |---|---|---|---|---|---|
   | classic | Violin | Piano | Cello | Viola | Drum Kit |
   | noir | Alto Sax | Piano | Double Bass | Dulcimer | Drum Kit |
   | chamber | Oboe | Church Organ | Bassoon | Clarinet | Timpani |
   | folk | Acoustic Guitar | Dulcimer | Double Bass | Kalimba | Drum Kit |

   Every instrument is **range-verified against the register its role
   writes** (`tests/test_ballad_palette.py`). The original default wrote the
   texture at 50–60, below the clarinet's 52 floor — a real out-of-range bug.

2. **Candidates vary different stems.** Within a round each slot mutates a
   distinct dimension instead of four takes on the bass:

   | slot | role | what changes |
   |---|---|---|
   | 0 | incumbent | control — previous winner / current palette |
   | 1 | anchor | bass groove density × offset |
   | 2 | lead | lead composition method (per-section swap) |
   | 3 | texture+bed | arp rate × spread, pad behaviour × drum level |

### Fair audition

Excerpts are **loudness-normalized** (`loudnorm I=-16`) before delivery. A
soft palette (sax/oboe) otherwise lands ~7 dB under a bright one (violin),
so the judge would pick the loudest candidate rather than the best.

### Search space

A `VariantSpec` (phase1_compose) controls every evolvable stem. Fitness is
**composite** — averaged over Lead/Bass/Arp, not the bass alone, since
scoring only the anchor made distinct tracks score identically.

Macro-structure (form, harmony, section roles) is frozen, per plan advice
#5: evolve phrases/anchors, not whole songs.

```bash
PY=/opt/data/micromamba/envs/musicom/bin/python
$PY Scripts/phase3_hitl.py                        # round 0
$PY Scripts/phase3_hitl.py --round 1 --from-round 0   # mutate round-0 winner
$PY Scripts/phase3_hitl.py --round 0 --pick 2     # record the human pick
```

Artifacts per round: `HITL/roundN/candidates/cand*.{mid,ogg}`,
`HITL/roundN/round.json`, and on a pick `HITL/roundN/evolution.json` +
provenance sidecar on the winner.

### Engine fixes shipped with phase 3

- **Mode-aware root lookup** (`rules/harmony.progression_roots`) replaced a
  bug duplicated in **four** places (`workflows/paths.py`,
  `workflows/hitl.py`, `workflows/evolution.py`, this project's phase 1).
  The old code did `MAJOR_DEGREES.index(deg.upper())`, collapsing every
  uppercase minor-mode degree (VI/III/VII) and every lowercase major-mode
  degree (ii/iii/vi/vii) onto index 0 — `i–VI–III–VII` in D gave
  `[38, 38, 38, 38]`. Now `[38, 46, 41, 48]` = D–B♭–F–C.
- **`record_pick` preserves candidate extras** (`spec`, `role`, per-stem
  fitness) into `evolution.json`, so a richer search space survives into the
  next round instead of silently resetting.
- **`build_framework(voices=...)`** accepts a custom voice stack, so a
  style-appropriate palette can be swapped in without forking the framework.
- **Phase 2 routes stems by role/index**, not by hardcoded GM name — the
  name-based router stopped matching the moment the palette changed.

Regression-locked by `tests/test_harmony_degrees.py` (16 tests) and
`tests/test_ballad_palette.py` (10 tests).

## HITL hook

Round 0 is rendered and awaiting the human pick. Reply with a candidate
number (0–3); the agent records it via `phase3_hitl.py --pick N`, writes
`evolution.json` + provenance, and spawns round 1 mutated around the winner
on the next palette.
