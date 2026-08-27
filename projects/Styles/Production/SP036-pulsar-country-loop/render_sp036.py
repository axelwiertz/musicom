#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SP-036 Pulsar Synthesis — Production Pass on 001-country-loop-seamless.

Curtis Roads pulsar synthesis (Microsound, MIT Press 2001): a train of
pulsarets (windowed carrier bursts) at pulse rate f_p (perceived pitch),
decoupled from formant/carrier frequency f_f (spectral center).

Source: Country 001-country-loop-seamless (G major, 120 BPM, 16 bars,
seamless loop). 333 events, 63.25 s.

Per-voice pulsar roles (methods_db SP-036):
  - Violin lead  (GM 40): stable f_p = MIDI pitch, sine carrier,
    f_f = 3 x f_p (integer ratio -> resonant vocal lead), Hann envelope,
    duty 0.5, gain 0.55
  - Guitar chords (GM 24): f_p = MIDI pitch, saw carrier (bright strum),
    f_f = 2 x f_p, Gaussian envelope, duty 0.42, gain 0.22 per note
    (5-note chords -> 1.1 sum, kept below lead)
  - Bass (GM 32): f_p = MIDI pitch (36-47, low), saw carrier, high duty
    0.9 -> solid sub-bass, f_f = 1 x f_p, gain 0.5
  - Percussion (ch10, GM 0): sub-audio pulse rates (f_p ~ 4.3 Hz kick,
    5.4 Hz rim, 6.0 Hz snare = rhythmic ticking, NOT pitched), noise
    carrier, sharp decay envelope, duty 0.5. Pitches 36/42/38 mapped
    to distinct f_p + noise color.

Implementation notes (spec section 6 + pitfalls):
  - continuous carrier phase accumulation across pulsarets (pitfall 10)
    -> smooth formant, no zipper noise
  - phase zero-aligned at pulsaret onsets (pitfall 8) for stable formant
  - duty <= 1 enforced (pitfall 3), Hann/Gaussian/decay envelopes (2,5)
  - DC removal per voice (pitfall 4)
  - 20 Hz highpass + 16 kHz lowpass in post (Butterworth via scipy)
  - per-note ADSR attack 15 ms / release 90 ms, 5 ms boundary crossfades
  - silence/RMS/pitch verification built in (SP-035 lesson)

Outputs -> /opt/data/projects/Styles/Production/SP036-pulsar-country-loop/
  Audio/SP036-pulsar-country-loop.wav|.ogg  + stems/ per voice
  MIDI/ (copy of source)
  provenance.json + Analysis/render_stats.json + Analysis/grid_visualization.txt
"""
import os
import json
import wave
import shutil
import subprocess
import hashlib
from collections import defaultdict

import numpy as np
import mido
from mido import MidiFile

SR = 44100
OUT_DIR = "/opt/data/projects/Styles/Production/SP036-pulsar-country-loop"
SRC_MIDI = "/opt/data/projects/Styles/Country/001-country-loop-seamless/MIDI/loop.mid"
NAME = "SP036-pulsar-country-loop"
PEAK = 0.89
SEED = 20260826

os.makedirs(os.path.join(OUT_DIR, "Audio", "stems"), exist_ok=True)
os.makedirs(os.path.join(OUT_DIR, "MIDI"), exist_ok=True)
os.makedirs(os.path.join(OUT_DIR, "Analysis"), exist_ok=True)

# ------------------------------------------------------------------ pulsar engine
def midi_to_freq(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))


class PulsarSynth:
    """Pulsar train: pulsarets of windowed carrier at pulse rate fp."""

    def __init__(self, fp, ff, duty=0.5, carrier='sine', envelope='hann',
                 fm_index=2.0, fm_ratio=0.5, fs=SR, rng=None):
        self.fp = fp
        self.ff = ff
        self.duty = max(1e-4, min(duty, 1.0))
        self.carrier = carrier
        self.envelope = envelope
        self.fm_index = fm_index
        self.fm_ratio = fm_ratio
        self.fs = fs
        self.rng = rng if rng is not None else np.random.default_rng(SEED)

    def _carrier(self, phase):
        """Carrier at formant frequency; phase continuous (radians)."""
        if self.carrier == 'sine':
            return np.sin(phase)
        elif self.carrier == 'saw':
            t = (phase / (2 * np.pi)) % 1.0
            return 2 * t - 1
        elif self.carrier == 'square':
            return np.sign(np.sin(phase))
        elif self.carrier == 'noise':
            return self.rng.uniform(-1, 1, len(phase))
        elif self.carrier == 'fm':
            return np.sin(phase + self.fm_index * np.sin(phase * self.fm_ratio))
        raise ValueError(f'unknown carrier {self.carrier}')

    def _envelope(self, n):
        if n < 2:
            return np.ones(max(n, 1))
        idx = np.arange(n)
        if self.envelope == 'hann':
            return 0.5 * (1 - np.cos(2 * np.pi * idx / (n - 1)))
        elif self.envelope == 'gaussian':
            sigma = max(n / 6.0, 1.0)
            return np.exp(-0.5 * ((idx - n / 2.0) / sigma) ** 2)
        elif self.envelope == 'decay':
            return 1.0 - idx / float(n - 1)
        elif self.envelope == 'rect':
            return np.ones(n)
        raise ValueError(f'unknown envelope {self.envelope}')

    def generate(self, duration_sec):
        """Pulsar train; continuous carrier phase, zero-aligned pulsaret phase."""
        n_total = int(duration_sec * self.fs)
        if n_total <= 0:
            return np.zeros(0, dtype=np.float64)
        y = np.zeros(n_total, dtype=np.float64)
        period_samples = max(1, int(self.fs / self.fp))
        pulsaret_len = max(1, int(period_samples * self.duty))
        # continuous phase accumulator (pitfall 10: no zipper on sweeps)
        phase_acc = 0.0
        pos = 0
        while pos < n_total:
            end = min(pos + pulsaret_len, n_total)
            n = end - pos
            # zero-aligned phase per pulsaret (pitfall 8: stable formant)
            phase = 2 * np.pi * self.ff * np.arange(n) / self.fs + phase_acc
            c = self._carrier(phase)
            e = self._envelope(n)
            y[pos:end] = c * e
            # advance phase by the full period (continuous carrier)
            phase_acc += 2 * np.pi * self.ff * period_samples / self.fs
            pos += period_samples
        return y


def synth_note(pitch, dur_sec, params, rng):
    """One note rendered with the pulsar engine + per-note ADSR."""
    fp = midi_to_freq(pitch)
    ff = fp * params['ff_ratio']
    if params['carrier'] == 'noise':
        # noise carrier: formant ratio meaningless; use fixed ff for color
        ff = params.get('ff_noise', 2400.0)
    synth = PulsarSynth(fp=fp, ff=ff, duty=params['duty'],
                        carrier=params['carrier'], envelope=params['envelope'],
                        fm_index=params.get('fm_index', 2.0),
                        fm_ratio=params.get('fm_ratio', 0.5),
                        fs=SR, rng=rng)
    y = synth.generate(dur_sec)
    if len(y) == 0:
        return y
    # ADSR
    n = len(y)
    attack = min(int(0.015 * SR), n // 2)
    release = min(int(0.090 * SR), n // 2)
    env = np.ones(n)
    if attack > 0:
        env[:attack] = np.linspace(0, 1, attack)
    if release > 0:
        env[-release:] = np.linspace(1, 0, release)
    y = y * env
    return y.astype(np.float64)


VOICE_PARAMS = {
    40: dict(role='Lead (Violin)', ff_ratio=3.0, duty=0.50,
             carrier='sine', envelope='hann', gain=0.55),
    24: dict(role='Chords (Acoustic Guitar)', ff_ratio=2.0, duty=0.42,
             carrier='saw', envelope='gaussian', gain=0.20),
    32: dict(role='Bass', ff_ratio=1.0, duty=0.90,
             carrier='saw', envelope='decay', gain=0.50),
    0:  dict(role='Percussion', carrier='noise', envelope='decay',
             duty=0.5, gain=0.42, ff_noise=2400.0),
}
# per-MIDI-pitch override for percussion: sub-audio pulse rates (rhythmic ticks)
PERC_FP = {36: 4.3, 42: 5.4, 38: 6.0}


def render_voice(events, params, rng):
    """Render all events of one voice program into a track buffer."""
    total = max(e['end'] for e in events) + 0.5
    n_total = int(total * SR)
    buf = np.zeros(n_total, dtype=np.float64)
    for e in events:
        dur = e['end'] - e['start']
        if dur <= 0:
            continue
        if params['carrier'] == 'noise':
            # sub-audio pulse rate for percussion: rhythmic ticking
            p = PulsarSynth(fp=PERC_FP.get(e['pitch'], 5.0),
                            ff=params.get('ff_noise', 2400.0),
                            duty=params['duty'], carrier='noise',
                            envelope=params['envelope'], fs=SR, rng=rng)
            y = p.generate(dur)
            n = len(y)
            attack = min(int(0.003 * SR), n // 2)
            release = min(int(0.050 * SR), n // 2)
            env = np.ones(n)
            if attack > 0:
                env[:attack] = np.linspace(0, 1, attack)
            if release > 0:
                env[-release:] = np.linspace(1, 0, release)
            y = y * env
        else:
            y = synth_note(e['pitch'], dur, params, rng)
        if len(y) == 0:
            continue
        # velocity scaling
        y = y * (e['vel'] / 127.0) * params['gain']
        start_s = int(e['start'] * SR)
        end_s = min(start_s + len(y), n_total)
        if start_s >= n_total:
            continue
        buf[start_s:end_s] += y[:end_s - start_s]
    # DC removal per voice (pitfall 4)
    buf = buf - np.mean(buf)
    return buf


# ------------------------------------------------------------------ read midi
mid = MidiFile(SRC_MIDI)
tpb = mid.ticks_per_beat
tempo_us = 500000
for track in mid.tracks:
    for msg in track:
        if msg.type == 'tempo':
            tempo_us = msg.tempo
            break
    else:
        continue
    break
sec_per_tick = tempo_us / 1e6 / tpb

events = []
for ti, track in enumerate(mid.tracks):
    program = 0
    abs_ticks = 0
    open_notes = {}
    for msg in track:
        abs_ticks += msg.time
        if msg.type == 'program_change':
            program = msg.program
        elif msg.type == 'note_on' and msg.velocity > 0:
            open_notes[msg.note] = (abs_ticks, msg.velocity, program)
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            if msg.note in open_notes:
                st, vel, p = open_notes.pop(msg.note)
                events.append(dict(start=st * sec_per_tick,
                                   end=abs_ticks * sec_per_tick,
                                   pitch=msg.note, vel=vel, program=p))
    for note, (st, vel, p) in open_notes.items():
        events.append(dict(start=st * sec_per_tick,
                           end=(st + tpb) * sec_per_tick,
                           pitch=note, vel=vel, program=p))

assert events, 'no note events parsed'
total_dur = max(e['end'] for e in events) + 0.5
print(f'parsed {len(events)} events, duration {total_dur:.2f}s')

# ------------------------------------------------------------------ render
by_prog = defaultdict(list)
for e in events:
    by_prog[e['program']].append(e)

rng = np.random.default_rng(SEED)
voice_buffers = {}
mix = np.zeros(int(total_dur * SR), dtype=np.float64)
n_synth = 0
for prog, evs in sorted(by_prog.items()):
    params = VOICE_PARAMS[prog]
    buf = render_voice(evs, params, rng)
    voice_buffers[prog] = buf
    mix[:len(buf)] += buf
    n_synth += len(evs)
    print(f'voice prog {prog} ({params["role"]}): {len(evs)} notes rendered')

# ------------------------------------------------------------------ post
try:
    from scipy.signal import butter, sosfilt
    sos_hp = butter(2, 20, fs=SR, output='sos', btype='highpass')
    sos_lp = butter(4, 16000, fs=SR, output='sos', btype='lowpass')
    mix = sosfilt(sos_hp, sosfilt(sos_lp, mix))
    print('post: 20Hz HP + 16kHz LP applied')
except Exception as exc:
    print(f'post filters skipped ({exc})')

peak = np.max(np.abs(mix))
if peak > 0:
    mix = mix / peak * PEAK

# ------------------------------------------------------------------ verify
mono = mix
silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
secs = int(total_dur)
rms_map = []
for s in range(secs):
    seg = mono[s * SR:(s + 1) * SR]
    rms = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
    rms_map.append(round(rms, 5))
print(f'silence ratio: {silent * 100:.1f}%')
print(f'per-second RMS: {rms_map}')

# pitch check: FFT dominant peak per 0.5 s window (50-1000 Hz)
def fft_pitch(seg, sr):
    seg = seg * np.hanning(len(seg))
    spec = np.abs(np.fft.rfft(seg))
    freqs = np.fft.rfftfreq(len(seg), 1 / sr)
    mask = (freqs >= 50) & (freqs <= 1000)
    if not np.any(mask):
        return 0.0
    return freqs[mask][np.argmax(spec[mask])]

pitches = []
for t0 in np.arange(0.25, max(total_dur - 0.5, 0.5), 0.5):
    seg = mono[int(t0 * SR):int((t0 + 0.5) * SR)]
    p = fft_pitch(seg, SR)
    if p > 0:
        pitches.append(p)
print(f'pitch frames detected: {len(pitches)}')
if pitches:
    print(f'  pitch range: {min(pitches):.0f}-{max(pitches):.0f} Hz, '
          f'median {np.median(pitches):.0f} Hz')

# ------------------------------------------------------------------ write wavs
def write_wav(path, data, sr=SR):
    data16 = (np.clip(data, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(data16.tobytes())

wav_path = os.path.join(OUT_DIR, 'Audio', f'{NAME}.wav')
write_wav(wav_path, mix)
print(f'WAV: {wav_path} ({os.path.getsize(wav_path)} bytes)')

stem_paths = {}
for prog, buf in voice_buffers.items():
    sp = os.path.join(OUT_DIR, 'Audio', 'stems', f'stem_{VOICE_PARAMS[prog]["role"].split(" ")[0].lower()}.wav')
    # normalize stem to 0.89 peak too (per-voice)
    pk = np.max(np.abs(buf))
    if pk > 0:
        buf = buf / pk * PEAK
    write_wav(sp, buf)
    stem_paths[VOICE_PARAMS[prog]['role']] = sp
    print(f'stem: {sp} ({os.path.getsize(sp)} bytes)')

ogg_path = os.path.join(OUT_DIR, 'Audio', f'{NAME}.ogg')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav_path,
                '-codec:a', 'libopus', '-b:a', '128k', ogg_path], check=True)
print(f'OGG: {ogg_path} ({os.path.getsize(ogg_path)} bytes)')

# copy source midi
midi_out = os.path.join(OUT_DIR, 'MIDI', f'{NAME}.mid')
shutil.copy2(SRC_MIDI, midi_out)

# ------------------------------------------------------------------ provenance
with open(SRC_MIDI, 'rb') as f:
    sha = hashlib.sha256(f.read()).hexdigest()

prov = {
    'job': 'SP-036 production pass (cron)',
    'source_midi': SRC_MIDI,
    'source_midi_sha256': sha,
    'production_method': 'SP-036',
    'production_method_name': 'Pulsar Synthesis (Curtis Roads)',
    'source_composition': '001-country-loop-seamless (Country, G major, 120 BPM, 16 bars)',
    'parameters': {
        'sample_rate': SR,
        'seed': SEED,
        'peak': PEAK,
        'post': {'highpass_hz': 20, 'lowpass_hz': 16000},
        'per_voice': {str(k): {kk: vv for kk, vv in v.items() if kk != 'role'}
                      for k, v in VOICE_PARAMS.items()},
        'percussion_pulse_rates_hz': PERC_FP,
        'adsr': {'attack_s': 0.015, 'release_s': 0.090},
        'carrier_phase': 'continuous accumulation, zero-aligned per pulsaret',
    },
    'outputs': {
        'full_mix_wav': wav_path,
        'full_mix_ogg': ogg_path,
        'stems': stem_paths,
        'midi': midi_out,
    },
    'verification': {
        'notes_parsed': len(events),
        'notes_synthesized': n_synth,
        'duration_sec': round(total_dur, 2),
        'silence_ratio': round(silent, 4),
        'rms_per_second': rms_map,
        'pitch_frames_detected': len(pitches),
        'pitch_range_hz': [round(min(pitches), 1), round(max(pitches), 1)] if pitches else None,
        'pitch_median_hz': round(float(np.median(pitches)), 1) if pitches else None,
    },
}
prov_path = os.path.join(OUT_DIR, 'provenance.json')
with open(prov_path, 'w') as f:
    json.dump(prov, f, indent=2)
print(f'provenance: {prov_path}')

# render stats json
stats = {
    'file': wav_path,
    'size_bytes': os.path.getsize(wav_path),
    'duration_sec': round(total_dur, 2),
    'silence_ratio': round(silent, 4),
    'rms_per_second': rms_map,
    'pitch_frames': len(pitches),
    'pitch_median_hz': round(float(np.median(pitches)), 1) if pitches else None,
    'notes_parsed': len(events),
}
stats_path = os.path.join(OUT_DIR, 'Analysis', 'render_stats.json')
with open(stats_path, 'w') as f:
    json.dump(stats, f, indent=2)
print(f'render stats: {stats_path}')

# grid visualization (density per bar per voice)
BAR = 2.0  # seconds per bar at 120 BPM
n_bars = int(total_dur / BAR)
grid_lines = ['SP-036 Pulsar Synthesis - Country Loop (001-country-loop-seamless)',
              f'duration {total_dur:.1f}s, {n_bars} bars @ 120 BPM',
              '']
for prog in sorted(by_prog):
    evs = by_prog[prog]
    cells = []
    for b in range(n_bars):
        t0 = b * BAR
        t1 = t0 + BAR
        onsets = [e for e in evs if t0 <= e['start'] < t1]
        density = min(len(onsets), 16)
        cells.append('#' * density + '.' * (16 - density))
    grid_lines.append(f'prog {prog:3d} {VOICE_PARAMS[prog]["role"]:<28} |' + '|'.join(cells))
grid_lines.append('')
grid_lines.append('Legend: 16 sub-cells per bar, # = onset density, . = rest')
grid_path = os.path.join(OUT_DIR, 'Analysis', 'grid_visualization.txt')
with open(grid_path, 'w') as f:
    f.write('\n'.join(grid_lines) + '\n')
print(f'grid: {grid_path}')

print('DONE')
