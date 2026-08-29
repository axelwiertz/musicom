# SP-014 Waveguide Mesh Physical Modeling — 039-marilou-vacation

**Date:** 2026-08-29 (cron production job)
**Method:** SP-014 — Waveguide Mesh Physical Modeling
**Source composition:** 039-marilou-vacation (Country-pop, Dutch lyrics: Marilou, vacation house, swimming pool, bus, forest and heath; 96 BPM, 20 s, verse+chorus)
**Source MIDI:** `/opt/data/projects/Styles/Country/039-marilou-vacation/marilou_verse_chorus.mid`

## Selection

- Method pool: SP-001..SP-056 minus the 23 already realized in `/opt/data/projects/Styles/Production/` → **SP-014** drawn (already realized once on modern_disco — engine reused, new source + per-voice presets).
- Composition pool: random pick from all canonical MIDI under `/opt/data/projects/Styles/` (phase-1 drafts excluded) → **039-marilou-vacation/marilou_verse_chorus.mid** drawn.
- Selection recorded in `/opt/data/projects/Styles/Production/.selection.txt`.

## Source composition

- Style: Country-pop; file tempo **96 BPM** (tempo 625000 µs/beat), 4/4, 20 s, verse + chorus.
- 6 voices (GM program / channel):
  - Lead Flute (73, ch0) — 32 notes, D4–D5 (64–74)
  - Acoustic Guitar strum (24, ch1) — 32 notes, A3–A4 (53–57)
  - Electric Bass (33, ch2) — 32 notes, F2–A3 (38–45)
  - Fiddle hook (110, ch4) — 32 notes, C5–A5 (72–81)
  - Pedal Steel fills (91, ch5) — 32 notes, D4–D5 (64–72)
  - Drum kit (ch9) — 32 notes (kick/snare/hat, pitch 36/38/42)
- 192 note events total, velocity 72 (pitched) / 88 (drums).

## SP-014 implementation

2D waveguide mesh (uniform P-wave mesh, 1-sample delay): each note strikes the
mesh at a pitch-scaled grid size (higher pitch → smaller grid → brighter
marimba/steel-pan ring; lower pitch → larger grid → drum/body), the displacement
wave propagates with clamped (−1 reflection) boundaries, and the pickup reads
the evolving pressure. Pitch is carried by a harmonic-rich decaying excitation
(f0 + 2f0 + 3f0 partials, 40 ms body) injected into the strike region; the mesh
resonator shapes decay and timbre.

Per-voice mesh roles:

| Voice | GM | grid | damping | gain | pan (L/R) |
|-------|----|------|---------|------|-----------|
| FiddleLead | 110 | ~11 (pitch-scaled) | 0.9960 | 1.00 | −0.30 / +0.20 |
| PedalSteel | 91 | ~13 | 0.9972 | 0.90 | +0.30 / −0.20 |
| LeadFlute | 73 | ~11 | 0.9965 | 0.95 | −0.15 / +0.25 |
| AcGuitar | 24 | ~15 | 0.9975 | 0.55 | −0.35 / +0.35 |
| BassBody | 33 | ~19 | 0.9980 | 1.50 | +0.10 / +0.10 |
| MeshBed (drone) | — | 23 | 0.9985 | 0.45 | center |

Drums (ch9) rendered via FluidSynth GM (TimGM6mb.sf2) to keep the country-pop
groove; mesh bed = low A2 drone struck once per bar on a large plate.

### Pitfalls addressed
- Mesh buffers COPIED per step (rebind aliases buffers → divergence).
- Per-note ADSR (attack 4 ms, decay 80 ms, sustain 0.8, release 60 ms) — no clicks.
- Per-note peak normalization → velocity-scaled gain (soft knee).
- Post: musicom MasteringChain (StereoImager 1.15 + Limiter −1.0 dB + LUFS −14).
- OGG via ffmpeg libopus voip 48k; MIDI source copied for DAW.
- Verification built in (SP-035 lesson): FFT pitch check, silence ratio, RMS map.

## Pitch verification (SP-035 lesson — MUST report)

Primary (built-in, on the full mix):
- FFT dominant peak per 0.5 s window, 50–1000 Hz: **45/45 frames detected (100%)**
- Detected range **330–786 Hz**, median **440 Hz** (A4 — matches the country-pop
  register: lead flute/fiddle in 4th–5th octaves, guitar 3rd–4th)
- Note-match (detected peak within 2% of an expected MIDI note freq × 1..4 harmonic): **45/45 (100%)**
- Silence ratio: **6.8%** (all in the 2.5 s tail pad after the last note; see RMS map)
- Per-second RMS: 0.13–0.16 across the 20 s body, tail decays 0.03 → 0.0009 — no mid-track gaps
- Whole-mix harmonic energy in first 8 harmonics of the *lowest* fundamental (D2 = 73.4 Hz): **0.3%** — LOW, but explained below; not a noise indicator here.

Deep verification (supplementary, `verify_pitch.py` + per-stem analysis):
- Autocorrelation pitch frames (SP-035 noise detector) on the full mix: **44/45 frames pitched (98%)**, detected ~52–98 Hz + octave region — clearly periodic, NOT noise.
- Per-voice energy concentration in ±2% bands around each voice's OWN expected
  fundamentals (f0..8f0):
  - FiddleLead **77.6%**, PedalSteel **66.3%**, LeadFlute **62.0%**, AcGuitar **54.3%** — strongly tonal
  - BassBody **29.0%** — lower, by design: the large low mesh is a *modal* resonator (steel-pan/drum-like), so its energy spreads across inharmonic mesh modes rather than stacking on the harmonic series; bass autocorr locks onto the correct pitches (99 Hz = G2, 111 Hz = A2, matching source bass notes 43/45).

**Verdict: PASS** — the render is clearly pitched and tonal. The 0.3% whole-mix
harmonic figure is an artifact of (a) broadband GM drums in the mix and (b) the
modal (deliberately inharmonic) nature of the waveguide mesh — the SP-035
harmonic-energy heuristic assumes a harmonic-stack synthesizer and does not
transfer to modal physical modeling. The autocorrelation (98% pitched frames)
and per-voice note-band concentration (54–78%) are the correct noise detectors
for this method family, and both pass decisively.

## Silence / RMS

- **Silence ratio: 6.8%** (well under the 30% suspect threshold; all silence is the 2.5 s tail pad).
- Per-second RMS (22 s): 0.13–0.16 across the 20 s musical body — no mid-track gaps; final 2 s decay 0.031 → 0.0009.

## Artifacts

| File | Size |
|------|------|
| `Audio/SP014-waveguide-mesh-marilou.wav` | 3,969,044 B (stereo 44.1 kHz 16-bit, 22.5 s) |
| `Audio/SP014-waveguide-mesh-marilou.ogg` | 153,574 B (Opus 48k voip) |
| `Audio/stems/Drums_GM.wav` | 4,454,444 B |
| `Audio/stems/FiddleLead.wav` | 3,969,044 B |
| `Audio/stems/PedalSteel.wav` | 3,969,044 B |
| `Audio/stems/LeadFlute.wav` | 3,969,044 B |
| `Audio/stems/AcGuitar.wav` | 3,969,044 B |
| `Audio/stems/BassBody.wav` | 3,969,044 B |
| `Audio/stems/MeshBed.wav` | 3,969,044 B |
| `MIDI/marilou_verse_chorus.mid` | 1,859 B (source copy) |
| `produce_sp014_marilou.py` | render script (engine + verification) |
| `verify_pitch.py` | deep verification script |
| `provenance.json` | full params + verification |
| `Analysis/render_stats.json` | verification snapshot |
| `Analysis/pitch_verification.json` | deep per-voice analysis |
| `Analysis/grid_visualization.txt` | per-voice density grid |

## Notes / next moves

- The waveguide mesh gives the country-pop tune a marimba/steel-pan sheen:
  fiddle lead rings bright (small grid), bass thumps deep (large grid), pedal
  steel becomes a soft resonant plate — a "vacation jukebox" character that
  fits the Marilou holiday lyric.
- Drums stay GM so the groove reads instantly; a future pass could mesh-render
  the kick too (grid ~23, sub-audio excitation).
- Next variable candidates: raise bass damping to concentrate the fundamental
  (higher harmonic energy for the SP-035 heuristic); add a second pickup point
  per voice for stereo width; or excite the mesh with a noise burst instead of
  the harmonic impulse for a steel-drum "mallet" attack.
