# REPORT — Electric Bass (pick) (GM34)

**Date**: 2026-11-14 · **Job**: nightly instrument research (layer-aligned)
**Files**: `Bass/pick_bass/instrument.md`, `Bass/pick_bass/pick_bass.py`,
registered in `instrument_registry.py`, documented in `registry.md`
**Verify**: `_test/verify_pick_bass.py` → `_test/verify_pick_bass_out.txt`
**Artifacts**: `_test/pick_bass_test.mid`, `_test/pick_bass_test.wav`,
`_test/stems_pick_bass/`

---

## 1. Instrument identity

**Electric Bass (pick) (GM34, 0-indexed)** — the PLECTRUM voice of the
solidbody electric bass guitar. Same instrument as GM33 Electric Bass
(finger): same body, strings and magnetic pickups; the difference is the
right-hand tool. A hard plastic/nylon pick strikes the string at a sharper
angle with a stiffer contact than a fingertip, producing:

- a bright broadband **click** at the attack (the identity),
- a leaner fundamental and a brighter partial balance,
- more even note-to-note dynamics (a pick has no flesh cushion),
- **palm muting as a first-class articulation** (heel of hand on the saddles).

Canonical players: Chris Squire (Yes — Rickenbacker + pick), Paul McCartney
(post-1966), Carol Kaye (felt pick), Dee Dee Ramone, Mike Dirnt (Green Day),
Peter Hook (Joy Division / New Order — the melodic high-register pick-bass
hook), Justin Chancellor (Tool), Lemmy (pick + distortion), Kim Deal,
Krist Novoselic.

**Selection note**: GM34 was collision-free — `by_program(34)` raised
KeyError before this entry, `Electric_Bass_pick` stem label unclaimed. The
Bass family previously had finger (33), acoustic/upright (32), fretless (35),
slap (36), and two synth basses (38/39) but **no picked electric bass**, a
gap in every rock/punk/metal/new-wave composition job. GM37 "Slap Bass 2"
(FluidR3 "Pop Bass") remains the unclaimed sibling.

## 2. MIDI / GM facts

| Fact | Value |
|---|---|
| Program | 34 (0-indexed = FluidR3 preset 34 = `GM_PROGRAMS[34]`) |
| Pipeline stem label | `GM_PROGRAMS[34]` = **"Electric Bass (pick)"** → sanitized `Electric_Bass_pick` |
| FluidR3 preset 34 | **"Picked Bass"** (phdr-verified) |
| `MidiInstrument` enum | NOT present (10-member legacy enum) — use raw `program=34` |
| Channel | melodic 0–9 (channel 9 = drum map) |
| Transposition | none — written pitch = sounding pitch (fundamental measured 82.1 Hz for written E2 = 82.4 Hz) |

**Stem-label quirk**: routing-wise NONE. `GM_PROGRAMS[34]` = "Electric Bass
(pick)"; the sanitizer strips the parens and keeps the inner word →
`track00_Electric_Bass_pick.wav` (verified on disk). Cosmetic only: FluidR3
preset 34 is named "Picked Bass".

## 3. Range (empirical, FluidR3 pitch sweep)

Sweep: single note per file, velocity 90, `-g 1.2`, RMS over 0–0.4 s.

| Note | Name | RMS (×1000) |
|---|---|---|
| 21 | A0 | 91.8 |
| 24 | C1 | 91.6 |
| 30 | F#1 | 98.6 |
| 36 | C2 | 97.0 |
| 42 | F#2 | 92.8 |
| 48 | C3 | 99.0 |
| 54 | F#3 | 98.2 |
| 60 | C4 | 95.3 |
| 66 | F#4 | 92.1 |
| 72 | C5 | 87.3 |
| 78 | F#5 | 81.1 |
| 84 | C6 | 74.5 |
| 87 | D#6 | **0.0 — silent** |
| 90–108 | — | **0.0 — silent** |

Patch span = **21–84 (A0–C6)**, essentially FLAT in RMS (0.067–0.099) with a
gentle treble rolloff and a HARD ceiling: nothing above 84. Real 4-string
bass (E1–G4, 20/22 frets) = 28–67.

Zones: sub 21–35 (felt > heard), groove 36–50 (primary pick 8ths/16ths +
palm-mute chug), mid 51–64 (pick-bass hooks, D/G-string cut-through), high
65–84 (accents, exposed fills; thin). Sweet spot 40–55 (E2–G3), solo range
36–57 (C2–A3).

## 4. Role

`bass, rhythm, groove, countermelody, accent` — the driving rock/punk/metal
and new-wave bass attack. Primary bass (root-fifth 8ths/16ths, pedal tones),
rhythm (palm-muted chug patterns, alternate-picked engines), groove
(post-punk/new-wave melodic grooves, ska/reggae pick lines), countermelody
(the high-register Hook-style hook answering the vocal an octave below),
accent (downstroke digs, pick scrapes, mute stops). NOT a lead voice, NOT a
harmony/pad voice (monophonic), NOT a high-register sustain voice.

Registry table row:
`| Bass | Electric Bass (pick) | 34 | 21–84 | bass, rhythm, groove, countermelody, accent |`

## 5. Synthesis engine

**Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) — primary.
Plucked waveguide is the exact physical model; the pick is the excitation.

```python
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9965,   # shorter ring than finger 0.9970, longer than slap 0.9955
    "lowpass_hz": 5600.0,  # brighter than finger 5000 — the pick click band
    "width": 0.5,
    "excitation": "pick",  # stiff plectrum burst
    "role": "bass",
}
```

Damping ladder confirmed by measurement (tail 1–2 s, note E2):
harp 0.9985 > acoustic 0.9975 > finger 0.9970 > **pick 0.9965 (0.00219)** >
slap 0.9955; pick is **0.94× the finger tail** and **2.1× the 0.990 dull
control** — shorter than the finger patch, as intended, and still clearly
ringing.

Fallbacks: **ModalSynth** `MODAL_PRESET = "string"` (no pickup colour, no
click); **PhaseModSynth** saw carrier, ratio 1.0, depth 2.4, attack 3 ms
(chiptune/synthwave bed only, not idiomatic).

## 6. Articulations

| Technique | Velocity | Duration factor |
|---|---|---|
| pick (default) | 84 | 0.90 |
| alt_pick | 80 | 0.85 |
| downstroke | 92 | 0.80 |
| palm_mute | 48 | 0.25 |
| staccato | 86 | 0.30 |
| ghost | 36 | 0.18 |
| slide | 64 | 1.05 |
| accent | 96 | 0.75 |

## 7. Production defaults

- `REVERB_TAIL = 1.2` s (drier than finger 1.4 — DI/close-mic, click upfront)
- `EQ_BODY = (200, -2.5)` (low-mid box cut; lower/deeper than finger's 250 Hz)
- `EQ_PRESENCE = (1200, 3.0)` (the pick click band; above finger's 800 Hz growl)
- `EQ_AIR = (6000, 2.0)` (plectrum scrape + roundwound sizzle)
- `PAN = 0.0` (centre — bass is mixed mono in every idiom)

## 8. Constants (full)

```python
MIDI_PROGRAM = 34
GM_NAME = "Electric Bass (pick)"
STEM_LABEL = "Electric_Bass_pick"
RANGE_MIN, RANGE_MAX = 21, 84
SOLO_RANGE = (36, 57)
SWEET_SPOT = (40, 55)
ZONES = {"sub": (21, 35), "groove": (36, 50), "mid": (51, 64), "high": (65, 84)}
SYNTHESIS = "karplus"
MODAL_PRESET = "string"
FM_DEFAULTS = {"carrier_shape": "saw", "mod_freq_ratio": 1.0, "mod_depth": 2.4,
               "attack": 0.003, "release": 0.20}
REVERB_TAIL = 1.2
EQ_BODY = (200, -2.5)
EQ_PRESENCE = (1200, 3.0)
EQ_AIR = (6000, 2.0)
PAN = 0.0
```

## 9. Registration proof (`instrument_registry.py` run)

Full run: `_test/registry_out_pick_bass.txt` (exit 0, 93 instruments loaded).

```
| Bass | Electric Bass (pick) | 34 | 21–84 | bass, rhythm, groove, countermelody, accent |
```

```
=== Electric Bass (pick) (GM34) ===
  PICK_BASS.midi_program = 34 (should be 34)
  by_name('electric bass (pick)') = <Instrument Electric Bass (pick) (family=Bass, program=34, range=21-84)>
  by_name('pick bass') = <Instrument Electric Bass (pick) (family=Bass, program=34, range=21-84)>
  by_program(34) = <Instrument Electric Bass (pick) (family=Bass, program=34, range=21-84)>
  by_program(33) = <Instrument Electric Bass (finger) (family=Bass, program=33, range=24-84)> (distinct: electric bass finger)
  PICK_BASS.in_sweet_spot(45) = True
  PICK_BASS.in_sweet_spot(90) = False
  PICK_BASS.range_min = 21 PICK_BASS.range_max = 84
  PICK_BASS.stem_label = 'Electric_Bass_pick'
  PICK_BASS.synthesis = 'karplus'
  PICK_BASS.karplus_defaults = {'loop_gain': 0.9965, 'lowpass_hz': 5600.0, 'width': 0.5, 'excitation': 'pick', 'role': 'bass'}
```

Registered: `_INSTRUMENT_MODULES["Bass.pick_bass.pick_bass"] = "pick_bass"`,
constant `PICK_BASS`, `registry_table()` role branch for
"electric bass (pick)", verification block in `__main__`.

## 10. End-to-end verification (`verify_pick_bass.py`)

```
registry: <Instrument Electric Bass (pick) (family=Bass, program=34, range=21-84)>
Zero-drift: True (OK)
MIDI: _test/pick_bass_test.mid (219 bytes)
soundfont: .../FluidR3_GM.sf2
WAV (solo): _test/pick_bass_test.wav (741676 bytes)
Spectral check: 4-8kHz buzz energy = 0.2% (OK)
Written 40 (82.4 Hz) rendered fundamental peak 82.1 Hz (ratio 1.00x — NON-transposing)
note 40: centroid finger(GM33)=   593 Hz pick(GM34)=   796 Hz (+  34%)
note 45: centroid finger(GM33)=   697 Hz pick(GM34)=  1309 Hz (+  88%)
note 50: centroid finger(GM33)=   738 Hz pick(GM34)=  1119 Hz (+  52%)
Karplus loop_gain=0.9965: peak=0.290 tail(1-2s)=0.00219 vs 0.990 dull 0.00104 (2.1x)
                          and vs finger 0.9970 0.00232 (0.94x — SHORTER, as intended)
Stem label: GM_PROGRAMS[34] = 'Electric Bass (pick)' -> file 'Electric_Bass_pick'
SF2 preset 34 -> 'Picked Bass'
Stems (2):
  track00_Electric_Bass_pick.wav (741676 bytes)
  track01_Drums.wav (787756 bytes)
ALL CHECKS PASSED
```

Audio check rendered the instrument **SOLO** (one melodic voice, one track);
the drum track exists only in the MIDI for context and zero-drift, never in
the solo WAV. No unison doubling anywhere.

## 11. Quirks found

1. **Patch attack is SOFT (sample-level quirk)**: FluidR3 "Picked Bass"
   reaches ~90% of peak at 50–80 ms, whereas the fingered patch (GM33) gets
   there at ~30 ms. A real plectrum transient is 3–5 ms — the SF2 sample has
   a softer edge than the physics. Consequence: write staccato / palm-mute
   notes ≥ 100 ms or the patch never speaks; do not expect a click at 5 ms.
2. **Hard treble ceiling**: patch is SILENT from MIDI 87 up (sweep 21–84
   audible, 87+ = 0.000 RMS). RANGE_MAX 84 is a measured limit, not a
   convention. Do not write melodic pick-bass lines above C6.
3. **Third partial rivals the fundamental** on low notes (E2: fundamental
   82.1 Hz amplitude 1.00, 3rd partial 125 Hz = 0.835) — that IS the pick
   brightness, but it breaks naive pitch checks: use a band-limited peak
   search (±10% of f0), not the global FFT argmax (which lands on the 3rd
   partial in short windows). The verify script documents this.
4. **Patch-name mismatch (cosmetic)**: GM_PROGRAMS[34] = "Electric Bass
   (pick)"; FluidR3 preset 34 = "Picked Bass". No routing impact; STEM_LABEL
   follows the pipeline label.
5. **Not in `MidiInstrument`** (legacy enum has 10) — use raw `program=34`.
6. **Same-pitch doubling rule**: do NOT layer the pick bass with the finger
   bass (or any second melodic patch) on the same pitches — identical
   fundamentals = comb filtering. Different octaves are fine.

## 12. Follow-up candidates

GM37 "Slap Bass 2" (FluidR3 "Pop Bass"), GM50/51 Synth Strings 1/2, GM63
Synth Brass 2, GM17/18 Percussive/Rock Organ, GM2 Bright Acoustic Piano,
GM115 Woodblock, GM112 Tinkle Bell.
