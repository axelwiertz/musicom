#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo
from music21 import converter, midi, stream, instrument

# Project Root
ROOT = Path("/opt/data/projects/Genres/Blues/027-delta-blues-shack")
MIDI_PATH = ROOT / "MIDI" / "027_delta_blues.mid"
WAV_PATH = ROOT / "Renders" / "027_delta_blues.wav"
OGG_PATH = ROOT / "Audio" / "027_delta_blues.ogg"
XML_PATH = ROOT / "Scores" / "027_delta_blues.musicxml"
MANIFEST_PATH = ROOT / "Analysis" / "027_manifest.json"
SOUNDFONT = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")

TPB = 480
BPM = 72
TEMPO = bpm2tempo(BPM)
# Delta blues slow 12/8 swing feel - each beat in 12/8 is represented by 3 eighth-note triplet sub-pulses
# We can model this in 4/4 with eighth-note triplets, or write it directly where 1 bar = 4 main beats (480 * 4 = 1920 ticks)
BAR = TPB * 4

# 12-Bar Blues progression: I - I - I - I | IV - IV - I - I | V - IV - I - I
SECTION_ORDER = [
    {"name": "Intro", "kind": "intro", "bars": 2, "chords": ["A7", "E7"]},
    {"name": "Verse 1", "kind": "verse", "bars": 12, "chords": ["A7", "A7", "A7", "A7", "D7", "D7", "A7", "A7", "E7", "D7", "A7", "E7"]},
    {"name": "Verse 2", "kind": "verse", "bars": 12, "chords": ["A7", "A7", "A7", "A7", "D7", "D7", "A7", "A7", "E7", "D7", "A7", "E7"]},
    {"name": "Guitar Solo", "kind": "solo", "bars": 12, "chords": ["A7", "A7", "A7", "A7", "D7", "D7", "A7", "A7", "E7", "D7", "A7", "E7"]},
    {"name": "Verse 3", "kind": "verse", "bars": 12, "chords": ["A7", "A7", "A7", "A7", "D7", "D7", "A7", "A7", "E7", "D7", "A7", "E7"]},
    {"name": "Outro", "kind": "outro", "bars": 2, "chords": ["A7", "A7"]},
]

# Chords (A7, D7, E7) using standard registration spacing to keep Midground clean
CHORDS = {
    "A7": [45, 57, 61, 64, 67],   # A2, A3, C#4, E4, G4
    "D7": [50, 57, 60, 62, 66],   # D3, A3, C4, D4, F#4
    "E7": [40, 52, 56, 59, 62, 64], # E2, E3, G#3, B3, D4, E4
}

# Instruments / Tracks matching acoustic registers
ROWS = [
    {"name": "Resonator Guitar (Refined Melodic Lead)", "kind": "lead", "channel": 0, "program": 25}, # GM Steel Acoustic Guitar (25)
    {"name": "Acoustic Slide (Harmony Accompaniment)", "kind": "harmony", "channel": 1, "program": 26}, # Acoustic Jazz Guitar (26) or Steel Guitar (25)
    {"name": "Mono Fingerstyle Thumb Bass (Sub-Bass)", "kind": "bass", "channel": 2, "program": 32}, # Acoustic Bass
    {"name": "Stomp Box and Claps (Background Rhythm)", "kind": "drums", "channel": 9, "program": 0},
]

# Grid Onsets (Refined 12/8 triplet swing grid)
# main beat has three triplet subdivision onsets at 0.0, 0.33, 0.66
CELL_LIBRARY = {
    "lead": {
        "intro": [
            {"notes": [69, 72, 74], "beats": [0.0, 1.0, 2.0], "dur": 0.8, "vel": 85},
            {"notes": [75, 74, 72, 69], "beats": [0.0, 0.67, 1.33, 2.0], "dur": 0.4, "vel": 80}
        ],
        "verse": [
            # Call and response phrases walking the Pentatonic Minor + Tritone scale (A=69, C=72, D=74, Eb=75, E=76, G=79)
            # Bar 1-4 (Call): descending sliding themes
            {"notes": [79, 76, 75, 74, 72, 69], "beats": [0.0, 0.67, 1.0, 1.67, 2.0, 2.67], "dur": 0.3, "vel": 90},
            {"notes": [72, 74, 75, 76], "beats": [0.0, 0.5, 1.0, 1.5], "dur": 0.35, "vel": 88},
            # Bar 5-8 (Response): syncopated riffs 
            {"notes": [69, 72, 69, 74, 72], "beats": [0.0, 0.67, 2.0, 2.67, 3.33], "dur": 0.28, "vel": 94},
            {"notes": [76, 75, 74, 72, 69], "beats": [0.0, 0.33, 0.67, 1.33, 2.0], "dur": 0.4, "vel": 92}
        ],
        "solo": [
            # Passionate sliding improvisation with Liquidation & Fragmentation
            {"notes": [79, 79, 79, 76], "beats": [0.0, 0.33, 0.67, 1.0], "dur": 0.25, "vel": 105}, # Fragmentation
            {"notes": [76, 75, 74, 72, 69, 72, 74], "beats": [0.0, 0.33, 0.67, 1.0, 1.33, 1.67, 2.0], "dur": 0.2, "vel": 100},
            {"notes": [75, 75, 72, 69], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.5, "vel": 98},
            {"notes": [69, 72, 74, 76], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.6, "vel": 95}
        ],
        "outro": [
            {"notes": [76, 75, 74, 72], "beats": [0.0, 0.67, 1.33, 2.0], "dur": 0.4, "vel": 85},
            {"notes": [69], "beats": [0.0], "dur": 2.0, "vel": 80} # Last single held string
        ]
    },
    "harmony": {
        "intro": [
            {"notes": [57, 61, 64], "beats": [0.0, 2.0], "dur": 1.5, "vel": 70},
            {"notes": [59, 62, 66], "beats": [0.0, 2.0], "dur": 1.5, "vel": 72}
        ],
        "verse": [
            # Rhythm guitar chunks (blues shuffle walking pattern on the 5th and 6th degrees)
            {"notes": [57, 64], "beats": [0.0, 0.67, 1.0, 1.67], "dur": 0.3, "vel": 75}, # A-E chord chunks
            {"notes": [57, 66], "beats": [2.0, 2.67, 3.0, 3.67], "dur": 0.3, "vel": 75}, # A-F# chunks
            {"notes": [62, 69], "beats": [0.0, 0.67, 1.0, 1.67], "dur": 0.3, "vel": 72}, # D-A chunks
            {"notes": [64, 71], "beats": [0.0, 0.67, 1.0, 1.67], "dur": 0.3, "vel": 78}  # E-B chunks
        ],
        "solo": [
            {"notes": [57, 64], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.4, "vel": 80},
            {"notes": [57, 66], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.4, "vel": 80},
            {"notes": [62, 69], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.4, "vel": 78},
            {"notes": [64, 71], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.4, "vel": 82}
        ],
        "outro": [
            {"notes": [57, 61, 64], "beats": [0.0], "dur": 1.8, "vel": 65},
            {"notes": [45, 57, 61, 64], "beats": [0.0], "dur": 3.0, "vel": 60}
        ]
    },
    "bass": {
        "intro": [
            {"notes": [45, 33], "beats": [0.0, 2.0], "dur": 1.2, "vel": 85},
            {"notes": [40, 28], "beats": [0.0, 2.0], "dur": 1.2, "vel": 88}
        ],
        "verse": [
            # Steady thumping mono bass on strong beats (< 130Hz registering for sub-bass safety)
            {"notes": [45], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.8, "vel": 82}, # Root A
            {"notes": [38], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.8, "vel": 80}, # Root D 
            {"notes": [40], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.8, "vel": 85}, # Root E
            {"notes": [45], "beats": [0.0, 2.0], "dur": 1.8, "vel": 78}
        ],
        "solo": [
            {"notes": [45], "beats": [0.0, 0.67, 1.0, 1.67, 2.0, 2.67, 3.0, 3.67], "dur": 0.4, "vel": 88}, # Driving pulse
            {"notes": [38], "beats": [0.0, 0.67, 1.0, 1.67, 2.0, 2.67, 3.0, 3.67], "dur": 0.4, "vel": 86},
            {"notes": [40], "beats": [0.0, 0.67, 1.0, 1.67, 2.0, 2.67, 3.0, 3.67], "dur": 0.4, "vel": 90},
            {"notes": [45], "beats": [0.0, 2.0], "dur": 1.5, "vel": 80}
        ],
        "outro": [
            {"notes": [45], "beats": [0.0, 2.0], "dur": 1.5, "vel": 75},
            {"notes": [33], "beats": [0.0], "dur": 3.0, "vel": 70}
        ]
    },
    "drums": {
        "intro": [
            {"notes": [36, 42], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.1, "vel": 70}, # Steady floor stomps
            {"notes": [36, 42], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.1, "vel": 70}
        ],
        "verse": [
            # Foot stomp on beats 1 and 3 (note 36), handclap on 2 and 4 (note 39)
            # Swing eighths (note 42 hi-hat) on triplets to add delta sway
            {"notes": [36, 42], "beats": [0.0, 0.67], "dur": 0.1, "vel": 80},
            {"notes": [39, 42], "beats": [1.0, 1.67], "dur": 0.1, "vel": 85},
            {"notes": [36, 42], "beats": [2.0, 2.67], "dur": 0.1, "vel": 80},
            {"notes": [39, 42], "beats": [3.0, 3.67], "dur": 0.1, "vel": 85}
        ],
        "solo": [
            # Driving beat with open hat triplets (note 46)
            {"notes": [36, 46], "beats": [0.0, 0.67, 1.0, 1.67, 2.0, 2.67, 3.0, 3.67], "dur": 0.1, "vel": 90},
            {"notes": [36, 46], "beats": [0.0, 0.67, 1.0, 1.67, 2.0, 2.67, 3.0, 3.67], "dur": 0.1, "vel": 90},
            {"notes": [36, 46], "beats": [0.0, 0.67, 1.0, 1.67, 2.0, 2.67, 3.0, 3.67], "dur": 0.1, "vel": 90},
            {"notes": [36, 46], "beats": [0.0, 0.67, 1.0, 1.67, 2.0, 2.67, 3.0, 3.67], "dur": 0.1, "vel": 90}
        ],
        "outro": [
            {"notes": [36, 42], "beats": [0.0, 1.0, 2.0], "dur": 0.1, "vel": 70},
            {"notes": [36], "beats": [0.0], "dur": 0.2, "vel": 60}
        ]
    }
}

def add_note(events: List[Tuple[int, Message]], channel: int, note: int, start: int, dur: int, velocity: int) -> None:
    # Metrical Gravity & Breathing pass: accent downbeats (beat 1 & 3 are start_ticks multiples of 1920 or 960)
    acc_vel = velocity
    beat_pos = start % BAR
    # downbeat beats (beat 0) receives +10 velocity boost
    if beat_pos == 0:
        acc_vel = min(127, velocity + 10)
    # weak triplet subdivision gets -8 velocity attenuation for syncopated breathing
    elif beat_pos % TPB != 0:
        acc_vel = max(30, velocity - 12)  # slightly more contrast

    # Physicality Strum roll delay for Resonator and Acoustic Slide (channels 0 and 1)
    # 20ms strum delay = 0.02s * 72 bpm = 1.44 beats / min? Let's use ticks. 
    # TPB = 480. 1 beat = 480 ticks. 72 BPM -> 1.2 beats/sec -> 1 beat is 0.833s.
    # 20ms is roughly 0.02 * (480 / 0.833) = 11.5 ticks, let's delay each note in a chord slightly.
    delay = 0
    if channel in [0, 1]:
        # Simple pitch-dependent or arbitrary slight offset to stagger strum notes
        delay = (note % 6) * 6  # stagger up to 30 ticks for strum realism

    events.append((start + delay, Message("note_on", channel=channel, note=note, velocity=acc_vel, time=0)))
    events.append((start + delay + dur, Message("note_off", channel=channel, note=note, velocity=0, time=0)))

def add_program(events: List[Tuple[int, Message]], channel: int, program: int, tick: int = 0) -> None:
    events.append((tick, Message("program_change", channel=channel, program=program, time=0)))

def build_track(events: List[Tuple[int, Message]], name: str) -> MidiTrack:
    track = MidiTrack()
    track.append(MetaMessage("track_name", name=name, time=0))
    prev = 0
    order = {"program_change": 0, "control_change": 1, "note_on": 2, "note_off": 3}
    for tick, msg in sorted(events, key=lambda item: (item[0], order.get(item[1].type, 9), item[1].type)):
        msg.time = tick - prev
        track.append(msg)
        prev = tick
    track.append(MetaMessage("end_of_track", time=0))
    return track

def build_midi() -> MidiFile:
    midi_file = MidiFile(type=1, ticks_per_beat=TPB)
    
    # 0. Tempo Map / Conductor Track
    tempo_track = MidiTrack()
    tempo_track.append(MetaMessage("track_name", name="Conductor", time=0))
    tempo_track.append(MetaMessage("set_tempo", tempo=TEMPO, time=0))
    tempo_track.append(MetaMessage("time_signature", numerator=12, denominator=8, clocks_per_click=36, notated_32nd_notes_per_beat=8, time=0))
    tempo_track.append(MetaMessage("end_of_track", time=0))
    midi_file.tracks.append(tempo_track)
    
    # Track structures
    track_events = {row["name"]: [] for row in ROWS}
    
    # Program Changes initialization
    for row in ROWS:
        add_program(track_events[row["name"]], row["channel"], row["program"], 0)
        
    # Generate cells across the section order
    current_tick = 0
    for section in SECTION_ORDER:
        kind = section["kind"]
        bars = section["bars"]
        chords_in_sec = section["chords"]
        
        for bar_idx in range(bars):
            chord_name = chords_in_sec[bar_idx % len(chords_in_sec)]
            bar_start = current_tick + (bar_idx * BAR)
            
            # Retrieve cells for kind
            for row in ROWS:
                kind_key = kind if kind in CELL_LIBRARY[row["kind"]] else "verse"
                cells = CELL_LIBRARY[row["kind"]][kind_key]
                # choose cell based on bar index
                cell = cells[bar_idx % len(cells)]
                
                # Assign notes based on register kind
                for n_idx, beat in enumerate(cell["beats"]):
                    start_offset = int(beat * TPB)
                    dur_ticks = int(cell["dur"] * TPB)
                    
                    raw_notes = cell["notes"]
                    # If bass or harmony chunk, map notes based on backing chord roots or triad tones
                    if row["kind"] == "bass":
                        # standard delta walking base notes (root and fifth)
                        root = CHORDS[chord_name][0]
                        note_mapped = root if n_idx % 2 == 0 else root + 7
                        add_note(track_events[row["name"]], row["channel"], note_mapped, bar_start + start_offset, dur_ticks, cell["vel"])
                    elif row["kind"] == "harmony" and kind == "verse":
                        # follow actual chord triad
                        chord_notes = CHORDS[chord_name]
                        note_mapped = chord_notes[n_idx % len(chord_notes)]
                        add_note(track_events[row["name"]], row["channel"], note_mapped, bar_start + start_offset, dur_ticks, cell["vel"])
                    else:
                        # Lead, solo or drums
                        for single_n in raw_notes if isinstance(raw_notes, list) else [raw_notes]:
                            add_note(track_events[row["name"]], row["channel"], single_n, bar_start + start_offset, dur_ticks, cell["vel"])
                            
        current_tick += (bars * BAR)
        
    # Assemble and append tracks to MIDI file
    for row in ROWS:
        track = build_track(track_events[row["name"]], row["name"])
        midi_file.tracks.append(track)
        
    return midi_file

def main():
    print("Writing delta blues multitrack MIDI file...")
    midi_file = build_midi()
    MIDI_PATH.parent.mkdir(parents=True, exist_ok=True)
    midi_file.save(str(MIDI_PATH))
    print(f"MIDI successfully written to {MIDI_PATH}")
    
    # 1. Proactive Verification of MIDI Tracks and Channel 10
    print("Verifying MIDI output structure...")
    read_mid = MidiFile(str(MIDI_PATH))
    for idx, track in enumerate(read_mid.tracks):
        print(f"Track {idx}: {track.name} - Events: {len(track)}")
        for msg in track:
            if msg.type == 'note_on' and msg.channel == 9:
                print("SUCCESS: Percussion events confirmed on Channel 10.")
                break
                
    # 2. HQ FluidSynth Rendering and normalization
    print("Rendering audio via FluidSynth...")
    WAV_PATH.parent.mkdir(parents=True, exist_ok=True)
    OGG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Run FluidSynth CLI
    # Use -af gain/volume adjustments and peaks adjustments inside ffmpeg to output HQ OGG format
    shell_cmd = f"fluidsynth -ni -g 1.5 -F {WAV_PATH} {SOUNDFONT} {MIDI_PATH}"
    print(f"Running command: {shell_cmd}")
    subprocess.run(shell_cmd.split(), check=True)
    
    # Output to OGG containing high-quality voice-bubble encoding via ffmpeg
    print("Encoding and normalizing to OGG...")
    ffmpeg_cmd = f"ffmpeg -i {WAV_PATH} -af volume=10dB -codec:a libopus -b:a 64k {OGG_PATH} -y"
    print(f"Running command: {ffmpeg_cmd}")
    subprocess.run(ffmpeg_cmd.split(), check=True)
    print(f"Audio successfully rendered to {OGG_PATH}")
    
    # 3. Export to MusicXML via Music21 (using continuous binary str writing safety)
    print("Converting MIDI back to MusicXML score...")
    score_stream = converter.parse(str(MIDI_PATH))
    
    # Assign specific part names in Stream
    for idx, part in enumerate(score_stream.parts):
        if idx < len(ROWS):
            part.id = ROWS[idx]["name"]
            part.partName = ROWS[idx]["name"]
            
    XML_PATH.parent.mkdir(parents=True, exist_ok=True)
    score_stream.write("musicxml", fp=str(XML_PATH))
    print(f"Score successfully written to {XML_PATH}")
    
    # 4. Write manifest
    manifest = {
        "project": "027-delta-blues-shack",
        "genre": "Blues",
        "subgenre": "Delta Blues",
        "bpm": BPM,
        "key": "A pentatonic minor / blues hexatonic",
        "instrumentation": [row["name"] for row in ROWS],
        "sections": [{"name": sec["name"], "bars": sec["bars"]} for sec in SECTION_ORDER],
        "files": {
            "midi": str(MIDI_PATH.relative_to(ROOT.parent.parent)),
            "wav": str(WAV_PATH.relative_to(ROOT.parent.parent)),
            "ogg": str(OGG_PATH.relative_to(ROOT.parent.parent)),
            "musicxml": str(XML_PATH.relative_to(ROOT.parent.parent)),
        }
    }
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)
    print("Manifest written.")

if __name__ == "__main__":
    main()
