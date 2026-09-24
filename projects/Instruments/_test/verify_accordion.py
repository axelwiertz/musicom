# -*- coding: utf-8 -*-
"""Verify Accordion constants work with musicom engine.

Solo render via FluidSynth (discover_soundfont → FluidR3_GM.sf2).
No unison doubling — accordion is the only melodic voice.
"""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from Keys.accordion.accordion import (
    MIDI_PROGRAM as ACC_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, FM_DEFAULTS, REVERB_TAIL, EQ_BODY,
    EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)

print(f"Accordion: program={ACC_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Accordion: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} fm_depth={FM_DEFAULTS['mod_depth']} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Accordion: C2={midi_to_freq(36):.1f}Hz C4={midi_to_freq(60):.1f}Hz C6={midi_to_freq(84):.1f}Hz C7={midi_to_freq(96):.1f}Hz")

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("Accordion", program=ACC_PGM, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Accordion: melodic/chordal instrument on channel 0 (NOT ch9) — sweet-spot
# arpeggiated line, end flush at BAR (terminal landmark).
# Solo instrument — no unison doubling, no second melodic patch.
u = MusicUnit()
for i, p in enumerate([60, 64, 67, 72, 79, 76, 72]):
    u.add_event(MusicEvent(p, 78, i * 240, BAR if i == 6 else i * 240 + 200))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/accordion_test.mid"
import os
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# Render SOLO via discover_soundfont() (FluidR3_GM.sf2 preferred)
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/accordion_test.wav"
render_midi(midi_path, wav, solo=0)  # track 1 = Accordion (first voice)
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
for idx in [20, 21, 22, 23]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Accordion -> {labels[ACC_PGM]!r}")
assert labels[ACC_PGM] == "Accordion", f"stem label mismatch: {labels[ACC_PGM]!r}"
assert STEM_LABEL == "Accordion"

# SF2 preset name for program 21 (verified from phdr chunk)
sf2 = None
from sound.render.fluidsynth import discover_soundfont
sf2_path = discover_soundfont()
if sf2_path:
    import struct
    data = open(sf2_path, "rb").read()
    phdr_pos = data.find(b"phdr")
    phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
    preset_names = {}
    for i in range(phdr_size // 38):
        off = phdr_pos + 8 + i * 38
        name = data[off:off+20].split(b"\x00")[0].decode("latin1")
        preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
        preset_names[(bank, preset_num)] = name
    sf2_name = preset_names.get((0, ACC_PGM), "MISSING")
    print(f"SF2 preset {ACC_PGM} -> {sf2_name!r}")
    # FluidR3 preset 21 = "Accordian" (archaic spelling — cosmetic only,
    # no routing impact; the pipeline uses "Accordion")

# Full RenderPipeline stem render — accordion stem label on disk
out_dir = "/opt/data/projects/Instruments/_test/stems_accordion"
fluidsynth_bin = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth_bin, soundfont_path=sf2_path, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Accordion" in f for f in stem_files), f"no Accordion stem in {stem_files}"
acc_stem = [f for f in stem_files if "Accordion" in f][0]
assert os.path.getsize(os.path.join(out_dir, acc_stem)) > 40, "empty Accordion stem"

# PhaseModSynth smoke test: free-reed continuous tone
from sound.synthesis.phase_mod import PhaseModSynth
pms = PhaseModSynth(sample_rate=22050)
freq = midi_to_freq(69)  # A4 = 440 Hz
audio = pms.render_note(freq=freq, duration=0.5, carrier_shape='saw',
                        mod_freq_ratio=1.0, mod_depth=3.2, attack=0.015, release=0.05)
import numpy as np
peak = np.max(np.abs(audio))
late_rms = np.sqrt(np.mean(audio[-2205:] ** 2))  # last 100 ms
late_ratio = late_rms / peak if peak > 0 else 1.0
print(f"\nPhaseModSynth accordion (A4={freq:.1f}Hz): peak={peak:.3f} late_rms/peak={late_ratio:.3f}")
assert peak > 0, "phase_mod accordion render silent"
# Free reed sustains — late tail should be significant
assert late_ratio > 0.01, "accordion tail collapsed (reed not sustaining)"

print("\nALL CHECKS PASSED")
