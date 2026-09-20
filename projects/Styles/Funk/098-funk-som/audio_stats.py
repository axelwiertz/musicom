# -*- coding: utf-8 -*-
"""Compute audio statistics for 098-funk-som: duration, silence, RMS, FFT tonal windows."""
import json
import wave
import numpy as np
from pathlib import Path

ROOT = Path("/opt/data/repos/musicom/projects/Styles/Funk/098-funk-som")
out = {}
for name in ("098-funk-som", "098-funk-som-phase1"):
    wav = ROOT / "Audio" / f"{name}.wav"
    if not wav.exists():
        continue
    wf = wave.open(str(wav), "rb")
    sr, ch = wf.getframerate(), wf.getnchannels()
    raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    wf.close()
    mono = raw.reshape(-1, ch).mean(axis=1) if ch > 1 else raw
    dur = len(mono) / sr
    sil = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    secs = [float(np.sqrt(np.mean(mono[int(s * sr):int((s + 1) * sr)] ** 2))) for s in range(int(dur))]
    silent = [s for s, v in enumerate(secs) if v < 0.001]
    last_audio = max([s for s, v in enumerate(secs) if v >= 0.001] or [0])
    peak = float(np.max(np.abs(mono)))
    rms = float(np.sqrt(np.mean(mono ** 2)))
    
    # 0.5s FFT windows for tonal verification in 50-1000 Hz
    tonal, nwin = 0, 0
    win = int(0.5 * sr)
    for start in range(0, len(mono) - win, win):
        seg = mono[start:start + win]
        nwin += 1
        if np.max(np.abs(seg)) < 0.001:
            continue
        spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        freqs = np.fft.rfftfreq(len(seg), 1.0 / sr)
        band = (freqs >= 50) & (freqs <= 1000)
        if band.any():
            f_peak = freqs[band][np.argmax(spec[band])]
            if f_peak >= 50:
                tonal += 1
    out[name] = {
        "duration_s": round(dur, 2),
        "channels": ch,
        "silence_ratio": round(sil, 4),
        "silent_secs": silent,
        "last_audio_sec": last_audio,
        "peak": round(peak, 4),
        "rms_mean": round(rms, 5),
        "tonal_windows": f"{tonal}/{nwin}"
    }
    print(name, json.dumps(out[name]))

with open(ROOT / "Analysis" / "render_stats.json", "w") as f:
    json.dump(out, f, indent=2)
print("Saved render_stats.json")
