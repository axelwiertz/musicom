from rules import (
    Scale7PitchDegree,
    Scale7ChordDegree,
    PatternMovement,
    PatternProgressions,
    Counterpoint,
)
from rules.movement import Scale7DegreeFunction
from rules.progression import PatternMovementRules, MusicForm


def test_pattern():
    # Common chord progression patterns are well-formed
    assert PatternMovement.bestseller_progression == (1, 5, 6, 4)
    assert PatternMovement.fifties_progression == (1, 6, 2, 5)
    assert PatternMovement.minor_pop_progression == (1, 7, 6, 7)
    assert PatternMovement.flamenco_progression == (1, 7, 6, 5)

    # Cadence progressions cover the four classical cadence types
    cadences = PatternMovement.cadence_progressions
    assert set(cadences.keys()) == {"Perfect", "Plagal", "Imperfect", "Interrupted"}
    assert cadences["Perfect"] == (5, 1)
    assert cadences["Plagal"] == (4, 1)

    # Pre-built blues forms have the expected number of one-bar cells
    assert len(PatternProgressions.blues12_major_progression) == 3
    assert len(PatternProgressions.blues8_major_progression) == 3
    for cell in PatternProgressions.blues12_major_progression:
        assert len(cell) == 4

    # Music forms expose their section patterns
    form = MusicForm("Ternary", MusicForm.common_section_patterns["Ternary"])
    assert form.section_pattern == ("A", "B", "A")


def test_movement():
    # Scale degree functions
    assert Scale7DegreeFunction.degree_functions[1] == "tonic"
    assert Scale7DegreeFunction.degree_functions[5] == "dominant"
    assert Scale7DegreeFunction.degree_functions[7] == "leading tone"

    # Voice pitch movement: ANY wildcard is 0
    assert Scale7PitchDegree.ANY == 0
    # Active degrees (2,4,6,7) resolve by step; stable degrees (1,3,5) are free
    assert Scale7PitchDegree.movement_rules[1] == Scale7PitchDegree.ANY
    assert Scale7PitchDegree.movement_rules[7] == 1
    assert Scale7PitchDegree.movement_rules[4] == -1

    # Chord-degree harmonic functions
    assert Scale7ChordDegree.function[Scale7ChordDegree.TONIC] == 1
    assert Scale7ChordDegree.function[Scale7ChordDegree.DOMINANT] == (7, 5)
    assert Scale7ChordDegree.function[Scale7ChordDegree.SUBDOMINANT] == (4, 2)

    # Triad movement rules: dominant (5) resolves to tonic (1)
    assert PatternMovementRules.movement_rules[5] == 1
    assert PatternMovementRules.movement_rules[7] == 1

    # Diatonic pitch lookup for C major (cumulative intervals from the root)
    c_major = [0, 2, 4, 5, 7, 9, 11]
    assert Scale7ChordDegree.get_diatonic_note(60, c_major, 0) == 60  # C
    assert Scale7ChordDegree.get_diatonic_note(60, c_major, 2) == 64  # E
    assert Scale7ChordDegree.get_diatonic_note(60, c_major, 7) == 72  # C an octave up
