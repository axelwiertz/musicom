# -*- coding: utf-8 -*-
"""Verify English Horn constants work with musicom engine (registry-backed, solo render)."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- Registration proof: import THROUGH the registry ---------------------
from instrument_registry import (
    by_name, by_program, registry_table, ALL_INSTRUMENTS, ENGLISH_HORN
)

EH = by_name("english horn")
print("Registry: by_name('english horn') =", EH)
print("Registry: by_program(69) =", by_program(69))
assert EH.midi_program == 69
assert by_program(69).name == "English Horn"
assert ENGLISH_HORN.midi_program == 69
print("Registry: ALL_INSTRUMENTS count =", len(ALL_INSTRUMENTS))
table = registry_table()
assert "| Woodwind | English Horn | 69 |" in table, "english horn row missing from registry_table()"
print("Registry row: | Woodwind | English Horn | 69 | 50–85 | ... OK")

# ---- Constants through the registry ---------------------------------------
MIDI_PROGRAM = EH.midi_program
GM_NAME = EH.gm_name
STEM_LABEL = EH.stem_label
SOLO_RANGE = EH.solo_range
SWEET_SPOT = EH.sweet_spot
ZONES = EH.zones
ARTICULATIONS = EH.articulations
SYNTHESIS = EH.synthesis
FM_DEFAULTS = EH.fm_defaults
from Woodwind.english_horn.english_horn import midi_to_freq
REVERB_TAIL = EH.reverb_tail
EQ_BODY = EH.eq_body
EQ_PRESENCE = EH.eq_presence
EQ_AIR = EH.eq_air
PAN = EH.pan

print(f"\nEnglish Horn: program={MIDI_PROGRAM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"range={EH.range_min}-{EH.range_max} sweet={SWEET_SPOT} solo={SOLO_RANGE}")
print(f"English Horn: zones={ZONES}")
print(f"English Horn: art={list(ARTICULATIONS)} synth={SYNTHESIS} fm={FM_DEFAULTS}")
print(f"English Horn: D3={midi_to_freq(50):.1f}Hz A3={midi_to_freq(57):.1f}Hz "
      f"C4={midi_to_freq(60):.1f}Hz A4={midi_to_freq(69):.1f}Hz "
      f"C5={midi_to_freq(72):.1f}Hz C#6={midi_to_freq(85):.1f}Hz")

assert EH.in_range(50) and EH.in_range(85) and not EH.in_range(49)
assert not EH.in_range(86)
assert EH.in_sweet_spot(57) and EH.in_sweet_spot(65) and EH.in_sweet_spot(72)

# ---- Engine test: UnitMatrixComposer (1 bar, 1 section) --------------------
# Voice stack: English Horn solo (ch0). Context: ONE low bass note well below (ch1, GM33)
# NO unison doubling of identical pitches.
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("English_Horn", program=MIDI_PROGRAM, channel=0)
comp.add_voice("Bass", program=33, channel=1)
comp.add_section("A", bars=1)

BAR = 1920

# English Horn: lyrical cantabile phrase in sweet spot (A3–C5)
# Melody: New World inspired pastoral theme [A3(57), C4(60), D4(62), F4(65), E4(64), D4(62), C4(60), A3(57)]
# Last event ends flush at BAR (terminal landmark).
u = MusicUnit()
line = [57, 60, 62, 65, 64, 62, 60, 57]
for i, p in enumerate(line):
    start = i * 240
    end = BAR if i == len(line) - 1 else start + 215
    u.add_event(MusicEvent(p, 82, start, end))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

# Context: low bass C1 (24) — 3 octaves below lowest melodic pitch
u = MusicUnit()
u.add_event(MusicEvent(24, 60, 0, BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/english_horn_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---- Render SOLO via discover_soundfont() (FluidR3 preferred) -------------
from _test.render_audio import render_midi, spectral_buzz_check

wav = "/opt/data/projects/Instruments/_test/english_horn_test.wav"

render_midi(midi_path, wav, solo=0)  # track 1 = English Horn solo
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok_buzz, rep_buzz = spectral_buzz_check(wav)
print(f"Spectral check: {rep_buzz}")

# ---- Stem label check against ACTUAL pipeline GM_PROGRAMS (0-indexed) -----
import inspect
import re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
for idx in [68, 69, 70, 71, 72]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  English Horn -> {labels[MIDI_PROGRAM]!r}")
assert labels[MIDI_PROGRAM] == "English Horn", f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"

# Render pipeline full stem check
pipeline = RenderPipeline()
stems_dir = "/opt/data/projects/Instruments/_test/stems_english_horn"
os.makedirs(stems_dir, exist_ok=True)
from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
stems = pipeline.render_stems(midi_path, stems_dir, soundfont=sf2)
print(f"Pipeline render_stems: {list(stems.keys())}")
assert "track00_English_Horn" in stems, f"expected track00_English_Horn, got {list(stems.keys())}"
print("Verification complete: ALL OK!")
