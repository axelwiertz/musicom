# 079-minimalism-isorhythm — Minimalism / Method 032 Isorhythmic Talea-Color Mapping

**Style:** Minimalism (Pärt holy-minimalism) · **Method:** 032 Isorhythmic Talea-Color Mapping (TintinnabuliGenerator)
**BPM:** 92 · **Key:** E natural minor · **Bars:** 24 · **Sections:** Intro, Mvt1, Mvt2, Mvt3, Mvt4, Outro (4 bars each)

## Concept
Arvo Pärt-style holy minimalism: a conjunct M-voice (stepwise, mode-bound) is
shadowed by a T-voice that only ever uses tones of the E-minor tintinnabuli
triad (E-G-B). The isorhythmic engine cyclically maps a repeating pitch *color*
onto a repeating duration *talea* (coprime lengths → pitch and rhythm never
lock into a static pattern). Phase 1 runs the raw isorhythmic walk; Phase 2
resolves it onto a diatonic E-minor progression with tintinnabuli doubling,
strict chord-tone quantization, and voice-leading rules.

## Two-Phase Pipeline
- **Phase 1** (`MIDI/079-minimalism-isorhythm-phase1.mid`): raw single-voice
  isorhythmic draft. Pitches = color offsets + chromatic register wander
  (unquantized); rhythm = talea durations (fractional, off-grid). No harmonic
  context, no bass, no drums. Audibly a floating, breathing solo line.
- **Phase 2** (`MIDI/079-minimalism-isorhythm.mid`): rules post-process. Every
  phase-1 event (1) grid-locked to the 16th grid (120 ticks @ 92 BPM),
  (2) snapped to E-natural-minor mode degrees (M-voice conjunct tendency),
  (3) chord-quantized to the bar's diatonic chord using GLOBAL bar lookup,
  (4) leap-capped <= 9 semitones, then a full minimalist texture:
  M-Voice (Viola 41), T-Voice (Cello 42, E-G-B triad ∩ bar-chord), sustained
  organum pad (Violin 40, bar root+fifth), double-bass root drone (43),
  Music-Box bells (9, bar chord tones), soft pulse percussion.

## Voices
M-Voice(41), T-Voice(42), Violin(40), DblBass(43), Bells(9), Drums(ch9)

## Progression (24 bars)
i VI III iv | i VI III iv | i VI III V | i VI iv V | i VI III iv | i III iv i

## Artifacts
- `MIDI/079-minimalism-isorhythm.mid` + `MIDI/079-minimalism-isorhythm-phase1.mid` (both with provenance sidecars)
- `Audio/079-minimalism-isorhythm.ogg` / `.wav` + phase1 renders
- `Analysis/grid_visualization.txt`, `Analysis/summary.json`
- `compose.py` (engine-only, preflight-clean), `REPORT.md`

## Verification (see REPORT.md)
- Phase1 validate: OK · Phase2 validate: OK
- Grid audit: **0 off-grid** on every voice (16th=120 AND 8th=240)
- Harmony audit: **0 out-of-scale, 0 out-of-chord** on every pitched voice
- Silence: 13.3% (mix) / 3.4% (phase1) — no silent-WAV trap
- FFT pitch verify: 144/144 tonal frames (196Hz=G3, 66Hz=E2 drone, 392Hz=G4)
- Preflight: exit 0 (compliant, no raw-MIDI)
