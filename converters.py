"""
Musicom converters
Module for converting musical scores between different formats using Music21 and MusicPy.
"""
from typing import List
from config import Config
import platform
import copy

from constants import MIDIinstrument
from structures import MusicUnit, MusicSection, MusicVoice, MusicComposition, MusicTime

from musicpy import structures, musicpy as mp
from music21 import converter, stream, note, midi, serial, tempo

# Conversion between music21 and musicpy
from music21py import m21_to_mpy, mpy_to_m21
# Show score
from showscore import show
import pandas as pd
import os

# Helper functions
def sequence_rotations(sequence: list | tuple) -> list:
    # Generate all rotations of a given sequence
    rotations = [sequence[x:] + sequence[:x] for x in range(len(sequence))]
    return rotations

def interval_to_step(intervals: list[int]) -> list[int]:
    # Convert a list of n intervals to a sequential mask with n+1 sequential degree/onset numbers and zeroes
    # Example [2, 3] -> [1, 0, 2, 0, 0, 3]
    steps = []
    sequence_nr = 1
    for x in intervals:
        steps.append(sequence_nr)
        sequence_nr += 1
        for y in range(1, x):
            steps.append(0)
    return steps

def intervals_to_nodes(pitch_intervals: List[int], start_pitch_node: int = 0) -> List[int]:
    # Convert a list of pitch intervals to pitch nodes starting from start_pitch_node
    pitch_nodes = []
    current_pitch = start_pitch_node
    pitch_nodes.append(current_pitch)
    for pitch_interval in pitch_intervals:
        current_pitch += pitch_interval
        pitch_nodes.append(current_pitch)
    return pitch_nodes


# Music21 converters
def tonerow_to_stream (tonerow_base: serial.ToneRow = serial.ToneRow(row=[0, 4, 7, 4]),
                   octave : int = 4
                   ) -> stream.Stream:
    stream_out = stream.Stream()
    # Tonerow
    for pcs in enumerate(tonerow_base):
        pcs.octave = octave
        stream_out.append(pcs)

    return stream_out


# Composition converters: display and playback
def score_to_visual(score: stream.Score):
    """
    Show or play the score depending on the platform.
    1. On Windows, display text and musical notation.
    2. On iOS, display text (MIDI playback code is commented out).
    """
    if platform.system() == 'Windows':
        score.show('text')
        #    score.show('midi')  # Play MIDI
        # Showing score without external programs like Musescore
        show(score)  # Show musical notation

    elif platform.system() == 'IOS':
        score.show('text')

def score_to_sound(score: stream.Score):
    # Play or show the score depending on the platform.
    if platform.system() == 'Windows':
        score.show('text')
        #    score.show('midi')  # Play MIDI
        show(score)  # Show musical notation

    elif platform.system() == 'IOS':
        # Pyhonista may not support direct MIDI playback; try to import sound module if available
        try:
            import importlib
            sound = importlib.import_module('sound')
        except Exception:
            sound = None
        # Play the result (IOS) when sound module is available
        score.show('text')
        player = sound.MIDIPlayer('target.mid')
        player.play()
        player.stop()

# Print converters
def track_to_print(track: structures.track):
    print('Name     : ' + str(track.track_name))
    print('Notes    : ' + str(track.content.notes))
    print('Duration : ' + str(track.content.duration))
    print('Interval : ' + str(track.content.interval))

def section_to_part (section: MusicSection) -> stream.Part:
    part_out = stream.Part()
    for u in section.units:
        part_out.append(unit_to_stream(u))

def part_to_unit (part : stream.Part) -> MusicUnit:
    # Convert part to unit
    unit = stream_to_unit(part_to_stream(part))
    return unit

# Unit converters
def unit_to_sound (unit: MusicUnit, midi_instrument: int = MIDIinstrument.PIANO):
    mp.play (unit.chord, bpm=unit.time.bpm, instrument=midi_instrument, wait=True)

def unit_to_chord(unit: MusicUnit) -> structures.chord:
    return structures.chord(unit.pitch_nodes, unit.durations, unit.onset_intervals, unit.volumes)

def chord_to_unit(chord: structures.chord) -> MusicUnit:
    unit = MusicUnit()
    unit.pitch_nodes = chord.notes
    unit.durations = chord.get_duration()
    unit.onset_intervals = chord.interval
    unit.volumes = chord.get_volume()
    return unit

def unit_to_stream (unit: MusicUnit) -> stream.Stream:
    # Create a stream with notes and rests
    stream_out = stream.Stream()
    # Iterate over the list of pitches, intervals, durations and volumes
    for i in range(len(unit.pitch_nodes)):
        # Add notes and rests to the stream
        restduration = unit.onset_intervals[i] - unit.durations[i]
        if restduration > 0:
            stream_out.append(note.Rest(quarterLength=restduration))
        else:
            new_note = note.Note(pitch=unit.pitch_nodes[i], quarterLength=unit.durations[i])
            new_note.volume.velocity = unit.volumes[i]
            stream_out.append(new_note)
    return stream_out

def stream_to_unit (stream_in : stream.Stream) -> MusicUnit:
    # Convert m21 stream to unit
    # via chord
    chord = stream_to_chord(stream_in)
    unit = chord_to_unit(chord)
    # direct
    """
    for i in range(len(unit.pitch_nodes)):
        # Add notes and rests to the unit
        if isinstance(element, note.Note):
            unit.pitch_nodes += unit.stream[i].pitch.midi

        if isinstance(element, note.Rest):
            restduration = unit.onset_intervals[i] - unit.durations[i]
            unit.volumes[i] += unit.stream[i].volume.velocity

    unit.nodes_to_intervals()
    """
    # Transfer notes, rests and chords from the stream to the unit
    for element in stream_in:
        if isinstance(element, (note.Note, note.Rest)):
            if isinstance(element, note.Note):
                unit.pitch_nodes += [element.pitch.midi]
                unit.durations += [element.duration.quarterLength]
                unit.volumes += [element.volume.velocity if element.volume.velocity is not None else 100]
            elif isinstance(element, note.Rest):
                # Add rest as onset interval
                if len(unit.onset_intervals) == 0:
                    unit.onset_intervals += [element.duration.quarterLength]
                else:
                    unit.onset_intervals[-1] += element.duration.quarterLength
    return unit

def stream_to_chord (stream_in: stream.Stream) -> structures.chord:
    # convert music21 score to musicpy piece
    return m21_to_mpy(stream_in)

def chord_to_stream (chord: structures.chord) -> stream.Stream:
    # convert musicpy piece to music21 score
    return mpy_to_m21(chord)

# --- DataFrame / Excel helpers for MusicUnit ---
def unit_to_dataframe(unit: MusicUnit) -> pd.DataFrame:
    """Convert a MusicUnit into a pandas DataFrame.

    Columns: pitch_node, pitch_interval, onset_interval, duration, velocity, onset_cumulative
    Handles uneven field lengths by padding with None.
    """
    # lazy import fallback for environments without pandas available at module import
    try:
        import pandas as _pd
    except Exception:
        raise RuntimeError("pandas is required for unit_to_dataframe; please install it (pip install pandas)")

    fields = {
        'pitch_node': list(getattr(unit, 'pitch_nodes', []) or []),
        'pitch_interval': list(getattr(unit, 'pitch_intervals', []) or []),
        'onset_interval': list(getattr(unit, 'onset_intervals', []) or []),
        'duration': list(getattr(unit, 'durations', []) or []),
        'velocity': list(getattr(unit, 'volumes', []) or []),
    }

    n = max((len(v) for v in fields.values()), default=0)
    for k, v in fields.items():
        if len(v) < n:
            fields[k] = v + [None] * (n - len(v))

    df = _pd.DataFrame(fields)
    # cumulative onset (start times) - treat None as 0
    try:
        df['onset_cumulative'] = (_pd.to_numeric(df['onset_interval'], errors='coerce').fillna(0.0)).cumsum()
    except Exception:
        # best-effort: ignore if conversion fails
        pass

    return df


def unit_to_excel(unit: MusicUnit, filename: str | None = None, path: str = Config.DEFAULT_PATH, sheet_name: str | None = None, engine: str | None = 'openpyxl') -> str:
    """Save a MusicUnit to an Excel file and return the filepath.

    - `filename`: if None, a filename is auto-generated.
    - `path`: base directory to save into (defaults to Config.DEFAULT_PATH).
    - `sheet_name`: Excel sheet name (defaults to 'MusicUnit').
    - `engine`: pandas Excel writer engine (defaults to 'openpyxl').
    """
    df = unit_to_dataframe(unit)

    if filename is None:
        # safe filename
        filename = f"MusicUnit_{id(unit)}.xlsx"

    # ensure directory exists
    os.makedirs(path, exist_ok=True)
    filepath = os.path.join(path, filename)

    try:
        df.to_excel(filepath, sheet_name=sheet_name or 'MusicUnit', index=False, engine=engine)
    except TypeError:
        # engine param may not be accepted by older pandas versions
        df.to_excel(filepath, sheet_name=sheet_name or 'MusicUnit', index=False)

    return filepath

# Section cobverters

def to_stream(section: MusicSection) -> stream.Stream:
    """Concatenate the music21 streams from contained units into a single Stream."""
    s = stream.Stream()
    for u in section.units:
        if hasattr(u, 'stream') and u.stream is not None:
            # deep copy to avoid side effects when appending
            s.append(copy.deepcopy(u.stream))
    return s

def section_to_track(section: MusicSection) -> structures.track:
    """Build a musicpy track by concatenating unit chords if available."""
    t = structures.track([], track_name=section.name)
    for u in section.units:
        if hasattr(u, 'chord') and u.chord is not None:
            try:
                t = t + u.chord
            except Exception:
                # fall back to extend if addition is not supported
                try:
                    t.extend(u.chord)
                except Exception:
                    pass
    return t


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

def score_set_time(score : stream.Score, time : MusicTime):
    # Set the time signature, key signature and tempo
    score.insert(0, time.timesignature)
    score.insert(0, tempo.MetronomeMark(number=time.bpm))

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

def piece_play (piece : structures.piece):
    # Play piece and wait until finish, writes temp.midi
    mp.play(piece, wait=True)

def file_to_comp (comp: MusicComposition, filename_in: str = Config.DEFAULT_MIDI_FILE_IN):
    # Load a score
    comp.score = converter.parse (Config.DEFAULT_PATH + filename_in)
    comp.piece = mp.read(Config.DEFAULT_PATH + Config.DEFAULT_MIDI_FILE_IN, get_off_drums=True, split_channels=True)

def score_to_midifile (score: stream.Score , filename_out: str = Config.DEFAULT_MIDI_FILE_OUT):
    # Save score
    score.write(fmt='midi', fp=Config.DEFAULT_PATH + filename_out)

def percussionscore_to_midifile (score: stream.Score, filename_out: str = Config.DEFAULT_MIDI_FILE_OUT):
    # Set to percussion instrument (General MIDI channel 10)
    # Write to MIDI
    mf = midi.translate.streamToMidiFile(score)
    # music21 uses an unpitched instrument class; channel will be set by MIDI export
    mf.open(Config.DEFAULT_PATH+filename_out, 'wb')
    mf.write()
    mf.close()