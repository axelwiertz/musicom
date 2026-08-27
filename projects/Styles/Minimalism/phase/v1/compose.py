#!/usr/bin/env python3
"""Minimalism Phase-Shifting — Method 026 (DPSM) + 032 (Isorhythmic)"""

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

TPB, BPM, BPB = 480, 120, 4
BAR, SECTION = TPB * BPB, TPB * BPB * 16
composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
composer.create_matrix(num_voices=4, num_sections=2)
composer.add_voice("Marimba1", program=12, channel=0)
composer.add_voice("Marimba2", program=12, channel=1)
composer.add_voice("Piano", program=MidiInstrument.PIANO, channel=2)
composer.add_voice("Strings", program=MidiInstrument.STRING_ENSEMBLE, channel=3)
composer.add_section("A", bars=16); composer.add_section("B", bars=16)

base = [60, 64, 67, 72, 67, 64, 60, 55, 60, 64, 67, 72, 67, 64, 60, 55]
marimba1_events, marimba2_events = [], []
for b in range(32):
    ph = int(b * 0.0625 * BAR)
    for i, p in enumerate(base):
        t1 = b * BAR + i * (BAR // 16)
        t2 = t1 + ph
        if t2 >= (b + 1) * BAR: t2 -= BAR
        marimba1_events.append(MusicEvent(pitch=p, volume=75, start_tick=t1, end_tick=t1+BAR//16-20))
        marimba2_events.append(MusicEvent(pitch=p, volume=75, start_tick=t2, end_tick=t2+BAR//16-20))

talea, color = [1, 0, 1, 1, 0, 1, 0, 1], [48, 52, 55, 60, 64, 67, 72, 67]
piano_events, strings_events = [], []
ti_p, ci_p = 0, 0
for b in range(32):
    for st in range(16):
        t = b * BAR + st * (BAR // 16)
        if talea[ti_p % len(talea)] == 1:
            piano_events.append(MusicEvent(pitch=color[ci_p%len(color)], volume=80, start_tick=t, end_tick=t+BAR//16-20))
            ci_p += 1
        ti_p += 1
    chord = [[48, 55, 60], [50, 57, 62]][(b // 4) % 2]
    for n in chord: strings_events.append(MusicEvent(pitch=n, volume=65, start_tick=b*BAR, end_tick=(b+1)*BAR))

for i, s in enumerate(["A", "B"]):
    composer.fill_voice_section("Marimba1", s, build_unit(marimba1_events, i, SECTION))
    composer.fill_voice_section("Marimba2", s, build_unit(marimba2_events, i, SECTION))
    composer.fill_voice_section("Piano", s, build_unit(piano_events, i, SECTION))
    composer.fill_voice_section("Strings", s, build_unit(strings_events, i, SECTION))

out_dir = "/opt/data/projects/Styles/Minimalism/phase/v1"
os.makedirs(out_dir, exist_ok=True)
mid = os.path.join(out_dir, "minimalism_phase.mid")
composer.to_midi(mid)
write_grid_visualization(composer.matrix, os.path.join(out_dir, "grid_visualization.txt"), ticks_per_character=480, voice_names=["M1", "M2", "Piano", "Strings"], bpm=BPM)
write_provenance(mid, AI_ASSISTED, "minimalism_phase", parameters={"bpm": BPM, "methods": ["026", "032"]})
print(f"✓ Minimalism Redone: {mid}")
