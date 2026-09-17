# -*- coding: utf-8 -*-
"""Verify Harpsichord constants work with musicom engine (registry-backed, solo render)."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- Registration proof: import THROUGH the registry ---------------------
from instrument_registry import (
    by_name, by_program, registry_table, ALL_INSTRUMENTS,
)

HC = by_name("harpsichord")
print("Registry: by_name('harpsichord') =", HC)
print("Registry: by_program(6) =", by_program(6))
assert HC.midi_program == 6
assert by_program(6).name == "Harpsichord"
print("Registry: ALL_INSTRUMENTS count =", len(ALL_INSTRUMENTS))
table = registry_table()
assert "| Keys | Harpsichord | 6 |" in table, "harpsichord row missing from registry_table()"
print("Registry row: | Keys | Harpsichord | 6 | 29-89 | ... OK")

# ---- Constants through the registry ---------------------------------------
MIDI_PROGRAM = HC.midi_program
GM_NAME = HC.gm_name
STEM_LABEL = HC.stem_label
SOLO_RANGE = HC.solo_range
SWEET_SPOT = HC.sweet_spot
ZONES = HC.zones
ARTICULATIONS = HC.articulations
SYNTHESIS = HC.synthesis
MODAL_PRESET = HC.modal_preset
KARPLUS_DEFAULTS = HC.karplus_defaults
from Keys.harpsichord.harpsichord import HARPSICHORD_MODES as HM, midi_to_freq, FM_DEFAULTS
REVERB_TAIL = HC.reverb_tail
EQ_BODY = HC.eq_body
EQ_PRESENCE = HC.eq_presence
EQ_AIR = HC.eq_air
PAN = HC.pan

print(f"\nHarpsichord: program={MIDI_PROGRAM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"range={HC.range_min}-{HC.range_max} sweet={SWEET_SPOT} solo={SOLO_RANGE}")
print(f"Harpsichord: zones={ZONES}")
print(f"Harpsichord: art={list(ARTICULATIONS)} synth={SYNTHESIS} modal={MODAL_PRESET!r}")
print(f"Harpsichord: karplus={KARPLUS_DEFAULTS} fm={FM_DEFAULTS}")
print(f"Harpsichord: F1={midi_to_freq(29):.1f}Hz C3={midi_to_freq(48):.1f}Hz "
      f"A4={midi_to_freq(69):.1f}Hz C6={midi_to_freq(84):.1f}Hz F6={midi_to_freq(89):.1f}Hz")
assert HC.in_range(29) and HC.in_range(89) and not HC.in_range(28)
assert not HC.in_range(90)   # the 61-key compass ends at F6
assert HC.in_sweet_spot(69)
# 8'+4' registration: the octave DOUBLE layer is a real mode (0.55 amp),
# stacked with the 8' octave partial (0.45) — octave band total strongest
assert [round(f / 440.0, 2) for f, _, _ in HM] == [1.0, 2.0, 2.0, 3.0, 4.0, 6.0]
assert HC.in_sweet_spot(60) and HC.in_sweet_spot(84)

# ---- Engine test: UnitMatrixComposer (1 bar, 1 section) --------------------
# Voice stack: Harpsichord solo (ch0). Context: ONE low bass note an octave+
# below (ch1, GM33) — NOT a second melodic patch on the same pitches.
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Harpsichord", program=MIDI_PROGRAM, channel=0)
comp.add_voice("Bass", program=33, channel=1)
comp.add_section("A", bars=1)

BAR = 1920

# Harpsichord: baroque-style melodic figure with a trill tail —
# D4 F4 A4 D5 F5 A4 F4 D4 — last event ends FLUSH at BAR (terminal landmark).
u = MusicUnit()
line = [62, 65, 69, 74, 77, 69, 65, 62]
for i, p in enumerate(line):
    start = i * 240
    end = BAR if i == len(line) - 1 else start + 220
    u.add_event(MusicEvent(p, 88, start, end))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

# Context: low bass D2 (38) — well below the harpsichord's sweet band
u = MusicUnit()
u.add_event(MusicEvent(38, 58, 0, BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/harpsichord_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---- Render SOLO via discover_soundfont() (FluidR3 preferred) -------------
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/harpsichord_test.wav"
render_midi(midi_path, wav, solo=0)  # track 1 = Harpsichord (first voice) ONLY
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
for idx in [4, 5, 6, 7, 8]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Harpsichord -> {labels[MIDI_PROGRAM]!r}")
assert labels[MIDI_PROGRAM] == "Harpsichord", f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"
assert STEM_LABEL == "Harpsichord"

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
assert sf2_name == "Harpsichord", f"SF2 preset mismatch: {sf2_name!r}"

# ---- Full RenderPipeline stem render — harpsichord stem label on disk -----
out_dir = "/opt/data/projects/Instruments/_test/stems_harpsichord"
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Harpsichord" in f for f in stem_files), f"no harpsichord stem in {stem_files}"
hc_stem = [f for f in stem_files if "Harpsichord" in f][0]
assert os.path.getsize(os.path.join(out_dir, hc_stem)) > 40, "empty harpsichord stem"

# ---- Empirical FluidR3 pitch sweep (RMS, notes 29-89) ---------------------
# The 61-key compass must be playable across the whole span, no gaps.
import numpy as np
import wave
def rms_at(pitch, vel=88):
    pth = f"/tmp/hc_sweep_{pitch}.mid"
    c = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice("Harpsichord", program=MIDI_PROGRAM, channel=0)
    c.add_section("A", bars=1)
    u = MusicUnit()
    u.add_event(MusicEvent(pitch, vel, 0, 1920))
    c.set_unit(0, 0, u)
    ok, m2 = c.validate()
    assert ok, m2
    c.to_midi(pth)
    out = f"/tmp/hc_sweep_{pitch}.wav"
    render_midi(pth, out, solo=None)  # single-voice MIDI already
    w = wave.open(out, "rb")
    n = w.getnframes()
    d = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    w.close()
    os.unlink(pth); os.unlink(out)
    return np.sqrt(np.mean(d ** 2))

sweep_notes = [29, 36, 43, 50, 57, 64, 71, 78, 85, 89]
print("\nFluidR3 pitch sweep (notes 29-89):")
vals = []
for p_ in sweep_notes:
    r = rms_at(p_)
    vals.append(r)
    print(f"  note {p_:>2}: rms={r:.4f}")
audible = sum(1 for v in vals if v > 1e-3)
print(f"  audible {audible}/{len(vals)}")
assert audible == len(vals), "pitch sweep found gaps — SF2 clips a composition"

# ---- Karplus-Strong PRIMARY: ring between harp and sitar ------------------
from sound.synthesis.karplus_strong import karplus_strong
sr = 44100
ks = karplus_strong(pitch=69, dur=3.0, vel=100, loop_gain=KARPLUS_DEFAULTS["loop_gain"])
ks_harp = karplus_strong(pitch=69, dur=3.0, vel=100, loop_gain=0.9985)   # harp-class
ks_sitar = karplus_strong(pitch=69, dur=3.0, vel=100, loop_gain=0.9975)  # sitar-class
ks_dull = karplus_strong(pitch=69, dur=3.0, vel=100, loop_gain=0.990)    # dull control
kp, kh, ksi, kd = (np.max(np.abs(a)) for a in (ks, ks_harp, ks_sitar, ks_dull))
kt = np.sqrt(np.mean(ks[1 * sr:2 * sr] ** 2)) / kp if kp > 0 else 1.0
kt_harp = np.sqrt(np.mean(ks_harp[1 * sr:2 * sr] ** 2)) / kh if kh > 0 else 1.0
kt_sitar = np.sqrt(np.mean(ks_sitar[1 * sr:2 * sr] ** 2)) / ksi if ksi > 0 else 1.0
kt_dull = np.sqrt(np.mean(ks_dull[1 * sr:2 * sr] ** 2)) / kd if kd > 0 else 1.0
print(f"\nKarplus-Strong harpsichord loop_gain={KARPLUS_DEFAULTS['loop_gain']}: "
      f"tail_rms/peak(1-2s)={kt:.4f} (harp 0.9985: {kt_harp:.4f}, "
      f"sitar 0.9975: {kt_sitar:.4f}, dull control 0.990: {kt_dull:.4f})")
assert kp > 0, "KS harpsichord render silent"
assert kt > 2 * kt_dull, "harpsichord KS shows no ring advantage over dull control"
assert kt_harp > kt > kt_sitar, "harpsichord loop_gain must ring between harp and sitar"

# partial structure: octave-double present (the 4' choir lesson)
spec = np.abs(np.fft.rfft(ks[: int(0.5 * sr)]))
freqs = np.fft.rfftfreq(int(0.5 * sr), 1 / sr)
def band(f, tol=12.0):
    sel = (freqs >= f - tol) & (freqs <= f + tol)
    return spec[sel].max() if sel.any() else 0.0
f0, f2, f3 = band(440.0), band(880.0), band(1320.0)
print(f"  KS partials: f0={f0:.1f} 2x={f2:.1f} ({(f2 / f0) * 100:.1f}% of f0) "
      f"3x={f3:.1f} ({(f3 / f0) * 100:.1f}% of f0)")
assert f0 > 0 and f3 < f0 and f3 <= f2, "harpsichord harmonic stack must decay upward"

# ---- ModalSynth 'string' fallback + HARPSICHORD_MODES ring check ----------
from sound.synthesis.modal import ModalSynth
ms = ModalSynth(sample_rate=sr)
audio = ms.render_custom(HM, duration=3.0, excitation="impulse")
peak = np.max(np.abs(audio))
late = np.sqrt(np.mean(audio[int(1.0 * sr):int(1.5 * sr)] ** 2))
late_ratio = late / peak if peak > 0 else 1.0
mar = ms.render_preset("marimba", duration=3.0, excitation="impulse")
mar_late = np.sqrt(np.mean(mar[int(1.0 * sr):int(1.5 * sr)] ** 2)) / np.max(np.abs(mar))
print(f"\nModalSynth HARPSICHORD_MODES: peak={peak:.3f} late(1.0-1.5s)_rms/peak={late_ratio:.3f}")
print(f"  marimba stock preset late(1.0-1.5s)_rms/peak={mar_late:.4f}")
assert peak > 0, "harpsichord modal render silent"
assert late_ratio > 0.01, "harpsichord string decayed too fast — expected a long ring"
assert late_ratio > 3 * mar_late, "harpsichord shows no ring advantage over the marimba preset"

# octave-double check: 4' choir modeled as explicit 2x mode at ~half amplitude
oct2 = sum(a for f, a, _ in HM if abs(f / 440.0 - 2.0) < 0.01)
fund = sum(a for f, a, _ in HM if abs(f / 440.0 - 1.0) < 0.01)
print(f"  modal octave-band amplitude {oct2:.2f} vs fundamental {fund:.2f} "
      f"(ratio {oct2 / fund:.2f} — the 4' choir doubling)")
assert oct2 > 0.4 and oct2 <= fund, "4' choir octave-double missing or dominant"

print("\nALL CHECKS PASSED")
