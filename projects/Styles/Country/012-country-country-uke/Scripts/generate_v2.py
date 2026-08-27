#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo
from music21 import converter

ROOT = Path("/opt/data/projects/Genres/Country/012-country-country-uke")
MIDI_PATH = ROOT / "MIDI" / "v2_country_unitmatrix.mid"
WAV_PATH = ROOT / "Renders" / "v2_country_unitmatrix.wav"
OGG_PATH = ROOT / "Audio" / "v2_country_unitmatrix.ogg"
XML_PATH = ROOT / "Scores" / "v2_country_unitmatrix.musicxml"
MANIFEST_PATH = ROOT / "Analysis" / "v2_manifest.json"
SOUNDFONT = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")

TPB = 480
BPM = 96
TEMPO = bpm2tempo(BPM)
BAR = TPB * 4

SECTION_ORDER = [
    {"name": "Intro", "kind": "intro", "bars": 4, "chords": ["G", "D", "Em", "C"]},
    {"name": "Verse 1", "kind": "verse", "bars": 8, "chords": ["G", "D", "Em", "C", "G", "D", "C", "D"]},
    {"name": "Chorus 1", "kind": "chorus", "bars": 8, "chords": ["G", "D", "Em", "C", "G", "D", "C", "D"]},
    {"name": "Verse 2", "kind": "verse", "bars": 8, "chords": ["G", "D", "Em", "C", "G", "D", "C", "D"]},
    {"name": "Chorus 2", "kind": "chorus", "bars": 8, "chords": ["G", "D", "Em", "C", "G", "D", "C", "D"]},
    {"name": "Bridge", "kind": "bridge", "bars": 4, "chords": ["Em", "C", "G", "D"]},
    {"name": "Final Chorus", "kind": "final", "bars": 4, "chords": ["G", "D", "C", "D"]},
    {"name": "Outro", "kind": "outro", "bars": 4, "chords": ["G", "C", "G", "G"]},
]

CHORDS = {
    "G": [55, 59, 62],        # G3 B3 D4
    "D": [50, 54, 57],        # D3 F#3 A3
    "Em": [52, 55, 59],       # E3 G3 B3
    "C": [48, 52, 55],        # C3 E3 G3
    "G6": [55, 59, 62, 64],
    "Cadd9": [48, 52, 55, 59, 62],
    "Dsus4": [50, 55, 57, 62],
    "Em7": [52, 55, 59, 62],
}

ROWS = [
    {"name": "Lead Vocal", "kind": "lead", "channel": 0, "program": 53},
    {"name": "Harmony Vox", "kind": "harmony", "channel": 1, "program": 52},
    {"name": "Acoustic Guitar", "kind": "acoustic", "channel": 2, "program": 24},
    {"name": "Electric Guitar", "kind": "electric", "channel": 3, "program": 29},
    {"name": "Bass", "kind": "bass", "channel": 4, "program": 33},
    {"name": "Drums", "kind": "drums", "channel": 9, "program": 0},
    {"name": "Fiddle", "kind": "fiddle", "channel": 5, "program": 40},
    {"name": "Pedal Steel", "kind": "steel", "channel": 6, "program": 48},
]

# One-bar motif templates. Notes and beats are paired 1:1.
CELL_LIBRARY = {
    "lead": {
        "intro": {"base": "Scale: G major | Degrees: 1-2-3-5", "notes": [67, 69, 71, 74], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.8, "vel": 88},
        "verse": {"base": "Scale: G major | Degrees: 1-2-3-5-3-2-1-2", "notes": [67, 69, 71, 74, 71, 69, 67, 69], "beats": [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], "dur": 0.35, "vel": 84},
        "chorus": {"base": "Scale: G major | Degrees: 5-6-1-2-3-2-1", "notes": [74, 76, 67, 69, 71, 69, 67], "beats": [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0], "dur": 0.4, "vel": 92},
        "bridge": {"base": "Scale: E minor / G major | Degrees: 6-5-3-2", "notes": [76, 74, 71, 69], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.8, "vel": 86},
        "final": {"base": "Scale: G major | Degrees: 5-6-1-2-3-5", "notes": [74, 76, 67, 69, 71, 74], "beats": [0.0, 0.5, 1.0, 1.5, 2.5, 3.0], "dur": 0.45, "vel": 96},
        "outro": {"base": "Scale: G major | Degrees: 1-5-1", "notes": [67, 74, 67], "beats": [0.0, 1.5, 3.0], "dur": 0.9, "vel": 78},
    },
    "harmony": {
        "intro": {"base": "Scale: G major | Degrees: 3-5-6", "notes": [71, 74, 76], "beats": [0.0, 1.5, 3.0], "dur": 1.2, "vel": 76},
        "verse": {"base": "Scale: G major | Degrees: 3-2-1-2", "notes": [71, 69, 67, 69], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.9, "vel": 72},
        "chorus": {"base": "Scale: G major | Degrees: 6-5-3-2", "notes": [76, 74, 71, 69], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.9, "vel": 80},
        "bridge": {"base": "Scale: G major | Degrees: 5-3-2-1", "notes": [74, 71, 69, 67], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.9, "vel": 74},
        "final": {"base": "Scale: G major | Degrees: 3-5-6-5", "notes": [71, 74, 76, 74], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 1.0, "vel": 84},
        "outro": {"base": "Scale: G major | Degrees: 3-2-1", "notes": [71, 69, 67], "beats": [0.0, 1.5, 3.0], "dur": 1.1, "vel": 70},
    },
    "acoustic": {
        "intro": {"base": "Chord grid: G | D | Em | C | strum on 1 + 3", "notes": [55, 59, 62, 50, 54, 57, 52, 55, 59, 48, 52, 55], "beats": [0.0, 0.0, 0.0, 2.0, 2.0, 2.0, 0.0, 0.0, 0.0, 2.0, 2.0, 2.0], "dur": 0.45, "vel": 74},
        "verse": {"base": "Chord grid: G | D | Em | C | G | D | C | D | strum on 1 + 3", "notes": [55, 59, 62, 50, 54, 57, 52, 55, 59, 48, 52, 55], "beats": [0.0, 0.0, 0.0, 2.0, 2.0, 2.0, 0.0, 0.0, 0.0, 2.0, 2.0, 2.0], "dur": 0.42, "vel": 70},
        "chorus": {"base": "Chord grid: G | D | Em | C | lift with open voicings", "notes": [55, 59, 62, 50, 54, 57, 52, 55, 59, 48, 52, 55], "beats": [0.0, 0.0, 0.0, 2.0, 2.0, 2.0, 0.0, 0.0, 0.0, 2.0, 2.0, 2.0], "dur": 0.48, "vel": 84},
        "bridge": {"base": "Chord grid: Em | C | G | D | drop to lighter strum", "notes": [52, 55, 59, 48, 52, 55, 55, 59, 62, 50, 54, 57], "beats": [0.0, 0.0, 0.0, 2.0, 2.0, 2.0, 0.0, 0.0, 0.0, 2.0, 2.0, 2.0], "dur": 0.5, "vel": 68},
        "final": {"base": "Chord grid: G | D | C | D | tag ending", "notes": [55, 59, 62, 50, 54, 57, 48, 52, 55, 50, 54, 57], "beats": [0.0, 0.0, 0.0, 2.0, 2.0, 2.0, 0.0, 0.0, 0.0, 2.0, 2.0, 2.0], "dur": 0.5, "vel": 86},
        "outro": {"base": "Chord grid: G | C | G | G | fade out", "notes": [55, 59, 62, 48, 52, 55], "beats": [0.0, 0.0, 0.0, 2.0, 2.0, 2.0], "dur": 0.7, "vel": 64},
    },
    "electric": {
        "intro": {"base": "Scale: G major pentatonic | Degrees: 5-6-1-2", "notes": [74, 76, 67, 69], "beats": [0.5, 1.5, 2.5, 3.5], "dur": 0.3, "vel": 78},
        "verse": {"base": "Scale: G major pentatonic | Degrees: 5-6-1-2-3", "notes": [74, 76, 67, 69, 71], "beats": [0.5, 1.25, 2.0, 2.75, 3.5], "dur": 0.28, "vel": 76},
        "chorus": {"base": "Scale: G major pentatonic | Degrees: 3-5-6-5-3", "notes": [71, 74, 76, 74, 71], "beats": [0.25, 1.0, 1.75, 2.5, 3.25], "dur": 0.24, "vel": 88},
        "bridge": {"base": "Scale: G major pentatonic | Degrees: 2-3-5-6", "notes": [69, 71, 74, 76], "beats": [0.5, 1.5, 2.5, 3.5], "dur": 0.28, "vel": 74},
        "final": {"base": "Scale: G major pentatonic | Degrees: 5-6-1-2-3 | turnaround", "notes": [74, 76, 67, 69, 71], "beats": [0.25, 1.0, 1.75, 2.5, 3.25], "dur": 0.26, "vel": 90},
        "outro": {"base": "Scale: G major pentatonic | Degrees: 1-5-1", "notes": [67, 74, 67], "beats": [0.5, 2.0, 3.5], "dur": 0.45, "vel": 68},
    },
    "bass": {
        "intro": {"base": "Chord roots + fifths | G-D-Em-C", "notes": [43, 50, 45, 52], "beats": [0.0, 2.0, 0.0, 2.0], "dur": 0.9, "vel": 88},
        "verse": {"base": "Chord roots + fifths | walking country pulse", "notes": [43, 50, 45, 48], "beats": [0.0, 2.0, 0.0, 2.0], "dur": 0.9, "vel": 84},
        "chorus": {"base": "Chord roots + fifths | push into chorus", "notes": [43, 50, 45, 48], "beats": [0.0, 2.0, 0.0, 2.0], "dur": 0.92, "vel": 92},
        "bridge": {"base": "Chord roots + fifths | lower lift", "notes": [45, 48, 43, 50], "beats": [0.0, 2.0, 0.0, 2.0], "dur": 0.95, "vel": 82},
        "final": {"base": "Chord roots + fifths | tag ending", "notes": [43, 50, 48, 50], "beats": [0.0, 2.0, 0.0, 2.0], "dur": 0.95, "vel": 96},
        "outro": {"base": "Chord roots + fifths | fade", "notes": [43, 48, 43, 43], "beats": [0.0, 2.0, 0.0, 2.0], "dur": 1.0, "vel": 76},
    },
    "drums": {
        "intro": {"base": "Subset: country kit | kick + snare + hat", "notes": [36, 42, 38, 42, 36, 42, 38, 42], "beats": [0.0, 0.0, 1.0, 1.5, 2.0, 2.0, 3.0, 3.5], "dur": 0.15, "vel": 88},
        "verse": {"base": "Subset: country kit | kick on 1/3, snare on 2/4, hat eighths", "notes": [36, 42, 42, 38, 42, 42, 36, 42], "beats": [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], "dur": 0.12, "vel": 84},
        "chorus": {"base": "Subset: country kit | bigger backbeat + open hat", "notes": [36, 42, 46, 38, 42, 46, 36, 42], "beats": [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], "dur": 0.12, "vel": 94},
        "bridge": {"base": "Subset: country kit | pull back to half-time", "notes": [36, 42, 36, 42], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.16, "vel": 78},
        "final": {"base": "Subset: country kit | fill into ending", "notes": [36, 42, 46, 38, 42, 46, 36, 42], "beats": [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], "dur": 0.12, "vel": 98},
        "outro": {"base": "Subset: country kit | taper", "notes": [36, 42, 38, 42], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.12, "vel": 70},
    },
    "fiddle": {
        "intro": {"base": "Scale: G major | Degrees: 3-5-6-5", "notes": [71, 74, 76, 74], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.7, "vel": 78},
        "verse": {"base": "Scale: G major | Degrees: 5-6-1-2-3", "notes": [74, 76, 67, 69, 71], "beats": [0.0, 0.75, 1.5, 2.25, 3.0], "dur": 0.45, "vel": 74},
        "chorus": {"base": "Scale: G major | Degrees: 6-5-3-2-1", "notes": [76, 74, 71, 69, 67], "beats": [0.0, 0.75, 1.5, 2.25, 3.0], "dur": 0.45, "vel": 86},
        "bridge": {"base": "Scale: E minor / G major | Degrees: 2-3-5-6", "notes": [69, 71, 74, 76], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.55, "vel": 72},
        "final": {"base": "Scale: G major | Degrees: 5-6-1-2-3", "notes": [74, 76, 67, 69, 71], "beats": [0.0, 0.75, 1.5, 2.25, 3.0], "dur": 0.4, "vel": 90},
        "outro": {"base": "Scale: G major | Degrees: 3-2-1", "notes": [71, 69, 67], "beats": [0.0, 1.5, 3.0], "dur": 0.75, "vel": 68},
    },
    "steel": {
        "intro": {"base": "Chord tones + sus4 | G6 add color", "notes": [55, 59, 62, 64], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 1.4, "vel": 72},
        "verse": {"base": "Chord tones + sus4 | soft slides", "notes": [55, 59, 62, 60], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 1.2, "vel": 68},
        "chorus": {"base": "Chord tones + sus4 | wider lift", "notes": [55, 59, 62, 64], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 1.25, "vel": 82},
        "bridge": {"base": "Chord tones + sus4 | moody sustain", "notes": [52, 55, 59, 62], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 1.3, "vel": 66},
        "final": {"base": "Chord tones + sus4 | tag ending", "notes": [55, 59, 62, 64], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 1.35, "vel": 86},
        "outro": {"base": "Chord tones + sus4 | fade", "notes": [55, 59, 62], "beats": [0.0, 1.5, 3.0], "dur": 1.5, "vel": 62},
    },
}


def add_note(events: List[Tuple[int, Message]], channel: int, note: int, start: int, dur: int, velocity: int) -> None:
    events.append((start, Message("note_on", channel=channel, note=note, velocity=velocity, time=0)))
    events.append((start + dur, Message("note_off", channel=channel, note=note, velocity=0, time=0)))


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

    meta = MidiTrack()
    meta.append(MetaMessage("track_name", name="Meta", time=0))
    meta.append(MetaMessage("time_signature", numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
    meta.append(MetaMessage("set_tempo", tempo=TEMPO, time=0))
    meta.append(MetaMessage("key_signature", key="G", time=0))
    meta.append(MetaMessage("end_of_track", time=0))
    midi_file.tracks.append(meta)

    track_events: Dict[str, List[Tuple[int, Message]]] = {row["name"]: [] for row in ROWS}
    for row in ROWS:
        add_program(track_events[row["name"]], row["channel"], row["program"], 0)

    section_offset = 0
    for section in SECTION_ORDER:
        kind = section["kind"]
        bars = section["bars"]
        chords = section["chords"]
        for bar_idx in range(bars):
            bar_start = (section_offset + bar_idx) * BAR
            chord_name = chords[bar_idx % len(chords)]
            chord = CHORDS[chord_name]

            for row in ROWS:
                cell = CELL_LIBRARY[row["kind"]][kind]
                events = track_events[row["name"]]

                if row["kind"] == "acoustic":
                    # strum the current section chord on beats 1 and 3
                    for beat in (0.0, 2.0):
                        for i, note in enumerate(chord):
                            add_note(events, row["channel"], note, bar_start + int((beat + i * 0.03) * TPB), int(cell["dur"] * TPB), cell["vel"])
                elif row["kind"] == "bass":
                    root = chord[0] - 12
                    fifth = chord[2] - 12
                    line = [root, fifth, root, fifth]
                    beats = [0.0, 2.0, 0.0, 2.0]
                    for note, beat in zip(line, beats):
                        add_note(events, row["channel"], note, bar_start + int(beat * TPB), int(cell["dur"] * TPB), cell["vel"])
                elif row["kind"] == "drums":
                    for note, beat in zip(cell["notes"], cell["beats"]):
                        add_note(events, row["channel"], note, bar_start + int(beat * TPB), int(cell["dur"] * TPB), cell["vel"])
                else:
                    for note, beat in zip(cell["notes"], cell["beats"]):
                        add_note(events, row["channel"], note, bar_start + int(beat * TPB), int(cell["dur"] * TPB), cell["vel"])

        section_offset += bars

    for row in ROWS:
        midi_file.tracks.append(build_track(track_events[row["name"]], row["name"]))

    return midi_file


def verify_midi(path: Path) -> Dict[str, int | List[int]]:
    check = MidiFile(path)
    note_on = 0
    percussion = 0
    channels = set()
    for track in check.tracks:
        for msg in track:
            if not msg.is_meta and hasattr(msg, "channel"):
                channels.add(msg.channel)
                if msg.type == "note_on" and msg.velocity > 0:
                    note_on += 1
                    if msg.channel == 9:
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
        "fluidsynth", "-ni", str(SOUNDFONT), str(midi_path), "-F", str(WAV_PATH), "-r", "44100"
    ], check=True)
    subprocess.run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(WAV_PATH), "-af", "volume=18dB", "-codec:a", "libopus", "-b:a", "96k", str(OGG_PATH)
    ], check=True)


def export_musicxml(midi_path: Path) -> None:
    score = converter.parse(str(midi_path))
    score.write("musicxml", fp=str(XML_PATH))


def build_manifest(verification: Dict[str, int | List[int]]) -> Dict:
    matrix = []
    for row in ROWS:
        row_data = {"name": row["name"], "kind": row["kind"], "cells": []}
        for section in SECTION_ORDER:
            cell = CELL_LIBRARY[row["kind"]][section["kind"]]
            row_data["cells"].append({
                "section": section["name"],
                "section_kind": section["kind"],
                "bars": section["bars"],
                "base": cell["base"],
                "notes": cell["notes"],
                "beats": cell["beats"],
            })
        matrix.append(row_data)

    return {
        "project": "012-country-country-uke",
        "workflow": "UnitMatrix-first",
        "settings": {
            "genre": "Country",
            "subgenre": "Country-pop road song",
            "tempo_bpm": BPM,
            "meter": "4/4",
            "key": "G major",
            "total_bars": sum(section["bars"] for section in SECTION_ORDER),
            "sections": SECTION_ORDER,
            "rows": [row["name"] for row in ROWS],
        },
        "matrix": matrix,
        "files": {
            "midi": str(MIDI_PATH),
            "musicxml": str(XML_PATH),
            "wav": str(WAV_PATH),
            "ogg": str(OGG_PATH),
        },
        "verification": verification,
        "soundfont": str(SOUNDFONT),
    }


def ensure_dirs() -> None:
    for sub in ["MIDI", "Audio", "Renders", "Scores", "Analysis", "Notes", "Scripts"]:
        (ROOT / sub).mkdir(parents=True, exist_ok=True)


def main() -> None:
    ensure_dirs()
    midi = build_midi()
    midi.save(str(MIDI_PATH))
    verification = verify_midi(MIDI_PATH)
    render_audio(MIDI_PATH)
    export_musicxml(MIDI_PATH)
    manifest = build_manifest(verification)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
