# -*- coding: utf-8 -*-
"""Verify Harmonica constants work with musicom engine (SOLO render)."""
import sys
import os
import struct
import inspect
import re
import subprocess
import mido
sys.path.insert(0, "/opt/data/projects/Instruments")

from Woodwind.harmonica.harmonica import (
    MIDI_PROGRAM as HARM_PGM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES,
    ARTICULATIONS, SYNTHESIS, FM_DEFAULTS, REVERB_TAIL, EQ_BODY,
    EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)

print(f"Harmonica: program={HARM_PGM} gm={GM_NAME!r} stem={STEM_LABEL!r} sweet={SOLO_RANGE} A4={midi_to_freq(69):.1f}Hz")
print(f"Harmonica: zones={ZONES} art={list(ARTICULATIONS)} synth={SYNTHESIS} fm_defaults={FM_DEFAULTS} reverb={REVERB_TAIL}s pan={PAN}")
print(f"Harmonica: D3={midi_to_freq(50):.1f}Hz C4={midi_to_freq(60):.1f}Hz C6={midi_to_freq(84):.1f}Hz C7={midi_to_freq(96):.1f}Hz")

# Full engine test: UnitMatrixComposer — SOLO harmonica only
# (no unison doubling of same pitches — that caused buzz in prior tests)
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=1, num_sections=1)
comp.add_voice("Harmonica", program=HARM_PGM, channel=0)
comp.add_section("A", bars=1)

BAR = 1920

# Harmonica: melodic free-reed solo — blues-style melody, end flush at BAR
u = MusicUnit()
for i, p in enumerate([64, 67, 71, 72, 71, 67, 64]):
    end_tick = BAR if i == 6 else i * 240 + 220
    u.add_event(MusicEvent(p, 78, i * 240, end_tick))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

midi_path = "/opt/data/projects/Instruments/_test/harmonica_test.mid"
import os
os.makedirs(os.path.dirname(midi_path), exist_ok=True)
comp.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f"MIDI: {midi_path} ({size} bytes)")
assert size > 40, "empty/corrupt MIDI"

# Render SOLO harmonica via discover_soundfont() (FluidR3 preferred)
from _test.render_audio import render_midi, spectral_buzz_check
from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
print(f"SoundFont: {sf2}")

wav = "/opt/data/projects/Instruments/_test/harmonica_test.wav"
render_midi(midi_path, wav, solo=0)  # solo=0 = first voice track
wsize = os.path.getsize(wav)
print(f"WAV (solo): {wav} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"

# Spectral buzz check
ok, rep = spectral_buzz_check(wav)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"

# Stem label check against ACTUAL pipeline GM_PROGRAMS (0-indexed)
import inspect
import re
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem labels (pipeline GM_PROGRAMS, 0-indexed):")
for idx in [20, 21, 22, 23, 24]:
    print(f"  [{idx}] = {labels[idx]!r}")
print(f"  Harmonica at [{HARM_PGM}] = {labels[HARM_PGM]!r}")
assert labels[HARM_PGM] == "Harmonica", f"stem label mismatch: {labels[HARM_PGM]!r}"
assert STEM_LABEL == "Harmonica"

# SF2 preset name for program 22 (verified from phdr chunk)
import struct
data = open(sf2, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off+20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
sf2_name = preset_names.get((0, HARM_PGM), "MISSING")
print(f"SF2 preset {HARM_PGM} -> {sf2_name!r}")
assert sf2_name == "Harmonica", f"SF2 preset mismatch: {sf2_name!r}"

# Full RenderPipeline stem render — check harmonica stem label on disk
out_dir = "/opt/data/projects/Instruments/_test/stems_harmonica"
pipeline = RenderPipeline(
    fluidsynth_bin="/opt/data/micromamba/envs/musicom/bin/fluidsynth",
    soundfont_path=sf2,
    gain=1.2
)
pipeline.render_stems(midi_path, out_dir)
stem_files = sorted(os.listdir(out_dir))
print(f"\nStems rendered ({len(stem_files)} files):")
for f in stem_files:
    fp = os.path.join(out_dir, f)
    print(f"  {f} ({os.path.getsize(fp)} bytes)")
assert any("Harmonica" in f for f in stem_files), f"no Harmonica stem in {stem_files}"
harm_stem = [f for f in stem_files if "Harmonica" in f][0]
assert os.path.getsize(os.path.join(out_dir, harm_stem)) > 40, "empty Harmonica stem"

# Quick pitch sweep: verify patch plays across full range
print(f"\nFluidR3 pitch sweep (notes 48-96, every 4th):")
for note in range(48, 97, 4):
    m = mido.MidiFile(ticks_per_beat=480)
    trk = mido.MidiTrack()
    trk.append(mido.MetaMessage("set_tempo", tempo=500000))
    trk.append(mido.Message("program_change", program=HARM_PGM, time=0))
    trk.append(mido.Message("note_on", note=note, velocity=80, time=0))
    trk.append(mido.MetaMessage("end_of_track", time=480))
    m.tracks.append(trk)
    tmp = "/tmp/harm_sweep_note.mid"
    m.save(tmp)
    r = subprocess.run(
        ["/opt/data/micromamba/envs/musicom/bin/fluidsynth", "-ni", "-g", "1.2", "-F", "/dev/null", sf2, tmp],
        capture_output=True, timeout=30
    )
    ok = "OK" if r.returncode == 0 else "FAIL"
    note_name = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"][note % 12] + str(note // 12 - 1)
    print(f"  Note {note} ({note_name}): {ok}")

print("\nALL CHECKS PASSED")