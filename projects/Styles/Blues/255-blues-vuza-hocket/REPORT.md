# Report — 255-blues-vuza-hocket (Vuza Tiling Canon Composition, Blues)

Autonomous nightly two-phase composition job · 2026-10-21.

| | |
|---|---|
| **Project** | `Styles/Blues/255-blues-vuza-hocket/` |
| **Style** | Blues |
| **Method** | **111 — Vuza Tiling Canon Composition (VTCC)** |
| **Layer** | **concrete** (Rules-Based, Grid-Locked, deterministic combinatorial) |
| **Form** | **blues-12** (12 bars, single "Blues" section) |
| **Key** | E major (ionian): E F♯ G♯ A B C♯ D♯ = pcs {4,6,8,9,11,1,3} |
| **Tempo / meter** | 112 BPM · 4/4 · 480 TPB (bar = 1920 · 8th = 240 · 16th = 120) |
| **Progression** | I I I I · IV IV · I I · V · IV · I V  (degrees `[0,0,0,0,3,3,0,0,4,3,0,4]`) |

## Method 111 — Vuza tiling canon (verified this session)

A rhythmic tiling canon `A ⊕ B = ℤ₇₂`: motif `A` (|A| = 12) played verbatim by
6 entry voices at offsets `B`, covering every one of the 72 eighth-note slots
exactly once — a **perfect hocket** (zero collisions, zero gaps). Both factors
are **aperiodic**, making it a true Vuza / RCMC canon (smallest admissible n).

```
motif A  = {0, 1, 5, 6, 12, 25, 29, 36, 42, 48, 49, 53}
entries B = {0, 8, 16, 18, 26, 34}
A ⊕ B = ℤ₇₂   — asserts hold: tiles() == True; is_periodic(A)=None; is_periodic(B)=None
```

- 72 onsets = 6 entries × 12 motif onsets; slot = eighth note (240 ticks) →
  the canon spans **9 bars**.
- Bars 10–12 (the turnaround V–IV–I) clear the hocket into a held triad
  (E0/E1/E2 voice a sustained inversion).

## Voices + instruments (from the instrument registry)

| Voice | Instrument | GM | Ch | Role | Pitched |
|---|---|---|---|---|---|
| Lead | Harmonica | 22 | 0 | chord-tone arpeggio melody | ✓ |
| E0 | Clean Electric Guitar | 27 | 1 | hocket entry 0 + turnaround hold | ✓ |
| E1 | Electric Piano 2 | 5 | 2 | hocket entry 1 + turnaround hold | ✓ |
| E2 | Drawbar Organ | 16 | 3 | hocket entry 2 + turnaround hold | ✓ |
| E3 | Vibraphone | 11 | 4 | hocket entry 3 | ✓ |
| E4 | Steel Acoustic Guitar | 25 | 5 | hocket entry 4 | ✓ |
| E5 | Marimba | 12 | 6 | hocket entry 5 | ✓ |
| Bass | Electric Bass | 33 | 7 | walking (quarter grid) | ✓ |
| Drums | Drum Kit | — | 9 | shuffle backbeat | ✗ |

## Two-phase architecture

- **Phase 1** (`-phase1.mid`): the 72-onset hocket flattened to a single voice,
  scale-mapped pitch (`64 + scale[(slot+j)%7] + 12·(j//3)` — NOT chord-tone
  quantized), eighth-note slots, no harmony, no texture. Own zero-drift gate.
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): hocket split over 6 entry
  voices, chord-tone quantization per bar against the I–IV–V progression, 8th/16th
  grid snap, harmonica lead + electric bass + shuffle drums, voice-leading
  optimization on the triads, zero-drift gate, then dual-version export.

## Grid audit (per voice, read-back via mido)

| Voice | notes | perfect off16 / off8 | humanized off16 / off8 |
|---|---|---|---|
| Lead | 84 | **0 / 0** | 78 / 78 |
| E0 | 15 | **0 / 0** | 13 / 13 |
| E1 | 15 | **0 / 0** | 13 / 13 |
| E2 | 15 | **0 / 0** | 13 / 13 |
| E3 | 12 | **0 / 0** | 9 / 9 |
| E4 | 12 | **0 / 0** | 8 / 8 |
| E5 | 12 | **0 / 0** | 9 / 9 |
| Bass | 48 | **0 / 0** | 48 / 48 |
| Drums | 145 | **0 / 48** | 116 / 125 |

- **Perfect = 0 off-grid on the 16th grid** for every voice. ✓
- **Humanized > 0 off-grid** for every voice — proves the humanizer ran. ✓
- Drums `off8 = 48` (perfect) is *expected*: the swung hi-hat lands on 16th-grid
  positions (360/840/1320/1800), on the 16th grid (`off16 = 0`); the band is not
  confined to the 8th grid.

## Harmony audit (every pitched voice)

| Voice | out-of-scale | out-of-chord |
|---|---|---|
| Lead, E0–E5, Bass | **0** | **0** |

Every pitched note is both in E major **and** a chord tone of its bar's triad
(all chords are diatonic major triads; the lead/bass/canon are chord-tone only).
**0 out-of-key, 0 out-of-chord** across all 8 pitched voices. ✓

## Humanization (always-on, style-derived, seeded)

- Profile: `profile_for_style("blues")` → default base (blues not in
  `STYLE_HUMANIZE`; timing σ 10 ms, vel σ 7, layback 3 ms, phrase corr 0.55),
  then **per-instrument DNA** from the registry.
- Master seed **25756** (255·101+1); per-voice child seeds `2601356…2601364`.

| Voice | mean shift (t) | max shift (t) | mean vel Δ |
|---|---|---|---|
| Lead (harmonica) | 3.96 | 12 | 5.55 |
| E0–E2 | 2.6–3.5 | 6–9 | 3.6–4.0 |
| E3–E5 | 1.25–2.0 | 3–7 | 3.2–4.25 |
| Bass | **8.08** | 14 | 2.83 |
| Drums | **1.28** | 4 | 3.36 |

Drums anchor the grid (tightest), bass lays back (+8 ms layback DNA → largest
mean shift) — role DNA behaving as specified. ✓

## Zero-drift readback

All **9 tracks equal length (23040 ticks)** in both perfect and humanized MIDI;
`validate()` passed for both phases and both dual versions. ✓

## Voice-leading

`optimize_voice_leading` + correction pass over the 12 triads: **0 corrections,
0 parallel/hidden-fifth violations** (diatonic triads, clean close voicing). ✓

## Render + master (FluidSynth CLI → master → Opus OGG)

`target_for_style("blues") = −14.0 LUFS`, ceiling −1.0 dBTP. All three mastered.

| Render | LUFS (target −14) | true peak | silence ratio |
|---|---|---|---|
| phase1 | **−14.0** | −5.43 dB | 0.290 |
| perfect | **−14.0** | −1.00 dB | 0.083 |
| humanized | **−14.0** | −1.00 dB | 0.085 |

- `phase1` peaks at −5.43 dBTP: a sparse single-voice hocket + 3 empty
  turnaround bars is legitimately below the −1 ceiling (true-peak is a ceiling,
  not a target). Silence 29 % is the 3 authored-silent turnaround bars — honest
  for a raw phase-1 draft.
- `perfect` / `humanized`: 8.3 % / 8.5 % silence (well under the 30 % suspect
  threshold), no mid-track gaps.

## Files

| Path | Size |
|---|---|
| `MIDI/255-blues-vuza-hocket-phase1.mid` | 705 B |
| `MIDI/255-blues-vuza-hocket-perfect.mid` | 3326 B |
| `MIDI/255-blues-vuza-hocket-humanized.mid` | 3314 B |
| `Audio/255-blues-vuza-hocket-phase1.ogg` | 229 911 B |
| `Audio/255-blues-vuza-hocket-perfect.ogg` | 248 938 B |
| `Audio/255-blues-vuza-hocket-humanized.ogg` | 247 373 B |

Plus `-provenance.json` sidecars per MIDI, `Analysis/summary.json`,
`Analysis/grid_visualization.txt`, `Analysis/render_stats.json`, `README.md`.

## Fixes applied

None required — first pass passed every gate (0 off-grid perfect, 0 out-of-key,
0 out-of-chord, 0 voice-leading violations, zero-drift clean, LUFS on target on
all three renders).