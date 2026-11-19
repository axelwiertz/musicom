---
type: instrument
family: Keys
name: Percussive Organ
midi_program: 17
gms: "Percussive Organ"
range_min: 36
range_max: 96
solo_range: [48, 84]
role: [comp, rhythm, harmony, pad, lead, bass, accent, drone]
synthesis: [additive, phase_mod]
---

# Percussive Organ

## MIDI / GM

- **Program**: 17 (GM1 0-based "Percussive Organ" — the 18th entry). Neighbours:
  16 Drawbar Organ, 18 Rock Organ, 19 Church Organ, 20 Reed Organ.
- **Channel**: melodic channel (NOT 10). Polyphonic — a keyboard player voices
  3–4 notes per hand; chord writing is idiomatic.
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2, bank 0 preset 17 =
  **"Percussive Organ"** (read from the SF2 `phdr` chunk, 2026-11-19).
  TimGM6mb also carries preset 17 but is the thin fallback — do not use it.
- **RenderPipeline stem label**: `GM_PROGRAMS[17] = "Percussive Organ"` →
  `trackXX_Percussive_Organ.wav`. Label and preset name match exactly —
  **no quirk**.
- **MidiInstrument enum**: not exposed (only 10 instruments are). Pass the raw
  integer `17`; the registry is the full knowledge base.

## Identity — what makes it "percussive"

The Hammond tonewheel organ has a **percussion tab**: a single fast-decaying
partial (2nd = 4', or 3rd = 2 2/3') fired by the key contact, independent of
the drawbar registration, that dies away in 80–400 ms while the drawbars keep
sounding. GM17 models that tab. Contrast with its siblings:

| Patch | Program | Character |
|---|---|---|
| Drawbar Organ | 16 | clean B-3, no percussion, warm sustain |
| **Percussive Organ** | **17** | **bright/thin drawbars + key-on ping — articulate comp** |
| Rock Organ | 18 | B-3 through a saturated amp + fast Leslie |
| Church Organ | 19 | pipes, no percussion, no drawbars |

Because every note arrives with its own transient, the patch cuts through a
dense mix at moderate velocity — the classic funk/soul/jazz comping voice
(Jimmy Smith, Jimmy McGriff, Billy Preston, Booker T.'s bright stops).

## Range

61-key manual, sounding pitch, non-transposing. No pedal board — the low zone
is left-hand key bass (percussion tab normally OFF there).

| Zone | MIDI | Pitches | Register | Character |
|---|---|---|---|---|
| Full range | 36–96 | C2–C7 | 61-key manual | GM17 patch span |
| Bass | 36–55 | C2–G3 | left hand | 16'+8', percussion off, riff roots |
| Mid (comp) | 56–79 | G#3–G5 | right hand | primary comp register, 3rd-harmonic ping |
| High | 80–96 | G#5–C7 | top octave+ | funk stabs, 2nd-harmonic ping, solos |

Solo/comp focus 48–84 (C3–C6); sweet spot 52–84 (E3–C6). Below C2 the patch
collides with bass guitar and the sub layer turns to mud; above C6 the 8'
fundamental thins out and only the ping and upper drawbars remain.

**Measured level flatness** (FluidR3, vel 100, 24 notes 24–108 step 4): RMS
0.112–0.176, i.e. within ±2 dB across 7.5 octaves — no dead notes, no gaps.
Octave-to-octave balance is safe for melodies as well as comping.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Sustain | 78–86 | full | held chord, flat body under the ping |
| Stab | 92–100 | ≤1/4 (0.18×) | the funk/soul rhythm cell — percussion leads |
| Chop | 70–78 | 1/16 (0.09×) | key-click + ping only, body barely speaks |
| Percussion | 88–96 | ~0.3× | key-on 3rd-harmonic ping, body ducked |
| Key click | 66–74 | 1/32 (0.05×) | busbar transient, almost no tone |
| Accent | 100–108 | 0.8–1.0 | downbeat, full drawbars + percussion |
| Swell | 90–98 | full | pedal crescendo on a sustained chord |
| Smear | 60–70 | ~0.9× | chromatic smear / glissando fill |

Velocity on FluidR3 GM17 is **amplitude only** — measured spectral centroid is
flat at 1.37–1.43 kHz from velocity 20 to 127, and peak amplitude rises
0.016 → 0.64 (≈ +32 dB). So write real dynamics with velocity (unlike the
Drawbar Organ, where velocity barely matters), and get brightness from
registration/register, not from hitting harder.

## Timbre DNA

- **Harmonic content**: tonewheel sine stack; measured partials at C4 relative
  to the fundamental: 1× 0 dB, 1.5× (5 1/3' quint) −1 dB, **0.25× (two-octave
  sub layer) −3 dB**, 0.5× −11 dB, 3× −40 dB. The quint is nearly as loud as
  the fundamental (that is the "thin, reedy" colour) and the sub layer gives
  the patch body weight — see quirks below.
- **Attack**: broadband key click plus the percussion ping; the *body* swells
  in over ~150–250 ms in FluidR3 (measured), so very short notes are all
  transient and no tone.
- **Sustain**: not perfectly flat in FluidR3 — the body decays ~5 dB/s after
  the swell and wobbles ±2 dB at ~0.7 Hz (preset chorus/rotary). Native
  additive synthesis is flat; arrange for the SF2 patch accordingly.
- **Release**: hard ~40 ms cut with a click — write legato by overlapping
  note-ends a few ticks.
- **Noise floor**: click and amp hiss are part of the sound; do not gate.

## Arrangement roles

| Role | Register | Notes |
|---|---|---|
| Comp / rhythm | 55–79 | short stabs on 2 and 4, up-strokes, funk/soul/gospel |
| Harmony / pad | 48–72 | sustained 3–4 note voicings; omit the 5th when dense |
| Lead | 67–88 | single-note solos, unison with guitar (line only) |
| Bass | 36–52 | left-hand key bass roots when there is no bass guitar |
| Accent | 60–84 | downbeat punctuation, section markers |
| Drone | 48–60 | held root/fifth under a vamp (ballad registration) |

- Best paired with: drum kit, electric bass, clean/distorted guitar, horn
  section. The ping occupies 2–3 kHz — leave that band to it.
- **Avoid**: doubling the same sustained pitches as piano or a second organ —
  identical-pitch unison with two patches beats/comb-filters (the 2026-09-01
  buzz bug). Give the organ its own register or rhythmic role.
- Against strings, place the organ above or below the pad octave; the organ's
  ping masks bow noise in the same register.

## Synthesis

**Engine: `additive`** (`sound/synthesis/additive.py`, `SoundWave`).

1. Build the partial bank from `ADDITIVE_HARMONICS[registration]`, normalized
   to sum 1.0 (the engine asserts this). Percussive banks carry *less* 4x/6x
   than Rock Organ but *more* 3x — the ping is a 3rd harmonic.
2. Envelope `ADDITIVE_ENVELOPE`: 4 ms attack, no decay, sustain 1.0,
   40 ms release.
3. Add the percussion ping as a **separate** voice on the same pitch:
   `PERCUSSION_DEFAULTS["harmonic"]` (3 by default), `level` 0.45, envelope
   from `percussion_envelope()` (exponential, −60 dB at 180 ms). It is a
   mix-in, not part of the ADSR — that is exactly how the tab works.
4. Optional slow wobble (0.7 Hz, ±2 dB) if you want the FluidR3 rotary
   character in the native render; skip it when rendering the SF2 preset,
   which already has it.

Fallback: `phase_mod` (PhaseModSynth) with a 3.0 ratio and short decay for a
cheap percussive-organ stand-in. NOT Karplus-Strong, NOT ModalSynth — there is
no struck/plucked resonator.

## Production defaults

| Parameter | Value | Why |
|---|---|---|
| `REVERB_TAIL` | 1.6 s | club/stage ambience; shorter than church organ |
| `EQ_BODY` | (300 Hz, −1.0 dB) | clear the 16'/sub mud under the ping |
| `EQ_PRESENCE` | (2500 Hz, +2.5 dB) | the key-on percussion ping band |
| `EQ_AIR` | (8000 Hz, +1.5 dB) | key click and drawbar top |
| `PAN` | 0.0 (centre) | ±0.25 only when doubled with a clean organ |

FluidR3 preset 17 is already bright — do **not** stack a second exciter or
distortion stage on a rendered WAV.

## FluidSynth / SF2 behaviour (measured 2026-11-19, FluidR3_GM.sf2)

- **Pitch tracking**: correct — each note produces its notated fundamental.
  But the **loudest partial is often not the fundamental**: at C4 the
  fundamental wins (0 dB) with the 5 1/3' quint at −1 dB; at G4 the two-octave
  sub (98 Hz) is loudest and the fundamental sits at −9 dB; at C5 the 3rd
  harmonic (786 Hz) is loudest. Melody is still unambiguous in context, but do
  not use GM17 as the only voice on a bare unison line in the top octave —
  double it or keep it in chords.
- **Sub-octave layer**: a 0.25× partial is present at −3 dB (C4) — the patch
  sounds heavier than written. Never write the organ's lowest octave under a
  bass guitar; it will mask the bass fundamental.
- **Attack swell**: body reaches full level ~150–250 ms after note-on (peak
  0.048 at 0 ms → 0.386 at 250 ms). Staccato shorter than ~1/8 at 120 bpm
  reads as a click, not a chord — for tight stabs use velocity ≥ 92 and
  accept the transient-led sound, or lengthen to 1/4.
- **Slow decay + wobble**: −5 dB/s body decay and ±2 dB at ~0.7 Hz while
  held; long pads need re-triggering every 2–4 bars if you want constant
  level.
- **Velocity → amplitude only** (centroid flat), roughly linear below vel 100
  and slightly compressed above.
- **Percussion tab is baked into the preset** — you cannot turn it off in GM
  MIDI (no CC for it). For a percussion-free organ use GM16 Drawbar Organ.

## RenderPipeline stem quirks

- Stem file: `trackXX_Percussive_Organ.wav` — `GM_PROGRAMS[17]` and the
  FluidR3 preset both read "Percussive Organ"; sanitizer only rewrites spaces
  to underscores. **No quirk.**
- **Distinct from GM16/GM18**: all three are Hammond-family patches and share
  the stem-name pattern; a project using several organs gets separable stems
  but similar timbres — expected, not a routing bug.
- Known pipeline-wide behaviour (documented with Melodic Tom, 2026-11-15):
  every second note-on *event* inside one track can render 30–50 dB down with
  this FluidSynth binary. On a sustaining organ this is mostly masked; on
  staccato funk stabs alternate hits may drop — put stabs in separate
  sections/units or accept the accent pattern.

## Composition notes

- Write it as an **articulating** voice: the ping gives the attack, the
  drawbars give the body. Funk/soul comping = short chords on 2 and 4 with a
  gap between them; do not fill every 8th.
- Voicings: 3–4 notes, root+3rd+7th; omit the 5th in dense mixes (the quint
  partial already supplies a fifth above the root — a written 5th doubles it).
- Keep the left hand above C2 when a bass guitar is present; below that the
  sub layer fights the bass.
- Humanize: Keys DNA (6 ms timing sigma, 5 velocity sigma, 0 layback) — it is
  a keyboard, it sits ON the grid; the percussion tab supplies the groove.
- Do **not** unison-double the same pitches with piano/clarinet (comb
  filtering); double the *line* an octave away or harmonise.
