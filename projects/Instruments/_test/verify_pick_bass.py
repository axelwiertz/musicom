# -*- coding: utf-8 -*-
"""Verify Electric Bass (pick) (GM34) end-to-end — registry → composer → MIDI → WAV.

Structure follows _test/verify_guitar_harmonics.py (which follows verify_marimba.py):
constants are imported THROUGH the registry and the audio check renders the
instrument SOLO (one melodic voice, one track). A drum track is added only as
a context check and is NOT part of the solo WAV.
"""
import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

# ---- 1. Registration proof: constants come from the registry ------------
from instrument_registry import by_name, by_program, PICK_BASS as PB

print(f"registry: {PB!r}")
print(f"PB.midi_program={PB.midi_program} name={PB.gm_name!r} "
      f"stem={PB.stem_label!r} range={PB.range_min}-{PB.range_max} "
      f"sweet={PB.sweet_spot} synth={PB.synthesis}")
print(f"by_name('pick bass') = {by_name('pick bass')!r}")
print(f"by_program(34) = {by_program(34)!r}")

from Bass.pick_bass.pick_bass import (
    MIDI_PROGRAM, GM_NAME, STEM_LABEL, SOLO_RANGE, ZONES, ARTICULATIONS,
    SYNTHESIS, MODAL_PRESET, KARPLUS_DEFAULTS, FM_DEFAULTS,
    REVERB_TAIL, EQ_BODY, EQ_PRESENCE, EQ_AIR, PAN, midi_to_freq,
)

assert MIDI_PROGRAM == PB.midi_program == 34
assert PB.zones == ZONES and PB.articulations == ARTICULATIONS
assert PB.karplus_defaults == KARPLUS_DEFAULTS
print(f"\nzones={ZONES}")
print(f"articulations={list(ARTICULATIONS)}")
print(f"reverb={REVERB_TAIL}s eq_body={EQ_BODY} eq_presence={EQ_PRESENCE} "
      f"eq_air={EQ_AIR} pan={PAN}")
print(f"freq: E1(28)={midi_to_freq(28):.1f}Hz E2(40)={midi_to_freq(40):.1f}Hz "
      f"A4(69)={midi_to_freq(69):.1f}Hz")

# ---- 2. Zero-drift composer ---------------------------------------------
from structures import MusicEvent, MusicUnit
from workflows.unitmatrix_composer import UnitMatrixComposer

BAR = 1920
comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=2, num_sections=1)
comp.add_voice("PickBass", program=MIDI_PROGRAM, channel=0)
comp.add_voice("Drums", program=0, channel=9)   # context only; NOT in solo WAV
comp.add_section("A", bars=1)

# Driving pick-bass eighth-note riff: E2 E2 B2 B2 G2 G2 A2 B2 (root-fifth)
riff = [40, 40, 47, 47, 43, 43, 45, 47]
u = MusicUnit()
for i, p in enumerate(riff):
    start = i * 240
    end = BAR if i == len(riff) - 1 else start + 220
    u.add_event(MusicEvent(p, 88, start, end))
if u.len_ticks() < BAR:
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
comp.set_unit(0, 0, u)

u = MusicUnit()
for p, v, s in [(36, 96, 0), (42, 62, 0), (42, 54, 240), (38, 88, 480),
                (42, 56, 720), (36, 94, 960), (42, 60, 960), (42, 52, 1200),
                (38, 86, 1440), (42, 58, 1680)]:
    u.add_event(MusicEvent(p, v, s, min(s + 120, BAR)))
u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))      # terminal landmark
comp.set_unit(1, 0, u)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"zero-drift failed: {msg}"

MID = "/opt/data/projects/Instruments/_test/pick_bass_test.mid"
comp.to_midi(MID)
msize = os.path.getsize(MID)
print(f"MIDI: {MID} ({msize} bytes)")
assert msize > 40, "empty/corrupt MIDI"

# ---- 3. Solo WAV render through discover_soundfont() --------------------
import wave
import numpy as np
from sound.render.fluidsynth import discover_soundfont
from _test.render_audio import render_midi, spectral_buzz_check

sf2 = discover_soundfont()
print(f"soundfont: {sf2}")
assert sf2 and "FluidR3" in os.path.basename(sf2), f"wrong soundfont: {sf2}"

WAV = "/opt/data/projects/Instruments/_test/pick_bass_test.wav"
render_midi(MID, WAV, solo=0)          # SOLO pick bass — track 1 only
wsize = os.path.getsize(WAV)
print(f"WAV (solo): {WAV} ({wsize} bytes)")
assert wsize > 40, "empty/corrupt WAV"

ok, rep = spectral_buzz_check(WAV)
print(f"Spectral check: {rep}")
assert ok, f"buzz in solo render: {rep}"


def load(path):
    w = wave.open(path, "rb")
    sr = w.getframerate()
    d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    w.close()
    return sr, d.astype(np.float32) / 32768


def centroid(x, sr):
    s = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    f = np.fft.rfftfreq(len(x), 1 / sr)
    return float((s * f).sum() / max(s.sum(), 1e-9))


# ---- 4. Pitch + PICK BRIGHTNESS proof in the rendered artifact ----------
sr, audio = load(WAV)
seg = audio[int(0.02 * sr):int(0.30 * sr)]        # first note = written 40
spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
fr = np.fft.rfftfreq(len(seg), 1 / sr)
expected = midi_to_freq(40)
# fundamental-band peak search (±10% of E2) — the patch's 3rd partial can
# rival the fundamental in a short window, so do NOT take the global argmax
band = np.where(np.abs(fr - expected) < 0.10 * expected)[0]
peak = fr[band[np.argmax(spec[band])]]
print(f"\nWritten 40 ({expected:.1f} Hz) rendered fundamental peak {peak:.1f} Hz "
      f"(ratio {peak / expected:.2f}x — pick bass is NON-transposing)")
assert abs(peak - expected) / expected < 0.06, "pitch not confirmed"

# brightness: same note through GM34 (pick) vs GM33 (finger) in the SF2
import mido
import subprocess
import tempfile


def render_note(program, note=45, dur=960):
    m = mido.MidiFile(); m.ticks_per_beat = 480
    t0 = mido.MidiTrack(); m.tracks.append(t0)
    t0.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120), time=0))
    t0.append(mido.MetaMessage("end_of_track", time=2 * dur))
    t1 = mido.MidiTrack(); m.tracks.append(t1)
    t1.append(mido.Message("program_change", program=program, channel=0, time=0))
    t1.append(mido.Message("note_on", note=note, velocity=90, channel=0, time=0))
    t1.append(mido.Message("note_off", note=note, velocity=0, channel=0, time=dur))
    t1.append(mido.MetaMessage("end_of_track", time=dur))
    fd, mid = tempfile.mkstemp(suffix=".mid"); os.close(fd); m.save(mid)
    wav = mid.replace(".mid", ".wav")
    r = subprocess.run([os.environ.get("MUSICOM_FLUIDSYNTH",
                                       "/opt/data/micromamba/envs/musicom/bin/fluidsynth"),
                        "-ni", "-g", "1.2", "-F", wav, sf2, mid],
                       capture_output=True)
    assert r.returncode == 0, r.stderr[-300:]
    s, a = load(wav)
    os.unlink(mid); os.unlink(wav)
    return s, a


for note in (40, 45, 50):
    s1, a1 = render_note(33, note)
    s2, a2 = render_note(34, note)
    n = int(0.5 * s1)
    c1, c2 = centroid(a1[:n], s1), centroid(a2[:n], s2)
    print(f"note {note}: centroid finger(GM33)={c1:6.0f} Hz "
          f"pick(GM34)={c2:6.0f} Hz (+{100 * (c2 - c1) / c1:4.0f}%)")
    assert c2 > c1, f"pick patch not brighter at note {note}"

# ---- 5. Karplus-Strong smoke -------------------------------------------
from sound.synthesis.karplus_strong import karplus_strong

kd = KARPLUS_DEFAULTS
ks = karplus_strong(40, 3.0, vel=100, loop_gain=kd["loop_gain"],
                    width=kd["width"], sr=44100)
ks_peak = float(np.max(np.abs(ks)))
ks_late = float(np.sqrt(np.mean(ks[int(1.0 * 44100):int(2.0 * 44100)] ** 2))) / ks_peak
dull = karplus_strong(40, 3.0, vel=100, loop_gain=0.990,
                      width=kd["width"], sr=44100)
dull_peak = float(np.max(np.abs(dull)))
dull_late = float(np.sqrt(np.mean(dull[int(1.0 * 44100):int(2.0 * 44100)] ** 2))) / dull_peak
finger = karplus_strong(40, 3.0, vel=100, loop_gain=0.9970,
                        width=0.6, sr=44100)
finger_peak = float(np.max(np.abs(finger)))
finger_late = float(np.sqrt(np.mean(finger[int(1.0 * 44100):int(2.0 * 44100)] ** 2))) / finger_peak
print(f"\nKarplus loop_gain={kd['loop_gain']}: peak={ks_peak:.3f} "
      f"tail(1-2s)={ks_late:.5f} vs 0.990 dull {dull_late:.5f} "
      f"({ks_late / dull_late:.1f}x) and vs finger 0.9970 {finger_late:.5f} "
      f"({ks_late / finger_late:.2f}x — SHORTER, as intended)")
assert ks_peak > 0 and ks_late / dull_late > 1.5, "KS ring not longer than dull control"
assert ks_late / finger_late < 1.15, "pick ring should not exceed the finger patch"

# ---- 6. Stem labels + SF2 preset ---------------------------------------
import inspect
import re
import struct
from sound.render.pipeline import RenderPipeline

src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print(f"\nStem label: GM_PROGRAMS[34] = {labels[34]!r} -> "
      f"file {labels[34].replace(' ', '_').replace('(', '').replace(')', '')!r}")
assert labels[34] == "Electric Bass (pick)", f"stem label mismatch: {labels[34]!r}"
assert STEM_LABEL == "Electric_Bass_pick"

data = open(sf2, "rb").read()
phdr = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr + 4:phdr + 8])[0]
presets = {}
for i in range(phdr_size // 38):
    off = phdr + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    pn, bk = struct.unpack("<HH", data[off + 20:off + 24])
    presets[(bk, pn)] = name
sf2_name = presets.get((0, 34), "MISSING")
print(f"SF2 preset 34 -> {sf2_name!r}")
assert "Picked" in sf2_name, f"SF2 preset mismatch: {sf2_name!r}"

out_dir = "/opt/data/projects/Instruments/_test/stems_pick_bass"
pipeline = RenderPipeline(fluidsynth_bin=os.environ["MUSICOM_FLUIDSYNTH"],
                          soundfont_path=sf2, gain=1.2)
pipeline.render_stems(MID, out_dir)
stems = sorted(os.listdir(out_dir))
print(f"Stems ({len(stems)}):")
for f in stems:
    print(f"  {f} ({os.path.getsize(os.path.join(out_dir, f))} bytes)")
hit = [f for f in stems if "Electric_Bass_pick" in f]
assert hit, f"no Electric_Bass_pick stem in {stems}"
assert os.path.getsize(os.path.join(out_dir, hit[0])) > 40, "empty stem"

print("\nALL CHECKS PASSED")
