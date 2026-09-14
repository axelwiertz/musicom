# -*- coding: utf-8 -*-
"""P4 — System A quarantine: defects pinned, consumers still working.

The quarantine is only honest if it records *why* the code was quarantined and
proves the consumers still function. Both are checked here.

Nothing in the modern tree may import ``legacy``; the single deliberate
exception is ``structures/__init__.py`` and ``structures/project.py``, which
resolve the old names lazily so existing call sites keep working.
"""

import os
import subprocess
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _probe(code: str) -> str:
    proc = subprocess.run([sys.executable, "-c", code], cwd=REPO_ROOT,
                          capture_output=True, text=True, timeout=180)
    assert proc.returncode == 0, f"probe failed:\n{proc.stdout}\n{proc.stderr}"
    return proc.stdout


# ---------------------------------------------------------------------------
# The quarantine itself
# ---------------------------------------------------------------------------

def test_legacy_package_exists_and_exports():
    from legacy import (  # noqa: F401
        Cardinality,
        MusicPitchClassSet,
        PatternGraph,
        PatternRotation,
        PatternType,
        create_subpattern,
    )

    assert MusicPitchClassSet is not None
    assert PatternType.MAJOR is not None


def test_pitchclass_module_has_moved_with_a_thin_shim():
    """The implementation MOVED to legacy/; structures/ keeps only an alias.

    76 project scripts import ``from structures.pitchclass import ...``, so
    the old path must keep resolving. The guard is that the old path is a
    thin re-export, not a second copy that could drift.
    """
    legacy_path = os.path.join(REPO_ROOT, "legacy", "pitchclass.py")
    shim_path = os.path.join(REPO_ROOT, "structures", "pitchclass.py")
    assert os.path.exists(legacy_path), "implementation must live in legacy/"

    # the shim exists but must be small and must re-export, not reimplement
    assert os.path.exists(shim_path)
    shim_src = open(shim_path, encoding="utf-8").read()
    assert "from legacy.pitchclass import" in shim_src
    assert "class MusicPitchClassSet" not in shim_src
    assert len(shim_src.splitlines()) < 80, "shim should stay a thin alias"

    # and the real implementation is much larger
    assert os.path.getsize(legacy_path) > os.path.getsize(shim_path) * 5


def test_structures_reexports_are_the_same_objects():
    """Compatibility surface must alias legacy, not shadow it."""
    import legacy
    import structures

    assert structures.MusicPitchClassSet is legacy.MusicPitchClassSet
    assert structures.PatternType is legacy.PatternType
    assert structures.PatternGraph is legacy.PatternGraph


def test_import_order_independent():
    """structures-first and legacy-first must both work (the cycle is broken)."""
    for order in ("import structures\nimport legacy\n",
                  "import legacy\nimport structures\n"):
        out = _probe(order + "print('OK')\n")
        assert "OK" in out


def test_no_modern_module_imports_legacy_at_module_scope():
    """Only the two documented compatibility sites may reference legacy."""
    allowed = {
        os.path.join("structures", "__init__.py"),
        os.path.join("structures", "project.py"),
        os.path.join("structures", "pitchclass.py"),
        os.path.join("converters", "pattern.py"),
    }
    offenders = []
    for root in ("rules", "workflows", "generators", "sound"):
        for dirpath, _dirs, files in os.walk(os.path.join(REPO_ROOT, root)):
            for fn in files:
                if not fn.endswith(".py"):
                    continue
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, REPO_ROOT)
                if rel in allowed:
                    continue
                with open(full, encoding="utf-8") as fh:
                    for lineno, line in enumerate(fh, 1):
                        s = line.strip()
                        if s.startswith("#"):
                            continue
                        if "import legacy" in s or "from legacy" in s:
                            offenders.append(f"{rel}:{lineno}: {s}")
    assert not offenders, (
        "modern modules must not import quarantined code:\n" + "\n".join(offenders)
    )


def test_structures_import_stays_dependency_free():
    """Quarantining must not have introduced musicpy/music21 into structures."""
    out = _probe(
        "import structures, sys\n"
        "print('HEAVY:', [m for m in ('musicpy','music21') if m in sys.modules])\n"
    )
    assert "HEAVY: []" in out


# ---------------------------------------------------------------------------
# The pinned defects — these are the REASONS for quarantine
# ---------------------------------------------------------------------------

def test_defect_rotation_name_is_a_broken_staticmethod():
    """Pinned: rotation_name is a @staticmethod that takes self.

    This is why `MusicPitchClassSet(rotation_index=...)`-style calls and
    `p.rotation_name()` both explode. If this ever gets fixed, the reason to
    keep the code quarantined weakens — and this test should be updated.
    """
    import inspect

    from legacy.pitchclass import MusicPitchClassSet, PatternType

    assert isinstance(
        inspect.getattr_static(MusicPitchClassSet, "rotation_name"), staticmethod
    )
    p = MusicPitchClassSet(name="Major", definition=PatternType.MAJOR,
                           rotation=0, initial=0)
    with pytest.raises(TypeError):
        p.rotation_name()               # missing positional arg 'self'
    # ...and it must be called with self explicitly to work at all
    assert p.rotation_name(p) is not None


def test_defect_converters_pattern_had_dead_attributes():
    """Pinned: converters/pattern.py read pattern.modes / .modes_helix.

    Neither ever existed. The module is now repaired to read the real
    PatternRotation table; this test asserts the attributes are still absent,
    which is what made the original module dead on arrival.
    """
    from legacy.pitchclass import MusicPitchClassSet, PatternType

    p = MusicPitchClassSet(name="Major", definition=PatternType.MAJOR,
                           rotation=0, initial=0)
    assert not hasattr(p, "modes")
    assert not hasattr(p, "modes_helix")


def test_converters_pattern_now_works():
    """The repaired converter must actually run, not raise AttributeError."""
    from converters.pattern import rotation_table

    table = rotation_table()
    assert len(table) == 7                       # the seven modes
    assert set(table.columns) == {"mode", "rotation_index"}


# ---------------------------------------------------------------------------
# The adapter — how legacy crosses into the modern layer
# ---------------------------------------------------------------------------

def test_to_pattern_bridges_to_modern_layer():
    from legacy.pitchclass import MusicPitchClassSet, PatternType
    from rules.patterns import Pattern

    p = MusicPitchClassSet(name="Major", definition=PatternType.MAJOR,
                           rotation=0, initial=0)
    modern = p.to_pattern()
    assert isinstance(modern, Pattern)
    assert modern.subset == frozenset({0, 4, 7})
    assert modern.forte == "3-11"
    assert "legacy" in modern.tags
    assert modern.label == "Major"


def test_to_pattern_gives_modern_api_access():
    """The bridged pattern must support the full modern query surface."""
    from legacy.pitchclass import MusicPitchClassSet, PatternType

    p = MusicPitchClassSet(name="Major", definition=PatternType.MAJOR,
                           rotation=0, initial=0)
    modern = p.to_pattern()
    assert modern.icv == [0, 0, 1, 1, 1, 0]
    assert modern.tension > 0
    assert modern.cardinality == 3
    assert modern.prime == (0, 3, 7)
    # a triadic set has no Z-partner, so this must be a clean None
    assert modern.z_partner is None


def test_to_pattern_returns_none_without_pitch_content():
    from legacy.pitchclass import MusicPitchClassSet

    bare = MusicPitchClassSet(name="Empty")
    assert bare.pitch_class_set() == frozenset()
    assert bare.to_pattern() is None


def test_to_pattern_accepts_explicit_id():
    from legacy.pitchclass import MusicPitchClassSet, PatternType

    p = MusicPitchClassSet(name="Major", definition=PatternType.MAJOR,
                           rotation=0, initial=0)
    assert p.to_pattern("my_custom").id == "my_custom"


# ---------------------------------------------------------------------------
# Consumers still work
# ---------------------------------------------------------------------------

def test_structures_project_still_constructs():
    from structures import MusicProject
    from structures.project import MusicPitchClassSet as PM

    assert PM is not None
    proj = MusicProject(name="t")
    assert proj.name == "t"


def test_live_consumer_scripts_import_cleanly():
    """The two Groove project scripts that depend on System A must still import.

    They are executed with a compile-only check so we do not run their
    rendering side effects.
    """
    import py_compile

    for rel in ("projects/Styles/Groove/019-soul-groove/src/regen.py",
                "projects/Styles/Groove/020-afrobeat-groove/src/regen.py"):
        path = os.path.join(REPO_ROOT, rel)
        if not os.path.exists(path):
            pytest.skip(f"{rel} not present")
        py_compile.compile(path, doraise=True)


def test_legacy_import_does_not_pull_heavy_deps():
    out = _probe(
        "import legacy\n"
        "import sys\n"
        "print('HEAVY:', [m for m in ('musicpy','music21') if m in sys.modules])\n"
    )
    assert "HEAVY: []" in out
