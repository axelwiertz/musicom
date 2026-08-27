import numpy as np, wave, os
for name in ("074-groove-gpc.wav", "074-groove-gpc-phase1.wav"):
    p = f"/opt/data/projects/Styles/Groove/074-groove-gpc/Audio/{name}"
    w = wave.open(p, "rb")
    sr = w.getframerate()
    n = w.getnframes()
    data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32767.0
    mono = data[:: w.getnchannels()]
    silent = np.sum(np.abs(mono) < 0.001) / len(mono)
    sec = len(mono) / sr
    print(f"{name}: sr={sr} dur={sec:.1f}s silence={100*silent:.1f}% peak={np.max(np.abs(mono)):.3f}")
    # per-second RMS map
    per = [np.sqrt(np.mean(mono[i:i+sr]**2)) for i in range(0, len(mono)-sr, sr)]
    print("  per-sec RMS:", " ".join(f"{v:.3f}" for v in per))
