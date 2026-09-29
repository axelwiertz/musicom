# -*- coding: utf-8 -*-
"""Verify Music Box constants work with musicom engine.

Tests: registry load, UnitMatrixComposer zero-drift, MIDI export,
FluidSynth SOLO render via discover_soundfont(), spectral buzz check,
stem label match, and Music Box modal/KS preset smoke tests.
"""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

# Import through the REGISTRY (proves registration works)
from instrument_registry import MUSIC_BOX, by_name, by_program, ALL_INSTRUMENTS

print("=== Music Box Registry Verification ===")
print(f"MUSIC_BOX = {MUSIC_BOX}")
mb = by_name("music box")
print(f"by_name('music box') = {mb}")
mb2 = by_program(10)
print(f"by_program(10) = {mb2}")
print(f"MIDI_PROGRAM = {mb.midi_program} (should be 10)")
print(f"GM_NAME = {mb.gm_name!r} (should be 'Music Box')")
print(f"STEM_LABEL = {mb.stem_label!r}")
print(f"RANGE_MIN = {mb.range_min}, RANGE_MAX = {mb.range_max}")
print(f"SOLO_RANGE = {mb.solo_range}")
print(f"SWEET_SPOT = {mb.sweet_spot}")
print(f"SYNTHESIS = {mb.synthesis}")
print(f"MODAL_PRESET = {mb.modal_preset}")
print(f"REVERB_TAIL = {mb.reverb_tail}")
print(f"PAN = {mb.pan}")
print(f"in_range(60) = {mb.in_range(60)}")
print(f"in_range(96) = {mb.in_range(96)}")
print(f"in_range(48) = {mb.in_range(48)}")
print(f"in_sweet_spot(74) = {mb.in_sweet_spot(74)}")
print(f"in_sweet_spot(55) = {mb.in_sweet_spot(55)}")
assert mb.midi_program == 10, f"wrong program: {mb.midi_program}"
assert mb.gm_name == "Music Box"
assert mb.stem_label == "Music_Box"
assert mb.range_min == 60
assert mb.range_max == 96
print("All constants OK")

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

print("\n=== UnitMatrixComposer Test ===")
comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("MusicBox", program=MUSIC_BOX.midi_program, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Music Box: melodic percussion on channel 0 (NOT ch9) — sweet-spot lead line,
# single-note melody (music box is monophonic), end flush at BAR
u = MusicUnit()
# A simple C major scale: C5 D5 E5 F5 G5 A5 B5 C6
notes = [72, 74, 76, 77, 79, 81, 83, 84]
for i, p in enumerate(notes):
    start = i * 240
    end = BAR if i == len(notes) - 1 else start + 200
    u.add_event(MusicEvent(p, 82, start, end))
# zero-drift: if unit ends short, pad with terminal landmark
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"Zero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/music_box_test.mid"
import os
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# SOLO render via discover_soundfont() — NO unison doubling
print("\n=== FluidSynth SOLO Render ===")
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/music_box_test.wav"
render_midi(midi_path, wav, solo=0)  # track 1 = Music Box (first voice, index 0)
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# Stem label check against ACTUAL pipeline GM_PROGRAMS (0-indexed)
print("\n=== Stem Label Check ===")
import inspect
import re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
for idx in [9, 10, 11, 12]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Music Box (GM10) -> {labels[10]!r}")
assert labels[10] == "Music Box", f"stem label mismatch: {labels[10]!r}"
assert MUSIC_BOX.stem_label == "Music_Box"

# SF2 preset name for program 10 (verified from phdr chunk)
print("\n=== SF2 Preset Check ===")
from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
import struct
data = open(sf2, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off+20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
sf2_name = preset_names.get((0, 10), "MISSING")
print(f"SF2 preset 10 -> {sf2_name!r}")
assert sf2_name == "Music Box", f"SF2 preset mismatch: {sf2_name!r}"

# ModalSynth 'bell' preset smoke test: struck tine = fast exponential decay
print("\n=== ModalSynth Smoke Test ===")
from sound.synthesis.modal import ModalSynth
ms = ModalSynth(sample_rate=22050)
audio = ms.render_preset('bell', duration=0.5, excitation='impulse')
import numpy as np
peak = np.max(np.abs(audio))
tail_rms = np.sqrt(np.mean(audio[-2205:] ** 2))
tail_ratio = tail_rms / peak if peak > 0 else 1.0
print(f"ModalSynth 'bell': peak={peak:.3f} tail_rms/peak={tail_ratio:.3f}")
assert peak > 0, "modal bell render silent"
assert tail_ratio < 0.3, "bell decay NOT fast enough (music box = fast tine decay)"

print("\n=== ALL CHECKS PASSED ===")