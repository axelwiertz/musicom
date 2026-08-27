#!/usr/bin/env python3
import os, numpy as np
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from scipy.io import wavfile

project_dir = "/opt/data/projects/Styles/Fanfare/002-drumband-seamless"
os.makedirs(f"{project_dir}/MIDI", exist_ok=True)
os.makedirs(f"{project_dir}/Audio", exist_ok=True)
os.makedirs(f"{project_dir}/Scores", exist_ok=True)

TPB = 480
TEMPO_BPM = 132
TEMPO = bpm2tempo(TEMPO_BPM)
BAR_TICKS = TPB * 4
EIGHT_BARS = BAR_TICKS * 8

def build_track(name, channel, program, events):
    tr = MidiTrack(); tr.name = name
    if program is not None:
        tr.append(Message('program_change', program=program, channel=channel, time=0))
    last_on = 0
    pending = []
    # events are (start_tick, duration_tick, note, velocity)
    # sort note-off after note-on at same tick not needed because we use explicit deltas
    timeline = []
    for start, dur, note, vel in events:
        timeline.append((start, 'on', note, vel))
        timeline.append((start + dur, 'off', note, 0))
    timeline.sort(key=lambda x: (x[0], 0 if x[1] == 'on' else 1))
    cur = 0
    for tick, typ, note, vel in timeline:
        delta = tick - cur
        if delta < 0:
            raise ValueError(f'Negative delta in {name}: tick={tick}, cur={cur}')
        if typ == 'on':
            tr.append(Message('note_on', note=note, velocity=vel, channel=channel, time=delta))
        else:
            tr.append(Message('note_off', note=note, velocity=0, channel=channel, time=delta))
        cur = tick
    tr.append(MetaMessage('end_of_track', time=EIGHT_BARS - cur))
    return tr

mid = MidiFile(ticks_per_beat=TPB)
meta = MidiTrack()
meta.append(MetaMessage('set_tempo', tempo=TEMPO, time=0))
meta.append(MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
meta.append(MetaMessage('end_of_track', time=EIGHT_BARS))
mid.tracks.append(meta)

# Events in ticks
lead_events = [(i * TPB, TPB, p, 96) for i, p in enumerate([70, 74, 77, 74, 75, 77, 79, 77] * 4)]
harm_chords = [[58, 62, 65], [58, 62, 65], [51, 55, 58], [58, 62, 65], [58, 62, 65], [53, 57, 60], [51, 55, 58], [58, 62, 65]]
harm_events = []
for i, chord in enumerate(harm_chords):
    start = i * BAR_TICKS
    for p in chord:
        harm_events.append((start, BAR_TICKS, p, 76))
bass_events = [(i * TPB, TPB, p, 88) for i, p in enumerate([46, 41, 46, 50, 39, 46, 41, 46] * 4)]
perc_events = []
for bar in range(8):
    base = bar * BAR_TICKS
    for beat in [0, 1, 2, 3]:
        perc_events.append((base + beat * TPB, TPB // 4, 42, 72))
    for beat, pitch, vel in [(0, 36, 104), (1, 38, 96), (2, 36, 104), (3, 38, 96)]:
        perc_events.append((base + beat * TPB, TPB // 4, pitch, vel))
    if bar in (3, 7):
        perc_events.append((base + int(3.75 * TPB), TPB // 4, 49, 84))

mid.tracks.append(build_track('Trumpet', 0, 56, lead_events))
mid.tracks.append(build_track('Horn', 1, 60, harm_events))
mid.tracks.append(build_track('Tuba', 2, 58, bass_events))
mid.tracks.append(build_track('Percussion', 9, 0, perc_events))

midi_path = f'{project_dir}/MIDI/loop.mid'
mid.save(midi_path)

# WAV fallback: pitched voices only
sr = 44100
duration_sec = 8 * 4 * 60.0 / TEMPO_BPM
audio = np.zeros(int(sr * duration_sec), dtype=np.float32)
A4 = 440.0
def midi_to_freq(n): return A4 * (2 ** ((n - 69) / 12.0))
for start, dur, note_num, vel in lead_events + bass_events:
    freq = midi_to_freq(note_num)
    st = int(start / TPB * 60.0 / TEMPO_BPM * sr)
    en = min(len(audio), st + int(dur / TPB * 60.0 / TEMPO_BPM * sr))
    if en > st:
        env = np.linspace(1.0, 0.0, en - st, endpoint=False)
        audio[st:en] += (vel / 127.0) * 0.12 * np.sin(2 * np.pi * freq * np.arange(en - st) / sr) * env
for i, chord in enumerate(harm_chords):
    start = i * BAR_TICKS
    for note_num in chord:
        freq = midi_to_freq(note_num)
        st = int(start / TPB * 60.0 / TEMPO_BPM * sr)
        en = min(len(audio), st + int((BAR_TICKS * 2) / TPB * 60.0 / TEMPO_BPM * sr))
        if en > st:
            env = np.linspace(1.0, 0.0, en - st, endpoint=False)
            audio[st:en] += 0.05 * np.sin(2 * np.pi * freq * np.arange(en - st) / sr) * env
mx = float(np.max(np.abs(audio)))
if mx > 0:
    audio = audio / mx * 0.9
wavfile.write(f'{project_dir}/Audio/loop.wav', sr, audio.astype(np.float32))
with open(f'{project_dir}/index.html', 'w') as f:
    f.write('<html><body><h1>Fanfare 002 — Drumband Seamless</h1></body></html>')
print('ok')
print(midi_path)
