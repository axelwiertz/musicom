---
type: instrument
family: Strings
name: Tremolo Strings
midi_program: 44
gms: "Tremolo Strings"
range_min: 24
range_max: 96
solo_range: [53, 89]
role: [accent, tension, texture, harmony, pad, countermelody]
synthesis: [additive, bowed, phase_mod, modal]
---

# Tremolo Strings

## MIDI / GM

- **Program**: 44 (GM1 spec program 45 "Tremolo Strings"; Roland GS
  "Tremolo Strings", Yamaha XG "TremoloStrings")
- **Channel**: melodic channel (0–9); channel 9 would trigger the drum-kit
  map (timpani/taiko lesson)
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 44 =
  "Tremolo" (one-word SF2 spelling vs GM label "Tremolo Strings" — cosmetic
  only, no routing impact). RenderPipeline stem label: GM_PROGRAMS[44] =
  "Tremolo Strings" → `trackXX_Tremolo_Strings.wav` — matches exactly,
  **no quirk**.
- **Not in MidiInstrument enum** (it only exposes 10): use raw 44; the
  registry is the full KB.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 24–96 | C1–C7 | string-section span (empirical FluidR3 sweep: audible every note, SILENT at 108+) |
| Low | 24–47 | C1–B2 | contrabass/cello — rumbling tension bottom, blurs fast, use sparingly |
| Middle | 48–71 | C3–B4 | viola/cello — the underscore workhorse body |
| High | 72–96 | C5–C7 | violin top — cutting, glassy, chattering (sul ponticello zone) |

Sweet spot 60–84 (C4–C6). Low-register tremolo turns into indistinct
rumble fast — write the chattering texture in the mid/upper section and
double the tension with a low sustained string (cello/bass) below.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Tremolo | 70–80 | full | the patch default — sustained rapid bow strokes |
| Sustain | 72–80 | full | regular bowed notes (the sample tremolos regardless — it is amplitude-modulated, measured ripple ~1.0) |
| Sul ponticello | 78–88 | 0.9× | bow near the bridge — glassy, brighter, cutting |
| Staccato | 62–70 | 1/4 | short bow bursts — rhythmic tension |
| Accent | 88–96 | 0.9× | sforzando dig — downbeat stab |
| Crescendo | 74–84 | 1.4× | roll/swell into a peak — the surge-and-release staple |

## Timbre DNA

- **Harmonic content**: dense section stack (many detuned strings); the
  amplitude modulation (tremolo) is the identity — the note chatters at
  ~6–8 Hz bow-stroke rate
- **Attack**: near-instant — the bow is ALREADY moving when the note starts
  (no slow onset, unlike String Ensemble 1's 0.35 s bow swell)
- **Decay/Sustain**: sustained while bowed; no decay plateau — the tremolo
  is a continuous energy
- **Release**: fast stop on bow lift (0.2 s), no ring
- **Character**: tense, chattering, glassy, urgent — the film-score
  "danger" texture; in the high register it turns shimmering/piercing

## Role in Arrangement

- Accent/tension texture (the #1 use: underscore, thriller, chase)
- Pad/harmony layer with motion (a trembling version of String Ensemble 1)
- Countermelody/ostinato in the mid register
- NOT a solo melody voice (the chattering AM eats pitch clarity — the
  vibrato/tremolo masks intonation; solo lines go to violin/string_ensemble)
- NOT a bass voice (low tremolo is rumble, not pitch)

## Synthesis Engines (musicom)

1. **Additive** (`sound/synthesis/additive.py` SoundWave) — **primary**.
   The section = detuned harmonic stack (String Ensemble 1 precedent,
   `section_full` partials, ±0.6% detune, 3 voices). The tremolo itself is
   NOT a synthesis parameter in musicom — write it at the note layer (fast
   repeated 16ths/32nds ≈ 7 Hz) or AM a long note at 7 Hz in production.
2. **BowedString** — single-string physical model; secondary. Faster bow
   (`bow_velocity` 0.26 — tremolo bowing is driven) + firm force 1.6; one
   string only, stack 4–8 for section mass.
3. **PhaseModSynth** — saw "string machine" + AM tremolo; cheap 70s alt.
4. **ModalSynth** `'string'` — section pizzicato fallback only.

## Production

- **Reverb**: hall 2.4 s — tension blooms in space but the chattering
  attack must stay defined (string_ensemble 2.6 s is TOO long — the
  tremolo muddies in a huge tail)
- **EQ**: cut 250 Hz low-mid mud (tremolo doubles section mass), boost
  3 kHz bow-stroke bite, gentle 8.5 kHz air
- **Pan**: center; ±0.3 spread for wide section
- **Layering**: idiomatic doubling is octaves or a low sustained string
  below — NEVER unison with another melodic patch (the 2026-09-01
  comb-filter lesson; a section tremolo + unison flute on the same pitch
  is a buzz machine)

## Verification

- GM44 → stem `trackXX_Tremolo_Strings.wav` (label matches, no quirk)
- FluidR3 preset 44 = "Tremolo" (verified from phdr chunk; one-word SF2
  spelling, cosmetic only)
- Empirical FluidR3 sweep: audible 24–96 (rms 0.030–0.045, trem-ripple
  1.00 on every note — the patch IS amplitude-modulated), SILENT at 108
- Solo render spectral check: 4–8 kHz gate passes (no comb-filtering)
- Zero-drift: units end flush at BAR (terminal landmark)
