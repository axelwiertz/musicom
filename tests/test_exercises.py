# -*- coding: utf-8 -*-
"""P5 — exercises: the registry runs, verifies, and exports."""

import os

import pytest

from rules.exercises import (
    ABSTRACT_EXERCISES,
    CONCRETE_EXERCISES,
    EXERCISE_REGISTRY,
    Exercise,
    ExerciseResult,
    list_exercises,
    run_exercise,
)

# ---------------------------------------------------------------------------
# Registry integrity
# ---------------------------------------------------------------------------

def test_registry_has_8_exercises():
    assert len(EXERCISE_REGISTRY) == 8
    assert len(ABSTRACT_EXERCISES) == 4
    assert len(CONCRETE_EXERCISES) == 4


def test_ids_are_wellformed_and_unique():
    ids = list(EXERCISE_REGISTRY)
    assert len(ids) == len(set(ids))
    for eid in ids:
        assert eid.startswith(("ABS-EX-", "CON-EX-"))
        layer = "abstract" if eid.startswith("ABS") else "concrete"
        assert EXERCISE_REGISTRY[eid].layer == layer


def test_registry_entries_are_data_not_closures():
    """The registry maps id -> Exercise (dataclass), not id -> callable."""
    for ex in EXERCISE_REGISTRY.values():
        assert isinstance(ex, Exercise)
        assert ex.fn.startswith("_")


def test_list_exercises_filters_by_layer():
    assert len(list_exercises("abstract")) == 4
    assert len(list_exercises("concrete")) == 4
    assert all(e.layer == "abstract" for e in list_exercises("abstract"))


def test_unknown_exercise_raises():
    with pytest.raises(KeyError):
        run_exercise("NOPE-EX-999")


# ---------------------------------------------------------------------------
# Every exercise runs and verifies
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ex_id", sorted(EXERCISE_REGISTRY))
def test_exercise_passes_its_own_assertions(ex_id):
    result = run_exercise(ex_id)
    assert result.ok, (
        f"{ex_id} failed: {[(n, m) for n, ok, m in result.failed]}"
    )
    assert result.checks, "exercise produced no checks at all"
    assert not result.artifacts, "no MIDI unless to_midi=True"


def test_exercise_results_record_failures():
    """The result object must record failures, not raise past them."""
    r = ExerciseResult(exercise_id="x", ok=True, layer="abstract")
    assert r.check("always", True) is True
    assert r.check("never", False, "because") is False
    assert r.failed == [("never", False, "because")]
    r.ok = not r.failed
    assert r.ok is False


# ---------------------------------------------------------------------------
# The exercises' musical content is real
# ---------------------------------------------------------------------------

def test_z_swap_exercise_uses_the_standard_library_z_tetrad():
    """The carrier must be 4-Z29 (the only Z tetrad in the standard library)."""
    result = run_exercise("ABS-EX-001")
    assert result.ok
    assert result.data["progression"][1] == "z0137"
    assert result.data["swapped"][1] == "z0146"
    # same tension, different harmony — the whole point
    from rules.patterns import standard_patterns

    lib = {p.id: p for p in standard_patterns()}
    a, b = lib["z0137"], lib["z0146"]
    assert a.tension == b.tension
    assert a.prime != b.prime


def test_tension_arc_exercise_is_calibrated():
    """Targets must match the standard library's actual tension values."""
    result = run_exercise("ABS-EX-002")
    assert result.ok
    assert result.data["picked"][3] == "dom70"       # peak = dominant 7th
    assert result.data["picked"][0] == result.data["picked"][4]  # resolves


def test_mode_walk_exercise_covers_all_seven_modes():
    result = run_exercise("ABS-EX-004")
    assert result.ok
    assert len(result.data["modes"]) == 7


def test_cardinality_expansion_grows_smoothly():
    result = run_exercise("ABS-EX-003")
    assert result.ok
    assert result.data["ladder"] == ["maj0", "maj70", "wholetone"]


# ---------------------------------------------------------------------------
# Concrete layer — MIDI export path
# ---------------------------------------------------------------------------

def test_concrete_exercise_exports_validated_midi(tmp_path):
    result = run_exercise("CON-EX-001", to_midi=True, out_dir=str(tmp_path))
    assert result.ok
    assert len(result.artifacts) == 1
    path = result.artifacts[0]
    assert os.path.getsize(path) > 40, "empty/corrupt artifact"
    # the zero-drift gate must have run as one of the checks
    names = [n for n, ok, _ in result.checks]
    assert "zero-drift-validate" in names
    assert "artifact-non-empty" in names


def test_abstract_exercise_never_exports_midi(tmp_path):
    result = run_exercise("ABS-EX-001", to_midi=True, out_dir=str(tmp_path))
    assert result.ok
    assert result.artifacts == []
    assert os.listdir(str(tmp_path)) == []


def test_exercise_midi_is_structurally_sound(tmp_path):
    """Exported MIDI must be readable and end at exactly 4 bars."""
    import mido

    result = run_exercise("CON-EX-001", to_midi=True, out_dir=str(tmp_path))
    mid = mido.MidiFile(result.artifacts[0])
    assert mid.type == 1
    assert len(mid.tracks) == 2          # tempo track + Lead
    # 4 bars * 4 beats * 480 tpq = 7680 ticks
    track = max(mid.tracks, key=lambda t: sum(m.time for m in t))
    assert sum(m.time for m in track) == 7680


def test_exercise_module_is_pure():
    import subprocess
    import sys

    code = (
        "import rules.exercises, sys\n"
        "bad = [m for m in ('musicpy','music21') if m in sys.modules]\n"
        "print('BAD:' + ','.join(bad))\n"
    )
    proc = subprocess.run([sys.executable, "-c", code],
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr
    line = [l for l in proc.stdout.splitlines() if l.startswith("BAD:")][0]
    assert line == "BAD:", f"rules.exercises pulled in {line[4:]!r}"
