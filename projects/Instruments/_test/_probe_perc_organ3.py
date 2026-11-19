import sys, os, subprocess, tempfile, numpy as np, wave
sys.path.insert(0,'/opt/data/projects/Instruments')
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
    fd,p=tempfile.mkstemp(suffix='.mid'); os.close(fd); mid.save(p)
    wav=p.replace('.mid','.wav')
    subprocess.run([FS,'-ni','-g','1.2','-F',wav,SF2,p],capture_output=True,check=True)
    w=wave.open(wav); sr=w.getframerate(); n=w.getnframes()
    a=np.frombuffer(w.readframes(n),dtype='int16').astype(float)/32768.0
    os.unlink(p); os.unlink(wav); return a,sr
def acf_f0(x,sr,lo=40,hi=1200):
    x=x-x.mean(); c=np.correlate(x,x,'full')[len(x)-1:]
    a,b=int(sr/hi),int(sr/lo)
    lag=a+np.argmax(c[a:b]); return sr/lag, c[lag]/c[0]
for note in [36,43,48,55,60,67,72,79,84,90,96]:
    a,sr=render([note],dur=2.0)
    seg=a[int(0.4*sr):int(1.0*sr)]
    f0,q=acf_f0(seg,sr)
    print(f"note {note} exp={440*2**((note-69)/12):7.1f}Hz acf={f0:7.1f}Hz clarity={q:.2f} rms={np.sqrt(np.mean(seg**2)):.3f}")
a,sr=render([60],dur=0.5)
print("pre-note rms", np.sqrt(np.mean(a[:int(0.005*sr)]**2)))
