from structures import MusicUnit, MusicTime, UnitMatrix
from converters.music21_note import note_to_event, event_to_note, tick_gap_to_rest
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

def unit_to_stream(unit: MusicUnit, time: MusicTime) -> stream.Stream:
    # Convert unit to m21 stream
    stream_out = stream.Stream()
    if unit is None:
        return stream_out
    # Create a stream with notes and rests
    # Iterate over the list of MusicEvents in the unit
    for i, event in enumerate(unit.events):
        stream_out.append(event_to_note(event, time))
        # Add rest for gap to next event
        if i + 1 < len(unit.events):
            next_event = unit.events[i + 1]
            gap_ticks = next_event.start_tick - event.end_tick
            if gap_ticks > 0:
                stream_out.append(tick_gap_to_rest(gap_ticks, time))
    return stream_out


def stream_to_unit(stream_in: stream.Stream, time: MusicTime) -> MusicUnit:
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

def matrix_row_to_stream(matrix: UnitMatrix, row: int, time: MusicTime) -> stream.Stream:
    """Concatenate the music21 streams from contained units into a single Stream."""
    stream_out = stream.Stream()
    for col in range(matrix.cols):
        unit_ = matrix.get_unit(row, col)
        if unit_ is None:
            rest_ = tick_gap_to_rest(matrix.units_in_col(col)[0].len_ticks(), time)
            stream_out.append(rest_)
        else:
            stream_out.append(unit_to_stream(unit_, time))
    return stream_out
