# -*- coding: utf-8 -*-
"""Generate Project 014 Exercise 1: Balfolk vs Jazz vs Hybrid.
Minimal stack: mido + fluidsynth CLI + ffmpeg.
"""
from pathlib import Path
import math
import subprocess
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo

ROOT = Path('/opt/data/projects/014-genre-pattern-matrix')
MIDI = ROOT / 'MIDI'
RENDERS = ROOT / 'Renders'
AUDIO = ROOT / 'Audio'
ANALYSIS = ROOT / 'Analysis'
for d in [MIDI, RENDERS, AUDIO, ANALYSIS, ROOT/'Notes', ROOT/'Exercises', ROOT/'Scripts']:
    d.mkdir(parents=True, exist_ok=True)

TPB = 480
SF2 = '/usr/share/sounds/sf2/FluidR3_GM.sf2'

# ---------- MIDI helpers ----------
def add_track(score, name, channel, program=None):
    tr = MidiTrack()
    score.tracks.append(tr)
    tr.append(MetaMessage('track_name', name=name, time=0))
    if program is not None and channel != 9:
        tr.append(Message('program_change', channel=channel, program=program, time=0))
    return tr

def add_note(track, channel, note, start, dur, vel=90):
    # store absolute events for later conversion
    track._events.append((start, Message('note_on', channel=channel, note=note, velocity=vel, time=0)))
    track._events.append((start+dur, Message('note_off', channel=channel, note=note, velocity=0, time=0)))

def add_chord(track, channel, notes, start, dur, vel=75):
    for n in notes:
        add_note(track, channel, n, start, dur, vel)

def finalize_track(track):
    events = sorted(track._events, key=lambda x: (x[0], 0 if x[1].type=='note_off' else 1))
    last = 0
    for t, msg in events:
        msg.time = max(0, int(t-last))
        track.append(msg)
        last = t
    delattr(track, '_events')

def make_score(title, tempo_bpm, time_sig):
    mid = MidiFile(ticks_per_beat=TPB)
    meta = MidiTrack()
    mid.tracks.append(meta)
    meta.append(MetaMessage('track_name', name=title, time=0))
    meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(tempo_bpm), time=0))
    meta.append(MetaMessage('time_signature', numerator=time_sig[0], denominator=time_sig[1], time=0))
    return mid

def render(mid_path):
    wav = RENDERS / (mid_path.stem + '.wav')
    ogg = AUDIO / (mid_path.stem + '.ogg')
    subprocess.run(['fluidsynth','-ni',SF2,str(mid_path),'-F',str(wav),'-r','44100'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(wav),'-af','volume=0.9','-codec:a','libopus','-application','voip','-b:a','64k',str(ogg)], check=True)
    return wav, ogg

# ---------- note maps ----------
D4,E4,F4,G4,A4,B4,C5,D5 = 62,64,65,67,69,71,72,74
C4,Db4,Eb4,F4n,G4n,Ab4,Bb4 = 60,61,63,65,67,68,70

# ---------- Exercise A: Balfolk ----------
def balfolk():
    # 6/8 dotted-quarter 95 => quarter BPM 142.5
    mid = make_score('Exercise 1A Balfolk Dorian Jig', 142.5, (6,8))
    lead = add_track(mid, 'Fiddle Lead - D Dorian', 0, 40); lead._events=[]
    acc = add_track(mid, 'Accordion/Guitar Chords', 1, 21); acc._events=[]
    bass = add_track(mid, 'Bass Drone', 2, 32); bass._events=[]
    perc = add_track(mid, 'Foot Pulse', 9); perc._events=[]
    eighth = TPB//2
    bar = 6*eighth
    chords = [
        [50,57,62,65], [48,55,60,64], [50,57,62,65], [43,50,55,59],
        [50,57,62,65], [48,55,60,64], [43,50,55,59], [50,57,62,65],
    ]
    roots = [38,36,38,43,38,36,43,38]
    # Folk-simple Dorian motif, accented on 1 and 4.
    bars_notes = [
        [D4,E4,F4,A4,G4,F4], [E4,F4,G4,C5,B4,A4], [D4,F4,E4,A4,G4,F4], [G4,A4,B4,A4,G4,E4],
        [D4,E4,F4,A4,G4,F4], [E4,F4,G4,C5,B4,A4], [G4,A4,B4,D5,C5,A4], [F4,E4,D4,A4,F4,D4],
    ]
    for i in range(8):
        s=i*bar
        # chord pulses on 1 and 4
        add_chord(acc,1,chords[i],s,eighth*2,70)
        add_chord(acc,1,chords[i],s+3*eighth,eighth*2,64)
        add_note(bass,2,roots[i],s,bar,72)
        for k,n in enumerate(bars_notes[i]):
            vel = 108 if k in [0,3] else 82
            add_note(lead,0,n,s+k*eighth,eighth*0.92,vel)
        # foot pulse: low drum on 1 and 4
        add_note(perc,9,36,s,eighth//2,90)
        add_note(perc,9,36,s+3*eighth,eighth//2,72)
    for tr in [lead,acc,bass,perc]: finalize_track(tr)
    out=MIDI/'exercise1a_balfolk_dorian_jig.mid'
    mid.save(out)
    return out

# ---------- Exercise B: Jazz ----------
def jazz():
    mid = make_score('Exercise 1B Jazz ii-V-I Swing', 120, (4,4))
    sax = add_track(mid, 'Sax Lead - chord tone targets', 0, 65); sax._events=[]
    piano = add_track(mid, 'Piano Comping', 1, 0); piano._events=[]
    bass = add_track(mid, 'Walking Bass', 2, 32); bass._events=[]
    drums = add_track(mid, 'Ride and Backbeat', 9); drums._events=[]
    q=TPB; bar=4*q
    # Dm7 G7 Cmaj7 Cmaj7 Em7 A7 Dm7-G7 Cmaj7
    chords = [
        [50,57,60,65], [43,53,59,65], [48,55,59,64], [48,55,59,64],
        [52,59,62,67], [45,55,61,67], None, [48,55,59,64]
    ]
    roots = [[50,53,57,60],[43,47,50,53],[48,52,55,59],[48,52,55,59],[52,55,59,62],[45,49,52,55],[50,53,57,59],[48,52,55,60]]
    # swing: long 8th = 2/3 beat, short = 1/3 beat
    long=int(q*2/3); short=q-long
    melodies = [
        [62,65,69,72,71,69], [65,67,71,74,72,71], [64,67,71,76,74,72], [67,64,62,60],
        [64,67,71,74,72,71], [61,64,67,73,72,69], [65,69,72,71,67,65], [64,62,60,55]
    ]
    for i in range(8):
        s=i*bar
        # walking bass quarters
        for k,n in enumerate(roots[i]): add_note(bass,2,n,s+k*q,q*0.9,78)
        # ride every quarter, snare/hat 2+4
        for k in range(4): add_note(drums,9,51,s+k*q,q//4,55)
        add_note(drums,9,38,s+q,q//4,68); add_note(drums,9,38,s+3*q,q//4,68)
        # comp chords on 2 and 4; bar 7 split ii-V
        if i==6:
            add_chord(piano,1,[50,57,60,65],s+q,q,64)
            add_chord(piano,1,[43,53,59,65],s+3*q,q,64)
        else:
            add_chord(piano,1,chords[i],s+q,q,64)
            add_chord(piano,1,chords[i],s+3*q,q,60)
        # melody swing pairs, target first notes on chord tones
        t=s
        for j,n in enumerate(melodies[i]):
            dur = long if j%2==0 else short
            add_note(sax,0,n,t,dur*0.95,92 if j in [0,2,4] else 78)
            t += dur
            if t >= s+bar: break
    for tr in [sax,piano,bass,drums]: finalize_track(tr)
    out=MIDI/'exercise1b_jazz_ii_v_i_swing.mid'
    mid.save(out)
    return out

# ---------- Exercise C: Hybrid ----------
def hybrid():
    mid = make_score('Exercise 1C Hybrid Balfolk Jazz Dorian 9ths', 142.5, (6,8))
    fiddle = add_track(mid, 'Fiddle Folk Lead', 0, 40); fiddle._events=[]
    piano = add_track(mid, 'Jazz Color Chords', 1, 0); piano._events=[]
    bass = add_track(mid, 'Modal Bass', 2, 32); bass._events=[]
    perc = add_track(mid, 'Jig Pulse', 9); perc._events=[]
    eighth=TPB//2; bar=6*eighth
    # Dm9 | Cmaj7 | Dm9 | G13, repeated
    chords = [
        [50,57,60,64,65], [48,55,59,64], [50,57,60,64,65], [43,53,57,59,64],
        [50,57,60,64,65], [48,55,59,64], [43,53,57,59,64], [50,57,60,64,65]
    ]
    roots=[38,36,38,43,38,36,43,38]
    motif = [D4,F4,E4,A4,G4,F4]
    vars = [motif, [E4,F4,G4,C5,B4,A4], motif, [G4,A4,B4,A4,G4,E4], motif, [E4,F4,G4,C5,B4,A4], [G4,A4,B4,D5,C5,A4], [F4,E4,D4,A4,F4,D4]]
    for i in range(8):
        s=i*bar
        add_chord(piano,1,chords[i],s,eighth*2,62)
        add_chord(piano,1,chords[i],s+3*eighth,eighth*2,58)
        add_note(bass,2,roots[i],s,bar,76)
        for k,n in enumerate(vars[i]):
            # folk melody unchanged; jazz color under it
            add_note(fiddle,0,n,s+k*eighth,eighth*0.94,104 if k in [0,3] else 82)
        add_note(perc,9,36,s,eighth//2,86)
        add_note(perc,9,36,s+3*eighth,eighth//2,70)
    for tr in [fiddle,piano,bass,perc]: finalize_track(tr)
    out=MIDI/'exercise1c_hybrid_balfolk_jazz.mid'
    mid.save(out)
    return out

# ---------- Combined compare file ----------
def combined(parts):
    # concatenate by putting rendered audio easier not midi merge; make simple markdown only.
    pass

if __name__ == '__main__':
    midis=[balfolk(), jazz(), hybrid()]
    rendered=[]
    for m in midis:
        rendered.append(render(m))
    # concatenate OGGs via ffmpeg concat from WAVs for easy A/B/C listening
    concat_txt = ROOT/'Renders'/'concat.txt'
    with open(concat_txt,'w') as f:
        for wav,ogg in rendered:
            f.write(f"file '{wav}'\n")
    allwav=RENDERS/'exercise1_all_three_compare.wav'
    allogg=AUDIO/'exercise1_all_three_compare.ogg'
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(concat_txt),'-c','copy',str(allwav)], check=True)
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(allwav),'-codec:a','libopus','-application','voip','-b:a','64k',str(allogg)], check=True)
    print('Generated:')
    for m in midis: print(m)
    for wav,ogg in rendered: print(ogg)
    print(allogg)
