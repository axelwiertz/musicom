
from utilities import Config
from music21 import stream, converter, midi
from musicpy import musicpy, structures


# MIDI file converters
def midifile_to_piece(filename_in: str = Config.DEFAULT_MIDI_FILE_IN) -> structures.piece:
    # Load a piece
    return musicpy.read(Config.DEFAULT_PATH + filename_in, get_off_drums=True, split_channels=True)


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
