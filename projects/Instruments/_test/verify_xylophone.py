# -*- coding: utf-8 -*-
"""Verify Xylophone constants work with musicom engine (registry-backed, solo render)."""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- Registration proof: import THROUGH the registry ---------------------
from instrument_registry import (
    by_name, by_program, registry_table, ALL_INSTRUMENTS,
)

XYLOPHONE = by_name("xylophone")
print("Registry: by_name('xylophone') =", XYLOPHONE)
print("Registry: by_program(13) =", by_program(13))
assert XYLOPHONE.midi_program == 13
assert by_program(13).name == "Xylophone"
print("Registry: ALL_INSTRUMENTS count =", len(ALL_INSTRUMENTS))
table = registry_table()
print("Registry table:\n" + table)
assert "| Percussion | Xylophone | 13 |" in table, "xylophone row missing from registry_table()"

# ---- Constants through the registry ---------------------------------------
MIDI_PROGRAM = XYLOPHONE.midi_program
GM_NAME = XYLOPHONE.gm_name
STEM_LABEL = XYLOPHONE.stem_label
SOLO_RANGE = XYLOPHONE.solo_range
SWEET_SPOT = XYLOPHONE.sweet_spot
ZONES = XYLOPHONE.zones
ARTICULATIONS = XYLOPHONE.articulations
SYNTHESIS = XYLOPHONE.synthesis
MODAL_PRESET = XYLOPHONE.modal_preset
XYLOPHONE_MODES = XYLOPHONE.xylophone_modes
KARPLUS_DEFAULTS = XYLOPHONE.karplus_defaults
FM_DEFAULTS = XYLOPHONE.fm_defaults
REVERB_TAIL = XYLOPHONE.reverb_tail
EQ_BODY = XYLOPHONE.eq_body
EQ_PRESENCE = XYLOPHONE.eq_presence
EQ_AIR = XYLOPHONE.eq_air
PAN = XYLOPHONE.pan

print(f"\nXylophone: program={MIDI_PROGRAM} gm={GM_NAME!r} stem={STEM_LABEL!r} "
      f"range={XYLOPHONE.range_min}-{XYLOPHONE.range_max} sweet={SWEET_SPOT} "
      f"solo={SOLO_RANGE}")
print(f"Xylophone: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} "
      f"modal={MODAL_PRESET!r}")
print(f"Xylophone: karplus={KARPLUS_DEFAULTS} fm={FM_DEFAULTS}")
print(f"Xylophone: reverb={REVERB_TAIL}s eq={EQ_BODY},{EQ_PRESENCE},{EQ_AIR} pan={PAN}")
from Percussion.xylophone.xylophone import midi_to_freq, XYLOPHONE_MODES as MODES_DIRECT
print(f"Xylophone: F3={midi_to_freq(53):.1f}Hz C4={midi_to_freq(60):.1f}Hz "
      f"A4={midi_to_freq(69):.1f}Hz C6={midi_to_freq(84):.1f}Hz F6={midi_to_freq(89):.1f}Hz")
print(f"Xylophone: modes={XYLOPHONE_MODES}")
assert XYLOPHONE.in_range(53) and XYLOPHONE.in_range(89) and not XYLOPHONE.in_range(52)
assert XYLOPHONE.in_sweet_spot(72)
# arch-tuned 1:3:6 partial structure (rosewood: octave discarded, 12th kept)
assert [round(f / 440.0, 2) for f, _, _ in XYLOPHONE_MODES] == [1.0, 3.0, 6.0]

# ---- Engine test: UnitMatrixComposer (1 bar, 1 section) --------------------
# Voice stack: Xylophone solo melody (ch0). Context: ONE low bass note an
# octave+ below (ch1, GM33) — NOT a second melodic patch on the same pitches.
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("Xylophone", program=MIDI_PROGRAM, channel=0)
comp.add_voice("Bass", program=33, channel=1)
comp.add_section("A", bars=1)

BAR = 1920

# Xylophone: bright staccato melody line in the mid zone, 8 events, last one
# ends FLUSH at BAR (terminal landmark).
u = MusicUnit()
mel = [67, 71, 74, 76, 74, 71, 67, 74]   # G4 B4 D5 E5 D5 B4 G4 D5 — G major, mid zone
for i, p in enumerate(mel):
    start = i * 240
    end = BAR if i == len(mel) - 1 else start + 200
    u.add_event(MusicEvent(p, 84, start, end))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

# Context: low bass G2 (43) — well below the xylophone's lowest note (53)
u = MusicUnit()
u.add_event(MusicEvent(43, 58, 0, BAR))
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/xylophone_test.mid"
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# ---- Render SOLO via discover_soundfont() (FluidR3 preferred) -------------
from _test.render_audio import render_midi, spectral_buzz_check
wav = "/opt/data/projects/Instruments/_test/xylophone_test.wav"
render_midi(midi_path, wav, solo=0)  # track 1 = Xylophone (first voice) ONLY
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
for idx in [8, 9, 10, 11, 12, 13, 14, 15]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Xylophone -> {labels[MIDI_PROGRAM]!r}")
assert labels[MIDI_PROGRAM] == "Xylophone", f"stem label mismatch: {labels[MIDI_PROGRAM]!r}"
assert STEM_LABEL == "Xylophone"

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
assert sf2_name == "Xylophone", f"SF2 preset mismatch: {sf2_name!r}"

# ---- Full RenderPipeline stem render — xylophone stem label on disk ------
out_dir = "/opt/data/projects/Instruments/_test/stems_xylophone"
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
pipeline = RenderPipeline(fluidsynth_bin=fluidsynth, soundfont_path=sf2, gain=1.2)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Xylophone" in f for f in stem_files), f"no Xylophone stem in {stem_files}"
xy_stem = [f for f in stem_files if "Xylophone" in f][0]
assert os.path.getsize(os.path.join(out_dir, xy_stem)) > 40, "empty Xylophone stem"

# ---- ModalSynth XYLOPHONE_MODES: short dry ring + fundamental dominance ----
from sound.synthesis.modal import ModalSynth
import numpy as np
sr = 44100
ms = ModalSynth(sample_rate=sr)
audio = ms.render_custom(XYLOPHONE_MODES, duration=1.5, excitation="impulse")
peak = np.max(np.abs(audio))
late = np.sqrt(np.mean(audio[int(1.0 * sr):int(1.5 * sr)] ** 2))
late_ratio = late / peak if peak > 0 else 1.0
# marimba stock preset rings FAR longer (wrong structure + too-slow decay)
mar = ms.render_preset("marimba", duration=1.5, excitation="impulse")
mar_late = np.sqrt(np.mean(mar[int(1.0 * sr):int(1.5 * sr)] ** 2)) / np.max(np.abs(mar))
print(f"\nModalSynth XYLOPHONE_MODES: peak={peak:.3f} late(1.0-1.5s)_rms/peak={late_ratio:.4f}")
print(f"  marimba stock preset late(1.0-1.5s)_rms/peak={mar_late:.4f}")
assert peak > 0, "xylophone modal render silent"
assert late_ratio < 0.02, "xylophone bar should be DRY — expected a ~0.4 s ring, not a long one"
assert late_ratio < mar_late, "xylophone must decay FASTER than the marimba preset"

# partial check: fundamental dominates the 3x and 6x arch partials
spec = np.abs(np.fft.rfft(audio[: int(0.5 * sr)]))
freqs = np.fft.rfftfreq(int(0.5 * sr), 1 / sr)
def band(f, tol=12.0):
    sel = (freqs >= f - tol) & (freqs <= f + tol)
    return spec[sel].max() if sel.any() else 0.0
f0, f3, f6 = band(440.0), band(1320.0), band(2640.0)
print(f"  partials: f0={f0:.1f} 3x={f3:.1f} ({(f3 / f0) * 100:.1f}% of f0) "
      f"6x={f6:.1f} ({(f6 / f0) * 100:.1f}% of f0)")
assert f0 > f3 > f6, "xylophone fundamental must dominate the arch partials"

# decay rate check: fundamental mode rate 9.0 → e^-9t; at 0.4 s that's ~2.7%
# amplitude — check the 0.2-0.4 s window is well into decay
w1 = np.sqrt(np.mean(audio[int(0.1 * sr):int(0.2 * sr)] ** 2))
w2 = np.sqrt(np.mean(audio[int(0.3 * sr):int(0.4 * sr)] ** 2))
print(f"  decay: rms(0.1-0.2s)={w1:.4f} -> rms(0.3-0.4s)={w2:.4f} "
      f"(ratio {w2 / w1:.3f})")
assert 0 < w2 / w1 < 0.5, "expected clear decay across 0.1-0.4 s (rosewood-dry ring)"

# ---- Karplus-Strong fallback smoke test ----------------------------------
# Xylophone ring is the SHORTEST of the struck/plucked set (rosewood bar,
# ~0.4 s) — measure the 0.2-0.5 s window (kalimba lesson: NOT the 1-2 s
# window used for sitar/koto). Threshold 1.5x over the dull control, as for
# kalimba (short-ring instruments separate late, not 3x early).
from sound.synthesis.karplus_strong import karplus_strong
ks = karplus_strong(pitch=69, dur=1.5, vel=100, loop_gain=KARPLUS_DEFAULTS["loop_gain"])
ks_lo = karplus_strong(pitch=69, dur=1.5, vel=100, loop_gain=0.990)
kp, klp = np.max(np.abs(ks)), np.max(np.abs(ks_lo))
kt = np.sqrt(np.mean(ks[int(0.2 * sr):int(0.5 * sr)] ** 2)) / kp if kp > 0 else 1.0
kt_lo = np.sqrt(np.mean(ks_lo[int(0.2 * sr):int(0.5 * sr)] ** 2)) / klp if klp > 0 else 1.0
print(f"Karplus-Strong xylophone (fallback): tail_rms/peak(0.2-0.5s)={kt:.4f} "
      f"(dull control {kt_lo:.4f}, ratio {kt / kt_lo:.2f}x)")
assert kp > 0 and kt > 1.5 * kt_lo, "KS fallback shows no ring advantage"

# ordering check: xylophone ring must be SHORTER than kalimba's (wood bar
# vs metal tine) and shorter than banjo's (taut head) — both measured at the
# same 0.2-0.6 s window in their verify scripts
ks_kal = karplus_strong(pitch=69, dur=1.5, vel=100, loop_gain=0.9940)
ks_ban = karplus_strong(pitch=69, dur=1.5, vel=100, loop_gain=0.9960)
kt_kal = np.sqrt(np.mean(ks_kal[int(0.2 * sr):int(0.5 * sr)] ** 2)) / np.max(np.abs(ks_kal))
kt_ban = np.sqrt(np.mean(ks_ban[int(0.2 * sr):int(0.5 * sr)] ** 2)) / np.max(np.abs(ks_ban))
print(f"  ordering @0.2-0.5s: xylophone={kt:.4f} < kalimba={kt_kal:.4f} "
      f"< banjo={kt_ban:.4f} (expected)")
assert kt < kt_kal < kt_ban, "xylophone ring should be the shortest of the plucked/struck set"

# ---- Empirical FluidR3 pitch sweep (RMS, notes across range) --------------
from mido import MidiFile, MidiTrack, Message
import subprocess
import tempfile
import wave
notes = [53, 57, 60, 65, 69, 72, 77, 81, 84, 89]
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
