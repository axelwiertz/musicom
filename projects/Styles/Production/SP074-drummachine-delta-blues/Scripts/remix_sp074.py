# -*- coding: utf-8 -*-
"""Re-mix SP074 with time-aligned beds (fix length bug) + verify."""
import json
import shutil
import subprocess
import wave
from pathlib import Path
import numpy as np

SR = 44100
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP074-drummachine-delta-blues")

def read_wav(p):
    with wave.open(str(p), "rb") as wf:
        n = wf.getnframes(); ch = wf.getnchannels()
        raw = wf.readframes(n)
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    if ch == 2:
        a = a.reshape(-1, 2)
    else:
        a = np.stack([a, a], axis=1)
    return a

def write_wav(p, audio, sr=44100):
    a = np.asarray(audio)
    a = np.clip(a, -1.0, 1.0)
    ints = (a * 32767).astype(np.int16)
    ch = 1 if a.ndim == 1 else a.shape[1]
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(ch); wf.setsampwidth(2); wf.setframerate(sr)
        wf.writeframes(ints.tobytes())

# load: pitched beds from stems_dry (keep native lengths, fluidsynth tails legit)
beds = {}
for k in ["track00_Acoustic_Guitar_steel", "track01_Electric_Guitar_jazz", "track02_Acoustic_Bass"]:
    beds[k] = read_wav(OUT / "Audio" / "stems_dry" / (k + ".wav"))
bull = read_wav(OUT / "Audio" / "stems_processed" / "track04_Drums_BULLFROG.wav")
sub = read_wav(OUT / "Audio" / "stems_processed" / "track05_CV_sub_garnish.wav")

# target length = longest bed (lead 44.68s incl. fluid tail) - NO truncation of music
L = max(a.shape[0] for a in list(beds.values()) + [bull, sub])
print(f"target L={L} ({L/SR:.2f}s)")
def pad(a, L):
    if a.shape[0] < L:
        return np.vstack([a, np.zeros((L - a.shape[0], 2))])
    return a[:L]
beds_p = {k: pad(a, L) for k, a in beds.items()}
bull_p = pad(bull, L)
sub_p = pad(sub, L)

# music-aware balance: lead bed carries 290-note slide line; bass/harm support
mix = 1.0 * beds_p["track00_Acoustic_Guitar_steel"] \
    + 0.8 * beds_p["track01_Electric_Guitar_jazz"] \
    + 0.9 * beds_p["track02_Acoustic_Bass"] \
    + 1.0 * bull_p + sub_p
mix = mix / np.max(np.abs(mix)) * 0.89

from sound.effects.mastering import normalize_to_lufs, Limiter, measure_lufs
mix_lufs = normalize_to_lufs(mix, -14.0, SR)
final = Limiter(threshold_db=-1.0).process(mix_lufs)
lufs_val = float(measure_lufs(final, SR))
print(f"LUFS={lufs_val:.2f} peak={np.max(np.abs(final)):.4f}")

write_wav(OUT / "SP074-drummachine-delta-blues.wav", final, SR)
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(OUT / "SP074-drummachine-delta-blues.wav"),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(OUT / "SP074-drummachine-delta-blues.ogg")], capture_output=True, text=True)
print(f"ffmpeg rc={r.returncode}")
print(f"wav={ (OUT/'SP074-drummachine-delta-blues.wav').stat().st_size } ogg={(OUT/'SP074-drummachine-delta-blues.ogg').stat().st_size}")

# silence/RMS on remix
mono = final.mean(axis=1)
sil = float(np.sum(np.abs(mono) < 0.001) / len(mono))
print(f"silence={sil*100:.2f}%")
rms = [float(np.sqrt(np.mean(mono[i*SR:(i+1)*SR]**2))) for i in range(int(len(mono)/SR))]
print("RMS/s:", " ".join(f"{v:.3f}" for v in rms))

# update provenance
prov = json.loads((OUT / "provenance.json").read_text())
prov["lufs_remix"] = lufs_val
prov["mix_balance"] = "lead 1.0 / harm 0.8 / bass 0.9 / bullfrog 1.0 + cv sub; beds native-length (no truncation), zero-padded to longest (lead 44.68s)"
prov["fix"] = "V1 truncated all beds to drum-stem length (38.96s) cutting bars 11-12; V2 pads to longest bed, music intact"
(OUT / "provenance.json").write_text(json.dumps(prov, indent=2))
print("REMIX DONE")
