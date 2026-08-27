#!/usr/bin/env python3
"""Hip-Hop Boom-Bap — Method 011 (Euclidean) + 002 (Markov) + 026 (DPSM)"""

import sys
import os
import random
import copy
sys.path.insert(0, '/opt/data/repos/musicom')

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

# === Method 011: Euclidean Groove ===
def euclidean_rhythm(hits, steps):
    if hits >= steps: return [1] * steps
    if hits == 0: return [0] * steps
    pattern = [[1] if i < hits else [0] for i in range(steps)]
    while len(pattern) > hits:
        num_to_merge = min(hits, len(pattern) - hits)
        for i in range(num_to_merge):
            pattern[i].extend(pattern.pop())
    res = []
    for p in pattern: res.extend(p)
    return res

# === Method 002: Markov Melody ===
def markov_melody(key_root, scale_intervals, length):
    melody = [key_root]
    for _ in range(length - 1):
        interval = random.choice([-2, -1, 0, 1, 2, 3])
        next_note = melody[-1] + interval
        octave = (next_note - key_root) // 12
        scale_pos = (next_note - key_root) % 12
        closest = min(scale_intervals, key=lambda x: abs(x - scale_pos))
        melody.append(key_root + octave * 12 + closest)
    return melody

# === Method 026: DPSM (Phase-Shift Minimalism) ===
def dpsm_arpeggio(chord_notes, bars, bpm, tpb, phase_offset=0):
    events = []
    BAR = tpb * 4
    EIGHTH = BAR // 8
    for bar in range(bars):
        for i in range(8):
            tick = bar * BAR + i * EIGHTH + phase_offset
            events.append(MusicEvent(pitch=chord_notes[i % len(chord_notes)], volume=65, start_tick=tick, end_tick=tick + EIGHTH - 20))
    return events

# Setup
TPB, BPM, BPB = 480, 90, 4
BAR, SECTION = TPB * BPB, TPB * BPB * 16

composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
composer.create_matrix(num_voices=4, num_sections=2)
composer.add_voice("Drums", program=0, channel=9)
composer.add_voice("Bass", program=MidiInstrument.BASS, channel=0)
composer.add_voice("Lead", program=MidiInstrument.PIANO, channel=1)
composer.add_voice("Pad", program=MidiInstrument.SYNTH_PAD, channel=2)
composer.add_section("A", bars=16)
composer.add_section("B", bars=16)

def build_unit(all_events, section_idx, section_ticks):
    start = section_idx * section_ticks
    end = (section_idx + 1) * section_ticks
    events = []
    for e in all_events:
        if start <= e.start_tick < end:
            new_e = copy.deepcopy(e)
            new_e.start_tick -= start
            new_e.end_tick -= start
            if new_e.end_tick > section_ticks: new_e.end_tick = section_ticks
            events.append(new_e)
    if not events or (events[-1].end_tick < section_ticks):
        events.append(MusicEvent(pitch=0, volume=0, start_tick=section_ticks-10, end_tick=section_ticks))
    return MusicUnit(events=events)

# Drums
kick, snare = euclidean_rhythm(5, 16), euclidean_rhythm(7, 16)
drum_events = []
for bar in range(32):
    for step in range(16):
        t = bar * BAR + step * (BAR // 16)
        if kick[step]: drum_events.append(MusicEvent(pitch=36, volume=100, start_tick=t, end_tick=t+60))
        if snare[step]: drum_events.append(MusicEvent(pitch=38, volume=90, start_tick=t, end_tick=t+60))
        if step % 2 == 0: drum_events.append(MusicEvent(pitch=42, volume=60, start_tick=t, end_tick=t+30))

# Bass
bass_notes = [40, 40, 43, 45, 40, 40, 47, 45]
bass_events = []
for bar in range(32):
    for i, n in enumerate(bass_notes):
        t = bar * BAR + i * (BAR // 8)
        bass_events.append(MusicEvent(pitch=n, volume=85, start_tick=t, end_tick=t+BAR//8))

# Lead/Pad
lead_p = markov_melody(64, [0, 2, 3, 5, 7, 8, 10], 128)
lead_events = []
for i, n in enumerate(lead_p):
    t, dur = i * (BAR // 4), (BAR // 4 if i % 4 != 3 else BAR // 2)
    lead_events.append(MusicEvent(pitch=n, volume=random.randint(70, 90), start_tick=t, end_tick=t+dur-20))

chord_prog = [[52, 55, 59], [53, 57, 60], [55, 59, 62], [52, 55, 59]]
pad_events = []
for bar in range(32):
    for layer in range(3):
        phase = layer * (BAR // 24)
        for e in dpsm_arpeggio(chord_prog[bar % 4], 1, BPM, TPB, phase):
            e.start_tick += bar * BAR; e.end_tick += bar * BAR
            pad_events.append(e)

for i, s in enumerate(["A", "B"]):
    composer.fill_voice_section("Drums", s, build_unit(drum_events, i, SECTION))
    composer.fill_voice_section("Bass", s, build_unit(bass_events, i, SECTION))
    composer.fill_voice_section("Lead", s, build_unit(lead_events, i, SECTION))
    composer.fill_voice_section("Pad", s, build_unit(pad_events, i, SECTION))

out_dir = "/opt/data/projects/Styles/HipHop/boom-bap/v1"
os.makedirs(out_dir, exist_ok=True)
mid = os.path.join(out_dir, "hiphop_boom_bap.mid")
composer.to_midi(mid)
write_grid_visualization(composer.matrix, os.path.join(out_dir, "grid_visualization.txt"), ticks_per_character=480, voice_names=["Drums", "Bass", "Lead", "Pad"], bpm=BPM)
write_provenance(mid, AI_ASSISTED, "hiphop_boom_bap", parameters={"bpm": BPM, "key": "Em", "bars": 32, "methods": ["011", "002", "026"]})
print(f"✓ Hip-Hop Redone: {mid}")
