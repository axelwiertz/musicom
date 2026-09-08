# -*- coding: utf-8 -*-
"""Verify Sitar constants work with musicom engine (registry-backed, solo render)."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- Registration proof: import THROUGH the registry ---------------------
from instrument_registry import (
    by_name, by_program, registry_table, ALL_INSTRUMENTS,
)
SITAR = by_name("sitar")
print("Registry: by_name('sitar') =", SITAR)
print("Registry: by_program(104) =", by_program(104))
assert SITAR.midi_program == 104
assert by_program(104).name == "Sitar"
print("Registry: ALL_INSTRUMENTS count =", len(ALL_INSTRUMENTS))
print("Registry table:\n" + registry_table())

# ---- Constants through the registry ---------------------------------------
MIDI_PROGRAM = SITAR.midi_program
GM_NAME = SITAR.gm_name
STEM_LABEL = SITAR.stem_label
SOLO_RANGE = SITAR.solo_range
SWEET_SPOT = SITAR.sweet_spot
ZONES = SITAR.zones
ARTICULATIONS = SITAR.articulations
SYNTHESIS = SITAR.synthesis
KARPLUS_DEFAULTS = SITAR.karplus_defaults
FM_DEFAULTS = SITAR.fm_defaults
REVERB_TAIL = SITAR.reverb_tail
EQ_BODY = SITAR.eq_body
EQ_PRESENCE = SITAR.eq_presence
EQ_AIR = SITAR.eq_air
PAN = SITAR.pan

print(f"\nSitar: program={MIDI_PROGRAM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"range={SITAR.range_min}-{SITAR.range_max} sweet={SWEET_SPOT} "
      f"solo={SOLO_RANGE}")
print(f"Sitar: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"karplus={KARPLUS_DEFAULTS} fm={FM_DEFAULTS}")
print(f"Sitar: reverb={REVERB_TAIL}s eq={EQ_BODY},{EQ_PRESENCE},{EQ_AIR} pan={PAN}")
from World.sitar.sitar import midi_to_freq
print(f"Sitar: G3={midi_to_freq(55):.1f}Hz C4={midi_to_freq(60):.1f}Hz "
      f"A4={midi_to_freq(69):.1f}Hz C6={midi_to_freq(84):.1f}Hz "
      f"C7={midi_to_freq(96):.1f}Hz")
assert SITAR.in_range(55) and SITAR.in_range(96) and not SITAR.in_range(54)
assert SITAR.in_sweet_spot(69)

# ---- Engine test: UnitMatrixComposer (1 bar, 1 section) --------------------
# Voice stack: Sitar solo melody (ch0). Context: ONE low bass note an octave
# below (ch1, GM33) — NOT a second melodic patch on the same pitches.
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Sitar", program=MIDI_PROGRAM, channel=0)
comp.add_voice("Bass", program=33, channel=1)
comp.add_section("A", bars=1)

BAR = 1920

# Sitar: monophonic plucked line, sweet spot, terminal landmark flush at BAR
u = MusicUnit()
mel = [64, 67, 69, 72, 69, 67, 64]          # E4 G4 A4 C5 ... (sweet spot)
for i, p in enumerate(mel):
    u.add_event(MusicEvent(p, 82, i * 240, BAR if i == len(mel) - 1 else i * 240 + 200))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

# Context: low bass C3 (48) — a full octave below the lowest sitar note (64)
u = MusicUnit()
u.add_event(MusicEvent(48, 60, 0, BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/sitar_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---- Render SOLO via discover_soundfont() (FluidR3 preferred) -------------
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/sitar_test.wav"
render_midi(midi_path, wav, solo=0)  # track 1 = Sitar (first voice) ONLY
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# ---- Stem label check against ACTUAL pipeline GM_PROGRAMS (0-indexed) -----
import inspect
import re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
for idx in [104, 105, 106, 107]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Sitar -> {labels[MIDI_PROGRAM]!r}")
assert labels[MIDI_PROGRAM] == "Sitar", f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"
assert STEM_LABEL == "Sitar"

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
assert sf2_name == "Sitar", f"SF2 preset mismatch: {sf2_name!r}"

# ---- Full RenderPipeline stem render — sitar stem label on disk -----------
out_dir = "/opt/data/projects/Instruments/_test/stems_sitar"
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Sitar" in f for f in stem_files), f"no Sitar stem in {stem_files}"
sit_stem = [f for f in stem_files if "Sitar" in f][0]
assert os.path.getsize(os.path.join(out_dir, sit_stem)) > 40, "empty Sitar stem"

# ---- Karplus-Strong smoke test: high loop_gain -> long ringing tail -------
from sound.synthesis.karplus_strong import karplus_strong
import numpy as np
sr = 44100
audio = karplus_strong(pitch=69, dur=2.5, vel=100, loop_gain=KARPLUS_DEFAULTS["loop_gain"])
audio_lo = karplus_strong(pitch=69, dur=2.5, vel=100, loop_gain=0.990)  # dull control
peak = np.max(np.abs(audio))
tail_rms = np.sqrt(np.mean(audio[int(1.0 * sr):int(2.0 * sr)] ** 2))  # 1-2 s, pre-fade
tail_ratio = tail_rms / peak if peak > 0 else 1.0
peak_lo = np.max(np.abs(audio_lo))
tail_lo = np.sqrt(np.mean(audio_lo[int(1.0 * sr):int(2.0 * sr)] ** 2)) / peak_lo if peak_lo > 0 else 1.0
print(f"\nKarplus-Strong sitar: peak={peak:.3f} tail_rms/peak(1-2s)={tail_ratio:.3f} "
      f"(low-gain control={tail_lo:.3f})")
assert peak > 0, "karplus sitar render silent"
assert tail_ratio > 0.003, "sitar decay too fast — loop_gain too low for jivari ring"
assert tail_ratio > 3 * tail_lo, "sitar loop_gain shows no ring advantage over dull control"

print("\nALL CHECKS PASSED")
