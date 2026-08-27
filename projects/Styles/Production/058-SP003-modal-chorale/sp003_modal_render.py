#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SP-003 Modal Physical Modeling (Plate/Bar) production render.

Applies modal synthesis (parallel second-order resonator biquad bank) to
058-markov-chorale.mid. Each MIDI voice is mapped to a modal object preset:
  - highest register  -> marimba bar   (bright, warm woody; ratios 1:4:10)
  - upper-mid         -> glass bar     (bar with inharmonicity, more modes)
  - lower-mid         -> rectangular plate (deep resonant)
  - lowest register   -> large church plate/bell (dark, long decay)

Per-note: velocity maps to excitation amplitude + mallet hardness, note-onset
triggers a force impulse, object rings with natural modal decay (no envelope
generator). Render via scipy.signal.lfilter (C-speed biquad per mode). Sum,
DC-remove, normalize to -0.9 dBFS, write WAV. Method per methods_db.md SP-003
(cross-ref SP-042 modal-bank mechanics: eigenfreq table, gamma damping,
mode-shape strike/listen weights).
"""
import wave
import os
import json
import numpy as np
import scipy.signal as sig
import mido
from mido import MidiFile

SR = 44100
FS = SR
MIDI_PATH = '/opt/data/projects/Styles/Experimental/058-markov-chorale/MIDI/058-markov-chorale.mid'
OUT_DIR = '/opt/data/projects/Styles/Production/058-SP003-modal-chorale'
TAIL = 3.0          # max natural decay tail appended after note off
MAX_DUR = 12.0      # overall render ceiling (buffer)

os.makedirs(f'{OUT_DIR}/Audio', exist_ok=True)
os.makedirs(f'{OUT_DIR}/MIDI', exist_ok=True)


def midi_to_freq(n):
    return 440.0 * (2.0 ** ((n - 69) / 12.0))


# --- modal preset generators (methods_db SP-042 / SP-003 physics) ---
def marimba_bar(f0, num_modes=5, inharmonicity=0.0):
    """Tuned bar modes at 1:4:10 (warm woody marimba)."""
    ratios = np.array([1.0, 4.0, 10.0, 13.2, 18.5])[:num_modes]
    freqs = f0 * ratios * np.sqrt(1.0 + inharmonicity * np.arange(1, num_modes + 1) ** 2)
    gamma = 2.0 + 0.15 * np.arange(num_modes) + 0.0004 * freqs   # radiation damping
    phi_f = np.array([1.0, 0.1, 0.8, 0.3, 0.5])[:num_modes]
    phi_r = np.ones(num_modes)
    return freqs, gamma, phi_f, phi_r


def glass_bar(f0, num_modes=6, inharmonicity=0.25):
    """Glass-armanica bar: stronger inharmonicity + more modes (bright glassy)."""
    ratios = np.array([1.0, 2.32, 4.0, 5.45, 8.4, 11.0])[:num_modes]
    freqs = f0 * ratios * np.sqrt(1.0 + inharmonicity * np.arange(1, num_modes + 1) ** 2)
    gamma = 1.5 + 0.5 * np.arange(num_modes) + 0.0006 * freqs
    phi_f = np.array([1.0, 0.35, 0.7, 0.4, 0.25, 0.3])[:num_modes]
    phi_r = np.ones(num_modes)
    return freqs, gamma, phi_f, phi_r


def rectangular_plate(f0, Lx=1.0, Ly=0.7):
    """Rectangular plate modes (deep resonant)."""
    freqs, pf, pr = [], [], []
    for m in range(1, 6):
        for n in range(1, 5):
            ratio = np.sqrt((m / Lx) ** 2 + (n / Ly) ** 2)
            ratio_ref = np.sqrt((1.0 / Lx) ** 2 + (1.0 / Ly) ** 2)
            freqs.append(f0 * ratio / ratio_ref)
            val = abs(np.sin(m * np.pi * 0.45) * np.sin(n * np.pi * 0.45))
            pf.append(val)
            pr.append(val)
    freqs = np.array(freqs)
    gamma = 1.0 + 0.05 * freqs + 0.0003 * freqs
    return freqs, gamma, np.array(pf), np.array(pr)


def church_plate(f0, num_modes=7):
    """Church-bell style low plate: dark, long decay (bass voice)."""
    ratios = np.array([0.5, 1.0, 1.2, 1.5, 2.0, 2.5, 3.0])[:num_modes]
    freqs = f0 * ratios
    gamma = np.array([0.3, 0.5, 1.0, 1.5, 3.0, 5.0, 7.0])[:num_modes] + 0.0002 * freqs
    return freqs, gamma, np.ones(num_modes), np.ones(num_modes)


def render_modal(out, f0, preset_fn, strike_len, hardness, exc_amp, dur, ns_total, place):
    """Render one struck modal object into buffer `out` at sample offset `place`.

    biquad H(z) = 1 / (1 - a1 z^-1 - a2 z^-2), input = impulse * gain.
    """
    freqs, gamma, pf, pr = preset_fn(f0)
    freqs = freqs[freqs < FS / 4]      # clamp below Nyquist (pitfall #3/#4)
    gamma = gamma[:len(freqs)]
    pf = pf[:len(freqs)]
    pr = pr[:len(freqs)]
    ns = min(int(dur * FS), ns_total - place)
    if ns <= 0:
        return
    T = 1.0 / FS
    # strike excitation: half-sine mallet (soft) or impulse (hard)
    x = np.zeros(ns)
    ml = max(1, int(0.002 / max(hardness, 0.05) * FS))
    ml = min(ml, ns)
    if hardness >= 0.9:
        x[0] = 1.0
    else:
        tm = np.linspace(0, np.pi, ml)
        x[:ml] = np.sin(tm)
    block = np.zeros(ns)
    for k in range(len(freqs)):
        om = 2.0 * np.pi * freqs[k]
        gam = gamma[k]
        omd_sq = om * om - gam * gam
        if omd_sq <= 0:
            continue
        omd = np.sqrt(omd_sq)
        R = np.exp(-gam * T)
        a1 = -2.0 * R * np.cos(omd * T)
        a2 = R * R
        gain = pf[k] * pr[k] * exc_amp
        # denominator 1 + a1 z^-1 + a2 z^-2  (a1=-2Rcos, a2=R^2 -> stable)
        yi = sig.lfilter([gain], [1.0, a1, a2], x)
        block += yi
    out[place:place + ns] += block


# --- parse MIDI (read-only, mido allowed) ---
mf = MidiFile(MIDI_PATH)
tempo = 500000
track_notes = []   # list of (start_sec, dur_sec, note, vel) per track
for tr in mf.tracks:
    t = 0
    events = []
    for msg in tr:
        t += msg.time
        if msg.type == 'set_tempo':
            tempo = msg.tempo
        if msg.type == 'note_on' and msg.velocity > 0:
            events.append({'tick': t, 'note': msg.note, 'vel': msg.velocity})
        if msg.type == 'note_off':
            # match by note (last unclosed)
            for e in reversed(events):
                if e['note'] == msg.note and 'end' not in e:
                    e['end'] = t
                    break
        if msg.type == 'note_on' and msg.velocity == 0:
            for e in reversed(events):
                if e['note'] == msg.note and 'end' not in e:
                    e['end'] = t
                    break
    spb = tempo / 1e6
    secs = [(e['tick'] * spb / mf.ticks_per_beat,
             (e.get('end', e['tick'] + mf.ticks_per_beat) - e['tick']) * spb / mf.ticks_per_beat,
             e['note'], e['vel']) for e in events if e.get('end') is not None]
    if secs:
        track_notes.append(secs)

# assign presets by mean register (highest -> marimba, ... lowest -> church plate)
means = [np.mean([n[2] for n in tn]) for tn in track_notes]
order = np.argsort(means)[::-1]   # high to low
preset_list = [marimba_bar, glass_bar, rectangular_plate, church_plate]
presets = {int(ti): preset_list[min(i, len(preset_list) - 1)]
           for i, ti in enumerate(order)}

total_dur = min(MAX_DUR, max((s + d for tn in track_notes for s, d, _, _ in tn), default=4) + TAIL)
n_total = int(total_dur * SR)
out = np.zeros(n_total)

for ti, tn in enumerate(track_notes):
    preset = presets.get(ti, marimba_bar)
    for s, d, note, vel in tn:
        f0 = midi_to_freq(note)
        amp = (vel / 127.0) ** 1.2 * 0.9
        hardness = 0.35 + 0.55 * (vel / 127.0)   # louder = harder mallet
        dur = min(d + TAIL, total_dur - s)
        place = int(s * FS)
        render_modal(out, f0, preset, strike_len=0.002, hardness=hardness,
                     exc_amp=amp, dur=dur, ns_total=n_total, place=place)

# --- master: DC remove, normalize -0.9 dBFS ---
out -= np.mean(out)
peak = np.max(np.abs(out))
if peak > 0:
    out = out / peak * 0.9
mono = out

# stereo width: simple complementary comb (left slight lead, right slight lag)
delay = int(0.008 * FS)
L = mono.copy()
R = mono.copy()
if len(mono) > delay:
    L[delay:] += 0.25 * mono[:-delay]
    R[:-delay] += 0.25 * mono[delay:]
mix = np.stack([L, R], axis=1)
mix /= np.max(np.abs(mix)) * 0.9 / 0.9
mix = np.clip(mix, -1.0, 1.0)

# silence metric (production gate: >30% silence suspect)
mono_check = (L + R) * 0.5
silent = float(np.sum(np.abs(mono_check) < 0.001) / len(mono_check))

wav_path = f'{OUT_DIR}/Audio/058-markov-chorale-SP003-modal-plate.wav'
with wave.open(wav_path, 'w') as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    data = (mix * 32767.0).astype(np.int16)
    wf.writeframes(data.tobytes())

os.system(f'cp {MIDI_PATH} {OUT_DIR}/MIDI/058-markov-chorale-original.mid')
os.system(f'ffmpeg -y -i {wav_path} -codec:a libopus -application voip -b:a 48k '
          f'{OUT_DIR}/Audio/058-markov-chorale-SP003-modal-plate.ogg -loglevel error')

wav_bytes = os.path.getsize(wav_path)
ogg_bytes = os.path.getsize(f'{OUT_DIR}/Audio/058-markov-chorale-SP003-modal-plate.ogg')

info = {
    'midi': MIDI_PATH,
    'method': 'SP-003',
    'method_name': 'Modal Physical Modeling (Plate/Bar)',
    'voice_presets': {str(k): v.__name__ for k, v in presets.items()},
    'tempo_bpm': 60_000_000 / tempo,
    'track_means': [round(m, 1) for m in means],
    'n_notes': sum(len(tn) for tn in track_notes),
    'duration_s': round(total_dur, 2),
    'silence_ratio': round(silent, 3),
    'wav_bytes': wav_bytes,
    'ogg_bytes': ogg_bytes,
}
print(json.dumps(info, indent=2))
with open(f'{OUT_DIR}/provenance.json', 'w') as f:
    json.dump(info, f, indent=2)

assert wav_bytes > 40000, 'WAV suspiciously small'
assert ogg_bytes > 10000, 'OGG suspiciously small'
print('OK')
