---
type: instrument
family: Vocal
name: Human Voice
midi_program: 53
gm_name: "Choir Aahs"
range_min: 48
range_max: 84
solo_range: [55, 79]
sweet_spot: [60, 76]
role: [lead, melody, countermelody]
synthesis: [singing_voice]
---

# Human Voice

A synthetic **singing-voice** virtual instrument. This is the musicom
attempt to reproduce the timbre of a human voice as a *playable model of
the vocal tract*, not a sampled choir.

## The model (source–filter)

The voice is a **source–filter** system (Fant 1960). We synthesize both
halves:

```
glottal source  →  vocal tract  →  radiation
(asymmetric        (formant          (bright lip
 flow derivative)   resonators)       characteristic)
```

### 1. Glottal source — the key to "not a synth"

The single most important timbre decision. A raw saw/sine/impulse train
sounds like an oscillator; a *voice* is distinguished by its **glottal
pulse**: the vocal folds open gradually and snap shut quickly. The closing
produces a sharp negative spike in the volume-velocity derivative that
carries the high harmonics — the "ring", the "brass" of a real voice.

Engine uses the **modified-Rosenberg** pulse (Klatt & Klatt 1990, KLSYN88):
an asymmetric open (half-cosine rise) / close (faster fall) cycle. Controls:

- **open quotient (OQ)** 0.4–0.8 — fraction of the cycle the folds are open.
  Lower = breathier/lighter; higher = pressed/bright.
- **speed quotient (SQ)** 1.0–3.0 — rise/fall asymmetry. Higher = faster
  closure = more high-harmonic ring.

### 2. Vocal tract — the vowel

A cascade of five second-order resonators at the vowel's **formants**
F1–F5 (Peterson & Barney 1952; Klatt 1980), with Klatt bandwidths
(B1=90, B2=110, B3=170, B4=250, B5=300 Hz). Vowel formants:

| vowel | F1 | F2 | F3 |
|---|---|---|---|
| /a/ | 730 | 1090 | 2440 |
| /e/ | 530 | 1840 | 2480 |
| /i/ | 270 | 2290 | 3010 |
| /o/ | 570 | 840 | 2410 |
| /u/ | 300 | 870 | 2240 |

### 3. The extras that sell "voice"

- **Singer's formant** — a parallel resonator at 2.8–3.2 kHz (Sundberg 1974),
  the "ring" that lets a trained voice project over an orchestra.
- **Aspiration** — shaped breath noise (1–5 kHz) mixed into the source,
  for a breathy, intimate timbre.
- **Vibrato** — delayed-onset pitch modulation (~5.5 Hz, ±0.45 semitone).
- **Jitter / shimmer** — per-pulse pitch and amplitude micro-perturbations,
  the irregularity that separates a living voice from a machine.
- **Radiation** — the flow derivative already embodies the +6 dB/octave lip
  characteristic; the cascade normalization trims synthetic harshness.

### 4. Voice types

| type | f0 center | formant scale | singer's formant |
|---|---|---|---|
| soprano | 440 Hz | 1.18 | 3200 Hz |
| alto | 330 Hz | 1.12 | 3000 Hz |
| tenor | 220 Hz | 1.00 | 2800 Hz |
| bass | 165 Hz | 0.92 | 2600 Hz |

The **formant scale** models vocal-tract length: a shorter tract (female,
child) raises every formant, brightening the timbre at the same fundamental
— the acoustic basis of voice type.

## Range

| Zone | MIDI | Register |
|---|---|---|
| Full | 48–84 | C3 (bass) – C6 (soprano) |
| Solo | 55–79 | G3–G5 — practical lead vocal |
| Sweet spot | 60–76 | C4–E5 — pop/classical core |

## Why not a GM preset?

GM 52 ("Choir Aahs") is a *sampled* static pad — one timbre, no vowel, no
pitch control, no articulation. It cannot reproduce the sound of a human
voice; it reproduces a recording of many. This instrument is a **model**:
the same vowel, register, voice type and breath are all parameters, so a
composition can *sing* a phrase, not just play a pad.

## Synthesis engine (musicom)

`sound/synthesis/singing_voice.py` — `SingingVoice`:

```python
from sound.synthesis.singing_voice import SingingVoice
voice = SingingVoice(voice_type="alto")
wav = voice.render_note(69, 1.0, vowel="a")        # A4 "ah"
phrase = voice.render_phrase([(67, 0.5, "a"), (69, 0.5, "e"), (71, 1.0, "i")])
```

- `render_unit(unit, path, vowels=[...])` — drop a `MusicUnit` melody in
  and get a sung WAV (mirrors `FormantVocalGuide.render_melody`).
- `render_phrase_wav(...)` — one-call helper.

## Production

- **Reverb**: hall 1.5–2.2 s — a sung lead wants space, not articulation.
- **EQ**: cut ~350 Hz chest mud; boost ~2.8 kHz (singer's formant);
  gentle high shelf ~8 kHz for consonant clarity.
- **Doubling**: two voices, slightly detuned / different jitter seeds, panned
  L/R — the classic "vocal stack" width.
