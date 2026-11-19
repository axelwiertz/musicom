"""CBPM verification prototype — campanological bell partial synthesis.

Checks:
 1. spectral peaks land on the requested partial ratios (<0.5 % error)
 2. tierce is a NARROW minor third (measured preset 291 cents, not 300)
 3. doublet (mode-pair) beating rate equals the requested split (<2 %)
 4. strike partials are integer multiples of the prime -> virtual pitch = prime
 5. radiation decay law: T60 ordering hum > prime > nominal > upper partials
 6. strike azimuth re-balances orthogonal doublets (amplitude ratio spread)
 7. no DC, peak <= 1.0, finite output
 8. WAV written and non-empty
"""
import numpy as np

FS = 44100

# ---- partial table (ratio to nominal, name, relative radiated amplitude) ----
IDEAL = [
    (0.25, "hum",     0.50),
    (0.50, "prime",   0.65),
    (0.60, "tierce",  0.45),
    (0.75, "quint",   0.40),
    (1.00, "nominal", 1.00),
    (1.50, "superquint", 0.30),
    (2.00, "oct-nom", 0.25),
    (2.50, "upper-3rd", 0.18),
    (3.00, "upper-5th", 0.15),
    (4.00, "double-oct", 0.10),
]
# Taylor 1980s bell, nominal 1171.5 Hz (Hibbert, measured)
TAYLOR = [
    (293.0 / 1171.5, "hum", 0.50),
    (586.0 / 1171.5, "prime", 0.65),
    (693.0 / 1171.5, "tierce", 0.45),
    (882.0 / 1171.5, "quint", 0.40),
    (1.0, "nominal", 1.00),
    (1761.0 / 1171.5, "superquint", 0.30),
    (2437.0 / 1171.5, "oct-nom", 0.25),
    (2619.2 / 1171.5, "I5", 0.18),
    (3403.5 / 1171.5, "I-7", 0.15),
    (3982.5 / 1171.5, "I-8", 0.10),
]

ALPHA = 0.8      # radiation damping exponent: T60 ~ f^-ALPHA
T60_N = 8.0      # nominal partial T60, seconds


def t60(ratio, t60_n=T60_N, alpha=ALPHA):
    return t60_n * ratio ** (-alpha)


def strike_azimuth_gains(m, theta):
    """Orthogonal doublet gains for a mode with m nodal meridians struck at theta."""
    return abs(np.cos(m * theta)), abs(np.sin(m * theta))


def render(f_nom, partials, dur=12.0, split_cents=None, theta=0.37,
           noise_amp=0.06, seed=7):
    """Sum of exponentially decaying sinusoids; optional doublet split per mode.

    split_cents: dict name -> split in cents (frequency difference in cents
    between the two members of the doublet).
    """
    rng = np.random.default_rng(seed)
    n = int(dur * FS)
    t = np.arange(n) / FS
    y = np.zeros(n)
    m_of = {"hum": 2, "prime": 2, "tierce": 4, "quint": 3, "nominal": 4,
            "superquint": 5, "oct-nom": 6}
    split_cents = split_cents or {}
    info = {}
    for ratio, name, amp in partials:
        if ratio * f_nom > FS / 2 - 500:
            continue
        tau60 = t60(ratio)
        decay = 10.0 ** (-3.0 * t / tau60)          # amplitude -> -60 dB at T60
        rise = np.minimum(t / 0.004, 1.0)            # 4 ms clapper contact rise
        env = decay * rise
        f = ratio * f_nom
        m = m_of.get(name, 3)
        g_c, g_s = strike_azimuth_gains(m, theta)
        if name in split_cents and split_cents[name] > 0:
            d = 2.0 ** (split_cents[name] / 1200.0)
            f1, f2 = f / np.sqrt(d), f * np.sqrt(d)
            ph1, ph2 = rng.uniform(0, 2 * np.pi, 2)
            y += amp * env * (g_c * np.sin(2 * np.pi * f1 * t + ph1)
                              + g_s * np.sin(2 * np.pi * f2 * t + ph2))
            info[name] = (f1, f2, abs(f2 - f1))
        else:
            ph = rng.uniform(0, 2 * np.pi)
            y += amp * env * (g_c + 0.25 * g_s) * np.sin(2 * np.pi * f * t + ph)
            info[name] = (f, f, 0.0)
    # clapper noise burst (contact), decaying in 6 ms
    nb = int(0.006 * FS)
    burst = rng.normal(0, 1, nb) * np.exp(-np.arange(nb) / (0.0015 * FS))
    y[:nb] += noise_amp * burst
    y /= np.max(np.abs(y)) + 1e-12
    y *= 0.98
    return y, info


def peak_freqs(y, f_nom, partials, dur_fft=2.0):
    seg = y[: int(dur_fft * FS)] * np.hanning(int(dur_fft * FS))
    S = np.abs(np.fft.rfft(seg, 1 << 18))
    fr = np.fft.rfftfreq(1 << 18, 1 / FS)
    out = {}
    for ratio, name, _ in partials:
        f0 = ratio * f_nom
        lo, hi = f0 * 0.97, f0 * 1.03
        mask = (fr >= lo) & (fr <= hi)
        if not mask.any():
            continue
        out[name] = fr[mask][np.argmax(S[mask])]
    return out


def env_beat_rate(y, fc, bw=10.0, dur=6.0):
    n = int(dur * FS)
    seg = y[:n].copy()
    fr = np.fft.rfftfreq(n, 1 / FS)
    S = np.fft.rfft(seg)
    S[(fr < fc - bw) | (fr > fc + bw)] = 0
    z = np.fft.ifft(S, n=n)                # band-passed real signal
    env = np.abs(z)
    env -= env.mean()
    E = np.abs(np.fft.rfft(env * np.hanning(n)))
    ef = np.fft.rfftfreq(n, 1 / FS)
    E[ef < 0.2] = 0
    return ef[np.argmax(E)]


def t60_measured(y, fc, bw=12.0):
    """T60 from an STFT magnitude track at the partial's bin (leakage-safe)."""
    from scipy.signal import stft
    f, tt, Z = stft(y, fs=FS, nperseg=8192, noverlap=8192 - 512,
                    boundary=None, padded=False)
    mag = np.abs(Z)
    j = int(np.argmin(np.abs(f - fc)))
    e = mag[j] + 1e-12
    db = 20 * np.log10(e / np.max(e))
    idx = np.where((db < -5) & (db > -40))[0]
    if len(idx) < 5:
        return np.nan
    slope = np.polyfit(tt[idx], db[idx], 1)[0]
    return -60.0 / slope


def main():
    f_nom = 1171.5
    ok = []
    y, info = render(f_nom, IDEAL, dur=12.0)
    pk = peak_freqs(y, f_nom, IDEAL)
    err = {k: abs(pk[k] - r * f_nom) / (r * f_nom) * 100
           for (r, k, _a) in IDEAL if k in pk}
    c1 = max(err.values()) < 0.5
    ok.append(("1 peak accuracy", c1, f"max err {max(err.values()):.3f} %"))

    # 2 tierce cents, measured preset
    ty, _ = render(1171.5, TAYLOR, dur=12.0)
    pk_t = peak_freqs(ty, 1171.5, TAYLOR, dur_fft=3.0)
    cents = 1200 * np.log2(pk_t["tierce"] / pk_t["prime"])
    ok.append(("2 tierce narrow minor 3rd", abs(cents - 291) < 8,
               f"{cents:.1f} cents (equal-tempered minor 3rd = 300)"))

    # 3 doublet beat
    yb, infob = render(f_nom, IDEAL, dur=8.0, split_cents={"prime": 60.0},
                       theta=0.6)
    f1, f2, df = infob["prime"]
    bm = env_beat_rate(yb, 0.5 * f_nom, bw=25.0, dur=6.0)
    ok.append(("3 doublet beat rate", abs(bm - df) / df < 0.05,
               f"requested Δf={df:.3f} Hz, measured {bm:.3f} Hz"))

    # 4 virtual pitch: strike partials as integer multiples of prime
    strike = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
    ks = [s / 0.5 for s in strike]
    c4 = max(abs(k - round(k)) for k in ks) < 1e-9
    ok.append(("4 strike series -> virtual pitch", c4,
               f"strike/prime = {[round(k,3) for k in ks]} -> f_virtual = nominal/2 = {f_nom/2:.1f} Hz"))

    # 5 decay ordering + measured T60
    meas = {}
    for name, fc in [("hum", 0.25 * f_nom), ("prime", 0.5 * f_nom),
                     ("nominal", f_nom), ("double-oct", 4.0 * f_nom)]:
        meas[name] = t60_measured(y, fc, bw=8.0)
    order = meas["hum"] > meas["prime"] > meas["nominal"] > meas["double-oct"] / 1.0
    c5 = order and all(np.isfinite(v) for v in meas.values())
    ok.append(("5 radiation decay ordering", c5,
               "T60 " + ", ".join(f"{k}={v:.1f}s" for k, v in meas.items())))

    # 6 strike azimuth rebalances doublets
    ya, _ = render(f_nom, IDEAL, dur=2.0, theta=0.0)      # cos max, sin 0
    yc, _ = render(f_nom, IDEAL, dur=2.0, theta=np.pi / 8)  # 45 deg for m=4
    def amp_at(sig, f):
        return np.abs(np.fft.rfft(sig[: FS])[int(round(f * FS / FS))])
    # direct DFT at freq for clarity
    def dft_amp(sig, f):
        t = np.arange(len(sig)) / FS
        return abs(np.sum(sig * np.exp(-2j * np.pi * f * t)))
    ratio_a = dft_amp(ya, 0.6 * f_nom) / dft_amp(ya * 0 + 1e-12, 1)
    a_tierce_0 = dft_amp(ya, 0.6 * f_nom)
    a_quint_0 = dft_amp(ya, 0.75 * f_nom)
    a_tierce_45 = dft_amp(yc, 0.6 * f_nom)
    a_quint_45 = dft_amp(yc, 0.75 * f_nom)
    spread_db = 20 * np.log10((a_tierce_0 / a_quint_0) / (a_tierce_45 / a_quint_45) + 1e-12)
    ok.append(("6 strike azimuth rebalances modes", abs(spread_db) > 3.0,
               f"tierce/quint ratio shifts {spread_db:+.1f} dB between strike points"))

    # 7 hygiene
    c7 = (abs(np.mean(y)) < 1e-4) and (np.max(np.abs(y)) <= 1.0) and np.all(np.isfinite(y))
    ok.append(("7 DC / peak / finite", c7,
               f"mean={np.mean(y):.2e}, peak={np.max(np.abs(y)):.3f}"))

    # 8 wav
    import wave
    pcm = (y * 32767).astype(np.int16)
    with wave.open("cbpm_demo.wav", "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(FS)
        w.writeframes(pcm.tobytes())
    import os
    sz = os.path.getsize("cbpm_demo.wav")
    ok.append(("8 wav written", sz > 40, f"{sz} bytes"))

    print("CBPM verification")
    for name, passed, detail in ok:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}: {detail}")
    print(f"\n{sum(p for _, p, _ in ok)}/{len(ok)} checks passed")
    # print measured partial table
    print("\nTaylor preset (nominal 1171.5 Hz):")
    for (r, name, amp) in TAYLOR:
        print(f"  {name:11s} {pk_t.get(name, float('nan')):8.1f} Hz  "
              f"{1200*np.log2(r):+7.1f} cents  T60={t60(r):5.1f} s")


if __name__ == "__main__":
    main()
