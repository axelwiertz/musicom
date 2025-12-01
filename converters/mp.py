"""MusicPy converters."""
from base.midi import MidiInstrument
from base.twelvetone import PitchClass
from base.diatonic import Cardinality, PatternType
from utilities.config import Config
from structures.unit import MusicUnit
from structures.time import MusicTime
from structures.project import MusicVoice
from structures.pattern import MusicPattern
from musicpy import musicpy, structures
from music21 import stream
from music21py import mpy_to_m21

def chord_to_stream (chord: structures.chord) -> stream.Stream:
    # convert musicpy piece to music21 score
    return mpy_to_m21(chord)

def pattern_to_mpscale (pattern : MusicPattern ) -> structures.scale:
    mpscale = structures.scale()

    # Diatonic (7 pitch class) scale
    if pattern.cardinality == Cardinality.HEPTA and pattern.interval_pattern == PatternType.SCALE:
        # MusicPy structures
        mpscale = structures.scale(PitchClass.NAMES_SHARP[pattern.tonic], interval=pattern.modes[pattern.mode])

    return mpscale


def midifile_to_piece (filename_in: str = Config.DEFAULT_MIDI_FILE_IN) -> structures.piece:
    # Load a piece
    return musicpy.read(Config.DEFAULT_PATH + filename_in, get_off_drums=True, split_channels=True)

# Print converters
def track_to_print(track: structures.track):
    print('Name     : ' + str(track.track_name))
    print('Notes    : ' + str(track.content.notes))
    print('Duration : ' + str(track.content.duration))
    print('Interval : ' + str(track.content.interval))

def modulate_unit(unit: MusicUnit,
                  scale_source: structures.scale,
                  scale_target: structures.scale):
    # Modulate
    unit.pitch_nodes = unit_to_chord(unit).modulation(scale_source, scale_target).pitches


# Unit converters
def unit_to_sound (unit: MusicUnit, time : MusicTime, midi_instrument: int = MidiInstrument.PIANO):
    musicpy.play (unit_to_chord (unit), bpm=time.bpm, instrument=midi_instrument, wait=True)

def unit_to_chord(unit: MusicUnit) -> structures.chord:
    return structures.chord(unit.pitch_nodes, unit.durations, unit.onset_intervals, unit.volumes)

def chord_to_unit(chord: structures.chord) -> MusicUnit:
    unit = MusicUnit()
    unit.pitch_nodes = chord.notes
    unit.durations = chord.get_duration()
    unit.onset_intervals = chord.interval
    unit.volumes = chord.get_volume()
    return unit

def voice_to_track(voice: MusicVoice) -> structures.track:
    """Build a musicpy track by concatenating unit chords if available."""
    track = structures.track([], track_name=voice.name)
    for unit in voice.units:
        track += unit_to_chord(unit)
    return track

def piece_play (piece : structures.piece):
    # Play piece and wait until finish, writes temusicpy.midi
    musicpy.play(piece, wait=True)
