---
type: instrument
family: Synth
name: Calliope
midi_program: 82
gms: "Lead 3 (calliope)"
range_min: 60
range_max: 96
solo_range: [67, 89]
role: [lead, melody, ornament, accent, countermelody]
synthesis: [phase_mod, additive, air_pipe]
---

# Calliope (GM82 — Lead 3)

## MIDI / GM

- **Program**: 82 (GM1 "Lead 3 (calliope)"). The GM Lead-family patch modelled
  on the **steam calliope** ("steam piano"): a bank of steam-driven organ
  pipes / brass whistles played from a keyboard — the sound of circus,
  carnival, fairground and Mississippi riverboat (the *Robert E. Lee*,
  *Delta Queen* calliopes; the calliope solo in "Entrance of the Gladiators"
  fairground tradition; Nino Rota carnival cues).
- **Enum note**: `structures/instrument.py` `MidiInstrument` exposes only 10
  instruments and has NO calliope constant — use the raw GM number 82; the
  registry is the full KB.
- **Channel**: melodic channel (0–9). Channel 9 with program 82 would trigger
  the drum-kit map and the ch9 program-0 fallback label
  `Acoustic_Grand_Piano` (ch9 quirk — see timpani lesson).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 82 =
  **"Calliope Lead"** (verified from phdr). RenderPipeline stem label:
  GM_PROGRAMS[82] = "Lead 3 (calliope)" → sanitized `trackXX_Lead_3_calliope.wav`
  (spaces → `_`, parens stripped) — STEM_LABEL `Lead_3_calliope` matches the
  pipeline's real sanitization, **no routing quirk**. The SF2 preset's
  internal name "Calliope Lead" differs from the GM label cosmetically only.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 60–96 | C4–C7 | idiomatic writing band (real steam rack ~3 octaves) |
| Low | 60–71 | C4–B4 | pipe bottom — warm round, chunky |
| Mid | 72–83 | C5–B5 | PRIMARY melody register — carnival tunes |
| High | 84–96 | C6–C7 | bright top — whistle-y, cutting |

Empirical FluidR3 pitch sweep (RMS, velocity 90, notes 24–108 step 6): preset
82 audible **15/15 notes, no gaps** (RMS 670–2125 across the whole span;
bottom C1 loudest at 2125, treble rolls off gently to 670 at C8) —
full-keyboard patch, no ceiling — SF2 never clips a composition. Range 60–96
is the idiomatic *writing* band (the real calliope rack), NOT a physical limit.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Pipe (sustain) | 65–82 | full | held steam pipe — THE default gesture |
| Chiff | 65–78 | 0.3× | short pipe bursts — rhythmic carnival blips |
| Marcato | 80–90 | 0.85× | hard valve onset — accented entrance |
| Trill | 75–85 | 0.25× | fast repeated pipes — the fairground ornament |
| Swell | 55–70 | 1.2× | pressure swell — steam builds, the note blooms |
| Accent | 84–95 | 0.9× | downbeat hit — the calliope "yell" |

## Timbre DNA

- **Harmonic content**: near-sine pipe fundamentals with a mild harmonic
  stack (measured FluidR3 solo: spectral centroid C6 ≈ 2230 Hz — mellow for
  a lead; the chiff/steam noise rides 3–5 kHz at low level). The pipe is
  closer to a pure tone than any reed or brass patch — the tone is the
  fundamental, the character is the chiff
- **Attack**: 10–30 ms — fast valve opening; steam pressure is already up,
  the note starts with the key (no breath transient, no reed squeak)
- **Decay/sustain**: indefinite while held (pressure-driven); release 0.1 s
  — the valve closes, the pipe cuts
- **Vibrato**: none built-in (steam pressure is constant) — MIDI pitch-bend
  is the only idiomatic wobble
- **Character**: bright-but-mellow, slightly breathy, nostalgic-carnival;
  instantly "circus/fairground" — the happiest patch in the GM set

## Role in Arrangement

- **Lead** — carnival/circus cue melodies: the oom-pah tune, the fairground
  theme (the "Entrance of the Gladiators" register)
- **Melody** — retro/fantasy top lines; the "toy town" melodic voice
- **Ornament** — trills and chiff blips are the idiom (the calliope player's
  showmanship)
- **Accent** — downbeat pipe stabs, whistle-y punctuations
- **Countermelody** — second pipe voice under a lead, thirds/sixths apart
- **NOT** a bass voice (use the bass family); NOT a pad (pipes are rhythmic
  and per-key; the slow-attack pad role is synth_pad GM88); light 2–3 note
  pipe chords are OK (calliopes are played two-handed) but dense harmony
  smears — keep chords short and in the mid register
- Polyphonic: line + light harmony fully idiomatic; unison doubling with
  another melodic patch on the same pitches is NOT (comb-filter rule)

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — **primary**. The pipe
   recipe: sine carrier + sine modulator at the fundamental (ratio 1.0,
   depth **1.8** — between flute 1.5 and shakuhachi 2.0: a pipe is brighter
   than a flute, mellower than the reed voices 2.2–4.5), attack 0.02 s (the
   valve), release 0.12 s (the cutoff), sustain 0.9 (FM_DEFAULTS).
2. **Additive** (`sound/synthesis/additive.py`) — mellow harmonic pipe stack
   (weights [1.0, 0.55, 0.30, 0.18, 0.10, 0.05] — strong fundamental, gentle
   rolloff, no reed brightness; the organ-pipe precedent)
   (ADDITIVE_DEFAULTS).
3. **AirPipe** (`sound/synthesis/air_pipe.py`, AirPipe) — physical model,
   tertiary. A pressure-driven flue pipe IS the calliope physics (steam
   pressure = the air supply): open pipe (`stopped=False`), pressure 0.6
   (below the 0.75 overblow threshold so the pipe stays on the fundamental),
   length_scale 1.0 (AIRPIPE_DEFAULTS).

## Production

- **Reverb**: hall/plate 1.8–2.4 s — REVERB_TAIL 2.0 s; fairground space,
  shorter than the pad family (3.2 s) because calliope phrases are rhythmic
  and the pipes carry their own steam
- **EQ**: cut ~400 Hz (pipe-stack low-mid boxiness); boost ~3 kHz presence
  (the whistle/chiff clarity band); gentle 9 kHz air shelf (steam shimmer)
- **Pan**: center for the composed stem; ±0.3 L/R spread on wide pipe-rack
  choruses
- **Layering**: idiomatic doubling is octaves or thirds (calliope + same
  patch 8va = the full pipe rack), NEVER unison with another melodic patch
  on the same pitches (2026-09-01 comb-filter rule). + a tuba/bass oom-pah
  an octave+ below + snare = the complete circus band

## Verification

- GM82 → stem `trackXX_Lead_3_calliope.wav` (GM_PROGRAMS[82] = "Lead 3
  (calliope)" sanitized; FluidR3 preset 82 = "Calliope Lead" — internal SF2
  name differs cosmetically, **no routing quirk**)
- `by_name('calliope')` → Calliope, `by_program(82)` → Calliope (distinct
  from 88 pad / 62 brass / 54 voice / 80–81 lead-1/lead-2 family members),
  `in_sweet_spot(72)` = True, `in_sweet_spot(48)` = False
- Empirical pitch sweep: preset 82 audible 15/15 notes (24–108, step 6), no
  gaps (RMS 670–2125, mellow centroid ~2230 Hz at C6)
- Buzz check: solo render passes the 4–8 kHz spectral gate (single voice +
  single patch, no comb-filtering; measured 11.2% at C6 probe, lower in the
  mid register)
- Zero-drift: pipe phrase ends flush at BAR (terminal landmark)
- Engine smoke: PhaseModSynth sine-pipe note renders (peak > 0, sustain
  holds); AirPipe pressure-driven pipe renders (peak > 0)

## Stem label / quirks

- GM_PROGRAMS[82] = "Lead 3 (calliope)" → sanitized stem `Lead_3_calliope`
  (spaces → underscore, parens stripped) — STEM_LABEL matches the pipeline's
  real sanitization, **no routing quirk**
- FluidR3 preset 82 = "Calliope Lead" — internal name differs from the GM
  label (cosmetic only; stems are labelled from GM_PROGRAMS, not the SF2)
- GM83 "Lead 4 (chiff)" is the soft recorder-ish sibling, GM84 "Lead 5
  (charang)" the bright fuzz lead, GM85 "Lead 6 (voice)" the formant solo
  voice, GM86 "Lead 7 (fifths)" the stacked-fifths lead, GM87 "Lead 8 (bass
  + lead)" the hybrid — all future candidates; GM82 is the mellow pipe
  member of the Lead 80s family
- Enum `MidiInstrument` has NO calliope constant (10-instrument legacy
  enum) — use raw GM 82; the registry is the full KB
- Channel quirk: melodic channel (0–9) — channel 9 triggers the drum map
- FluidR3 calliope preset is a full-keyboard patch (no per-note ceiling) —
  never clips; the fast attack means short chiff notes stay dry and
  separated (no smear — contrast the synth-voice bloom)
