# -*- coding: utf-8 -*-
"""
Pop 5-part — Phase 2 (production: per-voice + per-section methods).

Phase 1 produced the MIDI framework with per-section COMPOSITION methods.
Phase 2 applies a DIFFERENT production method per VOICE and per SECTION:

Per-voice production (5 distinct DSP methods on rendered stems):
  Melody -> TapeDelay (echo)
  Pad    -> FDN reverb (space)
  Bass   -> Biquad lowpass 400Hz (warm)
  Arp    -> StereoImager widen + highshelf (air)
  Drums  -> MultibandCompressor (punch)

Per-section production (5 distinct treatments on the mixed bus):
  Intro  -> lowpass 1200Hz (muffled build-in)
  Verse  -> dry (clean)
  Chorus -> StereoImager widen + highshelf (lift)
  Bridge -> FDN reverb wash
  Outro  -> lowpass 800Hz + fade-out

Then master: LUFS -14 + limiter -1dB. Export full mix WAV + OGG + stems.
"""

import os
import numpy as np

from sound.render import RenderPipeline
from sound.utils.io import read_wav, write_wav
from sound.effects import (
    TapeDelay, FDN, BiquadFilter, StereoImager, MultibandCompressor,
    normalize_to_lufs, Limiter, measure_lufs,
)

SR = 44100
SF2 = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
MIDI = "/opt/data/projects/Styles/Pop/pop-5part-methods/MIDI/pop_5part_methods.mid"
PROJ = "/opt/data/projects/Styles/Pop/pop-5part-methods"

# Section boundaries in seconds (120 BPM, 4/4 -> bar = 2.0s)
# bars: Intro 4, Verse 8, Chorus 8, Bridge 4, Outro 4
SECTION_EDGES = [("Intro", 0.0, 8.0), ("Verse", 8.0, 24.0), ("Chorus", 24.0, 40.0),
                 ("Bridge", 40.0, 48.0), ("Outro", 48.0, 56.0)]


def _mono(a):
    return a[:, 0] if a.ndim > 1 else a


def _to_stereo(a):
    return a if a.ndim > 1 else np.column_stack([a, a])


def _rms(a):
    m = _mono(a)
    return float(np.sqrt(np.mean(m ** 2)))


def _silence_ratio(a):
    m = _mono(a)
    return float(np.sum(np.abs(m) < 0.001) / len(m))


def render_stems():
    pipe = RenderPipeline(fluidsynth_bin=FLUID, soundfont_path=SF2, gain=1.2)
    stems_dir = os.path.join(PROJ, "Audio", "stems")
    os.makedirs(stems_dir, exist_ok=True)
    return pipe.render_stems(MIDI, stems_dir, format="wav")


def apply_voice_production(stems):
    """Apply a distinct production method per voice. Returns dict name->audio (mono)."""
    out = {}
    for name, path in stems.items():
        a, sr = read_wav(path)
        a = _mono(a)
        if "Recorder" in name or "Flute" in name:   # Melody -> manual echo (dry + delayed)
            d = int(0.28 * sr)
            wet = np.zeros(len(a) + d, dtype=np.float64)
            wet[:len(a)] += a.astype(np.float64)
            wet[d:] += 0.35 * a.astype(np.float64)
            a = wet[:len(a)].astype(np.float32)
        elif "String" in name:                   # Pad -> FDN reverb
            fdn = FDN(sample_rate=sr)
            fdn.set(size=0.8, decay=0.6, brightness=0.7, wet_dry=0.35)
            a = fdn.process(a)
        elif "Bass" in name:                     # Bass -> lowpass warm
            bq = BiquadFilter(sample_rate=sr)
            bq.design("lowpass", 400.0, Q=0.707)
            a = bq.process(a)
        elif "Pad" in name:                      # Arp (Synth Pad program) -> widen + air
            im = StereoImager(sample_rate=sr)
            im.set_width(1.4, above_hz=2000)
            a = im.process(a)
            a = _mono(a)
            bq = BiquadFilter(sample_rate=sr)
            bq.design("highshelf", 6000.0, Q=0.7, gain_db=3.0)
            a = bq.process(a)
        elif "Piano" in name:                    # Drums (program 0, ch9) -> multiband punch
            mbc = MultibandCompressor(sample_rate=sr)
            mbc.add_band(0, threshold_db=-10, ratio=2.5)
            mbc.add_band(2, threshold_db=-12, ratio=2.0)
            a = mbc.process(a)
        else:
            pass
        out[name] = a.astype(np.float32)
    return out


def mix_stems(produced):
    """Pan voices onto a stereo bus, align to common length."""
    names = list(produced.keys())
    n = max(len(v) for v in produced.values())
    L = np.zeros(n, dtype=np.float64)
    R = np.zeros(n, dtype=np.float64)
    for name in names:
        v = produced[name].astype(np.float64)
        if "Recorder" in name or "Flute" in name:  # melody center-left
            L[:len(v)] += v * 0.9; R[:len(v)] += v * 0.7
        elif "Bass" in name:     # bass center
            L[:len(v)] += v * 0.8; R[:len(v)] += v * 0.8
        elif "String" in name:   # pad wide
            L[:len(v)] += v * 0.55; R[:len(v)] += v * 0.55
        elif "Pad" in name:      # arp slightly right
            L[:len(v)] += v * 0.5; R[:len(v)] += v * 0.65
        else:                    # drums (Piano) center
            L[:len(v)] += v * 0.75; R[:len(v)] += v * 0.75
    bus = np.column_stack([L, R])
    peak = np.max(np.abs(bus))
    if peak > 0:
        bus = bus / peak * 0.9
    return bus.astype(np.float32)


def apply_section_production(mix):
    """Slice the mix at section boundaries and apply a distinct treatment each."""
    sr = SR
    n = len(mix)
    out = np.zeros_like(mix, dtype=np.float64)
    for name, t0, t1 in SECTION_EDGES:
        i0 = int(t0 * sr)
        i1 = min(int(t1 * sr), n)
        seg = mix[i0:i1].astype(np.float64)
        if name == "Intro":
            bq = BiquadFilter(sample_rate=sr); bq.design("lowpass", 1200.0, Q=0.707)
            seg = bq.process(seg)
        elif name == "Verse":
            pass  # dry
        elif name == "Chorus":
            im = StereoImager(sample_rate=sr); im.set_width(1.3, above_hz=2000)
            seg = im.process(seg)
            bq = BiquadFilter(sample_rate=sr); bq.design("highshelf", 8000.0, Q=0.7, gain_db=2.5)
            seg = bq.process(seg)
        elif name == "Bridge":
            fdn = FDN(sample_rate=sr); fdn.set(size=0.85, decay=0.7, wet_dry=0.4)
            seg = fdn.process(seg)
        elif name == "Outro":
            bq = BiquadFilter(sample_rate=sr); bq.design("lowpass", 800.0, Q=0.707)
            seg = bq.process(seg)
            fade = np.linspace(1.0, 0.0, len(seg))
            seg = seg * fade[:, None]
        out[i0:i1] = seg
    return out.astype(np.float32)


def master(mix):
    mix = normalize_to_lufs(mix, target_lufs=-14.0, sample_rate=SR)
    lim = Limiter(threshold_db=-1.0, release_ms=100, sample_rate=SR)
    mix = lim.process(mix)
    return mix.astype(np.float32)


def main():
    os.makedirs(os.path.join(PROJ, "Audio"), exist_ok=True)

    print("Rendering stems...")
    stems = render_stems()
    for k, v in stems.items():
        print(f"  stem {k}: {os.path.getsize(v)} bytes")

    print("Applying per-voice production...")
    produced = apply_voice_production(stems)
    for k, v in produced.items():
        print(f"  {k}: rms={_rms(v):.4f} silence={_silence_ratio(v)*100:.1f}%")

    print("Mixing stereo bus...")
    mix = mix_stems(produced)
    print(f"  mix rms={_rms(mix):.4f} silence={_silence_ratio(mix)*100:.1f}%")

    print("Applying per-section production...")
    mix = apply_section_production(mix)

    print("Mastering (LUFS -14, limiter -1dB)...")
    mix = master(mix)
    lufs = measure_lufs(mix, SR)
    print(f"  final LUFS={lufs:.1f} peak={np.max(np.abs(mix)):.3f}")

    # Export
    wav_path = os.path.join(PROJ, "Audio", "pop_5part_methods.wav")
    write_wav(wav_path, mix, SR, normalize=False)
    ogg_path = os.path.join(PROJ, "Audio", "pop_5part_methods.ogg")
    os.system(f"ffmpeg -y -loglevel error -i {wav_path} -codec:a libopus -application voip -b:a 48k {ogg_path}")

    print(f"\nWAV: {wav_path} ({os.path.getsize(wav_path)} bytes)")
    print(f"OGG: {ogg_path} ({os.path.getsize(ogg_path)} bytes)")

    # silence verification on final
    a, sr = read_wav(wav_path)
    print(f"FINAL silence ratio: {_silence_ratio(a)*100:.1f}%  rms={_rms(a):.4f}")


if __name__ == "__main__":
    main()
