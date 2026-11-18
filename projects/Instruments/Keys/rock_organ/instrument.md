---
type: instrument
family: Keys
name: Rock Organ
midi_program: 18
gms: "Rock Organ"
range_min: 36
range_max: 96
solo_range: [48, 84]
role: [lead, rhythm, harmony, comp, pad, bass, accent, drone]
synthesis: [additive, phase_mod]
---

# Rock Organ

## MIDI / GM

- **Program**: 18 (GM1 0-based "Rock Organ" — the 19th entry). Neighbours:
  16 Drawbar Organ, 17 Percussive Organ, 19 Church Organ, 20 Reed Organ.
- **Channel**: melodic channel (NOT 10). Polyphonic; a keyboard player voices
  3–5 notes per hand, so chord writing is idiomatic and cheap.
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2, bank 0 preset 18 =
  **"Rock Organ"** (verified from the SF2 `phdr` chunk). TimGM6mb also carries
  preset 18 but it is the thin fallback — do not use it for this instrument.
- **RenderPipeline stem label**: `GM_PROGRAMS[18] = "Rock Organ"` →
  `trackXX_Rock_Organ.wav`. Label and preset name match exactly — **no quirk**.
- **MidiInstrument enum**: not exposed (only 10 instruments are). Pass the raw
  integer `18` — the registry is the full knowledge base.

## Range

Standard 61-key manual, sounding pitch, non-transposing. The GM patch is a
single manual (no pedal board); the low zone is the left-hand key bass, which
is exactly how Booker T./Jon Lord played it.

| Zone | MIDI | Pitches | Register | Character |
|---|---|---|---|---|
| Full range | 36–96 | C2–C7 | 61-key manual | GM18 patch span |
| Bass | 36–55 | C2–G3 | left hand | 16'+8' only, riff roots |
| Mid (comp/lead) | 56–79 | G#3–G5 | right hand | full drawbars, bark |
| High | 80–96 | G#5–C7 | top octave+ | 1' partial, screaming solos |

Solo/comp focus 48–84 (C3–C6); sweet spot 55–79 (G3–G5) where the saturated
mids cut without turning to mud. Below C2 the patch is only usable as a
pedal-like sub (and it collides with bass guitar); above C6 the 8' fundamental
is thin and the 1' partial dominates.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Sustain | 80–90 | full | held key, flat output, no decay |
| Stab | 90–100 | ≤1/4 | percussive hit — the rock/ska rhythm cell |
| Chop | 72–84 | 1/8 | key-click dominated muted chop |
| Percussion | 85–95 | ~1/3 | key-on 2nd/3rd-harmonic ping, fast decay |
| Key click | 68–78 | 1/16 | busbar transient only, almost no tone |
| Accent | 95–105 | 0.8–1.0 | full drawbars + percussion on a downbeat |
| Smear | 60–72 | ~1.0 | chromatic palm smear / glissando fill |
| Swell | 90–100 | full | pedal swell — crescendo target |

Velocity is a **mix/attack** value, not loudness: the key contact is a binary
switch. Write dynamics with drawbar choice, note density and the swell pedal.
Because GM MIDI has no drawbar CC, velocity-modulated brightness in FluidR3 is
weak — prefer arrangement (density, register, doubling) over velocity curves.

## Timbre DNA

- **Harmonic content**: tonewheel sine stack (1x … 8x) with strong 2x/3x and —
  unlike the clean Drawbar Organ — significant 4x/6x/8x energy from tube
  saturation. Odd-harmonic emphasis from the clipper is what makes it "rock".
- **Attack**: 3 ms contact closure plus a broadband key click; percussion tab
  adds a fast-decaying 3rd-harmonic ping on key-on.
- **Sustain**: dead flat while the key is held (no decay, no tremolo unless the
  Leslie is engaged) — the organ *fills* the arrangement instead of decaying
  out of it. Release is a hard ~40–50 ms cut plus click.
- **Modulation**: Leslie rotor. Rock settings park it on FAST (~6.9 Hz, deep),
  which produces amplitude tremolo + ~7 cents Doppler wobble; chorale (0.8 Hz)
  is the ballad setting.
- **Noise floor**: key click and amp hiss are part of the sound — do not gate.

## Arrangement roles

| Role | Register | Notes |
|---|---|---|
| Lead | 60–84 | unison lines with guitar, or organ solo over a stop-time |
| Rhythm / comp | 55–79 | short stabs on the backbeat (ska/reggae/rock) |
| Harmony / pad | 48–72 | sustained triads, 3–4 voices, no doubling of guitar |
| Bass | 36–48 | left-hand key bass roots when there is no bass guitar |
| Accent | 60–84 | downbeat stabs, song-section markers |
| Drone | 48–60 | single held root/fifth under a vamp |

- Best paired with: distorted guitar (organ doubles the *line*, never the
  chord voicing), bass guitar, drums.
- **Avoid**: doubling the same sustained pitches as a piano or second organ —
  identical-pitch unison with two patches beats/comb-filters (the 2026-09-01
  buzz bug). Give the organ its own register or its own rhythmic role.
- Does not blend with strings well in the same octave (organ mask kills bow
  noise); put organ above or below the string pad.

## Synthesis

**Engine: `additive`** (`sound/synthesis/additive.py`, `SoundWave`).

The Hammond tonewheel generator *is* additive synthesis: 91 sine wheels, nine
drawbar levels mixing integer-and-a-half ratios. Recipe:

1. Build the partial bank from `ADDITIVE_HARMONICS[registration]`, normalizing
   to sum 1.0 (the engine asserts this).
2. Envelope `ADDITIVE_ENVELOPE`: 3 ms attack, **no decay**, sustain 1.0,
   45 ms release.
3. Overdrive stage `OVERDRIVE_DEFAULTS`: `tanh(drive * x)` with slight
   asymmetry, then a 2.4 kHz low-pass (cabinet) — this is the difference from
   the clean GM16 patch.
4. Leslie `MOTOR_DEFAULTS`: amplitude tremolo + Doppler pitch wobble at 6.9 Hz.
5. `drawbar_harmonics(preset)` returns the exact `{ratio: gain}` map for
   custom registrations (it can express the 0.5x 16' and 1.5x 5 1/3' bars that
   an integer-partial bank cannot).

Fallback: `phase_mod` (PhaseModSynth, `FM_DEFAULTS` — 3.0 ratio, depth 3.2)
gives a cheap DX7-ish rock organ. NOT Karplus-Strong, NOT ModalSynth: there is
no struck or plucked resonator anywhere in the signal chain.

## Production defaults

| Parameter | Value | Why |
|---|---|---|
| `REVERB_TAIL` | 1.3 s | club/stage; the amp is close-mic'd, not a cathedral |
| `EQ_BODY` | (250 Hz, −1.5 dB) | clear the 16' register under the drive |
| `EQ_PRESENCE` | (1800 Hz, +3.0 dB) | the saturated mid bark |
| `EQ_AIR` | (7000 Hz, +1.5 dB) | key click and rotor top |
| `PAN` | 0.0 (centre) | ±0.2–0.35 only when doubled with a clean organ |

Gain staging: the clipper adds ~3 dB — trim `output_trim_db` back so the organ
sits under the vocal and does not dominate the mix bus. FluidSynth preset 18
is already saturated; do **not** add a second distortion stage on top of a
FluidR3 render.

## FluidSynth / SF2 behaviour

- FluidR3_GM preset 18 responds to velocity only as amplitude (wind/organ
  patches in FluidR3 have no velocity→filter mapping). Long held notes sustain
  indefinitely; a note-off produces an immediate cut, so write legato by
  overlapping note-ends by a few ticks.
- The GM18 preset already contains Leslie-ish chorus/rotary movement; adding
  the external motor model doubles the wobble. Pick one: SF2 render → skip
  `MOTOR_DEFAULTS`; native additive render → keep it.
- No pitch bend in the GM patch beyond the standard ±2 semitone range — no
  organ glissando via bend; write the chromatic smear as notes.

## RenderPipeline stem quirks

- Stem file: `trackXX_Rock_Organ.wav` — `GM_PROGRAMS[18]` and the FluidR3
  preset both read "Rock Organ"; sanitizer only rewrites spaces → underscores.
- **Distinct from GM16 Drawbar Organ** (`trackXX_Drawbar_Organ.wav`): both are
  Hammond-family patches. If a project uses both, the stems are separable by
  label but will sound similar — that is expected, not a routing bug.
- Known pipeline-wide behaviour (documented with Melodic Tom, 2026-11-15):
  every second note-on *event* inside one track can render 30–50 dB down with
  this FluidSynth binary. On a sustaining organ this is mostly masked; on
  staccato ska stabs, alternate hits may drop — keep stabs on separate
  sections/units or accept the accent pattern.

## Composition notes

- Write as a **sustaining** voice, not a decaying one: fills come from note
  density and register jumps, not from letting notes ring out.
- Chord voicings: 3–4 notes, root+3rd+7th (omit the 5th when distorted —
  intermodulation mud). Power-chord style root+fifth works for riffs.
- In rock/blues contexts the organ doubles the guitar *line* an octave up or
  harmonises a third below; it should never play the guitar's exact voicing.
- Ska/reggae: short stabs on beats 2 and 4 ("up-strokes"), upper mid register.
- Humanize: Keys-family DNA (6 ms timing sigma, 5 velocity sigma, 0 layback) —
  the organ is a keyboard, it sits ON the grid; the Leslie supplies the motion.
