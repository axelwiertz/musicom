# -*- coding: utf-8 -*-
"""Verify Piccolo constants work with musicom engine (registry-backed, solo render)."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- Registration proof: import THROUGH the registry ---------------------
from instrument_registry import (
    by_name, by_program, registry_table, ALL_INSTRUMENTS, PICCOLO
)

PIC = by_name("piccolo")
print("Registry: by_name('piccolo') =", PIC)
print("Registry: by_program(72) =", by_program(72))
assert PIC.midi_program == 72
assert by_program(72).name == "Piccolo"
assert PICCOLO.midi_program == 72
print("Registry: ALL_INSTRUMENTS count =", len(ALL_INSTRUMENTS))
table = registry_table()
assert "| Woodwind | Piccolo | 72 |" in table, "piccolo row missing from registry_table()"
print("Registry row: | Woodwind | Piccolo | 72 | 72-108 | ... OK")

# ---- Constants through the registry ---------------------------------------
MIDI_PROGRAM = PIC.midi_program
GM_NAME = PIC.gm_name
STEM_LABEL = PIC.stem_label
SOLO_RANGE = PIC.solo_range
SWEET_SPOT = PIC.sweet_spot
ZONES = PIC.zones
ARTICULATIONS = PIC.articulations
SYNTHESIS = PIC.synthesis
FM_DEFAULTS = PIC.fm_defaults
from Woodwind.piccolo.piccolo import AIR_PIPE_DEFAULTS, midi_to_freq
REVERB_TAIL = PIC.reverb_tail
EQ_BODY = PIC.eq_body
EQ_PRESENCE = PIC.eq_presence
EQ_AIR = PIC.eq_air
PAN = PIC.pan

print(f"\nPiccolo: program={MIDI_PROGRAM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"range={PIC.range_min}-{PIC.range_max} sweet={SWEET_SPOT} solo={SOLO_RANGE}")
print(f"Piccolo: zones={ZONES}")
print(f"Piccolo: art={list(ARTICULATIONS)} synth={SYNTHESIS}")
print(f"Piccolo: fm={FM_DEFAULTS} air_pipe={AIR_PIPE_DEFAULTS}")
print(f"Piccolo: C5={midi_to_freq(72):.1f}Hz D5={midi_to_freq(74):.1f}Hz "
      f"C6={midi_to_freq(84):.1f}Hz A6={midi_to_freq(93):.1f}Hz "
      f"C7={midi_to_freq(96):.1f}Hz C8={midi_to_freq(108):.1f}Hz")

assert PIC.in_range(72) and PIC.in_range(108) and not PIC.in_range(71)
assert not PIC.in_range(109)
assert PIC.in_sweet_spot(84) and PIC.in_sweet_spot(96)

# ---- Engine test: UnitMatrixComposer (1 bar, 1 section) --------------------
# Voice stack: Piccolo solo (ch0). Context: ONE low bass note well below (ch1, GM33)
# NO unison doubling of identical pitches.
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Piccolo", program=MIDI_PROGRAM, channel=0)
comp.add_voice("Bass", program=33, channel=1)
comp.add_section("A", bars=1)

BAR = 1920

# Piccolo: rapid virtuosic orchestral woodwind line in sweet spot (C6–C7)
# Notes: C6 (84), E6 (88), G6 (91), C7 (96), B6 (95), G6 (91), E6 (88), D6 (86)
# Last event ends flush at BAR (terminal landmark).
u = MusicUnit()
line = [84, 88, 91, 96, 95, 91, 88, 86]
for i, p in enumerate(line):
    start = i * 240
    end = BAR if i == len(line) - 1 else start + 210
    u.add_event(MusicEvent(p, 85, start, end))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

# Context: low bass C2 (36) — 4 octaves below piccolo
u = MusicUnit()
u.add_event(MusicEvent(36, 60, 0, BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/piccolo_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---- Render SOLO via discover_soundfont() (FluidR3 preferred) -------------
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/piccolo_test.wav"

render_midi(midi_path, wav, solo=0)  # track 1 = Piccolo solo
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
for idx in [70, 71, 72, 73, 74, 75]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Piccolo -> {labels[MIDI_PROGRAM]!r}")
assert labels[MIDI_PROGRAM] == "Piccolo", f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"
assert STEM_LABEL == "Piccolo"

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
assert sf2_name == "Piccolo", f"SF2 preset mismatch: {sf2_name!r}"

# ---- Full RenderPipeline stem render — piccolo stem label on disk ---------
stems_dir = "/opt/data/projects/Instruments/_test/stems_piccolo"
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, stems_dir)
stem_files = sorted(os.listdir(stems_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(stems_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Piccolo" in f for f in stem_files), f"no piccolo stem in {stem_files}"
pic_stem = [f for f in stem_files if "Piccolo" in f][0]
assert os.path.getsize(os.path.join(stems_dir, pic_stem)) > 40, "empty piccolo stem"

# ---- Synthesis engine test: PhaseModSynth and AirPipe ---------------------
import numpy as np
from sound.synthesis.phase_mod import PhaseModSynth
pms = PhaseModSynth(sample_rate=44100)
pm_audio = pms.render_note(freq=midi_to_freq(84), duration=1.0,
                           carrier_shape=FM_DEFAULTS["carrier_shape"],
                           mod_shape=FM_DEFAULTS["mod_shape"],
                           mod_freq_ratio=FM_DEFAULTS["mod_freq_ratio"],
                           mod_depth=FM_DEFAULTS["mod_depth"],
                           attack=FM_DEFAULTS["attack"],
                           release=FM_DEFAULTS["release"])
pm_peak = np.max(np.abs(pm_audio))
print(f"\nPhaseModSynth piccolo C6: peak={pm_peak:.3f}, len={len(pm_audio)}")
assert pm_peak > 0, "PhaseModSynth render silent"

from sound.synthesis.air_pipe import AirPipe
ap = AirPipe(midi_note=84, pressure=AIR_PIPE_DEFAULTS["pressure"],
             stopped=AIR_PIPE_DEFAULTS["stopped"],
             length_scale=AIR_PIPE_DEFAULTS["length_scale"])
print(f"AirPipe piccolo C6: length={ap.length*100:.1f} cm, radius={ap.radius*1000:.1f} mm, modes={len(ap.mode_freqs())}")
print(f"AirPipe mode frequencies (Hz): {[round(float(f), 1) for f in ap.mode_freqs()[:4]]}")

print("\nALL VERIFICATIONS PASSED!")
