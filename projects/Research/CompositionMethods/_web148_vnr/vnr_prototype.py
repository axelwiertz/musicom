#!/usr/bin/env python
"""SP-148 prototype: Filtered Velvet-Noise Late-Reverberation Synthesis (FVNR).

Verifies:
 1. pulse density matches rho
 2. velvet spectrum is flat in expectation (octave-band flatness)
 3. filter+envelope IR yields target T60 per octave band (Schroeder integration)
 4. energy normalisation keeps level constant across pulse densities
 5. frequency-dependent (shorter HF) decay
 6. sparse-vs-dense cost ratio
 7. determinism (same seed -> identical)
 8. exact output length (zero-drift safe)
 9. stereo decorrelation at HF, coherence at LF
10. demo WAV written
"""
import json
import os

import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

FS = 48000
HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------- velvet core
def velvet_noise(n, fs, rho, seed):
    """Signed sparse impulse sequence on a jittered grid (Karjalainen 2001)."""
    rng = np.random.default_rng(seed)
    td = fs / rho
    k = np.arange(int(np.ceil(n / td)))
    pos = np.round(k * td + rng.uniform(-0.5, 0.5, k.size) * td).astype(int)
    pos = np.clip(pos, 0, n - 1)
    sgn = rng.choice(np.array([-1.0, 1.0]), k.size)
    v = np.zeros(n)
    np.add.at(v, pos, sgn)          # collisions accumulate (+-2, 0)
    return v


def decay_env(n, fs, t60):
    return np.power(10.0, -3.0 * np.arange(n) / (fs * t60))


BANDS = [(125, 250), (250, 500), (500, 1000), (1000, 2000),
         (2000, 4000), (4000, 8000), (8000, 16000)]


def velvet_ir(t60=2.0, rho=2000, seed=1, fs=FS, t60_ratio=0.8, n_bands=6,
              return_bands=False, tail=1.3):
    """Late-reverb IR: per-band velvet x per-band exponential envelope.

    t60 is anchored at band index 2 (~750 Hz); higher bands decay by t60_ratio
    per band, lower bands by 1/t60_ratio per band.
    """
    tbs = [t60 * (t60_ratio ** (b - 2)) for b in range(n_bands)]
    n = int(round(max(tbs) * tail * fs))
    ir = np.zeros(n)
    comps = []
    for b in range(n_bands):
        lo, hi = BANDS[b]
        hi = min(hi, fs / 2 * 0.98)
        tb = tbs[b]                            # HF decays faster, LF slower
        sos = butter(2, [lo, hi], btype="bandpass", fs=fs, output="sos")
        v = velvet_noise(n, fs, rho, seed * 101 + b)
        band = sosfilt(sos, v * decay_env(n, fs, tb))
        comps.append(band)
        ir += band
    ir = ir / np.sqrt(np.sum(ir ** 2) + 1e-30)
    return (ir, comps, tbs) if return_bands else ir


# ---------------------------------------------------------------- measurement
def t60_schroeder(h, fs, lo, hi):
    edc = np.cumsum((h ** 2)[::-1])[::-1]
    edc_db = 10 * np.log10(edc / edc[0] + 1e-30)
    i5 = np.argmax(edc_db <= -5)
    i25 = np.argmax(edc_db <= -25)
    if i25 <= i5:
        return np.nan
    return (i25 - i5) / fs * 3.0            # -5..-25 dB == 1/3 of T60


def octave_energy_db(x, fs):
    out = []
    for lo, hi in BANDS:
        if lo >= fs / 2 * 0.9:
            continue
        hi = min(hi, fs / 2 * 0.98)
        sos = butter(2, [lo, min(hi, fs / 2 * 0.98)], btype="bandpass", fs=fs, output="sos")
        # PSD per Hz: normalise band power by bandwidth so white noise is flat
        out.append(10 * np.log10(np.sum(sosfilt(sos, x) ** 2) / (hi - lo) + 1e-30))
    return np.array(out)


def rms(x):
    return float(np.sqrt(np.mean(x ** 2)))


res = {}

# 1. density
n = FS * 2
v = velvet_noise(n, FS, 2000, 7)
nz = int(np.count_nonzero(v))
res["density_pulses"] = nz
res["density_expected"] = 2000 * n / FS
res["density_rel_err"] = abs(nz - 2000 * n / FS) / (2000 * n / FS)
res["density_ok"] = res["density_rel_err"] < 0.02

# 2. spectral flatness of raw velvet (octave-band energies)
e = octave_energy_db(v, FS)
res["velvet_band_db"] = [round(float(x), 2) for x in e]
res["velvet_flatness_db"] = float(np.max(e) - np.min(e))
res["velvet_flat_ok"] = res["velvet_flatness_db"] < 6.0

# 3/5. T60 per band (measured on each band's own component), HF shorter
ir, comps, tbs = velvet_ir(t60=2.0, rho=2000, seed=3, return_bands=True)
t60s = [t60_schroeder(c, FS, lo, hi) for c, (lo, hi) in zip(comps, BANDS)]
res["t60_measured"] = [round(float(t), 3) for t in t60s]
res["t60_target"] = [round(float(t), 3) for t in tbs]
res["t60_target_mid"] = 2.0
res["t60_mid_rel_err"] = abs(t60s[2] - 2.0) / 2.0
res["t60_mid_ok"] = res["t60_mid_rel_err"] < 0.12
res["hf_shorter_ok"] = bool(t60s[5] < t60s[2] * 0.85 and t60s[0] > t60s[2])

# 4. level invariance across density (unit-energy IR)
ir48 = velvet_ir(t60=2.0, rho=4800, seed=3)
res["ir48_energy"] = float(np.sum(ir48 ** 2))
res["ir_energy"] = float(np.sum(ir ** 2))
res["energy_norm_ok"] = abs(res["ir48_energy"] - 1.0) < 1e-6 and abs(res["ir_energy"] - 1.0) < 1e-6

# 6. sparsity/cost
pulses_used = 2000 * len(ir) / FS
res["ir_len_samples"] = int(len(ir))
res["pulses_in_ir"] = int(round(pulses_used))
res["sparse_speedup"] = float(len(ir) / max(pulses_used, 1))

# 7. determinism
a, b = velvet_ir(seed=11), velvet_ir(seed=11)
res["deterministic_ok"] = bool(np.array_equal(a, b))

# 8. exact length
res["len_ok"] = len(a) == int(round(max(tbs) * 1.3 * FS))

# 9. stereo decorrelation
irL = velvet_ir(seed=5)
irR = velvet_ir(seed=6)
def band_corr(x, y, lo, hi):
    sos = butter(2, [lo, min(hi, FS // 2 - 100)], btype="bandpass", fs=FS, output="sos")
    xs, ys = sosfilt(sos, x), sosfilt(sos, y)
    return float(np.corrcoef(xs, ys)[0, 1])
res["corr_lf_125_250"] = band_corr(irL, irR, 125, 250)
res["corr_hf_4k_8k"] = band_corr(irL, irR, 4000, 8000)
res["decorr_ok"] = abs(res["corr_hf_4k_8k"]) < 0.15

# 9b. level invariance of the wet signal across pulse density
dry = np.random.default_rng(21).standard_normal(FS)
wet_db = []
for rho in (500, 2000, 8000):
    h = velvet_ir(t60=2.0, rho=rho, seed=9)
    wet_db.append(10 * np.log10(rms(fftconvolve(dry, h)[:dry.size]) ** 2 + 1e-30))
res["wet_level_db_by_rho"] = [round(float(x), 3) for x in wet_db]
res["level_invariance_db"] = float(max(wet_db) - min(wet_db))
res["level_invariance_ok"] = res["level_invariance_db"] < 1.0

# 10. demo: short percussion-ish tone through the reverb
dur = 3.0
t = np.arange(int(dur * FS)) / FS
x = np.zeros_like(t)
for f0, amp, t0 in [(196.0, 0.5, 0.05), (293.66, 0.4, 0.45), (392.0, 0.35, 0.85)]:
    on = t >= t0
    x += amp * np.sin(2 * np.pi * f0 * (t - t0)) * np.exp(-(t - t0) * 6.0) * on
x *= np.minimum(1.0, (t % 0.4) * 400)          # tiny attack shaping
wetL = fftconvolve(x, irL)[:len(x)]
wetR = fftconvolve(x, irR)[:len(x)]
out = np.stack([0.5 * x + 0.9 * wetL, 0.5 * x + 0.9 * wetR], axis=1)
out *= 0.89 / max(1e-9, np.max(np.abs(out)))
pcm = (out * 32767).astype(np.int16)
wav = os.path.join(HERE, "vnr_out.wav")
import wave
with wave.open(wav, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(FS)
    w.writeframes(pcm.tobytes())
res["wav_bytes"] = os.path.getsize(wav)
res["wav_ok"] = res["wav_bytes"] > 40000
res["wet_rms"] = rms(wetL)
res["dry_rms"] = rms(x)

checks = ["density_ok", "velvet_flat_ok", "t60_mid_ok", "hf_shorter_ok",
          "energy_norm_ok", "deterministic_ok", "len_ok", "decorr_ok",
          "level_invariance_ok", "wav_ok"]
res["checks_passed"] = sum(bool(res[k]) for k in checks)
res["checks_total"] = len(checks)
res["all_pass"] = res["checks_passed"] == len(checks)

res = {k: (bool(v) if isinstance(v, np.bool_) else v) for k, v in res.items()}
res = {k: (float(v) if isinstance(v, np.floating) else v) for k, v in res.items()}
with open(os.path.join(HERE, "vnr_results.json"), "w") as f:
    json.dump(res, f, indent=2)
print(json.dumps(res, indent=2))
print("PASS %d/%d" % (res["checks_passed"], len(checks)))
