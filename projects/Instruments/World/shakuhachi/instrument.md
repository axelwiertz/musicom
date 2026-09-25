---
type: instrument
family: World
name: Shakuhachi
midi_program: 77
gms: "Shakuhachi"
range_min: 55
range_max: 100
solo_range: [62, 86]
role: [lead, melody, ornament, drone, accent]
synthesis: [phase_mod, additive]
---

# Shakuhachi

## MIDI / GM

- **Program**: 77 (GM Shakuhachi)
- **Channel**: melodic channel; monophonic line instrument
- **Stem label**: GM_PROGRAMS[77] = "Shakuhachi" (exact match, no quirk)
- **FluidR3 preset 77** = "Shakuhachi" (exact match, no quirk)

## Range

| Zone | Japanese | MIDI | Pitches | Register |
|------|----------|------|---------|----------|
| Full range (1.8 shaku) | — | 62–86 | D4–D6 | standard 2 octaves |
| Full range (longer flutes) | — | 55–100 | G3–E7 | extended (2.4 shaku → A3, expert → E7) |
| Otsu (lower) | 乙/呂 | 62–73 | D4–D5 | dark, full, meditative — honkyoku core |
| Kan (upper) | 甲 | 74–85 | E5–D6 | bright, penetrating, clear |
| Dai-kan (3rd octave) | 大甲 | 86–100 | E6–E7 | airy, stretched, expert only |

## Articulations

| Technique | Velocity | Duration | Timbre |
|-----------|----------|----------|--------|
| Legato | 65–80 | full | smooth, connected (oshi finger hit) |
| Staccato | 55–65 | 1/8–1/4 | short oshi break (not tongued) |
| Muraiki | 85–100 | sustained | explosive breath blast attack |
| Meri (bend ↓) | 70–80 | sustained | pitch lowered by embouchure/angle change |
| Kari (bend ↑) | 75–85 | sustained | pitch raised by embouchure/angle change |
| Yuri (vibrato) | 65–80 | sustained | horizontal pitch modulation (5–6 Hz) |
| Accent | 88–100 | full | emphasized tsuyoshi oshi hit |
| Breath tone | 40–55 | sustained | airy, whispery, minimal defined pitch |

## Timbre DNA

- **Harmonic content**: fundamental strong, moderate 2nd/3rd harmonics; significant breath noise above 6 kHz (the "wind in bamboo" character)
- **Attack**: 40–90 ms (breath onset with characteristic "fu" sound — the muraiki blast attack can be near-instantaneous at 20 ms)
- **Decay**: sustained but breath-driven; the bamboo tube rings briefly after breath stops (~200 ms)
- **Release**: 150–300 ms (bamboo resonance after blow ceases)
- **Vibrato**: yuri (horizontal pitch modulation, 5–6 Hz, moderate depth) — distinct from Western flute vibrato (amplitude-based)
- **Character**: breathy, meditative, woody; can be soft/ethereal or piercing/projecting
- **Pitch bending**: meri/kari can bend a whole tone or more — seamlessly glissando (composition jobs can use pitch-bend MIDI events)

## Role in Arrangement

- Lead melody (otsu/kan register — the honkyoku line)
- Ornamentation (meri/kari slides, muraiki accents, yuri vibrato)
- Drone/pedal (long sustained notes, Zen meditation style)
- Accent/SFX (muraiki breath blasts, percussive finger strikes)
- **Line-instrument quirk**: monophonic bamboo flute — no dense chords or harmony. Pairs naturally with koto (GM107), shamisen (GM106), taiko (GM116).

## Synthesis Engines (musicom)

1. **PhaseModSynth** — primary: carrier sine + modulator sine, ratio 1.0, depth 2.0 (more than flute 1.5: shakuhachi has richer upper harmonics). Attack 0.06 s (breath transient), release 0.20 s (bamboo ring). Add noise component for the breathy muraiki character.

2. **Additive** — alternative: fundamental + small 2nd/3rd harmonics + noise floor above 6 kHz; good for sustained Zen-style tones.

3. **BowedString** — not recommended (wrong physics; no bow friction in an end-blown flute).

4. **Karplus-Strong** — not applicable (no string/reed; the bamboo tube resonator is not a waveguide).

## Production

- **Reverb**: hall 2.0–3.0 s (shakuhachi loves large temple/hall spaces; the longest tail in the World family after taiko)
- **EQ**: cut 300–500 Hz (bamboo box resonance); boost 3–5 kHz (breath edge presence); high shelf 8 kHz (airy breath shimmer)
- **Delay**: subtle dotted 8th for ambient/meditative contexts
- **Pan**: center for solo; slightly left when paired with koto or shamisen

## Verification

- GM77 renders as `trackXX_Shakuhachi.wav` in RenderPipeline stems (exact match, no quirk)
- Airy check: noise energy above 6 kHz present (breath/muraiki component)
- Pentatonic/meri character: shakuhachi is tuned to D-minor pentatonic; fully chromatic via meri/kari bending but best idiomatic writing is pentatonic lines with occasional chromatics
- Longer flutes: 2.4-shaku shakuhachi has fundamental of A3 (MIDI 57); composition jobs targeting deeper register use notes 55–60