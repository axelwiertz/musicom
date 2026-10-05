# -*- coding: utf-8 -*-
"""Production pass — chanson-champs-study (Chanson Française polish).

Pipeline (idiomatic to 1960s French pop, NOT EDM):
  1. render per-track stems (FluidSynth)
  2. per-voice chanson FX:
       Accordion -> lush Schroeder reverb (the musette cabaret wash)
       Strings   -> reverb (air / space an octave up)
       Lead      -> light reverb + vintage slap echo (single-tap, ~120 ms)
       Guitar    -> light reverb
       Bass      -> clean, kept centered (tight oom-pah, no reverb)
       Drums     -> light room reverb (air)
  3. section polish:
       Intro    -> fade-in + gentle LPF (muffled build-in)
       Chorus   -> stereo widen (mid/side) + high-shelf brightness (the lift)
       Outro    -> LPF + fade-out
  4. stereo imaging (mono sub <100 Hz, widen highs >3 kHz)
  5. mastering: LUFS normalize (-14) -> limiter (-1 dB)
"""
import os
import json

import numpy as np

from sound.render import RenderPipeline
from sound.effects.reverb import AlgorithmicReverb
from sound.effects.filter import StateVariableFilter
from sound.effects.mastering import (StereoImager, Limiter,
                                     normalize_to_lufs, measure_lufs)
from sound.utils.io import read_wav, write_wav
from sound.render.fluidsynth import discover_soundfont

SR = 44100
PROJ = os.path.dirname(os.path.abspath(__file__))
MID = os.path.join(PROJ, "MIDI", "chanson-champs-study.mid")
STEM_DIR = os.path.join(PROJ, "Audio", "stems")
OUT_WAV = os.path.join(PROJ, "Audio", "chanson-champs-study.wav")
OUT_OGG = os.path.join(PROJ, "Audio", "chanson-champs-study.ogg")

BPM = 126
BPB = 4
BAR = 60.0 / BPM * BPB          # 1.90476 s
# section -> (start_bar, end_bar)
SEC_BARS = [
    ("Intro",   0, 4),
    ("Verse1",  4, 12),
    ("Chorus1", 12, 20),
    ("Verse2",  20, 28),
    ("Chorus2", 28, 36),
    ("Outro",   36, 40),
]
SEC = {n: (a * BAR, b * BAR) for n, a, b in SEC_BARS}


def to_stereo(a):
    if a.ndim == 1:
        return np.column_stack([a, a])
    if a.shape[1] == 1:
        return np.repeat(a, 2, axis=1)
    return a


def find_stem(stems, *keys):
    for name, path in stems.items():
        if all(k in name for k in keys):
            return path
    return None


def apply_reverb(a, room, damping, wet, sample_rate=SR):
    r = AlgorithmicReverb(sample_rate=sample_rate, room_size=room,
                          damping=damping, wet_dry=wet, width=0.9)
    return r.process(a)


def apply_delay(a, delay_s, feedback):
    """Clean single-tap echo (manual overlay). Do NOT use TapeDelay here — its
    feedback+saturation loop self-oscillates into full-scale noise."""
    mono = a[:, 0] if a.ndim == 2 else a
    d = int(delay_s * SR)
    wet = mono.copy()
    if d < len(mono):
        wet[d:] += feedback * mono[:len(mono) - d]
    return a + 0.35 * np.column_stack([wet, wet])


def lp_region(mix, t0, t1, cutoff, xfade=0.06, sr=SR):
    n = len(mix)
    i0 = int(t0 * sr)
    i1 = int(min(t1 * sr, n))
    xf = int(xfade * sr)
    a = max(0, i0 - xf)
    b = min(n, i1 + xf)
    if b <= a:
        return mix
    out = mix.copy()
    svf = StateVariableFilter(sample_rate=sr)
    filtered = svf.process(mix[a:b], cutoff=cutoff, resonance=0.4, mode="lp")
    w = np.ones(b - a)
    if i0 > a:
        w[: i0 - a] = np.linspace(0, 1, i0 - a)
    if b > i1:
        w[i1 - a:] = np.linspace(1, 0, b - i1)
    out[a:b] = mix[a:b] * (1 - w[:, None]) + filtered * w[:, None]
    return out


def widen_brighten_region(mix, t0, t1, width=1.5, bright_db=1.5, xfade=0.25, sr=SR):
    """Stereo widen (mid/side) + high-shelf brightness over [t0,t1], edge-ramped."""
    n = len(mix)
    i0 = int(t0 * sr)
    i1 = int(min(t1 * sr, n))
    if i1 <= i0:
        return mix
    seg = mix[i0:i1]
    L = seg[:, 0]
    R = seg[:, 1]
    mid = (L + R) / 2.0
    side = (L - R) / 2.0
    side *= width
    wide = np.column_stack([mid + side, mid - side])
    # high-shelf brightness: add a scaled high-passed copy
    svf = StateVariableFilter(sample_rate=sr)
    hp = svf.process(seg, cutoff=3000, resonance=0.7, mode="hp")
    g = 10.0 ** (bright_db / 20.0) - 1.0
    out_seg = wide + g * hp

    xf = int(xfade * sr)
    env = np.ones(i1 - i0)
    if i0 > 0:
        env[: min(xf, i1 - i0)] = np.linspace(0, 1, min(xf, i1 - i0))
    if i1 < n:
        env[-min(xf, i1 - i0):] = np.linspace(1, 0, min(xf, i1 - i0))
    mix[i0:i1] = seg * (1 - env[:, None]) + out_seg * env[:, None]
    return mix


def fade(mix, t0, t1, g0, g1, sr=SR):
    i0 = int(t0 * sr)
    i1 = int(min(t1 * sr, len(mix)))
    if i1 <= i0:
        return mix
    ramp = np.linspace(g0, g1, i1 - i0)
    mix[i0:i1] *= ramp[:, None]
    return mix


def main():
    print("== render stems ==")
    sf = discover_soundfont()
    pipeline = RenderPipeline(soundfont_path=sf)
    stems = pipeline.render_stems(MID, STEM_DIR, format="wav")
    print("stems:", sorted(stems.keys()))

    accord_p = find_stem(stems, "Accordion")
    gtr_p = find_stem(stems, "Acoustic_Guitar_steel")
    str_p = find_stem(stems, "String_Ensemble")
    lead_p = find_stem(stems, "Trumpet")
    bass_p = find_stem(stems, "Acoustic_Bass")
    drums_p = find_stem(stems, "Drums")
    for label, p in [("Accordion", accord_p), ("Guitar", gtr_p), ("Strings", str_p),
                     ("Lead", lead_p), ("Bass", bass_p), ("Drums", drums_p)]:
        print(f"  {label}: {os.path.basename(p) if p else 'MISSING'}")

    audio = {}
    length = None
    for label, p in [("Accordion", accord_p), ("Guitar", gtr_p), ("Strings", str_p),
                     ("Lead", lead_p), ("Bass", bass_p), ("Drums", drums_p)]:
        a, sr = read_wav(p)
        a = to_stereo(a).astype(np.float64)
        audio[label] = a
        length = len(a) if length is None else min(length, len(a))
    for k in audio:
        audio[k] = audio[k][:length]

    print("== per-voice FX ==")
    accord = apply_reverb(audio["Accordion"], 0.80, 0.40, 0.35)   # musette wash
    strings = apply_reverb(audio["Strings"], 0.72, 0.35, 0.32)     # air
    lead = apply_delay(audio["Lead"], 0.120, 0.25)                 # vintage slap
    lead = apply_reverb(lead, 0.45, 0.30, 0.20)                    # room air
    guitar = apply_reverb(audio["Guitar"], 0.52, 0.30, 0.22)
    bass = audio["Bass"]                                           # clean, centered
    drums = apply_reverb(audio["Drums"], 0.35, 0.40, 0.12)         # room air
    print("  accordion reverb, strings reverb, lead slap+reverb, guitar reverb, "
          "drums reverb; bass clean")

    mix = (0.90 * accord + 0.80 * strings + 0.95 * lead
           + 0.85 * guitar + 0.95 * bass + 0.90 * drums)

    print("== section polish ==")
    mix = fade(mix, SEC["Intro"][0], SEC["Intro"][0] + 1.9, 0.0, 1.0)     # build-in
    mix = lp_region(mix, *SEC["Intro"], cutoff=2400)                      # muffled
    for sec in ("Chorus1", "Chorus2"):
        mix = widen_brighten_region(mix, *SEC[sec], width=1.5, bright_db=1.5)
    mix = lp_region(mix, *SEC["Outro"], cutoff=1300)
    mix = fade(mix, SEC["Outro"][1] - 3 * BAR, SEC["Outro"][1], 1.0, 0.0)  # fade-out
    print("  intro fade-in + LPF, chorus widen+brighten, outro LPF + fade-out")

    print("== stereo imaging ==")
    imager = StereoImager(sample_rate=SR)
    imager.set_width(0.0, below_hz=100)
    imager.set_width(1.25, above_hz=3000)
    mix = imager.process(mix)

    print("== mastering ==")
    mix = normalize_to_lufs(mix, target_lufs=-14.0, sample_rate=SR)
    limiter = Limiter(threshold_db=-1.0, release_ms=100)
    mix = limiter.process(mix)
    mix = np.clip(mix, -1.0, 1.0)

    lufs = measure_lufs(mix, SR)
    peak = float(np.max(np.abs(mix)))
    rms = float(np.sqrt(np.mean(mix ** 2)))
    silent = float(np.sum(np.abs(mix[:, 0]) < 0.001) / len(mix))
    print(f"  master: LUFS={lufs:.2f} peak={peak:.4f} rms={rms:.4f} "
          f"silence={100*silent:.1f}%")

    write_wav(OUT_WAV, mix, SR, normalize=False)
    os.system(f'ffmpeg -y -loglevel error -i "{OUT_WAV}" '
              f'-codec:a libopus -b:a 128k "{OUT_OGG}"')

    # ---- verification (real numbers) ----
    mono = mix[:, 0]

    def band(t0, t1, lo, hi):
        seg = mono[int(t0 * SR):int(t1 * SR)]
        seg = seg - seg.mean()
        X = np.fft.rfft(seg * np.hanning(len(seg)))
        f = np.fft.rfftfreq(len(seg), 1 / SR)
        m = (f >= lo) & (f < hi)
        return float(np.sqrt(np.mean(np.abs(X[m]) ** 2)))

    def side_ratio(t0, t1):
        seg = mix[int(t0 * SR):int(t1 * SR)]
        L, R = seg[:, 0], seg[:, 1]
        mid = (L + R) / 2.0
        side = (L - R) / 2.0
        return float(np.sqrt(np.mean(side ** 2)) /
                     (np.sqrt(np.mean(mid ** 2)) + 1e-9))

    hi_intro = band(*SEC["Intro"], 6000, 12000)
    hi_verse = band(*SEC["Verse1"], 6000, 12000)
    side_verse = side_ratio(*SEC["Verse1"])
    side_chorus = side_ratio(*SEC["Chorus1"])
    # bass fundamentals: dominant FFT peaks in Verse1 lo band
    seg = mono[int(SEC["Verse1"][0] * SR):int(SEC["Verse1"][1] * SR)]
    seg = seg - seg.mean()
    X = np.fft.rfft(seg * np.hanning(len(seg)))
    f = np.fft.rfftfreq(len(seg), 1 / SR)
    lo = X[(f >= 60) & (f <= 250)]
    flo = f[(f >= 60) & (f <= 250)]
    top = flo[np.argsort(np.abs(lo))[-3:]]
    print(f"  intro hi 6-12kHz={hi_intro:.3f} vs verse={hi_verse:.3f} "
          f"(intro darker={hi_intro < hi_verse})")
    print(f"  side ratio verse={side_verse:.3f} vs chorus={side_chorus:.3f} "
          f"(wider={side_chorus > side_verse})")
    print(f"  bass FFT peaks: {[round(float(t), 1) for t in sorted(top)]} Hz")

    stats = {
        "sr": SR, "duration_s": round(length / SR, 2),
        "lufs": round(lufs, 2), "peak": round(peak, 4),
        "rms": round(rms, 4), "silence_ratio": round(silent, 4),
        "intro_hi_vs_verse": round(hi_intro, 3),
        "verse_hi": round(hi_verse, 3),
        "side_verse": round(side_verse, 3), "side_chorus": round(side_chorus, 3),
        "bass_fft_peaks_hz": [round(float(t), 1) for t in sorted(top)],
        "effects": ["reverb(Accordion/Strings/Guitar/Drums)",
                    "slap_delay(Lead 120ms)", "bass clean",
                    "intro fade-in + LPF 2400", "chorus widen 1.5 + bright +1.5dB",
                    "outro LPF 1300 + fade-out", "stereo_imager",
                    "LUFS -14", "limiter -1dB"],
    }
    with open(os.path.join(PROJ, "Analysis", "production_stats.json"), "w") as fh:
        json.dump(stats, fh, indent=2)
    print("== wrote", OUT_OGG, "==")


if __name__ == "__main__":
    main()
