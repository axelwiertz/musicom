
from music21 import stream, note, key, scale, roman
import copy
import random

from rules.harmony import Scale7ChordHarmony
from structures import MusicalUnit, Diatonic

# Voices in a canon
VOICE1 = 0
VOICE2 = 1
VOICE3 = 2
VOICE4 = 3
VOICE5 = 4

# Transformation types
IDENTICAL = 0
ONE_TO_THREE = 1
TWO_TO_THREE = 2
TWO_TO_FOUR = 3
# Transformations of single/double note to series of new notes
ONE_TRANS_SET = [IDENTICAL, IDENTICAL, ONE_TO_THREE]
# list of transformations that transform a single note based on both current and next note
TWO_TRANS_SET = [IDENTICAL, IDENTICAL, TWO_TO_THREE, TWO_TO_FOUR]
# identity is listed more than once to increase the chance of it getting chosen


def pairwise(iterable):
    # takes a list and returns a new list containing the elements pairwise
    # with overlap

    #    s -> (s[0], s[1]), (s[1], s[2]), (s[2], s[3]), ..., (s[Last], None)
    return list(zip(iterable, iterable[1:])) + [(iterable[-1], None)]


def pitch_middle_in_scale(pitch_in1: note.Pitch, pitch_in2: note.Pitch, scale_in: scale.ConcreteScale ) -> note.Pitch:
    # return the middle of two pitches in a scale

    pitches = scale_in.getPitches (minPitch=pitch_in1, maxPitch=pitch_in2,
                                   direction=scale.Direction.ASCENDING)
    length = len(pitches)

#    if length == 0:
#        return None

#    if length == 1:
#        return pitches[0]

    if length % 2 == 0:
        odd_even = random.choice([0, 1]) # list with even length can go down or up
    else:
        odd_even = 1 # list with odd length

    return pitches[(length - odd_even) // 2]


def note_split_middle_neighbor (note_in: note.Note, scale_in: scale.ConcreteScale) -> stream.Stream:
    # randomly transforms one note
    stream_out = stream.Stream()

    if note_in.isRest:
        stream_out.append(copy.deepcopy(note_in))
        return stream_out

    # original duration is kept, and divided in three parts
    possible_durations = [
        # [ 1.0/3, 1.0/3, 1.0/3],
            [0.5, 0.25, 0.25],
            [0.25, 0.5, 0.25],
            [0.25, 0.25, 0.5]      ]
    chosen_dur = random.choice(possible_durations)

    # first note and last note equal the original note
    stream_out.append(
        note.Note(pitch= note_in.pitch,
                  quarterlength= chosen_dur[0] * note_in.quarterLength))
    # middle note is the neighbour note
    stream_out.append(
        note.Note(pitch= scale_in.nextPitch(pitchOrigin= note_in.pitch,
                            direction=random.choice([scale.Direction.ASCENDING, scale.Direction.DESCENDING])),
                    quarterlength= chosen_dur[1] * note_in.quarterLength))
    # last note is equal the original note
    stream_out.append(
        note.Note(pitch= note_in.pitch,
                  quarterlength= chosen_dur[2] * note_in.quarterLength))

    return stream_out


def note_split_passing_next (note1 : note.Note, note2 : note.Note, scale: scale.ConcreteScale) -> stream.Stream:
    # interpolates a passing note in between current and next note
    # generalization of
    stream_out = stream.Stream()

    if note1.isRest:
        stream_out.append(copy.deepcopy(note1))
        return stream_out

    if note2 is None:
        stream_out.insert(0, copy.deepcopy(note1))
        return stream_out

    # total duration doesn't change: duration of current note is
    # spread over a copy of the current note and an interpolated note
    possible_durations = [  # [ 1.0/3, 2.0/3],
            # [ 2.0/3, 1.0/3],
            [0.5, 0.5],
            [0.75, 0.25],
            # [ 0.25, 0.75  ]
                        ]

    chosen_dur = random.choice(possible_durations)

    # first note is equal to original first note
    stream_out.append(
        note.Note(pitch=note1.pitch,
                  quarterlength=chosen_dur[0] * note1.quarterLength))

    # second note is in between first and next note
    stream_out.append(
        note.Note(pitch= pitch_middle_in_scale (note1.pitch, note2.pitch, scale),
                  quarterlength= chosen_dur[1] * note1.quarterLength))


    return stream_out


def note_split_twopassing_next (note1 : note.Note, note2 : note.Note, scale: scale.ConcreteScale) -> stream.Stream:
    # creates notes oscillates a single scale degree above and below the next note,
    # and uses those notes in the current beat (kind of cambiata?)
    stream_out = stream.Stream()

    if note1.isRest:
        stream_out.append(copy.deepcopy(note1))
        return stream_out

    if note2 is None:
        stream_out.insert(0, copy.deepcopy(note1))
        return stream_out

    possible_durations = [
        [0.5, 0.25, 0.25],
        [0.25, 0.5, 0.25]
        ]
    chosen_dur = random.choice(possible_durations)

    chosen_directions = random.choice([[scale.Direction.ASCENDING, scale.Direction.DESCENDING],
                                      [scale.Direction.DESCENDING, scale.Direction.ASCENDING]
                                      ])
    stream_out.append(
        note.Note(pitch= note1.pitch,
                  quarterlength= chosen_dur[0] * note1.quarterLength))
    stream_out.append(
        note.Note(pitch= scale.nextPitch(
                            pitchOrigin= note2.pitch,
                            direction=chosen_directions[0]),
                    quarterlength= chosen_dur[1] * note2.quarterLength))
    stream_out.append(
        note.Note(pitch= scale.nextPitch(
                            pitchOrigin= note2.pitch,
                            direction=chosen_directions[1]),
                    quarterlength= chosen_dur[2] * note2.quarterLength))

    return stream_out


# OBSOLETE
transformation_set = [None, None, None, None, # high changce of no transformation
                     'note_split_middle_neighbor',
                     'note_split_passing_next',
                     'note_split_twopassing_next'
                     ]


def stream_transform_random(stream_in: stream.Stream,
                            scale_in: scale.ConcreteScale) -> stream.Stream:
    # transform Stream with random operations

    stream_out = stream.Stream()

    for i in range(len(stream_in)):

        method = random.choice(transformation_set)
        new_stream = stream.Stream()
        match method:
            case 'note_split_middle_neighbor':
                new_stream = note_split_middle_neighbor (stream_in[i], scale_in)
            case 'note_split_passing_next':
                new_stream = note_split_passing_next (stream_in[i], stream_in[i+1], scale_in)
            case 'note_split_twopassing_next':
                new_stream = note_split_twopassing_next (stream_in[i], stream_in[i+1], scale_in)
        stream_out.append (new_stream)

    return stream_out.flatten()





def create_stream_from_chords (stream_chords: stream.Stream,
                               number_of_voices : int = 3,
                               octave_in: int = 4,
                               quarterLength_in = 2) -> stream.Stream:
    # given chords, return a stream of voices,
    # starting in octave octave_in, and ascending
    # prepare some streams: one per voice
    # all bass notes of each chord form one voice
    # all 2nd notes of each chord form a second voice

    stream_out = stream.Stream()

    # create voice streams to hold chords
    for i in range(number_of_voices):
        stream_out.append(stream.Stream())

    for i, chord_in in enumerate(stream_chords):

        octave_correction = octave_in - chord_in.notes[0].octave
        for n in chord_in.notes:
            n.octave += octave_correction

        # split each chord into separate voices
        for j in range(number_of_voices):
            stream_out[j].append()
            stream_out.append(note.Note(chord_in.notes[j].pitch, quarterLength_in))

    return stream_out



def stream_transform_canon(stream_in: stream.Stream,
                           delay_ql : int = 4,
                           number_of_voices: int = 5):
    # and turn it into a canon. Add extra transpositions to some number_of_voices to create some diversity


    stream_out = stream.Stream()

    parts = [stream_out.new_part("piano") for _ in range(number_of_voices)]
    initial_rests = [i * delay_ql for i in range(number_of_voices)]

    # define extra transpositions for different voices (e.g. +12, -24, ...)
    voice_transpositions = {VOICE1: 0, VOICE2: 0, VOICE3: -12, VOICE4: -24, VOICE5: -12}

    stacking = 3
    canonized = number_of_voices * stacking
    for v in range(number_of_voices):
        interval = voice_transpositions[v]
        v = copy.deepcopy(stream_in.transpose(interval).flatten().notesAndRests)


def main():
    unit = MusicalUnit()
    # Create based on chord progression
    unit.scale = Diatonic.DEFAULT_SCALE
    main_key = key.Key('C')
    # chord_degrees = [1, 4, 6, 2, 5, 1]
    chord_degrees = Scale7ChordHarmony.PROGRESSIONS[0]

    main_chords = stream.Stream()
    for i in chord_degrees:
        main_chords.append(roman.RomanNumeral(i, main_key))

    main_stream = create_stream_from_chords(main_chords, 3, 4, 2)

    # if direction_in == scale.Direction.DESCENDING:
    #    pitches.reverse()


    new_stream = stream_transform_random(main_stream, unit.scale)

    canon_stream = stream_transform_canon(main_stream)


if __name__ == '__main__':
    main()
