# -*- coding: utf-8 -*-
"""Verify String Ensemble 2 constants end-to-end — through the REGISTRY, SOLO render.

Pattern from _test/verify_warm_pad.py (itself from verify_marimba.py), with the
2026-09-01 fixes:
  * import constants via instrument_registry.by_name (proves registration)
  * audio check is the INSTRUMENT SOLO only (no unison doubling -> no comb buzz)
  * SoundFont resolved by discover_soundfont() (FluidR3 preferred)
"""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")
sys.path.insert(0, "/opt/data/repos/musicom")

from instrument_registry import by_name, by_program, ALL_INSTRUMENTS, STRING_ENSEMBLE_2

inst = by_name("string ensemble 2")
print(f"registry: by_name('string ensemble 2') -> {inst!r}")
print(f"registry: by_name('String Ensemble 2') -> {by_name('String Ensemble 2')!r}")
print(f"registry: by_program(49) -> {by_program(49)!r}")
print(f"registry: by_program(48) -> {by_program(48)!r} (distinct: string ensemble 1)")
print(f"registry: STRING_ENSEMBLE_2 is ALL_INSTRUMENTS['string_ensemble_2'] -> "
      f"{STRING_ENSEMBLE_2 is ALL_INSTRUMENTS['string_ensemble_2']}")
print(f"registry: family={inst.family} program={inst.midi_program} "
      f"range={inst.range_min}-{inst.range_max} solo={inst.solo_range} "
      f"sweet={inst.sweet_spot}")
print(f"registry: stem_label={inst.stem_label!r} reverb={inst.reverb_tail} pan={inst.pan}")
print(f"registry: synthesis={inst.synthesis} synthesis_defaults={inst.synthesis_defaults}")
print(f"registry: string_ensemble_defaults={inst.string_ensemble_defaults}")
print(f"registry: in_sweet_spot(72)={inst.in_sweet_spot(72)} "
      f"in_sweet_spot(24)={inst.in_sweet_spot(24)} in_range(60)={inst.in_range(60)}")

PGM = inst.midi_program
STEM_LABEL = inst.stem_label
SOLO_RANGE = inst.solo_range
ZONES = inst.zones
ARTICULATIONS = inst.articulations
SYNTHESIS = inst.synthesis
SYNTHESIS_DEFAULTS = inst.synthesis_defaults
STRING_ENSEMBLE_DEFAULTS = inst.string_ensemble_defaults
REVERB_TAIL = inst.reverb_tail
EQ_BODY, EQ_PRESENCE, EQ_AIR = inst.eq_body, inst.eq_presence, inst.eq_air
PAN = inst.pan
from Strings.string_ensemble_2.string_ensemble_2 import midi_to_freq, ADDITIVE_HARMONICS, POLYSYNTH_DEFAULTS

print(f"\nString Ensemble 2: program={PGM} gm={inst.gm_name!r} stem={STEM_LABEL!r} "
      f"sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"String Ensemble 2: zones={ZONES}")
print(f"String Ensemble 2: art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"reverb={REVERB_TAIL}s pan={PAN}")
print(f"String Ensemble 2: A3={midi_to_freq(57):.1f}Hz C4={midi_to_freq(60):.1f}Hz "
      f"C5={midi_to_freq(72):.1f}Hz")

# ---------------------------------------------------------------- composition
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

BAR = 1920
comp = UnitMatrixComposer(bpm=100, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("StringEnsemble2", program=PGM, channel=0)
comp.add_voice("Drums", program=0, channel=9)   # context only (channel 9)
comp.add_section("A", bars=1)

# String Ensemble 2 SOLO: slow-attack pad chords — C major (C4/E4/G4) half bar,
# then A minor (A3/C4/E4). All notes end flush at BAR (terminal landmark).
u = MusicUnit()
for p in (60, 64, 67):
    u.add_event(MusicEvent(p, 74, 0, 960))
for p in (57, 60, 64):
    u.add_event(MusicEvent(p, 72, 960, BAR))
comp.set_unit(0, 0, u)

# Drums context: kick on the beats + hat ticks (channel 9, drum-kit map)
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

midi_path = "/opt/data/projects/Instruments/_test/string_ensemble_2_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---------------------------------------------------------------- solo render
from _test.render_audio import render_midi, spectral_buzz_check

wav = "/opt/data/projects/Instruments/_test/string_ensemble_2_test.wav"
render_midi(midi_path, wav, solo=0)   # track 1 = String Ensemble 2 (first voice), SOLO
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
for idx in [48, 49, 50, 51]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  String Ensemble 2 -> {labels[PGM]!r}")
assert labels[PGM] == "String Ensemble 2", f"stem label mismatch: {labels[PGM]!r}"
assert STEM_LABEL == "String_Ensemble_2"

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
print(f"\nSF2: {sf2}")
sf2_name = preset_names.get((0, PGM), "MISSING")
print(f"SF2 preset {PGM} -> {sf2_name!r}")
assert sf2_name == "Slow Strings", f"SF2 preset mismatch: {sf2_name!r}"

# ---------------------------------------------------------------- stems on disk
out_dir = "/opt/data/projects/Instruments/_test/stems_string_ensemble_2"
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    print(f"  {f} ({os.path.getsize(os.path.join(out_dir, f))} bytes)")
assert any("String_Ensemble_2" in f for f in stem_files), f"no String Ensemble 2 stem in {stem_files}"
assert os.path.getsize(os.path.join(out_dir, [f for f in stem_files if "String_Ensemble_2" in f][0])) > 40

# ---------------------------------------------------------------- engine smokes
import numpy as np

# 1) StringEnsembleVoice (primary engine): slow-swell sustained chord
from sound.synthesis.string_ensemble import StringEnsembleVoice

sev = StringEnsembleVoice(n_voices=STRING_ENSEMBLE_DEFAULTS["n_voices"],
                          octave_mix=STRING_ENSEMBLE_DEFAULTS["octave_mix"],
                          detune_cents=STRING_ENSEMBLE_DEFAULTS["detune_cents"],
                          drift_rate=STRING_ENSEMBLE_DEFAULTS["drift_rate"],
                          attack_s=STRING_ENSEMBLE_DEFAULTS["attack_s"],
                          release_s=STRING_ENSEMBLE_DEFAULTS["release_s"],
                          layer_mix=STRING_ENSEMBLE_DEFAULTS["layer_mix"],
                          flavour=STRING_ENSEMBLE_DEFAULTS["flavour"],
                          sr=22050, seed=7)
ch = sev.render_chord([60, 64, 67], dur_s=2.5, velocity=0.8, sr=22050)
peak = float(np.abs(ch).max())
swell = float(np.sqrt(np.mean(ch[:, int(1.5 * 22050):int(2.0 * 22050)] ** 2)))
onset = float(np.sqrt(np.mean(ch[:, 0:int(0.1 * 22050)] ** 2)))
print(f"\nStringEnsembleVoice Cmaj (2.5s): peak={peak:.3f} onset_rms={onset:.4f} "
      f"late_rms={swell:.4f}")
assert peak > 0, "StringEnsembleVoice silent"
assert swell > onset * 2, f"no slow swell: onset {onset:.4f} late {swell:.4f}"

# 2) Polysynth (secondary): detuned saw stack through low-pass
from sound.synthesis.polysynth import PolyVoice

pv = PolyVoice(sample_rate=22050)
pv.osc1.waveform = POLYSYNTH_DEFAULTS["osc1_waveform"]           # saw
pv.osc2.waveform = POLYSYNTH_DEFAULTS["osc2_waveform"]           # saw
pv.osc2.detune_cents = POLYSYNTH_DEFAULTS["osc2_detune_cents"]   # +8c
pv.osc3.waveform = POLYSYNTH_DEFAULTS["osc3_waveform"]           # saw
pv.osc3.detune_cents = POLYSYNTH_DEFAULTS["osc3_detune_cents"]   # -8c
pv.osc3.level = POLYSYNTH_DEFAULTS["osc3_level"]
pv.filter.cutoff = POLYSYNTH_DEFAULTS["filter_cutoff"]           # 2200 Hz
pv.filter.resonance = POLYSYNTH_DEFAULTS["filter_resonance"]
pv.env1.set(attack=POLYSYNTH_DEFAULTS["env_attack"],
            decay=POLYSYNTH_DEFAULTS["env_decay"],
            sustain=POLYSYNTH_DEFAULTS["env_sustain"],
            release=POLYSYNTH_DEFAULTS["env_release"])
pv.env2.set(attack=POLYSYNTH_DEFAULTS["env_attack"],
            decay=POLYSYNTH_DEFAULTS["env_decay"],
            sustain=POLYSYNTH_DEFAULTS["env_sustain"],
            release=POLYSYNTH_DEFAULTS["env_release"])
audio = pv.render_note(freq=220.0, duration=2.5)   # A3
peak = float(np.max(np.abs(audio)))
late_ps = float(np.sqrt(np.mean(audio[int(1.0 * 22050):int(1.5 * 22050)] ** 2)))
rel_ps = float(np.sqrt(np.mean(audio[int(2.0 * 22050):int(2.5 * 22050)] ** 2)))
print(f"Polysynth slow strings (A3): peak={peak:.3f} sustain_rms={late_ps:.4f} "
      f"release_rms={rel_ps:.4f} hold_ratio={late_ps / max(rel_ps, 1e-9):.2f}")
assert peak > 0, "polysynth slow strings silent"
assert late_ps > 0.1, "polysynth slow strings sustain too quiet"
assert late_ps / max(rel_ps, 1e-9) > 1.5, "polysynth sustain collapsed (no hold)"

# 3) Additive (tertiary): slow-swell pad stack with decay_S 1e-4 (pad recipe)
from sound.synthesis.additive import SoundWave

factor = np.array(ADDITIVE_HARMONICS["slow_strings"], dtype=float)
factor = factor / factor.sum()
sw = SoundWave(sample_rate=22050, duration=2.0, frequency=261.63)
sw.apply_overtones(list(factor))
sw.get_adsr_weights(length=[0.4, 0.05, 0.45, 0.1],
                    decay=[0.05, 0.02, 1e-4, 0.05],
                    sustain_level=0.9)
late = sw.weights[int(1.0 * 22050):int(1.5 * 22050)]
print(f"Additive slow_strings: late(1.0-1.5s) env max = {float(np.max(late)):.3f} (gate >= 0.45)")
assert float(np.max(late)) >= 0.45, "additive slow_strings envelope collapses"

# ---------------------------------------------------------------- pitch sweep
print("\nEmpirical FluidR3 pitch sweep (RMS, velocity 90):")
import subprocess, tempfile, wave
fs = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
def render_note(note, vel=90):
    c = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice("X", program=PGM, channel=0)
    c.add_section("A", bars=1)
    u = MusicUnit()
    end = int(BAR * 0.9)
    u.add_event(MusicEvent(note, vel, 0, end))
    if u.len_ticks() < BAR:
        u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
    c.set_unit(0, 0, u)
    assert c.validate()[0]
    fd, mp = tempfile.mkstemp(suffix=".mid"); os.close(fd)
    c.to_midi(mp)
    fd2, wv = tempfile.mkstemp(suffix=".wav"); os.close(fd2)
    os.unlink(wv)
    r = subprocess.run([fs, "-ni", "-g", "1.2", "-F", wv, sf2, mp], capture_output=True)
    os.unlink(mp)
    if r.returncode != 0 or not os.path.exists(wv):
        return None
    with wave.open(wv, "rb") as f:
        sr = f.getframerate()
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
# 108+ is the patch ceiling: its RMS is the render noise floor (~1) vs
# ~900–1800 for real notes — check it as a FRACTION of the audible median
# (0.9947 / ~1200 = 0.06% — effectively silent), not an absolute 0.01
med = float(np.median([r for _, r in sweep if r and r > 10]))
assert all(r < 0.02 * med for n, r in sweep if n >= 108), "108+ should be silent (patch ceiling)"

print("\nALL CHECKS PASSED")
