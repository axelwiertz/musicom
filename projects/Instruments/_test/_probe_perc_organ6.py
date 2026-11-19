import sys, os, subprocess, tempfile, numpy as np, wave
sys.path.insert(0,'/opt/data/projects/Instruments')
from mido import Message, MidiFile, MidiTrack
from sound.render.fluidsynth import discover_soundfont
SF2=discover_soundfont(); FS="/opt/data/micromamba/envs/musicom/bin/fluidsynth"
def render(pgm,note,vel=100,dur=3.0):
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
for pgm in (16,17,18):
    a,sr=render(pgm,60)
    print(f"=== pgm {pgm} note60 ===")
    for ms in [0,5,10,20,40,60,100,150,250,400,700,1000,1500,2000,2500]:
        i=int(ms/1000*sr); seg=a[i:i+int(0.02*sr)]
        print(f"  {ms:5d}ms peak={np.max(np.abs(seg)):.4f} rms={np.sqrt(np.mean(seg**2)):.4f}")
