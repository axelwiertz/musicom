#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regenerate provenance sidecars for the rev3 stems (rev1 leftovers were removed)."""
from pathlib import Path

from workflows.provenance import write_provenance, AI_ASSISTED

ROOT = Path("/opt/data/repos/musicom")
OUT = ROOT / "projects/Styles/Production/SP011-karplus-hiphop-boombap"
SRC = ROOT / "projects/Styles/HipHop/boom-bap/v1/hiphop_boom_bap.mid"
for role in ("lead", "comp", "bass", "perc"):
    p = next((OUT / "Audio/stems").glob(f"track*_{role}.wav"))
    write_provenance(str(p), AI_ASSISTED, "SP-011 Karplus-Strong stem (rev3)",
                     sources=[str(SRC)], parameters={"role": role, "method": "SP-011"})
    print("provenance ok:", p.name)
