---
type: instrument
family: Strings
name: Cello
midi_program: 42
gms: "Cello"
range_min: 36
range_max: 84
solo_range: [48, 76]    # C2-C6 playable, solo repertoire focus C3-E5
role: [bass, melody, countermelody, harmony]
synthesis: [bowed, modal, additive]
---

# Cello

## MIDI / GM

- **Program**: 42 (GM1 Cello) — NOT in `structures/instrument.py` MidiInstrument enum (only 10 instruments exposed); use raw `program=42`
- **Channel**: any melodic channel (0-9); solo or section voice
- **FluidSynth**: TimGM6mb.sf2 renders GM42 → solo cello; low register (C2-C3) renders dark, use `-g 1.2` to avoid tail truncation

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 36–84 | C2–C6 | concert cello range (4 strings, C-G-D-A) |
| Sweet spot | 48–67 | C3–G4 | singing register, projects well, solo focus |
| Low | 36–47 | C2–B2 | dark, rich, warm — bass/foundation role |
| High | 68–84 | G4–C6 | bright, intense, tenor/treble — thinning above 76 |

Open strings: C2(36), G2(43), D3(50), A3(57). Thumb position extends past A5; solo literature to ~E5 (76), extensions to C6.

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Sustained (legato) | 65–90 | full note | smooth, steady bow, warm core |
| Staccato | 55–75 | 1/8–1/4 note | short, crisp, separated |
| Spiccato | 50–70 | very short | bouncing bow off string |
| Tremolo | 60–80 | 16th repetitions | rapid bow changes, agitation |
| Pizzicato | 45–65 | short | plucked, woody, no bow — lower & richer than violin |
| Accent/marcato | 85–105 | full note, strong attack | emphasized onset |
| Sul ponticello | 55–70 | sustained | glassy, harsh, near-bridge bow |
| Harmonics (natural) | 40–50 | sustained | airy, flute-like, weak |
| Glissando | — | portamento between notes | slide (MIDI: bend) |

## Timbre DNA

- **Harmonic content**: strong fundamental + prominent 2nd/3rd; overtones rich but darker than violin (larger body, longer string → more low partials)
- **Attack**: 20–50 ms (bow contact) — smooth, no clicks
- **Decay**: sustained (bow-driven, no natural decay while bowed)
- **Release**: 100–200 ms (bow lift; longer than violin)
- **Noise component**: bow scratch transient at attack; body/wind noise in low register
- **Vibrato**: natural 5–6 Hz, ±0.2–0.5 semitone (pitch bend or synthesis param); slower/wider in low register

## Role in Arrangement

- Bass/foundation (low zone C2-B2) — doubles or replaces double bass in pop/indie
- Lead melody (sweet spot C3-G4) — expressive solo lines
- Countermelody (mid register) — pairs with violin
- Harmony (mid register) — section pads, string quartet inner voice
- NOT rhythm (sustained melodic voice)

## Synthesis Engines (musicom)

1. **BowedString** (`sound/synthesis/bowed.py`) — physical waveguide, best match
   - Fundamental present, bridge LPF (verify spectral, not argmax)
   - Use `freq = midi_to_freq(pitch)`; fix octave via `D = sr/(2*freq)`
   - Lower `bow_position` (0.1-0.15) for darker cello-like tone vs violin 0.15-0.2
2. **ModalSynth** preset `string` (`sound/synthesis/modal.py`) — pluck/attack, good for pizzicato
3. **PhaseModSynth** — additive harmonics for synthetic cello pad texture

## Production

- **Reverb**: hall, 2–3 s tail (solo cello); shorter 1.5 s for section
- **EQ**: cut 250–400 Hz boxiness; boost 2–3 kHz presence/bow; high shelf subtle above 8 kHz (less air than violin)
- **Delay**: none for legato; dotted 8th echo for pop lines
- **Pan**: center (solo), -0.2/-0.3 for section placement; low register sits well mono

## Verification

- GM42 renders as `trackXX_Cello.wav` in RenderPipeline stems — pipeline `GM_PROGRAMS[42] = "Cello"` ✓ (no quirk)
- Verified end-to-end: UnitMatrixComposer → zero-drift validate ✓ → MIDI → FluidSynth WAV ✓ (2026-08-21)
- Bowed string: check fundamental PRESENT in spectrum (not global argmax — bridge LPF boosts harmonics)
