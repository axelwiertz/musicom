#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Post-render audit: assert all artifacts exist, non-empty, sizes sane, JSON valid."""
import json
import os
import sys
from pathlib import Path

OUT = Path('/opt/data/projects/Styles/Production/SP032-fdn-groove-sieve')
ok = True


def check(path, min_bytes):
    global ok
    p = OUT / path
    if not p.exists():
        print('MISSING', path)
        ok = False
        return
    sz = p.stat().st_size
    if sz < min_bytes:
        print('TOO SMALL', path, sz)
        ok = False
        return
    print('ok %10d  %s' % (sz, path))


for f, mb in [
    ('Audio/SP032-fdn-groove-sieve.wav', 1000000),
    ('Audio/SP032-fdn-groove-sieve.ogg', 10000),
    ('dry_full_mix.wav', 1000000),
    ('MIDI/080-groove-sieve.mid', 100),
    ('provenance.json', 200),
    ('Analysis/render_stats.json', 100),
    ('Analysis/pitch_verification.json', 50),
    ('REPORT.md', 500),
]:
    check(f, mb)

for stem in ['track00_Soprano_Sax', 'track01_Brass_Section', 'track02_Electric_Piano_1',
             'track03_Electric_Bass_finger', 'track04_Drums_GM']:
    check('Audio/stems/%s.wav' % stem, 200000)

# JSON validity + key fields
try:
    prov = json.loads((OUT / 'provenance.json').read_text())
    assert prov['production_method'] == 'SP-032'
    assert prov['checks']['pitch_verification']['verdict'] == 'PASS'
    pv = json.loads((OUT / 'Analysis/pitch_verification.json').read_text())
    assert pv['verdict'] == 'PASS'
    rs = json.loads((OUT / 'Analysis/render_stats.json').read_text())
    assert rs['silence_ratio'] < 0.30
    assert rs['peak_dBFS'] == -1.0
    print('JSON checks PASS')
except Exception as e:
    print('JSON CHECK FAIL:', e)
    ok = False

print('AUDIT', 'PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)
