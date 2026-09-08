# -*- coding: utf-8 -*-
"""Verify Dulcimer constants work with musicom engine (registry-backed, solo render)."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- Registration proof: import THROUGH the registry ---------------------
from instrument_registry import (
    by_name, by_program, registry_table, ALL_INSTRUMENTS,
)
DULCIMER = by_name("dulcimer")
print("Registry: by_name('dulcimer') =", DULCIMER)
print("Registry: by_program(15) =", by_program(15))
assert DULCIMER.midi_program == 15
assert by_program(15).name == "Dulcimer"
print("Registry: ALL_INSTRUMENTS count =", len(ALL_INSTRUMENTS))
print("Registry table:\n" + registry_table())

# ---- Constants through the registry ---------------------------------------
MIDI_PROGRAM = DULCIMER.midi_program
GM_NAME = DULCIMER.gm_name
STEM_LABEL = DULCIMER.stem_label
SOLO_RANGE = DULCIMER.solo_range
SWEET_SPOT = DULCIMER.sweet_spot
ZONES = DULCIMER.zones
ARTICULATIONS = DULCIMER.articulations
SYNTHESIS = DULCIMER.synthesis
MODAL_PRESET = DULCIMER.modal_preset
KARPLUS_DEFAULTS = DULCIMER.karplus_defaults
FM_DEFAULTS = DULCIMER.fm_defaults
REVERB_TAIL = DULCIMER.reverb_tail
EQ_BODY = DULCIMER.eq_body
EQ_PRESENCE = DULCIMER.eq_presence
EQ_AIR = DULCIMER.eq_air
PAN = DULCIMER.pan

print(f"\nDulcimer: program={MIDI_PROGRAM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"range={DULCIMER.range_min}-{DULCIMER.range_max} sweet={SWEET_SPOT} "
      f"solo={SOLO_RANGE}")
print(f"Dulcimer: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"modal={MODAL_PRESET!r} karplus={KARPLUS_DEFAULTS} fm={FM_DEFAULTS}")
print(f"Dulcimer: reverb={REVERB_TAIL}s eq={EQ_BODY},{EQ_PRESENCE},{EQ_AIR} pan={PAN}")
from Keys.dulcimer.dulcimer import midi_to_freq
print(f"Dulcimer: C3={midi_to_freq(48):.1f}Hz C4={midi_to_freq(60):.1f}Hz "
      f"A4={midi_to_freq(69):.1f}Hz C6={midi_to_freq(84):.1f}Hz "
      f"C7={midi_to_freq(96):.1f}Hz")
assert DULCIMER.in_range(48) and DULCIMER.in_range(96) and not DULCIMER.in_range(47)
assert DULCIMER.in_sweet_spot(69)

# ---- Engine test: UnitMatrixComposer (1 bar, 1 section) --------------------
# Voice stack: Dulcimer solo melody (ch0). Context: ONE low bass note an octave
# below (ch1, GM33) — NOT a second melodic patch on the same pitches.
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Dulcimer", program=MIDI_PROGRAM, channel=0)
comp.add_voice("Bass", program=33, channel=1)
comp.add_section("A", bars=1)

BAR = 1920

# Dulcimer: hammered melodic line in sweet spot, terminal landmark flush at BAR
# D4 F#4 A4 D5 A4 F#4 D4 — hammered-dulcimer dance feel, sweet spot (62..86)
u = MusicUnit()
mel = [62, 66, 69, 74, 69, 66, 62]
for i, p in enumerate(mel):
    u.add_event(MusicEvent(p, 84, i * 240, BAR if i == len(mel) - 1 else i * 240 + 200))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

# Context: low bass C2 (36) — below the dulcimer's low C3 (48), no overlap
u = MusicUnit()
u.add_event(MusicEvent(36, 60, 0, BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/dulcimer_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---- Render SOLO via discover_soundfont() (FluidR3 preferred) -------------
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/dulcimer_test.wav"
render_midi(midi_path, wav, solo=0)  # track 1 = Dulcimer (first voice) ONLY
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
for idx in [6, 12, 15, 19, 25]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Dulcimer -> {labels[MIDI_PROGRAM]!r}")
assert labels[MIDI_PROGRAM] == "Dulcimer", f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"
assert STEM_LABEL == "Dulcimer"

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
assert sf2_name == "Dulcimer", f"SF2 preset mismatch: {sf2_name!r}"

# ---- Full RenderPipeline stem render — dulcimer stem label on disk ---------
out_dir = "/opt/data/projects/Instruments/_test/stems_dulcimer"
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Dulcimer" in f for f in stem_files), f"no Dulcimer stem in {stem_files}"
dul_stem = [f for f in stem_files if "Dulcimer" in f][0]
assert os.path.getsize(os.path.join(out_dir, dul_stem)) > 40, "empty Dulcimer stem"

# ---- ModalSynth smoke test: struck-string ring ----------------------------
from sound.synthesis.modal import ResonatorBank
import numpy as np
sr = 44100
bank = ResonatorBank.preset(MODAL_PRESET, sr)
audio = bank.excite_impulse(1.5)
peak = np.max(np.abs(audio))
tail_rms = np.sqrt(np.mean(audio[int(0.2 * sr):int(0.6 * sr)] ** 2))
tail_ratio = tail_rms / peak if peak > 0 else 1.0
print(f"\nModalSynth '{MODAL_PRESET}' preset: peak={peak:.3f} "
      f"tail_rms/peak(0.2-0.6s)={tail_ratio:.3f}")
assert peak > 0, "modal dulcimer render silent"
assert tail_ratio > 0.01, "modal preset decays too fast"

# Custom struck-string resonator (instrument.md modes scaled to A4=440)
custom = ResonatorBank(sr)
f0 = 440.0
for ratio, amp, decay in [(1.0, 1.0, 3.0), (2.0, 0.55, 5.0), (3.0, 0.30, 7.0),
                          (4.0, 0.18, 9.0), (5.0, 0.12, 11.0), (6.0, 0.08, 13.0)]:
    custom.add_mode(f0 * ratio, amp, decay)
c_audio = custom.excite_impulse(1.5)
c_peak = np.max(np.abs(c_audio))
print(f"Custom struck-string modes: peak={c_peak:.3f}")
assert c_peak > 0, "custom dulcimer render silent"

# ---- Karplus-Strong smoke test: bright ring vs dull control ---------------
from sound.synthesis.karplus_strong import karplus_strong
audio_k = karplus_strong(pitch=69, dur=2.5, vel=100, loop_gain=KARPLUS_DEFAULTS["loop_gain"])
audio_dull = karplus_strong(pitch=69, dur=2.5, vel=100, loop_gain=0.990)
peak_k = np.max(np.abs(audio_k))
tail_k = np.sqrt(np.mean(audio_k[int(0.2 * sr):int(0.6 * sr)] ** 2)) / peak_k if peak_k > 0 else 1.0
peak_dull = np.max(np.abs(audio_dull))
tail_dull = np.sqrt(np.mean(audio_dull[int(0.2 * sr):int(0.6 * sr)] ** 2)) / peak_dull if peak_dull > 0 else 1.0
print(f"\nKarplus-Strong dulcimer: peak={peak_k:.3f} tail_rms/peak(0.2-0.6s)={tail_k:.3f} "
      f"(low-gain control={tail_dull:.3f})")
assert peak_k > 0, "karplus dulcimer render silent"
assert tail_k > 1.3 * tail_dull, "dulcimer loop_gain shows no ring advantage over dull control"

print("\nALL CHECKS PASSED")
