#!/usr/bin/env python3
"""Refine Study 03 motif: stable input pitch becomes b7 anchor + blues-rock answer."""
from pathlib import Path
import json, subprocess, math
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo

ROOT=Path('/opt/data/projects/014-rock-apprenticeship')
AN=ROOT/'Analysis/voice-motif'
MIDI_DIR=ROOT/'MIDI'; AUDIO_DIR=ROOT/'Audio'
TITLE='study-03-voice-derived-motif'
MIDI_PATH=MIDI_DIR/f'{TITLE}.mid'; RAW=AUDIO_DIR/f'{TITLE}-raw.wav'; WAV=AUDIO_DIR/f'{TITLE}.wav'; OGG=AUDIO_DIR/f'{TITLE}.ogg'
SF2='/usr/share/sounds/sf2/FluidR3_GM.sf2'
features=json.loads((AN/'voice_motif_analysis.json').read_text())
BPM=108; TPB=480
# Source was stable around MIDI 74 = D5. Treat as b7 in E blues.
# Preserve attack counts, then compose answer in E blues.
source_notes=[74,74,74,74]          # D5 repeated = input DNA
answer=[71,70,69,67,64]             # B4 Bb4 A4 G4 E4 = blues answer/resolution
lead_notes=source_notes+answer
# Rhythm from detected IOI mapped to compact 4-bar hook.
durs=[TPB//2, TPB//2, TPB, TPB//2, TPB//2, TPB//2, TPB//2, TPB, TPB]
starts=[]; t=TPB//2
for d in durs[:len(lead_notes)]:
    starts.append(t); t += d

def add(ev,t,d,p,v,ch):
    ev.append((t,Message('note_on',note=p,velocity=v,channel=ch,time=0)))
    ev.append((t+d,Message('note_off',note=p,velocity=0,channel=ch,time=0)))
def chord(ev,t,d,ps,v,ch):
    for p in ps: add(ev,t,d,p,v,ch)
def track(ev,name,program=None,ch=0):
    tr=MidiTrack(); tr.append(MetaMessage('track_name',name=name,time=0))
    if program is not None: tr.append(Message('program_change',program=program,channel=ch,time=0))
    last=0
    for tt,msg in sorted(ev,key=lambda x:(x[0],0 if x[1].type=='note_off' else 1)):
        msg.time=max(0,tt-last); tr.append(msg); last=tt
    tr.append(MetaMessage('end_of_track',time=1)); return tr
lead=[]; guitar=[]; bass=[]; drums=[]
vel=[92,86,104,88,92,100,96,90,112]
for s,d,p,v in zip(starts,durs,lead_notes,vel): add(lead,s,max(60,d-24),p,v,2)
# 4-bar E blues bed.
roots=[40,40,45,40]
for bar,r in enumerate(roots):
    b=bar*TPB*4
    chord(guitar,b,TPB*2,[r+12,r+19,r+22],78,0) # root 5 b7
    chord(guitar,b+TPB*2,TPB*2,[r+12,r+19,r+21],70,0) # grind to 6
    pat=[0,7,10,7,0,7,9,10]
    for i,off in enumerate(range(0,TPB*4,TPB//2)): add(bass,b+off,TPB//2-20,r+pat[i],96,1)
    for beat in range(4):
        bt=b+beat*TPB
        add(drums,bt,50,42,48,9); add(drums,bt+TPB*2//3,50,42,42,9)
        if beat in [0,2]: add(drums,bt,70,36,102,9)
        if beat in [1,3]: add(drums,bt,80,38,112,9)
# add final E stab
chord(guitar,4*TPB*4,TPB*2,[52,59,64],96,0); add(bass,4*TPB*4,TPB*2,40,110,1); chord(lead,4*TPB*4,TPB,[64,76],104,2)
mid=MidiFile(ticks_per_beat=TPB)
meta=MidiTrack(); meta.append(MetaMessage('track_name',name='014 Study 03 Voice-Derived Motif Refined',time=0)); meta.append(MetaMessage('set_tempo',tempo=bpm2tempo(BPM),time=0)); meta.append(MetaMessage('time_signature',numerator=4,denominator=4,time=0)); meta.append(MetaMessage('text',text='Input sound stable near D5. D becomes b7 anchor in E blues; answer resolves B-Bb-A-G-E.',time=0)); meta.append(MetaMessage('end_of_track',time=1)); mid.tracks.append(meta)
mid.tracks += [track(guitar,'E blues rhythm guitar',29,0), track(bass,'Boogie bass',33,1), track(lead,'Voice-derived lead: D anchor to E resolve',30,2), track(drums,'Shuffle drums',None,9)]
mid.save(MIDI_PATH)
subprocess.run(['fluidsynth','-ni',SF2,str(MIDI_PATH),'-F',str(RAW),'-r','44100'],check=True)
subprocess.run(['ffmpeg','-y','-i',str(RAW),'-af','volume=0.95,alimiter=limit=0.95',str(WAV)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
subprocess.run(['ffmpeg','-y','-i',str(WAV),'-codec:a','libopus','-application','voip','-b:a','64k',str(OGG)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try: RAW.unlink()
except FileNotFoundError: pass
(AN/'voice_motif_composition.md').write_text(f'''# Voice-Derived Motif Composition\n\nInput analysis: stable voiced pitch around MIDI 74 = D5 (~590 Hz).\n\nComposition choice: in E blues, D = b7. Use it as a hook anchor, then answer down through blues scale.\n\n```text\nInput DNA: D5 D5 D5 D5\nMotif:     D5 D5 D5 D5 | B4 Bb4 A4 G4 E4\nFunction:  b7 anchor   | 5  b5  4  b3 1\n```\n\nRhythm: detected voice attacks compressed into 4-bar blues-rock hook at {BPM} BPM.\n\nFiles:\n- MIDI: `{MIDI_PATH}`\n- OGG: `{OGG}`\n''')
print(MIDI_PATH); print(OGG)
