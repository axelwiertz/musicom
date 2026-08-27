#!/usr/bin/env python3
from workflows.provenance import write_provenance, AI_ASSISTED
import os

ogg_path = 'Audio/056-perlin-lpc.ogg'
write_provenance(
    ogg_path,
    classification=AI_ASSISTED,
    generator='056-perlin-lpc/src/apply_lpc.py',
    parameters={
        'method': 'SP-028-LPC-Synthesis',
        'lpc_order': 12,
        'frame_size': 1024,
        'hop_size': 512,
        'normalization': '-1dB',
        'codec': 'opus',
        'bitrate': '48k',
    },
    notes='LPC analysis/synthesis post-processing on FluidSynth render. Formant-like spectral coloration.'
)
print(f'Provenance written: {os.path.getsize(ogg_path + ".provenance.json")} bytes')
