# -*- coding: utf-8 -*-
"""P0 regression net — the generator package must not drag in musicpy/music21.

Background: ``generators/__init__.py`` used to eagerly import every generator.
Because Python executes a package ``__init__`` on *any* submodule import,
``import generators.generator_registry`` (a pure data table, imported by
``workflows/selector.py`` and ``workflows/paths.py``) pulled in
``chord_degrees`` -> ``converters.musicpy_converter`` (musicpy) and
``harmonics`` -> music21.

A composition job once burned its entire budget fixing those converters
instead of composing. These tests pin the lazy-import fix.

The dependency checks run in a SUBPROCESS so that unrelated tests importing
musicpy earlier in the session cannot pollute ``sys.modules`` and mask a
regression.
"""

import os
import subprocess
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _run_probe(code: str) -> str:
    """Run *code* in a fresh interpreter and return stdout."""
    proc = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert proc.returncode == 0, (
        f"probe failed (exit {proc.returncode})\n"
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    return proc.stdout


@pytest.mark.parametrize(
    "import_stmt",
    [
        "import generators",
        "import generators.generator_registry",
        "from generators.generator_registry import GENERATOR_REGISTRY",
    ],
)
def test_import_leaves_musicpy_absent(import_stmt):
    """Neither musicpy nor music21 may load on the registry import path."""
    out = _run_probe(
        f"{import_stmt}\n"
        "import sys\n"
        "loaded = [m for m in ('musicpy', 'music21') if m in sys.modules]\n"
        "print('LOADED:' + ','.join(loaded))\n"
    )
    line = [l for l in out.splitlines() if l.startswith("LOADED:")][0]
    assert line == "LOADED:", (
        f"`{import_stmt}` pulled in heavy deps: {line[7:]!r} — "
        "generators/__init__.py must resolve names lazily (PEP 562)."
    )


def test_rules_and_structures_are_pure():
    """The abstract layers stay dependency-free (mirrors subset_network docstring)."""
    out = _run_probe(
        "import rules.set_theory, rules.subset_network, structures\n"
        "import sys\n"
        "loaded = [m for m in ('musicpy', 'music21') if m in sys.modules]\n"
        "print('LOADED:' + ','.join(loaded))\n"
    )
    line = [l for l in out.splitlines() if l.startswith("LOADED:")][0]
    assert line == "LOADED:", f"rules/structures pulled in heavy deps: {line[7:]!r}"


def test_all_exported_names_still_resolve():
    """Lazy resolution must keep every documented name importable."""
    from generators import (  # noqa: F401
        ChordDegreeGenerator,
        GeneticGenerator,
        HarmonicsGenerator,
        MarkovChainGenerator,
        PatternGenerator,
        RhythmGenerator,
        StochasticGenerator,
        TintinnabuliGenerator,
        TonalNetworkGenerator,
        isorhythmize,
    )

    assert callable(RhythmGenerator)
    assert callable(TonalNetworkGenerator)
    assert callable(TintinnabuliGenerator)
    assert callable(isorhythmize)


def test_rhythm_generator_import_is_light():
    """The 75 project scripts importing RhythmGenerator must stay cheap.

    ``rhythm.py`` is dependency-free, so pulling it in must not fire the
    heavy generators' imports.
    """
    out = _run_probe(
        "from generators import RhythmGenerator\n"
        "import sys\n"
        "loaded = [m for m in ('musicpy', 'music21') if m in sys.modules]\n"
        "print('LOADED:' + ','.join(loaded))\n"
    )
    line = [l for l in out.splitlines() if l.startswith("LOADED:")][0]
    assert line == "LOADED:", (
        f"importing RhythmGenerator pulled in {line[7:]!r} — lazy resolution "
        "should only import generators.rhythm."
    )


def test_attribute_error_for_unknown_name():
    import generators

    with pytest.raises(AttributeError):
        _ = generators.NoSuchGeneratorExists


def test_dir_includes_lazy_names():
    import generators

    listed = dir(generators)
    for name in ("RhythmGenerator", "TonalNetworkGenerator", "ChordDegreeGenerator"):
        assert name in listed
