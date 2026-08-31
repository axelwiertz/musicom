---
type: instrument
family: Woodwind
name: Bassoon
midi_program: 70
gms: "Bassoon"
range_min: 34
range_max: 88
solo_range: [43, 74]    # Bb1-E6 playable, solo repertoire focus G2-D5
role: [bass, harmony, countermelody, lead]
synthesis: [phase_mod, additive]
---

# Bassoon

## MIDI / GM

- **Program**: 70 — 0-indexed MIDI program = strict GM #71 (Bassoon). NOT in `structures/instrument.py` MidiInstrument enum (only 10 instruments exposed); use raw `program=70`
- **Channel**: any melodic channel (0-9); bass voice of the woodwind choir
- **FluidSynth**: prefers FluidR3_GM.sf2 (preset 70 = `Bassoon`, full low-end)
  over TimGM6mb.sf2 (`Bassoon`, thin). `discover_soundfont()` picks FluidR3
  automatically when present.
- **Stem label**: pipeline `GM_PROGRAMS[70] = "Bassoon"` ✓ → `trackXX_Bassoon.wav` (label matches, no quirk)

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 34–88 | Bb1–E6 | concert bassoon range (sounding pitch) |
| Sweet spot | 48–72 | C3–C5 | most characteristic, warm singing tenor register |
| Low | 34–52 | Bb1–E3 | bass register, reedy dark, tuba-like weight, blends into bass |
| Mid | 53–72 | F3–C5 | warm, vocal, the bassoon "money" register — expressive |
| High | 73–88 | Db5–E6 | alto register, expressive, reedy/thin above ~A5 (81) |

Orchestral bass writing sits Bb1–C4 (34–60); solo literature spans G2–D5 (43–74); altissimo to C6 (84) common in virtuoso writing, E6 (88) is the practical top.

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Legato | 70–90 | full note | smooth, reedy, warm vocal core |
| Tenuto | 60–75 | 9/10 note | full weight, slight separation |
| Staccato | 50–70 | 1/8–1/4 note | short, crisp tongue stop — double-tongue possible |
| Marcato | 80–100 | full note, strong attack | emphasized onset, punchy |
| Accent | 85–100 | full note, strong attack | emphasized onset |
| Flutter tongue | 55–75 | sustained | rapid tongue flutter, agitation (rare) |
| Glissando/portamento | 55–75 | smear between notes | vocal slide, rare (jazz/avant-garde) |

## Timbre DNA

- **Harmonic content**: strong fundamental + even/odd mix (double reed), 2nd/3rd strong, upper harmonics present but softer than oboe — darker, tuba-like low end
- **Attack**: 40–80 ms (double-reed air onset) — slower than clarinet, similar to oboe
- **Decay**: sustained (breath-driven, no natural decay while blown)
- **Release**: 60–140 ms (breath release)
- **Noise component**: reed buzz (transient at attack); key clacks in fast passagework; breath noise
- **Vibrato**: natural 4–6 Hz, narrow (classical); more in jazz/pop solo lines

## Role in Arrangement

- Bass (low zone Bb1–E3) — bass of the woodwind choir, doubles cello/contrabass
- Harmony (mid register) — inner-voice support, tenor line in woodwind choir
- Countermelody (mid register) — distinctive reedy counter-line, cuts through
- Lead (solo repertoire G2–D5) — tenor solo voice, characterful
- NOT rhythm (sustained melodic voice; staccato possible but not idiomatic)
- NOT pad (single-reed double-reed voice, not sustained chordal)

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — PM/FM synthesis, best match for double-reed
   - Carrier: triangle; modulator: sine at 1:1 ratio; mod depth 2.0 (darker than oboe, brighter than tuba)
   - Attack 50–80 ms (double reed speaks slow-ish); release 100–140 ms
   - `render_note(freq=midi_to_freq(pitch), duration=..., carrier_shape='triangle', mod_freq_ratio=1.0, mod_depth=2.0, attack=0.06, release=0.12)`
2. **Additive** (`sound/synthesis/additive.py`) — explicit harmonic control
   - Build bassoon spectrum: strong fundamental + even/odd mix (double reed), 2nd/3rd strong, upper harmonics softer than oboe
3. **ModalSynth** — less suitable (better for strings/percussion); avoid for double reeds

## Production

- **Reverb**: hall, 1.4–2.0 s tail (medium — keep articulation clarity); plate for pop
- **EQ**: cut 200–400 Hz mud/boxiness; boost 2–3 kHz presence/definition; gentle high shelf above 6 kHz (reed/key noise air)
- **Delay**: none for classical; dotted 8th echo for pop/jazz solo lines (rare)
- **Pan**: center (solo); slight off-center -0.15..-0.25 in section

## Verification

- GM70 renders as `trackXX_Bassoon.wav` in RenderPipeline stems — pipeline `GM_PROGRAMS[70] = "Bassoon"` ✓ (0-indexed list; no quirk)
- SF2 preset 70 = `Bassoon` (name matches pipeline label — no cosmetic difference)
- Verified end-to-end: UnitMatrixComposer → zero-drift validate ✓ → MIDI → FluidSynth WAV ✓ (2026-08-28)
- Woodwind reed: check fundamental PRESENT in spectrum (PM synthesis may boost harmonics; verify spectral, not argmax)
