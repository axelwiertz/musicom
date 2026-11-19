import sys, os, subprocess, tempfile, numpy as np, wave, mido
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
    os.unlink(p); os.unlink(wav)
    return a, sr

def spec(x,sr):
    X=np.abs(np.fft.rfft(x*np.hanning(len(x)))); f=np.fft.rfftfreq(len(x),1/sr)
    return f,X

for note in [48,55,60,67,72,79,84]:
    a,sr=render([note],dur=1.2)
    seg=a[int(0.3*sr):int(1.1*sr)]
    f,X=spec(seg,sr)
    idx=np.argsort(X)[::-1]
    peaks=[]
    for i in idx:
        if f[i]<30: continue
        if all(abs(f[i]-p)>25 for p,_ in peaks): peaks.append((f[i],X[i]))
        if len(peaks)>=5: break
    r=X.max()
    print(f"note {note} f0exp={440*2**((note-69)/12):.1f}: "+", ".join(f"{p:.0f}Hz({20*np.log10(v/r):.0f}dB)" for p,v in peaks))
    tot=np.sqrt(np.mean(seg**2)); print(f"   rms={tot:.3f}")
# attack profile at 1ms resolution for note 60
a,sr=render([60],dur=0.5)
for ms in [0,2,5,10,20,40,80,150,300]:
    i=int(ms/1000*sr); print(f"t={ms}ms rms={np.sqrt(np.mean(a[i:i+int(0.005*sr)]**2)):.4f} peak={np.max(np.abs(a[i:i+int(0.005*sr)])):.3f}")
