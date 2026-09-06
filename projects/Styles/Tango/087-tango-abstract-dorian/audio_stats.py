# -*- coding: utf-8 -*-
"""087 audio stats: correct stereo-aware silence + RMS (duration sanity)."""
import json
import wave
import numpy as np
from pathlib import Path

ROOT = Path("/opt/data/projects/Styles/Tango/087-tango-abstract-dorian")
out = {}
for name in ("087-tango-abstract-dorian", "087-tango-abstract-dorian-phase1"):
    wav = ROOT / "Audio" / f"{name}.wav"
    wf = wave.open(str(wav), "rb")
    sr, ch = wf.getframerate(), wf.getnchannels()
    raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    wf.close()
    mono = raw.reshape(-1, ch).mean(axis=1) if ch > 1 else raw
    dur = len(mono) / sr
    sil = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    secs = [float(np.sqrt(np.mean(mono[int(s * sr):int((s + 1) * sr)] ** 2)))
            for s in range(int(dur))]
    silent = [s for s, v in enumerate(secs) if v < 0.001]
    last_audio = max(s for s, v in enumerate(secs) if v >= 0.001)
    peak = float(np.max(np.abs(mono)))
    rms = float(np.sqrt(np.mean(mono ** 2)))
    out[name] = {"duration_s": round(dur, 2), "channels": ch,
                 "silence_ratio": round(sil, 4), "silent_secs": silent,
                 "last_audio_sec": last_audio, "peak": round(peak, 4),
                 "rms_mean": round(rms, 5)}
    print(name, json.dumps(out[name]))
with open(ROOT / "Analysis" / "render_stats.json", "w") as f:
    json.dump(out, f, indent=2)
