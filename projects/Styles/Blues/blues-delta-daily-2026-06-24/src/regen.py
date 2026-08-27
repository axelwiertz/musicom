#!/usr/bin/env python3
"""Blues Delta Daily - 2026-06-24 - Delta Blues Composition"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo
from music21 import converter

# --- Project Paths ---
STYLE = "Blues"
DATE_STR = "2026-06-24"
COMP_NAME = "blues-delta-daily-" + DATE_STR
ROOT = Path("/opt/data/projects/Styles/" + STYLE + "/" + COMP_NAME)
MIDI_PATH = ROOT / "MIDI" / (COMP_NAME + ".mid")
WAV_PATH = ROOT / "Renders" / (COMP_NAME + ".wav")
OGG_PATH = ROOT / "Audio" / (COMP_NAME + ".ogg")
XML_PATH = ROOT / "Scores" / (COMP_NAME + ".musicxml")
ANALYSIS_PATH = ROOT / "Analysis" / "theory.md"
SOUNDFONT = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")

TPB = 480
BPM = 72
TEMPO = bpm2tempo(BPM)
BAR = TPB * 4

# --- 12-Bar Blues Structure (compact 8-bar form + intro/outro = 12 bars) ---
SECTION_ORDER = [
    {"name": "Intro", "kind": "intro", "bars": 2, "chords": ["A7", "A7"]},
    {"name": "Verse", "kind": "verse", "bars": 8, "chords": ["A7", "A7", "D7", "A7", "D7", "A7", "E7", "A7"]},
    {"name": "Outro", "kind": "outro", "bars": 2, "chords": ["A7", "A7"]},
]

CHORDS = {
    "A7": [45, 57, 61, 64, 67],
    "D7": [50, 57, 60, 62, 66],
    "E7": [40, 52, 56, 59, 62, 64],
}

ROWS = [
    {"name": "Resonator Slide (Lead Melody)", "kind": "lead", "channel": 0, "program": 25},
    {"name": "Acoustic Rhythm (Harmony)", "kind": "harmony", "channel": 1, "program": 26},
    {"name": "Fingerstyle Bass (Root)", "kind": "bass", "channel": 2, "program": 32},
    {"name": "Stomp & Clap (Percussion)", "kind": "drums", "channel": 9, "program": 0},
]

CELL_LIBRARY = {
    "lead": {
        "intro": [
            {"notes": [76, 75, 74, 72], "beats": [0.0, 0.67, 1.33, 2.67], "dur": 0.35, "vel": 82},
            {"notes": [69, 72, 74], "beats": [0.0, 1.0, 2.0], "dur": 0.4, "vel": 85},
        ],
        "verse": [
            {"notes": [79, 76, 75, 74, 72, 69], "beats": [0.0, 0.67, 1.0, 1.67, 2.33, 3.0], "dur": 0.3, "vel": 92},
            {"notes": [72, 69, 72, 74, 72, 69], "beats": [0.33, 1.0, 1.33, 2.0, 2.67, 3.33], "dur": 0.25, "vel": 95},
            {"notes": [69, 75, 74, 72], "beats": [0.0, 0.67, 1.33, 2.0], "dur": 0.4, "vel": 88},
            {"notes": [76, 74, 72, 69, 72, 74], "beats": [0.0, 0.5, 1.0, 1.5, 2.0, 2.5], "dur": 0.3, "vel": 90},
        ],
        "outro": [
            {"notes": [76, 74, 72, 69], "beats": [0.0, 0.67, 1.33, 2.0], "dur": 0.4, "vel": 80},
            {"notes": [69], "beats": [0.0], "dur": 3.5, "vel": 75},
        ]
    },
    "harmony": {
        "intro": [
            {"notes": [57, 61, 64], "beats": [0.0, 2.0], "dur": 1.5, "vel": 68},
            {"notes": [57, 61, 64], "beats": [0.0, 2.0], "dur": 1.5, "vel": 68},
        ],
        "verse": [
            {"notes": [57, 64], "beats": [0.0, 0.67, 1.0, 1.67, 2.0, 2.67, 3.0, 3.67], "dur": 0.25, "vel": 74},
            {"notes": [62, 69], "beats": [0.0, 0.67, 1.0, 1.67, 2.0, 2.67, 3.0, 3.67], "dur": 0.25, "vel": 72},
            {"notes": [64, 71], "beats": [0.0, 0.67, 1.0, 1.67, 2.0, 2.67, 3.0, 3.67], "dur": 0.25, "vel": 76},
            {"notes": [57, 64, 67], "beats": [0.0, 0.67, 1.0, 1.67, 2.0, 2.67, 3.0, 3.67], "dur": 0.25, "vel": 74},
        ],
        "outro": [
            {"notes": [57, 61, 64], "beats": [0.0], "dur": 2.0, "vel": 62},
            {"notes": [45, 57, 61, 64], "beats": [0.0], "dur": 3.5, "vel": 58},
        ]
    },
    "bass": {
        "intro": [
            {"notes": [45], "beats": [0.0, 2.0], "dur": 1.2, "vel": 82},
            {"notes": [45], "beats": [0.0, 2.0], "dur": 1.2, "vel": 82},
        ],
        "verse": [
            {"notes": [45], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.7, "vel": 84},
            {"notes": [50], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.7, "vel": 82},
            {"notes": [40], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.7, "vel": 86},
            {"notes": [45, 52], "beats": [0.0, 0.67, 1.0, 1.67, 2.0, 2.67, 3.0, 3.67], "dur": 0.35, "vel": 80},
        ],
        "outro": [
            {"notes": [45], "beats": [0.0, 2.0], "dur": 1.5, "vel": 72},
            {"notes": [33], "beats": [0.0], "dur": 3.5, "vel": 66},
        ]
    },
    "drums": {
        "intro": [
            {"notes": [36, 42], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.1, "vel": 68},
            {"notes": [36, 42], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.1, "vel": 68},
        ],
        "verse": [
            {"notes": [36, 42], "beats": [0.0, 0.67, 2.0, 2.67], "dur": 0.1, "vel": 78},
            {"notes": [39, 42], "beats": [1.0, 1.67, 3.0, 3.67], "dur": 0.1, "vel": 82},
            {"notes": [36, 42], "beats": [0.0, 0.67, 1.0, 2.0, 2.67, 3.0], "dur": 0.1, "vel": 80},
            {"notes": [39, 42], "beats": [0.33, 1.33, 1.67, 3.33, 3.67], "dur": 0.1, "vel": 84},
        ],
        "outro": [
            {"notes": [36, 42], "beats": [0.0, 1.0, 2.0, 3.0], "dur": 0.1, "vel": 66},
            {"notes": [36], "beats": [0.0], "dur": 0.2, "vel": 58},
        ]
    }
}


def add_note(events, channel, note, start, dur, velocity):
    beat_pos = start % BAR
    if beat_pos == 0:
        acc_vel = min(127, velocity + 10)
    elif beat_pos % TPB != 0:
        acc_vel = max(30, velocity - 10)
    else:
        acc_vel = velocity
    delay = 0
    if channel in [0, 1]:
        delay = (note % 5) * 5
    events.append((start + delay, Message("note_on", channel=channel, note=note, velocity=acc_vel, time=0)))
    events.append((start + delay + dur, Message("note_off", channel=channel, note=note, velocity=0, time=0)))


def add_program(events, channel, program, tick=0):
    events.append((tick, Message("program_change", channel=channel, program=program, time=0)))


def build_track(events, name):
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


def build_midi():
    midi_file = MidiFile(type=1, ticks_per_beat=TPB)
    tempo_track = MidiTrack()
    tempo_track.append(MetaMessage("track_name", name="Conductor", time=0))
    tempo_track.append(MetaMessage("set_tempo", tempo=TEMPO, time=0))
    tempo_track.append(MetaMessage("time_signature", numerator=12, denominator=8, clocks_per_click=36, notated_32nd_notes_per_beat=8, time=0))
    tempo_track.append(MetaMessage("end_of_track", time=0))
    midi_file.tracks.append(tempo_track)

    track_events = {row["name"]: [] for row in ROWS}
    for row in ROWS:
        add_program(track_events[row["name"]], row["channel"], row["program"], 0)

    current_tick = 0
    for section in SECTION_ORDER:
        kind = section["kind"]
        bars = section["bars"]
        chords = section["chords"]

        for bar_idx in range(bars):
            chord_name = chords[bar_idx % len(chords)]
            bar_start = current_tick + (bar_idx * BAR)

            for row in ROWS:
                kind_key = kind if kind in CELL_LIBRARY[row["kind"]] else "verse"
                cells = CELL_LIBRARY[row["kind"]][kind_key]
                cell = cells[bar_idx % len(cells)]

                for n_idx, beat in enumerate(cell["beats"]):
                    start_offset = int(beat * TPB)
                    dur_ticks = int(cell["dur"] * TPB)

                    if row["kind"] == "bass":
                        root = CHORDS[chord_name][0]
                        note_mapped = root if n_idx % 2 == 0 else root + 7
                        add_note(track_events[row["name"]], row["channel"], note_mapped, bar_start + start_offset, dur_ticks, cell["vel"])
                    elif row["kind"] == "harmony" and kind == "verse":
                        chord_notes = CHORDS[chord_name]
                        note_mapped = chord_notes[n_idx % len(chord_notes)]
                        add_note(track_events[row["name"]], row["channel"], note_mapped, bar_start + start_offset, dur_ticks, cell["vel"])
                    elif row["kind"] == "harmony":
                        raw_notes = cell["notes"]
                        for single_n in raw_notes if isinstance(raw_notes, list) else [raw_notes]:
                            add_note(track_events[row["name"]], row["channel"], single_n, bar_start + start_offset, dur_ticks, cell["vel"])
                    elif row["kind"] == "drums":
                        raw_notes = cell["notes"]
                        for single_n in raw_notes if isinstance(raw_notes, list) else [raw_notes]:
                            add_note(track_events[row["name"]], row["channel"], single_n, bar_start + start_offset, dur_ticks, cell["vel"])
                    else:
                        raw_notes = cell["notes"]
                        for single_n in raw_notes if isinstance(raw_notes, list) else [raw_notes]:
                            add_note(track_events[row["name"]], row["channel"], single_n, bar_start + start_offset, dur_ticks, cell["vel"])

        current_tick += (bars * BAR)

    for row in ROWS:
        track = build_track(track_events[row["name"]], row["name"])
        midi_file.tracks.append(track)

    return midi_file


def main():
    print("=== Delta Blues Daily: " + DATE_STR + " ===")

    # 1. Build MIDI
    print("Building MIDI...")
    midi_file = build_midi()
    MIDI_PATH.parent.mkdir(parents=True, exist_ok=True)
    midi_file.save(str(MIDI_PATH))
    print("  MIDI saved: " + str(MIDI_PATH))

    # 2. Verify
    print("Verifying MIDI...")
    read_mid = MidiFile(str(MIDI_PATH))
    for idx, track in enumerate(read_mid.tracks):
        print("  Track " + str(idx) + ": " + str(track.name) + " - " + str(len(track)) + " events")
        for msg in track:
            if msg.type == 'note_on' and msg.channel == 9:
                print("  -> Percussion on Ch.10: OK")
                break

    # 3. Render audio
    print("Rendering WAV via FluidSynth...")
    WAV_PATH.parent.mkdir(parents=True, exist_ok=True)
    OGG_PATH.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run("fluidsynth -ni -g 1.4 -F " + str(WAV_PATH) + " " + str(SOUNDFONT) + " " + str(MIDI_PATH), shell=True, check=True)
    print("  WAV saved: " + str(WAV_PATH))

    # 4. Encode OGG
    print("Encoding OGG...")
    subprocess.run("ffmpeg -i " + str(WAV_PATH) + " -af volume=10dB -codec:a libopus -b:a 64k " + str(OGG_PATH) + " -y", shell=True, check=True, capture_output=True)
    print("  OGG saved: " + str(OGG_PATH))

    # 5. MusicXML
    print("Exporting MusicXML...")
    try:
        score_stream = converter.parse(str(MIDI_PATH))
        for idx, part in enumerate(score_stream.parts):
            if idx < len(ROWS):
                part.id = ROWS[idx]["name"]
                part.partName = ROWS[idx]["name"]
        XML_PATH.parent.mkdir(parents=True, exist_ok=True)
        score_stream.write("musicxml", fp=str(XML_PATH))
        print("  XML saved: " + str(XML_PATH))
    except Exception as e:
        print("  XML export skipped: " + str(e))

    # 6. Theory / Analysis doc
    print("Writing analysis...")
    ANALYSIS_PATH.parent.mkdir(parents=True, exist_ok=True)
    total_bars = sum(s["bars"] for s in SECTION_ORDER)
    theory_lines = []
    theory_lines.append("# Delta Blues Daily -- " + DATE_STR)
    theory_lines.append("")
    theory_lines.append("## Overview")
    theory_lines.append("- **Style**: Blues (Delta Blues)")
    theory_lines.append("- **Tempo**: " + str(BPM) + " BPM")
    theory_lines.append("- **Time Signature**: 12/8 (swung triplet feel)")
    theory_lines.append("- **Key Center**: A (Blues Hexatonic + Blue Notes)")
    theory_lines.append("- **Form**: Intro (2 bars) -> 8-Bar Blues Verse -> Outro (2 bars) = " + str(total_bars) + " bars total")
    theory_lines.append("")
    theory_lines.append("## Instrumentation")
    theory_lines.append("| Track | Instrument (GM) | Register | Role |")
    theory_lines.append("|-------|-----------------|----------|------|")
    theory_lines.append("| 1 | Steel-String Acoustic (25) | C4-E6 | Lead melody, slide calls & responses |")
    theory_lines.append("| 2 | Jazz Guitar (26) | C3-C5 | Rhythmic harmony, shuffle chord chunks |")
    theory_lines.append("| 3 | Acoustic Bass (32) | E1-C3 | Root-fifth walking bass line |")
    theory_lines.append("| 4 | Standard Kit (Ch.10) | -- | Stomp [36], Clap [39], Hat [42] |")
    theory_lines.append("")
    theory_lines.append("## Harmonic Progression (8-Bar Blues in A7)")
    theory_lines.append("| Bar | Chord | Function |")
    theory_lines.append("|-----|-------|----------|")
    theory_lines.append("| 1 | A7 | Tonic (I7) |")
    theory_lines.append("| 2 | A7 | Tonic (I7) |")
    theory_lines.append("| 3 | D7 | Subdominant (IV7) |")
    theory_lines.append("| 4 | A7 | Tonic (I7) |")
    theory_lines.append("| 5 | D7 | Subdominant (IV7) |")
    theory_lines.append("| 6 | A7 | Tonic (I7) |")
    theory_lines.append("| 7 | E7 | Dominant (V7) -- turnaround |")
    theory_lines.append("| 8 | A7 | Tonic (I7) -- resolution |")
    theory_lines.append("")
    theory_lines.append("## Melodic Material")
    theory_lines.append("- **Scale**: A Blues Hexatonic [A, C, D, Eb, E, G] = pitch classes [0, 3, 5, 6, 7, 10]")
    theory_lines.append("- **Blue Notes**: Eb (b3), G (b7) create characteristic blues tension")
    theory_lines.append("- **Motifs**: Descending call phrases (G->E->Eb->D->C->A), syncopated response fragments")
    theory_lines.append("- **Developmental Ops**: Fragmentation in response bars, liquidation on turnaround")
    theory_lines.append("")
    theory_lines.append("## Rhythm")
    theory_lines.append("- **Metrical Gravity**: [1.0, 0, 0.5, 0] -- strong downbeats (1, 3)")
    theory_lines.append("- **Shuffle Grid**: Triplet subdivisions (0.0, 0.33, 0.67) per beat")
    theory_lines.append("- **Bass**: Root on beats 1 & 3, fifth on 2 & 4")
    theory_lines.append("- **Drums**: Stomp on 1 & 3, clap on 2 & 4, hi-hat on swing eighths")
    theory_lines.append("")
    theory_lines.append("## Pitch Classes Used")
    theory_lines.append("[0, 3, 5, 6, 7, 10]")
    theory_lines.append("")
    theory_lines.append("## Files")
    theory_lines.append("- MIDI: `MIDI/" + COMP_NAME + ".mid`")
    theory_lines.append("- WAV: `Renders/" + COMP_NAME + ".wav`")
    theory_lines.append("- OGG: `Audio/" + COMP_NAME + ".ogg`")
    theory_lines.append("- MusicXML: `Scores/" + COMP_NAME + ".musicxml`")

    theory_doc = "\n".join(theory_lines)
    with open(ANALYSIS_PATH, "w") as f:
        f.write(theory_doc)
    print("  Analysis: " + str(ANALYSIS_PATH))

    # 7. Manifest
    manifest = {
        "project": COMP_NAME,
        "style": "Blues",
        "subgenre": "Delta Blues",
        "bpm": BPM,
        "time_sig": "12/8",
        "key": "A Blues Hexatonic",
        "instrumentation": [row["name"] for row in ROWS],
        "sections": [{"name": s["name"], "bars": s["bars"]} for s in SECTION_ORDER],
        "files": {
            "midi": str(MIDI_PATH.relative_to(ROOT.parent.parent)),
            "wav": str(WAV_PATH.relative_to(ROOT.parent.parent)),
            "ogg": str(OGG_PATH.relative_to(ROOT.parent.parent)),
            "musicxml": str(XML_PATH.relative_to(ROOT.parent.parent)),
        },
        "total_bars": total_bars,
        "pitch_classes": [0, 3, 5, 6, 7, 10],
        "scale": "Blues Hexatonic",
        "metrical_gravity": [1.0, 0, 0.5, 0],
    }
    manifest_path = ROOT / "Analysis" / (COMP_NAME + "_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print("  Manifest: " + str(manifest_path))

    # 8. Index HTML
    print("Writing index page...")
    index_html = '<!DOCTYPE html><html lang="en"><head>'
    index_html += '<meta charset="UTF-8"><title>' + COMP_NAME + '</title>'
    index_html += '<style>body{font-family:sans-serif;max-width:800px;margin:2em auto;background:#1a1a2e;color:#eee;}h1{color:#e94560;}a{color:#0f3460;}pre{background:#16213e;padding:1em;border-radius:6px;}</style>'
    index_html += '</head><body>'
    index_html += '<h1>' + COMP_NAME + '</h1>'
    index_html += '<p><strong>Style:</strong> Blues (Delta Blues) | <strong>Date:</strong> ' + DATE_STR + '</p>'
    index_html += '<p><strong>Tempo:</strong> ' + str(BPM) + ' BPM | <strong>Time:</strong> 12/8 | <strong>Key:</strong> A Blues Hexatonic</p>'
    index_html += '<h2>Audio</h2>'
    index_html += '<audio controls><source src="Audio/' + COMP_NAME + '.ogg" type="audio/ogg"></audio>'
    index_html += '<h2>Scores</h2><ul>'
    index_html += '<li><a href="MIDI/' + COMP_NAME + '.mid">MIDI</a></li>'
    index_html += '<li><a href="Renders/' + COMP_NAME + '.wav">WAV</a></li>'
    index_html += '<li><a href="Scores/' + COMP_NAME + '.musicxml">MusicXML</a></li>'
    index_html += '</ul>'
    index_html += '<h2>Analysis</h2>'
    index_html += '<p><a href="Analysis/theory.md">Theory (Markdown)</a> | <a href="Analysis/' + COMP_NAME + '_manifest.json">Manifest</a></p>'
    index_html += '</body></html>'

    index_path = ROOT / "index.html"
    with open(index_path, "w") as f:
        f.write(index_html)
    print("  Index: " + str(index_path))

    print("=== Done ===")


if __name__ == "__main__":
    main()