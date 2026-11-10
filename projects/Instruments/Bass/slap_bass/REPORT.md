# REPORT — Slap Bass 1 (GM36)

**Date**: 2026-11-10 · **Job**: nightly instrument research (layer-aligned)
**Files**: `Bass/slap_bass/instrument.md`, `Bass/slap_bass/slap_bass.py`,
registered in `instrument_registry.py`, documented in `registry.md`

---

## 1. Instrument identity

**Slap Bass 1 (GM36, 0-indexed)** — the thumb-slap + finger-pop FUNK/DISCO
bass voice on the electric bass guitar. **Slap** = strike the string with
the thumb so it smacks against the fretboard (bright percussive thump +
fretboard clack); **pop** = pull the string away and release so it snaps
back (harmonic-rich bright click, usually on the D/G strings).

History (Wikipedia "Slap bass", fetched 2026-11-10): on the double bass the
technique goes back to New Orleans jazz bands in the early 1900s (spread via
western swing, rockabilly); on the electric bass it is widely credited to
**Larry Graham** (Sly and the Family Stone, late 1960s — "Thank You
(Falettinme Be Mice Elf Agin)"), then funk/disco — Bootsy Collins, Verdine
White, Louis Johnson, Mark King (Level 42), Stanley Clarke, Victor Wooten,
Flea, Les Claypool.

Same instrument as Electric Bass (finger) GM33 (same body/strings/pickups,
DIFFERENT performance technique). GM37 "Slap Bass 2" (FluidR3 "Pop Bass")
is the rounder sibling patch — NOT claimed here. GM36 was collision-free:
`by_program(36)` had no owner, stem `Slap_Bass_1` unclaimed.

## 2. MIDI / GM facts

| Fact | Value |
|---|---|
| Program | 36 (0-indexed = FluidR3 preset 36 = pipeline `GM_PROGRAMS[36]`) |
| Pipeline stem label | `GM_PROGRAMS[36]` = **"Slap Bass 1"** → sanitized `Slap_Bass_1` |
| FluidR3 preset 36 | **"Slap Bass"** (phdr-verified — SF2 drops the number) |
| `MidiInstrument` enum | NOT present (10-member legacy enum) — use raw `program=36` |
| Channel | melodic 0–9 (channel 9 = drum map) |

**Stem-label quirk**: NONE routing-wise — `GM_PROGRAMS[36]` = "Slap Bass 1",
stem `track00_Slap_Bass_1.wav` (verified on disk). Cosmetic only: FluidR3
preset 36 names the technique "Slap Bass" without the number; stems are
labelled from GM_PROGRAMS so STEM_LABEL = `Slap_Bass_1` matches the real
pipeline output.

## 3. Range (empirical, FluidR3 pitch sweep)

Sweep (RMS, velocity 90, `-g 1.2`):

| Note | Name | RMS |
|---|---|---|
| 24 | C1 | 1272.1 |
| 28 | E1 | 1154.0 |
| 33 | A1 | 1110.5 |
| 36 | C2 | 1196.0 |
| 40 | E2 | 833.9 |
| 45 | A2 | 723.8 |
| 48 | C3 | 799.0 |
| 52 | E3 | 765.6 |
| 55 | G3 | 718.8 |
| 60 | C4 | 655.9 |
| 64 | E4 | 606.5 |
| 67 | G4 | 569.5 |
| 72 | C5 | 518.2 |
| 77 | F5 | 464.1 |
| 84 | C6 | 423.5 |
| **86** | **D6** | **0.99 = SILENT** |

- **Audible 15/15 from 24 to 84, no gaps**, smooth rolloff (1272 → 423).
- **Hard patch ceiling at C6 = 84** — SILENT at 86 (D6). Never write above 84.
- Patch also plays 21+ (A0/B0 sub-bass rumble below the real 4-string).

| Constants | Value |
|---|---|
| `RANGE_MIN` | 24 (C1) |
| `RANGE_MAX` | 84 (C6 — hard ceiling) |
| `SOLO_RANGE` | (36, 60) — C2–C4 |
| `SWEET_SPOT` | (33, 55) — A1–G3, the E/A/D-string thumb-slap money zone |
| `ZONES` | sub (24–35), slap_zone (36–55), pop_zone (56–72), high (73–84) |

Real instrument: 4-string E1–G4 = 28–67; 5-string adds B0 = 23.

## 4. Role

`bass, rhythm, groove, accent, ornament, lead` — bass (slap lines,
root-fifth groove, locks with the kick), rhythm (16th-note funk grooves,
octave-pop fills, ghost subdivisions), groove (syncopated offbeat pops +
muted 16ths), accent (downbeat slaps, sfz hits), ornament (hammer/pull-off
runs, double-thumb), lead (rare slap solos 56–72). **NOT** harmony/pad
(monophonic), NOT a warm fingerstyle voice (GM33), NOT sub-only.

## 5. Synthesis engine

**Karplus-Strong primary** (SP-011 — plucked waveguide = exact physical
model):

```python
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9955,     # SHORTEST in Bass family: slap ring is tight,
                             #  muting hand stops the string (0.3–1.0 s)
    "lowpass_hz": 5500.0,    # BRIGHTER than fingerstyle electric bass 5000:
                             #  the fretboard-clack top-end IS the identity
    "width": 0.4,
    "excitation": "slap",    # hard strike excitation
    "noise_component": 0.05, # fretboard clack transient
    "role": "bass",
}
```

- **PhaseModSynth secondary**: sine carrier, ratio 2.0 (pop's octave-ish
  snap sideband), depth 2.2, attack 0.003 s.
- **ModalSynth `'string'`** weak fallback.
- Smoke: Karplus E2 peak 0.290, head_rms 0.0073 → tail_rms 0.0010 (real
  decay); PhaseModSynth E2 peak 0.799.

## 6. Articulations

```python
ARTICULATIONS = {
    "slap": (92, 0.30), "pop": (96, 0.25), "finger": (74, 0.90),
    "ghost": (38, 0.15), "hammer_on": (66, 0.60), "pull_off": (66, 0.50),
    "double_thumb": (98, 0.20), "staccato": (70, 0.25), "accent": (100, 0.35),
}
```

## 7. Production defaults

```python
REVERB_TAIL = 1.2          # tight funk room/DI — dry; verb smears the 16ths
EQ_BODY = (250, -2.5)      # cut low-mid mud vs kick (thump is ~100 Hz, keep)
EQ_PRESENCE = (2800, 3.0)  # THE slap EQ move — 2–3 kHz snap/click band
EQ_AIR = (8000, 1.5)       # string clack — never low-pass a slap bass
PAN = 0.0                  # center, mono
```

## 8. Registration proof (registry run)

`/opt/data/micromamba/envs/musicom/bin/python instrument_registry.py`
(exit 0). Registry table now includes (row 6 of the table):

```
| Bass | Slap Bass 1 | 36 | 24–84 | bass, rhythm, groove, accent, ornament, lead |
```

Verification lines:

```
=== Slap Bass 1 (GM36) ===
  SLAP_BASS.midi_program = 36 (should be 36)
  by_name('slap bass') = <Instrument Slap Bass 1 (family=Bass, program=36, range=24-84)>
  by_name('slap bass 1') = <Instrument Slap Bass 1 (family=Bass, program=36, range=24-84)>
  by_program(36) = <Instrument Slap Bass 1 (family=Bass, program=36, range=24-84)>
  by_program(33) = <Instrument Electric Bass (finger) (family=Bass, program=33, range=24-84)> (distinct: electric bass finger)
  SLAP_BASS.in_sweet_spot(48) = True
  SLAP_BASS.in_sweet_spot(20) = False
  SLAP_BASS.range_min = 24 SLAP_BASS.range_max = 84
  SLAP_BASS.stem_label = 'Slap_Bass_1'
  SLAP_BASS.synthesis = 'karplus'
```

Registry edits: `_INSTRUMENT_MODULES["Bass.slap_bass.slap_bass"] =
"slap_bass"`; convenience constant `SLAP_BASS`; `registry_table()` role row;
`__main__` verification block. Full output saved at
`_test/registry_out_slap_bass.txt`.

## 9. End-to-end verification (verify_slap_bass.py)

Composition: UnitMatrixComposer, 1 bar × 1 section, 104 bpm,
2 voices — Slap Bass 1 (ch0, SOLO melodic voice) + Drum Kit (ch9, context
only). A-minor 16th-note funk groove: thumb slaps on A1/E2, offbeat pops on
A2/C3, ghost notes, terminal landmark at BAR.

| Check | Result |
|---|---|
| Zero-drift (`validate()`) | **True (OK)** |
| MIDI | `_test/slap_bass_test.mid` — **247 bytes** (> 40 ✓) |
| WAV (solo render, voice 0 only) | `_test/slap_bass_test.wav` — **795,948 bytes** (> 40 ✓) |
| Spectral 4–8 kHz buzz | **3.5%** (gate 20% — clean single voice, no comb-filtering) |
| Stem label (pipeline GM_PROGRAMS) | `GM_PROGRAMS[36]` = `'Slap Bass 1'` ✓ |
| SF2 preset (phdr) | preset 36 = `'Slap Bass'` (cosmetic vs "Slap Bass 1") |
| Stems on disk | `track00_Slap_Bass_1.wav` (795,948 B) + `track01_Drums.wav` (760,364 B) ✓ |
| Karplus smoke | E2 peak 0.290, head 0.0073 → tail 0.0010 (real decay) |
| PhaseMod smoke | E2 peak 0.799 |
| Pitch sweep | 15/15 audible 24–84, SILENT at 86 (ceiling proof) |

SoundFont resolved via `from sound.render.fluidsynth import
discover_soundfont()` → FluidR3_GM.sf2 (preferred; NOT hardcoded).

## 10. Quirks found

1. **Patch ceiling**: FluidR3 preset 36 plays through C6=84 and is
   SILENT at D6=86 — the documented RANGE_MAX is 84 and composition jobs
   must never write above it (pizzicato_strings/timpani-style ceiling
   lesson).
2. **SF2 name cosmetic**: preset 36 = "Slap Bass" vs pipeline "Slap Bass
   1" — stems are labelled from GM_PROGRAMS so `trackXX_Slap_Bass_1.wav`
   is correct; STEM_LABEL matches the pipeline.
3. **Monophonic**: one note at a time — no chords (slap/pop is a
   single-note technique).
4. **Velocity is the articulation map**: slap 85–105 / pop 90–110 / ghost
   30–50 / accent 95–110; the transient runs 20–30 dB hotter than the
   ring → compress in production (mix decision, not baked into defaults).
5. **No unison doubling** with another melodic patch on the same pitches
   (2026-09-01 comb-filter rule) — drums + a low bass note an octave+
   below are fine.
6. **MidiInstrument enum**: no slap-bass constant (10-member legacy enum)
   — raw 36 is the registry's full-KB value.

## 11. Selection note

GM36 was one of the three named "remaining sibling candidates" from the
2026-11-07/2026-11-09 changelog entries (GM31 "Guitar harmonics", GM49
"String Ensemble 2", GM36 "Slap Bass 1"). Collision-free: `by_program(36)`
had no owner; stem `Slap_Bass_1` unclaimed. Drive-by fix: registry.md
Registry table gained the missing **Synth Bass 2 | 39** row.
Remaining candidates now: GM31 "Guitar harmonics", GM49 "String Ensemble
2", GM63 "Synth Brass 2".
