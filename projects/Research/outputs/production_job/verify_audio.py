# -*- coding: utf-8 -*-
import numpy as np
import wave

w = wave.open('/opt/data/projects/Styles/Production/SP035-gendyn-soul-rbmpd/073-soul-rbmpd-gendyn.wav')
sr = w.getframerate()
n = w.getnframes()
data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32)/32767.0
dur = n/sr
mono = data
silent = np.sum(np.abs(mono) < 0.001)/len(mono)
print(f'duration={dur:.2f}s sr={sr} frames={n}')
print(f'silence_ratio={silent*100:.1f}%')
secs = int(dur)
rms = []
for s in range(secs):
    seg = mono[int(s*sr):int((s+1)*sr)]
    r = np.sqrt(np.mean(seg**2)) if len(seg) else 0
    rms.append(r)
line = ''.join('#' if r > 0.05 else ('+' if r > 0.01 else ('.' if r > 0.001 else ' ')) for r in rms)
print('RMS map per second:')
print(line)
peak = np.max(np.abs(mono))
print(f'peak={peak:.3f}')
