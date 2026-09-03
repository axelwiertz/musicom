# -*- coding: utf-8 -*-
"""Probe: musicom flat imports + preflight paths used by 080 render."""
import subprocess
from sound.render.fluidsynth import discover_soundfont
print("sf:", discover_soundfont())
r = subprocess.run(["/opt/data/micromamba/envs/musicom/bin/fluidsynth", "--version"],
                   capture_output=True, text=True)
print("fluidsynth:", r.stdout.splitlines()[0] if r.stdout else r.stderr[:200])
r2 = subprocess.run(["/usr/bin/ffmpeg", "-version"], capture_output=True, text=True)
print("ffmpeg:", r2.stdout.splitlines()[0] if r2.stdout else "MISSING")
