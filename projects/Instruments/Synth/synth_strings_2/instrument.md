---
type: instrument
family: Synth
name: Synth Strings 2
midi_program: 51
gms: "Synth Strings 2"
range_min: 36
range_max: 96
solo_range: [48, 86]
role: [pad, harmony, texture, drone, swell, countermelody]
synthesis: [polysynth, additive, phase_mod]
---

# Synth Strings 2

## MIDI / GM

- **Program**: 51 (GM1 "Synth Strings 2")
- **Channel**: melodic channel; polyphonic (the patch plays full chords)
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 51 =
  **"Synth Strings 2"** (verified from the `phdr` chunk; TimGM6mb's thin
  fallback also carries preset 51). RenderPipeline stem label:
  GM_PROGRAMS[51] = **"Synth Strings 2"** → `trackXX_Synth_Strings_2.wav`.
  The sanitizer only rewrites spaces/parens/slashes, so the label matches
  exactly — **no quirk** (verified on disk in `_test/stems_synth_strings_2/`).
- **Enum note**: `structures/instrument.py` `MidiInstrument` exposes only 10
  programs and has **no** synth-strings constant — use the raw GM number 51;
  the registry is the full KB.

## Identity — what this patch actually is

GM51 is the **second voice of the divide-down string machine** — the same
1972–1982 keyboard class as GM50: Eminent 310 Unique, ARP Solina String
Ensemble, ARP Omni, Roland RS-202, Korg Poly-Ensemble, Elka Rhapsody, Logan
String Melody, Crumar Performer. Same architecture underneath:

- **Divide-down oscillator bank** — one master oscillator chain divided down to
  all 12 pitches per octave, borrowed across octaves; bright buzzy core
  band-limited by the divider chain.
- **One shared filter + one shared LFO** for the whole keyboard. The machine is
  **paraphonic, not truly polyphonic**: every held note rides the same
  chorus/vibrato phase. In musicom this is modelled with a *static* per-voice
  detune — never per-note vibrato.
- **Triple BBD ensemble chorus** — three LFO-modulated delay lines producing
  the slow wide swirl. Measured on the render: the sustain envelope wobbles
  ±25% around its mean from chorus amplitude/phase modulation (visible in the
  GM50 render too — it is the machine, not a defect).
- **No velocity sensitivity, no bow noise, no rosin, no body resonance.**
  Infinite sustain while held, short capacitor release.

**What makes GM51 different from GM50** — measured, not lore. Identical Cmaj7
chord, same velocity, rendered solo through FluidR3_GM and analysed:

| Metric (1.5 s window) | GM50 Synth Strings 1 | GM51 Synth Strings 2 |
|---|---|---|
| Spectral centroid, mid (C4–B4) | 1738 Hz | **1853 Hz** |
| Spectral centroid, low (C2–E3) | 717 Hz | **1487 Hz** |
| Spectral centroid, high (C5–B5) | 2727 Hz | **2361 Hz** |
| 50–500 Hz energy share | 35.7% | 34.3% |
| 6–12 kHz "air" share | 4.2% | **3.4%** |
| Envelope at 20 ms (% of peak) | 16% | **12%** |
| Peak amplitude (same MIDI vel) | 0.496 | **0.544** |

Reading: GM51 **keeps roughly twice the upper-partial energy in the bass
register** (1487 vs 717 Hz centroid — GM50's low end turns to mud, GM51 stays
defined), **rolls the top octave off** (2361 vs 2727 Hz, less 6–12 kHz air),
has a **softer onset** (12% vs 16% of peak at 20 ms) and is ~0.8 dB louder at
the same velocity. In practice: GM51 is the **slow-swell, dark-topped,
clear-bottomed** variant — the cinematic/ambient bed; GM50 is the bright
disco/synth-pop string machine.

Records: the slow string beds of 70s/80s film and TV cues, Vangelis-style
sustained washes, ambient and post-rock pads, and the "strings from a
keyboard" layer under singer-songwriter records — anywhere GM50's divider fizz
would fatigue over a long section.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 36–96 | C2–C7 | GM patch span (original machines were 4-octave, 49-key) |
| Low | 36–55 | C2–G3 | cello-ish body; pad roots — GM51 stays readable here (unlike GM50) |
| Middle | 56–79 | G#3–G5 | primary pad/harmony band — the workhorse |
| High | 80–96 | G#5–C7 | soft sheen; rolled off by design, never shrill |

SOLO_RANGE 48–86 (C3–D6) is the idiomatic slow-pad band: the BBD chorus has
enough partials to swirl, the body stays clear, and the darker top does not
disappear. Note the **low bottom** (C3, not E3 as on GM50): GM51's measured
low-register clarity is its main edge, so pad roots and drone basses belong
here.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Sustain | 70 | 1.0 (held) | default pad chord — infinite hold, chorus swirl |
| Legato | 68 | 1.0 | overlapping chord change, no re-attack click |
| Swell | 84 | 1.0 | slow crescendo build — GM51's signature gesture |
| Bloom | 76 | 0.9 | soft entry that opens over ~0.4 s |
| Staccato | 62 | 0.25 | short chop — weak on GM51 (soft onset smears the attack) |
| Marcato | 82 | 0.85 | downbeat chord, chorus blooms after |
| Drone | 56 | 1.0 | static held harmony — ambient/cinematic bed |
| Accent | 88 | 0.9 | unison hit, then sustain |

Note: velocity has little effect on a real string machine (no velocity
sensing). In musicom velocity mainly scales loudness — write dynamics as
arrangement (density, register, doubling), not as hard/soft playing. Because
the onset is soft, **stabs and rhythmic chops are the wrong gesture**; use
GM50 or a synth brass patch for those.

## Timbre DNA

- **Harmonic content**: dense divide-down partial stack, but weighted lower
  than GM50 — weaker 6th–8th partials, so the top octave reads soft rather
  than fizzy; strong low-mid body (measured 1487 Hz centroid at C2–E3)
- **Attack**: ~90 ms soft swell — the slowest onset in the synth-string block
  (GM50 20–40 ms, pads 350 ms+)
- **Decay/sustain**: **none/sustained** — holds while the key is down; the
  ±25% envelope wobble is BBD chorus modulation, not decay
- **Release**: 300–500 ms airy capacitor fade (longer than GM50's 100–300 ms)
- **Modulation**: whole-ensemble chorus, ~±10–15 cents at 0.3–1.5 Hz, wide
  stereo; never a single-note vibrato
- **Character**: dark-topped, full-bodied, slow-blooming; "film pad" rather
  than "disco machine"

## Role in Arrangement

- **Pad / harmony** — sustained chords under lead or vocal; the default use
- **Texture** — wide chorus bed that does not fight a bright lead (no top-end
  fizz to mask a vocal sibilance or a flute)
- **Drone** — static held root/fifth for ambient or modal writing
- **Swell** — section-boundary build; the slow onset makes crescendos sound
  played rather than switched on
- **Countermelody** — long-note line under a moving lead
- NOT a lead voice for fast lines (soft onset smears articulation)
- NOT a rhythm/comp voice, and NOT a bass foundation (bottom is chorused —
  use a bass patch, or double the root an octave down on a real bass)
- NOT a realistic orchestral section (GM48/49 are the sampled sections); GM51
  sits beside GM50 as the *synthetic*, processed sibling

## Synthesis Engines (musicom)

1. **PolySynth** (`sound/synthesis/polysynth.py`) — **primary**. The subtractive
   architecture *is* the physical model: divide-down bank → shared low-pass →
   BBD ensemble chorus. Settings that reproduce the GM51 measurement: saw +
   saw (±11 cents) + triangle body at 0.75, filter **2700 Hz** (between GM50's
   3000 and warm_pad's 1400), resonance 0.25, **attack 0.09 s**, sustain 1.0,
   release 0.45 s, 3 unison voices.
2. **Additive** (`sound/synthesis/additive.py`) — secondary. Detuned harmonic
   stack `string_machine_airy` (softer top than GM50's stack: 8th partial 0.06
   vs 0.10), decay_S 1e-4 to hold the chord. Cheaper for dense arrangements,
   loses the BBD comb coloration.
3. **PhaseModSynth** — tertiary cheap approximation: saw carrier, ratio 1.0,
   depth **0.9** (gentler than GM50's 1.2 — do not re-brighten this patch),
   attack 0.09, release 0.5.

## Production

- **Reverb**: hall **3.4 s** (REVERB_TAIL) — longer than GM50's 2.8: slow
  onset + dark top = cinematic bed that wants the hall tail, not just chorus
  width
- **EQ**: cut 300 Hz −2.0 dB (less than GM50's −2.5 — GM51 already carries its
  low-mid body); boost 2.6 kHz +1.5 dB for articulation under the darker
  filter (GM50 lifts 3.2 kHz +2.0); gentle 9 kHz +1.0 dB shelf — add a little
  air, but do not chase GM50's 8 kHz +1.5 divider fizz
- **Pan**: center for the composed stem; the BBD chorus is already wide, so
  ±0.2 L/R is enough when doubling for a bigger bed
- **Doubling discipline**: never unison-double GM51 against GM50 or a sampled
  section on the SAME pitches — identical pitches from two patches comb-filter
  into buzz (2026-09-01 rule). If both are used, put GM51 an octave down (its
  clear low register) or on a different chord tone.

## Verification

- GM51 → stem `trackXX_Synth_Strings_2.wav` (label matches, no quirk)
- FluidR3 preset 51 = "Synth Strings 2" (verified from the `phdr` chunk)
- Zero-drift: sustained chord units end flush at BAR (terminal landmark)
- Solo render (no unison doubling): 4–8 kHz buzz gate ≤20% passes — GM51 is
  *supposed* to be the darker sibling, so a clean gate confirms no
  comb-filtering was introduced
- A/B measurement vs GM50 (table above) is the empirical basis for the
  range, filter, attack and EQ choices in this file
