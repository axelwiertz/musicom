# -*- coding: utf-8 -*-
"""Pitch sweep verification across full range of English Horn in FluidR3_GM.sf2."""
import wave
import numpy as np
import mido
import subprocess
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()

def test_note(pgm, note):
    mid = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.Message('program_change', channel=0, program=pgm, time=0))
    track.append(mido.Message('note_on', channel=0, note=note, velocity=80, time=0))
    track.append(mido.Message('note_off', channel=0, note=note, velocity=0, time=960))
    mid_path = '/opt/data/projects/Instruments/_test/english_horn_sweep.mid'
    mid.save(mid_path)
    wav_path = '/opt/data/projects/Instruments/_test/english_horn_sweep.wav'
    subprocess.run(['fluidsynth', '-ni', '-g', '1.2', '-F', wav_path, sf2, mid_path],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with wave.open(wav_path, 'rb') as wf:
        audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        rms = np.sqrt(np.mean(audio.astype(float)**2)) / 32768.0
        return rms

print("=== English Horn FluidR3_GM.sf2 Pitch Sweep (Notes 48 to 87) ===")
for note in range(48, 88):
    rms = test_note(69, note)
    status = "AUDIBLE" if rms > 0.005 else "SILENT"
    print(f"MIDI {note:2d}: RMS = {rms:.4f} [{status}]")
