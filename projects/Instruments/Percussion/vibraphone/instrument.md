---
type: instrument
family: Percussion
name: Vibraphone
midi_program: 11
gms: "Vibraphone"
range_min: 48
range_max: 89
solo_range: [53, 89]    # F3-F6 standard 3-octave; 4-octave models from C3=48
role: [lead, melody, harmony, countermelody, accent]
synthesis: [modal, phase_mod, karplus]
---

# Vibraphone

## MIDI / GM

- **Program**: 11 (GM1 Vibraphone — bank 0, preset 11). NOT in
  `structures/instrument.py` `MidiInstrument` enum (10 only) — use raw
  `program=11` in `add_voice`.
- **Channel**: any melodic channel (0-9) — a vibraphone is PITCHED; channel 9
  would trigger the drum-kit map and the program-0 fallback stem label
  `Acoustic_Grand_Piano`.
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 11 =
  "Vibraphone" (phdr-verified).
- **Pipeline stem label**: `GM_PROGRAMS[11]` = "Vibraphone" → disk stem
  `trackXX_Vibraphone.wav` — matches exactly, **no quirk** (contrast GM74
  Flute → `Recorder`, GM109 → `Bag_pipe`).

## Identity

The vibraphone (also "vibraharp", "vibes") is a **metallophone** — tuned
**aluminium alloy bars** suspended over **resonator tubes**, struck with
yarn- or cord-wrapped rubber mallets. It was developed by Herman E. Winterhoff
at Leedy (experiments from ~1916; marketed as the "vibraphone" from 1924) and
then re-made properly by J. C. Deagan's tuner Henry Schluter in 1927 with
**aluminium bars for a mellower tone, corrected bar tunings to remove the
dissonant harmonics of the steel original, and a foot-controlled damper bar**.
Schluter's design is the template for every modern instrument.

Three mechanisms define the sound:

1. **Arch-tuned bars** — material is ground away from the underside of each
   bar in a deep arch. The arch retunes the bar's modes from the raw
   free-free bar ratios (1 : 6.27 : 17.55 : 34.39) to the consonant
   **1 : 4 : 10** set (fundamental; two octaves above; an octave + major third
   above that). The same arch recipe is what makes the marimba mellow — a
   xylophone uses a shallow arch and stays bright; a glockenspiel has none.
2. **Resonator tubes** — a closed quarter-wavelength tube under each bar
   amplifies the **fundamental only** (not the upper partials), and is tuned
   slightly off-pitch to trade peak loudness for sustain.
3. **Sustain pedal + motor** — the damper pad (pedal up = notes stop, pedal
   down = notes ring for seconds) and the **motor**, which spins flat metal
   "fans" in the tube tops at **1–12 Hz** for a **tremolo** (plus a slight
   vibrato) — the instrument's namesake effect and a defining jazz colour.

It is the second most popular solo keyboard-percussion instrument in classical
music after the marimba, the defining voice of jazz vibes (Lionel Hampton,
Milt Jackson, Red Norvo, Gary Burton and the pianistic four-mallet style) and
of mid-century lounge/exotica (Arthur Lyman), and a standard orchestral /
concert-band / front-ensemble instrument (Berg's *Lulu*, Bernstein's *West
Side Story*, film and theatre scoring).

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 48–89 | C3–F6 | 4-octave models from C3 to standard top F6 |
| Sweet spot | 60–84 | C4–C6 | roundest, most singing; fullest resonator bloom |
| Solo range | 53–89 | F3–F6 | the standard 3-octave instrument |
| Low | 48–59 | C3–B3 | 4-octave model bass bars — dark, mellow, long bloom |
| Mid | 60–77 | C4–F5 | principal melodic/vocal register (ballad & jazz zone) |
| High | 78–89 | F#5–F6 | bright, metallic, shorter ring; clang + bowed glass |

The standard modern instrument is **3 octaves, F3–F6**; larger or 4-octave
models **from the C below middle C (C3)** are increasingly common (C–F or
C–C). The vibraphone is **non-transposing — written at concert pitch**. (Full
harpsichord/miniature piano-range keyboard instruments do not apply here: the
bars are physical, and the resonator tubes are cut per bar.)

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Strike (sustain) | 75–90 | full note, long ring | yarn mallet, full bar + tube |
| Hard-mallet clang | 85–105 | full note, strong attack | hard mallet — bright metallic |
| Soft-mallet ring | 55–70 | full note | mellow, no obvious attack |
| Motor (tremolo) | 70–85 | full note | fans rotating — pulsing AM |
| Roll (alternation) | 60–80 | repeated 16ths/32nds | rapid mallet alternation |
| Dead stroke | 60–75 | very short | mallet pressed on bar — choked |
| Damped / pedal up | 45–65 | very short | felt damper or hand damping — dry stop |
| Bowed bar | 50–70 | full note, NO decay | bass bow on the bar edge — glassy, higher harmonics |
| Pitch bend | 65–80 | medium | mallet slide nodal point → center, ≈ a semitone down |

Note the **inverted dynamic idiom**: a hard mallet is louder AND brighter, so
the timbre axis and the velocity axis are coupled (unlike marimba, where the
mallet is chosen mostly for tone). Composition jobs should pick the
articulation by *mallet hardness* first, velocity second.

## Timbre DNA

- **Harmonic content**: arch-tuned bar partials **1 : 4 : 10**, with the
  **fundamental strongly dominant** because the resonator tubes amplify it
  and not the upper partials. This is the crucial difference from a raw
  free-free bar (1 : 6.27 : 17.55 : 34.39, e.g. a music-box tine).
- **Attack**: 3–10 ms; mellow for a metallophone and **inversely coupled to
  decay** — the resonator tuning deliberately trades peak loudness for
  length of ring, so a well-voiced vibe sounds soft but carries.
- **Decay**: **SECONDS** — the longest of any mallet instrument. Slow, smooth
  exponential; the bars ring through chord changes unless damped.
- **Release**: controlled entirely by the player — the **sustain pedal**
  (after-pedaling and half-pedaling are standard techniques), mallet damping
  (press a ringing bar with another mallet), or hand/finger damping.
- **Vibrato / tremolo**: the MOTOR produces **amplitude** tremolo (1–12 Hz,
  ~5 Hz is the jazz default) plus a slight pitch vibrato — not hand vibrato.
- **Dynamic range**: narrow (pp–mf-ish) — the pedal and motor, not force, are
  the expressive tools; this is why four-mallet players are described as
  pianistic rather than percussive.
- **Sympathetic ringing**: because bars ring for seconds, un-damped chords
  blur; voicing must either embrace the wash or damp actively.

## Role in Arrangement

- **Lead / melody** (mid zone C4–F5) — the classic jazz-vibes solo voice; long
  singing lines with pedal sustain
- **Harmony / comping** (2–4 note four-mallet voicings, rolled or block) —
  a rhythm-section substitute for piano or guitar
- **Countermelody** against a horn or vocal lead
- **Accent / colour** (hard-mallet clangs, bowed bars, motor-on washes,
  cinematic shimmer)
- **NOT a bass voice** — no useful register below C3 and the tone is soft;
  write bass lines on a bass instrument
- **Pitched, so melodic channel** — never channel 9

## Synthesis Engines (musicom)

1. **ModalSynth** (`sound/synthesis/modal.py`) — **primary**; impulse-excited
   resonator bank. Use the custom `VIBRAPHONE_MODES` bank (vibraphone.py):
   modes at **1.0×, 4.0×, 10.0×** with amplitudes dominated by the
   fundamental (1.00 / 0.14 / 0.05) and **very low decay rates 0.30 / 0.60 /
   1.10** so the synthetic bar rings for seconds like the real one.
   `ModalSynth.render_custom(VIBRAPHONE_MODES, duration, excitation='impulse')`
   for the hard-mallet strike; `excitation='noise'` gives the soft-yarn
   mallet's softer onset. Modes are referenced to A4=440 — scale by the played
   note.
2. **Motor tremolo** — apply `MOTOR_DEFAULTS` (`rate_hz` 5.0, `depth` 0.35)
   as an amplitude-modulation envelope over the sustained render. This is the
   vibraphone's namesake effect and the single most idiomatic jazz signature;
   it is a production/effect step, not a different oscillator.
3. **MODAL_PRESET `'bell'`** — closest STOCK bank (inharmonic-ish partials,
   comparatively slow decay). Documented as an approximation only: it has
   neither the 1 : 4 : 10 tuning nor the multi-second ring.
4. **PhaseModSynth** — cheap vibraphone: sine carrier, `mod_freq_ratio` 4.0
   (the 2-octave partial), `mod_depth` 1.6 (mellow, not bell-like), attack
   0.004 s, release 1.6 s. Good enough for a pad/mock-vibes comp.
5. **Karplus-Strong** — fallback ONLY. The vibraphone is struck, not plucked;
   `loop_gain` 0.9975 (sitar-class low damping) approximates the multi-second
   ring and nothing else physical.
6. **Avoid BowedString** as the main engine (bowing is a genuine but rare
   extended technique — model it as a sustained additive/pad render, not the
   friction waveguide's bowed-string timbre).

## Production

- **Reverb**: hall/plate 1.6–2.0 s — the bars already sustain for seconds, so
  the room should be a sheen, not a smear (shorter than the timpani's 2.2 s
  hall). For jazz comping keep it tighter (~1.2–1.4 s).
- **EQ**: cut ~300 Hz for resonator-tube boom; presence boost ~4 kHz for the
  bar ping and mallet clarity; gentle 9 kHz shelf for aluminium shimmer —
  do NOT add high air, the bars produce none.
- **Dynamics**: compression is unnecessary and harmful (the narrow dynamic
  range is the instrument's character). If anything, use the MOTOR as the
  movement device instead of gain automation.
- **Pan**: center for solo; ±0.25 spread for a comping/ensemble vibes layer.

## Verification

- GM11 → stem `trackXX_Vibraphone.wav` (label matches pipeline GM_PROGRAMS[11]
  and FluidR3 preset 11 exactly — no quirk)
- Zero-drift: struck-percussion units MUST end with a terminal landmark
  `MusicEvent(0, 0, len_ticks, BAR)` or `validate()` fails
- Melodic percussion: channel 0–9 with program 11 — NOT channel 9
- ModalSynth `VIBRAPHONE_MODES`: check the LONG ring (late-window RMS still a
  real fraction of peak, well beyond the marimba preset's decay) AND that the
  4.0×/10.0× partials are present while the fundamental dominates
- Empirical FluidR3 pitch sweep (RMS): preset 11 audible across the tested
  span, no gaps — the SF2 patch never clips a composition
- Solo render only (no unison doubling — comb-filtering buzz)
