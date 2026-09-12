# -*- coding: utf-8 -*-
"""Phase 2: Pop Ballad — per-VOICE + per-SECTION production methods.

Applies DIFFERENT production methods per voice (on stems) AND per section
(on the mixed bus), then masters. Pattern: per-voice-per-section-production.md

Stems are routed BY ROLE (index order), not by hardcoded GM name — the
instrumentation palette rotates per HITL round, so a name-based router
("Recorder", "Contrabass") silently stopped matching the moment the
palette changed. `RenderPipeline.render_stems` names tracks
track00..trackN in voice order, which is exactly the order phase 1 adds
voices: Lead, Pad, Bass, Arp, Drums.

Per-voice production methods (on stems):
  Lead   -> SP-032 FDN reverb wash   (lead space)
  Pad    -> SP-020 SVF lowpass warm  (ballad bed)
  Bass   -> SP-020 SVF lowpass 700   (sub body)
  Arp    -> SP-019 waveshape         (harmonics)
  Drums  -> SP-008 multiband compress(punch)

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
import sys
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

# Voice order == stem index order (phase 1 build order).
ROLE_ORDER = ["Lead", "Pad", "Bass", "Arp", "Drums"]


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


def _stem_by_index(stems, idx):
    """Resolve a stem path by track index (track00 = first voice, ...).

    `render_stems` keys look like 'track03_Clarinet' — the numeric prefix
    is the voice order, which is stable across palette changes.
    """
    for key, path in stems.items():
        if key.startswith(f"track{idx:02d}"):
            return path
    return None


def _process_voice(role, audio):
    """Per-voice production method (dispatch by ROLE, not by GM name)."""
    if role == "Lead":
        return sp032_fdn(audio, size=0.75, decay=0.5, brightness=0.65,
                         wet=0.3)                       # lead space
    if role == "Pad":
        return sp020_lowpass(audio, 4500)               # warm bed
    if role == "Bass":
        return sp020_lowpass(audio, 700)                # sub body
    if role == "Arp":
        return sp019_waveshape(audio, 1.5)              # harmonics
    if role == "Drums":
        return sp008_mbc(audio)                         # punch
    return audio


def main(midi_path=None, out_stem=None):
    midi_path = Path(midi_path or MID)
    stem_name = out_stem or midi_path.stem
    AUDIO.mkdir(parents=True, exist_ok=True)
    STEMS.mkdir(parents=True, exist_ok=True)

    # ---- 1. render stems ----
    pipe = RenderPipeline(fluidsynth_bin=fluidsynth_bin(),
                          soundfont_path=soundfont_path(), gain=1.2)
    stems = pipe.render_stems(str(midi_path), str(STEMS), format="wav")
    print("stems:", {k: os.path.basename(v) for k, v in stems.items()})

    # ---- 2. per-voice production (route by ROLE / track index) ----
    processed = {}
    pan = {"Lead": 0.25, "Pad": 0.0, "Bass": 0.0, "Arp": 0.75, "Drums": 0.0}
    gains = {"Lead": 1.0, "Pad": 0.7, "Bass": 0.9, "Arp": 0.5, "Drums": 0.6}
    for idx, role in enumerate(ROLE_ORDER):
        p = _stem_by_index(stems, idx)
        if not p:
            print(f"  (no stem for role {role} / track{idx:02d})")
            continue
        a, _sr = read_wav(p)
        a = mono(a)
        out = _process_voice(role, a)
        processed[role] = out
        rms = float(np.sqrt(np.mean(out ** 2)))
        print(f"  {role}: {os.path.basename(p)} rms {rms:.4f}")

    # ---- 3. mix to stereo bus with pan ----
    n = max(len(v) for v in processed.values()) if processed else SR
    bus_l = np.zeros(n, dtype=np.float64)
    bus_r = np.zeros(n, dtype=np.float64)
    for role, sig in processed.items():
        g = gains.get(role, 0.7) * 0.5
        p = pan.get(role, 0.0)
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

    wav_path = AUDIO / f"{stem_name}.wav"
    ogg_path = AUDIO / f"{stem_name}.ogg"
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
    import argparse
    ap = argparse.ArgumentParser(description="Pop-ballad phase 2 production")
    ap.add_argument("--midi", default=None,
                    help="MIDI to produce (default: the canonical phase-1 mix)")
    ap.add_argument("--out-stem", default=None, help="output basename")
    a = ap.parse_args()
    main(midi_path=a.midi, out_stem=a.out_stem)
