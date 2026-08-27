#!/usr/bin/env python3
"""Metal Riff-Driven — Method 011 (Euclidean) + 001 (Skeleton-First)"""

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

TPB, BPM, BPB = 480, 160, 4
BAR, SECTION = TPB * BPB, TPB * BPB * 16
composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
composer.create_matrix(num_voices=5, num_sections=2)
composer.add_voice("Drums", program=0, channel=9)
composer.add_voice("Guitar", program=30, channel=0)
composer.add_voice("Bass", program=MidiInstrument.BASS, channel=1)
composer.add_voice("Rhythm", program=29, channel=2)
composer.add_voice("Lead", program=80, channel=3)
composer.add_section("A", bars=16); composer.add_section("B", bars=16)

# Drums
k, s = euclidean_rhythm(12, 16), [0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0]
drum_events = []
for b in range(32):
    for st in range(16):
        t = b * BAR + st * (BAR // 16)
        if k[st]: drum_events.append(MusicEvent(pitch=36, volume=110, start_tick=t, end_tick=t+60))
        if s[st]: drum_events.append(MusicEvent(pitch=38, volume=105, start_tick=t, end_tick=t+60))
        drum_events.append(MusicEvent(pitch=42, volume=65, start_tick=t, end_tick=t+30))

# Riffs
riff_p, riff_r = [0, 0, 3, 0, 5, 0, 3, 0], [2, 1, 2, 1, 2, 1, 2, 1]
guitar_events, bass_events, rhythm_events, lead_events = [], [], [], []
for b in range(32):
    t = b * BAR
    for i, (p, r) in enumerate(zip(riff_p, riff_r)):
        dur = (BAR // 8) * r
        guitar_events.append(MusicEvent(pitch=40+p, volume=(100 if i%4==0 else 85), start_tick=t, end_tick=t+dur-10))
        bass_events.append(MusicEvent(pitch=28+p, volume=95, start_tick=t, end_tick=t+dur-10))
        t += dur
    t_bar = b * BAR
    for bt in range(4):
        st = t_bar + bt * (BAR // 4)
        for n in ([52, 59] if b % 4 != 2 else [55, 62]): rhythm_events.append(MusicEvent(pitch=n, volume=95, start_tick=st, end_tick=st+120))
    for i in range(16):
        st = t_bar + i * (BAR // 16)
        lead_events.append(MusicEvent(pitch=64+(i%8), volume=80, start_tick=st, end_tick=st+60))

for i, s in enumerate(["A", "B"]):
    composer.fill_voice_section("Drums", s, build_unit(drum_events, i, SECTION))
    composer.fill_voice_section("Guitar", s, build_unit(guitar_events, i, SECTION))
    composer.fill_voice_section("Bass", s, build_unit(bass_events, i, SECTION))
    composer.fill_voice_section("Rhythm", s, build_unit(rhythm_events, i, SECTION))
    composer.fill_voice_section("Lead", s, build_unit(lead_events, i, SECTION))

out_dir = "/opt/data/projects/Styles/Metal/riff-driven/v1"
os.makedirs(out_dir, exist_ok=True)
mid = os.path.join(out_dir, "metal_riff.mid")
composer.to_midi(mid)
write_grid_visualization(composer.matrix, os.path.join(out_dir, "grid_visualization.txt"), ticks_per_character=480, voice_names=["Drums", "Guitar", "Bass", "Rhythm", "Lead"], bpm=BPM)
write_provenance(mid, AI_ASSISTED, "metal_riff", parameters={"bpm": BPM, "methods": ["011", "001"]})
print(f"✓ Metal Redone: {mid}")
