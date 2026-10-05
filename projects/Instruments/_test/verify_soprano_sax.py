# -*- coding: utf-8 -*-
"""Verify Soprano Saxophone constants work with musicom engine.

Solo render (NO unison doubling): one voice, one track = clean spectral check.

Pattern from verify_marimba.py but adapted for SOLO-only render as required
by the 2026-09-01 fix (no clarinet/piano unison doubling → comb-filtering).
"""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from Woodwind.soprano_sax.soprano_sax import (
    MIDI_PROGRAM as SAX_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, FM_DEFAULTS, REVERB_TAIL, EQ_BODY,
    EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)

print(f"Soprano Sax: program={SAX_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Soprano Sax: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Soprano Sax: A4={midi_to_freq(69):.1f}Hz C5={midi_to_freq(72):.1f}Hz C6={midi_to_freq(84):.1f}Hz")
print(f"FM defaults: {FM_DEFAULTS}")

# Full engine test: UnitMatrixComposer with instrument constants
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("SopranoSax", program=SAX_PGM, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Soprano Sax: SOLO melodic lead on channel 0
# Sweet-spot line in G4-G5 (SOPRANO_SAX sweet spot is 67-79)
# Play a bright ascending line through the money register, end at BAR
u = MusicUnit()
notes = [67, 71, 74, 79, 83, 86, 88]   # G4–F6 climbing, ends in altissimo territory
for i, p in enumerate(notes):
    start = i * 240
    end = BAR if i == len(notes) - 1 else i * 240 + 200
    u.add_event(MusicEvent(p, 85, start, end))
# Zero-drift: terminal landmark padded to BAR (drum/percussion rule)
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/soprano_sax_test.mid"
import os
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# Render SOLO via discover_soundfont() (FluidR3 preferred)
from _test.render_audio import render_midi_solo, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/soprano_sax_test.wav"
render_midi_solo(midi_path, wav, instrument_track=0)
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
for idx in [64, 65, 66, 67]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Soprano Sax -> {labels[SAX_PGM]!r}")
label_expected = "Soprano_Sax"
assert labels[SAX_PGM] == "Soprano Sax", f"stem label mismatch: {labels[SAX_PGM]!r}"
assert STEM_LABEL == label_expected, f"STEM_LABEL mismatch: {STEM_LABEL!r} != {label_expected!r}"

# SF2 preset name check via FluidR3
from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
data = open(sf2, "rb").read()
phdr_pos = data.find(b"phdr")
if phdr_pos >= 0:
    import struct
    phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
    preset_names = {}
    for i in range(phdr_size // 38):
        off = phdr_pos + 8 + i * 38
        name = data[off:off+20].split(b"\x00")[0].decode("latin1")
        preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
        preset_names[(bank, preset_num)] = name
    sf2_name = preset_names.get((0, SAX_PGM), "MISSING")
    print(f"SF2 preset {SAX_PGM} -> {sf2_name!r}")

print("\nALL CHECKS PASSED")