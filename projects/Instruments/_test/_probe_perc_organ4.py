import sys, os, subprocess, tempfile, numpy as np, wave
sys.path.insert(0,'/opt/data/projects/Instruments')
from mido import Message, MidiFile, MidiTrack
from sound.render.fluidsynth import discover_soundfont
SF2=discover_soundfont(); FS="/opt/data/micromamba/envs/musicom/bin/fluidsynth"
def render(pgm,note,vel=100,dur=2.0):
    mid=MidiFile(ticks_per_beat=480); tr=MidiTrack(); mid.tracks.append(tr)
    tr.append(Message('program_change', program=pgm, channel=0, time=0))
    tr.append(Message('note_on', note=note, velocity=vel, channel=0, time=0))
    tr.append(Message('note_off', note=note, velocity=0, channel=0, time=int(480*dur)))
    fd,p=tempfile.mkstemp(suffix='.mid'); os.close(fd); mid.save(p)
    wav=p.replace('.mid','.wav')
    subprocess.run([FS,'-ni','-g','1.2','-F',wav,SF2,p],capture_output=True,check=True)
    w=wave.open(wav); sr=w.getframerate(); n=w.getnframes()
    a=np.frombuffer(w.readframes(n),dtype='int16').astype(float)/32768.0
    os.unlink(p); os.unlink(wav); return a,sr
def lvl(x,sr,fc):
    X=np.abs(np.fft.rfft(x*np.hanning(len(x)))); f=np.fft.rfftfreq(len(x),1/sr)
    m=np.logical_and(f>fc*0.97, f<fc*1.03)
    return 20*np.log10(max(X[m].max(),1e-9)/X.max())
for note in [55,60,67,72]:
    a,sr=render(17,note); seg=a[int(0.4*sr):int(1.4*sr)]
    f0=440*2**((note-69)/12)
    print(note,"f0",round(f0,1), {r:round(lvl(seg,sr,f0*r)) for r in [0.25,0.5,0.75,1,1.5,2,2.5,3,4,5,6,8]})
print("--- comparison GM16 drawbar note 60 ---")
a,sr=render(16,60); seg=a[int(0.4*sr):int(1.4*sr)]
f0=261.63
print("GM16", {r:round(lvl(seg,sr,f0*r)) for r in [0.25,0.5,1,1.5,2,3,4]})
print("--- GM19 church note 60 ---")
a,sr=render(19,60); seg=a[int(0.4*sr):int(1.4*sr)]
print("GM19", {r:round(lvl(seg,sr,f0*r)) for r in [0.25,0.5,1,1.5,2,3,4]})
