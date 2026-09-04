# -*- coding: utf-8 -*-
"""Final artifact sanity: sizes + OGG duration via ffprobe."""
import os
import subprocess
import wave

base = "/opt/data/projects/Styles/Production/SP011-karplus-jazz-swing/Audio"
ogg = f"{base}/SP011-jazz-swing-karplus-strong.ogg"
wav = f"{base}/SP011-jazz-swing-karplus-strong.wav"
mid = "/opt/data/projects/Styles/Production/SP011-karplus-jazz-swing/MIDI/exercise1b_jazz_ii_v_i_swing.mid"

print("wav bytes:", os.path.getsize(wav))
print("ogg bytes:", os.path.getsize(ogg))
print("mid bytes:", os.path.getsize(mid))

with wave.open(wav, "rb") as f:
    print("wav dur:", round(f.getnframes() / f.getframerate(), 2), "s")

r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1", ogg],
                   capture_output=True, text=True)
print("ogg dur:", r.stdout.strip(), "s")
assert os.path.getsize(ogg) > 1000
assert os.path.getsize(wav) > 1000
assert os.path.getsize(mid) > 40
print("ARTIFACT CHECK OK")
