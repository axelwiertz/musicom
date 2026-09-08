# -*- coding: utf-8 -*-
"""Verify Bagpipe constants work with musicom engine (registry-backed, solo render)."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- Registration proof: import THROUGH the registry ---------------------
from instrument_registry import (
    by_name, by_program, registry_table, ALL_INSTRUMENTS,
)
BAGPIPE = by_name("bagpipe")
print("Registry: by_name('bagpipe') =", BAGPIPE)
print("Registry: by_program(109) =", by_program(109))
assert BAGPIPE.midi_program == 109
assert by_program(109).name == "Bagpipe"
print("Registry: ALL_INSTRUMENTS count =", len(ALL_INSTRUMENTS))
print("Registry table:\n" + registry_table())

# ---- Constants through the registry ---------------------------------------
MIDI_PROGRAM = BAGPIPE.midi_program
GM_NAME = BAGPIPE.gm_name
STEM_LABEL = BAGPIPE.stem_label
SOLO_RANGE = BAGPIPE.solo_range
SWEET_SPOT = BAGPIPE.sweet_spot
ZONES = BAGPIPE.zones
ARTICULATIONS = BAGPIPE.articulations
SYNTHESIS = BAGPIPE.synthesis
FM_DEFAULTS = BAGPIPE.fm_defaults
MODAL_PRESET = BAGPIPE.modal_preset
REVERB_TAIL = BAGPIPE.reverb_tail
EQ_BODY = BAGPIPE.eq_body
EQ_PRESENCE = BAGPIPE.eq_presence
EQ_AIR = BAGPIPE.eq_air
PAN = BAGPIPE.pan

print(f"\nBagpipe: program={MIDI_PROGRAM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"range={BAGPIPE.range_min}-{BAGPIPE.range_max} sweet={SWEET_SPOT} "
      f"solo={SOLO_RANGE}")
print(f"Bagpipe: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"fm={FM_DEFAULTS} modal={MODAL_PRESET!r}")
print(f"Bagpipe: reverb={REVERB_TAIL}s eq={EQ_BODY},{EQ_PRESENCE},{EQ_AIR} pan={PAN}")
from Woodwind.bagpipe.bagpipe import midi_to_freq
print(f"Bagpipe: A3={midi_to_freq(57):.1f}Hz A4={midi_to_freq(69):.1f}Hz "
      f"D4={midi_to_freq(62):.1f}Hz")
assert BAGPIPE.in_range(53) and BAGPIPE.in_range(96) and not BAGPIPE.in_range(52)
assert BAGPIPE.in_sweet_spot(62)

# ---- Engine test: UnitMatrixComposer (1 bar, 1 section) --------------------
# Voice stack: Bagpipe solo melody (ch0). Context: ONE low drone note an
# octave below (ch1, GM33) — NOT a second melodic patch on the same pitches.
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Bagpipe", program=MIDI_PROGRAM, channel=0)
comp.add_voice("Bass", program=33, channel=1)
comp.add_section("A", bars=1)

BAR = 1920

# Bagpipe: mixolydian chanter line in the real 9-note register (57-69).
# The chanter never stops: note changes are cuts — each note is long and
# the line is stepwise/ornamental. Last event ends FLUSH at BAR.
u = MusicUnit()
mel = [62, 64, 66, 69, 67, 66, 64, 62]  # D E F# A G F# E D — chanter idiom
n = len(mel)
dur = BAR // n  # 240 ticks each, contiguous — bagpipe sustains constantly
for i, p in enumerate(mel):
    start = i * dur
    end = BAR if i == n - 1 else (i + 1) * dur
    u.add_event(MusicEvent(p, 80, start, end))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

# Context: low drone A1 (33) — well below the chanter's A3 (57), no overlap
u = MusicUnit()
u.add_event(MusicEvent(33, 55, 0, BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/bagpipe_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---- Render SOLO via discover_soundfont() (FluidR3 preferred) -------------
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/bagpipe_test.wav"
render_midi(midi_path, wav, solo=0)  # track 1 = Bagpipe (first voice) ONLY
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
for idx in [104, 105, 106, 107, 108, 109, 110, 111]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Bagpipe -> {labels[MIDI_PROGRAM]!r}")
assert labels[MIDI_PROGRAM] == "Bag pipe", f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"
# STEM_LABEL = sanitized ACTUAL label ("Bag pipe" -> "Bag_pipe")
assert STEM_LABEL == "Bag_pipe"

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
assert sf2_name == "BagPipe", f"SF2 preset mismatch: {sf2_name!r}"

# ---- Full RenderPipeline stem render — bagpipe stem label on disk ---------
out_dir = "/opt/data/projects/Instruments/_test/stems_bagpipe"
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Bag_pipe" in f for f in stem_files), f"no Bag_pipe stem in {stem_files}"
bp_stem = [f for f in stem_files if "Bag_pipe" in f][0]
assert os.path.getsize(os.path.join(out_dir, bp_stem)) > 40, "empty Bagpipe stem"

# ---- PhaseModSynth smoke test: sustained reed tone ------------------------
from Woodwind.bagpipe.bagpipe import midi_to_freq
from sound.synthesis.phase_mod import PhaseModSynth
import numpy as np
synth = PhaseModSynth(sample_rate=22050)
audio = synth.render_note(freq=midi_to_freq(62), duration=0.8, **FM_DEFAULTS)
peak = np.max(np.abs(audio))
# A sustained reed should NOT collapse to silence: late-window RMS (0.5-0.7s)
# must still be a real fraction of the peak (sustain, not a pluck decay).
late_rms = np.sqrt(np.mean(audio[int(0.5 * 22050):int(0.7 * 22050)] ** 2))
ratio = late_rms / peak if peak > 0 else 1.0
print(f"\nPhaseModSynth bagpipe: peak={peak:.3f} late(0.5-0.7s)_rms/peak={ratio:.3f}")
assert peak > 0, "phase-mod bagpipe render silent"
assert ratio > 0.25, "bagpipe tone collapses — expected sustained reed, got pluck decay"

print("\nALL CHECKS PASSED")
