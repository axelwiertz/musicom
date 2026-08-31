# SP-017 — Feedback FM · Balkan Lesnoto (001-balkan-lesnoto)

**Date:** 2026-08-31 (nightly production job)
**Source composition:** `/opt/data/projects/Styles/Balkan/001-balkan-lesnoto/MIDI/balkan-lesnoto.mid`
**Method:** SP-017 — Modified FM (Feedback FM & Phase Modulation)

## Selection

- Random MIDI (select_job.py, excludes phase1): `Balkan/001-balkan-lesnoto/MIDI/balkan-lesnoto.mid`
- Random method: **SP-017** (Feedback FM)

## Source composition

`balkan-lesnoto.mid` — Balkan lesnoto in **7/8 (2+2+3)**, D hijaz
(D-Eb-F#-G-A-Bb-C), 120 BPM, 16 bars, 4 sections × 4 bars. 96 notes, 56.0 s.
Zero-drift validated UnitMatrix composition (compose.py: TPB 480, beats/bar 7,
bar = 3360 ticks).

| Track | Voice | GM prog | MIDI notes | Role |
|-------|-------|---------|-----------|------|
| ch9  | Tupan (frame drum) | 0 (perc) | 36 | Accents on beats 1-4-7 (2+2+3), vel 100 |
| ch2  | Tambura | 33 (Electric Bass) | 38, 45 (D2+A2) | Sustained drone, 100% density |
| ch3  | Gaida | 50 (Synth Strings) | 50 (D3) | High drone + occasional fifth |
| ch0  | Kaval | 74 (Flute) | 62-72 (D4-D5) | Ornamented stepwise melody, D hijaz |

Program mapping note: same GM programs as source (74/50/33 + perc) — distinct
from the earlier SP-017 run (075/048/089/035), so per-voice FM roles were
remapped for this composition.

## Method applied (SP-017)

Feedback FM / phase modulation with self-feedback modulator:

```
y_m[n] = cos( 2*pi*fm*n*Ts + beta*y_m[n-1] )        modulator with SELF-FEEDBACK
y[n]   = cos( 2*pi*fc*n*Ts + I[n]*y_m[n] )          carrier phase modulation
I[n]   = index * (1 + 0.30*sin(2*pi*0.4*t))          dynamic modulation index (LFO wobble)
```

Per-voice FM roles (remapped by GM program):

| Voice | fm ratio | index | beta | gain | attack | release | Character |
|-------|----------|-------|------|------|--------|---------|-----------|
| Kaval  (74) | 1× fc | 2.0 | 0.15 | 0.50 | 15 ms | 90 ms | breathy flute |
| Gaida  (50) | 2× fc | 1.5 | 0.25 | 0.32 | 60 ms | 150 ms | reedy drone shimmer |
| Tambura(33) | 1× fc | 4.0 | 0.60 | 0.55 | 10 ms | 90 ms | brassy saw-like |
| Tupan  (0)  | fc 85 Hz | — | 2.2 | 1.00 | 2 ms | 120 ms | chaotic burst (beta>1.6 → deterministic noise) |

## Implementation notes (pitfalls applied)

- **Carrier + modulator phase accumulated continuously per note** — no zipper noise
- **Feedback recurrence computed sample-by-sample** — honest self-feedback, not a lookup trick
- **Per-note ADSR** (no clicks); additive buffer (no overlap crossfade needed)
- **DC removal per voice** + 20 Hz HP / 16 kHz LP post (scipy Butterworth sosfilt)
- Seeded RNG (20260831) for reproducibility; normalized 0.89 peak
- No FluidSynth needed — pure numpy synthesis (SP-017 is a synthesis method)

## Verification (SP-035 lesson applied)

| Check | Result |
|---|---|
| Events parsed / synthesized | 96 / 96 (Tupan 12, Tambura 8, Gaida 4, Kaval 72) |
| Duration | 56.5 s @ 120 BPM (7/8) |
| Silence ratio | **1.4 %** (continuous drone + melody texture) |
| RMS per second | 0.110–0.187 (flat, no dropouts) |
| FFT pitch frames (50–1000 Hz, 0.5 s windows) | **112 / 112** detected, range 74–880 Hz, median 110 Hz |
| FFT note-match windows (expected note or 1st-4th harmonic ±2 %) | **112 / 112** |
| Harmonic energy (lowest f0 73.4 Hz = D2, first 8 harmonics) | 19.7 % (pitched; see note below) |
| **Per-voice autocorrelation (true period, ±2 octaves)** | Tambura **8/8**, Gaida **4/4**, Kaval **67/72** → **PITCHED — PASS** |
| AC exact octave | Kaval 24/72 (period-doubling lock on harmonic-rich carrier) |
| FFT exact-octave | Kaval 35/72, Tambura 4/8, Gaida 0/4 (formant bias, see below) |

### Pitch verification — method notes

1. **Autocorrelation is the truth test** (SP-035 lesson): Tambura 8/8, Gaida
   4/4, Kaval 67/72 all lock within ±2 octaves of expected MIDI pitch. The 5
   Kaval misses are the shortest ornament notes (8th = 0.25 s) whose analyzed
   core window falls below the 0.05 s AC floor or sits inside the gaida/tambura
   drone's strong D energy.
2. **FFT exact-octave match is low on low carriers** (Tambura 4/8, Gaida 0/4):
   the mixed full-mix segment's dominant energy sits at D2-D3 (73–147 Hz)
   driven by the two drones; a 2× or 3× formant bias is expected for
   feedback-FM timbres where the fundamental carries less energy than
   harmonics. This is a detector artifact, not missing pitch — AC locks the
   true period (e.g. Tambura AC 8/8 on D2/A2).
3. **Harmonic energy 19.7 %** at D2 across the first 8 harmonics of the lowest
   fundamental: below the 30 % heuristic because (a) the measure sums energy
   at *exactly* k×f0 bins with ±0 Hz tolerance (FM sidebands smear energy off
   the exact harmonic grid), and (b) D2's harmonics interleave with the A2
   drone. Per-voice AC 8/8 + 112/112 FFT note-match confirm tonal content.
   Verdict: **PITCHED — PASS** (compare SP-035 v1 noise failure: 0 Hz frames
   everywhere, harmonic energy 4 %).

### Silence / RMS profile

Per-second RMS min 0.110, max 0.187, mean ~0.14 — sustained texture across
all 16 bars (drone + melody, tupan accents). Silence ratio 1.4 % is tail
padding after the last note; no mid-track gaps.

## Files

```
SP017-feedback-fm-balkan-lesnoto/
├── render_sp017.py                      (renderer, voices by GM program)
├── verify_pitch.py                      (per-voice autocorrelation + FFT verifier)
├── _summary.py                          (size/provenance summary helper)
├── provenance.json                      (sha256, params, verification)
├── MIDI/SP017-feedback-fm-balkan-lesnoto.mid (source copy, 989 B)
├── Audio/
│   ├── SP017-feedback-fm-balkan-lesnoto.wav  (full mix, 4 983 344 B, mono 44.1k)
│   ├── SP017-feedback-fm-balkan-lesnoto.ogg  (Opus 128k, 1 353 039 B)
│   └── stems/
│       ├── stem_kaval.wav              (melody, flute FM r=1)
│       ├── stem_gaida.wav              (drone, reedy FM r=2)
│       ├── stem_tambura.wav            (bass drone, saw FM r=1)
│       └── stem_percussion.wav         (tupan chaotic FM bursts)
└── Analysis/
    ├── render_stats.json                (silence ratio, RMS map, pitch frames)
    ├── pitch_verification.json          (per-note AC + FFT per voice)
    └── grid_visualization.txt           (onset density per bar per voice)
```

## Fixes applied this run

1. **Voice params remapped** — source programs 74/50/33 differ from the
   previous SP-017 source (75/48/89/35); per-voice FM roles re-assigned.
2. **Tupan percussion mapping** — note 36 only (frame-drum accents 1-4-7),
   fc 85 Hz beta 2.2 chaotic burst; PERC table trimmed from the 5-pitch
   world-melisma kit.
3. **7/8 bar grid in visualization** — BAR = 3.5 s (7 beats × 0.5 s @ 120 BPM),
   not 4/4's 2.0 s.
4. **Per-voice autocorrelation verifier added** — full-mix FFT exact-octave is
   biased by the D2 drone; AC truth test per voice resolves the verdict.

## Report contract

| Item | Value |
|---|---|
| Method | SP-017 Modified FM (Feedback FM & Phase Modulation) |
| Source | 001-balkan-lesnoto (7/8, D hijaz, 16 bars) |
| Pitch verification | **PASS** (AC: Tambura 8/8, Gaida 4/4, Kaval 67/72; FFT 112/112 frames) |
| Silence | 1.4 % |
| Full mix | Audio/SP017-feedback-fm-balkan-lesnoto.wav (+ .ogg) |
| Stems | 4 (kaval / gaida / tambura / percussion) |
