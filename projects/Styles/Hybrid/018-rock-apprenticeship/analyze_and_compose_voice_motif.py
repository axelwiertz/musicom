#!/usr/bin/env python3
"""Analyze incoming voice/audio and compose a short blues-rock motif from its sound DNA."""
from pathlib import Path
import json, math, subprocess
import numpy as np
import librosa
import soundfile as sf
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo

ROOT = Path('/opt/data/projects/014-rock-apprenticeship')
AN = ROOT / 'Analysis' / 'voice-motif'
MIDI_DIR = ROOT / 'MIDI'
AUDIO_DIR = ROOT / 'Audio'
for d in [AN, MIDI_DIR, AUDIO_DIR]: d.mkdir(parents=True, exist_ok=True)

SRC = AN / 'source_voice.wav'
TITLE = 'study-03-voice-derived-motif'
MIDI_PATH = MIDI_DIR / f'{TITLE}.mid'
RAW_WAV = AUDIO_DIR / f'{TITLE}-raw.wav'
WAV_PATH = AUDIO_DIR / f'{TITLE}.wav'
OGG_PATH = AUDIO_DIR / f'{TITLE}.ogg'
PNG_PATH = AN / 'voice_motif_analysis.png'
JSON_PATH = AN / 'voice_motif_analysis.json'
MD_PATH = AN / 'voice_motif_analysis.md'
SF2 = '/usr/share/sounds/sf2/FluidR3_GM.sf2'

# --- load and analyze ---
y, sr = librosa.load(SRC, sr=22050, mono=True)
# trim silence/noise tails
trimmed, idx = librosa.effects.trim(y, top_db=28)
y = trimmed if len(trimmed) > sr * 0.25 else y
duration = len(y) / sr
rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=256)[0]
times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=256)
centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=256)[0]
flatness = librosa.feature.spectral_flatness(y=y, hop_length=256)[0]
zcr = librosa.feature.zero_crossing_rate(y, frame_length=1024, hop_length=256)[0]

# onset envelope and peaks
on_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=256)
on_times = librosa.times_like(on_env, sr=sr, hop_length=256)
peaks = librosa.util.peak_pick(on_env, pre_max=3, post_max=3, pre_avg=8, post_avg=8, delta=0.18, wait=3)
onsets = on_times[peaks]
# robust cap: use strongest <= 10 onsets
if len(onsets) > 10:
    strengths = on_env[peaks]
    keep = np.argsort(strengths)[-10:]
    onsets = np.sort(onsets[keep])

# pitch tracking: pyin, fallback spectral estimate
f0, voiced_flag, voiced_prob = librosa.pyin(y, fmin=librosa.note_to_hz('E2'), fmax=librosa.note_to_hz('E5'), sr=sr, frame_length=2048, hop_length=256)
f0_times = librosa.times_like(f0, sr=sr, hop_length=256)
valid = np.isfinite(f0)
if valid.sum() < 3:
    pitches, mags = librosa.piptrack(y=y, sr=sr, hop_length=256, fmin=80, fmax=1200)
    est=[]
    for i in range(pitches.shape[1]):
        j = np.argmax(mags[:,i])
        est.append(pitches[j,i] if mags[j,i] > np.percentile(mags, 85) else np.nan)
    f0=np.array(est); f0_times=librosa.frames_to_time(np.arange(len(f0)), sr=sr, hop_length=256); valid=np.isfinite(f0)

# Convert onsets to note samples. If few onsets, derive 5 evenly spaced contour points.
if len(onsets) < 4:
    onsets = np.linspace(0, max(0.2, duration*0.88), 5)

notes=[]
for t in onsets[:8]:
    win = (f0_times >= max(0,t-0.08)) & (f0_times <= min(duration,t+0.22)) & np.isfinite(f0)
    if win.any():
        hz = float(np.nanmedian(f0[win]))
    elif valid.any():
        hz = float(np.nanmedian(f0[valid]))
    else:
        hz = 164.81  # E3 fallback
    midi = int(round(69 + 12 * math.log2(hz/440.0)))
    notes.append((float(t), midi, hz))

# Normalize into E blues/pentatonic palette for project 014.
E_BLUES = [40,43,45,46,47,50,52,55,57,58,59,62,64,67,69,70,71,74,76]  # E2..E5 E blues + passing maj 3-ish
q_notes=[]
for t,m,hz in notes:
    qm = min(E_BLUES, key=lambda x: abs(x-m))
    q_notes.append((t,qm,hz,m))

# Rhythm extraction: convert inter-onset intervals to 16th grid at a chosen tempo.
# Choose tempo from median IOI mapped near blues-rock range 90-130.
ioi=np.diff([t for t,_,_,_ in q_notes]) if len(q_notes)>1 else np.array([0.5])
med=float(np.median(ioi)) if len(ioi) else 0.5
# Treat median as eighth-ish pulse.
bpm=int(round(60/(max(0.18,min(0.7,med))*2)*4/4))
bpm=max(88,min(124,bpm))
# Keep project groove if estimate weird.
if bpm in [88,124] or duration < 1: bpm=108
TPB=480
beat=60/bpm
# Quantize durations to [eighth, quarter, dotted quarter]
durs=[]
for i in range(len(q_notes)):
    if i < len(q_notes)-1:
        sec=max(0.16, q_notes[i+1][0]-q_notes[i][0])
    else:
        sec=max(0.28, med if med else 0.45)
    beats=sec/beat
    q=min([0.5,0.75,1.0,1.5], key=lambda x: abs(x-beats))
    durs.append(int(q*TPB))

# Compose motif: use extracted contour as A, then call-response transform as A'.
# Start motif on pickup if first onset late; otherwise beat 1.
melody=[]
time=0
for (_,m,_,orig), dur in zip(q_notes, durs):
    melody.append((time, dur, m, 96))
    time += dur
# response: transpose first half up octave/fourth-ish then resolve E
response_start = time + TPB//2
resp=[]
for idx,(_,m,_,orig) in enumerate(q_notes[:min(5,len(q_notes))]):
    target = m + (12 if idx % 2 == 0 else 7)
    target = min(E_BLUES, key=lambda x: abs(x-target))
    resp.append((response_start + idx*TPB//2, TPB//2, target, 88 + idx*3))
# final resolve
resp.append((response_start + len(resp)*TPB//2, TPB, 52, 108))
melody += resp
motif_len = max(t+d for t,d,_,_ in melody)
# pad to 4 bars
bars = max(4, math.ceil(motif_len/(TPB*4)))
total_ticks = bars*TPB*4

# MIDI helpers
def add_note(ev,start,dur,p,vel,ch):
    ev.append((start, Message('note_on', note=int(p), velocity=int(vel), channel=ch, time=0)))
    ev.append((start+dur, Message('note_off', note=int(p), velocity=0, channel=ch, time=0)))
def add_chord(ev,start,dur,pitches,vel,ch):
    for p in pitches: add_note(ev,start,dur,p,vel,ch)
def mk_track(ev,name,program=None,ch=0):
    tr=MidiTrack(); tr.append(MetaMessage('track_name', name=name, time=0))
    if program is not None: tr.append(Message('program_change', program=program, channel=ch, time=0))
    last=0
    for t,msg in sorted(ev, key=lambda x:(x[0],0 if x[1].type=='note_off' else 1)):
        msg.time=max(0,t-last); tr.append(msg); last=t
    tr.append(MetaMessage('end_of_track', time=1)); return tr

lead=[]; rhythm=[]; bass=[]; drums=[]
for t,d,p,v in melody:
    # lead guitar with short note gaps
    add_note(lead,t,max(60,d-24),p,v,2)
# 4-bar E blues support: E / A / E / B-A-E-B hits
roots=[40,45,40,47]
for bar_i,r in enumerate(roots):
    b=bar_i*TPB*4
    # power chord stab + b7 color on bar start
    add_chord(rhythm,b,TPB*3,[r+12,r+19,r+22],82,0)
    # bass boogie quarters/eighths
    pat=[0,7,9,10,9,7,3,0]
    for i,off in enumerate(range(0,TPB*4,TPB//2)):
        add_note(bass,b+off,TPB//2-18,r+pat[i%len(pat)],96,1)
    # drums shuffle-ish 8ths + backbeat
    for beat_i in range(4):
        bt=b+beat_i*TPB
        add_note(drums,bt,50,42,48,9)
        add_note(drums,bt+TPB*2//3,50,42,42,9)
        if beat_i in [0,2]: add_note(drums,bt,70,36,100,9)
        if beat_i in [1,3]: add_note(drums,bt,80,38,108,9)

mid=MidiFile(ticks_per_beat=TPB)
meta=MidiTrack()
meta.append(MetaMessage('track_name', name='014 Study 03 Voice-Derived Motif', time=0))
meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0))
meta.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))
meta.append(MetaMessage('text', text='Motif extracted from incoming voice/sound: pitch contour + onset rhythm mapped to E blues.', time=0))
meta.append(MetaMessage('end_of_track', time=1))
mid.tracks.append(meta)
mid.tracks.append(mk_track(rhythm,'E blues rhythm guitar bed',29,0))
mid.tracks.append(mk_track(bass,'Bass follows voice-derived pulse',33,1))
mid.tracks.append(mk_track(lead,'Voice-derived lead motif',30,2))
mid.tracks.append(mk_track(drums,'Shuffle backbeat drums',None,9))
mid.save(MIDI_PATH)

# Render audio
subprocess.run(['fluidsynth','-ni',SF2,str(MIDI_PATH),'-F',str(RAW_WAV),'-r','44100'], check=True)
subprocess.run(['ffmpeg','-y','-i',str(RAW_WAV),'-af','volume=0.95,alimiter=limit=0.95',str(WAV_PATH)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(['ffmpeg','-y','-i',str(WAV_PATH),'-codec:a','libopus','-application','voip','-b:a','64k',str(OGG_PATH)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try: RAW_WAV.unlink()
except FileNotFoundError: pass

# Plot
fig,axs=plt.subplots(3,1,figsize=(12,8),sharex=False)
librosa.display.waveshow(y, sr=sr, ax=axs[0], color='#00d992')
axs[0].vlines([t for t,_,_,_ in q_notes], -1,1, color='#fb7185', alpha=.7)
axs[0].set_title('Source waveform + detected onsets')
axs[1].plot(f0_times, f0, '.', ms=2, color='#60a5fa')
axs[1].set_title('Pitch trace (Hz)')
axs[1].set_ylabel('Hz')
axs[2].plot(times, centroid[:len(times)], color='#fbbf24', label='centroid')
axs[2].plot(times, flatness[:len(times)]*5000, color='#fb7185', label='flatness x5000')
axs[2].legend(); axs[2].set_title('Timbre: brightness/noisiness')
fig.tight_layout(); fig.savefig(PNG_PATH, dpi=150); plt.close(fig)

intervals=[]
for a,b in zip([m for _,m,_,_ in q_notes], [m for _,m,_,_ in q_notes][1:]): intervals.append(b-a)
features={
    'source': str(SRC), 'duration_sec': round(duration,3), 'bpm_used': bpm,
    'detected_onsets_sec': [round(float(x),3) for x in onsets.tolist()],
    'median_centroid_hz': round(float(np.median(centroid)),1),
    'median_flatness': round(float(np.median(flatness)),4),
    'median_zcr': round(float(np.median(zcr)),4),
    'voiced_frames': int(valid.sum()),
    'extracted_notes': [{'time':round(t,3),'raw_midi':int(orig),'quant_midi':int(m),'hz':round(hz,1)} for t,m,hz,orig in q_notes],
    'pitch_intervals_semitones': intervals,
    'motif_midi': str(MIDI_PATH), 'motif_ogg': str(OGG_PATH), 'analysis_png': str(PNG_PATH)
}
JSON_PATH.write_text(json.dumps(features, indent=2))

def midi_name(m):
    names=['C','C#','D','Eb','E','F','F#','G','Ab','A','Bb','B']
    return f"{names[m%12]}{m//12-1}"
notes_txt=' '.join(midi_name(m) for _,m,_,_ in q_notes)
ints=' '.join(f'{i:+d}' for i in intervals)
MD_PATH.write_text(f"""# Voice Motif Analysis — Study 03

Source duration: {features['duration_sec']}s
Tempo used: {bpm} BPM

## Sound DNA

- Median spectral centroid: {features['median_centroid_hz']} Hz
- Median flatness: {features['median_flatness']}
- Median zero-crossing rate: {features['median_zcr']}
- Voiced pitch frames: {features['voiced_frames']}

## Extracted pitch contour

```text
Notes:     {notes_txt}
Intervals: {ints}
```

## Rhythm DNA

Detected onset count: {len(q_notes)}

```text
Onsets: {' '.join(str(round(t,2)) for t,_,_,_ in q_notes)} seconds
Grid:   {' '.join('█' for _ in q_notes)}
```

## Composition rule

- Preserve input contour.
- Quantize pitches to E blues for Project 014.
- Preserve attack pattern as lead motif rhythm.
- Add E blues-rock bed: power-chord guitar, boogie bass, shuffle backbeat.

## Files

- MIDI: `{MIDI_PATH}`
- OGG: `{OGG_PATH}`
- PNG: `{PNG_PATH}`
""")
print(json.dumps(features, indent=2))
