---
type: instrument
family: Strings
name: Double Bass
midi_program: 43
gms: "Contrabass"
range_min: 28
range_max: 74
solo_range: [40, 62]    # E1-D5 playable, solo repertoire focus E2-D4
role: [bass, rhythm, accent, harmony]
synthesis: [bowed, modal, additive]
---

# Double Bass

## MIDI / GM

- **Program**: 43 — 0-indexed MIDI program = strict GM #44 (Contrabass). Same convention as violin=40/viola=41/cello=42. NOT in `structures/instrument.py` MidiInstrument enum (only 10 instruments exposed); use raw `program=43`
- **Channel**: any melodic channel (0-9); bass/section voice
- **FluidSynth**: TimGM6mb.sf2 preset 43 = `Contrabass` (verified from phdr chunk) → renders actual bowed bass; low register (E1-G2) renders dark/subby, use `-g 1.2` to avoid tail truncation
- **Stem label**: pipeline `GM_PROGRAMS[43] = "Contrabass"` ✓ → `trackXX_Contrabass.wav` (no quirk — name differs from folder/module `double_bass`, that's the actual label)

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 28–74 | E1–D5 | concert double bass range (4 strings, E-A-D-G) |
| Sweet spot | 40–55 | E2–G3 | foundation register, most characteristic, best projection |
| Low | 28–39 | E1–D#2 | sub-bass, dark, powerful — below ~35 loses definition in mix |
| High | 53–74 | F3–D5 | tenor/treble, solo virtuoso — thinning above 62 |

Open strings: E1(28), A1(33), D2(38), G2(43). 5-string extends to C1(24). Orchestral parts rarely exceed A4(69); solo literature (bowed, higher positions) to ~D5(74). Pizzicato sounds an octave lower than written in jazz/pop feel.

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Sustained (legato) | 60–90 | full note | smooth bow, warm dark core |
| Pizzicato | 45–70 | short | plucked, woody thump — THE bass voice in jazz/pop |
| Staccato | 50–75 | 1/8–1/4 note | short, separated, punchy |
| Spiccato | 45–65 | very short | bouncing bow, light |
| Tremolo | 55–80 | 16th repetitions | rapid bow, agitation (dramatic low strings) |
| Accent/marcato | 85–105 | full note, strong attack | emphasized onset, heavy |
| Sul ponticello | 50–70 | sustained | glassy, raspy, near-bridge bow |
| Harmonics (natural) | 40–50 | sustained | airy, flute-like, weak |
| Glissando | — | portamento between notes | slide (MIDI: bend) — jazz/pop staple |

## Timbre DNA

- **Harmonic content**: strong fundamental + modest 2nd/3rd; low partials dominate, rolls off fast above 1–2 kHz (shortest/largest string of the family → darkest)
- **Attack**: 30–80 ms (bow contact, heavy string) — slowest of strings; pizzicato attack 1–5 ms (pluck transient)
- **Decay**: sustained (bow-driven while bowed); pizzicato decays naturally 300–800 ms
- **Release**: 100–250 ms (bow lift; slowest of strings)
- **Noise component**: bow scratch at attack; fingerboard thump in pizzicato
- **Vibrato**: 4–5 Hz, ±0.2–0.4 semitone (slower/wider than violin); sparse in orchestral bass lines, more in solo

## Role in Arrangement

- Bass/foundation (low zone E1-D#2) — THE bass instrument of the strings family; doubles cello an octave down or tuba in orchestra
- Rhythm (pizzicato, mid-low) — walking bass, root/fifth pulse in jazz/pop/rockabilly
- Accent (pizzicato hits, marcato) — punchy downbeats, dramatic low punctuations
- Harmony (sustained low pedal) — pedal tones, drone, cinematic low pads
- NOT lead melody (except solo/jazz contexts, high register)
- NOT countermelody (too heavy, slow attack)

## Synthesis Engines (musicom)

1. **BowedString** (`sound/synthesis/bowed.py`) — physical waveguide, best match
   - Fundamental present, bridge LPF (verify spectral, not argmax)
   - Use `freq = midi_to_freq(pitch)`; fix octave via `D = sr/(2*freq)`
   - Lowest `bow_position` of the family (0.08–0.12) → darkest tone; low `lpf_coef` (0.4–0.5) for sub-bass roll-off
2. **ModalSynth** preset `string` (`sound/synthesis/modal.py`) — pluck/attack, good for pizzicato (the characteristic bass voice)
3. **PhaseModSynth** — additive harmonics for synthetic sub/pad bass texture

## Production

- **Reverb**: hall, 1.5–2.0 s tail (solo); shorter 1.0–1.2 s for section — keep bass defined, avoid mud
- **EQ**: cut 200–300 Hz mud/boxiness; boost 1–2 kHz string attack/wood presence; high shelf minimal (little air above 6 kHz); sub below 40 Hz highpass in dense mixes
- **Delay**: none for bass lines; dotted 8th echo only for solo jazz statements
- **Pan**: center (solo or section); low register sits well mono — do NOT spread bass wide

## Verification

- GM43 renders as `trackXX_Contrabass.wav` in RenderPipeline stems — pipeline `GM_PROGRAMS[43] = "Contrabass"` ✓ (no quirk; label is "Contrabass", not "Double_Bass")
- Verified end-to-end: UnitMatrixComposer → zero-drift validate ✓ → MIDI → FluidSynth WAV ✓ (2026-08-24)
- Bowed string: check fundamental PRESENT in spectrum (not global argmax — bridge LPF boosts harmonics)
