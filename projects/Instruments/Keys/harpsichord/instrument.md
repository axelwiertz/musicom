---
type: instrument
family: Keys
name: Harpsichord
midi_program: 6
gms: "Harpsichord"
range_min: 29
range_max: 89
solo_range: [29, 89]   # full 61-key concert-double compass
role: [harmony, continuo, melody, ornament, countermelody, accent]
synthesis: [karplus, modal, phase_mod]
---

# Harpsichord

## MIDI / GM

- **Program**: 6 (GM1 Harpsichord — GM program numbers are 0-based; 6 is the
  7th entry, "Harpsichord", part of the keyboard block 0–7). NOT in
  `structures/instrument.py` `MidiInstrument` enum (10 only) — use raw
  `program=6` in `add_voice`.
- **Channel**: any melodic channel (0-9) — the harpsichord is PITCHED; channel
  9 would trigger the drum-kit map and the program-0 fallback stem label
  `Acoustic_Grand_Piano` (ch9/pgm0 quirk).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 6 =
  "Harpsichord" (phdr-verified — labels match exactly, no routing impact).
- **Pipeline stem label**: `GM_PROGRAMS[6]` = "Harpsichord" → disk stem
  `trackXX_Harpsichord.wav` — matches exactly, **no quirk** (contrast GM74
  Flute → `Recorder`, GM109 → `Bag_pipe`).

## Identity

The harpsichord is a **plucked keyboard instrument**: each key lifts a jack
whose **quill (raven feather / leather plectrum)** plucks a string. It is the
principal keyboard instrument of the Baroque era (Bach *Goldberg Variations*,
couperin's *Pièces de clavecin*, Scarlatti sonatas) and survives as the
**continuo** instrument of every period ensemble and Baroque opera pit.

The defining invention is the **choir/registration system**: one manual
(keyboard) can have multiple string choirs per key — **16'** (one octave
down), **8'** (unison, two strings), **4'** (one octave up) — selected or
combined by hand stops, and a two-manual instrument couples manuals to switch
choirs mid-phrase. The **4' octave choir** is what makes a harpsichord sound
like a harpsichord: every note carries a bright octave double.

Consequences for composition:

- **No touch dynamics.** The quill plucks at a fixed displacement — pressing
  harder changes nothing. Dynamics are **terraced**: you change loudness by
  changing REGISTRATION (choir combinations) or by writing more notes
  (density). A composition job should keep velocities in a narrow band
  (84–100) and phrase with articulation + register — the exact inverse of
  the piano lesson.
- **Ornamentation is not decoration, it is the sustain mechanism.** Long
  notes on a harpsichord die fast (pluck decay), so Baroque performers
  trilled/mordent-ed sustained tones to keep them alive. Write trills and
  mordents where a pianist would write tenuto.
- **Two manuals** = instant terrace contrast (loud manual vs soft manual)
  without changing voicing.

## Range

61 keys, sounding pitch. **Non-transposing, written at concert pitch** (two
staves like the piano).

| Zone | MIDI | Pitches | Keys | Register |
|---|---|---|---|---|
| Full range | 29–89 | F1–F6 | 1–61 | modern concert double-manual compass |
| Sweet spot | 48–84 | C3–C6 | ~20–56 | 8' principal register; melody + continuo |
| Low | 29–47 | F1–B2 | 1–19 | 16'/8' bass: continuo bass line, big and snarling |
| Mid | 48–71 | C3–B4 | 20–43 | 8' principal: melody, harmony, the classic zone |
| High | 72–89 | C5–F6 | 44–61 | 4' upperworks + 8' treble: sparkle, ornaments |

The modern concert double (F1–F6, 61 notes) is the 20th-century standard
(Dolmetsch/Challis/Neupert); historic Ruckers/Taskin originals are shorter
(C/E–c''' = MIDI 36–84). Chords are fully polyphonic — the only mechanical
limit is **one pluck per key per stroke** (no true re-strike until the jack
resets, ~a few ms; trills are idiomatic precisely because the jack returns
fast).

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| 8' single choir | 84–92 | full decay, ring 2–5 s | the neutral harpsichord voice |
| Full choir (16'+8'+8'+4') | 94–102 | 1.2×, longer ring | tutti terrace, fanfare weight |
| 4' alone | 74–82 | 0.9× | thin, nasal, flute-like solo color |
| Lute/buff stop | 66–74 | 0.55× | leather-muted, nasal, intimate |
| Broken-chord continuo | 70–80 | per 8th/16th | the continuo job — arpeggiated bass |
| Trill (agrément) | 78–86 | 0.5× per note | THE sustain device; starts on the UPPER note |
| Mordent (pince) | 82–90 | 0.3× | quick upper-neighbor bite |
| Étouffer (hand-damp) | 48–58 | very short | palm/finger choke, dry release |

## Timbre DNA

- **Harmonic content**: near-harmonic string stack DOUBLED an octave up (the
  4' choir) — that strong 2nd-octave layer is the signature "twang";
  inharmonicity is real but mild (long thin steel/brass strings)
- **Attack**: 1–3 ms quill pluck — hard, immediate onset (sharper than a
  fingertip, comparable to a banjo nail attack), plus a tiny "tock" of
  jack contact noise
- **Decay**: fast pluck decay per note (bright shimmer 0.3 s, body 1–2 s)
  but the string keeps a long quiet tail WHILE THE KEY IS HELD (2–5 s bass);
  the damper stops it the instant the key releases — releases are CLEAN
- **Release**: key-up drops the cloth damper = immediate stop (contrast the
  harp's no-damper rings)
- **Vibrato**: none (no mechanism); expression = ornaments, articulation
  timing, registration
- **Character**: brilliant, nasal, articulate, dry-by-nature but ring-rich;
  glassy treble, snarling bass; "a guitar you can play chords on"

## Role in Arrangement

- **Continuo**: the bass line + broken chords that glue a Baroque ensemble
  (with cello/bassoon doubling) — the harpsichord's primary job for 150 years
- Arpeggiated harmony fills and broken-chord accompaniment under strings/winds
- Melody in the mid register — ornamented, terrace-dynamic lines
- Ornament/countermelody filigree above sustained orchestral textures
- Cadential flourishes (rising scale runs, the classic *cadenza* slot)
- NOT a pad (nothing sustains), NOT a bass foundation in a modern mix
  (the 16' snarls but does not own the bottom like a cello), NOT a
  velocity-dynamic voice

## Synthesis Engines (musicom)

1. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
   **primary**. Quill-plucked waveguide = the exact physical model (one
   string, one pluck, per key). `loop_gain` **0.9980** — between harp
   0.9985 (no dampers at all) and sitar 0.9975: harpsichord strings ring
   2–5 s while the key holds, then stop CLEAN on release; `width` 0.5 for
   the boxy-but-focused stereo image.
2. **ModalSynth** (`sound/synthesis/modal.py`) preset `'string'` — harmonic
   stack with moderate decay; the clean fallback. Custom
   `HARPSICHORD_MODES` bank models the 8'+4' registration: a near-harmonic
   stack with an explicit octave DOUBLE (4' choir fundamental at the same
   amplitude class as the octave partial), slightly faster decay rates
   (0.35–0.90) than the harp's 0.22–1.20 because the damper rail kills on
   release.
3. **PhaseModSynth** — cheap twangy harpsichord: sine carrier, mod ratio
   2.0, depth 2.2 (nasal — brighter than the harp's 1.3), attack 0.002,
   release 1.4.

## Production

- **Reverb**: chamber/baroque hall 1.5–2.0 s — harpsichords live in smaller
  resonant rooms than a symphonic stage; over-tailing washes out the pluck
  definition (shorter tail than the harp's 2.4 s hall)
- **EQ**: cut ~300 Hz soundboard boxiness; boost ~3.5 kHz for quill-pluck
  clarity; 9.5 kHz shelf for the 4' upperwork shimmer
- **Delay**: not idiomatic; the natural pluck decay IS the space
- **Pan**: center solo; right-of-center in a baroque continuo section
  (audience view), mirroring the harpsichord's orchestral seat
- **FluidSynth note**: FluidR3 preset 6 is a decent single-choir patch; for
  the 4' octave-double character use `HARPSICHORD_MODES` (ModalSynth) or
  double the melody line one octave up at ~half velocity in the MIDI

## Verification

- GM6 → stem `trackXX_Harpsichord.wav` (label matches, no quirk)
- FluidR3 preset 6 = "Harpsichord" (verified from phdr chunk — exact match)
- Solo render passes 4–8 kHz spectral gate (quill pluck, no comb buzz)
- Zero-drift: plucked units end flush at BAR (terminal landmark)
- **Fixed-velocity quirk**: no touch dynamics — keep velocities in the
  84–100 band and phrase with registration (density/octave doubling) +
  ornaments, NOT velocity swells
- **Empirical FluidR3 pitch sweep** (RMS, notes 29–89): preset 6 audible
  8/8 sampled notes, no gaps — SF2 never clips a composition (see
  `_test/verify_harpsichord.py`)

## Instrument.md companion

`harpsichord.py` — importable constants. Registered in
`instrument_registry.py` (2026-09-17) as `Keys.harpsichord.harpsichord` →
key `harpsichord`, constant `HARPSICHORD`.
