# -*- coding: utf-8 -*-
"""Production pass — 205-amapiano-study (amapiano-style sound effects + polish).

Pipeline:
  1. render per-track stems (FluidSynth)
  2. per-voice amapiano FX:
       Rhodes   -> lush Schroeder reverb (the spacey amapiano piano)
       LogDrum  -> sub-harmonic generator (adds the deep "log" weight)
       Sub      -> clean (kept centered/mono)
       Lead     -> light reverb (kalimba air)
       Guitar   -> tape delay (echo) + light reverb
       Drums    -> light reverb (clap snap + air)
  3. SFX (synthesized):
       riser (noise + sine sweep up) into the Climax
       sub drop (sine sweep down) into GrooveA
  4. section polish: intro LPF + fade-in, breakdown LPF, outro LPF + fade-out
  5. stereo imaging (mono sub, widen highs)
  6. mastering: LUFS normalize (-14) -> limiter (-1 dB)
"""
import os
import json

import numpy as np

from sound.render import RenderPipeline
from sound.effects.reverb import AlgorithmicReverb
from sound.effects.subharmonic import SubHarmonicGenerator
from sound.effects.filter import StateVariableFilter
from sound.effects.mastering import (StereoImager, Limiter,
                                     normalize_to_lufs, measure_lufs)
from sound.utils.io import read_wav, write_wav

SR = 44100
PROJ = "/opt/data/repos/musicom/projects/Styles/African/205-amapiano-study"
MID = os.path.join(PROJ, "MIDI", "205-amapiano-study.mid")
STEM_DIR = os.path.join(PROJ, "Audio", "stems")
OUT_WAV = os.path.join(PROJ, "Audio", "205-amapiano-study.wav")
OUT_OGG = os.path.join(PROJ, "Audio", "205-amapiano-study.ogg")
SF = "/opt/data/soundfonts/FluidR3_GM.sf2"

# section boundaries (seconds) at 112 BPM, bar = 60/112*4 = 2.142857 s
BAR = 60.0 / 112.0 * 4.0
SEC = {
    "Intro":     (0 * BAR, 4 * BAR),
    "GrooveA":   (4 * BAR, 12 * BAR),
    "GrooveB":   (12 * BAR, 20 * BAR),
    "Breakdown": (20 * BAR, 24 * BAR),
    "Climax":    (24 * BAR, 32 * BAR),
    "Outro":     (32 * BAR, 36 * BAR),
}


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
    """Clean single-tap echo (manual overlay).

    NOTE: do NOT use sound.effects.tape_delay.TapeDelay here — its
    feedback+saturation loop has small-signal gain > 1.0 and self-oscillates
    into full-scale noise (verified: peak 1.34 / RMS 0.96 in silent regions).
    Manual overlay is the safe echo (see musicom-engine-maintenance pitfall).
    """
    mono = a[:, 0] if a.ndim == 2 else a
    d = int(delay_s * SR)
    wet = np.zeros(len(mono))
    wet += mono
    if d < len(mono):
        wet[d:] += feedback * mono[:len(mono) - d]
    return np.column_stack([wet, wet]) * 0.5 + a


# ---------------------------------------------------------------- SFX
def make_riser(dur=2.0, sr=SR):
    n = int(dur * sr)
    t = np.arange(n) / sr
    f = 150.0 * (4000.0 / 150.0) ** (t / dur)          # exp pitch sweep up
    sweep = np.sin(2 * np.pi * np.cumsum(f) / sr)
    noise = np.random.default_rng(7).standard_normal(n)
    env = (t / dur) ** 2.0
    return ((0.5 * sweep + 0.5 * noise) * env).astype(np.float32)


def make_subdrop(dur=1.2, sr=SR):
    n = int(dur * sr)
    t = np.arange(n) / sr
    f = 130.0 * (45.0 / 130.0) ** (t / dur)            # exp pitch sweep down
    sweep = np.sin(2 * np.pi * np.cumsum(f) / sr)
    env = np.sin(np.pi * t / dur) ** 1.5
    return (sweep * env * 0.9).astype(np.float32)


def lp_region(mix, t0, t1, cutoff, xfade=0.06, sr=SR):
    """Lowpass [t0,t1] with short crossfade at both edges."""
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


def fade(mix, t0, t1, g0, g1, sr=SR):
    i0 = int(t0 * sr)
    i1 = int(min(t1 * sr, len(mix)))
    ramp = np.linspace(g0, g1, i1 - i0)
    mix[i0:i1] *= ramp[:, None]
    return mix


def main():
    print("== render stems ==")
    pipeline = RenderPipeline(soundfont_path=SF)
    stems = pipeline.render_stems(MID, STEM_DIR, format="wav")
    print("stems:", sorted(stems.keys()))

    rhodes_p = find_stem(stems, "Electric_Piano_1")
    log_p = find_stem(stems, "Synth_Bass_1")
    sub_p = find_stem(stems, "Synth_Bass_2")
    lead_p = find_stem(stems, "Kalimba")
    gtr_p = find_stem(stems, "Electric_Guitar_clean")
    drums_p = find_stem(stems, "Drums")
    for label, p in [("Rhodes", rhodes_p), ("LogDrum", log_p), ("Sub", sub_p),
                     ("Lead", lead_p), ("Guitar", gtr_p), ("Drums", drums_p)]:
        print(f"  {label}: {os.path.basename(p) if p else 'MISSING'}")

    # load + align to common length
    audio = {}
    length = None
    for label, p in [("Rhodes", rhodes_p), ("LogDrum", log_p), ("Sub", sub_p),
                     ("Lead", lead_p), ("Guitar", gtr_p), ("Drums", drums_p)]:
        a, sr = read_wav(p)
        a = to_stereo(a).astype(np.float64)
        audio[label] = a
        length = len(a) if length is None else min(length, len(a))
    for k in audio:
        audio[k] = audio[k][:length]

    print("== per-voice FX ==")
    rhodes = apply_reverb(audio["Rhodes"], 0.82, 0.35, 0.30)      # spacey piano
    lead = apply_reverb(audio["Lead"], 0.55, 0.30, 0.22)          # kalimba air
    gtr = apply_delay(audio["Guitar"], 0.32, 0.35)                # echo
    gtr = apply_reverb(gtr, 0.60, 0.30, 0.20)                     # + space
    drums = apply_reverb(audio["Drums"], 0.45, 0.40, 0.14)        # clap snap

    # log drum: sub-harmonic weight (deep "log")
    log_mono = audio["LogDrum"][:, 0]
    shg = SubHarmonicGenerator(sample_rate=SR)
    sub_layer = shg.process(log_mono, depth=0.6)
    logdrum = audio["LogDrum"] + 0.55 * np.column_stack([sub_layer, sub_layer])
    print("  log drum sub-harmonic added (depth 0.6)")

    sub = audio["Sub"]

    # ---- mix stems ----
    mix = (1.00 * rhodes + 1.00 * logdrum + 0.95 * sub
           + 0.85 * lead + 0.95 * gtr + 0.95 * drums)

    # ---- SFX placement ----
    riser = make_riser(2.0)
    subdrop = make_subdrop(1.2)
    def place(sfx, t_start, gain):
        i0 = int(t_start * SR)
        i1 = min(i0 + len(sfx), length)
        n = i1 - i0
        if n > 0:
            mix[i0:i1] += gain * np.column_stack([sfx[:n], sfx[:n]])
    place(riser, SEC["Climax"][0] - 2.0, 0.35)     # into climax
    place(subdrop, SEC["GrooveA"][0] - 1.2, 0.5)   # into GrooveA
    print("  SFX placed: riser -> Climax, sub drop -> GrooveA")

    # ---- section polish ----
    mix = lp_region(mix, *SEC["Intro"], cutoff=1600)         # muffled build-in
    mix = lp_region(mix, *SEC["Breakdown"], cutoff=2200)     # mild wash
    mix = lp_region(mix, *SEC["Outro"], cutoff=1200)         # darken + fade
    mix = fade(mix, SEC["Intro"][0], SEC["Intro"][0] + 2.0, 0.0, 1.0)   # fade-in
    mix = fade(mix, SEC["Outro"][1] - 4.0, SEC["Outro"][1], 1.0, 0.0)   # fade-out
    print("  section polish: intro LPF+fade-in, breakdown LPF, outro LPF+fade-out")

    # ---- stereo imaging ----
    imager = StereoImager(sample_rate=SR)
    imager.set_width(0.0, below_hz=100)      # mono sub
    imager.set_width(1.3, above_hz=3000)     # widen highs
    mix = imager.process(mix)
    print("  stereo imaged (mono sub, wide highs)")

    # ---- mastering ----
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

    stats = {
        "sr": SR, "duration_s": round(length / SR, 2),
        "lufs": round(lufs, 2), "peak": round(peak, 4),
        "rms": round(rms, 4), "silence_ratio": round(silent, 4),
        "effects": ["reverb(Rhodes/Lead/Guitar/Drums)", "tape_delay(Guitar)",
                    "sub_harmonic(LogDrum)", "riser->Climax", "subdrop->GrooveA",
                    "section LPF+fades", "stereo_imager", "LUFS -14", "limiter -1dB"],
    }
    with open(os.path.join(PROJ, "Analysis", "production_stats.json"), "w") as f:
        json.dump(stats, f, indent=2)
    print("== wrote", OUT_OGG, "==")


if __name__ == "__main__":
    main()
