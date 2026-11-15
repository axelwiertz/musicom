# -*- coding: utf-8 -*-
"""Verify Woodblock constants end-to-end — through the REGISTRY, SOLO render.

Pattern from _test/verify_marimba.py / verify_agogo.py, with the 2026-09-01 fixes:
  * import constants via instrument_registry.by_name (proves registration)
  * audio check is the INSTRUMENT SOLO only (no unison doubling -> no comb buzz)
  * SoundFont resolved by discover_soundfont() (FluidR3 preferred)
"""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")
sys.path.insert(0, "/opt/data/repos/musicom")

from instrument_registry import by_name, by_program, ALL_INSTRUMENTS, WOODBLOCK

inst = by_name("woodblock")
assert inst is not None
print(f"registry: by_name('woodblock') -> {inst!r}")
print(f"registry: by_name('Woodblock') -> {by_name('Woodblock')!r}")
print(f"registry: by_program(115) -> {by_program(115)!r}")
print(f"registry: WOODBLOCK is ALL_INSTRUMENTS['woodblock'] -> "
      f"{WOODBLOCK is ALL_INSTRUMENTS['woodblock']}")
print(f"registry: family={inst.family} program={inst.midi_program} "
      f"range={inst.range_min}-{inst.range_max} solo={inst.solo_range} "
      f"sweet={inst.sweet_spot}")
print(f"registry: stem_label={inst.stem_label!r} reverb={inst.reverb_tail} pan={inst.pan}")
print(f"registry: synthesis={inst.synthesis} modal_preset={inst.modal_preset}")
print(f"registry: woodblock_modes={inst.woodblock_modes}")
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
WOODBLOCK_MODES = inst.woodblock_modes
from Percussion.woodblock.woodblock import midi_to_freq  # noqa: E402

print(f"Woodblock: program={PGM} gm={inst.gm_name!r} stem={STEM_LABEL!r} "
      f"sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Woodblock: zones={ZONES}")
print(f"Woodblock: art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"modal_preset={MODAL_PRESET} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Woodblock: C5={midi_to_freq(72):.1f}Hz C6={midi_to_freq(84):.1f}Hz")

# ---------------------------------------------------------------- composition
from structures import MusicEvent, MusicUnit  # noqa: E402
from workflows.unitmatrix_composer import UnitMatrixComposer  # noqa: E402

BAR = 1920
comp = UnitMatrixComposer(bpm=104, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Woodblock", program=PGM, channel=0)
comp.add_voice("Drums", program=0, channel=9)   # context only (channel 9)
comp.add_section("A", bars=1)

# Woodblock SOLO part: a dry 8th/16th ostinato on the patch's home note 72
# (C5, measured ~430 Hz), accents + ghosts + a double-stroke pickup.
# One pitch only — the GM115 patch does not transpose (measured quirk).
u = MusicUnit()
strokes = [
    (0, 106, 120), (240, 36, 90), (360, 90, 90),          # accent, ghost, double-a
    (480, 36, 90), (600, 90, 90), (720, 92, 110),
    (840, 36, 90), (960, 60, 90), (1080, 92, 110),        # stick_click, 8ths
    (1200, 36, 90), (1320, 90, 90), (1440, 106, 120),
    (1560, 36, 90), (1680, 90, 90), (1800, 90, 60), (1860, 90, 60),  # pickup
]
for start, vel, dur in strokes:
    u.add_event(MusicEvent(72, vel, start, start + dur))
u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))   # terminal landmark
comp.set_unit(0, 0, u)

# Drums context: low kick + hat ticks only (channel 9) — never a second
# melodic patch on the woodblock's pitch.
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

midi_path = "/opt/data/projects/Instruments/_test/woodblock_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---------------------------------------------------------------- solo render
from _test.render_audio import render_midi, spectral_buzz_check  # noqa: E402

wav = "/opt/data/projects/Instruments/_test/woodblock_test.wav"
render_midi(midi_path, wav, solo=0)   # track 1 = Woodblock (first voice), SOLO
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# ---------------------------------------------------------------- stem labels
import inspect  # noqa: E402
import re  # noqa: E402

from sound.render.pipeline import RenderPipeline  # noqa: E402

src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print("\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
for idx in [113, 114, 115, 116]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Woodblock -> {labels[PGM]!r}")
assert labels[PGM] == "Woodblock", f"stem label mismatch: {labels[PGM]!r}"
assert STEM_LABEL == "Woodblock"

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
assert sf2_name == "Woodblock", f"SF2 preset mismatch: {sf2_name!r}"

# ---------------------------------------------------------------- stems on disk
out_dir = "/opt/data/projects/Instruments/_test/stems_woodblock"
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    print(f"  {f} ({os.path.getsize(os.path.join(out_dir, f))} bytes)")
matches = [f for f in stem_files if "Woodblock" in f]
assert matches, f"no Woodblock stem in {stem_files}"
assert os.path.getsize(os.path.join(out_dir, matches[0])) > 40

# ---------------------------------------------------------------- ModalSynth
import numpy as np  # noqa: E402

from sound.synthesis.modal import ModalSynth  # noqa: E402

ms = ModalSynth(sample_rate=22050)
audio = ms.render_custom(WOODBLOCK_MODES, duration=0.5, excitation="impulse")
peak = float(np.max(np.abs(audio)))
head = float(np.sqrt(np.mean(audio[:441] ** 2)))
mid = float(np.sqrt(np.mean(audio[int(0.03 * 22050):int(0.06 * 22050)] ** 2)))
late = float(np.sqrt(np.mean(audio[int(0.25 * 22050):int(0.5 * 22050)] ** 2)))
print(f"\nModalSynth WOODBLOCK_MODES: peak={peak:.3f} head_rms={head:.4f} "
      f"mid_rms={mid:.4f} late_rms={late:.4f} late/peak={late / peak:.5f}")
assert peak > 0, "modal woodblock render silent"
assert mid / head < 0.35, "woodblock does not decay fast enough (should be a tock)"
assert late / peak < 0.005, "woodblock rings too long — not a tock"

# partial ratio check (measured FluidR3 ratios baked into the bank)
spec = np.abs(np.fft.rfft(audio[:2048]))
freqs = np.fft.rfftfreq(2048, 1 / 22050)


def band(f, w=15):
    return float(spec[(freqs > f - w) & (freqs < f + w)].max())


f0 = band(430.0)
print("  partials vs f0 (430 Hz):")
for ratio, freq in ((1.96, 843.0), (2.18, 937.0), (3.44, 1480.0), (5.50, 2365.0)):
    print(f"    {ratio:4.2f}x ({freq:6.0f} Hz) = {band(freq) / f0 * 100:5.1f}% of f0")
assert band(937.0) / f0 > 0.05, "2.18x wooden partial missing — wrong timbre"

print("\nALL CHECKS PASSED")
