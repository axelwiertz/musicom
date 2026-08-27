#!/usr/bin/env python3
"""Final gate: provenance validity + key file sizes."""
import json, os

proj = "/opt/data/projects/Styles/Production/SP016-granular-cuban-trova"

prov = json.load(open(os.path.join(proj, "provenance.json")))
print("provenance keys:", sorted(prov.keys()))
print("method:", prov["production_method"], prov["production_method_name"])
print("source:", prov["source_midi"])

info = json.load(open(os.path.join(proj, "Analysis", "render_info.json")))
print("render_info keys:", sorted(info.keys()))
print("quality:", info["quality"])

for f, min_sz in [("Audio/SP016-granular-cuban-trova.wav", 1000),
                  ("Audio/SP016-granular-cuban-trova.ogg", 1000),
                  ("MIDI/original_cuban_trova_fixed.mid", 40)]:
    p = os.path.join(proj, f)
    sz = os.path.getsize(p)
    assert sz > min_sz, f"too small: {f}"
    print(f"{f}: {sz} bytes OK")

# OGG plays? ffprobe
import subprocess
r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                    "format=duration,format_name",
                    "-of", "default=noprint_wrappers=1",
                    os.path.join(proj, "Audio/SP016-granular-cuban-trova.ogg")],
                   capture_output=True, text=True, timeout=60)
print("ffprobe rc:", r.returncode)
print(r.stdout.strip())
assert r.returncode == 0
print("ALL GATES PASS")