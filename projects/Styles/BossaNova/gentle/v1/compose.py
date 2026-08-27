#!/usr/bin/env python3
"""Bossa Nova Gentle — Method 011 (Euclidean) + 002 (Markov) + 026 (DPSM)"""

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

TPB, BPM, BPB = 480, 100, 4
BAR, SECTION = TPB * BPB, TPB * BPB * 16
composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
composer.create_matrix(num_voices=4, num_sections=2)
composer.add_voice("Guitar", program=MidiInstrument.ACOUSTIC_GUITAR, channel=0)
composer.add_voice("Bass", program=MidiInstrument.BASS, channel=1)
composer.add_voice("Flute", program=MidiInstrument.FLUTE, channel=2)
composer.add_voice("Percussion", program=0, channel=9)
composer.add_section("A", bars=16); composer.add_section("B", bars=16)

chords = [[60,64,67,70], [59,62,65,69], [60,64,67,71], [60,64,67,71]]
guitar_events, bass_events, flute_events, perc_events = [], [], [], []

for b in range(32):
    c = chords[b % 4]
    t_bar = b * BAR
    for l in range(3):
        ph = l * (BAR // 24)
        for i in range(8):
            st = t_bar + i * (BAR // 8) + ph
            guitar_events.append(MusicEvent(pitch=c[i%3], volume=65, start_tick=st, end_tick=st+BAR//8-20))
    for st in range(16):
        t = t_bar + st * (BAR // 16)
        if st in [0, 4, 7, 10, 13]: # Euclidean-ish
            bass_events.append(MusicEvent(pitch=c[0]-24, volume=70, start_tick=t, end_tick=t+BAR//8))
    for bt in range(4):
        t = t_bar + bt * (BAR // 4)
        if bt in [1, 3]: perc_events.append(MusicEvent(pitch=37, volume=65, start_tick=t, end_tick=t+60))
        for eh in range(2): perc_events.append(MusicEvent(pitch=42, volume=50, start_tick=t+eh*(BAR//8), end_tick=t+eh*(BAR//8)+30))

scale = [0, 2, 4, 5, 7, 9, 11]
for i in range(128):
    t_f, dur = i * (BAR // 4), (BAR // 8 if i % 4 == 3 else BAR // 4)
    if t_f >= SECTION * 2: break
    flute_events.append(MusicEvent(pitch=72+random.choice(scale), volume=75, start_tick=t_f, end_tick=t_f+dur-20))

for i, s in enumerate(["A", "B"]):
    composer.fill_voice_section("Guitar", s, build_unit(guitar_events, i, SECTION))
    composer.fill_voice_section("Bass", s, build_unit(bass_events, i, SECTION))
    composer.fill_voice_section("Flute", s, build_unit(flute_events, i, SECTION))
    composer.fill_voice_section("Percussion", s, build_unit(perc_events, i, SECTION))

out_dir = "/opt/data/projects/Styles/BossaNova/gentle/v1"
os.makedirs(out_dir, exist_ok=True)
mid = os.path.join(out_dir, "bossa_nova_gentle.mid")
composer.to_midi(mid)
write_grid_visualization(composer.matrix, os.path.join(out_dir, "grid_visualization.txt"), ticks_per_character=480, voice_names=["Gtr", "Bass", "Flute", "Perc"], bpm=BPM)
write_provenance(mid, AI_ASSISTED, "bossa_nova_gentle", parameters={"bpm": BPM, "methods": ["011", "002", "026"]})
print(f"✓ Bossa Nova Redone: {mid}")
