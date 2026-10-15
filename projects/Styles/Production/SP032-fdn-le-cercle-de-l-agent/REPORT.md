# SP-032 FDN Reverb — le_cercle_de_l_agent (Balfolk jig)

**Job:** random-style production (SP methods) — LAYER-ALIGNED
**Date:** 2026-10-15  **Seed:** 20261015

## Selection

| Field | Value |
|---|---|
| Registry source | `workflows.musicom_workflow.SP_METHODS` (48 registered) |
| Method | `SP-032` |
| Module | `sound.effects.fdn_reverb` |
| Description | Feedback Delay Network Reverb — 8 prime delay lines, normalized Hadamard feedback matrix, per-line one-pole LPF, slow LFO delay modulation, input ducking, mid/side width (Rev Ocean "Tidal"-style) |
| Layer | ABSOLUTE — one FDN config applied to the whole piece |
| Recent excluded (7d) | SP-026, SP-028, SP-074, SP-085, SP-092, SP-098, SP-103 |
| Pool size | 40 |
| Well-formed candidates | 233 / 342 |

**Source composition:** `Styles/Balfolk/005-balfolk-production/midi/le_cercle_de_l_agent.mid`
- 16-bar 6/8 Balfolk jig ("Cercle Circassien"), 120 BPM, TPB 480 (BAR = 1440 ticks)
- G-major pentatonic folk tune over a G drone
- Voices (source track names): Violin (melody), Guitar (bass), Piano (comp)
- Note counts (source): 96 melody / 32 bass / 32 comp = 160 pitched notes

## PRE-FLIGHT AUDIT (3-rule gate)

| Rule | Before | After | Verdict |
|---|---|---|---|
| Grid sync (8th = 240 ticks @ 480 TPB, 6/8) | 0 off-grid | 0 | PASS |
| Harmony — in scale (G major) | 0 out-of-scale | 0 | PASS |
| Harmony — chord tone of bar | 21 out-of-chord (8 A + 13 E, vs G-triad) | 0 (vs G6/9) | FAIL → reworked → PASS |
| Zero-drift (equal track lengths) | 23040 / 22560 / 21840 (UNEQUAL) | 23040 = 23040 = 23040 | FAIL → reworked → PASS |
| Meta (program / tempo / time sig) | none (would render all as Acoustic Grand Piano) | Violin 40 / Guitar 25 / Piano 1, 120 BPM, 6/8 | FAIL → reworked → PASS |

**Verdict: FAIL → reworked → PASS.** Three distinct problems in the source:

1. **Zero-drift** — the three tracks ended at 23040 / 22560 / 21840 ticks
   (bass stopped 480 ticks early, comp 1200 ticks early). Genuine track
   desync, the most clear-cut rule break.
2. **Chord-tone** — the melody's G-major-pentatonic passing/color tones A
   (2nd/9th) and E (6th/13th) are not chord tones of the bare G-triad that
   the comp (G-B dyad) implied. 21 notes flagged under a strict G-triad read.
3. **Meta** — no program changes, no tempo, no time signature. Rendered
   as-is, all three tracks would sound as Acoustic Grand Piano (program 0),
   silently discarding the intended Violin/Guitar/Piano timbres.

### Rework applied (two-phase, melody-preserving)

- Phase-1 sidecar: `midi/le_cercle_de_l_agent-phase1.mid` (raw original).
- Phase-2 (`_cron_rework_le_cercle.py`, `UnitMatrixComposer`):
  - **Melody (Violin) & bass (Guitar) preserved note-for-note** (96 + 32 notes
    unchanged — the tune is the identity marker and is already fully diatonic
    + grid-locked).
  - **Comp re-harmonized** G-B dyad → **G6/9** (G3 B3 D4 E4 A4), the full
    G-major-pentatonic sonority the melody implies, so every melody note (G A
    B D E) is now a genuine chord tone of the sounding harmony. This is the
    correct folk-drone reading — the A and E are chord tones of G6/9, not
    "non-chord crud" — rather than flattening the tune to a G-B-D arpeggio.
  - **GM programs added** (Violin 40 / Acoustic Guitar 25 / Piano 1), tempo
    120 BPM, 6/8 time signature.
  - All tracks padded to 23040 ticks; `validate()` → True; re-exported
    `le_cercle_de_l_agent.mid` (1830 B).

Chord-tone set per bar: G6/9 = {G, B, D, E, A} throughout (G-major drone).

## Method parameters (SP-032 — absolute layer)

| Param | Value |
|---|---|
| n_delays | 8 |
| size (feedback gain) | 0.55 |
| decay (tail length) | 0.80 |
| brightness (HF damping) | 0.72 |
| modulation (LFO depth) | 0.25 |
| width (mid/side spread) | 0.85 |
| duck_amount (input ducking) | 0.12 |
| wet_dry | 0.35 |
| fs | 44100 |

Chain: dry FluidSynth render (reverb/chorus OFF) → trim spurious FluidSynth
tail → pad 3.5 s → FDN.process() (dry+wet mixed internally at wet_dry) →
`normalize_to_lufs(−14)` → `Limiter(−1 dBFS)`.

Sizing choice: folk jig needs clarity + a tight-but-audible room — decay 0.80,
moderate wet_dry 0.35, light input ducking 0.12 so the 6/8 violin pick stays
articulate while the G6/9 drone blooms.

## Pitch verification (mandatory) — PASS

| Metric | Wet | Dry (SP-001 ref) | Gate |
|---|---|---|---|
| Valid 0.5 s windows | 53 | — | — |
| FFT pitch-class hit rate | **1.000** | 1.000 | ≥ 0.60 |
| Mean harmonic energy (8 harmonics) | **0.5776** | 0.5498 | ≥ 0.30 |
| HE retention | **1.051** | — | ≥ 0.40 |

**Pitch verdict: PASS.** FDN reverb is a linear time-domain effect and preserves
every fundamental exactly; hit rate stayed at 100%. Harmonic energy rises
slightly (0.550 → 0.578, retention 1.05 > 1.0) because the reverb tail sustains
the harmonics past each note's release. Lowest source fundamental is G2 = 98 Hz
(> 50 Hz band floor), so no octave-match special case was needed.

## Silence / RMS profile

- Silence ratio: **20.65%** (below the 30% suspect threshold; the silence is
  the FDN reverb tail + the violin's long FluidR3_GM release, not mid-track
  holes — the dry per-second RMS map shows continuous content 0–24 s).
- Overall RMS: 0.1344
- LUFS: −14.00  |  Peak: 0.8913 (−1.0 dBFS; true-peak ceiling is a ceiling, not a target)
- Mono correlation: 0.867

## Artifacts

| File | Size |
|---|---|
| `SP032-fdn-le-cercle-de-l-agent.wav` | 6,266,272 B (35.5 s) |
| `SP032-fdn-le-cercle-de-l-agent.ogg` | 214,010 B |
| `dry_full_mix_sp001_reference.wav` | 7,896,108 B (44.76 s, untrimmed) |
| `MIDI/le_cercle_de_l_agent.mid` (reworked source copy) | 1,830 B |
| `Audio/stems_dry/*.wav` (3 dry stems) | 4.6–7.9 MB |
| `Audio/stems_wet/*_FDN.wav` (3 wet stems) | 5.1–6.3 MB |
| `provenance.json`, `Analysis/render_stats.json`, `Analysis/select_20261015.json` | — |

Stem labels: `track00_Violin`, `track01_Acoustic_Guitar_steel`,
`track02_Bright_Acoustic_Piano`.

## Notes

- Selection script: `Production/select_job_20261015.py` (→ `.selection_cron.json`).
- Source rework script: `Balfolk/005-balfolk-production/_cron_rework_le_cercle.py`.
- Production script: `Scripts/produce_sp032_cron.py`.
- **FluidSynth 2.5.6 silent-tail quirk (fixed this run):** with the reworked
  MIDI's GM programs (Violin 40 / Guitar 25), FluidSynth renders a ~20 s silent
  tail past the 24 s content (44.76 s total) because the FluidR3_GM string
  patches carry long release tails; the bare all-piano render is only 26.9 s.
  Confirmed by A/B: programs→0 renders 26.9 s, programs 40/25/1 renders 44.76 s.
  v1 of this run shipped at 41.6% silence. Fix: `trim_tail()` after the dry
  render (keep last sample above 0.0005 + 1.5 s), then FDN pad 3.5 s → final
  silence 20.65%. Dry full-mix WAV kept untrimmed for reference.
- The 6/8 time signature was verified NOT to affect render duration (6/8, no
  time-sig, and 4/4 variants all rendered 44.76 s pre-trim) — the tail is purely
  the string patch release, not the meter.
