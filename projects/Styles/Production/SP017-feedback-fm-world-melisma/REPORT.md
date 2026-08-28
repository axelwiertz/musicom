# SP-017 Modified FM (Feedback FM & Phase Modulation) — 072-world-melisma

**Date:** 2026-08-28 (cron production job)
**Method:** SP-017 — Modified FM (Feedback FM & Phase Modulation)
**Source composition:** 072-world-melisma (World, D Dorian, file tempo 120 BPM, 20 bars, 5 sections: Intro/Verse/Chorus/Verse2/Outro, 4 bars each)
**Source MIDI:** `/opt/data/projects/Styles/World/072-world-melisma/MIDI/072-world-melisma.mid`

## Selection

- Method pool: SP-001..SP-056 minus the 22 already realized in `/opt/data/projects/Styles/Production/` → **SP-017** drawn (not previously realized).
- Composition pool: recent unitmatrix compositions (066–079) not yet used in Production → **072-world-melisma** drawn.
- Selection recorded in `/opt/data/projects/Styles/Production/.selection.txt`.

## Source composition

- Style: World; Key: D Dorian (D E F G A B C), file tempo 120 BPM (composed @100 BPM intent, MIDI carries 120 BPM), 4/4, 20 bars.
- Harmony: Markov walk over dorian degrees i–ii–III–IV–v (M-022 Markov-Constraint / markov-harmony, seed 20260818).
- Voices (GM program / channel): Lead Pan Flute (75), Counter String Ensemble (48), Pad Synth Pad (89), Bass Fretless (35), Percussion (ch10).
- 429 note events parsed, 40.5 s total.

## SP-017 implementation

Feedback-FM core (sample-by-sample, honest self-feedback):

```
y_m[n] = cos( 2*pi*fm*n*Ts + beta * y_m[n-1] )      modulator w/ self-feedback
y[n]   = cos( 2*pi*fc*n*Ts + I[n] * y_m[n] )        carrier phase modulation
I[n]   = index * (1 + 0.30*sin(2*pi*0.4*t))          dynamic modulation index (LFO wobble)
```

Per-voice FM roles:

| Voice | GM | fm mult | index | beta | gain | attack | release |
|-------|----|---------|-------|------|------|--------|---------|
| Lead (Pan Flute) | 75 | 1× | 2.0 | 0.15 | 0.52 | 20 ms | 100 ms |
| Counter (Strings) | 48 | 3× | 3.0 | 0.30 | 0.22 | 25 ms | 120 ms |
| Pad (Synth Pad) | 89 | 2× | 1.5 | 0.10 | 0.30 | 80 ms | 150 ms |
| Bass (Fretless) | 35 | 1× | 4.0 | 0.60 | 0.55 | 8 ms | 90 ms |

Percussion (ch10): chaotic feedback FM (beta > 1.6 → deterministic noise bursts):
kick 35 @60 Hz β2.2, low tom 41 @120 Hz β2.0, high tom 50 @220 Hz β2.0, shaker 82 @3000 Hz β3.0, cabasa 69 @5200 Hz β3.0.

### Pitfalls addressed
- Carrier + modulator **phase accumulated continuously** per note (no zipper clicks).
- Feedback recurrence solved **sample-by-sample** (true self-feedback, not vectorized approximation).
- Per-note ADSR; additive per-voice buffers (no crossfade artifacts).
- **DC removal per voice**.
- Post: 20 Hz highpass + 16 kHz lowpass (scipy 4-pole Butterworth), normalize 0.89 peak.
- Seeded (20260828) for reproducibility.

## Pitch verification (SP-035 lesson — MUST report)

- FFT dominant peak per 0.5 s window, 50–1000 Hz: **80/80 frames detected** (100%).
- Detected range: **60–588 Hz**, median **110 Hz** (consistent with D-dorian texture: bass around D2 73.4 Hz, lead/strings in 3rd–5th octaves).
- Note-match (detected peak within 2% of an expected MIDI note freq × 1..4 harmonic): **78/80 windows** (97.5%).
- Harmonic energy in first 8 harmonics of lowest fundamental (D2 = 73.4 Hz): **25.1%** (t0→8 s: 0.21–0.33).
  - Verdict: **PASS** — clearly tonal, not noise. (FM sidebands are inherently spread outside the first 8 harmonics of the *lowest* fundamental; 25% is far above the single-digit noise floor seen in the broken SP-035 v1 at 4%.)

## Silence / RMS

- **Silence ratio: 1.9%** (well under the 30% suspect threshold; the tail pad after the last note is the only near-silence).
- Per-second RMS map (40 s): uniform **0.11–0.14**, no mid-track gaps. Section density (Intro sparse → Chorus dense → Outro sparse) follows the score.

## Artifacts

| File | Size |
|------|------|
| `Audio/SP017-feedback-fm-world-melisma.wav` | 3,572,144 B (mono 44.1 kHz 16-bit, 40.5 s) |
| `Audio/SP017-feedback-fm-world-melisma.ogg` | 800,103 B (Opus 128k) |
| `Audio/stems/stem_lead.wav` | 3,436,168 B |
| `Audio/stems/stem_counter.wav` | 3,528,044 B |
| `Audio/stems/stem_pad.wav` | 3,566,630 B |
| `Audio/stems/stem_bass.wav` | 3,572,144 B |
| `Audio/stems/stem_percussion.wav` | 3,572,144 B |
| `MIDI/SP017-feedback-fm-world-melisma.mid` | source copy (403 B) |
| `provenance.json` | full params + verification |
| `Analysis/render_stats.json` | verification snapshot |
| `Analysis/grid_visualization.txt` | per-bar onset density per voice |

## Notes / next moves
- FM timbres give the modal world texture a bright synthetic sheen; the lead flutes (fm 1×, β0.15) stay breathy-soft while bass feedback (β0.60) adds sawtooth grit.
- Next variable candidates: increase lead index LFO depth for more vocal wobble; stereo-width the pad via detuned dual oscillators; or swap percussion chaos β for a rhythmic carrier to blend with the shaker grid.
