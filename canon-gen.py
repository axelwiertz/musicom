from music21.scale import MinorScale, MajorScale

from library import *


import copy
import random



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
    # takes a list and returns a new list containing the elements pairwise
    # with overlap

    #    s -> (s[0], s[1]), (s[1], s[2]), (s[2], s[3]), ..., (s[Last], None)
    return list(zip(iterable, iterable[1:])) + [(iterable[-1], None)]


def pitch_middle_in_scale(minpitch: note.Pitch, maxpitch: note.Pitch, scale_in: scale.ConcreteScale ) -> note.Pitch:
    # return the middle of two pitches in a scale

    pitches = scale_in.getPitches(minpitch, maxpitch)
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


def realize_chord(chord_in : chord.Chord,
                  numofpitch : int = 3,
                  baseoctave : int = 4,
                  direction: scale.Direction = scale.Direction.ASCENDING) -> stream.Stream:
    # given a chord like Am7, return a stream of numofpitch pitches, starting in octave baseoctave, and ascending
    stream_out = stream.Stream()

    stream_out.append (chord_in.notes)

    pitches = chord_in.pitches
    num_iter = numofpitch // len(pitches) + 1
    octave_correction = baseoctave - pitches[0].octave
    actual_pitches = 0
    for i in range(num_iter):
        for p in pitches:
            if actual_pitches < numofpitch:
                newp = copy.deepcopy(p)
                newp.octave = newp.octave + octave_correction
                stream_out.append(newp)
                actual_pitches += 1
            else:
                if direction == scale.Direction.ASCENDING:
                    return stream_out
                else:
                    stream_out.reverse()
                    return stream_out
        octave_correction += 1

    # if direction == "descending", reverse the list of pitches before returning them

    if direction == scale.Direction.ASCENDING:
        return stream_out
    else:
        stream_out.reverse()
        return stream_out


def note_split_middle_neighbor (note: note.Note, scale: scale.ConcreteScale) -> stream.Stream:
    # randomly transforms one note
    stream_out = stream.Stream()

    if note.isRest:
        stream_out.append(copy.deepcopy(note))
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
        note.Note(pitch= note.pitch,
                  quarterlength= chosen_dur[0] * note.quarterLength))
    # middle note is the neighbour note
    stream_out.append(
        note.Note(pitch= scale.nextPitch(pitch= note.pitch,
                            direction=random.choice([scale.Direction.ASCENDING, scale.Direction.DESCENDING])),
                    quarterlength= chosen_dur[1] * note.quarterLength))
    # last note is equal the original note
    stream_out.append(
        note.Note(pitch= note.pitch,
                  quarterlength= chosen_dur[2] * note.quarterLength))

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
                            pitch= note2.pitch,
                            direction=chosen_directions[0]),
                    quarterlength= chosen_dur[1] * note2.quarterLength))
    stream_out.append(
        note.Note(pitch= scale.nextPitch(
                            pitch= note2.pitch,
                            direction=chosen_directions[1]),
                    quarterlength= chosen_dur[2] * note2.quarterLength))



    return stream_out


# OBSOLETE
transformation_set = [None, None, None, None, # high changce of no transformation
                     'note_split_middle_neighbor',
                     'note_split_passing_next',
                     'note_split_twopassing_next'
                     ]


def stream_transform_random(stream_in, scale) -> stream.Stream:
    # transform stream with random operations

    stream_out = stream.Stream()

    for i in range(len(stream_in)):

        method = random.choice(transformation_set)
        match method:
            case 'note_split_middle_neighbor':
                stream_out.appemd (note_split_middle_neighbor (stream_in[i], scale))
            case 'note_split_passing_next':
                stream_out.append (note_split_passing_next (stream_in[i], stream_in[i+1], scale))
            case 'note_split_twopassing_next':
                stream_out.append (note_split_twopassing_next (stream_in[i], stream_in[i+1], scale))

    return stream_out.flatten()


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



def create_canon ():

    scale01 = MinorScale()
    scale = MajorScale("C") # scale in which to interpret these chords
    main_key = key.Key ('C')

    chords = "C F Am Dm G C"
    main_chord_prog = [1, 4, 6, 2, 5, 1] # define a chord progression

    main_chords : list(int) = []
    for i in main_chord_prog:
        main_chords.append(roman.RomanNumeral(i, main_key))

    chord_progressions = lstChordPattern
    for i in range (len(chord_progressions[0])):
        chord01 = roman.RomanNumeral (chord_progressions[0][i], main_key)
        chord01.duration.quarterLength = quarterlength_in
        stream_in.append(chord01)

    voices = 5 # realize the chords using the given number of voices (e.g. 4)
    octave = 4 # realize the chords in octave 4 (e.g. 4)

    quarterLength_in = 2 # realize the chords using half notes (e.g. 1 for a whole note)

    # define extra transpositions for different voices (e.g. +12, -24, ...)
    # note that the currently implemented method only gives good results with multiples of 12
    voice_transpositions = {VOICE1: 0, VOICE2: 0, VOICE3: -12, VOICE4: -24, VOICE5: -12}

    # prepare some streams: one per voice
    # all bass notes of each chord form one voice
    # all 2nd notes of each chord form a second voice
    # ...
    # convert chords to notes and stuff into a stream
    main_stream = stream.Stream())

    # split each chord into a separate voice
    for c in main_chords:
        pitches = realize_chord (c, voices, octave, direction="descending")
        for v in range(voices):
            note = note.Note (pitches[v], quarterLength_in)
            main_stream.append(note)

    stream_out.append(stream_transform_random(stream_in, scale))

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
