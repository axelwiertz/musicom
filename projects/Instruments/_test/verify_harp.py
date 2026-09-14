# -*- coding: utf-8 -*-
"""Verify Harp constants work with musicom engine (registry-backed, solo render)."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- Registration proof: import THROUGH the registry ---------------------
from instrument_registry import (
    by_name, by_program, registry_table, ALL_INSTRUMENTS,
)

HARP = by_name("harp")
print("Registry: by_name('harp') =", HARP)
print("Registry: by_program(46) =", by_program(46))
assert HARP.midi_program == 46
assert by_program(46).name == "Orchestral Harp"
print("Registry: ALL_INSTRUMENTS count =", len(ALL_INSTRUMENTS))
table = registry_table()
print("Registry table:\n" + table)
assert "| Strings | Orchestral Harp | 46 |" in table, "harp row missing from registry_table()"

# ---- Constants through the registry ---------------------------------------
MIDI_PROGRAM = HARP.midi_program
GM_NAME = HARP.gm_name
STEM_LABEL = HARP.stem_label
SOLO_RANGE = HARP.solo_range
SWEET_SPOT = HARP.sweet_spot
ZONES = HARP.zones
ARTICULATIONS = HARP.articulations
SYNTHESIS = HARP.synthesis
MODAL_PRESET = HARP.modal_preset
KARPLUS_DEFAULTS = HARP.karplus_defaults
from Strings.harp.harp import HARP_MODES as HM, midi_to_freq, FM_DEFAULTS
REVERB_TAIL = HARP.reverb_tail
EQ_BODY = HARP.eq_body
EQ_PRESENCE = HARP.eq_presence
EQ_AIR = HARP.eq_air
PAN = HARP.pan

print(f"\nHarp: program={MIDI_PROGRAM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"range={HARP.range_min}-{HARP.range_max} sweet={SWEET_SPOT} solo={SOLO_RANGE}")
print(f"Harp: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} modal={MODAL_PRESET!r}")
print(f"Harp: karplus={KARPLUS_DEFAULTS} fm={FM_DEFAULTS}")
print(f"Harp: C1={midi_to_freq(24):.1f}Hz C3={midi_to_freq(48):.1f}Hz "
      f"C4={midi_to_freq(60):.1f}Hz A4={midi_to_freq(69):.1f}Hz "
      f"C6={midi_to_freq(84):.1f}Hz G7={midi_to_freq(103):.1f}Hz")
print(f"Harp: modes={HM}")
assert HARP.in_range(24) and HARP.in_range(103) and not HARP.in_range(23)
assert not HARP.in_range(104)  # piano tops at 108 but harp strings end at G7
assert HARP.in_sweet_spot(69)
# near-harmonic partial structure (1 : 2 : 3 : 4 : 5)
assert [round(f / 440.0, 2) for f, _, _ in HM] == [1.0, 2.0, 3.0, 4.0, 5.0]

# ---- Engine test: UnitMatrixComposer (1 bar, 1 section) --------------------
# Voice stack: Harp solo arpeggio (ch0). Context: ONE low bass note an octave+
# below (ch1, GM33) — NOT a second melodic patch on the same pitches.
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Harp", program=MIDI_PROGRAM, channel=0)
comp.add_voice("Bass", program=33, channel=1)
comp.add_section("A", bars=1)

BAR = 1920

# Harp: rising arpeggio C3-G3-C4-E4-G4-C5-E5-G5 (the signature harp texture),
# 8 events, last one ends FLUSH at BAR (terminal landmark).
u = MusicUnit()
arp = [48, 55, 60, 64, 67, 72, 76, 79]   # C3 G3 C4 E4 G4 C5 E5 G5 — C major
for i, p in enumerate(arp):
    start = i * 240
    end = BAR if i == len(arp) - 1 else start + 220
    u.add_event(MusicEvent(p, 80, start, end))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

# Context: low bass C2 (36) — well below the harp arpeggio's sweet band
u = MusicUnit()
u.add_event(MusicEvent(36, 58, 0, BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/harp_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---- Render SOLO via discover_soundfont() (FluidR3 preferred) -------------
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/harp_test.wav"
render_midi(midi_path, wav, solo=0)  # track 1 = Harp (first voice) ONLY
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
for idx in [44, 45, 46, 47, 48]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Harp -> {labels[MIDI_PROGRAM]!r}")
assert labels[MIDI_PROGRAM] == "Orchestral Harp", f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"
assert STEM_LABEL == "Orchestral_Harp"

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
assert sf2_name == "Harp", f"SF2 preset mismatch: {sf2_name!r}"

# ---- Full RenderPipeline stem render — harp stem label on disk ------------
out_dir = "/opt/data/projects/Instruments/_test/stems_harp"
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Orchestral_Harp" in f for f in stem_files), f"no harp stem in {stem_files}"
hp_stem = [f for f in stem_files if "Orchestral_Harp" in f][0]
assert os.path.getsize(os.path.join(out_dir, hp_stem)) > 40, "empty harp stem"

# ---- Karplus-Strong PRIMARY: longest ring of the plucked set --------------
from sound.synthesis.karplus_strong import karplus_strong
import numpy as np
sr = 44100
ks = karplus_strong(pitch=69, dur=3.0, vel=100, loop_gain=KARPLUS_DEFAULTS["loop_gain"])
ks_sitar = karplus_strong(pitch=69, dur=3.0, vel=100, loop_gain=0.9975)   # next-best plucked
ks_dull = karplus_strong(pitch=69, dur=3.0, vel=100, loop_gain=0.990)     # dull control
kp, ks_p, kd = np.max(np.abs(ks)), np.max(np.abs(ks_sitar)), np.max(np.abs(ks_dull))
kt = np.sqrt(np.mean(ks[1 * sr:2 * sr] ** 2)) / kp if kp > 0 else 1.0
kt_sitar = np.sqrt(np.mean(ks_sitar[1 * sr:2 * sr] ** 2)) / ks_p if ks_p > 0 else 1.0
kt_dull = np.sqrt(np.mean(ks_dull[1 * sr:2 * sr] ** 2)) / kd if kd > 0 else 1.0
print(f"\nKarplus-Strong harp loop_gain={KARPLUS_DEFAULTS['loop_gain']}: "
      f"tail_rms/peak(1-2s)={kt:.4f} (sitar-class 0.9975: {kt_sitar:.4f}, "
      f"dull control 0.990: {kt_dull:.4f})")
assert kp > 0, "KS harp render silent"
assert kt > 2 * kt_dull, "harp KS shows no ring advantage over dull control"
assert kt > kt_sitar, "harp loop_gain must out-ring the sitar-class setting (0.9975)"

# partial structure: fundamental + near-harmonic stack (2x dominates upper)
spec = np.abs(np.fft.rfft(ks[: int(0.5 * sr)]))
freqs = np.fft.rfftfreq(int(0.5 * sr), 1 / sr)
def band(f, tol=12.0):
    sel = (freqs >= f - tol) & (freqs <= f + tol)
    return spec[sel].max() if sel.any() else 0.0
f0, f2, f3 = band(440.0), band(880.0), band(1320.0)
print(f"  KS partials: f0={f0:.1f} 2x={f2:.1f} ({(f2 / f0) * 100:.1f}% of f0) "
      f"3x={f3:.1f} ({(f3 / f0) * 100:.1f}% of f0)")
# harp stack is near-harmonic and octave-rich (a real gut string's 2nd partial
# is as strong as its fundamental); the stack must still DECAY upward
assert f0 > 0 and f3 < f0 and f3 <= f2, "harp harmonic stack must decay upward"

# ---- ModalSynth 'string' fallback + HARP_MODES ring check -----------------
from sound.synthesis.modal import ModalSynth
ms = ModalSynth(sample_rate=sr)
audio = ms.render_custom(HM, duration=3.0, excitation="impulse")
peak = np.max(np.abs(audio))
late = np.sqrt(np.mean(audio[int(1.0 * sr):int(1.5 * sr)] ** 2))
late_ratio = late / peak if peak > 0 else 1.0
mar = ms.render_preset("marimba", duration=3.0, excitation="impulse")
mar_late = np.sqrt(np.mean(mar[int(1.0 * sr):int(1.5 * sr)] ** 2)) / np.max(np.abs(mar))
print(f"\nModalSynth HARP_MODES: peak={peak:.3f} late(1.0-1.5s)_rms/peak={late_ratio:.3f}")
print(f"  marimba stock preset late(1.0-1.5s)_rms/peak={mar_late:.4f}")
assert peak > 0, "harp modal render silent"
assert late_ratio > 0.01, "harp string decayed too fast — expected a multi-second ring"
assert late_ratio > 3 * mar_late, "harp shows no ring advantage over the marimba preset"

print("\nALL CHECKS PASSED")
