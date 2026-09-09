#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SP-001 FluidSynth SoundFont production pass — 2026-09-09 cron.

Source composition : Styles/Celtic/090-celtic-subset-walk/MIDI/090-celtic-subset-walk.mid
                     (ABS-002 subset-walk Celtic texture, D minor, 108 BPM,
                      24 bars / ~53 s, 6 voices: violin lead, flute counter,
                      cello pad, piano harp rolls, double bass, drum kit)
Method (registry)   : SP-001 -> sound.render.fluidsynth (SP_METHODS registry
                      in workflows.musicom_workflow.py)
Layer discipline    : ABSOLUTE layer - FluidSynth GM SoundFont rendering is the
                      production/timbre layer for ALL voices (full mix + per-voice
                      stems). Internal reverb/chorus stay ON (GM default
                      production sound); stems are dry per-voice GM renders for
                      DAW remix.

Chain:
  MIDI -> RenderPipeline.render_to_wav (fluidsynth CLI, FluidR3_GM.sf2, 44.1k,
          gain 1.2, internal FX on) -> -1 dBFS master -> trim -> OGG (Opus 48k)
  + RenderPipeline.render_stems (per-voice WAV + OGG)
  + pitch verification (FFT dominant peak vs MIDI fundamentals), silence/RMS
  + provenance.json per artifact, REPORT.md
"""
import os
import json
import shutil
import hashlib
import subprocess
import wave
from pathlib import Path

import numpy as np
import mido

SRC = Path('/opt/data/projects/Styles/Celtic/090-celtic-subset-walk/MIDI/090-celtic-subset-walk.mid')
OUT = Path('/opt/data/projects/Styles/Production/SP001-celtic-subset-walk')
AUDIO = OUT / 'Audio'
STEMS = AUDIO / 'stems'
MIDIDIR = OUT / 'MIDI'
ANALYSIS = OUT / 'Analysis'
for d in (AUDIO, STEMS, MIDIDIR, ANALYSIS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
FFMPEG = '/usr/bin/ffmpeg'

from sound.render.fluidsynth import discover_soundfont
from sound.render import RenderPipeline

SF = discover_soundfont()
assert SF and os.path.exists(SF), 'no soundfont'
print('soundfont:', SF)

# ---------------------------------------------------------------- dry renders
print('rendering full mix ...')
pipe = RenderPipeline(soundfont_path=SF, sample_rate=SR, gain=1.2)
WAV_OUT = AUDIO / 'SP001-celtic-subset-walk.wav'
pipe.render_to_wav(str(SRC), str(WAV_OUT))
assert os.path.getsize(WAV_OUT) > 40000, 'WAV empty'
assert os.path.getsize(WAV_OUT) < 100 * 1024 * 1024, 'WAV too big'


def load_wav(path):
    with wave.open(str(path), 'rb') as wf:
        n = wf.getnframes()
        assert wf.getframerate() == SR
        ch = wf.getnchannels()
        raw = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
    if ch == 2:
        return raw.reshape(-1, 2)
    return np.column_stack([raw, raw])


full = load_wav(WAV_OUT)
print('full mix: %.2fs peak=%.3f' % (len(full) / SR, np.abs(full).max()))

# ------------------------------------------------------------- master / trim
mono = (full[:, 0] + full[:, 1]) * 0.5
content_end = len(mono) - 1
while content_end > 0 and abs(mono[content_end]) <= 0.001:
    content_end -= 1
content_end_s = content_end / SR
print('content ends at %.2fs' % content_end_s)

# tail: find last note-off time from MIDI, allow reverb tail beyond it
mid = mido.MidiFile(str(SRC))
tpb = mid.ticks_per_beat
tempo = None
for msg in mid.tracks[0]:
    if msg.type == 'set_tempo':
        tempo = msg.tempo
        break
sec_per_tick = tempo / 1e6 / tpb
last_off_t = 0.0
for tr in mid.tracks[1:]:
    t = 0
    for msg in tr:
        t += msg.time
        if msg.type in ('note_off',) or (msg.type == 'note_on' and msg.velocity == 0):
            last_off_t = max(last_off_t, t * sec_per_tick)
        elif msg.type == 'note_on':
            last_off_t = max(last_off_t, t * sec_per_tick)
last_off_t += 2.0  # 2s minimum padding for note tails
target_len = max(content_end_s + 3.5, min(last_off_t + 2.5, content_end_s + 6.0))
print('midi last note ~%.2fs  target len %.2fs' % (last_off_t, target_len))
full = full[:min(len(full), int(target_len * SR))]

peak = np.abs(full).max()
full = full * (10 ** (-1.0 / 20.0)) / peak

mono = (full[:, 0] + full[:, 1]) * 0.5
silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
rms_per_s = [float(np.sqrt(np.mean(mono[i:i + SR] ** 2))) for i in range(0, len(mono), SR)]
print('silence ratio: %.4f (%.1f%%)' % (silent, silent * 100))
assert silent < 0.30, 'too silent'

pcm = (np.clip(full, -1.0, 1.0) * 32767.0).astype(np.int16)
with wave.open(str(WAV_OUT), 'wb') as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes(pcm.tobytes())
assert os.path.getsize(WAV_OUT) > 40000
print('WAV written:', WAV_OUT, os.path.getsize(WAV_OUT), 'bytes, %.2fs' % (len(pcm) / SR))

# ---------------------------------------------------------------------- OGG
OGG_OUT = AUDIO / 'SP001-celtic-subset-walk.ogg'
subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-i', str(WAV_OUT),
                '-codec:a', 'libopus', '-application', 'voip', '-b:a', '48k',
                str(OGG_OUT)], check=True, timeout=180)
assert os.path.getsize(OGG_OUT) > 10000
print('OGG:', OGG_OUT, os.path.getsize(OGG_OUT), 'bytes')

# -------------------------------------------------------------------- stems
print('rendering stems ...')
stem_wavs = pipe.render_stems(str(SRC), str(STEMS), soundfont=SF, format='wav')
for name, path in sorted(stem_wavs.items()):
    assert os.path.getsize(path) > 40000, 'stem empty: ' + name
print('stems:', len(stem_wavs))
stem_oggs = {}
for name, wav_path in sorted(stem_wavs.items()):
    op = str(wav_path).replace('.wav', '.ogg')
    subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-i', wav_path,
                    '-codec:a', 'libopus', '-application', 'voip', '-b:a', '48k',
                    op], check=True, timeout=120)
    stem_oggs[name] = op
print('stem OGGs done')

# ------------------------------------------------------------------- copy MIDI
MIDI_OUT = MIDIDIR / '090-celtic-subset-walk.mid'
shutil.copy2(str(SRC), str(MIDI_OUT))

# ----------------------------------------------------- pitch verification
def midi_note_freq(n):
    return 440.0 * 2.0 ** ((n - 69) / 12.0)


ons = {}
for tr in mid.tracks[1:]:
    t = 0
    pending = {}
    for msg in tr:
        t += msg.time
        if msg.type == 'note_on':
            if msg.velocity > 0 and msg.channel != 9:
                pending[msg.note] = t
            elif msg.channel != 9 and msg.note in pending:
                ons.setdefault(msg.note, []).append((pending.pop(msg.note), t))
        elif msg.type == 'note_off' and msg.channel != 9 and msg.note in pending:
            ons.setdefault(msg.note, []).append((pending.pop(msg.note), t))
    for note, t0 in pending.items():
        ons.setdefault(note, []).append((t0, t))
intervals = {}
for note, lst in ons.items():
    intervals[note] = [(a * sec_per_tick, b * sec_per_tick) for a, b in lst]

win = int(0.5 * SR)
n_wins = len(mono) // win
freqs = np.fft.rfftfreq(win, 1.0 / SR)
spec_mask = (freqs >= 50) & (freqs <= 1000)
checked = 0
ok = 0
he_list = []
for w in range(n_wins):
    t0w = w * 0.5
    t1w = t0w + 0.5
    act = set()
    for note, lst in intervals.items():
        for (a, b) in lst:
            if a < t1w and b > t0w:
                act.add(note)
                break
    if not act:
        continue
    seg = mono[w * win:(w + 1) * win]
    if len(seg) < win or np.sqrt(np.mean(seg ** 2)) < 0.01:
        continue
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    m = spec_mask[:len(spec)]
    f_band = freqs[:len(spec)][m]
    s_band = spec[:len(spec)][m]
    dom = f_band[int(np.argmax(s_band))]
    funds = [midi_note_freq(n) for n in act]
    hit = False
    for f in funds:
        for cand in (f, f / 2, f * 2):
            if abs(dom - cand) / cand < 0.04:
                hit = True
                break
        if hit:
            break
    checked += 1
    ok += 1 if hit else 0
    f0 = min(funds)
    har = sum(s_band[np.abs(f_band - f0 * k) < max(15, f0 * 0.02)].sum() for k in range(1, 9))
    he_list.append(har / max(float(s_band.sum()), 1e-12))
hit_rate = ok / max(checked, 1)
he_mean = float(np.mean(he_list)) if he_list else 0.0
print('pitch windows checked: %d  dominant-peak hit rate: %.3f' % (checked, hit_rate))
print('harmonic energy (8 harmonics of lowest fund): mean=%.3f' % he_mean)
pitch_ver = {
    'windows_checked': checked,
    'dominant_peak_hit_rate': round(hit_rate, 4),
    'harmonic_energy_mean_8h': round(he_mean, 4),
    'method': 'FFT dominant peak per 0.5s window, 50-1000 Hz band, '
              '+/-4% tolerance vs active MIDI fundamentals (or octave below/above)',
    'verdict': ('PASS' if (hit_rate >= 0.6 and he_mean >= 0.25) else 'FAIL'),
}
print('pitch verdict:', pitch_ver['verdict'])

# ---------------------------------------------------------------- artifacts
def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


stats = {
    'duration_s': round(len(pcm) / SR, 2),
    'silence_ratio': round(silent, 4),
    'peak_dBFS': -1.0,
    'rms_per_second': [round(r, 4) for r in rms_per_s],
    'wav_bytes': os.path.getsize(WAV_OUT),
    'ogg_bytes': os.path.getsize(OGG_OUT),
    'stem_wav_bytes': {k: os.path.getsize(v) for k, v in sorted(stem_wavs.items())},
}
with open(ANALYSIS / 'render_stats.json', 'w') as f:
    json.dump(stats, f, indent=2)
with open(ANALYSIS / 'pitch_verification.json', 'w') as f:
    json.dump(pitch_ver, f, indent=2)

prov = {
    'job': 'random-style production pass (SP) - LAYER-ALIGNED 2026-09-09',
    'selection_source': 'workflows.musicom_workflow.SP_METHODS registry (12 implemented, 2026-09-02 layer-aligned spec)',
    'composition_source': str(SRC),
    'composition_sha256': sha256(str(SRC)),
    'production_method': 'SP-001',
    'production_method_name': 'Multi-timbral SoundFont (FluidSynth)',
    'registered_module': 'sound.render.fluidsynth',
    'layer_discipline': ('absolute layer: FluidSynth GM SoundFont rendering is the '
                         'production/timbre layer for ALL voices (full mix + per-voice stems)'),
    'parameters': {'soundfont': SF, 'sample_rate': SR, 'gain': 1.2,
                   'fluid_internal_reverb': True, 'fluid_internal_chorus': True,
                   'normalization_dBFS': -1.0},
    'checks': {
        'silence_ratio': round(silent, 4),
        'pitch_verification': pitch_ver,
    },
    'artifacts': {
        'midi': str(MIDI_OUT),
        'processed_wav': str(WAV_OUT),
        'processed_ogg': str(OGG_OUT),
        'stems_wav': {k: str(v) for k, v in sorted(stem_wavs.items())},
        'stems_ogg': {k: str(v) for k, v in sorted(stem_oggs.items())},
    },
}
with open(OUT / 'provenance.json', 'w') as f:
    json.dump(prov, f, indent=2)
print('provenance.json written')
print('DONE')
