"""Tests for hierarchical metrical structures (promoted from research/rhythm.py)."""
import pytest

from structures.metrical import (
    MetricalNode, HierarchicalEvent, QuantizedEvent,
    seconds_to_ticks, quantize_onsets_to_ticks, build_common_tree,
    assign_metrical_level,
)
from structures import MetricalNode as ExportedNode


class TestSecondsToTicks:
    def test_basic_conversion(self):
        # 2.0s at 120 BPM = 4 beats = 1920 ticks at 480 tpb
        assert seconds_to_ticks(2.0, 120, 480) == 1920

    def test_rounds(self):
        # non-integer beat fraction still returns int
        assert isinstance(seconds_to_ticks(0.123, 90, 480), int)


class TestQuantizeOnsets:
    def test_snaps_to_tick_grid(self):
        events = quantize_onsets_to_ticks([0.0, 0.5, 0.75], 120, 480)
        # 0.5s at 120 = 1 beat = 480 ticks; 0.75s = 1.5 beats = 720
        assert [e.tick for e in events] == [0, 480, 720]

    def test_sorted_output(self):
        events = quantize_onsets_to_ticks([0.75, 0.0, 0.5], 120, 480)
        assert [e.tick for e in events] == [0, 480, 720]

    def test_duration_positive(self):
        events = quantize_onsets_to_ticks([1.0], 120, 480, duration_s=0.1)
        assert all(e.duration_ticks >= 1 for e in events)


class TestMetricalTree:
    def test_build_common_tree_structure(self):
        tree = build_common_tree(bpm=120, beats=4, beats_per_bar=4, subdivisions=2)
        assert tree.level_name == "measure"
        # measure of 4 beats at 0.5s/beat = 2.0s
        assert tree.period == pytest.approx(2.0)
        assert tree.period / 4 == pytest.approx(0.5)   # beat period
        children = tree.children
        assert len(children) == 4
        # first beat has a subdivision child
        assert children[0].children[0].level_name == "subdivision"
        assert children[0].children[0].period == pytest.approx(0.25)

    def test_total_seconds(self):
        leaf = MetricalNode("beat", period=0.5)
        assert leaf.total_seconds(4) == pytest.approx(2.0)

    def test_tick_phase(self):
        leaf = MetricalNode("beat", period=0.5)
        # at 480 tpb with 0.5s/beat -> ticks per period = 0.5*480 = 240
        # tick 120 -> phase 0.5
        assert leaf.tick_phase(120, ticks_per_beat=480) == pytest.approx(0.5)


class TestAssignLevel:
    def test_deepest_match(self):
        tree = build_common_tree(bpm=120, beats=4, beats_per_bar=4, subdivisions=2)
        events = assign_metrical_level([0.0, 0.5, 0.75], tree)
        # t=0 on the downbeat -> measure; t=0.5 on a beat; t=0.75 on subdivision
        # 0.25,3.4 ), 0.5 -> beat, 0.75 -> subdivision
        labels = [e.label for e in events]
        assert labels == ["measure", "beat", "subdivision"]

    def test_fallback_to_root(self):
        tree = build_common_tree(bpm=120)
        # an off-grid time resolves to the root
        ev = assign_metrical_level([0.13], tree)[0]
        assert ev.label == "measure"


class TestExport:
    def test_exported_via_package(self):
        assert ExportedNode is MetricalNode