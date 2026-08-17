"""Tests for just-intonation ratio lattice."""
import pytest

from sound.tuning.ratio_lattice import RatioLattice


class TestRatioLattice:
    def test_multiply(self):
        lat = RatioLattice(base_freq=220.0)
        # 3:2 * 3:2 = 9:4
        assert lat.multiply((3, 2), (3, 2)) == (9, 4)
        # 3:2 * 4:3 = 2:1 (fifth up, fourth up = octave)
        assert lat.multiply((3, 2), (4, 3)) == (2, 1)

    def test_walk_fifths(self):
        lat = RatioLattice(base_freq=220.0)
        path = lat.walk([(3, 2), (3, 2)])
        # A3(220) -> E4(330) -> B4(495)
        freqs = lat.path_freqs(path)
        assert freqs[0] == 220.0
        assert freqs[1] == 330.0
        assert freqs[2] == 495.0

    def test_freqs_to_midi(self):
        lat = RatioLattice(base_freq=220.0)
        midi = lat.freqs_to_midi([220.0, 440.0, 880.0])
        assert midi == [57, 69, 81]  # A3, A4, A5

    def test_harmonic_seventh(self):
        lat = RatioLattice(base_freq=220.0)
        h7 = lat.walk([(7, 4)])
        freq = lat.path_freqs(h7)[-1]
        # 7:4 of 220 = 385 Hz (harmonic minor 7th above A3)
        assert abs(freq - 385.0) < 1e-6

    def test_path_to_pitches(self):
        lat = RatioLattice(base_freq=220.0)
        pitches = lat.path_to_pitches([(3, 2), (3, 2), (3, 2)], base_midi=57)
        # circle of fifths: A E B F#
        assert pitches[0] == 57
        assert pitches[1] == 64
        assert pitches[2] == 71
        assert pitches[3] == 78
