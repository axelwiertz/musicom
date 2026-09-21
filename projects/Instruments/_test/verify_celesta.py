# -*- coding: utf-8 -*-
"""Verify Celesta constants work with musicom engine (registry-backed, solo render)."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- Registration proof: import THROUGH the registry ---------------------
from instrument_registry import (
    by_name, by_program, registry_table, ALL_INSTRUMENTS, CELESTA
)

CEL = by_name("celesta")
print("Registry: by_name('celesta') =", CEL)
print("Registry: by_program(8) =", by_program(8))
assert CEL.midi_program == 8
assert by_program(8).name == "Celesta"
assert CELESTA.midi_program == 8
print("Registry: ALL_INSTRUMENTS count =", len(ALL_INSTRUMENTS))
table = registry_table()
assert "| Keys | Celesta | 8 |" in table, "celesta row missing from registry_table()"
print("Registry row: | Keys | Celesta | 8 | 48–108 | ... OK")

# ---- Constants through the registry ---------------------------------------
MIDI_PROGRAM = CEL.midi_program
GM_NAME = CEL.gm_name
STEM_LABEL = CEL.stem_label
SOLO_RANGE = CEL.solo_range
SWEET_SPOT = CEL.sweet_spot
ZONES = CEL.zones
ARTICULATIONS = CEL.articulations
SYNTHESIS = CEL.synthesis
MODAL_PRESET = CEL.modal_preset
from Keys.celesta.celesta import CELESTA_MODES, midi_to_freq
KARPLUS_DEFAULTS = CEL.karplus_defaults
FM_DEFAULTS = CEL.fm_defaults
REVERB_TAIL = CEL.reverb_tail
EQ_BODY = CEL.eq_body
EQ_PRESENCE = CEL.eq_presence
EQ_AIR = CEL.eq_air
PAN = CEL.pan

print(f"\nCelesta: program={MIDI_PROGRAM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"range={CEL.range_min}-{CEL.range_max} sweet={SWEET_SPOT} solo={SOLO_RANGE}")
print(f"Celesta: zones={ZONES}")
print(f"Celesta: art={list(ARTICULATIONS)} synth={SYNTHESIS} modal_preset={MODAL_PRESET}")
print(f"Celesta: modes={CELESTA_MODES} karplus={KARPLUS_DEFAULTS} fm={FM_DEFAULTS}")
print(f"Celesta: C3={midi_to_freq(48):.1f}Hz C4={midi_to_freq(60):.1f}Hz "
      f"C5={midi_to_freq(72):.1f}Hz C6={midi_to_freq(84):.1f}Hz "
      f"C7={midi_to_freq(96):.1f}Hz C8={midi_to_freq(108):.1f}Hz")

assert CEL.in_range(48) and CEL.in_range(108) and not CEL.in_range(47)
assert not CEL.in_range(109)
assert CEL.in_sweet_spot(72) and CEL.in_sweet_spot(84) and CEL.in_sweet_spot(96)

# ---- Engine test: UnitMatrixComposer (1 bar, 1 section) --------------------
# Voice stack: Celesta solo (ch0). Context: ONE low bass note well below (ch1, GM33)
# NO unison doubling of identical pitches.
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Celesta", program=MIDI_PROGRAM, channel=0)
comp.add_voice("Bass", program=33, channel=1)
comp.add_section("A", bars=1)

BAR = 1920

# Celesta: sparkling arpeggio arabesque in sweet spot (C5–C7)
# Notes: G5 (79), C6 (84), E6 (88), G6 (91), C7 (96), B6 (95), G6 (91), E6 (88)
# Last event ends flush at BAR (terminal landmark).
u = MusicUnit()
line = [79, 84, 88, 91, 96, 95, 91, 88]
for i, p in enumerate(line):
    start = i * 240
    end = BAR if i == len(line) - 1 else start + 210
    u.add_event(MusicEvent(p, 80, start, end))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

# Context: low bass C1 (24) — 4.5 octaves below celesta melody
u = MusicUnit()
u.add_event(MusicEvent(24, 60, 0, BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/celesta_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---- Render SOLO via discover_soundfont() (FluidR3 preferred) -------------
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/celesta_test.wav"

render_midi(midi_path, wav, solo=0)  # track 1 = Celesta solo
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
for idx in [6, 7, 8, 9, 10]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Celesta -> {labels[MIDI_PROGRAM]!r}")
assert labels[MIDI_PROGRAM] == "Celesta", f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"
assert STEM_LABEL == "Celesta"

# Render pipeline full stem check
pipeline = RenderPipeline()
stems_dir = "/opt/data/projects/Instruments/_test/stems_celesta"
os.makedirs(stems_dir, exist_ok=True)
from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
stems = pipeline.render_stems(midi_path, stems_dir, soundfont=sf2)
print(f"Pipeline render_stems: {list(stems.keys())}")
assert "track00_Celesta" in stems, f"expected track00_Celesta, got {list(stems.keys())}"
print("Verification complete: ALL OK!")
