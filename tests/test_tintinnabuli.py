"""Tests for tintinnabuli + isorhythm generators (promoted from research/)."""
import pytest

from generators.tintinnabuli import TintinnabuliGenerator, isorhythmize
from generators import TintinnabuliGenerator as ExportedGen


class TestTintinnabuliMvoice:
    def test_snaps_to_mode(self):
        gen = TintinnabuliGenerator(tonic=60, mode='major')
        m = gen.m_voice([60, 64, 67, 63])
        # 63 (Eb) snaps up/down onto the C major scale; nearest scale deg
        pitches = m.pitches
        assert len(pitches) == 4
        # every snapped pitch must be a scale tone relative to tonic 60
        scale_pc = {0, 2, 4, 5, 7, 9, 11}
        for i, p in enumerate(pitches):
            assert (p % 12) in scale_pc

    def test_accepts_unit_input(self):
        from structures.unit import MusicUnit, MusicEvent
        gen = TintinnabuliGenerator(tonic=60, mode='major')
        u = MusicUnit(events=[MusicEvent(61, 90, 0, 10), MusicEvent(62, 90, 10, 20)])
        m = gen.m_voice(u)
        # event count preserved, rhythm preserved
        assert len(m.events) == 2
        assert [e.start_tick for e in m.events] == [0, 10]

    def test_duet_has_two_voices_count(self):
        gen = TintinnabuliGenerator(tonic=60, mode='major')
        # 4 melody notes
        duet = gen.duet([60, 62, 64, 67])
        assert len(duet.events) == 8  # 4 M + 4 T


class TestTintinnabuliTvoice:
    def test_t_voice_is_triad_only(self):
        gen = TintinnabuliGenerator(tonic=60, mode='major')
        t = gen.t_voice([60, 62, 64, 67])
        # all T-voice pitches must resolve to the C-major triad {60,64,67}
        triad_pc = {0, 4, 7}
        for p in t.pitches:
            assert p % 12 in triad_pc

    def test_position_changes_pitch(self):
        gen = TintinnabuliGenerator(tonic=60, mode='major')
        t0 = gen.t_voice([62], position=0)
        t1 = gen.t_voice([62], position=1)
        assert t0.pitches[0] != t1.pitches[0]

    def test_duet_merges_voices(self):
        gen = TintinnabuliGenerator(tonic=60, mode='major')
        both = gen.duet([60, 62, 64], position=1)
        # every pitch must be either a scale tone OR a triad tone
        scale_pc = {0, 2, 4, 5, 7, 9, 11}
        triad_pc = {0, 4, 7}
        for p in both.pitches:
            pc = p % 12
            assert pc in scale_pc or pc in triad_pc


class TestIsorhythm:
    def test_cycles_color_and_talea(self):
        color = [0, 4, 7]
        talea = [1.0, 0.5]
        unit = isorhythmize(color, talea, ticks_per_beat=480, start_pitch=60)
        # max(len) = 3 events
        assert len(unit.events) == 3
        # pitches cycle 60, 64, 67
        assert unit.pitches == [60, 64, 67]

    def test_talea_durations(self):
        color = [0, 2]
        talea = [1.0, 0.5]
        unit = isorhythmize(color, talea, ticks_per_beat=480, start_pitch=60)
        # durations: 480 (1 beat), 240 (0.5 beat) — pattern length 2
        assert unit.durations == [480, 240]

    def test_empty_rejected(self):
        with pytest.raises(ValueError):
            isorhythmize([], [1.0])
        with pytest.raises(ValueError):
            isorhythmize([0], [])


class TestExport:
    def test_exported_via_package(self):
        assert ExportedGen is TintinnabuliGenerator