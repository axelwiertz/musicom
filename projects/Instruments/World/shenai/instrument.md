---
type: instrument
family: World
name: Shenai
midi_program: 111
gms: "Shanai"
range_min: 55
range_max: 96
solo_range: [62, 84]    # real shehnai register D4-C6; GM patch stretches 55-96
role: [lead, melody, ornament, drone, accent]
synthesis: [phase_mod, modal]
---

# Shenai

## MIDI / GM

- **Program**: 111 (GM2 Shanai — 0-indexed GM program; the 112th entry of
  the GM1 list). NOT in `structures/instrument.py` `MidiInstrument` enum
  (only 10 instruments exposed); use raw `program=111` in `add_voice`.
- **Spelling quirk**: the GM2 spec names it **"Shanai"**; the instrument is
  the North Indian **shehnai** (also "shenai"). FluidR3 preset 111 =
  "Shenai" (verified from phdr chunk).
- **Channel**: any melodic channel (0-9) — sustained double-reed instrument,
  NOT channel 9.
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 111 =
  "Shenai". TimGM6mb fallback also has a preset at 111.
- **Pipeline stem label**: `GM_PROGRAMS[111]` = **"Shanai"** → stem file
  `trackXX_Shanai.wav`. **QUIRK**: the pipeline label ("Shanai") differs from
  the instrument name ("Shenai") and from the SF2 preset ("Shenai") — the GM
  spec spelling wins in the pipeline. STEM_LABEL is set to `"Shanai"` (the
  sanitized ACTUAL pipeline label) so stem-file matching works.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 55–96 | G3–C7 | practical GM-patch span (empirical FluidR3 sweep: audible, no gaps) |
| Sweet spot | 64–79 | E4–G5 | shehnai core solo register — fullest reed presence |
| Solo (real) | 62–84 | D4–C6 | the physical shehnai's ~2-octave melodic register |
| Low | 55–61 | G3–B3 | dark, breathy low reed — soft, less carrying |
| High | 85–96 | C#6–C7 | GM extension above the physical instrument — thin, whistle-y |

The physical shehnai (North Indian double-reed conical-bore oboe with a
flared metal bell) plays roughly D4–C6 (MIDI 62–84): about two octaves of
melodic range, with G4–G5 the sweetest, most piercing register. FluidR3
preset 111 stretches chromatically across the whole GM span, so composition
jobs can step outside 62–84 without the SF2 going silent — but the
*idiomatic* shehnai line stays inside the real register: a continuous
raga-based melody over a tanpura-style Sa-Pa drone. Written above ~C6 the
patch reads as "whistle", not "shehnai".

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Sustain | 70–88 | full note | continuous blown tone — the default; circular breathing, the line never stops |
| Kan (grace) | 84–98 | 1/16–1/32 | ornamental grace flick (always above the main note) — the signature shehnai ornament |
| Meend (slide) | 68–82 | 1.5–2× | pitch glide across the register — vocal, plaintive |
| Gamak (osc.) | 80–94 | 1/4–1/3 | fast oscillating ornament around the main note |
| Tongued cut | 76–88 | 1/4–1/2 | re-articulated note (reed re-strike) — rhythmic punctuation |
| Accent | 88–100 | full note | hard reed overblow — sharp "squeak" attack, ceremonial emphasis |

## Timbre DNA

- **Harmonic content**: strong fundamental + rich even AND odd harmonics
  (double reed + conical bore) — the bright, nasal, piercing "reed wall";
  presence energy 1.5–3 kHz is extreme, comparable to bagpipe/oboe but with
  a slightly rounder body (the flared metal bell).
- **Attack**: fast reed transient ~30–80 ms — the shehnai's characteristic
  sharp, slightly squeaky onset (harder than oboe, softer than bagpipe).
- **Sustain**: indefinite with circular breathing — like the bagpipe, the
  shehnai line is a continuous tone with note changes on top; the reed never
  stops during a phrase.
- **Release**: none natural — ends when the player stops blowing (a quick,
  slightly pitch-dropping cutoff).
- **Noise component**: low-moderate — reed rasp + breath; the bell adds a
  subtle metallic shimmer.
- **Vibrato**: mostly pitch-based (meend/andolan) — slow, wide oscillating
  bends; not fast amplitude vibrato.
- **Character**: bright, piercing, ceremonial, vocal — instantly
  North-Indian classical/wedding/temple. Reads as auspicious and festive.

## Role in Arrangement

- Lead melody (real register 62–84 — raga lines: continuous, ornamented,
  often over a Sa-Pa drone)
- Ornament (kan graces, meend slides, gamak oscillations — the idiom IS the
  ornament, like bagpipe skirls)
- Drone/pedal partner (a held tonic/fifth under the line — tanpura-style;
  pair with sitar/tanpura for a full Hindustani texture)
- Accent / ceremonial statement (wedding/processional entries, festive
  moments)
- NOT harmony (monophonic — one note at a time; no chords)
- NOT a quiet background voice (constant tone, extreme presence — it cuts
  through everything; feature it or leave it out)
- NOT bass (the drone is a pedal, not a walking bass)

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — best match
   - A shehnai is a self-sustained double-reed oscillator driven by airflow
     (same family as oboe/bagpipe). Saw carrier + PM reproduces the even+odd
     harmonic reed spectrum. mod_depth 3.2 — between oboe (2.5) and bagpipe
     (4.5): the shehnai is brighter than the oboe but rounder than the
     bagpipe's scream.
   - `attack: 0.06` — a real reed transient (the shehnai's sharp squeaky
     onset), unlike bagpipe (reeds already blown, 0.03).
   - `mod_freq_ratio: 1.5` — slight inharmonic offset for the reed rasp.
2. **ModalSynth** (`sound/synthesis/modal.py`) — fallback, preset `'string'`
   - Slow-decay harmonic stack gives a crude continuous tone. No drone
     part — layer a held low note (tanpura drone) under the modal line, or
     use FluidSynth (preset 111 includes the full sample).
3. **Additive** — possible: even+odd partial stack with a strong 1.5–3 kHz
   presence region, constant amplitude envelope. Crude but workable.
4. Karplus-Strong / BowedString / DrumMachine — WRONG for a sustained reed.

## Production

- **Reverb**: temple/darbar hall 1.8–2.2 s tail — shehnai is a solo voice;
  the hall gives it the ceremonial space without smearing the ornaments.
- **EQ**: cut ~400–500 Hz (reed nasal honk); presence boost ~2.5–3 kHz (the
  reed cut — the whole point of the instrument); gentle air shelf 6–8 kHz.
- **Pan**: center for solo; slight L/R spread if doubling with sitar (never
  double the same part — unison doubling of identical pitches comb-filters).
- **Compression**: light — continuous tone sits at a steady level; only the
  reed-transient peaks need taming.

## Verification

- GM111 → stem `trackXX_Shanai.wav` — pipeline label "Shanai" QUIRK
  (GM-spec spelling; instrument name "Shenai", SF2 preset "Shenai"),
  STEM_LABEL matches the actual pipeline label.
- Solo render passes the 4–8 kHz spectral gate — the shehnai is *supposed*
  to be bright, so verify solo with no unison doubling (comb-filter buzz is
  the failure mode, not the reed's own partials).
- Zero-drift: sustained units end flush at BAR (terminal landmark).
- FluidR3 preset 111 audible across the full span (empirical RMS sweep, no
  gaps — the SF2 never clips a composition).

## Instrument.md companion

`shenai.py` — importable constants. Registered in
`instrument_registry.py` (2026-09-10) as `World.shenai.shenai` → key
`shenai`, constant `SHENAI`.
