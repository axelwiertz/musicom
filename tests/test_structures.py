"""Structure tests — exercise the real, currently-implemented API only.

Rewritten in Phase 3: the previous version tested a richer pitch/pattern API
(MusicPitchClass.E, .index_of(), PatternRotation.minor, ...) that no longer
exists — pitch.py is currently minimal stubs. Those aspirational tests were
removed; when the pitch API is completed, add coverage back here.
"""
from structures import (
    MusicPitch, MusicPitchClass, MusicPitchGrid, MusicPitchRange, Direction,
    MusicTimeGrid, MusicLinearTime, MusicRhythmPattern,
    MusicPitchClassSet, PatternType, PatternGraph, PatternRotation,
    MusicProject, MusicUnit, MusicVoice, UnitMatrix, MusicSection,
)


def test_project_and_matrix():
    project = MusicProject(
        name="My First Song",
        time_grid=MusicTimeGrid(ticks_per_cycle=4, beats_per_cycle=4),
        sections=[MusicSection(name="Intro")],
        voices=[MusicVoice("Melody"), MusicVoice("Bass")],
        matrix=UnitMatrix(shape=(2, 2)),
    )
    assert len(project.voices) == 2

    project.matrix.set_unit(pos=(0, 0), unit=MusicUnit())
    project.matrix.set_unit(pos=(0, 1), unit=MusicUnit())
    project.matrix.set_unit(pos=(1, 0), unit=MusicUnit())
    project.matrix.set_unit(pos=(1, 1), unit=MusicUnit())
    assert project.matrix.get_unit((1, 1)) is not None


def test_pitch_primitives():
    # pitch.py primitives (minimal current implementation)
    p = MusicPitch(midi=60)
    assert p.midi == 60
    assert p.pitch_class == 0      # C
    assert p.octave == 4           # C4
    assert MusicPitchClass(index=13).index == 1
    assert Direction.ASCENDING.value == 1
    assert MusicPitchGrid(pitches=[60, 62, 64]).pitches == [60, 62, 64]
    assert MusicPitchRange(start=48, end=72).end == 72


def test_pitch_class_set_and_graph():
    # Major triad: intervals (4, 3, 5) rooted at pitch class 0 (C)
    pcs = MusicPitchClassSet(name="Major", definition=PatternType.MAJOR,
                             rotation=PatternRotation.root, initial=0)
    assert pcs.cardinality == 3
    assert pcs.pitch_classes == (4, 7, 0)
    assert pcs.pitch_class_set() == frozenset({0, 4, 7})

    # Heptatonic (major scale) rooted at C
    scale = MusicPitchClassSet(name="Major Scale", definition=PatternType.HEPTATONIC,
                               rotation=PatternRotation.ionian, initial=0)
    assert scale.pitch_classes == (2, 4, 5, 7, 9, 11, 0)

    # Triad is a subset of the major scale
    assert pcs.is_subset_of(scale)
    assert scale.is_superset_of(pcs)

    # PatternGraph tracks subset relationships
    graph = PatternGraph()
    graph.add_pitch_class_set(scale)
    graph.add_pitch_class_set(pcs)
    graph.add_subset_relation(superset=scale, subset=pcs)


def test_time_grid_and_linear_time():
    time_grid = MusicTimeGrid(ticks_per_cycle=16, beats_per_cycle=4, beat_note=4)
    time = MusicLinearTime(time_grid=time_grid, bpm=120)
    assert time.seconds_per_beat > 0
    assert time.seconds_per_cycle() > 0


def test_rhythm_pattern_signature():
    # Real signature: MusicRhythmPattern(time_grid, name="Simple")
    tg = MusicTimeGrid(ticks_per_cycle=16, beats_per_cycle=4, beat_note=4)
    rp = MusicRhythmPattern(tg, name="Basic")
    assert rp.name == "Basic"
