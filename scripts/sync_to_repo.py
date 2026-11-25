# -*- coding: utf-8 -*-
"""Musicom repo sync — COMMIT-ONLY (restructure 2026-09-08).

Pre-restructure this script COPIED the working tree (/opt/data/projects/...)
into the repo. Since the restructure moved the tree INTO the repo and the old
paths are symlinks, there is nothing to copy — every write already lands in the
repo working dir. The job now only:
  1. renders the docs indexes (instruments.md, methods.md, human-methods.md),
  2. git add + commit + push (with retry + rebase-on-divergence).

Keep the CLI/exit contract identical so the cron job (daily-repo-sync) works
unchanged.

NOTE: the live cron copy lives at /opt/data/scripts/sync_to_repo.py (the cron
`script:` field resolves under ~/scripts/, NOT ~/.hermes/scripts/). Keep all
three copies in sync (this file, ~/.hermes/scripts/, repo scripts/).
"""
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

HERMES = "/opt/data/projects"          # legacy root — still resolves via symlinks
REPO = "/opt/data/repos/musicom"
DOCS = os.path.join(REPO, "docs")
PUSH_RETRIES = 3
PUSH_RETRY_DELAY = 15


def log(msg):
    print(f"[sync] {msg}", flush=True)


def git(*args):
    r = subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True)
    return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()


def push_main():
    """Push origin/main, retrying transient failures and rebasing on divergence."""
    last = (1, "", "")
    for attempt in range(1, PUSH_RETRIES + 1):
        rc, out, err = git("push", "origin", "main")
        if rc == 0:
            return rc, out, err
        last = (rc, out, err)
        low = (out + err).lower()
        if "non-fast-forward" in low or "rejected" in low or "fetch first" in low:
            log(f"  push diverged — pull --rebase (attempt {attempt})")
            prc, _, perr = git("pull", "--rebase", "origin", "main")
            if prc != 0:
                log(f"  pull --rebase failed rc={prc}: {perr[:200]}")
        else:
            log(f"  push attempt {attempt} failed rc={rc}: {err[:200]}")
        if attempt < PUSH_RETRIES:
            time.sleep(PUSH_RETRY_DELAY)
    return last


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log(f"Musicom repo sync (commit-only) — {today}")

    # 1. Render docs indexes into docs/ (still generated, not hand-maintained)
    os.makedirs(DOCS, exist_ok=True)
    docs_n = 0
    copies = [
        (os.path.join(HERMES, "Instruments", "registry.md"), os.path.join(DOCS, "instruments.md")),
        (os.path.join(HERMES, "Research", "CompositionMethods", "methods_db.md"), os.path.join(DOCS, "methods.md")),
        (os.path.join(HERMES, "Research", "CompositionMethods", "human_methods_db.md"), os.path.join(DOCS, "human-methods.md")),
    ]
    for src, dst in copies:
        if os.path.exists(src):
            shutil.copy2(src, dst)
            docs_n += 1
    log(f"  docs/: {docs_n} files")

    # 2. Commit (working tree IS the repo — no copy step)
    rc, out, err = git("add", "-A", "docs", "projects")
    log(f"  git add: rc={rc} {err[:200] if err else ''}")
    rc, out, err = git("commit", "-m", f"sync: musicom agent data {today}")
    if rc == 0:
        log(f"  committed: {out.splitlines()[0] if out else 'ok'}")
    elif "nothing to commit" in (out + err):
        log("  nothing to commit (no changes)")
    else:
        log(f"  commit failed rc={rc}: {err[:300]}")
        sys.exit(1)

    # 3. Push with retry
    rc, out, err = push_main()
    if rc == 0:
        log(f"  pushed: {out.splitlines()[0] if out else 'ok'}")
    else:
        log(f"  push failed rc={rc}: {err[:300]}")
        sys.exit(1)

    rc, out, _ = git("log", "--oneline", "-3")
    log("recent commits:")
    for line in out.splitlines()[:3]:
        log(f"    {line}")
    log("DONE — committed + pushed")


if __name__ == "__main__":
    main()
