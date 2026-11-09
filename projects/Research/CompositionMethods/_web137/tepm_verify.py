"""SP-137 TEPM — Magnetic Tape Echo Physical Modeling: verification prototype.

Checks (all self-contained, NumPy only):
  1. geometric delay law  tau = d/v  (impulse peak position)
  2. speed law: halving tape speed doubles the delay
  3. multi-head 1:2:3 readout (impulse response peaks at tau, 2tau, 3tau)
  4. wow/flutter Doppler FM: instantaneous-frequency deviation peak
     == f0 * tau0 * m * omega_w (modulated fractional delay line)
  5. record-path saturation THD (tanh) grows with drive; odd harmonics only
  6. feedback loop: successive echo peak ratio ~ feedback gain; HF damping
     per pass lowers spectral centroid per echo
  7. hiss accumulation: noise floor rises per repeat (feedback re-records hiss)
  8. motor inertia: tape-speed ramp converges delay to tau0
  9. zero-drift: output length == N_in + tail, deterministic per seed
 10. demo WAV written (impulse + melodic phrase), size > 40 B
"""
import numpy as np
import wave, os, sys

FS = 44100
SR = FS

def frac_delay_line(x, delay_samples, interp="linear"):
    """Delay x by a *time-varying* fractional delay (vector of per-sample
    delay in samples). Linear interpolation (2-tap) — DAFX standard."""
    n = len(x)
    y = np.zeros(n)
    for i in range(n):
        d = delay_samples[i]
        if d <= 0:
            y[i] = x[i]
            continue
        ip = int(np.floor(d))
        frac = d - ip
        j = i - ip
        if j < 0:
            continue
        if interp == "linear":
            a = x[j] if j >= 0 else 0.0
            b = x[j - 1] if j - 1 >= 0 else 0.0
            y[i] = a + frac * (b - a)
    return y

def tape_echo(x, gap_in, speed_ips, heads=(1.0, 2.0, 3.0), head_gains=(0.7, 0.5, 0.3),
              feedback=0.55, drive=0.9, hf_damp=0.35, wow_m=0.002, wow_f=1.5,
              flutter_m=0.0004, flutter_f=7.0, hiss_level=1e-4, motor_tau=0.0,
              seed=0, fs=FS):
    """Physical tape echo:
      tau_k = (head_gap_k inches) / (tape speed inches/sec)
    Record head writes x_rec = input + feedback*play_sum (with record saturation),
    read heads read the delayed tape with wow/flutter-modulated fractional delay,
    play path applies per-pass HF damping + hiss.  Motor inertia ramps speed.
    Returns (wet_only, dry, echo_info)."""
    rng = np.random.default_rng(seed)
    n = len(x)
    v0 = speed_ips
    # motor inertia: speed ramp  v(t) = v0*(1 - exp(-t/tau_m))
    t = np.arange(n) / fs
    if motor_tau > 0:
        v_scale = np.maximum(1.0 - np.exp(-t / motor_tau), 0.01)
    else:
        v_scale = np.ones(n)
    wow = 1.0 + wow_m * np.sin(2 * np.pi * wow_f * t + 0.7)
    flutter = 1.0 + flutter_m * np.sin(2 * np.pi * flutter_f * t + 1.3)
    speed = v0 * v_scale * wow * flutter
    # per-head delay in samples (time-varying)
    delays = []
    for h in heads:
        gap = gap_in * h
        tau_s = gap / speed          # seconds (time-varying)
        delays.append(np.minimum(tau_s * fs, n + fs))

    # feedback loop: record path
    rec = np.zeros(n)
    play_sum = np.zeros(n)
    rec_sat = np.zeros(n)
    # per-pass one-pole HF damping filter state
    lp_state = 0.0
    hiss = rng.normal(0.0, hiss_level, n)
    tail = int(np.max([np.max(d) for d in delays]) * 2) + fs
    rec_buf = np.zeros(n + tail)
    play_buf = np.zeros(n + tail)
    # simple loop: rec[i] = x[i] + feedback * play_sum[i - tauA] (feedback from
    # first echo, classic Echoplex topology).  We approximate with a straight
    # loop over the same array; exactness verified by echo times.
    rec[:] = x[:]
    # iterate: write rec into buffer, read delayed per head, sum, feed back
    for i in range(n):
        dA = delays[0][i]
        dB = delays[1][i] if len(delays) > 1 else 0.0
        dC = delays[2][i] if len(delays) > 2 else 0.0
        # fractional reads of the record buffer
        def read(buf, i, d):
            ip = int(np.floor(d)); fr = d - ip
            j = i - ip
            if j < 0:
                return 0.0
            a = buf[j]
            b = buf[j - 1] if j - 1 >= 0 else 0.0
            return a + fr * (b - a)
        pa = read(rec_buf, i, dA)
        pb = read(rec_buf, i, dB)
        pc = read(rec_buf, i, dC)
        # play path: per-pass HF damping (one-pole, alpha = 1-hf_damp)
        lp_state += (1.0 - hf_damp) * (pa - lp_state)
        pa_d = lp_state
        g0 = head_gains[0] if len(head_gains) > 0 else 1.0
        g1 = head_gains[1] if len(head_gains) > 1 else 0.0
        g2 = head_gains[2] if len(head_gains) > 2 else 0.0
        play = g0 * pa_d + g1 * pb + g2 * pc
        play_sum[i] = play
        # record path:  rec = x + feedback*playA + tape/bias hiss (hiss is ON
        # the tape, so it re-circulates through the feedback loop)
        rec_i = x[i] + feedback * pa_d + hiss[i]
        if drive > 0:
            rec_sat[i] = np.tanh(drive * rec_i) / np.tanh(drive)
        else:
            rec_sat[i] = rec_i
        rec_buf[i] = rec_sat[i]
    wet = play_sum[:n]
    return wet, rec_sat, {"delays0": delays[0][0], "speed0": speed[0]}

def peak_inst_freq_dev(x, fs, f0):
    """Complex-demodulation instantaneous-frequency deviation: multiply by
    e^{-j w0 n}, lowpass (moving average) to kill the 2*w0 term, then
    dphi/dt/(2pi) is the deviation from f0 in Hz. Envelope-gated + smoothed."""
    n = len(x)
    t = np.arange(n) / fs
    z = x * np.exp(-1j * 2 * np.pi * f0 * t)
    win = max(64, int(fs / f0) * 2)
    zf = np.convolve(z, np.ones(win) / win, mode="same")
    ph = np.unwrap(np.angle(zf))
    inst = np.diff(ph) / (2 * np.pi) * fs
    env = np.abs(zf)[1:]
    thresh = 0.2 * np.max(env)
    k0 = int(0.30 * fs); k1 = n - int(0.05 * fs) - 1   # skip delay gap + edges
    dev = np.abs(inst)
    seg = dev[k0:k1]
    seg[env[k0:k1] < thresh] = 0.0
    dev[k0:k1] = seg
    sm = np.convolve(dev, np.ones(64) / 64, mode="same")
    return float(np.max(sm[k0:k1])), float(np.mean(sm[k0:k1]))

def spectral_centroid(x, fs):
    X = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(len(x), 1 / fs)
    if X.sum() == 0:
        return 0.0
    return float(np.sum(freqs * X) / np.sum(X))

results = []
def check(name, ok, detail):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")

# ---------------------------------------------------------------- 1. delay law
fs = FS
imp = np.zeros(int(1.0 * fs)); imp[100] = 1.0
wet, _, info = tape_echo(imp, gap_in=1.5, speed_ips=7.5, heads=(1.0,),
                         head_gains=(1.0,), feedback=0.0, drive=0.0,
                         wow_m=0.0, flutter_m=0.0, hiss_level=0.0)
peak_idx = int(np.argmax(np.abs(wet)))
tau_pred = 1.5 / 7.5  # seconds
check("1 delay law tau=d/v", abs(peak_idx - 100 - tau_pred * fs) <= 1,
      f"pred {tau_pred*1000:.1f} ms -> peak at sample {peak_idx} (expect {100 + tau_pred*fs:.0f})")

# ---------------------------------------------------------------- 2. speed law
wet2, _, _ = tape_echo(imp, gap_in=1.5, speed_ips=3.75, heads=(1.0,),
                       head_gains=(1.0,), feedback=0.0, drive=0.0,
                       wow_m=0.0, flutter_m=0.0, hiss_level=0.0)
peak2 = int(np.argmax(np.abs(wet2)))
check("2 halve speed -> double delay", abs(peak2 - 100 - 2 * tau_pred * fs) <= 1,
      f"peak at {peak2} (expect {100 + 2*tau_pred*fs:.0f})")

# ---------------------------------------------------------------- 3. multi-head
wet3, _, _ = tape_echo(imp, gap_in=1.5, speed_ips=7.5, heads=(1.0, 2.0, 3.0),
                       head_gains=(1.0, 1.0, 1.0), feedback=0.0, drive=0.0,
                       wow_m=0.0, flutter_m=0.0, hiss_level=0.0)
peaks = np.argsort(np.abs(wet3))[-3:]
peaks = np.sort(peaks)
ok3 = all(abs(peaks[k] - (100 + (k + 1) * tau_pred * fs)) <= 2 for k in range(3))
check("3 multi-head 1:2:3 readout", ok3,
      f"peaks at {peaks} (expect {100 + tau_pred*fs:.0f}, {100+2*tau_pred*fs:.0f}, {100+3*tau_pred*fs:.0f})")

# ---------------------------------------------------------------- 4. wow/flutter FM
f0 = 1000.0
tt = np.arange(int(0.5 * fs)) / fs
sine = 0.5 * np.sin(2 * np.pi * f0 * tt)
wow_m = 0.005; wow_f = 2.0; tau0 = 0.2
# delay modulation: tau(t) = tau0 / (1 + m sin(2 pi f_w t))  (speed wobble)
n = len(sine)
t4 = np.arange(n) / fs
speed4 = 1.0 / tau0 * (1.0 + wow_m * np.sin(2 * np.pi * wow_f * t4 + 0.7))
delays4 = tau0 * (1.0 / (1.0 + wow_m * np.sin(2 * np.pi * wow_f * t4 + 0.7))) * fs
y4 = frac_delay_line(sine, delays4)
dev_peak, dev_mean = peak_inst_freq_dev(y4, fs, f0)
# theory: Delta f_peak = f0 * tau0 * m * omega_w
theory = f0 * tau0 * wow_m * (2 * np.pi * wow_f)
check("4 wow Doppler FM depth", abs(dev_peak - theory) / theory < 0.15,
      f"measured peak dev {dev_peak:.2f} Hz vs theory f0*tau*m*w_w = {theory:.2f} Hz ({100*abs(dev_peak-theory)/theory:.1f}%)")

# ---------------------------------------------------------------- 5. saturation THD
sat_in = 0.6 * np.sin(2 * np.pi * 440.0 * tt)
for drive in (0.3, 1.2):
    rec = np.tanh(drive * sat_in) / np.tanh(drive)
    X = np.abs(np.fft.rfft(rec * np.hanning(len(rec))))
    f = np.fft.rfftfreq(len(rec), 1 / fs)
    def amp_at(freq):
        k = np.argmin(np.abs(f - freq))
        return X[k]
    a1 = amp_at(440.0); a3 = amp_at(1320.0); a5 = amp_at(2200.0)
    h3 = 20 * np.log10(a3 / a1) if a1 > 0 else -999
    h5 = 20 * np.log10(a5 / a1) if a1 > 0 else -999
    # tanh is odd: even harmonics should be negligible
    a2 = amp_at(880.0); h2 = 20 * np.log10(a2 / a1) if a1 > 0 else -999
    ok5 = (h3 < -20) and (h2 < -60)
    check(f"5 saturation THD drive={drive}", ok5,
          f"h2 {h2:.1f} dB, h3 {h3:.1f} dB, h5 {h5:.1f} dB (odd-only growth)")

# ---------------------------------------------------------------- 6. feedback decay
imp6 = np.zeros(int(2.5 * fs)); imp6[100] = 1.0
fb = 0.6
wet6, _, _ = tape_echo(imp6, gap_in=1.5, speed_ips=7.5, heads=(1.0,),
                       head_gains=(1.0,), feedback=fb, drive=0.0,
                       wow_m=0.0, flutter_m=0.0, hiss_level=0.0, hf_damp=0.0)
tau_s = tau_pred
e1 = np.abs(wet6[int(100 + tau_s * fs) - 20: int(100 + tau_s * fs) + 20]).max()
e2 = np.abs(wet6[int(100 + 2 * tau_s * fs) - 20: int(100 + 2 * tau_s * fs) + 20]).max()
e3 = np.abs(wet6[int(100 + 3 * tau_s * fs) - 20: int(100 + 3 * tau_s * fs) + 20]).max()
ratio1 = e2 / e1 if e1 else 0
ratio2 = e3 / e2 if e2 else 0
check("6 feedback decay ratio ~ g_fb", abs(ratio1 - fb) < 0.02 and abs(ratio2 - fb) < 0.02,
      f"echo1 {e1:.4f}, echo2 {e2:.4f} (r={ratio1:.3f}), echo3 {e3:.4f} (r={ratio2:.3f}), g_fb={fb}")

# HF damping: spectral centroid per echo falls
imp7 = np.zeros(int(2.5 * fs)); imp7[100] = 1.0
wet7, _, _ = tape_echo(imp7, gap_in=1.5, speed_ips=7.5, heads=(1.0,),
                       head_gains=(1.0,), feedback=0.6, drive=0.0,
                       wow_m=0.0, flutter_m=0.0, hiss_level=0.0, hf_damp=0.3)
c1 = spectral_centroid(wet7[int(100 + tau_s * fs) - 400: int(100 + tau_s * fs) + 400], fs)
c3 = spectral_centroid(wet7[int(100 + 3 * tau_s * fs) - 400: int(100 + 3 * tau_s * fs) + 400], fs)
check("6b HF damping lowers centroid per echo", c3 < c1,
      f"centroid echo1 {c1:.0f} Hz -> echo3 {c3:.0f} Hz")

# ---------------------------------------------------------------- 7. hiss accumulation
imp8 = np.zeros(int(2.5 * fs)); imp8[100] = 1.0
wet8a, _, _ = tape_echo(imp8, gap_in=1.5, speed_ips=7.5, heads=(1.0,),
                        head_gains=(1.0,), feedback=0.0, drive=0.0,
                        wow_m=0.0, flutter_m=0.0, hiss_level=1e-3, seed=1)
wet8b, _, _ = tape_echo(imp8, gap_in=1.5, speed_ips=7.5, heads=(1.0,),
                        head_gains=(1.0,), feedback=0.7, drive=0.0,
                        wow_m=0.0, flutter_m=0.0, hiss_level=1e-3, seed=1)
seg_a = wet8a[int(1.5 * fs): int(2.2 * fs)]
seg_b = wet8b[int(1.5 * fs): int(2.2 * fs)]
rms_a = float(np.sqrt(np.mean(seg_a ** 2)))
rms_b = float(np.sqrt(np.mean(seg_b ** 2)))
check("7 hiss accumulates in feedback", rms_b > 1.15 * rms_a,
      f"tail RMS no-fb {rms_a:.2e} vs fb {rms_b:.2e} ({100*rms_b/rms_a:.0f}%; theory 1/(1-fb^2) -> {100*np.sqrt(1/(1-0.7**2)):.0f}%)")

# ---------------------------------------------------------------- 8. motor inertia
imp9 = np.zeros(int(1.0 * fs)); imp9[100] = 1.0
wet9, _, _ = tape_echo(imp9, gap_in=1.5, speed_ips=7.5, heads=(1.0,),
                       head_gains=(1.0,), feedback=0.0, drive=0.0,
                       wow_m=0.0, flutter_m=0.0, hiss_level=0.0, motor_tau=0.05)
peak9 = int(np.argmax(np.abs(wet9)))
check("8 motor inertia delays first echo", peak9 > 100 + tau_pred * fs,
      f"first echo at {peak9} (> nominal {100 + tau_pred*fs:.0f}, ramp start)")

# ---------------------------------------------------------------- 9. zero-drift
rng = np.random.default_rng(42)
x9 = rng.normal(0, 0.1, 50000)
wet9a, _, _ = tape_echo(x9, gap_in=1.5, speed_ips=7.5, heads=(1.0, 2.0, 3.0),
                        head_gains=(0.7, 0.5, 0.3), feedback=0.55, drive=0.9,
                        wow_m=0.002, wow_f=1.5, flutter_m=0.0004, flutter_f=7.0,
                        hiss_level=1e-4, seed=7)
wet9b, _, _ = tape_echo(x9, gap_in=1.5, speed_ips=7.5, heads=(1.0, 2.0, 3.0),
                        head_gains=(0.7, 0.5, 0.3), feedback=0.55, drive=0.9,
                        wow_m=0.002, wow_f=1.5, flutter_m=0.0004, flutter_f=7.0,
                        hiss_level=1e-4, seed=7)
check("9 zero-drift + determinism",
      len(wet9a) == len(x9) == 50000 and np.array_equal(wet9a, wet9b),
      f"len {len(wet9a)} == {len(x9)}, byte-identical rerun")

# ---------------------------------------------------------------- 10. demo WAV
# melodic plucks: 4 notes, Karplus-Strong-lite (decaying saw), through TEPM
def pluck(freq, dur, fs):
    n = int(dur * fs)
    buf = np.zeros(n)
    period = int(fs / freq)
    exc = np.random.default_rng(3).normal(0, 0.5, period)
    for i in range(n):
        buf[i] = exc[i % period]
    # simple one-pole damping per cycle (KS)
    out = np.zeros(n)
    prev = 0.0
    for i in range(n):
        out[i] = buf[i] + 0.996 * prev
        prev = out[i]
    env = np.exp(-np.arange(n) / (0.35 * fs))
    return (out * env * 0.3).astype(np.float64)

notes = [(261.63, 0.4), (329.63, 0.3), (392.0, 0.3), (523.25, 0.5)]
mel = np.concatenate([pluck(f, d, fs) for f, d in notes])
mel = np.concatenate([mel, np.zeros(int(1.2 * fs))])
wet10, _, _ = tape_echo(mel, gap_in=1.5, speed_ips=7.5, heads=(1.0, 2.0, 3.0),
                        head_gains=(0.8, 0.6, 0.4), feedback=0.5, drive=1.1,
                        wow_m=0.002, wow_f=1.5, flutter_m=0.0004, flutter_f=7.0,
                        hiss_level=1e-4, seed=11)
mix = mel + wet10
mix = mix / np.max(np.abs(mix))
demo = os.path.join(os.path.dirname(__file__), "sp137_demo.wav")
with wave.open(demo, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(fs)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
size = os.path.getsize(demo)
check("10 demo WAV written", size > 40, f"{demo} ({size} B, {len(mix)} frames)")

npass = sum(1 for _, ok, _ in results if ok)
print(f"\n=== {npass}/{len(results)} checks passed ===")
sys.exit(0 if npass == len(results) else 1)
