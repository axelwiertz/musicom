# -*- coding: utf-8 -*-
"""Verify Whistle constants work with musicom engine.

Solo render — no unison doubling (comb-filtering buzz rule).
"""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

# Import directly from whistle module (for unit-level const tests)
from Woodwind.whistle.whistle import (
    MIDI_PROGRAM as WH_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, REVERB_TAIL, EQ_BODY,
    EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)
# Import through registry to prove registration
from instrument_registry import WHISTLE, ALL_INSTRUMENTS, by_name, by_program

print(f"Whistle: program={WH_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Whistle: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Whistle: D4={midi_to_freq(62):.1f}Hz G4={midi_to_freq(67):.1f}Hz C5={midi_to_freq(72):.1f}Hz D6={midi_to_freq(86):.1f}Hz A6={midi_to_freq(93):.1f}Hz")

# Prove registry registration
print(f"Registry: WHISTLE.program={WHISTLE.midi_program} WHISTLE.name={WHISTLE.name!r}")
print(f"Registry: by_name('whistle') -> {by_name('whistle').name}")
print(f"Registry: by_program(78) -> {by_program(78).name}")
assert WHISTLE.midi_program == 78
assert by_name("whistle").midi_program == 78
assert by_program(78).midi_program == 78

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)  # SOLO — one voice only
comp.add_voice("Whistle", program=WH_PGM, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Whistle: monophonic folk melody line on channel 0, sweet spot G4-D6
# A simple ascending jig-like line, end flush at BAR
u = MusicUnit()
notes = [67, 69, 71, 72, 74, 76, 78, 79]  # G4-A4-B4-C5-D5-E5-F5-G5
for i, p in enumerate(notes):
    start = i * 240
    end = start + 200 if i < len(notes) - 1 else BAR
    u.add_event(MusicEvent(p, 80, start, end))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/whistle_test.mid"
import os
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# Now use the shared audio render utilities
sys.path.insert(0, "/opt/data/projects/Instruments/_test")
from _test.render_audio import render_midi, spectral_buzz_check
from sound.render.fluidsynth import discover_soundfont

wav = "/opt/data/projects/Instruments/_test/whistle_test.wav"
render_midi(midi_path, wav, solo=0)  # track 1 = Whistle (only voice)
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# Stem label check against ACTUAL pipeline GM_PROGRAMS (0-indexed)
import inspect
import re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
print(f"  Whistle (GM{WH_PGM}) -> {labels[WH_PGM]!r}")
assert labels[WH_PGM] == "Whistle", f"stem label mismatch: {labels[WH_PGM]!r}"
assert STEM_LABEL == "Whistle"

# FluidSynth SF2 preset 78 (Whistle) phdr check
sf2_path = discover_soundfont()
print(f"\nSoundFont: {sf2_path}")
import struct
data = open(sf2_path, "rb").read()
phdr_pos = data.find(b"phdr")
if phdr_pos >= 0:
    phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
    preset_names = {}
    for i in range(phdr_size // 38):
        off = phdr_pos + 8 + i * 38
        name = data[off:off+20].split(b"\x00")[0].decode("latin1")
        preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
        preset_names[(bank, preset_num)] = name
    sf2_name = preset_names.get((0, WH_PGM), "MISSING")
    print(f"SF2 preset {WH_PGM} -> {sf2_name!r}")
    assert sf2_name == "Whistle", f"SF2 preset mismatch: {sf2_name!r}"

# RenderPipeline stem render for complete verification
fluidsynth_bin = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
out_dir = "/opt/data/projects/Instruments/_test/stems_whistle"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth_bin, soundfont_path=sf2_path, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Whistle" in f for f in stem_files), f"no Whistle stem in {stem_files}"
wh_stem = [f for f in stem_files if "Whistle" in f][0]
assert os.path.getsize(os.path.join(out_dir, wh_stem)) > 40, "empty Whistle stem"

# PhaseModSynth whistle preset smoke test: open-tube flue tone
from sound.synthesis.phase_mod import PhaseModSynth
pm = PhaseModSynth(sample_rate=22050)
audio = pm.render_note(
    freq=midi_to_freq(72),  # C5 = 523.25 Hz
    duration=0.5,
    carrier_shape="sine",
    mod_shape="sine",
    mod_freq_ratio=1.0,
    mod_depth=1.5,
    attack=0.04,
    release=0.10,
)
import numpy as np
peak = np.max(np.abs(audio))
assert peak > 0, "phase_mod whistle render silent"
print(f"\nPhaseModSynth whistle C5: peak={peak:.3f} audio_len={len(audio)}")

print("\nALL CHECKS PASSED")