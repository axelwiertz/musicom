# -*- coding: utf-8 -*-
"""Verify Glockenspiel constants work with musicom engine (registry-backed, solo render)."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- Registration proof: import THROUGH the registry ---------------------
from instrument_registry import (
    by_name, by_program, registry_table, ALL_INSTRUMENTS, GLOCKENSPIEL
)

GL = by_name("glockenspiel")
print("Registry: by_name('glockenspiel') =", GL)
print("Registry: by_program(9) =", by_program(9))
assert GL.midi_program == 9
assert by_program(9).name == "Glockenspiel"
assert GLOCKENSPIEL.midi_program == 9
print("Registry: ALL_INSTRUMENTS count =", len(ALL_INSTRUMENTS))
table = registry_table()
assert "| Percussion | Glockenspiel | 9 |" in table, "glockenspiel row missing from registry_table()"
print("Registry row: | Percussion | Glockenspiel | 9 | 79-108 | ... OK")

# ---- Constants through the registry ---------------------------------------
MIDI_PROGRAM = GL.midi_program
GM_NAME = GL.gm_name
STEM_LABEL = GL.stem_label
SOLO_RANGE = GL.solo_range
SWEET_SPOT = GL.sweet_spot
ZONES = GL.zones
ARTICULATIONS = GL.articulations
SYNTHESIS = GL.synthesis
MODAL_PRESET = GL.modal_preset
KARPLUS_DEFAULTS = GL.karplus_defaults
from Percussion.glockenspiel.glockenspiel import GLOCKENSPIEL_MODES, midi_to_freq, FM_DEFAULTS
REVERB_TAIL = GL.reverb_tail
EQ_BODY = GL.eq_body
EQ_PRESENCE = GL.eq_presence
EQ_AIR = GL.eq_air
PAN = GL.pan

print(f"\nGlockenspiel: program={MIDI_PROGRAM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"range={GL.range_min}-{GL.range_max} sweet={SWEET_SPOT} solo={SOLO_RANGE}")
print(f"Glockenspiel: zones={ZONES}")
print(f"Glockenspiel: art={list(ARTICULATIONS)} synth={SYNTHESIS} modal={MODAL_PRESET!r}")
print(f"Glockenspiel: karplus={KARPLUS_DEFAULTS} fm={FM_DEFAULTS}")
print(f"Glockenspiel: G5={midi_to_freq(79):.1f}Hz C6={midi_to_freq(84):.1f}Hz "
      f"A6={midi_to_freq(93):.1f}Hz C7={midi_to_freq(96):.1f}Hz C8={midi_to_freq(108):.1f}Hz")

assert GL.in_range(79) and GL.in_range(108) and not GL.in_range(78)
assert not GL.in_range(109)
assert GL.in_sweet_spot(84) and GL.in_sweet_spot(96)

# ---- Engine test: UnitMatrixComposer (1 bar, 1 section) --------------------
# Voice stack: Glockenspiel solo (ch0). Context: ONE low bass note well below (ch1, GM33)
# NO unison doubling of identical pitches.
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Glockenspiel", program=MIDI_PROGRAM, channel=0)
comp.add_voice("Bass", program=33, channel=1)
comp.add_section("A", bars=1)

BAR = 1920

# Glockenspiel: crystalline melodic sparkle figure
# C6, E6, G6, C7, B6, G6, E6, C6 (sounding pitches: 84, 88, 91, 96, 95, 91, 88, 84)
# Last event ends flush at BAR (terminal landmark).
u = MusicUnit()
line = [84, 88, 91, 96, 95, 91, 88, 84]
for i, p in enumerate(line):
    start = i * 240
    end = BAR if i == len(line) - 1 else start + 220
    u.add_event(MusicEvent(p, 90, start, end))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

# Context: low bass C2 (36) — multiple octaves below glockenspiel
u = MusicUnit()
u.add_event(MusicEvent(36, 60, 0, BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/glockenspiel_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---- Render SOLO via discover_soundfont() (FluidR3 preferred) -------------
from _test.render_audio import render_midi
wav = "/opt/data/projects/Instruments/_test/glockenspiel_test.wav"

render_midi(midi_path, wav, solo=0)  # track 1 = Glockenspiel solo
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"

# ---- Stem label check against ACTUAL pipeline GM_PROGRAMS (0-indexed) -----
import inspect
import re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
for idx in [7, 8, 9, 10, 11, 12, 13]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Glockenspiel -> {labels[MIDI_PROGRAM]!r}")
assert labels[MIDI_PROGRAM] == "Glockenspiel", f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"
assert STEM_LABEL == "Glockenspiel"

# ---- SF2 preset name check (phdr chunk, resolved SoundFont) ---------------
from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
print(f"\nSF2: {sf2}")
import struct
with open(sf2, "rb") as f:
    data = f.read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
sf2_name = preset_names.get((0, MIDI_PROGRAM), "MISSING")
print(f"SF2 preset {MIDI_PROGRAM} -> {sf2_name!r}")
assert sf2_name == "Glockenspiel", f"SF2 preset mismatch: {sf2_name!r}"

# ---- Full RenderPipeline stem render — glockenspiel stem label on disk -----
stems_dir = "/opt/data/projects/Instruments/_test/stems_glockenspiel"
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, stems_dir)
stem_files = sorted(os.listdir(stems_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(stems_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Glockenspiel" in f for f in stem_files), f"no glockenspiel stem in {stem_files}"
gl_stem = [f for f in stem_files if "Glockenspiel" in f][0]
assert os.path.getsize(os.path.join(stems_dir, gl_stem)) > 40, "empty glockenspiel stem"

# ---- ModalSynth 'bell' stock preset and custom modes check -----------------
import numpy as np
from sound.synthesis.modal import ModalSynth
sr = 44100
ms = ModalSynth(sample_rate=sr)
bell_audio = ms.render_preset("bell", duration=2.0, excitation="impulse")
custom_audio = ms.render_custom(GLOCKENSPIEL_MODES, duration=2.0, excitation="impulse")
b_peak = np.max(np.abs(bell_audio))
c_peak = np.max(np.abs(custom_audio))
print(f"\nModalSynth bell preset: peak={b_peak:.3f}, len={len(bell_audio)}")
print(f"ModalSynth custom glock modes: peak={c_peak:.3f}, len={len(custom_audio)}")
assert b_peak > 0, "bell preset modal render silent"
assert c_peak > 0, "custom glockenspiel modal render silent"

# ---- Karplus-Strong fallback ring check -----------------------------------
from sound.synthesis.karplus_strong import karplus_strong
ks = karplus_strong(pitch=84, dur=2.0, vel=100, loop_gain=KARPLUS_DEFAULTS["loop_gain"])
ks_peak = np.max(np.abs(ks))
ks_tail = np.sqrt(np.mean(ks[int(0.8 * sr):int(1.2 * sr)] ** 2))
print(f"\nKarplus-Strong glockenspiel: peak={ks_peak:.3f}, tail_rms={ks_tail:.4f}")
assert ks_peak > 0, "KS render silent"
assert ks_tail > 0.001, "KS render decayed too quickly"

print("\nALL VERIFICATIONS PASSED!")
