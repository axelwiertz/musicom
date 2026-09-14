# -*- coding: utf-8 -*-
"""Doc-drift guard for docs/patterns.md.

Every code claim on that page is re-executed here. If the API drifts and the
docs go stale, this file fails — the docs are treated like the golden hash:
verified, not trusted.

Keep the snippets in sync with docs/patterns.md (same discipline as
tests/test_docs_smoke.py).
"""

import os
import tempfile

from rules.set_theory import (
    all_sets_of_cardinality,
    all_z_pairs,
    forte_name,
    interval_vector,
    pcs_from_forte,
    prime_form,
    z_partner,
)


def test_kernel_snippets():
    assert forte_name([0, 4, 7]) == "3-11"
    assert forte_name([0, 1, 4, 6]) == "4-Z15"
    assert z_partner([0, 1, 4, 6]) == frozenset({0, 1, 3, 7})
    assert len(all_z_pairs(6)) == 15
    assert pcs_from_forte("4-Z15") == frozenset({0, 1, 4, 6})
    assert len(all_sets_of_cardinality(3)) == 12


def test_library_snippets():
    from rules.patterns import (
        Pattern,
        chromatic_tetrads,
        chromatic_triads,
        standard_patterns,
        z_pair_catalogue,
    )

    p = Pattern("my_chord", frozenset({0, 1, 3, 7}))
    assert p.forte == "4-Z29"
    assert p.z_partner.forte == "4-Z15"
    assert len(chromatic_triads()) == 48
    assert len(chromatic_tetrads()) == 60
    assert len(standard_patterns()) == 91

    a, b = z_pair_catalogue(4)[0]
    assert {a.forte, b.forte} == {"4-Z15", "4-Z29"}


def test_realize_snippets():
    from rules.patterns import Pattern, RhythmPattern, patterns_from_degrees
    from rules.realize import place_in_register, realize, realize_progression
    from structures.unit import MusicEvent

    p = Pattern("my_chord", frozenset({0, 1, 3, 7}))

    events = realize(p, register=(48, 72), bar_ticks=1920)
    assert events
    events = realize_progression(
        patterns_from_degrees(0, ("I", "V", "vi", "IV")),
        register=(48, 72), bars_per_pattern=1, smooth=True,
    )
    assert events
    events = realize(p, register=(48, 72),
                     rhythm=RhythmPattern("tresillo", 8, (0, 3, 6)))
    assert events
    assert all(isinstance(e, MusicEvent) for e in events)


def test_exercise_snippets():
    from rules.exercises import list_exercises, run_exercise

    result = run_exercise("ABS-EX-001")
    assert result.ok
    assert result.checks
    assert len(list_exercises()) == 8

    with tempfile.TemporaryDirectory() as d:
        result = run_exercise("CON-EX-001", to_midi=True, out_dir=d)
        assert result.ok
        assert len(result.artifacts) == 1
        assert os.path.getsize(result.artifacts[0]) > 40


def test_legacy_bridge_snippet():
    from legacy.pitchclass import MusicPitchClassSet, PatternType

    modern = MusicPitchClassSet(
        "Dorian", PatternType.HEPTATONIC, rotation=1, initial=2
    ).to_pattern()
    assert modern.forte == "7-35"
