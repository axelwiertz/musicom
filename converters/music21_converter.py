"""Converters between music21 and other structures."""
import platform
from utilities import Config
from structures import MusicEvent, Cardinality, PatternType, MusicTime, MusicUnit, MusicMatrix, MusicPattern
from converters.time import time_to_meter, time_to_tempo, ticks_to_quarter_length, quarter_length_to_ticks
from music21 import serial, stream, note, chord, midi, converter, scale, key
from musicpy import structures
from showscore import show
from music21py import m21_to_mpy


def stream_to_chord(stream_in: stream.Stream) -> structures.chord:
    # convert music21 stream to musicpy chord
    return m21_to_mpy(stream_in)


def key_to_pattern(m21key: key.Key) -> MusicPattern:
    """Convert music21 key to MusicPattern."""

    # Assuming a standard heptatonic scale from a key
    pattern = MusicPattern("Heptatonic Scale from Key",
                           cardinality=Cardinality.HEPTA,
                           pattern_type=PatternType.SCALE,
                           )
    # Set mode and tonic
    pattern.set_mode_name(m21key.mode)
    pattern.set_tonic_pitch_class(m21key.tonic.pitchClass)

    return pattern


def pattern_to_m21scale(pattern: MusicPattern) -> scale.ConcreteScale:
    # Convert pattern to music21 scale
    m21scale = scale.ConcreteScale()
    # Diatonic (7 pitch class) scale
    if pattern.cardinality == Cardinality.HEPTA and pattern.pattern_type == PatternType.SCALE:
        # m21 scale from key
        m21key = key.Key(mode=pattern.mode_name, tonic=note.Pitch(pattern.tonic_pitch_class))
        m21scale = m21key.getScale()

    return m21scale


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


def score_to_midifile(score: stream.Score, filename_out: str = Config.DEFAULT_MIDI_FILE_OUT):
    # Save score
    score.write(fmt='midi', fp=Config.DEFAULT_PATH + filename_out)


def midifile_to_score(filename_in: str = Config.DEFAULT_MIDI_FILE_IN) -> stream.Score:
    # Load a score
    return converter.parse(Config.DEFAULT_PATH + filename_in)


def percussion_stream_to_midifile(stream_in: stream.Stream, filename_out: str = Config.DEFAULT_MIDI_FILE_OUT):
    # Set to percussion instrument (General MIDI channel 10)
    # Write to MIDI
    mf = midi.translate.streamToMidiFile(stream_in)
    # music21 uses an unpitched instrument class; channel will be set by MIDI export
    mf.open(Config.DEFAULT_PATH + filename_out, 'wb')
    mf.write()
    mf.close()


def score_to_visual(score: stream.Score):
    """
    Show or play the score depending on the platform.
    1. On Windows, display text and musical notation.
    2. On iOS, display text (MIDI playback code is commented out).
    """
    if platform.system() == 'Windows':
        score.show('text')
        #    score.show('midi')  # Play MIDI
        # Showing score without external programs like Musescore
        show(score)  # Show musical notation

    elif platform.system() == 'IOS':
        score.show('text')


def score_to_sound(score: stream.Score):
    # Play or show the score depending on the platform.
    if platform.system() == 'Windows':
        score.show('text')
        # score.show('midi')  # Play MIDI
        show(score)  # Show musical notation

    elif platform.system() == 'IOS':
        # Pyhonista may not support direct MIDI playback; try to import sound module if available
        import importlib
        try:
            sound = importlib.import_module('sound')
        except ImportError:
            sound = None
        # Play the result (IOS) when sound module is available
        score.show('text')
        player = sound.MIDIPlayer('target.mid')
        player.play()
        player.stop()


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


def note_to_event(note_in: note.Note, time: MusicTime) -> MusicEvent:
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


def event_to_note(event_in: MusicEvent, time: MusicTime) -> note.Note:
    # Convert MusicEvent to m21 note
    start = ticks_to_quarter_length(event_in.start_tick, time)
    end = ticks_to_quarter_length(event_in.end_tick, time)
    new_note = note.Note(pitch=event_in.pitch, quarterLength=end - start)
    new_note.volume.velocity = event_in.volume
    return new_note


def time_to_stream(stream_: stream.Stream, time: MusicTime):
    # Set the time signature and tempo
    stream_.insert(0, time_to_meter(time))
    stream_.insert(0, time_to_tempo(time))


def tick_gap_to_rest(tick_gap: int, time: MusicTime) -> note.Rest:
    """Convert a tick gap to a music21 Rest."""
    rest_ = note.Rest()
    rest_.duration = ticks_to_quarter_length(tick_gap, time)
    return rest_

# Matrix converters

def matrix_row_to_stream(matrix: MusicMatrix, row: int, time: MusicTime) -> stream.Stream:
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
