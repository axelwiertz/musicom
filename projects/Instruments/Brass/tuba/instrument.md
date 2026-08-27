---
type: instrument
family: Brass
name: Tuba
midi_program: 58
gms: "Tuba"
range_min: 26
range_max: 72
solo_range: [36, 62]    # D1-C5 playable, solo repertoire focus C2-D4
role: [bass, harmony, accent, rhythm]
synthesis: [phase_mod, additive]
---

# Tuba

## MIDI / GM

- **Program**: 58 — 0-indexed MIDI program = strict GM #59 (Tuba). NOT in `structures/instrument.py` MidiInstrument enum (only 10 instruments exposed); use raw `program=58`
- **Channel**: any melodic channel (0-9); bass voice of the brass choir
- **FluidSynth**: TimGM6mb.sf2 preset 58 = `Tuba` (verified from phdr chunk) → renders tuba bass; use `-g 1.2` to avoid tail truncation
- **Stem label**: pipeline `GM_PROGRAMS[58] = "Tuba"` ✓ → `trackXX_Tuba.wav` (label matches, no quirk)

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 26–72 | D1–C5 | concert tuba range (CC/BBb tuba, sounding pitch) |
| Sweet spot | 43–58 | G2–Bb3 | most characteristic, full round tuba tone, foundation register |
| Low | 26–42 | D1–F2 | pedal/contra, dark sub-bass, blends into section, quiet |
| Mid | 43–58 | G2–Bb3 | warm, round, the tuba "money" register — projects well |
| High | 59–72 | C4–C5 | solo/tenor, bright, effortful above ~G4 (67), thin at top |

Pedal tones down to C1(24) possible on CC tuba but weak; orchestral literature spans D1–F4 (26–65), most solo writing G2–E4 (43–64). Above C5 (72) is virtuoso/extended territory.

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Sustained (legato) | 70–90 | full note | smooth, round, fat core |
| Tenuto | 65–80 | 9/10 note | full weight, slight separation |
| Staccato | 55–70 | 1/8–1/4 note | short, crisp, tongue stop — faster than it looks |
| Marcato | 85–100 | full note, strong attack | emphasized onset, punchy bass hits |
| Sforzando | 95–110 | strong attack, decay | explosive onset, quick decay |
| Flutter tongue | 65–85 | sustained | rapid tongue flutter, agitation |
| Glissando/rip | 60–80 | smear between notes | slide (valve/trombone-style in jazz), rare |

## Timbre DNA

- **Harmonic content**: very strong fundamental + moderate 2nd/3rd, upper harmonics roll off fast — darkest of the brass family, lowest harmonic brightness
- **Attack**: 30–70 ms (lip/air onset) — large mouthpiece speaks slower than trumpet/trombone
- **Decay**: sustained (breath-driven, no natural decay while blown)
- **Release**: 80–160 ms (breath release)
- **Noise component**: breath noise at attack; valve clack (transient); no reed/mechanical buzz
- **Vibrato**: not native — none in classical; subtle 4–5 Hz in jazz/pop solo lines

## Role in Arrangement

- Bass (low-mid zone D1–Bb3) — foundation of the brass choir, the tuba's #1 job
- Harmony (mid register) — doubling basses/left-hand piano at octave, root-of-chord anchor
- Accent (low register) — sub-bass hits, oom-pah bass lines, march rhythm
- Rhythm (walking bass) — jazz/pop walking bass lines in the low-mid register
- NOT lead (high register too effortful/thin for sustained melody)
- NOT countermelody (too dark/low to cut through except as bass counter-line)

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — FM synthesis, best match for brass
   - Carrier: sawtooth; modulator: sine at 1:1 ratio; mod depth 2.0 (darker/rounder than trombone 3.0 — tuba has fewer strong upper harmonics)
   - Attack 50–70 ms (large mouthpiece speaks slow); release 140–160 ms
   - `render_note(freq=midi_to_freq(pitch), duration=..., carrier_shape='saw', mod_freq_ratio=1.0, mod_depth=2.0, attack=0.06, release=0.16)`
2. **Additive** (`sound/synthesis/additive.py`) — explicit harmonic control
   - Build tuba spectrum: dominant fundamental + gentle 2nd/3rd, 4th+ rolls off fast (lowest brass brightness)
3. **ModalSynth** — less suitable (better for strings/percussion); avoid for brass

## Production

- **Reverb**: hall, 1.2–1.8 s tail (keep bass definition — long reverb muddies low end); plate for pop
- **EQ**: cut 150–250 Hz mud/boxiness; boost 1–2 kHz presence/definition; gentle high shelf above 4 kHz (least air of brass)
- **Delay**: none for classical; dotted 8th echo for jazz/pop walking lines (rare)
- **Pan**: center (solo/root anchor); slight off-center -0.2..-0.3 in section — keep low end centered

## Verification

- GM58 renders as `trackXX_Tuba.wav` in RenderPipeline stems — pipeline `GM_PROGRAMS[58] = "Tuba"` ✓ (0-indexed list; no quirk)
- SF2 preset 58 = `Tuba` (name matches pipeline label — no cosmetic difference)
- Verified end-to-end: UnitMatrixComposer → zero-drift validate ✓ → MIDI → FluidSynth WAV ✓ (2026-08-27)
- Brass: check fundamental PRESENT in spectrum (FM synthesis may boost harmonics; verify spectral, not argmax)
