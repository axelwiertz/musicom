# -*- coding: utf-8 -*-
"""Reverse-path tests: compose() -> analyze_midi() round-trip.

Proves the reverse entry point reconstructs key / progression / Forte / grid
from a composed MIDI, fully headless (no music21, no display, no network).
"""

import pytest


def _unique_in_order(seq):
    out = []
    for x in seq:
        if not out or out[-1] != x:
            out.append(x)
    return out


@pytest.fixture(scope="module")
def composed(tmp_path_factory):
    from workflows.musicom_workflow import compose
    d = tmp_path_factory.mktemp("analyze_roundtrip")
    r = compose(style="pop", key="C", bpm=120, out_dir=str(d))
    return r


def test_roundtrip_key_and_progression(composed):
    from workflows.analyze import analyze_midi
    rep = analyze_midi(composed.midi_path, key="C")
    assert rep.key == "C"
    assert rep.mode == "major"
    # 5 sections hold I - V - vi - IV - I
    assert _unique_in_order(rep.roman_progression) == ["I", "V", "vi", "IV", "I"]
    assert rep.total_notes > 0
    assert rep.grid  # non-empty high-contrast grid


def test_key_estimate_detects_c_major(composed):
    from workflows.analyze import analyze_midi
    rep = analyze_midi(composed.midi_path)
    assert rep.key == "C"
    assert rep.mode == "major"


def test_forte_names_are_major_minor_triads(composed):
    from workflows.analyze import analyze_midi
    rep = analyze_midi(composed.midi_path, key="C")
    assert "3-11" in rep.forte_names  # major/minor triad set class


def test_analysis_import_is_pure():
    # Importing workflows.analyze must NOT load musicpy/music21 (purity
    # invariant). Run in a fresh interpreter so prior test imports don't
    # pollute sys.modules.
    import subprocess
    import sys
    code = (
        "import sys; "
        "from workflows.analyze import analyze_midi; "
        "print('music21' in sys.modules, 'musicpy' in sys.modules)"
    )
    out = subprocess.run([sys.executable, "-c", code],
                         capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "False False"

