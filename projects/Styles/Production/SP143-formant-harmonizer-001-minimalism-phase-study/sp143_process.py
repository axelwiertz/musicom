# -*- coding: utf-8 -*-
"""SP-143 Formant-Preserving Vocal Harmonizer applied to 001-minimalism-phase-study.

Absolute-layer method: run the harmonizer across the whole mixed render.
Full mix -> mono downmix -> PitchCorrector (C major) + HarmonyStacker
(thirds/fifth harmony), then master to -18 LUFS (minimal) + Opus OGG.
"""
import os
import numpy as np
from sound.effects.formant_harmonizer import PitchCorrector, HarmonyStacker, droid
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, "Audio")
MID = os.path.join(HERE, "MIDI")
os.makedirs(AUD, exist_ok=True)

mix_path = os.path.join(AUD, "full_mix.wav")
audio, sr = read_wav(mix_path)          # (N, 2) time-major float32
print("full_mix:", audio.shape, "sr", sr, "dur_s", audio.shape[0] / sr)

# mono downmix for the (monophonic-assuming) harmonizer
mono = audio.mean(axis=1)

KEY = "C"
SCALE = "major"        # piece is C pentatonic over C major drone

# 1. PitchCorrector: retune to C major (transparent style + hard snap)
pc = PitchCorrector(sr)
tuned = pc.process(mono, key=KEY, scale=SCALE, style=0.5)
write_wav(os.path.join(AUD, "sp143_tuned.wav"), tuned, sr, normalize=True)

# 2. HarmonyStacker: stack diatonic 3rd + 5th up, 4th below (3 parts)
hs = HarmonyStacker(sr)
res = hs.process(mono, key=KEY, scale=SCALE, intervals=(2, 4, -3), style=0.35)
harm_mix = res["mix"]                     # (2, N) stereo
write_wav(os.path.join(AUD, "sp143_harmonized_raw.wav"), harm_mix.T, sr, normalize=True)

# 3. a "Droid" formant character variant on the tuned lead
droid_out = droid(tuned, sr=sr, formant_semitones=-4.0)
droid_mix = np.stack([droid_out, tuned])  # formant-shifted vs clean (L/R)
write_wav(os.path.join(AUD, "sp143_droid.wav"), droid_mix.T, sr, normalize=True)

# 4. master the harmonized mix to genre target
target = target_for_style("minimal")
mastered, rep = master(harm_mix.T, target_lufs=target, ceiling_db=-1.0, sample_rate=sr)
write_wav(os.path.join(AUD, "sp143_harmonized.wav"), mastered, sr, normalize=False)
print("MASTER:", target, "integrated_lufs", round(rep["integrated_lufs"], 2),
      "true_peak_db", round(rep["true_peak_db"], 2))

print("DONE. outputs in", AUD)