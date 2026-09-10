# -*- coding: utf-8 -*-
"""Phase 2: Pop Ballad — per-VOICE + per-SECTION production methods.

Applies DIFFERENT production methods per voice (on stems) AND per section
(on the mixed bus), then masters. Pattern: per-voice-per-section-production.md

Per-voice production methods (on stems, matched by GM stem label):
  Lead  (Recorder/GM74)   -> SP-032 FDN reverb wash  (vocal lead space)
  Pad   (Acoustic_Grand)  -> SP-020 SVF lowpass warm (ballad bed)
  Bass  (Contrabass)      -> SP-011 Karplus body (sub presence) via EQ boost
  Arp   (Clarinet)        -> SP-019 waveshape (harmonics, widen)
  Drums (Drums)           -> SP-008 multiband compress (punch)

Per-section production methods (on the mixed bus, sliced at bar boundaries):
  Intro  (0-4)  -> SP-020 lowpass 1200 Hz (muffled build-in)
  Verse  (4-12) -> dry (lyric clarity)
  Chorus (12-20)-> SP-021 stereo widen + highshelf lift
  Bridge (20-24)-> SP-032 FDN wash (size .85, wet .4)
  Outro  (24-28)-> SP-020 lowpass 800 Hz + fade to 0
Master: normalize_to_lufs(-14) then Limiter(-1 dB) LAST.
"""
import os
import subprocess
from pathlib import Path

import numpy as np

from utilities.env import fluidsynth_bin, soundfont_path
from sound.render import RenderPipeline
from sound.effects.fdn_reverb import FDN
from sound.effects.filter import BiquadFilter, StateVariableFilter
from sound.effects.multiband import MultibandCompressor
from sound.effects.mastering import StereoImager, Limiter, normalize_to_lufs
from sound.utils.io import read_wav, write_wav

SR = 44100
PROJECT = Path("/opt/data/repos/musicom/projects/Styles/Pop/ballad-hitl")
MID = PROJECT / "MIDI" / "pop-ballad-hitl.mid"
AUDIO = PROJECT / "Audio"
STEMS = AUDIO / "stems"
BPM = 72
BAR_S = 60.0 / BPM * 4          # 3.333 s per bar at 72bpm 4/4
SEC_BOUNDS = [0, 4, 12, 20, 24, 28]   # section start bars: intro/verse/chorus/bridge/outro


def sp020_lowpass(a, cutoff_hz):
    """SP-020: SVF lowpass (analog-style warmth)."""
    f = StateVariableFilter(sample_rate=SR)
    return f.process(a, cutoff=cutoff_hz, resonance=0.707, mode="lp")


def sp032_fdn(a, size=0.8, decay=0.6, brightness=0.7, wet=0.35):
    """SP-032: FDN reverb wash."""
    r = FDN(sample_rate=SR)
    r.set(size=size, decay=decay, brightness=brightness, wet_dry=wet)
    return r.process(a)


def sp019_waveshape(a, drive=2.0):
    """SP-019: Chebyshev-style soft waveshaping (harmonics)."""
    return np.tanh(a * drive) * (1.0 / max(1e-9, np.tanh(drive)))


def sp008_mbc(a):
    """SP-008: multiband punch."""
    m = MultibandCompressor(sample_rate=SR)
    m.add_band(0, threshold_db=-14.0, ratio=2.5)
    m.add_band(1, threshold_db=-16.0, ratio=2.0)
    m.add_band(2, threshold_db=-18.0, ratio=1.8)
    return m.process(a)


def sp021_widen(a, amount=1.35):
    """SP-021: stereo image widen (mid/side boost above 2 kHz)."""
    s = StereoImager(sample_rate=SR)
    s.set_width(amount, below_hz=2000.0)
    return s.process(a)


def mono(a):
    if a.ndim > 1:
        return np.mean(a, axis=1)
    return a


def main():
    AUDIO.mkdir(parents=True, exist_ok=True)
    STEMS.mkdir(parents=True, exist_ok=True)

    # ---- 1. render stems ----
    pipe = RenderPipeline(fluidsynth_bin=fluidsynth_bin(),
                          soundfont_path=soundfont_path(), gain=1.2)
    stems = pipe.render_stems(str(MID), str(STEMS), format="wav")
    print("stems:", {k: os.path.basename(v) for k, v in stems.items()})

    # ---- 2. per-voice production (route by ACTUAL GM stem label) ----
    def _find(label_substr):
        for k, v in stems.items():
            if label_substr in k:
                return v
        return None

    processed = {}
    for label_sub in ["Recorder", "Bright_Acoustic", "Contrabass", "Clarinet", "Drums"]:
        p = _find(label_sub)
        if not p:
            print(f"  (no stem matching {label_sub})")
            continue
        a, _sr = read_wav(p)
        a = mono(a)
        if "Recorder" in p:
            out = sp032_fdn(a, size=0.75, decay=0.5, brightness=0.65, wet=0.3)   # lead space
        elif "Bright_Acoustic" in p:
            out = sp020_lowpass(a, 4500)                                          # warm pad
        elif "Contrabass" in p:
            out = sp020_lowpass(a, 700)                                           # sub body
        elif "Clarinet" in p:
            out = sp019_waveshape(a, 1.5)                                         # arp harmonics
        elif "Drums" in p:
            out = sp008_mbc(a)                                                    # punch
        else:
            out = a
        processed[label_sub] = out
        rms = float(np.sqrt(np.mean(out ** 2)))
        print(f"  {label_sub}: rms {rms:.4f}")

    # ---- 3. mix to stereo bus with pan (lead L, arp R, rest center) ----
    n = max(len(v) for v in processed.values()) if processed else SR
    bus_l = np.zeros(n, dtype=np.float64)
    bus_r = np.zeros(n, dtype=np.float64)
    pan = {"Recorder": 0.25, "Bright_Acoustic": 0.0, "Contrabass": 0.0,
           "Clarinet": 0.75, "Drums": 0.0}
    gains = {"Recorder": 1.0, "Bright_Acoustic": 0.7, "Contrabass": 0.9,
             "Clarinet": 0.5, "Drums": 0.6}
    for label_sub, sig in processed.items():
        g = gains.get(label_sub, 0.7) * 0.5
        p = pan.get(label_sub, 0.0)
        bus_l[:len(sig)] += sig * g * (1.0 - p)
        bus_r[:len(sig)] += sig * g * (1.0 + p)
    mix = np.stack([bus_l, bus_r], axis=1)

    # ---- 4. per-section production on the bus ----
    total_bars = 28
    full_len = int(total_bars * BAR_S * SR)
    mix = mix[:full_len]
    out = np.zeros_like(mix)
    for i in range(5):
        s0 = int(SEC_BOUNDS[i] * BAR_S * SR)
        s1 = int(SEC_BOUNDS[i + 1] * BAR_S * SR)
        seg = mix[s0:s1]
        if i == 0:      # Intro: lowpass 1200 (muffled build-in)
            seg = sp020_lowpass(mono(seg), 1200)
            seg = np.stack([seg, seg], axis=1)
        elif i == 1:    # Verse: dry
            pass
        elif i == 2:    # Chorus: widen + lift
            seg = sp021_widen(seg, 1.35)
        elif i == 3:    # Bridge: FDN wash
            seg = sp032_fdn(mono(seg), size=0.85, decay=0.7, wet=0.4)
            seg = np.stack([seg, seg], axis=1)
        elif i == 4:    # Outro: lowpass 800 + fade
            seg = sp020_lowpass(mono(seg), 800)
            seg = np.stack([seg, seg], axis=1)
            fade = np.linspace(1.0, 0.0, len(seg))
            seg = seg * fade[:, None]
        out[s0:s1] = seg

    # ---- 5. master: LUFS then limiter LAST ----
    out = normalize_to_lufs(out, target_lufs=-14.0, sample_rate=SR)
    lim = Limiter(threshold_db=-1.0)
    out = lim.process(out)

    wav_path = AUDIO / "pop-ballad-hitl.wav"
    ogg_path = AUDIO / "pop-ballad-hitl.ogg"
    write_wav(str(wav_path), out, SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(ogg_path)], check=True)

    # ---- 6. verify ----
    from sound.effects.mastering import measure_lufs
    peak = float(np.max(np.abs(out)))
    lufs = measure_lufs(out, SR)
    silent = float(np.mean(np.abs(out) < 0.001))
    print(f"WAV {wav_path.name}: {os.path.getsize(wav_path)} B")
    print(f"OGG {ogg_path.name}: {os.path.getsize(ogg_path)} B")
    print(f"LUFS {lufs:.2f} peak {peak:.3f} silence {silent*100:.1f}%")


if __name__ == "__main__":
    main()
