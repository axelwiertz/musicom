# -*- coding: utf-8 -*-
"""Verify Kalimba constants work with musicom engine (registry-backed, solo render)."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- Registration proof: import THROUGH the registry ---------------------
from instrument_registry import (
    by_name, by_program, registry_table, ALL_INSTRUMENTS,
)
KALIMBA = by_name("kalimba")
print("Registry: by_name('kalimba') =", KALIMBA)
print("Registry: by_program(108) =", by_program(108))
assert KALIMBA.midi_program == 108
assert by_program(108).name == "Kalimba"
print("Registry: ALL_INSTRUMENTS count =", len(ALL_INSTRUMENTS))
print("Registry table:\n" + registry_table())

# ---- Constants through the registry ---------------------------------------
MIDI_PROGRAM = KALIMBA.midi_program
GM_NAME = KALIMBA.gm_name
STEM_LABEL = KALIMBA.stem_label
SOLO_RANGE = KALIMBA.solo_range
SWEET_SPOT = KALIMBA.sweet_spot
ZONES = KALIMBA.zones
ARTICULATIONS = KALIMBA.articulations
SYNTHESIS = KALIMBA.synthesis
KARPLUS_DEFAULTS = KALIMBA.karplus_defaults
FM_DEFAULTS = KALIMBA.fm_defaults
REVERB_TAIL = KALIMBA.reverb_tail
EQ_BODY = KALIMBA.eq_body
EQ_PRESENCE = KALIMBA.eq_presence
EQ_AIR = KALIMBA.eq_air
PAN = KALIMBA.pan

print(f"\nKalimba: program={MIDI_PROGRAM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"range={KALIMBA.range_min}-{KALIMBA.range_max} sweet={SWEET_SPOT} "
      f"solo={SOLO_RANGE}")
print(f"Kalimba: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"karplus={KARPLUS_DEFAULTS} fm={FM_DEFAULTS}")
print(f"Kalimba: reverb={REVERB_TAIL}s eq={EQ_BODY},{EQ_PRESENCE},{EQ_AIR} pan={PAN}")
from World.kalimba.kalimba import midi_to_freq
print(f"Kalimba: C3={midi_to_freq(48):.1f}Hz C4={midi_to_freq(60):.1f}Hz "
      f"A4={midi_to_freq(69):.1f}Hz C6={midi_to_freq(84):.1f}Hz "
      f"C7={midi_to_freq(96):.1f}Hz")
assert KALIMBA.in_range(48) and KALIMBA.in_range(96) and not KALIMBA.in_range(47)
assert KALIMBA.in_sweet_spot(69)

# ---- Engine test: UnitMatrixComposer (1 bar, 1 section) --------------------
# Voice stack: Kalimba solo melody (ch0). Context: ONE low bass note an octave
# below (ch1, GM33) — NOT a second melodic patch on the same pitches.
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Kalimba", program=MIDI_PROGRAM, channel=0)
comp.add_voice("Bass", program=33, channel=1)
comp.add_section("A", bars=1)

BAR = 1920

# Kalimba: plucked melodic line in sweet spot, terminal landmark flush at BAR
u = MusicUnit()
mel = [64, 67, 69, 72, 69, 67, 64]          # E4 G4 A4 C5 ... (sweet spot)
for i, p in enumerate(mel):
    u.add_event(MusicEvent(p, 82, i * 240, BAR if i == len(mel) - 1 else i * 240 + 200))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

# Context: low bass C3 (48) — a full octave below the lowest kalimba note (64)
u = MusicUnit()
u.add_event(MusicEvent(48, 60, 0, BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/kalimba_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---- Render SOLO via discover_soundfont() (FluidR3 preferred) -------------
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/kalimba_test.wav"
render_midi(midi_path, wav, solo=0)  # track 1 = Kalimba (first voice) ONLY
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
for idx in [104, 106, 107, 108]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Kalimba -> {labels[MIDI_PROGRAM]!r}")
assert labels[MIDI_PROGRAM] == "Kalimba", f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"
assert STEM_LABEL == "Kalimba"

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
assert sf2_name == "Kalimba", f"SF2 preset mismatch: {sf2_name!r}"

# ---- Full RenderPipeline stem render — kalimba stem label on disk ---------
out_dir = "/opt/data/projects/Instruments/_test/stems_kalimba"
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Kalimba" in f for f in stem_files), f"no Kalimba stem in {stem_files}"
kal_stem = [f for f in stem_files if "Kalimba" in f][0]
assert os.path.getsize(os.path.join(out_dir, kal_stem)) > 40, "empty Kalimba stem"

# ---- Karplus-Strong smoke test: metal-tine ring vs dull control -----------
from sound.synthesis.karplus_strong import karplus_strong
import numpy as np
sr = 44100
audio = karplus_strong(pitch=69, dur=2.5, vel=100, loop_gain=KARPLUS_DEFAULTS["loop_gain"])
audio_lo = karplus_strong(pitch=69, dur=2.5, vel=100, loop_gain=0.990)  # dull control
peak = np.max(np.abs(audio))
# Kalimba ring is SHORT (metal tine) — measure 0.2-0.6 s. Probe (2026-09-05):
# loop_gain 0.994 gives ratio 0.0142 (1.7x control); the 0.5-1.5 s window used
# for sitar/koto is past the kalimba ring (both readings at noise floor).
tail_rms = np.sqrt(np.mean(audio[int(0.2 * sr):int(0.6 * sr)] ** 2))
tail_ratio = tail_rms / peak if peak > 0 else 1.0
peak_lo = np.max(np.abs(audio_lo))
tail_lo = np.sqrt(np.mean(audio_lo[int(0.2 * sr):int(0.6 * sr)] ** 2)) / peak_lo if peak_lo > 0 else 1.0
print(f"\nKarplus-Strong kalimba: peak={peak:.3f} tail_rms/peak(0.2-0.6s)={tail_ratio:.3f} "
      f"(low-gain control={tail_lo:.3f})")
assert peak > 0, "karplus kalimba render silent"
assert tail_ratio > 0.01, "kalimba decay too fast — loop_gain too low for tine ring"
assert tail_ratio > 1.5 * tail_lo, "kalimba loop_gain shows no ring advantage over dull control"

# Kalimba ring must be SHORTER than sitar's (metal tine vs sympathetic strings)
audio_sitar = karplus_strong(pitch=69, dur=2.5, vel=100, loop_gain=0.9975)
peak_s = np.max(np.abs(audio_sitar))
tail_s = np.sqrt(np.mean(audio_sitar[int(0.2 * sr):int(0.6 * sr)] ** 2)) / peak_s if peak_s > 0 else 1.0
print(f"Kalimba tail {tail_ratio:.3f} vs sitar tail {tail_s:.3f} (kalimba < sitar expected)")
assert tail_ratio < tail_s, "kalimba should decay faster than sitar (metal tine physics)"

print("\nALL CHECKS PASSED")
