# -*- coding: utf-8 -*-
"""Regression tests for mode-aware roman-numeral degree parsing.

Locks in the fix for the static-harmony bug: the historical root lookup
did `MAJOR_DEGREES.index(deg.upper())`, so every uppercase minor-mode
degree (VI/III/VII in an aeolian progression) and every lowercase
major-mode degree (ii/iii/vi/vii) collapsed onto index 0. The result was
all-tonic harmony: e.g. i-VI-III-VII in D produced [38, 38, 38, 38].

Canonical implementation: rules/harmony.py (progression_roots and the
degree helpers), re-exported through workflows.paths.progression_roots.
"""
import pytest

from rules.harmony import (
    degree_offset, infer_mode, parse_degree, progression_roots,
    tonic_offset,
)
from workflows.paths import progression_roots as paths_progression_roots


# ------------------------------------------------------------ parse_degree --

def test_parse_degree_index_case_insensitive():
    assert parse_degree("I")[0] == 0
    assert parse_degree("i")[0] == 0
    assert parse_degree("vi")[0] == 5
    assert parse_degree("VI")[0] == 5
    assert parse_degree("VII")[0] == 6
    assert parse_degree("iii")[0] == 2


def test_parse_degree_accidentals_and_suffixes():
    assert parse_degree("bVII") == (6, -1)
    assert parse_degree("#IV") == (3, 1)
    # quality / extension suffixes are ignored
    assert parse_degree("ii°")[0] == 1
    assert parse_degree("V7")[0] == 4


def test_parse_degree_rejects_garbage():
    for bad in ("", "  ", "X", "VIII", "banana", None, 7):
        with pytest.raises(ValueError):
            parse_degree(bad)


# ----------------------------------------------------------- degree_offset --

def test_degree_offset_major():
    assert degree_offset("I", "major") == 0
    assert degree_offset("V", "major") == 7
    assert degree_offset("vi", "major") == 9
    assert degree_offset("vii", "major") == 11


def test_degree_offset_minor_aeolian():
    # aeolian: b3, b6, b7 relative to the tonic
    assert degree_offset("i", "minor") == 0
    assert degree_offset("III", "minor") == 3
    assert degree_offset("VI", "minor") == 8
    assert degree_offset("VII", "minor") == 10


def test_degree_offset_minor_flat_is_idempotent():
    # the aeolian table already carries the flat, so bIII == III
    assert degree_offset("bIII", "minor") == degree_offset("III", "minor")
    assert degree_offset("bVI", "minor") == degree_offset("VI", "minor")
    # a sharp still applies (harmonic-minor leading tone)
    assert degree_offset("#VII", "minor") == 11


def test_degree_offset_bad_mode():
    with pytest.raises(ValueError):
        degree_offset("I", "lydian")


# ------------------------------------------------------- mode / key wiring --

def test_infer_mode():
    assert infer_mode("D", ["i", "VI"]) == "minor"
    assert infer_mode("Dm", ["I", "V"]) == "minor"
    assert infer_mode("D", ["I", "V"]) == "major"
    assert infer_mode("C", None) == "major"


def test_tonic_offset_minor_key_uses_letter():
    assert tonic_offset("D") == 2
    assert tonic_offset("Dm") == 2
    assert tonic_offset("Am") == 9
    assert tonic_offset("F") == 5


# -------------------------------------------------------- progression_roots --

def test_minor_progression_roots_vary():
    """The bug: i-VI-III-VII in D used to be [38, 38, 38, 38]."""
    roots = progression_roots(["i", "VI", "III", "VII"], 4, "D")
    assert roots == [38, 46, 41, 48]          # D2, Bb2, F2, C3
    assert len(set(roots)) == 4, "harmony must not be static"


def test_minor_roots_tile_over_bars():
    roots = progression_roots(["i", "VI", "III", "VII"], 8, "D")
    assert roots == [38, 46, 41, 48, 38, 46, 41, 48]


def test_harmonic_rhythm_holds_each_chord():
    roots = progression_roots(["i", "VI", "III", "VII"], 8, "D",
                              harmonic_rhythm=2)
    assert roots == [38, 38, 46, 46, 41, 41, 48, 48]


def test_major_progression_roots():
    assert progression_roots(["I", "V", "vi", "IV"], 4, "C") == [36, 43, 45, 41]
    assert progression_roots(["I", "V", "vi", "IV"], 4, "D") == [38, 45, 47, 43]


def test_minor_key_suffix_equivalent_to_bare_key():
    a = progression_roots(["i", "VI", "III", "VII"], 4, "D")
    b = progression_roots(["i", "VI", "III", "VII"], 4, "Dm")
    assert a == b


def test_paths_reexport_matches_canonical():
    prog = ["i", "VI", "III", "VII"]
    assert paths_progression_roots(prog, 8, "D") == \
        progression_roots(prog, 8, "D")


def test_empty_progression_rejected():
    with pytest.raises(ValueError):
        progression_roots([], 4, "C")
