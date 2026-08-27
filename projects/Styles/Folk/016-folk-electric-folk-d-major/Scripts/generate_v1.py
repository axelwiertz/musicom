#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, random, subprocess
from pathlib import Path

OUT = Path('/tmp/hermes/songs/electric_folk_d_major_130')
OUT.mkdir(parents=True, exist_ok=True)
base = OUT/'electric_folk_d_major_130'
mid_path = str(base.with_suffix('.mid'))
wav_path = str(base.with_suffix('.wav'))
ogg_path = str(base.with_suffix('.ogg'))
readme_path = str(OUT/'README.txt')
TPB=480; BPM=130; BARS=32; PPQ=TPB
random.seed(42)
import mido
mid = mido.MidiFile(type=1, ticks_per_beat=PPQ)

def add_track(name, program=None, channel=0):
    tr=mido.MidiTrack(); mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if program is not None:
        tr.append(mido.Message('program_change', program=program, channel=channel, time=0))
    return tr

def note_events(track, events, channel=0):
    msgs=[]
    for st,dur,p,v in events:
        msgs.append((int(st),0,mido.Message('note_on', note=int(p), velocity=int(max(1,min(127,v))), channel=channel, time=0)))
        msgs.append((int(st+dur),1,mido.Message('note_off', note=int(p), velocity=0, channel=channel, time=0)))
    msgs.sort(key=lambda x:(x[0],x[1])); last=0
    for t,_,msg in msgs:
        msg.time=max(0,t-last); track.append(msg); last=t

def human(t, amt=10): return int(t + random.randint(-amt, amt))
def vel(base, spread=8): return max(1,min(127,base+random.randint(-spread,spread)))

meta=add_track('Tempo / Form')
meta.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM), time=0))
meta.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
meta.append(mido.MetaMessage('marker', text='Electric folk, D major, 130 BPM, no slow sections', time=0))

ac_gtr=add_track('Driving acoustic rhythm guitar',25,0)
el_gtr=add_track('Electric guitar melodic lines',29,1)
fiddle=add_track('Prominent fiddle',40,2)
bass=add_track('Electric bass',33,3)
vocal=add_track('Lead vocal guide - clear powerful delivery',53,4)
drums=add_track('Live drums strong backbeat',None,9)

progressions=[]
for b in range(BARS):
    if 16 <= b < 24:
        chords=[('Em',[52,55,59]),('G',[55,59,62]),('D',[50,54,57]),('A',[45,52,57])]
        name,chord=chords[(b-16)%4]
    else:
        chords=[('D',[50,54,57]),('A',[45,52,57]),('Bm',[47,54,59]),('G',[43,50,55])]
        name,chord=chords[b%4]
    progressions.append((name,chord))

ac=[]
for b,(name,ch) in enumerate(progressions):
    bar=b*4*PPQ; voicing=[n+12 for n in ch]+[ch[0]+24]
    for i in range(8):
        st=bar+i*(PPQ//2); dur=int(PPQ*0.42); accent=102 if i in (2,6) else (88 if i%2==0 else 78)
        if i%2==0: ac.append((human(st,6), int(PPQ*0.30), ch[0]+12, vel(82,5)))
        for j,n in enumerate(voicing): ac.append((human(st+j*7,7), dur, n, vel(accent-8+j*2,6)))

ba=[]
for b,(name,ch) in enumerate(progressions):
    bar=b*4*PPQ; root=ch[0]; fifth=ch[2]
    pattern=[root,root,fifth,root, root,root+12,fifth,root]
    for i,p in enumerate(pattern):
        st=bar+i*(PPQ//2)
        if i==7 and b%4 in (1,3): st += PPQ//8
        ba.append((human(st,5), int(PPQ*0.46), p, vel(96 if i in (0,4) else 83,6)))

Dr=[]; kick=36; snare=38; hat=42; openhat=46; crash=49; tom1=45; tom2=47
for b in range(BARS):
    bar=b*4*PPQ
    if b in (0,8,16,24): Dr.append((bar, PPQ//8, crash, 112))
    for i in range(8):
        st=bar+i*(PPQ//2); Dr.append((human(st,4), PPQ//8, openhat if i==7 and b%4==3 else hat, vel(74 if i%2 else 84,6)))
    for beat in [0,2,2.5]: Dr.append((human(bar+int(beat*PPQ),5), PPQ//8, kick, vel(103,7)))
    for beat in [1,3]: Dr.append((human(bar+int(beat*PPQ),4), PPQ//8, snare, vel(115,6)))
    if b%8==7:
        for k,p in enumerate([snare,tom2,tom1,snare,tom2,tom1,snare,crash]): Dr.append((bar+int((3+k/4)*PPQ), PPQ//8, p, vel(95+k*3,5)))

el=[]; hook=[62,66,69,71,69,66,64,62,69,71,74,76,74,71,69,66]; rhythm=[0,0.5,1.0,1.5,2.25,2.75,3.25,3.5]
for b in range(BARS):
    bar=b*4*PPQ
    if b%4 in (0,2):
        for i,bt in enumerate(rhythm):
            p=hook[(i+b)%len(hook)] + (12 if b>=24 else 0); dur=PPQ//3 if i not in (3,7) else PPQ//2
            el.append((human(bar+int(bt*PPQ),8), dur, p, vel(98 if i in (3,7) else 87,7)))
    else:
        for bt,p in [(0.75,74),(1.0,76),(2.75,74),(3.0,71),(3.5,69)]: el.append((human(bar+int(bt*PPQ),8), PPQ//3, p, vel(88,7)))

fid=[]; fid_base=[74,76,78,81,78,76,74,71,74,76,78,81,83,81,78,76]
for b in range(BARS):
    bar=b*4*PPQ; active=b<8 or b>=16
    if active:
        for i in range(16):
            p=fid_base[(i+b*2)%len(fid_base)]
            if b>=24: p += 12 if i in (8,12,14) else 0
            if not (i in (6,13) and b%4==1): fid.append((human(bar+i*(PPQ//4),7), int(PPQ*0.22), p, vel(94 if i in (0,4,8,12) else 79,9)))
    else:
        for bt,pair in [(0.5,[74,78]),(1.5,[76,81]),(2.5,[74,78]),(3.5,[71,76])]:
            for p in pair: fid.append((human(bar+int(bt*PPQ),6), PPQ//3, p, vel(82,6)))

voc=[]; phrase=[66,69,71,74,71,69,66,64,62,64,66,69,71,69,66,62]
for b in range(4,16):
    bar=b*4*PPQ
    for i,bt in enumerate([0,0.75,1.5,2.0,2.75,3.25]):
        p=phrase[(i+(b-4)*2)%len(phrase)]; dur=int(PPQ*(0.55 if i not in (2,5) else 0.75))
        voc.append((human(bar+int(bt*PPQ),5), dur, p, vel(101 if i in (2,5) else 91,5)))
for b in range(24,32):
    bar=b*4*PPQ
    for i,bt in enumerate([0,0.5,1.0,1.5,2.25,2.75,3.25]):
        p=[74,76,78,81,78,76,74][i]
        voc.append((human(bar+int(bt*PPQ),5), int(PPQ*0.42), p, vel(105 if i in (3,6) else 93,5)))

note_events(ac_gtr,ac,0); note_events(el_gtr,el,1); note_events(fiddle,fid,2); note_events(bass,ba,3); note_events(vocal,voc,4); note_events(drums,Dr,9)
mid.save(mid_path)

sf2_candidates=['/usr/share/sounds/sf2/FluidR3_GM.sf2','/usr/share/soundfonts/FluidR3_GM.sf2','/opt/data/soundfonts/FluidR3_GM.sf2']
sf2=next((p for p in sf2_candidates if os.path.exists(p)), None)
fs=subprocess.run(['bash','-lc','command -v fluidsynth || true'],capture_output=True,text=True).stdout.strip()
if fs and sf2:
    subprocess.run([fs,'-ni',sf2,mid_path,'-F',wav_path,'-r','44100'],check=True)
else:
    import pretty_midi, numpy as np, soundfile as sf
    pm=pretty_midi.PrettyMIDI(mid_path); audio=pm.synthesize(fs=44100)
    audio=np.tanh(audio*1.5); peak=np.max(np.abs(audio)) if len(audio) else 1
    if peak>0: audio=audio*(10**(-1/20))/peak
    sf.write(wav_path,audio.astype('float32'),44100)
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',wav_path,'-codec:a','libopus','-application','voip','-b:a','64k',ogg_path],check=True)
readme = f"""Electric Folk - D Major - 130 BPM

Brief:
- Key: D major
- Tempo: 130 BPM
- Meter: 4/4, 32 bars
- Energy: continuous drive, no slow/introspective sections
- Band: acoustic rhythm guitar, electric melodic guitar, prominent fiddle, electric bass, live drums, single lead vocal guide

Harmony DNA:
- Main: I-V-vi-IV = D-A-Bm-G
- Lift: ii-IV-I-V = Em-G-D-A

Rhythm DNA:
KICK  █░░░█░█░
SNARE ░░█░░░█░
HAT   █░█░█░█░
- Acoustic guitar: 8th-note boom-chuck, accents on 2 and 4
- Drums: kick drives 1/3/push, snare hard backbeat on 2/4
- Bass: root/fifth 8ths locked to kick

Pitch DNA:
- Electric guitar: D major pentatonic hook with octave lift in final section
- Fiddle: reel-like 16th-note runs, call-response against guitar/vocal
- Vocal guide: single clear lead contour, strong chorus high register
"""
Path(readme_path).write_text(readme, encoding='utf-8')
print(mid_path); print(ogg_path); print(wav_path); print(readme_path)
