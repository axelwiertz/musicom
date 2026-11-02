# -*- coding: utf-8 -*-
"""Verify Synth Bass 2 (GM39) constants through the registry + audio render.

Structural template: _test/verify_acoustic_bass.py.
Audio render: INSTRUMENT SOLO ONLY (one melodic voice, one track) — the
2026-09-01 comb-filter rule. A drum-kit voice rides along for context but is
NOT part of the solo render.
"""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# --- prove REGISTRATION: import through the registry, not the module -----
from instrument_registry import by_name, by_program, SYNTH_BASS_2

from Bass.synth_bass_2.synth_bass_2 import (
    MIDI_PROGRAM as SB2_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, SYNTHESIS_DEFAULTS, FM_DEFAULTS,
    MODAL_PRESET, REVERB_TAIL, EQ_BODY, EQ_PRESENCE, EQ_AIR, PAN,
    midi_to_freq,
)

assert SYNTH_BASS_2 is by_name("synth bass 2")
assert by_program(39) is SYNTH_BASS_2
assert SYNTH_BASS_2.midi_program == 39
assert SYNTH_BASS_2.name == "Synth Bass 2"
print(f"Registry: {SYNTH_BASS_2}")
print(f"Synth Bass 2: program={SB2_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"sweet={SYNTH_BASS_2.sweet_spot} A4={midi_to_freq(69):.1f}Hz")
print(f"Synth Bass 2: zones={ZONES}")
print(f"Synth Bass 2: art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"modal_preset={MODAL_PRESET} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Synth Bass 2: A1={midi_to_freq(33):.2f}Hz E2={midi_to_freq(40):.2f}Hz "
      f"A2={midi_to_freq(45):.2f}Hz C3={midi_to_freq(48):.2f}Hz")

# --- engine test: 1 bar, 1 section ---------------------------------------
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES, beat_pattern

BAR = 1920
comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Synth Bass 2", program=SB2_PGM, channel=0)
comp.add_voice("Drums", program=0, channel=9)         # context only
comp.add_section("A", bars=1)

# Acid line in A minor with offbeat accents + octave jump:
# A1 . A1(accent) . E2 . A2(octave) | E2 . A1 . A1(accent) . E2 ...
# (pitch, vel, start, end) with the terminal note flush at BAR
line = [
    (33, 78, 0, 240),      # A1 downbeat (staccato 16th)
    (33, 96, 240, 480),    # A1 offbeat accent — the acid gesture
    (40, 76, 480, 720),    # E2
    (45, 98, 720, 780),    # A2 octave-jump accent (house/electro signature)
    (40, 74, 780, 1200),   # E2
    (33, 76, 1200, 1440),  # A1
    (33, 92, 1440, 1680),  # A1 offbeat accent
    (40, 74, 1680, BAR),   # E2, terminal note ends flush at BAR
]
u = MusicUnit()
for p, v, s, e in line:
    u.add_event(MusicEvent(p, v, s, e))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

u = MusicUnit()
kick = beat_pattern()
snare = beat_pattern(beat_indices=(4, 12))
step = BAR // 16
for i in range(16):
    if kick[i]:
        u.add_event(MusicEvent(KIT["kick"], VELOCITIES["kick"], i * step, i * step + step))
    if snare[i]:
        u.add_event(MusicEvent(KIT["snare"], VELOCITIES["snare"], i * step, i * step + step))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/synth_bass_2_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
msize = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({msize} bytes)")
assert msize > 40, "empty/corrupt MIDI"

# --- audio: SOLO synth bass 2 only, FluidR3 via discover_soundfont ------
from _test.render_audio import render_midi, spectral_buzz_check
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
print(f"SoundFont: {sf2}")
assert sf2 and "FluidR3" in sf2, f"expected FluidR3, got {sf2}"

wav = "/opt/data/projects/Instruments/_test/synth_bass_2_test.wav"
render_midi(midi_path, wav, solo=0)          # voice 0 = Synth Bass 2
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# --- stem label check against the ACTUAL pipeline GM_PROGRAMS -----------
import inspect
import re
from sound.render.pipeline import RenderPipeline

src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem label: GM_PROGRAMS[{SB2_PGM}] = {labels[SB2_PGM]!r}")
assert labels[SB2_PGM] == "Synth Bass 2", f"stem label mismatch: {labels[SB2_PGM]!r}"
assert STEM_LABEL == "Synth Bass 2".replace(" ", "_")

# --- SF2 preset name (phdr) ---------------------------------------------
import struct
data = open(sf2, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
sf2_name = preset_names.get((0, SB2_PGM), "MISSING")
print(f"SF2 preset {SB2_PGM} -> {sf2_name!r}")
assert sf2_name == "Synth Bass 2", f"SF2 preset mismatch: {sf2_name!r}"

# --- RenderPipeline stem render on disk ---------------------------------
out_dir = "/opt/data/projects/Instruments/_test/stems_synth_bass_2"
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    print(f"  {f} ({os.path.getsize(os.path.join(out_dir, f))} bytes)")
assert any("Synth_Bass_2" in f for f in stem_files), f"no Synth_Bass_2 stem: {stem_files}"
stem = [f for f in stem_files if "Synth_Bass_2" in f][0]
assert os.path.getsize(os.path.join(out_dir, stem)) > 40, "empty Synth Bass 2 stem"

# --- MonoSynth engine smoke test (primary synthesis) ---------------------
import numpy as np
from sound.synthesis.mono_synth import MonoSynth

sr = 22050
ms = MonoSynth(sample_rate=sr)
for k, v in SYNTHESIS_DEFAULTS.items():
    setattr(ms, k, v)
audio = ms.render_note(midi_note=40, duration=1.0, velocity=100)  # E2
peak = float(np.max(np.abs(audio)))
head = float(np.sqrt(np.mean(audio[: int(0.2 * sr)] ** 2)))
mid = float(np.sqrt(np.mean(audio[int(0.25 * sr):int(0.75 * sr)] ** 2)))
tail = float(np.sqrt(np.mean(audio[-int(0.2 * sr):] ** 2)))
print(f"\nMonoSynth E2 (resonance {SYNTHESIS_DEFAULTS['filter_resonance']}): "
      f"peak={peak:.3f} head_rms={head:.4f} mid_rms={mid:.4f} tail_rms={tail:.4f}")
assert peak > 0.01, "mono_synth render silent"
assert mid > tail, "acid note collapses (sustain does not hold)"

# spectral squelch check: the 1-3 kHz resonance band must carry real energy
spec = np.abs(np.fft.rfft(audio))
freqs = np.fft.rfftfreq(len(audio), 1 / sr)
squelch = spec[(freqs >= 800) & (freqs < 3000)].sum()
tot = spec[(freqs >= 50) & (freqs < 16000)].sum()
sfrac = squelch / max(tot, 1e-9)
print(f"Squelch band (0.8-3 kHz) energy = {sfrac * 100:.1f}% of audible")
assert sfrac > 0.05, "no squelch band — resonance missing"

# --- PhaseModSynth alternative smoke test --------------------------------
from sound.synthesis.phase_mod import PhaseModSynth
pm = PhaseModSynth(sample_rate=sr)
fm = pm.render_note(freq=midi_to_freq(40), duration=1.0, **FM_DEFAULTS)
fm_peak = float(np.max(np.abs(fm)))
print(f"PhaseModSynth E2: peak={fm_peak:.3f}")
assert fm_peak > 0.01, "phase_mod render silent"

print("\nALL CHECKS PASSED")
