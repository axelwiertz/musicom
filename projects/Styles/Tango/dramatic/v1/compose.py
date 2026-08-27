#!/usr/bin/env python3
"""Tango Dramatic — Method 011 (Euclidean) + 001 (Skeleton-First) + 026 (DPSM)"""

import sys, os, copy
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

TPB, BPM, BPB = 480, 130, 4
BAR, SECTION = TPB * BPB, TPB * BPB * 16
composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
composer.create_matrix(num_voices=4, num_sections=2)
composer.add_voice("Bandoneon", program=21, channel=0)
composer.add_voice("Piano", program=MidiInstrument.PIANO, channel=1)
composer.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
composer.add_voice("Percussion", program=0, channel=9)
composer.add_section("A", bars=16); composer.add_section("B", bars=16)

dna_p = [69, 72, 74, 76, 74, 72, 69, 67, 65, 67, 69, 72, 74, 76, 77, 76]
dna_r = [BAR//4, BAR//8, BAR//8, BAR//4, BAR//8, BAR//8, BAR//4, BAR//4, BAR//8, BAR//8, BAR//4, BAR//8, BAR//8, BAR//4, BAR//8, BAR//8]
chords = [[57,60,64],[55,58,62],[52,56,59],[57,60,64]]
bandoneon_events, piano_events, bass_events, perc_events = [], [], [], []

for b in range(32):
    t_bar = b * BAR
    t_dna = 0
    for p, r in zip(dna_p, dna_r):
        bandoneon_events.append(MusicEvent(pitch=p, volume=85, start_tick=t_bar+t_dna, end_tick=t_bar+t_dna+r-20))
        t_dna += r
    t_hab = t_bar
    for d_mul in [3, 1, 2, 2]:
        dur = (BAR // 8) * d_mul
        for n in chords[b%4]: piano_events.append(MusicEvent(pitch=n, volume=80, start_tick=t_hab, end_tick=t_hab+dur-20))
        t_hab += dur
    for st in range(16):
        t = t_bar + st * (BAR // 16)
        if st in [0, 4, 7, 10, 13]: bass_events.append(MusicEvent(pitch=chords[b%4][0]-24, volume=90, start_tick=t, end_tick=t+BAR//8))
    for bt in range(4):
        t = t_bar + bt * (BAR // 4)
        if bt in [0, 2]: perc_events.append(MusicEvent(pitch=38, volume=95, start_tick=t, end_tick=t+60))
        if (b*2+bt)%3==0: perc_events.append(MusicEvent(pitch=42, volume=70, start_tick=t, end_tick=t+30))

for i, s in enumerate(["A", "B"]):
    composer.fill_voice_section("Bandoneon", s, build_unit(bandoneon_events, i, SECTION))
    composer.fill_voice_section("Piano", s, build_unit(piano_events, i, SECTION))
    composer.fill_voice_section("Bass", s, build_unit(bass_events, i, SECTION))
    composer.fill_voice_section("Percussion", s, build_unit(perc_events, i, SECTION))

out_dir = "/opt/data/projects/Styles/Tango/dramatic/v1"
os.makedirs(out_dir, exist_ok=True)
mid = os.path.join(out_dir, "tango_dramatic.mid")
composer.to_midi(mid)
write_grid_visualization(composer.matrix, os.path.join(out_dir, "grid_visualization.txt"), ticks_per_character=480, voice_names=["Band", "Piano", "Bass", "Perc"], bpm=BPM)
write_provenance(mid, AI_ASSISTED, "tango_dramatic", parameters={"bpm": BPM, "methods": ["011", "001", "026"]})
print(f"✓ Tango Redone: {mid}")
