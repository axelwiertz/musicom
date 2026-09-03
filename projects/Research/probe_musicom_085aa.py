# -*- coding: utf-8 -*-
"""Probe: registry instrument lookups for voice design."""
import sys
sys.path.insert(0, "/opt/data/repos/musicom/projects/Instruments")
from instrument_registry import (VIOLIN, VIOLA, CELLO, DOUBLE_BASS, PIANO,
                                 ORGAN, TRUMPET, TROMBONE, FRENCH_HORN, TUBA,
                                 FLUTE, CLARINET, OBOE, BASSOON, SAXOPHONE,
                                 ACOUSTIC_GUITAR, DRUM_KIT, MARIMBA, SITAR)
# groove-ensemble voice options
for name, inst in [("Soprano Sax (lead)", SAXOPHONE), ("Horns", TRUMPET),
                   ("Bass", DOUBLE_BASS), ("Viola pad", VIOLA),
                   ("Flute", FLUTE), ("Oboe", OBOE), ("Marimba", MARIMBA)]:
    print(f"{name}: program {inst.midi_program}, range {inst.range_min}-{inst.range_max}, sweet {inst.sweet_spot}")
