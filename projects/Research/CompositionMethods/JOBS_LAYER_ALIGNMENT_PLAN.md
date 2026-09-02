# Nightly Jobs → Layered Methodology Alignment Plan

Date: 2026-09-02. Status: **EXECUTED** (all 4 proposed job changes applied
2026-09-02 11:29 UTC; jobs.json updated_at bumped, scheduler confirmed live).

## Layer model (recap, LAYER_ARCHITECTURE.md)

| Layer | Produces | Code home |
|---|---|---|
| **abstract** | 12TET subset designs, progressions, tension plans | rules/subset_network.py, ABS-* |
| **concrete** | realized UnitMatrix cells, MIDI events | generators/*, workflows/*, SCALE |
| **absolute** | audio signal (stems → WAV/OGG) | sound/*, SP-* |

## Job-by-job assessment + applied changes

### 1. `daily-algorithmic-composition-production` (1fc3fd65d359, 23:00) — UPDATED ✅
- **Applied**: LAYERED METHODOLOGY section — selection from methods_db.md
  algorithmic table reads the **Layer** column; ~6/7 nights pick `concrete`,
  ~1/7 picks `abstract` (exercises abstract→concrete end-to-end); layer
  reported in REPORT.md + chat summary.
- **Applied**: instrument selection now points at the full importable registry
  `instrument_registry.py` (18 instruments) instead of the 10-entry
  MidiInstrument enum.
- **Applied**: render via `workflows.musicom_workflow.produce(midi, "SP-001")`
  adapter (discover_soundfont auto), no hardcoded TimGM6mb.

### 2. `random-style-production` (9a2813f77dac, 22:00) — UPDATED ✅
- **Applied**: pick pool = `workflows.musicom_workflow.SP_METHODS` (code truth,
  7 implemented entries) — not the stale "SP-001 to SP-035+" range; spec-only
  SP research IDs (SP-160) excluded so it can never stall on unrenderable
  specs. Fallback SP-001 if pool < 4.
- **Applied**: absolute-layer discipline note (method applies across whole
  piece); adapter guidance for non-SP-001 methods (call module API directly).

### 3. `MusicTech Surveillance` (e2760579d2c8, Mon/Thu 09:00) — UPDATED ✅
- **Applied**: mandatory registration step — every replicated sound/ module
  gets an SP-ID assigned (next free: max numeric SP_METHODS ∪
  methods-registry.md, +1) and an `SP_METHODS` entry so nightly production can
  route it. Unregistered module = dead code (called out).
- **Applied**: hermes_agent tables (surveillance.md, methods-registry.md,
  sound-methods-overview.md) kept as tracking docs w/ truthful statuses +
  SP-IDs; PARTIAL findings get NO SP-ID and no code.

### 4. `nightly-instrument-research` (f5be3c580639, 20:00) — UPDATED ✅
- **Applied**: REGISTRY DISCIPLINE — new instrument must be added to
  `_INSTRUMENT_MODULES` in `instrument_registry.py` + convenience constant,
  proven via `python instrument_registry.py` (registry_table shows new row);
  registry.md updated. Writing `<name>.py` alone no longer counts as done.
- **Applied**: verification imports through the registry (`from
  instrument_registry import by_name`), not just the raw constants module.

### 5. `daily-repo-sync` (76c1731c5a30, 23:00) — aligned, no change
### 6. `weekly-newsletter-digest-summarizer` (4da0554c15c0, Mon 09:00) — out of scope, no change

## Execution log

| Job | Change | When |
|---|---|---|
| random-style-production | SP pick pool = implemented SP_METHODS; layer note; adapter guidance | 2026-09-02 11:29 UTC |
| MusicTech surveillance | SP-ID + SP_METHODS registration step for replicated modules | 2026-09-02 11:29 UTC |
| daily-algorithmic-composition-production | Layer-aware selection (concrete 6/7, abstract 1/7); instrument_registry; produce() adapter | 2026-09-02 11:29 UTC |
| nightly-instrument-research | instrument_registry registration + proof; import through registry | 2026-09-02 11:29 UTC |

Backup of pre-change jobs.json: `cron/jobs.json.bak_align`. All 10 jobs valid;
scheduler reloaded (ticker heartbeat + cron list show new prompt previews).
