---
type: instrument
family: Vocal
name: Voice-Like Family
midi_program: 20
gm_name: "Vox Humana (Reed Organ stand-in)"
range_min: 48
range_max: 84
solo_range: [55, 79]
sweet_spot: [60, 76]
role: [lead, melody, countermelody, pad, bass]
synthesis: [voice_like]
members: [vox_humana, kazoo, jaw_harp, didgeridoo, singing_saw, talkbox]
---

# Voice-Like Family

Six synthesized instruments that sound **familiar like a human voice without
being voices**. None of them sings; none has vocal folds, consonants, lyrics,
or a text-to-speech path. Each is a genuine *instrument* — a free reed, a
membrane, a plucked lamella, a lip reed, a bowed blade, an amplified saw —
whose output happens to land in the ear as "voice-adjacent".

## The question this answers

> "I'm not looking for a human voice. I want new *synthesized* instruments
> that sound familiar, like a human voice. Does that exist?"

**Yes — and it is one of the oldest categories in instrument making.** The
answer is not a list; it is a principle:

> **Vocal familiarity is carried by the formant envelope, not by the vocal
> folds.** Any harmonically rich, non-vocal excitation routed through a
> vocal-tract-like formant bank will be heard as voice-like.

This is Fant's (1960) **source–filter theory**: the pitch and harmonic content
come from the source, but *which vowel / what kind of voice* you hear comes
almost entirely from the filter — the resonances of the tract. Change the
source and the instrument changes; keep the formant envelope and it stays
uncannily vocal.

### The historic evidence (this is not a new idea)

| Instrument | Date | Its non-vocal source | Why it reads as voice |
|---|---|---|---|
| **Vox humana** (pipe organ) | 16th c. | free reed in a short resonator | literally named for the voice; played with a tremulant |
| **Kazoo / mirliton** | 19th c. | vibrating membrane (goldbeater's skin) | modulates whatever is hummed into it |
| **Jew's / jaw harp** | ~4000 yrs old | plucked metal lamella | the *mouth cavity* selects one overtone |
| **Didgeridoo** | ~1000 yrs old | lip reed in a long bore | mouth formants shape the drone — a "voice in a tube" |
| **Musical / singing saw** | ~19th c. | bowed steel friction | near-harmonic friction tone + wide vibrato |
| **Talkbox** | 1970s | instrument driven through a tube into the mouth | the mouth IS the filter (Frampton, Zapp, Daft Punk) |
| **Vocoder** (SP-046) | 1939 | filter-bank envelope transfer | imposes a voice's spectral shape on any carrier |
| **FOF** (SP-025) | 1978, IRCAM | triggered cosine wave-packets | formant channels sum to a vocal timbre |
| **Formant synths** (FS1R etc.) | 1998 | parallel formant branch | formants with no voice source at all |

So the category already exists as **formant synthesis** and **cross-synthesis**
— what is new here is exposing it as a *playable family of six distinct
instruments* inside this engine.

## Architecture

```
excitation (instrument-specific)  →  vocal-tract formant cascade  →  radiation
reed / membrane / lamella /          5 unity-DC resonators at         DC block
lip-reed / friction / saw            F1..F5 of a vowel
```

The engine is `sound/synthesis/voice_like.VoiceLikeInstrument`. It is
deliberately **not** `singing_voice.py` (that models an actual sung voice with
a glottal pulse, aspiration, singer's formant, jitter/shimmer). Here the source
is a plain band-limited harmonic series with an instrument-specific amplitude
law — the timbre must come from the tract, and the tests prove it does.

### Why the tract is a **cascade** (and why that matters)

Each section is a second-order resonator normalized to **unity DC gain**
(`b0 = 1 + a1 + a2`), exactly Klatt's cascade branch. Because every section is
unity at DC but resonant at its formant, the higher formants receive
progressively more gain (F3 lands ~+30 dB relative to its input). That boost
automatically cancels the source's 1/f rolloff, so the summed envelope tracks
the **formants** instead of the source tilt.

It also means the whole thing is genuinely all-pole — which is what lets LPC
recover the formants from the output, and that is how the family is verified.
(A *parallel* sum of resonators is pole-zero, LPC cannot fit it, and the source
tilt dominates. That was the first, wrong, version of this module.)

### The members

| key | source | GM program | character |
|---|---|---|---|
| `vox_humana` | free reed + short resonator | 20 Reed Organ | hollower, tremulant, churchy |
| `kazoo` | mirliton membrane | 59 Muted Trumpet | bright, nasal, buzzy honk |
| `jaw_harp` | plucked lamella | 106 Shamisen | twangy drone, sharp attack |
| `didgeridoo` | lip reed, long bore | 20 Reed Organ | deep vocal drone, breathy |
| `singing_saw` | bowed steel friction | 81 Lead 2 (saw) | ethereal, wide vocal vibrato |
| `talkbox` | amplified saw through mouth | 80 Lead 1 (square) | "talking" lead, vowel morph |

## Usage

```python
from sound.synthesis.voice_like import VoiceLikeInstrument, INSTRUMENTS

vi = VoiceLikeInstrument("kazoo", sample_rate=44100, seed=0)
audio = vi.render_note(f0=220.0, duration=1.5, vowel="a")      # mono float64
phrase = vi.render_phrase([(57, 0.5, "a"), (60, 0.5, "o")])
```

`vowel` selects the formant envelope: `a e i o u`. `talkbox` additionally
supports `vowel_end=` to glide formants across a note (its `morph` flag).

For a WAV:

```python
from sound.synthesis.voice_like import render_phrase_wav
render_phrase_wav("out.wav", [(69, 0.5, "o"), (72, 0.8, "a")], instrument="talkbox")
```

## Using these in compositions (the "singing" track)

These instruments are the natural **singing voice** of an arrangement. They
have **no real GM equivalent** — a track assigned "Talkbox" exports MIDI
program 80, and the soundfont would play *Lead 1 (square)*. So producing a
composition that uses them needs two engines on one file:

```
voice tracks  ->  VoiceLikeInstrument (synthesized, per track)
other tracks  ->  FluidSynth (soundfont, the backing band)
then sum -> master -> encode
```

That is **SP-075** (`sound/render/hybrid.py`), wired into the workflow spine:

```python
from workflows.musicom_workflow import produce

r = produce("song.mid", method="SP-075",
            params={"voice_instruments": ["talkbox", None, None, None, None],
                    "bpm": 72})
# → r.wav_path, r.ogg_path ; r.info["engines"] shows which engine per track
```

`voice_instruments` is aligned to the MIDI's **note-bearing tracks** in the
composer's `add_voice()` order (track 0, the tempo track, is skipped —
the same convention as `RenderPipeline.render_stems`). `None` = use the
soundfont for that track.

### In the ballad project

`projects/Styles/Pop/ballad-hitl/` has two palettes with voice-like leads
(`vocal`: Talkbox / Jaw Harp, `drone`: Singing Saw / Vox Humana / Didgeridoo)
and a bridge that produces the routing automatically:

```python
from phase1_compose import PALETTES, voice_instrument_map
voice_instrument_map(PALETTES["vocal"])
# → ['talkbox', None, None, 'jaw_harp', None]
```

Render the demo (4 mastered OGGs, incl. a soundfont-vs-voice A/B):

```bash
$MUSICOM_PYTHON projects/Styles/Pop/ballad-hitl/Scripts/render_vocal_ballad.py
```

**Range caution**: the voice-like members do not all span the same register.
Check before assigning to a role — `jaw_harp` tops at 74 and `didgeridoo` at
55, so neither fits a lead line written 62–77. The palette ranges are
verified by tests.

## Verification (measured, not claimed)

`projects/Instruments/Vocal/voice_like_family/analyze_and_render.py` runs four
checks. Reproduce with:

```bash
$MUSICOM_PYTHON projects/Instruments/Vocal/voice_like_family/analyze_and_render.py
```

1. **Control** — LPC on the bank's own impulse response must recover the
   chosen formants (max error 91 Hz, all five vowels).
2. **Tract vs source** — each rendered note's LPC envelope correlates with its
   instrument's own tract response at **r = 0.83–0.98** (all six tract-driven).
3. **Vowel ID** — confusion matrix on `vox_humana`: **4/5 (80 %)**. The one
   confusion is `/a/` vs `/o/`, which differ only in F1 730 vs 570 Hz and F2
   1090 vs 840 Hz — adjacent vowels on the phonetic chart.
4. **Distinct instruments** — centroids at the same pitch and vowel range
   296 Hz (didgeridoo) to 991 Hz (kazoo), so these are six instruments, not
   one filter with six labels.

`tests/test_voice_like.py` guards all of the above; **47 tests**.
`tests/test_voice_hybrid.py` covers the composition integration (SP-075
routing, the palette bridge, per-engine routing, determinism, and the
soundfont-vs-voice A/B); **24 tests**.

## Method notes / pitfalls

- **A raw FFT cannot show formants on a harmonic tone.** It shows one spike
  per harmonic. You must smooth the harmonic structure away — use LPC
  (`lpc_spectral_envelope`), the standard method. An earlier analysis script
  smoothed a raw FFT by hand with a window narrower than the 110 Hz harmonic
  spacing and reported pure nonsense.
- **Correlate envelopes in dB, not linear amplitude.** A linear correlation is
  dominated by the single largest peak and hides the formant structure.
- **Unity peak gain needs the *minimum* of |denominator|**, not the maximum
  (`|H| = b0/|den|`). Using the max overshoots the gain 6–40× and the bank
  clips. For the cascade, unity DC gain (`b0 = 1+a1+a2`) is the right
  normalization.
- **`a2 = r²`, not `−r²`.** For poles at `r·e^{±jθ}` the denominator is
  `1 − 2r·cosθ·z⁻¹ + r²·z⁻²`; flipping the sign puts the poles outside the
  unit circle and the filter diverges to NaN.
- **Percussive members (`jaw_harp`) cannot be measured in steady state.** Its
  colour is fixed at the pluck instant and then decays; a windowed fit
  understates it. Its filter is verified by the impulse-response control
  instead.

## Relationship to the other Vocal engines

| module | what it is | use it for |
|---|---|---|
| `voice_like.py` (this) | non-vocal instruments with a vocal tract colour | voice-adjacent leads, pads, drones |
| `singing_voice.py` | source-filter model of an actual sung voice | believable "ah/eh/ee" singing lines |
| `vocal.py` | formant guide-vocal utility | scratch guide vocals in a sketch |
| `effects/vowel_filter.py` | formant filter bank over existing audio | imposing vowels on a rendered track |
| SP-046 channel vocoder | cross-synthesis | robot-voice / talkbox effect on any material |
| SP-025 FOF | formant wave functions | vocal/resonant timbres from MIDI |
