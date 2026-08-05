"""MusicXML export/import for UnitMatrix and MusicUnit.

Writing uses the canonical absolute-tick model: each ``UnitMatrix`` row
becomes a MusicXML part, and every ``MusicEvent`` becomes a note whose
duration is derived from ``end_tick - start_tick``. ``music21`` is imported
lazily so this module stays importable in minimal environments.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from structures import UnitMatrix


def _require_music21():
    try:
        import music21
        return music21
    except ImportError as e:
        raise ImportError(
            "music21 is required for MusicXML support. Install with: pip install music21"
        ) from e


def _matrix_to_m21_score(matrix: "UnitMatrix", ticks_per_beat: int, bpm: float):
    """Convert a UnitMatrix to a music21 Score (one part per row)."""
    music21 = _require_music21()

    score = music21.stream.Score()
    tempo_mark = music21.tempo.MetronomeMark(number=bpm)

    num_rows, num_cols = matrix.data.shape

    for r_idx in range(num_rows):
        part = music21.stream.Part()
        part.id = f"Voice_{r_idx}"
        if r_idx == 0:
            part.append(tempo_mark)

        # Gather events across all cells of the row in absolute ticks
        abs_events = []
        cumulative_offset = 0
        for c_idx in range(num_cols):
            unit = matrix.get_unit((r_idx, c_idx))
            if unit is not None:
                for event in unit.events:
                    if event.pitch <= 0:
                        continue
                    abs_events.append((
                        cumulative_offset + event.start_tick,
                        cumulative_offset + event.end_tick,
                        event.pitch,
                        event.volume,
                    ))
                cumulative_offset += unit.len_ticks()

        abs_events.sort(key=lambda x: (x[0], x[1]))

        for start, end, pitch, volume in abs_events:
            note = music21.note.Note(pitch)
            note.duration.quarterLength = (end - start) / ticks_per_beat
            note.offset = start / ticks_per_beat
            try:
                note.volume.velocity = volume
            except Exception:
                pass
            part.append(note)

        score.append(part)

    return score


def export_musicxml(matrix: "UnitMatrix", path: str,
                    ticks_per_beat: int = 480, bpm: float = 120.0) -> bool:
    """
    Export a UnitMatrix to a MusicXML file (one part per voice row).

    Args:
        matrix: UnitMatrix to export
        path: Destination ``.musicxml`` / ``.xml`` path
        ticks_per_beat: Ticks per quarter note used for the conversion
        bpm: Tempo marking written into the score

    Returns:
        True on success
    """
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    score = _matrix_to_m21_score(matrix, ticks_per_beat, bpm)
    score.write('musicxml', fp=path)
    return True


class MusicXMLWriter:
    """Write MusicXML files from a UnitMatrix or a list of MusicUnits."""

    def __init__(self, ticks_per_beat: int = 480, bpm: float = 120.0):
        self.ticks_per_beat = ticks_per_beat
        self.bpm = bpm

    def write(self, matrix: "UnitMatrix", path: str) -> bool:
        """Write a UnitMatrix to MusicXML."""
        return export_musicxml(matrix, path, self.ticks_per_beat, self.bpm)


class MusicXMLReader:
    """Read MusicXML files into MusicUnits (one per part, absolute ticks)."""

    def __init__(self, ticks_per_beat: int = 480):
        self.ticks_per_beat = ticks_per_beat

    def read(self, filepath: str) -> List["MusicUnit"]:
        """
        Read a MusicXML file and return one MusicUnit per part.

        Args:
            filepath: Path to the MusicXML file

        Returns:
            List of MusicUnit, one per part, with absolute tick timing
        """
        from structures.unit import MusicUnit, MusicEvent

        music21 = _require_music21()
        score = music21.converter.parse(filepath)

        units: List[MusicUnit] = []
        parts = score.parts if getattr(score, 'parts', None) else [score]

        for part in parts:
            unit = MusicUnit()
            for el in part.recurse().notes:
                if isinstance(el, music21.note.Note):
                    start = int(round(el.offset * self.ticks_per_beat))
                    end = start + int(round(el.duration.quarterLength * self.ticks_per_beat))
                    velocity = 64
                    try:
                        velocity = el.volume.velocity or 64
                    except Exception:
                        pass
                    unit.add_event(MusicEvent(
                        pitch=el.pitch.midi,
                        volume=velocity,
                        start_tick=start,
                        end_tick=end,
                    ))
            units.append(unit)

        return units
