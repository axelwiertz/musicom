# -*- coding: utf-8 -*-
"""Project 053 -- Euclidean Binaural
Composition Method 012: Euclidean Groove Locking (Bjorklund)
Sound Production SP-021: Binaural Woodworth-Schlosberg Spatialization

Concept: Multiple Euclidean rhythm patterns mapped to D Dorian pitches.
Form AABA. Binaural spatialization in post-processing.
"""
import os
import json
import math
import wave
import numpy as np

from structures import MusicUnit, MusicEvent, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

# ---------------------------------------------------------------- CONFIG -----
PROJECT_NAME = "053-euclidean-binaural"
PROJECT_DIR = "/opt/data/projects/Styles/Experimental/053-euclidean-binaural"
BPM = 110
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR = TICKS_PER_BEAT * BEATS_PER_BAR  # 1920 ticks
SECTION_BARS = 2
SECTION_TICKS = SECTION_BARS * BAR    # 3840 ticks

# D Dorian scale pitches
D_DORIAN = [62, 64, 65, 67, 69, 71, 72]
D_DORIAN_LOW = [38, 40, 41, 43, 45, 47, 48]


def bjorklund(k, n):
    """Euclidean rhythm: distribute k onsets in n steps."""
    if k == 0:
        return [0] * n
    if k >= n:
        return [1] * n
    # Bucket method (simple, correct)
    pattern = []
    bucket = 0
    for i in range(n):
        bucket += k
        if bucket >= n:
            bucket -= n
            pattern.append(1)
        else:
            pattern.append(0)
    return pattern


def make_lead_unit(section_idx, section_ticks):
    """Lead: E(3,8) tresillo mapped to D Dorian."""
    euclid = bjorklund(3, 8)
    onsets = [i for i, v in enumerate(euclid) if v == 1]
    sub_div = section_ticks // 8
    degrees_cycle = [0, 4, 2, 5, 3, 6, 1]

    unit = MusicUnit()
    for bar in range(SECTION_BARS):
        offset = bar * BAR
        note_idx = 0
        for step in onsets:
            tick = offset + step * sub_div
            deg_idx = (section_idx * 6 + bar * 3 + note_idx) % len(degrees_cycle)
            pitch = D_DORIAN[degrees_cycle[deg_idx]]
            end = min(tick + sub_div, offset + BAR)
            unit.add_event(MusicEvent(pitch=pitch, volume=85, start_tick=tick, end_tick=end))
            note_idx += 1
    return unit


def make_lead_b_unit(section_ticks):
    """Lead B section: E(5,8) for contrast."""
    euclid = bjorklund(5, 8)
    onsets = [i for i, v in enumerate(euclid) if v == 1]
    sub_div = section_ticks // 8
    degrees_cycle = [4, 2, 6, 0, 5, 3, 1]

    unit = MusicUnit()
    for bar in range(SECTION_BARS):
        offset = bar * BAR
        note_idx = 0
        for step in onsets:
            tick = offset + step * sub_div
            deg_idx = (bar * 5 + note_idx) % len(degrees_cycle)
            pitch = D_DORIAN[degrees_cycle[deg_idx]]
            end = min(tick + sub_div, offset + BAR)
            unit.add_event(MusicEvent(pitch=pitch, volume=95, start_tick=tick, end_tick=end))
            note_idx += 1
    return unit


def make_pad_unit(section_idx, section_ticks):
    """Pad: E(5,16) chord tones."""
    euclid = bjorklund(5, 16)
    onsets = [i for i, v in enumerate(euclid) if v == 1]
    sub_div = section_ticks // 16
    chords = [
        [62, 65, 69],  # Dm
        [55, 59, 62],  # G
        [57, 60, 64],  # Am
        [53, 57, 60],  # F
    ]
    chord = chords[section_idx % len(chords)]

    unit = MusicUnit()
    for bar in range(SECTION_BARS):
        offset = bar * BAR
        for step in onsets:
            tick = offset + step * sub_div
            pitch = chord[step % len(chord)]
            dur = sub_div * 2
            end = min(tick + dur, offset + BAR)
            unit.add_event(MusicEvent(pitch=pitch, volume=55, start_tick=tick, end_tick=end))
    return unit


def make_bass_unit(section_idx, section_ticks):
    """Bass: E(2,5) walking bass."""
    euclid = bjorklund(2, 5)
    onsets = [i for i, v in enumerate(euclid) if v == 1]
    sub_div = section_ticks // 5
    bass_notes = [38, 43, 40, 45, 41, 43, 38, 40]

    unit = MusicUnit()
    for bar in range(SECTION_BARS):
        offset = bar * BAR
        for j, step in enumerate(onsets):
            tick = offset + step * sub_div
            pitch = bass_notes[(section_idx * 2 + bar + j) % len(bass_notes)]
            end = min(tick + sub_div, offset + BAR)
            unit.add_event(MusicEvent(pitch=pitch, volume=100, start_tick=tick, end_tick=end))
    return unit


def make_perc_unit(section_idx, section_ticks):
    """Percussion: E(7,16) samba pattern."""
    euclid = bjorklund(7, 16)
    onsets = [i for i, v in enumerate(euclid) if v == 1]
    sub_div = section_ticks // 16

    unit = MusicUnit()
    for bar in range(SECTION_BARS):
        offset = bar * BAR
        for step in onsets:
            tick = offset + step * sub_div
            drum_pitch = 36 if step % 2 == 0 else 38
            vol = 100 if drum_pitch == 36 else 80
            end = min(tick + 120, offset + BAR)
            unit.add_event(MusicEvent(pitch=drum_pitch, volume=vol, start_tick=tick, end_tick=end))
    return unit


def build_composer():
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    c.create_matrix(num_voices=4, num_sections=4)

    c.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
    c.add_voice("Pad", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
    c.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
    c.add_voice("Percussion", program=0, channel=9)

    c.add_section("A1", bars=SECTION_BARS)
    c.add_section("A2", bars=SECTION_BARS)
    c.add_section("B", bars=SECTION_BARS)
    c.add_section("A3", bars=SECTION_BARS)

    sections = ["A1", "A2", "B", "A3"]

    for sec_idx, sec_name in enumerate(sections):
        if sec_name == "B":
            lead_unit = make_lead_b_unit(SECTION_TICKS)
        else:
            lead_unit = make_lead_unit(sec_idx, SECTION_TICKS)
        pad_unit = make_pad_unit(sec_idx, SECTION_TICKS)
        bass_unit = make_bass_unit(sec_idx, SECTION_TICKS)
        perc_unit = make_perc_unit(sec_idx, SECTION_TICKS)

        c.fill_voice_section("Lead", sec_name, lead_unit)
        c.fill_voice_section("Pad", sec_name, pad_unit)
        c.fill_voice_section("Bass", sec_name, bass_unit)
        c.fill_voice_section("Percussion", sec_name, perc_unit)

    return c


def apply_binaural(wav_path, out_path, sr=44100):
    """SP-021: Binaural spatialization via Woodworth-Schlosberg ITD/ILD."""
    with wave.open(wav_path, 'r') as wf:
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    sr = framerate
    audio = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    n_samples = len(audio)

    head_radius = 0.0875
    c_sound = 343.0

    t = np.linspace(0, 1, n_samples)
    azimuth = 60.0 * np.sin(2 * np.pi * 0.15 * t)
    theta_rad = np.radians(azimuth)
    itd_seconds = (head_radius / c_sound) * (theta_rad + np.sin(theta_rad))
    itd_samples = np.round(itd_seconds * sr).astype(int)
    ild_db = 2.5 * np.sin(theta_rad)

    max_delay = max(abs(itd_samples.min()), abs(itd_samples.max()), 1)
    out_len = n_samples + max_delay
    left = np.zeros(out_len)
    right = np.zeros(out_len)

    for i in range(n_samples):
        delay = int(itd_samples[i])
        level_l = 10 ** (-ild_db[i] / 20.0) if ild_db[i] > 0 else 1.0
        level_r = 10 ** (ild_db[i] / 20.0) if ild_db[i] < 0 else 1.0

        li = i + max(0, delay)
        ri = i + max(0, -delay)
        if 0 <= li < out_len:
            left[li] += audio[i] * level_l
        if 0 <= ri < out_len:
            right[ri] += audio[i] * level_r

    peak = max(np.max(np.abs(left)), np.max(np.abs(right)))
    if peak > 0:
        scale = 0.89 / peak
        left *= scale
        right *= scale

    with wave.open(out_path, 'w') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        interleaved = np.empty(out_len * 2, dtype=np.float64)
        interleaved[0::2] = left
        interleaved[1::2] = right
        interleaved = np.clip(interleaved, -1.0, 1.0)
        wf.writeframes((interleaved * 32767).astype(np.int16).tobytes())

    return out_path


def main():
    os.makedirs(PROJECT_DIR, exist_ok=True)
    midi_dir = os.path.join(PROJECT_DIR, "MIDI")
    audio_dir = os.path.join(PROJECT_DIR, "Audio")
    analysis_dir = os.path.join(PROJECT_DIR, "Analysis")
    os.makedirs(midi_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(analysis_dir, exist_ok=True)

    composer = build_composer()

    ok, msg = composer.validate()
    if not ok:
        raise SystemExit(f"Validation failed: {msg}")

    midi_path = os.path.join(midi_dir, f"{PROJECT_NAME}.mid")
    composer.to_midi(midi_path)

    size = os.path.getsize(midi_path)
    assert size > 40, f"MIDI empty/corrupt: {size} bytes"
    print(f"MIDI OK: {midi_path} ({size} bytes)")

    grid_path = os.path.join(analysis_dir, "grid_visualization.txt")
    write_grid_visualization(
        composer.matrix, grid_path,
        ticks_per_character=240, bpm=BPM
    )
    print(f"Grid: {grid_path}")

    write_provenance(
        midi_path, classification=AI_ASSISTED,
        generator="053-euclidean-binaural/compose.py",
        parameters={
            "bpm": BPM,
            "key": "D Dorian",
            "method": "012-Euclidean Groove Locking",
            "sp_method": "SP-021 Binaural Spatialization",
            "euclidean_patterns": ["E(3,8)", "E(5,16)", "E(2,5)", "E(7,16)"],
            "form": "AABA",
        },
        notes="Euclidean rhythm patterns mapped to D Dorian scale. Binaural spatialization via Woodworth-Schlosberg ITD/ILD model."
    )

    # Euclidean pattern analysis
    with open(os.path.join(analysis_dir, "euclidean_patterns.txt"), "w") as f:
        f.write("# Euclidean Rhythm DNA (Method 012)\n\n")
        for k, n, label in [(3, 8, "Lead tresillo"), (5, 16, "Pad latin"), (2, 5, "Bass khaling"), (7, 16, "Perc samba")]:
            pat = bjorklund(k, n)
            grid = "".join(["X" if v else "." for v in pat])
            f.write(f"E({k},{n}) {label}: {grid}\n")
        f.write("\n## Voice Assignment\n")
        f.write("Lead:  E(3,8)  tresillo - melodic motif\n")
        f.write("Pad:   E(5,16) latin  - harmonic texture\n")
        f.write("Bass:  E(2,5)  khaling - walking bass\n")
        f.write("Perc:  E(7,16) samba   - rhythmic drive\n")
        f.write("\n## Binaural (SP-021)\n")
        f.write("Woodworth-Schlosberg ITD/ILD model\n")
        f.write("Azimuth: +/-60deg sine sweep at 0.15Hz\n")
        f.write("Head radius: 8.75cm, c=343m/s\n")

    print("Composition complete.")


if __name__ == "__main__":
    main()
