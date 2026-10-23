# Composition Design Space — paths, roles, variations

Canonical reference for the composition decision space: the full path from
method selection (abstract vs concrete) through voice-role orchestration to
section fill, plus the variation axes and their sub-options.

Written 2026-10-23 (Hermes analysis). Non-executive — design reference.

---

## 1. Pipeline: start → roles → fill

### 1.1 Layer routing (abstract vs concrete)

Three layers, routed by `workflows/selector.py::select_chain(profile, layers_needed=("abstract","concrete","absolute"))`.

| Layer | Produces | Method IDs | Output shape |
|---|---|---|---|
| **Abstract** | design *only* — no notes | ABS-001..005 | progression skeleton, tension curve, progression-ID walk |
| **Concrete** | *realize* → raw events | SCALE L1–L4 (~74) + HC-* (~23) | `pitch_index [0,1]`, fractional onset, velocity |
| **Absolute** | audio | SP-* | stems → WAV/OGG |

Abstract-layer methods (`rules/subset_network.py` + `generator_registry`):

- **ABS-001 Tension Curve Planner** (L4) — per-section tension targets from form
  (intro low → chorus peak → bridge max → outro resolve).
- **ABS-002 Subset Walker** (L4) — `PatternNetwork.walk(start, length, tension_curve, home)` → progression-id sequence; chords as subset walks, tension from set relations (no functional labels).
- **ABS-003 Z-Variation** (L3) — swap chord for Z-partner (same ICV, different notes). **Triad caveat:** triads have no Z-partner (`z_partner([0,4,7])` is None — Z-relation starts at tetrads). Voice 7th chords for a real Z-swap.
- **ABS-004 Parsimonious Voice Leading** (L3) — P/L/R moves, ≤2 semitone total motion (Cohn/Neo-Riemannian).
- **ABS-005 Complement Contrast** (L3) — move to complement: matched tension, maximal contrast.

**Path combos:**

- `concrete-only` — method → notes directly (nightly cron default).
- `abstract + concrete` — ABS design skeleton → concrete method fills it.
- `abstract + concrete + absolute` — full chain to audio.
- `abstract-only` — design/analysis, no realization (progression/tension only).

### 1.2 Concrete method levels (SCALE)

`workflows/paths.py::SCALE` tags each method with a level:

- **L4** macro/form — 001, 006, 010, 034, HC-001, ABS-001/002.
- **L3** meso/loop — 003, 012, 018, 023-adjacent, HC-012, ABS-003/004/005.
- **L2** voice/contour — 023, 040, 043.
- **L1** note→note transition — 002, 011, 050.

**Path C** = `compose_middle_out()`: L3 anchor groove → L4 form around it → L2 lines on top → L1 fills. Deterministic per seed, zero-drift gated.

**Registry truth:** a method is routable ONLY if `generator_registry` has code.
9 concrete methods are code-implemented (`001/002/003/010/012/018/023/040/079`);
~100 are spec-only (e.g. 065 Twelve-Tone Serial) → realized by the bespoke
compose.py, not the registry.

### 1.3 Voice roles & relations (orchestration)

`projects/Instruments/orchestrator.py` — role → instrument → register → dynamics → balance.

| role | register | velocity | balance | primary | secondary |
|---|---|---|---|---|---|
| bass | 36–55 | 90 | 0.9 | Double Bass | Bass Gtr, Tuba, Cello |
| harmony | 48–71 | 60 | 0.7 | Piano | Guitar, Organ |
| pad | 48–72 | 50 | 0.5 | Strings Section | Synth Pad, Organ, Choir |
| counter | 55–79 | 70 | 0.8 | Viola | Clarinet, Oboe, Trombone |
| accent | 60–84 | 95 | 0.95 | Trumpet | Trombone, Crash, Timpani |
| melody/lead | 67–96 | 85 | 1.0 | Violin | Flute, Trumpet, Piano |
| rhythm | — (ch9) | 80 | 0.8 | Drum Kit | Congas, Djembe, strum |

Non-crossing register stack (low→high): `bass → harmony → pad → counter → accent → melody`. `rhythm` = percussion, channel 9, no pitch register.

**Orchestration presets** (`ORCHESTRATION_PRESETS`):

- `pop` — `[melody, harmony, bass, rhythm, pad]`
- `classical` — `[melody, counter, harmony, bass, accent]`
- `jazz` — `[melody, harmony, bass, rhythm]`

**Section dynamics** (`SECTION_DYNAMICS`, pop):
Intro `[melody, pad]` · Verse `[melody, harmony, bass, rhythm]` · Chorus `[melody, harmony, bass, rhythm, pad]` · Bridge `[melody, counter, harmony, pad]` · Outro `[melody, harmony, pad]`.

**Role determination (two sources, pick one):**

- *position-based* — `workflows/cell_engine.py::default_resolve_role(vi, inst, ctx)` → `0=lead 1=pad 2=bass 3=arp 4=rhythm` (rhythm slot only fills for drum-kit instruments).
- *method-output* — `workflows/method_contract.py` contract `resolve_role(ctx) → "lead"|"counter"|"harmony"|"bass"|"pad"|"rhythm"`. Role is a method output, not a static column; `ctx.other_roles` lets a method see "lead taken → pick counter".

### 1.4 Fill sections

`create_matrix → add_voice → add_section → fill_voice_section → validate → to_midi`.

`CellComposer.fill_cell(vname, sname, ctx, role)` → `realize_spine.realize(notes, ctx, role, grid)`.

ROLE_FILLERS: **lead 8th-arp / pad sustained / bass 1&3 / arp 16ths / rhythm grid**.

Two-phase: **phase1** raw draft (off-grid, single voice, own zero-drift gate) →
**phase2** rules (grid-snap → chord-quant → harmonize → vary → embellish → audit).
Tiered pitch: strong beat = in-scale AND in-chord; weak = in-scale; tagged
chromatic ornaments allowed on lead/counter only.
Dual-version: `-perfect` (grid-locked) + `-humanized` (jitter).

---

## 2. Variation space (axes, one level deep)

### Axis 1 — Layer path

- `concrete-only`
  - registry method (adapter for the 9 implemented)
  - spec-only method (bespoke compose.py realizes the ~100 prose methods)
- `abstract + concrete`
  - ABS-002 walker → progression IDs → concrete fills the skeleton
  - ABS-001 tension curve → drives per-section density/register
  - ABS-003 Z-swap (needs tetrads) · ABS-004 parsimonious VL (≤2 st) · ABS-005 complement
- `abstract + concrete + absolute` — append SP-* production (FluidSynth / hybrid synth / Karplus-Strong)
- `abstract-only` — design/analysis (progression + tension, no audio)

### Axis 2 — Method paradigm (concrete)

- **Stochastic** — Markov 002 (transition weights) · Tendency Masking 023 (corridor pitch clouds) · Lévy 053 (heavy-tail walks) · Quantum Walk 052 (interference, ballistic spread) · Hawkes 045 (self-exciting bursts) · ACOPF 041 (swarm) · SMA 039 (spectral from audio)
- **Rules** — Skeleton 001 (grids from DNA seeds) · Euclidean 011 (pulse/hit cycles) · Xenakis Sieve 025 (modular congruences) · Isorhythm 032 (talea+color coprime) · WFC 033 (constraint collapse) · PCFG 034 (recursive rewrite) · OTVL 050 (optimal-transport VL) · SGLM 051 (spectral graph) · Species Counterpoint 056 (Fux constraints) · PHTDA 044 (topology)
- **Nature** — DPSM 026 (phase-shift polyrhythm) · Reaction-Diffusion 030 (Turing) · Boids 031 (flocking) · Physarum 035 (slime mold) · Sandpile 036 (avalanches) · FHN 037 (neural spikes) · Kuramoto 038 (phase sync) · Strange Attractor 043 (Lorenz/Rössler) · Reflected Brownian 048 · IFS 049 (fractal)
- **AI** — NST 042 · VAE 046 · MT-GAC 057 · NODE 058 (headless/cron-excluded)

### Axis 3 — Lead count / melody structure

- **0 leads** (ambient) — pad-only drone · evolving pad · arp-only texture
- **1 lead** (mono) — single melodic line, register + instrument choice
- **1 + counter** — counter constraints: contrast (never sounds lead's pitch class simultaneously) + complementary density (onsets only on grid slots the lead leaves free)
- **2 leads** — duet (parallel 3rds/6ths) · echo/canon (offset) · call-response
- **lead + accent** — brass/percussion stabs on strong beats, not a full counterline

### Axis 4 — Percussion style

- **none** — solo, pad-only, a cappella-like
- **minimal** — kick + snare backbeat only
- **full kit** — straight 8th · straight 16th · swing/shuffle
- **16th funk** — syncopated kick (0, 720, 960, 1680) + ghost snare
- **swing/shuffle** — ride at 2/3 beat (tick 320 @ 480 tpb), hi-hat chick 2&4, feather kick 1&3
- **hand percussion** — congas/djembe/shaker, clave patterns
- **Euclidean** (011) — E(k,n) cycles (mind the Bjorklund phase-shift; use beat-aligned patterns)
- **accent-only** — crash/timpani on section peaks

### Axis 5 — Harmonization voices

- **none** — monophonic (lead ± bass)
- **pad** — sustained whole/half notes; 1-voice vs chord block
- **comp** — rhythmic chord stabs: "and of 2 / and of 4" · syncopated · montuno (repeating pattern)
- **arp** — 16th broken chord: up / down / alternating · octave span
- **counter** — contrapuntal line (see 056 Species); contrast rules
- **4-part** — SATB block vs arpeggiated
- **voicing color** — triad vs 7th vs extended (9/11/13) · inversions

### Axis 6 — Voice count / texture

- 1 voice (phase-1 raw draft)
- 2 (lead + bass)
- 3 (lead + harmony + bass)
- 4 (lead + harmony + bass + rhythm)
- 5 (lead + counter + harmony + bass + rhythm/pad)
- 6+ (add accent, second harmony, double lead)

### Axis 7 — Register allocation

- non-crossing stack (default: `bass → harmony → pad → counter → accent → melody`)
- shifted (lead low / tenor register, harmony high)
- doubling — unison (comb-filter risk!) vs octave (safe)

### Axis 8 — Density / motion

- sparse (half/whole notes)
- 8th-note
- 16th-note
- diminution (16th runs) vs augmentation (×2 durations)
- per-section map (intro sparse → verse 8th → chorus 16th → bridge dense → outro fade)

### Axis 9 — Form

- loop (4/8/16 bar)
- aba · aabb · intro-a-a-b-a
- blues-12
- verse-chorus (intro-verse-chorus-verse2-chorus2-outro)
- head-solos-head
- 5-part · through-composed
- sub: per-section bars + harmonic region (midpoint root — NOT bar-0, which collapses every section to tonic)

### Axis 10 — Humanization

- none (perfect grid-locked)
- style-derived (`STYLE_HUMANIZE`: groove tight, organic loose)
- per-voice override (`hz_instruments` dict)
- **timing authority (2026-10-23):** STYLE governs melodic-voice `timing_sigma_ms` + `layback_ms`; drums (2 ms / 0) + bass (8 ms layback) keep role DNA. Melodic `humanize_dna` returns `None` for timing/layback → style wins.
- sub-knobs: timing σ · layback · phrase_corr (correlated drift vs white noise) · velocity σ

### Axis 11 — Role source

- position-based (`default_resolve_role`)
- method-output (`resolve_role`, role-first)
- sub: `ctx.other_roles` (lead taken → counter), counter contrast + complementary density

Full space = product of axes. Example: `concrete-only × Stochastic(Markov) × 1+counter × full-kit × pad+comp × 5 voices × non-crossing × 16th × intro-a-a-b-a × style-humanized × method-output`.

---

## 3. Example design (reference — not executed)

**Target:** funk groove, F minor, 104 BPM, 32 bar.

| decision | pick |
|---|---|
| layer path | concrete-only (method 075 SOM-C, spec-realized) |
| method | 075 SOM-C (Kohonen map + Markov walk → pitch contour) |
| lead | 2 melodic — lead trumpet + tenor-sax counter (active where lead rests) |
| percussion | full kit, straight 16th (hats 16th + syncopated kick + backbeat snare) |
| harmonization | piano comp ("and of 2 / and of 4") + synth pad (Chorus/Break only) |
| voices | 5 = Lead, Counter, Piano, Bass, Drums |
| register | bass 38–50 → piano 48–72 → counter 55–79 → lead 60–88 |
| density | Intro sparse → Verse 8th → Chorus 16th → Break diminution |
| form | intro-verse-chorus-bridge-verse2-chorus2-break-outro (8×4 bar) |
| role source | method-output (lead taken → sax picks counter) |
| humanization | groove-tight σ 3–4 ms, lead layback 0 |

Gates: zero-drift 69120 · perfect off-grid 0 · harmony 0/0/0 · humanized off-grid > 0 · master −14 LUFS / −1 dBTP.
