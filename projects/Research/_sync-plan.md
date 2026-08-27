# Musicom Agent — Data Sync Plan

**Goal**: Consolidate all musicom agent data (projects, research, methods, instruments, styles, production reports, job outputs) into the canonical musicom repo (`/opt/data/repos/musicom/`). All jobs and chats contribute. Daily sync via cron.

**Status**: DRAFT — awaiting approval before execution.

---

## 1. Current State (scattered)

| Data | Location | Size | Git-tracked? |
|---|---|---|---|
| musicom engine code | `/opt/data/repos/musicom/` | ~50MB | ✓ (git) |
| Compositions (Styles) | `/opt/data/projects/Styles/` | ~200MB | ✗ |
| Research (methods DB) | `/opt/data/projects/Research/` | ~10MB | ✗ |
| Instruments KB | `/opt/data/projects/Instruments/` | ~1MB | ✗ |
| Production reports | `/opt/data/projects/Styles/Production/` | ~50MB | ✗ |
| Agent KB | `/opt/data/repos/musicom/hermes_agent/` | ~1MB | ✓ |
| Hermes skills | `~/.hermes/skills/` | ~5MB | ✗ |
| Hermes memory | `~/.hermes/memories/` | ~100KB | ✗ |
| Cron jobs | `/opt/data/cron/jobs.json` | ~35KB | ✗ |

**Problem**: Agent knowledge is split across 3 locations. No single source of truth. If the VM dies, projects/research/instruments are lost.

---

## 2. Target State (consolidated)

```
/opt/data/repos/musicom/
├── sound/                    (existing — synthesis/effects)
├── generators/               (existing — composition methods)
├── structures/               (existing — core types)
├── workflows/                (existing — pipelines)
├── rules/                    (existing — voice leading)
├── tests/                    (existing)
├── examples/                 (existing)
├── hermes_agent/             (existing — agent KB)
│   ├── composition.md
│   ├── sound-production.md
│   ├── methods-registry.md
│   ├── surveillance.md
│   ├── decisions.md
│   └── reports/              (NEW — daily job reports)
│       ├── composition_2026-08-28.md
│       ├── production_2026-08-28.md
│       └── ...
├── projects/                 (NEW — all project data)
│   ├── Styles/               (compositions by genre)
│   │   ├── Pop/
│   │   │   ├── pop-5part-methods/
│   │   │   │   ├── MIDI/
│   │   │   │   ├── Analysis/
│   │   │   │   ├── README.md
│   │   │   │   └── compose.py
│   │   │   ├── orchestrated-pop/
│   │   │   └── ...
│   │   ├── Soul/
│   │   │   └── 078-soul-voiceleading/
│   │   ├── Jazz/
│   │   └── ...
│   ├── Research/
│   │   ├── CompositionMethods/
│   │   │   ├── methods_db.md
│   │   │   ├── human_methods_db.md
│   │   │   ├── method_059_*.md
│   │   │   ├── sound_method_SP-045_*.md
│   │   │   ├── human_method_HC-007_*.md
│   │   │   └── reports/
│   │   │       ├── report_059.md
│   │   │       ├── report_SP-045.md
│   │   │       └── ...
│   │   └── Newsletters/
│   │       └── digest_2026-08-28.md
│   ├── Instruments/
│   │   ├── registry.md
│   │   ├── orchestrator.py
│   │   ├── Strings/
│   │   │   ├── violin/
│   │   │   │   ├── instrument.md
│   │   │   │   ├── violin.py
│   │   │   │   └── REPORT.md
│   │   │   └── cello/
│   │   ├── Keys/
│   │   ├── Brass/
│   │   └── ...
│   └── Production/
│       └── SP035-gendyn-markov-chorale/
│           ├── REPORT.md
│           ├── provenance.json
│           └── Audio/
│               └── *.ogg  (small, tracked)
├── docs/                     (NEW — user-facing docs)
│   ├── README.md
│   ├── instruments.md        (rendered from Instruments/registry.md)
│   └── methods.md            (rendered from methods_db.md summary table)
├── .gitignore                (update — see §4)
└── AGENTS.md                 (update — see §5)
```

---

## 3. What's Tracked vs Ignored

### Tracked (git add)
- All `.md` files (documentation, reports, READMEs)
- All `.py` files (composition scripts, instrument constants)
- All `.json` files (provenance, summary)
- All `.mid` files (MIDI — small, editable)
- All `.ogg` files (compressed audio — ~300KB each, playable)
- All `.txt` files (grid visualizations)

### Ignored (.gitignore)
- `*.wav` (large raw audio — ~10MB each, renderable from MIDI)
- `*.sf2` (SoundFonts — large, external)
- `.env*` (secrets)
- `__pycache__/`, `*.pyc`
- `_test/` (ephemeral test artifacts)
- `node_modules/`, `.venv/`
- `*.log`

**Rationale**: WAV files are derivable from MIDI + FluidSynth. OGG files are small and provide instant playback. MIDI is the source of truth.

---

## 4. Sync Mechanism

### Per-job commit (immediate)
Each job writes its output, then commits its own files:
```bash
cd /opt/data/repos/musicom
git add projects/Styles/<genre>/<project>/
git commit -m "project: <project-name> (method <NNN>)"
```

### Daily sync cron (23:59 UTC)
New cron job: `daily-repo-sync`
- Runs `git add -A` (stages all tracked files)
- Commits with message: `daily sync: <date> (<N> files changed)`
- Notifies user (does NOT auto-push — per existing memory: "Always ask before git push")
- User reviews + approves push to remote

### Push policy
- Local commits are automatic (per-job + daily sync)
- Push to remote requires user approval (existing convention)
- Sync job reports: "committed <N> files, ready to push"

---

## 5. Job Updates (report contract)

All 8 jobs already updated (§previous turn) to write `REPORT.md` in their output folder. Now add:

**After writing REPORT.md, each job must:**
```bash
cd /opt/data/repos/musicom
git add <path-to-report> <path-to-outputs>
git commit -m "<job-type>: <method/project> (<date>)"
```

**Example** (daily-algorithmic-composition):
```bash
cd /opt/data/repos/musicom
git add projects/Styles/Soul/079-soul-markov/
git commit -m "composition: 079-soul-markov (method 007)"
```

---

## 6. AGENTS.md Updates

Update `/opt/data/repos/musicom/AGENTS.md` to document the new structure:

```markdown
## Project data (tracked)

All composition projects, research, instruments, and production reports live
under `projects/`. Each job writes to its own subfolder and commits immediately.

### Folder structure
- `projects/Styles/<Genre>/<project>/` — compositions (MIDI, scripts, reports)
- `projects/Research/CompositionMethods/` — methods DB + standalone files
- `projects/Research/Newsletters/` — weekly digest MDs
- `projects/Instruments/<family>/<name>/` — instrument KB
- `projects/Production/<method>-<project>/` — production reports + audio

### What's tracked
- `.md`, `.py`, `.json`, `.mid`, `.ogg`, `.txt` (documentation, code, MIDI, audio)

### What's ignored
- `*.wav` (large raw audio — renderable from MIDI)
- `.env*` (secrets)
- `__pycache__/`, `_test/` (ephemeral)

### Sync
- Per-job commit (immediate after output)
- Daily sync cron (23:59 UTC) — stages all, commits, notifies
- Push requires user approval (existing convention)
```

---

## 7. Migration Steps (execution order)

1. **Create folder structure** in `/opt/data/repos/musicom/`:
   - `projects/Styles/`, `projects/Research/`, `projects/Instruments/`, `projects/Production/`
   - `hermes_agent/reports/`
   - `docs/`

2. **Move data** (rsync, preserve history):
   ```bash
   rsync -av /opt/data/projects/Styles/ /opt/data/repos/musicom/projects/Styles/
   rsync -av /opt/data/projects/Research/ /opt/data/repos/musicom/projects/Research/
   rsync -av /opt/data/projects/Instruments/ /opt/data/repos/musicom/projects/Instruments/
   ```

3. **Update .gitignore** (add `*.wav`, `.env*`, `__pycache__/`, `_test/`)

4. **Update AGENTS.md** (document new structure + sync policy)

5. **Update all 8 job prompts** (add git commit step after REPORT.md write)

6. **Create daily-sync cron job** (23:59 UTC, git add -A + commit + notify)

7. **Initial commit** (stage all moved data, commit as "consolidate agent data")

8. **Verify** (git status clean, all jobs can write + commit)

---

## 8. Risks + Mitigations

| Risk | Mitigation |
|---|---|
| Large audio files bloat repo | `.gitignore` `*.wav`, track only `.ogg` |
| Merge conflicts (multiple jobs commit same day) | Per-job commits (small, isolated) + daily sync (stages all) |
| Secrets leak (`.env.mail`) | `.gitignore` `.env*` |
| Repo grows too large | Monitor with `git count-objects -vH`, consider LFS for OGG if >1GB |
| Push fails (network, auth) | Daily sync commits locally, notifies user, retry next day |
| Job writes outside `projects/` | AGENTS.md enforces `projects/` as canonical output root |

---

## 9. Verification

After migration:
```bash
cd /opt/data/repos/musicom
git status                    # should be clean (nothing to commit)
git log --oneline -5          # should show "consolidate agent data" + job commits
find projects/ -type f | wc -l  # count migrated files
```

Test a job:
```bash
# Run daily-algorithmic-composition manually
# Verify it writes to projects/Styles/<genre>/<project>/
# Verify it commits (git log shows the commit)
```

---

## 10. Open Questions

1. **Audio strategy**: Track `.ogg` (small, playable) or only `.mid` (source of truth)?
   - Recommendation: Track `.ogg` for instant playback, `.wav` ignored (renderable)

2. **Hermes skills/memory**: Migrate to repo or keep in `~/.hermes/`?
   - Recommendation: Keep in `~/.hermes/` (Hermes-internal, not musicom-specific)

3. **Cron job definitions**: Track `jobs.json` in repo?
   - Recommendation: No (Hermes-internal, VM-specific)

4. **Push cadence**: Daily push or weekly?
   - Recommendation: Daily commit, push on user approval (existing convention)

5. **Remote repo**: GitHub? GitLab? Self-hosted?
   - Recommendation: User decides (not in scope of this plan)

---

## 11. Next Steps

**Awaiting approval**:
- [ ] Approve folder structure (§2)
- [ ] Approve tracked/ignored files (§3)
- [ ] Approve sync mechanism (§4)
- [ ] Approve migration steps (§7)
- [ ] Answer open questions (§10)

**After approval**:
1. Execute migration (steps 1-7)
2. Update all 8 job prompts (add git commit)
3. Create daily-sync cron job
4. Verify + test
5. Report completion

---

**Plan author**: Hermes Agent
**Date**: 2026-08-27
**Status**: DRAFT — awaiting user approval
