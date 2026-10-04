# Musicom 1.0.0 — composition + production + analysis

[![Python 3.11+](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/axelwiertz/musicom)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/axelwiertz/musicom)
[![Tests](https://img.shields.io/badge/tests-688%20passing-brightgreen.svg)](tests/)

**Musicom** is an educational framework for **AI-assisted music composition
and production with full control of every step**. It exists to teach — and to
let you (or an AI agent) practice — how music is actually built: from an
abstract harmony plan, to concrete note-by-note realization, to the absolute
audio you finally hear. No black boxes: every stage is explicit, inspectable,
and replaceable, so you always know *why* a piece sounds the way it does.

Algorithmic composition is treated as a series of transparent transformations
on organized data structures — never as a black-box prompt-to-audio model.

---

## Why Musicom — full control, every step

Most AI music tools hide the pipeline behind a single generation call. Musicom
takes the opposite approach: **each step is a deliberate, auditable
transformation you can inspect, modify, or swap out**:

| Stage | What you control | Where |
|---|---|---|
| **Plan the harmony** | pc-sets, subset walks, tension curves, form | `rules/subset_network.py` |
| **Choose the method** | 100+ catalogued methods, each documented with its layer, paradigm, complexity | `projects/Research/CompositionMethods/methods_db.md` |
| **Realize the notes** | voices × sections UnitMatrix, grid lock, chord quantize, voice-leading | `workflows/unitmatrix_composer.py`, `rules/voice_leading.py` |
| **Assign instruments** | 18-instrument registry (ranges, articulations, synthesis presets) | `projects/Instruments/` |
| **Produce the sound** | 12+ production methods (SoundFont render, Karplus-Strong, physical modeling, …) | `sound/`, `workflows/musicom_workflow.py` |
| **Verify the result** | zero-drift gate, grid/harmony audits, silence/RMS stats, provenance sidecars | `projects/Research/preflight_check.py`, per-project `audit.py` |

Every artifact carries a `provenance.json` sidecar (classification, generator,
parameters, timestamp) — so a piece can always be traced back to the exact
method, seed, and chain that produced it.

## The three layers

Musicom organizes all composition knowledge into **three layers**. Each layer
has its own methods, its own invariant, and its own code home. A composition
flows *abstract → concrete → absolute* — and you can intervene at every hop.

```
┌──────────────────────────────────────────────────────────────────┐
│  ABSTRACT   composition plan — stays pitch/register-invariant    │
│             pc-set subsets · tension curves · pattern network    │
│             z-relations · P/L/R moves · form/tension plans       │
│             code: rules/subset_network.py, ABS-* methods         │
└──────────────────────────┬───────────────────────────────────────┘
                           ▼  realization
┌──────────────────────────────────────────────────────────────────┐
│  CONCRETE   realization plan — voices × sections UnitMatrix      │
│             resolved MusicEvents (pitch, onset, dur, velocity)   │
│             grid lock · chord-tone quantize · voice leading      │
│             code: generators/*, workflows/*, rules/*, SCALE L1–L4│
└──────────────────────────┬───────────────────────────────────────┘
                           ▼  production
┌──────────────────────────────────────────────────────────────────┐
│  ABSOLUTE   sound production — audio signal                      │
│             stems → WAV → OGG; SP-* production methods           │
│             code: sound/synthesis/*, sound/effects/*,            │
│                   sound/render/* (SP_METHODS registry)           │
└──────────────────────────────────────────────────────────────────┘
```

### Method layers at a glance

Every method in the DB carries a **Layer** tag. Current catalog (2026-09-08):

| Layer | DB | Count | Examples |
|---|---|---|---|
| **Abstract** | `ABS-001…005` | 5 | Subset Walker, Tension Curve Planner, Z-Variation, Parsimonious Voice Leading |
| **Concrete** | `001…081` | 95 rows | Markov transitions, Euclidean groove locking, genetic selection, FHN spiking |
| **Human (→ concrete)** | `HC-001…029` | 29 | Flamenco compás, Ewe cross-rhythm, raga-tala, species counterpoint |
| **Absolute (sound)** | `SP-001…SP-096+` | 71 | FluidSynth render, Karplus-Strong, modal/physical modeling, granular, FM |
| — implemented in engine | `SCALE` registry | 14 concrete + 12 SP | routable right now via selector/produce() |

The catalog is **living research**: nightly jobs research one new method per
day (composition, sound-production, human-comp), classify its layer, write a
full report, and a weekly job promotes implemented methods into code registries
(`workflows/paths.py` SCALE + `SP_METHODS`). See
[Projects & Research](#projects--the-living-research-tree).

### The composition pipeline in one call (and underneath)

```python
from workflows.musicom_workflow import compose, produce

# DESIGN: framework + note material, validated, zero-drift guaranteed
r = compose(style="pop", key="C", bpm=120)
# r.midi_path, r.provenance_path

# REALIZATION → ABSOLUTE: two production methods on the same MIDI
p1 = produce(r.midi_path, method="SP-001")   # FluidSynth SoundFont → WAV + OGG
p2 = produce(r.midi_path, method="SP-011")   # Karplus-Strong plucked strings
```

`compose()` fills a real I–V–vi–IV framework across intro/verse/chorus/bridge/
outro from a style template; `produce()` dispatches SP methods to the shared
`sound/` modules. For full control drop to the low-level composer (next
section) — every intermediate value is yours.

### Reverse — analyze a MIDI back into its plan

```python
from workflows.analyze import analyze_midi

rep = analyze_midi("out.mid")           # headless, mido READ-only
rep.key                                # "C"
rep.mode                               # "major"
rep.roman_progression                  # ["I", "V", "vi", "IV", ...]
rep.forte_names                        # ["3-11", ...]
print(rep.grid)                        # █/░ high-contrast timeline
```

Forward and reverse are symmetric — `MIDI/audio → UnitMatrix → key/chords/sets/grid`
mirrors `plan → UnitMatrix → MIDI/audio`. Folder layout lives in
**[REPO_MAP.md](REPO_MAP.md)**.

---

## Features

### 🎼 Core Music Theory
- **12-TET** pitch-class system (`structures/pitchclass`)
- Chromatic pitch management with helix representation
- Diatonic patterns: scales, all 7 modes, triads/seventh/extended chords
- Serial transformations: Prime, Inversion, Retrograde, Retrograde-Inversion

### 🎵 Musical Structures
- **MusicEvent** — absolute ticks (pitch, volume, start, end)
- **MusicUnit** — numpy-backed event sequences; transpose/retrograde/invert
- **UnitMatrix** — voices × sections grid; **zero-drift invariant** (all rows
  equal length, gate-checked before every export)
- **MusicVoice / MusicSection / MusicProject** — organizational layers

### 🎹 Harmony & Rules
- Scale degrees, chord degrees, harmonic functions (T/D/S)
- **Counterpoint** + **voice-leading rules** (parallel/hidden 5ths & 8ves) with
  automated check-and-fix
- **Set theory kernel** — normal form, prime form, interval vector
  (`rules/set_theory.py`)
- **Subset network** — Forte-style pattern graph with Tn/I/Z/complement/P-L-R
  relations + tension-steered walks (the abstract-layer engine)

### 🥁 Rhythm
- Quantized time grids, euclidean (Bjorklund) rhythms, clave/tresillo patterns
- Hierarchical metrical structure with beat-depth analysis
- **16th-grid lock** discipline for phase-2 arrangement (078-rule)

### 🤖 Algorithmic Generation (`generators/`)
PatternGenerator, MarkovChainGenerator, GeneticGenerator, HarmonicsGenerator,
StochasticGenerator, RhythmGenerator, ChordDegreeGenerator — all emitting
`MusicUnit` and combinable with `rules/voice_leading`.

### 🔄 Transformations
Canon, serial transforms, matrix transpose/rotation, neighbor/passing-tone
splitting, modulation.

### 🔊 Sound Synthesis & Production (`sound/` — the Absolute layer)
77 modules across synthesis / effects / generators / modular / render / tuning:
- Physical modeling (modal ResonatorBank, bowed string, mass-spring)
- Granular, phase-mod/FM, formant, additive, west-coast wavefolding
- Reverb (algorithmic, FDN), filters (SVF/biquad), mastering
  (LUFS/DynamicEQ/StereoImager/Limiter)
- **RenderPipeline** — FluidSynth full-mix + per-track stems, resolved through
  the ONE-ENV contract (`utilities/env.py` — `$MUSICOM_FLUIDSYNTH`)
- DAW clock bridge (MIDI clock 24 PPQN)

### 📊 Visualization & Analysis
Density grid (█/░ per-voice timeline), helix/cycle pitch space, music21/musicpy
score analysis, key/chord/roman-numeral detection, provenance sidecars.

### 📁 File I/O
MIDI read/audit (mido) + validated export (engine only), MusicXML, audio
WAV/OGG via ffmpeg, Music21 ↔ MusicPy conversion.

---

## Installation

### One-env contract

Musicom standardizes on a single micromamba environment. All binaries
(fluidsynth, ffmpeg) and paths resolve through `utilities/env.py` + env vars:

```bash
export MUSICOM_ROOT=/path/to/musicom            # repo root
export MUSICOM_PYTHON=$MUSICOM_ENV/bin/python   # the only python to use
export MUSICOM_FLUIDSYNTH=$MUSICOM_ENV/bin/fluidsynth
export MUSICOM_SOUNDFONT=.../FluidR3_GM.sf2
export PATH="$MUSICOM_ENV/bin:$PATH"            # bare `fluidsynth` works
```

### Reproducible setup

```bash
git clone https://github.com/axelwiertz/musicom.git
cd musicom
micromamba create -f environment.yml          # or: conda env create -f
pip install -e ".[dev]"
bash scripts/setup_env.sh --check             # verify env + binaries + imports
```

`environment.yml` (toolchain) + `requirements.lock` (full pin set) are
committed, so the environment is reproducible byte-for-byte.

### Install dependencies only

```bash
pip install numpy mido scipy music21 networkx pandas matplotlib
```

> **Flat layout note:** top-level dirs (`structures/`, `workflows/`,
> `generators/`, `sound/`, …) *are* the importable packages. Imports are
> cwd-independent after the editable install. `import musicom` as a namespace
> is an alias only — do not rely on it.

---

## Project structure

```
musicom/
├── structures/            # MusicEvent / MusicUnit / UnitMatrix core
├── workflows/             # composers, selector, paths (SCALE), provenance
├── generators/            # algorithmic generators + generator_registry
├── rules/                 # harmony, voice_leading, subset_network, set_theory
├── sound/                 # 77-module synthesis/effects/render stack (Absolute layer)
├── transformers/          # canon, serial, matrix transformations
├── visualization/         # density grids, helix, cycle
├── utilities/             # env.py (ONE-ENV contract), config, helpers
├── analysis/              # music21/musicpy analysis tools
├── converters/            # MIDI/MusicXML/musicpy converters
├── examples/              # runnable example scripts
├── docs/                  # generated indexes: methods.md, human-methods.md, instruments.md
├── hermes_agent/          # agent operational knowledge (surveillance, registries, decisions)
├── projects/              # THE living research + composition tree (git-tracked)
│   ├── Styles/            #   genre-organized compositions (MIDI + OGG + Analysis per project)
│   ├── Research/          #   methods DBs (methods_db.md, human_methods_db.md), reports
│   ├── Instruments/       #   18-instrument registry (instrument_registry.py)
│   ├── Production/        #   nightly SP-method productions
│   └── Legacy/            #   archived pre-restructure projects (read-only)
├── tests/                 # 688 tests incl. zero-drift golden MIDI harness
├── environment.yml        # env spec (micromamba/conda)
├── requirements.lock      # full pip freeze
├── scripts/setup_env.sh   # idempotent env setup + verification
└── AGENTS.md              # machine-facing operating guide (AI agents: read this)
```

**One tree, one repo** (2026-09-08 restructure): the composition/research
working tree lives *inside* this repo under `projects/`, git-tracked and
auto-pushed nightly. `/opt/data/projects/{Styles,Research,Instruments}` on the
Hermes host are symlinks into it — a single source of truth with no
copy-mirroring drift.

---

## Quick start

All snippets below are executed verbatim by the doc-verification script and pass.

### 1. MusicEvent & MusicUnit

```python
from structures import MusicUnit, MusicEvent

# MusicEvent uses ABSOLUTE ticks: (pitch, volume, start_tick, end_tick)
events = [
    MusicEvent(pitch=60, volume=100, start_tick=0,   end_tick=480),   # C4
    MusicEvent(pitch=62, volume=100, start_tick=480, end_tick=960),   # D4
    MusicEvent(pitch=64, volume=100, start_tick=960, end_tick=1440),  # E4
]
melody = MusicUnit(events=events)

melody.pitches        # [60, 62, 64]
melody.len_ticks()    # 1440

melody.transpose(12)  # up an octave
melody.retrograde()   # reverse event order
melody.invert(60)     # mirror around a pivot
```

### 2. UnitMatrix

```python
from structures import UnitMatrix

matrix = UnitMatrix(shape=(2, 2))   # 2 voices (rows) x 2 sections (cols)
matrix.set_unit((0, 0), melody)
matrix.validate_timing()            # True when all rows share equal length
```

### 3. UnitMatrixComposer — zero-drift workflow

```python
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit,
)
from structures import MidiInstrument

composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
composer.create_matrix(num_voices=2, num_sections=1)
composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
composer.add_voice("Bass", program=MidiInstrument.BASS,  channel=1)
composer.add_section("A", bars=1)

BAR = 480 * 4
composer.fill_voice_section("Lead", "A", create_note_unit(pitch=72, duration_ticks=BAR))
composer.fill_voice_section("Bass", "A", create_note_unit(pitch=36, duration_ticks=BAR))

ok, msg = composer.validate()       # (True, "OK") — zero-drift gate
composer.to_midi("composition.mid")
```

**Canonical order:** `create_matrix()` → `add_voice()` → `add_section()` →
`set_unit()` / `fill_voice_section()` → `validate()` → `to_midi()`.
Tempo meta goes in track 0; percussion on channel 9.

### 4. Render to audio

```bash
fluidsynth -ni -g 1.2 -F out.wav "$MUSICOM_SOUNDFONT" composition.mid
ffmpeg -y -i out.wav -codec:a libopus -b:a 48k out.ogg
```

SoundFont preference is auto-resolved by
`from sound.render.fluidsynth import discover_soundfont` — FluidR3_GM
(141 MB, proper woodwind/brass/strings) preferred; TimGM6mb is a thin
fallback only. Never hardcode the soundfont path.

---

## Key concepts

### MusicEvent
Single event: **pitch** (0–127), **volume** (0–127), **start_tick**,
**end_tick** — all absolute.

### MusicUnit
numpy-backed MusicEvent sequence; slices, iterates, transforms. Core building
block. (No `append()` — use `add_event()`.)

### UnitMatrix
2D framework — rows = voices, columns = sections, cells = MusicUnit:

```
        Section 1   Section 2   Section 3   Section 4
Voice 1:   [A₁]       [A₂]        [A₃]        [A₁']
Voice 2:   [B₁]       [B₂]        [B₁]        [B₃]
Voice 3:   [C₁]       [C₁]        [C₂]        [C₂']
Voice 4:   [D₁]       [D₂]        [D₃]        [D₁]
```

**Zero-drift invariant**: every voice's section units must end exactly at the
section boundary; `validate()` gates every export.

### SCALE levels (within the concrete layer)

| Level | Scope | Example methods |
|---|---|---|
| **L4 MACRO** | form, sections, tonal plans | Skeleton-First (001), Tension Curves (ABS-001) |
| **L3 MESO** | phrase, motif, groove | Euclidean Groove Locking (012), Schillinger Resultants (018) |
| **L2 VOICE** | one line's contour | Tendency Masking (023), Perlin Noise (040) |
| **L1 MICRO** | note → note transitions | Markov Transitions (002) |

Composition paths chain levels — e.g. **middle-out** (Path C): L3 groove
anchor → L4 form around it → L2 lines → L1 fills
(`workflows/paths.py: compose_middle_out()`).

---

## Projects & the living research tree

`projects/` is not example output — it is the **primary research corpus** of
this repo, grown by scheduled autonomous agents and fully git-tracked:

| Tree | Contents |
|---|---|
| `projects/Styles/` | 55+ genre folders, 100+ numbered compositions — each with MIDI (phase 1 raw + phase 2 arrangement), audio, grid/harmony audits, provenance, REPORT.md |
| `projects/Research/` | **methods_db.md** (95 algorithmic methods), **human_methods_db.md** (29 human-composition methods), sound SP methods, per-method research reports, LAYER_ARCHITECTURE.md |
| `projects/Instruments/` | 18 researched instruments — importable registry with GM program, ranges, sweet spots, articulations, synthesis presets |
| `projects/Production/` | nightly SP-method production outputs |
| `projects/Legacy/` | archived pre-restructure projects (read-only) |

**How a method travels from idea to code:**

1. **Research** (nightly): a new method is researched, classified by layer
   (abstract / concrete / absolute / human), and written up with sources.
2. **DB**: one row per method in `methods_db.md` (Layer column included) or
   `human_methods_db.md`.
3. **Registration** (weekly): implemented methods are promoted into code —
   `workflows/paths.py` SCALE + `generators/generator_registry.py` (concrete),
   `SP_METHODS` in `workflows/musicom_workflow.py` (absolute) — via
   `register_method()`, keeping DB and code in sync.
4. **Production** (nightly): compositions pick implemented methods, run the
   two-phase pipeline (raw generative draft → grid/harmony/voice-leading
   post-process), render audio, and audit the result (grid 0 off-grid, harmony
   0 violations, zero-drift, provenance).

---

## Testing

```bash
pytest tests/                                    # 688 passing
pytest tests/ --cov=structures --cov=workflows   # with coverage
```

> **Suite status:** green — 688 passed, 1 skipped. Highlights:
> - `tests/test_harness_golden.py` — **zero-drift golden MIDI**: a fixed
>   composition must export byte-identical, deterministic, equal-length tracks.
> - `tests/test_phase2_bugfixes.py` — regression guards for the fixed engine bugs.
> - `tests/test_docs_smoke.py` — proves documented code actually runs.

Pre-project gate: run the composition preflight before committing any project
artifacts:

```bash
$MUSICOM_PYTHON $MUSICOM_ROOT/projects/Research/preflight_check.py <project_dir>
```

---

## Contributing

Contributions welcome — engine code, methods research, and instrument
knowledge all live in this one repo.

### Priority areas

1. **Selector layer-chaining** — `workflows/selector.py` currently picks
   single methods; wire `layers_needed` → ordered abstract→concrete→absolute
   chains.
2. **More SP-method adapters** — 12 SP methods are routable via
   `produce()`; most of the 77 `sound/` modules await workflow adapters
   (`SP_METHODS` registry in `workflows/musicom_workflow.py`).
3. **Abstract-layer methods** — implement more ABS-* subset-network plans
   (`rules/subset_network.py`) and wire them as harmony sources.
4. **Time-signature metadata** — asymmetric meters (7/8, 5/4) aren't encoded
   in exported MIDI (`converters/midi_converter.py`).
5. **Pitch-class set operations** — inversion/retrograde/transposition TODO in
   `structures/pitchclass.py`.

### Workflow

1. Fork + clone; `bash scripts/setup_env.sh`.
2. `pytest tests/` — the suite must stay green (688 tests).
3. Follow the flat-package layout; never hand-roll raw mido authoring (the
   `UnitMatrixComposer.validate()` zero-drift gate is the whole point).
4. Add tests for new modules; keep the golden harness intact.
5. Update `CHANGELOG.md` under `[Unreleased]`.

---

## License

MIT — see [LICENSE](LICENSE).

## History

See [CHANGELOG.md](CHANGELOG.md) and the git log for the full phase-by-phase
record (370+ commits, 2024 → present). For the machine-facing operating
contract (env, imports, workflow gates), read [AGENTS.md](AGENTS.md).

## Acknowledgments

- [music21](https://web.mit.edu/music21/) — MIT's music analysis toolkit
- [musicpy](https://github.com/Rainbow-Dreamer/musicpy) — computational music structures
- Classical theory, serialism, xenakis-style formalized music, and the
  algorithmic composition tradition

---

**Musicom is an educational research project** for exploring AI-assisted
composition and production with full, inspectable control of every step —
built for composers, music theorists, and developers who want to understand
*how* music is made, not just generate it.
