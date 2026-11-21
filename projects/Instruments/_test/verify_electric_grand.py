# -*- coding: utf-8 -*-
"""Verify Electric Grand Piano (GM2) end-to-end — through the REGISTRY, SOLO render.

Pattern from _test/verify_blown_bottle.py, with the 2026-09-01 fixes:
  * import constants via instrument_registry.by_name (proves registration)
  * audio check is the INSTRUMENT SOLO only (no unison doubling -> no comb buzz)
  * SoundFont resolved by discover_soundfont() (FluidR3 preferred)
  * Karplus-Strong smoke test with the instrument's own KARPLUS_DEFAULTS
    (the CP is a struck real piano string through a magnetic pickup)
"""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")
sys.path.insert(0, "/opt/data/repos/musicom")

from instrument_registry import by_name, by_program, ALL_INSTRUMENTS, ELECTRIC_GRAND  # noqa: E402

inst = by_name("electric grand piano")
assert inst is not None
print(f"registry: by_name('electric grand piano') -> {inst!r}")
print(f"registry: by_name('Electric Grand Piano') -> {by_name('Electric Grand Piano')!r}")
print(f"registry: by_program(2) -> {by_program(2)!r}")
print(f"registry: ELECTRIC_GRAND is ALL_INSTRUMENTS['electric_grand'] -> "
      f"{ELECTRIC_GRAND is ALL_INSTRUMENTS['electric_grand']}")
print(f"registry: family={inst.family} program={inst.midi_program} "
      f"range={inst.range_min}-{inst.range_max} solo={inst.solo_range} "
      f"sweet={inst.sweet_spot}")
print(f"registry: stem_label={inst.stem_label!r} reverb={inst.reverb_tail} pan={inst.pan}")
print(f"registry: synthesis={inst.synthesis} karplus_defaults={inst.karplus_defaults}")
print(f"registry: in_sweet_spot(72)={inst.in_sweet_spot(72)} "
      f"in_sweet_spot(30)={inst.in_sweet_spot(30)} in_range(108)={inst.in_range(108)}")

PGM = inst.midi_program
STEM_LABEL = inst.stem_label
SOLO_RANGE = inst.solo_range
ZONES = inst.zones
ARTICULATIONS = inst.articulations
SYNTHESIS = inst.synthesis
KARPLUS_DEFAULTS = inst.karplus_defaults
MODAL_PRESET = inst.modal_preset
ELECTRIC_GRAND_MODES = inst.electric_grand_modes
FM_DEFAULTS = inst.fm_defaults
REVERB_TAIL = inst.reverb_tail
EQ_BODY, EQ_PRESENCE, EQ_AIR = inst.eq_body, inst.eq_presence, inst.eq_air
PAN = inst.pan
from Keys.electric_grand.electric_grand import midi_to_freq  # noqa: E402

print(f"Electric Grand: program={PGM} gm={inst.gm_name!r} stem={STEM_LABEL!r} "
      f"sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Electric Grand: zones={ZONES}")
print(f"Electric Grand: art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"modal_preset={MODAL_PRESET} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Electric Grand: A0={midi_to_freq(21):.1f}Hz C4={midi_to_freq(60):.1f}Hz "
      f"C6={midi_to_freq(84):.1f}Hz C8={midi_to_freq(108):.1f}Hz")

# ---------------------------------------------------------------- composition
from structures import MusicEvent, MusicUnit  # noqa: E402
from workflows.unitmatrix_composer import UnitMatrixComposer  # noqa: E402

BAR = 1920
comp = UnitMatrixComposer(bpm=104, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("ElectricGrand", program=PGM, channel=0)
comp.add_voice("Drums", program=0, channel=9)   # context only (channel 9)
comp.add_section("A", bars=1)

# Electric Grand SOLO part: a glassy sweet-spot hook (C5-E5-G5-C6-G5-E5-C5 —
# the CP signature attack line) + one low C2 pedal (octave+ below, same patch)
# so the arrangement has a context bass without a second melodic patch.
u = MusicUnit()
u.add_event(MusicEvent(36, 55, 0, BAR))            # low C2 pedal (octaves below)
line = [
    (0, 72, 85, 300),      # C5 glassy
    (300, 76, 80, 200),    # E5
    (500, 79, 88, 260),    # G5 accent
    (760, 84, 92, 420),    # C6 glassy top
    (1180, 79, 76, 220),   # G5
    (1400, 76, 72, 200),   # E5
    (1600, 72, 84, 320),   # C5 -> ends flush at BAR
]
for start, p, vel, dur in line:
    u.add_event(MusicEvent(p, vel, start, start + dur))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))   # terminal landmark
comp.set_unit(0, 0, u)

# Drums context: low kick + hat ticks only (channel 9) — never a second
# melodic patch on the piano's pitch.
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

midi_path = "/opt/data/projects/Instruments/_test/electric_grand_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---------------------------------------------------------------- solo render
from _test.render_audio import render_midi, spectral_buzz_check  # noqa: E402

wav = "/opt/data/projects/Instruments/_test/electric_grand_test.wav"
render_midi(midi_path, wav, solo=0)   # track 1 = Electric Grand (first voice), SOLO
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
for idx in [1, 2, 3, 4, 5]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Electric Grand -> {labels[PGM]!r}")
assert labels[PGM] == "Electric Grand Piano", f"stem label mismatch: {labels[PGM]!r}"
assert STEM_LABEL == "Electric_Grand_Piano"

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
# QUIRK: FluidR3 names preset 2 "Electric Piano" (the generic electric-piano
# family name), NOT "Electric Grand Piano" — cosmetic SF2 spelling only; the
# stem label comes from the pipeline's GM_PROGRAMS[2] = "Electric Grand
# Piano". No routing impact.
assert sf2_name == "Electric Piano", f"SF2 preset mismatch: {sf2_name!r}"

# ---------------------------------------------------------------- stems on disk
out_dir = "/opt/data/projects/Instruments/_test/stems_electric_grand"
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    print(f"  {f} ({os.path.getsize(os.path.join(out_dir, f))} bytes)")
matches = [f for f in stem_files if "Electric_Grand_Piano" in f]
assert matches, f"no Electric_Grand_Piano stem in {stem_files}"
assert os.path.getsize(os.path.join(out_dir, matches[0])) > 40

# ---------------------------------------------------------------- Karplus-Strong
import numpy as np  # noqa: E402

from sound.synthesis.karplus_strong import karplus_strong  # noqa: E402

# CP = real piano string through a magnetic pickup -> the waveguide model.
# loop_gain 0.9982 (no soundboard to damp the string) must ring FAR longer
# than a 0.990 dull control.
audio = karplus_strong(72, 2.0, 90,
                       loop_gain=KARPLUS_DEFAULTS["loop_gain"],
                       width=KARPLUS_DEFAULTS["width"])
dull = karplus_strong(72, 2.0, 90, loop_gain=0.990, width=0.8)
peak = float(np.max(np.abs(audio)))
late = float(np.sqrt(np.mean(audio[int(1.5 * 22050):] ** 2)))
dull_late = float(np.sqrt(np.mean(dull[int(1.5 * 22050):] ** 2)))
print(f"\nKarplus-Strong C5 (loop_gain {KARPLUS_DEFAULTS['loop_gain']}): "
      f"peak={peak:.3f} late(1.5-2.0s)rms={late:.4f} late/peak={late / max(peak, 1e-9):.3f}")
print(f"  dull 0.990 control: late rms={dull_late:.4f} — "
      f"ring ratio {late / max(dull_late, 1e-9):.1f}x")
assert peak > 0, "KS electric-grand render silent"
assert late > dull_late * 3, "CP ring not long enough vs dull control"

# ModalSynth-family smoke with the custom ELECTRIC_GRAND_MODES bank
# (ResonatorBank: near-harmonic string stack, SLOW decay rates -> long
# soundboard-less ring; decay is a rate, y(t)=A*exp(-decay*t)).
from sound.synthesis.modal import ResonatorBank  # noqa: E402

ms = ResonatorBank(sample_rate=22050)
for freq, amp, decay in ELECTRIC_GRAND_MODES:
    ms.add_mode(freq, amp, decay)
audio = ms.excite_impulse(duration=2.0)
peak = float(np.max(np.abs(audio)))
late = float(np.sqrt(np.mean(audio[int(1.5 * 22050):] ** 2)))
print(f"ModalSynth ELECTRIC_GRAND_MODES: peak={peak:.3f} "
      f"late(1.5-2.0s)rms/peak={late / max(peak, 1e-9):.3f}")
assert peak > 0, "modal electric-grand render silent"
assert late / max(peak, 1e-9) > 0.01, "electric-grand modal ring collapsed"

# PhaseModSynth smoke with the FM_DEFAULTS (bright FM piano alt)
from sound.synthesis.phase_mod import PhaseModSynth  # noqa: E402

pms = PhaseModSynth(sample_rate=22050)
audio = pms.render_note(freq=523.25, duration=1.5, **FM_DEFAULTS)  # C5
peak = float(np.max(np.abs(audio)))
print(f"PhaseModSynth FM_DEFAULTS (C5=523.25Hz): peak={peak:.3f}")
assert peak > 0, "FM electric-grand render silent"

print("\nALL CHECKS PASSED")
