#!/usr/bin/env python3
import os, numpy as np
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from scipy.io import wavfile

project_dir = "/opt/data/projects/Styles/Fanfare/003-dutch-fanfare-seamless"
os.makedirs(f"{project_dir}/MIDI", exist_ok=True)
os.makedirs(f"{project_dir}/Audio", exist_ok=True)
os.makedirs(f"{project_dir}/Scores", exist_ok=True)

TPB = 480
TEMPO_BPM = 120
TEMPO = bpm2tempo(TEMPO_BPM)
BAR = TPB * 4
TOTAL = BAR * 8


def build_track(name, channel, program, events):
    tr = MidiTrack(); tr.name = name
    if program is not None:
        tr.append(Message('program_change', program=program, channel=channel, time=0))
    timeline = []
    for s, d, n, v in events:
        timeline.append((s, 0, n, v))
        timeline.append((s + d, 1, n, 0))
    timeline.sort(key=lambda x: (x[0], x[1]))
    cur = 0
    for tick, kind, n, v in timeline:
        dt = tick - cur
        if dt < 0:
            raise ValueError(f'negative delta {name} at {tick} < {cur}')
        if kind == 0:
            tr.append(Message('note_on', note=n, velocity=v, channel=channel, time=dt))
        else:
            tr.append(Message('note_off', note=n, velocity=0, channel=channel, time=dt))
        cur = tick
    tr.append(MetaMessage('end_of_track', time=TOTAL - cur))
    return tr

mid = MidiFile(ticks_per_beat=TPB)
meta = MidiTrack()
meta.append(MetaMessage('set_tempo', tempo=TEMPO, time=0))
meta.append(MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
meta.append(MetaMessage('end_of_track', time=TOTAL))
mid.tracks.append(meta)

lead_events = []
for bar in range(8):
    base = bar * BAR
    notes = [70, 74, 77, 74] if bar % 2 == 0 else [75, 77, 79, 77]
    for i, n in enumerate(notes):
        lead_events.append((base + i * TPB, TPB, n, 100 if i == 0 else 94))

harm_events = []
harm_chords = [[58, 62, 65], [58, 62, 65], [51, 55, 58], [58, 62, 65], [55, 58, 62], [58, 62, 65], [53, 57, 60], [58, 62, 65]]
for i, chord in enumerate(harm_chords):
    start = i * BAR
    for n in chord:
        harm_events.append((start, BAR - 60, n, 72))

bass_pattern = [46, 41, 46, 50, 39, 46, 41, 46]
bass_events = [(i * TPB, TPB, p, 90) for i, p in enumerate(bass_pattern * 4)]

perc_events = []
for bar in range(8):
    b = bar * BAR
    for beat in [0, 2]:
        perc_events.append((b + beat * TPB, TPB // 4, 36, 108))
    for beat in [1, 3]:
        perc_events.append((b + beat * TPB, TPB // 4, 38, 98))
    if bar in (3, 7):
        perc_events.append((b + int(3.5 * TPB), TPB // 4, 49, 88))

mid.tracks.append(build_track('Trumpet', 0, 56, lead_events))
mid.tracks.append(build_track('Horn', 1, 60, harm_events))
mid.tracks.append(build_track('Tuba', 2, 58, bass_events))
mid.tracks.append(build_track('Percussion', 9, 0, perc_events))

midi_path = f'{project_dir}/MIDI/loop.mid'
mid.save(midi_path)

sr = 44100
secs = 8 * 4 * 60.0 / TEMPO_BPM
audio = np.zeros(int(sr * secs), dtype=np.float32)
A4 = 440.0
m2f = lambda n: A4 * (2 ** ((n - 69) / 12.0))
for start, dur, n, v in lead_events + bass_events:
    st = int(start / TPB * 60.0 / TEMPO_BPM * sr)
    en = min(len(audio), st + int(dur / TPB * 60.0 / TEMPO_BPM * sr))
    if en > st:
        env = np.linspace(1, 0, en - st, endpoint=False)
        audio[st:en] += (v / 127.0) * 0.11 * np.sin(2*np.pi*m2f(n)*np.arange(en-st)/sr) * env
for i, chord in enumerate(harm_chords):
    start = i * BAR
    st = int(start / TPB * 60.0 / TEMPO_BPM * sr)
    en = min(len(audio), st + int((BAR - 60) / TPB * 60.0 / TEMPO_BPM * sr))
    for n in chord:
        if en > st:
            env = np.linspace(1, 0, en - st, endpoint=False)
            audio[st:en] += 0.04 * np.sin(2*np.pi*m2f(n)*np.arange(en-st)/sr) * env
mx = float(np.max(np.abs(audio)))
if mx > 0:
    audio = audio / mx * 0.9
wavfile.write(f'{project_dir}/Audio/loop.wav', sr, audio.astype(np.float32))
with open(f'{project_dir}/index.html', 'w') as f:
    f.write('<html><body><h1>Fanfare 003 — Dutch Fanfare Seamless</h1></body></html>')
print('ok')
print(midi_path)
