#!/usr/bin/env python3
"""Ambient Evolving — Method 026 (DPSM) + 023 (Tendency Masking)"""

import sys, os, copy, random
sys.path.insert(0, '/opt/data/repos/musicom')
from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

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

TPB, BPM, BPB = 480, 60, 4
BAR, SECTION = TPB * BPB, TPB * BPB * 16
composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
composer.create_matrix(num_voices=4, num_sections=2)
composer.add_voice("Pad", program=MidiInstrument.SYNTH_PAD, channel=0)
composer.add_voice("Texture", program=MidiInstrument.SYNTH_PAD, channel=1)
composer.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=3)
composer.add_section("A", bars=16); composer.add_section("B", bars=16)

chord_prog = [[48, 55, 60], [48, 55, 62], [50, 57, 62], [52, 59, 64]]
pad_events, texture_events, bass_events, lead_events = [], [], [], []

for b in range(32):
    c = chord_prog[b % 4]
    t = b * BAR
    for n in c: pad_events.append(MusicEvent(pitch=n, volume=55, start_tick=t, end_tick=t+BAR))
    for l in range(3):
        ph = l * (BAR // 24)
        for i in range(8):
            st = t + i * (BAR // 8) + ph
            texture_events.append(MusicEvent(pitch=c[i%3], volume=50, start_tick=st, end_tick=st+BAR//8-20))
    bass_events.append(MusicEvent(pitch=c[0]-12, volume=60, start_tick=t, end_tick=t+BAR))
    
    # Lead Tendency Masking
    center, width = 72 + int(4 * (b/32)), 12
    for _ in range(random.randint(2,3)):
        st = t + random.randint(0, BAR-480)
        lead_events.append(MusicEvent(pitch=random.randint(center-width//2, center+width//2), volume=random.randint(40,60), start_tick=st, end_tick=st+BAR//2))

for i, s in enumerate(["A", "B"]):
    composer.fill_voice_section("Pad", s, build_unit(pad_events, i, SECTION))
    composer.fill_voice_section("Texture", s, build_unit(texture_events, i, SECTION))
    composer.fill_voice_section("Bass", s, build_unit(bass_events, i, SECTION))
    composer.fill_voice_section("Lead", s, build_unit(lead_events, i, SECTION))

out_dir = "/opt/data/projects/Styles/Ambient/evolving/v1"
os.makedirs(out_dir, exist_ok=True)
mid = os.path.join(out_dir, "ambient_evolving.mid")
composer.to_midi(mid)
write_grid_visualization(composer.matrix, os.path.join(out_dir, "grid_visualization.txt"), ticks_per_character=480, voice_names=["Pad", "Texture", "Bass", "Lead"], bpm=BPM)
write_provenance(mid, AI_ASSISTED, "ambient_evolving", parameters={"bpm": BPM, "methods": ["023", "026"]})
print(f"✓ Ambient Redone: {mid}")
