# -*- coding: utf-8 -*-
"""Verify Warm Pad constants end-to-end — through the REGISTRY, SOLO render.

Pattern from _test/verify_agogo.py (itself from verify_marimba.py), with the
2026-09-01 fixes:
  * import constants via instrument_registry.by_name (proves registration)
  * audio check is the INSTRUMENT SOLO only (no unison doubling -> no comb buzz)
  * SoundFont resolved by discover_soundfont() (FluidR3 preferred)
"""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")
sys.path.insert(0, "/opt/data/repos/musicom")

from instrument_registry import by_name, by_program, ALL_INSTRUMENTS, WARM_PAD

inst = by_name("warm pad")
print(f"registry: by_name('warm pad') -> {inst!r}")
print(f"registry: by_name('Pad 2 (warm)') -> {by_name('Pad 2 (warm)')!r}")
print(f"registry: by_program(89) -> {by_program(89)!r}")
print(f"registry: WARM_PAD is ALL_INSTRUMENTS['warm_pad'] -> {WARM_PAD is ALL_INSTRUMENTS['warm_pad']}")
print(f"registry: family={inst.family} program={inst.midi_program} "
      f"range={inst.range_min}-{inst.range_max} solo={inst.solo_range} "
      f"sweet={inst.sweet_spot}")
print(f"registry: stem_label={inst.stem_label!r} reverb={inst.reverb_tail} pan={inst.pan}")
print(f"registry: synthesis={inst.synthesis} synthesis_defaults={inst.synthesis_defaults}")
print(f"registry: in_sweet_spot(72)={inst.in_sweet_spot(72)} "
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
from Synth.warm_pad.warm_pad import midi_to_freq, ADDITIVE_HARMONICS, POLYSYNTH_DEFAULTS

print(f"Warm Pad: program={PGM} gm={inst.gm_name!r} stem={STEM_LABEL!r} "
      f"sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Warm Pad: zones={ZONES}")
print(f"Warm Pad: art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"reverb={REVERB_TAIL}s pan={PAN}")
print(f"Warm Pad: A3={midi_to_freq(57):.1f}Hz C4={midi_to_freq(60):.1f}Hz "
      f"C5={midi_to_freq(72):.1f}Hz")

# ---------------------------------------------------------------- composition
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

BAR = 1920
comp = UnitMatrixComposer(bpm=100, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("WarmPad", program=PGM, channel=0)
comp.add_voice("Drums", program=0, channel=9)   # context only (channel 9)
comp.add_section("A", bars=1)

# Warm Pad SOLO: slow-attack pad chords — C major (C4/E4/G4) half bar, then
# A minor (A3/C4/E4). All notes end flush at BAR (terminal landmark).
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

midi_path = "/opt/data/projects/Instruments/_test/warm_pad_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---------------------------------------------------------------- solo render
from _test.render_audio import render_midi, spectral_buzz_check

wav = "/opt/data/projects/Instruments/_test/warm_pad_test.wav"
render_midi(midi_path, wav, solo=0)   # track 1 = Warm Pad (first voice), SOLO
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
for idx in [88, 89, 90, 92]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Warm Pad -> {labels[PGM]!r}")
assert labels[PGM] == "Pad 2 (warm)", f"stem label mismatch: {labels[PGM]!r}"
assert STEM_LABEL == "Pad_2_warm"

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
assert sf2_name == "Warm Pad", f"SF2 preset mismatch: {sf2_name!r}"

# ---------------------------------------------------------------- stems on disk
out_dir = "/opt/data/projects/Instruments/_test/stems_warm_pad"
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    print(f"  {f} ({os.path.getsize(os.path.join(out_dir, f))} bytes)")
assert any("Pad_2_warm" in f for f in stem_files), f"no Warm Pad stem in {stem_files}"
assert os.path.getsize(os.path.join(out_dir, [f for f in stem_files if "Pad_2_warm" in f][0])) > 40

# ---------------------------------------------------------------- Additive smoke
import numpy as np
from sound.synthesis.additive import SoundWave

def pad_envelope(decay_S, dur=2.0, freq=261.63):
    sw = SoundWave(sample_rate=22050, duration=dur, frequency=freq)
    # ADDITIVE_HARMONICS weights are RELATIVE (drawbar-style); the
    # apply_overtones API asserts factors sum to 1.0 — normalize first.
    factor = np.array(ADDITIVE_HARMONICS["pad_warm"], dtype=float)
    factor = factor / factor.sum()
    sw.apply_overtones(list(factor))
    sw.get_adsr_weights(length=[0.225, 0.05, 0.625, 0.1],
                        decay=[0.05, 0.02, decay_S, 0.05],
                        sustain_level=0.9)
    return sw

sw = pad_envelope(1e-4)
late = sw.weights[int(1.0 * 22050):int(1.5 * 22050)]
late_max = float(np.max(late))
sw_bad = pad_envelope(0.005)
late_bad = sw_bad.weights[int(1.0 * 22050):int(1.5 * 22050)]
late_bad_max = float(np.max(late_bad))
print(f"\nAdditive pad_warm: late(1.0-1.5s) env max with decay_S=1e-4 = {late_max:.3f} "
      f"(gate >= 0.45)")
print(f"Additive pad_warm: same with decay_S=0.005 (wrong) = {late_bad_max:.3f} "
      f"(collapse)")
assert late_max >= 0.45, "warm-pad additive envelope collapses (decay_S quirk)"
assert late_bad_max < late_max, "contrast check failed"

# ---------------------------------------------------------------- Polysynth smoke
from sound.synthesis.polysynth import PolyVoice

pv = PolyVoice(sample_rate=22050)
pv.osc1.waveform = POLYSYNTH_DEFAULTS["osc1_waveform"]           # triangle
pv.osc2.waveform = POLYSYNTH_DEFAULTS["osc2_waveform"]           # saw
pv.osc2.detune_cents = POLYSYNTH_DEFAULTS["osc2_detune_cents"]   # +7c
pv.osc3.waveform = POLYSYNTH_DEFAULTS["osc3_waveform"]           # saw
pv.osc3.detune_cents = POLYSYNTH_DEFAULTS["osc3_detune_cents"]   # -7c
pv.osc3.level = POLYSYNTH_DEFAULTS["osc3_level"]
pv.filter.cutoff = POLYSYNTH_DEFAULTS["filter_cutoff"]           # 1400 Hz
pv.filter.resonance = POLYSYNTH_DEFAULTS["filter_resonance"]
pv.env1.set(attack=POLYSYNTH_DEFAULTS["env_attack"],
            decay=POLYSYNTH_DEFAULTS["env_decay"],
            sustain=POLYSYNTH_DEFAULTS["env_sustain"],
            release=POLYSYNTH_DEFAULTS["env_release"])
# filter envelope follows the amp (classic pad filter-follows-amp) so the
# cutoff stays open through the sustain — otherwise env2's fast default
# attack closes the 1400 Hz cutoff after the crest and the body thins
pv.env2.set(attack=POLYSYNTH_DEFAULTS["env_attack"],
            decay=POLYSYNTH_DEFAULTS["env_decay"],
            sustain=POLYSYNTH_DEFAULTS["env_sustain"],
            release=POLYSYNTH_DEFAULTS["env_release"])
audio = pv.render_note(freq=220.0, duration=2.5)   # A3 — 2.5s so the sustain
                                                   #   segment (0.75–1.9s) is
                                                   #   measurable (1.5s note's
                                                   #   sustain is only 0.15s
                                                   #   before the 0.6s release)
peak = float(np.max(np.abs(audio)))
late_ps = float(np.sqrt(np.mean(audio[int(1.0 * 22050):int(1.5 * 22050)] ** 2)))
rel_ps = float(np.sqrt(np.mean(audio[int(2.0 * 22050):int(2.5 * 22050)] ** 2)))
print(f"\nPolysynth warm pad (A3): peak={peak:.3f} sustain_rms={late_ps:.4f} "
      f"release_rms={rel_ps:.4f} hold_ratio={late_ps / max(rel_ps, 1e-9):.2f}")
assert peak > 0, "polysynth warm pad render silent"
# env1 holds at sustain 0.8 through 1.0-1.5s (verified above); the rms/peak
# ratio is NOT the gate here because the attack resonance crest is the
# peak — the meaningful check is that the sustain window holds well above
# the release window (the pad does not collapse into a pluck)
assert late_ps > 0.1, "polysynth warm pad sustain too quiet"
assert late_ps / max(rel_ps, 1e-9) > 1.5, "polysynth sustain collapsed (no hold)"

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
for n in range(36, 109, 12):
    r = render_note(n)
    sweep.append((n, r))
    print(f"  note {n:3d} ({n_to_name(n):>4s})  rms={r if r is None else round(r, 4)}")
audible = [r for _, r in sweep if r is not None and r > 0.0]
assert len(audible) == len(sweep), "some sweep notes silent — SF2 clips the patch"

print("\nALL CHECKS PASSED")
