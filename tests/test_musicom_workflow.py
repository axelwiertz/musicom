# -*- coding: utf-8 -*-
"""Tests for the musicom workflow (design → realization spine)."""
import os
import sys

import pytest

# ensure instruments registry importable
sys.path.insert(0, "/opt/data/projects/Instruments")

from workflows.musicom_workflow import (
    compose, produce, _midi_to_notes,
    method_table, sp_method_table, style_table,
)


@pytest.fixture(scope="module")
def composed():
    r = compose(style="pop", key="C", bpm=120)
    return r


def test_compose_produces_valid_midi(composed):
    assert os.path.exists(composed.midi_path)
    assert os.path.getsize(composed.midi_path) > 40, "empty/corrupt MIDI"
    assert composed.method == "001"


def test_compose_writes_provenance(composed):
    assert composed.provenance_path
    assert os.path.exists(composed.provenance_path)


def test_produce_fluidsynth(composed):
    p = produce(composed.midi_path, method="SP-001")
    assert os.path.exists(p.wav_path)
    assert os.path.getsize(p.wav_path) > 1000
    assert p.ogg_path and os.path.exists(p.ogg_path)


def test_produce_karplus(composed):
    p = produce(composed.midi_path, method="SP-011")
    assert os.path.exists(p.wav_path)
    assert os.path.getsize(p.wav_path) > 1000
    assert p.info["note_count"] > 10


def test_midi_to_notes(composed):
    notes = _midi_to_notes(composed.midi_path)
    assert len(notes) > 10
    assert all("pitch" in n and "start" in n and "end" in n for n in notes)
    # notes sorted by start
    starts = [n["start"] for n in notes]
    assert starts == sorted(starts)


def test_tables():
    mt = method_table()
    assert "001" in mt
    st = sp_method_table()
    assert "SP-001" in st and "SP-011" in st
    sty = style_table()
    assert "pop" in sty and "flamenco" in sty
