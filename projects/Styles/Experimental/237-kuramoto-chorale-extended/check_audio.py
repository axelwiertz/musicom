# -*- coding: utf-8 -*-
import wave
import numpy as np

WAV = "/opt/data/projects/Styles/Experimental/237-kuramoto-chorale-extended/Audio/237-kuramoto-chorale-extended.wav"
w = wave.open(WAV, "rb")
sr = w.getframerate()
n = w.getnframes()
ch = w.getnchannels()
data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
w.close()
if ch == 2:
    data = data.reshape(-1, 2)
    mono = data.mean(axis=1)
else:
    mono = data
dur = n / sr / ch  # note: n is total frames; for stereo, frames = n//ch
print(f"sr={sr} ch={ch} frames={n} duration={n/sr/ch:.2f}s")
silent = np.sum(np.abs(mono) < 0.001) / len(mono)
print(f"silence ratio (<0.001 abs) = {silent*100:.2f}%")
rms = np.sqrt(np.mean(mono**2))
peak = np.max(np.abs(mono))
print(f"RMS = {rms:.4f}, peak = {peak:.4f}")
# per-second RMS map (first 60s)
secs = min(60, len(mono)//sr)
print("per-second RMS (dBFS):")
for i in range(secs):
    seg = mono[i*sr:(i+1)*sr]
    r = np.sqrt(np.mean(seg**2))
    db = 20*np.log10(r+1e-9)
    print(f"  {i:2d}s: {db:6.1f} dB")
