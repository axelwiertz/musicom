---
type: instrument
family: World
name: Fiddle
midi_program: 110
gms: "Fiddle"
range_min: 55
range_max: 96
solo_range: [60, 89]
role: [lead, melody, ornament, countermelody, accent]
synthesis: [bowed, modal, phase_mod]
---

# Fiddle

## MIDI / GM

- **Program**: 110 (GM2 Fiddle; 0-indexed — the 111th entry of the GM1
  list). NOT in `structures/instrument.py` `MidiInstrument` enum (10 only) —
  use raw `program=110` in `add_voice`.
- **Channel**: any melodic channel (0-9); line voice — one melodic line (or
  drone double-stop), not dense chords.
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 110 =
  "Fiddle" (phdr-verified). RenderPipeline stem label: GM_PROGRAMS[110] =
  "Fiddle" → `trackXX_Fiddle.wav` — matches exactly, **no quirk**.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 55–96 | G3–C6 | concert fiddle (violin-dimension, GDAE) |
| Low | 55–61 | G3–B3 | dark open-G register — drones, double stops |
| Middle (tune) | 62–77 | D4–F5 | primary melodic register — where folk tunes live |
| High | 78–96 | F#5–C6 | bright, singing, cutting; ornaments (grace notes, high kicks) |

Practical melodic core is C4–E6 (60–88). The GDAE first position covers
G3–E5 with no shifting; quick shifts reach C6 (96). Fiddle style adds double
stops (open-string drones under the melody) — the *one* harmony trick this
line voice allows.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Sustain (long bow) | 70–90 | full note | steady folk line |
| Drive (heavy bow) | 80–95 | ~full | aggressive attack — dance tune |
| Staccato | 60–75 | 1/8–1/4 | short separated strokes |
| Spiccato | 65–80 | very short | bouncing bow — reel/céilidh rhythm |
| Tremolo | 65–75 | 16th repetitions | rapid bow — tension/ornament |
| Pizzicato | 50–65 | short | plucked — bluegrass/old-time |
| Accent | 85–100 | full, strong onset | downbeat punch |
| Grace (cut) | 60–70 | tiny | cut/grace note — idiom ornament |

## Timbre DNA

- **Harmonic content**: strong fundamental + rich 2nd–5th partials, slightly
  brighter stack than concert violin (heavy bow, low bow pressure → more
  high harmonics)
- **Attack**: 10–25 ms bow contact, with rosin scratch noise — folk fiddles
  are deliberately *noisy* attacks
- **Decay**: sustained while bowed (no natural decay); short release on bow
  lift
- **Noise component**: rosin scrape at every bow change — part of the idiom
- **Vibrato**: narrow/flat (folk) vs concert violin 5–7 Hz wide — drive
  comes from bow, not vibrato
- **Character**: bright, wiry, nasal; tunes cut through a band (fiddle is
  amplified by its own aggressive bowing, not pickups)

## Role in Arrangement

- Lead melody (mid zone D4–F5) — reels, jigs, hornpipes, ballad tunes
- Ornament (grace notes, cuts, rolls, drones)
- Countermelody / call-response with flute, whistle, or second fiddle
- Accent (short rhythmic bow punches on downbeats)
- NOT harmony (line voice; only double-stops with open-string drones allowed)
- NOT bass (no low register below G3)
- NOT background pad

## Synthesis Engines (musicom)

1. **BowedString** (`sound/synthesis/bowed.py`, SP-024) — **primary**.
   Friction waveguide = the correct physical model (Helmholtz stick-slip).
   Fiddle idiom: `bow_velocity` 0.24 (higher than concert violin 0.2 —
   aggressive bow), `bow_force` 1.8 (firm contact), `bow_position` 0.15,
   `noise_level` 0.025 (rosin scratch). Use `midi_to_freq(pitch)` as `freq`;
   keep `bow_velocity` high for the folk drive character.
2. **ModalSynth** `'string'` preset — pizzicato/plucked passages; crude for
   sustained bowing.
3. **PhaseModSynth** — cheap fiddle: saw carrier, mod ratio 1.0, depth 2.5,
   attack 0.02. Twangy synthetic string, usable for bluegrass shots.

## Production

- **Reverb**: room/plate 1.4–1.8 s — dance music needs dry cut; shorter
  than concert violin (2.0). Long halls smear reel rhythms.
- **EQ**: cut 300–450 Hz body boxiness; boost ~2.5–3 kHz for bow attack +
  rosin; subtle shelf only above 7.5 kHz (fiddle projects on the mid).
- **Delay**: dotted-8th echo for ballad lines; none for dance tunes.
- **Pan**: center solo; 0.15–0.3 for twin-fiddle/ensemble spread.

## Verification

- GM110 → stem `trackXX_Fiddle.wav` (label matches, no quirk; FluidR3
  preset 110 = "Fiddle" phdr-verified)
- Zero-drift: folk melody units end flush at BAR (terminal landmark)
- Solo render only (no unison doubling — comb-filtering buzz)