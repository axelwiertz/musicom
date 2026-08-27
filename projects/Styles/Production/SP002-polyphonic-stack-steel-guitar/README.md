# SP-002 — VST3 Polyphonic Stacking · Steel Guitar Demo

**Production pass:** 2026-08-13 (autonomous nightly cron)
**Source composition:** `Country/038-steel-guitar-demo/daily-2026-06-26_country_038-steel-guitar-v5.mid`
**Method:** [SP-002 — VST3 Polyphonic Stacking](../../Research/CompositionMethods/methods_db.md)

---

## Method (from methods_db.md)

> **SP-002 | VST3 Polyphonic Stacking | Synthesis Engines | Multi-Instrument Render**
> "Renders voices independently through virtual instruments, then sums outputs in NumPy."

**Environment adaptation:** No VST3 plugins or DawDreamer are available in this headless
environment (verified: `dawdreamer` not installed, no `.vst3` files on disk). The method's
*spirit* is preserved exactly — **independent per-voice virtual-instrument rendering,
summed in NumPy** — by using the musicom `sound/` synthesis engines as the virtual
instruments:

| Voice | MIDI pitch(es) | Virtual instrument (engine) | Character |
|-------|---------------|-----------------------------|-----------|
| Low (left) | D4 (62) | `BowedString` (SP-024 friction waveguide) | Sustaining cello-like foundation, legato-filled rests |
| Mid (center) | E4 (64) | `ResonatorBank` (SP-003 modal) | Plucked modal resonance, decay 4 s |
| High (right) | G4 (67) | `PhaseModSynth` (SP-010 FM-style) | Soft bell bloom, ratio 1.0, depth 0.8 |

## Source material

- 80 BPM, 4/4, 12.0 s, single track (program 42), **32 notes**, all 0.188 s 16th notes,
  velocity 80, pitches D4/E4/G4 — a picked steel-guitar-style melodic cell, repeated.
- Pitch-based voice allocation: D4 → Low (16 notes), E4 → Mid (12 notes), G4 → High (4 notes).

## Pipeline

1. Parse source MIDI with `mido` (read/analyze only — no authoring).
2. Split notes by pitch register into 3 voices.
3. Render each voice **independently** through its own synthesis engine.
4. **Sum in NumPy** with per-voice gain + fixed stereo pan (L / C / R).
5. Mix: soft-knee saturation → `AlgorithmicReverb` (Schroeder/Moorer, room 0.65,
   wet/dry 0.28) → peak normalize −1 dBFS.
6. Write stereo WAV → Opus OGG (48 kbps, voip profile).

### Silent-render trap fix (SP-011 lesson applied)

First render hit **51.3% silence** — the source's structural rests (16th-note pick
pattern, ~50% duty cycle) plus decaying-only synthesis left gaps. Fixed by:
- **Legato extension** in the sustaining voices (bowed string holds until next onset).
- **Longer decays** in pluck (0.9 s) and bell (up to 1.5 s).
- **Algorithmic reverb** tail (2 s) to fill and glue.
- Result: **3.8% silence** — healthy. (After DC fix re-render: 9.0% — the 45 Hz HPF
  trims subsonic rumble; still well under the 30% gate.)

## Outputs

| File | Path |
|------|------|
| Full mix WAV | `Audio/SP002-polyphonic-stack-steel-guitar.wav` (2.4 MB, 13.62 s) |
| Full mix OGG | `Audio/SP002-polyphonic-stack-steel-guitar.ogg` (108 KB, Opus 48 kHz stereo) |
| Original MIDI | `MIDI/daily-2026-06-26_country_038-steel-guitar-v5.mid` |
| Render info | `Analysis/render_info.json` |
| Producer script | `produce_sp002.py` |

## Quality gate

- Silence fraction: **0.090** (threshold < 0.30) ✓
- Per-second RMS: −11 to −12 dBFS flat, reverb tail −43 dB ✓ (no dead zones)
- Peak: 0.950 / 0.739 (−0.4 / −2.6 dBFS) ✓
- **DC offset: 0.03 / 0.03 (was +11516 / +6027)** ✓ — fixed by final-stage 45 Hz HPF
- Peak: 0.743 (−2.6 dBFS) ✓
- Spectral balance: fundamentals present (D4 293.7 Hz amp 106), harmonics decay
  (x2 69.8, x3 21.4), dominant 578 Hz (D4×2) — warm plucked-string character ✓
- WAV 2.4 MB, OGG 108 KB — both > 1 KB ✓
- OGG verified playable via ffprobe (opus, 48 kHz, stereo, 13.63 s) ✓

## Listen for

1. The **bowed-string low voice** holding D4 legato underneath — the "pedal" of the steel part.
2. The **modal pluck** (E4) giving each 16th its attack bite, center-panned.
3. The **bell bloom** (G4) landing on the phrase high notes, right-panned.
4. How the three engines stack into one instrument: attack from the pluck, sustain from
   the bow, sparkle from the bell — the SP-002 polyphonic-stack concept in one texture.

## Next moves (if iterating)

- Add a fourth voice (bass register below D4) to thicken the low end.
- Velocity humanization (SP-006) on top of the stack for a less mechanical 16th grid.
- Spectral masking EQ (SP-007) to carve the pluck's 2–4 kHz against the bell.
