"""
Music Composition Assistant
"""
import random
from datetime import datetime
from collections import defaultdict
#import sound

from constants import TwelveTET, MIDIpercussion, MIDIinstrument
from structures import MusicComposition, MusicUnit, MusicVoice
from converters import unit_to_chord

# Musical datastructures
from theory import MusicTime, MusicScale, Diatonic, PitchRegister
from harmony import Scale7ChordHarmony, Scale7PitchDegree, Scale7Triad

# Genetic algorithm
from generators.genetic import Genome, generate_population, run_evolution, print_stats, genome_to_string

# Showing score without external programs like Musescore

# Music21 modules: music notation and analysis
from music21 import stream, roman, percussion, note, chord, key, clef, harmony, serial, interval
# MusicPy modules: computational music structures and algorithms
# Conversion between music21 and musicpy



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
    comp.voices_to_parts()
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
    unit.onset_intervals = euclidian_rhythm (3, 8)
    unit.intervals_to_nodes()

    voice = MusicVoice('Rhythm voice', [unit], MIDIinstrument.PIANO)
    comp = MusicComposition('Rhythm',
                            MusicScale(Diatonic.HEPTA, Diatonic.SCALE, TwelveTET.C, Diatonic.major_mode),
                            [],
                            [0],
                            [voice]
                            )

    voice.units_to_part()
    comp.voices_to_parts()
    comp.score_show()


def percussion_load ():
    # Load
    comp = MusicComposition('Percussion')
    comp.load('r_son.mid')
    comp.score.parts[0].insert(0, clef.PercussionClef())
    comp.score_show()
    comp.piece.show()

    # To unit
    comp.parts_to_voices()
    comp.voices[0].part_to_unit()

    comp.load('midipercussionmidi.mid')


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
    comp.voices_to_parts()

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




def scale_library():

    comp = scale_library(MusicScale(Diatonic.HEPTA, Diatonic.SCALE, 60, Diatonic.mixolydian))
    # Save score
    comp.save('chordlibrary_in_key_' + TwelveTET.PITCH_CLASS_NAMES_SHARP(comp.scale.tonic) +'.mid')


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