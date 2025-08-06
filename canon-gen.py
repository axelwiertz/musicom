from music21.scale import MinorScale, MajorScale

from library import *


import copy
import random

# Constants
SINGLE_NOTE = 0
DOUBLE_NOTE = 1
methods = [SINGLE_NOTE, DOUBLE_NOTE]

ASCENDING = 1
DESCENDING = -1

ODD_UPPER = True
ODD_LOWER = False

VOICE1 = 0
VOICE2 = 1
VOICE3 = 2
VOICE4 = 3
VOICE5 = 4

IDENTICAL = 0
ONE_TO_THREE = 1
TWO_TO_THREE = 2
TWO_TO_FOUR = 3
ONE_TRANS_SET = [IDENTICAL, IDENTICAL, ONE_TO_THREE]
TWO_TRANS_SET = [IDENTICAL, IDENTICAL, TWO_TO_THREE, TWO_TO_FOUR]
# list of transformations that transform a single note to a series of new notes
# identity is listed more than once to increase the chance of it getting chosen

# list of transformations that transform a single note based on both current and next note
# idenity is listed more than once to give it more chance of being chosen



def pairwise(iterable):
    """
    takes a list and returns a new list containing the elements pairwise
    with overlap

    s -> (s[0], s[1]), (s[1], s[2]), (s[2], s[3]), ..., (s[Last], None)
    """
    return list(zip(iterable, iterable[1:])) + [(iterable[-1], None)]


def median(lst, if_even_length_use_upper_element=False):
    """ return the median of a list """
    length = len(lst)

    if length == 0:
        return None

    if length == 1:
        return lst[0]

    if length % 2 != 0:
        # median of a list with odd lenght is well-defined
        return lst[(length - 1) // 2]
    else:
        # median of a list with even length is a bit tricky
        if not if_even_length_use_upper_element:
            return lst[(length - 1) // 2]
        else:
            return lst[(length) // 2]


def realize_chord(chordstring, numofpitch=3, baseoctave=4, direction=ASCENDING):
    """
    given a chordstring like Am7, return a list of numofpitch pitches, starting in octave baseoctave, and ascending
    if direction == "descending", reverse the list of pitches before returning them
    """
    pitches = harmony.ChordSymbol(chordstring).pitches
    num_iter = numofpitch // len(pitches) + 1
    octave_correction = baseoctave - pitches[0].octave
    result = []
    actual_pitches = 0
    for i in range(num_iter):
        for p in pitches:
            if actual_pitches < numofpitch:
                newp = copy.deepcopy(p)
                newp.octave = newp.octave + octave_correction
                result.append(newp)
                actual_pitches += 1
            else:
                if direction == ASCENDING:
                    return result
                else:
                    result.reverse()
                    return result
        octave_correction += 1

    if direction == ASCENDING:
        return result
    else:
        result.reverse()
        return result


def Identity(object) -> stream.Stream:
    new_stream = stream.Stream()
    new_stream.append(note)
    return new_stream


def OneToThree(note: note.Note, scale: scale.ConcreteScale) -> stream.Stream:
    # randomly transforms one note into three notes
    # total duration is kept
    # first note and last note equal the original note
    # middle note is the neighbour note
    stream_out = stream.Stream()

    if note.isRest:
        stream_out.append(copy.deepcopy(note))
        return stream_out

    possible_durations = [  # [ 1.0/3, 1.0/3, 1.0/3],
            [0.5, 0.25, 0.25],
            [0.25, 0.5, 0.25],
            [0.25, 0.25, 0.5]      ]
    chosen_dur = random.choice(possible_durations)


    stream_out.append(
        note.Note(pitch= note.pitch,
                  quarterlength= chosen_dur[0] * note.quarterLength))

    stream_out.append(
        note.Note(pitch= scale.nextPitch(
                            pitch= note.pitch,
                            direction=random.choice([scale.Direction.ASCENDING, scale.Direction.DESCENDING])),
                    quarterlength= chosen_dur[1] * note.quarterLength))

    stream_out.append(
        note.Note(pitch= note.pitch,
                  quarterlength= chosen_dur[2] * note.quarterLength))

    return stream_out


def TwoToThree(note1, note2, scale) -> stream.Stream:
    # interpolates a note in between current and next note
    # generalization of passing note
    # total duration doesn't change: duration of current note is
    # spread over a copy of the current note and an interpolated note
    stream_out = stream.Stream()

    new_note = copy.deepcopy(note1)

    if note2 is None:
        stream_out.insert(0, new_note)
        return stream_out

    if new_note.isRest:
        stream_out.append(new_note)
        return stream_out

    pitches = scale.getPitches(new_note.pitch, note2.pitch)
    rounding_strategy = random.choice([ODD_UPPER, ODD_LOWER])

    possible_durations = [  # [ 1.0/3, 2.0/3],
            # [ 2.0/3, 1.0/3],
            [0.5, 0.5],
            [0.75, 0.25],
            # [ 0.25, 0.75  ]
        ]

    chosen_dur = random.choice(possible_durations)

    new_note.quarterLength = chosen_dur[0] * note1.quarterLength
    stream_out.append(new_note)

    new_note2 = copy.deepcopy(new_note)
    new_note2.pitch = median(pitches, rounding_strategy)
    new_note2.quarterLength = chosen_dur[1] * note1.quarterLength
    stream_out.append(new_note2)

    return stream_out


def TwoToFour(note1, note2, scale) -> stream.Stream:
    """
    transformation that looks at next note,
    creates notes oscillates a single scale degree
    above and below the next note, and uses those
    notes in the current beat (kind of cambiata?)
    """
    stream_out = stream.Stream()

    new_note = copy.deepcopy(note1)

    if note2 is None:
        stream_out.insert(0, new_note)
        return stream_out

    if new_note.isRest:
        stream_out.append(new_note)
        return stream_out

    possible_durations = [
        [0.5, 0.25, 0.25],
        [0.25, 0.5, 0.25]
        ]
    chosen_dur = random.choice(possible_durations)

    possible_directions = [
            "ascending",
            "descending"
        ]
    chosen_direction = random.choice(possible_directions)
    other_direction = list(set(possible_directions) - set([chosen_direction]))[0]

    new_note.quarterLength = chosen_dur[0] * note1.quarterLength
    stream_out = stream.Stream()
    stream_out.append(new_note)

    new_note2 = copy.deepcopy(note2)
    new_note2.pitch = scale.next(note2.pitch, direction=chosen_direction)
    new_note2.quarterLength = chosen_dur[1] * note1.quarterLength
    stream_out.append(new_note2)

    new_note3 = copy.deepcopy(note2)
    new_note3.pitch = scale.next(note2.pitch, direction=other_direction)
    new_note3.quarterLength = chosen_dur[2] * note1.quarterLength
    stream_out.append(new_note3)

    return stream_out


# OBSOLETE
single_note_transformers = [Identity,
                            Identity,
                            OneToThree
                            ]
double_note_transformers = [Identity,
                            Identity,
                            TwoToThree,
                            TwoToFour,
                            ]


def spiceup_streams(streams, scale, repetitions=1):
    """
    function that takes a stream of parts
    and spices up every part using the
    Identity, OneToThree, TwoToThree, TwoToFour, ...
    transformations

    * it requires a scale in which to interpret the streams
    * it can create "repetitions" spiced sequences of the given stream
    """
    newtotalstream = stream.Stream()
    for i, part in enumerate(streams):
        newstream = stream.Stream()
        for x in range(repetitions):
            for note, nextnote in pairwise(part.notesAndRests):
                new_note = copy.deepcopy(note)
                new_nextnote = copy.deepcopy(nextnote)
                method = random.choice(methods)
                if method == SINGLE_NOTE:
                    trafo = random.choice(single_note_transformers)()
                    newstream.append(trafo.transform(scale, new_note).flatten().elements)
                elif method == DOUBLE_NOTE:
                    trafo = random.choice(double_note_transformers)()
                    newstream.append(trafo.transform(scale, new_note, new_nextnote).flatten().elements)
        newtotalstream.insert(0, newstream)
    return newtotalstream


def serialize_stream(stream, repeats=1) -> stream.Stream:
    # sequenced stream of parallel parts
    stream_out = stream.Stream()
    length = 0
    copies = len(stream)
    for i in range(copies):
        for part in reversed(stream):
            length += part.duration.quarterLength
            stream_out.append(copy.deepcopy(part.flatten().elements))

    return stream_out, length


    NOTE = type(note.Note())
    REST = type(note.Rest())
    for event in notesandrests:
        if type(event) == NOTE:
            #print(f"{event=}, {event.quarterLength=}, {event.pitch.midi=}")
            part.play_note(event.pitch.midi, 0.7, event.quarterLength)
        elif type(event) == REST:
            #print(f"{event=}")
            scamp.wait(event.quarterLength)


    range(voices)

    copy.deepcopy(stream01).transpose(interval01).flat.notesAndRests


from music21 import scale

def create_canon ():

    scale01 = MinorScale()
    scale = MajorScale("C") # scale in which to interpret these chords
    main_key = key.Key ('C')

    chords = "C F Am Dm G C"
    main_chord_prog = [1, 4, 6, 2, 5, 1] # define a chord progression

    main_chords : list(int) = []
    for i in main_chord_prog:
        main_chords.append(roman.RomanNumeral(i, main_key))


    voices = 5 # realize the chords using the given number of voices (e.g. 4)
    octave = 4 # realize the chords in octave 4 (e.g. 4)
    quarterLength = 2 # realize the chords using half notes (e.g. 1 for a whole note)
    spice_depth = 1 # number of times to spice-up the streams (e.g. 2)
    stacking = 1 # how many instances of the same chords to stack (e.g. 2)

    # define extra transpositions for different voices (e.g. +12, -24, ...)
    # note that the currently implemented method only gives good results with multiples of 12
    voice_transpositions = {VOICE1: 0, VOICE2: 0, VOICE3: -12, VOICE4: -24, VOICE5: -12}
    ############################################################################
    #
    # END OF USER EDITABLE CODE
    #
    ############################################################################

    # prepare some streams: one per voice
    # all bass notes of each chord form one voice
    # all 2nd notes of each chord form a second voice
    # ...
    # convert chords to notes and stuff into a stream
    streams = {}
    splitted_chords = chords.split(" ")
    for v in range(voices):
        streams[v] = stream.Stream()
    # split each chord into a separate voice
    for c in splitted_chords:
        pitches = realize_chord (c, voices, octave, direction="descending")
        for v in range(voices):
            note = note.Note (pitches[v], quarterLength)
            streams[v].append(note)

    # combine all voices to one big stream
    totalstream = stream.Stream()
    for r in range(stacking):
        for s in streams:
            totalstream.insert(0, copy.deepcopy(streams[s]))

    spiced_streams = [totalstream]
    spiced_streams.append(spiceup_streams(spiced_streams[s], scale))

    # unfold the final spiced up chord progression into a serialized stream
    stream_series, delay = serialize_stream(spiced_streams[-1])
    # ser.show('musicxml')

    # and turn it into a canon. Add extra transpositions to some voices to create some diversity
    parts = [s.new_part("piano") for _ in range(voices)]
    initial_rests = [i * delay for i in range(voices)]

    canonized = voices * stacking
    for v in range(voices):
        interval = voice_transpositions[v]
        v = copy.deepcopy(stream_series.transpose(interval).flatten().notesAndRests)


        # show the final product
    canonized.to_score(title="Canon", composer="canon-generator.py", max_divisor=16).show_xml()


def main():
    create_canon()

if __name__ == '__main__':
    main()
