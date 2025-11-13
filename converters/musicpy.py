from constants import MIDIinstrument
from utilities import Config
from structures import MusicUnit, MusicSection
from musicpy import musicpy, structures
from music21 import stream
from music21py import mpy_to_m21

def chord_to_stream (chord: structures.chord) -> stream.Stream:
    # convert musicpy piece to music21 score
    return mpy_to_m21(chord)


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
def unit_to_sound (unit: MusicUnit, midi_instrument: int = MIDIinstrument.PIANO):
    musicpy.play (unit_to_chord (unit), bpm=unit.time.bpm, instrument=midi_instrument, wait=True)

def unit_to_chord(unit: MusicUnit) -> structures.chord:
    return structures.chord(unit.pitch_nodes, unit.durations, unit.onset_intervals, unit.volumes)

def chord_to_unit(chord: structures.chord) -> MusicUnit:
    unit = MusicUnit()
    unit.pitch_nodes = chord.notes
    unit.durations = chord.get_duration()
    unit.onset_intervals = chord.interval
    unit.volumes = chord.get_volume()
    return unit

def section_to_track(section: MusicSection) -> structures.track:
    """Build a musicpy track by concatenating unit chords if available."""
    t = structures.track([], track_name=section.name)
    for u in section.units:
        if hasattr(u, 'chord') and u.chord is not None:
            try:
                t = t + u.chord
            except Exception:
                # fall back to extend if addition is not supported
                try:
                    t.extend(u.chord)
                except Exception:
                    pass
    return t

def piece_play (piece : structures.piece):
    # Play piece and wait until finish, writes temusicpy.midi
    musicpy.play(piece, wait=True)
