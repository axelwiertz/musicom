#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SP-034 BBD (bucket-brigade-device) chorus production pass — 2026-09-03 cron.

Source composition : Styles/Country/039-marilou-vacation/MIDI/039-marilou-vacation-v3.mid
                     (Dutch country-pop vocal loop, 96 BPM, ~10 s, 6 voices)
Method (registry)   : SP-034 -> sound.effects.bbd_chorus (SP_METHODS registry in
                      workflows.musicom_workflow.py)
Layer discipline    : ABSOLUTE layer - BBD chorus replaces the modulation/spatial
                      layer for the WHOLE piece (applied on the full mix;
                      per-voice dry stems also shipped for DAW remix).

Chain:
  MIDI -> fluidsynth dry render (internal reverb/chorus OFF so BBD is the sole
          modulation layer) -> BBDChorus.process_stereo (registered module)
          -> -1 dBFS master -> OGG
  + per-voice dry stems (RenderPipeline-style extraction, same FX-off flags)
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

SRC = Path('/opt/data/projects/Styles/Country/039-marilou-vacation/MIDI/039-marilou-vacation-v3.mid')
OUT = Path('/opt/data/projects/Styles/Production/SP034-bbd-chorus-marilou-vacation')
AUDIO = OUT / 'Audio'
STEMS = AUDIO / 'stems'
MIDIDIR = OUT / 'MIDI'
ANALYSIS = OUT / 'Analysis'
for d in (AUDIO, STEMS, MIDIDIR, ANALYSIS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
FLUID = '/opt/data/micromamba/envs/musicom/bin/fluidsynth'
FFMPEG = '/usr/bin/ffmpeg'
from sound.render.fluidsynth import discover_soundfont
SF = discover_soundfont()
assert SF and os.path.exists(SF), 'no soundfont'
print('soundfont:', SF)

VOICES = [  # (track index in MIDI, voice name, gm program, channel)
    (1, 'Flute lead', 73, 0),      # lead vocal line (flute program)
    (2, 'Nylon Guitar', 25, 1),    # acoustic strum
    (3, 'Bass', 33, 2),            # Electric Bass (finger)
    (4, 'Drums', 0, 9),            # GM percussion
    (5, 'Fiddle', 110, 4),         # fiddle lead / hook
    (6, 'Pad', 91, 5),             # pad 1 (new age)
]
STEM_NAMES = ['track00_Flute', 'track01_Acoustic_Guitar_nylon',
              'track02_Electric_Bass_finger', 'track03_Drums_GM',
              'track04_Fiddle', 'track05_Pad_1_new_age']

FLUID_BASE = [FLUID, '-ni', '-g', '1.2',
              '-o', 'synth.reverb.active=no',
              '-o', 'synth.chorus.active=no',
              '-F']


def fluid_render(midi_path: str, wav_path: str):
    cmd = FLUID_BASE + [wav_path, '-r', str(SR), SF, midi_path]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0 or not os.path.exists(wav_path):
        raise RuntimeError('fluidsynth failed: ' + (r.stderr or r.stdout)[-500:])
    assert os.path.getsize(wav_path) < 100 * 1024 * 1024, 'WAV too big'
    assert os.path.getsize(wav_path) > 40000, 'WAV empty'


def load_wav(path):
    with wave.open(str(path), 'rb') as wf:
        n = wf.getnframes()
        assert wf.getframerate() == SR
        ch = wf.getnchannels()
        raw = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
    if ch == 2:
        return raw.reshape(-1, 2)
    return np.column_stack([raw, raw])


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- dry renders
dry_full = OUT / 'dry_full_mix.wav'
print('rendering dry full mix (internal FX off) ...')
fluid_render(str(SRC), str(dry_full))
dry = load_wav(dry_full)
print('dry_full_mix: %.2fs peak=%.3f' % (len(dry) / SR, np.abs(dry).max()))

# per-voice stems
mid = mido.MidiFile(str(SRC))
tempo_msg = None
for msg in mid.tracks[0]:
    if msg.type == 'set_tempo':
        tempo_msg = msg
        break
assert tempo_msg is not None
tpb = mid.ticks_per_beat
sec_per_tick = tempo_msg.tempo / 1e6 / tpb

stem_paths = {}
for (tr_idx, voice, prog, ch), sname in zip(VOICES, STEM_NAMES):
    st = mido.MidiFile(ticks_per_beat=tpb)
    tt = mido.MidiTrack()
    tt.append(tempo_msg)
    st.tracks.append(tt)
    vt = mido.MidiTrack()
    for msg in mid.tracks[tr_idx]:
        vt.append(msg)
    st.tracks.append(vt)
    tmp = OUT / ('_stem_%s.mid' % sname)
    st.save(str(tmp))
    wav = STEMS / (sname + '.wav')
    print('rendering stem', sname, '...')
    fluid_render(str(tmp), str(wav))
    tmp.unlink()
    stem_paths[sname] = str(wav)
print('stems done:', len(stem_paths))

# ------------------------------------------------- BBD chorus processing
from sound.effects.bbd_chorus import BBDChorus

BBD_PARAMS = dict(voices=6.0, rate_hz=0.5, depth_ms=4.0, lfo_spread=0.40,
                  clock_mult=4, compander=0.5, hiss=0.015,
                  mix=0.45, width=0.80, seed=20260903)

bbd = BBDChorus(sample_rate=SR, voices=BBD_PARAMS['voices'],
                rate_hz=BBD_PARAMS['rate_hz'], depth_ms=BBD_PARAMS['depth_ms'],
                lfo_spread=BBD_PARAMS['lfo_spread'],
                clock_mult=BBD_PARAMS['clock_mult'],
                compander=BBD_PARAMS['compander'],
                hiss=BBD_PARAMS['hiss'], seed=BBD_PARAMS['seed'])
print('BBD chorus processing (process_stereo, %.1fs input) ...' % (len(dry) / SR))
wet_out = bbd.process_stereo(dry, mix=BBD_PARAMS['mix'], width=BBD_PARAMS['width'])
print('BBD done, shape', wet_out.shape)

# --- BBD effectiveness checks (chorus must CHANGE the signal, decorrelate L/R)
mono_dry = (dry[:, 0] + dry[:, 1]) * 0.5
mono_wet = (wet_out[:, 0] + wet_out[:, 1]) * 0.5
diff_rms = float(np.sqrt(np.mean((mono_wet - mono_dry) ** 2)))
corr_lr_dry = float(np.corrcoef(dry[:, 0], dry[:, 1])[0, 1])
corr_lr_wet = float(np.corrcoef(wet_out[:, 0], wet_out[:, 1])[0, 1])
print('wet-vs-dry diff RMS: %.5f  L/R corr dry=%.4f wet=%.4f'
      % (diff_rms, corr_lr_dry, corr_lr_wet))
assert diff_rms > 0.002, 'BBD changed nothing - chorus ineffective'
assert corr_lr_wet < corr_lr_dry + 1e-9, 'stereo decorrelation did not increase'

# dry content end (tail trim reference)
dry_end = len(mono_dry) - 1
while dry_end > 0 and abs(mono_dry[dry_end]) <= 0.001:
    dry_end -= 1
dry_end_s = dry_end / SR
print('dry content ends at %.2fs' % dry_end_s)

# master: peak normalize to -1 dBFS, trim to dry_end + 3.5 s tail
wet_out = wet_out[:min(len(wet_out), int((dry_end_s + 3.5) * SR))]
peak = np.abs(wet_out).max()
wet_out = wet_out * (10 ** (-1.0 / 20.0)) / peak

mono = (wet_out[:, 0] + wet_out[:, 1]) * 0.5
silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
rms_per_s = [float(np.sqrt(np.mean(mono[i:i + SR] ** 2))) for i in range(0, len(mono), SR)]
print('silence ratio: %.4f (%.1f%%)' % (silent, silent * 100))
assert silent < 0.30, 'too silent'

# ----------------------------------------------------------------- write WAV
WAV_OUT = AUDIO / 'SP034-bbd-chorus-marilou-vacation.wav'
pcm = (np.clip(wet_out, -1.0, 1.0) * 32767.0).astype(np.int16)
with wave.open(str(WAV_OUT), 'wb') as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes(pcm.tobytes())
assert os.path.getsize(WAV_OUT) > 40000
print('WAV:', WAV_OUT, os.path.getsize(WAV_OUT), 'bytes, %.2fs' % (len(pcm) / SR))

# --------------------------------------------------------------------- OGG
OGG_OUT = AUDIO / 'SP034-bbd-chorus-marilou-vacation.ogg'
subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-i', str(WAV_OUT),
                '-codec:a', 'libopus', '-application', 'voip', '-b:a', '48k',
                str(OGG_OUT)], check=True, timeout=180)
assert os.path.getsize(OGG_OUT) > 10000
print('OGG:', OGG_OUT, os.path.getsize(OGG_OUT), 'bytes')

MIDI_OUT = MIDIDIR / '039-marilou-vacation-v3.mid'
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
stats = {
    'duration_s': round(len(pcm) / SR, 2),
    'silence_ratio': round(silent, 4),
    'peak_dBFS': -1.0,
    'rms_per_second': [round(r, 4) for r in rms_per_s],
    'bbd_diff_rms_vs_dry': round(diff_rms, 5),
    'lr_corr_dry': round(corr_lr_dry, 4),
    'lr_corr_wet': round(corr_lr_wet, 4),
    'wav_bytes': os.path.getsize(WAV_OUT),
    'ogg_bytes': os.path.getsize(OGG_OUT),
}
with open(ANALYSIS / 'render_stats.json', 'w') as f:
    json.dump(stats, f, indent=2)
with open(ANALYSIS / 'pitch_verification.json', 'w') as f:
    json.dump(pitch_ver, f, indent=2)

prov = {
    'job': 'random-style production pass (SP) - LAYER-ALIGNED 2026-09-03',
    'selection_source': 'workflows.musicom_workflow.SP_METHODS registry (10 implemented)',
    'composition_source': str(SRC),
    'composition_sha256': sha256(str(SRC)),
    'production_method': 'SP-034',
    'production_method_name': 'BBD Chorus Ensemble (Clock/Compander/Per-Voice Variation)',
    'registered_module': 'sound.effects.bbd_chorus',
    'layer_discipline': ('absolute layer: BBD chorus replaces the modulation layer for '
                         'ALL voices (applied to full mix; per-voice dry stems for DAW remix)'),
    'parameters': {**BBD_PARAMS, 'sample_rate': SR,
                   'normalization_dBFS': -1.0,
                   'fluid_internal_reverb': False, 'fluid_internal_chorus': False,
                   'fluid_gain': 1.2},
    'checks': {
        'wet_vs_dry_diff_rms': round(diff_rms, 5),
        'lr_corr_dry': round(corr_lr_dry, 4),
        'lr_corr_wet': round(corr_lr_wet, 4),
        'silence_ratio': round(silent, 4),
        'pitch_verification': pitch_ver,
    },
    'artifacts': {
        'midi': str(MIDI_OUT),
        'dry_full_mix_wav': str(dry_full),
        'processed_wav': str(WAV_OUT),
        'processed_ogg': str(OGG_OUT),
        'stems': stem_paths,
    },
}
with open(OUT / 'provenance.json', 'w') as f:
    json.dump(prov, f, indent=2)
print('provenance.json written')
print('DONE')
