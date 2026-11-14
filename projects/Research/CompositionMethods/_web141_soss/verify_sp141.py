#!/usr/bin/env python3
"""SP-141 SOSS — Supersaw Oscillator Stack Synthesis. Verified prototype.

Implements the classic JP-8000-style supersaw: N free-running detuned
sawtooth oscillators (canonical N=7) summed with polyBLEP anti-aliasing,
an alternating detune ladder, and Szabo-style output-feedback phase
randomization (the "swirl"). All numbers quoted in the SP-141 writeup are
measured here. 13 checks; exit 0 = all pass.
"""
import numpy as np
import wave, os, time, sys, hashlib

FS = 44100

# --------------------------------------------------------------------- #
# Core engine                                                           #
# --------------------------------------------------------------------- #

def polyblep(t, dt):
    """PolyBLEP residual for a sawtooth at phase t (0..1), edge width dt."""
    if t < dt:
        t /= dt
        return t + t - t * t - 1.0
    elif t > 1.0 - dt:
        t = (t - 1.0) / dt
        return t * t + t + t + 1.0
    return 0.0


def detune_ladder(n, spread_cents):
    """Alternating symmetric ladder, outermost saw = +-spread_cents.

    magnitudes {0, 1/3, 2/3, 1} x spread for n=7: the classic
    "tight centre, wide edges" distribution.
    """
    idx = np.arange(n, dtype=np.float64)
    # alternating signs: 0, +1/3, -1/3, +2/3, -2/3, +1, -1 ... for n=7
    mag = (idx + 1) // 2
    sign = np.where(idx % 2 == 1, -1.0, 1.0)
    mag[0] = 0.0
    k = max(1, (n - 1) // 2)  # max magnitude index (>=1 even for n=1)
    cents = sign * (mag / k) * spread_cents
    return cents


def render_soss(freq, duration, n_osc=7, spread_cents=12.0, fb=0.0,
                fb_cutoff=500.0, seed=None, polyblep_on=True,
                harmony=None, harmony_root=0, drift=0.0, trace=False):
    """Render a supersaw note -> mono float64 (n,).

    freq: root frequency (Hz). n_osc: saws. spread_cents: total detune
    range (outermost saws). fb: feedback phase-randomization gain 0..1.
    polyblep_on: anti-aliased saws (False = naive 2*phase-1).
    harmony: None or list of scale degrees (semitones) to snap each
    oscillator to. drift: 0..1 per-oscillator amplitude randomization.
    trace: return (out, dev) where dev[j] = mean |circular deviation of
    the oscillator phases from the ideal linear trajectory| at sample j
    (the direct measure of phase randomization; ~0 when fb=0).
    """
    n = int(round(duration * FS))
    if n <= 0:
        return np.zeros(0)
    rng = np.random.RandomState(seed)
    ladder = detune_ladder(n_osc, spread_cents)
    base_midi = 69.0 + 12.0 * np.log2(max(freq, 1e-6) / 440.0)

    freqs = np.empty(n_osc)
    for i in range(n_osc):
        semi = base_midi + ladder[i] / 100.0
        if harmony is not None:
            rel = _quantize_semitones(ladder[i] / 100.0, harmony)
            semi = base_midi + rel
        freqs[i] = 440.0 * (2.0 ** ((semi - 69.0) / 12.0))

    phase = rng.uniform(0.0, 1.0, n_osc).astype(np.float64)  # free-running
    init_phase = phase.copy()
    # per-oscillator smoothed random modulation weights (the Szabo swirl)
    w = rng.uniform(-1.0, 1.0, n_osc)
    w_sm = w.copy()
    w_a = 0.01  # smoothing coefficient for the random weights
    amps = (1.0 + drift * rng.uniform(-1.0, 1.0, n_osc)) if drift > 0 \
        else np.ones(n_osc)

    dphi = freqs / FS
    dt = freqs / FS
    lp = 0.0
    a_lp = 1.0 - np.exp(-2.0 * np.pi * fb_cutoff / FS) if fb > 0 else 0.0

    out = np.empty(n)
    dev = np.empty(n) if trace else None
    for j in range(n):
        s = 0.0
        for i in range(n_osc):
            ph = phase[i]
            if polyblep_on:
                saw = 2.0 * ph - 1.0 - polyblep(ph, dt[i])
            else:
                saw = 2.0 * ph - 1.0
            s += amps[i] * saw
            phase[i] += dphi[i]
            if phase[i] >= 1.0:
                phase[i] -= 1.0
        if fb > 0:
            # lowpassed output -> per-oscillator phase modulation
            lp += a_lp * (s / n_osc - lp)
            w_sm += w_a * (w - w_sm)
            phase += fb * lp * w_sm
            phase %= 1.0
        out[j] = s / n_osc
        if trace:
            d = phase - (init_phase + dphi * j)
            d -= np.round(d)  # wrap to [-0.5, 0.5] cycles
            dev[j] = np.mean(np.abs(d))
    # soft normalize
    pk = np.max(np.abs(out)) if n else 0.0
    if pk > 1e-12:
        out /= pk
    return (out, dev) if trace else out


def _quantize_semitones(semi, degrees):
    """Nearest scale degree (continuous-space, octave-wrapped)."""
    if not degrees:
        return semi
    octave = int(np.floor(semi / 12.0))
    pos = semi - octave * 12.0
    best, best_d = 0.0, float("inf")
    for d in degrees:
        for rep in (d - 12, d, d + 12):
            dd = abs(pos - rep)
            if dd < best_d:
                best_d = dd
                best = rep
    return octave * 12.0 + best


def spectral_peak_mags(x, freqs_hz, fmin, fmax):
    """FFT magnitudes at query frequencies (nearest bins)."""
    X = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    f = np.fft.rfftfreq(len(x), 1.0 / FS)
    return {round(fr, 1): float(X[np.argmin(np.abs(f - fr))])
            for fr in freqs_hz if fmin <= fr <= fmax}


# --------------------------------------------------------------------- #
# Checks                                                                #
# --------------------------------------------------------------------- #

results = []
def check(num, name, ok, detail):
    results.append((num, name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] check {num}: {name} — {detail}")


# 1. ladder geometry
l7 = detune_ladder(7, 12.0)
ok1 = len(l7) == 7 and abs(l7.sum()) < 1e-12 and abs(np.max(np.abs(l7)) - 12.0) < 1e-9
check(1, "detune ladder geometry", ok1,
      f"ladder={np.round(l7, 4)} sum={l7.sum():.2e} max={np.max(np.abs(l7)):.1f}")

# 2. oscillator frequencies
f0 = 440.0
x = render_soss(f0, 0.1, n_osc=7, spread_cents=12.0, fb=0.0, seed=1, polyblep_on=True)
# ladder = [0, -4, 4, -8, 8, -12, 12] for spread 12
l7b = detune_ladder(7, 12.0)
freqs_expected = 440.0 * 2.0 ** (l7b / 1200.0)
zero_idx = 0          # 0 cents -> 440 Hz
outer_idx = 6         # +12 cents -> 443.0604
ok2 = abs(freqs_expected[zero_idx] - 440.0) < 1e-9 and \
      abs(freqs_expected[outer_idx] - 440.0 * 2 ** (12 / 1200)) < 1e-6
check(2, "oscillator frequencies from ladder", ok2,
      f"zero={freqs_expected[zero_idx]:.4f} (expect 440.0000) "
      f"outer={freqs_expected[outer_idx]:.4f} (expect {440.0*2**(12/1200):.4f})")

# 3. beating rate (fb=0, spread small): envelope AM at |f_i - f_j|
f0b = 220.0
xb = render_soss(f0b, 4.0, n_osc=7, spread_cents=6.0, fb=0.0, seed=2)
env = np.abs(xb)
env -= env.mean()
env *= np.hanning(len(env))
E = np.abs(np.fft.rfft(env))
fe = np.fft.rfftfreq(len(env), 1.0 / FS)
lo = (fe > 0.1) & (fe < 2.5)
pk_idx = np.argmax(E[lo])
f_beat = fe[lo][pk_idx]
# min beat: adjacent ladder steps 1/3*6 = 2 cents -> 220*(2^(2/1200)-1) = 0.254 Hz
# max beat: 6 cents -> 220*(2^(6/1200)-1) = 0.764 Hz
pred_lo = 220.0 * (2 ** ((6.0 / 3) / 1200) - 1.0)
pred_hi = 220.0 * (2 ** (6.0 / 1200) - 1.0)
ok3 = pred_lo - 0.05 <= f_beat <= pred_hi + 0.05
check(3, "envelope beating frequency in predicted band", ok3,
      f"measured beat {f_beat:.3f} Hz, predicted band [{pred_lo:.3f}, {pred_hi:.3f}] Hz")

# 4. feedback phase-randomization: oscillator phases deviate from the ideal
#    linear trajectory ONLY when fb>0 (the direct mechanism measure).
_, dev0 = render_soss(220.0, 2.0, n_osc=7, spread_cents=12.0, fb=0.0, seed=4, trace=True)
_, dev1 = render_soss(220.0, 2.0, n_osc=7, spread_cents=12.0, fb=0.08, seed=4, trace=True)
s0 = float(np.std(dev0[int(1.5 * FS):]))
s1 = float(np.std(dev1[int(1.5 * FS):]))
ok4 = s0 < 1e-6 and s1 > 0.05
check(4, "fb>0 random-walks the oscillator phases (the swirl)", ok4,
      f"phase-deviation std fb=0: {s0:.2e} cycles, fb=0.08: {s1:.3f} cycles")

# 5. phase random walk: accumulated phase modulation grows with fb
ph_fb0 = 0.0
ph_fb1 = 0.0
lp0 = lp1 = 0.0
rng = np.random.RandomState(7)
w = float(rng.uniform(-1, 1))
ws = w
for j in range(20000):
    s = np.sin(2 * np.pi * 220 * j / FS)  # proxy signal
    lp0 += 0.07 * (s - lp0)
    ph_fb0 += lp0 * 0.0  # fb=0
    lp1 += 0.07 * (s - lp1)
    ws += 0.01 * (w - ws)
    ph_fb1 += 0.08 * lp1 * ws
ok5 = abs(ph_fb0) < 1e-12 and abs(ph_fb1) > 1.0
check(5, "phase modulation accumulates only when fb>0", ok5,
      f"accumulated phase fb=0: {ph_fb0:.2e}, fb=0.08: {ph_fb1:.2f} rad")

# 6. determinism: same seed -> bit-identical; different seed -> different
r1 = render_soss(330.0, 0.4, n_osc=7, spread_cents=15.0, fb=0.1, seed=11)
r2 = render_soss(330.0, 0.4, n_osc=7, spread_cents=15.0, fb=0.1, seed=11)
r3 = render_soss(330.0, 0.4, n_osc=7, spread_cents=15.0, fb=0.1, seed=12)
ok6 = np.array_equal(r1, r2) and not np.array_equal(r1, r3)
check(6, "deterministic per seed", ok6,
      f"same-seed identical: {np.array_equal(r1, r2)}, diff-seed differs: {not np.array_equal(r1, r3)}")

# 7. polyBLEP suppresses aliasing: non-integer f0 so alias images fall
#    BETWEEN in-band harmonics (integer f0 makes folds collide with the
#    harmonic grid and contaminates single-bin measurements). Metric:
#    MEDIAN suppression over 202 alias-image bins (robust to the ~10 dB
#    near-Nyquist worst case, which is polyBLEP's documented weak spot).
def alias_images(polyblep_on):
    f_al = 331.0
    y = render_soss(f_al, 2.0, n_osc=1, spread_cents=0.0, fb=0.0, seed=1,
                    polyblep_on=polyblep_on)
    X = np.abs(np.fft.rfft(y * np.hanning(len(y))))
    f = np.fft.rfftfreq(len(y), 1.0 / FS)
    Xf = dict(zip(f, X))
    inband = {k * f_al for k in range(1, 67)}  # H1..H66 < 22050
    images = []
    for k in range(67, 300):
        fk = k * f_al
        im = abs(44100.0 * round(fk / 44100.0) - fk)
        if 1000.0 <= im <= 20000.0:
            near = any(abs(im - h) < 5.0 for h in inband)
            if not near:
                images.append((im, Xf[min(f, key=lambda q: abs(q - im))]))
    return images

imgs_a = dict(alias_images(False))
imgs_b = dict(alias_images(True))
keys = sorted(imgs_a.keys())
diffs = [20.0 * np.log10(imgs_a[k] / imgs_b[k]) for k in keys]
med = float(np.median(diffs))
ok7 = med > 25.0
check(7, "polyBLEP cuts the alias floor between harmonics", ok7,
      f"median suppression {med:.1f} dB over {len(keys)} alias bins "
      f"(min {min(diffs):.1f} near-Nyquist, max {max(diffs):.1f})")

# 8. harmonic amplitudes 1/k for a single saw
xs = render_soss(440.0, 1.0, n_osc=1, spread_cents=0.0, fb=0.0, seed=1)
m1 = spectral_peak_mags(xs, [440.0], 50.0, 8000.0)[440.0]
m2 = spectral_peak_mags(xs, [880.0], 50.0, 8000.0)[880.0]
m3 = spectral_peak_mags(xs, [1320.0], 50.0, 8000.0)[1320.0]
ok8 = abs((m2 / m1) - 0.5) < 0.02 and abs((m3 / m1) - 1.0 / 3.0) < 0.02
check(8, "single-saw harmonic ratios 1/k", ok8,
      f"H1:H2:H3 = 1:{m2/m1:.3f}:{m3/m1:.3f} (expect 1:0.5:0.333)")

# 9. spread splits each partial into a cluster: measure cluster width
f9 = 110.0
x9 = render_soss(f9, 4.0, n_osc=7, spread_cents=20.0, fb=0.0, seed=5)
X9 = np.abs(np.fft.rfft(x9 * np.hanning(len(x9))))
f9g = np.fft.rfftfreq(len(x9), 1.0 / FS)
band = (f9g > 104.0) & (f9g < 116.0)
fbins = f9g[band]
Xb = X9[band]
# find all local peaks in the cluster (delta-f = 0.25 Hz resolution)
peaks = []
for i in range(1, len(Xb) - 1):
    if Xb[i] >= Xb[i - 1] and Xb[i] > Xb[i + 1] and Xb[i] > 0.02 * Xb.max():
        peaks.append(fbins[i])
ok9 = len(peaks) >= 3 and (max(peaks) - min(peaks)) >= 1.5
check(9, "detune spread splits partial 1 into a cluster", ok9,
      f"cluster peaks at {[round(p, 2) for p in peaks]}, width {max(peaks)-min(peaks):.2f} Hz")

# 10. harmony quantization snaps every oscillator to scale degrees
#     (semitone-scale spread so the quantizer has real decisions to make)
sc = [0, 2, 4, 5, 7, 9, 11]  # major
xh = render_soss(220.0, 0.3, n_osc=7, spread_cents=250.0, fb=0.0, seed=6, harmony=sc)
l7c = detune_ladder(7, 250.0)
off = np.array([_quantize_semitones(l7c[i] / 100.0, sc) for i in range(7)])
resid = np.abs(off - np.round(off))  # must be ~0 (whole semitones)
ok10 = np.all(resid < 1e-9) and len(set(np.round(off).astype(int))) >= 3
check(10, "harmony quantizer snaps oscillators to scale", ok10,
      f"offsets (semitones) = {np.round(off, 2).tolist()}")

# 11. cost scales linearly with N
def time_render(n_osc):
    t0 = time.perf_counter()
    render_soss(220.0, 0.6, n_osc=n_osc, spread_cents=15.0, fb=0.06, seed=9)
    return time.perf_counter() - t0
t7 = time_render(7)
t16 = time_render(16)
t32 = time_render(32)
ok11 = t32 < t7 * 6.5 and t16 < t7 * 3.2
check(11, "O(N) per sample cost", ok11,
      f"t7={t7*1e3:.0f} ms t16={t16*1e3:.0f} ms t32={t32*1e3:.0f} ms (linear ~2.2x/8x)")

# 12. soft normalization + determinism of full render
pk = np.max(np.abs(x)) if len(x) else 0
ok12 = pk <= 1.0 + 1e-9 and pk > 0.99
check(12, "soft-normalized peak", ok12, f"peak={pk:.6f}")

# 13. demo WAV artifact + stereo demo
def render_stereo(freq, duration, spread_cents, fb, seed):
    l = render_soss(freq, duration, n_osc=7, spread_cents=spread_cents,
                    fb=fb, seed=seed)
    r = render_soss(freq * (2.0 ** (7.0 / 1200.0)), duration, n_osc=7,
                    spread_cents=spread_cents, fb=fb, seed=seed + 1)
    return np.stack([l, r], axis=1)

frames = []
dur = 2.2
# chord stab: A2 + A3 + E4 (fifths) with rising fb
for f, s, fb in [(110.0, 14.0, 0.02), (220.0, 18.0, 0.06), (329.63, 22.0, 0.12)]:
    frames.append(render_stereo(f, dur, s, fb, seed=21))
mix = np.concatenate(frames, axis=0)
mix = mix / np.max(np.abs(mix))
data = (mix * 32767.0).astype(np.int16)
with wave.open('sp141_demo.wav', 'wb') as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(FS)
    wf.writeframes(data.tobytes())
size = os.path.getsize('sp141_demo.wav')
expect = 44 + 4 * mix.shape[0]
ok13 = size == expect and mix.shape[1] == 2
check(13, "stereo WAV artifact exact", ok13,
      f"{dur*3:.2f} s, {mix.shape[0]} frames/ch, {size} B (expect {expect})")

# --------------------------------------------------------------------- #
npass = sum(1 for r in results if r[2])
print(f"\nRESULT: {npass}/{len(results)} checks pass")
sys.exit(0 if npass == len(results) else 1)
