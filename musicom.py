"""
Music Composition Assistant
"""
from config import Config
import platform
import copy
import random
from datetime import datetime
from collections import defaultdict
#import sound

from twelvetet import TwelveTET, MIDIpercussion, MIDIinstrument

# Musical datastructures
from theory import MusicTime, MusicScale, Diatonic, PitchRegister
from harmony import Scale7ChordHarmony, Scale7PitchDegree, Scale7Triad

# Genetic algorithm
from genetic import Genome, generate_population, run_evolution, print_stats, genome_to_string
# Conversion between music21 and musicpy
from music21py import *

# Showing score without external programs like Musescore
from showscore import show

# Music21 modules: music notation and analysis
from music21 import metadata, stream, roman, midi, converter, analysis, instrument, percussion, note, chord, key, tempo, clef, harmony, serial, scale, interval
# MusicPy modules: computational music structures and algorithms
from musicpy import musicpy as mp, algorithms, structures


class MusicUnit:
    # Harmonic rhythm: sequential pattern of onsets at timesteps
    # A rhythm sequence is defined by
    #  - a sequence of timestep intervals between onsets
    def __init__(self,
                time: MusicTime = MusicTime(),
                register: PitchRegister = PitchRegister(),
                pitch_nodes : list [int] = (),
                pitch_intervals: list[int] = (),
                onset_intervals: list[float] = (),
                durations: list[float] = (),
                velocities: list[int] = (),
                ):
        self.time = time
        self.register = register
        self.pitch_nodes = pitch_nodes
        self.pitch_intervals = pitch_intervals
        # The sum of the intervals is the total number of timesteps in MusicTime
        self.onset_intervals = onset_intervals
        self.durations = durations
        self.velocities = velocities
        #self.refresh()
        self.timesteps = sum(self.onset_intervals)

        # m21
        self.stream =  stream.Stream()
        # mp
        self.chord = structures.chord([])

    def __add__(self, other):
        # Combine two musical units
        new_unit = MusicUnit()
        new_unit.pitch_nodes = self.pitch_nodes + other.pitch_nodes
        new_unit.pitch_intervals = self.pitch_intervals + other.pitch_intervals
        new_unit.onset_intervals = self.onset_intervals + other.onset_intervals
        new_unit.durations = self.durations + other.durations
        new_unit.velocities = self.velocities + other.velocities

        # m21
        new_unit.stream = copy.deepcopy(self.stream)
        new_unit.stream.append(other.stream)
        # mp
        new_unit.chord = self.chord + other.chord

        new_unit.refresh()
        return new_unit

    def refresh (self):
        # Refresh derived attributes
        self.timesteps = sum(self.onset_intervals)


    def nodes_to_intervals(self):
        self.pitch_intervals = [self.pitch_nodes[i+1]-self.pitch_nodes[i] for i in range(len(self.pitch_nodes)-1)]

    def intervals_to_nodes(self, start_pitch_node: int = 0):
        self.pitch_nodes = []
        current_pitch = start_pitch_node
        self.pitch_nodes.append(current_pitch)
        for pitch_interval in self.pitch_intervals:
            current_pitch += pitch_interval
            self.pitch_nodes.append(current_pitch)

    def unit_to_chord(self):
        self.chord = structures.chord(self.pitch_nodes, self.durations, self.onset_intervals, self.velocities)

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

    def modulate (self,
                    scale_source : structures.scale,
                    scale_target : structures.scale):
        # Modulate
        self.chord = self.chord.modulation(scale_source, scale_target)

    def chord_play (self, midiinstrument: int = MIDIinstrument.PIANO):
        mp.play (self.chord, bpm=self.time.bpm, instrument=midiinstrument, wait=True)

    def add_pitch (self, pitch, duration : int = 1, onset_interval : int = 1, velocity: int = 100):
        self.pitch_nodes += [pitch]
        self.pitch_intervals += [self.pitch_nodes[-1] - self.pitch_nodes[-2] if len(self.pitch_nodes) > 1 else 0]
        self.onset_intervals += [onset_interval]
        self.durations += [duration]
        self.velocities += [velocity]

    def add_pitches_vertical (self, pitches, duration=4):
        for p in pitches:
            self.add_pitch(p,0, duration)

    def pitches_transpose (self, pitch_interval : int, direction : str = PitchRegister.ASCENDING):
        # Transpose the unit's pitches by interval in positive or negative direction (ASCENDING or DESCENDING)
        tonerow = serial.ToneRow(self.pitch_nodes).transpose(pitch_interval * direction)
        # Update pitch nodes
        return tonerow.pitches.midiNumbers

    # Transform pitch sequence in tomerow
    PRIME = 'P'
    INVERSION = 'I'
    RETROGRADE = 'R'
    RETROGRADE_INVERSION = 'RI'

    def random_select (self):
        return random.choice ([self.PRIME, self.INVERSION, self.RETROGRADE, self.RETROGRADE_INVERSION])

    def transform (self, trans : str, index : int = 0) -> list[int]:
        # Transform tone row
        tonerow = serial.ToneRow(self.pitch_nodes).zeroCenteredTransformation (trans, index)
        return tonerow.pitches.midiNumbers


class MusicVoice:
    # A musical voice
    def __init__(self,
                 name: str = 'Voice',
                 units: list[MusicUnit] = (),
                 midi_instrument: int = MIDIinstrument.PIANO,
                 ):
        self.name = name
        self.midi_instrument = midi_instrument
        self.units = units

        self.track = structures.track([], track_name=name,instrument=instrument)
        self.part = stream.Part()

    def track_notes(self, i: int = 0, j: int = 4):
        return self.track[i:j]

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


class MusicComposition:
    #
    def __init__(self,
                 title: str = "Composition",
                 main_scale: MusicScale = MusicScale(Diatonic.HEPTA, Diatonic.SCALE, TwelveTET.C, Diatonic.major_mode),
                 voices : list[MusicVoice] = (),
                 main_progression: list = (),
                 form: list = ()
                ):

        self.title = title
        self.form = form
        self.main_scale = main_scale
        self.main_progression = main_progression
        self.voices = voices

        # Music21 score
        self.score = stream.Score()
        self.score.metadata = metadata.Metadata()
        self.score.metadata.title = title
        self.score.metadata.composer = 'Musicom'

        # MusicPy piece
        self.piece = structures.piece

    def voices_to_score (self):
        # Convert voices to score parts
        for v in self.voices:
            self.score.append(v.part)

    def score_set_time(self, time : MusicTime):
        # Set the time signature, key signature and tempo
        self.score.insert(0, time.timesignature)
        self.score.insert(0, tempo.MetronomeMark(number=time.bpm))

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

    def analysis(self):
        # Analyze score

        # self.score.plot('3d')
        # self.score.plot('histogram','pitch')
        # self.score.show('abc')
        # Key
        key01 = self.score.analyze('key')
        print('Score :')
        print(self.score)
        print(' with key ' + str(key01))

        # m21 Chord analysis
        chordset = self.score.chordify()
        # Check for specific chords
        for chd01 in chordset.recurse().getElementsByClass(chord.Chord):
            if chd01.isDominantSeventh():
                print(chd01.measureNumber, chd01.beatStr, chd01)

        # All chords
        for chd01 in chordset.recurse().getElementsByClass(chord.Chord):
            # Put chord in closed position
            chd01.closedPosition(forceOctave=4, inPlace=True)
            # Annotate chord intervals
            chd01.annotateIntervals(inPlace=True)
            # Add Roman numerals in lyrics
            rn = roman.romanNumeralFromChord(chd01, key01)
            chd01.addLyric(str(rn.figure))

        chordset.partName = "Chord analysis"
        self.score.append(chordset)
        self.score.makeMeasures(inPlace=True)
        # Music21 analysis
        result = analysis.metrical.labelBeatDepth(self.score)
        print('Metrical analysis: beat depth' + str(result))
        # MusicPy analysis
        str1 = algorithms.detect(self.piece)
        str2 = algorithms.chord_analysis(self.piece)
        str3 = mp.analyze_rhythm(self.piece)
        print('MusicPy analysis:')
        print(str1)
        print(str2)
        print(str3)


    def score_show (self):
        """
        Show or play the stream
        """
        if platform.system() == 'Windows':
            self.score.show('text')
    #    score.show('midi')  # Play MIDI
            show(self.score)  # Show musical notation

        elif platform.system() == 'IOS':
            self.score.show('text')

            # Play the result (IOS):
            #player = sound.MIDIPlayer('target.mid')
            #player.play()
            #player.stop()



class PercussionUnit(MusicUnit):

    def __init__(self):
        super().__init__()
        self.clef = clef.PercussionClef()
        self.instrument = instrument.Woodblock()



def progression_in_scale (chord_progression: list[int],
                            music_scale : MusicScale ):
    # Chord progression patterns in a key
    time = MusicTime(4,4,4)
    reg = PitchRegister()
    unit_prog = MusicUnit(time, reg)
    voice_prog = MusicVoice('Chord progression voice',
                            [unit_prog],
                            MIDIinstrument.PIANO)
    comp = MusicComposition('Chord progressions',
                       music_scale,
                       [voice_prog],
                       chord_progression,
                       [0]
                       )
    # mp
    unit_prog.chord = music_scale.mpscale.chord_progression(
            chord_progression,
            durations=1 / 2,
            intervals=0,
            volumes=None,
            chords_interval=None)
    # m21
    for i in range (len(chord_progression)):
        # m21 Create chord from Roman numeral
        chord01 = roman.RomanNumeral (chord_progression[i], keyOrScale=music_scale.m21scale)
        chord01.duration.quarterLength = 4
        unit_prog.stream.append(chord01)

    comp.score_show()

def triads_in_scale7 (scale7 : MusicScale):
    progression_in_scale([1,2,3,4,5,6,7],
                         scale7)

def compose_unit ():
    # Create a musical unit
    time = MusicTime(16, 4, 4, 120)
    reg = PitchRegister()
    unit = MusicUnit(time, reg,
                        [0, reg.index_of(TwelveTET.C,4),
                                    reg.index_of(TwelveTET.E,4)],
                        [0, 4],
                        [8, 3, 5],
                        [0, 3, 5],
                        [0, 100, 100])
    voice = MusicVoice('Compose voice', [unit], MIDIinstrument.PIANO)
    # Create a composition
    comp = MusicComposition('Composition',
                            MusicScale(Diatonic.HEPTA, Diatonic.SCALE, TwelveTET.C, Diatonic.major_mode),
                            [voice],
                            [1,4,5,1],
                            [0]
            )
    # Add several new notes in m21 stream
    unit.add_pitch(89, 2, 4, 100)
    unit.add_pitch(93, 2, 4, 100)

    triads = Scale7Triad()
    print (triads)
    # triads.pattern_major.pitch_intervals

    unit.unit_to_chord()
    unit.chord_play()

    voice.units_to_part()
    comp.voices_to_score()
    comp.score_show()


class MarkovChain:
    # Markov chain of transitions
    def __init__(self, train):
        # build transition dict for pitches
        self.trans = defaultdict(list)
        for a, b in zip(train, train[1:]):
            self.trans[a[0]].append(b[0])

    def sample(self, start, length=16):
        out = [start]
        cur = start
        for _ in range(length - 1):
            choices = self.trans.get(cur) or list(self.trans.keys())
            cur = random.choice(choices)
            out.append(cur)
        return out


def create_random_pitches ():

    chord_chain = MarkovChain(Scale7ChordHarmony.movement_rules)
    gen_chords = chord_chain.sample('1', length=16)
    print('Generated chords by Markov chain: ' + str(gen_chords))

    pitch_chain = MarkovChain(Scale7PitchDegree.movement_rules)
    gen_pitches = pitch_chain.sample('1', length=16)
    print('Generated pitches by Markov chain: ' + str(gen_pitches))


def create_population():
    # Use a genetic algorithm to create a population of musical units
    pr = PitchRegister()
    time = MusicTime(8, 4, 4, 100)
    unit = MusicUnit(time, pr)
    voice = MusicVoice('Genetic voice', [unit], MIDIinstrument.PIANO)
    comp = MusicComposition('Genetic '+str(int(datetime.now().timestamp())),
                             MusicScale(Diatonic.HEPTA, Diatonic.SCALE, TwelveTET.C, Diatonic.major_mode),
                [voice])

    def fitness_func(genome_in: Genome) -> int:
        # Simple fitness function: sum of genome values
        return sum(genome_in)

    # Binary genome representation
    pitch_interval_bits = 6  # binary 24 pitch intervals
    #max_pitch_interval = pow(2, pitch_interval_bits - 1)
    onset_interval_bits = 4  # binary 8 timesteps
    duration_bits = 4  # binary 8 timesteps
    velocity_bits = 4  # binary 8 levels
    totalbits = pitch_interval_bits + duration_bits + onset_interval_bits + velocity_bits

    # Run the genetic algorithm
    final_population, generations = run_evolution(
        populate_func=lambda: generate_population(10, 20),
        fitness_func=fitness_func,
        fitness_limit=20,
        generation_limit=50,
        printer=print_stats
    )

    print("Final Population after %d generations:" % generations)
    for genome in final_population:
        print("%s (Fitness: %d)" % (genome_to_string(genome), fitness_func(genome)))

    # Convert best genome to musical unit
    unit = MusicUnit(time)

    genome = final_population[0]
    # Transform a generated genome into a unit
    # Split genome in parts of 'bits' length
    numparts = len(genome) % totalbits
    genes_binary = []
    for i in range(numparts):
        # Extract binary elements
        genes_binary += [genome[(i * totalbits):(i * totalbits) + totalbits]]

    for gene_binary in genes_binary:
        pitch_nr = int(sum([bit * pow(2, i) for i, bit in enumerate(gene_binary)]))


    voice = MusicVoice('Genetic voice', [unit], MIDIinstrument.PIANO)
    voice.part.insert(0, clef.TrebleClef())
    voice.units_to_part()
    # Add clef of part

    comp.analysis()
    comp.score_show()
    comp.save()


def euclidian_rhythm (onsets: int = 4,
                      timesteps: int = 4 ) -> list [int] :
    # Divide number of onsets evenly over number of timesteps, reduced if duplicate

    # Onsets gets an equal timestep interval
    base_timestep_interval = timesteps // onsets
    # And the remaining timesteps are a separate time step interval
    remaining_timesteps = timesteps % onsets

    rhythm = []
    for i in range(onsets):
        rhythm_timestep_interval = base_timestep_interval
        if i < remaining_timesteps:
            rhythm_timestep_interval += 1
        rhythm.append (rhythm_timestep_interval)

    # Reduce
    while rhythm[0] != rhythm[-1]:
        for group in rhythm:
            if group != rhythm[-1]:
                    group += rhythm.pop(-1)

    last_interval = timesteps - sum(rhythm)
    if last_interval > 0:
        rhythm.append(last_interval)

    return rhythm

"""
These three aspects of TimeSignatures are controlled by the
music21.meter.TimeSignature.
    beatSequence   : where the beats in the measure are and how many there are
    beamSequence   : How the notes should be beamed
    accentSequence : How much accent or weight each note gets
All sequences are of class MeterSequence
"""

def create_rhythm ():

    time = MusicTime(8, 4, 4, 100)
    reg = PitchRegister()
    unit = MusicUnit(time, reg)
    voice = MusicVoice('Rhythm voice', [unit], MIDIinstrument.PIANO)
    comp = MusicComposition('Rhythm',
                            MusicScale(Diatonic.HEPTA, Diatonic.SCALE, TwelveTET.C, Diatonic.major_mode),
                            [],
                            [0],
                            [voice]
                            )
    unit.onset_intervals = euclidian_rhythm (3, 8)
    unit.intervals_to_nodes()

    voice.units_to_part()
    comp.voices_to_score()
    comp.score_show()


def percussion_load ():
    # Load
    comp = MusicComposition('Percussion')
    comp.load('r_son.mid')
    unit = MusicUnit()
    unit.stream = comp.score.flatten()
    unit.stream_to_unit()
    voice = MusicVoice('Percussion voice', [unit], MIDIinstrument.PERCUSSION)

    voice.units_to_part()
    comp.voices_to_score()
    comp.score_show()

    comp.analysis()
    comp.load('midipercussionmidi.mid')

    comp.score.append(clef.PercussionClef())

    comp.score_show()



def create_percussion ():
    # Meter 4/4, 8 timesteps, 0,5 beat per timestep
    time = MusicTime(8, 4, 4, 100)
    reg = PitchRegister()
    unit_bass = MusicUnit (
        time, reg,
        # Onset lines
        # bass drum on beats 1 & 3), snare on 2 & 4,
        [MIDIpercussion.BASS_DRUM, MIDIpercussion.ACOUSTIC_SNARE, MIDIpercussion.BASS_DRUM, MIDIpercussion.ACOUSTIC_SNARE],
        [],
        [2, 2, 2, 2],
        [1, 1, 1, 1],
        [110, 110, 110, 110, 110, 110, 110, 110])

    unit_hihat = MusicUnit (
        time, reg,
        # hh on every eighth
        [MIDIpercussion.CLOSED_HIHAT, MIDIpercussion.CLOSED_HIHAT, MIDIpercussion.CLOSED_HIHAT, MIDIpercussion.CLOSED_HIHAT,
                         MIDIpercussion.CLOSED_HIHAT, MIDIpercussion.CLOSED_HIHAT, MIDIpercussion.CLOSED_HIHAT, MIDIpercussion.CLOSED_HIHAT],
        [],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [70, 70, 70, 70, 70, 70, 70, 70])

    voice = MusicVoice('Percussion voice', [unit_bass, unit_hihat], MIDIinstrument.PERCUSSION)


    # Create
    comp = MusicComposition('Percussion')

    pchord = percussion.PercussionChord()


    unit_bass.unit_to_stream()

    unit_hihat.unit_to_stream()

    voice.units_to_part()
    comp.voices_to_score()

    comp.score_show()
    comp.write_to_midi()

class ChordSet:
    """
    Set of chords
    """
    def __init__(self, chords):
        self.chords = chords
        
        ch = chord.Chord()
        
        h = harmony.ChordSymbol('maj7', 'C')
        h.romanNumeral = roman.RomanNumeral('I', 'C')
        h.romanNumeral = roman.RomanNumeral('IV', 'A')

        self.chords.append(harmony.ChordSymbol('sus4', 'D'))
        self.chords[1].romanNumeral = 'III'
        self.chords[1].romanNumeral.key = key.Key('B')




def project_big_yellow_taxi():
    # Big Yellow Taxi

    t = TwelveTET()
    helix = PitchRegister()

    time = MusicTime(8,4,4)
    comp = MusicComposition('Big yellow taxi',
                            MusicScale(Diatonic.HEPTA, Diatonic.SCALE, TwelveTET.B_FLAT, Diatonic.major_mode))


    # Create unit
    unit = MusicUnit(time,
        t.name_to_midi (name=['B3', 'C#4', 'E4', 'E4', 'F#4', 'C#4', 'E4', 'E4', 'F#4', 'E4', 'G#3', 'B3', 'B3', 'C#4',
        'E4', 'F#4', 'B3', 'B3', 'F#4', 'F#4', 'F#4', 'G#4', 'F#4', 'E4', 'E4'])
        )
    # Analyze score
    comp.analysis()

def project_berendans():
    # Berendans
    reg = PitchRegister()
    time = MusicTime(8,4,4)
    # Create units
    unit1 = MusicUnit(time,reg)
    unit2 = MusicUnit(time,reg)
    # Create voices
    voice1 = MusicVoice('Melody voice', [unit1], MIDIinstrument.FLUTE)
    voice2 = MusicVoice('Accompaniment voice', [unit2], MIDIinstrument.PIANO)
    # Create composition
    comp = MusicComposition('Berendans',
                       MusicScale(Diatonic.HEPTA, Diatonic.SCALE, TwelveTET.B_FLAT, Diatonic.major_mode),
                [voice1, voice2])


def create_new ():
    tt = TwelveTET()
    # New composition
    time = MusicTime(4,4,4)
    reg = PitchRegister()
    unit1a = MusicUnit(time,reg,
                      tt.name_to_midi(['C5', 'D5', 'E5', 'F5']),
                      [1,1,1,1],
                      [1, 1, 1, 1],
                      [100, 100, 100,100])
    unit1b = MusicUnit(time,reg,
                      tt.name_to_midi(['G5', 'A5', 'B4', 'C5']),
                      [1,1,1,1],
                      [1, 1, 1, 1],
                      [100, 100, 100,100])

    unit2a = MusicUnit(time,reg,
                      tt.name_to_midi(['C4', 'E4', 'G4']),
                        [1,1,2],
                        [1, 1, 1],
                        [100, 100, 100])
    unit2b = MusicUnit(time,reg,
                      tt.name_to_midi(['F4', 'A4', 'C5']),
                        [1,1,2],
                        [1, 1, 1],
                        [100, 100, 100])

    unit3 = MusicUnit(time,reg,
                      tt.name_to_midi(['C3', 'G3']),
                        [2,2],
                        [2,2],
                        [100, 100])

    # Patterns in scales
    # 3 Tria patterns:
    scale3 = MusicScale (Diatonic.TRIA, Diatonic.MAJOR)
    # 4 Tetra patterns:
    scale4 = MusicScale(Diatonic.TETRA, Diatonic.MAJOR7)
    # 5 Penta patterns:
    scale5 = MusicScale(Diatonic.PENTA, Diatonic.SCALE)


    # Create three voices for melody and accompaniment
    voice1 = MusicVoice('Voice 1', [unit1a, unit1b], MIDIinstrument.FLUTE)
    voice2 = MusicVoice('Voice 2', [unit2a, unit2b], MIDIinstrument.VIOLIN)
    voice3 = MusicVoice('Accomp', [unit3], MIDIinstrument.BASS)

    comp = MusicComposition('New',
                            MusicScale(Diatonic.HEPTA, Diatonic.SCALE, TwelveTET.C, Diatonic.major_mode),
                            [voice1, voice2, voice3],
                       [],
                       [0, 0, 1, 0])

    pitches_list = [comp.main_scale.m21scale.pitches[0:3],
                    ["G4", "A4", "B4", "C5"]]

    for v in comp.voices:
        v.units_to_part()

    # Analyze score
    comp.analysis()
    comp.score_show()
    # Save score
    comp.save("new.mid")


def create_balfolk ():
    tt = TwelveTET()
    # Style : Balfolk
    # Parts:  melody and bass
    reg = PitchRegister()
    # typical Balfolk rhythm
    time = MusicTime(6, 6, 8, 120)
    unit = MusicUnit(time,reg)
    # C major/A minor
    scale7aminor = MusicScale(Diatonic.HEPTA, Diatonic.SCALE, tt.A, Diatonic.minor_mode)

    melody_voice = MusicVoice()
    bass_voice = MusicVoice()
    comp = MusicComposition('Balfolk',
                            MusicScale(Diatonic.HEPTA, Diatonic.SCALE, tt.C, Diatonic.major_mode),
                            [melody_voice, bass_voice],
                            [1,2,3,4],
                            [0, 1, 2, 3]
                            )

    # Bourrée-inspired melody

    # Create notes with Balfolk-style rhythm
    melody_notes = [
        ['C4', 'E4', 'G4'],
        ['D4', 'F4', 'A4'],
        ['E4', 'G4', 'B4'],
        ['F4', 'A4', 'C5']
    ]
    melody_intervals = [1, 1, 1]
    melody_onsets = [1, 1, 1]
    melody_durations = [1, 1, 1]

    # Create melody with rhythmic variation
    for i in range(16):  # 4 measures
        # Choose a random melodic fragment
        fragment = random.choice(melody_notes)

        # Arpeggiate chords
        for note_name in fragment:
            n = note.Note(note_name)
            n.duration.type = 'eighth'
            melody_voice.part.append(n)

    # Create accompaniment (drone/rhythmic support)
    bass_notes = ['C3', 'G3']
    for i in range(32):  # matching melody length
        bass_note = note.Note(random.choice(bass_notes))
        bass_note.duration.type = 'eighth'
        bass_voice.part.append(bass_note)

    # Analyze score
    comp.analysis()
    comp.score_show()
    # Save score
    comp.save("balfolk.mid")


def create_counterpoint():

    h = PitchRegister()
    main_key = key.Key('C', 'major')
    main_scale = scale.MajorScale ('C')

    # Counterpoint
    comp = MusicComposition('Counterpoint')

    length = 16  # Length of the counterpoint

    voice1, voice2 = MusicUnit()
    voice1.stream = stream_create_random_from_list(length)
    voice2.stream = stream_create_random_from_list(length)

    # Keep generating until counterpoint reached
    while not stream_is_counterpoint(voice1, voice2):
        voice2 = stream_create_random_from_list(length)

    comp.score.append(voice1)
    comp.score.append(voice2)
    # Analyze score
    comp.analysis()
    comp.score_show()
    # Save score
    comp.save()


def create_key_library (musicscale: MusicScale):
    # Create a score with library elements
    reg = PitchRegister()
    time = MusicTime(4, 4, 4)
    # Common chord progressions
    #
    triads_in_scale = MusicUnit(time, reg)
    triads_in_scale.chord = musicscale.mpscale % (1234567, 1)

    prog_in_scale = MusicUnit(time, reg)
    progression_in_scale(Scale7ChordHarmony.common_progressions, musicscale)

    voice = MusicVoice('Chord progression voice', [triads_in_scale, prog_in_scale], MIDIinstrument.PIANO)
    comp = MusicComposition('Chord progressions and triads',
                            musicscale,
                            [voice],
                            [1,2,3,4,5,6,7],
                            [0,1])

    comp.analysis()
    comp.score_show()
    # Save score
    comp.save('chordlibrary_in_key_' + TwelveTET.PITCH_CLASS_NAMES_SHARP(musicscale.tonic) +'.mid')


def harmonic_series (fundamental_pitch  : int,
                           harmonic_numbers: list[int] = range(1,17)) -> chord.Chord:
    # The harmonic series of a fundamental pitch

    harmonic_chord = chord.Chord()
    stream_out = stream.Stream()
    for harmonic in harmonic_numbers:
        new_pitch = note.Pitch(fundamental_pitch).getHarmonic(harmonic)
        harmonic_chord.add (note.Note(new_pitch.midi))
        stream_out.append (note.Note(new_pitch))

    return harmonic_chord


def create_harmonic():

    t = TwelveTET()
    ph = PitchRegister()

    time = MusicTime(8,4,4)
    unit = MusicUnit(time,
                   t.name_to_midi( ['E4', 'D4', 'B3', 'Bb3', 'Eb4', 'Db4', 'C4', 'G3', 'A3']))

    for bass_pitch in unit.pitch_nodes:
        random_harmonics = random.sample(range(4,21), random.randrange(3, 6))
        new_chord = harmonic_series(bass_pitch, random_harmonics)
        new_chord.transpose(interval.Interval(new_chord[0],
                                              note.Pitch(bass_pitch),
                            inPlace=True))

        new_chord.duration = note.Duration(random.choice([time.M21_QUARTER/2, time.M21_QUARTER/1]))

    unit.stream = harmonic_series(note.Pitch('A1').midi,[5,6,7,9,12,15])



"""
Creation
"""

def stream_create_random_from_list(length,
                        pitch_set: list[note.Pitch] = None,
                        duration_set: list[note.Duration] = None) -> stream.Stream:

    # Create a random stream from a list of pitches and durations
    stream_out = stream.Stream()
    for i in range(length):
        stream_out.append(
            note.Note(pitch= random.choice(pitch_set),
                      quarterLength=random.choice(duration_set)
                      )
        )

    return stream_out


def stream_is_counterpoint(stream1: stream.Stream, stream2: stream.Stream) -> bool:
    # Generate two counterpoint voices
    # Ensure the voices are of the same length
    if len(stream1) != len(stream2):
        raise ValueError("Voices must be of the same length")

    # Check for parallel perfect intervals
    for i in range(len(stream1) - 1):
        intv1 = interval.DiatonicInterval(stream1[i], stream1[i + 1])
        intv2 = interval.DiatonicInterval(stream2[i], stream2[i + 1])
        if intv1.perfectable and intv2.perfectable and intv1.direction == intv2.direction:
            return False

    # Check for hidden parallels
    for i in range(len(stream1) - 1):
        intv1 = interval.DiatonicInterval(stream1[i], stream1[i + 1])
        intv2 = interval.DiatonicInterval(stream2[i], stream2[i + 1])
        if intv1.perfectable and intv2.perfectable and intv1.direction == intv2.direction:
            return False

    # Check for crossing voices
    for i in range(len(stream1) - 1):
        if stream1[i].pitch < stream2[i].pitch and stream1[i + 1].pitch > stream2[i + 1].pitch:
            return False

    return True



def idea_tonerow():
    # Music 21 ToneRow
    chromaticrow = serial.TwelveToneRow(TwelveTET.PITCH_CLASS_NUMBERS)
    matrixobj = chromaticrow.matrix()

    unit = MusicUnit()
    unit.pitch_nodes = chromaticrow.pitches
    unit.nodes_to_intervals()

    unit.transform (unit.PRIME, 0)


def tonerow_create(tonerow_base: serial.ToneRow = serial.ToneRow(row=[0, 4, 7, 4]),
                   octave : int = 4
                   ) -> stream.Stream:
    stream_out = stream.Stream()
    # Tonerow
    for pcs in enumerate(tonerow_base):
        pcs.octave = octave
        stream_out.append(pcs)

    return stream_out




def main():
    # Main: create or load, analyze or transform

    #comp = load_and_analyze('Sousta.mid')
    #comp.score_show()

    #create_rhythm()
    #create_new()

    #create_harmonic()

    percussion_load()
    #create_percussion()
    #create_balfolk()
    #create_counterpoint()

#    create_Population()
#    create_key_library(key.Key('C', 'major'))


if __name__ == '__main__':
    main()