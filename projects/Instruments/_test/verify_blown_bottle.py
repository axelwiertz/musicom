# -*- coding: utf-8 -*-
"""Verify Blown Bottle constants end-to-end — through the REGISTRY, SOLO render.

Pattern from _test/verify_woodblock.py / verify_ocarina.py, with the 2026-09-01
fixes:
  * import constants via instrument_registry.by_name (proves registration)
  * audio check is the INSTRUMENT SOLO only (no unison doubling -> no comb buzz)
  * SoundFont resolved by discover_soundfont() (FluidR3 preferred)
  * PhaseModSynth smoke test with the instrument's own FM_DEFAULTS (aerophone)
"""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")
sys.path.insert(0, "/opt/data/repos/musicom")

from instrument_registry import by_name, by_program, ALL_INSTRUMENTS, BLOWN_BOTTLE

inst = by_name("blown bottle")
assert inst is not None
print(f"registry: by_name('blown bottle') -> {inst!r}")
print(f"registry: by_name('Blown Bottle') -> {by_name('Blown Bottle')!r}")
print(f"registry: by_program(76) -> {by_program(76)!r}")
print(f"registry: BLOWN_BOTTLE is ALL_INSTRUMENTS['blown_bottle'] -> "
      f"{BLOWN_BOTTLE is ALL_INSTRUMENTS['blown_bottle']}")
print(f"registry: family={inst.family} program={inst.midi_program} "
      f"range={inst.range_min}-{inst.range_max} solo={inst.solo_range} "
      f"sweet={inst.sweet_spot}")
print(f"registry: stem_label={inst.stem_label!r} reverb={inst.reverb_tail} pan={inst.pan}")
print(f"registry: synthesis={inst.synthesis} fm_defaults={inst.fm_defaults}")
print(f"registry: in_sweet_spot(72)={inst.in_sweet_spot(72)} "
      f"in_sweet_spot(36)={inst.in_sweet_spot(36)} in_range(60)={inst.in_range(60)}")

PGM = inst.midi_program
STEM_LABEL = inst.stem_label
SOLO_RANGE = inst.solo_range
ZONES = inst.zones
ARTICULATIONS = inst.articulations
SYNTHESIS = inst.synthesis
FM_DEFAULTS = inst.fm_defaults
REVERB_TAIL = inst.reverb_tail
EQ_BODY, EQ_PRESENCE, EQ_AIR = inst.eq_body, inst.eq_presence, inst.eq_air
PAN = inst.pan
from Woodwind.blown_bottle.blown_bottle import midi_to_freq  # noqa: E402

print(f"Blown Bottle: program={PGM} gm={inst.gm_name!r} stem={STEM_LABEL!r} "
      f"sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Blown Bottle: zones={ZONES}")
print(f"Blown Bottle: art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"reverb={REVERB_TAIL}s pan={PAN}")
print(f"Blown Bottle: C4={midi_to_freq(60):.1f}Hz C5={midi_to_freq(72):.1f}Hz "
      f"C6={midi_to_freq(84):.1f}Hz")

# ---------------------------------------------------------------- composition
from structures import MusicEvent, MusicUnit  # noqa: E402
from workflows.unitmatrix_composer import UnitMatrixComposer  # noqa: E402

BAR = 1920
comp = UnitMatrixComposer(bpm=104, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("BlownBottle", program=PGM, channel=0)
comp.add_voice("Drums", program=0, channel=9)   # context only (channel 9)
comp.add_section("A", bars=1)

# Blown Bottle SOLO part: a slow breathy sweet-spot line (G4-A4-C5-D5-C5-A4-G4)
# — swells, puffs, accents, one ghost. The slow blow-in attack means notes
# need >= ~1/8; the long final note lets the swell speak.
u = MusicUnit()
line = [
    (0, 67, 85, 480),      # G4 swell
    (480, 69, 78, 360),    # A4 blow
    (840, 72, 95, 300),    # C5 accent (hard blow)
    (1140, 74, 78, 480),   # D5 blow
    (1620, 72, 64, 120),   # C5 puff
    (1740, 69, 36, 90),    # A4 ghost breath
    (1830, 67, 85, 90),    # G4 swell tail -> ends flush at BAR
]
for start, p, vel, dur in line:
    u.add_event(MusicEvent(p, vel, start, start + dur))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))   # terminal landmark
comp.set_unit(0, 0, u)

# Drums context: low kick + hat ticks only (channel 9) — never a second
# melodic patch on the bottle's pitch.
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

midi_path = "/opt/data/projects/Instruments/_test/blown_bottle_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---------------------------------------------------------------- solo render
from _test.render_audio import render_midi, spectral_buzz_check  # noqa: E402

wav = "/opt/data/projects/Instruments/_test/blown_bottle_test.wav"
render_midi(midi_path, wav, solo=0)   # track 1 = Blown Bottle (first voice), SOLO
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
for idx in [74, 75, 76, 77, 78]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Blown Bottle -> {labels[PGM]!r}")
assert labels[PGM] == "Blown Bottle", f"stem label mismatch: {labels[PGM]!r}"
assert STEM_LABEL == "Blown_Bottle"

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
# QUIRK: FluidR3 names preset 76 "Bottle Chiff" (the sample's chiff/breath
# character), NOT "Blown Bottle" — cosmetic SF2 spelling only; the stem label
# comes from the pipeline's GM_PROGRAMS[76] = "Blown Bottle". No routing impact.
assert sf2_name == "Bottle Chiff", f"SF2 preset mismatch: {sf2_name!r}"

# ---------------------------------------------------------------- stems on disk
out_dir = "/opt/data/projects/Instruments/_test/stems_blown_bottle"
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    print(f"  {f} ({os.path.getsize(os.path.join(out_dir, f))} bytes)")
matches = [f for f in stem_files if "Blown_Bottle" in f]
assert matches, f"no Blown_Bottle stem in {stem_files}"
assert os.path.getsize(os.path.join(out_dir, matches[0])) > 40

# ---------------------------------------------------------------- PhaseModSynth
import numpy as np  # noqa: E402

from sound.synthesis.phase_mod import PhaseModSynth  # noqa: E402

pms = PhaseModSynth(sample_rate=22050)
audio = pms.render_note(freq=523.25, duration=1.5, **FM_DEFAULTS)  # C5
peak = float(np.max(np.abs(audio)))
late = float(np.sqrt(np.mean(audio[int(1.125 * 22050):] ** 2)))
print(f"\nPhaseModSynth FM_DEFAULTS (C5=523.25Hz): peak={peak:.3f} "
      f"late_rms={late:.4f} late/peak={late / max(peak, 1e-9):.3f}")
assert peak > 0, "FM blown-bottle render silent"
assert late / max(peak, 1e-9) > 0.1, "blown-bottle sustain collapsed (no blow)"

# the near-sine Helmholtz tone: 2nd harmonic energy well below the fundamental
spec = np.abs(np.fft.rfft(audio[: int(0.5 * 22050)]))
freqs = np.fft.rfftfreq(int(0.5 * 22050), 1 / 22050)


def band(f, w=20):
    b = (freqs > f - w) & (freqs < f + w)
    return float(spec[b].max()) if b.any() else 0.0


f0 = band(523.25)
f1 = band(1046.5)
print(f"  harmonic check: 2nd/1st = {f1 / max(f0, 1e-9):.2f} (near-sine Helmholtz tone)")
assert f1 / max(f0, 1e-9) < 0.5, "FM bottle too bright — not a cavity tone"

print("\nALL CHECKS PASSED")
