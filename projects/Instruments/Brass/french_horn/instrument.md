---
type: instrument
family: Brass
name: French Horn
midi_program: 60
gms: "French Horn"
range_min: 41
range_max: 84
solo_range: [53, 77]    # F2-C6 playable, solo sweet spot F3-F5
role: [harmony, countermelody, accent, lead]
synthesis: [phase_mod, additive]
---

# French Horn

## MIDI / GM

- **Program**: 60 — 0-indexed MIDI program = strict GM #61 (French Horn). NOT in `structures/instrument.py` MidiInstrument enum (only 10 instruments exposed); use raw `program=60`
- **Channel**: any melodic channel (0-9); solo or section voice
- **FluidSynth**: TimGM6mb.sf2 preset 60 = `French Horns` (plural, verified from phdr chunk) → renders horn section color; use `-g 1.2` to avoid tail truncation
- **Stem label**: pipeline `GM_PROGRAMS[60] = "French Horn"` ✓ → `trackXX_French_Horn.wav` (label singular, SF2 preset plural — cosmetic only, no routing impact)

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 41–84 | F2–C6 | concert horn range (sounding pitch; F transposing instrument) |
| Sweet spot | 53–77 | F3–F5 | most characteristic, warm singing, solo focus |
| Low | 41–55 | F2–G3 | dark, mellow, muffled — pedal tones B1-F2, blends into section |
| Mid | 56–72 | G#3–C5 | warm, round, horn-section foundation |
| High | 73–84 | C#5–C6 | bright, heroic, projecting — thin/fragile above ~G5 (79) |

Pedal tones down to B1(35) possible but weak; orchestral literature tops at ~C6 (84), most solo writing G5-A5 (79-81).

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Sustained (legato) | 70–90 | full note | smooth, round, warm core |
| Tenuto | 65–80 | 9/10 note | full weight, slight separation |
| Staccato | 55–70 | 1/8–1/4 note | short, crisp, tongue stop |
| Marcato | 85–100 | full note, strong attack | emphasized onset, punchy |
| Sforzando | 95–110 | strong attack, decay | explosive onset, quick decay |
| Stopped (hand/mute) | 50–70 | sustained | nasal, buzzy, distant — transposes up a semitone acoustically |
| Flutter tongue | 65–85 | sustained | rapid tongue flutter, agitation |
| Glissando/rip | 60–80 | smear between notes | horn rip, rare (jazz/pop) |

## Timbre DNA

- **Harmonic content**: strong fundamental + prominent 2nd/3rd/4th/5th; conical bore brass — less bright than trumpet, more rounded than trombone
- **Attack**: 40–80 ms (air/lip onset) — slowest bloom of the brass section
- **Decay**: sustained (breath-driven, no natural decay while blown)
- **Release**: 80–150 ms (breath release)
- **Noise component**: breath noise at attack; stopped-horn buzz; valve clack (transient)
- **Vibrato**: subtle 4–5 Hz, ±0.1–0.3 semitone (hand vibrato in jazz/solo); classical uses none

## Role in Arrangement

- Harmony (mid-low zone G#3-C5) — horn section pads, brass choir inner voice, the horn's #1 job
- Countermelody (mid register F3-F5) — lyrical lines against strings/woodwinds
- Accent/fanfare (high register) — heroic hits, hunting-call figures
- Lead (solo register F3-F5) — exposed solos, film-score melody
- NOT bass (low register too dark/quiet; use trombone/tuba)
- NOT rhythm (sustained melodic voice)

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — FM synthesis, best match for brass
   - Carrier: sawtooth; modulator: sine at 1:1 ratio; mod depth 2.5 (between trombone 2–4 and trumpet 4.0 — horn is rounder)
   - Attack 60–80 ms (slower than trumpet — horn blooms); release 120–150 ms
   - `render_note(freq=midi_to_freq(pitch), duration=..., carrier_shape='saw', mod_freq_ratio=1.0, mod_depth=2.5, attack=0.07, release=0.13)`
2. **Additive** (`sound/synthesis/additive.py`) — explicit harmonic control
   - Build horn spectrum: fundamental + 2nd/3rd/4th strong, 5th+ rolling off, brighter than trombone but less than trumpet
3. **ModalSynth** — less suitable (better for strings/percussion); avoid for brass

## Production

- **Reverb**: hall, 1.8–2.5 s tail (solo horn); 1.2–1.5 s for section blend
- **EQ**: cut 400–500 Hz nasal honk; boost 2–3 kHz presence; gentle high shelf above 6 kHz (less air than trumpet)
- **Delay**: none for classical; dotted 8th echo for pop solo lines
- **Pan**: center (solo); spread -0.3/-0.2/+0.2/+0.3 for horn quartet; section sits well mid-left/right

## Verification

- GM60 renders as `trackXX_French_Horn.wav` in RenderPipeline stems — pipeline `GM_PROGRAMS[60] = "French Horn"` ✓ (0-indexed list; no quirk)
- SF2 preset 60 = `French Horns` (plural) — label cosmetic difference only
- Verified end-to-end: UnitMatrixComposer → zero-drift validate ✓ → MIDI → FluidSynth WAV ✓ (2026-08-26)
- Brass: check fundamental PRESENT in spectrum (FM synthesis may boost harmonics; verify spectral, not argmax)
