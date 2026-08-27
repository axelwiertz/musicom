# -*- coding: utf-8 -*-
"""Final verification for the SP-011 production pass."""
import json
import os
from pathlib import Path

root = Path("/opt/data/projects/Styles/Production/SP011-karplus-cellular-chorale")

# 1. JSON validity
for j in ["provenance.json", "Analysis/render_info.json", "Analysis/chorale_dna.json"]:
    d = json.loads((root / j).read_text())
    print(f"{j}: OK")

# 2. Required outputs exist and non-trivial
required = [
    "MIDI/057-cellular-chorale.mid",
    "Audio/SP011-cellular-chorale-karplus-strong.wav",
    "Audio/SP011-cellular-chorale-karplus-strong.ogg",
    "README.md",
    "provenance.json",
    "Analysis/chorale_dna_grid.txt",
    "Analysis/render_info.json",
]
for r in required:
    p = root / r
    ok = p.exists() and p.stat().st_size > 40
    print(f"{'OK ' if ok else 'MISSING/EMPTY'} {r} ({p.stat().st_size if p.exists() else 0} bytes)")
    assert ok, r

# 3. No huge intermediate WAVs (FluidSynth bloat guard — not applicable here, but assert)
for p in root.rglob("*.wav"):
    assert p.stat().st_size < 100_000_000, f"WAV too large: {p}"

# 4. provenance sanity
prov = json.loads((root / "provenance.json").read_text())
assert prov["production_method"] == "SP-011"
assert prov["source_midi_sha256"] == "f7539d488ec2b047afc4b41b3ade5aa28a233fdedf4517d1c39f2b3a43bfb3fa"
print("provenance fields OK")

print("ALL CHECKS PASSED")
