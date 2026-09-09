# -*- coding: utf-8 -*-
"""Verify Steel Drums constants work with musicom engine (registry-backed, solo render)."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- Registration proof: import THROUGH the registry ---------------------
from instrument_registry import (
    by_name, by_program, registry_table, ALL_INSTRUMENTS,
)
STEEL = by_name("steel drums")
print("Registry: by_name('steel drums') =", STEEL)
print("Registry: by_program(114) =", by_program(114))
assert STEEL.midi_program == 114
assert by_program(114).name == "Steel Drums"
print("Registry: ALL_INSTRUMENTS count =", len(ALL_INSTRUMENTS))
print("Registry table:\n" + registry_table())

# ---- Constants through the registry ---------------------------------------
MIDI_PROGRAM = STEEL.midi_program
GM_NAME = STEEL.gm_name
STEM_LABEL = STEEL.stem_label
SOLO_RANGE = STEEL.solo_range
SWEET_SPOT = STEEL.sweet_spot
ZONES = STEEL.zones
ARTICULATIONS = STEEL.articulations
SYNTHESIS = STEEL.synthesis
KARPLUS_DEFAULTS = STEEL.karplus_defaults
MODAL_PRESET = STEEL.modal_preset
FM_DEFAULTS = STEEL.fm_defaults
REVERB_TAIL = STEEL.reverb_tail
EQ_BODY = STEEL.eq_body
EQ_PRESENCE = STEEL.eq_presence
EQ_AIR = STEEL.eq_air
PAN = STEEL.pan

print(f"\nSteel Drums: program={MIDI_PROGRAM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"range={STEEL.range_min}-{STEEL.range_max} sweet={SWEET_SPOT} "
      f"solo={SOLO_RANGE}")
print(f"Steel Drums: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"karplus={KARPLUS_DEFAULTS} modal={MODAL_PRESET!r} fm={FM_DEFAULTS}")
print(f"Steel Drums: reverb={REVERB_TAIL}s eq={EQ_BODY},{EQ_PRESENCE},{EQ_AIR} pan={PAN}")
from Percussion.steel_drums.steel_drums import midi_to_freq, PAN_MODES
print(f"Steel Drums: G3={midi_to_freq(55):.1f}Hz C4={midi_to_freq(60):.1f}Hz "
      f"A4={midi_to_freq(69):.1f}Hz C6={midi_to_freq(84):.1f}Hz "
      f"C7={midi_to_freq(96):.1f}Hz")
print(f"Steel Drums: PAN_MODES (freq, amp, decay) = {PAN_MODES}")
assert STEEL.in_range(55) and STEEL.in_range(96) and not STEEL.in_range(54)
assert STEEL.in_sweet_spot(69)

# ---- Engine test: UnitMatrixComposer (1 bar, 1 section) --------------------
# Voice stack: Steel Drums solo melody (ch0). Context: ONE low bass note an
# octave+ below (ch1, GM33) — NOT a second melodic patch on the same pitches.
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Steel Drums", program=MIDI_PROGRAM, channel=0)
comp.add_voice("Bass", program=33, channel=1)
comp.add_section("A", bars=1)

BAR = 1920

# Steel Drums: calypso lead line in the sweet spot; last event ends FLUSH at
# BAR (terminal landmark -> zero-drift). C5 E5 G5 A5 G5 E5 C5.
u = MusicUnit()
mel = [72, 76, 79, 81, 79, 76, 72]
for i, p in enumerate(mel):
    start = i * 240
    end = BAR if i == len(mel) - 1 else start + 200
    u.add_event(MusicEvent(p, 84, start, end))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

# Context: low bass G2 (43) — below the pan's G3 (55), no overlap
u = MusicUnit()
u.add_event(MusicEvent(43, 60, 0, BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/steel_drums_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---- Render SOLO via discover_soundfont() (FluidR3 preferred) -------------
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/steel_drums_test.wav"
render_midi(midi_path, wav, solo=0)  # track 1 = Steel Drums (first voice) ONLY
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
for idx in [108, 109, 110, 114, 115]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Steel Drums -> {labels[MIDI_PROGRAM]!r}")
assert labels[MIDI_PROGRAM] == "Steel Drums", f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"
assert STEM_LABEL == "Steel Drums"

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
assert sf2_name == "Steel Drums", f"SF2 preset mismatch: {sf2_name!r}"

# ---- Full RenderPipeline stem render — steel drums stem label on disk ------
out_dir = "/opt/data/projects/Instruments/_test/stems_steel_drums"
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Steel_Drums" in f for f in stem_files), f"no Steel_Drums stem in {stem_files}"
steel_stem = [f for f in stem_files if "Steel_Drums" in f][0]
assert os.path.getsize(os.path.join(out_dir, steel_stem)) > 40, "empty Steel Drums stem"

# ---- ModalSynth smoke test: exact pan modes (struck membrane) --------------
from sound.synthesis.modal import ModalSynth
import numpy as np
ms = ModalSynth(sample_rate=22050)
audio = ms.render_custom(PAN_MODES, duration=0.5, excitation='impulse')
peak = np.max(np.abs(audio))
# Fast exponential decay expected: tail (last 100 ms, ~t=0.4s) far below peak
tail_rms = np.sqrt(np.mean(audio[-2205:] ** 2))
tail_ratio = tail_rms / peak if peak > 0 else 1.0
print(f"\nModalSynth steel pan (custom PAN_MODES): peak={peak:.3f} "
      f"tail_rms/peak={tail_ratio:.3f}")
assert peak > 0, "modal steel pan render silent"
assert tail_ratio < 0.2, "steel pan decay NOT fast (no sustain plateau expected)"

# Stock marimba preset still works (the MODAL_PRESET recommendation)
audio_m = ms.render_preset('marimba', duration=0.5, excitation='impulse')
peak_m = np.max(np.abs(audio_m))
print(f"ModalSynth 'marimba' preset (MODAL_PRESET): peak={peak_m:.3f}")
assert peak_m > 0, "modal marimba preset silent"

# Karplus-Strong fallback: ring between kalimba (0.9940) and banjo (0.9960)
from sound.synthesis.karplus_strong import karplus_strong
sr = 44100
audio_k = karplus_strong(pitch=69, dur=2.5, vel=100,
                         loop_gain=KARPLUS_DEFAULTS["loop_gain"])
audio_dull = karplus_strong(pitch=69, dur=2.5, vel=100, loop_gain=0.990)
peak_k = np.max(np.abs(audio_k))
tail_k = np.sqrt(np.mean(audio_k[int(0.2 * sr):int(0.6 * sr)] ** 2)) / peak_k if peak_k > 0 else 1.0
peak_d = np.max(np.abs(audio_dull))
tail_d = np.sqrt(np.mean(audio_dull[int(0.2 * sr):int(0.6 * sr)] ** 2)) / peak_d if peak_d > 0 else 1.0
print(f"Karplus-Strong steel pan: peak={peak_k:.3f} "
      f"tail_rms/peak(0.2-0.6s)={tail_k:.3f} (dull control={tail_d:.3f})")
assert peak_k > 0, "karplus steel pan render silent"
assert tail_k > 1.3 * tail_d, "steel pan loop_gain shows no ring advantage over dull control"

print("\nALL CHECKS PASSED")
