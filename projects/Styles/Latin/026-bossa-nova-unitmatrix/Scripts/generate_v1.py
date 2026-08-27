#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

ROOT = Path("/opt/data/projects/Genres/Latin/026-bossa-nova-unitmatrix")
MIDI_PATH = ROOT / "MIDI" / "v1_bossa_nova_unitmatrix.mid"
WAV_PATH = ROOT / "Renders" / "v1_bossa_nova_unitmatrix.wav"
OGG_PATH = ROOT / "Audio" / "v1_bossa_nova_unitmatrix.ogg"
ANALYSIS_PATH = ROOT / "Analysis" / "v1_manifest.json"
SOUNDFONT = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")

TPB = 480
BPM = 80
TEMPO = bpm2tempo(BPM)
BAR = TPB * 4

GUITAR_CH = 0
BASS_CH = 1
DRUM_CH = 9

# GM programs
NYLON_GUITAR = 24
ACOUSTIC_BASS = 32

# GM percussion notes
KICK = 36
SIDE_STICK = 37
CLOSED_HAT = 42
OPEN_HAT = 46
SHAKER = 54
LOW_CONGA = 64
HIGH_CONGA = 63

SECTIONS: List[Tuple[str, int]] = [
    ("Intro", 4),
    ("A", 12),
    ("B", 8),
    ("A_prime", 12),
    ("Outro", 4),
]

# UnitMatrix concept: rows = voices / pattern layers, cols = sections.
UNIT_MATRIX = {
    "rows": ["Guitar", "Bass", "Percussion"],
    "cols": [name for name, _ in SECTIONS],
    "cells": {
        "Guitar": {
            "Intro": {"pitch_pattern": [62, 65, 69, 72], "rhythm_pattern": [0.0, 1.5]},
            "A": {"pitch_pattern": [62, 65, 67, 69, 72], "rhythm_pattern": [0.0, 0.75, 1.5, 2.5, 3.25]},
            "B": {"pitch_pattern": [67, 69, 72, 74, 77], "rhythm_pattern": [0.0, 0.75, 1.5, 2.5, 3.25]},
            "A_prime": {"pitch_pattern": [62, 65, 67, 69, 72], "rhythm_pattern": [0.0, 0.75, 1.5, 2.5, 3.25]},
            "Outro": {"pitch_pattern": [62, 65, 69], "rhythm_pattern": [0.0]},
        },
        "Bass": {
            "Intro": {"pitch_pattern": [38, 41, 45, 47], "rhythm_pattern": [0.0, 2.0]},
            "A": {"pitch_pattern": [38, 41, 43, 45, 47], "rhythm_pattern": [0.0, 1.0, 2.0, 3.0]},
            "B": {"pitch_pattern": [43, 45, 47, 50, 52], "rhythm_pattern": [0.0, 1.0, 2.0, 3.0]},
            "A_prime": {"pitch_pattern": [38, 41, 43, 45, 47], "rhythm_pattern": [0.0, 1.0, 2.0, 3.0]},
            "Outro": {"pitch_pattern": [38, 41], "rhythm_pattern": [0.0]},
        },
        "Percussion": {
            "Intro": {"kick": [0.0, 2.0], "stick": [1.5, 3.5], "hat": [0.5, 1.5, 2.5, 3.5]},
            "A": {"kick": [0.0, 2.0], "stick": [1.0, 3.0], "hat": [0.5, 1.5, 2.5, 3.5]},
            "B": {"kick": [0.0, 1.75, 2.0], "stick": [1.0, 3.0], "hat": [0.5, 1.5, 2.5, 3.5], "conga": [0.75, 2.75]},
            "A_prime": {"kick": [0.0, 2.0], "stick": [1.0, 3.0], "hat": [0.5, 1.5, 2.5, 3.5], "shaker": [0.25, 0.75, 1.25, 1.75, 2.25, 2.75, 3.25, 3.75]},
            "Outro": {"kick": [0.0], "stick": [2.0], "hat": [0.5, 2.5]},
        },
    },
}


def add_note(events: List[Tuple[int, Message]], channel: int, note: int, start: int, dur: int, velocity: int) -> None:
    events.append((start, Message("note_on", channel=channel, note=note, velocity=velocity, time=0)))
    events.append((start + dur, Message("note_off", channel=channel, note=note, velocity=0, time=0)))


def add_program(events: List[Tuple[int, Message]], channel: int, program: int, tick: int = 0) -> None:
    events.append((tick, Message("program_change", channel=channel, program=program, time=0)))


def build_track(events: List[Tuple[int, Message]]) -> MidiTrack:
    track = MidiTrack()
    prev = 0
    for tick, msg in sorted(events, key=lambda item: (item[0], 0 if item[1].type in {"program_change", "control_change"} else 1, item[1].type)):
        delta = tick - prev
        msg.time = delta
        track.append(msg)
        prev = tick
    track.append(MetaMessage("end_of_track", time=0))
    return track


def bar_start(section_index: int, bar_in_section: int) -> int:
    return sum(length for _, length in SECTIONS[:section_index]) * BAR + bar_in_section * BAR


def build_midi() -> MidiFile:
    midi_file = MidiFile(type=1, ticks_per_beat=TPB)

    # Meta track
    meta = MidiTrack()
    meta.append(MetaMessage("track_name", name="Meta", time=0))
    meta.append(MetaMessage("time_signature", numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
    meta.append(MetaMessage("set_tempo", tempo=TEMPO, time=0))
    meta.append(MetaMessage("key_signature", key="Dm", time=0))
    meta.append(MetaMessage("end_of_track", time=0))
    midi_file.tracks.append(meta)

    guitar_events: List[Tuple[int, Message]] = []
    bass_events: List[Tuple[int, Message]] = []
    drum_events: List[Tuple[int, Message]] = []

    add_program(guitar_events, GUITAR_CH, NYLON_GUITAR, 0)
    add_program(bass_events, BASS_CH, ACOUSTIC_BASS, 0)

    section_offset = 0
    for section_index, (section_name, bars) in enumerate(SECTIONS):
        for bar in range(bars):
            abs_bar = section_offset + bar
            start = abs_bar * BAR
            cells = UNIT_MATRIX["cells"]

            g_cell = cells["Guitar"][section_name]
            g_durs = [TPB // 2, TPB // 2, TPB // 2, TPB // 2, TPB // 2]
            for i, off_beats in enumerate(g_cell["rhythm_pattern"]):
                beat = int(off_beats * TPB)
                pitch = g_cell["pitch_pattern"][i % len(g_cell["pitch_pattern"])]
                dur = g_durs[i % len(g_durs)]
                add_note(guitar_events, GUITAR_CH, pitch, start + beat, dur, 82 if i == 0 else 64)

            b_cell = cells["Bass"][section_name]
            bass_line = b_cell["pitch_pattern"]
            for i, off_beats in enumerate(b_cell["rhythm_pattern"]):
                beat = int(off_beats * TPB)
                pitch = bass_line[i % len(bass_line)]
                dur = TPB // 2
                add_note(bass_events, BASS_CH, pitch, start + beat, dur, 84 if i == 0 else 72)

            d_cell = cells["Percussion"][section_name]
            for off_beats in d_cell.get("kick", []):
                add_note(drum_events, DRUM_CH, KICK, start + int(off_beats * TPB), TPB // 8, 98)
            for off_beats in d_cell.get("stick", []):
                add_note(drum_events, DRUM_CH, SIDE_STICK, start + int(off_beats * TPB), TPB // 8, 84)
            for off_beats in d_cell.get("hat", []):
                add_note(drum_events, DRUM_CH, CLOSED_HAT, start + int(off_beats * TPB), TPB // 16, 74)
            for off_beats in d_cell.get("conga", []):
                add_note(drum_events, DRUM_CH, HIGH_CONGA, start + int(off_beats * TPB), TPB // 8, 82)
            for off_beats in d_cell.get("shaker", []):
                add_note(drum_events, DRUM_CH, SHAKER, start + int(off_beats * TPB), TPB // 16, 68)

        section_offset += bars

    midi_file.tracks.append(build_track(guitar_events))
    midi_file.tracks.append(build_track(bass_events))
    midi_file.tracks.append(build_track(drum_events))
    return midi_file


def verify_midi(path: Path) -> Dict[str, int]:
    check = MidiFile(path)
    percussion = 0
    note_on = 0
    channels = set()
    for track in check.tracks:
        for msg in track:
            if not msg.is_meta and hasattr(msg, "channel"):
                channels.add(msg.channel)
                if msg.type == "note_on" and msg.velocity > 0:
                    note_on += 1
                    if msg.channel == DRUM_CH:
                        percussion += 1
    if percussion == 0:
        raise RuntimeError("No percussion note_on events on channel 9 in MIDI")
    return {"note_on": note_on, "percussion_note_on": percussion, "channels": sorted(channels)}


def render_audio(midi_path: Path) -> None:
    if not SOUNDFONT.exists():
        raise FileNotFoundError(f"SoundFont missing: {SOUNDFONT}")
    for path in [WAV_PATH, OGG_PATH]:
        if path.exists():
            path.unlink()
    subprocess.run([
        "fluidsynth",
        "-ni",
        str(SOUNDFONT),
        str(midi_path),
        "-F",
        str(WAV_PATH),
        "-r",
        "44100",
    ], check=True)
    subprocess.run([
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(WAV_PATH),
        "-af",
        "volume=18dB",
        "-codec:a",
        "libopus",
        "-b:a",
        "96k",
        str(OGG_PATH),
    ], check=True)


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    for sub in ["MIDI", "Audio", "Renders", "Analysis", "Notes", "Scripts", "Scores", "BandLab"]:
        (ROOT / sub).mkdir(parents=True, exist_ok=True)

    midi_file = build_midi()
    midi_file.save(str(MIDI_PATH))
    verification = verify_midi(MIDI_PATH)
    render_audio(MIDI_PATH)

    manifest = {
        "project": "026-bossa-nova-unitmatrix",
        "workflow": "UnitMatrix-first",
        "rows": UNIT_MATRIX["rows"],
        "columns": UNIT_MATRIX["cols"],
        "files": {
            "midi": str(MIDI_PATH),
            "wav": str(WAV_PATH),
            "ogg": str(OGG_PATH),
        },
        "tempo_bpm": BPM,
        "meter": "4/4",
        "sections": SECTIONS,
        "verification": verification,
        "soundfont": str(SOUNDFONT),
    }
    ANALYSIS_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
