#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SP-071 completion: grid visualization + provenance + stats (post-render).

The main renderer (produce_sp071_cron.py) completed MIDI->audio->FX->stems->
pitch-verification->OGG, then died on a visualization kwarg typo. This script
finishes the remaining artifacts WITHOUT re-running the DSP chain.
"""
import hashlib
import json
import os
import shutil
import wave
from pathlib import Path

import numpy as np
import mido

OUT = Path('/opt/data/repos/musicom/projects/Styles/Production/SP071-severance-techno-brownian')
AUDIO = OUT / 'Audio'
STEMS_DRY = AUDIO / 'stems_dry'
STEMS_PROC = AUDIO / 'stems_processed'
MIDIDIR = OUT / 'MIDI'
ANALYSIS = OUT / 'Analysis'
for d in (AUDIO, STEMS_DRY, STEMS_PROC, MIDIDIR, ANALYSIS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 128.0
SRC = Path('/opt/data/repos/musicom/projects/Styles/Techno/083-techno-brownian/MIDI/'
           '083-techno-brownian.mid')
WAV = OUT / 'SP071-severance-techno-brownian.wav'
OGG = OUT / 'SP071-severance-techno-brownian.ogg'
DRY = OUT / 'dry_full_mix.wav'


def load_wav(path):
    with wave.open(str(path), 'rb') as wf:
        n, ch, rate = wf.getnframes(), wf.getnchannels(), wf.getframerate()
        raw = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
    assert rate == SR
    return raw.reshape(-1, ch) if ch == 2 else np.column_stack([raw, raw])


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(65536), b''):
            h.update(c)
    return h.hexdigest()


def silence_stats(mono):
    sil = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    rms = [float(np.sqrt(np.mean(mono[i:i + SR] ** 2))) for i in range(0, len(mono), SR)]
    return sil, rms


wet = load_wav(WAV)
dry = load_wav(DRY)
sil_wet, rms_wet = silence_stats(wet.mean(axis=1))
sil_dry, rms_dry = silence_stats(dry.mean(axis=1))
print('wet: %.2fs peak %.4f silence %.2f%%' % (len(wet) / SR, np.abs(wet).max(), sil_wet * 100))
print('dry: %.2fs peak %.4f silence %.2f%%' % (len(dry) / SR, np.abs(dry).max(), sil_dry * 100))

from sound.effects.mastering import measure_lufs
lufs = float(measure_lufs(wet, SR))
print('LUFS %.2f' % lufs)

# ---------------------------------------------------------------- grid vis
from structures import MusicUnit, MusicEvent, UnitMatrix
from visualization.grid import write_grid_visualization

mid = mido.MidiFile(str(SRC))
tpb = mid.ticks_per_beat
BARS_PER, N_SECTIONS = 4, 6
BAR = tpb * 4
SEC_LEN = BAR * BARS_PER

VOICES = []
for i, track in enumerate(mid.tracks):
    prog = ch = None
    n = 0
    for m in track:
        if m.type == 'program_change' and prog is None:
            prog, ch = m.program, m.channel
        if m.type == 'note_on' and m.velocity:
            n += 1
            if ch is None:
                ch = getattr(m, 'channel', 0)
    if n >= 2:
        VOICES.append((i, 'track%02d' % i, prog, ch))

matrix = UnitMatrix(shape=(len(VOICES), N_SECTIONS))
for r, (tr, name, prog, ch) in enumerate(VOICES):
    for s in range(N_SECTIONS):
        matrix.set_unit((r, s), MusicUnit(events=[]))
    t = 0
    open_notes = {}
    for m in mid.tracks[tr]:
        t += m.time
        if m.type == 'note_on' and m.velocity:
            open_notes[m.note] = t
        elif m.type == 'note_off' or (m.type == 'note_on' and not m.velocity):
            st_t = open_notes.pop(m.note, t)
            sec = min(N_SECTIONS - 1, st_t // SEC_LEN)
            off = sec * SEC_LEN
            u = matrix.get_unit((r, int(sec)))
            u.add_event(MusicEvent(m.note, 90, int(st_t - off), int(min(t, (sec + 1) * SEC_LEN) - off)))
    for s in range(N_SECTIONS):
        u = matrix.get_unit((r, s))
        last = int(max((e.end_tick for e in u.events), default=SEC_LEN - 10))
        u.add_event(MusicEvent(0, 0, min(last, SEC_LEN - 10), SEC_LEN))
        for e in u.events:
            if e.end_tick > SEC_LEN:
                e.end_tick = SEC_LEN

gpath = write_grid_visualization(
    matrix, str(ANALYSIS / 'grid_visualization.txt'),
    ticks_per_character=240,
    voice_names=[v[1] + (' (drums ch9)' if v[3] == 9 else ' GM%s' % v[2]) for v in VOICES],
    bpm=int(BPM), mode='F natural minor')
print('grid ->', gpath)

# --------------------------------------------------------------- provenance
shutil.copy2(SRC, MIDIDIR / SRC.name)

pv = json.loads((ANALYSIS / 'pitch_verification.json').read_text())
rs = json.loads((ANALYSIS / 'render_stats.json').read_text())

# refresh stats with the values measured from the FINAL files
rs.update({'silence_ratio_dry': round(sil_dry, 4),
           'silence_ratio_wet': round(sil_wet, 4),
           'rms_per_second_dry': [round(x, 4) for x in rms_dry],
           'rms_per_second_wet': [round(x, 4) for x in rms_wet],
           'lufs_wet': round(lufs, 2),
           'peak_wet': round(float(np.abs(wet).max()), 4),
           'duration_s': round(len(wet) / SR, 3)})
(ANALYSIS / 'render_stats.json').write_text(json.dumps(rs, indent=2))

stem_meta = {}
for name in sorted(p.stem for p in STEMS_DRY.glob('track*.wav')):
    d = STEMS_DRY / (name + '.wav')
    pr = STEMS_PROC / (name + '_serverance.wav')
    stem_meta[name] = {'dry_wav': str(d), 'dry_bytes': os.path.getsize(d),
                       'processed_wav': str(pr) if pr.exists() else None,
                       'processed_bytes': os.path.getsize(pr) if pr.exists() else None}

prov = {
    'job': 'random-style production SP layer-aligned 2026-09-12',
    'method': 'SP-071',
    'module': 'sound.effects.severance',
    'desc': 'Gated Reverb + Dual-Engine Delay + Glitch Chain + Parallel Band Compressor (ZERO9-style)',
    'registry': 'workflows.musicom_workflow.SP_METHODS',
    'source_midi': str(SRC),
    'out_dir': str(OUT),
    'layer_discipline': 'absolute - ZERO9 suite replaces the space/echo/glue layer for ALL voices (full mix bus + per-voice processed stems)',
    'params': {
        'bpm': BPM,
        'gate_len_s': 60.0 / BPM / 2.0,
        'gate_triggers': 372,
        'gated_reverb': {'tail_gain': 0.55, 'declash': 0.5, 'movement': 0.5, 'decay': 0.62},
        'dual_engine_delay': {'time_cont_s': 0.3515625, 'time_gran_s': 0.703125,
                              'feedback': 0.42, 'routing': 'serial', 'splice': 4,
                              'grain_len': 512,
                              'note': 'dotted-8th (3x16th) + dotted-quarter (6x16th) at 128 BPM'},
        'glitch_chain': {'steps': 16,
                         'patterns': [[1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                                      [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
                         'note': 'sparse by design: ~3 of 16 steps per bar active; decimate stage OFF'},
        'parallel_band_comp': {'down_threshold_db': -16.0, 'down_ratio': 3.0,
                               'up_threshold_db': -44.0, 'up_amount': 0.30,
                               'parallel_mix': 0.45},
        'declash_blend': 0.35,
        'master': {'target_lufs': -14.0, 'limiter_threshold_db': -1.0},
    },
    'soundfont': '/opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2',
    'dry_full_mix': {'path': str(DRY), 'bytes': os.path.getsize(DRY),
                     'silence_ratio': round(sil_dry, 4)},
    'wet_full_mix': {'path': str(WAV), 'bytes': os.path.getsize(WAV),
                     'ogg': str(OGG), 'ogg_bytes': os.path.getsize(OGG),
                     'lufs': round(lufs, 2), 'peak': round(float(np.abs(wet).max()), 4),
                     'silence_ratio': round(sil_wet, 4), 'sha256': sha256(WAV)},
    'stems': stem_meta,
    'pitch_verification': pv,
    'fixes_applied': [
        'render_grid() kwarg is ticks_per_character (not ticks_per_char) - fixed',
        'sparse tempo-locked glitch patterns chosen so the 4-stage chain does not shred the mix',
        'per-channel (L/R independent) chain application to preserve stereo image',
    ],
}
(OUT / 'provenance.json').write_text(json.dumps(prov, indent=2))
print('provenance ->', OUT / 'provenance.json')
print('DONE')
