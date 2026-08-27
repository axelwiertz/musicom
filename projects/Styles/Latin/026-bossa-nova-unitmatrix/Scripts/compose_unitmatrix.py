#!/usr/bin/env python3
"""UnitMatrix-first composer template.

Use for daily and on-demand composer tasks.
Rules:
- Build UnitMatrix first.
- Rows = voices/pattern layers.
- Columns = form sections.
- Cells = PitchPattern + RhythmPattern data.
- Percussion must be written as low-level MIDI on channel 9.
- Verify exported MIDI before rendering audio.
- Render audio from the exact same MIDI path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple
import json
import subprocess

from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

TPB = 480
BAR = TPB * 4
DRUM_CH = 9

@dataclass
class UnitCell:
    pitch_pattern: List[int] = field(default_factory=list)
    rhythm_pattern: List[float] = field(default_factory=list)
    percussion: Dict[str, List[float]] = field(default_factory=dict)

@dataclass
class UnitMatrix:
    rows: List[str]
    cols: List[str]
    cells: Dict[str, Dict[str, UnitCell]]


def add_note(events, channel, note, start, dur, vel):
    events.append((start, Message('note_on', channel=channel, note=note, velocity=vel, time=0)))
    events.append((start + dur, Message('note_off', channel=channel, note=note, velocity=0, time=0)))


def build_track(events):
    track = MidiTrack()
    prev = 0
    for tick, msg in sorted(events, key=lambda item: (item[0], 0 if item[1].type in {'program_change', 'control_change'} else 1)):
        msg.time = tick - prev
        track.append(msg)
        prev = tick
    track.append(MetaMessage('end_of_track', time=0))
    return track


def verify_midi(path: Path) -> dict:
    mid = MidiFile(path)
    percussion = 0
    channels = set()
    for track in mid.tracks:
        for msg in track:
            if not msg.is_meta and hasattr(msg, 'channel'):
                channels.add(msg.channel)
                if msg.type == 'note_on' and msg.velocity > 0 and msg.channel == DRUM_CH:
                    percussion += 1
    if percussion == 0:
        raise RuntimeError('No percussion on channel 9')
    return {'channels': sorted(channels), 'percussion_note_on': percussion}


def render_with_fluidsynth(midi_path: Path, wav_path: Path, soundfont: Path) -> None:
    subprocess.run(['fluidsynth', '-ni', str(soundfont), str(midi_path), '-F', str(wav_path), '-r', '44100'], check=True)


def render_ogg(wav_path: Path, ogg_path: Path) -> None:
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', str(wav_path), '-af', 'volume=18dB', '-codec:a', 'libopus', '-b:a', '96k', str(ogg_path)], check=True)


def compose_unitmatrix_to_midi(matrix: UnitMatrix, midi_path: Path, bpm: int = 80) -> dict:
    mid = MidiFile(type=1, ticks_per_beat=TPB)
    meta = MidiTrack()
    meta.append(MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
    meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0))
    meta.append(MetaMessage('end_of_track', time=0))
    mid.tracks.append(meta)
    return {'status': 'template'}


if __name__ == '__main__':
    print('UnitMatrix composer template ready.')
