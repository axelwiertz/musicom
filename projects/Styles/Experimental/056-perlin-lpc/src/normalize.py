# -*- coding: utf-8 -*-
"""Normalize LPC output to -1dB peak"""
import os
import numpy as np
import wave

INPUT = "/opt/data/projects/Styles/Experimental/056-perlin-lpc/Audio/056-perlin-lpc_lpc.wav"
OUTPUT = "/opt/data/projects/Styles/Experimental/056-perlin-lpc/Audio/056-perlin-lpc_norm.wav"

def read_wav(path):
    with wave.open(path, 'rb') as wf:
        sr = wf.getframerate()
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)
    if sampwidth == 2:
        audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    else:
        raise ValueError(f"Unsupported: {sampwidth}")
    if n_channels == 2:
        audio = audio.reshape(-1, 2).mean(axis=1)
    return audio, sr

def write_wav(path, audio, sr):
    audio_int16 = (audio * 32767).astype(np.int16)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_int16.tobytes())

audio, sr = read_wav(INPUT)
peak = np.max(np.abs(audio))
if peak > 0:
    target = 10 ** (-1.0 / 20.0)  # -1dB
    audio = audio * (target / peak)
write_wav(OUTPUT, audio, sr)
print(f"OK: {OUTPUT} ({os.path.getsize(OUTPUT)} bytes)")
