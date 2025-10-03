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
# tools
from library import *
# Harmony rules
from harmony import *


"""
Composition - Structure
"""

# Genetic creation
from genetic import (Genome, selection_pair, single_point_crossover, mutation,
                     generate_population, sort_population)
# Bianry representation of note in genetic creation
BITS_PER_NOTE = 4



def create_markov ():
    # Markov chain of transitions

    # Example training tokens: list of (pitch_name_or_rest, dur)
    train = [('C4', 1), ('E4', 1), ('G4', 1), ('C5', 1), ('E4', 1), ('G4', 1), ('rest', 1)]

    # build transition dict for pitches
    trans = defaultdict(list)
    for a, b in zip(train, train[1:]):
        trans[a[0]].append(b[0])

    def sample_markov(start, length=16):
        out = [start]
        cur = start
        for _ in range(length - 1):
            choices = trans.get(cur) or list(trans.keys())
            cur = random.choice(choices)
            out.append(cur)
        return out

    gen_pitches = sample_markov('C4', length=16)
    # fixed duration 1 quarter for simplicity
    part = stream.Part()
    for p in gen_pitches:
        if p == 'rest':
            part.append(note.Rest(quarterLength=1))
        else:
            part.append(note.Note(p, quarterLength=1))


def genome_to_stream (genome: Genome,
                     num_bars: int,
                     num_notes_per_measure: int,
                     include_rests: bool,
                     scale_in: scale.ConcreteScale) -> stream.Stream:
    # Transform a generated genomen into a Stream
    stream_out = stream.Stream()

    pitch_degrees = []
    durations = []

    pitch_degrees_binary = []
    for i in range(num_bars * num_notes_per_measure):
        pitch_degrees_binary += [genome[i * BITS_PER_NOTE:i * BITS_PER_NOTE + BITS_PER_NOTE]]

    note_length = 4 / float(num_notes_per_measure)

    scl = scale_in.pitches

    for pitch_binary in pitch_degrees_binary:
        pitch_degree = int(sum([bit * pow(2, i) for i, bit in enumerate(pitch_binary)]))

        max_degree = pow(2, BITS_PER_NOTE - 1)
        # Degrees not in scale are rest
        if not include_rests:
            pitch_degree = int(pitch_degree % max_degree)

        if pitch_degree >= max_degree:
            pitch_degrees += [0]
            durations += [note_length]
        else:
            pitch_degrees += [pitch_degree]
            durations += [note_length]

    for i, degree in enumerate(pitch_degrees):
        if degree > 0:
            new_note = note.Note(pitch=scl[degree], quarterLength=durations[i])
            stream_out.append(new_note)
        else:
            stream_out.append(note.Rest(length=durations[i]))

    return stream_out


def stream_rate_rules(genome: Genome) -> int:
    # Rating of generation
    rating = genome[1]

    return rating


def create_genetic():
    # Number of measures    Length of the generated stream in measures
    num_measures = 4
    # Notes per bar	        Number of notes in a measure
    num_notes_per_measure = 4
    # Include rests	    Introduce rests between notes OR a constant stream of notes?
    include_rests: bool = True

    main_key = key.Key('C', 'major')
    main_scale = scale.MajorScale('C')
    title = 'Genetic '+str(int(datetime.now().timestamp()))
    main_score = score_create(title,
                              main_key,
                              meter.TimeSignature('4/4'),
                              120)

    # Population Size   Number of streams per generation to rate and recombine
    population_size: int = 10
    genome_size = num_measures * num_notes_per_measure * BITS_PER_NOTE

    # Generate populations
    population = generate_population(population_size, genome_size)

    # Continue with the fittest populations
    population = sort_population (population, fitness_func=stream_rate_rules)

    # Three fittest as next population
    next_generation = population[0:2]

    parents = selection_pair(population, stream_rate_rules)
    offspring_a, offspring_b = single_point_crossover(parents[0], parents[1])

    #   Number of mutations	    Max number of mutations that should be possible per child generated
    num_mutations: int = 2
    #   Mutation probability
    mutation_probability: float = 0.5

    offspring_a = mutation(offspring_a, num=num_mutations, probability=mutation_probability)
    offspring_b = mutation(offspring_b, num=num_mutations, probability=mutation_probability)
    next_generation += [offspring_a, offspring_b]

    new_stream = genome_to_stream (population[0],
                                  num_measures,
                                  num_notes_per_measure,
                                  include_rests,
                                  main_scale)

    main_score.append(part_create_from_stream(new_stream, instrument.Piano()))

    # Analyze score
    score_analyze (main_score)
    score_show(main_score)
    # Save score
    main_score.write(fmt='midi', fp=Config.DEFAULT_PATH + title +".mid")


def euclidian_rhythm (num_onset: int = 4, num_timestep: int = 4 ) -> list [int] :
    # Divide number of onsets evenly over number of timesteps, reduced if duplicate

    # Onsets gets an equal timestep interval
    base_timestep_interval = num_timestep // num_onset
    # And the remaining timesteps are a separate time step interval
    remaining_timesteps = num_timestep % num_onset

    rhythm = []
    for i in range(num_onset):
        rhythm_timestep_interval = base_timestep_interval
        if i < remaining_timesteps:
            rhythm_timestep_interval += 1
        rhythm.append (rhythm_timestep_interval)

    # Reduce
    while rhythm[0] != rhythm[-1]:
        for group in rhythm:
            if group != rhythm[-1]:
                    group += rhythm.pop(-1)

    last_interval = num_timestep - sum(rhythm)
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
    # Timestep is the rhythm relative unit, represented as integer
    # Harmonic rhythm: sequential pattern of onsets at timesteps
    # A rhythm sequence is defined by
    #  - a sequence of timestep in tervals between onsets
    #
    # The number of timesteps is the sum of the intervals

    rhythm_seq = euclidian_rhythm (3, 8)

    # [2,1,1.1]
    # [2,2,1,1,2]
    # [4, 3, 3, 3, 4]
    # [6, 4, 1, 5, 6]

    num_timesteps = sum(rhythm_seq)

    # Linking rhythm timesteps to meter beats
    timesteps_per_beat = 2

    # Meter: measure cycle of beats
    beat_note = 4  # eigth

    num_beats_in_measure = 4
    main_timesignature = meter.TimeSignature(str(num_beats_in_measure)+'/'+str(beat_note))

    main_beatcount =  main_timesignature.beatCount

    beat_duration = MCTime.QUARTER/beat_note
    beat_duration = main_timesignature.beatDuration.quarterLength


    main_score = score_create('Rhythm',DiatonicLayer.DEFAULT_KEY,main_timesignature)

    rhythm_stream = stream.Stream()
    # Apply rhythm in note stream without rests
    for timestep_interval in rhythm_seq:
        rhythm_note = note.Note(pitch=note.Pitch ('C5'),
                                duration=note.Duration(timestep_interval * beat_duration / timesteps_per_beat))
        rhythm_stream.append(rhythm_note)

    rhythm_part = part_create_from_stream(rhythm_stream)

    main_score.append(rhythm_part)
    score_show(main_score)

    return rhythm_stream


def percussion_load ():
    # Load
    main_score = load_and_analyze('midipercussion.mid')
    main_score = load_and_analyze('midipercussionmidi.mid')
    main_score.append(clef.PercussionClef())
    score_show(main_score)

def create_percussion ():

    # Create
    main_score = score_create('Percussion', DiatonicLayer.DEFAULT_KEY, MCTime.DEFAULT_TIMESIGNATURE, 100)

    # percussion_score =
    for part in create_percussion_parts().parts:
        main_score.append(part)

    score_show(main_score)


    # Write to MIDI
    mf = midi.translate.streamToMidiFile(main_score)
    mf.open(Config.DEFAULT_PATH+'percussion_example.mid', 'wb')
    mf.write()
    mf.close()



def create_percussion_parts () -> stream.Score:

    score_out = stream.Score()


    pchord = percussion.PercussionChord()



    # Helper to create an unpitched percussion note by MIDI pitch number
    # General MIDI percussion mapping (channel 10): 35-81 common drums


    def perc_note(midi_pitch, dur=0.5, velocity=100):
#        n = note.Unpitched()
        n = note.Note(pitch=midi_pitch, duration=dur)
        # set volume (velocity) for MIDI export
        n.volume.velocity = velocity
        return n

    # Meter 4/4, 8 timesteps, 0,5 beat per timestep
    num_timestep = 8
    timesteps_per_beat = 2
    # Three onset lines
    # BD on beats1 & (quarter = 1, 3), snare on 2 & 4,
    bass_pitches = [MCMIDI.BASS_DRUM, MCMIDI.ACOUSTIC_SNARE, MCMIDI.BASS_DRUM, MCMIDI.ACOUSTIC_SNARE]
    bass_rhythm = [2, 2, 2, 2]
    bass_durations = [1, 1, 1, 1]
    bass_volumes = [110, 110, 110, 110, 110, 110, 110, 110]
    # hh on every eighth
    hihat_pitches = [MCMIDI.CLOSED_HIHAT,MCMIDI.CLOSED_HIHAT,MCMIDI.CLOSED_HIHAT,MCMIDI.CLOSED_HIHAT,MCMIDI.CLOSED_HIHAT,MCMIDI.CLOSED_HIHAT,MCMIDI.CLOSED_HIHAT,MCMIDI.CLOSED_HIHAT]
    hihat_rhythm = [1,1,1,1,1,1,1,1]
    hihat_durations = [1,1,1,1,1,1,1,1]
    hihat_volumes = [70, 70, 70, 70, 70, 70, 70, 70]

    # Set to percussion instrument (General MIDI channel 10)
    # music21 uses an unpitched instrument class; channel will be set by MIDI export
    bass_part = part_create_from_stream(stream_create(bass_pitches, bass_rhythm, bass_durations, hihat_volumes), instrument.Woodblock(),clef.PercussionClef() )
    hihat_part = part_create_from_stream(stream_create(hihat_pitches, hihat_rhythm, hihat_durations, bass_volumes), instrument.Woodblock(), clef.PercussionClef())

    return score_out


def project_big_yellow_taxi():
    # Big Yellow Taxi
    main_key = key.Key('Bb', 'major')

    main_score = score_create('Big yellow taxi', main_key,meter.TimeSignature('4/4'))

    main_score.append(
        serial.ToneRow (
        ['B3', 'C#4', 'E4', 'E4', 'F#4', 'C#4', 'E4', 'E4', 'F#4', 'E4', 'G#3', 'B3', 'B3', 'C#4',
        'E4', 'F#4', 'B3', 'B3', 'F#4', 'F#4', 'F#4', 'G#4', 'F#4', 'E4', 'E4']
        )
    )
    # Analyze score
    score_analyze (main_score)

def project_berendans():
    # Berendans
    main_key = key.Key('Bb', 'major')
    main_score = score_create('Berendans',main_key,meter.TimeSignature('4/4'))

    progr = ['I', 'V', 'I']



def load_and_analyze (filename_in: str = Config.DEFAULT_MIDI_FILE_IN) -> stream.Score:
    # Load and analyze a score

    # Load a score
    main_score = converter.parse (Config.DEFAULT_PATH + filename_in)

    # Analyze score
    score_analyze (main_score)

    return main_score


def load_and_transform (filename_in: str = 'in.mid',
                        filename_out: str = 'out.mid'):
    # Load a score
    main_score = converter.parse (Config.DEFAULT_PATH + filename_in)


    # Add to score
    # Insert several new notes
    new_note_1 = note.Note(DiatonicLayer.DEFAULT_PITCH, quarterLength=0.75)
    new_note_2 = note.Note(DiatonicLayer.DEFAULT_PITCH, quarterLength=0.25)
    main_score.insertAndShift([2, new_note_1, 2.75, new_note_2])


    # Save score
    main_score.write(fmt='midi', fp=Config.DEFAULT_PATH + filename_out)


def create_new ():
    # Create new score template
    # Form
    num_voices = 3
    form = ('A', 'A', 'B', "A")
    form_num_measures = (8, 8, 8, 8)


    main_key = key.Key('C', 'major')
    main_scale = scale.MajorScale ('C')
    main_scale = scale.MelodicMinorScale ('C')

    main_score = score_create('New score', main_key,signature_in= meter.TimeSignature('4/4'))

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

        main_score.append(
            part_create_from_stream(stream_create(pitches_list1 [i], durations_list[i], onset_intervals_list [i], velocities_list [i]), instruments_list[i])
        )

    # Analyze score
    score_analyze (main_score)
    score_show(main_score)
    # Save score
    main_score.write(fmt='midi', fp=Config.DEFAULT_PATH + "new.mid")


def create_balfolk ():
    # Style : Balfolk
    # Parts:  melody and bass

    # C major/A minor
    main_key = key.Key('C', 'major')
    main_scale = scale.MajorScale ('C')

    # Bourrée-inspired melody (typical Balfolk rhythm)

    main_score = score_create('Balfolk',main_key,meter.TimeSignature('6/8'))
    melody_part = stream.Part()
    bass_part = stream.Part()
    main_score.append(melody_part)
    main_score.append(bass_part)

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
    score_analyze (main_score)
    score_show(main_score)
    # Save score
    main_score.write(fmt='midi', fp=Config.DEFAULT_PATH + "balfolk.mid")


    return


def create_counterpoint():

    main_key = key.Key('C', 'major')
    main_scale = scale.MajorScale ('C')

    # Counterpoint
    main_score = score_create('Counterpoint', main_key,meter.TimeSignature('4/4'))

    length = 16  # Length of the counterpoint
    voice1 = stream_create_random_from_list(length)
    voice2 = stream_create_random_from_list(length)

    # Keep generating until counterpoint reached
    while not stream_is_counterpoint(voice1, voice2):
        voice2 = stream_create_random_from_list(length)

    main_score.append(voice1)
    main_score.append(voice2)
    # Analyze score
    score_analyze (main_score)
    score_show(main_score)
    # Save score
    main_score.write(fmt='midi', fp=Config.DEFAULT_PATH + "counterpoint.mid")


def create_key_library (key_in: key.Key):
    # Create a score with library elements

    # Common chord progressions
    main_score = score_create('Chord progressions and triads in C', key_in,meter.TimeSignature('4/4'))

    stream_lib = create_stream_triads_in_key(key_in, 1)
    part_lib = part_create_from_stream(stream_lib)
    main_score.append(part_lib)

    stream_lib = create_stream_chords_in_key(ChordHarmony.PROGRESSIONS, key_in, 1)
    part_lib = part_create_from_stream(stream_lib)
    main_score.append(part_lib)

    score_analyze(main_score)
    score_show(main_score)
    # Save score
    main_score.write(fmt='midi', fp=Config.DEFAULT_PATH + 'chordlibrary_in_key_' + key_in.name +'.mid')


def create_stream_chords_in_key (chord_progressions: list, key_in: key.Key ,  quarterlength_in: int = 4 ) -> stream.Stream:
    # Stream of chord progression patterns in a key
    stream_out = stream.Stream()
    for i in range(1, len(chord_progressions)-1):
        stream_out.append(note.Rest(quarterLength= quarterlength_in))
        for j in range (0, len(chord_progressions[i])):
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

    main_score = score_create('Harmonic sequence and chords')

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

    main_score.append(part_create_from_stream(harmonic_stream))

    score_analyze(main_score)
    score_show(main_score)


def main():
    # Main: create or load, analyze or transform

    #main_score = load_and_analyze('Sousta.mid')
    #score_show(main_score)

    #create_rhythm()
    #create_new()

    #create_harmonic()

    create_percussion()
    #create_balfolk()
    #create_counterpoint()

#    create_genetic()
#    create_key_library(key.Key('C', 'major'))
#    tonerow()

"""
Creation
"""
def score_create ( title: str = 'New score',
                    key_in: key.Key = DiatonicLayer.DEFAULT_KEY ,
                   signature_in: meter.TimeSignature = MCTime.DEFAULT_TIMESIGNATURE ,
                   bpm_in: int = MCTime.DEFAULT_TEMPO)\
        -> stream.Score:
    # Create a stream to hold the musical elements
    score_out = stream.Score()
    score_out.metadata = metadata.Metadata()
    score_out.metadata.title = title
    score_out.metadata.composer = 'Musicom'

# Set the time signature, key signature and tempo
    score_out.insert(0, key_in)
    score_out.insert(0, signature_in)
    score_out.insert(0, tempo.MetronomeMark(number=bpm_in))

    return score_out


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


def score_analyze (score_in: stream.Score):
    # Analyze score

    #score_in.plot('3d')
    #score_in.plot('histogram','pitch')
    #score_in.show('abc')
    # Key
    key01 = score_in.analyze('key')
    print ('Imported :')
    print (score_in)
    print (' with key ' + str(key01))

    # Analyze parts ?
    #    for score_part in score_in.parts:
    #    show(score_part)

    chordset = score_in.chordify()
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
    score_in.append (chordset)

    score_in.makeMeasures(inPlace=True)
    post = analysis.metrical.labelBeatDepth(score_in)


def idea_tonerow():
    """
    Music21 ToneRow
    """

    # Music 21 TwelveToneRow
    chromaticRow = serial.TwelveToneRow(ChromaticLayer.PITCHCLASSES_INT)
    matrixObj = chromaticRow.matrix()

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
