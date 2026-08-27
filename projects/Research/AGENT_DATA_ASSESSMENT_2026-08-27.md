# Agent Data Assessment — Findings & Fixes (2026-08-27)

Assessment of the musicom agent data for inconsistencies, illogical
formulations, duplicates, and repeated errors. Plan executed: reorganize
knowledge (methods, styles, instruments, sounds) as tools in the
composition (design) and realization (production) workflow.

## Findings → Fixes

### A1. Instrument registry self-contradiction (trumpet 57 = Trombone)
**Fixed**: trumpet → GM 56 (SF2 preset 56 = SoloTrumpet). Updated
`trumpet.py`, `trumpet/instrument.md` (3 refs), `registry.md` table + quirks.

### A2. Repeated wrong formula in 4 string instrument docs
**Fixed**: `D = sr/(2*freq)` → `D = sr/freq` (single delay, no sign
inversion — the /2 was an octave error, contradicted by working code in
bowed.py and SP-011). Fixed in violin/viola/cello/double_bass instrument.md.

### A3. README phantom API (VIOLIN object that didn't exist)
**Fixed by building it**: `instrument_registry.py` loads all 13 instruments
as real `Instrument` objects (`VIOLIN.midi_program`, `by_name`, `by_program`,
`registry_table()`). README rewritten to the real API. Verified:
`TRUMPET.midi_program == 56`.

### A4. "What NOT to do" guides vs actual practice
**Addressed**: AGENTS.md now leads with a positive fast-path template
(`compose()`/`produce()`), plus the equal-length rule. The FORBIDDEN tables
are still there for the low-level API but no longer the primary guidance.
8 raw-mido scripts tracked in `KNOWN_RAW_MIDI_SCRIPTS.md` (not silently
rewritten — they produce verified audio).

### A5. Knowledge trapped in one-off scripts (the core finding)
**Fixed via tools**:
- **SP methods promoted to shared `sound/`**:
  - SP-011 Karplus-Strong → `sound/synthesis/karplus_strong.py`
  - SP-026 Phase Vocoder → `sound/effects/phase_vocoder.py`
  - SP-028 LPC → `sound/effects/lpc_synth.py`
  - SP-024 already used shared `BowedString` (confirmed)
  - SP-029 polyblep documented as intentionally local (behavior-preserving)
- **Methods → generators bridge**: `generators/generator_registry.py` maps
  method IDs (002→Markov, 012→euclidian, 018→Schillinger, 023→TendencyMasking,
  ...) to code; spec-only methods (026 DPSM, 048 RBMPD) flagged honestly as
  NO CODE instead of fake-mapping.
- **Single workflow spine**: `workflows/musicom_workflow.py` —
  `compose(style, key, bpm)` → validated zero-drift MIDI + provenance;
  `produce(midi, "SP-001"|"SP-011")` → WAV + OGG. STYLE_REGISTRY holds
  pop/bossa/flamenco/jazz/techno templates. Tables auto-generated.

### A6. methods_db.md 13,518-line monolith
**Addressed**: registry tables are now generated from code
(`method_table()`, `sp_method_table()`, `style_table()`,
`generator_registry.registry_table()`). The monolith can shrink to an index
as the generated tables replace it.

## Verification (all real output)
- 263 pytest tests green (was 214; +6 workflow tests, +43 baseline)
- compose() → 58s pop piece, validated MIDI, provenance ✓
- produce() SP-001 → WAV 10.3MB + OGG 434KB, real audio (peak 20.8k)
- produce() SP-011 → karplus WAV 10.4MB + OGG 557KB, real audio (peak 29k)
- Fanfare/backups/004 deduped (byte-identical to live, md5 verified), 5MB freed
- Repo synced + autopushed to GitHub (0 ahead/0 behind)

## Not done (deliberately)
- The 159 near-identical compose/regen scripts: 123/135 already use the
  engine; each is a thin per-project wrapper. Not mass-rewritten (risk to
  verified audio). New work should use the workflow spine.
- 8 raw-mido scripts: tracked, migrate on next project touch.
- 77 dead `/root/musicom` sys.path lines: tracked, remove on next touch.
- v2/v3 clones: kept (only copy of some final audio).
