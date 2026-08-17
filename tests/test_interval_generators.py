"""Tests for interval-based generators (Markov chain + L-System)."""
import pytest

from generators.interval_chain import IntervalMarkovGenerator
from generators.interval_lsystem import IntervalLSystem


class TestIntervalMarkov:
    def test_chain_length(self):
        gen = IntervalMarkovGenerator()
        d = gen.generate_sequence(length=16, seed=1)
        assert len(d) == 16

    def test_transposition_invariant(self):
        gen = IntervalMarkovGenerator()
        d = gen.generate_sequence(length=12, seed=5)
        p1 = gen.to_pitches(d, 60)
        p2 = gen.to_pitches(d, 67)
        assert p2[0] - p1[0] == 7
        assert [b - a for a, b in zip(p1, p1[1:])] == \
               [b - a for a, b in zip(p2, p2[1:])]

    def test_determinism(self):
        gen = IntervalMarkovGenerator()
        assert gen.generate_sequence(16, seed=42) == \
               gen.generate_sequence(16, seed=42)

    def test_to_unit(self):
        gen = IntervalMarkovGenerator()
        d = gen.generate_sequence(length=8, seed=3)
        unit = gen.to_unit(d, start=60, duration=480)
        assert len(unit.events) == len(d) + 1  # +1 tail pad

    def test_train_intervals(self):
        # deterministic train: [0, +2, -1] repeated
        train = [0, 2, -1, 0, 2, -1, 0]
        gen = IntervalMarkovGenerator(train_intervals=train)
        d = gen.generate_sequence(length=7, seed=0)
        # states only from {0, 2, -1}
        assert set(d) <= {0, 2, -1}


class TestIntervalLSystem:
    def test_generate_string(self):
        ls = IntervalLSystem(axiom="A", rules={"A": "A+B", "B": "A-B"},
                             symbols={"+": 2, "-": 1})
        assert ls.generate_string(1) == "A+B"
        assert ls.generate_string(2) == "A+B+A-B"

    def test_deltas(self):
        ls = IntervalLSystem(axiom="A", rules={"A": "A+B", "B": "A-B"},
                             symbols={"+": 2, "-": 1})
        d = ls.generate_deltas(3)
        # only terminal symbols mapped
        assert all(x in (2, 1) for x in d)
        assert len(d) > 0

    def test_to_pitches(self):
        ls = IntervalLSystem(axiom="A", rules={"A": "A+B", "B": "A-B"},
                             symbols={"+": 2, "-": 1})
        d = ls.generate_deltas(2)
        p = ls.to_pitches(d, 60)
        assert p[0] == 60
        assert len(p) == len(d) + 1

    def test_to_unit_section_padding(self):
        ls = IntervalLSystem(axiom="A", rules={"A": "A+B", "B": "A-B"},
                             symbols={"+": 2, "-": 1})
        d = ls.generate_deltas(2)
        unit = ls.to_unit(d, start=60, duration=480, section_ticks=3840)
        # events must not exceed section boundary
        assert all(e.end_tick <= 3840 for e in unit.events)
