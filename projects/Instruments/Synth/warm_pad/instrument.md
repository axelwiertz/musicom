---
type: instrument
family: Synth
name: Warm Pad
midi_program: 89
gms: "Pad 2 (warm)"
range_min: 36
range_max: 96
solo_range: [55, 84]
role: [pad, harmony, texture, drone, accent]
synthesis: [additive, polysynth, phase_mod]
---

# Warm Pad (GM89 — Pad 2)

## MIDI / GM

- **Program**: 89 (GM1 "Pad 2 (warm)"). The classic **warm analog synth pad**:
  a detuned oscillator stack (triangle/saw) through a low-pass filter with a
  slow attack and wide chorus — the 80s ballad / synthwave / ambient bed
  (Roland Juno-60 warm programs, Oberheim OB-X pads, Vangelis *Charlots of
  Fire* beds, M83 / Tame Impala warmth). The **darker sibling** of synth_pad
  GM88 "Pad 1 (new age)": where new-age is bright/digital glass (air +
  shimmer), warm is rounder and darker — a stronger fundamental, weaker high
  partials, wider chorus, gentler top. FluidR3 preset 89 = **"Warm Pad"**
  (verified from phdr; the synth_pad entry already flagged it as the darker
  sibling — this entry claims it).
- **Enum note**: `structures/instrument.py` `MidiInstrument` exposes only 10
  instruments and has NO warm-pad constant — use the raw GM number 89; the
  registry is the full KB.
- **Channel**: melodic channel (0–9). Channel 9 with program 89 would trigger
  the drum-kit map and the ch9 program-0 fallback label
  `Acoustic_Grand_Piano` (ch9 quirk — see timpani lesson).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 89 =
  **"Warm Pad"** (verified from phdr). RenderPipeline stem label:
  GM_PROGRAMS[89] = "Pad 2 (warm)" → sanitized `trackXX_Pad_2_warm.wav`
  (spaces → `_`, parens stripped) — STEM_LABEL `Pad_2_warm` matches the
  pipeline's real sanitization, **no routing quirk**.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 36–96 | C2–C7 | idiomatic writing band (GM patch plays the full keyboard) |
| Low | 36–55 | C2–G3 | sub/mid-bass pad — roots, drone bottom (mud below C2) |
| Mid | 56–79 | G3–G5 | PRIMARY chord-pad body — the workhorse band |
| High | 80–96 | G5–C7 | warm top — rounded, NOT the new-age shimmer (rolls off) |

Empirical FluidR3 pitch sweep (RMS, velocity 90, notes 36–108 step 12):
preset 89 audible everywhere in the writing band — no gaps, no ceiling —
SF2 never clips a composition (full sweep data in REPORT.md).

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Sustain | 65–82 | full | slow-swelling held pad — THE default gesture |
| Legato | 68 | 1.0× | seamless voice crossfade — chord changes |
| Swell | 80–88 | 1.0× | whole-bar crescendo — the ballad build |
| Bloom | 62–70 | 1.25× | extra-long swell past the bar — feeds the reverb, the warm signature |
| Staccato | 62–70 | 0.25× | short pad "blip" — rhythmic filter-pulse motif |
| Marcato | 82–90 | 0.85× | attack override — plucked/bell onset (D-50 style) |
| Drone | 58–64 | 1.0× | static sustained harmony — ambient bed |
| Accent | 84–94 | 0.9× | hard entrance — downbeat hit, then bloom |

## Timbre DNA

- **Harmonic content**: strong fundamental with a FAST rolloff — the warm
  body lives in the low-mid (measured FluidR3 solo spectral centroid is
  LOW for a pad: ~1.8–2.5 kHz at C4, vs new-age shimmer above); the top is
  rounded, not sparkling
- **Attack**: 300–600 ms slow swell (between string_ensemble 0.35 and
  synth_pad 0.55 — warm starts a touch faster than the new-age glass);
  chords ENTER, they don't stab
- **Decay/sustain**: indefinite while held (sustain 0.9), release 0.6 s —
  tails feed the reverb
- **Chorus**: the widest detune in the pad family (±1.5% per voice, 3
  voices) — the analog ensemble blur IS the identity
- **Character**: dark, round, enveloping — "the chord you can hug";
  instantly 80s ballad / synthwave / ambient; the anti-shimmer sibling of
  GM88

## Role in Arrangement

- **Pad** — the harmonic canvas: sustained chords, the song-bed voice
- **Harmony** — 3–5 note chords fully idiomatic (the warm stack blooms in
  space)
- **Texture** — ambient beds, evolving swells, drone washes
- **Drone** — static sustained harmony / root pedals (low zone 36–55)
- **Accent** — soft marcato entrances on downbeats (NOT stabs — slow attack
  smears; use synth_brass_1 for stabs)
- **NOT** a lead voice (slow attack — melodic runs smear; the lead pad role
  goes to synth_voice), NOT a rhythm/comp voice, NOT a bass voice (use the
  Bass family)
- Polyphonic: chords fully idiomatic; unison doubling with another melodic
  patch on the same pitches is NOT (comb-filter rule — the 2026-09-01
  lesson; this is the SECOND pad in the KB after synth_pad, and
  pad-stacking unison is the classic buzz machine)

## Synthesis Engines (musicom)

1. **Additive** (`sound/synthesis/additive.py`) — **primary**. The pad IS a
   detuned harmonic stack (synth_pad / string_ensemble / organ engine
   precedent): `ADDITIVE_HARMONICS["pad_warm"]` =
   [1.0, 0.78, 0.58, 0.40, 0.26, 0.15, 0.08] — strong fundamental, FASTER
   rolloff than pad_newage [1.0, 0.65, 0.5, 0.35, 0.22, 0.15, 0.1, 0.06].
   SYNTHESIS_DEFAULTS: attack 0.45 s, detune ±0.015 (2× the string-section
   chorus, wider than synth_pad's ±0.012), stack 3, release 0.6, sustain
   0.9, **decay_S 1e-4** (the 2026-10-12 additive quirk: `apply_overtones`
   leaves `self.frequency` at the TOP partial so `get_adsr_weights`' grid
   step is per-grid-step — a pad recipe MUST use decay_S ~1e-4 or the
   chord collapses).
2. **Polysynth** (`sound/synthesis/polysynth.py`, PolyVoice) — **secondary**,
   the analog-pad architecture: triangle core + 2 detuned saws (±7 cents),
   **low-pass 1400 Hz** (half of synth_brass_1's 2800 — the darkness IS the
   point), resonance 0.35, env attack 0.45 / sustain 0.8 / release 0.6,
   3 unison voices (POLYSYNTH_DEFAULTS).
3. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — **tertiary** FM pad:
   saw carrier, ratio 1.0, depth 1.5 (gentle — warm pads are NOT brassy;
   contrast synth_brass_1 3.2), attack 0.5, release 0.6.

## Production

- **Reverb**: hall 2.6–3.2 s — REVERB_TAIL 3.0 s; between string_ensemble
  2.6 and synth_pad 3.2: the warm pad blooms in a big hall but keeps more
  body than the new-age shimmer (which needs the full 3.2 air wash)
- **EQ**: cut ~250 Hz (the strong fundamental piles the low-mid fast — cut a
  touch LOWER than synth_pad's 300: warmth = more fundamental mass); boost
  ~2.4 kHz +2 dB (the warm BODY presence band, contrast new-age 3.8 kHz);
  gentle 7.5 kHz +1.5 dB air shelf (warmth rolls the top off by design,
  contrast new-age 9.5 kHz +2.0)
- **Pan**: center for the composed stem; ±0.4 L/R spread on wide stereo
  swells (same as synth_pad)

## Layering / writing quirks

- Idiomatic doubling is **octaves or zone-splitting** (55–79 + 80–96),
  NEVER unison with another melodic patch on the same pitches (the
  2026-09-01 comb-filter lesson — a warm pad + string ensemble unison is
  the definitive buzz machine)
- Hold chords ≥ 1.5–2 s or the slow attack never speaks (same pad-writing
  quirk as synth_pad); write a gap before chord changes or the swell
  smears into the next harmony
- The warm pad is the "anti-new-age" choice: when the arrangement needs a
  DARK bed (ballads, synthwave verses, ambient underscores), GM89; when it
  needs glass/shimmer (Enya-style air), GM88
- GM90 "Pad 3 (polysynth)", GM92 "Pad 5 (bowed)", GM93 "Pad 6 (metallic)",
  GM94 "Pad 7 (halo)" are future sibling candidates — GM89 is the warm
  member of the Pad 88–95 family

## Verification

- GM89 → stem `trackXX_Pad_2_warm.wav` (GM_PROGRAMS[89] = "Pad 2 (warm)"
  sanitized; FluidR3 preset 89 = "Warm Pad" — internal SF2 name differs
  cosmetically, **no routing quirk**)
- `by_name('warm pad')` → Warm Pad, `by_program(89)` → Warm Pad (distinct
  from 88 synth_pad), `in_sweet_spot(72)` = True, `in_sweet_spot(24)` =
  False
- Empirical pitch sweep: preset 89 audible across the full writing band, no
  gaps (full RMS table in REPORT.md)
- Buzz check: solo render passes the 4–8 kHz spectral gate (single voice +
  single patch, no comb-filtering — warm pad is DARK, buzz is minimal)
- Zero-drift: pad chord ends flush at BAR (terminal landmark)
- Engine smoke: Additive warm-pad chord holds (late-sustain envelope max
  ≥ 0.45 collapse gate with decay_S 1e-4); Polysynth warm-pad note renders
  (peak > 0)

## Stem label / quirks

- GM_PROGRAMS[89] = "Pad 2 (warm)" → sanitized stem `Pad_2_warm` (spaces →
  underscore, parens stripped) — STEM_LABEL matches the pipeline's real
  sanitization, **no routing quirk**
- FluidR3 preset 89 = "Warm Pad" — internal name differs from the GM label
  (cosmetic only; stems are labelled from GM_PROGRAMS, not the SF2)
- Enum `MidiInstrument` has NO warm-pad constant (10-instrument legacy
  enum) — use raw GM 89; the registry is the full KB
- Channel quirk: melodic channel (0–9) — channel 9 triggers the drum map
- FluidR3 warm-pad preset is a full-keyboard patch (no per-note ceiling) —
  never clips; the slow attack means short blips bloom into the next note —
  write stabs with a gap or accept the smear (same as synth_voice)
