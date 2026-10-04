# -*- coding: utf-8 -*-
"""utilities/env.py — ONE-ENV path/binary resolution contract.

Every musicom process (cron jobs, examples, workflows, tests) should resolve
the python interpreter, fluidsynth binary, and soundfont through this module
instead of hardcoding /opt/data/... absolute paths (RESTRUCTURE plan §1.3).

Resolution order — env var → explicit default → discovery:
  MUSICOM_ROOT        repo root (fallback: repo-relative parent of this file)
  MUSICOM_PYTHON      python interpreter for the musicom env
  MUSICOM_FLUIDSYNTH  fluidsynth binary
  MUSICOM_SOUNDFONT   preferred soundfont path

All accessors are lazy (no side effects at import) and never raise — a missing
env var falls back to a discoverable default so old callers keep working.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def _here() -> Path:
    return Path(__file__).resolve()


def repo_root() -> Path:
    """Repo root: $MUSICOM_ROOT, else the repo-relative location of this file."""
    env = os.environ.get("MUSICOM_ROOT")
    if env:
        return Path(env)
    # utilities/env.py -> repo root is two levels up
    return _here().parent.parent


def env_dir() -> Path:
    """Musicom env dir: $MUSICOM_ENV, else the sibling micromamba env."""
    env = os.environ.get("MUSICOM_ENV")
    if env:
        return Path(env)
    # repo-relative: repo root is <prefix>/repos/musicom -> env at <prefix>/micromamba/envs/musicom
    return repo_root().parent.parent / "micromamba" / "envs" / "musicom"


def python_bin() -> str:
    """The musicom python interpreter (env var first, then env dir, then current)."""
    env = os.environ.get("MUSICOM_PYTHON")
    if env and os.path.exists(env):
        return env
    cand = env_dir() / "bin" / "python"
    if cand.exists():
        return str(cand)
    return shutil.which("python") or "python"


def fluidsynth_bin() -> str:
    """The fluidsynth binary ($MUSICOM_FLUIDSYNTH, env dir, or PATH)."""
    env = os.environ.get("MUSICOM_FLUIDSYNTH")
    if env and os.path.exists(env):
        return env
    cand = env_dir() / "bin" / "fluidsynth"
    if cand.exists():
        return str(cand)
    return shutil.which("fluidsynth") or "fluidsynth"


def soundfont_path() -> str:
    """Preferred soundfont: $MUSICOM_SOUNDFONT, else discovery result."""
    env = os.environ.get("MUSICOM_SOUNDFONT")
    if env and os.path.exists(env):
        return env
    try:
        from sound.render.fluidsynth import discover_soundfont
        found = discover_soundfont()
        if found:
            return found
    except Exception:
        pass
    return ""


def run_python(args, **kwargs):
    """Run a subprocess with the musicom python. Returns CompletedProcess."""
    return subprocess.run([python_bin(), *args], **kwargs)


if __name__ == "__main__":
    print(f"repo_root      = {repo_root()}")
    print(f"env_dir        = {env_dir()}")
    print(f"python_bin     = {python_bin()}")
    print(f"fluidsynth_bin = {fluidsynth_bin()}")
    print(f"soundfont_path = {soundfont_path()}")
