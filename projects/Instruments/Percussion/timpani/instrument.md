---
type: instrument
family: Percussion
name: Timpani
midi_program: 47
gms: "Timpani"
range_min: 36
range_max: 65
solo_range: [38, 57]    # C2-F4 playable, standard four-drum set D2-A3
role: [accent, rhythm, bass, drone]
synthesis: [modal, drum606, additive]
---

# Timpani

## MIDI / GM

- **Program**: 47 (GM1 Timpani — bank 0, preset 47)
- **Channel**: any melodic channel (0-9) — a timpano is PITCHED, NOT channel 9
  (ch9 would trigger the drum-kit map and the program-0 fallback stem label
  `Acoustic_Grand_Piano`)
- **FluidSynth**: FluidR3_GM.sf2 renders GM47 → "Timpani" (preset name matches
  exactly, verified from the phdr chunk)
- **Pipeline stem label**: `GM_PROGRAMS[47]` = "Timpani" → `trackXX_Timpani.wav`
  (no quirk)

## Identity

The timpani (kettledrums, "timps") are hemispherical vessel drums: a membrane
head stretched over a large copper bowl, struck with felt-headed timpani
sticks and tuned to definite pitches by a foot pedal (pedal timpani are the
modern standard). They are the only standard orchestral drum that carries
written pitch and bass-clef notation, and the only percussion instrument with
a continuous-roll technique used as a genuine melodic/pedal voice (Haydn's
"Drumroll" Symphony No. 103 opens with an unaccompanied timpani roll).

Sizes run from ~84 cm bowls down to *piccoli timpani* of 30 cm or less; each
drum covers about a perfect fifth (7 semitones), which is why a set is tuned
per piece and why a player re-tunes between movements. The standard console is
four drums (≈81/74/66/58 cm) spanning roughly **D2–A3**; a 32-inch drum reaches
**C2**, and piccolo timpani plus extended techniques reach up to about **C4**
(Stravinsky writes B3 for a piccolo timpano in *The Rite of Spring*; Milhaud
requires F#4=66 in *La création du monde*).

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 36–65 | C2–F4 | 32-inch low drum to piccolo-timpano ceiling |
| Sweet spot | 41–55 | F2–G3 | fullest tone, clearest pitch, best roll projection |
| Solo range | 38–57 | D2–A3 | the standard four-drum set (majority of the repertoire) |
| Low | 36–47 | C2–B2 | 32/29-inch booms — deep, slow roll rumble |
| Mid | 48–57 | C3–A3 | 26/23-inch drums — classic tuning/roll/melodic zone |
| High | 58–65 | B3–F4 | piccolo timpano — thin, hollow, dry; accents/effects |

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Stroke (sustain) | 75–92 | full note, long natural ring | felt mallet, full head |
| Roll (tremolo) | 60–80 | repeated 16th/32nd, continuous | two-stick roll, sustained roar |
| Muffled / damped | 55–70 | very short | hand pads on head, dead |
| Accent / marcato | 90–110 | full note, hard attack | hard stroke, sforzando |
| Soft stroke / pp roll | 40–60 | full note | beguiling, distant |
| Edge stroke | 65–80 | medium | struck near rim — thin, hollow (Bartók/Bernstein) |
| Center stroke | 70–90 | short | near-toneless thud (Gershwin, *An American in Paris*) |
| Double stop | 85–100 | full note | two drums struck together (Beethoven 9, Brahms) |
| Con sordino / coperti | 50–70 | full note | muted/covered head — dark, muffled |

## Timbre DNA

- **Harmonic content**: INHARMONIC. An ideal circular membrane's partials sit
  at the Bessel-zero ratios **1 : 1.594 : 2.136 : 2.296 : 2.653**; bowl
  stiffness and air loading pull a real timpano toward roughly
  **1 : 1.5 : 2.1 : 2.3 : 2.65**. That inharmonic-but-regular set is what makes
  a timpano read as "definite pitch with a hollow roar" rather than a tone
  (contrast marimba's odd-harmonic bars or a string's true harmonic series).
- **Attack**: 1–5 ms (felt mallet on head) — soft relative to a snare, with a
  head-slap noise component that scales with mallet hardness (wood sticks =
  bright clack, sponge/felt = round).
- **Decay**: SLOW — the longest of the drum family. Low drums ring 2–4 s+;
  rolls are the only way to hold a sustained note (multiple-bounce rolls are
  avoided; timpanists use controlled single strokes).
- **Release**: natural decay; players must MUFFLE by hand because the head
  rings far past the written note value.
- **Vibrato**: none native. Pitch bends come from pedal glissandi (an
  extended technique), not from hand vibrato.
- **Sympathetic resonance**: undamped drums ring along with the ensemble —
  the instrument's free "reverb", exploited in Carter's *Eight Pieces*.

## Role in Arrangement

- Accent / punctuation (the orchestra's punctuation section — hits, sforzandi)
- Rhythm (the pedal-point pulse under tutti passages; the roll as a
  sustained low layer)
- Bass support (doubles brass/string bass roots an octave below the melody;
  the tuned low C2–G2 anchoring zone)
- Drone / pedal (continuous roll on the tonic or dominant — Haydn, Wagner,
  film-score tension builds)
- NOT a melody voice at speed (single tuned drums; fast lines only as
  extended technique or with several timpanists)
- NOT a harmony voice (double stops are two drums max; fully voiced chords
  need multiple players — Berlioz's Requiem uses ten)

## Synthesis Engines (musicom)

1. **ModalSynth** (`sound/synthesis/modal.py`) — best match; impulse-excited
   resonator bank. Use the custom `TIMPANI_MODES` bank (see timpani.py):
   modes at 1.0×, 1.59×, 2.14×, 2.30×, 2.65× with LOW decay rates (0.9–3.0,
   vs marimba's 8–20) so the synthetic drum rings long like the real one.
   `ModalSynth.render_custom(TIMPANI_MODES, duration, excitation='impulse')`;
   the felt mallet is closer to `excitation='noise'` (soft head slap).
   Mode frequencies are referenced to A4=440 — scale them by the played note.
2. **DrumSynth606** (`sound/synthesis/drum_synth_606.py`) — `DrumSynth606.tom(
   freq, decay, pitch_sweep)` gives the pitch-swept-sine thump of the strike
   transient (see `DRUM606_DEFAULTS`: decay 0.9, sweep 1.35). Cheap, and
   correct for the first 100 ms.
3. **Additive** — decaying inharmonic stack (fundamental + the membrane
   partial set), fast attack, long release; second-best tonal path.
4. **Stock ModalSynth preset `'drum'`** — the closest stock bank, but its
   decays (15–35) are far too fast for a timpano; use for a "damped/covered"
   character only.
5. **Avoid** BowedString (no bow) and Karplus-Strong (there is no string —
   the KS loop's harmonic series is the wrong partial structure).

## Production

- **Reverb**: hall 2.0–2.5 s tail — the longest in the instrument set (marimba
  1.0 s / steel drums 1.4 s). The timpani's bloom IS the room; do not choke it.
- **EQ**: cut 150–250 Hz to tame copper-bowl boom (keep 40–80 Hz for the
  low-drum weight); presence boost ~3 kHz for the mallet attack; gentle 6–7 kHz
  shelf for hall air on the head noise.
- **Pan**: center for a single drum; spread −0.3..+0.3 across a four-drum arc
  (low drum left in the American setup).
- **Compression**: minimal (the dynamic range from pp roll to ff hit is the
  point). If needed, 1.5:1 with a slow attack to preserve the transient.

## Verification

- GM47 renders as `trackXX_Timpani.wav` in RenderPipeline stems (label matches
  exactly, no quirk — see registry quirks table)
- ModalSynth `TIMPANI_MODES`: check long ring (1.0–1.5 s tail still above ~5%
  of peak) AND an inharmonic partial near 1.59× f0 — the contrast check against
  the marimba preset's fast odd-harmonic decay
- Melodic percussion: channel 0–9 with program 47 — NOT channel 9 (ch9 maps to
  the drum kit and mislabels the stem "Acoustic_Grand_Piano")
- Empirical FluidR3 pitch sweep (RMS, notes 24–84): preset 47 audible across
  the whole span, no gaps — SF2 never clips a composition
- Zero-drift: percussion units MUST end with a terminal landmark
  `MusicEvent(0, 0, len_ticks, BAR)` or `validate()` fails
