import sys, os, subprocess, tempfile, numpy as np
sys.path.insert(0,'/opt/data/projects/Instruments'); sys.path.insert(0,'/opt/data/projects/Instruments/_test')
import mido
from mido import Message, MidiFile, MidiTrack
from sound.render.fluidsynth import discover_soundfont
SF2=discover_soundfont(); FS="/opt/data/micromamba/envs/musicom/bin/fluidsynth"

def render(notes, vel=100, dur=1.0, gap=1.0):
    mid=MidiFile(ticks_per_beat=480); tr=MidiTrack(); mid.tracks.append(tr)
    tr.append(Message('program_change', program=17, channel=0, time=0))
    ev=[]
    for i,p in enumerate(notes):
        ev.append((i*gap, Message('note_on', note=p, velocity=vel, channel=0)))
        ev.append((i*gap+dur, Message('note_off', note=p, velocity=0, channel=0)))
    ev.sort(key=lambda x:x[0]); t=0
    for at,msg in ev:
        msg.time=int((at-t)*480); t=at; tr.append(msg)
    tr.append(Message('note_off', note=0, velocity=0, channel=0, time=int(480)))
    fd,p=tempfile.mkstemp(suffix='.mid'); os.close(fd); mid.save(p)
    wav=p.replace('.mid','.wav')
    subprocess.run([FS,'-ni','-g','1.2','-F',wav,SF2,p],capture_output=True,check=True)
    import wave
    w=wave.open(wav); sr=w.getframerate(); n=w.getnframes()
    a=np.frombuffer(w.readframes(n),dtype='int16').astype(float)/32768.0
    if a.ndim>1: a=a.mean(axis=1)
    os.unlink(p)
    return a, sr, wav

def centroid(x,sr):
    X=np.abs(np.fft.rfft(x*np.hanning(len(x)))); f=np.fft.rfftfreq(len(x),1/sr)
    return float((X*f).sum()/max(X.sum(),1e-12))

def peakfreq(x,sr):
    X=np.abs(np.fft.rfft(x*np.hanning(len(x)))); f=np.fft.rfftfreq(len(x),1/sr)
    return float(f[np.argmax(X)])

for note in [36,48,60,72,84,96]:
    a,sr,wav=render([note])
    seg=a[int(0.05*sr):int(0.45*sr)]
    print(f"note {note}: peak={np.max(np.abs(a)):.3f} f0={peakfreq(seg,sr):.1f}Hz cent={centroid(seg,sr):.0f}Hz")
    os.unlink(wav)
print("--- velocity response (note 60, 300ms) ---")
for v in [20,40,60,80,100,120,127]:
    a,sr,wav=render([60],vel=v,dur=0.3)
    print(f" vel {v}: peak={np.max(np.abs(a)):.4f} cent={centroid(a[int(0.02*sr):int(0.25*sr)],sr):.0f}")
    os.unlink(wav)
print("--- decay/envelope note 60 held 1.5s ---")
a,sr,wav=render([60],dur=1.5)
hop=int(0.1*sr)
for i in range(0,len(a)-hop,hop):
    if i/sr>1.7: break
    print(f"  t={i/sr:.1f}s rms={np.sqrt(np.mean(a[i:i+hop]**2)):.4f}")
os.unlink(wav)
