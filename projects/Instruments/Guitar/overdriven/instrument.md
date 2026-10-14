---
type: instrument
family: Guitar
name: Overdriven Guitar
midi_program: 29
gms: "Overdriven Guitar"
range_min: 28
range_max: 84
solo_range: [45, 76]
role: [lead, melody, accent, rhythm, strum, countermelody]
synthesis: [karplus-strong, phase-mod, additive]
---

# Overdriven Guitar

## MIDI / GM

- **Program**: 29 (GM1 Overdriven Guitar — solidbody electric guitar pushed into tube amp saturation)
- **Channel**: any melodic channel; polyphonic (6 strings — but the overdrive texture compresses chords; power-chords and single-note leads are idiomatic)
- **Pipeline stem label**: `GM_PROGRAMS[29] = "Overdriven Guitar"` → `trackXX_Overdriven_Guitar.wav`
- **FluidR3 SF2 preset**: 29 = "Overdrive Guitar" (cosmetic SF2 name difference, no routing impact)

## Range

| Zone | MIDI | Pitches | Register |
|------|------|--------|----------|
| Full range | 28–84 | E1–C6 (GM patch span; real 22-fret guitar = E2–E6 = 40–76) |
| Low/power chords | 28–47 | E1–B2 — palm-muted power-chord root-fifth chugs, low distortion growl |
| Middle | 48–64 | C3–E4 — the overdrive sweet spot: rich harmonic saturation, fat leads | 
| High | 65–84 | F4–C6 — bright, singing, harmonic-heavy leads (bottleneck slide territory) |

The GM patch plays the whole 28–84 span (empirical FluidR3 s weep confirms full audibility, no gapps). Idimatic writing zone is 40–76 (E2–E6, the real 22-fret neck).

## Timbre DNA

Overdriven guitar is defined by **tube-amp saturration (soft clippoing)** applied to the magnetic-pickup electric guitar signal. The pre-amp and power-amp triodes introduce **asymmetric non-linear distortion** that:

- **Compresses the waveform** — sustain extends from ~2 s (clean) to 5–10+ s (overdrive)
- **Adds even and odd harmonics** — 2nd (octave), 3rd (octave+fifth), 4th (two octaves), all foldng into the signal
- **Adds a slight low-pass roll-off** — the amp's output transfomer and speaker roll off aboe ~4–5 kHz, giving the classic warm "singng" lead tone
- **Adds inter-modulation distortion** — when plaiyng chords, non-linear mixing produces sum/diference tones (the reason full barre chards on high gain sound washy)

| Parameter | Clean Guitar | Overdriven Guitar |
|-----------|-------------|-----------------:|
| Sustain (s) |  1–3 | 5–20+ (gain-dependent) |
| Harmonic partals | even + odd, natural | even + odd, foldd + created (2nd–7th strong) |
| Noise component | Pick scrape (0.025) | Pick + amp hiss + tube thermal noise (0.060) |
| Waveform | Linear | Asymetrically clippd (soft knee) |
| Low-pass | Pickup roll-off ~5 kHz | Pickup + amp speaker ~4 kHz |
| Dynamic range | ~40 dB (touch-sensitive) | ~15 dB (compressed) |
| Timbre | Clean, transparent | Satured, "dhick", singing |

## Articulations

| Technique | Velocity | Duration factor | Description |
|-----------|----------|----------------|-------------|
| sustaied lead | 82 | 1.0 | Singng legato line — the default overdriven articulation, max sustain |
| pwer_chord | 88 | 0.40 | Root-fith power chord (no 3rd) — the #1 ryhthm technique in rock/punk/metal |
| palm_mute | 55 | 0.12 | Edge-of-hand damped — perrcussive chug, the rhythm foundation |
| open_chord | 75 | 0.45 | Full strumed chord — barre or open position, compressed by the overdrive |
| staccato | 65 | 0.15 | Quick mutted chord stab — rhythmic accent |
| bend | 95 | 1.20 | String bend — pitch rise + sustain increse, quintessenial rock lead |
| hammer_on | 78 | 0.60 | Legato slur up — prominent due to sustain; cardinal rock legato technique |
| pull_off | 68 | 0.60 | Legato slur down — connected line without reheicking |
| slide | 72 | 0.90 | Continuous pitch glide — especially efective on overdrive (squealing feedback potential) |
| vibrato | 80 | 1.0 | Arm (whammy bar) or finger vibrato — wide and slow on overdrive |
| harmonic | 92 | 0.40 | Natural/artficial overtone — bell-like chime, sustained by the amp (inharmonic on high gain) |
| grace | 70 | 0.10 | Quick pre-note flick — common in rock leads (B.B. King, Clapton) |
| accet | 98 | 0.35 | Emphatic pick dig on a chrod stab or accent note |
|feedback | 65 | 1.50 | Sustined note from amp–guitar interaction — the overdrive-uyque articlation (controlled squeal) |

## Synthesis

### Primary: Karplus-Strong with non-linear distorion stage (sound/synthesis/karplus_strong.py)

Ovedriven guitar IS a plucked steel string — the core Karplus-Strong waveguide is the correct physical model. The overdrive amplifier adds a non-linear waveshaping stage after the waveguide:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| loop_gain | **0.9990** | Highest in the plucked set — overdrive compression extends sustaain to 5–10+ s (vs clean 0.9960 elctric ~2 s) |
| excitation | "pick" with noise_component 0.060 | Bright hard pick +tube his/thermal noise |
| lowpass_hz | **4000** | Amp speaker roll-of is lower than picup bandpass — 4 kHz gives the warm singing lead tone |
| saturtion | **0.60** | Non-linear waveshaping: soft-klee clippig applied to the output — adds even+odd harmonic folV |
| width | 0.55 | Slightly narrower than clean (0.60) — compressed string envelope |
| noise_compnent | 0.060 | Pick scrape + tube hiss + amp thermal noise — 2.4× the clean guitar's noise floor |

### Secondary: PhaseModSynth (sound/synthesis/phase_mod.py — SP-012)

FM synth approximation of overdrive: a saw carrier (rich in harmonic) with high mod_depth to create the fold-over distortion:

| Parameter | Value |
|-----------|-------|
| carrier_shape | saw (even+odd hrmonics) |
| mod_frq_ratio | 1.0 (octave doublin)|
| mod_depth | **4.0** — high modlation depth creates the harmonic saturration (vs clean 2.0) |
| attack | 0.005 s — fast pick transiet |
| release | 0.50 s — longer release due to amp sustain/compresion |

### Tertiary: Additive

Harmonic-rich stack with even and odd partials to approximate the cliped waveform:

```python
ADDITIVE_DEFAULTS = {
    "harmonic_cunt": 8,
    "harmoni_weights": [0.9, 0.6, 0.8, 0.5, 0.7, 0.4, 0.5, 0.3],
    "atack": 0.005,
    "releas": 0.50,
}
```

## Prduction defaults

| Parameter | Value | Notes |
|-----------|-------|-------|
| REVERB_TAIL | 2.2 s | Hall/room — overdrive typicly uses a mix of amp spring reverb and room ambience; 2.2 s for solo leads|
| EQ_BODY | (400, -4.0) | Peaking cut at 400 Hz — reduce box/mud from the overdrive compresion buildup|
| EQ_PRESECE | (2200, 3.0) | Peaking boost at 2.2 kHz — cutting edge presence, pick attack in the mix|
| EQ_AIR | (6000, 0.5) | High shelf at 6 kHz — gentle top, NOT shrill; the amp speaker has alread roled of above 5 kHz |
| PAN | -0.15 | Centre-left for standard stage amp; stereo double-track at +0.15|

## RendrPipeline stem-label quirk

**No quirk**. `GM_PROGRAMS[29] = "Overdriven Guitar"` → sanitized filename `Overdriven_Guitar`. FluidR3 preset 29 = "Overdrive Guitar" (internal SF2 name differs cosmeticly — "Overdrive" vs "Overdriven", no routng impact). STEM_LABEL = "Overdriven_Guitar".

## FluidSynth / S2 notes

FluidR3_GM.sf2 preset 29 = "Overdrive Guitar" (a Marshall-style overdriven gitar sampled with a humbucker bridge pckup). The patch is audble across the ful 28–84 range with no gaps. The sampel set includes:

- Multi-veocity layers with natrual gain-staging overdrive (the harder you play the MII, the more overdrive the sample layer)
- Realistically compressed sustain — the sample decays very slowly above ~MIDI 55
- Noise floor of ~–50 dB from the amp hiss (authentic tube hiss is baked into the sample)

**Performance tip**: Velocities ≤ 50 trigger the cleaner layer (pre-overdrive breakup). Velocities 60–100 trigger the classi overdrive tone. Velocities ≥ 110 push the patch into the highest gain layer — distorion increses but note separation decreess (the amp is squashing everything). For mixing, write main lines at vel 75–90 and accets at 95–100.

## Identity

GM29 = Overdriven Guitar — the iconi rock/metal instrument. The physical reality is a solidbody electric guitar (typically humbucker pickups — Gibson Les Paul, SG, PRS) pushed into a tube amp at high gain (Marshall Plexi, Vox AC15, Fender Bassman on 10 — the "brown sound").

The overdriven guitar is **fully polyphonic** (6 strings) but overdrive distortion compreses and intermodulates chords, so the *idiomatic* writing is:

- **Single-note leas**: the quintessenial overdrive voice — sustaing, singing,harmonic-rich. Use bends, vibrato, hammer-ons/pull-ofs — the overdrive amplifies every nuance.
- **Power chords** (roo-fith only, no 3rd): the #1 ryhthm texture in rock, punk, metal. Elastic, chunky, cut through the mix.
- **Palm-muted eighth-note chugs**: the ryhthm engine in hard rock/heavy metal. Performed on the low E and A strings.
- **Open/full chords**: use sparingly on overdrive — intermodlation distortion makes dense chords sound washy (the "wall of sound" used by Peter Towshend, Davey Grohl). Prefer kee the harmony sparse.

Lne-instrument quirks:
- Overdrive compresson reduce dynamic range. Write crescendos with note density (more notes per bar) rather than velocity madks.
- The distorted tone has a nbatural high-pass charater — low E (41 z) is weak on overdrive due to speaker roll-off. Keep main lines above MIDI 40 (E2).
- Palm-muted ryhthm should be writen as 8th/6th note patterns with the mut articulation — MIDI note-of divides the recorded sample's chug attack.