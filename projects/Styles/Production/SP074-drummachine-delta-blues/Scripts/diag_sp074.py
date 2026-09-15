# -*- coding: utf-8 -*-
"""Diagnose harm-energy + silence loci for SP074."""
import wave
from pathlib import Path
import numpy as np
import mido

SR = 44100
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP074-drummachine-delta-blues")

def read_mono(p):
    with wave.open(str(p), "rb") as wf:
        n = wf.getnframes(); ch = wf.getnchannels()
        raw = wf.readframes(n)
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    if ch == 2:
        a = a.reshape(-1, 2).mean(axis=1)
    return a

def midi_to_freq(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))

SRC = OUT / "MIDI" / "blues-delta-daily-2026-06-24.mid"
mid = mido.MidiFile(str(SRC))
tpb = mid.ticks_per_beat
tempo = 833333
for msg in mid.tracks[0]:
    if msg.type == "set_tempo":
        tempo = msg.tempo
sec_per_tick = tempo / 1e6 / tpb
notes = []
for track in mid.tracks:
    ab = 0; act = {}
    for msg in track:
        ab += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            c = msg.channel if hasattr(msg, "channel") else -1
            if c == 9: continue
            act[msg.note] = ab
        elif msg.type in ("note_off",) or (msg.type == "note_on" and msg.velocity == 0):
            if msg.note in act:
                s = act.pop(msg.note)
                notes.append((s*sec_per_tick, ab*sec_per_tick, msg.note))

def harm(seg, f0):
    n = len(seg)
    w = seg * np.hanning(n)
    spec = np.abs(np.fft.rfft(w))
    freqs = np.fft.rfftfreq(n, 1.0/SR)
    tot = np.sum(spec[(freqs>=50)&(freqs<=8000)]) + 1e-12
    h = sum(np.sum(spec[(freqs>=f0*k*0.97)&(freqs<=f0*k*1.03)]) for k in range(1,9))
    return float(h/tot)

for name in ["SP074-drummachine-delta-blues.wav", "dry_full_mix.wav"]:
    a = read_mono(OUT / name).astype(np.float64)
    WIN = 1.0; nwin = int(len(a)/SR/WIN)
    hs = []
    for i in range(nwin):
        s0 = i*WIN
        seg = a[int(s0*SR):int((s0+WIN)*SR)]
        exp = [p for (x,y,p) in notes if x < s0+WIN and y > s0]
        if not exp: continue
        hs.append(harm(seg, midi_to_freq(min(exp))))
    print(f"{name}: median_harm={float(np.median(hs)):.3f} n={len(hs)}", flush=True)

# pitched-only sum (dry stems minus drums) - align to shortest
arrs = []
for f in sorted((OUT/"Audio"/"stems_dry").glob("*.wav")):
    if "Drum" in f.name: continue
    arrs.append(read_mono(f).astype(np.float64))
L = min(len(a) for a in arrs)
pitched = sum(a[:L] for a in arrs)
pitched = pitched / np.max(np.abs(pitched)) * 0.89
WIN = 1.0; nwin = int(len(pitched)/SR/WIN)
hs = []
for i in range(nwin):
    s0 = i*WIN
    seg = pitched[int(s0*SR):int((s0+WIN)*SR)]
    exp = [p for (x,y,p) in notes if x < s0+WIN and y > s0]
    if not exp: continue
    hs.append(harm(seg, midi_to_freq(min(exp))))
print(f"pitched-only-sum: median_harm={float(np.median(hs)):.3f}", flush=True)

# bullfrog drums alone harm (expect low - noise)
b = read_mono(OUT/"Audio"/"stems_processed"/"track04_Drums_BULLFROG.wav").astype(np.float64)
WIN = 1.0; nwin = int(len(b)/SR/WIN)
hs = []
for i in range(min(nwin, 40)):
    seg = b[int(i*WIN*SR):int((i+WIN)*SR)]
    hs.append(harm(seg, 55.0))
print(f"bullfrog-drums@55Hz harm={float(np.median(hs)):.3f} (noise ref)", flush=True)

# silence loci on final
a = read_mono(OUT / "SP074-drummachine-delta-blues.wav")
mask = np.abs(a) < 0.001
# longest silent run + where
idx = np.where(mask)[0]
print(f"silence total {mask.mean()*100:.2f}%", flush=True)
# per-second silence
for i in range(int(len(a)/SR)):
    seg = mask[i*SR:(i+1)*SR]
    print(f"s{i:02d} sil={seg.mean()*100:5.1f}%", flush=True)
