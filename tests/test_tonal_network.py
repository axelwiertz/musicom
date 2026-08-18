"""Tests for the tonal network progression generator (research->library)."""
import pytest

from generators.tonal_network import TonalNetworkGenerator, CHORD_QUALITY
from generators import TonalNetworkGenerator as ExportedGen


class TestGraph:
    def test_catalog_roles(self):
        gen = TonalNetworkGenerator(root=60)
        assert 'tonic' in gen.roles
        assert 'dominant' in gen.roles
        assert len(gen.roles) >= 3

    def test_node_pitches_qol(self):
        gen = TonalNetworkGenerator(root=60)
        tonic = gen.node_pitches('tonic')
        # major triad {0,4,7} above root 60
        assert tonic == [60, 64, 67]

    def test_affinity_weights_exposed(self):
        gen = TonalNetworkGenerator(root=60)
        assert gen.transitions()['dominant']


class TestProgression:
    def test_roles_length(self):
        gen = TonalNetworkGenerator(root=60, seed=1)
        assert len(gen.progression_roles(6)) == 6

    def test_progression_has_expected_events(self):
        gen = TonalNetworkGenerator(root=60, seed=1)
        unit = gen.progression(num_chords=3, duration_beats=1.0, ticks_per_beat=480)
        # 3 chords x 3 tones (major triads) = 9 events
        assert len(unit.events) == 9

    def test_determinism(self):
        g1 = TonalNetworkGenerator(root=60, seed=42)
        g2 = TonalNetworkGenerator(root=60, seed=42)
        assert g1.progression_roles(8) == g2.progression_roles(8)

    def test_starts_on_tonic(self):
        gen = TonalNetworkGenerator(root=60)
        assert gen.progression_roles(4)[0] == 'tonic'

    def test_generate(self):
        gen = TonalNetworkGenerator(root=60, seed=7)
        units = gen.generate()
        assert len(units) == 1
        assert len(units[0].events) > 0


class TestChordQuality:
    def test_known_qualities(self):
        assert CHORD_QUALITY['major'] == (0, 4, 7)
        assert CHORD_QUALITY['dominant7'] == (0, 4, 7, 10)


class TestExport:
    def test_exported_via_package(self):
        assert ExportedGen is TonalNetworkGenerator