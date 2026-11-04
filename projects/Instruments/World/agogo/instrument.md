---
type: instrument
family: World
name: Agogo
midi_program: 113
gms: "Agogo"
range_min: 55
range_max: 96
solo_range: [67, 84]
role: [rhythm, accent, ornament, drone]
synthesis: [modal, phase_mod]
---

# Agogô

## MIDI / GM

- **Program**: 113 (GM1 "Agogo"; GM numbers are 0-based, so 113 is the 114th
  entry)
- **Channel**: melodic channel (0–9). The GM113 patch is **pitched** — each
  played note is a bell tone, so the two-bell set is written as two pitches.
  NOT channel 9: channel 9 triggers the drum-kit map and the
  `Acoustic_Grand_Piano` program-0 fallback stem label (timpani/taiko lesson).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 113 =
  "Agogo" (verified from the phdr chunk). RenderPipeline stem label:
  `GM_PROGRAMS[113] = "Agogo"` → `trackXX_Agogo.wav` — matches exactly,
  **no quirk**.
- GM neighbours: 112 Tinkle Bell, 114 Steel Drums, 115 Woodblock, 116 Taiko
  Drum — the percussion tail of the GM map. Agogo is the bright metal
  timeline voice; 115 Woodblock is its dry wooden counterpart and 112 Tinkle
  Bell its high sparkle cousin.

## Range

Sounding pitch. Real instrument: the Brazilian agogô is a pair (sometimes
three or four) of conical sheet-metal bells welded to a curved handle; the
two bells are tuned roughly a **third to a fourth apart**, the low bell
around A4–C5 and the high bell a fourth above (D5–G5). Three- and four-bell
sets extend upward to about C6.

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 55–96 | G3–C7 | GM patch span (pitched bell) |
| Low | 55–66 | G3–F#4 | large low bell (agogô grande / candomblé gã): fat bronze ring |
| Middle (core) | 67–79 | G4–G5 | the standard samba pair — low + high bell |
| High | 80–96 | G#5–C7 | agogô-mirim small bell: thin bright tick, 3–4 bell sets |

Practical writing range is G4–C6 (67–84); the pair itself lives in
A4–G5 (69–79). Below G3 the patch loses its pitch centre and reads as a dull
clank; above C6 the metal thins to a tick.

## Articulations

The agogô is played with **one stick**, striking the two bells alternately —
never both at once (a two-note "chord" is not idiomatic).

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Open high bell | 90–100 | 0.6× | bright free ring — the "teleco" of the timeline |
| Open low bell | 86–98 | 0.8× | fatter, longer bronze ring — the downbeat "tá" |
| Alternating (timeline) | 78–90 | 0.5× | high/low alternation in 16ths — the clave figure |
| Muted (hand clamp) | 60–78 | 0.15× | dead click, no ring — the "closed" bell |
| Rim strike | 80–95 | 0.10× | metallic tick on the bell edge, sharpest sound |
| Double stroke | 88–99 | 0.35× | stick bounce flam — pushes a samba virada |
| Ghost | 30–48 | 0.12× | barely-there 16th, keeps the flow unaccented |
| Accent | 100–110 | 0.55× | hard downbeat — the batucada "1" |
| Roll (one bell) | 58–72 | 0.08× | fast single-stick tremolo — only sustain illusion |

## Timbre DNA

- **Harmonic content**: mostly TUNED metal — a strong fundamental plus a
  near-octave partner (~2×), then a short inharmonic tail (~2.7×, ~4.1×,
  ~5.4×). Far more pitched than a church bell (no minor-third tierce
  dominance), far brighter than a woodblock.
- **Attack**: ~1–3 ms — a hard stick on thin sheet metal; the click is part
  of the sound (unlike a mallet on a bar).
- **Decay**: ~0.8–1.5 s free ring; the high bell dies faster than the low
  bell. Muting with the free hand cuts it to a click.
- **Release**: no damper mechanism — the ring is stopped by the hand or by
  the next stroke.
- **Vibrato**: none.
- **Character**: bright, cutting, metallic, insistent. The agogô is the
  **timekeeper** — its job is to state the timeline cycle so the whole
  bateria agrees on where the beat is.

## Role in Arrangement

- Rhythm — the timeline: a fixed cyclic 16th-note figure over the samba /
  batucada groove (the Brazilian analogue of the Afro-Cuban clave). This is
  the instrument's primary function.
- Accent — hard downbeat strokes that mark the "1" of each cycle.
- Ornament — rim ticks, flams and short rolls at section changes (viradas).
- Drone / pedal — a repeated single bell on the offbeats as a textural pedal
  under a melody (common in samba de roda and capoeira).
- Pairs with: surdo (the bass drum pulse), tamborim, cuíca, drum kit, and
  any World melody (koto, shenai, pan flute). In the KB, put it against
  `drum_kit` or `taiko` for the low pulse.
- NOT a melodic lead: the patch is pitched, but agogô idiom is rhythm.
- NOT a harmony/chord voice: one stick, two bells, one note at a time.
- NOT a bass voice: the bells sit above 400 Hz.

## Synthesis Engines (musicom)

1. **ModalSynth** (`sound/synthesis/modal.py`) — **primary**. A struck metal
   bell is exactly a bank of damped sinusoids. Custom `AGOGO_MODES`:
   fundamental (440 Hz at the A4 reference) + ~2× octave partner + ~2.72×,
   ~4.07×, ~5.4× inharmonic tail, decay rates 2.2–7.0 (low rates = long
   ring; the agogô rings ~1 s, longer than the marimba but shorter than the
   vibraphone). The stock `'bell'` preset is the closest bank but models a
   Western cast bell (minor-third tierce, very slow tail).
2. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — cheap bell: sine
   carrier, **non-integer** mod ratio 2.72 (inharmonic FM is the classic bell
   recipe), depth 2.4, attack 0.001, release 0.9. Boxy but serviceable.
3. **Additive** — acceptable fallback: partial stack 1 : 2 : 2.72 : 4.07
   with fast-decaying upper terms.
4. **Karplus-Strong — EXPLICITLY REJECTED**: there is no string. A KS loop
   produces a harmonic series, the wrong partial structure for a struck
   metal bell (the timpani/taiko precedent).

## Production

- **Reverb**: 1.1–1.5 s. Samba is street/roda music: the bell is dry and
  must cut through a full bateria. Shorter than the taiko (1.6) and much
  shorter than any hall instrument.
- **EQ**: cut ~420 Hz (boxy low-mid under the bell fundamental); boost
  ~3.2 kHz for the stick-on-metal clank; +1 dB shelf at 9 kHz for
  sheet-metal shimmer. Bells carry real top end — do not low-pass them.
- **Pan**: centre for solo; in a bateria spread place it slightly right
  (+0.15), opposite the tamborim.
- **Layering**: use it as the rhythmic anchor over drums or as the top
  texture over a World melody. NEVER double the same bell pitches with a
  second pitched patch (comb-filter buzz — the 2026-09-01 lesson); octaves
  or a different bell pitch are fine.

## Idiom / writing quirks

- **Timeline, not fills**: the agogô repeats a short cycle. Write 1–2 bar
  patterns and let them loop; do not write through-composed melodies.
- **Two pitches, alternating**: model the pair as low bell (root) and high
  bell (a fourth above) and alternate. Simultaneous strikes are wrong.
- **Straight 16ths**: samba agogô is metronomic — humanize with tiny timing
  sigma, not swing. Velocity accents carry the groove, not timing.
- **Ghost notes matter**: the quiet 16ths between accents are what makes the
  pattern breathe; keep them at velocity 30–48.

## Verification

- GM113 → stem `trackXX_Agogo.wav` (label matches, no quirk)
- FluidR3 preset 113 = "Agogo" (verified from phdr chunk)
- Solo render passes the 4–8 kHz spectral gate (bright metal, no comb buzz)
- Zero-drift: struck units end flush at BAR (terminal landmark)
- Empirical FluidR3 pitch sweep (RMS, notes 43–96): preset 113 audible
  15/15, no gaps — SF2 never clips a composition

## Instrument.md companion

`agogo.py` — importable constants. Registered in `instrument_registry.py`
(2026-09-02 nightly) as `World.agogo.agogo` → key `agogo`, constant `AGOGO`.
