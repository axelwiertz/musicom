import wave, numpy as np, os

for name in ("072-world-melisma.wav", "072-world-melisma-phase1.wav"):
    p = f"/opt/data/projects/Styles/World/072-world-melisma/Audio/{name}"
    with wave.open(p, "rb") as wf:
        sr = wf.getframerate()
        n = wf.getnframes()
        ch = wf.getnchannels()
        data = np.frombuffer(wf.readframes(n), dtype=np.int16)
    mono = data.reshape(-1, ch).mean(axis=1) / 32768.0
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    dur = len(mono) / sr
    print(f"{name}: sr={sr} ch={ch} dur={dur:.2f}s peak={np.max(np.abs(mono)):.3f} silence={silent*100:.1f}%")
    # per-second RMS map
    rms = []
    sec = sr
    for i in range(0, len(mono), sec):
        seg = mono[i:i+sec]
        rms.append(float(np.sqrt(np.mean(seg**2))) if len(seg) else 0.0)
    print("  per-sec RMS:", " ".join(f"{v:.3f}" for v in rms))