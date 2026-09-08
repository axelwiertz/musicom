---
type: instrument
family: Woodwind
name: Bagpipe
midi_program: 109
gms: "Bagpipe"
range_min: 53
range_max: 96
solo_range: [57, 69]    # real GHB chanter = A3-A4; GM patch stretches 53-96
role: [lead, melody, ornament, drone, accent]
synthesis: [phase_mod, modal]
---

# Bagpipe

## MIDI / GM

- **Program**: 109 (GM2 Bagpipe — 0-indexed GM program; the 110th entry of
  the GM1 list). NOT in `structures/instrument.py` `MidiInstrument` enum
  (only 10 instruments exposed); use raw `program=109` in `add_voice`.
- **Channel**: any melodic channel (0-9) — sustained reed instrument, NOT
  channel 9.
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 109 =
  "BagPipe" (verified from phdr chunk). TimGM6mb fallback also has a preset
  at 109.
- **Pipeline stem label**: `GM_PROGRAMS[109]` = **"Bag pipe"** (with a
  space!) → stem file `trackXX_Bag_pipe.wav`. **QUIRK**: the pipeline label
  is two words ("Bag pipe"), while GM_NAME/SF2 say "Bagpipe"/"BagPipe".
  STEM_LABEL is set to `"Bag_pipe"` (the sanitized ACTUAL pipeline label) so
  stem-file matching works. This is the first World/ethnic-adjacent program
  where the pipeline label differs from the instrument name.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 53–96 | F3–C7 | practical GM-patch span (empirical FluidR3 sweep: audible, no gaps) |
| Sweet spot | 62–74 | D4–D5 | chanter core (D4=62 is the modal center) + a 5th of writing-room |
| Chanter (real) | 57–69 | A3–A4 | the physical Great Highland chanter — 9 notes only |
| Drone | 53–56 | F3–Bb3 | below chanter bottom — pedal/growl effect, NOT melody |
| High | 70–96 | B4–C7 | GM extension above the physical chanter — whistle-y, less idiomatic |

The real Great Highland Bagpipe chanter is the most range-limited melodic
instrument in the library: **9 notes, A3–A4 (MIDI 57–69), mixolydian on D**
(A B C# D E F# G A — no C natural, no F natural). FluidR3 preset 109
stretches chromatically across the whole GM span, so composition jobs can
step outside 57–69 without the SF2 going silent — but the *idiomatic* bagpipe
line is a modal melody inside the 9-note chanter, over a D/A drone. Anything
written above the chanter reads as "whistle", not "bagpipe".

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Sustain | 68–85 | full note | steady blown tone — the default; the chanter never stops, tune = note changes |
| Skirl | 88–100 | 1/8–1/4 | gracenote-doubling attack — the GHB signature "scream", piercing |
| Gracenote | 82–96 | 1/16–1/32 | single-lead gracenote flick (G-D-E throws) — always higher than the main note |
| Crisp | 74–86 | 1/2–full | clean articulated note change (tongued cut) |
| Accent | 88–98 | full note | hard blow / top-hand emphasis on a long note |

## Timbre DNA

- **Harmonic content**: very strong fundamental + rich even AND odd
  harmonics (double reed + conical-ish bore) — the piercing "reed wall" of
  the GHB; presence energy 2–4 kHz is extreme (louder than oboe).
- **Attack**: the reeds are ALREADY blown by the bag — there is no breath
  transient. Note changes are instantaneous cuts + gracenotes. The only
  "attack" envelope is the initial bag-pressure swell (~30–80 ms) when the
  drone starts.
- **Sustain**: indefinite — bagpipes have no rests; the melody is a
  continuous tone with note changes on top. The drone (A2, 110 Hz) never
  stops while the bag has pressure.
- **Release**: none natural — the sound ends only when the bag is emptied
  (a quick, slightly pitch-dropping cutoff) or the piper stops the chanter
  in the armpit.
- **Noise component**: very low — no breath hiss (air comes from the bag);
  the chanter reed has a steady rasp. Grace notes add a percussive "chiff".
- **Vibrato**: NONE — bagpipe tone is steady and unvibratoed; expressive
  variation comes from gracenote ornamentation and slight pressure changes.
- **Character**: constant, piercing, reedy, triumphant/martial — reads
  instantly as Scottish/folk.

## Role in Arrangement

- Lead melody (chanter register 57–69 — modal lines: mixolydian, pentatonic,
  Highland pipe tunes)
- Ornament (skirls, gracenote throws, doublings — the idiom IS the ornament)
- Drone/pedal (a held A2/D2-style root under folk textures; the bagpipe's
  own drone is implied — a real drone part is idiomatic, use low strings or
  a held bass)
- Accent / fanfare / march statements (triumphal entries, key changes of
  mood in folk/rock arrangements)
- NOT harmony (the chanter is monophonic — one note at a time; no chords)
- NOT a quiet background voice (constant tone, extreme presence — it cuts
  through everything; feature it or leave it out)
- NOT bass (the drone is a pedal, not a walking bass)

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — best match
   - A reed is a self-sustained oscillator driven by airflow. Saw carrier +
     PM (even+odd harmonics) reproduces the chanter's reed spectrum — the
     same family as the oboe/sax patches but with the HIGHEST mod_depth of
     the woodwind set (4.5 vs oboe 2.5 / sax 2.8) for the bagpipe's
     piercing presence.
   - `attack: 0.03` — NOT a 50–80 ms reed onset: the reeds are already
     blown; the only swell is bag pressure.
   - `freq = midi_to_freq(pitch)`; release 0.15 s.
2. **ModalSynth** (`sound/synthesis/modal.py`) — fallback, preset `'string'`
   - Slow-decay harmonic stack gives a crude continuous tone. No drone
     part — a composition needing the true chanter+drone sound should
     layer a held low note (drone) under the modal line, or use FluidSynth
     (preset 109 includes the drone in the sample).
3. **Additive** — possible: odd+even partial stack with a strong 2–4 kHz
   presence region, constant amplitude envelope. Crude but workable.
4. Karplus-Strong / BowedString / DrumMachine — WRONG for a sustained reed.

## Production

- **Reverb**: big hall or outdoor space, 2.0–3.0 s tail — the GHB lives
  outdoors; a long tail also smooths the chanter/drone beat roughness.
- **EQ**: cut ~400–500 Hz (chanter nasal honk); presence boost ~2.5 kHz
  (the reed scream — the whole point of the instrument); gentle air shelf
  6–8 kHz.
- **Pan**: center for solo; in a pipe band, spread individual pipes
  L/R for width (never double the same part — unison doubling of identical
  pitches comb-filters).
- **Compression**: light — the bagpipe's constant tone already sits at a
  steady level; the gracenote transients are the only peaks.

## Verification

- GM109 → stem `trackXX_Bag_pipe.wav` — pipeline label "Bag pipe" QUIRK
  (space), STEM_LABEL matches the actual label; FluidR3 preset 109 =
  "BagPipe".
- Solo render passes the 4–8 kHz spectral gate — the bagpipe is *supposed*
  to be bright, so verify solo with no unison doubling (comb-filter buzz is
  the failure mode, not the reed's own partials).
- Zero-drift: sustained units end flush at BAR (terminal landmark).
- FluidR3 preset 109 audible across the full span (empirical RMS sweep, no
  gaps — the SF2 never clips a composition).

## Instrument.md companion

`bagpipe.py` — importable constants. Registered in
`instrument_registry.py` (2026-09-08) as `Woodwind.bagpipe.bagpipe` → key
`bagpipe`, constant `BAGPIPE`.
