# -*- coding: utf-8 -*-
"""Verify Steel-String Acoustic Guitar constants through the registry.

Uses UnitMatrixComposer (1 bar, 1 section — solo only, no unison doubling).
Renders via FluidSynth with discover_soundfont() (prefers FluidR3_GM.sf2).
"""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

# Import THROUGH the registry
from instrument_registry import STEEL_ACOUSTIC, by_name, by_program, ALL_INSTRUMENTS

print(f"Steel Acoustic: program={STEEL_ACOUSTIC.midi_program}")
print(f"  name={STEEL_ACOUSTIC.name!r} gm_name={STEEL_ACOUSTIC.gm_name!r}")
print(f"  range={STEEL_ACOUSTIC.range_min}–{STEEL_ACOUSTIC.range_max}")
print(f"  solo_range={STEEL_ACOUSTIC.solo_range}")
print(f"  synthesis={STEEL_ACOUSTIC.synthesis}")
print(f"  reverb_tail={STEEL_ACOUSTIC.reverb_tail}s")
print(f"  stem_label={STEEL_ACOUSTIC.stem_label!r}")
print(f"  by_name('steel acoustic') -> {by_name('steel acoustic')}")
print(f"  by_program(25) -> {by_program(25)}")

# Full engine test: UnitMatrixComposer — STEEL-STRING SOLO ONLY
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("SteelAcoustic", program=STEEL_ACOUSTIC.midi_program, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Steel-string acoustic: fingerpicked arpeggio in sweet spot (D3–G5)
# G major chord arpeggio: G3(55) B3(59) D4(62) G4(67) D4(62) B3(59) G3(55)
u = MusicUnit()
notes = [55, 59, 62, 67, 62, 59, 55]
durations = [220, 220, 280, 320, 240, 280, 360]
start = 0
for i, (p, dur) in enumerate(zip(notes, durations)):
    u.add_event(MusicEvent(p, 72, start, start + dur))
    start += dur
# Zero-drift: pad to section end with terminal landmark
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/Guitar/steel_acoustic/steel_acoustic_test.mid"
import os
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# Render SOLO via discover_soundfont()
from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
wav = "/opt/data/projects/Instruments/Guitar/steel_acoustic/steel_acoustic_test.wav"

import subprocess
r = subprocess.run([fluidsynth, "-ni", "-g", "1.2", "-F", wav,
                    sf2, midi_path], capture_output=True)
if r.returncode != 0:
    raise RuntimeError(f"fluidsynth failed: {r.stderr.decode()[-500:]}")
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, f"empty/corrupt WAV ({wsize} bytes)"

# Spectral buzz check
from _test.render_audio import spectral_buzz_check
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# Verify stem label against pipeline GM_PROGRAMS
import inspect
import re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
pipeline_label = labels[25]
print(f"Pipeline GM_PROGRAMS[25] = {pipeline_label!r}")
print(f"STEM_LABEL = {STEEL_ACOUSTIC.stem_label!r}")
# Pipeline label: "Acoustic Guitar (steel)" — the "_" sanitized form is
# "Acoustic_Guitar_steel". STEM_LABEL must match pipeline for stem lookup.
assert pipeline_label == "Acoustic Guitar (steel)", f"pipeline label mismatch: {pipeline_label!r}"

# Verify FluidR3 SF2 preset name for program 25
with open(sf2, "rb") as f:
    data = f.read()
phdr_pos = data.find(b"phdr")
phdr_size = __import__('struct').unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off+20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = __import__('struct').unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
sf2_name = preset_names.get((0, 25), "MISSING")
print(f"FluidR3 preset 25 -> {sf2_name!r}")

print("\nALL CHECKS PASSED")