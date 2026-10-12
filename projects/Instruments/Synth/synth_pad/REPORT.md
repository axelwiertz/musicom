# Synth Pad (Pad 1, new age) — Instrument Research Report

**Date**: 2026-10-12 (nightly instrument job)
**Instrument**: Synth Pad — GM88 "Pad 1 (new age)"
**Family**: **Synth** (NEW family — first entry)
**Files**:
- `Synth/synth_pad/instrument.md` (research doc)
- `Synth/synth_pad/synth_pad.py` (constants)
- `Synth/synth_pad/REPORT.md` (this file)
- `_test/verify_synth_pad.py` (end-to-end verification)
- `_test/synth_pad_test.mid/.wav`, `_test/stems_synth_pad/` (artifacts)

---

## 1. Why this instrument

`orchestration.md`'s Pad role: *"sustained background, texture — **Strings
(sustained), Synth Pad, Organ**"*. String Ensemble 1 (2026-10-11) and Church
Organ already exist in the KB — **"Synth Pad" was the only pad-role voice
with NO KB entry**. Worse: composition jobs have been sending
`MidiInstrument.SYNTH_PAD` (= 88) for Pad voices for months (Arabic
235-arabic-rast-rework, 071-arabic-rast-ant-colony, Ambient evolving v1,
Experimental 044-isorhythmic-spatial) with nothing in the registry behind
it. Same "referenced-with-no-entry" pattern that motivated Pizzicato
Strings (10-10) and String Ensemble 1 (10-11).

## 2. Identity / GM mapping

| Field | Value |
|---|---|
| MIDI program | **88** (GM1 "Pad 1 (new age)") — 0-based; the 89th GM entry |
| GM name | `Pad 1 (new age)` |
| Enum | `MidiInstrument.SYNTH_PAD = 88` — **matches the raw GM program for once** (unlike FLUTE=74/STRING_ENSEMBLE=49 legacy off-by-ones). Do NOT "correct" it. |
| FluidR3 preset | **"Fantasia"** (verified from phdr — FluidR3's internal name for the GM new-age pad; preset 89 = "Warm Pad" is the darker sibling) |
| Stem label | GM_PROGRAMS[88] = "Pad 1 (new age)" → sanitized `Pad_1_new_age` → **`track00_Pad_1_new_age.wav`** (verified on disk) — **no routing quirk** (parens stripped, spaces → underscore) |

## 3. Range (empirically verified)

| Zone | MIDI | Pitches | Notes |
|---|---|---|---|
| Full range (writing band) | 36–96 | C2–C7 | GM pad patch plays the WHOLE keyboard — **no patch ceiling** |
| Low | 36–55 | C2–G3 | drone/root bottom (mud below C2) |
| Mid | 56–79 | G3–G5 | primary chord-pad body — the workhorse band |
| High | 80–96 | G5–C7 | shimmer top — new-age sparkle |
| Sweet spot | 60–84 | C4–C6 | fullest body + air balance |

Empirical FluidR3 pitch sweep (RMS @ vel 72, 1-bar sustained notes):
36→603, 48→697, 60→805, 72→865, 84→842, 96→838, 108→392 — **audible
everywhere** (contrast: timpani/pizzicato patches die at 102+). C7+ softens
to shimmer; C2− is sub-bass mud. Range is a *writing* guideline, not a
physical or patch limit.

## 4. Role in arrangement

`pad, harmony, texture, drone, accent` — the harmonic canvas voice. NOT a
rhythm voice, NOT a lead line. Slow onset means it colors, it does not
articulate; write chords ≥ 2 s.

## 5. Articulations (velocity, duration_factor)

| Technique | Vel | Dur | Use |
|---|---|---|---|
| sustain | 70 | 1.0 | slow-swelling pad — default |
| legato | 68 | 1.0 | seamless chord changes |
| swell | 82 | 1.0 | crescendo build (Enya/Vangelis move) |
| staccato | 64 | 0.25 | pad "blip" — filter-pulse motif |
| marcato | 85 | 0.85 | attack override (D-50 bell onset) |
| drone | 60 | 1.0 | static ambient bed |
| accent | 88 | 0.9 | hard entrance, then bloom |

## 6. Synthesis engine recommendation

1. **Additive** (primary — `sound/synthesis/additive.py`): the pad IS a
   detuned harmonic stack (organ/string-ensemble engine precedent).
   `ADDITIVE_HARMONICS.pad_warm` [1.0,0.8,0.6,0.45,0.3,0.2,0.12] /
   `pad_newage` [1.0,0.65,0.5,0.35,0.22,0.15,0.1,0.06] (relative weights —
   normalize to sum 1.0 for `apply_overtones`); SYNTHESIS_DEFAULTS:
   attack 0.55 s, detune ±0.012 (2× string-ensemble chorus), stack 4,
   release 0.5 s, sustain 0.9.
2. **PhaseModSynth** (alt — `sound/synthesis/phase_mod.py`): saw carrier,
   sine mod ratio 1.0, depth 2.0, attack 0.6 s, sustain 0.85 (FM_DEFAULTS).
3. **polysynth** (polyBLEP subtractive — brighter/edgier pads).

## 7. Production defaults

| Param | Value | Rationale |
|---|---|---|
| REVERB_TAIL | **3.2 s** | LONGEST in the KB (string ens 2.6, harp 2.2) — the pad blooms in space |
| EQ_BODY | 300 Hz, −3.0 dB | synth chords pile up 250–400 Hz fast |
| EQ_PRESENCE | 3.8 kHz, +2.5 dB | shimmer/presence |
| EQ_AIR | 9.5 kHz shelf, +2.0 dB | new-age AIR is the identity (contrast: string ens CUTS 8.5k) |
| PAN | 0.0 (center) | ±0.4 L/R for wide stereo swells |

## 8. Registration proof (registry = the KB gate)

`instrument_registry.py` edits: `"Synth.synth_pad.synth_pad": "synth_pad"`
in `_INSTRUMENT_MODULES`, `SYNTH_PAD = ALL_INSTRUMENTS["synth_pad"]`
constant, role mapping in `registry_table()`, verification block in
`__main__`.

Registry verification run (must re-run nightly job gate) — new table row:

```
| Synth | Pad 1 (new age) | 88 | 36–96 | pad, harmony, texture, drone, accent |
```

Verification lines:

```
=== Synth Pad (Pad 1 new age, GM88) ===
  SYNTH_PAD.midi_program = 88 (should be 88)
  by_name('synth pad') = <Instrument Pad 1 (new age) (family=Synth, program=88, range=36-96)>
  by_name('pad 1 (new age)') = <Instrument Pad 1 (new age) (family=Synth, program=88, range=36-96)>
  by_program(88) = <Instrument Pad 1 (new age) (family=Synth, program=88, range=36-96)>
  SYNTH_PAD.in_sweet_spot(72) = True
  SYNTH_PAD.in_sweet_spot(24) = False
  SYNTH_PAD.range_min = 36 SYNTH_PAD.range_max = 96
  SYNTH_PAD.stem_label = 'Pad_1_new_age'
```

Registry total: 59 → **60 modules** (65 keys incl. voice-like members).

## 9. Verification results (end-to-end)

| Check | Result |
|---|---|
| Registry import (`by_name`/`by_program`) | ✓ (see §8) |
| UnitMatrixComposer (1 voice, 1 section, 1 bar; C4-E4-G4-C5 whole-bar) | zero-drift **True (OK)** |
| MIDI export | `synth_pad_test.mid` — **75 bytes** (> 40 ✓) |
| WAV render (SOLO — one voice, `discover_soundfont()` → FluidR3_GM.sf2, `-g 1.2`) | `synth_pad_test.wav` — **1,629,996 bytes (~1.63 MB)** (> 40 ✓) |
| Spectral buzz check (4–8 kHz) | **8.2%** — under the 20% gate; no comb-filtering (single patch, no unison doubling) |
| Pitch sweep | 7/7 notes audible 36–108 (see §3) |
| SF2 preset name (phdr) | 88 → "Fantasia", 89 → "Warm Pad" |
| RenderPipeline stems | **`track00_Pad_1_new_age.wav`** (1.63 MB) ✓ |
| PhaseModSynth smoke (FM_DEFAULTS, C4) | peak 0.783; onset/late RMS **0.065** — slow attack confirmed |
| Additive smoke (pad_warm, C4, 2 s) | late-sustain envelope max **0.79** (≥ 0.45 gate) — sustain holds, no collapse |

## 10. Quirks discovered (register for the KB)

1. **`MidiInstrument.SYNTH_PAD = 88` is CORRECT** — the rare enum/raw-GM
   exact match (all other enum values are legacy off-by-ones). Composition
   jobs in Styles/ already send 88 for Pad voices; this entry documents the
   exact patch they render.
2. **FluidR3 preset 88 = "Fantasia"** — SF2 internal name ≠ GM label
   ("Pad 1 (new age)"). Cosmetic only; stems come from pipeline
   GM_PROGRAMS, so stems say `Pad_1_new_age`.
3. **Paren-strip stem sanitization**: GM_PROGRAMS[88] "Pad 1 (new age)" →
   `Pad_1_new_age` (spaces → `_`, parens stripped) — the parenthesized GM
   name is the only wrinkle; STEM_LABEL matches the real stem file.
4. **Additive engine decay grid (found 2026-10-12)**: `apply_overtones`
   leaves `self.frequency` at the TOP partial (~7× fundamental), so
   `get_adsr_weights`' grid interval ≈ 1/(duration×top_partial) s and all
   decay rates are PER-GRID-STEP. A 2 s pad chord needs decay_S ≈ 1e-4
   (measured late-sustain 0.79) vs 1e-3 (measured 0.25 — apparent
   "collapse" that is actually grid-density, not the 10-11 tail bug; the
   tail fix itself holds). Recipes must scale decay by ~1/freq — documented
   in instrument.md §Synthesis.
5. **No patch ceiling**: full-keyboard GM pad patches (contrast
   timpani/pizzicato at 102+). Safe to write anywhere 36–96; sweet 60–84.
6. **Pad-writing rule**: chords ≥ 2 s or the 0.4–1.0 s attack never
   speaks; velocity shapes the final swell level (LA-synth behavior), not
   the onset bite.
7. **Layering**: octave doubling or zone-splitting (55–79 + 80–96), never
   unison with a second melodic patch (comb-filter lesson 2026-09-01).
8. **Channel**: melodic channel 0–9; ch9 → drum map + `Acoustic_Grand_Piano`
   program-0 stem fallback (timpani lesson).

## 11. Files changed

- `instrument_registry.py` — module dict + SYNTH_PAD constant + table role +
  verification block (60 modules)
- `registry.md` — Registry table row, stem-label quirks row (88), dated
  changelog entry (2026-10-12)
- `Synth/synth_pad/instrument.md` — NEW
- `Synth/synth_pad/synth_pad.py` — NEW
- `_test/verify_synth_pad.py` — NEW (pattern: verify_marimba.py, SOLO render)
- Full pytest suite: re-run (693 passed baseline; see run output)

## 12. Conclusions

GM88 "Pad 1 (new age)" is now the registered **Synth** family's first
entry and the KB answer to orchestration.md's "Synth Pad" role. It is
verified end-to-end: registered, zero-drift, MIDI 75 B, FluidR3 solo WAV
1.63 MB with 8.2% high-band energy (clean), correct stems, both synthesis
recommendations smoke-tested. Next Synth-family candidates: GM89 "Pad 2
(warm)" (darker sibling — complement), GM50 Synth Strings 1, GM38 Synth
Bass 1, GM62 Synth Brass 1, then leads (80–87) and pads (90–95).