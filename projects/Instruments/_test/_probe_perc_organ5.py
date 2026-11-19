import sys, os, subprocess, tempfile, numpy as np, wave
sys.path.insert(0,'/opt/data/projects/Instruments')
from mido import Message, MidiFile, MidiTrack
from sound.render.fluidsynth import discover_soundfont
from scipy.signal import butter, sosfiltfilt
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
def acf(x,sr,lo,hi):
    x=x-x.mean(); c=np.correlate(x,x,'full')[len(x)-1:]
    a,b=int(sr/hi),int(sr/lo); lag=a+np.argmax(c[a:b]); return sr/lag
for pgm in (16,17,18,19):
    a,sr=render(pgm,60); seg=a[int(0.4*sr):int(1.4*sr)]
    sos=butter(6,400,'low',fs=sr,output='sos'); lp=sosfiltfilt(sos,seg)
    print(f"pgm{pgm} note60: acf_lp400={acf(lp,sr,30,400):.1f}Hz  energy<100Hz={np.sum(np.abs(np.fft.rfft(lp))**2)/np.sum(np.abs(np.fft.rfft(seg))**2):.3f}")
print("piano ref"); a,sr=render(0,60); seg=a[int(0.4*sr):int(1.4*sr)]; print("acf raw", acf(seg,sr,60,1000))
