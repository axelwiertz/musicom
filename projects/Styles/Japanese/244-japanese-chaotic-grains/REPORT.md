# 244-japanese-chaotic-grains — REPORT

Japanese × Method 028 **Chaotically Modulated Cellular Grains (CMCG)** (concrete, Nature-Led).

| Field | Value |
|---|---|
| Project | 244-japanese-chaotic-grains |
| Style | Japanese |
| Method | 028 — Chaotically Modulated Cellular Grains (CMCG) |
| Layer | **concrete** |
| Paradigm | Nature-Led · Continuous/Fluid · Meso/Phrase · O(G·P) |
| Key | D Hirajoshi (D E F A Bb) — pentatonic `[0,2,3,7,8]` |
| Tempo | 80 BPM · 4/4 · 480 TPB |
| Form | **strophic** — 4 × Verse × 8 bars = 32 bars |
| Date | 2026-10-15 (nightly two-phase job) |

## 1. Method mechanics (Method 028, concrete)

CMCG bridges chaotic dynamical systems and granular synthesis: a **Henon map**

```
x_{n+1} = 1 − a·x_n² + y_n
y_{n+1} = b·x_n          (a = 1.4, b = 0.3 — full-chaos regime)
```

drives each "grain" of the melodic lead. Per the method's musical-element
framework:

- **PITCH** ← `x`-coordinate: the chaotic `x` value (bounded ±1.28) selects the
  chord-tone index each grain lands on (`tone_idx = floor((x+1.28)/2.55·3)`).
- **RHYTHM** ← `y`-coordinate: the chaotic `y` value (bounded ±0.38) selects the
  8th-grid slot each grain occupies (`slot = floor((y+0.38)/0.76·8)`).
- **STRUCTURE** ← regime sweep: the four strophic verses realize the method's
  "gradual transition of chaotic parameters" as a *grain-density* trajectory —
  Verse1 = stable/periodic (4 grains/bar), Verse2 = bifurcation (8/bar),
  Verse3 = full chaos (12/bar, taiko off-beats + 8th hats), Verse4 = return
  (5/bar). The harmonic strophe is identical each verse (strophic identity);
  the chaotic *texture* is what evolves.

Because Method 028 is Continuous/Fluid, Phase 1's "rawness" is genuine
off-grid micro-timing and unquantized pitch; Phase 2 snaps every onset to the
8th grid (240) and every pitch to the bar's chord tones (the musicom rules
layer).

## 2. Two-phase architecture

- **Phase 1 (raw)** — single koto voice, 256 grains. `x → pitch = round(67+14x)`
  (raw int, NOT scale-snapped), `y → onset jitter ±240 ticks`. Off-grid by
  design, no harmony. Exported `244-japanese-chaotic-grains-phase1.mid`
  (zero-drift gate passed).
- **Phase 2 (rules)** — chord-tone quantization + 8th-grid snap + full texture:
  koto grain lead, shakuhachi sustained counterline, shamisen arpeggio, taiko +
  ch9 drums. Exported `244-japanese-chaotic-grains.mid` (zero-drift gate passed).

## 3. Harmonic plan (D Hirajoshi, strophic 8-bar cycle ×4)

All chord-tone pitch classes are subsets of the Hirajoshi set `{2,4,5,9,10}`.

| Bar | Roman | Chord | Root PC | Chord-tone PCs |
|---|---|---|---|---|
| 0 | i | Dm | 2 | D F A |
| 1 | bVI | Bb | 10 | Bb D F |
| 2 | bIII | F6 | 5 | F A D |
| 3 | v | Asus | 9 | A D E |
| 4 | i | Dm | 2 | D F A |
| 5 | bVI | Bb | 10 | Bb D F |
| 6 | bIII | F6 | 5 | F A D |
| 7 | i | Dm | 2 | D F A |

(cycle repeats for bars 8–31)

## 4. Voices (instrument registry — source of truth)

| Voice | Program | Channel | Role |
|---|---|---|---|
| Koto | 107 | 0 | Henon grain lead |
| Shakuhachi | 77 | 1 | sustained counterline (1 chord tone/bar) |
| Shamisen | 106 | 2 | 8th-note chord arpeggio |
| Taiko | 116 | 3 | deep DON (beat 1, +3 in Verse3) |
| Drums | 0 | 9 | kick + low-tom pulse, 8th hats in Verse3 |

## 5. Verification (real numbers)

### 5a. Grid audit (exported phase-2 MIDI readback via mido)

| Voice | notes | off-16th | off-8th |
|---|---|---|---|
| Koto | 179 | 0 | 0 |
| Shakuhachi | 32 | 0 | 0 |
| Shamisen | 256 | 0 | 0 |
| Taiko | 40 | 0 | 0 |
| Drums | 128 | 0 | 0 |

**Verdict: 0 off-grid across all 5 voices.**

### 5b. Harmony audit (pitched voices: Koto, Shakuhachi, Shamisen)

| Voice | out-of-scale | out-of-chord |
|---|---|---|
| Koto | 0 | 0 |
| Shakuhachi | 0 | 0 |
| Shamisen | 0 | 0 |

**Verdict: 0 out-of-scale, 0 out-of-chord.** (Taiko/Drums are percussion —
excluded from scale/chord audit by convention.)

### 5c. Zero-drift gate

Phase 1 `validate()` → True. Phase 2 `validate()` → True.

### 5d. Voice-leading

Shakuhachi sustained-line parallel/hidden-fifth check → **0 violations**.

### 5e. Render + master

| File | size | silence | peak | LUFS | dBTP |
|---|---|---|---|---|---|
| 244-japanese-chaotic-grains.wav | 17,583,404 B | 3.61% | 0.890 | −14.18 | −1.00 |
| 244-japanese-chaotic-grains-phase1.wav | 17,585,196 B | 4.04% | 0.891 | −15.00 | −1.00 |

- Silence ratio well under the 30% suspect threshold; the ~2 near-silent
  seconds are the FluidSynth master tail (legit).
- Both WAVs mastered to streaming standard (−14 LUFS / −1 dBTP) *after* the raw
  FluidSynth render, before Opus encode.
- Post-master integrated LUFS −14.18 (target −14) and true peak −1.00 dBTP
  (ceiling −1) for the phase-2 mix. Phase-1 lands −15.00 (single-voice sparser
  source — ceiling holds, quiet material is not pumped; correct behaviour).
- Tonal-content check (dominant freq per 0.5 s window, 50–1000 Hz): 54 Hz
  (taiko/kick DON), 588 Hz (D5), 698 Hz (F5) — real pitched content, not noise.

## 6. Files

```
MIDI/244-japanese-chaotic-grains.mid            (5,867 B) + provenance
MIDI/244-japanese-chaotic-grains-phase1.mid     (2,232 B) + provenance
Audio/244-japanese-chaotic-grains.wav           (17.6 MB, mastered)
Audio/244-japanese-chaotic-grains.ogg           (810 KB, Opus)
Audio/244-japanese-chaotic-grains-phase1.wav    (17.6 MB, mastered)
Audio/244-japanese-chaotic-grains-phase1.ogg    (912 KB, Opus)
Analysis/summary.json                           (chord path + regime + audit)
Analysis/grid_visualization.txt                 (ASCII grid)
Analysis/readback_audit.json                    (mido readback audit)
```

## 7. Fixes / decisions

- Strophic form's `form_to_sections` returns 4 identical "Verse" names; the
  matrix composer keys cells by section *name*, so the 4 verses were
  disambiguated to `Verse1..Verse4` (documented in README/REPORT).
- Render gain 0.6 (not `produce()`'s 1.2) — the dense 5-voice GM mix clips at
  the higher gain; 0.6 lands peak 0.89 with zero clipped samples.
- Henon `x`/`y` mapping uses the classic attractor bounds (±1.28 / ±0.38) to
  index chord tones and 8th slots without array overrun.
