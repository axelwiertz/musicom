from structures import MusicUnit, MusicTimeGrid, UnitMatrix
from converters.music21_note import note_to_event, event_to_note
from converters.time import ticks_to_quarter_length

from music21 import serial, stream, note, chord


def tonerow_to_stream(tonerow_base: serial.ToneRow = serial.ToneRow(row=[0, 4, 7, 4]),
                      octave: int = 4
                      ) -> stream.Stream:
    """Convert a tone row to a music21 stream."""
    stream_out = stream.Stream()
    # Tone row
    for pcs in enumerate(tonerow_base):
        pcs.octave = octave
        stream_out.append(pcs)

    return stream_out

def unit_to_stream(unit: MusicUnit, time_grid: MusicTimeGrid) -> stream.Stream:
    # Convert unit to m21 stream
    stream_out = stream.Stream()
    if unit is None:
        return stream_out
    # Create a stream with notes and rests
    # Iterate over the list of MusicEvents in the unit
    for i, event in enumerate(unit.events):
        stream_out.append(event_to_note(event, time_grid))
        # Add rest for gap to next event
        if i + 1 < len(unit.events):
            next_event = unit.events[i + 1]
            gap_ticks = int(next_event.start_tick - event.end_tick)
            if gap_ticks > 0:
                stream_out.append(note.Rest(duration=ticks_to_quarter_length(gap_ticks, time_grid)))
    return stream_out


def stream_to_unit(stream_in: stream.Stream, time: MusicTimeGrid) -> MusicUnit:
    # Convert m21 stream to unit
    unit = MusicUnit()
    # Transfer notes and chords from the stream to the unit
    for element in stream_in.flatten():
        if isinstance(element, note.Note):
            unit.add_event(note_to_event(element, time))
        elif isinstance(element, chord.Chord):
            for note_ in element.notes:
                unit.add_event(note_to_event(note_, time))
    return unit

def matrix_row_to_stream(matrix: UnitMatrix, row: int, time_grid: MusicTimeGrid) -> stream.Stream:
    """Concatenate the music21 streams from contained units into a single Stream."""
    stream_out = stream.Stream()
    for col in range(matrix.num_cols):
        unit_ = matrix.get_unit(pos=(row, col))
        if unit_ is None:
            # Add rest for the duration of the column
            stream_out.append(note.Rest(
                duration=ticks_to_quarter_length(matrix.units_in_col(col)[0].len_ticks(), time_grid)))
        else:
            # Append the unit's stream
            stream_out.append(unit_to_stream(unit_, time_grid))
    return stream_out
