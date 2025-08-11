"""
Music Composition Assistant
"""
import copy
import random
import platform
from datetime import datetime


#import sound

# Musical data
from library import *
from music21 import stream, note
# Harmony rules
from harmony import *

# Showing score without external programs like Musescore
from showscore import show


"""
Composition - Structure
"""
# Main score
MAIN_PATH = 'C:\\temp\\Music\\'
DEFAULT_KEY = key.Key('C', 'major')
DEFAULT_SCALE = scale.MajorScale('C')

DEFAULT_TEMPO = 100
DEFAULT_TIMESIGNATURE = '4/4'

# Three voice score
MELODY_VOICE = 0
HARMONY_VOICE = 1
BASS_VOICE = 2

PART_A = 0
PART_B = 1
PART_C = 2
PART_D = 3

from genetic import generate_genome, Genome, selection_pair, single_point_crossover, mutation

BITS_PER_NOTE = 4


def int_from_bits(bits: list[int]) -> int:
    return int(sum([bit * pow(2, index) for index, bit in enumerate(bits)]))


def genome_to_melody(genome: Genome,
                     num_bars: int,
                     num_notes: int,
                     num_steps: int,
                     pauses: int,
                     scale_in: scale.ConcreteScale,
                     root_octave: int) -> stream.Stream:
    # Dict[str, list]:

    melody = {
        "notes": [],
        "volume": [],
        "duration": []
    }
    stream_out = stream.Stream()

    notes = []
    for i in range(num_bars * num_notes):
        notes = [genome[i * BITS_PER_NOTE:i * BITS_PER_NOTE + BITS_PER_NOTE]]

    note_length = 4 / float(num_notes)

    scl = scale_in.pitches

    for note_bits in notes:
        integer = int_from_bits(note_bits)

        if not pauses:
            integer = int(integer % pow(2, BITS_PER_NOTE - 1))

        if integer >= pow(2, BITS_PER_NOTE - 1):
            melody["notes"] += [0]
            melody["volume"] += [0]
            melody["duration"] += [note_length]
        else:
            if len(melody["notes"]) > 0 and melody["notes"][-1] == integer:
                melody["duration"][-1] += note_length
            else:
                melody["notes"] += [integer]
                melody["volume"] += [127]
                melody["duration"] += [note_length]

    steps = []
    for step in range(num_steps):
        steps.append([scl[(note01 + step * 2) % len(scl)] for note01 in melody["notes"]])

    melody["notes"] = steps

    for i, vol in enumerate(melody["volume"]):
        if vol > 0:
            for step in melody["notes"]:
                new_note = note.Note(pitch=step[i], duration=melody["duration"][i])
                stream_out.append(new_note)

    return stream_out


def stream_rate_rules(genome: Genome) -> int:
    rating = genome[1]

    return rating


def create_genetic():
    # Number of measures    Length of the generated stream in measures
    num_measures = 3
    # Notes per bar	        Number of notes in a measure
    num_notes_per_measure = 4
    # Number of steps	    Number of pitches per note
    num_steps_per_note = 1
    # Include rests	    Introduce rests between notes OR a constant stream of notes?
    include_rests: bool = True

    root_octave: int = 4

    main_key = key.Key('C', 'major')
    main_scale = scale.MajorScale('C')
    main_score = score_create('Genetic', main_key, '4/4', 120)

    #   Population Size	        Number of melodies per generation to rate and recombine
    population_size: int = 10
    #   Number of mutations	    Max number of mutations that should be possible per child generated
    num_mutations: int = 2
    #   Mutation probability	Probability for a mutation to occur
    mutation_probability: float = 0.5

    new_stream = stream.Stream

    title = str(int(datetime.now().timestamp()))

    population = []
    for _ in range(population_size):
        genome_size = num_measures * num_notes_per_measure * BITS_PER_NOTE
        population.append(generate_genome(genome_size))

    population_id = 0

    random.shuffle(population)
    population_fitness = []
    for i, genome in enumerate(population):
        population_fitness.append (stream_rate_rules(genome))

    sorted_population_fitness = sorted(population_fitness, key=lambda e: e[1], reverse=True)
    population = [e[0] for e in sorted_population_fitness]

    next_generation = population[0:2]


    def fitness_lookup(genome):
        for e in population_fitness:
            if e[0] == genome:
                return e[1]
        return 0


    parents = selection_pair(population, fitness_lookup)
    offspring_a, offspring_b = single_point_crossover(parents[0], parents[1])
    offspring_a = mutation(offspring_a, num=num_mutations, probability=mutation_probability)
    offspring_b = mutation(offspring_b, num=num_mutations, probability=mutation_probability)
    next_generation += [offspring_a, offspring_b]

    new_stream = genome_to_melody(population[0], num_measures, num_notes_per_measure, num_steps_per_note, include_rests, main_scale, root_octave)


def big_yellow_taxi():
    # Big Yellow Taxi
    main_key = key.Key('Bb', 'major')

    main_score = score_create('Big yellow taxi', main_key,'4/4')

    main_score.append(
        serial.ToneRow (
        ['B3', 'C#4', 'E4', 'E4', 'F#4', 'C#4', 'E4', 'E4', 'F#4', 'E4', 'G#3', 'B3', 'B3', 'C#4',
        'E4', 'F#4', 'B3', 'B3', 'F#4', 'F#4', 'F#4', 'G#4', 'F#4', 'E4', 'E4']
        )
    )
    # Analyze score
    score_analyze (main_score)

def berendans():
    # Berendans
    main_key = key.Key('Bb', 'major')

    main_score = score_create('Berendans',main_key,'4/4')

    progr = ['I', 'V', 'I']



def load_and_analyze ():
    # Load and analyze a score

    # Load a score
    main_score = converter.parse (MAIN_PATH + 'in.mid')

    # Analyze score
    score_analyze (main_score)


def load_and_transform ():
    # Load a score
    main_score = converter.parse (MAIN_PATH + 'in.mid')


    # Add to score
    # Insert several new notes
    new_note_1 = note.Note('C4', quarterLength=0.75)
    new_note_2 = note.Note('C4', quarterLength=0.25)
    main_score.insertAndShift([2, new_note_1, 2.75, new_note_2])


    # Transform pitch sequence in tomerow
    trw01 = serial.ToneRow()
    trw02 = tonerow_transform (trw01)


def create_new ():
    # Create new score template
    # Form
    parts = 3
    voices = []
    numvoices = 3
    form = (16, 16, 16)

    main_key = key.Key('C', 'major')
    main_scale = scale.MajorScale ('C')
    main_scale = scale.MelodicMinorScale ('C')

    main_score = score_create('New score', main_key,signature_in= '4/4')

    # Create three voices for melody and accompaniment
    # Motifs of voices
    pitches_list = [['C5', 'D5', 'E5', 'F5', 'G5', 'A5', 'B4', 'C5'],
                    ['C4', 'E4', 'G4', '', 'F4', 'A4', 'C5', ''],
                    ['C3', 'G3']]
    durations_list = [[1, 1, 1, 1, 1, 1, 1, 1],
                      [1, 1, 1, 1, 1, 1, 1, 1]]
    instruments_list = [instrument.Flute(),
                        instrument.Violin(),
                        instrument.Bass()]

    for i in range (0, len(pitches_list)-1):
        main_score.append(
            part_create(pitches_list [i], durations_list[i], instruments_list[i])
        )

    # Analyze score
    score_analyze (main_score)
    score_show(main_score)
    # Save score
    main_score.write(fmt='midi', fp=MAIN_PATH + "new.mid")


def create_balfolk ():
    # Style : Balfolk
    # Parts:  melody and bass

    # C major/A minor
    main_key = key.Key('C', 'major')
    main_scale = scale.MajorScale ('C')


    main_score = score_create('Balfolk',main_key,'6/8')
    melody_part = stream.Part()
    bass_part = stream.Part()
    main_score.append(melody_part)
    main_score.append(bass_part)

    # Bourrée-inspired melody (typical Balfolk rhythm)
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
    main_score.write(fmt='midi', fp=MAIN_PATH + "balfolk.mid")


    return


def create_percussion ():
    # Percussion

    main_key = key.Key('C', 'major')
    main_scale = scale.MajorScale ('C')


    main_score = score_create('Percussion',main_key,'4/4')
    signature : meter.TimeSignature
    signature = main_score.getElementsByClass('TimeSignature')[0]
    # number of beats per measure
    beats = signature.numerator
    # signature in quarterlength
    beatduration = signature.denominator * QUARTER

    # Percussion
    rhythm01 = [BT, RS, BT, BT, BT, BT, RS]

    pchord = percussion.PercussionChord()
    pitch_list01 = ['C4', '', 'C4', 'C4', 'C4', 'C4', '']
    durations01 = [1.0, 1.0, 1.5, 1.5, 1.0, 1.0, 1.0]

    rtm_example02 = [BT, BT, RS, BT, BT, RS]
    pitch_list02 = ['C4', 'C4', '', 'C4', 'C4', '']
    durations02 = [1.5, 0.5, 0.5, 0.25, 0.25, 1]

    rhythm_pattern = FOUR_RHYTHM

    pitches_list = [["C4", "D4", "E4", "F4"],
                    ["G4", "A4", "B4", "C5"]]


    # Generate durations
    # 1/32 note
    duration_unit = 0.125
    duration_factor = 8
    duration_new = duration_unit * duration_factor


def create_counterpoint():

    main_key = key.Key('C', 'major')
    main_scale = scale.MajorScale ('C')

    # Counterpoint
    main_score = score_create('Counterpoint', main_key,'4/4')

    length = 16  # Length of the counterpoint
    voice1 = stream_create_random(length)
    voice2 = stream_create_random(length)

    while not stream_is_counterpoint(voice1, voice2):
        voice2 = stream_create_random(length)

    main_score.append(voice1)
    main_score.append(voice2)
    # Analyze score
    score_analyze (main_score)
    score_show(main_score)
    # Save score
    main_score.write(fmt='midi', fp=MAIN_PATH + "counterpoint.mid")


def create_key_library (key_in: key.Key):
    # Create a score with library elements

    # Common chord progressions
    main_score = score_create('Chord progressions and triads in C', key_in,'4/4')

    stream_lib = create_stream_triads_in_key(key_in, 1)
    part_lib = part_create_from_stream(stream_lib)
    main_score.append(part_lib)

    stream_lib = create_stream_chords_in_key(lstChordPattern, key_in, 1)
    part_lib = part_create_from_stream(stream_lib)
    main_score.append(part_lib)

    score_analyze(main_score)
    score_show(main_score)
    # Save score
    main_score.write(fmt='midi', fp=MAIN_PATH + 'chordlibrary_in_key_' + key_in.name +'.mid')


def create_stream_chords_in_key (chord_progressions: list, key_in: key.Key ,  quarterlength_in: int = 1 ) -> stream.Stream:
    # Stream of chord progression patterns in a key
    stream_out = stream.Stream()
    for i in range(1, len(chord_progressions)-1):
        stream_out.append(note.Rest(quarterLength= quarterlength_in))
        for j in range (0, len(chord_progressions[i])):
            chord01 = roman.RomanNumeral (chord_progressions[i][j], keyOrScale=key_in)
            chord01.duration.quarterLength = quarterlength_in
            stream_out.append(chord01)

    return stream_out


def create_stream_triads_in_key (key_in: key.Key ,  quarterlength_in: int = 1 ) -> stream.Stream:
    # Stream of all triads in a key
    stream_out = stream.Stream()

    for i in range(HEPTA):
        triad = roman.RomanNumeral(i+1, key_in)
        triad.duration.quarterLength = quarterlength_in
        stream_out.append(triad)
        stream_out.append(note.Rest(quarterLength=quarterlength_in))

    return stream_out



def main():
    # Main: create or transform
    #create_new()
    #create_percussion()
    #create_balfolk()
    #create_counterpoint()

    create_genetic()
#    create_key_library(key.Key('C', 'major'))


"""
Creation
"""
def score_create ( title: str = 'New score',
                    key_in: key.Key = DEFAULT_KEY ,
                   signature_in: str = DEFAULT_TIMESIGNATURE ,
                   bpm_in: int = DEFAULT_TEMPO)\
        -> stream.Score:
    # Create a stream to hold the musical elements
    score_out = stream.Score()
    score_out.metadata = metadata.Metadata()
    score_out.metadata.title = title
    score_out.metadata.composer = 'Musicom'

# Set the time signature, key signature and tempo
    score_out.insert(0, key_in)
    score_out.insert(0, meter.TimeSignature(signature_in))
    score_out.insert(0, tempo.MetronomeMark(number=bpm_in))

    return score_out


def part_create(pitches : list[str],
                durations : list[float],
                instr: instrument.Instrument = instrument.Piano()
                ) -> stream.Part:
    # Create a part with notes and rests
    part_out = stream.Part()
    # Add instrument of part
    part_out.insert(0, instr)

    # Iterate over the list of pitches
    for i in range(len(pitches)) :
        # Add beats and rests to the stream
        if pitches[i] == '':
            part_out.append(note.Rest(quarterLength=durations[i]))
        else:
            part_out.append(note.Note(pitch=pitches[i], quarterLength=durations[i]))

    return part_out




def stream_create_random(length,
                        pitch_set: list = ('C4','D4','E4','F4','G4'),
                        duration_set: list = (0.5, 1, 2)) -> stream.Stream:
    # Create a random voice from a list of pitches and durations
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
        intv1 = interval.Interval(stream1[i], stream1[i + 1])
        intv2 = interval.Interval(stream2[i], stream2[i + 1])
        if is_perfect_interval(intv1) and is_perfect_interval(intv2) and intv1.direction == intv2.direction:
            return False

    # Check for hidden parallels
    for i in range(len(stream1) - 1):
        intv1 = interval.Interval(stream1[i], stream1[i + 1])
        intv2 = interval.Interval(stream2[i], stream2[i + 1])
        if is_perfect_interval(intv1) and is_perfect_interval(intv2) and intv1.direction == intv2.direction:
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
    # print (key01)

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

    score_in.append (chordset)



def score_show (score_in):
    """
    Show or play the stream
    """
    if platform.system() == 'Windows':
        score_in.show('text')
#    score.show('midi')  # Play MIDI
        show(score_in)  # Show musical notation

    elif platform.system() == 'IOS':
        score_in.show('text')

        # Play the result (IOS):
        #player = sound.MIDIPlayer('target.mid')
        #player.play()
        #player.stop()


"""
ToneRow
"""

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
