# REPORT — Warm Pad (GM89 "Pad 2 (warm)")

**Date**: 2026-11-06 (nightly instrument research job, layer-aligned)
**Family**: Synth (fifth entry — after synth_pad, synth_brass_1, synth_voice, calliope)
**Files**:
- `Synth/warm_pad/instrument.md` — full research reference
- `Synth/warm_pad/warm_pad.py` — importable constants
- `Synth/warm_pad/REPORT.md` — this report
- `_test/verify_warm_pad.py` + `_test/verify_warm_pad_out.txt` — end-to-end proof
- `_test/registry_out_warm_pad.txt` — registry verification run

---

## 1. Instrument identity

GM89 **"Pad 2 (warm)"** is the classic **warm analog synth pad**: a detuned
oscillator stack (triangle/saw) through a low-pass filter, slow attack, wide
chorus — the 80s ballad / synthwave / ambient bed (Roland Juno-60 warm
programs, Oberheim OB-X pads, Vangelis *Charlots of Fire* beds, M83 / Tame
Impala warmth). It is the **DARK sibling of synth_pad GM88 "Pad 1 (new
age)"**: where new-age is bright/digital glass (air + shimmer), warm is
rounder and darker — stronger fundamental, weaker high partials, wider
chorus, gentler top. FluidR3 preset 89 = **"Warm Pad"** — the synth_pad
entry (2026-10-12) explicitly flagged it ("preset 89 = 'Warm Pad' is the
darker sibling"); this entry claims it.

Selection rationale: the "remaining candidates" sweep (GM programs not yet
in the 86-instrument registry) surfaced GM2/3 (piano family), GM17/18
(organs), GM31 (guitar harmonics), GM34/36/37 (bass family), GM49/50/51
(strings/synth-strings), GM55 (orchestra hit), GM63 (synth brass 2),
GM76/83–87 (leads/blown bottle), GM89–95 (pads), GM112/115/117/118
(percussion). GM89 was the highest-value pick: (a) pads are a core
arrangement role for the nightly composition job and the KB had only ONE
synth pad; (b) the KB already named GM89 as the natural sibling; (c) **zero
collisions** — no `voice_like` stand-in claims program 89 (unlike 80/81,
which are claimed by talkbox/singing_saw — the distortion_guitar and choir
selection lessons), and `by_program(89)` was free.

## 2. MIDI / GM

| Item | Value |
|---|---|
| Program | **89** (raw GM number; `MidiInstrument` enum has no pad-2 constant — 10-instrument legacy enum, registry is the full KB) |
| GM label | "Pad 2 (warm)" (GM1 spec) |
| Channel | melodic 0–9 (ch9 triggers the drum map + `Acoustic_Grand_Piano` fallback label — timpani lesson) |
| FluidR3 preset 89 | **"Warm Pad"** (verified from phdr of the `discover_soundfont()`-resolved FluidR3_GM.sf2) |
| RenderPipeline stem | GM_PROGRAMS[89] = "Pad 2 (warm)" → sanitized `trackXX_Pad_2_warm.wav` — STEM_LABEL `Pad_2_warm` matches, **no routing quirk** |

## 3. Range (verified)

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full (writing band) | 36–96 | C2–C7 | idiomatic pad-writing band |
| Low | 36–55 | C2–G3 | roots, drone bottom |
| Mid | 56–79 | G3–G5 | PRIMARY chord-pad body |
| High | 80–96 | G5–C7 | warm top (rounded, NOT new-age shimmer) |
| Sweet spot | 60–84 | C4–C6 | chord-pad zone |
| Solo range | 55–84 | G3–C6 | solo-pad focus |

**Empirical FluidR3 pitch sweep** (RMS, velocity 90, single-note renders via
UnitMatrixComposer → fluidsynth):

| Note | Pitch | RMS |
|---|---|---|
| 36 | C2 | 1186.9 |
| 48 | C3 | 1353.8 |
| 60 | C4 | 1143.7 |
| 72 | C5 | 1076.3 |
| 84 | C6 | 815.4 |
| 96 | C7 | 773.4 |
| 108 | C8 | 760.2 |

**7/7 audible, no gaps, no ceiling** — essentially flat across the whole
span with a gentle treble rolloff (C8 still audible at 760). Full-keyboard
patch — SF2 never clips a composition. Range 36–96 is the idiomatic WRITING
band, not a physical limit.

## 4. Role in arrangement

**pad, harmony, texture, drone, accent** — the anti-new-age DARK bed:
ballads, synthwave verses, ambient underscores. NOT a lead (slow attack
smears melodic runs — the lead-pad role is synth_voice), NOT rhythm/comp,
NOT bass. Polyphonic: 3–5 note chords fully idiomatic. `registry_table()`
role row: `| Synth | Pad 2 (warm) | 89 | 36–96 | pad, harmony, texture,
drone, accent |`.

## 5. Synthesis engines (musicom)

1. **Additive — PRIMARY** (`sound/synthesis/additive.py`, SoundWave). The
   pad IS a detuned harmonic stack (synth_pad / string_ensemble / organ
   precedent).
   - `ADDITIVE_HARMONICS["pad_warm"]` = `[1.0, 0.78, 0.58, 0.40, 0.26, 0.15,
     0.08]` — strong fundamental, FASTER rolloff than pad_newage
     `[1.0, 0.65, 0.5, 0.35, 0.22, 0.15, 0.1, 0.06]`: the warmth is the
     low-mid body, the top is rounded not sparkling.
   - **Quirk found**: the weights are RELATIVE (drawbar-style); the
     `apply_overtones()` API asserts factors sum to 1.0 — normalize before
     calling (documented in warm_pad.py + instrument.md).
   - `SYNTHESIS_DEFAULTS` (load through registry): attack 0.45 s (between
     string_ensemble 0.35 and synth_pad 0.55), detune ±0.015 (widest in the
     pad family — the analog chorus IS the identity), stack 3 (fewer than
     synth_pad's 4 = less top brightness), release 0.6, sustain 0.9,
     **decay_S 1e-4** (the 2026-10-12 additive per-grid-step quirk).
   - **Measured**: late(1.0–1.5 s) envelope max **0.828** with decay_S 1e-4
     vs **0.014** with decay_S 0.005 (collapse) — the quirk is real and the
     recipe beats it.
2. **Polysynth — SECONDARY** (`sound/synthesis/polysynth.py`, PolyVoice).
   The polyBLEP subtractive architecture IS the analog warm-pad model:
   triangle core + 2 detuned saws (±7 cents), **low-pass 1400 Hz** (HALF of
   synth_brass_1's 2800 — the darkness IS the point), resonance 0.35,
   env attack 0.45 / decay 0.3 / sustain 0.8 / release 0.6, filter env
   follows the amp (pad filter-follows-amp). **Measured**: A3 peak 0.927,
   sustain-window rms 0.178 vs release-window 0.094 — hold_ratio **1.90**,
   sustain holds, no collapse (env1 measured at 0.8 through 1.0–1.5 s).
3. **PhaseModSynth — TERTIARY** (`sound/synthesis/phase_mod.py`): FM pad,
   saw carrier, ratio 1.0, depth **1.5** (gentle — warm pads are NOT brassy;
   contrast synth_brass_1 3.2), attack 0.5, release 0.6, sustain 0.85.

## 6. Production defaults

- **REVERB_TAIL 3.0 s** — between string_ensemble 2.6 and synth_pad 3.2:
  blooms in a big hall but keeps more body than the new-age shimmer (which
  needs the full 3.2 air wash).
- **EQ_BODY** cut 250 Hz −2.5 dB — the strong fundamental piles the low-mid
  fast; cut a touch LOWER than synth_pad's 300 (warmth = more fundamental
  mass).
- **EQ_PRESENCE** boost 2.4 kHz +2.0 dB — the warm BODY band (contrast
  new-age 3.8 kHz shimmer).
- **EQ_AIR** highshelf 7.5 kHz +1.5 dB — GENTLE top air (warmth rolls the
  top off by design; contrast new-age 9.5 kHz +2.0).
- **PAN 0.0** centre; ±0.4 L/R spread on wide stereo swells.

## 7. Registration (REGISTRY DISCIPLINE)

`instrument_registry.py` updated:
1. `_INSTRUMENT_MODULES`: `"Synth.warm_pad.warm_pad": "warm_pad"`
2. Convenience constant: `WARM_PAD = ALL_INSTRUMENTS["warm_pad"]`
3. `registry_table()` role row (see §4)
4. `__main__` verification block

**Registry run** (`python instrument_registry.py` → full `registry_table()`
+ verification, captured in `_test/registry_out_warm_pad.txt`):

```
=== Warm Pad (Pad 2 warm, GM89) ===
  WARM_PAD.midi_program = 89 (should be 89)
  by_name('warm pad') = <Instrument Pad 2 (warm) (family=Synth, program=89, range=36-96)>
  by_name('Pad 2 (warm)') = <Instrument Pad 2 (warm) (family=Synth, program=89, range=36-96)>
  by_program(89) = <Instrument Pad 2 (warm) (family=Synth, program=89, range=36-96)>
  WARM_PAD.in_sweet_spot(72) = True
  WARM_PAD.in_sweet_spot(24) = False
  WARM_PAD.range_min = 36 WARM_PAD.range_max = 96
  WARM_PAD.stem_label = 'Pad_2_warm'
  WARM_PAD.synthesis = 'additive'
  WARM_PAD.synthesis_defaults = {'instrument': 'warm_pad', 'attack': 0.45, 'detune': 0.015, 'stack': 3, 'release': 0.6, 'sustain_level': 0.9, 'decay_S': 0.0001}
```

`registry_table()` new row (87 instruments total, verified present):

```
| Synth | Pad 2 (warm) | 89 | 36–96 | pad, harmony, texture, drone, accent |
```

## 8. End-to-end verification (verify_warm_pad.py — ALL CHECKS PASSED)

- **Composition**: UnitMatrixComposer, 1 bar / 1 section, 100 bpm, Warm Pad
  SOLO on ch0 (C major C4/E4/G4 half-bar → A minor A3/C4/E4 half-bar, all
  flush at BAR) + drum-kit context on ch9. **NO second melodic patch on the
  same pitches** (2026-09-01 comb-filter rule).
- **Zero-drift**: `True (OK)`.
- **MIDI**: `warm_pad_test.mid`, **177 bytes** (> 40 ✓).
- **WAV solo render** (FluidSynth via `discover_soundfont()` → FluidR3):
  `warm_pad_test.wav`, **1,305,900 bytes** (> 40 ✓).
- **Spectral gate**: 4–8 kHz buzz **5.2%** (OK — well under the 20% gate; a
  DARK pad, as designed).
- **Stems on disk**: `track00_Pad_2_warm.wav` (1,305,900 B) +
  `track01_Drums.wav` (849,708 B) — stem label matches pipeline GM_PROGRAMS.
- **Stem label**: `GM_PROGRAMS[89]` = `"Pad 2 (warm)"` → `Pad_2_warm`;
  `STEM_LABEL == 'Pad_2_warm'` ✓; FluidR3 preset 89 = `"Warm Pad"` ✓
  (internal SF2 name differs cosmetically, no routing impact).
- **Engine smoke**: Additive pad_warm holds (0.828 vs 0.014 collapse —
  decay_S quirk demonstrated); Polysynth warm pad sustains (hold_ratio
  1.90).

## 9. Quirks found

1. **Additive relative weights**: `ADDITIVE_HARMONICS` stacks are relative
   (drawbar-style) — `apply_overtones()` asserts sum 1.0, normalize first
   (same class of constraint as the tango_accordion note).
2. **Additive decay_S quirk** (inherited from synth_pad, 2026-10-12):
   `apply_overtones` leaves `self.frequency` at the TOP partial, so the ADSR
   grid step is per-grid-step and a pad recipe MUST use decay_S ~1e-4 or the
   chord collapses (measured 0.828 vs 0.014).
3. **Slow attack**: short staccato blips bloom into the next note — write
   stabs with a gap or accept the smear (same as synth_voice).
4. **No unison pad-stacking**: warm pad + another pad/string patch on the
   same pitches is the definitive comb-filter buzz (2026-09-01 rule) —
   octaves or zone-splitting (55–79 + 80–96) only.
5. **Stem sanitization**: GM_PROGRAMS[89] "Pad 2 (warm)" → `Pad_2_warm`
   (parens stripped) — STEM_LABEL matches the pipeline's real label, no
   routing quirk. SF2 internal name "Warm Pad" differs from the GM label,
   cosmetic only.
6. **Full-keyboard patch**: preset 89 plays 36–108 with no ceiling (C8=108
   still audible, RMS 760) — range 36–96 is the idiomatic writing band, not
   a physical limit.
