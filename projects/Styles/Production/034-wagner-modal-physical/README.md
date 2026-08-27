# 034 — Wagner Study · Modal Physical Modeling (SP-003)

**Job**: Autonomous production pass (nightly cron)
**Date**: 2026-08-18

## Random Selection

| Slot | Choice |
|------|--------|
| Source composition | `Styles/Classical/033-wagner-study-v2/midi/wagner_poly.mid` |
| Production method | **SP-003 — Modal Physical Modeling (Plate/Bar)** |

## About the source

`wagner_poly.mid` is a 32s, 120 BPM, 4-voice SATB choral study (Soprano / Alto /
Tenor / Bass). 16 entries staggered ~2s apart, each note 2s long, velocity 90.
Timbre source was left open — ideal candidate for physical modeling timbres.

## Method applied (SP-003)

SP-003 simulates physical vibration of struck objects via **modal synthesis**:
each object is a bank of damped resonators (modes), each mode = eigenfrequency +
decay + mode-shape amplitude. MIDI pitch → fundamental `f0 = 440·2^((n−69)/12)`;
each note excites its bank with an impulse and the object rings naturally.

**Engine**: musicom canonical `sound/synthesis/modal.py` (`ResonatorBank`).

### Object assignments (voice → physical object)

| Voice | Object | Mode ratios | Character |
|-------|--------|-------------|-----------|
| Soprano | **Bar (marimba)** | 1 : 4 : 10 : 13.2 : 18.5 | bright, tuned, woody-mallet |
| Alto | **String** | 1 : 2 : 3 : 4 : 5 : 6 | harmonic series, moderate decay |
| Tenor | **Plate** | 1 : 1.73 : 2.83 : 3.61 : 4.58 | inharmonic, slow decay |
| Bass | **Bell** | 0.5 : 1 : 1.2 : 1.5 : 2 : 2.5 : 3 | deep, long, clangorous |

Each voice bank is a modal scaling of its ratio set to the note's fundamental.
Gain per voice normalized to ≈ −6 dBFS, mix normalized to −0.9 dBFS.

## Render health (verify-don't-trust)

- **Silence fraction: 1.3%** ✅ (gate: >30% suspect — first preset-based attempt hit 31.7%, fixed by rebuilding banks with gentle damping so objects ring across the 2s chorale gaps)
- Per-second RMS continuous across all 34s — no dead spans.
- Dur: 34.0s (2s decay tail past last entry). SR 44100, mono int16 WAV.
- OGG (Opus/voip/48k) non-empty, 309 KB.

## Files

```
midi/wagner_poly_source.mid      # original composition (copied)
audio/wagner_modal_SP003.wav     # modal physical modeling render (full)
audio/wagner_modal_SP003.ogg     # Telegram/listening deliverable
provenance.json                  # source + method provenance
README.md
```

## What to listen for

- Each entrance is a struck **physical object**, not a sustained choir note — dry, resonant, decaying.
- Soprano rings like a marimba bar, bass like a deep bell — SATB registers read as four distinct objects.
- Gaps between the staggered entrances stay alive via natural object decay → texture is continuous, never silent.
- Inharmonic plate/bar/bell partials add body the way sustained pads can't.