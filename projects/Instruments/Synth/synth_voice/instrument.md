---
type: instrument
family: Synth
name: Synth Voice
midi_program: 54
gms: "Synth Voice"
range_min: 36
range_max: 96
solo_range: [60, 84]
role: [lead, melody, harmony, pad, countermelody, accent]
synthesis: [phase_mod, additive, polysynth]
---

# Synth Voice (GM54)

## MIDI / GM

- **Program**: 54 (GM1 "Synth Voice"; Roland GS "Synth Voice", Yamaha XG
  "SynthVoice"). The classic analog/digital synthesizer "choir": a detuned
  saw/square oscillator stack shaped by a vowel (formant) filter, slow
  breathy attack, delayed LFO vibrato — the "aaah" voice of 70s/80s synth
  music (Roland VP-330 choir preset, Yamaha CS-80 "voice", Korg M1 voice
  programs; Vangelis *Blade Runner*, Jean-Michel Jarre *Oxygène*, Tangerine
  Dream, synthwave leads).
- **Enum note**: `structures/instrument.py` `MidiInstrument` exposes only 10
  instruments (and is 1-based: FLUTE=74, SYNTH_PAD=88, STRING_ENSEMBLE=49)
  and has NO synth-voice constant. Use the raw GM number 54 — the registry
  is the full KB.
- **Channel**: melodic channel (0–9). Channel 9 with program 54 would trigger
  the drum-kit map and the ch9 program-0 fallback label `Acoustic_Grand_Piano`
  (ch9 quirk — see timpani lesson).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 54 =
  **"Synth Voice"** (verified from phdr). RenderPipeline stem label:
  GM_PROGRAMS[54] = "Synth Voice" → sanitized `trackXX_Synth_Voice.wav` —
  matches STEM_LABEL "Synth_Voice" exactly, **no quirk**. (GM53 "Voice Oohs"
  is the sampled solo voice; GM54 is the SYNTH one. GM55 "Orchestra Hit" is
  the one-shot stab sibling.)

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 36–96 | C2–C7 | GM-patch idiomatic writing band |
| Low | 36–55 | C2–G3 | dark pad bottom — chord roots, drone beds (mud below C2) |
| Mid | 56–71 | G3–C5 | workhorse band — melody, chord body |
| High | 72–84 | C5–C6 | voice-lead top — the Blade Runner register |
| Top extension | 85–96 | C6–C7 | thin shimmer, riser sparkle |

Empirical FluidR3 pitch sweep (RMS, velocity 90, notes 24–108 step 12): preset
54 audible **8/8 notes, no gaps** (RMS 1308–2067 across the whole span —
bottom 24 the loudest at 2067, mid C4 dips to 1308, treble recovers; full-
keyboard patch, no ceiling). GM synth patches are full-keyboard: **no patch
ceiling** — SF2 never clips a composition. Range 36–96 is the idiomatic
*writing* band, NOT a physical limit.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Ah (sustain) | 65–80 | full | THE default — held open-vowel lead, slow breathy onset |
| Legato | 65–78 | full | seamless voice crossfade — phrase joins |
| Swell | 55–70 | 1.15× | crescendo on a held note — the filter opens, the voice "blooms in" (Jarre move) |
| Marcato | 80–90 | 0.85× | hard onset — accented entrance, word-like attack |
| Staccato | 70–80 | 0.3× | short gated blips — rhythmic voice stabs |
| Vibrato | 72–80 | full | lead with LFO vibrato (delayed ~1.5 s; MIDI CC1/aftertouch — SF2 presets often carry built-in vibrato) |
| Accent | 85–95 | 0.9× | downbeat hit then bloom — the "ah!" entrance |
| Decay fade | 55–62 | full | phrase-end taper — the voice recedes into reverb |

## Timbre DNA

- **Harmonic content**: saw + square oscillator stack with slight detune (the
  synth "section" width), vowel formants imposed by a resonant filter —
  measured (FluidR3, solo): spectral centroid C4 = 4626 Hz, C6 = 6068 Hz —
  a genuinely BRIGHT voice (brighter than the sampled choir; the formant
  band sits 2.4–4.6 kHz and carries the "ah" intelligibility)
- **Attack**: 50–300 ms — the signature gesture: the voice BREATHES in
  (contrast synth brass 1–20 ms stabs, sampled choir ~180 ms)
- **Decay/sustain**: indefinite while held (synthesizer); release 0.3–0.5 s —
  the voice recedes rather than cuts
- **Vibrato**: delayed LFO (onset ~1.5 s, ~5–6 Hz, subtle) — the classic
  synth-voice vibrato; usually absent on stabs/pads, present on held leads
- **Character**: "aaah"-like, choral-but-synthetic, warm mid, airy top;
  instantly 70s/80s sci-fi — a vocal stand-in with no real singer

## Role in Arrangement

- **Lead** — synth-voice leads are THE use: sustained melody lines in the
  vocal register (60–84), doubled at the octave or +third for width
- **Melody** — the "singing" patch for synthwave/retro-pop/film top lines
- **Harmony** — 3–5 note voice pads (slow attack = no chord "blips"; enter
  them legato or on the beat with marcato)
- **Pad** — sustained vowel beds under a lead; the slow attack hides chord
  entrances (the "rising choir" cue)
- **Countermelody** — second voice under a lead, octave/thirds apart
- **Accent** — marcato/word-like downbeat hits, swell climaxes
- **NOT** a bass voice (use synth_bass_1 GM38 / electric_bass GM33); NOT a
  real choir substitute (no breath/ensemble section — that is GM52 Choir
  Aahs); NOT a stab patch (slow attack — keep stabs short but expect bloom)
- Polyphonic: pads and 2–3 note harmonies fully idiomatic; unison melody +
  octave doubling is the width trick

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — **primary**. A
   formant-ish FM voice: saw carrier + sine modulator at the fundamental
   (ratio 1.0, depth **2.6** — between synth_pad 2.0 and synth_brass_1 3.2:
   a voice is softer than a horn, edgier than a pad), attack 0.25 s (the
   breath), release 0.35 s, sustain 0.85 (FM_DEFAULTS).
2. **Additive** (`sound/synthesis/additive.py`) — formant-weighted harmonic
   stack (choir.py precedent: partials near the vowel formants are boosted;
   weights [1.0, 0.78, 0.62, 0.55, 0.40, 0.28, 0.18, 0.10] — brighter top
   than the real choir, the SYNTH voice) (ADDITIVE_DEFAULTS).
3. **Polysynth** (`sound/synthesis/polysynth.py`, PolyVoice) — subtractive
   oscillator-choir: saw + square stack, 6-cent detune, low-pass 3200 Hz
   resonance 0.6 (the vowel peak), slow gate 0.25 s, 3 unison voices
   (POLYSYNTH_DEFAULTS).

## Production

- **Reverb**: hall/plate 2.4–3.0 s — REVERB_TAIL 2.8 s; same as choir (a
  voice is ALWAYS in a room), shorter than synth_pad 3.2 (leads keep
  presence)
- **EQ**: cut ~350 Hz (oscillator stack + vowel formants pile up in the
  low-mid); boost ~2.4 kHz presence (the F3 vowel band — "ah" intelligibility);
  gentle 8.5 kHz air shelf (bright but NOT sibilant — cut 8k = hiss)
- **Pan**: center for the composed stem; ±0.3 L/R spread on wide doubled-lead
  swells
- **Layering**: idiomatic doubling is octaves or thirds (synth voice + same
  patch 8va, or + choir aahs for the hybrid synth/real chorus) — NEVER unison
  with another melodic patch on the same pitches (comb-filtering — the
  2026-09-01 lesson). + synth bass root-octave below = the classic
  synthwave lead stack

## Verification

- GM54 → stem `trackXX_Synth_Voice.wav` (GM_PROGRAMS[54] = "Synth Voice",
  FluidR3 preset 54 = "Synth Voice" — labels match exactly) — **no quirk**
- `by_name('synth voice')` → Synth Voice, `by_program(54)` → Synth Voice
  (distinct from 52 Choir Aahs / 53 Voice Oohs), `in_sweet_spot(67)` = True,
  `in_sweet_spot(24)` = False
- Empirical pitch sweep: preset 54 audible 8/8 notes (24–108, step 12), no
  gaps (RMS 1308–2067, flat-ish, bottom loudest)
- Buzz check: solo render passes the 4–8 kHz spectral gate (single voice +
  single patch, no comb-filtering)
- Zero-drift: voice phrase ends flush at BAR (terminal landmark)
- Engine smoke: PhaseModSynth saw-voice note renders (peak > 0, sustain
  holds); additive formant stack renders

## Stem label / quirks

- GM_PROGRAMS[54] = "Synth Voice" → sanitized stem `Synth_Voice` (space →
  underscore) — matches STEM_LABEL, **no routing quirk**
- FluidR3 preset 54 = "Synth Voice" — exact match (contrast: GM74 Flute →
  "Recorder", GM109 → "Bag pipe", GM111 → "Shanai" quirks)
- GM55 "Orchestra Hit" is the one-shot stab sibling (a future candidate —
  same synth-voice era, different gesture); GM53 "Voice Oohs" is the sampled
  solo voice (Vocal family)
- Enum `MidiInstrument` has NO synth-voice constant (10-instrument legacy
  enum) — use raw GM 54; the registry is the full KB
- Channel quirk: melodic channel (0–9) — channel 9 triggers the drum map
- FluidR3 synth-voice preset is a full-keyboard patch (no per-note ceiling)
  — never clips; the slow attack means short staccato notes bloom into the
  next note — write stabs with a gap or accept the smear
