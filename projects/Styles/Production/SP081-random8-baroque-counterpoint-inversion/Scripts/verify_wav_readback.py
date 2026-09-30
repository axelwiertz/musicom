import wave, subprocess, numpy as np, os

base = "/opt/data/repos/musicom/projects/Styles/Production/SP081-random8-baroque-counterpoint-inversion"
wav = base + "/SP081-random8-baroque-counterpoint-inversion.wav"
ogg = base + "/SP081-random8-baroque-counterpoint-inversion.ogg"
stem = base + "/Audio/stems_wet/track00_Acoustic_Grand_Piano_RANDOM8.wav"

for p in [wav, ogg, stem]:
    print(p, os.path.getsize(p), "bytes")

with wave.open(wav, "rb") as wf:
    n = wf.getnframes(); sr = wf.getframerate(); nch = wf.getnchannels()
    raw = np.frombuffer(wf.readframes(n), dtype=np.int16)
    raw = raw.reshape(-1, nch) if nch == 2 else raw
    peak = np.max(np.abs(raw)) / 32767.0
    rms = float(np.sqrt(np.mean((raw.astype(np.float64)/32767.0)**2)))
    nz = int(np.sum(np.abs(raw) > 20))
    print(f"WAV read-back: sr={sr} nch={nch} dur={n/sr:.2f}s peak={peak:.4f} rms={rms:.4f} nonzero_samples={nz}/{raw.size}")

out = subprocess.run(["ffmpeg","-y","-loglevel","error","-i",ogg,"-f","f32le","-"],capture_output=True)
a = np.frombuffer(out.stdout, dtype=np.float32)
print(f"OGG decode: samples={a.size} peak={np.max(np.abs(a)):.4f} rms={float(np.sqrt(np.mean(a**2))):.4f}")
