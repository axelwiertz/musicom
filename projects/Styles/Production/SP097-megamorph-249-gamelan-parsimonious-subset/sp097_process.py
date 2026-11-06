# -*- coding: utf-8 -*-
"""SP-097 MegaMorph multi-lane parameter modulation applied to 249 gamelan.

Absolute-layer method: render the full mix, drive THREE MegaMorph lanes
(gate/cutoff/pan) across the WHOLE piece, then master to the gamelan target.

Lanes (tempo-synced 108 BPM):
  gate   — quarter-note sidechain pump (LOOP, smoothstep rise / exp fall)
  cutoff — 4-beat lowpass bounce sweep (BOUNCE, 250..9000 Hz log map)
  pan    — 2-beat constant-power stereo LFO (LOOP)
"""
import os
import subprocess
import json
import numpy as np

from sound.effects.mega_morph import (
    MultiSegmentEnv, EnvSegment, SegmentShape, EnvMode, MegaMorph,
)
from sound.effects.filter import StateVariableFilter
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav
from sound.render.fluidsynth import discover_soundfont
from utilities.env import fluidsynth_bin

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, "Audio")
MID = os.path.join(HERE, "MIDI")
os.makedirs(AUD, exist_ok=True)
os.makedirs(MID, exist_ok=True)

SRC_MIDI = ("/opt/data/repos/musicom/projects/Styles/Gamelan/"
            "249-gamelan-parsimonious-subset/MIDI/"
            "249-gamelan-parsimonious-subset-humanized.mid")
SF = discover_soundfont()
FLUID = fluidsynth_bin()
BPM = 108.0
STYLE = "gamelan"

# ---- 1. render full mix ------------------------------------------------
mix_path = os.path.join(AUD, "full_mix.wav")
if not os.path.exists(mix_path):
    r = subprocess.run([FLUID, "-ni", "-g", "1.2", "-F", mix_path, SF, SRC_MIDI],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-500:]
audio, sr = read_wav(mix_path)          # (N, 2) time-major float32
N = len(audio)
dur = N / sr
print("full_mix:", audio.shape, "sr", sr, "dur_s", round(dur, 2))

# ---- 2. MegaMorph lanes (control rate) ---------------------------------
gate = MultiSegmentEnv([
    EnvSegment(1.0, 0.5, 0.0, shape=SegmentShape.SMOOTHSTEP),
    EnvSegment(0.32, 0.5, 0.0, shape=SegmentShape.EXPONENTIAL, curvature=3.0),
], mode=EnvMode.LOOP, initial_value=0.6, bpm=BPM)

cutoff = MultiSegmentEnv([
    EnvSegment(0.12, 2.0, 0.0, shape=SegmentShape.SMOOTHSTEP),
    EnvSegment(0.95, 2.0, 0.0, shape=SegmentShape.SMOOTHSTEP),
], mode=EnvMode.BOUNCE, initial_value=0.5, bpm=BPM)

pan = MultiSegmentEnv([
    EnvSegment(1.0, 1.0, 0.0, shape=SegmentShape.SMOOTHSTEP),
    EnvSegment(0.0, 1.0, 0.0, shape=SegmentShape.SMOOTHSTEP),
], mode=EnvMode.LOOP, initial_value=0.5, bpm=BPM)

mm = MegaMorph(bpm=BPM)
mm.add_lane("gate", gate)
mm.add_lane("cutoff", cutoff)
mm.add_lane("pan", pan)

step = 0.005
ctrl = mm.render(dur, step_sec=step)
t_ctrl = np.arange(len(ctrl["gate"])) * step
t_audio = np.arange(N) / sr


def up(x):
    return np.interp(t_audio, t_ctrl, x)


gate_curve = up(ctrl["gate"])
cutoff_curve = up(ctrl["cutoff"])
pan_curve = up(ctrl["pan"])
print("lanes:", {k: (round(float(v.min()), 3), round(float(v.max()), 3))
                 for k, v in ctrl.items()})

# ---- 3. apply modulation (whole mix) -----------------------------------
gated = audio * gate_curve[:, None]

cutoff_hz = 250.0 * (9000.0 / 250.0) ** cutoff_curve   # log map 250..9000 Hz
out = np.zeros_like(gated)
block = 512
for ch in range(2):
    f = StateVariableFilter(sr)
    for i in range(0, N, block):
        seg = gated[i:i + block, ch]
        fc = float(np.mean(cutoff_hz[i:i + block]))
        out[i:i + block, ch] = f.process(seg, cutoff=fc, resonance=0.5, mode="lp")

pos = pan_curve * 2.0 - 1.0          # -1..1
ang = (pos + 1.0) * np.pi / 4.0      # 0..pi/2
pl = np.cos(ang)
pr = np.sin(ang)
panned = np.stack([out[:, 0] * pl, out[:, 1] * pr], axis=1)

write_wav(os.path.join(AUD, "sp097_morph_raw.wav"), panned, sr, normalize=True)

# ---- 4. master ---------------------------------------------------------
target = target_for_style(STYLE)
mastered, rep = master(panned, target_lufs=target, ceiling_db=-1.0, sample_rate=sr)
write_wav(os.path.join(AUD, "sp097_morph.wav"), mastered, sr, normalize=False)
print("MASTER:", STYLE, "target", target,
      "integrated_lufs", round(rep["integrated_lufs"], 2),
      "true_peak_db", round(rep["true_peak_db"], 2))

# ---- 5. silence profile ------------------------------------------------
def silence_profile(x):
    mono = x.mean(axis=1) if x.ndim == 2 else x
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    rms = [round(float(np.sqrt(np.mean(mono[s:s + sr] ** 2))), 4)
           for s in range(0, len(mono) - sr, sr)]
    gaps = sum(1 for r in rms if r < 0.005)
    return {"silence_ratio": round(silent, 4), "low_rms_seconds": gaps,
            "n_seconds": len(rms), "per_second_rms": rms}


prof = silence_profile(mastered)
print("SILENCE:", prof["silence_ratio"], "low_rms_sec",
      prof["low_rms_seconds"], "/", prof["n_seconds"])

# ---- 6. Opus OGG -------------------------------------------------------
for name in ("full_mix", "sp097_morph"):
    wav = os.path.join(AUD, name + ".wav")
    ogg = os.path.join(AUD, name + ".ogg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                    "-codec:a", "libopus", "-b:a", "128k", ogg],
                   capture_output=True, text=True)
    print(name, "ogg", os.path.getsize(ogg), "B")

with open(os.path.join(AUD, "silence_profile.json"), "w") as f:
    json.dump(prof, f, indent=2)

print("DONE. outputs in", AUD)
