"""A/B probe: FluidR3 preset 50 (Synth Strings 1) vs 51 (Synth Strings 2).

Renders the SAME sustained Cmaj7 chord on each program, solo, and measures
attack rise (10%->90% of peak), spectral centroid, band energy, and RMS
envelope shape so the instrument entry is based on measured timbre, not lore.
"""
import os
import sys
import wave
import numpy as np

sys.path.insert(0, "/opt/data/projects/Instruments")
sys.path.insert(0, "/opt/data/projects/Instruments/_test")

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from _test.render_audio import render_midi

BAR = 1920
OUT = "/opt/data/projects/Instruments/_test/probe_50_51"
os.makedirs(OUT, exist_ok=True)

CHORD = [60, 64, 67, 71]  # Cmaj7, mid register


def build(program, path):
    comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    comp.create_matrix(num_voices=1, num_sections=1)
    comp.add_voice("Pad", program=program, channel=0)
    comp.add_section("A", bars=2)
    u = MusicUnit()
    for p in CHORD:
        u.add_event(MusicEvent(p, 76, 0, BAR * 2))
    comp.set_unit(0, 0, u)
    ok, msg = comp.validate()
    assert ok, msg
    comp.to_midi(path)
    return path


def analyse(wav):
    w = wave.open(wav, "rb")
    sr = w.getframerate()
    ch = w.getnchannels()
    data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    w.close()
    if ch > 1:
        data = data.reshape(-1, ch).mean(axis=1)
    mono = data
    # envelope in 5 ms frames
    hop = int(0.005 * sr)
    env = np.array([np.sqrt(np.mean(mono[i:i + hop] ** 2)) for i in range(0, len(mono) - hop, hop)])
    peak = env.max()
    # attack: first time env crosses 10% and 90% of peak
    def cross(level):
        idx = np.argmax(env >= level * peak)
        return idx * 0.005
    t10, t90 = cross(0.10), cross(0.90)
    # centroid over first 1.5 s
    seg = mono[: int(1.5 * sr)]
    spec = np.abs(np.fft.rfft(seg))
    freqs = np.fft.rfftfreq(len(seg), 1 / sr)
    centroid = float((spec * freqs).sum() / max(spec.sum(), 1e-9))
    band = lambda lo, hi: float(spec[(freqs >= lo) & (freqs < hi)].sum() / max(spec.sum(), 1e-9))
    # sustain flatness: rms at 0.5-0.7 s vs 1.6-1.8 s
    def rms(t0, t1):
        s = mono[int(t0 * sr): int(t1 * sr)]
        return float(np.sqrt(np.mean(s ** 2)))
    return {
        "sr": sr, "dur": len(mono) / sr,
        "attack_10": t10, "attack_90": t90,
        "centroid": centroid,
        "b_lo": band(50, 500), "b_mid": band(500, 2000), "b_hi": band(2000, 6000),
        "b_air": band(6000, 12000),
        "rms_early": rms(0.5, 0.7), "rms_late": rms(1.6, 1.8),
        "peak": float(np.abs(mono).max()),
    }


for pgm, tag in ((50, "ss1"), (51, "ss2")):
    mid = build(pgm, f"{OUT}/{tag}.mid")
    wav = render_midi(mid, f"{OUT}/{tag}.wav", solo=0)
    r = analyse(wav)
    print(f"--- {tag} (GM{pgm}) {os.path.getsize(wav)} bytes")
    for k, v in r.items():
        print(f"    {k}: {v:.4f}" if isinstance(v, float) else f"    {k}: {v}")
