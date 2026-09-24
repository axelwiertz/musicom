---
type: instrument
family: Keys
name: Accordion
midi_program: 21
gms: "Accordion"
range_min: 36
range_max: 96
solo_range: [53, 89]
role: [harmony, melody, bass, rhythm, ornament]
synthesis: [phase_mod, additive, modal]
---

# Accordion

## MIDI / GM

- **Program**: 21 (GM1 Accordion)
- **Channel**: melodic channel (0-9). Full polyphony — the accordion plays
  melody (right hand), chords (right hand), and bass+chord accompaniment
  (left hand) simultaneously. NOT channel 9.
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 21 =
  "Accordian" (cosmetic archaic spelling — SF2 labels "Accordian", NOT
  "Accordion"; no routing impact). TimGM6mb fallback also has
  preset 21 = "Accordion". RenderPipeline stem label: GM_PROGRAMS[21] =
  "Accordion" → `trackXX_Accordion.wav` — matches exactly, **no quirk**.
- **GM1 identity**: program 21 is the standard piano accordion (right-hand
  piano keyboard + left-hand Stradella bass/chord system), NOT the button
  accordion (chromatic or diatonic) or bandoneon.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 36–96 | C2–C7 | combined treble+bass of a 4/5 full-size accordion |
| Bass (left hand) | 36–52 | C2–E3 | Stradella fundamental + counter bass rows; C2=36 is the lowest 8' bass reed |
| Low treble | 53–59 | F3–B3 | bottom of the right-hand keyboard — dark, full, mellow |
| Middle treble | 60–76 | C4–E5 | primary melodic register — richest, most expressive |
| High treble | 77–89 | F5–F6 | bright, cutting — piccolo and violin register switches |
| Extended high | 90–96 | G6–C7 | top keys on extended-range instruments — thin, piercing |

The standard piano accordion right-hand keyboard spans F3 (53) to A6 (93).
Full-size instruments (41 keys, 120 basses) cover the full range. Some
models extend to C7 (96). The left-hand Stradella system provides single
bass notes (C2–C4, 36–60) plus pre-set major/minor/7th/dim chords across
the entire circle of fifths.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Sustain | 68–85 | full note | steady blown tone — default; bellows pressure held constant |
| Staccato | 72–86 | 1/8–1/4 | short bellows pulse, crisp release |
| Bellows shake | 78–92 | 1/4–1/2 | rapid bellows vibrato (amplitude modulation) — expressive, vocal |
| Marcato | 82–95 | 3/4–full | hard bellows accent, strong attack |
| Legato | 60–72 | full note | smooth connected notes, minimal bellows change |
| Sforzando | 88–100 | 1/2–full | sudden forceful bellows push, then ease |

Bellows control IS the primary expressive mechanism — unlike a piano where
velocity determines loudness, the accordionist controls dynamics via
bellows pressure *during* the note. MIDI velocity maps to the initial
attack force, but the sustain level is constant (set by bellows).
For realistic expression, use CC7 (volume) or CC11 (expression) to
simulate bellows pressure changes over a phrase.

## Timbre DNA

- **Harmonic content**: rich even+odd harmonic spectrum (free reed =
  symmetric oscillating tongue = both even and odd partials). Multiple reed
  ranks (2-4 per note) produce a thick, chorused tone with slight
  detuning between ranks — the musette (wet) tuning is the classic French
  cafe sound; dry tuning is cleaner, closer to a harmonium.
- **Attack**: 5–15 ms (reed speaks instantly on airflow) — no breath
  transient. The bellows attack gives a subtle pressure swell ~20-40 ms.
- **Sustain**: indefinite — as long as bellows have air (15-30 seconds
  typical, depending on dynamic level). Constant tone under steady
  bellows pressure.
- **Release**: instant — reeds stop as soon as airflow stops. No natural
  decay tail; the bellows must be actively reversed to continue sound.
- **Noise component**: very low — clean reed tone, some mechanical key
  click on fast passages. Bellows have a faint air whoosh at high
  pressure.
- **Vibrato**: available via bellows shake (amplitude modulation) or
  musette tuning (beating between slightly detuned reeds = inherent
  tremolo). Not a pitch vibrato.
- **Character**: warm, reedy, full-bodied, slightly nasal — instantly
  evokes folk, cafe, tango, and musette.

## Role in Arrangement

- Harmony (chordal comping — right hand plays 2-4 note chords, left hand
  provides bass+chord accompaniment; the accordion IS a one-person band)
- Melody (right hand single-note lines — folk tunes, tango melodies,
  classical cantabile)
- Bass (left hand Stradella system provides walking bass lines + chord
  buttons; free bass extends the melodic range of the left hand)
- Rhythm (bellows-pulse chords — oom-pah, habanera, tango, polka patterns)
- Ornament (rapid trills, mordents, glissandi — bellows accents add punch)
- Pad (sustained chordal passages with held bellows pressure — less common
  but effective in folk-instrumental arrangements)
- NOT a quiet background pad (constant tone, cuts through a mix — the
  accordion has a strong midrange presence; feature it or support it
  with space in the arrangement)

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — **primary**
   - A free reed is a self-sustained oscillator: a saw carrier (even+odd
     harmonics) with phase modulation reproduces the reed's characteristic
     buzzy richness. Mod_depth 3.2 sits between oboe (2.5) and bagpipe
     (4.5), reflecting the accordion's moderate reed buzz.
   - `attack: 0.015` — very fast reed onset; the real bellows attack is
     slightly slower but the reed speaks instantly once air flows.
   - Multiple layered PhaseModSynth voices at slight pitch offsets (±2-5
     cents) simulate the multi-rank musette/chorus effect.
   - `release: 0.05` — the reed stops nearly instantly on bellows reversal.
2. **Additive** (`sound/synthesis/additive.py`) — alternative
   - A harmonic stack with strong even partials (free reed symmetry) and
     a slight amplitude wobble (LFO at ~5-7 Hz) for the musette effect.
     Multiple detuned partial sets replicate the 2-4 rank register.
3. **ModalSynth** (`sound/synthesis/modal.py`) — fallback
   - Preset `'string'` gives a generic sustained tone. Works in a pinch
     but loses the reedy buzz and multi-rank thickness.
4. Karplus-Strong / BowedString / DrumMachine — WRONG for a reed
   instrument. The accordion is not plucked or bowed.

### Multi-rank simulation

A realistic accordion sound benefits from layering 2-3 slightly detuned
voices (the "musette" chorus effect). In PhaseModSynth, this means:
- Voice 1: base pitch +0 cents, mod_depth 3.2
- Voice 2: base pitch +3 cents, mod_depth 2.8 (medium reed rank)
- Voice 3: base pitch -2 cents, mod_depth 2.5 (soft reed rank)
Mix dry, 60% / 30% / 10% for a standard accordion register.

## Production

- **Reverb**: room/hall 1.0–1.6 s — the accordion is a dry, close-mic'd
  instrument; too much reverb washes out the reed detail. A small room
  ambience keeps the folk/cafe intimacy.
- **EQ**: cut 250–350 Hz (bellows body resonance / boxiness); presence
  boost 2.0–3.0 kHz for reed clarity and cut; gentle air shelf 7–9 kHz
  for key-click sparkle (not breath — there's no breath noise).
- **Pan**: center for solo; ±0.15–0.25 spread for left-hand (bass) vs
  right-hand (treble) in a stereo accordion recording. In an ensemble,
  pan the accordion slightly off-center to leave room for the lead.
- **Compression**: moderate — the bellows naturally control dynamics, but
  a 3:1 ratio with slow attack smooths out bellows transients in a dense
  mix.

## Verification

- GM21 → stem `trackXX_Accordion.wav` — pipeline label "Accordion",
  matches exactly, **no quirk**.
- FluidR3 preset 21 = "Accordion" (verified from phdr chunk).
- Solo render must pass the 4–8 kHz spectral gate — accordion is naturally
  bright in the upper register (piccolo reed rank); verify solo with no
  unison doubling.
- Zero-drift: sustained/chord units end flush at BAR (terminal landmark).
- FluidR3 preset 21 audible across the full span (empirical RMS sweep, no
  gaps — the SF2 never clips a composition).
- Multi-rank musette effect: if using layered PhaseModSynth, keep the
  pitch detuning within ±5 cents to avoid audible beating (the musette
  beat rate is ~5-7 Hz).
