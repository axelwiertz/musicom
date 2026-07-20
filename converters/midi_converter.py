# Copyright (c) 2026 Axel Wiertz / Musicom
#
# Licensed under the MIT License.

"""
converters/midi_converter.py — MIDI exporter for Musicom UnitMatrix.

Uses 'mido' for native multi-track, multi-channel MIDI file rendering.
This ensures precise start/end timings and supports multi-voice channel grouping.
"""

from __future__ import annotations
import os
import mido
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from structures import UnitMatrix


def export_midi(matrix: UnitMatrix, path: str) -> bool:
    """
    Exports a symmetric UnitMatrix directly to a standard Multitrack MIDI file.
    
    Ensures:
      - Correct pitch tracking
      - Strict note durations and start offsets
      - Separate MIDI track per voice row
    """
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)

    mid = mido.MidiFile(ticks_per_beat=960)

    # 1. Track 0: Tempo Meta Events
    meta_track = mido.MidiTrack()
    mid.tracks.append(meta_track)
    meta_track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(120), time=0))
    meta_track.append(mido.MetaMessage('end_of_track', time=0))

    # 2. Tracks 1..N: Musical Voices
    num_rows, num_cols = matrix.data.shape

    for r_idx in range(num_rows):
        track = mido.MidiTrack()
        mid.tracks.append(track)
        
        # Track initialization / name
        voice_label = f"Voice_{r_idx}"
        track.append(mido.MetaMessage('track_name', name=voice_label, time=0))

        # Compile and sort all NoteEvents chronologically in absolute tick space
        abs_events: list[tuple[int, str, int, int]] = [] # (tick, type_on_off, pitch, velocity)
        
        cumulative_offset = 0
        for c_idx in range(num_cols):
            unit = matrix.get_unit((r_idx, c_idx))
            if unit is not None:
                for event in unit.events:
                    # Capture absolute timeline ticks
                    on_tick = cumulative_offset + event.start_tick
                    off_tick = cumulative_offset + event.end_tick
                    
                    abs_events.append((on_tick, 'note_on', event.pitch, event.volume))
                    abs_events.append((off_tick, 'note_off', event.pitch, 0))
                
                # Advance timeline by cell length
                cumulative_offset += unit.len_ticks()

        # Sort chronological events. On tie, handle 'note_off' before 'note_on' to prevent overlap choke.
        abs_events.sort(key=lambda x: (x[0], 0 if x[1] == 'note_off' else 1))

        # Translate absolute ticks to MIDI Delta Ticks
        last_tick = 0
        for tick, ev_type, pitch, velocity in abs_events:
            delta = tick - last_tick
            track.append(mido.Message(ev_type, note=pitch, velocity=velocity, time=delta))
            last_tick = tick

        track.append(mido.MetaMessage('end_of_track', time=0))

    mid.save(path)
    return True


# Stub compatibility functions for music21 metrics (loaded inside converters/__init__.py)
def midifile_to_piece(filename_in: str):
    return None

def score_to_midifile(score, filename_out: str):
    import os
    from utilities import Config
    os.makedirs(Config.DEFAULT_PATH, exist_ok=True)
    score.write(fmt='midi', fp=Config.DEFAULT_PATH + filename_out)

def midifile_to_score(filename_in: str):
    from music21 import converter
    from utilities import Config
    return converter.parse(Config.DEFAULT_PATH + filename_in)

def percussion_stream_to_midifile(stream_in, filename_out: str):
    from music21 import midi
    from utilities import Config
    os.makedirs(Config.DEFAULT_PATH, exist_ok=True)
    mf = midi.translate.streamToMidiFile(stream_in)
    mf.open(Config.DEFAULT_PATH + filename_out, 'wb')
    mf.write()
    mf.close()
