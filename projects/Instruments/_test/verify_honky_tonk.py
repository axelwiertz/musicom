# -*- coding: utf-8 -*-
"""Verify Honky-tonk Piano constants end-to-end — through the REGISTRY, SOLO.

Pattern from _test/verify_warm_pad.py (itself from verify_agogo.py /
verify_marimba.py):
  * import constants via instrument_registry.by_name (proves registration)
  * audio check is the INSTRUMENT SOLO only (no unison doubling -> no comb buzz)
  * SoundFont resolved by discover_soundfont() (FluidR3 preferred)
"""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")
sys.path.insert(0, "/opt/data/repos/musicom")

from instrument_registry import by_name, by_program, ALL_INSTRUMENTS, HONKY_TONK

inst = by_name("honky tonk")
print(f"registry: by_name('honky tonk') -> {inst!r}")
print(f"registry: by_name('Honky-tonk Piano') -> {by_name('Honky-tonk Piano')!r}")
print(f"registry: by_program(3) -> {by_program(3)!r}")
print(f"registry: HONKY_TONK is ALL_INSTRUMENTS['honky_tonk'] -> "
      f"{HONKY_TONK is ALL_INSTRUMENTS['honky_tonk']}")
print(f"registry: family={inst.family} program={inst.midi_program} "
      f"range={inst.range_min}-{inst.range_max} solo={inst.solo_range} "
      f"sweet={inst.sweet_spot}")
print(f"registry: stem_label={inst.stem_label!r} reverb={inst.reverb_tail} pan={inst.pan}")
print(f"registry: synthesis={inst.synthesis} synthesis_defaults={inst.synthesis_defaults}")
print(f"registry: in_sweet_spot(67)={inst.in_sweet_spot(67)} "
      f"in_sweet_spot(24)={inst.in_sweet_spot(24)} in_range(60)={inst.in_range(60)}")

PGM = inst.midi_program
STEM_LABEL = inst.stem_label
SOLO_RANGE = inst.solo_range
ZONES = inst.zones
ARTICULATIONS = inst.articulations
SYNTHESIS = inst.synthesis
SYNTHESIS_DEFAULTS = inst.synthesis_defaults
REVERB_TAIL = inst.reverb_tail
EQ_BODY, EQ_PRESENCE, EQ_AIR = inst.eq_body, inst.eq_presence, inst.eq_air
PAN = inst.pan
from Keys.honky_tonk.honky_tonk import (
    midi_to_freq, HONKY_TONK_MODES, ADDITIVE_HARMONICS, FM_DEFAULTS,
)

print(f"Honky-tonk: program={PGM} gm={inst.gm_name!r} stem={STEM_LABEL!r} "
      f"sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Honky-tonk: zones={ZONES}")
print(f"Honky-tonk: art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"reverb={REVERB_TAIL}s pan={PAN}")

# ---------------------------------------------------------------- composition
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

BAR = 1920
comp = UnitMatrixComposer(bpm=104, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("HonkyTonk", program=PGM, channel=0)   # SOLO melodic voice
comp.add_voice("Drums", program=0, channel=9)         # context only (channel 9)
comp.add_section("A", bars=1)

# One bar of stride: LH "oom" (C2/C3 octave) on 1 and 3, RH chord "pah"
# (E4/G4/C5) on the off-beats, plus a syncopated ragtime turn. All notes end
# flush at BAR (terminal landmark).
u = MusicUnit()
# stride bass — octaves, beats 1 and 3
for start in (0, 960):
    for p in (36, 48):
        u.add_event(MusicEvent(p, 92, start, start + 300))
# off-beat chords — beats 2 and 4 (clipped)
for start in (480, 1440):
    for p in (64, 67, 72):
        u.add_event(MusicEvent(p, 80, start, start + 220))
# ragtime syncopated melody turn (C5-E5-G5) in the last half bar
for start, p in [(1200, 72), (1320, 76), (1440, 79)]:
    u.add_event(MusicEvent(p, 88, start, start + 240))
# terminal landmark
u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

# Drums context (never a second melodic patch on the same pitches)
u = MusicUnit()
for start, pitch, vel in [(0, 36, 108), (480, 38, 96), (960, 36, 108),
                          (1440, 38, 96), (240, 42, 44), (720, 42, 40),
                          (1200, 42, 44), (1680, 42, 40)]:
    u.add_event(MusicEvent(pitch, vel, start, start + 110))
u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/honky_tonk_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---------------------------------------------------------------- solo render
from _test.render_audio import render_midi, spectral_buzz_check

wav = "/opt/data/projects/Instruments/_test/honky_tonk_test.wav"
render_midi(midi_path, wav, solo=0)   # voice 0 = Honky-tonk, SOLO
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
for idx in [0, 1, 2, 3, 4]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Honky-tonk -> {labels[PGM]!r}")
assert labels[PGM] == "Honky-tonk Piano", f"stem label mismatch: {labels[PGM]!r}"
assert STEM_LABEL == "Honky-tonk_Piano"

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
assert sf2_name == "Honky Tonk", f"SF2 preset mismatch: {sf2_name!r}"

# ---------------------------------------------------------------- stems on disk
out_dir = "/opt/data/projects/Instruments/_test/stems_honky_tonk"
fs_bin = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
pipeline = RenderPipeline(fluidsynth_bin=fs_bin, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    print(f"  {f} ({os.path.getsize(os.path.join(out_dir, f))} bytes)")
assert any("Honky-tonk_Piano" in f for f in stem_files), f"no stem in {stem_files}"
stem_path = [f for f in stem_files if "Honky-tonk_Piano" in f][0]
assert os.path.getsize(os.path.join(out_dir, stem_path)) > 40

# ---------------------------------------------------------------- beating (modal)
import numpy as np
from sound.synthesis.modal import ResonatorBank

sr = 22050
bank = ResonatorBank(sr)
for freq, amp, decay in HONKY_TONK_MODES:
    bank.add_mode(freq, amp, decay)
audio = bank.excite_impulse(duration=2.0)
win = int(0.02 * sr)
nwin = len(audio) // win
env = np.array([np.sqrt(np.mean(audio[i * win:(i + 1) * win] ** 2))
                for i in range(nwin)])
env = env - env.mean()
spec = np.abs(np.fft.rfft(env * np.hanning(len(env))))
freqs = np.fft.rfftfreq(len(env), d=win / sr)
band = (freqs >= 1.0) & (freqs <= 12.0)
beat_hz = float(freqs[band][np.argmax(spec[band])])
beat_depth = float(np.std(env) / max(np.mean(np.abs(env)), 1e-9))
print(f"\nModal honky bank: measured beat {beat_hz:.2f} Hz "
      f"(gate 3.5-5.5), AM depth {beat_depth:.2f}")
assert 3.5 <= beat_hz <= 5.5, f"beating not the honky 4.3 Hz — got {beat_hz:.2f}"
assert beat_depth > 0.15, "detuned twin does not modulate — not a honky-tonk"

# control: a SINGLE (tuned) bank must not beat at 4.3 Hz as strongly
bank_tuned = ResonatorBank(sr)
for freq, amp, decay in HONKY_TONK_MODES:
    if abs(freq - 444.3) < 1e-6:
        continue          # drop the detuned twin
    bank_tuned.add_mode(freq, amp, decay)
audio_t = bank_tuned.excite_impulse(duration=2.0)
env_t = np.array([np.sqrt(np.mean(audio_t[i * win:(i + 1) * win] ** 2))
                  for i in range(nwin)])
env_t = env_t - env_t.mean()
spec_t = np.abs(np.fft.rfft(env_t * np.hanning(len(env_t))))
beat_t = float(freqs[band][np.argmax(spec_t[band])])
print(f"Control (no detuned twin): dominant envelope peak {beat_t:.2f} Hz")
assert beat_t != beat_hz or float(np.max(spec_t[band])) < float(np.max(spec[band]))

# ---------------------------------------------------------------- additive smoke
from sound.synthesis.additive import SoundWave

w = np.array(ADDITIVE_HARMONICS["honky_tonk"], dtype=float)
w = w / w.sum()
sw = SoundWave(sample_rate=sr, duration=1.0, frequency=261.63)
sw.apply_overtones(list(w))
peak = float(np.max(np.abs(sw.wavedata)))
print(f"Additive honky_tonk stack: peak={peak:.1f} (weights sum 1.0, no assert)")
assert peak > 0

# ---------------------------------------------------------------- pitch sweep
print("\nEmpirical FluidR3 pitch sweep (RMS, velocity 90):")
import subprocess, tempfile, wave
def render_note(note, vel=90):
    c = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice("X", program=PGM, channel=0)
    c.add_section("A", bars=1)
    uu = MusicUnit()
    uu.add_event(MusicEvent(note, vel, 0, int(BAR * 0.9)))
    if uu.len_ticks() < BAR:
        uu.add_event(MusicEvent(0, 0, uu.len_ticks(), BAR))
    c.set_unit(0, 0, uu)
    assert c.validate()[0]
    fd, mp = tempfile.mkstemp(suffix=".mid"); os.close(fd)
    c.to_midi(mp)
    fd2, wv = tempfile.mkstemp(suffix=".wav"); os.close(fd2)
    os.unlink(wv)
    r = subprocess.run([fs_bin, "-ni", "-g", "1.2", "-F", wv, sf2, mp],
                       capture_output=True)
    os.unlink(mp)
    if r.returncode != 0 or not os.path.exists(wv):
        return None
    with wave.open(wv, "rb") as f:
        srate = f.getframerate()
        raw = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(np.float64)
    os.unlink(wv)
    mono = raw.reshape(-1, 2).mean(axis=1) if raw.size % 2 == 0 else raw
    return float(np.sqrt(np.mean(mono ** 2)))

def n_to_name(n):
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return f"{names[n % 12]}{n // 12 - 1}"

sweep = []
for n in range(24, 109, 12):
    r = render_note(n)
    sweep.append((n, r))
    print(f"  note {n:3d} ({n_to_name(n):>4s})  rms={r if r is None else round(r, 4)}")
audible = [r for _, r in sweep if r is not None and r > 0.0]
assert len(audible) == len(sweep), "some sweep notes silent — SF2 clips the patch"

print("\nALL CHECKS PASSED")
