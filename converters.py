"""
Musicom converters module
Module for converting musical scores between different formats using Music21 and MusicPy.
"""
from config import Config
import platform

from structures import MusicUnit, MusicVoice

from musicpy import musicpy as mp
from music21 import converter, stream, note, chord, midi

# Conversion between music21 and musicpy
from music21py import m21_to_mpy, mpy_to_m21
from showscore import show

def score_show(self):
    """
    Show or play the score depending on the platform.
    1. On Windows, display text and musical notation.
    2. On iOS, display text (MIDI playback code is commented out).
    """
    if platform.system() == 'Windows':
        self.score.show('text')
        #    score.show('midi')  # Play MIDI
        show(self.score)  # Show musical notation

    elif platform.system() == 'IOS':
        self.score.show('text')

        # Play the result (IOS):
        # player = sound.MIDIPlayer('target.mid')
        # player.play()
        # player.stop()


# Composition converters
def voices_to_parts (self):
    # Convert voices to score parts
    for v in self.voices:
        self.score.append(v.part)

def parts_to_voices (self):
    # Convert score parts to voices
    self.voices = []
    for p in self.score.parts:
        unit = MusicUnit()
        voice = MusicVoice(name=p.partName, units=[unit])
        voice.part = p
        self.voices.append(voice)

def score_to_piece (self):
    # convert music21 score to musicpy piece
    self.piece = m21_to_mpy(self.score)

def piece_to_score (self):
    # convert musicpy piece to music21 score
    self.score = mpy_to_m21(self.piece)

def piece_play (self):
    # Play piece and wait until finish, writes temp.midi
    mp.play(self.piece, wait=True)

def load (self, filename_in: str = Config.DEFAULT_MIDI_FILE_IN):
    # Load a score
    self.score = converter.parse (Config.DEFAULT_PATH + filename_in)
    self.piece = mp.read(Config.DEFAULT_PATH + Config.DEFAULT_MIDI_FILE_IN, get_off_drums=True, split_channels=True)

def save (self, filename_out: str = Config.DEFAULT_MIDI_FILE_OUT):
    # Save score
    self.score.write(fmt='midi', fp=Config.DEFAULT_PATH + filename_out)

def write_to_midi (self):
    # Set to percussion instrument (General MIDI channel 10)
    # Write to MIDI
    mf = midi.translate.streamToMidiFile(self.score)
    # music21 uses an unpitched instrument class; channel will be set by MIDI export
    mf.open(Config.DEFAULT_PATH+'percussion_example.mid', 'wb')
    mf.write()
    mf.close()

def print_piece (self):
    for i in range(len(self.voices)):
        self.voices[i].track_print()


# Voice converters
def track_play (self):
    mp.play(self.track, wait=True)

def track_print(self):
    print('Name     : ' + str(self.track.track_name))
    print('Notes    : ' + str(self.track.content.notes))
    print('Duration : ' + str(self.track.content.duration))
    print('Interval : ' + str(self.track.content.interval))

def units_to_part (self):
    for u in self.units:
        u.unit_to_stream()
        self.part.append(u.stream)

def part_to_unit (self) -> MusicUnit:
    # Convert part to unit
    unit = MusicUnit()
    unit.stream = stream.Stream()
    for e in self.part.recurse().notesAndRests:
        unit.stream.append(e)
    self.units.append(unit)
    return unit

# Unit converters
def unit_to_chord(self):
    self.chord = mp.structures.chord(self.pitch_nodes, self.durations, self.onset_intervals, self.velocities)

def chord_to_unit(self):
    self.pitch_nodes = self.chord.notes
    self.nodes_to_intervals()
    self.durations = self.chord.get_duration()
    self.onset_intervals = self.chord.interval
    self.velocities = self.chord.get_volume()

def unit_to_stream (self):
    # Create a stream with notes and rests
    # Iterate over the list of pitches, intervals, durations and velocities
    for i in range(len(self.pitch_nodes)):
        # Add notes and rests to the stream
        restduration = self.onset_intervals[i] - self.durations[i]
        if restduration > 0:
            self.stream.append(note.Rest(quarterLength=restduration))
        else:
            new_note = note.Note(pitch=self.pitch_nodes[i], quarterLength=self.durations[i])
            new_note.volume.velocity = self.velocities[i]
            self.stream.append(new_note)

def stream_to_unit (self):
    # Convert m21 stream to unit
    # via chord
    self.stream_to_chord()
    self.chord_to_unit()
    # direct
    """
    for i in range(len(self.pitch_nodes)):
        # Add notes and rests to the unit
        if isinstance(element, note.Note):
            self.pitch_nodes += self.stream[i].pitch.midi

        if isinstance(element, note.Rest):
            restduration = self.onset_intervals[i] - self.durations[i]
            self.velocities[i] += self.stream[i].volume.velocity

    self.nodes_to_intervals()
    """
    # Transfer notes, rests and chords from the stream to the unit
    for element in self.stream:
        if isinstance(element, (note.Note, note.Rest, chord.Chord)):
            if isinstance(element, note.Note):
                self.pitch_nodes += [element.pitch.midi]
                self.durations += [element.duration.quarterLength]
                self.velocities += [element.volume.velocity if element.volume.velocity is not None else 100]
            elif isinstance(element, note.Rest):
                # Add rest as onset interval
                if len(self.onset_intervals) == 0:
                    self.onset_intervals += [element.duration.quarterLength]
                else:
                    self.onset_intervals[-1] += element.duration.quarterLength
            elif isinstance(element, chord.Chord):
                for p in element.pitches:
                    self.pitch_nodes += [p.midi]
                    self.durations += [element.duration.quarterLength]
                    self.velocities += [element.volume.velocity if element.volume.velocity is not None else 100]


def stream_to_chord (self):
    # convert music21 score to musicpy piece
    self.chord = m21_to_mpy(self.stream)

def chord_to_stream (self):
    # convert musicpy piece to music21 score
    self.stream = mpy_to_m21(self.chord)
