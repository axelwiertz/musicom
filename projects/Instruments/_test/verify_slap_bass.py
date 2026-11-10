# -*- coding: utf-8 -*-
"""Verify Slap Bass 1 (GM36) constants through the registry + audio render.

Structural template: _test/verify_synth_bass_2.py.
Audio render: INSTRUMENT SOLO ONLY (one melodic voice, one track) — the
2026-09-01 comb-filter rule. A drum-kit voice rides along for context but is
NOT part of the solo render.
"""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# --- prove REGISTRATION: import through the registry, not the module -----
from instrument_registry import by_name, by_program, SLAP_BASS

from Bass.slap_bass.slap_bass import (
    MIDI_PROGRAM as SB_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, KARPLUS_DEFAULTS, FM_DEFAULTS,
    MODAL_PRESET, REVERB_TAIL, EQ_BODY, EQ_PRESENCE, EQ_AIR, PAN,
    midi_to_freq,
)

assert SLAP_BASS is by_name("slap bass")
assert by_name("slap bass 1") is SLAP_BASS
assert by_program(36) is SLAP_BASS
assert SLAP_BASS.midi_program == 36
assert SLAP_BASS.name == "Slap Bass 1"
print(f"Registry: {SLAP_BASS}")
print(f"Slap Bass 1: program={SB_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"sweet={SLAP_BASS.sweet_spot} A4={midi_to_freq(69):.1f}Hz")
print(f"Slap Bass 1: zones={ZONES}")
print(f"Slap Bass 1: art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"modal_preset={MODAL_PRESET} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Slap Bass 1: E1={midi_to_freq(28):.2f}Hz A1={midi_to_freq(33):.2f}Hz "
      f"E2={midi_to_freq(40):.2f}Hz G3={midi_to_freq(55):.2f}Hz")

# --- engine test: 1 bar, 1 section ---------------------------------------
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES, beat_pattern

BAR = 1920
comp = UnitMatrixComposer(bpm=104, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Slap Bass 1", program=SB_PGM, channel=0)
comp.add_voice("Drums", program=0, channel=9)         # context only
comp.add_section("A", bars=1)

# One bar of funk slap groove in A (16ths, step = 120 ticks):
#  thumb slaps on A1/E2 (downbeats + syncopated), pops on A2/G3 (offbeats),
#  ghost notes between — the classic Larry Graham pocket.
step = BAR // 16
slap_line = [
    # (pitch, vel, start_tick, end_tick) — 16th grid
    (33, 100, 0 * step, 0 * step + 90),        # A1 downbeat SLAP (accent)
    (33, 70, 1 * step, 1 * step + 60),         # A1
    (45, 90, 2 * step, 2 * step + 80),         # A2 offbeat POP
    (38, 42, 3 * step, 3 * step + 45),         # D1 ghost
    (33, 78, 4 * step, 4 * step + 60),         # A1
    (45, 94, 5 * step, 5 * step + 70),         # A2 POP
    (33, 40, 6 * step, 6 * step + 45),         # A1 ghost
    (33, 82, 7 * step, 7 * step + 60),         # A1
    (40, 100, 8 * step, 8 * step + 90),        # E2 SLAP (beat 3)
    (38, 45, 9 * step, 9 * step + 45),         # D1 ghost
    (45, 92, 10 * step, 10 * step + 70),       # A2 POP
    (33, 76, 11 * step, 11 * step + 60),       # A1
    (33, 80, 12 * step, 12 * step + 60),       # A1
    (48, 96, 13 * step, 13 * step + 75),       # C3 POP (octave pop fill)
    (38, 40, 14 * step, 14 * step + 45),       # D1 ghost
    (33, 88, 15 * step, BAR),                  # A1 terminal — ends flush at BAR
]
u = MusicUnit()
for p, v, s, e in slap_line:
    u.add_event(MusicEvent(p, v, s, e))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

u = MusicUnit()
kick = beat_pattern()
snare = beat_pattern(beat_indices=(4, 12))
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

midi_path = "/opt/data/projects/Instruments/_test/slap_bass_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
msize = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({msize} bytes)")
assert msize > 40, "empty/corrupt MIDI"

# --- audio: SOLO slap bass only, FluidR3 via discover_soundfont ----------
from _test.render_audio import render_midi, spectral_buzz_check
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
print(f"SoundFont: {sf2}")
assert sf2 and "FluidR3" in sf2, f"expected FluidR3, got {sf2}"

wav = "/opt/data/projects/Instruments/_test/slap_bass_test.wav"
render_midi(midi_path, wav, solo=0)          # voice 0 = Slap Bass 1
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
print(f"\nStem label: GM_PROGRAMS[{SB_PGM}] = {labels[SB_PGM]!r}")
assert labels[SB_PGM] == "Slap Bass 1", f"stem label mismatch: {labels[SB_PGM]!r}"
assert STEM_LABEL == "Slap_Bass_1"

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
sf2_name = preset_names.get((0, SB_PGM), "MISSING")
print(f"SF2 preset {SB_PGM} -> {sf2_name!r}")
assert sf2_name == "Slap Bass", f"SF2 preset mismatch: {sf2_name!r}"

# --- RenderPipeline stem render on disk ---------------------------------
out_dir = "/opt/data/projects/Instruments/_test/stems_slap_bass"
pipeline = RenderPipeline(fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                          soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    print(f"  {f} ({os.path.getsize(os.path.join(out_dir, f))} bytes)")
assert any("Slap_Bass_1" in f for f in stem_files), f"no Slap_Bass_1 stem: {stem_files}"
stem = [f for f in stem_files if "Slap_Bass_1" in f][0]
assert os.path.getsize(os.path.join(out_dir, stem)) > 40, "empty Slap Bass 1 stem"

# --- Karplus-Strong engine smoke test (primary synthesis) ----------------
import numpy as np
from sound.synthesis.karplus_strong import karplus_strong

sr = 22050
audio = karplus_strong(pitch=40, dur=1.0, vel=100,   # E2
                       loop_gain=KARPLUS_DEFAULTS["loop_gain"],
                       width=KARPLUS_DEFAULTS["width"], sr=sr)
peak = float(np.max(np.abs(audio)))
head = float(np.sqrt(np.mean(audio[: int(0.2 * sr)] ** 2)))
tail = float(np.sqrt(np.mean(audio[-int(0.2 * sr):] ** 2)))
print(f"\nKarplus E2 (loop_gain {KARPLUS_DEFAULTS['loop_gain']}): "
      f"peak={peak:.3f} head_rms={head:.4f} tail_rms={tail:.4f}")
assert peak > 0.01, "karplus render silent"
assert head > tail, "slap string does not decay (no ring release)"

# --- PhaseModSynth alternative smoke test ---------------------------------
from sound.synthesis.phase_mod import PhaseModSynth
pm = PhaseModSynth(sample_rate=sr)
fm = pm.render_note(freq=midi_to_freq(40), duration=1.0, **FM_DEFAULTS)
fm_peak = float(np.max(np.abs(fm)))
print(f"PhaseModSynth E2: peak={fm_peak:.3f}")
assert fm_peak > 0.01, "phase_mod render silent"

# --- empirical pitch sweep (patch ceiling proof) --------------------------
print("\nEmpirical FluidR3 pitch sweep (RMS, velocity 90):")
import subprocess, tempfile, wave
def render_note(note, vel=90):
    c = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice("X", program=SB_PGM, channel=0)
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
    r = subprocess.run(["/opt/data/micromamba/envs/musicom/bin/fluidsynth",
                        "-ni", "-g", "1.2", "-F", wv, sf2, mp],
                       capture_output=True)
    os.unlink(mp)
    if r.returncode != 0 or not os.path.exists(wv):
        return None
    with wave.open(wv, "rb") as f:
        raw = np.frombuffer(f.readframes(f.getnframes()),
                            dtype=np.int16).astype(np.float64)
    os.unlink(wv)
    mono = raw.reshape(-1, 2).mean(axis=1) if raw.size % 2 == 0 else raw
    return float(np.sqrt(np.mean(mono ** 2)))

def n_to_name(n):
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return f"{names[n % 12]}{n // 12 - 1}"

sweep = []
for n in [24, 28, 33, 36, 40, 45, 48, 52, 55, 60, 64, 67, 72, 77, 84, 86]:
    r = render_note(n)
    sweep.append((n, r))
    print(f"  note {n:3d} ({n_to_name(n):>4s})  rms={r if r is None else round(r, 4)}")
audible = [(n, r) for n, r in sweep if r is not None and r > 1.0]
assert len(audible) == 15, f"expected 15 audible (24..84), got {len(audible)}"
assert all(n <= 84 for n, _ in audible), "patch plays above documented ceiling"
silent = [n for n, r in sweep if r is not None and r <= 1.0]
assert 86 in silent, f"expected 86 to be silent, got {silent}"

print("\nALL CHECKS PASSED")
