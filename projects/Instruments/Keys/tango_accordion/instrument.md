---
type: instrument
family: Keys
name: Tango Accordion
midi_program: 23
gms: "Tango Accordion (FluidR3 preset: Bandoneon)"
range_min: 41
range_max: 96
solo_range: [53, 91]
role: [lead, melody, ornament, harmony, accent, pad]
synthesis: [phase_mod, additive, modal]
---

# Tango Accordion / Bandoneón (GM23)

## MIDI / GM

- **Program**: 23 (GM1 "Tango Accordion"; Roland GS "Bandoneon", Yamaha XG
  "TangoAccordion"). GM gave this slot to the tango repertoire's signature
  voice: the **bandoneón**, the bisonoric German concertina that became the
  melodic soul of the orquesta típica. GM numbers are 0-based, so 23 is the
  24th entry.
- **Enum note**: `structures/instrument.py` `MidiInstrument` exposes only 10
  instruments (PIANO, CHURCH_ORGAN, ACOUSTIC_GUITAR, VIOLIN, STRING_ENSEMBLE,
  TRUMPET, FLUTE, SYNTH_PAD, BASS — and its numbering is a legacy mix, e.g.
  PIANO=0 but VIOLIN=41) and has no accordion-family constant at all. Use the
  raw GM number 23; the registry is the full KB.
- **Channel**: melodic channel (0–9). Channel 9 with program 23 triggers the
  drum-kit map and the program-0 fallback label `Acoustic_Grand_Piano`
  (ch9 quirk — see the timpani lesson).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 23 =
  **"Bandoneon"** (verified from the phdr chunk). RenderPipeline stem label is
  GM_PROGRAMS[23] = "Tango Accordion" → sanitized `trackXX_Tango_Accordion.wav`
  — the **labels differ** (GM name vs SF2 preset name) but the stem filename
  comes from GM_PROGRAMS, so routing is unaffected. Cosmetic-only quirk.
- **Distinct from `accordion` (GM21)**: piano accordion = piano keyboard +
  Stradella chords, unisonoric, musette-detuned multi-rank chorus. Bandoneón =
  71 buttons, bisonoric (different note on push vs pull), no register
  switches, and every note sounds **two reeds an octave apart**
  (octave-coupled, not detuned). That pairing is the instrument's whole timbre
  identity.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 41–96 | F2–C7 | practical written band (≈4½ octaves) |
| Bass (left hand, wooden box) | 41–59 | F2–B3 | nasal, muted, reedy — bass lines, marcato roots |
| Low-mid (hand overlap) | 60–67 | C4–G4 | full, woody body; both keyboards reach here |
| Cantabile | 68–79 | G#4–G5 | THE tango melody register — singing, crying |
| High | 80–91 | G#5–G6 | bright, sharp right hand — ornaments, counter-lines |
| Top | 92–96 | G6–C7 | thin, squealing — rhetorical accents only |

The physical 142-tone / 71-key Rheinische-system bandoneón spans nearly five
octaves: German Wikipedia states the playable compass is "fast fünf Oktaven",
French Wikipedia says the tessitura "approaches six octaves" once the
octave-coupled second voice is counted. The exact endpoints differ by system
(142 vs 152 tones; the Kusserow/Peguri unisonoric systems re-centre the
keyboard), so this entry documents the standard tango instrument as F2 (lowest
left-hand reed) to C7 (top of the right-hand keyboard).

Empirical FluidR3 pitch sweep (RMS, velocity 90, notes 24–108): preset 23 is a
full-keyboard patch — **9/9 sweep notes audible, no gaps** (RMS 1055–1613,
essentially flat, dip at C5 1055 Hz, slight rise above C6). SF2 never clips a
composition; the F2–C7 band above is the idiomatic *writing* range.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Cantabile | 65–75 | full | singing draw-stroke line — the default melodic touch |
| Sustain | 70–82 | full | steady bellows, held note |
| Marcato (acento) | 88–96 | 0.85× | hard bellows start — the tango accent on 1 and 3 |
| Picado | 78–86 | 0.22× | staccato short bellows pulse |
| Fuelle | 72–84 | 0.5× | bellows tremolo/swell — the tango "breath" |
| Llorón | 68–78 | full | "crying": wide slow vibrato + pressure, the Piazzolla slow-movement voice |
| Arrastre | 82–90 | 0.65× | "drag" — slide into the note (a fast chromatic grace run in MIDI; SF2 ignores portamento) |
| Chasquido | 92–100 | 0.12× | whip/click — bellows slap punctuation |
| Golpe | 96–104 | 0.08× | tap on the instrument box — a knock, not a pitch |
| Sforzando | 94–102 | 0.55× | sudden forceful push, then release |

## Timbre DNA

- **Harmonic content**: free-reed (symmetric) spectrum, strong fundamental plus
  a **prominent second harmonic** — the octave-coupled reed pair. Measured
  (FluidR3, solo, held notes): spectral centroid **3568 Hz at C4**, **5999 Hz
  at C6** — for comparison the synth-brass patch measures 1744 Hz at C4; the
  bandoneón is a genuinely bright, nasal voice, not a mellow accordion.
- **Attack**: ~10–20 ms — the reed speaks on bellows pressure; slightly slower
  than a piano-accordion reed (more air mass), far faster than a bowed string.
- **Decay/sustain**: essentially none while the bellows move — the level is
  held by air pressure; release is near-instant at the button (a choked,
  reedy stop, unlike a string's ring-out).
- **Vibrato**: player-driven and expressive — typically 4.5–6 Hz, amplitude
  plus slight pitch, deepening on long notes ("llorón"). No instrument-wide
  musette beating: the octave pair beats at the octave, not at 2–5 cents.
- **Character**: nasal, cutting, reedy, slightly hollow; left hand darker and
  muted (wooden box), right hand bright and sharp. The sound of tango —
  Arolas, Troilo, Piazzolla's nuevo tango.

## Role in Arrangement

- **Lead** — the tango melody voice, cantabile register 68–79; also the
  counter-line above a violin or piano lead
- **Melody** — statement of the tune; the orquesta típica's frontline
  (two bandoneones) plays in thirds/sixths, an octave apart, or in call and
  response
- **Ornament** — arrastre slides, llorón cries, picado pickups, chasquido
  punctuation
- **Harmony** — sustained chord pads (the bandoneón can sound 3–4 note chords;
  in the ensemble it usually plays single lines or two-note dyads)
- **Accent** — marcato stabs and golpe knocks mark the tango's 4/4-with-
  habanera phrasing
- **Pad** — slow swell beds under a singer or violin
- **NOT** a bass instrument (left-hand reeds go down to F2 but the part belongs
  to double bass / cello), NOT a rhythm comping voice (no chord buttons like
  Stradella), and NOT a substitute for the piano accordion's musette folk
  sound — that is GM21 `accordion`
- Ensemble idiom: 2 bandoneones + 2 violins + piano + double bass (+ flute or
  clarinet) = orquesta típica; sextet = 2 bandoneones + 2 violins + piano +
  bass

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — **primary**. A free
   reed is a phase-modulated oscillator: saw carrier (symmetric, even + odd
   harmonics), sine modulator at ratio 1.0, depth **3.4** (edgier than the
   accordion's 3.2, well below bagpipe 4.5), attack 0.018 s, release 0.07 s,
   sustain 0.82. The **octave-coupled second reed** is a second PhaseModSynth
   voice one octave up at amplitude **0.45** (`FM_DEFAULTS["octave_double"]`)
   — do not detune it a few cents; the bandoneón pair is tuned in octaves.
   Smoke: A4 + octave reed peak 1.135, sustain/peak 0.301 (holds, no collapse).
2. **Additive** (`sound/synthesis/additive.py`, SoundWave) — explicit
   octave-heavy harmonic stack, h2/h1 = 0.55 (ADDITIVE_DEFAULTS). Normalize the
   weights before `apply_overtones()` — the API asserts they sum to 1.0.
3. **ModalSynth** (`sound/synthesis/modal.py`) — `'tube'` preset fallback
   (closed-tube/reed-ish resonator; accordion and reed_organ use `'string'`,
   but the tube keeps the hollow odd-harmonic read).

## Production

- **Reverb**: REVERB_TAIL 1.8 s — tango salon/hall. Longer than accordion 1.4
  (a dry bandoneón sounds like a toy), shorter than string_ensemble 2.6.
- **EQ**: cut 250 Hz (wooden-box boom + nasal left-hand resonance); boost
  3 kHz (the reed edge that cuts through an ensemble); gentle 7.5 kHz air
  shelf (valve/key noise, not a cymbal).
- **Pan**: centre for a composed stem; ±0.2 when splitting left-hand bass
  against right-hand treble, or when doubling two bandoneones.
- **Layering**: idiomatic doubling is OCTAVES (the instrument already has an
  octave reed; doubling the part 8vb with the same patch is natural) or
  thirds/sixths with a violin. **NEVER** unison with another melodic patch on
  the same pitches (comb-filtering — the 2026-09-01 rule). A drum kit or a bass
  note an octave+ below is fine.

## Verification

- Registered in `instrument_registry.py` (`"Keys.tango_accordion.tango_accordion":
  "tango_accordion"`, convenience constant `TANGO_ACCORDION`, table role row).
  `registry_table()` row:
  `| Keys | Tango Accordion | 23 | 41–96 | lead, melody, ornament, harmony, accent, pad |`
- `by_name('tango accordion')` / `by_name('TANGO ACCORDION')` → Tango Accordion;
  `by_program(23)` → Tango Accordion, `by_program(21)` → Accordion (distinct);
  `in_sweet_spot(72)` = True, `in_sweet_spot(30)` = False
- Zero-drift UnitMatrixComposer test (1 bar, 1 section, bandoneón + drums
  context) → `validate()` True; MIDI 181 bytes
- Solo FluidSynth render (FluidR3 via `discover_soundfont()`) → WAV 777,004
  bytes; 4–8 kHz buzz energy 8.0% (passes the 20% gate — single voice, no
  comb-filtering)
- RenderPipeline stems: `track00_Tango_Accordion.wav` (777,004 B) +
  `track01_Drums.wav` (706,092 B)

## Stem label / quirks

- GM_PROGRAMS[23] = "Tango Accordion" → `trackXX_Tango_Accordion.wav`;
  FluidR3 preset 23 = **"Bandoneon"** — label mismatch GM-name vs SF2-name,
  cosmetic only (the pipeline names stems from GM_PROGRAMS, not the SF2)
- `MidiInstrument` enum has no GM23 constant — use raw 23; the registry is the
  full KB
- Channel quirk: melodic channel (0–9); channel 9 is the drum map
- Bisonoric reality: a real bandoneón changes note on bellows reversal; a MIDI
  patch cannot. Do not write push/pull-dependent figures (repeated same-button
  alternation); write the sounding line only
- Bisonoric layout is not scale-friendly — real tango players play almost
  entirely on the draw stroke and close the bellows on the air button. Fast
  chromatic runs are idiomatic in the *sound*, not in the fingering; keep
  written runs stepwise
- SF2 ignores portamento (CC5/CC65): write `arrastre` as a fast chromatic
  grace run, not a controller slide
- Polyphony: the patch is polyphonic (chords stack), but the *ensemble* role is
  a single melodic line; avoid dense block chords in the low register (mud)
