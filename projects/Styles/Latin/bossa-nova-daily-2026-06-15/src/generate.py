#!/usr/bin/env python3
"""
Bossa Nova Daily Pattern Composition - 2026-06-15
Focus: Metrical gravity and syncopation in 2 bars.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple
from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo
import subprocess

TPB = 480
BAR = TPB * 4
DRUM_CH = 9

@dataclass
class UnitCell:
    pitch_pattern: List[int] = field(default_factory=list)
    rhythm_pattern: List[float] = field(default_factory=list) # fractional beats
    percussion: Dict[int, List[float]] = field(default_factory=dict) # midi_note -> [fractional beats]

@dataclass
class UnitMatrix:
    rows: List[str]
    cols: List[str]
    cells: Dict[str, Dict[str, UnitCell]]

def add_note(events, channel, note, start_tick, dur_tick, vel):
    events.append((start_tick, Message('note_on', channel=channel, note=note, velocity=vel, time=0)))
    events.append((start_tick + dur_tick, Message('note_off', channel=channel, note=note, velocity=0, time=0)))

def build_track(events):
    track = MidiTrack()
    prev = 0
    # Sort events by tick
    for tick, msg in sorted(events, key=lambda x: (x[0], 0 if x[1].type == 'note_off' else 1)):
        msg.time = int(tick - prev)
        track.append(msg)
        prev = tick
    track.append(MetaMessage('end_of_track', time=0))
    return track

def run():
    # Bossa Nova 2-bar pattern
    # Row 1: Bass (Surdo/Acoustic Bass)
    # Row 2: Harmony (Guitar Clave)
    # Row 3: Percussion
    
    rows = ["Bass", "Harmony", "Percussion"]
    cols = ["Main"]
    
    # Bass: Downbeat + syncopated pickup
    bass_pitches = [45, 45, 45, 45] # A
    bass_rhythms = [0.0, 1.5, 2.0, 3.5, 4.0, 5.5, 6.0, 7.5] # Beats
    
    # Harmony: Classic Bossa Clave
    clave_rhythm = [0.0, 0.75, 1.5, 2.5, 3.5, 4.5, 5.25, 6.5, 7.5]
    harmony_pitch = [52, 57, 60, 64] # Am chord
    
    # Percussion: Shaker (eighths) + Rimshot (syncopated)
    rimshot_note = 37
    shaker_note = 69
    
    perc_map = {
        shaker_note: [x * 0.5 for x in range(16)],
        rimshot_note: [0.0, 0.75, 1.5, 2.5, 3.5, 4.5, 5.25, 6.5, 7.5]
    }
    
    cell = UnitCell(
        pitch_pattern=bass_pitches,
        rhythm_pattern=bass_rhythms,
        percussion=perc_map
    )
    
    matrix = UnitMatrix(rows=rows, cols=cols, cells={"Bass": {"Main": cell}})
    
    mid = MidiFile(ticks_per_beat=TPB)
    
    # Setup track
    meta = MidiTrack()
    meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(84), time=0))
    mid.tracks.append(meta)
    
    # Instrument tracks
    bass_events = []
    harm_events = []
    perc_events = []
    
    # Bass
    for b in bass_rhythms:
        add_note(bass_events, 0, 33, int(b * TPB), int(0.5 * TPB), 80)
        
    # Harmony
    for b in clave_rhythm:
        for p in [57, 60, 64, 67]: # Am7
            add_note(harm_events, 1, p, int(b * TPB), int(0.25 * TPB), 70)
            
    # Percussion
    for note, beats in perc_map.items():
        for b in beats:
            add_note(perc_events, DRUM_CH, note, int(b * TPB), int(0.125 * TPB), 90 if b % 1.0 == 0 else 60)
            
    mid.tracks.append(build_track(bass_events))
    mid.tracks.append(build_track(harm_events))
    mid.tracks.append(build_track(perc_events))
    
    midi_path = Path("composition.mid")
    mid.save(midi_path)
    
    # Render
    wav_path = Path("composition.wav")
    sf = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
    subprocess.run(['fluidsynth', '-ni', sf, str(midi_path), '-F', str(wav_path), '-r', '44100'], check=True)
    subprocess.run(['ffmpeg', '-y', '-i', str(wav_path), '-codec:a', 'libvorbis', '-q:a', '5', 'composition.ogg'], check=True)

if __name__ == "__main__":
    run()
