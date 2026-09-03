# -*- coding: utf-8 -*-
"""Probe: drum kit module constants for the phase-2 drums voice."""
import sys
sys.path.insert(0, "/opt/data/repos/musicom/projects/Instruments")
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES
print("KIT:", KIT)
print("VEL:", VELOCITIES)
print("GM notes:", {k: v % 12 for k, v in KIT.items()})
