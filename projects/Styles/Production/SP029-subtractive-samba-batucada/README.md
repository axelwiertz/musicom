# SP-029 Subtractive Synthesis — Production Pass

**Job:** Autonomous daily production pipeline (`9a2813f77dac`)
**Run type:** Random composition × random sound-production method

## Selection (this run)

| Item | Value |
|------|-------|
| Source composition | **Samba Batucada** (daily 2026-06-18, Latin / Samba) |
| Source MIDI | `/opt/data/projects/Styles/Latin/samba-batucada-daily-2026-06-18/composition.mid` |
| Production method | **SP-029 — Subtractive Synthesis with PolyBLEP Anti-Aliased Oscillators and Analog Filter Emulation** |

## Source analysis

The composition is a **2-voice UnitMatrix** (Surdo + Agogo), 120 BPM, 7-sixteenth bar:

| Voice | MIDI | Pattern (per loop) |
|-------|------|--------------------|
| Track 1 — Surdo/kick | 36 (C2) | 6 hits on sixteenths 0, 1, 2, 3, 6, 7 (metrical gravity on beat 2) |
| Track 2 — Agogo bell | 64 (E4) | 14 hits, every sixteenth (0.125 s per hit) |

Each loop = 0.875 s. The production renders **8 loops = 7.0 s** delivery loop.

## Method applied (SP-029)

Signal flow per voice: **PolyBLEP oscillator(s) → mixer → Moog 4-pole ladder (envelope-modulated cutoff) → VCA (ADSR)**, per the reference implementation in `methods_db.md` (lines 4408–4646).

- **PolyBLEP anti-aliasing**: polynomial band-limited step correction subtracted at
  the saw reset and at both square edges — kills the fold-back aliasing a naive
  oscillator would produce on the high E4 agogo ring (~60 dB suppression to ~10 kHz
  at 44.1 kHz per the method notes).
- **Moog ladder filter**: 4 cascaded one-pole stages (trapezoidal integration,
  `alpha = pi*fc/fs`) with global feedback resonance and per-stage `tanh` saturation
  (Cemple-style) for the classic analog warmth.

### Voice design

| Voice | Oscillator | Filter | Envelope |
|-------|-----------|--------|----------|
| **Kick (surdo)** | sine + pitch envelope 120→40 Hz (tau 35 ms) | — (none needed) | A 2 ms / D 160 ms / S 0 / R 50 ms |
| **Agogo (E4)** | 2× PolyBLEP square, PW 0.25, unison detune ±7 cents | Moog ladder, res 1.8, beta 1.6, fc sweep 900 Hz + 9000 Hz depth (open→close "dong"→ring) | A 1 ms / D 100 ms / S 0.30 / R 90 ms |

### Mix

- `0.9 × agogo + 1.0 × kick` → `tanh(1.5x)` soft-saturation glue → peak-normalized to **-1 dBFS**.
- Loop seams crossfaded (5 ms) to avoid clicks.

## Output artifacts

| File | Description |
|------|-------------|
| `MIDI/original.mid` | Source composition (unedited, for reference) |
| `Audio/SP029-samba-batucada-subtractive.wav` | Final full mix (7.0 s, 44.1 kHz mono) |
| `Audio/SP029-samba-batucada-subtractive.ogg` | Final mix, Opus 48k voip (delivery format) |
| `Audio/stem_kick_surdo.wav` | Kick/surdo stem only |
| `Audio/stem_agogo_polyblep.wav` | Agogo bell stem only |
| `provenance.json` | Source SHA-256 + synthesis parameters |
| `Analysis/grid_visualization.txt` | Rhythm DNA grid |
| `produce_sp029.py` | Reproducible production script |

## Render chain

```
composition.mid --(mido analysis)--> event map (kick 36, agogo 64, 7x16th bar @120)
event map --(PolyBLEP squares + sine, Moog ladder, ADSR)--> stems
stem_kick + stem_agogo --(tanh glue, -1 dBFS)--> full_mix.wav
full_mix.wav --(ffmpeg libopus 48k voip)--> full_mix.ogg
```

## Verification

- All WAV/OGG files non-empty (> 40 bytes).
- Duration: 7.006 s @ 44.1 kHz (all outputs).
- Peak: **-1.0 dB** (mix), mean -10.7 dB — healthy headroom, no clipping.
- Stems: kick RMS 0.199 / peak 0.898; agogo RMS 0.168 / peak 0.568; both fully
  populated (no silence).
- `provenance.json` written with source + output metadata.

## Listen guide

- **agogo stem alone**: the PolyBLEP square through the Moog sweep is the giveaway —
  it starts bright (filter open ~9.9 kHz), then the cutoff closes over ~90 ms,
  leaving a ringing E4 with analog saturation warmth. Compare with a GM bell patch:
  no aliasing artifacts, fatter attack.
- **kick stem alone**: sine pitch envelope 120→40 Hz = classic surdo thump,
  matching the composition's "heavy surdo emphasis" DNA note.
- **full mix**: the 7-sixteenth groove (agogo constant 16ths + surdo on 0,1,2,3,6,7)
  locks into a driving batucada pulse; the tanh glue adds a touch of analog
  saturation on the transient peaks.

## Method notes

- SP-029 is the **subtractive complement** to additive (SP-024): start rich (harmonics),
  sculpt with filters. Here the agogo's square harmonics are the "rich" source and the
  Moog sweep is the sculpting.
- Per integration notes: resonance 1.8 / beta 1.6 keeps the ladder stable (k < 4)
  while still self-warming; unison detune (±7 cents, 2 osc) widens the bell.
