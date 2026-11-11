# SP-069 Switched Discrete Distortion Topology Bank — moonlight-shadow

Random-style production job (SP methods), layer-aligned, **2026-11-11**.

## Selection

| Item | Value |
|---|---|
| Seed | `20261111` |
| Registry | `workflows.musicom_workflow.SP_METHODS` (87 pickable methods) |
| Selected method | **SP-069** — `sound.effects.topology_distortion` |
| Method desc | Switched Discrete Distortion Topology Bank (FuzzBillion-style) |
| Source composition | `Pop/moonlight-shadow/MIDI/moonlight-shadow-variant2.mid` |
| Pool (after exclusions) | 79 methods |
| Recent excluded (≤7 d) | SP-097, SP-113, SP-117, SP-119, SP-138, SP-143, SP-146 |
| Baseline excluded | SP-001 |
| Already on source | (none) |
| Candidates / well-formed / meaningful | 442 / 337 / 336 |

## Source composition

- **Genre**: Pop (Mike Oldfield "Moonlight Shadow" cover, genetic-method
  phase-2 chord-tone-quantized — provenance `method=genetic`, `phase=2`).
- **Key**: E major · **Tempo**: 126 BPM · 4/4 · 480 ticks/beat.
- **Form**: Intro(4) + Verse1(8) + Chorus(8) + Verse2(8) + Outro(4) = **32 bars** ≈ 61 s.
- **Voices** (6 note tracks):
  | Track | GM | Voice |
  |---|---|---|
  | 1 | 74 Recorder | Melody (ch0) |
  | 2 | 49 String Ensemble 2 | Strings pad (ch1) |
  | 3 | 88 New Age Pad | Arp pad (ch2) |
  | 4 | 33 Electric Bass finger | Bass (ch3) |
  | 5 | 25 Acoustic Guitar steel | Guitar strums (ch4) |
  | 6 | ch9 | Drums |

## Pre-flight rules audit (BEFORE any sound change)

| Rule | Verdict | Numbers |
|---|---|---|
| 1. Grid sync | **FAIL → FIXED** | 59 / 737 pitched onsets off-grid (all 59 at residual 119 = 1 tick *before* a bar seam) |
| 2. Harmony | **PASS** | 0 / 737 out-of-scale (E major). Lead melody consonant with accompaniment (6 in-key colour tones = the song's B-over-IV riff) |
| 3. Zero-drift | **PASS** | all 6 note tracks terminate at 61440 ticks (32 bars) |

### What failed and the fix

The only defect was **Rule 1**: 59 one-tick "stub" notes in the melody track,
each a `note_on` 1 tick before a bar seam (`t % 1920 == 1919`) with `note_off`
1 tick later (dur = 1 tick ≈ 1 ms — inaudible, but off-grid). These are
section-boundary clamp artifacts from the original genetic pipeline (chord
stubs like B–D♯–F♯ at the Verse1→Chorus seam, A–G♯ at Verse2→Outro).

**Rework**: surgical removal of the 59 stub notes, everything else byte-exact
(pitches, velocities, durations, programs, channels, terminal pads). Raw draft
kept as `moonlight-shadow-variant2-phase1.mid` sidecar.

**Why surgical, not `UnitMatrixComposer`**: the source has ~150 sustained notes
that ring across *bar* boundaries inside multi-bar sections (Intro 4 / Verse 8 /
Chorus 8 / Verse2 8 / Outro 4). A 1-bar-per-section matrix reconstruction would
clamp every one of those sustains at the bar line (audible chop); the surgical
edit deletes only the 59 stubs and preserves every sustain.

### After rework (re-audit)

| Rule | Verdict | Numbers |
|---|---|---|
| 1. Grid sync | **PASS** | 0 / 678 off-grid |
| 2. Harmony | **PASS** | 0 / 678 out-of-scale |
| 3. Zero-drift | **PASS** | all tracks 61440 ticks; `len(set(end_ticks))==1` |

All three read 0 after rework.

## SP-069 application (absolute layer, whole piece)

Engine: `FuzzBillion` — 11 serially-switched nonlinear stages, 10 options each
→ **10¹¹ distinct circuits** (`circuit_count()`). Switch order = signal order.
Dry FluidSynth render (`-ni -g 1.2`, FluidR3_GM.sf2) → whole-mix distortion.

| Variant | Circuit (11 switches) | Gain | I/O | Role |
|---|---|---|---|---|
| `fuzz_ge` | `3 5 8 1 3 4 5 7 6 0 5` | 2.0 | inst | main |
| `fuzz_hard` | `2 0 3 9 6 2 3 7 7 6 0` | 3.0 | line | alt |
| `full_mix` | (none) | — | — | dry reference |

Circuit profiles (220 Hz sine, `FuzzBillion.profile()`):
- `fuzz_ge` — spectral centroid 239.8 Hz, harmonic ratio 1.92, peak 0.432.
- `fuzz_hard` — centroid 242.0 Hz, harmonic ratio 2.60, peak 0.562.

Both raise harmonic content above the bypassed chain (harmonic ratio ≫ 1);
`fuzz_hard`'s transformer+CMOS+opamp stages saturate harder (higher ratio and
peak) than the germanium-soft chain.

## Mastering (`master()`, target `pop` → −9.0 LUFS, −1 dBTP ceiling)

| Render | Integrated LUFS | True peak |
|---|---|---|
| `full_mix` | −9.79 | −1.0 dB |
| `fuzz_ge` | −9.0 | −1.99 dB |
| `fuzz_hard` | −9.0 | −2.4 dB |

The dry mix hits the −1 dBTP ceiling (transient-rich guitar strums). The fuzz
renders land **below** the ceiling because distortion compresses the crest
factor (peak-to-average) — true-peak is a ceiling, not a target; nothing to fix.

## Pitch / spectral verification (not noise)

FFT dominant peak + band-energy fraction per render:

| Render | Dominant Hz | Band frac (50–1000 Hz) | Low frac (40–300 Hz) |
|---|---|---|---|
| full_mix | 184.8 (F♯3) | 0.939 | 0.646 |
| fuzz_ge | 184.8 (F♯3) | 0.907 | 0.599 |
| fuzz_hard | 184.8 (F♯3) | 0.881 | 0.565 |

- **Tonal content confirmed**: dominant 184.8 Hz = F♯3 (in-key, ii of E major)
  preserved through the distortion chain; band energy ≫ single digits
  (noise would read < 0.1). Distortion adds harmonics, so the 50–1000 Hz band
  stays dense and the low-band fraction dips slightly as energy spreads upward.

## Silence profile

| Render | Silence ratio | Low-RMS seconds (of 68) |
|---|---|---|
| full_mix | 8.89 % | 5 |
| fuzz_ge | 8.49 % | 5 |
| fuzz_hard | 8.43 % | 5 |

All far below the 30 % suspect threshold; the 5 low-RMS seconds are the intro
lead-in and section-break gaps, not mid-track holes.

## Files

```
Audio/full_mix.wav          12.1 MB  (dry reference, mastered)
Audio/full_mix.ogg           1.24 MB
Audio/fuzz_ge.wav           12.1 MB  (main SP-069 treatment, mastered)
Audio/fuzz_ge.ogg            1.20 MB
Audio/fuzz_ge_raw.wav       12.1 MB  (pre-master)
Audio/fuzz_hard.wav         12.1 MB  (alt SP-069 treatment, mastered)
Audio/fuzz_hard.ogg          1.22 MB
Audio/fuzz_hard_raw.wav     12.1 MB  (pre-master)
Audio/stems/*.wav            6 stems (time-aligned, padded)
Audio/provenance.json               (method, circuits, master, pitch, silence)
Analysis/silence_profile.json
Analysis/spectral.json
MIDI/moonlight-shadow-clean.mid             (reworked, 0 off-grid / 0 out-of-scale)
MIDI/moonlight-shadow-variant2-phase1.mid   (original raw, sidecar)
MIDI/rework_audit.json                      (before/after audit numbers)
```

## Fixes applied this run

1. **Rule 1 (grid sync)**: removed 59 one-tick stub notes at bar seams
   (59 → 0 off-grid). Surgical edit preserved all 153 cross-bar sustains.
2. **Rules 2–3**: already clean (0 out-of-scale, zero-drift intact) — no change.

The SP-069 treatment is a timbral transformation (register/harmonic saturation),
not a correction to the composition.
