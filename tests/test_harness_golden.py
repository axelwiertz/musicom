"""Phase 3 test harness — zero-drift regression + artifact integrity.

Two guarantees this locks in:
  1. GOLDEN FILE: a fixed composition must always export byte-identical MIDI.
     If the hash changes, either a real regression happened or the change was
     intentional (then update GOLDEN_SHA256 deliberately).
  2. VERIFY-DON'T-TRUST: every export must produce a non-empty, equal-length
     (zero-drift) multi-track file. Empties historically appeared as 16-22 bytes.
"""
import hashlib
import os
import tempfile

import mido
import pytest

from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit,
)
from structures import MidiInstrument


# Golden hash of the canonical fixture below (bpm=120, tpb=480, 3 voices x 2 sections).
# Recompute intentionally only when the export format legitimately changes.
GOLDEN_SHA256 = "d6c847a4181bbb10b4a0241230c9f8d9fff6f752f8c45e51468bab74a820c6b0"
BAR = 480 * 4


def _build_fixture() -> UnitMatrixComposer:
    """Deterministic reference composition — no randomness."""
    c = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    c.create_matrix(num_voices=3, num_sections=2)
    c.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
    c.add_voice("Chord", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
    c.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
    c.add_section("A", bars=1)
    c.add_section("B", bars=1)
    for col, (lead, bass) in enumerate([(72, 36), (74, 38)]):
        c.set_unit(0, col, create_note_unit(lead, BAR))
        c.set_unit(1, col, create_chord_unit([60, 64, 67], BAR))
        c.set_unit(2, col, create_note_unit(bass, BAR))
    return c


def test_fixture_validates():
    ok, msg = _build_fixture().validate()
    assert ok, msg


def test_golden_midi_hash_stable():
    """Same input -> byte-identical MIDI (proves determinism + no regression)."""
    data = _build_fixture().to_midi_bytes()
    actual = hashlib.sha256(data).hexdigest()
    assert actual == GOLDEN_SHA256, (
        f"MIDI export changed!\n  expected {GOLDEN_SHA256}\n  actual   {actual}\n"
        "If this change is intentional, update GOLDEN_SHA256 deliberately."
    )


def test_export_is_deterministic():
    a = hashlib.sha256(_build_fixture().to_midi_bytes()).hexdigest()
    b = hashlib.sha256(_build_fixture().to_midi_bytes()).hexdigest()
    assert a == b


def test_artifact_non_empty():
    """Guard against silent empty/corrupt writes (historically 16-22 bytes)."""
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "fixture.mid")
        _build_fixture().to_midi(out)
        size = os.path.getsize(out)
        assert size > 40, f"MIDI too small (likely empty/corrupt): {size} bytes"


def test_zero_drift_equal_track_lengths():
    """Every voice track must end at the same absolute tick (no drift)."""
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "fixture.mid")
        _build_fixture().to_midi(out)
        mid = mido.MidiFile(out)
        # Track 0 is the tempo meta track; voices follow.
        voice_lengths = [sum(m.time for m in trk) for trk in mid.tracks[1:]]
        assert len(voice_lengths) == 3
        assert len(set(voice_lengths)) == 1, f"track length drift: {voice_lengths}"
        assert voice_lengths[0] == BAR * 2  # 2 sections of 1 bar each
