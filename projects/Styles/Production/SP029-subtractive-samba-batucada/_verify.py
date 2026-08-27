import os, wave, numpy as np

base = "/opt/data/projects/Styles/Production/SP029-subtractive-samba-batucada/Audio"
for name in ["stem_kick_surdo.wav", "stem_agogo_polyblep.wav", "SP029-samba-batucada-subtractive.wav"]:
    p = os.path.join(base, name)
    with wave.open(p, "rb") as wf:
        n = wf.getnframes()
        sr = wf.getframerate()
        data = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
    rms = np.sqrt(np.mean(data ** 2))
    peak = np.max(np.abs(data))
    dur = n / sr
    print(f"{name}: dur={dur:.2f}s rms={rms:.4f} peak={peak:.3f} nonzero={np.count_nonzero(data)}/{len(data)}")
