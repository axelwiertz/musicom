# -*- coding: utf-8 -*-
"""Verify Melodic Tom constants end-to-end — through the REGISTRY, SOLO render.

Pattern from _test/verify_woodblock.py (2026-09-01 fixes):
  * import constants via instrument_registry.by_name (proves registration)
  * audio check is the INSTRUMENT SOLO only (no unison doubling -> no comb buzz)
  * SoundFont resolved by discover_soundfont() (FluidR3 preferred)
"""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")
sys.path.insert(0, "/opt/data/repos/musicom")

from instrument_registry import by_name, by_program, ALL_INSTRUMENTS, MELODIC_TOM  # noqa: E402

inst = by_name("melodic tom")
assert inst is not None
print(f"registry: by_name('melodic tom') -> {inst!r}")
print(f"registry: by_name('Melodic Tom') -> {by_name('Melodic Tom')!r}")
print(f"registry: by_program(117) -> {by_program(117)!r}")
print(f"registry: MELODIC_TOM is ALL_INSTRUMENTS['melodic_tom'] -> "
      f"{MELODIC_TOM is ALL_INSTRUMENTS['melodic_tom']}")
print(f"registry: family={inst.family} program={inst.midi_program} "
      f"range={inst.range_min}-{inst.range_max} solo={inst.solo_range} "
      f"sweet={inst.sweet_spot}")
print(f"registry: stem_label={inst.stem_label!r} reverb={inst.reverb_tail} pan={inst.pan}")
print(f"registry: synthesis={inst.synthesis} modal_preset={inst.modal_preset}")
print(f"registry: melodic_tom_modes={inst.melodic_tom_modes}")
print(f"registry: in_sweet_spot(60)={inst.in_sweet_spot(60)} "
      f"in_sweet_spot(30)={inst.in_sweet_spot(30)} in_range(36)={inst.in_range(36)}")

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
MELODIC_TOM_MODES = inst.melodic_tom_modes
from Percussion.melodic_tom.melodic_tom import midi_to_freq  # noqa: E402

print(f"Melodic Tom: program={PGM} gm={inst.gm_name!r} stem={STEM_LABEL!r} "
      f"sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Melodic Tom: zones={ZONES}")
print(f"Melodic Tom: art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"modal_preset={MODAL_PRESET} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Melodic Tom: C3={midi_to_freq(48):.1f}Hz C4={midi_to_freq(60):.1f}Hz "
      f"C5={midi_to_freq(72):.1f}Hz")

# ---------------------------------------------------------------- composition
from structures import MusicEvent, MusicUnit  # noqa: E402
from workflows.unitmatrix_composer import UnitMatrixComposer  # noqa: E402

BAR = 1920
comp = UnitMatrixComposer(bpm=104, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Melodic Tom", program=PGM, channel=0)
comp.add_voice("Drums", program=0, channel=9)   # context only (channel 9)
comp.add_section("A", bars=1)

# Melodic Tom SOLO part: a 70s/80s-style 16th-note fill in the sweet spot
# (A3-F4), accent + ghosts + a landing note. 16 sixteenths x 120 ticks =
# 1 bar. One voice, one track — no unison doubling (comb-buzz rule).
u = MusicUnit()
fill = [
    (0, 104, 80), (120, 96, 70), (240, 104, 80), (360, 96, 70),
    (480, 112, 100), (600, 96, 70), (720, 104, 80), (840, 96, 70),
    (960, 104, 80), (1080, 96, 70), (1200, 104, 80), (1320, 96, 70),
    (1440, 112, 100), (1560, 96, 70), (1680, 104, 80), (1800, 112, 120),
]
for start, vel, dur in fill:
    # notes alternate A3(57) / C4(60) / E4(64) / F4(65) in the sweet spot
    n = [57, 60, 64, 65][(start // 120) % 4]
    u.add_event(MusicEvent(n, vel, start, start + dur))
u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))   # terminal landmark
comp.set_unit(0, 0, u)

# Drums context: low kick + hat ticks only (channel 9) — never a second
# melodic patch on the tom's pitches.
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

midi_path = "/opt/data/projects/Instruments/_test/melodic_tom_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---------------------------------------------------------------- solo render
from _test.render_audio import render_midi, spectral_buzz_check  # noqa: E402

wav = "/opt/data/projects/Instruments/_test/melodic_tom_test.wav"
render_midi(midi_path, wav, solo=0)   # track 1 = Melodic Tom (first voice), SOLO
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# per-16th levels — documents the pipeline every-2nd-note-on quirk (the
# even hits read ~6-8 dB quieter at fill tempo; the ring masks the gap)
import numpy as np  # noqa: E402
import wave  # noqa: E402

w = wave.open(wav, "rb")
sr = w.getframerate()
n = w.getnframes()
data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
w.close()
sp16 = 60.0 / 104 / 4
levels = []
for i in range(16):
    seg = data[int(i * sp16 * sr):int((i + 1) * sp16 * sr)]
    levels.append(float(np.sqrt(np.mean(seg ** 2))))
print("per-16th RMS (pipeline note-on alternation visible as level dip on "
      "even hits):")
print("  " + " ".join(f"{v:.3f}" for v in levels))

# ---------------------------------------------------------------- stem labels
import inspect  # noqa: E402
import re  # noqa: E402

from sound.render.pipeline import RenderPipeline  # noqa: E402

src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print("\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
for idx in [115, 116, 117, 118]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Melodic Tom -> {labels[PGM]!r}")
assert labels[PGM] == "Melodic Tom", f"stem label mismatch: {labels[PGM]!r}"
assert STEM_LABEL == "Melodic Tom"

# SF2 preset name (verified from the phdr chunk of the RESOLVED soundfont)
import struct  # noqa: E402

from sound.render.fluidsynth import discover_soundfont  # noqa: E402

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
assert sf2_name == "Melodic Tom", f"SF2 preset mismatch: {sf2_name!r}"

# ---------------------------------------------------------------- stems on disk
out_dir = "/opt/data/projects/Instruments/_test/stems_melodic_tom"
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    print(f"  {f} ({os.path.getsize(os.path.join(out_dir, f))} bytes)")
matches = [f for f in stem_files if "Melodic_Tom" in f]
assert matches, f"no Melodic_Tom stem in {stem_files}"
assert os.path.getsize(os.path.join(out_dir, matches[0])) > 40

# ---------------------------------------------------------------- ModalSynth
from sound.synthesis.modal import ModalSynth  # noqa: E402

ms = ModalSynth(sample_rate=22050)
audio = ms.render_custom(MELODIC_TOM_MODES, duration=1.0, excitation="impulse")
peak = float(np.max(np.abs(audio)))
head = float(np.sqrt(np.mean(audio[:441] ** 2)))
mid = float(np.sqrt(np.mean(audio[int(0.05 * 22050):int(0.2 * 22050)] ** 2)))
late = float(np.sqrt(np.mean(audio[int(0.5 * 22050):int(1.0 * 22050)] ** 2)))
print(f"\nModalSynth MELODIC_TOM_MODES: peak={peak:.3f} head_rms={head:.4f} "
      f"mid_rms={mid:.4f} late_rms={late:.4f} late/peak={late / peak:.5f}")
assert peak > 0, "modal tom render silent"
assert mid / head < 0.9, "tom does not decay (should be a struck drum)"
assert late / peak < 0.10, "tom rings too long (should be ~0.5-1.0 s)"

# partial ratio check (membrane Bessel partners baked into the bank)
spec = np.abs(np.fft.rfft(audio[:4096]))
freqs = np.fft.rfftfreq(4096, 1 / 22050)


def band(f, w=15):
    return float(spec[(freqs > f - w) & (freqs < f + w)].max())


f0 = band(174.0)
print("  partials vs f0 (174 Hz):")
for ratio, freq in ((1.59, 277.0), (2.14, 372.0), (2.78, 483.0), (3.56, 620.0)):
    print(f"    {ratio:4.2f}x ({freq:6.0f} Hz) = {band(freq) / f0 * 100:5.1f}% of f0")
assert band(277.0) / f0 > 0.05, "1.59x membrane partner missing — wrong timbre"

print("\nALL CHECKS PASSED")
