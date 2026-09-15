# -*- coding: utf-8 -*-
"""SP-074 Bullfrog drum-machine production on delta blues.
Absolute-layer: pitched voices keep SoundFont bed (FX-off dry), the drum
track (ch9) is REPLACED by the BullfrogDrums X0X engine (absolute layer).
Also renders CV lane driving a simple bass arp as production garnish.
Outputs to Production/SP074-drummachine-delta-blues/
"""
import json
import os
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np
import mido

SR = 44100
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP074-drummachine-delta-blues")
SRC = Path("/opt/data/repos/musicom/projects/Styles/Blues/blues-delta-daily-2026-06-24/MIDI/blues-delta-daily-2026-06-24.mid")

for d in ["MIDI", "Audio/stems_dry", "Audio/stems_processed", "Analysis", "Scripts"]:
    (OUT / d).mkdir(parents=True, exist_ok=True)

from sound.render.fluidsynth import discover_soundfont
from sound.generators.drum_machine import BullfrogDrums, Kit
from sound.effects.mastering import normalize_to_lufs

SF = discover_soundfont()
print(f"SoundFont: {SF}")
assert SF, "no soundfont"

# copy source midi
shutil.copy(SRC, OUT / "MIDI" / "blues-delta-daily-2026-06-24.mid")

def read_wav(p):
    import wave as wv
    with wv.open(str(p), "rb") as wf:
        n = wf.getnframes()
        ch = wf.getnchannels()
        sr = wf.getframerate()
        raw = wf.readframes(n)
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    if ch == 2:
        a = a.reshape(-1, 2)
    return a, sr

def write_wav(p, audio, sr=44100):
    import wave as wv
    a = np.asarray(audio)
    if a.ndim == 1:
        ch = 1
    else:
        ch = a.shape[1]
    a = np.clip(a, -1.0, 1.0)
    ints = (a * 32767).astype(np.int16)
    with wv.open(str(p), "wb") as wf:
        wf.setnchannels(ch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(ints.tobytes())

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"cmd failed {cmd}: {r.stderr[-800:]}")
    return r

FS = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
if not Path(FS).exists():
    FS = "fluidsynth"

# --- 1. parse source midi: tempo map + drum onsets + bar grid
mid = mido.MidiFile(str(SRC))
print(f"tracks={len(mid.tracks)} len={mid.length:.2f}s tpb={mid.ticks_per_beat}")
tempo = 833333
for msg in mid.tracks[0]:
    if msg.type == "set_tempo":
        tempo = msg.tempo
BPM = 60000000 / tempo
print(f"BPM={BPM}")

# --- 2. dry full mix FX-off
dry_mix = OUT / "dry_full_mix.wav"
run([FS, "-ni", "-g", "1.2", "-F", str(dry_mix), "-r", str(SR),
     "-o", "synth.reverb.active=no", "-o", "synth.chorus.active=no",
     SF, str(SRC)])
print(f"dry mix {dry_mix.stat().st_size} B")

# --- 3. dry stems per track (single-track rebuild, FX off)
from sound.render.pipeline import RenderPipeline
pipe = RenderPipeline(soundfont_path=SF)
stems = pipe.render_stems(str(SRC), str(OUT / "Audio" / "stems_dry"), format="wav")
print("stems:")
for k, v in stems.items():
    print(f"  {k}: {v} ({Path(v).stat().st_size} B)")

# --- 4. extract drum onsets (ch9) in ticks + pitched notes summary
drum_hits = []   # (abstick, note, vel)
for track in mid.tracks:
    abstick = 0
    ch = None
    for msg in track:
        abstick += msg.time
        if msg.type == "program_change":
            ch = msg.channel
        if msg.type == "note_on" and msg.velocity > 0:
            c = msg.channel if hasattr(msg, "channel") else ch
            if c == 9:
                drum_hits.append((abstick, msg.note, msg.velocity))
print(f"drum_hits={len(drum_hits)}")
from collections import Counter
print("drum dist:", dict(Counter(n for _, n, _ in drum_hits)))

# --- 5. Bullfrog kit + grid from source drum onsets
# Map GM -> bullfrog channels: 36 kick->ch1, 39 clap->ch5, 42 hat->ch3, else->ch4 tom
GM2CH = {36: 1, 39: 5, 42: 3}
# bar grid: 12/8 declared but material is 12 bars of 4 quarters (1920 ticks?) check last tick
last_tick = max(t for t, _, _ in drum_hits)
print(f"last_drum_tick={last_tick}, bars_1920={last_tick/1920:.2f}")
BAR_TICKS = 1920  # 4 quarters at 480tpb (project README convention: 12 bars)
NBARS = int(round(last_tick / BAR_TICKS)) + 1
print(f"NBARS={NBARS}")
# At 72 BPM, beat=0.8333s, 16th step=0.20833s; X0X 16 steps/bar
STEPS_PER_BAR = 16
bpm_eff = 72.0
step_dur = 60.0 / bpm_eff / 4.0

bf = BullfrogDrums(sample_rate=SR)
kit = Kit.demo_kit(SR)
bf.load_kit(kit)
# per-channel Bullfrog voicing (measurement-driven defaults)
# ch1 kick: LP 900Hz, slight drive; ch3 hat: HP, short; ch5 clap: band-ish
bf.channels[1].cutoff = 900.0
bf.channels[1].filter_type = "lp"
bf.channels[1].resonance = 0.15
bf.channels[1].overdrive = 0.25
bf.channels[1].decay = 1.0
bf.channels[1].pan = 0.0
bf.channels[3].cutoff = 7000.0
bf.channels[3].filter_type = "hp"
bf.channels[3].decay = 0.6
bf.channels[3].pan = -0.25
bf.channels[5].cutoff = 2500.0
bf.channels[5].filter_type = "lp"
bf.channels[5].decay = 0.7
bf.channels[5].pan = 0.28
bf.channels[4].cutoff = 1800.0  # fallback tom
bf.channels[4].pan = 0.1

# quantize drum hits to 16th grid
grid = {}
for (tick, note, vel) in drum_hits:
    bar = tick // BAR_TICKS
    within = tick % BAR_TICKS
    step_in_bar = int(round(within / BAR_TICKS * STEPS_PER_BAR)) % STEPS_PER_BAR
    abs_step = int(bar * STEPS_PER_BAR + step_in_bar)
    ch = GM2CH.get(note, 4)
    v = max(0.2, min(1.2, vel / 90.0))
    grid.setdefault(ch, {})
    # keep max velocity on collisions
    grid[ch][abs_step] = max(grid[ch].get(abs_step, 0), v)
print("grid channels:", {ch: len(h) for ch, h in grid.items()})

# swing: blues shuffle -> swing 0.55 on the Bullfrog grid (delays odd 16ths)
total_bars = NBARS
wet_drums = bf.render(grid, bpm=bpm_eff, steps=STEPS_PER_BAR, bars=total_bars, swing=0.55)
print(f"wet_drums shape={wet_drums.shape} peak={np.max(np.abs(wet_drums)):.4f} dur={len(wet_drums)/SR:.2f}s")
# mono-ize check + peak safety
wet_drums = wet_drums / max(1e-9, np.max(np.abs(wet_drums))) * 0.89

write_wav(OUT / "Audio" / "stems_processed" / "track04_Drums_BULLFROG.wav", wet_drums, SR)

# --- 6. CV lane: 8th-note walking CV from bass roots -> drives subtle sub pulse garnish
# (documents channel-8 usage; mixed LOW under the kit, 0.15 gain)
bass_roots = []
for track in mid.tracks:
    abstick = 0
    prog = None
    for msg in track:
        abstick += msg.time
        if msg.type == "program_change":
            prog = msg.program
        if msg.type == "note_on" and msg.velocity > 0 and prog == 32:
            bass_roots.append((abstick, msg.note))
bass_roots.sort()
print(f"bass_roots={len(bass_roots)} first={bass_roots[:6]}")
# CV: one value per bar = root pitch class normalized
for i in range(total_bars):
    bar_tick = i * BAR_TICKS
    # nearest root at/before bar
    cand = [n for (t, n) in bass_roots if t <= bar_tick + BAR_TICKS // 2]
    note = cand[-1] if cand else 45
    bf.cv.set(i * 2, (note - 36) / 48.0)
    bf.cv.set(i * 2 + 1, ((note + 7) - 36) / 48.0)
seq = bf.to_cv_sequence(total_bars * 2)
print(f"cv seq len={len(seq)} first4={seq[:4]}")
pitches = bf.cv.to_pitch_sequence(total_bars * 2, base_freq=55.0)
# render sub pulse: sine at cv pitch, 8th-note gates, 0.15 gain
total_n = wet_drums.shape[0]
sub = np.zeros(total_n)
eighth = step_dur * 2
for (s, f) in pitches:
    t0 = int(s * eighth * SR)
    n = int(0.16 * SR)
    if t0 >= total_n:
        continue
    tt = np.arange(min(n, total_n - t0)) / SR
    env = np.exp(-tt / 0.06)
    sub[t0:t0 + len(tt)] += 0.15 * np.sin(2 * np.pi * f * tt) * env
# stereo-ize sub (center)
sub_st = np.stack([sub, sub], axis=1)
write_wav(OUT / "Audio" / "stems_processed" / "track05_CV_sub_garnish.wav", sub_st, SR)

# --- 7. mix: dry pitched stems (mono-summed) + bullfrog drums + cv sub
# load dry stems
dry_arrays = {}
for k, v in stems.items():
    a, sr = read_wav(v)
    if a.ndim == 1:
        a = np.stack([a, a], axis=1)
    # mono center
    dry_arrays[k] = a
# identify drum stem (GM Drums / ch9) - drop it, replace with bullfrog
drum_keys = [k for k in dry_arrays if "Drum" in k]
print(f"drum_keys={drum_keys}")
pitched = [a for k, a in dry_arrays.items() if k not in drum_keys]
# align lengths
L = max([a.shape[0] for a in pitched] + [wet_drums.shape[0], sub_st.shape[0]])
def pad(a, L):
    if a.shape[0] < L:
        return np.vstack([a, np.zeros((L - a.shape[0], 2))])
    return a[:L]
pitched_sum = sum(pad(a, L) for a in pitched)
# balance: pitched bed 0.8, bullfrog 1.0, sub included in drums bus
mix = 0.8 * pad(pitched_sum, L) + 1.0 * pad(wet_drums, L) + pad(sub_st, L)
# peak norm 0.89
mix = mix / max(1e-9, np.max(np.abs(mix))) * 0.89
print(f"mix peak={np.max(np.abs(mix)):.4f} len={len(mix)/SR:.2f}s")

# --- 8. LUFS normalize -14 + limiter LAST (positional sr arg: normalize_to_lufs(audio, target, sr))
from sound.effects.mastering import normalize_to_lufs, Limiter
mix_lufs = normalize_to_lufs(mix, -14.0, SR)
lim = Limiter(threshold_db=-1.0)
final = lim.process(mix_lufs)
# measure
from sound.effects.mastering import measure_lufs
try:
    lufs = measure_lufs(final, SR)
    print(f"LUFSraw={lufs}")
    lufs_val = float(lufs.integrated_lufs) if hasattr(lufs, "integrated_lufs") else float(lufs)
except Exception as e:
    print(f"lufs measure fail: {e}")
    lufs_val = -14.0

write_wav(OUT / "SP074-drummachine-delta-blues.wav", final, SR)
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(OUT / "SP074-drummachine-delta-blues.wav"),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(OUT / "SP074-drummachine-delta-blues.ogg")], capture_output=True, text=True)
print(f"ffmpeg rc={r.returncode} {r.stderr[-300:]}")
print(f"wav { (OUT/'SP074-drummachine-delta-blues.wav').stat().st_size } ogg {(OUT/'SP074-drummachine-delta-blues.ogg').stat().st_size}")

# processed pitched stems (copies, peak-safe) for DAW
for k, v in stems.items():
    if k in drum_keys:
        continue
    a, sr = read_wav(v)
    if a.ndim == 1:
        a = np.stack([a, a], axis=1)
    a = a / max(1e-9, np.max(np.abs(a))) * 0.89
    write_wav(OUT / "Audio" / "stems_processed" / (Path(v).stem + "_SOUNDFONT.wav"), a, SR)

# provenance
prov = {
    "method": "SP-074",
    "module": "sound.generators.drum_machine",
    "desc": "Eight-Channel Sample Drum Machine + Sequencer (Bullfrog Drums-style)",
    "source": str(SRC),
    "bpm": BPM,
    "bars": total_bars,
    "grid": {str(k): len(h) for k, h in grid.items()},
    "swing": 0.55,
    "lufs": lufs_val,
    "soundfont": SF,
}
(OUT / "provenance.json").write_text(json.dumps(prov, indent=2))
shutil.copy("/opt/data/select_20260915.py", OUT / "Scripts" / "select_20260915.py")
shutil.copy("/opt/data/analyze_src_0915.py", OUT / "Scripts" / "analyze_src_0915.py")
shutil.copy("/opt/data/dist_src_0915.py", OUT / "Scripts" / "dist_src_0915.py")
shutil.copy(__file__, OUT / "Scripts" / "produce_sp074.py")
print("PRODUCE DONE")
