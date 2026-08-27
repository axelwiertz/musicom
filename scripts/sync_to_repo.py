#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily sync: Musicom Agent data → musicom repo (docs + artifacts).

Copies documentation + compact artifacts from the Hermes working FS into
the musicom repo, stages, and commits. Hermes FS stays the working tree
(jobs write there); repo holds the versioned, synced documentation.

User decision (2026-08-27):
- Keep Hermes Agent standard file system (working location)
- Sync ALL documentation into the musicom repo daily
- Store musicom files (scripts, MIDI, OGG, MD, JSON, TXT) as much as possible
- WAV ignored (large, renderable from MIDI); .env ignored (secrets)

Run: /opt/data/micromamba/envs/musicom/bin/python sync_to_repo.py
"""
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

HERMES = "/opt/data/projects"
REPO = "/opt/data/repos/musicom"
DOCS = os.path.join(REPO, "docs")

# (source under HERMES, dest under REPO) — md/json/py/mid/ogg/txt synced
SYNC_PAIRS = [
    # Styles: composition projects (docs + MIDI + OGG, skip WAV)
    ("Styles", os.path.join("projects", "Styles")),
    # Research: methods DB + reports + newsletters
    ("Research", os.path.join("projects", "Research")),
    # Instruments KB
    ("Instruments", os.path.join("projects", "Instruments")),
]

# Extensions to copy (compact, versioned). WAV excluded (renderable from MIDI),
# OGG included (small, playable — user decision #1 "track .ogg").
KEEP_EXT = {".md", ".py", ".json", ".mid", ".ogg", ".txt", ".yaml", ".yml", ".toml"}
SKIP_DIRS = {"__pycache__", ".git", ".idea", ".vscode", "_test", "node_modules", ".venv", "outputs"}


def log(msg):
    print(f"[sync] {msg}", flush=True)


def should_copy(rel):
    ext = os.path.splitext(rel)[1].lower()
    return ext in KEEP_EXT


def sync_tree(src_root, dst_root):
    """Copy KEEP_EXT files from src_root into dst_root, mirroring structure."""
    n = 0
    if not os.path.isdir(src_root):
        log(f"  skip missing source: {src_root}")
        return n
    for dirpath, dirnames, filenames in os.walk(src_root):
        rel_dir = os.path.relpath(dirpath, src_root)
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            src = os.path.join(dirpath, fn)
            rel = os.path.join(rel_dir, fn) if rel_dir != "." else fn
            if not should_copy(rel):
                continue
            dst = os.path.join(dst_root, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            n += 1
    return n


def git(*args):
    r = subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True)
    return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log(f"Musicom sync to repo — {today}")
    total = 0

    # 1. Copy tracked extensions from Hermes FS into repo projects/
    for src, dst in SYNC_PAIRS:
        s = os.path.join(HERMES, src)
        d = os.path.join(REPO, dst)
        os.makedirs(d, exist_ok=True)
        n = sync_tree(s, d)
        log(f"  {src} → projects/{src}: {n} files")
        total += n

    # 2. Render docs index (registry + methods summaries) into docs/
    os.makedirs(DOCS, exist_ok=True)
    docs_n = 0
    reg_src = os.path.join(HERMES, "Instruments", "registry.md")
    if os.path.exists(reg_src):
        shutil.copy2(reg_src, os.path.join(DOCS, "instruments.md"))
        docs_n += 1
    methods_src = os.path.join(HERMES, "Research", "CompositionMethods", "methods_db.md")
    if os.path.exists(methods_src):
        shutil.copy2(methods_src, os.path.join(DOCS, "methods.md"))
        docs_n += 1
    human_src = os.path.join(HERMES, "Research", "CompositionMethods", "human_methods_db.md")
    if os.path.exists(human_src):
        shutil.copy2(human_src, os.path.join(DOCS, "human-methods.md"))
        docs_n += 1
    log(f"  docs/: {docs_n} files")

    # 3. Commit
    rc, out, err = git("add", "-A", "docs", "projects")
    log(f"  git add: rc={rc} {err[:200] if err else ''}")
    rc, out, err = git("commit", "-m", f"sync: musicom agent data {today} ({total} files)")
    if rc == 0:
        log(f"  committed: {out.splitlines()[0] if out else 'ok'}")
    else:
        # rc 1 = nothing to commit (no changes)
        if "nothing to commit" in (out + err):
            log("  nothing to commit (no changes)")
        else:
            log(f"  commit failed rc={rc}: {err[:300]}")
            sys.exit(1)

    # 4. Report stats
    rc, out, _ = git("log", "--oneline", "-3")
    log("recent commits:")
    for line in out.splitlines()[:3]:
        log(f"    {line}")
    log(f"DONE — {total} files synced, committed")


if __name__ == "__main__":
    main()
