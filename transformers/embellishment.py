""" Module for transforming musical streams with various note transformations. """
import random
from copy import deepcopy
from structures.factory import Transformer
from music21 import stream, note, scale



class EmbellishmentTransformer(Transformer):
    # Class for transforming musical streams with various note transformations.
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
        stream_out.append(deepcopy(note_in))
        return stream_out

    # original duration is kept, and divided in three parts
    possible_durations = [
        # [ 1.0/3, 1.0/3, 1.0/3],
            [0.5, 0.25, 0.25],
            [0.25, 0.5, 0.25],
            [0.25, 0.25, 0.5]
    ]
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
        stream_out.append(deepcopy(note1))
        return stream_out

    if note2 is None:
        stream_out.insert(0, deepcopy(note1))
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
        stream_out.append(deepcopy(note1))
        return stream_out

    if note2 is None:
        stream_out.insert(0, deepcopy(note1))
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
