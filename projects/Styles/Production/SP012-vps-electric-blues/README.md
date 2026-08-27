# SP-012 — Vector Phase Shaping (VPS) — Electric Blues

**Autonomous production pass (nightly cron job).**

## Source

| Field | Value |
|---|---|
| Composition | `039-electric-blues` (Blues) |
| Source MIDI | `midi/daily-2026-06-27_blues_039-electric-blues-v5.mid` |
| Notes | 144, single track, program 30 (distortion guitar), pitch 52–60 |
| Duration | ~36 s |
| Tempo | 80 BPM (default 750000 µs/beat) |

## Method — SP-012 Vector Phase Shaping (VPS)

From `methods_db.md`:

> **SP-012** | Vector Phase Shaping (VPS) | **Synthesis Engines** |
> Dynamic/Harmonic Brass & Digital Timbres | Synthesis modifying phase
> distortion speed via dynamic vectors. Creates expressive sweeps and
> complex sidebands.

### Implementation

Every blues note is rendered through a **Vector Phase Shaping** engine:

1. **Carrier phase accumulator** drives a saw wavetable (2·φ − 1).
2. **Dynamic distortion vector K(t)** — the phase-distortion *speed* is
   modulated by a slow LFO sweep (`sweep_rate = 0.6 Hz`, `sweep_depth = 1.6`),
   so the spectral brightness of each note *sweeps and wavers* over its
   duration instead of staying static. This is the "dynamic vectors /
   expressive sweeps" character of the method.
3. **Phase-distortion warp** applies an S-curve `|2φ−1|^power` (power = 1.5)
   scaled by K(t), trading smooth glassiness for an overdriven, vocal edge.
4. **PM sideband modulator** (ratio 2.0, index 0.9) injects inharmonic
   sidebands — the "complex sidebands" of the method — giving the lead a
   living, slightly detuned chorus-like shimmer.
5. A 1-sample moving average softens aliasing; an ADSR (4 ms attack,
   80 ms decay, 0.72 sustain, 100 ms release) shapes each note.

### Mix stage

- Velocity → gain mapping (prog-30 guitar dynamics preserved).
- Per-note pan spread across the stereo field with a slow cyclic motion
  (blues swagger).
- **Soft-knee saturator** (threshold 0.82, slope 0.35) for overdrive warmth.
- **Freeverb** algorithmic reverb (room 0.55, damping 0.5, wet 0.22, width 0.8)
  for space.
- Peak normalize to **−1 dBFS**.

## Outputs

| Artifact | Path |
|---|---|
| WAV (stereo 44.1 kHz) | `Audio/SP012-electric-blues-vps.wav` |
| OGG (Opus 48k voip) | `Audio/SP012-electric-blues-vps.ogg` |
| Source MIDI (copy) | `MIDI/daily-2026-06-27_blues_039-electric-blues-v5.mid` |
| Render info (JSON) | `Analysis/render_info.json` |
| Provenance | `provenance.json` |

## Listen for

- **Expressive sweep**: each note's brightness swells and relaxes (the VPS
  dynamic vector) — most obvious on the held bends.
- **Sideband shimmer**: the PM modulator adds a subtle detuned chorus, denser
  on the upper pitches (57–60).
- **Overdriven vocal edge**: the phase-distortion S-curve warps the saw into a
  dirty, horn-like guitar voice fitting the 12-bar blues.

## Quality gate

- Silence fraction: **4.5%** (well under 30% suspect threshold — no
  silent-render trap).
- WAV 6.79 MB, OGG 277 KB — both non-empty and valid.
- `assert os.path.getsize(...) > 1000` passed for both outputs.