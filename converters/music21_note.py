""""""
from structures import MusicEvent, MusicTimeGrid
from converters.time import quarter_length_to_ticks, ticks_to_quarter_length
from music21 import note

def note_to_event(note_in: note.Note, time: MusicTimeGrid) -> MusicEvent:
    # Convert m21 note to MusicEvent
    start = note_in.offset
    end = start + note_in.duration.quarterLength
    event = MusicEvent(
        pitch=note_in.pitch.midi,
        volume=note_in.volume.velocity,
        start_tick=quarter_length_to_ticks(start, time),
        end_tick=quarter_length_to_ticks(end, time),
    )
    return event


def event_to_note(event_in: MusicEvent, time: MusicTimeGrid) -> note.Note:
    # Convert MusicEvent to m21 note
    start = ticks_to_quarter_length(event_in.start_tick, time)
    end = ticks_to_quarter_length(event_in.end_tick, time)
    new_note = note.Note(pitch=event_in.pitch, quarterLength=end - start)
    new_note.volume.velocity = event_in.volume
    return new_note

