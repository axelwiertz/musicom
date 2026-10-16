# -*- coding: utf-8 -*-
"""Verify Recorder (GM74) constants work with musicom engine.

Renders a 1-bar recorder melody SOLO (no unison doubling) and validates
zero-drift, MIDI export, and FluidSynth WAV output via discover_soundfont().
"""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

# Import through the REGISTRY — proves registration
from instrument_registry import by_name

rec = by_name("recorder")
print(f"Recorder: name={rec.name!r} family={rec.family} "
      f"program={rec.midi_program} gm={rec.gm_name!r} "
      f"stem={rec.stem_label!r} sweet={rec.solo_range} "
      f"range={rec.range_min}–{rec.range_max}")
print(f"  A4 = {440.0 * 2.0 ** ((69 - 69) / 12.0):.1f} Hz")
print(f"  zones = {rec.zones}")
print(f"  art = {list(getattr(rec, 'articulations', {}))}")
print(f"  synth = {rec.synthesis}")
print(f"  reverb = {rec.reverb_tail}s pan = {rec.pan}")
print(f"  eq_body = {rec.eq_body}  eq_presence = {rec.eq_presence}  eq_air = {rec.eq_air}")

# Full engine test: UnitMatrixComposer — SOLO recorder, 1 voice
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("Recorder", program=rec.midi_program, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Recorder: sweet-spot melody (C5-E5-G5-C6-G5-E5-C5) on melodic channel
u = MusicUnit()
notes = [72, 76, 79, 84, 79, 76, 72]  # C5 E5 G5 C6 G5 E5 C5
for i, p in enumerate(notes):
    start = i * 240
    end = BAR if i == len(notes) - 1 else start + 200
    u.add_event(MusicEvent(p, 80, start, end))
# Pad to BAR (zero-drift invariant)
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/Woodwind/recorder/recorder_test.mid"
import os
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# Render SOLO via FluidSynth + discover_soundfont()
from _test.render_audio import render_midi_solo, spectral_buzz_check
wav = "/opt/data/projects/Instruments/Woodwind/recorder/recorder_test.wav"
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
for idx in [72, 73, 74, 75, 76]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Recorder stem -> {labels[rec.midi_program]!r}")
assert labels[rec.midi_program] == "Recorder", \
    f"stem label mismatch: {labels[rec.midi_program]!r}"
assert rec.stem_label == "Recorder"

# SF2 preset name check — read from FluidR3 phdr chunk
from sound.render.fluidsynth import discover_soundfont
sf2_path = discover_soundfont()
print(f"\nSoundFont: {sf2_path}")
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
sf2_name = preset_names.get((0, rec.midi_program), "MISSING")
print(f"SF2 preset {rec.midi_program} -> {sf2_name!r}")
# FluidR3 GM set: preset 74 = "Recorder" should match

# Full RenderPipeline stem render — recorder stem label on disk
out_dir = "/opt/data/projects/Instruments/Woodwind/recorder/stems"
from utilities.env import fluidsynth_bin as _fluid_bin
pipeline = RenderPipeline(fluidsynth_bin=_fluid_bin(), soundfont_path=sf2_path, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
import glob
stem_files = sorted(glob.glob(os.path.join(out_dir, "*.wav")))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    print(f"  {os.path.basename(f)} ({os.path.getsize(f)} bytes)")
assert any("Recorder" in f for f in stem_files), f"no Recorder stem in {stem_files}"
rec_stem = [f for f in stem_files if "Recorder" in f][0]
assert os.path.getsize(rec_stem) > 40, "empty Recorder stem"

# PhaseModSynth smoke test: pure tone
from sound.synthesis.phase_mod import PhaseModSynth
pm = PhaseModSynth(sample_rate=22050)
audio = pm.render_note(
    freq=440.0, duration=0.5,
    carrier_shape="sine", mod_shape="sine",
    mod_freq_ratio=1.0, mod_depth=1.5,
    attack=0.03, release=0.08
)
import numpy as np
peak = np.max(np.abs(audio))
print(f"\nPhaseModSynth recorder (440Hz, 0.5s): peak={peak:.3f}")
assert peak > 0, "phase mod recorder render silent"

print("\nALL CHECKS PASSED")