"""SP-134 prototype part B: nonlinear single-reed + conical modal bore, tuned loop."""
import numpy as np

c, rho, fs = 343.0, 1.2, 48000.0
x0, Lt = 0.102, 1.370
L_full = x0 + Lt

def cone_poles(fmax=4000.0, df=0.25):
    f = np.arange(1.0, fmax, df)
    k = 2 * np.pi * f / c
    Z = 1j * rho * c * k * x0 * np.sin(k * Lt) / (k * x0 * np.cos(k * Lt) + np.sin(k * Lt))
    a = np.abs(Z)
    idx = np.where((a[1:-1] > a[:-2]) & (a[1:-1] > a[2:]))[0] + 1
    idx = [i for i in idx if a[i] > 5 * np.median(a)]
    out = []
    for i in idx:
        y0_, y1_, y2_ = a[i - 1], a[i], a[i + 1]
        d = 0.5 * (y0_ - y2_) / (y0_ - 2 * y1_ + y2_ + 1e-30)
        out.append(f[i] + d * df)
    return np.array(out)

FC = cone_poles()
F0 = FC[0]

k_r, S_r, H0 = 1500.0, 1.0e-4, 0.8e-3
w_eff, alpha = 0.012, 0.7

def render(p_mouth, dur=0.8, nmode=30, Q0=14.0, Qexp=0.6, gain=1.0, K=420.0, seed=3):
    n = int(dur * fs)
    fm = FC[:nmode]
    Q = Q0 * (fm / fm[0]) ** Qexp
    r = np.exp(-np.pi * fm / (Q * fs))
    a1 = 2 * r * np.cos(2 * np.pi * fm / fs)
    a2 = -r * r
    y1 = np.zeros(nmode); y2 = np.zeros(nmode)
    g = gain / (1.0 + (fm / fm[0]) ** 1.2)      # radiation + viscothermal rolloff

    m_r, fr, Qr = 1.0e-5, 1600.0, 4.0
    rr = 2 * np.pi * fr * m_r / Qr
    x = xd = 0.0
    pb = 0.0
    out = np.zeros(n); hmin = 1.0; pmax = 0.0
    for i in range(n):
        dpv = p_mouth - pb
        for _ in range(4):
            h = 1.0 / (4 * fs)
            xdd = (-S_r * dpv - rr * xd - k_r * x) / m_r
            xd += h * xdd
            x += h * xd
            if x < -0.97*H0:     # reed slaps against the lay (unilateral stop)
                x = -0.97*H0; xd = -0.3*xd
        H = H0 + x
        if H <= 1e-9:
            uv = 0.0
        else:
            uv = alpha * w_eff * H * np.sqrt(2 * abs(dpv) / rho) * np.sign(dpv)
        hmin = min(hmin, H)
        yn = a1 * y1 + a2 * y2 + g * uv
        y2, y1 = y1, yn
        pb = K * yn.sum()
        pmax = max(pmax, abs(pb))
        out[i] = pb
    return out, hmin, pmax

def spec(y, f0, nh=12):
    w = np.hanning(len(y)); Y = np.abs(np.fft.rfft(y * w))
    fa = np.fft.rfftfreq(len(y), 1 / fs)
    sel = (fa > 60) & (fa < 4000)
    pk = fa[sel][np.argmax(Y[sel])]
    lv = []
    for hh in range(1, nh + 1):
        m = np.abs(fa - hh * pk) < 4.0
        lv.append(Y[m].max() if m.any() else 0.0)
    lv = np.array(lv)
    return pk, 20 * np.log10(lv / lv.max() + 1e-12)

print(f"f1(pole)={F0:.2f} Hz  n*c/2L={c/(2*L_full):.2f}")
for pm in (3000.0, 4500.0, 6000.0, 7500.0, 9000.0):
    y, hmin, pmax = render(pm)
    pk, lv = spec(y, F0)
    # spectral centroid as brightness proxy
    w = np.hanning(len(y)); Y = np.abs(np.fft.rfft(y * w)); fa = np.fft.rfftfreq(len(y), 1 / fs)
    m = (fa > 50) & (fa < 8000)
    cen = (fa[m] * Y[m]).sum() / Y[m].sum()
    rms = np.sqrt(np.mean(y ** 2))
    print(f"pm={pm:5.0f} Pa  f0={pk:7.2f}  pb_rms={rms:6.0f} Pa  pb_peak={pmax:6.0f}  "
          f"minH={hmin*1e3:5.2f} mm  centroid={cen:6.0f} Hz")
    print("   harm dB:", np.round(lv, 1))
