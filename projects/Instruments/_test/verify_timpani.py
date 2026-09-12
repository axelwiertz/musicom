# -*- coding: utf-8 -*-
"""Verify Timpani constants work with musicom engine (registry-backed, solo render)."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- Registration proof: import THROUGH the registry ---------------------
from instrument_registry import (
    by_name, by_program, registry_table, ALL_INSTRUMENTS,
)
TIMP = by_name("timpani")
print("Registry: by_name('timpani') =", TIMP)
print("Registry: by_program(47) =", by_program(47))
assert TIMP.midi_program == 47
assert by_program(47).name == "Timpani"
print("Registry: ALL_INSTRUMENTS count =", len(ALL_INSTRUMENTS))
table = registry_table()
print("Registry table:\n" + table)
assert "| Percussion | Timpani | 47 |" in table, "timpani row missing from registry_table()"

# ---- Constants through the registry ---------------------------------------
MIDI_PROGRAM = TIMP.midi_program
GM_NAME = TIMP.gm_name
STEM_LABEL = TIMP.stem_label
SOLO_RANGE = TIMP.solo_range
SWEET_SPOT = TIMP.sweet_spot
ZONES = TIMP.zones
ARTICULATIONS = TIMP.articulations
SYNTHESIS = TIMP.synthesis
MODAL_PRESET = TIMP.modal_preset
DRUM606_DEFAULTS = TIMP.drum606_defaults
FM_DEFAULTS = TIMP.fm_defaults
REVERB_TAIL = TIMP.reverb_tail
EQ_BODY = TIMP.eq_body
EQ_PRESENCE = TIMP.eq_presence
EQ_AIR = TIMP.eq_air
PAN = TIMP.pan

print(f"\nTimpani: program={MIDI_PROGRAM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"range={TIMP.range_min}-{TIMP.range_max} sweet={SWEET_SPOT} "
      f"solo={SOLO_RANGE}")
print(f"Timpani: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"modal={MODAL_PRESET!r} drum606={DRUM606_DEFAULTS} fm={FM_DEFAULTS}")
print(f"Timpani: reverb={REVERB_TAIL}s eq={EQ_BODY},{EQ_PRESENCE},{EQ_AIR} pan={PAN}")
from Percussion.timpani.timpani import midi_to_freq, TIMPANI_MODES
print(f"Timpani: C2={midi_to_freq(36):.1f}Hz D2={midi_to_freq(38):.1f}Hz "
      f"A4={midi_to_freq(69):.1f}Hz F4={midi_to_freq(65):.1f}Hz")
print(f"Timpani: TIMPANI_MODES (freq, amp, decay) = {TIMPANI_MODES}")
assert TIMP.in_range(36) and TIMP.in_range(65) and not TIMP.in_range(35)
assert TIMP.in_sweet_spot(45)

# ---- Engine test: UnitMatrixComposer (1 bar, 1 section) --------------------
# Voice stack: Timpani solo line (ch0, pitched melodic channel). Context: ONE
# low bass note an octave+ below (ch1, GM33) — NOT a second melodic patch on
# the same pitches. NO drums stacked on top of the timpani test WAV.
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Timpani", program=MIDI_PROGRAM, channel=0)
comp.add_voice("Bass", program=33, channel=1)
comp.add_section("A", bars=1)

BAR = 1920

# Timpani: tonic-dominant strokes + a roll in the mid zone (D2-A3 set),
# last event ends FLUSH at BAR (terminal landmark -> zero-drift).
u = MusicUnit()
mel = [45, 45, 50, 45, 52, 50, 45]   # A2 A2 D3 A2 E3 D3 A2 (drone + punctuation)
for i, p in enumerate(mel):
    start = i * 240
    end = BAR if i == len(mel) - 1 else start + 200
    u.add_event(MusicEvent(p, 90, start, end))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

# Context: low bass D2 (38) — at/below the timpani's A2 line, no unison clash
u = MusicUnit()
u.add_event(MusicEvent(38, 60, 0, BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/timpani_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---- Render SOLO via discover_soundfont() (FluidR3 preferred) -------------
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/timpani_test.wav"
render_midi(midi_path, wav, solo=0)  # track 1 = Timpani (first voice) ONLY
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
for idx in [45, 46, 47, 48, 49]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Timpani -> {labels[MIDI_PROGRAM]!r}")
assert labels[MIDI_PROGRAM] == "Timpani", f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"
assert STEM_LABEL == "Timpani"

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
assert sf2_name == "Timpani", f"SF2 preset mismatch: {sf2_name!r}"

# ---- Full RenderPipeline stem render — timpani stem label on disk ---------
out_dir = "/opt/data/projects/Instruments/_test/stems_timpani"
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Timpani" in f for f in stem_files), f"no Timpani stem in {stem_files}"
tim_stem = [f for f in stem_files if "Timpani" in f][0]
assert os.path.getsize(os.path.join(out_dir, tim_stem)) > 40, "empty Timpani stem"

# ---- ModalSynth smoke test: custom TIMPANI_MODES (long inharmonic ring) ----
from sound.synthesis.modal import ModalSynth
import numpy as np
sr = 22050
ms = ModalSynth(sample_rate=sr)
audio = ms.render_custom(TIMPANI_MODES, duration=2.0, excitation='impulse')
peak = float(np.max(np.abs(audio)))

def band_ratio(sig, lo, hi, sr):
    seg = sig[:int(0.5 * sr)]
    spec = np.abs(np.fft.rfft(seg))
    fr = np.fft.rfftfreq(len(seg), 1 / sr)
    tot = spec[(fr >= 50) & (fr < 4000)].sum()
    band = spec[(fr >= lo) & (fr < hi)].sum()
    return float(band / max(tot, 1e-9))

late = float(np.sqrt(np.mean(audio[int(1.0 * sr):int(1.5 * sr)] ** 2)) / peak)
p159 = band_ratio(audio, 660, 740, sr)   # 1.59 x 440 Hz region
print(f"\nModalSynth timpani (custom TIMPANI_MODES): peak={peak:.3f} "
      f"late(1.0-1.5s)_rms/peak={late:.3f} 1.59x-partial band energy={p159 * 100:.1f}%")
assert peak > 0, "modal timpani render silent"
assert late > 0.05, "timpani ring collapses — expected a long-sustaining drum"
assert p159 > 0.02, "no 1.59x membrane partial — inharmonic timpano character missing"

# Contrast control: stock 'marimba' preset decays FAST (per-bar strike)
audio_m = ms.render_preset('marimba', duration=2.0, excitation='impulse')
peak_m = float(np.max(np.abs(audio_m)))
late_m = float(np.sqrt(np.mean(audio_m[int(1.0 * sr):int(1.5 * sr)] ** 2)) / peak_m)
print(f"Contrast ModalSynth 'marimba' preset: peak={peak_m:.3f} "
      f"late(1.0-1.5s)_rms/peak={late_m:.4f} (fast decay)")
assert late > 3 * late_m, "timpani should out-ring the marimba preset by >3x"

# Stock 'drum' preset is the closest stock bank (documented as too-fast)
audio_d = ms.render_preset('drum', duration=2.0, excitation='impulse')
print(f"Stock 'drum' preset (MODAL_PRESET): peak={float(np.max(np.abs(audio_d))):.3f}")

# ---- DrumSynth606 alternative: pitch-swept-sine thump ----------------------
from sound.synthesis.drum_synth_606 import DrumSynth606
ds = DrumSynth606(sample_rate=sr)
thumb = ds.tom(freq=DRUM606_DEFAULTS["freq"], decay=DRUM606_DEFAULTS["decay"],
               pitch_sweep=DRUM606_DEFAULTS["pitch_sweep"])
print(f"DrumSynth606 tom (DRUM606_DEFAULTS): peak={float(np.max(np.abs(thumb))):.3f} "
      f"len={len(thumb) / sr:.2f}s")
assert float(np.max(np.abs(thumb))) > 0, "606 timpani thump silent"

print("\nALL CHECKS PASSED")
