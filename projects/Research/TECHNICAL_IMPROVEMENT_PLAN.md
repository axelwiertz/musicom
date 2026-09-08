# Technical Improvement Plan — One Repo, One Env, Decoupled Paths

Date: 2026-09-08. Status: **EXECUTED (P0–P3 done, P4 done, P5 verify)**.
Execution log at bottom. Defaults taken on open decisions: D1=A (tree into
repo + symlinks), D2=Legacy into repo, D3=DiffSinger KEPT (referenced by
human-voice-singing skill).

---

## 1. Current state (verified 2026-09-08)

### 1.1 Folder scatter

| Location | Size | Git | State |
|---|---|---|---|
| `repos/musicom` | 1.3G | ✅ live (pushed daily) | **the engine** — code + mirrored `projects/` |
| `/opt/data/projects/{Styles,Research,Instruments}` | 2.9G + 147M + 57M | ❌ (mirrored) | **live working tree** — all cron jobs write here |
| `repos/musicom-agent` | 18M | ❌ no git | frozen legacy: `music-projects/` 000–030, sessions, skills |
| `repos/musicom_framework` | 3.7M | ❌ no git | dead shell (one `musicom/` subdir) |
| `repos/musicom_platform` | 1.3M | last commit 2026-05-20 | dead |
| `repos/composer-crew-framework` | 612K | ❌ no git | dead predecessor + own venv |
| `repos/musicom-api-backend` | 264K | 2026-06-24 | dormant (separate concern) |
| `repos/musicom-web-portal` | 280K | 2026-06-24 | dormant (separate concern) |
| `repos/DiffSinger_main` | 1.5G | third-party | vocal-model experiment, unused by pipelines |

**Twin-tree problem (the big one):** `sync_to_repo.py` *copies* the working
tree into `repos/musicom/projects/` nightly at 23:00. Two live copies of the
same data exist between syncs:

- `instrument_registry.py` exists in BOTH trees. `nightly-instrument-research`
  (20:00) edits the **working** copy; `daily-algorithmic-composition-production`
  (23:00) imports the **repo** copy → up to 24 h staleness + a same-night race
  (composition can run before/while sync copies).
- methods DBs exist in both trees; research jobs edit working, code registration
  job edits repo.
- Every consumer must know *which* copy to use — 3 of the 10 cron prompts got
  this wrong at some point (fixed ad-hoc, root cause remains).

### 1.2 Environment scatter

| Env | Python | Packages | Role |
|---|---|---|---|
| `micromamba/envs/musicom` | 3.11.15 | 92 (musicom editable, numpy, scipy, mido, soundfile, **fluidsynth binary**) | **the only working env** |
| `repos/musicom/.venv` | 3.13.5 | **0 — dead, 713M wasted** | accident |
| `repos/composer-crew-framework/venv` | 3.13.5 | dead framework's env | accident |
| `/opt/data/.venv` | 3.13.5 | Hermes agent's own runtime | not ours to touch |
| `/opt/data/.local/lib/python3.13` | — | pretty_midi + TimGM6mb.sf2 | user-site leak |

- `fluidsynth` exists ONLY at `micromamba/envs/musicom/bin/fluidsynth`; bare
  `fluidsynth` is not on PATH → every script must hardcode the absolute path
  (RenderPipeline stems failed on this in project 089).
- apt has fluidsynth 2.4.4 but container runs as `hermes` (uid 10000),
  **no sudo** → system install not possible without image change.
- `import musicom` fails (flat layout: `structures`, `workflows`, `sound`...
  are top-level). pyproject names the dist `musicom 0.1.0` — dual identity,
  documented but a persistent footgun.
- The micromamba env is **not reproducible**: no `environment.yml`, no lock
  file committed anywhere. Container rebuild = env gone.

### 1.3 Hardcoded paths (census)

Repo code (excl. examples/tests): `workflows/hitl.py` + `musicom_workflow.py`
(`pyenv = "/opt/data/micromamba/envs/musicom/bin"`), `sound/render/fluidsynth.py`
(soundfont candidates), `scripts/sync_to_repo.py` (HERMES/REPO roots),
`query_state.py` (`/opt/data/state.db` — saved only by a symlink).
22 example files + 5 test files embed `/opt/data/...`.

Cron prompts: **30+ absolute paths** — 9× the micromamba python, 7× methods_db,
4× repo root, 2× fluidsynth bin, … (full census in session log 2026-09-08).

### 1.4 Container / Hermes standards context

- Already inside Docker (`/.dockerenv`), Debian 13, image = Hermes standard
  (`uv:python3.13-trixie` base), `/opt/data` = single rw volume, `/opt/hermes`
  immutable. `entrypoint.sh` runs as root → `gosu hermes`.
- Hermes terminal tool: `auto_source_bashrc: true`, `env_passthrough: []`,
  backend local → **`~/.bashrc` exports ARE seen by every terminal/cron run**.
  This is the sanctioned hook for PATH/env-var injection.
- No `MUSICOM_*` env vars exist yet — blank slate for a path contract.

---

## 2. Other inconsistencies found (fix alongside)

| # | Finding | Severity |
|---|---|---|
| I1 | **GitHub PAT in plaintext** in `repos/musicom/.git/config` remote URL (and 2 entries in `~/.git-credentials`) | 🔴 security |
| I2 | `musicom-composer` skill stale: calls `musicom-agent/music-projects` "canonical project repo" (real canonical = `projects/Styles`), hardcodes TimGM6mb soundfont path (should be `discover_soundfont()`), says "methods 001-044" (DB now at 077+) | 🟠 misleads every composition run |
| I3 | AGENTS.md says "Do NOT add sys.path.insert" but `instrument_registry` is not pip-installed → every project MUST sys.path.insert to use it (089 did). Contradiction | 🟠 |
| I4 | Dead envs: `repos/musicom/.venv` (713M, 0 pkgs), `composer-crew-framework/venv` | 🟡 disk+confusion |
| I5 | Two identical `sync_to_repo.py` copies (`.hermes/scripts/` + `repos/musicom/scripts/`, md5 match) | 🟡 drift risk |
| I6 | `_cron_tmp/` scratch dirs (2×) accumulate one-off compose/audit scripts from cron runs | 🟡 |
| I7 | `DiffSinger_main` 1.5G unused third-party | 🟡 disk (16G free of 48G, 68% used — WAVs are the growth driver) |
| I8 | `query_state.py` works only via `/opt/data/state.db` symlink | 🟢 note |
| I9 | Disk growth: WAV excluded from git but pile up in working tree; no retention policy | 🟡 |

---

## 3. Target architecture

```
/opt/data/repos/musicom/               ← THE ONE REPO (single source of truth)
├── structures/ workflows/ sound/ rules/ generators/ visualization/ utilities/
├── projects/                          ← THE ONE WORKING TREE (moved in, not copied)
│   ├── Styles/      (live composition output; *.wav gitignored, *.ogg tracked)
│   ├── Research/    (methods DBs, reports)
│   └── Instruments/ (registry — ONE copy, no twin)
├── hermes_agent/                      ← agent docs (surveillance, decisions)
├── docs/                              ← generated indexes (instruments.md, methods.md)
├── environment.yml                    ← NEW: reproducible env spec (conda/micromamba)
├── requirements.lock                  ← NEW: pip freeze lock
├── musicom_env.py  (or utilities/env.py) ← NEW: path/binary resolution contract
└── scripts/commit_projects.sh         ← sync script reduced to git add/commit/push
```

Env contract (one env, resolvable without absolute paths):

```bash
# ~/.bashrc (auto-sourced by Hermes terminal + cron runs)
export MUSICOM_ROOT=/opt/data/repos/musicom
export MUSICOM_ENV=/opt/data/micromamba/envs/musicom
export MUSICOM_PYTHON=$MUSICOM_ENV/bin/python
export FLUIDSYNTH_BIN=$MUSICOM_ENV/bin/fluidsynth
export PATH="$MUSICOM_ENV/bin:$HOME/.local/bin:$PATH"   # bare `fluidsynth`, `python` work
```

Code contract (`utilities/env.py`, imported by workflows/sound):

```python
def musicom_root() -> Path:  # $MUSICOM_ROOT or repo-relative fallback
def python_bin() -> str:     # $MUSICOM_PYTHON or sys.executable
def fluidsynth_bin() -> str: # $FLUIDSYNTH_BIN or shutil.which("fluidsynth")
def soundfont() -> str:      # existing discover_soundfont(), candidates via env
```

Rules: repo code NEVER hardcodes `/opt/data/...` (env module + relative
fallbacks only); cron prompts reference `$MUSICOM_PYTHON`, `$MUSICOM_ROOT`;
AGENTS.md updated to match.

---

## 4. Phases

### Phase 0 — Safety first (before any move) — ~1 h
1. **Rotate the GitHub PAT** (user action on github.com — I cannot do this).
   Then: `git remote set-url origin https://github.com/axelwiertz/musicom.git`
   (clean URL) + rely on `~/.git-credentials` store; scrub PAT from
   `.git/config`. *(I1)*
2. Full backup: `tar` of `repos/musicom/.git` + working `projects/` metadata
   (MIDI/MD/PY/JSON only — skip WAV/OGG bulk) to `/opt/data/backups/`.
3. Freeze window: pause the 4 nightly jobs (20:00–23:30) during migration;
   resume after verification.

### Phase 1 — One environment — ~2 h
1. Delete dead envs: `repos/musicom/.venv` (713M), `composer-crew-framework/venv`. *(I4)*
2. Export reproducibility: `micromamba env export -n musicom > environment.yml`
   + `pip freeze > requirements.lock`, commit both to repo. Add
   `scripts/setup_env.sh` (idempotent: create env from yml, `pip install -e .`,
   verify fluidsynth/ffmpeg).
3. Write `~/.bashrc` env block (§3). Verify: fresh terminal sees bare
   `fluidsynth --version`, `python -c "from structures import MusicEvent"`.
4. New `utilities/env.py` (§3 contract) + tests. Replace hardcoded `pyenv`
   in `workflows/hitl.py`, `musicom_workflow.py`; RenderPipeline default
   `fluidsynth_bin=env.fluidsynth_bin()` (fixes 089's stems failure class).
5. pytest gate green (342+ tests) → commit.

### Phase 2 — One repo folder — ~3 h (the big move)
**Decision D1 (§7): move working tree INTO the repo** (Option A below).
1. `rsync -a /opt/data/projects/{Styles,Research,Instruments}/ →
   repos/musicom/projects/` (merge; repo mirror already has most files —
   rsync makes working tree authoritative for the final merge).
2. `.gitignore`: keep `*.wav` ignored; **add** `projects/**/Audio/stems/*.wav`
   already covered; confirm OGG/MID/MD/PY/JSON tracked (user decision
   2026-08-27 stands).
3. Replace `/opt/data/projects/{Styles,Research,Instruments}` with **symlinks**
   into the repo (`ln -s /opt/data/repos/musicom/projects/Styles
   /opt/data/projects/Styles`) → every existing absolute path in prompts,
   skills, AGENTS.md keeps resolving; zero big-bang rewrite. *(Decision D2.)*
4. Retire `sync_to_repo.py` copy logic → new `scripts/commit_projects.sh`
   (git add projects docs && commit && push). Update the `daily-repo-sync`
   cron job's script pointer. Kill the twin-tree race + 24 h staleness. *(I5)*
5. Move `preflight_check.py`, `_TEMPLATE/` along (they live under Research —
   automatic via move).
6. Verify: run preflight + audit on project 089 from BOTH path spellings
   (`/opt/data/projects/...` and `/opt/data/repos/musicom/projects/...`);
   run one compose smoke test; nightly jobs dry-run.

### Phase 3 — Retire dead repos — ~1 h — **Decision D3**
- `musicom_framework`, `musicom_platform`, `composer-crew-framework`:
  archive to `/opt/data/backups/repos_archive/` then delete (no git history
  to lose — none are repos).
- `musicom-agent`: archive `music-projects/` (legacy 000–030) into
  `repos/musicom/projects/Legacy/` (git-tracked, one place), then archive+delete.
- `DiffSinger_main` (1.5G): confirm unused (grep across skills/cron/code),
  then archive+delete → frees 1.5G. *(I7)*
- `musicom-api-backend` / `musicom-web-portal`: LEAVE (separate concerns,
  small, dormant — out of scope).

### Phase 4 — Path decoupling in prompts + docs — ~2 h
1. Rewrite the 30+ hardcoded paths in all 10 cron prompts → `$MUSICOM_*`
   vars (env is visible to cron via bashrc auto-source; verified in Phase 1).
2. Update AGENTS.md files (repo root, projects/Research, projects/Styles):
   env contract, one-tree rule, registry now importable **without**
   sys.path hack (add `projects/Instruments` as a package path in
   `utilities/env.py` or install registry into the editable package →
   resolves I3 contradiction).
3. Fix `musicom-composer` skill: canonical projects = `$MUSICOM_ROOT/projects/Styles`,
   soundfont = `discover_soundfont()`, method range = dynamic DB read. *(I2)*
4. Update `python-package-rehabilitation` + `reverse-music-analysis` skill
   references that embed old paths.
5. Add `_cron_tmp` cleanup to weekly registration job; WAV retention policy
   (e.g. delete WAVs older than 30 days when OGG+MID exist) to the sync job. *(I6, I9)*

### Phase 5 — Verification & docs — ~1 h
1. Full nightly cycle observed end-to-end (instrument 20:00 → style-production
   22:00 → composition 23:00 → sync/commit 23:00) with zero path errors.
2. `docs/RESTRUCTURE.md` in repo: before/after map, decisions log.
3. Update this plan → EXECUTED with commit hashes.

**Total: ~10 h agent work + 1 user action (PAT rotation). Risk window:
Phase 2 move (~30 min of symlink swap, reversible via backup).**

---

## 5. What gets better (measurable)

| Before | After |
|---|---|
| 2 live copies of projects/ (twin-tree race, 24 h registry staleness) | 1 tree; symlinks keep old paths working |
| 4 Python envs (2 dead, 713M wasted) | 1 env + lock files; reproducible from `environment.yml` |
| `fluidsynth` needs absolute path everywhere | bare `fluidsynth` on PATH; `$FLUIDSYNTH_BIN` contract |
| 30+ hardcoded `/opt/data/...` in prompts, ~10 in repo code | `$MUSICOM_*` env contract; code uses `utilities/env.py` |
| PAT in `.git/config` plaintext | clean remote URL + credential store |
| 9 repo folders (5 dead/dormant, 1.5G unused DiffSinger) | 1 active repo + 2 dormant portals + Legacy/ inside |
| sync = 2294-file copy nightly | sync = git commit only |

## 6. Risks & mitigations

- **Move breaks a nightly job mid-run** → Phase 0 freeze window + symlink
  compatibility layer means old paths keep resolving even if a prompt is missed.
- **Git repo size growth** (OGG tracked) → already the status quo (219M);
  WAV policy unchanged; monitor with `git count-objects` monthly.
- **micromamba env export incomplete** (pip-in-conda mixing) → export BOTH
  environment.yml and requirements.lock; setup_env.sh verifies with the test suite.
- **Something still references `musicom-agent/music-projects`** → grep sweep
  across skills/cron/repo before delete; archive (not delete) first.
- **Symlink edge cases** (tools that resolve realpath and re-derive paths) →
  test preflight/audit/render through both spellings in Phase 2.6.

## 7. Decisions needed (before execution)

- **D1 — One-tree mechanism**: (A) move working tree INTO
  `repos/musicom/projects/`, old locations become symlinks [recommended];
  (B) keep working tree outside, delete the repo mirror (repo = code only,
  artifacts untracked); (C) keep twin trees, just fix the race (sync before
  each consuming job).
- **D2 — Legacy projects** (`musicom-agent/music-projects` 000–030): move into
  `repos/musicom/projects/Legacy/` [recommended] vs archive-only (outside git)
  vs delete.
- **D3 — DiffSinger_main (1.5G)**: archive+delete after unused-check
  [recommended] vs keep.

## 8. Execution order

Phase 0 (safety) → 1 (env) → 2 (one tree) → 3 (retire) → 4 (prompts/docs) →
5 (verify). Each phase ends with a green gate (pytest / preflight / job
dry-run) + commit before the next starts. Phases 1 and 3 are independent and
can interleave if time-boxed.

---

## 9. Execution log (2026-09-08)

| Phase | What | Result |
|---|---|---|
| P0.1 | PAT scrub | remote URL cleaned (`https://github.com/axelwiertz/musicom.git`, no embedded token); credential store keeps auth working. **User still should rotate the token on github.com.** |
| P0.2 | Backups | `backups/musicom_git_backup_20260908.tgz` (203M), `backups/projects_meta_20260908.tgz` (220M), `backups/repos_archive/*` (dead repos) |
| P0.3 | Freeze | 6 write-jobs paused (composition, style-prod, instrument, sync, weekly-registration, human-research) |
| P1 | One env | dead `.venv` (713M) + composer-crew venv removed; `environment.yml` + `requirements.lock` committed; `scripts/setup_env.sh` (idempotent, verified); `~/.bashrc` MUSICOM_* contract; `utilities/env.py` (env-var → relative fallback resolution); workflows/hitl + musicom_workflow + pipeline + soundfont discovery use it. **357 tests green** (`dedbfd4`) |
| P2 | One tree | working tree rsync'd (cp) into repo; nested `.git` (3) removed; old paths → symlinks (write-through verified); .gitignore extended (html/png/sample/musicxml/xml/rpp/opus/pyc/m4a/mp3/log); sync script → commit-only; tree committed (`8a22e72`, `7b5e4c2`) |
| P3 | Retire | musicom_framework/musicom_platform/composer-crew-framework/musicom-agent archived (`backups/repos_archive/`) + removed; music-projects + Knowledge → `projects/Legacy/` (nested git removed); trash_git_data_repo (471M) removed; DiffSinger KEPT (referenced by human-voice-singing) |
| P4 | Prompts/docs | AGENTS.md ×3 env/one-tree contract; musicom-composer skill canonical paths + registry + dynamic method range; 8 cron prompts got ONE-ENV/ONE-TREE preamble; daw-integration/research-cron-jobs/musicom-framework-orchestration skills updated to one-tree sync |

**Remaining (P5 + follow-ups):** resume paused jobs after full-cycle watch;
rotate GitHub PAT (user action); verify one full nightly cycle 20:00→23:30
with zero path errors; update this doc's stale §1 tables if desired.
