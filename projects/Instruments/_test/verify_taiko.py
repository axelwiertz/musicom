# -*- coding: utf-8 -*-
"""Verify Taiko constants work with musicom engine (registry-backed, solo render)."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- Registration proof: import THROUGH the registry ---------------------
from instrument_registry import (
    by_name, by_program, registry_table, ALL_INSTRUMENTS,
)

TAIKO = by_name("taiko")
print("Registry: by_name('taiko') =", TAIKO)
print("Registry: by_name('taiko drum') =", by_name("taiko drum"))
print("Registry: by_program(116) =", by_program(116))
assert TAIKO.midi_program == 116
assert by_program(116).name == "Taiko Drum"
print("Registry: ALL_INSTRUMENTS count =", len(ALL_INSTRUMENTS))
table = registry_table()
print("Registry table:\n" + table)
assert "| World | Taiko Drum | 116 |" in table, "taiko row missing from registry_table()"

# ---- Constants through the registry ---------------------------------------
MIDI_PROGRAM = TAIKO.midi_program
GM_NAME = TAIKO.gm_name
STEM_LABEL = TAIKO.stem_label
SOLO_RANGE = TAIKO.solo_range
SWEET_SPOT = TAIKO.sweet_spot
ZONES = TAIKO.zones
ARTICULATIONS = TAIKO.articulations
SYNTHESIS = TAIKO.synthesis
MODAL_PRESET = TAIKO.modal_preset
TAIKO_MODES = TAIKO.taiko_modes if hasattr(TAIKO, "taiko_modes") else None
DRUM606_DEFAULTS = TAIKO.drum606_defaults
FM_DEFAULTS = TAIKO.fm_defaults
REVERB_TAIL = TAIKO.reverb_tail
EQ_BODY = TAIKO.eq_body
EQ_PRESENCE = TAIKO.eq_presence
EQ_AIR = TAIKO.eq_air
PAN = TAIKO.pan

print(f"\nTaiko: program={MIDI_PROGRAM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"range={TAIKO.range_min}-{TAIKO.range_max} sweet={SWEET_SPOT} "
      f"solo={SOLO_RANGE}")
print(f"Taiko: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"modal={MODAL_PRESET!r}")
print(f"Taiko: drum606={DRUM606_DEFAULTS} fm={FM_DEFAULTS}")
print(f"Taiko: reverb={REVERB_TAIL}s eq={EQ_BODY},{EQ_PRESENCE},{EQ_AIR} pan={PAN}")
from World.taiko.taiko import midi_to_freq, TAIKO_MODES as MODES_DIRECT
print(f"Taiko: C2={midi_to_freq(36):.1f}Hz E2={midi_to_freq(40):.1f}Hz "
      f"A2={midi_to_freq(45):.1f}Hz G3={midi_to_freq(55):.1f}Hz G4={midi_to_freq(67):.1f}Hz")
print(f"Taiko: modes={MODES_DIRECT}")
assert TAIKO.in_range(36) and TAIKO.in_range(67) and not TAIKO.in_range(35)
assert TAIKO.in_sweet_spot(50)
assert not TAIKO.in_sweet_spot(36), "C2 is range floor, not sweet spot"
# modes: shell ~90 Hz below head (0,1) 110 Hz; inharmonic partners 1.6x/2.14x/2.65x
assert MODES_DIRECT[0][0] == 90.0 and MODES_DIRECT[1][0] == 110.0
assert [round(f / 110.0, 2) for f, _, _ in MODES_DIRECT[2:]] == [1.6, 2.13, 2.64]

# ---- Engine test: UnitMatrixComposer (1 bar, 1 section) --------------------
# Voice stack: Taiko solo kuchi-shoga line (ch0). Context: ONE low bass note
# an octave+ below (ch1, GM33) — NOT a second melodic patch on the same pitches.
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=90, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Taiko", program=MIDI_PROGRAM, channel=0)
comp.add_voice("Bass", program=33, channel=1)
comp.add_section("A", bars=1)

BAR = 1920

# Taiko: DON don DOKO DON — kuchi-shoga festival pattern. DON = fat accent
# strokes on the beat (high velocity), DOKO = lighter off-beat. Last event
# ends FLUSH at BAR (terminal landmark).
u = MusicUnit()
# (pitch, vel, start, dur) — E2/G2/G3 DONs + A2 DOKOs, kumi-daiko floor zone
pattern = [
    (40, 99, 0, 480),      # DON  (E2, beat 1 — the accent)
    (45, 74, 480, 240),    # doko (A2, off-beat)
    (45, 74, 720, 240),    # doko
    (43, 96, 960, 480),    # DON  (G2, beat 3)
    (45, 74, 1440, 240),   # doko
    (45, 74, 1680, 240),   # doko
    (40, 99, 1920 - 480, 480),  # DON pickup into next bar — ends flush
]
# NOTE: pattern starts at 0 and the last stroke lands at 1440+480=1920 —
# re-lay it cleanly below (previous list kept for documentation).
u = MusicUnit()
pattern = [
    (40, 99, 0, 480),      # DON  E2, beat 1
    (45, 74, 480, 240),    # doko A2
    (45, 74, 720, 240),    # doko
    (43, 96, 960, 480),    # DON  G2, beat 3
    (45, 74, 1440, 240),   # doko
    (45, 99, 1680, 240),   # DON  A2 pickup, ends at 1920 FLUSH
]
for p, v, s, d in pattern:
    u.add_event(MusicEvent(p, v, s, s + d))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

# Context: low bass E1 (28) — below the taiko's lowest note (36)
u = MusicUnit()
u.add_event(MusicEvent(28, 58, 0, BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/taiko_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---- Render SOLO via discover_soundfont() (FluidR3 preferred) -------------
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/taiko_test.wav"
render_midi(midi_path, wav, solo=0)  # voice 0 = Taiko ONLY
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# ---- Stem label check against ACTUAL pipeline GM_PROGRAMS (0-indexed) -----
import inspect
import re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
for idx in [112, 113, 114, 115, 116, 117, 118]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Taiko -> {labels[MIDI_PROGRAM]!r}")
assert labels[MIDI_PROGRAM] == "Taiko Drum", f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"
assert STEM_LABEL == "Taiko Drum"

# ---- SF2 preset name check (phdr chunk, resolved SoundFont) ---------------
from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
print(f"\nSF2: {sf2}")
import struct
with open(sf2, "rb") as f:
    data = f.read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
sf2_name = preset_names.get((0, MIDI_PROGRAM), "MISSING")
print(f"SF2 preset {MIDI_PROGRAM} -> {sf2_name!r}")
assert sf2_name == "Taiko Drum", f"SF2 preset mismatch: {sf2_name!r}"

# ---- Full RenderPipeline stem render — taiko stem label on disk -----------
out_dir = "/opt/data/projects/Instruments/_test/stems_taiko"
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Taiko_Drum" in f for f in stem_files), f"no Taiko_Drum stem in {stem_files}"
tk_stem = [f for f in stem_files if "Taiko_Drum" in f][0]
assert os.path.getsize(os.path.join(out_dir, tk_stem)) > 40, "empty Taiko stem"

# ---- ModalSynth TAIKO_MODES: shell-body thump + inharmonic membrane -------
from sound.synthesis.modal import ModalSynth
import numpy as np
sr = 22050
ms = ModalSynth(sample_rate=sr)
audio = ms.render_custom(MODES_DIRECT, duration=2.0, excitation="impulse")
peak = float(np.max(np.abs(audio)))

def band_ratio(sig, lo, hi, sr):
    seg = sig[:int(0.5 * sr)]
    spec = np.abs(np.fft.rfft(seg))
    fr = np.fft.rfftfreq(len(seg), 1 / sr)
    tot = spec[(fr >= 30) & (fr < 4000)].sum()
    band = spec[(fr >= lo) & (fr < hi)].sum()
    return float(band / max(tot, 1e-9))

# shell-body band (60-110 Hz) must be the loudest region — the chest thump
p_shell = band_ratio(audio, 60, 110, sr)
p_head = band_ratio(audio, 100, 125, sr)
p_16 = band_ratio(audio, 160, 195, sr)   # 1.6x membrane partner
late = float(np.sqrt(np.mean(audio[int(1.0 * sr):int(1.5 * sr)] ** 2)) / peak)
print(f"\nModalSynth taiko (custom TAIKO_MODES): peak={peak:.3f} "
      f"late(1.0-1.5s)_rms/peak={late:.3f}")
print(f"  shell band 60-110Hz = {p_shell * 100:.1f}% of total, "
      f"head (0,1) 100-125Hz = {p_head * 100:.1f}%, 1.6x partner = {p_16 * 100:.1f}%")
assert peak > 0, "modal taiko render silent"
assert p_shell > 0.30, "no shell-body thump — chest character missing"
assert p_16 > 0.02, "no 1.6x membrane partner — inharmonic head character missing"

# Decay identity: taiko ring SHORTER than timpani (measured same way:
# late(1.0-1.5s) rms/peak). A taiko is ~0.5-0.8 s; timpani measured 0.134.
tim = ms.render_custom(
    [(440.0, 1.00, 0.9), (699.6, 0.50, 1.3), (941.6, 0.28, 1.8),
     (1012.0, 0.18, 2.4), (1166.0, 0.10, 3.0)], duration=2.0, excitation="impulse")
tim_late = float(np.sqrt(np.mean(tim[int(1.0 * sr):int(1.5 * sr)] ** 2))
                 / np.max(np.abs(tim)))
print(f"  ordering: taiko late={late:.4f} < timpani late={tim_late:.4f} (expected)")
assert late < tim_late, "taiko must ring SHORTER than the timpani bank"

# Stock 'drum' preset (MODAL_PRESET): closest bank, but too fast + no body
audio_d = ms.render_preset("drum", duration=2.0, excitation="impulse")
late_d = float(np.sqrt(np.mean(audio_d[int(1.0 * sr):int(1.5 * sr)] ** 2))
               / float(np.max(np.abs(audio_d))))
print(f"Stock 'drum' preset (MODAL_PRESET): late(1.0-1.5s)_rms/peak={late_d:.4f} "
      f"(too-fast documented)")

# ---- DrumSynth606 alternative: pitch-swept-sine thump ----------------------
from sound.synthesis.drum_synth_606 import DrumSynth606
ds = DrumSynth606(sample_rate=sr)
thumb = ds.tom(freq=DRUM606_DEFAULTS["freq"], decay=DRUM606_DEFAULTS["decay"],
               pitch_sweep=DRUM606_DEFAULTS["pitch_sweep"])
print(f"DrumSynth606 tom (DRUM606_DEFAULTS): peak={float(np.max(np.abs(thumb))):.3f} "
      f"len={len(thumb) / sr:.2f}s")
assert float(np.max(np.abs(thumb))) > 0, "606 taiko thump silent"

# ---- Empirical FluidR3 pitch sweep (RMS, notes across range) ---------------
from mido import MidiFile, MidiTrack, Message
import subprocess
import tempfile
import wave
notes = [36, 40, 45, 50, 55, 60, 64, 67]
results = {}
with tempfile.TemporaryDirectory() as td:
    for midi_note in notes:
        f = 440.0 * 2.0 ** ((midi_note - 69) / 12.0)
        mid = MidiFile(ticks_per_beat=480)
        tr = MidiTrack()
        tr.append(Message("program_change", program=MIDI_PROGRAM, channel=0, time=0))
        tr.append(Message("note_on", note=midi_note, velocity=100, channel=0, time=0))
        tr.append(Message("note_off", note=midi_note, velocity=0, channel=0, time=960))
        mid.tracks.append(tr)
        mpath = os.path.join(td, f"n{midi_note}.mid")
        wpath = os.path.join(td, f"n{midi_note}.wav")
        mid.save(mpath)
        r = subprocess.run([fluidsynth, "-ni", "-g", "1.2", "-F", wpath, sf2, mpath],
                           capture_output=True)
        assert r.returncode == 0, r.stderr.decode()[-300:]
        w = wave.open(wpath, "rb")
        srate = w.getframerate()
        d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        w.close()
        seg = d[:int(0.6 * srate)]
        rms = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
        results[midi_note] = (f, rms)
        print(f"note {midi_note:3d} ({f:7.1f} Hz) -> RMS {rms:.4f} "
              f"{'OK' if rms > 0.005 else 'SILENT?'}")
audible = sum(1 for _, r in results.values() if r > 0.005)
print(f"\nSweep: {audible}/{len(notes)} notes audible")
assert audible == len(notes), "SF2 gaps inside documented range"

print("\nALL CHECKS PASSED")
