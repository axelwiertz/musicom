import os, subprocess, json
import numpy as np
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav

SF = "/opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2"
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
FFMPEG = "/opt/data/micromamba/envs/musicom/bin/ffmpeg"
MIDI_DIR = "/opt/data/projects/Styles/Blues/295-blues-aco-suite/MIDI"
AUDIO_DIR = "/opt/data/projects/Styles/Blues/295-blues-aco-suite/Audio"

def render(base):
    mid = os.path.join(MIDI_DIR, f"{base}.mid")
    wav = os.path.join(AUDIO_DIR, f"{base}.wav")
    ogg = os.path.join(AUDIO_DIR, f"{base}.ogg")
    subprocess.run([FLUID, "-ni", "-g", "1.2", "-R", "no", "-C", "no",
                    "-F", wav, SF, mid], check=True, capture_output=True)
    audio, sr = read_wav(wav)
    target = target_for_style("blues")
    mastered, rep = master(audio, target_lufs=target, ceiling_db=-1.0, sample_rate=sr)
    write_wav(wav, mastered, sr, normalize=False)
    mono = mastered.mean(axis=1) if mastered.ndim > 1 else mastered
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    subprocess.run([FFMPEG, "-y", "-i", wav, "-codec:a", "libopus",
                    "-application", "voip", "-b:a", "48k", ogg],
                   check=True, capture_output=True)
    return {"base": base, "lufs": rep["integrated_lufs"], "true_peak_db": rep["true_peak_db"],
            "silence_ratio": round(silent, 4), "sr": sr,
            "wav_size": os.path.getsize(wav), "ogg_size": os.path.getsize(ogg)}

results = []
for base in ["295-blues-aco-suite-perfect", "295-blues-aco-suite-humanized"]:
    r = render(base)
    results.append(r)
    print(json.dumps(r))
with open(os.path.join(AUDIO_DIR, "render_report.json"), "w") as f:
    json.dump(results, f, indent=2)
print("DONE")