# -*- coding: utf-8 -*-
"""Verify Ocarina constants work with musicom engine (SOLO render).

Uses the registry (by_name) to prove registration, then builds a 1-bar
UnitMatrixComposer with the ocarina solo on one voice. Renders to MIDI + WAV
via FluidSynth using discover_soundfont(). No unison doubling — no buzz.
"""
import os, sys
sys.path.insert(0, "/opt/data/repos/musicom")
sys.path.insert(0, "/opt/data/repos/musicom/projects/Instruments")

from instrument_registry import by_name, by_program, OCARINA

ocarina = by_name("ocarina")
print(f"Ocarina via registry: program={ocarina.midi_program} name={ocarina.name!r} "
      f"stem={ocarina.stem_label!r} sweet={ocarina.solo_range} "
      f"range={ocarina.range_min}-{ocarina.range_max}")

# Confirm by_program works too
inst = by_program(79)
assert inst.name == "Ocarina", f"by_program(79) -> {inst.name}"
print(f"by_program(79) -> {inst.name} (OK)")

# Import constants for direct reference
from Woodwind.ocarina.ocarina import (
    MIDI_PROGRAM as OC_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, FM_DEFAULTS, REVERB_TAIL, EQ_BODY,
    EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)

print(f"Ocarina consts: program={OC_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"solo={SOLO_RANGE} synth={SYNTHESIS} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Zones={ZONES}")
print(f"Arts={list(ARTICULATIONS)}")
print(f"FM: shape={FM_DEFAULTS['carrier_shape']} ratio={FM_DEFAULTS['mod_freq_ratio']} "
      f"depth={FM_DEFAULTS['mod_depth']}")
print(f"EQ: body={EQ_BODY} presence={EQ_PRESENCE} air={EQ_AIR}")

# ---- Full engine test: UnitMatrixComposer ----
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)  # SOLO — one voice only
comp.add_voice("Ocarina", program=OC_PGM, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Ocarina solo: sweet-spot melody line, end flush at BAR
u = MusicUnit()
notes = [72, 74, 76, 79, 81, 79, 76]  # C5 D5 E5 G5 A5 G5 E5
for i, p in enumerate(notes):
    start = i * 240
    end = BAR if i == len(notes) - 1 else start + 200
    u.add_event(MusicEvent(p, 78, start, end))
# Terminal landmark: fill any remaining ticks to BAR
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Research/outputs/ocarina_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, f"empty/corrupt MIDI ({size} bytes)"

# ---- Render SOLO via discover_soundfont() ----
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
print(f"\nSoundFont: {sf2}")
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

wav = "/opt/data/projects/Research/outputs/ocarina_test.wav"

# Solo render: extract only the ocarina track (voice 0 = track index 1)
import mido
import tempfile
m = mido.MidiFile(midi_path)
keep = [m.tracks[0]]  # tempo track
keep.append(m.tracks[1])  # ocarina (first voice = track 1)
sub = mido.MidiFile()
sub.ticks_per_beat = m.ticks_per_beat
sub.tracks = keep
fd, tmp_midi = tempfile.mkstemp(suffix=".mid")
os.close(fd)
sub.save(tmp_midi)

import subprocess
r = subprocess.run([fluidsynth, "-ni", "-g", "1.2", "-F", wav, sf2, tmp_midi],
                   capture_output=True)
os.unlink(tmp_midi)
if r.returncode != 0:
    raise RuntimeError(f"fluidsynth failed: {r.stderr.decode()[-500:]}")

wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, f"empty/corrupt WAV ({wsize} bytes)"

# ---- Spectral buzz check ----
import numpy as np
import wave
from numpy.fft import rfft

w = wave.open(wav, "rb")
sr = w.getframerate()
n = w.getnframes()
data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
w.close()
seg = data[:int(0.5 * sr)]
spec = np.abs(rfft(seg))
freqs = np.fft.rfftfreq(len(seg), 1 / sr)
buzz = spec[(freqs >= 4000) & (freqs < 8000)].sum()
tot = spec[(freqs >= 50) & (freqs < 16000)].sum()
frac = buzz / max(tot, 1e-9)
print(f"Spectral check: 4-8kHz buzz = {frac * 100:.1f}% "
      f"({'OK' if frac <= 0.20 else 'BUZZ'})")
assert frac <= 0.20, f"buzz too high: {frac*100:.1f}%"

# ---- Stem label check against pipeline GM_PROGRAMS ----
import inspect
import re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
print(f"  [79] = {labels[79]!r}")
assert labels[79] == "Ocarina", f"stem label mismatch: {labels[79]!r}"
print(f"  Ocarina -> {labels[OC_PGM]!r} (matches STEM_LABEL={STEM_LABEL!r})")

# RenderPipeline stem render
out_dir = "/opt/data/projects/Research/outputs/stems_ocarina"
os.makedirs(out_dir, exist_ok=True)
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Ocarina" in f for f in stem_files), f"no Ocarina stem in {stem_files}"
oc_stem = [f for f in stem_files if "Ocarina" in f][0]
assert os.path.getsize(os.path.join(out_dir, oc_stem)) > 40, "empty Ocarina stem"

print("\nALL CHECKS PASSED")