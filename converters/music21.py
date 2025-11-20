import platform
from utilities import Config
from structures import MusicUnit, MusicSection
from converters.musicpy import chord_to_unit
from analysis.music21 import serial, stream, note, midi, converter
from musicpy import structures
from showscore import show
from copy import deepcopy
from music21py import m21_to_mpy

def stream_to_chord (stream_in: stream.Stream) -> structures.chord:
    # convert music21 stream to musicpy chord
    return m21_to_mpy(stream_in)


# Music21 converters
def tonerow_to_stream (tonerow_base: serial.ToneRow = serial.ToneRow(row=[0, 4, 7, 4]),
                   octave : int = 4
                   ) -> stream.Stream:
    stream_out = stream.Stream()
    # Tonerow
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

def percussionscore_to_midifile (score: stream.Score, filename_out: str = Config.DEFAULT_MIDI_FILE_OUT):
    # Set to percussion instrument (General MIDI channel 10)
    # Write to MIDI
    mf = midi.translate.streamToMidiFile(score)
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
        #    score.show('midi')  # Play MIDI
        show(score)  # Show musical notation

    elif platform.system() == 'IOS':
        # Pyhonista may not support direct MIDI playback; try to import sound module if available
        try:
            import importlib
            sound = importlib.import_module('sound')
        except Exception:
            sound = None
        # Play the result (IOS) when sound module is available
        score.show('text')
        player = sound.MIDIPlayer('target.mid')
        player.play()
        player.stop()

def section_to_part (section: MusicSection) -> stream.Part:
    part_out = stream.Part()
    for u in section.units:
        part_out.append(unit_to_stream(u))
    return part_out

def part_to_unit (part : stream.Part) -> MusicUnit:
    # Convert part to unit
    unit = stream_to_unit(part_to_stream(part))
    return unit


def unit_to_stream (unit: MusicUnit) -> stream.Stream:
    # Create a stream with notes and rests
    stream_out = stream.Stream()
    # Iterate over the list of pitches, intervals, durations and volumes
    for i in range(len(unit.pitch_nodes)):
        # Add notes and rests to the stream
        restduration = unit.onset_intervals[i] - unit.durations[i]
        if restduration > 0:
            stream_out.append(note.Rest(quarterLength=restduration))
        else:
            new_note = note.Note(pitch=unit.pitch_nodes[i], quarterLength=unit.durations[i])
            new_note.volume.velocity = unit.volumes[i]
            stream_out.append(new_note)
    return stream_out

def stream_to_unit (stream_in : stream.Stream) -> MusicUnit:
    # Convert m21 stream to unit
    # via chord
    chord = stream_to_chord(stream_in)
    unit = chord_to_unit(chord)
    # direct
    """
    for i in range(len(unit.pitch_nodes)):
        # Add notes and rests to the unit
        if isinstance(element, note.Note):
            unit.pitch_nodes += unit.stream[i].pitch.midi

        if isinstance(element, note.Rest):
            restduration = unit.onset_intervals[i] - unit.durations[i]
            unit.volumes[i] += unit.stream[i].volume.velocity

    unit.nodes_to_intervals()
    """
    # Transfer notes, rests and chords from the stream to the unit
    for element in stream_in:
        if isinstance(element, (note.Note, note.Rest)):
            if isinstance(element, note.Note):
                unit.pitch_nodes += [element.pitch.midi]
                unit.durations += [element.duration.quarterLength]
                unit.volumes += [element.volume.velocity if element.volume.velocity is not None else 100]
            elif isinstance(element, note.Rest):
                # Add rest as onset interval
                if len(unit.onset_intervals) == 0:
                    unit.onset_intervals += [element.duration.quarterLength]
                else:
                    unit.onset_intervals[-1] += element.duration.quarterLength
    return unit

# Section converters

def section_to_stream(section: MusicSection) -> stream.Stream:
    """Concatenate the music21 streams from contained units into a single Stream."""
    s = stream.Stream()
    for u in section.units:
        if hasattr(u, 'stream') and u.stream is not None:
            # deep copy to avoid side effects when appending
            s.append(deepcopy(u.stream))
    return s
