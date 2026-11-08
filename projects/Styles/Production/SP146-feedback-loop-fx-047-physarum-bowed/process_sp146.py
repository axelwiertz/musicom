# -*- coding: utf-8 -*-
"""SP-146 Feedback-Loop Echo + Codec Loss applied to 047-physarum-bowed (reworked).

Absolute-layer method: render the whole mix via FluidSynth (dry, no reverb tail),
apply the RC-20-style feedback-loop echo as a single production layer, plus an
offline spectral-codec pass.  Master both to the genre target.

Memory-lean: explicit gc between stages, float32 passthrough, dry render.
"""
import os
import gc
import subprocess
import json
import numpy as np

from sound.effects.feedback_loop_fx import FeedbackLoopFX, spectral_codec
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav
from sound.render.fluidsynth import discover_soundfont
from utilities.env import fluidsynth_bin

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, "Audio")
MID = os.path.join(HERE, "MIDI")
ANA = os.path.join(HERE, "Analysis")
for d in (AUD, MID, ANA):
    os.makedirs(d, exist_ok=True)

SRC_MIDI = os.path.join(MID, "047-physarum-bowed.mid")   # reworked (chord-tone clean)
SF = discover_soundfont()
FLUID = fluidsynth_bin()
BPM = 110.0
STYLE = "experimental"
DELAY_MS = 60000.0 / BPM   # 545.45 ms quarter-note echo


def log(*a):
    print(*a, flush=True)


# ---- 1. render full mix (reference, dry: no reverb/chorus tail) ----------
mix_path = os.path.join(AUD, "full_mix.wav")
r = subprocess.run([FLUID, "-ni", "-g", "1.2", "-R", "no", "-C", "no",
                    "-F", mix_path, SF, SRC_MIDI],
                   capture_output=True, text=True)
assert r.returncode == 0, r.stderr[-500:]
audio, sr = read_wav(mix_path)          # (N, 2) float32
N = len(audio)
dur = N / sr
log("full_mix:", audio.shape, "sr", sr, "dur_s", round(dur, 2))

# ---- 2. SP-146 feedback-loop echo (in-loop character chain) -----------
fx = FeedbackLoopFX(sr, delay_ms=DELAY_MS, feedback=0.55, mix=0.40,
                    wobble_cents=8.0, wobble_rate=0.5, flutter_rate=6.3,
                    drive=0.25, tone_hz=7000.0, smear=0.20,
                    codec=True, codec_bitrate=96.0)
log("feedback-loop processing ...")
wet = fx.process(audio).astype(np.float32)   # (N, 2)
write_wav(os.path.join(AUD, "sp146_feedback_raw.wav"), wet, sr, normalize=True)
log("feedback-loop done", wet.shape)

# ---- 3. offline spectral codec variant ---------------------------------
log("spectral codec processing ...")
codec = spectral_codec(audio, sr, bitrate_kbps=96.0).astype(np.float32)
write_wav(os.path.join(AUD, "sp146_codec_raw.wav"), codec, sr, normalize=True)
log("codec done", codec.shape)
del audio
gc.collect()

# ---- 4. master both ----------------------------------------------------
target = target_for_style(STYLE)
rep = {}
for name, sig in (("sp146_feedback", wet), ("sp146_codec", codec)):
    log("mastering", name, "...")
    mastered, rp = master(sig.astype(np.float32), target_lufs=target,
                          ceiling_db=-1.0, sample_rate=sr)
    write_wav(os.path.join(AUD, name + ".wav"), mastered, sr, normalize=False)
    rep[name] = {"target_lufs": target,
                 "integrated_lufs": round(rp["integrated_lufs"], 2),
                 "true_peak_db": round(rp["true_peak_db"], 2)}
    log("MASTER", name, "target", target,
        "integrated_lufs", round(rp["integrated_lufs"], 2),
        "true_peak_db", round(rp["true_peak_db"], 2))
    del mastered
    gc.collect()

# ---- 5. silence profile -------------------------------------------------
def silence_profile(x):
    mono = x.mean(axis=1) if x.ndim == 2 else x
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    rms = [round(float(np.sqrt(np.mean(mono[s:s + sr] ** 2))), 4)
           for s in range(0, len(mono) - sr, sr)]
    gaps = sum(1 for v in rms if v < 0.005)
    return {"silence_ratio": round(silent, 4), "low_rms_seconds": gaps,
            "n_seconds": len(rms), "per_second_rms": rms}

prof = {}
for name in ("full_mix", "sp146_feedback", "sp146_codec"):
    a, _ = read_wav(os.path.join(AUD, name + ".wav"))
    prof[name] = silence_profile(a)
    log("SILENCE", name, prof[name]["silence_ratio"],
        "low_rms_sec", prof[name]["low_rms_seconds"], "/", prof[name]["n_seconds"])
    del a
    gc.collect()

# ---- 6. Opus OGG -------------------------------------------------------
for name in ("full_mix", "sp146_feedback", "sp146_codec"):
    wav = os.path.join(AUD, name + ".wav")
    ogg = os.path.join(AUD, name + ".ogg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                    "-codec:a", "libopus", "-b:a", "128k", ogg],
                   capture_output=True, text=True)
    log(name, "ogg", os.path.getsize(ogg), "B")

# ---- 7. sidecars -------------------------------------------------------
with open(os.path.join(AUD, "silence_profile.json"), "w") as f:
    json.dump(prof, f, indent=2)
prov = {
    "method": "SP-146", "module": "sound.effects.feedback_loop_fx",
    "style": STYLE, "bpm": BPM, "delay_ms": round(DELAY_MS, 2),
    "feedback": 0.55, "mix": 0.40, "wobble_cents": 8.0, "drive": 0.25,
    "tone_hz": 7000, "smear": 0.20, "codec": True, "codec_bitrate_kbps": 96,
    "spectral_codec_bitrate_kbps": 96,
    "soundfont": SF, "master": rep, "dur_s": round(dur, 2),
}
with open(os.path.join(AUD, "provenance.json"), "w") as f:
    json.dump(prov, f, indent=2)

log("DONE. outputs in", AUD)
