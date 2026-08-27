---
type: instrument
family: Strings
name: Viola
midi_program: 41
gms: "Viola"
range_min: 48
range_max: 91
solo_range: [55, 79]    # G3-G5 playable, solo repertoire focus G3-E5
role: [harmony, countermelody, lead, accent]
synthesis: [bowed, additive, modal]
---

# Viola

## MIDI / GM

- **Program**: 41 (GM1 Viola) — NOT in `structures/instrument.py` MidiInstrument enum (only 10 instruments exposed; enum values are 1-indexed — VIOLIN=41 there is itself off-by-one vs the 0-indexed convention used here); use raw `program=41`
- **Channel**: any melodic channel (0-9); solo or section voice
- **FluidSynth**: TimGM6mb.sf2 renders GM41 → viola; dark low register (C3-F3) renders soft, use `-g 1.2` to avoid tail truncation
- **Stem label**: pipeline `GM_PROGRAMS[41] = "Viola"` ✓ → `trackXX_Viola.wav`

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 48–91 | C3–G6 | concert viola range (4 strings, C-G-D-A) |
| Sweet spot | 60–76 | C4–E5 | singing register, projects well, solo focus |
| Low | 48–59 | C3–B3 | dark, warm, veiled — alto/bass role, doubles cello |
| High | 72–91 | C5–G6 | bright, intense — thinning above 84 (E6) |

Open strings: C3(48), G3(55), D4(62), A4(69). Solo literature to ~E5 (76); extensions (false harmonics, thumb position) to ~C6 (84); extreme solo extensions to G6 (91). Orchestral section typically C3–E5.

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Sustained (legato) | 65–90 | full note | smooth, steady bow, warm core |
| Staccato | 55–75 | 1/8–1/4 note | short, crisp, separated |
| Spiccato | 50–70 | very short | bouncing bow off string |
| Tremolo | 60–80 | 16th repetitions | rapid bow changes, agitation |
| Pizzicato | 45–65 | short | plucked, woody — warmer/darker than violin |
| Accent/marcato | 85–105 | full note, strong attack | emphasized onset |
| Sul ponticello | 55–70 | sustained | glassy, harsh, near-bridge bow |
| Harmonics (natural) | 40–50 | sustained | airy, flute-like, weak |
| Glissando | — | portamento between notes | slide (MIDI: bend) |

## Timbre DNA

- **Harmonic content**: strong fundamental + prominent 2nd/3rd; overtones darker and less brilliant than violin (larger body, thicker strings → stronger low partials, weaker above 6–8 kHz)
- **Attack**: 15–40 ms (bow contact) — smooth, no clicks; slightly slower than violin
- **Decay**: sustained (bow-driven, no natural decay while bowed)
- **Release**: 75–175 ms (bow lift; between violin and cello)
- **Noise component**: bow scratch transient at attack; body/wind noise in low register
- **Vibrato**: natural 5–6.5 Hz, ±0.2–0.5 semitone (pitch bend or synthesis param); wider in low register, narrower in high

## Role in Arrangement

- Harmony (mid zone C4-E5) — string section inner voice, viola's classic role
- Countermelody (mid register) — pairs with violin/cello
- Lead melody (sweet spot C4-E5) — alto voice, warm expressive solo lines
- Accent (high register) — orchestral hits, sectional color
- NOT bass (cello/double bass own that; low zone only doubles)
- NOT rhythm (sustained melodic voice)

## Synthesis Engines (musicom)

1. **BowedString** (`sound/synthesis/bowed.py`) — physical waveguide, best match
   - Fundamental present, bridge LPF (verify spectral, not argmax)
   - Use `freq = midi_to_freq(pitch)`; delay length `D = sr/freq` (single delay, no sign inversion — do NOT divide by 2)
   - `bow_position` 0.12–0.18 (between violin 0.15-0.2 and cello 0.1-0.15) for viola-like darkness
2. **ModalSynth** preset `string` (`sound/synthesis/modal.py`) — pluck/attack, good for pizzicato
3. **PhaseModSynth** — additive harmonics for synthetic viola pad texture

## Production

- **Reverb**: hall, 1.8–2.5 s tail (solo viola); shorter 1.5 s for section
- **EQ**: cut 250–400 Hz boxiness/nasality; boost 2–3 kHz presence/bow; high shelf subtle above 7 kHz (less air than violin, more than cello)
- **Delay**: none for legato; dotted 8th echo for pop lines
- **Pan**: center (solo), -0.15/-0.25 for section placement; low register sits well mono

## Verification

- GM41 renders as `trackXX_Viola.wav` in RenderPipeline stems — pipeline `GM_PROGRAMS[41] = "Viola"` ✓ (no quirk)
- Verified end-to-end: UnitMatrixComposer → zero-drift validate ✓ → MIDI → FluidSynth WAV ✓ (2026-08-23)
- Bowed string: check fundamental PRESENT in spectrum (not global argmax — bridge LPF boosts harmonics)
