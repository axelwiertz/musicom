---
type: instrument
family: Guitar
name: Distortion Guitar
midi_program: 30
gms: "Distortion Guitar"
range_min: 28
range_max: 84
solo_range: [45, 76]
role: [lead, melody, accent, rhythm, power_chord, strum, countermelody]
synthesis: [karplus-strong, phase-mod, additive]
---

# Distortion Guitar

## MIDI / GM

- **Program**: 30 (GM1 Distortion Guitar — solidbody electric guitar pushed
  into HARD tube-amp distortion; Roland GS "Dist Guitar", Yamaha XG
  "DistortionGt"). 0-indexed — matches FluidR3 preset 30 and the
  RenderPipeline `GM_PROGRAMS[30]`. NOT in `structures/instrument.py`
  `MidiInstrument` enum (10 only) — use raw `program=30` in `add_voice`.
- **Channel**: any melodic channel (0-9); polyphonic (6 strings — but hard
  clipping intermodulates chords; power chords and single-note leads are
  idiomatic, never dense full-position chords).
- **Pipeline stem label**: `GM_PROGRAMS[30] = "Distortion Guitar"` →
  `trackXX_Distortion_Guitar.wav` — matches exactly, **no quirk**.
- **FluidR3 SF2 preset**: 30 = "Distortion Guitar" (phdr-verified — labels
  match exactly, no routing impact). Distinct from preset 29 "Overdrive
  Guitar" (the softer sibling).
- **Identity**: GM30 is the high-gain rock/metal guitar — the heavier
  sibling of Overdriven Guitar (GM29). Same physical instrument (solidbody,
  humbuckers, Marshall/JCM-style amp) but driven harder: harder clipping,
  more compression sustain, darker speaker roll-off, tighter palm-muted
  chug. The voice of classic metal rhythm (palm-muted 16ths), hard-rock
  riffing, and screaming single-note leads.

## Range

| Zone | MIDI | Pitches | Register |
|------|------|--------|----------|
| Full range | 28–84 | E1–C6 (GM patch span; real 22-fret guitar = E2–E6 = 40–76) |
| Low strings | 28–47 | E1–B2 — palm-muted power-chord chug roots, low distortion growl |
| Middle | 48–64 | C3–E4 — the distortion sweet spot: power-chord pocket, riff centre, fat leads |
| High | 65–84 | F4–C6 — screaming single-note leads, harmonics, squeal territory |

The GM patch plays the whole 28–84 span (empirical FluidR3 sweep confirms
full audibility, no gaps). Idiomatic writing zone is 40–76 (E2–E6, the real
22-fret neck); the sweet spot is 52–72 (E3–C5) where power-chord chugs and
singing leads have maximum body.

## Timbre DNA

Distortion guitar is defined by **hard clipping (waveshaping saturation)**
applied to the magnetic-pickup electric guitar signal. The high-gain pre-amp
stages introduce strong non-linear distortion that:

- **Compresses the waveform** — sustain extends from ~2 s (clean) to
  10–20+ s (distortion, gain-dependent); the note becomes nearly a flat
  saturated tone while the string rings
- **Folds harmonics up and down** — even AND odd harmonics created by the
  transfer curve; the spectrum fills from ~100 Hz to the speaker cutoff
  (~4–5 kHz) with intermodulation products
- **Darkens the top** — the output transformer and 4x12 speaker roll off
  above ~4 kHz, giving the classic thick "wall" tone (darker than
  overdriven's ~4 kHz shelf — the heavier the gain, the darker the voicing)
- **Intermodulates chords** — non-linear mixing produces sum/difference
  tones, so dense chords smear; root-fifth power chords survive because
  they only contain the fundamental + fifth (no 3rd to beat)

| Parameter | Overdriven (GM29) | Distortion (GM30) |
|-----------|-------------------|-------------------|
| Sustain (s) | 5–20+ (gain-dependent) | 10–20+ (harder compression) |
| Clipping | Soft knee (0.60) | Hard clip (0.85) |
| Harmonic content | Even+odd, folded | Even+odd, folded + denser intermodulation |
| Noise component | Pick + tube hiss (0.060) | Pick + tube hiss + gain-stage noise (0.080) |
| Low-pass | ~4 kHz speaker roll-off | ~3.8 kHz — heavier roll-off, darker |
| Dynamic range | ~15 dB (compressed) | ~10 dB (more compressed) |
| Rhythm signature | Chunky riffs | Tight palm-muted 16th chug |
| Timbre | Saturated, "thick", singing | Hard, "gnarly", aggressive |

## Articulations

| Technique | Velocity | Duration factor | Description |
|-----------|----------|----------------|-------------|
| sustained_lead | 86 | 1.0 | Singing legato line — the default distortion lead, max sustain |
| power_chord | 90 | 0.40 | Root-fifth power chord (no 3rd) — the #1 rhythm technique in rock/metal |
| palm_mute | 58 | 0.10 | Edge-of-hand damped — percussive chug, the metal rhythm engine |
| open_chord | 78 | 0.45 | Full strumed chord — heavily compressed by hard clipping |
| staccato | 68 | 0.12 | Quick muted chord stab — rhythmic accent |
| bend | 96 | 1.30 | Wide string bend — pitch rise + max sustain; the scream-lead signature |
| hammer_on | 80 | 0.60 | Legato slur up — prominent due to sustain |
| pull_off | 70 | 0.60 | Legato slur down — connected line without re-picking |
| slide | 74 | 0.90 | Continuous pitch glide — effective on gain |
| vibrato | 82 | 1.0 | Arm (whammy bar) or finger vibrato — wide and slow on distortion |
| harmonic | 93 | 0.40 | Natural/artificial overtone — bell-like chime, sustained by the amp |
| grace | 72 | 0.10 | Quick pre-note flick — common in rock leads |
| accent | 100 | 0.30 | Emphatic pick dig on a chord stab or accent note |
| feedback | 66 | 1.50 | Sustained note from amp–guitar coupling — controlled squeal |
| tremolo_pick | 84 | 0.25 | Rapid alternate picking (16ths) — the metal rhythm signature |

## Synthesis

### Primary: Karplus-Strong with a HARD distortion stage (sound/synthesis/karplus_strong.py)

Distortion guitar IS a plucked steel string — the core Karplus-Strong
waveguide is the correct physical model. The high-gain amplifier adds a
non-linear waveshaping stage after the waveguide; the distortion stage
clips HARDER than the overdriven entry's soft knee:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| loop_gain | **0.9992** | HIGHEST in the plucked set — hard-clip compression extends sustain to 10–20+ s (overdriven 0.9990, harp 0.9985) |
| excitation | "pick" with noise_component 0.080 | Bright hard pick + tube hiss + gain-stage noise — the highest noise floor in the Guitar family |
| lowpass_hz | **3800** | Heavier speaker roll-off than overdriven 4000 — the darker, thicker distortion voicing |
| saturation | **0.85** | Hard clipping — non-linear waveshaping applied to the output (overdriven 0.60 is soft-knee; distortion is harder) |
| width | 0.50 | Narrower than overdriven 0.55 — compressed string envelope |

### Secondary: PhaseModSynth (sound/synthesis/phase_mod.py)

FM approximation of the distortion: a saw carrier (rich in harmonics) with
the HIGHEST modulation depth in the Guitar family to create the fold-over
distortion:

| Parameter | Value |
|-----------|-------|
| carrier_shape | saw (even+odd harmonics) |
| mod_freq_ratio | 1.0 (fundamental modulation) |
| mod_depth | **4.5** — highest FM depth in the family (overdriven 4.0); harmonic foldover = the scream |
| attack | 0.005 s — fast pick transient |
| release | 0.60 s — longer release due to amp sustain/compression |

### Tertiary: Additive

Harmonic-rich stack with strong even AND odd partials to approximate the
clipped waveform:

```python
ADDITIVE_DEFAULTS = {
    "harmonic_count": 9,
    "harmonic_weights": [0.9, 0.7, 0.85, 0.55, 0.75, 0.45, 0.55, 0.35, 0.3],
    "attack": 0.005,
    "release": 0.60,
}
```

## Production defaults

| Parameter | Value | Notes |
|-----------|-------|-------|
| REVERB_TAIL | 2.4 s | Hall/room — big rock/metal stage; longer than overdriven 2.2 s (the lead screams in space) |
| EQ_BODY | (400, -4.5) | Peaking cut at 400 Hz — reduce box/mud from the distortion harmonic buildup (heavier than overdriven -4.0) |
| EQ_PRESENCE | (2500, 3.0) | Peaking boost at 2.5 kHz — pick attack and chug articulation in the mix |
| EQ_AIR | (5500, 0.5) | High shelf at 5.5 kHz — gentle top, NOT shrill; the amp speaker has already rolled off above ~4 kHz |
| PAN | -0.15 | Centre-left for the mono stage amp; stereo double-track at +0.15 |

## RenderPipeline stem-label quirk

**No quirk.** `GM_PROGRAMS[30] = "Distortion Guitar"` → sanitized filename
`Distortion_Guitar`. FluidR3 preset 30 = "Distortion Guitar" (phdr-verified)
— labels match exactly. `STEM_LABEL = "Distortion_Guitar"`.

## FluidSynth / SF2 notes

FluidR3_GM.sf2 preset 30 = "Distortion Guitar" — a high-gain distorted
guitar sampled through a 4x12 cab. The patch is audible across the full
28–84 range with no gaps (empirical sweep). The sample set includes:

- Multi-velocity layers with natural gain-staging — the harder you play the
  MIDI, the higher the gain layer (clean-ish → crunch → saturated)
- Heavily compressed sustain — notes ring long at high velocity
- Baked-in amp noise floor (~−50 dB tube hiss)

**Performance tip**: velocities ≤ 50 trigger the cleaner/crunch layer
(pre-breakup); velocities 60–100 trigger the classic distortion tone;
velocities ≥ 110 push the patch to the highest gain layer — sustain
increases but note separation decreases (the amp squashes everything). For
mixing, write main lines at vel 75–90 and accents at 95–100. Palm-muted
chug reads best at vel 55–70 (the damped layer stays articulate).

## Identity

GM30 = Distortion Guitar — the iconic heavy rock/metal instrument. The
physical reality is a solidbody electric guitar (typically humbucker
pickups — Gibson Les Paul, SG, PRS) pushed into a high-gain tube amp
(Marshall JCM800, Peavey 5150, Mesa Boogie — the metal lineage).

The distortion guitar is **fully polyphonic** (6 strings) but hard clipping
intermodulates chords, so the *idiomatic* writing is:

- **Single-note leads**: the quintessential distortion voice — sustaining,
  singing, harmonic-rich. Bends, vibrato, hammer-ons/pull-offs, feedback
  squeals — the amp amplifies every nuance.
- **Power chords** (root-fifth only, no 3rd): the #1 rhythm texture in
  rock, punk, metal. Elastic, chunky, cut through the mix.
- **Palm-muted 16th-note chugs**: the metal rhythm engine, performed on the
  low E and A strings (vel ~55–70, short durations — the
  `palm_mute`/`tremolo_pick` articulations).
- **Open/full chords**: use VERY sparingly on distortion — intermodulation
  makes dense chords a washy smear. Keep harmony sparse.

Line-instrument quirks:

- Distortion compression reduces dynamic range to ~10 dB. Write crescendos
  with note density (more notes per bar) rather than velocity marks.
- The distorted tone has a natural high-pass character — the low E (41 Hz)
  is weak on distortion due to the speaker roll-off. Keep main lines above
  MIDI 40 (E2).
- Palm-muted rhythm is written as 8th/16th patterns with short durations —
  the MIDI note-off divides the sample's chug attack.
- Feedback is a REAL distortion-only articulation (the note sustains from
  amp–guitar coupling, not from the string) — write it as a long note at
  vel 60–70 with `feedback` duration 1.5.

## Verification

- GM30 → stem `trackXX_Distortion_Guitar.wav` (labels match exactly — no
  quirk; FluidR3 preset 30 = "Distortion Guitar" phdr-verified)
- Zero-drift: units end flush at BAR (terminal landmark)
- Solo render only (no unison doubling — comb-filtering buzz rule applies if
  a second melodic patch plays the same line)
- Spectral 4–8 kHz buzz gate: distortion DOES add genuine high harmonics —
  the gate still applies (it is the comb-filter check, not a brightness
  limit); distortion energy is spread across the band, not a narrow buzz
- Karplus-Strong smoke test: high loop_gain 0.9992 ring clearly above the
  0.990 dull control — the hard-clip compression sustain
- Empirical FluidR3 pitch sweep: preset 30 audible across the full 28–84
  span, no gaps — SF2 never clips a composition
