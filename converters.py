"""
Musicom converters
Module for converting musical scores between different formats using Music21 and MusicPy.
"""
from config import Config
import platform

from constants import MIDIinstrument
from structures import MusicUnit, MusicVoice, MusicComposition

from musicpy import structures, musicpy as mp
from music21 import converter, stream, note, chord, midi, serial

# Conversion between music21 and musicpy
from music21py import m21_to_mpy, mpy_to_m21
# Show score
from showscore import show

# Helper functions
def sequence_rotations(sequence: list | tuple) -> list:
    # Generate all rotations of a given sequence
    rotations = [sequence[x:] + sequence[:x] for x in range(len(sequence))]
    return rotations

def interval_to_step(intervals: list[int]) -> list[int]:
    # Convert a list of n intervals to a sequential mask with n+1 sequential degree/onset numbers and zeroes
    # Example [2, 3] -> [1, 0, 2, 0, 0, 3]
    steps = []
    sequence_nr = 1
    for x in intervals:
        steps.append(sequence_nr)
        sequence_nr += 1
        for y in range(1, x):
            steps.append(0)
    return steps

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


# Composition converters: display and playback
def comp_to_visual(comp: MusicComposition):
    """
    Show or play the score depending on the platform.
    1. On Windows, display text and musical notation.
    2. On iOS, display text (MIDI playback code is commented out).
    """
    if platform.system() == 'Windows':
        comp.score.show('text')
        #    score.show('midi')  # Play MIDI
        # Showing score without external programs like Musescore
        show(comp.score)  # Show musical notation

    elif platform.system() == 'IOS':
        comp.score.show('text')

def comp_to_sound(comp: MusicComposition):
    # Play or show the score depending on the platform.
    if platform.system() == 'Windows':
        comp.score.show('text')
        #    score.show('midi')  # Play MIDI
        show(comp.score)  # Show musical notation

    elif platform.system() == 'IOS':
        # Pyhonista does not support direct MIDI playback, so we use MIDIPlayer
        import sound
        # Play the result (IOS):
        comp.score.show('text')
        player = sound.MIDIPlayer('target.mid')
        player.play()
        player.stop()

# Voice converters
def track_play (self):
    mp.play(self.track, wait=True)

def track_to_print(voice: MusicVoice):
    print('Name     : ' + str(voice.track.track_name))
    print('Notes    : ' + str(voice.track.content.notes))
    print('Duration : ' + str(voice.track.content.duration))
    print('Interval : ' + str(voice.track.content.interval))

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
def unit_to_sound (unit: MusicUnit, midi_instrument: int = MIDIinstrument.PIANO):
    mp.play (unit.chord, bpm=unit.time.bpm, instrument=midi_instrument, wait=True)

def unit_to_chord(unit: MusicUnit):
    unit.chord = structures.chord(unit.pitch_nodes, unit.durations, unit.onset_intervals, unit.velocities)

def chord_to_unit(unit: MusicUnit):
    unit.pitch_nodes = unit.chord.notes
    unit.nodes_to_intervals()
    unit.durations = unit.chord.get_duration()
    unit.onset_intervals = unit.chord.interval
    unit.velocities = unit.chord.get_volume()

def unit_to_stream (unit: MusicUnit):
    # Create a stream with notes and rests
    # Iterate over the list of pitches, intervals, durations and velocities
    for i in range(len(unit.pitch_nodes)):
        # Add notes and rests to the stream
        restduration = unit.onset_intervals[i] - unit.durations[i]
        if restduration > 0:
            unit.stream.append(note.Rest(quarterLength=restduration))
        else:
            new_note = note.Note(pitch=unit.pitch_nodes[i], quarterLength=unit.durations[i])
            new_note.volume.velocity = unit.velocities[i]
            unit.stream.append(new_note)

def stream_to_unit (unit: MusicUnit):
    # Convert m21 stream to unit
    # via chord
    stream_to_chord(unit)
    chord_to_unit(unit)
    # direct
    """
    for i in range(len(unit.pitch_nodes)):
        # Add notes and rests to the unit
        if isinstance(element, note.Note):
            unit.pitch_nodes += unit.stream[i].pitch.midi

        if isinstance(element, note.Rest):
            restduration = unit.onset_intervals[i] - unit.durations[i]
            unit.velocities[i] += unit.stream[i].volume.velocity

    unit.nodes_to_intervals()
    """
    # Transfer notes, rests and chords from the stream to the unit
    for element in unit.stream:
        if isinstance(element, (note.Note, note.Rest, chord.Chord)):
            if isinstance(element, note.Note):
                unit.pitch_nodes += [element.pitch.midi]
                unit.durations += [element.duration.quarterLength]
                unit.velocities += [element.volume.velocity if element.volume.velocity is not None else 100]
            elif isinstance(element, note.Rest):
                # Add rest as onset interval
                if len(unit.onset_intervals) == 0:
                    unit.onset_intervals += [element.duration.quarterLength]
                else:
                    unit.onset_intervals[-1] += element.duration.quarterLength
            elif isinstance(element, chord.Chord):
                for p in element.pitches:
                    unit.pitch_nodes += [p.midi]
                    unit.durations += [element.duration.quarterLength]
                    unit.velocities += [element.volume.velocity if element.volume.velocity is not None else 100]


def stream_to_chord (unit: MusicUnit):
    # convert music21 score to musicpy piece
    unit.chord = m21_to_mpy(unit.stream)

def chord_to_stream (unit: MusicUnit):
    # convert musicpy piece to music21 score
    unit.stream = mpy_to_m21(unit.chord)

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

def file_to_comp (comp: MusicComposition, filename_in: str = Config.DEFAULT_MIDI_FILE_IN):
    # Load a score
    comp.score = converter.parse (Config.DEFAULT_PATH + filename_in)
    comp.piece = mp.read(Config.DEFAULT_PATH + Config.DEFAULT_MIDI_FILE_IN, get_off_drums=True, split_channels=True)

def comp_to_file (comp : MusicComposition, filename_out: str = Config.DEFAULT_MIDI_FILE_OUT):
    # Save score
    comp.score.write(fmt='midi', fp=Config.DEFAULT_PATH + filename_out)

def comp_to_midifile (comp: MusicComposition):
    # Set to percussion instrument (General MIDI channel 10)
    # Write to MIDI
    mf = midi.translate.streamToMidiFile(comp.score)
    # music21 uses an unpitched instrument class; channel will be set by MIDI export
    mf.open(Config.DEFAULT_PATH+'percussion_example.mid', 'wb')
    mf.write()
    mf.close()

def print_piece (comp: MusicComposition):
    for i in range(len(comp.voices)):
        track_to_print(comp.voices[i])
