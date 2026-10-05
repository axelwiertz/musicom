# -*- coding: utf-8 -*-
"""Render 224-blues-otvl phase2 MIDI -> WAV (FluidSynth) -> OGG (Opus) +
silence / per-second RMS / FFT tonal verification."""
import json
import os
import subprocess
import wave

import numpy as np

PROJ = "/opt/data/repos/musicom/projects/Styles/Blues/224-blues-otvl"
MIDI = os.path.join(PROJ, "MIDI", "224-blues-otvl.mid")
WAV = os.path.join(PROJ, "Audio", "224-blues-otvl.wav")
OGG = os.path.join(PROJ, "Audio", "224-blues-otvl.ogg")
ANALYSIS = os.path.join(PROJ, "Analysis")
os.makedirs(os.path.join(PROJ, "Audio"), exist_ok=True)

PY = "/opt/data/micromamba/envs/musicom/bin"
FLUIDSYNTH = os.path.join(PY, "fluidsynth")

# discover soundfont
try:
    from sound.render.fluidsynth import discover_soundfont
    SF = discover_soundfont()
except Exception:
    SF = os.environ.get("MUSICOM_SOUNDFONT") or "/usr/share/sounds/sf2/FluidR3_GM.sf2"
print("soundfont:", SF)

# 1. FluidSynth -> WAV
cmd = [FLUIDSYNTH, "-ni", "-g", "1.2", "-F", WAV, SF, MIDI]
print("fluidsynth:", " ".join(cmd))
r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
print("fluidsynth rc:", r.returncode)
if r.returncode != 0:
    print("STDERR:", r.stderr[-2000:])
    raise SystemExit("fluidsynth failed")

# 2. Normalize WAV to ~-1 dBFS (peaknorm, fallback to volume if unavailable)
WAV_RAW = WAV
try:
    WAV_NORM = os.path.join(PROJ, "Audio", "224-blues-otvl-norm.wav")
    rn = subprocess.run(["ffmpeg", "-y", "-i", WAV_RAW, "-af", "peaknorm=level=-1",
                         WAV_NORM, "-loglevel", "error"],
                        capture_output=True, text=True, timeout=300)
    if rn.returncode == 0 and os.path.getsize(WAV_NORM) > 40:
        os.replace(WAV_NORM, WAV)
        print("normalized via peaknorm")
    else:
        rv = subprocess.run(["ffmpeg", "-y", "-i", WAV_RAW, "-af", "volume=1.07",
                             WAV_NORM, "-loglevel", "error"],
                            capture_output=True, text=True, timeout=300)
        if rv.returncode == 0 and os.path.getsize(WAV_NORM) > 40:
            os.replace(WAV_NORM, WAV)
            print("normalized via volume=1.07")
        else:
            print("normalization skipped (peak already safe)")
except Exception as e:
    print("normalization error (non-fatal):", repr(e))

# 3. WAV -> OGG (Opus voip)
cmd2 = ["ffmpeg", "-y", "-i", WAV, "-codec:a", "libopus",
        "-application", "voip", "-b:a", "48k", OGG, "-loglevel", "error"]
subprocess.run(cmd2, capture_output=True, text=True, timeout=300)

# 3. analysis
wf = wave.open(WAV, "rb")
sr = wf.getframerate()
nch = wf.getnchannels()
n = wf.getnframes()
data = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float32)
wf.close()
if nch == 2:
    data = data.reshape(-1, 2)
    mono = data.mean(axis=1)
else:
    mono = data

mono = mono / 32768.0
dur = len(mono) / sr
peak = float(np.max(np.abs(mono)))

# silence ratio (|x| < 0.001)
silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))

# per-second RMS map
secs = int(dur)
rms_map = []
for s in range(secs):
    seg = mono[s * sr:(s + 1) * sr]
    rms_map.append(round(float(np.sqrt(np.mean(seg ** 2))), 4))
zero_rms_secs = sum(1 for v in rms_map if v < 0.005)

# FFT tonal check: dominant peak per 0.5s window in 50-1000 Hz + harmonic energy
def fft_checks(sig, sr, win=0.5):
    doms = []
    win_n = int(sr * win)
    for s in range(0, len(sig) - win_n, win_n):
        seg = sig[s:s + win_n]
        if np.sqrt(np.mean(seg ** 2)) < 0.005:
            continue
        sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        freqs = np.fft.rfftfreq(len(seg), 1.0 / sr)
        band = (freqs >= 50) & (freqs <= 1000)
        if not np.any(band):
            continue
        f = freqs[band]
        m = sp[band]
        doms.append(round(float(f[np.argmax(m)]), 1))
    return doms

doms = fft_checks(mono, sr)
harmonic_ratio = None
# harmonic energy in first 8 harmonics of the lowest detected fundamental
if doms:
    f0 = min(doms)
    sp = np.abs(np.fft.rfft(mono[: int(sr * 2)] * np.hanning(min(int(sr * 2), len(mono)))))
    freqs = np.fft.rfftfreq(min(int(sr * 2), len(mono)), 1.0 / sr)
    harm = sum(sp[np.argmin(np.abs(freqs - f0 * k))] for k in range(1, 9))
    tot = np.sum(sp)
    harmonic_ratio = round(float(harm / tot), 3) if tot > 0 else None

stats = {
    "wav_bytes": os.path.getsize(WAV),
    "ogg_bytes": os.path.getsize(OGG),
    "sample_rate": sr,
    "channels": nch,
    "duration_s": round(dur, 3),
    "peak": round(peak, 4),
    "silence_ratio": round(silent, 4),
    "per_second_rms": rms_map,
    "zero_rms_seconds": zero_rms_secs,
    "fft_dominant_hz_first_frames": doms[:12],
    "harmonic_energy_ratio": harmonic_ratio,
}
with open(os.path.join(ANALYSIS, "render_stats.json"), "w") as f:
    json.dump(stats, f, indent=2)

print("duration_s:", round(dur, 3))
print("peak:", round(peak, 4))
print("silence_ratio:", round(silent, 4))
print("zero_rms_seconds:", zero_rms_secs, "of", secs)
print("fft dominant (first frames):", doms[:12])
print("harmonic_energy_ratio:", harmonic_ratio)
print("WAV bytes:", os.path.getsize(WAV), " OGG bytes:", os.path.getsize(OGG))
assert os.path.getsize(WAV) > 40
assert os.path.getsize(OGG) > 40
print("RENDER OK")
