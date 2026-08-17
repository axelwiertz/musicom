"""Tests for interval-based structures (set theory, Hindemith, expansion)."""
import pytest

from structures.intervals import (
    interval_class_vector, z_related, set_prime_form,
    hindemith_rank, harmonic_fluctuation, manage_fluctuation,
    interval_expansion, delta_encode, delta_decode, transposition_invariant,
)


class TestIntervalClassVector:
    def test_triad(self):
        # C-E-G: m3 (E-G), M3 (C-E), P4 (C-F... wait, C-G = P5)
        # pairs: C-E (M3, ic4), C-G (P5, ic5), E-G (m3, ic3)
        assert interval_class_vector([0, 4, 7]) == [0, 0, 1, 1, 1, 0]

    def test_minor_second_cluster(self):
        assert interval_class_vector([0, 1, 2]) == [2, 1, 0, 0, 0, 0]

    def test_tritone(self):
        assert interval_class_vector([0, 6]) == [0, 0, 0, 0, 0, 1]

    def test_octave_equivalence(self):
        # same set transposed an octave -> same ICV
        assert interval_class_vector([0, 4, 7]) == interval_class_vector([12, 16, 19])


class TestZRelation:
    def test_z_related(self):
        # 4-Z15 [0,1,4,6] and 4-Z29 [0,1,3,7] share ICV but no transposition
        assert z_related([0, 1, 4, 6], [0, 1, 3, 7])

    def test_transposition_not_z(self):
        # [0,4,7] and [2,6,9] are transpositions -> not Z
        assert not z_related([0, 4, 7], [2, 6, 9])

    def test_different_vectors_not_z(self):
        assert not z_related([0, 4, 7], [0, 1, 2])


class TestPrimeForm:
    def test_trichord(self):
        assert set_prime_form([0, 4, 7]) == (0, 3, 8)  # major triad prime form

    def test_minimal_rotation(self):
        assert set_prime_form([2, 4, 7]) == (0, 2, 5)


class TestHindemith:
    def test_rank_order(self):
        assert hindemith_rank(0) == 0   # unison most stable
        assert hindemith_rank(7) == 1   # fifth
        assert hindemith_rank(5) == 2   # fourth
        assert hindemith_rank(6) == 11  # tritone most tense

    def test_octave_equivalence(self):
        assert hindemith_rank(12) == hindemith_rank(0)
        assert hindemith_rank(19) == hindemith_rank(7)

    def test_fluctuation(self):
        # C-G is rank 1 (P5)
        assert harmonic_fluctuation([60, 67]) == [1]

    def test_manage_fluctuation(self):
        # [60, 67, 64] has ranks [1, 3] -> all <= 4, unchanged
        out = manage_fluctuation([60, 67, 64], 4)
        assert out == [60, 67, 64]
        # tritone (rank 11) gets collapsed when target <= 4
        out2 = manage_fluctuation([60, 66], 4)
        assert hindemith_rank(out2[1] - out2[0]) <= 4


class TestIntervalExpansion:
    def test_expansion_sequence(self):
        # m2 motif [0,1] expanded through [1,2,3,4,5,6,7] gives growing leaps
        out = interval_expansion([0, 1], [1, 2, 3, 4])
        # phrase starts at 0, then each phrase builds on previous end
        assert out[0] == 0
        assert len(out) == 8  # 4 phrases x 2 notes

    def test_monotone_growth(self):
        out = interval_expansion([0, 1], [1, 2, 3, 4, 5])
        # interval sizes are strictly increasing: 1,2,3,4,5
        sizes = [out[i + 1] - out[i] for i in range(0, len(out), 2)]
        assert sizes == [1, 2, 3, 4, 5]


class TestDeltaEncoding:
    def test_roundtrip(self):
        pitches = [60, 64, 67, 71, 74]
        deltas = delta_encode(pitches)
        assert delta_decode(deltas, start=60) == pitches

    def test_transposition_invariant(self):
        m1 = transposition_invariant([60, 64, 67], root=60)
        m2 = transposition_invariant([60, 64, 67], root=67)
        assert m2[0] - m1[0] == 7
        # same contour
        assert [b - a for a, b in zip(m1, m1[1:])] == [b - a for a, b in zip(m2, m2[1:])]
