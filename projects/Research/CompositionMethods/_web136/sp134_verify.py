"""SP-134 verification harness: conical single-reed (saxophone) bore synthesis.

Checks
 1. Analytic input impedance of a truncated cone -> all-harmonic pole series
    (+ cents stretch vs the ideal n*f1) vs a stopped cylinder -> odd-only series.
 2. Quasi-static reed characteristic u(dp): peak at k*H0/(3S), closing at k*H0/S.
 3. Time-domain modal bore + nonlinear single-reed valve, cone vs cylinder,
    same reed: even-harmonic content of the cone (h2) against the cylinder.
 4. Writes 16-bit WAVs and a text log.
"""
import json
import os
import wave

import numpy as np

c, rho, fs = 343.0, 1.2, 48000.0
x0, Lt = 0.102, 1.370                       # apex distance, truncated length (m)
L_full = x0 + Lt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sp134_out")
os.makedirs(OUT, exist_ok=True)
log = []


def say(s=""):
    print(s)
    log.append(str(s))


# ---------------------------------------------------------------- 1. poles
def cone_impedance(f):
    k = 2 * np.pi * f / c
    th = k * Lt
    return 1j * rho * c * k * x0 * np.sin(th) / (k * x0 * np.cos(th) + np.sin(th))


def cyl_impedance(f):
    k = 2 * np.pi * f / c
    return 1j * rho * c * np.tan(k * Lt)


def poles(zfun, fmax=4000.0, df=0.25):
    f = np.arange(1.0, fmax, df)
    a = np.abs(zfun(f))
    idx = np.where((a[1:-1] > a[:-2]) & (a[1:-1] > a[2:]))[0] + 1
    idx = [i for i in idx if a[i] > 5 * np.median(a)]
    out = []
    for i in idx:
        y0_, y1_, y2_ = a[i - 1], a[i], a[i + 1]
        d = 0.5 * (y0_ - y2_) / (y0_ - 2 * y1_ + y2_ + 1e-30)
        out.append(f[i] + d * df)
    return np.array(out)


FC = poles(cone_impedance)
FY = poles(cyl_impedance)
say(f"geometry: apex x0={x0:.3f} m, truncated length {Lt:.3f} m, "
    f"r_mouth={0.065*x0/L_full*1e3:.2f} mm, r_bell=65.0 mm")
say(f"c/(2*L_full) = {c/(2*L_full):.2f} Hz")
say(f"cone poles (Hz):  {np.round(FC[:12], 2)}")
say(f"cone ratios/f1:   {np.round(FC[:12]/FC[0], 3)}")
say(f"cone stretch vs n*f1 (cents): {np.round(1200*np.log2((FC[:12]/FC[0])/np.arange(1,13)), 1)}")
say(f"cyl poles (Hz):   {np.round(FY[:12], 2)}")
say(f"cyl ratios/f1:    {np.round(FY[:12]/FY[0], 3)}")
say(f"2nd partial: cone {FC[1]:.2f} Hz ({1200*np.log2(FC[1]/FC[0]):+.1f} cents above f1), "
    f"cylinder {FY[1]:.2f} Hz ({1200*np.log2(FY[1]/FY[0]):+.1f} cents = 3rd harmonic)")

# ------------------------------------------------------------ 2. reed table
k_r, S_r, H0 = 1500.0, 1.0e-4, 0.8e-3
w_eff, alpha = 0.012, 0.7
pclose = k_r * H0 / S_r


def flow_static(dp):
    H = np.clip(H0 - dp * S_r / k_r, 0.0, None)
    return alpha * w_eff * H * np.sqrt(2 * np.abs(dp) / rho) * np.sign(dp)


dp = np.linspace(0, pclose * 1.2, 400001)
u = flow_static(dp)
istar = int(np.argmax(u))
say(f"\nreed: k={k_r:.0f} N/m, S={S_r*1e4:.2f} cm^2, H0={H0*1e3:.2f} mm -> "
    f"closing pressure {pclose:.0f} Pa")
say(f"flow maximum at dp={dp[istar]:.0f} Pa (theory k*H0/(3S)={pclose/3:.0f} Pa), "
    f"u_max={u[istar]*1e3:.3f} L/s; zero at {pclose:.0f} Pa")
say(f"negative differential resistance above {dp[istar]:.0f} Pa -> self-oscillation band")

# --------------------------------------------------------------- 3. render
def render(p_mouth, mode="cone", dur=0.8, nmode=30, Q0=14.0, K=420.0):
    fm = (FC if mode == "cone" else FY)[:nmode]
    Q = Q0 * (fm / fm[0]) ** 0.6
    r = np.exp(-np.pi * fm / (Q * fs))
    a1 = 2 * r * np.cos(2 * np.pi * fm / fs)
    a2 = -r * r
    y1 = np.zeros(nmode)
    y2 = np.zeros(nmode)
    g = 1.0 / (1.0 + (fm / fm[0]) ** 1.2)

    m_r, fr, Qr = 1.0e-5, 1600.0, 4.0
    rr = 2 * np.pi * fr * m_r / Qr
    x = xd = 0.0
    pb = 0.0
    n = int(dur * fs)
    out = np.zeros(n)
    hmin = 1.0
    for i in range(n):
        dpv = p_mouth - pb
        for _ in range(4):
            h = 1.0 / (4 * fs)
            xdd = (-S_r * dpv - rr * xd - k_r * x) / m_r
            xd += h * xdd
            x += h * xd
            if x < -0.97 * H0:
                x = -0.97 * H0
                xd = -0.3 * xd
        H = H0 + x
        hmin = min(hmin, H)
        uv = 0.0 if H <= 1e-9 else alpha * w_eff * H * np.sqrt(2 * abs(dpv) / rho) * np.sign(dpv)
        yn = a1 * y1 + a2 * y2 + g * uv
        y2, y1 = y1, yn
        pb = K * float(yn.sum())
        out[i] = pb
    return out, hmin


def analyse(y, nh=10):
    w = np.hanning(len(y))
    Y = np.abs(np.fft.rfft(y * w))
    fa = np.fft.rfftfreq(len(y), 1 / fs)
    sel = (fa > 60) & (fa < 4000)
    pk = fa[sel][np.argmax(Y[sel])]
    lv = []
    for hh in range(1, nh + 1):
        m = np.abs(fa - hh * pk) < 4.0
        lv.append(Y[m].max() if m.any() else 0.0)
    lv = np.array(lv)
    cen = ((fa * Y)[((fa > 50) & (fa < 8000))]).sum() / Y[(fa > 50) & (fa < 8000)].sum()
    return pk, 20 * np.log10(lv / lv.max() + 1e-12), cen


def write_wav(path, y, norm=0.9):
    y = y / (np.abs(y).max() + 1e-12) * norm
    pcm = (y * 32767).astype("<i2")
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(int(fs))
        wf.writeframes(pcm.tobytes())
    assert os.path.getsize(path) > 40, "empty wav"
    return os.path.getsize(path)


say("\n--- time-domain modal bore + nonlinear reed ---")
res = {}
for mode in ("cone", "cyl"):
    y, hmin = render(4500.0, mode=mode)
    pk, lv, cen = analyse(y)
    res[mode] = dict(f0=pk, harm=lv.tolist(), centroid=cen,
                     rms=float(np.sqrt(np.mean(y ** 2))), minH=hmin)
    path = os.path.join(OUT, f"sax_{mode}.wav")
    sz = write_wav(path, y)
    say(f"{mode:5s}: f0={pk:7.2f} Hz  rms={res[mode]['rms']:6.1f} Pa  "
        f"centroid={cen:5.0f} Hz  minH={hmin*1e3:5.2f} mm  wav={sz} B")
    say(f"        harmonics dB: {np.round(lv, 1)}")
    say(f"        h2-h3 span: {lv[1]-lv[2]:+.1f} dB" if mode == "cone" else "")

say(f"\ncone vs cylinder even-harmonic (h2) level: "
    f"{res['cone']['harm'][1]:.1f} dB vs {res['cyl']['harm'][1]:.1f} dB")
say(f"cone h2,h4 present: {res['cone']['harm'][1]:.1f}, {res['cone']['harm'][3]:.1f} dB; "
    f"cylinder h2,h4: {res['cyl']['harm'][1]:.1f}, {res['cyl']['harm'][3]:.1f} dB")

with open(os.path.join(OUT, "verify_output.txt"), "w") as f:
    f.write("\n".join(log) + "\n")
with open(os.path.join(OUT, "verify.json"), "w") as f:
    json.dump(res, f, indent=1)
say(f"\nwrote {OUT}/verify_output.txt, verify.json, sax_cone.wav, sax_cyl.wav")
