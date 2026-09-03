# -*- coding: utf-8 -*-
"""Probe: provenance + grid visualizer + VoiceLeadingRules API."""
import sys
sys.path.insert(0, "/opt/data/repos/musicom/projects/Instruments")
from workflows.provenance import write_provenance, AI_GENERATED
import inspect
print("provenance sig:", inspect.signature(write_provenance))
from rules.voice_leading import VoiceLeadingRules
import inspect as i2
print("VLR methods:", [m for m in dir(VoiceLeadingRules) if not m.startswith("_")])
