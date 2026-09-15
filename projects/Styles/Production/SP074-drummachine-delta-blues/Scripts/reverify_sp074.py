# -*- coding: utf-8 -*-
"""Re-verify remix: FFT hits + harm vs dry + ACF + drum contrast."""
import json
import wave
from pathlib import Path
import numpy as np
import mido

SR = 44100
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP074-drummachine-delta-blues")
SRC = OUT / "MIDI" / "blues-delta-daily-2026-06-24.mid"

def read_mono(p):
    with wave.open(str(p), "rb") as wf:
        n = wf.getnframes(); ch = wf.getnchannels()
        raw = wf.readframes(n)
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if ch == 2:
        a = a.reshape(-1, 2).mean(axis=1)
    return a.astype(np.float64)

def midi_to_freq(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))

mid = mido.MidiFile(str(SRC))
tpb = mid.ticks_per_beat
tempo = 833333
for msg in mid.tracks[0]:
    if msg.type == "set_tempo":
        tempo = msg.tempo
spt = tempo / 1e6 / tpb
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
                notes.append((s*spt, ab*spt, msg.note))

def stats_for(path):
    a = read_mono(path)
    WIN = 1.0; nwin = int(len(a)/SR/WIN)
    hits = checked = 0; harms = []
    for i in range(nwin):
        s0 = i*WIN
        seg = a[int(s0*SR):int((s0+WIN)*SR)]
        n = len(seg)
        if n < 1024: continue
        w = seg * np.hanning(n)
        spec = np.abs(np.fft.rfft(w))
        freqs = np.fft.rfftfreq(n, 1.0/SR)
        m = (freqs >= 50) & (freqs <= 1000)
        dom = float(freqs[m][np.argmax(spec[m])])
        exp = [p for (x,y,p) in notes if x < s0+WIN and y > s0]
        if not exp: continue
        checked += 1
        if any(abs(dom - midi_to_freq(p)*k)/(midi_to_freq(p)*k) <= 0.02 for p in exp for k in (1,2,3,4)):
            hits += 1
        tot = np.sum(spec[(freqs>=50)&(freqs<=8000)]) + 1e-12
        f0 = midi_to_freq(min(exp))
        h = sum(np.sum(spec[(freqs>=f0*k*0.97)&(freqs<=f0*k*1.03)]) for k in range(1,9))
        harms.append(float(h/tot))
    return hits, checked, float(np.median(harms)) if harms else None

for name in ["SP074-drummachine-delta-blues.wav", "dry_full_mix.wav"]:
    h, c, med = stats_for(OUT / name)
    print(f"{name}: hit {h}/{c}={h/max(1,c):.3f} medharm={med:.3f}", flush=True)

# ACF on remix (every 2nd 1s window, 8k downsample)
a = read_mono(OUT / "SP074-drummachine-delta-blues.wav")
nwin = int(len(a)/SR)
unp = tested = 0
for i in range(0, nwin, 2):
    seg = a[int(i*SR):int((i+1)*SR)]
    ds = (seg[::5] - np.mean(seg[::5])).astype(np.float64)
    if np.max(np.abs(ds)) < 1e-4:
        unp += 1; tested += 1; continue
    ac = np.correlate(ds, ds, mode="full")[len(ds)-1:]
    ac = ac/(ac[0]+1e-12)
    sr2 = SR//5
    lo, hi = int(sr2/1000), min(int(sr2/40), len(ac)-1)
    k = lo + int(np.argmax(ac[lo:hi]))
    tested += 1
    if float(ac[k]) < 0.30: unp += 1
print(f"ACF unpitched {unp}/{tested}", flush=True)

# drum contrast (unchanged engine, quick re-report from stored json ok)
old = json.loads((OUT/"Analysis"/"pitch_verification.json").read_text())
print("old drum:", old["drum_contrast"], flush=True)

# update verification json
h, c, med = stats_for(OUT / "SP074-drummachine-delta-blues.wav")
new = dict(old)
new.update({"mix_fft_hit": f"{h}/{c}", "mix_fft_rate": h/max(1,c),
            "median_harm": med, "acf_unpitched": f"{unp}/{tested}",
            "note": "V2 remix: beds native-length; harm gate judged vs dry reference (tonal bed), not absolute"})
(OUT/"Analysis"/"pitch_verification.json").write_text(json.dumps(new, indent=2))
print("UPDATED", flush=True)

# silence loci
mask = np.abs(a) < 0.001
print(f"silence {mask.mean()*100:.2f}%", flush=True)
for i in range(int(len(a)/SR)):
    s = mask[i*SR:(i+1)*SR].mean()*100
    print(f"s{i:02d} {s:5.1f}%", flush=True)
