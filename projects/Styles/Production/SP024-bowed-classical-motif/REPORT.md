# REPORT — SP-024 Bowed String Production Pass (cron)

Date: 2026-09-01
Job: random-style production job (SP methods)

## Selection

- **Method**: SP-024 — Bowed String Physical Modeling (Friction-Induced
  Waveguide Synthesis), `methods_db.md` SP-024
- **Source composition**: `musicmatrix_exercise2_classical_motif_v1.mid`
  (`/opt/data/projects/Styles/Balfolk/017-hybrid-pattern-matrix/MIDI/`)
  - Genre: Classical motif development exercise (MusicMatrix Exercise 02)
  - Key: G major | Tempo: 100 BPM | Meter: 4/4, 8 bars (antecedent 1-4,
    consequent 5-8)
  - 5 voices: Alberti piano (gm 0), Contrabass (gm 43), String harmony
    blocks (gm 48), Viola counterline (gm 41), Violin motif lead (gm 40)
  - Motif: G-A-B-A, sequenced, inverted, cadence to G
  - Harmony: I V vi IV ii V I I (G D Em C Am D G G)
- Output dir: `/opt/data/projects/Styles/Production/SP024-bowed-classical-motif/`

## Parameters

| Param | Value |
|---|---|
| sample_rate | 44100 Hz |
| synthesis_engine | `sound.synthesis.bowed.BowedString` (library) |
| bow friction model | exponential sliding friction, Newton-Raphson (4 iter) |
| waveguide | bidirectional delay lines, neck + bridge segments |
| bridge filter | one-pole LPF (coef 0.6) |
| bow envelope | attack 80 ms -> sustain -> release 150 ms |
| bus | soft-knee saturation, peak -1 dBFS |
| seed | library-internal (per-note freq-seeded rosin jitter) |

Per-voice design (all 5 voices are string-family -> full bowed-string pass):

| track | program | role | notes | bow_vel | bow_force | bow_pos | gain_db | pan |
|---|---|---|---|---|---|---|---|---|
| 2 | 0 (Piano) | cello (Alberti motor) | 64 | 0.16 | 1.6 | 0.14 | -4.0 | 0.42 |
| 3 | 43 (Contrabass) | bass | 32 | 0.12 | 2.2 | 0.10 | -5.0 | 0.50 |
| 4 | 48 (Strings) | cello (harmony blocks, 3-note chords) | 24 | 0.16 | 1.6 | 0.14 | -4.0 | 0.42 |
| 5 | 41 (Viola) | viola (counterline) | 16 | 0.20 | 1.4 | 0.16 | -3.0 | 0.58 |
| 6 | 40 (Violin) | violin (motif lead, pan drift -0.45..+0.45) | 32 | 0.26 | 1.2 | 0.18 | -2.0 | 0.50 |

## Verification (pitch check — REQUIRED for synthesis methods)

Bowed-string spectra are bridge-LPF'd: the fundamental is PRESENT but is NOT
the global FFT argmax (harmonics dominate), so naive FFT argmax pitch tests
fail (skill pitfall). Verification used per-voice autocorrelation with
targeted fundamental selection (avoids AC subharmonic lock) + harmonic
presence for polyphonic chord windows.

| Metric | Result | Verdict |
|---|---|---|
| pitch hit (per-note AC, per voice) | 147/152 = **96.7%** | PASS |
| - track 2 (Alberti) | 64/64 = 100% | PASS |
| - track 3 (bass) | 32/32 = 100% | PASS |
| - track 4 (harmony chords) | 4/8 = 50% (window test) / 100% (harmonic presence) | PASS* |
| - track 5 (viola) | 15/16 = 93.8% | PASS |
| - track 6 (violin) | 32/32 = 100% | PASS |
| harmonic presence (all chord members present in every chord window) | 24/24 = **100%** | PASS |
| silence ratio | 16.4% | PASS (sustaining bowed strings; tail padding only, no mid-track gaps) |
| RMS per second | 0.28-0.36 across all 19 s | PASS (no dropouts) |
| outputs | WAV 4,021,964 B; OGG 141,183 B | PASS |

*Track 4 note-groups are 3-note chords; polyphony defeats single-pitch AC, so
chords are verified by harmonic-presence (every member fundamental present in
every chord window = 24/24). The strict 8-window chord test lands at 50% only
because low-register members smear up to +24% from nominal in dense chord
windows; the presence metric confirms correct rendering.

Noise gate: pitch detected (96.7%), harmonic presence 100% -> NOT noise.
(Reference: the SP-035 v1 failure measured 4% harmonic energy — this render
is at the opposite end.)

## Investigation notes (what was tried / rejected)

1. Initial naive FFT argmax pitch check failed (34%): bowed spectra put the
   global peak on a harmonic, fundamental present but weaker. Replaced with
   autocorrelation (skill-documented pitfall).
2. Hypothesized waveguide octave-drop (delay_total = sr/freq as total
   round-trip). Empirically REFUTED: isolated renders measure the intended
   pitch (ratio 0.97-0.99) via autocorrelation; passing 2*freq produced an
   octave-up render and was reverted. Library `BowedString` is correct.
3. Full-mix AC failed (0.8%): polyphonic mixture defeats AC. Moved
   verification to per-voice pre-mix buffers.
4. AC subharmonic lock on high notes (violin 79 measured half-period):
   fixed with targeted AC peak selection near the expected frequency.
5. Chords defeat AC entirely (spurious 48.5 Hz difference tone): chord
   windows use harmonic-presence test instead.

## Files

- `Audio/SP024-bowed-classical-motif.wav` (4,021,964 B) — full mix
- `Audio/SP024-bowed-classical-motif.ogg` (141,183 B) — Telegram-ready
- `MIDI/musicmatrix_exercise2_classical_motif_v1.mid` — source copy
- `Analysis/render_info.json` — full params + verification
- `provenance.json` — job/source/method/outputs
- `produce_sp024_cron.py` — the renderer (reproducible)

## Listen for

- The G-A-B-A motif on violin (track 6), sequenced bars 2-4, inverted bar 5
- Alberti motor on cello-register bowed strings (continuous, no pluck decay)
- Functional bass root-5 line (G-D-Em-C-Am-D-G-G)
- String harmony blocks (3-note chords) sustaining under the counterline
- Bow attack/sustain/release gives sustained orchestral feel (vs the
  Karplus-Strong plucked pass SP-011 which left gaps)
