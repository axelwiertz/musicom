---
type: instrument
family: Brass
name: Trombone
midi_program: 57
gms: "Trombone"
range_min: 40
range_max: 78
solo_range: [52, 72]    # E3-C5 playable, melodic sweet spot G3-A4
role: [bass, countermelody, accent, harmony]
synthesis: [phase_mod, additive]
---

# Trombone

## MIDI / GM

- **Program**: 57 — 0-indexed MIDI program = strict GM #58 (Trombone). Convention matches verified strings entries (violin=40, cello=42 are 0-indexed). NOT in `structures/instrument.py` MidiInstrument enum (only 10 instruments exposed, and enum uses 1-indexed GM numbers — TRUMPET=57 is itself off-by-one); use raw `program=57`
- **Channel**: any melodic channel (0-9); solo or section voice
- **FluidSynth**: TimGM6mb.sf2 preset 57 = `Trombone` (verified from phdr chunk) → renders actual trombone; low register (E2-G3) renders dark, use `-g 1.2` to avoid tail truncation
- **Stem label**: pipeline `GM_PROGRAMS[57] = "Trombone"` ✓ → `trackXX_Trombone.wav`

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 40–78 | E2–F5 | concert trombone range (tenor trombone, Bb-F) |
| Sweet spot | 55–70 | G3-A4 | most characteristic, projects well, solo focus |
| Low | 40–53 | E2-E3 | dark, powerful, bass/foundation role |
| High | 66–78 | F#4-F5 | bright, intense, tenor/treble — thinning above 72 |

Open positions: Bb1(34), F2(41), Bb2(46), D3(50), F3(53), Ab3(56), Bb3(58). Bass trombone extends to B1(35) with F attachment; tenor literature tops at ~F5 (78), orchestral at ~D5-E5 (74-76).

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Sustained (legato) | 70–90 | full note | smooth, steady breath, warm core |
| Tenuto | 65–80 | 9/10 note | full weight, slight separation |
| Staccato | 55–75 | 1/8–1/4 note | short, crisp, separated |
| Marcato | 85–100 | full note, strong attack | emphasized onset, punchy |
| Sforzando | 95–110 | strong attack, decay | explosive onset, quick decay |
| Glissando | 60–80 | slide between notes | characteristic slide (MIDI: bend or stepwise) |
| Muted (straight) | 50–70 | sustained | nasal, focused, distant |
| Flutter tongue | 65–85 | sustained | rapid tongue flutter, agitation |

## Timbre DNA

- **Harmonic content**: strong fundamental + prominent 2nd/3rd/4th harmonics; brass-like odd/even partial balance, less bright than trumpet
- **Attack**: 30–60 ms (lip/breath onset) — slower than trumpet, more "bloom"
- **Decay**: sustained (breath-driven, no natural decay while blown)
- **Release**: 80–150 ms (breath release; longer than trumpet)
- **Noise component**: breath noise transient at attack; slide noise in glissandi
- **Vibrato**: subtle 4–5 Hz, ±0.1–0.3 semitone (less than strings); used sparingly in jazz/solo

## Role in Arrangement

- Bass/foundation (low zone E2-E3) — doubles bass trombone or tuba in brass section
- Countermelody (mid register G3-A4) — lyrical lines, pairs with horns
- Accent/fanfare (high register) — punchy hits, marcato figures
- Harmony (mid-low register) — section pads, brass choir inner voice
- NOT lead melody (less agile than trumpet; possible in jazz/solo contexts)
- NOT rhythm (sustained melodic voice)

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — FM synthesis, best match for brass
   - Carrier: sawtooth (rich harmonics); modulator: sine at 1:1 ratio for brass-like spectrum
   - Mod depth 2–4 for characteristic brass "bite"; lower than trumpet (3.0 vs 4.0)
   - Attack 30–50 ms (slower than trumpet); release 100–150 ms
   - Use `freq = midi_to_freq(pitch)`
2. **Additive** (`sound/synthesis/additive.py`) — explicit harmonic control
   - Build brass spectrum: fundamental + 2nd/3rd/4th strong, 5th+ rolling off
   - Good for synthetic brass pad or ensemble texture
3. **ModalSynth** — less suitable (better for strings/percussion); avoid for brass

## Production

- **Reverb**: hall, 1.2–2.0 s tail (solo trombone); shorter 1.0 s for section
- **EQ**: cut 300–400 Hz nasal honk; boost 2–3 kHz presence/bell; high shelf subtle above 6 kHz (less air than trumpet)
- **Delay**: none for legato; dotted 8th echo for jazz lines
- **Pan**: center (solo), -0.2/-0.3 for section placement; low register sits well mono

## Verification

- GM57 renders as `trackXX_Trombone.wav` in RenderPipeline stems — pipeline `GM_PROGRAMS[57] = "Trombone"` ✓ (0-indexed list; no quirk)
- Verified end-to-end: UnitMatrixComposer → zero-drift validate ✓ → MIDI → FluidSynth WAV ✓ (2026-08-22)
- Brass: check fundamental PRESENT in spectrum (FM synthesis may boost harmonics; verify spectral, not argmax)
