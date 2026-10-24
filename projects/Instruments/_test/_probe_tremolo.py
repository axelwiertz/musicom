# -*- coding: utf-8 -*-
"""Probe FluidR3 preset 44 (Tremolo Strings): phdr name + pitch sweep."""
import os, struct, subprocess, tempfile, wave, sys
sys.path.insert(0, "/opt/data/projects/Instruments")
import numpy as np
import mido

from sound.render.fluidsynth import discover_soundfont
sf2_path = discover_soundfont()
print(f"SoundFont: {sf2_path}")

data = open(sf2_path, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name
print(f"SF2 preset 44 -> {preset_names.get((0, 44), 'MISSING')!r}")
print(f"SF2 preset 43 -> {preset_names.get((0, 43), 'MISSING')!r} (Contrabass)")
print(f"SF2 preset 45 -> {preset_names.get((0, 45), 'MISSING')!r} (Pizzicato)")
print(f"SF2 preset 48 -> {preset_names.get((0, 48), 'MISSING')!r} (String Ensemble 1)")

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
def midi_to_freq(m): return 440.0 * 2.0 ** ((m - 69) / 12.0)

print("Sweep (RMS, notes 24-108 step 12 + 55-89 step 6):")
sweep_notes = list(range(24, 109, 12)) + list(range(55, 90, 6))
sweep_notes = sorted(set(sweep_notes))
for note in sweep_notes:
    mf = mido.MidiFile()
    t = mido.MidiTrack()
    t.append(mido.Message("program_change", program=44, channel=0, time=0))
    t.append(mido.Message("note_on", note=note, velocity=90, channel=0, time=0))
    t.append(mido.Message("note_off", note=note, velocity=0, channel=0, time=960))
    mf.tracks.append(t)
    fd, tmp = tempfile.mkstemp(suffix=".mid"); os.close(fd)
    mf.save(tmp)
    tmp_wav = tempfile.mktemp(suffix=".wav")
    r = subprocess.run([FLUID, "-ni", "-g", "1.2", "-F", tmp_wav, sf2_path, tmp],
                       capture_output=True)
    w = wave.open(tmp_wav, "rb"); sr = w.getframerate(); n = w.getnframes()
    d = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    w.close()
    # tremolo note: measure RMS over full note + per-100ms windows (tremolo ripple)
    rms = float(np.sqrt(np.mean(d ** 2)))
    win = max(1, sr // 10)
    segs = [float(np.sqrt(np.mean(d[i:i+win] ** 2))) for i in range(0, len(d)-win, win)]
    ripple = (max(segs) - min(segs)) / max(max(segs), 1e-9) if segs else 0.0
    os.unlink(tmp); os.unlink(tmp_wav)
    flag = "OK" if rms > 0.002 else "SILENT!"
    print(f"  note {note:3d} ({midi_to_freq(note):7.1f} Hz) rms={rms:.4f} trem-ripple={ripple:.2f} {flag}")
