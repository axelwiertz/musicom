---
type: instrument
family: Percussion
name: Melodic Tom
midi_program: 117
gms: "Melodic Tom"
range_min: 36
range_max: 96
solo_range: [48, 72]
role: [rhythm, accent, ornament, color]
synthesis: [modal, drum606, phase_mod]
---

# Melodic Tom

## MIDI / GM

- **Program**: 117 (GM1 Melodic Tom — GM program numbers are 0-based; 117 is
  the 118th entry, "Melodic Tom")
- **Channel**: melodic channel (0–9); GM117 is a TUNED drum (pitch follows
  the played note, COARSELY — see the pitch quirk below). NOT channel 9 —
  channel 9 triggers the drum-kit map and the `Acoustic_Grand_Piano`
  program-0 fallback stem label (timpani lesson).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 117 =
  "Melodic Tom" (verified from the phdr chunk). RenderPipeline stem label:
  GM_PROGRAMS[117] = "Melodic Tom" → `trackXX_Melodic_Tom.wav` — matches
  exactly, **no quirk**. TimGM6mb.sf2 also carries preset 117.
- GM neighbors: 113 Agogo, 114 Steel Drums, 115 Woodblock, 116 Taiko Drum,
  118 Synth Drum — the low-fidelity GM percussion tail. Melodic Tom is the
  tuned-fill cousin of 116 Taiko (higher, drum-set toms for melodic fills).
- MidiInstrument enum: not exposed (the enum only covers 10 instruments) —
  use the raw GM number 117 (the registry is the full KB).

## Range

Sounding pitch. The GM patch plays the full span (isolated notes 30–108 all
audible, RMS 0.12–0.16 — no gaps, no clipping), but it is a **fill voice**,
not a chromatic instrument. Real anchors: a concert-tom/rototom set spans
~C2–C5 (36–72), rototoms reach C6 (84); the classic 70s/80s fill register is
C3–C5.

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 36–96 | C2–C6 | melodic-tom patch span |
| Low | 36–47 | C2–B2 | floor toms: chest thump, the fill "root" |
| Middle (fill core) | 48–60 | C3–C4 | the classic melodic-fill register |
| High | 61–96 | C#4–C6 | rack toms / rototoms: thin, bright, dry |

Practical composition core is 48–72 (C3–C5) — the sweet spot 52–67 (E3–G4)
has the fullest thump + clearest attack.

**PITCH QUIRK (measured, both soundfonts)**: GM117 does NOT chromatically
pitch-track. The dominant partial stays in the **50–95 Hz band** (rising
only ~1 octave of pitch across 4 octaves of notes: ~50 Hz at C2 → ~95 Hz at
C5), and the spectral centroid creeps just 1.1→1.5 kHz over the whole span.
Above ~C6 a weak partial near the written note appears but is not reliably
in tune (up to ±300 cents). Note number is a **coarse timbre/pitch
control** — never write chromatic runs or expect the notes to transpose
(the woodblock lesson: note number ≠ melody). Write fills on a small set of
scale tones and let the ring carry them.

## Articulations

Fills on a tuned tom set: stick strokes graded by intensity. Concert toms
have no dampers — the ring IS the sustain, and the player muffles by hand
before the next stroke.

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Fill 16th | 90–100 | 0.35× | standard fill unit — stick on tuned head |
| Fill 8th | 100–110 | 0.5× | bigger stroke, more ring |
| Accent | 110–115 | 0.6× | downbeat landing note of a fill |
| Ghost | 35–45 | 0.2× | texture tap between the loud hits |
| Rim shot | 85–92 | 0.12× | crack on the hoop, no tone |
| Roll (buzz) | 75–85 | 0.1× | buzz roll — the only sustain illusion |
| Flam | 90–95 | 0.15× | grace + main stroke |
| Soft | 55–65 | 0.5× | verse fills at p |
| Toms together | 95–105 | 0.4× | double-stop (two toms) — bigger fill hit |

## Timbre DNA

- **Harmonic content**: INHARMONIC membrane modal family (circular-head
  Bessel ratios ~1 : 1.59 : 2.14 : 2.65 — the timpani/taiko family) with a
  strong tuned-head (0,1) fundamental. No harmonic series, no sustained
  tone.
- **Attack**: ~3–5 ms — drumstick (or mallet) on a single tuned head;
  between the taiko's thick bachi and a marimba mallet
- **Decay**: ~0.5–1.0 s (measured FluidR3 A3: −90% in ~0.3–0.5 s, tail to
  ~1 s) — shorter than timpani (1–3 s), longer than woodblock (60–90 ms)
- **Release**: no dampers on concert toms; the player muffles by hand
- **Vibrato**: none
- **Character**: dry, punchy, pitched-but-not-chromatic — the drum-fill
  voice of 70s/80s pop-rock (Toto "Africa" intro, Men at Work "Down Under",
  The Police "Every Breath You Take", Phil Collins "In the Air Tonight"
  gated toms)

## Role in Arrangement

- Rhythm — melodic fills into/out of sections (the 70s/80s tom-fill trope),
  drum breaks, intro riffs; the fill IS the arrangement moment
- Accent — downbeat punctuation, stops, the "landing" hit of a drum break
- Ornament — ghost taps, rim cracks, flams, rolls as texture
- Color — tuned-drum colour under a World/pop track (pairs with taiko,
  timpani, or the drum kit)
- NOT a melodic lead: the patch does not chromatically track (measured) —
  never write a melody on GM117
- NOT a harmony/pad voice — it is a drum; no chords (a chord = a bigger hit,
  and real tom sets have one pitch per drum)
- NOT a bass melodic voice — use a real bass instrument under it

## Synthesis Engines (musicom)

1. **ModalSynth** (`sound/synthesis/modal.py`) — **primary**, impulse-excited
   resonator bank with a custom `MELODIC_TOM_MODES` bank: tuned (0,1) head
   mode (174 Hz at the F3 reference) coupled to inharmonic membrane partners
   (1.59×, 2.14×, 2.78×, 3.56×), decay rates 4.5–9.5 — between timpani
   (0.9–3.0, long ring) and marimba (8–20, dry bar). The stock `'drum'`
   preset is the closest bank but decays too fast and has no tuned-head
   fundamental.
2. **DrumSynth606** (`sound/synthesis/drum_synth_606.py`) — the strike
   thump: `DRUM606_DEFAULTS` with freq 174 (the tom speaks higher than the
   taiko's 80 Hz), decay 0.8, pitch_sweep 1.25.
3. **PhaseModSynth** — cheap tom: sine carrier, mod ratio 1.59 (the (1,1)
   membrane partner), depth 1.2, attack 0.001, release 0.5. Boxy, less
   authentic.
4. **Karplus-Strong — EXPLICITLY REJECTED**: there is no string; a KS
   loop's harmonic series is the wrong partial structure (the timpani/taiko
   precedent).

## Production

- **Reverb**: 1.0–1.4 s — pop/rock drum room; long enough for the fill to
  bloom, short enough to keep 16th-note clarity (taiko 1.6 festival hall vs
  woodblock 0.75 dry tick)
- **EQ**: cut ~280 Hz box honk (keep the thump below it); boost ~2.4 kHz
  for the stick-on-head attack (between taiko's 1.8k raw hide and
  woodblock's 3.6k stick crack); small 7 kHz air shelf
- **Pan**: center for a solo fill; a kit spreads toms −0.3..+0.3 (floor
  right, rack left — drummer's perspective)
- **Layering**: pairs with the drum kit (fills sit over the groove), taiko,
  timpani, or a World track; NEVER a second pitched patch in unison on the
  tom's pitches (comb buzz — the 2026-09-01 lesson)

## Verification

- GM117 → stem `trackXX_Melodic_Tom.wav` (label matches, no quirk)
- FluidR3 preset 117 = "Melodic Tom" (verified from phdr chunk)
- Solo render passes the 4–8 kHz spectral gate (9.8% — the stick band, no
  comb buzz)
- Zero-drift: struck units end flush at BAR (terminal landmark)
- Isolated-note sweep: 30–108 all audible, no gaps — SF2 never clips a
  composition (but the patch does not chromatically track, see pitch quirk)

## PIPELINE QUIRK (measured, 2026-11-16) — every 2nd note-on renders quiet

In this FluidSynth binary + the GM percussion/decaying patches, **every 2nd
note-on EVENT within a MIDI track renders ~30–50 dB down** (the 1st, 3rd,
5th... note-ons sound; the 2nd, 4th, 6th... are near-silent). Measured on
GM117 AND on the already-registered GM47 Timpani, GM115 Woodblock, GM116
Taiko, GM0 Piano, GM33 Electric Bass — but NOT on sustained patches (GM40
Violin, GM73 Flute). The toggle is per MIDI track (splitting tracks shifts
the count per track), ignores CCs / ghost notes on other channels / velocity
/ note length / gap, and is not fixed by `synth.polyphony=1024`,
`synth.reverb.active=0`, or `synth.chorus.active=0`. The previous nightly
run's accepted woodblock WAV (2026-11-15) contains the same artifact — it is
a KNOWN-ACCEPTED pipeline behavior for percussion renders.

Composition consequence: a straight 16th-note tom fill renders with the
even hits missing — at fill tempos the loud hits' ring masks the gap
(apparent accent ~6–8 dB, reads as natural dynamics), and at ≥0.5 s spacing
the even hits are audibly missing. Workarounds: (a) accept it — fills still
read as fills (woodblock precedent); (b) land the IMPORTANT fill notes on
odd note-on indices (1st, 3rd, 5th...); (c) use the ModalSynth/DrumSynth606
engine path, which does not have the artifact.

## Instrument.md companion

`melodic_tom.py` — importable constants. Registered in
`instrument_registry.py` (2026-11-16) as `Percussion.melodic_tom.melodic_tom`
→ key `melodic_tom`, constant `MELODIC_TOM`.
