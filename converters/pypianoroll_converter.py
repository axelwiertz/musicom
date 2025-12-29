"""Converters between musicom structures and pypianoroll objects."""
from __future__ import annotations

from typing import List

import numpy as np
from pypianoroll import Multitrack, Track

from structures.unit import MusicUnit, MusicEvent
from structures.project import MusicProject
from structures.matrix import UnitMatrix


# ---------------------------------------------------------------------------
# MusicUnit  <->  pypianoroll.Track
# ---------------------------------------------------------------------------

def musicunit_to_track(
    unit: MusicUnit,
    *,
    name: str = "unit",
    program: int = 0,
    is_drum: bool = False,
) -> Track:
    """
    Convert a MusicUnit into a pypianoroll.Track.

    MusicUnit stores events in a structured numpy array with fields:
      - pitch      (uint8)
      - volume     (uint8)
      - start_tick (uint16)
      - end_tick   (uint16)

    Pypianoroll Track uses a 2D pianoroll array of shape (time_steps, 128)
    where non-zero values represent velocity.
    """
    data = unit.data
    if data.size == 0:
        pianoroll = np.zeros((1, 128), dtype=np.uint8)
        return Track(
            name=name,
            program=program,
            is_drum=is_drum,
            pianoroll=pianoroll,
        )

    # Determine track length in ticks
    max_tick = int(data["end_tick"].max())
    if max_tick <= 0:
        max_tick = 1

    pianoroll = np.zeros((max_tick, 128), dtype=np.uint8)

    for e in data:
        pitch = int(e["pitch"])
        vol = int(e["volume"])
        start = int(e["start_tick"])
        end = int(e["end_tick"])

        if not (0 <= pitch <= 127):
            continue
        if end <= start:
            end = start + 1

        start = max(0, start)
        end = min(max_tick, end)
        pianoroll[start:end, pitch] = vol

    return Track(
        name=name,
        program=program,
        is_drum=is_drum,
        pianoroll=pianoroll,
    )


def track_to_musicunit(track: Track) -> MusicUnit:
    """
    Convert a pypianoroll.Track into a MusicUnit.

    Detects notes as contiguous non-zero velocity regions on each pitch.
    Each time step is treated as one tick.
    """
    pr = track.pianoroll
    if pr.size == 0:
        return MusicUnit()

    time_steps, _ = pr.shape
    events: List[MusicEvent] = []

    for pitch in range(128):
        column = pr[:, pitch]
        active = column > 0
        if not active.any():
            continue

        t = 0
        while t < time_steps:
            if not active[t]:
                t += 1
                continue

            # Note-on detected
            vel = int(column[t])
            start_tick = t
            t += 1

            # Find note-off (first zero or end)
            while t < time_steps and active[t]:
                t += 1
            end_tick = t

            events.append(MusicEvent(
                pitch=pitch,
                volume=vel,
                start_tick=start_tick,
                end_tick=end_tick,
            ))

    return MusicUnit(events=events)


# ---------------------------------------------------------------------------
# MusicProject  <->  pypianoroll.Multitrack
# ---------------------------------------------------------------------------

def musicproject_to_multitrack(
    project: MusicProject,
    *,
    resolution: int = 24,
    default_program: int = 0,
) -> Multitrack:
    """
    Convert a MusicProject into a pypianoroll.Multitrack.

    - Each row in project.matrix becomes one Track
    - Units in each row are concatenated in time order (by column)
    - Voice names and MIDI instruments are used when available
    """
    matrix: UnitMatrix = project.matrix
    if matrix is None:
        raise ValueError("MusicProject has no matrix to convert.")

    tracks: List[Track] = []

    for row_idx in range(matrix.num_rows):
        # Concatenate all units in this row
        combined_events: List[MusicEvent] = []
        current_offset = 0

        for col_idx in range(matrix.num_cols):
            cell = matrix.get_unit(row_idx, col_idx)
            if cell is None:
                continue

            # Shift events by current_offset
            for e in cell.data:
                combined_events.append(MusicEvent(
                    pitch=int(e["pitch"]),
                    volume=int(e["volume"]),
                    start_tick=int(e["start_tick"]) + current_offset,
                    end_tick=int(e["end_tick"]) + current_offset,
                ))

            # Advance offset by unit length
            if len(cell.data) > 0:
                unit_len = int(cell.data["end_tick"].max())
                current_offset += unit_len

        # Create MusicUnit from combined events
        if combined_events:
            row_unit = MusicUnit(events=combined_events)
        else:
            row_unit = MusicUnit()

        # Determine track name and program
        track_name = f"voice_{row_idx}"
        program = default_program

        if project.voices and row_idx < len(project.voices):
            voice = project.voices[row_idx]
            track_name = voice.name or track_name
            if hasattr(voice, "midi_instrument") and voice.midi_instrument is not None:
                program = voice.midi_instrument

        track = musicunit_to_track(
            row_unit,
            name=track_name,
            program=program,
            is_drum=False,
        )
        tracks.append(track)

    return Multitrack(tracks=tracks, resolution=resolution)


def multitrack_to_musicproject(
    multitrack: Multitrack,
    *,
    name: str = "from_multitrack",
) -> MusicProject:
    """
    Convert a pypianoroll.Multitrack into a MusicProject.

    - Each Track becomes one row in the matrix
    - Each row contains a single MusicUnit (column 0) with all track notes
    """
    from structures.project import MusicVoice

    units: List[MusicUnit] = []
    voices: List[MusicVoice] = []

    for idx, track in enumerate(multitrack.tracks):
        unit = track_to_musicunit(track)
        units.append(unit)

        voice = MusicVoice(
            name=track.name or f"voice_{idx}",
            midi_instrument=track.program if hasattr(track, "program") else 0,
            row_index=idx,
        )
        voices.append(voice)

    # Build matrix: n_tracks rows x 1 column
    n_rows = len(units)
    matrix = UnitMatrix(shape=(n_rows, 1))
    for i, u in enumerate(units):
        matrix.set_unit(i, 0, u)

    return MusicProject(
        name=name,
        pattern=None,
        time=None,
        sections=None,
        voices=voices,
        matrix=matrix,
    )

