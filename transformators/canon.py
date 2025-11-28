from music21 import stream
from copy import deepcopy

# Voices in a canon
VOICE1 = 0
VOICE2 = 1
VOICE3 = 2
VOICE4 = 3
VOICE5 = 4

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
        v = deepcopy(stream_in.transpose(interval).flatten().notesAndRests)

