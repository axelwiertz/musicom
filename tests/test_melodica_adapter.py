# Copyright (c) 2026 Axel Wiertz / Musicom
#
# Licensed under the MIT License.

"""Unit tests for MelodicaToMatrixConverter."""

import pytest
from structures import UnitMatrix, MusicUnit
from converters.melodica_adapter import MelodicaExchangeNote, MelodicaToMatrixConverter

def test_single_cell_conversion():
    # Instantiate converter
    converter = MelodicaToMatrixConverter(bpm=120.0, ticks_per_beat=960)

    # 1. Notes completely inside cell boundaries [0.0, 4.0)
    notes = [
        MelodicaExchangeNote(pitch=60, start_beat=0.0, duration_beats=1.0, velocity=100),
        MelodicaExchangeNote(pitch=64, start_beat=2.0, duration_beats=0.5, velocity=90),
        # This note starts outside cell and must be bypassed
        MelodicaExchangeNote(pitch=67, start_beat=4.5, duration_beats=1.0, velocity=110)
    ]

    unit = converter.to_music_unit(notes, start_beat=0.0, end_beat=4.0)

    # Check parsed events
    events = unit.events
    assert len(events) == 2
    
    # Verify exact integer tick translation (0.0 * 960 = 0)
    assert events[0].pitch == 60
    assert events[0].start_tick == 0
    assert events[0].end_tick == 960
    assert events[0].volume == 100

    # Verify second note (2.0 * 960 = 1920)
    assert events[1].pitch == 64
    assert events[1].start_tick == 1920
    assert events[1].end_tick == 2400
    assert events[1].volume == 90


def test_matrix_population():
    converter = MelodicaToMatrixConverter(bpm=120.0, ticks_per_beat=960)

    # Tracks dictionary mapping Track name -> Notes
    tracks = {
        "Violin_I": [
            MelodicaExchangeNote(pitch=72, start_beat=0.0, duration_beats=4.0),
            MelodicaExchangeNote(pitch=74, start_beat=4.0, duration_beats=4.0),
        ],
        "Cello": [
            MelodicaExchangeNote(pitch=48, start_beat=0.0, duration_beats=8.0),
        ]
    }

    # Boundaries: Two 4-beat sections (Intro [0.0, 4.0), Verse [4.0, 8.0))
    boundaries = [0.0, 4.0, 8.0]

    matrix = converter.populate_matrix(tracks, boundaries)

    # Matrix dimensions must be 2 rows (Cello, Violin_I) x 2 cols (Intro, Verse)
    assert matrix.data.shape == (2, 2)

    # Row 0: Cello (spanning both sections)
    cello_sec_0 = matrix.get_unit((0, 0))
    cello_sec_1 = matrix.get_unit((0, 1))

    assert len(cello_sec_0.events) == 1
    # Check clamping to cell boundaries (8.0 beats = 7680 ticks. In [0.0, 4.0) cell, clamped to end_tick=3840)
    assert cello_sec_0.events[0].pitch == 48
    assert cello_sec_0.events[0].start_tick == 0
    assert cello_sec_0.events[0].end_tick == 3840

    # Row 1: Violin I
    v1_sec_0 = matrix.get_unit((1, 0))
    v1_sec_1 = matrix.get_unit((1, 1))

    assert len(v1_sec_0.events) == 1
    assert v1_sec_0.events[0].pitch == 72
    assert v1_sec_0.events[0].start_tick == 0
    assert v1_sec_0.events[0].end_tick == 3840

    assert len(v1_sec_1.events) == 1
    assert v1_sec_1.events[0].pitch == 74
    # Starts relative to section 1 origin (4.0 * 960 = 3840 - 3840 = 0)
    assert v1_sec_1.events[0].start_tick == 0 
    assert v1_sec_1.events[0].end_tick == 3840

