"""Doc smoke test: proves the code shown in README.md / QUICK_REFERENCE.md /
AGENTS.md runs against the real API. If this fails, the docs have drifted.

Added in Phase 1 (docs-truth). Keep the snippets here in sync with the docs.
"""
import os
import tempfile

from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
from workflows.unitmatrix_composer import (
    UnitMatrixComposer,
    create_note_unit,
    create_chord_unit,
    create_empty_unit,
    create_blues_form_matrix,
)


def test_musicunit_basics():
    melody = MusicUnit(events=[
        MusicEvent(60, 100, 0, 480),
        MusicEvent(62, 100, 480, 960),
        MusicEvent(64, 100, 960, 1440),
    ])
    assert melody.pitches == [60, 62, 64]
    assert melody.volumes == [100, 100, 100]
    assert melody.pitch_intervals == [2, 2]
    assert melody.onset_intervals == [480, 480]
    assert melody.len_ticks() == 1440
    assert len(melody) == 3
    # Known quirk: duration is 0 when start_tick == 0.
    assert melody.durations == [0, 480, 480]


def test_musicunit_ops():
    melody = MusicUnit(events=[MusicEvent(60, 100, 0, 480), MusicEvent(62, 100, 480, 960)])
    melody.transpose(12)
    assert melody.pitches == [72, 74]
    a, b = melody.split(1)
    assert len(a) == 1 and len(b) == 1
    assert len(a + b) == 2


def test_unitmatrix_direct():
    m = UnitMatrix(shape=(2, 2))
    unit = create_note_unit(60, 1920)
    m.set_unit((0, 0), unit)
    assert m.get_unit((0, 0)) is not None


def test_composer_zero_drift_export():
    composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=3, num_sections=1)
    composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
    composer.add_voice("Chord", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
    composer.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
    composer.add_section("A", bars=1)

    bar = 480 * 4
    composer.fill_voice_section("Lead", "A", create_note_unit(72, bar))
    composer.fill_voice_section("Chord", "A", create_chord_unit([60, 64, 67], bar))
    composer.fill_voice_section("Bass", "A", create_note_unit(36, bar))

    ok, msg = composer.validate()
    assert ok, msg

    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "out.mid")
        composer.to_midi(out)
        # Verify-don't-trust: non-empty artifact (empties are 16-22 bytes).
        assert os.path.getsize(out) > 40


def test_blues_form_helper():
    composer, info = create_blues_form_matrix(bpm=80, num_bars=12)
    assert info["form"] == "12-bar blues"
    assert len(info["sections"]) == 3
