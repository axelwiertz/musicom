---
type: instrument
family: Percussion
name: Steel Drums
midi_program: 114
gms: "Steel Drums"
range_min: 55
range_max: 96
solo_range: [62, 88]    # G3-C7 playable, solo sweet spot D4-E6 (lead pan)
role: [lead, melody, accent, countermelody, harmony]
synthesis: [modal, karplus, additive]
---

# Steel Drums

## MIDI / GM

- **Program**: 114 (GM1 Steel Drums — bank 0, preset 114)
- **Channel**: any melodic channel (0-9) — melodic percussion, NOT channel 9
- **FluidSynth**: FluidR3_GM.sf2 renders GM114 → "Steel Drums" (preset name
  matches exactly, verified from phdr chunk)
- **Pipeline stem label**: `GM_PROGRAMS[114]` = "Steel Drums" →
  `trackXX_Steel_Drums.wav` (no quirk)

## Identity

GM114 "Steel Drums" is the **Trinidadian steelpan (pan)** family — the only
chromatic idiophone family born in the 20th century (Trinidad & Tobago,
1930s-40s, from repurposed 55-gallon oil drums). The instrument is a shallow
concave bowl hammered into the drum lid, with individual note "islands"
pounded into the dome. Members (high→low): lead/tenor pan ("ping pong",
soprano), double tenor, double second, guitar pan, cello pan, six-bass. The
GM patch is the bright lead/tenor character — melodic, NOT a bass voice
(bass pans are a separate sub-family with their own register and the patch
does not cover them).

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 55–96 | G3–C7 | lead-pan practical register (some extend to E7=100) |
| Sweet spot | 65–86 | F4–D6 | brightest, roundest tone, best projection |
| Low | 55–64 | G3–E4 | dark, warm, calypso bass-note/strum zone |
| Mid | 65–76 | F4–E5 | bright round melody zone — lead pan core |
| High | 77–96 | F5–C7 | pingy, cutting, fast decay (double-tenor top) |

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Strike (sustain) | 70–90 | full note | rubber-mallet strike, bowl ring, natural decay |
| Roll (tremolo) | 60–75 | 16th/32nd repeats | rapid alternating mallets, sustained illusion |
| Staccato | 60–70 | 1/8–1/16 note | short, dry, separated islands |
| Accent/marcato | 90–105 | full note, strong attack | hard mallet emphasis |
| Muted (choked) | 40–55 | very short | hand on island, damped |
| Glissando/sweep | — | sweep across notes | fast chromatic/scale sweep (idiomatic) |

## Timbre DNA

- **Harmonic content**: fundamental + slightly INHARMONIC partials — the
  classic pan overtone set ~2.0×, ~2.7×, ~3.6× the fundamental (the 2.7×
  "pan fifth" is the signature). Attack transient carries a metallic shimmer.
- **Attack**: 1–5 ms (mallet strike) — percussive, softer than xylophone,
  brighter than marimba
- **Decay**: exponential, 0.5–2.0 s — low notes ring longer, high notes dry fast
- **Release**: natural decay (no sustain control); note end = bowl stops ringing
- **Noise component**: mallet click / attack transient (rubber vs. hard mallet)
- **Vibrato**: NONE native — sustained notes are rolled tremolo, not pitch

## Role in Arrangement

- Lead melody (F4–D6 sweet spot — calypso/soca melody lines, pan ensembles)
- Accent/ornament (high-register runs, fills, glissandi)
- Countermelody (interlocking pan lines, pan-orchestra section writing)
- Harmony (pans play 2–4 note chords — idiomatic strums and rolled chords)
- Rhythm (chank/strum patterns in calypso; pans double the rhythm section)
- NOT bass (bass pans are a separate low sub-family; GM114 patch is bright)
- NOT a pad (no sustain; rolls substitute but stay rhythmic)

## Synthesis Engines (musicom)

1. **ModalSynth** (`sound/synthesis/modal.py`) — best match, impulse-excited
   resonator bank:
   - `ModalSynth.render_preset('marimba', duration, excitation='impulse')` —
     closest stock preset (odd-harmonic struck-bar bank, fast decays 8–20)
   - `ModalSynth.render_preset('bell', ...)` — metallic-pan alternative
     (inharmonic partials, slower decay)
   - **Exact-pan custom**: `render_custom(PAN_MODES, ...)` with struck-membrane
     modes f0, 2.0×, 2.7×, 3.6× at decays 12–28 (see `PAN_MODES` in
     steel_drums.py) — pitch-shift mode frequencies by the played note
   - Fast exponential decay is inherent (no ADSR needed)
2. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
   fallback: plucked-waveguide loop with loop_gain 0.9950 approximates the
   metallic ping; a pan is struck, not plucked, so this is second choice
3. **PhaseModSynth** — cheap synth-pan patch (sine carrier, mod ratio 2.7);
   FM is for reed/brass/synth timbres, not struck metal
4. **Avoid** BowedString (no sustain, no bow)

## Production

- **Reverb**: room/plate 1.2–1.6 s tail (intimate but with space; too much
  hall muddies the attack — contrast with marimba's 1.0 s)
- **EQ**: cut 400–600 Hz bowl boxiness; presence boost 3–4 kHz for the ping
  and mallet clarity; air shelf 8–10 kHz subtle (pans are already bright)
- **Pan**: center (solo); slight L/R spread for pan ensembles/ostinati
- **Compression**: light 2:1 — keep the transient, tame the decay tail

## Verification

- GM114 renders as `trackXX_Steel_Drums.wav` in RenderPipeline stems (label
  matches exactly, no quirk — see registry quirks table)
- ModalSynth pan modes: check strong fundamental + fast exponential decay,
  no sustain plateau
- Melodic percussion: channel 0-9 with program 114 — NOT channel 9 (ch9 would
  trigger the program-0 fallback label "Acoustic_Grand_Piano")
- Empirical FluidR3 pitch sweep (RMS, notes 24–96): preset 114 audible across
  the whole span, no gaps — SF2 never clips a composition
