#!/usr/bin/env python3
"""Funk Groove — Method 011 (Euclidean) + 026 (DPSM)"""

import sys, os, copy
sys.path.insert(0, '/opt/data/repos/musicom')
from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

def euclidean_rhythm(hits, steps):
    if hits >= steps: return [1] * steps
    if hits == 0: return [0] * steps
    pattern = [[1] if i < hits else [0] for i in range(steps)]
    while len(pattern) > hits:
        num_to_merge = min(hits, len(pattern) - hits)
        for i in range(num_to_merge): pattern[i].extend(pattern.pop())
    res = []
    for p in pattern: res.extend(p)
    return res

def build_unit(all_events, section_idx, section_ticks):
    start, end = section_idx * section_ticks, (section_idx + 1) * section_ticks
    events = []
    for e in all_events:
        if start <= e.start_tick < end:
            new_e = copy.deepcopy(e)
            new_e.start_tick -= start; new_e.end_tick -= start
            if new_e.end_tick > section_ticks: new_e.end_tick = section_ticks
            events.append(new_e)
    if not events or events[-1].end_tick < section_ticks:
        events.append(MusicEvent(pitch=0, volume=0, start_tick=section_ticks-10, end_tick=section_ticks))
    return MusicUnit(events=events)

TPB, BPM, BPB = 480, 110, 4
BAR, SECTION = TPB * BPB, TPB * BPB * 16
composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
composer.create_matrix(num_voices=5, num_sections=2)
composer.add_voice("Drums", program=0, channel=9)
composer.add_voice("Bass", program=MidiInstrument.BASS, channel=0)
composer.add_voice("Guitar", program=MidiInstrument.ACOUSTIC_GUITAR, channel=1)
composer.add_voice("Keys", program=MidiInstrument.PIANO, channel=2)
composer.add_voice("Horns", program=MidiInstrument.TRUMPET, channel=3)
composer.add_section("A", bars=16); composer.add_section("B", bars=16)

# Drums
k, s = euclidean_rhythm(5, 16), [0,0,0,0,1,0,0,0,0,0,1,0,0,1,0,0]
drum_events = []
for b in range(32):
    for st in range(16):
        t = b * BAR + st * (BAR // 16)
        if k[st]: drum_events.append(MusicEvent(pitch=36, volume=100, start_tick=t, end_tick=t+60))
        if s[st]: drum_events.append(MusicEvent(pitch=38, volume=95, start_tick=t, end_tick=t+60))
        drum_events.append(MusicEvent(pitch=42, volume=(60 if st%4==0 else 45), start_tick=t, end_tick=t+30))

# Bass
bass_events = []
for b in range(32):
    pat = [36, 48, 36, 41, 36, 48, 43, 36]
    for i, n in enumerate(pat):
        t, dur = b * BAR + i * (BAR // 8), (BAR // 8 if i % 2 == 0 else BAR // 4)
        bass_events.append(MusicEvent(pitch=n, volume=(95 if i%3==0 else 80), start_tick=t, end_tick=t+dur))

# Guitar scratches/Keys stabs
guitar_events, keys_events = [], []
chord_prog = [[60,64,67], [60,64,67], [62,65,69], [64,67,71]]
for b in range(32):
    for i in range(16):
        t = b * BAR + i * (BAR // 16)
        guitar_events.append(MusicEvent(pitch=(60 if i%2==0 else 64), volume=(70 if i%4==0 else 50), start_tick=t, end_tick=t+BAR//16-10))
        if i % 8 in [2, 6]:
            for n in chord_prog[b%4]: keys_events.append(MusicEvent(pitch=n, volume=85, start_tick=t, end_tick=t+60))

# Horns DPSM
horn_events = []
for b in range(32):
    for l in range(3):
        ph = l * (BAR // 24)
        for i in range(8):
            t = b * BAR + i * (BAR // 8) + ph
            horn_events.append(MusicEvent(pitch=chord_prog[b%4][i%3]+12, volume=75, start_tick=t, end_tick=t+BAR//8-20))

for i, s in enumerate(["A", "B"]):
    composer.fill_voice_section("Drums", s, build_unit(drum_events, i, SECTION))
    composer.fill_voice_section("Bass", s, build_unit(bass_events, i, SECTION))
    composer.fill_voice_section("Guitar", s, build_unit(guitar_events, i, SECTION))
    composer.fill_voice_section("Keys", s, build_unit(keys_events, i, SECTION))
    composer.fill_voice_section("Horns", s, build_unit(horn_events, i, SECTION))

out_dir = "/opt/data/projects/Styles/Funk/groove/v1"
os.makedirs(out_dir, exist_ok=True)
mid = os.path.join(out_dir, "funk_groove.mid")
composer.to_midi(mid)
write_grid_visualization(composer.matrix, os.path.join(out_dir, "grid_visualization.txt"), ticks_per_character=480, voice_names=["Drums", "Bass", "Guitar", "Keys", "Horns"], bpm=BPM)
write_provenance(mid, AI_ASSISTED, "funk_groove", parameters={"bpm": BPM, "methods": ["011", "026"]})
print(f"✓ Funk Redone: {mid}")
