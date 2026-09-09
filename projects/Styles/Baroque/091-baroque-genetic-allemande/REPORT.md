# 091-baroque-genetic-allemande — REPORT

**Date**: 2026-09-09 (nightly composition cron)
**Style**: Baroque (allemande — medium-slow 4/4 court dance, 8th-note flow)
**Layer**: concrete (6-of-7 concrete cadence; prior abstract runs 085/087/089/090)
**Method**: 003 Genetic Genome Selection (`GeneticGenerator`, generators/genetic.py)
  — Phase-2 harmony scaffold wired to 011 TonalNetworkGenerator role walk
**Key**: D aeolian / D minor (harmonic-minor C# + dorian B borrowings)
**BPM**: 92 · 4/4 · 480 TPB (bar = 1920, 8th = 240, 16th = 120)
**Form**: 6 sections × 4 bars = 24 bars —
  Intro | AllemandeA | AllemandeB | Lift | AllemandeA2 | Outro
  (section = 7680 ticks, total = 46080 ticks)

## Method (concrete layer)

Genetic Genome Selection (method 003): a population of binary genomes is
evolved toward a Bach-style fitness. Each genome decodes (library
`binary_to_unit`) to 48 raw events — 6-bit pitch interval, 4-bit onset,
4-bit duration, 4-bit velocity per event. The fitness rewards **conjunct
motion** (stepwise interval streaks score super-linearly, small leaps score,
large leaps penalized), so selection pressure pushes the raw draft toward
Baroque-idiomatic lines.

- Population 24, genome 864 bits (48 events × 18 bits), 6 generations,
  seed 20260909
- Best fitness 61 (raw random genomes score ~10-20; unguided `pitch % 24`
  leaps penalized)
- Raw draft = 48 events, off-grid fingerprint: 282/282 onsets off the 16th
  grid in phase 1 (unquantized by design), pitch intervals unconstrained
- Phase-2 harmony scaffold: `TonalNetworkGenerator` (method 011) role walk
  (tonic/dominant/subdominant/mediant/pre_dominant/borrow), 24 roles seeded
  the same way, realized **diatonically in D minor** (see fixes)

## Two-phase architecture

| Phase | Artifact | Content |
|---|---|---|
| 1 | `MIDI/091-baroque-genetic-allemande-phase1.mid` | Raw genetic draft: single violin voice, 48 events per section, unquantized onsets (off-grid fingerprint), no harmony/bass/drums |
| 2 | `MIDI/091-baroque-genetic-allemande.mid` | 16th-grid locked (120 @ 480 TPB), D-minor scale snap + chord-tone quantize per global bar, voice-leading check/correction, full 7-voice Baroque texture |

Both phases passed their own zero-drift `validate()` gate
(phase-1: OK; phase-2: OK).

## Progression (method-011 role walk, 24 bars — diatonic D-minor realization)

Walk roles (seeded 20260909):
`i i i bVII i iv V i i III iv ii iv V i V i i III iv ii V i III`

Bar-by-bar chords (D minor reading):
| bars | chord |
|---|---|
| 1-3  | Dm (i) |
| 4    | C (bVII) |
| 5    | Dm (i) |
| 6    | Gm (iv) |
| 7    | A (V) |
| 8-9  | Dm (i) |
| 10   | F (III) |
| 11   | Em (ii) |
| 12   | Gm (iv) |
| 13   | Em (ii) |
| 14   | A (V) |
| 15   | Dm (i) |
| 16   | A (V) |
| 17-18| Dm (i) |
| 19   | F (III) |
| 20   | Gm (iv) |
| 21   | Em (ii) |
| 22   | A (V) |
| 23   | Dm (i) |
| 24   | F (III) |

Cadence logic: V→i closes bars 7→8, 14→15, 16→17, 22→23; the final
bar ends on III (F) — a half-cadence-ish Baroque "lift" into the repeat.

## Voices (instrument_registry)

| Voice | Instrument | GM | Register | Role |
|---|---|---|---|---|
| Lead | Violin | 40 | 60–88 | genetic raw draft, evolved conjunct line |
| Oboe | Oboe | 68 | 72–88 | answering 8th-note counterline (beats 2 & 4) |
| Cello | Cello | 42 | 36–62 | sustained whole-bar root-position triad shell |
| Piano | Acoustic Grand Piano | 1 | 60–84 | continuo-style 16th arpeggio rolls |
| Viola | Viola | 41 | 48–67 | sustained inner-harmony chord tone |
| Bass | Double Bass | 43 | 33–52 | walking 8th roots + quarter pulse, 16th push in Lift |
| Drums | Drum Kit | ch9 | — | kick 1&3, snare 2&4, 8th/16th hats, claps in B sections |

## Verification (real numbers)

### Grid audit (phase-2 MIDI, mido read-only) — contract: 16th grid (120)
| Voice | Notes | Off-grid (16th) | Off-grid (8th)* |
|---|---|---|---|
| Lead | 163 | 0 | 55 |
| Oboe | 96 | 0 | 0 |
| Cello | 66 | 0 | 0 |
| Piano | 384 | 0 | 192 |
| Viola | 24 | 0 | 0 |
| Bass | 160 | 0 | 3 |
| Drums | 328 | 0 | 64 |
| **Total** | **1221** | **0** | 314 |

\* 8th off-counts are expected: 16th subdivisions legitimately fall between
8th slots. The mandatory rule is 16th-grid lock — **0 off-grid** on the
16th grid for every voice.

Phase-1 raw fingerprint: **282/282 onsets off the 16th grid** — confirms the
raw genetic draft is NOT grid-locked (two-phase separation evidence).

### Harmony audit (phase-2, every pitched voice)
| Voice | Out-of-scale | Out-of-chord |
|---|---|---|
| Lead | 0 | 0 |
| Oboe | 0 | 0 |
| Cello | 0 | 0 |
| Piano | 0 | 0 |
| Viola | 0 | 0 |
| Bass | 0 | 0 |

Scale family: D aeolian {2,4,5,7,9,10,0} + harmonic-minor C# (1) + dorian B
(11) = {0,1,2,4,5,7,9,10,11}. Chords: triad scaffold from the role walk
(i/iv/ii minor, V/III/bVII major). **0 out-of-scale, 0 out-of-chord.**

### Zero-drift status
- Phase 1: all tracks end 46080, drift 0 (OK)
- Phase 2: all 7 tracks end 46080, drift 0 (OK — all cells carry the
  terminal landmark at SECTION_TICKS)

### Silence / RMS profile (rendered WAV, 65.28 s @ 44.1 kHz)
- Peak: 0.638 (≈ −3.9 dBFS)
- Silence ratio (|x| < 0.001): 4.13% — only the final 2 s tail (64-65 s);
  mid-track gaps: none (all 64 active seconds RMS 0.050–0.120)
- Verdict: PASS (no mid-track silence; the 30% threshold is far clear)

## Files

| Artifact | Path | Bytes |
|---|---|---|
| Phase-1 MIDI | `MIDI/091-baroque-genetic-allemande-phase1.mid` | 2244 |
| Phase-2 MIDI | `MIDI/091-baroque-genetic-allemande.mid` | 11058 |
| Phase-1 prov. | `MIDI/091-baroque-genetic-allemande-phase1.mid.provenance.json` | 538 |
| Phase-2 prov. | `MIDI/091-baroque-genetic-allemande.mid.provenance.json` | 652 |
| WAV (P2) | `Audio/091-baroque-genetic-allemande.wav` | 11515692 |
| OGG (P2) | `Audio/091-baroque-genetic-allemande.ogg` | 446685 |
| WAV (P1) | `Audio/091-baroque-genetic-allemande-phase1.wav` | 11503660 |
| OGG (P1) | `Audio/091-baroque-genetic-allemande-phase1.ogg` | 466277 |
| Grid viz | `Analysis/grid_visualization.txt` | — |
| Audit JSON | `Analysis/audit.json` | — |
| Summary | `Analysis/summary.json` | — |
| Render stats | `Analysis/render_stats.json` | — |

All sizes > 40 bytes (no empty/corrupt exports).

## Fixes applied during the run

1. **Diatonic realization of the method-011 walk** (harmony audit failed on
   the first pass): `TonalNetworkGenerator`'s minor catalog uses a chromatic
   mediant (F#m) and a minor borrow (Fm) whose tones (F#, Ab) are
   out-of-scale in D minor. Kept the generator's *role walk* (the method-011
   output — the graph structure) but realized each role diatonically:
   mediant → III (F major), borrow → bVII (C major). Result: 0 out-of-scale.
2. **Drum backbeat overflow** (grid audit failed on 6 off-grid drum onsets):
   snare positions `t0+2880` and kick `t0+960` overflowed the last bar of
   each section when `t0 = bar*1920` with bar 3 → `t0+2880 = 7680 =
   SECTION_TICKS`, and the normalizer clamped them to `SECTION_TICKS-10`
   → off-grid 110-mod-120 clicks at the seams. Fixed with bar-local beat
   guards (skip beats that would cross the bar end). 0 off-grid after fix.
3. **GA fitness decoding** (first draft scored ~0): the fitness walked
   overlapping bits instead of 18-bit event chunks, so every interval looked
   random. Fixed to decode per-event 6-bit pitch field; best fitness rose
   from 0 → 61 with real stepwise streak pressure.
4. **Provenance API**: `write_provenance` takes `parameters=` (not `params=`).

## Method provenance
- `generators/genetic.py` `GeneticGenerator(binary_to_unit)` — raw draft
- `generators/tonal_network.py` `TonalNetworkGenerator(root=50,
  tonic_quality='minor')` — phase-2 harmonic scaffold (role walk)
- `rules/voice_leading.py` `VoiceLeadingRules(style='classical')` —
  parallel-motion / hidden-fifths check; 7 corrections applied + verified
- `workflows.unitmatrix_composer` `UnitMatrixComposer` — zero-drift matrix
- `workflows.musicom_workflow.produce(SP-001)` — FluidSynth render → OGG