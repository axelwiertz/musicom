# -*- coding: utf-8 -*-
"""Verify Vibraphone constants work with musicom engine (registry-backed, solo render)."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- Registration proof: import THROUGH the registry ---------------------
from instrument_registry import (
    by_name, by_program, registry_table, ALL_INSTRUMENTS,
)

VIBRAPHONE = by_name("vibraphone")
print("Registry: by_name('vibraphone') =", VIBRAPHONE)
print("Registry: by_program(11) =", by_program(11))
assert VIBRAPHONE.midi_program == 11
assert by_program(11).name == "Vibraphone"
print("Registry: ALL_INSTRUMENTS count =", len(ALL_INSTRUMENTS))
table = registry_table()
print("Registry table:\n" + table)
assert "| Percussion | Vibraphone | 11 |" in table, "vibraphone row missing from registry_table()"

# ---- Constants through the registry ---------------------------------------
MIDI_PROGRAM = VIBRAPHONE.midi_program
GM_NAME = VIBRAPHONE.gm_name
STEM_LABEL = VIBRAPHONE.stem_label
SOLO_RANGE = VIBRAPHONE.solo_range
SWEET_SPOT = VIBRAPHONE.sweet_spot
ZONES = VIBRAPHONE.zones
ARTICULATIONS = VIBRAPHONE.articulations
SYNTHESIS = VIBRAPHONE.synthesis
MODAL_PRESET = VIBRAPHONE.modal_preset
MOTOR_DEFAULTS = VIBRAPHONE.motor_defaults
KARPLUS_DEFAULTS = VIBRAPHONE.karplus_defaults
FM_DEFAULTS = VIBRAPHONE.fm_defaults
REVERB_TAIL = VIBRAPHONE.reverb_tail
EQ_BODY = VIBRAPHONE.eq_body
EQ_PRESENCE = VIBRAPHONE.eq_presence
EQ_AIR = VIBRAPHONE.eq_air
PAN = VIBRAPHONE.pan

print(f"\nVibraphone: program={MIDI_PROGRAM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"range={VIBRAPHONE.range_min}-{VIBRAPHONE.range_max} sweet={SWEET_SPOT} "
      f"solo={SOLO_RANGE}")
print(f"Vibraphone: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"modal={MODAL_PRESET!r}")
print(f"Vibraphone: motor={MOTOR_DEFAULTS} karplus={KARPLUS_DEFAULTS} fm={FM_DEFAULTS}")
print(f"Vibraphone: reverb={REVERB_TAIL}s eq={EQ_BODY},{EQ_PRESENCE},{EQ_AIR} pan={PAN}")
from Percussion.vibraphone.vibraphone import midi_to_freq, VIBRAPHONE_MODES
print(f"Vibraphone: C3={midi_to_freq(48):.1f}Hz F3={midi_to_freq(53):.1f}Hz "
      f"C4={midi_to_freq(60):.1f}Hz A4={midi_to_freq(69):.1f}Hz "
      f"C6={midi_to_freq(84):.1f}Hz F6={midi_to_freq(89):.1f}Hz")
print(f"Vibraphone: modes={VIBRAPHONE_MODES}")
assert VIBRAPHONE.in_range(48) and VIBRAPHONE.in_range(89) and not VIBRAPHONE.in_range(47)
assert VIBRAPHONE.in_sweet_spot(69)
# arch-tuned 1:4:10 partial structure
assert [round(f / 440.0, 2) for f, _, _ in VIBRAPHONE_MODES] == [1.0, 4.0, 10.0]

# ---- Engine test: UnitMatrixComposer (1 bar, 1 section) --------------------
# Voice stack: Vibraphone solo melody (ch0). Context: ONE low bass note an
# octave+ below (ch1, GM33) — NOT a second melodic patch on the same pitches.
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Vibraphone", program=MIDI_PROGRAM, channel=0)
comp.add_voice("Bass", program=33, channel=1)
comp.add_section("A", bars=1)

BAR = 1920

# Vibraphone: lush pedal-down chord/melody line in the sweet spot, 7 events,
# last one ends FLUSH at BAR (terminal landmark).
u = MusicUnit()
mel = [64, 67, 71, 72, 71, 67, 64]   # E4 G4 B4 C5 B4 G4 E4 — E minor, mid zone
for i, p in enumerate(mel):
    start = i * 240
    end = BAR if i == len(mel) - 1 else start + 200
    u.add_event(MusicEvent(p, 80, start, end))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

# Context: low bass E2 (40) — well below the vibraphone's lowest note (64)
u = MusicUnit()
u.add_event(MusicEvent(40, 58, 0, BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/vibraphone_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---- Render SOLO via discover_soundfont() (FluidR3 preferred) -------------
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/vibraphone_test.wav"
render_midi(midi_path, wav, solo=0)  # track 1 = Vibraphone (first voice) ONLY
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
for idx in [9, 10, 11, 12, 13, 14]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Vibraphone -> {labels[MIDI_PROGRAM]!r}")
assert labels[MIDI_PROGRAM] == "Vibraphone", f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"
assert STEM_LABEL == "Vibraphone"

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
assert sf2_name == "Vibraphone", f"SF2 preset mismatch: {sf2_name!r}"

# ---- Full RenderPipeline stem render — vibraphone stem label on disk ------
out_dir = "/opt/data/projects/Instruments/_test/stems_vibraphone"
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Vibraphone" in f for f in stem_files), f"no Vibraphone stem in {stem_files}"
vb_stem = [f for f in stem_files if "Vibraphone" in f][0]
assert os.path.getsize(os.path.join(out_dir, vb_stem)) > 40, "empty Vibraphone stem"

# ---- ModalSynth VIBRAPHONE_MODES: LONG ring + fundamental dominance -------
from sound.synthesis.modal import ModalSynth
import numpy as np
sr = 44100
ms = ModalSynth(sample_rate=sr)
audio = ms.render_custom(VIBRAPHONE_MODES, duration=2.5, excitation="impulse")
peak = np.max(np.abs(audio))
late = np.sqrt(np.mean(audio[int(1.0 * sr):int(1.5 * sr)] ** 2))
late_ratio = late / peak if peak > 0 else 1.0
# marimba stock preset decays FAR faster (timpani REPORT measured 0.0001)
mar = ms.render_preset("marimba", duration=2.5, excitation="impulse")
mar_late = np.sqrt(np.mean(mar[int(1.0 * sr):int(1.5 * sr)] ** 2)) / np.max(np.abs(mar))
print(f"\nModalSynth VIBRAPHONE_MODES: peak={peak:.3f} late(1.0-1.5s)_rms/peak={late_ratio:.3f}")
print(f"  marimba stock preset late(1.0-1.5s)_rms/peak={mar_late:.4f}")
assert peak > 0, "vibraphone modal render silent"
assert late_ratio > 0.01, "vibraphone bar decayed too fast — expected a multi-second ring"
assert late_ratio > 3 * mar_late, "vibraphone shows no ring advantage over the marimba preset"

# partial check: fundamental dominates the 4x and 10x partials
spec = np.abs(np.fft.rfft(audio[: int(0.5 * sr)]))
freqs = np.fft.rfftfreq(int(0.5 * sr), 1 / sr)
def band(f, tol=12.0):
    sel = (freqs >= f - tol) & (freqs <= f + tol)
    return spec[sel].max() if sel.any() else 0.0
f0, f4, f10 = band(440.0), band(1760.0), band(4400.0)
print(f"  partials: f0={f0:.1f} 4x={f4:.1f} ({(f4 / f0) * 100:.1f}% of f0) "
      f"10x={f10:.1f} ({(f10 / f0) * 100:.1f}% of f0)")
assert f0 > f4 > f10, "vibraphone fundamental must dominate the arch-tuned partials"

# ---- Motor tremolo (MOTOR_DEFAULTS) as amplitude modulation ---------------
t = np.arange(len(audio)) / sr
rate, depth = MOTOR_DEFAULTS["rate_hz"], MOTOR_DEFAULTS["depth"]
env = 1.0 - depth * 0.5 * (1.0 - np.cos(2 * np.pi * rate * t))
mod = audio * env
# the motor must create measurable envelope movement at the motor rate
env_fund = np.abs(np.fft.rfft(np.abs(mod)))
fr = np.fft.rfftfreq(len(mod), 1 / sr)
sel = (fr >= rate - 0.5) & (fr <= rate + 0.5)
motor_pk = env_fund[sel].max() if sel.any() else 0.0
broad = env_fund[(fr >= 0.1) & (fr <= 50.0)].max()
print(f"\nMotor tremolo: rate={rate}Hz depth={depth} — envelope peak@rate/nearby-max "
      f"= {motor_pk / broad:.3f}")
assert motor_pk > 0.05 * broad, "motor tremolo produced no measurable AM at the motor rate"

# ---- Karplus-Strong fallback smoke test ----------------------------------
from sound.synthesis.karplus_strong import karplus_strong
ks = karplus_strong(pitch=69, dur=2.5, vel=100, loop_gain=KARPLUS_DEFAULTS["loop_gain"])
ks_lo = karplus_strong(pitch=69, dur=2.5, vel=100, loop_gain=0.990)
kp, klp = np.max(np.abs(ks)), np.max(np.abs(ks_lo))
kt = np.sqrt(np.mean(ks[sr:2 * sr] ** 2)) / kp if kp > 0 else 1.0
kt_lo = np.sqrt(np.mean(ks_lo[sr:2 * sr] ** 2)) / klp if klp > 0 else 1.0
print(f"Karplus-Strong vibraphone (fallback): tail_rms/peak(1-2s)={kt:.4f} "
      f"(dull control {kt_lo:.4f})")
assert kp > 0 and kt > 3 * kt_lo, "KS fallback shows no ring advantage"

print("\nALL CHECKS PASSED")
