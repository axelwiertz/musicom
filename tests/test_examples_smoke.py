# -*- coding: utf-8 -*-
"""Smoke test for the curated examples — each must run headless as a script.

Proves the no-dependency path: SP-011 (Karplus-Strong) renders without a
SoundFont, and the reverse/transform examples run on a bare install (no
music21, no display, no network).
"""
import os
import subprocess
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CURATED = [
    "compose_simple.py",
    "transform_simple.py",
    "analyze_simple.py",
    "produce_simple.py",
]


@pytest.mark.parametrize("name", CURATED)
def test_curated_example_runs(name):
    path = os.path.join(REPO, "examples", name)
    r = subprocess.run(
        [sys.executable, path],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"{name} failed:\n--- stdout ---\n{r.stdout}\n--- stderr ---\n{r.stderr}"
