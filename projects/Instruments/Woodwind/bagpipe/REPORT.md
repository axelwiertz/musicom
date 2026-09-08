# REPORT — Bagpipe added to musicom Instruments (2026-09-08)

Nightly instrument-research job, layer-aligned run.

## Instrument

| Field | Value |
|---|---|
| Name | **Bagpipe** |
| Family | Woodwind (6th entry: flute, clarinet, oboe, bassoon, saxophone, bagpipe) |
| GM program | **109** (GM2 Bagpipe) — raw 0-indexed number, NOT in MidiInstrument enum |
| GM name | "Bagpipe" |
| Stem label | **"Bag_pipe"** → `trackXX_Bag_pipe.wav` (**QUIRK** — see below) |
| Identity | GM109 = **Great Highland Bagpipe**: sustained double-reed chanter over a constant drone |
| Files | `Woodwind/bagpipe/instrument.md`, `Woodwind/bagpipe/bagpipe.py`, `_test/verify_bagpipe.py`, `_test/sweep_bagpipe.py` |

**Why this pick**: World-family run completed (sitar→koto→shamisen→kalimba→
banjo, GM104–108, 2026-09-06). GM109 Bagpipe is the first remaining ethnic
sustained-reed entry with a proper FluidR3 preset ("BagPipe" at bank0/pgm109)
— a NEW voice type for the library: the only sustained-drone reed instrument,
and the first instrument where the RenderPipeline GM label differs from the
GM/SF2 name (stem-label quirk class #3, alongside GM74→"Recorder").

## Range / Role

- Full range 53–96 (F3–C7): the GM-patch span FluidR3 renders — empirical
  RMS sweep 8/8 notes audible (53/57/62/66/69/74/84/96, all RMS ≥ 0.075), no
  gaps, the SF2 never clips a composition.
- Real chanter register 57–69 (A3–A4): the physical Great Highland chanter is
  **9 notes**, mixolydian on D (A B C# D E F# G A — no C/F naturals). This is
  the most range-limited melodic instrument in the library.
- Sweet spot 62–74 (D4–D5); zones: drone 53–56 (pedal/growl only) /
  chanter 57–69 (melody) / high 70–96 (GM extension, whistle-y).
- Role: lead, melody, ornament, drone, accent — line instrument: modal melody
  over a pedal, NO dense harmony (monophonic chanter).

## Synthesis

- **SYNTHESIS = "phase_mod"** (PhaseModSynth, `sound/synthesis/phase_mod.py`)
  — sustained double reed = self-sustained oscillator driven by airflow.
  FM_DEFAULTS: saw carrier (even+odd harmonics), mod_freq_ratio 1.0,
  **mod_depth 4.5** (highest of the woodwind set: oboe 2.5, sax 2.8,
  clarinet 2.0 — the bagpipe's piercing reed wall), attack 0.03 s (reeds
  already blown by bag pressure — NO breath transient), release 0.15 s.
- ModalSynth preset 'string' fallback (slow-decay harmonic stack, crude
  continuous tone; no native chanter+drone two-part model in musicom).
- NOT Karplus/BowedString/DrumMachine — wrong physics for a sustained reed.

## Constants (bagpipe.py, loaded through registry)

```
MIDI_PROGRAM=109  GM_NAME="Bagpipe"  STEM_LABEL="Bag_pipe"
RANGE_MIN=53  RANGE_MAX=96  SOLO_RANGE=(57,69)  SWEET_SPOT=(62,74)
ZONES      = drone(53-56) chanter(57-69) high(70-96)
ARTICULATIONS = sustain(74,1.0) skirl(94,0.35) gracenote(88,0.15) crisp(80,0.5) accent(92,1.0)
SYNTHESIS  = "phase_mod"  MODAL_PRESET="string"
FM_DEFAULTS  = {saw carrier, ratio 1.0, depth 4.5, attack 0.03, release 0.15}
REVERB_TAIL=2.4s  EQ_BODY=(450,-3.0)  EQ_PRESENCE=(2500,3.0)  EQ_AIR=(7000,1.5)  PAN=0.0
```

## Registration proof (instrument_registry.py run)

Registry count 24→**25**; new row in `registry_table()`:

```
| Woodwind | Bagpipe | 109 | 53–96 | lead, melody, ornament, drone, accent |
```

Verification lines (real run):

```
BAGPIPE.midi_program = 109 (should be 109)
by_name('bagpipe') = <Instrument Bagpipe (family=Woodwind, program=109, range=53-96)>
by_program(109) = <Instrument Bagpipe (family=Woodwind, program=109, range=53-96)>
BAGPIPE.in_sweet_spot(62) = True
```

`instrument_registry.py` edits: `_INSTRUMENT_MODULES["Woodwind.bagpipe.bagpipe"]`,
`BAGPIPE` convenience constant, role mapping + verification prints.
`registry.md` edits: changelog entry (2026-09-08), Registry table row, stem
quirks table row for GM109.

## Verification results (real run, `_test/verify_bagpipe.py`)

| Check | Result |
|---|---|
| Registry import (`by_name("bagpipe")`, `by_program(109)`) | ✓ |
| UnitMatrixComposer 1 bar / 1 section (Bagpipe solo ch0 + context bass drone ch1 GM33, A1 — 2 octaves+ below) | ✓ built |
| Zero-drift `validate()` | **True (OK)** |
| MIDI export `bagpipe_test.mid` | **144 bytes** (> 40 ✓) |
| Solo WAV render (FluidR3 via `discover_soundfont()`, Bagpipe solo track 0 — NO unison doubling) | `bagpipe_test.wav` **794,668 bytes** |
| Spectral buzz check (4–8 kHz band) | **2.4%** (OK — no comb-filtering; the bagpipe's own reed brightness is expected) |
| Stem label `GM_PROGRAMS[109]` | **'Bag pipe'** (two words — QUIRK) → `trackXX_Bag_pipe.wav` |
| SF2 preset 109 (phdr) | FluidR3 `BagPipe` ✓ |
| Full RenderPipeline stem render | `track00_Bag_pipe.wav` (794,668 B) + `track01_Electric_Bass_finger.wav` ✓ |
| PhaseModSynth sustain smoke (saw, depth 4.5, note D4=62) | peak 0.775, late-window (0.5–0.7 s) rms/peak **0.464** — sustained reed, NO collapse ✓ |
| Empirical FluidR3 pitch sweep (RMS, notes 53–96) | 8/8 notes audible (RMS 0.075–0.113) — no gaps ✓ |
| ALL CHECKS PASSED | ✓ |

FluidSynth command (per pitfall spec): `/opt/data/micromamba/envs/musicom/bin/fluidsynth -ni -g 1.2 -F <wav> <sf2> <mid>` — via `_test/render_audio.py` `render_midi(midi_path, wav, solo=0)` which resolves the SoundFont through `discover_soundfont()`.

## Quirks found

1. **STEM-LABEL QUIRK (new class #3)**: `GM_PROGRAMS[109]` = **"Bag pipe"**
   (two words) — the actual RenderPipeline stem file is
   `trackXX_Bag_pipe.wav`, NOT `trackXX_Bagpipe.wav`. GM_NAME is "Bagpipe"
   and FluidR3 preset 109 is "BagPipe". STEM_LABEL is therefore set to
   `"Bag_pipe"` (the sanitized ACTUAL pipeline label) so stem-file matching
   works — same discipline as flute's "Recorder" and sax's "Alto_Sax", but
   the FIRST case where the difference is whitespace, not a synonym. Any
   code matching stems on GM_NAME ("Bagpipe") will miss.
2. **Identity quirk (documented, not a label quirk)**: GM109 is the Great
   Highland Bagpipe — the real chanter is only 9 notes (A3–A4, mixolydian on
   D). Composition jobs must write modal/scale lines (no C or F naturals in
   the core register) and NO dense harmony. Range 53–96 is the GM-patch
   span, not the physical instrument.
3. **Not in MidiInstrument enum** (only 10 exposed) — used raw 109; registry
   is the full KB.
4. **Channel**: melodic channel 0–9; ch9 would hit the program-0 fallback
   "Acoustic_Grand_Piano" stem-label trap.
5. **No native drone model**: musicom synthesis has no chanter+drone two-part
   physical model. PhaseModSynth renders the chanter tone; a composition
   wanting the true GHB sound should layer a held low drone under the modal
   line, or use FluidSynth preset 109 (the sample already contains the
   drone).
