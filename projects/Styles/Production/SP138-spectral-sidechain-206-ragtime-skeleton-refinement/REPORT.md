# SP-138 Spectral Sidechain — 206-ragtime-skeleton-refinement

Random-style production job (SP methods), layer-aligned, **2026-11-10**.

## Selection

| Item | Value |
|---|---|
| Seed | `20261110` |
| Registry | `workflows.musicom_workflow.SP_METHODS` (87 pickable methods) |
| Selected method | **SP-138** — `sound.effects.spectral_sidechain` |
| Method desc | Spectral Sidechain — STFT log-band ducking driven by competing-track band energy (threshold/ratio/knee, attack/release smoothing) + blob-map pan/height/depth analysis (Art DSP Canvas 2.0-style) |
| Source composition | `Ragtime/206-ragtime-skeleton-refinement/MIDI/206-ragtime-skeleton-refinement.mid` |
| Pool (after exclusions) | 79 methods |
| Recent excluded (≤7 d) | SP-097, SP-107, SP-113, SP-117, SP-119, SP-143, SP-146 |
| Baseline excluded | SP-001 |
| Already on source | (none) |

## Source composition

- **Genre**: Ragtime (solo-piano stride, Scott Joplin tradition).
- **Key**: C major · **Tempo**: 120 BPM · 4/4 · 480 ticks/beat.
- **Form**: Intro(4)+A(8)+B(8)+A2(8)+Trio(8)+Coda(4) = **40 bars** ≈ 80 s.
- **Voices** (all GM program 1, solo piano): Melody (ch0, RH lead),
  Bass (ch1, LH stride on beats 1&3), Comp (ch2, LH chord stabs 2&4).

## Pre-flight rules audit (BEFORE any sound change)

| Rule | Verdict | Numbers |
|---|---|---|
| 1. Grid sync | **PASS** | 0 / 600 pitched onsets off-16th (120 ticks); 80 off-8th = intended 16th syncopation |
| 2. Harmony | **PASS** | 0 / 600 out-of-scale · 0 / 600 out-of-chord (per voice: Melody 0/0, Bass 0/0, Comp 0/0) |
| 3. Zero-drift | **PASS** | 3 note tracks each terminate at 76800 ticks (40 bars) via terminal landmark |

Clean on first audit — **no rework required**. (My first measurement of
zero-drift via max-note-off looked unequal, but that excluded the terminal
landmark; every track carries a `note_on pitch=0 vel=0` at tick 76800 and ends
there — the engine's zero-drift invariant holds.) SP-138 applied directly on
the clean source MIDI.

## SP-138 application (absolute layer, whole piece)

Dry FluidSynth render (`-ni -g 1.2`, FluidR3_GM.sf2) → 3 per-voice stems →
spectral separation. STFT params: `fft 2048 · hop 512 · n_bands 12 ·
f_lo 40 Hz · f_hi 16 kHz · threshold −35 dB · ratio 8 · knee 6 dB ·
attack 5 ms · release 120 ms · mix 1.0`.

| Variant | Treatment |
|---|---|
| `canvas2mix` (main) | `Canvas2Mix` — each stem (Melody/Bass/Comp) ducked band-wise by the loudest competing track, re-summed → "space between the two hands" |
| `bass_duck` (alt) | classic pump — stride Bass sidechains Melody+Comp |
| `full_mix` (reference) | dry, no sidechain |

Stems arrive time-aligned (equal 76800-tick length; padded to 3637312 samples).
Downmixed to mono for the spectral pass; output duplicated to stereo for the bus.

## Mastering (`master()`, target `ragtime` → fallback −14.0 LUFS, −1 dBTP ceiling)

| Render | Integrated LUFS | True peak |
|---|---|---|
| `full_mix` | −14.00 | −1.0 dB |
| `canvas2mix` | −15.57 | −1.0 dB |
| `bass_duck` | −14.76 | −1.0 dB |

`canvas2mix` reads ~−15.6 LUFS because the sidechain ducks the low-band energy,
lowering average level and letting the transient-rich piano hits bind the −1 dBTP
ceiling first. Correct behaviour — true-peak is a ceiling, not a target.

## Pitch / spectral verification

FFT dominant peak in 50–1000 Hz + band-energy fraction + low-band retention:

| Render | Dominant Hz | Band frac (50–1000 Hz) | Low frac (40–300 Hz) |
|---|---|---|---|
| full_mix | 392.0 (G4) | 0.848 | 0.435 |
| canvas2mix | 392.0 (G4) | 0.531 | 0.197 |
| bass_duck | 524.1 (C5) | 0.486 | 0.135 |

- **Tonal content confirmed, not noise**: dominant 392 Hz = G4 present in both
  sidechain renders; harmonic band energy ≫ single digits.
- **The sidechain works as designed**: low-band energy fraction drops 0.435 →
  0.197 (canvas2mix) and → 0.135 (bass_duck) — the competing low register is
  ducked exactly where the bass/comp overlap, mid/air bands survive.

## Canvas blob map (descriptor, avg per frame)

| | pan | height (spectral centroid) | depth (RMS) |
|---|---|---|---|
| dry full_mix | −0.004 | 0.088 | 0.055 |
| canvas2mix | 0.0 | 0.166 | 0.003 |

Spectral centroid rises (0.088 → 0.166) after the low-band duck — the treated
mix reads brighter/taller on the Canvas axes; depth falls as low energy is
removed. Pan stays centred (mono piano).

## Silence profile

| Render | Silence ratio | Low-RMS seconds (of 82) |
|---|---|---|
| full_mix | 3.75 % | 2 |
| canvas2mix | 2.64 % | 1 |
| bass_duck | 4.78 % | 1 |

All far below the 30 % suspect threshold; the 1–2 low-RMS seconds are the intro
leading rest + final cadence decay, not mid-track gaps.

## Files

```
Audio/full_mix.wav          14.5 MB  (dry reference, mastered)
Audio/full_mix.ogg           1.66 MB
Audio/canvas2mix.wav        14.5 MB  (main SP-138 treatment, mastered)
Audio/canvas2mix.ogg         1.45 MB
Audio/canvas2mix_raw.wav    14.5 MB  (pre-master)
Audio/bass_duck.wav         14.5 MB  (alt SP-138 treatment, mastered)
Audio/bass_duck.ogg          1.43 MB
Audio/bass_duck_raw.wav     14.5 MB  (pre-master)
Audio/stems/*.wav            3 stems (Melody/Bass/Comp, time-aligned)
Audio/provenance.json               (method, params, master, pitch, blob map)
Analysis/silence_profile.json
Analysis/spectral.json
MIDI/ (source reference)           206-ragtime-skeleton-refinement.mid (clean, unchanged)
```

## Fixes applied this run

None required on the composition — all three pre-flight rules passed on first
audit (grid 0 off-grid, harmony 0/0, zero-drift clean). The SP-138 treatment is
an audience-perception change (register separation), not a correction.