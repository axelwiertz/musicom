from music21 import stream
from musicpy import structures
from music21py import m21_to_mpy, mpy_to_m21
from structures import MusicVoice, MusicComposition
from .m21 import unit_to_stream, stream_to_unit

# Composition converters
def voices_to_parts (composition: MusicComposition) -> list[stream.Part]:
    # Convert voices to score parts
    parts = []
    for v in composition.voices:
        for u in v.units:
            parts.append(unit_to_stream(u))
    return parts

def parts_to_voices (score: stream.Score) -> list[MusicVoice]:
    # Convert score parts to voices
    voices = []
    for p in score.parts:
        voice = MusicVoice(name=p.partName, units=[stream_to_unit(p)])
        voices.append(voice)
    return voices

def comp_to_score (comp : MusicComposition) -> stream.Score:
    # Convert composition to music21 score
    score_out = stream.Score()
    for v in comp.voices:
        part = stream.Part()
        part.partName = v.name
        for u in v.units:
            part.append(unit_to_stream(u))
        score_out.append(part)
    return score_out

def score_to_piece (score : stream.Score) -> structures.piece:
    # convert music21 score to musicpy piece
    return m21_to_mpy(score)

def piece_to_score (piece : structures.piece) -> stream.Score:
    # convert musicpy piece to music21 score
    return mpy_to_m21(piece)

