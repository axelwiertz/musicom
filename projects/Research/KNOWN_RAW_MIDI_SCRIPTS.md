# Known raw-MIDI scripts (AGENTS.md violations — tracked)

The AGENTS.md hard rule says: compose with the engine (UnitMatrixComposer →
validate → to_midi), never author with raw `mido`. These scripts were
discovered (2026-08-27 assessment) to use raw mido authoring with **zero**
engine references. They are NOT rewritten here because each produces
verified audio — changing them risks silent output changes.

They should be migrated to the engine (or the shared `workflows/musicom_workflow`
spine) when their project is next touched.

## Scripts with raw-mido authoring, no engine

| Path | Genre | Notes |
|---|---|---|
| `Cuban/004-cuban-rumba-clave-lab/src/regen.py` | Cuban | rumba clave lab |
| `Cuban/005-cuban-son-clave-lift/src/regen.py` | Cuban | son clave lift |
| `Country/041-country-railroad-morning/src/regen.py` | Country | railroad morning |
| `World/bollywood-study/src/compose.py` | World | bollywood study |
| `Fanfare/004-dutch-fanfare-integrated/src/regen.py` | Fanfare | **backup copy removed 2026-08-27; live copy uses raw mido** |
| `Fanfare/030-jan-klaassen/compose.py` | Fanfare | jan klaassen |
| `Pop/moonlight-shadow/compose.py` | Pop | moonlight shadow |
| `Reggae/001-reggae-dub-lab/compose.py` | Reggae | dub lab (has 3 engine refs — partial) |

## Also tracked

- **Dead `sys.path.insert(0, '/root/musicom')`**: 77 scripts point at a path
  that does not exist on this machine. These are legacy from before the
  editable install; they still run because the engine is installed globally,
  but the line is dead weight and misleading. Remove on next touch.
- **`v2`/`v3` project clones** (gamelan_kebyar_v2/v3, flamenco_solea_v2,
  bossa_nova_classic_v2/v3, blues_delta_v2, indian_classical_yaman_v2/v3,
  033-wagner-study-v2): these are iteration snapshots, often the ONLY copy of
  final audio. Kept deliberately; do not delete.
- **`Fanfare/backups/`**: 001/002/003 are backup-only projects (live removed);
  004 was byte-identical to live and removed (deduped, in /tmp/backup-004-check).
