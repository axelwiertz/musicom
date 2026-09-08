# -*- coding: utf-8 -*-
"""Verify Organ constants work with musicom engine."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from Keys.organ.organ import (
    MIDI_PROGRAM as ORG_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, ADDITIVE_HARMONICS, FM_DEFAULTS,
    REVERB_TAIL, EQ_BODY, EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)
from Keys.piano.piano import MIDI_PROGRAM as PIANO_PGM
from Strings.violin.violin import MIDI_PROGRAM as VIOLIN_PGM

print(f"Organ: program={ORG_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Organ: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS}")
print(f"Organ: harmonics_full={ADDITIVE_HARMONICS['full']} fm={FM_DEFAULTS}")
print(f"Organ: reverb={REVERB_TAIL}s eq={EQ_BODY},{EQ_PRESENCE},{EQ_AIR} pan={PAN}")
print(f"Organ: C2={midi_to_freq(36):.1f}Hz C3={midi_to_freq(48):.1f}Hz C4={midi_to_freq(60):.1f}Hz G5={midi_to_freq(79):.1f}Hz C7={midi_to_freq(96):.1f}Hz")
print(f"Context: piano_pgm={PIANO_PGM} violin_pgm={VIOLIN_PGM}")

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=3, num_sections=1)
comp.add_voice("Organ", program=ORG_PGM, channel=0)
comp.add_voice("Violin", program=VIOLIN_PGM, channel=1)
comp.add_voice("Piano", program=PIANO_PGM, channel=2)
comp.add_section("A", bars=1)

BAR = 1920

# Organ: pad/harmony role — sustained mid-zone chords + low-zone pedal,
# end flush at BAR (terminal landmark)
u = MusicUnit()
# pedal: C2 sustained whole bar
u.add_event(MusicEvent(36, 82, 0, BAR))
# mid-zone pad chords: C3+G3+E4, half notes, last ends flush at BAR
for i, p in enumerate([48, 55, 64]):
    u.add_event(MusicEvent(p, 70, 0, BAR if i == 2 else 960))
# zero-drift terminal landmark (belt + suspenders)
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

u = MusicUnit()
for i, p in enumerate([72, 74, 76, 77]):
    u.add_event(MusicEvent(p, 80, i * 480, BAR if i == 3 else i * 480 + 400))
comp.set_unit(1, 0, u)

u = MusicUnit()
for p in [60, 64, 67]:
    u.add_event(MusicEvent(p, 70, 0, BAR))
comp.set_unit(2, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/organ_test.mid"
import os
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

import subprocess
from _test.render_audio import render_midi, spectral_buzz_check
sf2_legacy = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
wav = "/opt/data/projects/Instruments/_test/organ_test.wav"
render_midi(midi_path, wav, solo=0)  # instrument SOLO (buzz fix)
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# RenderPipeline stem label check (GM_PROGRAMS list, 0-indexed)
import inspect
import re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem label (GM_PROGRAMS[{ORG_PGM}]): {labels[ORG_PGM]!r}")
assert labels[ORG_PGM] == "Church Organ", "stem label quirk!"
assert STEM_LABEL == "Church_Organ"

# SF2 preset name check (phdr chunk) for program 19
import struct
data = open(sf2_legacy, "rb").read()
pos = data.find(b"pdta")
pdta_off = pos - 8
pdta_size = struct.unpack("<I", data[pdta_off + 4:pdta_off + 8])[0]
phdr_pos = data.find(b"phdr", pdta_off, pdta_off + pdta_size)
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
presets = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    presets[(bank, preset_num)] = name
sf2_name = presets.get((0, ORG_PGM), "MISSING")
print(f"SF2 preset {ORG_PGM} -> {sf2_name!r}")
assert sf2_name == "Church Organ", f"SF2 preset mismatch: {sf2_name!r}"

# Full RenderPipeline stem render — organ stem label on disk
out_dir = "/opt/data/projects/Instruments/_test/stems_organ"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2_legacy, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Church_Organ" in f for f in stem_files), f"no Church_Organ stem in {stem_files}"
org_stem = [f for f in stem_files if "Church_Organ" in f][0]
assert os.path.getsize(os.path.join(out_dir, org_stem)) > 40, "empty Organ stem"

# Additive engine smoke: drawbar harmonic mix, sustain level 1.0
# (engine asserts factor sum == 1.0 — normalize the drawbar mix here;
#  the raw mix in organ.py is the human-readable registration)
from sound.synthesis.additive import SoundWave
sw = SoundWave(sample_rate=22050, duration=0.5, frequency=midi_to_freq(60))
_f = [x / sum(ADDITIVE_HARMONICS["full"]) for x in ADDITIVE_HARMONICS["full"]]
sw.apply_overtones(_f)
sw.get_adsr_weights(length=[0.01, 0.0, 0.95, 0.04], decay=[0.0, 0.0, 0.0, 0.5],
                    sustain_level=1.0)
import numpy as np
peak = np.max(np.abs(sw.fundamental))
print(f"\nAdditive engine: C4 organ note peak={peak:.1f} (harmonic mix full)")
assert peak > 0, "additive organ render silent"

print("\nALL CHECKS PASSED")
