import sys, os, subprocess, tempfile, numpy as np, wave
sys.path.insert(0,'/opt/data/projects/Instruments')
from mido import Message, MidiFile, MidiTrack
from sound.render.fluidsynth import discover_soundfont
SF2=discover_soundfont(); FS="/opt/data/micromamba/envs/musicom/bin/fluidsynth"
def render(notes, vel=100, dur=0.6, gap=0.8):
    mid=MidiFile(ticks_per_beat=480); tr=MidiTrack(); mid.tracks.append(tr)
    tr.append(Message('program_change', program=17, channel=0, time=0))
    ev=[]
    for i,p in enumerate(notes):
        ev.append((i*gap, Message('note_on', note=p, velocity=vel, channel=0)))
        ev.append((i*gap+dur, Message('note_off', note=p, velocity=0, channel=0)))
    ev.sort(key=lambda x:x[0]); t=0
    for at,msg in ev:
        msg.time=int((at-t)*480); t=at; tr.append(msg)
    fd,p=tempfile.mkstemp(suffix='.mid'); os.close(fd); mid.save(p)
    wav=p.replace('.mid','.wav')
    subprocess.run([FS,'-ni','-g','1.2','-F',wav,SF2,p],capture_output=True,check=True)
    w=wave.open(wav); sr=w.getframerate(); n=w.getnframes()
    a=np.frombuffer(w.readframes(n),dtype='int16').astype(float)/32768.0
    os.unlink(p); os.unlink(wav); return a,sr
notes=list(range(24,109,4))
a,sr=render(notes)
seg=int(0.8*sr); res=[]
for i,n in enumerate(notes):
    x=a[i*seg+int(0.1*sr):i*seg+int(0.5*sr)]
    r=np.sqrt(np.mean(x**2)); res.append(r)
print("notes:",notes)
print("rms:",[round(v,4) for v in res])
print("min/max",min(res),max(res))
