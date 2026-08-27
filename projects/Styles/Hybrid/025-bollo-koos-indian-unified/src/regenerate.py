#!/usr/bin/env python3
"""
Regenerate 025-bollo-koos-indian-cross MIDI from patterns.
"""

import sys
import itertools
from pathlib import Path

# Add musicom to path
sys.path.insert(0, str(Path.home() / "musicom"))

from structures.pitchclass import MusicPitchClassSet, PatternType
from structures.unit import MusicUnit, MusicEvent
from structures.timegrid import MusicTimeGrid
from generators import RhythmGenerator

def mid_to_freq(midi_note):
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

def generate_midi():
    # 1. Scale: D minor
    scale = MusicPitchClassSet(
        name="D Minor",
        definition=PatternType.HEPTATONIC,
        rotation=5,  # Aeolian
        initial=2    # D
    )
    
    # 2. Pitch pattern (Koos contour)
    pitch_pattern = (2, 1, -2, 3, -1, 2, -3, 1)
    
    # 3. Rhythm pattern (16-step Bollywood clave)
    rhythm_unit = RhythmGenerator(onsets=6, timesteps=16).generate()[0]
    rhythm_onsets = rhythm_unit.onset_intervals
    
    # 4. Build melody
    pitch_cycle = itertools.cycle(pitch_pattern)
    current_pitch = 62  # D4
    melody_events = []
    tick = 0
    step = 480  # 1 beat
    
    for onset_interval in rhythm_onsets:
        interval = next(pitch_cycle)
        pitch = current_pitch + interval
        pitch = max(48, min(84, pitch))  # Clamp
        melody_events.append(MusicEvent(
            pitch=pitch, volume=90,
            start_tick=tick, end_tick=tick + step
        ))
        current_pitch = pitch
        tick += int(step * onset_interval / 2)
    
    melody = MusicUnit(events=melody_events)
    
    # 5. Build harmony (i-VII-VI-V)
    chords = [
        [62, 65, 69],  # Dm
        [60, 64, 67],  # C
        [58, 62, 65],  # Bb
        [57, 61, 64]   # A
    ]
    chord_events = []
    for bar in range(4):
        for beat in range(2):
            chord = chords[bar]
            for pitch in chord:
                chord_events.append(MusicEvent(
                    pitch=pitch, volume=70,
                    start_tick=bar * 2 * step + beat * step,
                    end_tick=bar * 2 * step + beat * step + step
                ))
    
    harmony = MusicUnit(events=chord_events)
    
    # 6. Build percussion (GM Channel 10)
    percussion_map = {
        0: 36,   # Kick
        3: 38,   # Snare
        6: 42,   # Closed Hat
        9: 38,   # Snare
        12: 36,  # Kick
        15: 46   # Open Hat
    }
    percussion_events = []
    for step_idx in range(16):
        if step_idx in percussion_map:
            percussion_events.append(MusicEvent(
                pitch=percussion_map[step_idx], volume=100,
                start_tick=step_idx * (step // 4),
                end_tick=(step_idx + 1) * (step // 4),
                channel=9  # GM Channel 10
            ))
    
    percussion = MusicUnit(events=percussion_events)
    
    # 7. Combine into project
    from musicom.structures import MusicProject, MusicSection, MusicVoice
    
    project = MusicProject(name="025-bollo-koos-indian-cross")
    section = MusicSection(name="Loop", tempo=120)
    
    section.add_voice(MusicVoice(name="Melody", units=[melody]))
    section.add_voice(MusicVoice(name="Harmony", units=[harmony]))
    section.add_voice(MusicVoice(name="Percussion", units=[percussion]))
    
    project.add_section(section)
    
    # 8. Export MIDI
    from musicom.converters.music21_score import unit_to_stream
    from music21 import midi
    
    stream_out = unit_to_stream(project)
    mf = midi.translate.streamToMidiFile(stream_out)
    midi_bytes = mf.writestr()
    
    output_path = Path("/opt/data/projects/Genres/Hybrid/025-bollo-koos-indian-cross/MIDI/bollo_koos_indian_v1.mid")
    output_path.write_bytes(midi_bytes)
    
    print(f"MIDI regenerated: {output_path}")

if __name__ == "__main__":
    generate_midi()