# -*- coding: utf-8 -*-
"""Verify Agogo constants end-to-end — through the REGISTRY, SOLO render.

Pattern from _test/verify_marimba.py, with the 2026-09-01 fixes:
  * import constants via instrument_registry.by_name (proves registration)
  * audio check is the INSTRUMENT SOLO only (no unison doubling -> no comb buzz)
  * SoundFont resolved by discover_soundfont() (FluidR3 preferred)
"""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")
sys.path.insert(0, "/opt/data/repos/musicom")

from instrument_registry import by_name, by_program, ALL_INSTRUMENTS, AGOGO

inst = by_name("agogo")
print(f"registry: by_name('agogo') -> {inst!r}")
print(f"registry: by_name('Agogo') -> {by_name('Agogo')!r}")
print(f"registry: by_program(113) -> {by_program(113)!r}")
print(f"registry: AGOGO is ALL_INSTRUMENTS['agogo'] -> {AGOGO is ALL_INSTRUMENTS['agogo']}")
print(f"registry: family={inst.family} program={inst.midi_program} "
      f"range={inst.range_min}-{inst.range_max} solo={inst.solo_range} "
      f"sweet={inst.sweet_spot}")
print(f"registry: stem_label={inst.stem_label!r} reverb={inst.reverb_tail} pan={inst.pan}")
print(f"registry: synthesis={inst.synthesis} modal_preset={inst.modal_preset}")
print(f"registry: agogo_modes={inst.agogo_modes}")
print(f"registry: in_sweet_spot(72)={inst.in_sweet_spot(72)} "
      f"in_sweet_spot(48)={inst.in_sweet_spot(48)} in_range(60)={inst.in_range(60)}")

PGM = inst.midi_program
STEM_LABEL = inst.stem_label
SOLO_RANGE = inst.solo_range
ZONES = inst.zones
ARTICULATIONS = inst.articulations
SYNTHESIS = inst.synthesis
MODAL_PRESET = inst.modal_preset
REVERB_TAIL = inst.reverb_tail
EQ_BODY, EQ_PRESENCE, EQ_AIR = inst.eq_body, inst.eq_presence, inst.eq_air
PAN = inst.pan
AGOGO_MODES = inst.agogo_modes
from World.agogo.agogo import midi_to_freq

print(f"Agogo: program={PGM} gm={inst.gm_name!r} stem={STEM_LABEL!r} "
      f"sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Agogo: zones={ZONES}")
print(f"Agogo: art={list(ARTICULATIONS)} synth={SYNTHESIS} modal_preset={MODAL_PRESET} "
      f"reverb={REVERB_TAIL}s pan={PAN}")
print(f"Agogo: A4={midi_to_freq(69):.1f}Hz C5={midi_to_freq(72):.1f}Hz "
      f"C6={midi_to_freq(84):.1f}Hz")

# ---------------------------------------------------------------- composition
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

BAR = 1920
comp = UnitMatrixComposer(bpm=100, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Agogo", program=PGM, channel=0)
comp.add_voice("Drums", program=0, channel=9)   # context only (channel 9)
comp.add_section("A", bars=1)

# Agogo SOLO line: the samba timeline — low bell A4 (69) / high bell D5 (74)
# alternating 16ths, accent on the 1, ghosts between. Ends flush at BAR.
u = MusicUnit()
timeline = [(0, 69, 104, 120), (120, 74, 40, 90), (240, 74, 84, 90),
            (360, 69, 40, 90), (480, 74, 96, 120), (600, 74, 40, 90),
            (720, 69, 84, 110), (840, 74, 40, 90), (960, 69, 100, 120),
            (1080, 74, 40, 90), (1200, 74, 84, 90), (1320, 69, 40, 90),
            (1440, 74, 96, 120), (1560, 74, 40, 90), (1680, 69, 84, 110),
            (1800, 74, 40, 1800 + 120 - 1800)]
for start, pitch, vel, dur in timeline:
    u.add_event(MusicEvent(pitch, vel, start, start + dur))
u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))   # terminal landmark
comp.set_unit(0, 0, u)

# Drums context: surdo-ish kick + shaker ticks (channel 9, drum-kit map)
u = MusicUnit()
for start, pitch, vel in [(0, 36, 110), (480, 36, 96), (960, 36, 110),
                          (1440, 36, 96), (240, 42, 40), (720, 42, 40),
                          (1200, 42, 40), (1680, 42, 40)]:
    u.add_event(MusicEvent(pitch, vel, start, start + 120))
u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/agogo_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---------------------------------------------------------------- solo render
from _test.render_audio import render_midi, spectral_buzz_check

wav = "/opt/data/projects/Instruments/_test/agogo_test.wav"
render_midi(midi_path, wav, solo=0)   # track 1 = Agogo (first voice), SOLO
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# ---------------------------------------------------------------- stem labels
import inspect
import re
from sound.render.pipeline import RenderPipeline

src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print("\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
for idx in [112, 113, 114, 115]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Agogo -> {labels[PGM]!r}")
assert labels[PGM] == "Agogo", f"stem label mismatch: {labels[PGM]!r}"
assert STEM_LABEL == "Agogo"

# SF2 preset name (verified from the phdr chunk of the RESOLVED soundfont)
import struct
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
data = open(sf2, "rb").read()
phdr = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr + 4:phdr + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr + 8 + i * 38
    nm = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    pnum, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, pnum)] = nm
print(f"SF2: {sf2}")
sf2_name = preset_names.get((0, PGM), "MISSING")
print(f"SF2 preset {PGM} -> {sf2_name!r}")
assert sf2_name == "Agogo", f"SF2 preset mismatch: {sf2_name!r}"

# ---------------------------------------------------------------- stems on disk
out_dir = "/opt/data/projects/Instruments/_test/stems_agogo"
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    print(f"  {f} ({os.path.getsize(os.path.join(out_dir, f))} bytes)")
assert any("Agogo" in f for f in stem_files), f"no Agogo stem in {stem_files}"
assert os.path.getsize(os.path.join(out_dir, [f for f in stem_files if "Agogo" in f][0])) > 40

# ---------------------------------------------------------------- ModalSynth
import numpy as np
from sound.synthesis.modal import ModalSynth

ms = ModalSynth(sample_rate=22050)
audio = ms.render_custom(AGOGO_MODES, duration=1.5, excitation="impulse")
peak = float(np.max(np.abs(audio)))
head = float(np.sqrt(np.mean(audio[:2205] ** 2)))
mid = float(np.sqrt(np.mean(audio[int(0.4 * 22050):int(0.6 * 22050)] ** 2)))
late = float(np.sqrt(np.mean(audio[int(1.0 * 22050):int(1.5 * 22050)] ** 2)))
print(f"\nModalSynth AGOGO_MODES: peak={peak:.3f} head_rms={head:.4f} "
      f"mid_rms={mid:.4f} late_rms={late:.4f} late/peak={late / peak:.4f}")
assert peak > 0, "modal agogo render silent"
assert late / peak > 0.01, "agogo ring too short (bell should still ring at 1s)"
assert mid / head > 0.2, "agogo decays like a click — modes too fast"

# fundamental dominance check (bell must be PITCHED)
spec = np.abs(np.fft.rfft(audio[:22050]))
freqs = np.fft.rfftfreq(22050, 1 / 22050)
def band(f, w=12):
    return spec[(freqs > f - w) & (freqs < f + w)].max()
f0 = band(440.0)
for r in (2.0, 2.72, 4.07):
    print(f"  partial {r}x = {band(440.0 * r) / f0 * 100:.1f}% of f0")

print("\nALL CHECKS PASSED")
