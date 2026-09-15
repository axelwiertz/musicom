# -*- coding: utf-8 -*-
"""Fast verification for SP074 (downsampled ACF, vectorized)."""
import json
import wave
from pathlib import Path
import numpy as np
import mido

SR = 44100
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP074-drummachine-delta-blues")
SRC = OUT / "MIDI" / "blues-delta-daily-2026-06-24.mid"
FINAL = OUT / "SP074-drummachine-delta-blues.wav"
STEM_BULL = OUT / "Audio" / "stems_processed" / "track04_Drums_BULLFROG.wav"

def read_wav_mono(p, max_s=None):
    with wave.open(str(p), "rb") as wf:
        n = wf.getnframes()
        ch = wf.getnchannels()
        if max_s:
            n = min(n, int(max_s * wf.getframerate()))
        raw = wf.readframes(n)
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if ch == 2:
        a = a.reshape(-1, 2).mean(axis=1)
    return a

def midi_to_freq(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))

mid = mido.MidiFile(str(SRC))
tpb = mid.ticks_per_beat
tempo = 833333
for msg in mid.tracks[0]:
    if msg.type == "set_tempo":
        tempo = msg.tempo
sec_per_tick = tempo / 1e6 / tpb
notes = []
for ti, track in enumerate(mid.tracks):
    abstick = 0
    active = {}
    for msg in track:
        abstick += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            c = msg.channel if hasattr(msg, "channel") else -1
            if c == 9:
                continue
            active[msg.note] = abstick
        elif msg.type in ("note_off",) or (msg.type == "note_on" and msg.velocity == 0):
            if msg.note in active:
                s = active.pop(msg.note)
                notes.append((s * sec_per_tick, abstick * sec_per_tick, msg.note))
print(f"pitched notes={len(notes)}", flush=True)

audio = read_wav_mono(FINAL)
dur = len(audio) / SR
print(f"final dur={dur:.2f}s peak={np.max(np.abs(audio)):.4f}", flush=True)
silent = float(np.sum(np.abs(audio) < 0.001) / len(audio))
print(f"silence={silent*100:.2f}%", flush=True)
rms_s = []
for i in range(int(dur)):
    seg = audio[i*SR:(i+1)*SR]
    rms_s.append(float(np.sqrt(np.mean(seg.astype(np.float64)**2))) if len(seg) else 0.0)
print("RMS/s: " + " ".join(f"{v:.3f}" for v in rms_s), flush=True)

# FFT dom peak per 1.0s window (fewer, faster windows), vectorized rfft
WIN = 1.0
nwin = int(dur / WIN)
hits = checked = 0
harms = []
for i in range(nwin):
    s0 = i * WIN
    seg = audio[int(s0*SR):int((s0+WIN)*SR)].astype(np.float64)
    n = len(seg)
    w = seg * np.hanning(n)
    spec = np.abs(np.fft.rfft(w))
    freqs = np.fft.rfftfreq(n, 1.0/SR)
    m = (freqs >= 50) & (freqs <= 1000)
    dom = float(freqs[m][np.argmax(spec[m])])
    exp = [p for (a, b, p) in notes if a < s0 + WIN and b > s0]
    if not exp:
        continue
    checked += 1
    f0min = midi_to_freq(min(exp))
    # hit vs any expected f0 x1-4
    ok = any(abs(dom - midi_to_freq(p)*k)/(midi_to_freq(p)*k) <= 0.02 for p in exp for k in (1,2,3,4))
    hits += ok
    tot = np.sum(spec[(freqs>=50)&(freqs<=8000)]) + 1e-12
    h = sum(np.sum(spec[(freqs>=f0min*k*0.97)&(freqs<=f0min*k*1.03)]) for k in range(1,9))
    harms.append(float(h/tot))
print(f"mix FFT hit {hits}/{checked} = {hits/max(1,checked):.4f}", flush=True)
print(f"median harm={float(np.median(harms)):.3f}" if harms else "no harm", flush=True)

# ACF only on every 4th window (speed), downsampled to 8k
unpitched = tested = 0
for i in range(0, nwin, 2):
    seg = audio[int(i*WIN*SR):int((i+WIN)*SR)].astype(np.float64)
    ds = seg[::5]  # ~8820 Hz
    sr2 = SR // 5
    ds = ds - np.mean(ds)
    if np.max(np.abs(ds)) < 1e-4:
        unpitched += 1; tested += 1; continue
    ac = np.correlate(ds, ds, mode="full")[len(ds)-1:]
    ac = ac / (ac[0] + 1e-12)
    lo, hi = int(sr2/1000), int(sr2/40)
    hi = min(hi, len(ac)-1)
    k = lo + int(np.argmax(ac[lo:hi]))
    conf = float(ac[k])
    tested += 1
    if conf < 0.30:
        unpitched += 1
print(f"ACF unpitched {unpitched}/{tested} (every-2nd 1s window)", flush=True)

# drum onset contrast on bullfrog stem (fast cumsum RMS)
bull = read_wav_mono(STEM_BULL).astype(np.float64)
W = int(0.01*SR)
c = np.cumsum(np.concatenate([[0.0], bull**2]))
env = np.sqrt((c[W:] - c[:-W]) / W)
env = np.concatenate([np.zeros(W//2), env])[:len(bull)]
dh = []
for track in mid.tracks:
    abstick = 0
    for msg in track:
        abstick += msg.time
        if msg.type == "note_on" and msg.velocity > 0 and hasattr(msg, "channel") and msg.channel == 9:
            dh.append((abstick*sec_per_tick, msg.note))
dh.sort()
okc = 0
L = len(env)
for (t, n_) in dh:
    i = int(t*SR)
    if i >= L:
        continue
    v = env[i]
    a0, a1 = max(0,int((t-0.3)*SR)), max(0,int((t-0.06)*SR))
    b0, b1 = min(L,int((t+0.06)*SR)), min(L,int((t+0.3)*SR))
    parts = []
    if a1 > a0: parts.append(env[a0:a1])
    if b1 > b0: parts.append(env[b0:b1])
    base = float(np.median(np.concatenate(parts))) if parts else 1e-9
    if v > 2.0*max(base, 1e-4):
        okc += 1
print(f"drum contrast {okc}/{len(dh)} = {okc/len(dh):.3f}", flush=True)

res = {"dur_s": dur, "peak": float(np.max(np.abs(audio))), "silence_pct": silent*100,
       "rms_per_s": rms_s, "mix_fft_hit": f"{hits}/{checked}",
       "mix_fft_rate": hits/max(1,checked), "median_harm": float(np.median(harms)) if harms else None,
       "acf_unpitched": f"{unpitched}/{tested}", "drum_contrast": f"{okc}/{len(dh)}",
       "drum_rate": okc/len(dh)}
(OUT/"Analysis"/"pitch_verification.json").write_text(json.dumps(res, indent=2))
print("WROTE pitch_verification.json", flush=True)

BAR = 1920; NB = 12
names = ["Lead Slide", "Rhythm Harm", "Bass", "Drums(BF)"]
occ = {0:set(),1:set(),2:set(),3:set()}
vmap = {"Resonator":0,"Acoustic Rhythm":1,"Fingerstyle":2,"Stomp":3}
for ti, track in enumerate(mid.tracks):
    if ti == 0: continue
    vi = next((v for k,v in vmap.items() if k in track.name), None)
    if vi is None: continue
    abstick = 0
    for msg in track:
        abstick += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            occ[vi].add(abstick // BAR)
lines = ["="*70, "SP-074 DRUM-MACHINE DELTA BLUES - BAR GRID (12 bars, 72 BPM)", "="*70]
for vi, nm in enumerate(names):
    row = "".join("█" if b in occ[vi] else "░" for b in range(NB))
    lines.append(f"{nm:<14}: {row}  (bars {len(occ[vi])}/{NB})")
lines += ["-"*70, "Legend: █ = Sounding | ░ = Rest",
          "Drums row: Bullfrog X0X replaces GM kit 1:1 on source onsets (swing 0.55)."]
(OUT/"Analysis"/"grid_visualization.txt").write_text("\n".join(lines)+"\n")
print("\n".join(lines), flush=True)
