#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SP-035 Shimmer Reverb production pass — Tango Dramatic (layered).

Base: FluidSynth render of tango_dramatic.mid (multi-timbral, 4 voices).
Per-stem ShimmerVerb application (fractional pitch-shift feedback ladder),
then re-mix. Absolute-layer method: applied across ALL voices.
"""
import os, subprocess, wave, json, hashlib, sys
import numpy as np

# ---------------------------------------------------------------- paths
REPO = "/opt/data/repos/musicom"
PY = "/opt/data/micromamba/envs/musicom/bin/python"
FS = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
SF2 = "/opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2"
SRC = "/opt/data/projects/Styles/Tango/dramatic/v1/tango_dramatic.mid"
OUT = "/opt/data/projects/Styles/Production/SP035-shimmer-tango-dramatic"
os.makedirs(OUT, exist_ok=True)
for d in ("stems", "Analysis"):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)

sys.path.insert(0, REPO)
from sound.effects.shimmer_reverb import ShimmerVerb

SR = 44100

def read_wav(path):
    with wave.open(path, "rb") as w:
        n = w.getnframes(); ch = w.getnchannels(); sw = w.getsampwidth()
        fr = w.getframerate()
        raw = w.readframes(n)
    assert sw == 2, f"expect 16-bit, got {sw*8}"
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    if ch == 2:
        a = (a[0::2] + a[1::2]) * 0.5
    return a, fr

def write_wav(path, x, sr=SR):
    x = np.clip(x, -1.0, 1.0)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((x * 32767.0).astype(np.int16).tobytes())

def peaknorm(x, level=0.89):
    p = np.max(np.abs(x))
    return x * (level / p) if p > 1e-9 else x

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()

def silence_rms(x, sr=SR):
    mono = x
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    dur = len(mono) / sr
    # per-second RMS map
    rms = []
    for s in range(int(dur) + 1):
        seg = mono[s * sr:(s + 1) * sr]
        if len(seg):
            rms.append(float(np.sqrt(np.mean(seg ** 2))))
    return silent, rms

def pitch_verify(x, sr=SR, hop=0.5):
    """FFT dominant peak per 0.5s window in 50-1000 Hz + harmonic energy."""
    n_win = int(sr * hop)
    frames = []
    fft_freqs = np.fft.rfftfreq(n_win, 1.0 / sr)
    for lo in range(0, len(x) - n_win, n_win):
        seg = x[lo:lo + n_win] * np.hanning(n_win)
        spec = np.abs(np.fft.rfft(seg))
        m = (fft_freqs >= 50) & (fft_freqs <= 1000)
        if not np.any(m):
            continue
        dom = fft_freqs[m][np.argmax(spec[m])]
        frames.append(float(dom))
    frames = np.array(frames)
    f0 = float(np.median(frames)) if len(frames) else 0.0
    # harmonic energy in 8 harmonics of f0
    if f0 > 40:
        n_fft = 1 << 14
        seg = x[:n_fft] * np.hanning(n_fft)
        spec = np.abs(np.fft.rfft(seg))
        fr = np.fft.rfftfreq(n_fft, 1.0 / sr)
        tot = float(np.sum(spec[(fr >= 50) & (fr <= 1000)] ** 2))
        he = 0.0
        for k in range(1, 9):
            fc = f0 * k
            m = (fr >= fc - 15) & (fr <= fc + 15)
            if np.any(m):
                he += float(np.sum(spec[m] ** 2))
        he_ratio = he / tot if tot > 1e-12 else 0.0
    else:
        he_ratio = 0.0
    nz = int(np.sum(frames > 0))
    return f0, he_ratio, nz, len(frames)

# ---------------------------------------------------------------- 1. base render
base_wav = os.path.join(OUT, "base_fluidsynth.wav")
if not os.path.exists(base_wav):
    r = subprocess.run([FS, "-ni", "-g", "1.2", "-F", base_wav, SF2, SRC],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print("FluidSynth failed:", r.stderr[-2000:])
        sys.exit(1)
print("base render OK:", os.path.getsize(base_wav))

# ---------------------------------------------------------------- 2. per-track stems
# RenderPipeline.render_stems — try it; fallback to manual per-channel via mido parse
stem_dir = os.path.join(OUT, "stems")
stem_wavs = {}
try:
    from sound.render import RenderPipeline
    pipe = RenderPipeline(soundfont_path=SF2, fluidsynth_bin=FS)
    stems = pipe.render_stems(SRC, stem_dir, format="wav")
    stem_wavs = {k: v for k, v in stems.items() if os.path.exists(v)}
    print("render_stems:", list(stem_wavs))
except Exception as e:
    print("render_stems failed:", e)
    stem_wavs = {}

if not stem_wavs:
    # manual fallback: parse MIDI, group by channel, synth each channel alone
    print("manual per-channel fallback")
    import mido
    mid = mido.MidiFile(SRC)
    notes = {}
    for trk in mid.tracks:
        t = 0
        for msg in trk:
            t += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                ch = msg.channel
                notes.setdefault(ch, []).append((t, msg.note, msg.velocity, msg.time))
    # simpler: rebuild via musicom UnitMatrixComposer? no — synth per channel
    # by re-rendering with a channel-muted copy is complex; instead group events
    # and render each channel's note list to a small MIDI, then FluidSynth it.
    from collections import defaultdict
    evs = defaultdict(list)
    for trk in mid.tracks:
        t = 0
        for msg in trk:
            t += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                evs[msg.channel].append((t, msg.note, msg.velocity))
    evs = {ch: sorted(v) for ch, v in evs.items()}
    print("channels:", {ch: len(v) for ch, v in evs.items()})

    # This fallback is complex; simpler: FluidSynth layer files are overkill.
    # Use mido to write per-channel MIDI with identical timing, render each.
    import mido as mido_mod
    from mido import MidiFile, MidiTrack, Message, MetaMessage
    tick_total = {}
    for trk in mid.tracks:
        t = 0
        for msg in trk:
            t += msg.time
        tick_total[trk] = t
    max_tick = max(tick_total.values()) if tick_total else 0
    ppq = mid.ticks_per_beat
    # build per-channel files preserving program changes
    programs = {}
    for trk in mid.tracks:
        t = 0
        for msg in trk:
            t += msg.time
            if msg.type == "program_change":
                programs.setdefault(msg.channel, msg.program)
    for ch, evlist in evs.items():
        out_mid = MidiFile(ticks_per_beat=ppq)
        trk0 = MidiTrack(); trk0.append(MetaMessage("set_tempo", tempo=mid.tracks[0].tracks[0].tempo if False else 500000))
        # find tempo from first track meta
        for t0 in mid.tracks:
            for m in t0:
                if m.type == "set_tempo":
                    trk0 = MidiTrack(); trk0.append(MetaMessage("set_tempo", tempo=m.tempo)); break
            else:
                continue
            break
        out_mid.tracks.append(trk0)
        trk = MidiTrack()
        if ch in programs:
            trk.append(Message("program_change", program=programs[ch], channel=ch, time=0))
        last = 0
        for (t, note, vel) in evlist:
            trk.append(Message("note_on", note=note, velocity=vel, channel=ch, time=t - last))
            last = t
        # pad tail: note_off all at max_tick
        trk.append(Message("note_off", note=0, velocity=0, channel=ch, time=max_tick - last))
        out_mid.tracks.append(trk)
        per = os.path.join(stem_dir, f"ch{ch:02d}.mid")
        out_mid.save(per)
        pw = os.path.join(stem_dir, f"ch{ch:02d}.wav")
        r = subprocess.run([FS, "-ni", "-g", "1.2", "-F", pw, SF2, per],
                           capture_output=True, text=True, timeout=300)
        if r.returncode == 0:
            stem_wavs[f"ch{ch:02d}"] = pw
    print("manual stems:", stem_wavs)

# ---------------------------------------------------------------- 3. shimmer per stem
params = {
    "pitch_cents": 250,      # fractional semitone up (article headline trick)
    "rev_time": 0.6,
    "pitch_amount": 0.65,
    "filter_cutoff": 6500.0,
    "mix": 0.55,
}
sv = ShimmerVerb(sample_rate=SR, seed=7)
shimmer_stems = {}
lengths = []
for name, wp in sorted(stem_wavs.items()):
    a, fr = read_wav(wp)
    lengths.append(len(a))
    wet = sv.process(a, **params)
    out = peaknorm(wet)
    op = os.path.join(OUT, f"shimmer_{name}.wav")
    write_wav(op, out)
    shimmer_stems[name] = op
    print(f"shimmer {name}: in {len(a)} -> out {len(out)} peak {np.max(np.abs(out)):.3f}")

# ---------------------------------------------------------------- 4. mix
maxlen = max(lengths)
mix = np.zeros(maxlen)
for name, op in sorted(shimmer_stems.items()):
    a, fr = read_wav(op)
    if len(a) < maxlen:
        a = np.pad(a, (0, maxlen - len(a)))
    mix += a
mix = peaknorm(mix / len(shimmer_stems))
full_wav = os.path.join(OUT, "SP035-shimmer-tango-dramatic_full_mix.wav")
write_wav(full_wav, mix)

# tail ring: shimmer tail beyond base length — add reverb tail pass on full mix
sv2 = ShimmerVerb(sample_rate=SR, seed=11)
full_tail = sv2.process(mix, pitch_cents=120, rev_time=0.7, pitch_amount=0.4,
                        filter_cutoff=6000.0, mix=0.35)
full_tail = peaknorm(full_tail)
write_wav(full_wav, full_tail)

# ---------------------------------------------------------------- 5. OGG
ogg = os.path.join(OUT, "SP035-shimmer-tango-dramatic.ogg")
subprocess.run(["ffmpeg", "-y", "-i", full_wav, "-codec:a", "libopus",
                "-application", "voip", "-b:a", "48k", ogg],
               capture_output=True, text=True, timeout=120)

# ---------------------------------------------------------------- 6. analysis
silent, rms = silence_rms(full_tail)
f0, he, nz, nf = pitch_verify(full_tail)
print(f"silence: {silent*100:.1f}%  f0_median={f0:.1f} Hz  harm_energy={he*100:.1f}%  pitch_frames={nz}/{nf}")

analysis = os.path.join(OUT, "Analysis", "pitch_verification.txt")
with open(analysis, "w") as f:
    f.write("SP-035 Shimmer Tango Dramatic — pitch verification\n")
    f.write(f"median dominant FFT peak (50-1000Hz, 0.5s hops): {f0:.1f} Hz\n")
    f.write(f"harmonic energy in 8 harmonics of f0: {he*100:.1f}% (>=30% = tonal)\n")
    f.write(f"pitch frames with content: {nz}/{nf}\n")
    f.write(f"silence ratio: {silent*100:.1f}% (mid-track gaps >30% suspect)\n")
    f.write("per-second RMS:\n")
    f.write(", ".join(f"{v:.4f}" for v in rms) + "\n")

# ---------------------------------------------------------------- 7. provenance
def write_prov(artifact, label, extra):
    with open(artifact + ".provenance.json", "w") as f:
        json.dump({
            "artifact": os.path.basename(artifact),
            "sha256": sha256(artifact),
            "method": "SP-035",
            "module": "sound.effects.shimmer_reverb",
            "label": label,
            "source": SRC,
            "params": extra,
            "utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        }, f, indent=2)

write_prov(full_wav, "full mix (shimmer reverb, layered per-stem + tail pass)", params)
for name, op in sorted(shimmer_stems.items()):
    write_prov(op, f"per-stem shimmer {name}", params)
write_prov(ogg, "delivery ogg", params)

print("OUT:", OUT)
print("FILES:")
for root, dirs, files in os.walk(OUT):
    for fn in sorted(files):
        p = os.path.join(root, fn)
        print(f"  {p}  {os.path.getsize(p)}")
