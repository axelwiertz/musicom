"""
Music Composition Assistant
"""
import copy
import random
from datetime import datetime
from collections import defaultdict

#import sound

# Musical datastructures
from theory import *
# Harmony rules
from harmony import *
# Tools
from library import *
from genetic import *


# MusicPy modules: computational music structures and algorithms
from musicpy import musicpy as mp, algorithms, structures
from music21py import *

class Composition: 
    """
    Composition main structure
    """
    def __init__(self, title: str = 'New score',
                 key_in: key.Key = DiatonicLayer.DEFAULT_KEY,
                 meter_in: meter.TimeSignature = MCTime.DEFAULT_TIMESIGNATURE,
                 tempo_in: int = MCTime.DEFAULT_TEMPO):

        self.progression = None
        self.form = []
        self.bars = 0
        self.voices = 0
        self.style = 'Standard'
        self.key = None
        self.meter = None
        self.tempo = None

        # Music21 score
        self.score = stream.Score()

        self.score.metadata = metadata.Metadata()
        self.score.metadata.title = title
        self.score.metadata.composer = 'Musicom'

        # Set the time signature, key signature and tempo
        self.score.insert(0, key_in)
        self.score.insert(0, meter_in)
        self.score.insert(0, tempo.MetronomeMark(number=tempo_in))

        # MusicPy structures
        scalename = str(MCStyle.SCALE[self.style][0])
        scl01 = structures.scale(scalename)
        scl02 = structures.scale('C', 'major')
        self.piece = structures.piece

    def piece_track_notes (self, track_number: int = 0, nFrom: int = 0, nTo: int = 4):
        track_notes = self.piece(track_number)[nFrom:nTo]

        content = self.piece(track_number).tracks
        content_notes = self.piece(track_number).tracks.notes

    def score_show(self):
        score_show(self.score)

    def play_track (self, track_number: int = 0, instrument: int = MCMIDI.PIANO):
        mp.play(self.piece(track_number), instrument=instrument, wait=True)

    def play_piece (self):
        # convert music21 score to musicpy piece
        self.piece = m21_to_mpy(self.score)
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
        # Write to MIDI
        mf = midi.translate.streamToMidiFile(self.score)
        mf.open(Config.DEFAULT_PATH+'percussion_example.mid', 'wb')
        mf.write()
        mf.close()


    def print_piece (self):
        for i in range(0, len(self.piece)):
            print ('Track    : ' + str(i))
            print ('Notes    : ' + str(self.piece(i).tracks.notes))
            print ('Duration : ' + str(self.piece(i).tracks.duration))
            print ('Interval : ' + str(self.piece(i).tracks.interval))


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

        # Analyze parts ?
        #    for score_part in self.parts:
        #    show(score_part)

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
        post = analysis.metrical.labelBeatDepth(self.score)

        # MusicPy analysis

        str1 = algorithms.detect(self.piece)
        str2 = algorithms.chord_analysis(self.piece)
        str3 = mp.analyze_rhythm(self.piece)
        rhythmic_info = structures.rhythm.r.RhythmAnalyzer(self.piece)

        # Show the rhythmic information
        print(rhythmic_info.getRhythm())



class MusicalUnit ():
    # Stream with notes, chord, tempo, instrument
    def __init__(self,
                timesteps : int = 8,
                beat_note : int = 4,
                beats_in_measure : int = 4,
                pitches: list[int | str] = (),
                onset_intervals: list[float] = (),
                durations: list[float] = (),
                velocities: list[int] = (100),
                instrument: instrument.Instrument = instrument.Piano(),
                clef: clef.Clef = clef.TrebleClef(),
                scale: scale.ConcreteScale = DiatonicLayer.DEFAULT_SCALE,
                ):

        # Linking timesteps to meter beats
        self.timesteps = timesteps
        # Meter: measure cycle of beats
        beats_in_measure = beats_in_measure
        beat_note = beat_note

        self.timesignature = meter.TimeSignature(str(self.beats_in_measure) + '/' + str(self.beat_note))
        main_beatcount = self.timesignature.beatCount
        self.beat_duration = MCTime.QUARTER / self.beat_note
        beat_duration2 = self.timesignature.beatDuration.quarterLength

        self.pitches = pitches
        self.onset_intervals = onset_intervals
        self.durations = durations
        self.velocities = velocities

        self.scale = scale
        self.pitch_classes = scale.pitches
        self.instrument = instrument
        self.clef = clef


        pitch_bits = 8  # binary 128 pitches
        max_pitch = pow(2, self.pitch_bits - 1)

        duration_bits = 4  # binary 8 timesteps
        interval_bits = 4  # binary 8 timesteps
        velocity_bits = 4  # binary 8 levels
        bits = pitch_bits + duration_bits + interval_bits + velocity_bits

        # m21
        self.stream =  stream.Stream()
        # mp
        self.chord = structures.chord([])
        self.tempo = MCTime.DEFAULT_TEMPO
        self.instrument = instrument.Piano()

    def unit_to_chord(self):
        self.chord += structures.chord(self.pitches, self.durations, self.intervals)

    def unit_to_stream(self):
        self.stream = stream_create(self.pitches, self.onset_intervals, self.durations, self.velocities)

    def modulate (self, sclSource : structures.scale(),
             sclTarget : structures.scale()):
        # Modulate
        mpstream_out = self.chord.modulation(sclSource, sclTarget)

    def play (self):
        mp.play (self.track, bpm=self.tempo, instrument=self.instrument.midiProgram)

    def transform (self, method: int):
        # Transform a composition
        if method == 1:
            None

    def genome_to_unit(self, genome: Genome):
        # Transform a generated genome into a unit
        # Split genome in parts of 'bits' length
        numparts = len(genome) % self.bits
        genes_binary = []
        for i in range(numparts):
            # Extract binary elements
            genes_binary += [genome[(i * self.bits):(i * self.bits) + self.bits]]

        for gene_binary in genes_binary:
            pitch_nr = int(sum([bit * pow(2, i) for i, bit in enumerate(gene_binary)]))

    def stream_to_part (self) -> stream.Part:
        # Transfer notes, rests and chords from the original stream to a new Part
        part_out = stream.Part()
        # Add instrument of part
        part_out.insert(0, self.instrument)
        # Add clef of part
        part_out.insert(0, self.clef)

        # Create a part and add notes, rests and chords
        for element in self.stream:
            if isinstance(element, (note.Note, note.Rest, chord.Chord)):
                part_out.append(element)

        return part_out


def compose_unit ():
        # Create a musical unit
        unit1 = MusicalUnit()
        # Insert several new notes in m21 stream
        new_note_1 = note.Note(DiatonicLayer.DEFAULT_PITCH, quarterLength=MCTime.QUARTER/4)
        new_note_2 = note.Note(DiatonicLayer.DEFAULT_PITCH, quarterLength=MCTime.DEFAULT_DURATION)
        unit1.stream.insertAndShift([2, new_note_1, 2.75, new_note_2])



class MarkovChain:
    # Markov chain of transitions
    def __init__(self, train):
        # Example training tokens: list of (pitch_name_or_rest, dur)
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


def create_markov ():

    mc = MarkovChain([('C4', 1), ('E4', 1), ('G4', 1), ('C5', 1), ('E4', 1), ('G4', 1)])
    gen_pitches = mc.sample('C4', length=16)

    # fixed duration 1 quarter for simplicity
    part = stream.Part()
    for p in gen_pitches:
        part.append(note.Note(p, quarterLength=4/MCTime.QUARTER))


def create_population():
    # Create a genetic composition
    comp = Composition('Genetic '+str(int(datetime.now().timestamp())),
                       DiatonicLayer.DEFAULT_KEY,
                       MCTime.DEFAULT_TIMESIGNATURE,
                       120)

    def fitness_func(genome: Genome) -> int:
        return sum(genome)

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
    unit = MusicalUnit()
    unit.genome_to_unit (final_population[0])
    unit.instrument = instrument.Piano()
    unit.stream_to_part()
    comp.score.append(unit.part)

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

def create_rhythm () -> stream.Stream:
    # Timestep is the smallest rhythm relative unit, represented as integer
    # Harmonic rhythm: sequential pattern of onsets at timesteps
    # A rhythm sequence is defined by
    #  - a sequence of timestep intervals between onsets
    #
    # The number of timesteps is the sum of the intervals

    comp = Composition('Rhythm')
    unit = MusicalUnit(8, 4, 4)

    rhythm_seq = euclidian_rhythm (3, 8)
    num_timesteps = sum(rhythm_seq)

    # Apply rhythm in note stream
    for timestep_interval in rhythm_seq:
        rhythm_note = note.Note(pitch=DiatonicLayer.DEFAULT_PITCH,
                                duration=note.Duration(timestep_interval * unit.beat_duration / unit.timesteps_per_beat))
        unit.stream.append(rhythm_note)

    unit.stream_to_part()
    comp.score.append(unit.part)
    comp.score_show()


def percussion_load ():
    # Load
    comp = Composition('Percussion')
    comp.load('midipercussion.mid')
    comp.analysis()
    comp.load('midipercussionmidi.mid')

    comp.score.append(clef.PercussionClef())

    comp.score_show()

def create_percussion ():

    # Create
    comp = Composition('Percussion', DiatonicLayer.DEFAULT_KEY, MCTime.DEFAULT_TIMESIGNATURE, 100)

    pchord = percussion.PercussionChord()

    # Meter 4/4, 8 timesteps, 0,5 beat per timestep
    unit_bass = MusicalUnit(
        8, 4, 4,
        # Onset lines
        # bass drum on beats 1 & 3), snare on 2 & 4,
        [MCMIDI.BASS_DRUM, MCMIDI.ACOUSTIC_SNARE, MCMIDI.BASS_DRUM, MCMIDI.ACOUSTIC_SNARE],
        [2, 2, 2, 2],
        [1, 1, 1, 1],
        [110, 110, 110, 110, 110, 110, 110, 110],
        instrument.Woodblock(),
        clef.PercussionClef())
    unit_hihat = MusicalUnit(
        8, 4, 4,
        # hh on every eighth
        [MCMIDI.CLOSED_HIHAT, MCMIDI.CLOSED_HIHAT, MCMIDI.CLOSED_HIHAT, MCMIDI.CLOSED_HIHAT,
                         MCMIDI.CLOSED_HIHAT, MCMIDI.CLOSED_HIHAT, MCMIDI.CLOSED_HIHAT, MCMIDI.CLOSED_HIHAT],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [70, 70, 70, 70, 70, 70, 70, 70],
        instrument.Woodblock(),
        clef.PercussionClef())

    # Set to percussion instrument (General MIDI channel 10)
    # music21 uses an unpitched instrument class; channel will be set by MIDI export

    unit_bass.unit_to_stream()
    unit_bass.stream_to_part()
    comp.score.append(unit_bass.part)

    unit_hihat.unit_to_stream()
    unit_hihat.stream_to_part()
    comp.score.append(unit_hihat.part)

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
    main_key = key.Key('Bb', 'major')

    comp = Composition('Big yellow taxi', main_key,meter.TimeSignature('4/4'))

    comp.score.append(
        serial.ToneRow (
        ['B3', 'C#4', 'E4', 'E4', 'F#4', 'C#4', 'E4', 'E4', 'F#4', 'E4', 'G#3', 'B3', 'B3', 'C#4',
        'E4', 'F#4', 'B3', 'B3', 'F#4', 'F#4', 'F#4', 'G#4', 'F#4', 'E4', 'E4']
        )
    )
    # Analyze score
    comp.analysis()

def project_berendans():
    # Berendans
    main_key = key.Key('Bb', 'major')
    comp = Composition('Berendans',main_key,meter.TimeSignature('4/4'))

    comp.progression = ['I', 'V', 'I']





def create_new ():
    # Create new score template
    # Form
    num_voices = 3
    form = ('A', 'A', 'B', "A")
    form_num_measures = (8, 8, 8, 8)


    main_key = key.Key('C', 'major')
    main_scale = scale.MajorScale ('C')
    main_scale = scale.MelodicMinorScale ('C')

    comp = Composition('New score', main_key, meter.TimeSignature('4/4'))

    pitches_list = [main_scale.pitches[0:3],
                    ["G4", "A4", "B4", "C5"]]


    # Create three voices for melody and accompaniment
    # Motifs of voices
    pitches_list1 = [['C5', 'D5', 'E5', 'F5'],
                    ['C4', 'E4', 'G4'],
                    ['C3']]
    pitches_list12 = [['G5', 'A5', 'B4', 'C5'],
                    ['F4', 'A4', 'C5'],
                    ['G3']]
    # Onset intervals (harmonic rhythm)
    onset_intervals_list = [[1,1,1,1],
                  [1,1,2],
                  [2,2]]
    # Durations
    durations_list = [[1, 1, 1, 1],
                      [1, 1, 1],
                      [2,2]]

    # Velocities
    velocities_list = [[100, 100, 100,100],
                       [100, 100, 100],
                       [100, 100]]

    # Instruments
    instruments_list = [instrument.Flute(),
                        instrument.Violin(),
                        instrument.Bass()]

    for i in range (0, len(pitches_list1)-1):
        # Create unit
        unit = MusicalUnit(4,4,4,
            pitches_list1[i], durations_list[i], onset_intervals_list[i], velocities_list[i],
            instruments_list[i])
        unit.unit_to_stream()
        unit.stream_to_part()
        comp.score.append(unit)

    # Analyze score
    comp.analysis()
    comp.score_show()
    # Save score
    comp.save("new.mid")


def create_balfolk ():
    # Style : Balfolk
    # Parts:  melody and bass

    # C major/A minor
    main_key = key.Key('C', 'major')
    main_scale = scale.MajorScale ('C')

    # Bourrée-inspired melody (typical Balfolk rhythm)

    comp = Composition('Balfolk',main_key,meter.TimeSignature('6/8'))
    melody_part = stream.Part()
    bass_part = stream.Part()
    comp.score.append(melody_part)
    comp.score.append(bass_part)

    # Create notes with Balfolk-style rhythm
    chord_degrees = [1, 2, 3, 4]
    melody_notes = [
        ['C4', 'E4', 'G4'],
        ['D4', 'F4', 'A4'],
        ['E4', 'G4', 'B4'],
        ['F4', 'A4', 'C5']
    ]

    # Create melody with rhythmic variation
    for i in range(16):  # 4 measures
        # Choose a random melodic fragment
        fragment = random.choice(melody_notes)

        # Arpeggiate chords
        for note_name in fragment:
            n = note.Note(note_name)
            n.duration.type = 'eighth'
            melody_part.append(n)

    # Create accompaniment (drone/rhythmic support)
    bass_notes = ['C3', 'G3']
    for i in range(32):  # matching melody length
        bass_note = note.Note(random.choice(bass_notes))
        bass_note.duration.type = 'eighth'
        bass_part.append(bass_note)

    # Analyze score
    comp.analysis()
    comp.score_show()
    # Save score
    comp.save("balfolk.mid")


    return


def create_counterpoint():

    main_key = key.Key('C', 'major')
    main_scale = scale.MajorScale ('C')

    # Counterpoint
    comp = Composition('Counterpoint', main_key,meter.TimeSignature('4/4'))

    length = 16  # Length of the counterpoint
    voice1 = stream_create_random_from_list(length)
    voice2 = stream_create_random_from_list(length)

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


def create_key_library (key_in: key.Key):
    # Create a score with library elements

    # Common chord progressions
    comp = Composition('Chord progressions and triads in C', key_in,meter.TimeSignature('4/4'))

    stream_lib = create_stream_triads_in_key(key_in, 1)
    part_lib = unit.stream_to_part(stream_lib)
    comp.score.append(part_lib)

    stream_lib = create_stream_chords_in_key(ChordHarmony.PROGRESSIONS, key_in, 1)
    part_lib = unit.stream_to_part(stream_lib)
    comp.score.append(part_lib)

    comp.analysis()
    comp.score_show()
    # Save score
    comp.save('chordlibrary_in_key_' + key_in.name +'.mid')


def create_stream_chords_in_key (chord_progressions: list, key_in: key.Key ,  quarterlength_in: int = 4 ) -> stream.Stream:
    # m21 Stream of chord progression patterns in a key
    stream_out = stream.Stream()
    # mp
    mpscale = structures.scale(str(key_in.tonic.name), str(key_in.mode))
    chd01 = mpscale.chord_progression(chord_progressions[0])
    for i in range(1, len(chord_progressions)-1):
        # mp
        chd02 = mpscale.chord_progression(chord_progressions[i], durations=1 / 2, intervals=0, volumes=None,
                                        chords_interval=None)
        chd01 = chd01 + structures.rest(1 / 2) + chd02

        # m21 Add rest between progressions
        stream_out.append(note.Rest(quarterLength= quarterlength_in))
        for j in range (0, len(chord_progressions[i])):
            # m21 Create chord from Roman numeral
            chord01 = roman.RomanNumeral (chord_progressions[i][j], keyOrScale=key_in)
            chord01.duration.quarterLength = quarterlength_in
            stream_out.append(chord01)

    return stream_out


def create_stream_triads_in_key (key_in: key.Key ,  quarterlength_in: int = 4 ) -> stream.Stream:
    # Stream of all triads in a key
    stream_out = stream.Stream()

    for i in range(DiatonicLayer.HEPTA):
        triad = roman.RomanNumeral(i+1, key_in)
        triad.duration.quarterLength = quarterlength_in
        stream_out.append(triad)
        stream_out.append(note.Rest(quarterLength=quarterlength_in))

    # mp
    mpscale = structures.scale(str(key_in.tonic.name), str(key_in.mode))
    chords_in_scale = mpscale % (1234567, 0.5)
    mpstream_chords = chords_in_scale[0]
    for i in range(1, DiatonicLayer.HEPTA):
    #    print (PROGRESSIONS[i])
        mpstream_chords = mpstream_chords + structures.rest(1 / 2) + chords_in_scale[i]

    return stream_out


def chord_create_harmonic (fundamental_pitch  : note.Pitch = note.Pitch('C4'),
                           harmonic_numbers: list[int] = range(1,4)) -> chord.Chord:

    harmonic_chord = chord.Chord()
    for harmonic in harmonic_numbers:
        new_pitch = fundamental_pitch.getHarmonic(harmonic).midi
        harmonic_chord.add (note.Note(new_pitch))

    return harmonic_chord


def stream_create_harmonic (fundamental_pitch : note.Pitch = note.Pitch('A2'),
                            harmonic_numbers : list[int] = tuple(range(1,17))) -> stream.Stream:

    stream_out = stream.Stream()
    for harmonic in harmonic_numbers:
        new_pitch = fundamental_pitch.getHarmonic(harmonic).midi
        stream_out.append (note.Note(new_pitch))

    return stream_out


def create_harmonic():

    comp = Composition('Harmonic sequence and chords')

    harmonic_stream = stream.Stream()

    bass_pitches = ['E4', 'D4', 'B3', 'B-3', 'E-4', 'D-4', 'C4', 'G3', 'A3']
    bass_line = [note.Pitch(i) for i in bass_pitches]

    for bass_pitch in bass_line:
        random_harmonics = random.sample(range(4,21), random.randrange(3, 6))
        new_chord = chord_create_harmonic(bass_pitch, random_harmonics)

        transpose_by = interval.Interval(new_chord[0], bass_pitch)

        new_chord.transpose(transpose_by, inPlace=True)
        new_chord.duration = note.Duration(random.choice([MCTime.QUARTER/2, MCTime.QUARTER/1]))

        harmonic_stream.append(new_chord)

    #harmonic_stream = stream_create_harmonic()
    #harmonic_chord = chord_create_harmonic(note.Pitch('A1'),[5,6,7,9,12,15])
    #harmonic_stream.append(harmonic_chord)

    comp.score.append(unit.stream_to_part(harmonic_stream))

    comp.analysis()
    comp.score_show()


def main():
    # Main: create or load, analyze or transform

    #comp = load_and_analyze('Sousta.mid')
    #comp.score_show()

    #create_rhythm()
    #create_new()

    #create_harmonic()

    create_percussion()
    #create_balfolk()
    #create_counterpoint()

#    create_Population()
#    create_key_library(key.Key('C', 'major'))
#    tonerow()

"""
Creation
"""

def stream_create_random_from_list(length,
                        pitch_set: list[note.Pitch] = DiatonicLayer.DEFAULT_PITCHES,
                        duration_set: list[note.Duration] = MCTime.DEFAULT_DURATIONS) -> stream.Stream:

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
    """
    Music21 ToneRow
    """

    # Music 21 TwelveToneRow
    chromaticrow = serial.TwelveToneRow(ChromaticLayer.PITCHCLASSES_INT)
    matrixobj = chromaticrow.matrix()

    # Transform pitch sequence in tomerow
    trw01 = serial.ToneRow()
    trw02 = tonerow_transform (trw01)



def tonerow_create(tonerow_base: serial.ToneRow = serial.ToneRow(row=[0, 4, 7, 4]),
                   octave : int = 4
                   ) -> stream.Stream:
    stream_out = stream.Stream()
    # Tonerow
    for pcs in enumerate(tonerow_base):
        pcs.octave = octave
        stream_out.append(pcs)

    return stream_out


def tonerow_transform (tonerow_in: serial.ToneRow) -> serial.ToneRow:

    tonerow_out = copy.deepcopy(tonerow_in)

    # P I R RI
    transformations = ('P', 'I', 'R', 'RI')
    trans01 = random.choice (transformations)
    # Transform tone row
    tonerow_out = tonerow_in.zeroCenteredTransformation (trans01, 0)

    # Transpose the phrase up by a major third
    tonerow_out = tonerow_in.transpose("M3")
    #tonerow_out = tonerow_in.transpose(4)

    return tonerow_out


if __name__ == '__main__':
    main()


