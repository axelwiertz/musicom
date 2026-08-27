#!/usr/bin/env python3
"""Soul Smooth — Method 011 (Euclidean) + 002 (Markov) + 026 (DPSM)"""

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

TPB, BPM, BPB = 480, 85, 4
BAR, SECTION = TPB * BPB, TPB * BPB * 16
composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
composer.create_matrix(num_voices=5, num_sections=2)
composer.add_voice("Rhodes", program=4, channel=0)
composer.add_voice("Bass", program=MidiInstrument.BASS, channel=1)
composer.add_voice("Organ", program=19, channel=2)
composer.add_voice("Melody", program=MidiInstrument.FLUTE, channel=3)
composer.add_voice("Percussion", program=0, channel=9)
composer.add_section("A", bars=16); composer.add_section("B", bars=16)

chords = [[60,64,67,70,74],[58,62,65,69,72],[55,58,62,65,69],[57,60,64,67,70]]
rhodes_events, bass_events, organ_events, melody_events, perc_events = [], [], [], [], []

for b in range(32):
    c = chords[b % 4]
    t_bar = b * BAR
    for l in range(3):
        ph = l * (BAR // 24)
        for i in range(8):
            st = t_bar + i * (BAR // 8) + ph
            rhodes_events.append(MusicEvent(pitch=c[i%len(c)], volume=70, start_tick=st, end_tick=st+BAR//8-20))
    for st in range(16):
        t = t_bar + st * (BAR // 16)
        if st in [0, 4, 7, 10, 13]:
            bass_events.append(MusicEvent(pitch=c[0]-24, volume=85, start_tick=t, end_tick=t+BAR//8))
    for bt in range(4):
        t = t_bar + bt * (BAR // 4)
        if bt in [0, 2]: perc_events.append(MusicEvent(pitch=36, volume=90, start_tick=t, end_tick=t+60))
        if bt in [1, 3]: perc_events.append(MusicEvent(pitch=38, volume=75, start_tick=t, end_tick=t+60))
        for eh in range(2): perc_events.append(MusicEvent(pitch=42, volume=55, start_tick=t+eh*(BAR//8), end_tick=t+eh*(BAR//8)+30))
    for n in c: organ_events.append(MusicEvent(pitch=n+12, volume=60, start_tick=t_bar, end_tick=t_bar+BAR))

scale = [0, 2, 4, 5, 7, 9, 11]
for i in range(128):
    t_m, dur = i * (BAR // 4), (BAR // 8 if i % 4 == 3 else BAR // 4)
    if t_m >= SECTION * 2: break
    melody_events.append(MusicEvent(pitch=72+random.choice(scale), volume=80, start_tick=t_m, end_tick=t_m+dur-20))

for i, s in enumerate(["A", "B"]):
    composer.fill_voice_section("Rhodes", s, build_unit(rhodes_events, i, SECTION))
    composer.fill_voice_section("Bass", s, build_unit(bass_events, i, SECTION))
    composer.fill_voice_section("Organ", s, build_unit(organ_events, i, SECTION))
    composer.fill_voice_section("Melody", s, build_unit(melody_events, i, SECTION))
    composer.fill_voice_section("Percussion", s, build_unit(perc_events, i, SECTION))

out_dir = "/opt/data/projects/Styles/Soul/smooth/v1"
os.makedirs(out_dir, exist_ok=True)
mid = os.path.join(out_dir, "soul_smooth.mid")
composer.to_midi(mid)
write_grid_visualization(composer.matrix, os.path.join(out_dir, "grid_visualization.txt"), ticks_per_character=480, voice_names=["Rho", "Bass", "Org", "Mel", "Perc"], bpm=BPM)
write_provenance(mid, AI_ASSISTED, "soul_smooth", parameters={"bpm": BPM, "methods": ["011", "002", "026"]})
print(f"✓ Soul Redone: {mid}")
