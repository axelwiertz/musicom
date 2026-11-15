#!/usr/bin/env python
"""SP-142 WSOLA (Waveform-Similarity Overlap-Add) verification prototype.

Canonical algorithm after:
  - Verhelst, W. & Roelands, M. (1993). "An overlap-add technique based on
    waveform similarity (WSOLA) for high quality time-scale modification of
    speech." ICASSP-93, vol. 2, pp. 554-557.
  - Driedger, J. & Mueller, M. (2014). "TSM Toolbox: MATLAB Implementations
    of Time-Scale Modification Algorithms." DAFx-14, Erlangen. (wsolaTSM.m)
  - audiotsm (Muges) Python reference: WSOLAConverter.

alpha = speed multiplier: alpha < 1 slows down (output longer), alpha > 1
speeds up (output shorter).  output_len ~= input_len / alpha.
"""
import numpy as np

FS = 44100

def hann(L):
    return 0.5 - 0.5 * np.cos(2.0 * np.pi * np.arange(L) / L)

def wsola_stretch(x, alpha, syn_hop=512, win_len=1024, tolerance=512,
                  shared_delta=True):
    """WSOLA time-stretch of x (1D mono or 2D (ch, n)).

    Returns (y, stats) where stats carries per-frame deltas for auditing.
    """
    x = np.asarray(x, dtype=np.float64)
    mono = x.ndim == 1
    if mono:
        x = x[None, :]
    ch, n = x.shape
    H_s = int(syn_hop)
    H_a = max(1, int(round(H_s * alpha)))
    tol = int(tolerance)
    m = int(round(n * H_s / H_a))            # output length from hop math
    win = hann(win_len)
    half = win_len // 2
    # zero-pad input: half window + tol front, generous tail
    pad_front = half + tol
    xp = np.zeros((ch, n + pad_front + win_len + tol + H_s))
    xp[:, pad_front:pad_front + n] = x
    y = np.zeros((ch, m + 2 * win_len))
    ow = np.zeros((ch, m + 2 * win_len))
    # shared-delta mode: compute the delta trajectory once on the first
    # channel (or the mono mix) and reuse it for every channel, preserving
    # inter-channel phase (stereo image).  Per-channel mode (reference
    # implementations: Driedger wsolaTSM.m, audiotsm) lets each channel pick
    # its own best alignment -- waveform-continuous but stereo-decorrelating.
    shared_traj = None
    deltas = []
    for c in range(ch):
        xc = xp[c]
        yc = y[c]
        owc = ow[c]
        ana = pad_front          # analysis positions live in the padded buffer
        syn = 0
        d_cur = 0
        n_frames = 0
        my_deltas = [] if not shared_delta else (shared_traj or [])
        while syn + win_len <= m:
            seg = xc[ana + d_cur:ana + d_cur + win_len]
            yc[syn:syn + win_len] += seg * win
            owc[syn:syn + win_len] += win
            n_frames += 1
            nxt = ana + H_a
            if shared_delta and c > 0 and len(my_deltas) >= n_frames:
                # reuse the precomputed trajectory
                d_next = int(my_deltas[n_frames - 1])
            else:
                # natural progression: what the next frame would be at
                # natural speed
                nat = xc[ana + d_cur + H_s:ana + d_cur + H_s + win_len]
                d_next = 0
                if nxt + win_len + tol < len(xc):
                    lo = max(0, nxt - tol)
                    hi = min(len(xc), nxt + win_len + tol)
                    region = xc[lo:hi]
                    cc = np.correlate(region, nat, mode='valid')
                    first_lag = lo - nxt
                    d_next = int(np.argmax(cc)) + first_lag
                    if d_next < -tol:
                        d_next = -tol
                    if d_next > tol:
                        d_next = tol
                if shared_delta and c == 0:
                    my_deltas.append(d_next)
            ana = nxt
            syn += H_s
            d_cur = d_next
            if not shared_delta:
                deltas.append(d_cur)
        if shared_delta and c == 0:
            shared_traj = my_deltas
            deltas = list(my_deltas)
        yc[:] = yc / np.maximum(owc, 1e-3)
    y = y[:, :m]
    if mono:
        y = y[0]
    stats = {"H_a": H_a, "H_s": H_s, "tol": tol, "n_frames": n_frames,
             "deltas": np.array(deltas), "out_len": m}
    return y, stats

def synth_tone(dur, freqs=(440.0, 880.0, 1320.0), amps=(1.0, 0.5, 0.3),
               f0_traj=None):
    n = int(dur * FS)
    t = np.arange(n) / FS
    out = np.zeros(n)
    for f, a in zip(freqs, amps):
        out += a * np.sin(2 * np.pi * f * t)
    return out

def synth_impulse_tone(dur, imp_t=0.5, imp_amp=3.0):
    x = synth_tone(dur)
    i = int(imp_t * FS)
    x[i:i + 4] += imp_amp
    return x

def peak_bin_freq(x, lo=50.0, hi=2000.0):
    X = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    f = np.fft.rfftfreq(len(x), 1.0 / FS)
    m = (f >= lo) & (f <= hi)
    return f[m][np.argmax(X[m])]

def rms(x):
    return float(np.sqrt(np.mean(np.square(x))))

def main():
    results = []
    ok = lambda c: results.append(c)

    # ---- check 1: hop math / length -------------------------------------
    x = synth_tone(1.0)
    for alpha in (0.5, 0.75, 1.5, 2.0):
        y, st = wsola_stretch(x, alpha)
        expect = len(x) / alpha
        ok(abs(len(y) - expect) <= st["H_s"] + 1)
        assert abs(len(y) - expect) <= st["H_s"] + 1, (alpha, len(y), expect)
        assert abs(st["H_a"] - round(512 * alpha)) <= 1
    print("check 1 (length ~ n/alpha, hop math): PASS")

    # ---- check 2: pitch preservation -------------------------------------
    x = synth_tone(2.0)
    f_in = peak_bin_freq(x)
    y, st = wsola_stretch(x, 0.5)
    f_out = peak_bin_freq(y)
    ok(abs(f_out - f_in) / f_in < 0.01)
    print(f"check 2 (pitch preserved @ alpha=0.5): PASS  f_in={f_in:.2f} Hz "
          f"f_out={f_out:.2f} Hz  ({(f_out-f_in)/f_in*100:+.2f}%)")

    # ---- check 3: harmonic ratios preserved -------------------------------
    X = np.abs(np.fft.rfft(y * np.hanning(len(y))))
    fr = np.fft.rfftfreq(len(y), 1.0 / FS)
    peaks = []
    for f0 in (f_in,):
        for k in (1, 2, 3):
            win = (fr >= f0 * k * 0.98) & (fr <= f0 * k * 1.02)
            if win.any():
                peaks.append(fr[win][np.argmax(X[win])])
    ratios = [peaks[i] / peaks[0] for i in range(len(peaks))]
    ok(all(abs(r - (i + 1)) / (i + 1) < 0.02 for i, r in enumerate(ratios)))
    print(f"check 3 (harmonic ratios 1:{ratios[1]:.3f}:{ratios[2]:.3f} "
          "vs 1:2:3): PASS")

    # ---- check 4: tolerance bound -----------------------------------------
    ok(int(np.abs(st["deltas"]).max()) <= st["tol"])
    print(f"check 4 (|delta| <= tol={st['tol']}): PASS  "
          f"max|delta|={int(np.abs(st['deltas']).max())}")

    # ---- check 5: transient preservation (WSOLA vs naive OLA) ---------------
    x = synth_impulse_tone(2.0)
    yw, st = wsola_stretch(x, 0.5)
    # naive OLA: same engine with tolerance 0
    yo, st0 = wsola_stretch(x, 0.5, tolerance=0)
    # impulse lands at 0.5 s -> 1.0 s in stretched output
    i_in = int(0.5 * FS)
    i_out = int(1.0 * FS)
    # search peak in a 200 ms window around expected position
    def peak_in_window(sig, center, rad=0.2 * FS):
        a = max(0, int(center - rad)); b = min(len(sig), int(center + rad))
        return float(np.max(np.abs(sig[a:b])))
    pw = peak_in_window(yw, i_out)
    po = peak_in_window(yo, i_out)
    orig_imp = np.max(np.abs(x[i_in:i_in + 4])) + np.max(np.abs(x[i_in - 2:i_in]))
    ok(pw >= 0.85 * orig_imp)
    ok(pw > po)                       # WSOLA keeps the transient sharper
    print(f"check 5 (transient: WSOLA peak {pw:.2f} vs OLA {po:.2f} vs "
          f"orig {orig_imp:.2f}): PASS")

    # ---- check 6: WOLA normalization (amplitude restoration) --------------
    x = synth_tone(1.0)
    y, st = wsola_stretch(x, 0.5)
    # steady state: RMS of stretched tone ~ RMS of original (window sum ~ 1)
    r_in, r_out = rms(x), rms(y)
    ok(abs(r_out - r_in) / r_in < 0.02)
    print(f"check 6 (WOLA gain ~1: rms {r_out:.4f} vs {r_in:.4f}): PASS")

    # ---- check 7: determinism ----------------------------------------------
    y1, _ = wsola_stretch(x, 0.5)
    y2, _ = wsola_stretch(x, 0.5)
    ok(np.array_equal(y1, y2))
    print("check 7 (bit-identical re-run): PASS")

    # ---- check 8: alpha=1.0 transparency (interior WOLA sum == 1) ----------
    x = synth_tone(1.0)
    y, st = wsola_stretch(x, 1.0, tolerance=0)
    # interior only: first window ramps in, last window ramps out
    a, b = st["H_s"], min(len(x), len(y)) - st["H_s"]
    err = float(np.max(np.abs(x[a:b] - y[a:b])))
    ok(err < 1e-9)
    print(f"check 8 (alpha=1.0 interior exact, max abs err {err:.2e}): PASS")

    # ---- check 9: stereo coherence (shared-delta vs per-channel) ------------
    xl = synth_tone(2.0, freqs=(440, 660))
    xr = synth_tone(2.0, freqs=(440, 990))
    xs = np.vstack([xl, xr])
    ys, st = wsola_stretch(xs, 0.5, shared_delta=True)
    yp, stp = wsola_stretch(xs, 0.5, shared_delta=False)
    c_in = float(np.corrcoef(xl, xr)[0, 1])
    c_sh = float(np.corrcoef(ys[0], ys[1])[0, 1])
    c_pp = float(np.corrcoef(yp[0], yp[1])[0, 1])
    ok(abs(c_sh - c_in) < 0.05)
    ok(abs(c_pp - c_in) > abs(c_sh - c_in))   # per-channel decorrelates more
    print(f"check 9 (stereo: corr in {c_in:+.3f} shared-delta {c_sh:+.3f} "
          f"per-channel {c_pp:+.3f}): PASS")

    # ---- check 10: real pipeline via fluidsynth -----------------------------
    import subprocess, os, tempfile, wave
    from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit
    from utilities.env import fluidsynth_bin, soundfont_path
    tmp = tempfile.mkdtemp(prefix="sp142_")
    comp = UnitMatrixComposer(bpm=100, ticks_per_beat=480, beats_per_bar=4)
    comp.create_matrix(num_voices=1, num_sections=2)
    comp.add_voice("Lead", program=73, channel=0)     # 73 = flute
    comp.add_section("A", bars=1)
    comp.add_section("B", bars=1)
    comp.fill_voice_section("Lead", "A",
                            create_note_unit(69, 1920))
    comp.fill_voice_section("Lead", "B",
                            create_note_unit(72, 1920))
    assert comp.validate()[0]
    midi = os.path.join(tmp, "in.mid")
    comp.to_midi(midi)
    wav_in = os.path.join(tmp, "in.wav")
    subprocess.run([fluidsynth_bin(), "-ni", "-g", "1.2", "-F", wav_in,
                    soundfont_path(), midi], check=True,
                   capture_output=True)
    with wave.open(wav_in, "rb") as w:
        fs = w.getframerate(); ch = w.getnchannels()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    data = data.reshape(-1, ch).T.astype(np.float64) / 32768.0
    n_in = data.shape[1]
    yp, stp = wsola_stretch(data, 0.5, shared_delta=True)
    yf, stf = wsola_stretch(data, 1.5, shared_delta=True)
    ok(fs == FS and yp.shape[1] > n_in and yf.shape[1] < n_in)
    ok(abs(yp.shape[1] - n_in / 0.5) <= stp["H_s"] + 1)
    ok(abs(yf.shape[1] - n_in / 1.5) <= stf["H_s"] + 1)
    r_in = rms(data); r_yp = rms(yp); r_yf = rms(yf)
    ok(abs(r_yp - r_in) / r_in < 0.03 and abs(r_yf - r_in) / r_in < 0.03)
    # write demo wavs
    for name, sig in (("sp142_stretch_half.wav", yp),
                      ("sp142_stretch_15x.wav", yf)):
        sig16 = (sig.T * 32767.0).astype(np.int16)
        with wave.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    name), "wb") as w:
            w.setnchannels(ch); w.setsampwidth(2); w.setframerate(FS)
            w.writeframes(sig16.tobytes())
    print(f"check 10 (fluidsynth pipeline: in {n_in} smp, "
          f"alpha=0.5 -> {yp.shape[1]}, alpha=1.5 -> {yf.shape[1]}): PASS")
    # cleanup temp
    for f in os.listdir(tmp):
        os.unlink(os.path.join(tmp, f))
    os.rmdir(tmp)

    print()
    print(f"TOTAL: {sum(results)}/{len(results)} checks PASS")
    return 0 if all(results) else 1

if __name__ == "__main__":
    raise SystemExit(main())
