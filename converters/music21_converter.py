"""Converters between music21 and other structures."""
import platform

from structures.unit import MusicEvent
from utilities import Config
from structures import Cardinality, PatternType, MusicTime, MusicUnit, MusicMatrix, MusicPattern
from converters.time import time_to_meter, time_to_tempo
from music21 import serial, stream, note, midi, converter, scale, key
from musicpy import structures
from showscore import show
from music21py import m21_to_mpy

def stream_to_chord (stream_in: stream.Stream) -> structures.chord:
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


def pattern_to_m21scale (pattern : MusicPattern) -> scale.ConcreteScale:
    # Convert pattern to music21 scale
    m21scale = scale.ConcreteScale()
    # Diatonic (7 pitch class) scale
    if pattern.cardinality == Cardinality.HEPTA and pattern.pattern_type == PatternType.SCALE:
        # m21 scale from key
        m21key = key.Key(mode=pattern.mode_name, tonic=note.Pitch(pattern.tonic_pitch_class))
        m21scale = m21key.getScale()

    return m21scale


def tonerow_to_stream (tonerow_base: serial.ToneRow = serial.ToneRow(row=[0, 4, 7, 4]),
                   octave : int = 4
                   ) -> stream.Stream:
    """Convert a tone row to a music21 stream."""
    stream_out = stream.Stream()
    # Tone row
    for pcs in enumerate(tonerow_base):
        pcs.octave = octave
        stream_out.append(pcs)

    return stream_out


def score_to_midifile (score: stream.Score , filename_out: str = Config.DEFAULT_MIDI_FILE_OUT):
    # Save score
    score.write(fmt='midi', fp=Config.DEFAULT_PATH + filename_out)


def midifile_to_score (filename_in: str = Config.DEFAULT_MIDI_FILE_IN) -> stream.Score:
    # Load a score
    return converter.parse (Config.DEFAULT_PATH + filename_in)


def percussion_stream_to_midifile (stream_in: stream.Stream, filename_out: str = Config.DEFAULT_MIDI_FILE_OUT):
    # Set to percussion instrument (General MIDI channel 10)
    # Write to MIDI
    mf = midi.translate.streamToMidiFile(stream_in)
    # music21 uses an unpitched instrument class; channel will be set by MIDI export
    mf.open(Config.DEFAULT_PATH+filename_out, 'wb')
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
        #score.show('midi')  # Play MIDI
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


def unit_to_stream (unit: MusicUnit) -> stream.Stream:
    # Convert unit to m21 stream
    if unit is None:
        return stream.Stream()
    # Create a stream with notes and rests
    stream_out = stream.Stream()
    # Iterate over the list of pitches, intervals, durations and volumes
    for i in range(len(unit.pitch_nodes)):
        # Add notes and rests to the stream
        restduration = unit.onset_intervals[i] - unit.durations[i]
        if restduration > 0:
            stream_out.append(note.Rest(quarterLength=restduration))
        new_note = note.Note(pitch=unit.pitch_nodes[i], quarterLength=unit.durations[i])
        new_note.volume.velocity = unit.volumes[i]
        stream_out.append(new_note)
    return stream_out


def stream_to_unit (stream_in : stream.Stream) -> MusicUnit:
    # Convert m21 stream to unit
    unit = MusicUnit()
    # Transfer notes, rests and chords from the stream to the unit
    for element in stream_in.flatten():
        if isinstance(element, note.Note):
            event = MusicEvent(pitch=element.pitch.midi,
                               volume=element.volume.velocity if element.volume.velocity is not None else 100,
                               duration=element.duration.quarterLength,
                                onset_time = element.offset,
            )
            unit.add_event(event)
    return unit

def note_to_event (note_in : note.Note) -> MusicEvent:
    # Convert m21 note to MusicEvent
    event = MusicEvent(pitch=note_in.pitch.midi,
                       volume=note_in.volume.velocity if note_in.volume.velocity is not None else 100,
                       duration=note_in.duration.quarterLength,
                       onset_time=0.0,
                       )
    return event

def time_to_stream(stream_ : stream.Stream, time : MusicTime):
    # Set the time signature and tempo
    stream_.insert(0, time_to_meter(time))
    stream_.insert(0, time_to_tempo(time))


# Matrix converters

def matrix_row_to_stream(matrix: MusicMatrix, row: int) -> stream.Stream:
    """Concatenate the music21 streams from contained units into a single Stream."""
    stream_out = stream.Stream()
    for col in range(matrix.cols):
        unit_ = matrix.get_unit(row, col)
        if unit_ is None:
            rest_ = note.Rest()
            #TODO: fix duration calculation for empty units
            rest_.duration = matrix.units_in_col(col)[0].timesteps
            stream_out.append(rest_)
        else:
            stream_out.append(unit_to_stream(unit_))
    return stream_out
