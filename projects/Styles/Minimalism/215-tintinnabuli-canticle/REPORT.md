# REPORT — 215-tintinnabuli-canticle

**Date (UTC):** 2026-10-01
**Style:** Minimalism (Arvo Pärt holy-minimalism / tintinnabuli)
**Method:** 032 Isorhythmic Talea-Color Mapping — `generators.tintinnabuli` (`TintinnabuliGenerator` + `isorhythmize`)
**Seed:** 20261001
**Rework of:** `079-minimalism-isorhythm` (audit: 5/6 musical standards PASS, only index.html missing → identity-preserving extension)

---

## 1. Source Identity (preserved DNA)

| Field | Value |
|---|---|
| Genre | Minimalism (Arvo Pärt holy-minimalism) |
| Key | E natural minor — pcs {0, 2, 4, 6, 7, 9, 11} |
| Tempo | 92 BPM, 4/4, 480 TPB, BAR = 1920 ticks |
| Method | Isorhythmic talea-color mapping + tintinnabuli T-voice |
| Color motif | `[0, 2, 4, 7, 5, 7, 4, 2, 0, -1, -3, -5]` (semitone offsets from E4) |
| Talea | `[1.0, 0.5, 0.5, 1.0, 0.5, 1.5, 0.5, 1.0, 2.0, 0.5, 1.0, 0.5]` (beats) |
| Instrumentation | Viola (M-voice), Cello (T-voice), Violin (pad), Double Bass (drone), Glockenspiel (color), minimal percussion |

## 2. Audit Result

Result of the nightly audit on `079-minimalism-isorhythm`:

| Standard | Result |
|---|---|
| 1. Engine-authored (UnitMatrixComposer) | PASS — no raw mido authoring |
| 2. Zero-drift | PASS — 6 voice tracks, all 46080 ticks |
| 3. Rhythm-grid sync | PASS — 0 off-grid of 396 pitched onsets |
| 4. Valid track setup (≥4 voices) | PASS — 6 voices |
| 5. Two-phase artifacts | PASS — `.mid` + `-phase1.mid` both present |
| 6. provenance.json + index.html | **FAIL** — index.html missing |

**Decision: EXTEND (identity-preserving).** The single failure is a documentation artifact, not a compositional defect — all 5 musical standards pass, so the musical DNA is used as the seed rather than discarding compliant code.

## 3. What Changed — New Longer Form

| | Source (079) | New (215) |
|---|---|---|
| Sections | 6 | **8** |
| Bars | 24 | **32** |
| Voices | 6 | **7** (added canonical Counter violin) |
| Harmonic regions | 6 (repeated i starts) | **8 distinct** (per-section progressions, varied start degrees) |

Section map (each 4 bars):

| # | Name | Progression (start→end) | Start degree | Midpoint root | Variation technique |
|---|---|---|---|---|---|
| 0 | Intro | i i i i | i | i | sparse drone, no drums |
| 1 | TaleaA | i VI III iv | i | III | baseline talea-color (DNA seed) |
| 2 | TaleaB | III iv i VI | III | i | **retrograde** color |
| 3 | Chorus | i III VII i | i | VII | full texture + subtonic VII color |
| 4 | Inversio | iv VI v III | iv | v | **inversion** of color intervals |
| 5 | Augm | VI III iv i | VI | iv | **augmentation** (talea ×2) |
| 6 | Canon | i VI III iv | i | III | **register shift +12** + **canon** counterline |
| 7 | Outro | i i i i | i | i | **diminution** (talea ×0.5), thinning |

## 4. Variation Techniques (8 total, ≥3 required)

1. **Retrograde** — `TaleaB` reverses the color interval order.
2. **Inversion** — `Inversio` negates every color interval (up↔down).
3. **Augmentation** — `Augm` doubles every talea duration (half-speed, broader).
4. **Diminution** — `Outro` halves every talea duration (twice-speed flicker before close).
5. **Register shift** — `Canon` transposes the M-voice up an octave (+12).
6. **Canon / imitation** — `Canon` adds a second violin counterline imitating the M-voice at +2-beat offset, one octave below, re-quantized to its own bars.
7. **Density curve** — percussion density rides 0.0 → 0.4 → 0.6 → 0.9 → 0.7 → 0.5 → 1.0 → 0.3 across sections.
8. **Per-section harmonic regions** — each section has its own short progression with a distinct start degree (i, i, III, i, iv, VI, i, i) and midpoint root (i, III, i, VII, v, iv, III, i), defeating the bar-0-always-tonic bug.

## 5. Two-Phase Architecture

- **Phase 1** — raw isorhythmic talea-color walk (Pan Flute, single voice, unquantized chromatic wander, no harmony). Exported as `-phase1.mid` with its own `validate()` gate.
- **Phase 2** — musicom rules post-process:
  - rhythm grid-lock to the 16th note (120 ticks)
  - chord-tone quantization per bar (diatonic E-minor triads)
  - tintinnabuli T-voice (tonic-triad shadow, pc-restricted to bar chord)
  - voice-leading checks via `rules.voice_leading.VoiceLeadingRules`
  - full 7-voice texture, zero-drift normalization to exact section boundaries

## 6. Verification (real numbers)

| Check | Phase 2 | Phase 1 (raw) |
|---|---|---|
| Voice tracks | 7 | 1 |
| Zero-drift (all tracks equal length) | 7 × 61440 ticks ✓ | 1 × 61440 ✓ |
| Pitched onsets (non-ch9) | 547 | 153 |
| Off-grid onsets | **0** | 0 (raw is grid-snapped to tick boundaries by construction) |
| Scale violations (pc ∉ key) | **0** | 61 (expected — raw unquantized) |
| Chord violations (pc ∉ bar chord) | **0** | 119 (expected — raw unquantized) |
| WAV/OGG silence ratio | 6.1% (safe; <30% trap) | — |
| Peak / RMS | 0.453 / -20.8 dBFS | — |

Size asserts: all MIDI/WAV/OGG > 40 bytes ✓.

## 7. Why It Works (listening guide)

- **Tintinnabuli shadow**: the Cello (T-voice) always answers the Viola (M-voice) with a tonic-triad tone below — the sine qua non of Pärt's sound. On the single subtonic bar (Chorus bar 3, VII=D), the shadow correctly drops to D-major chord tones instead of forcing an E-G-B that would clash.
- **Tension → release**: the Chorus's VII (D major, "dorian" subtonic) is the piece's single harmonic lift off the tonic-triad axis; it resolves immediately back to i.
- **Climax**: the Canon section doubles the motion — octave-shifted melody chased by a canon at the lower octave — at full percussion density (1.0, ride cymbal).
- **Contrast**: Intro and Outro bookend the piece as sparse drones, the Outro's diminution giving a light flicker that evaporates rather than lands hard.

## 8. Next Useful Variable

- Humanization (micro-timing ±, velocity spread) on the M-voice.
- A dorian-mode section that borrows D-major (VII) for a full 4-bar phrase rather than a single bar.
- Bowed-string synthesis production pass (SP-024) to replace the FluidSynth GM render.