"""SP-136 verification prototype — Tabla syahi-loaded tension-modulated membrane.

Part 1: uniform circular membrane -> Bessel-zero mode ratios (1 : 1.593 : 2.136 ...).
Part 2: syahi-loaded membrane, Sathej & Adhikari (2008) smooth density profile,
        radial finite-volume eigenproblem -> modes collapse onto 1:2:3:4:5.
Part 3: modal synthesis of two strokes (dayan 'na' edge strike, bayan 'ghe' glide).
"""
import numpy as np
from scipy.special import jn_zeros

FS = 44100

# ---------- 1. uniform membrane ----------
uni = np.array([jn_zeros(0, 2)[0], jn_zeros(1, 1)[0], jn_zeros(2, 1)[0],
                jn_zeros(0, 2)[1], jn_zeros(3, 1)[0], jn_zeros(1, 2)[1],
                jn_zeros(4, 1)[0], jn_zeros(2, 2)[1], jn_zeros(0, 3)[2]])
uni = uni / uni[0]
print("uniform membrane alpha_mn/alpha_01:", np.round(uni, 4))

# ---------- 2. loaded membrane ----------
def loaded(sigma=3.125, k=0.4, xi=0.091, N=1400, m_max=4):
    """Radial finite-volume eigenproblem for a concentric syahi load.
    -(1/r) d/dr(r dR/dr) + m^2/r^2 R = (omega^2/T) rho(r) R,  R(1)=0."""
    h = 1.0 / N
    r = (np.arange(N) + 0.5) * h
    rho = 1.0 + (sigma**2 - 1.0) / 2.0 * (1.0 - np.tanh((r - k) / xi))
    freqs = []
    for m in range(m_max + 1):
        A = np.zeros((N, N))
        for i in range(N):
            rip, rim = r[i] + 0.5 * h, r[i] - 0.5 * h
            if i + 1 < N:
                A[i, i + 1] += -rip / (r[i] * h * h)
            if i > 0:
                A[i, i - 1] += -rim / (r[i] * h * h)
            A[i, i] += (rip + rim) / (r[i] * h * h) + m * m / (r[i] ** 2)
        lam = np.linalg.eigvals(np.linalg.solve(np.diag(rho), A))
        lam = np.sort(np.real(lam[lam > 1e-6]))
        for n, l in enumerate(np.sqrt(lam[:4])):
            freqs.append((m, n + 1, l))
    freqs.sort(key=lambda t: t[2])
    return freqs, rho

fr, rho = loaded()
print("syahi density: centre=%.2f  edge=%.2f (sigma^2=%.2f)" % (rho[0], rho[-1], 3.125 ** 2))
scale = fr[1][2] / 2.0                     # paper normalises psi_11 -> 2.00
print("lowest modes (m,n) normalised as in Sathej-Adhikari Table 1:")
for m, n, f in fr[:9]:
    print("   (m=%d,n=%d) %.4f" % (m, n, f / scale))

fr2, _ = loaded(sigma=2.57, k=0.492, xi=0.091)
s2 = fr2[1][2] / 2.0
print("optimum sigma=2.57 k=0.492:", np.round([f / s2 for _, _, f in fr2[:7]], 4))

# ---------- 3. tension glide ----------
for st in (-3, -5, -7):
    print("glide %+d semitones -> T/T0 = %.3f" % (st, 2 ** (2 * st / 12)))

# ---------- 4. modal synthesis ----------
def modal(ratios, f0, dur, taus, amps, glide_st=0.0, glide_ms=140.0,
          strike_noise=0.25, seed=0):
    n = int(dur * FS)
    t = np.arange(n) / FS
    target = 2.0 ** (glide_st / 12.0)
    s = 1.0 + (target - 1.0) * (1.0 - np.exp(-t / (glide_ms / 1000.0)))
    y = np.zeros(n)
    for r_, tau, a in zip(ratios, taus, amps):
        phase = 2 * np.pi * np.cumsum(f0 * r_ * s) / FS   # int f(t) dt
        y += a * np.exp(-t / tau) * np.sin(phase)
    rng = np.random.default_rng(seed)
    nz = np.diff(np.concatenate([[0.0], rng.standard_normal(n) * np.exp(-t / 0.004)]))
    y += strike_noise * nz
    return y / (np.max(np.abs(y)) + 1e-12)

dayan = np.array([1.0, 1.94, 2.91, 3.88, 4.85, 5.82])   # Table 1, /1.03
bayan = np.array([1.0, 1.98, 2.96, 3.93, 4.90])
na = modal(dayan, 146.8, 0.9, [0.35, 0.22, 0.16, 0.11, 0.08, 0.06],
           [1.0, 0.7, 0.5, 0.35, 0.25, 0.18], strike_noise=0.35, seed=1)
ghe = modal(bayan, 73.4, 1.2, [0.55, 0.40, 0.28, 0.20, 0.14],
            [1.0, 0.55, 0.30, 0.18, 0.10], glide_st=-5.0, glide_ms=160.0,
            strike_noise=0.15, seed=2)
for name, y in (("na", na), ("ghe", ghe)):
    sp = np.abs(np.fft.rfft(y)); f = np.fft.rfftfreq(len(y), 1 / FS)
    print("%s: peak=%.3f rms=%.3f centroid=%.0f Hz n=%d"
          % (name, np.max(np.abs(y)), np.sqrt(np.mean(y ** 2)),
             np.sum(f * sp) / np.sum(sp), len(y)))

mix = np.concatenate([na, ghe * 0.9])
pcm = (np.clip(mix, -1, 1) * 32767).astype("<i2")
import wave
with wave.open("/opt/data/projects/Research/CompositionMethods/_web136/sp136_demo.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(FS)
    w.writeframes(pcm.tobytes())
print("wav bytes:", len(pcm.tobytes()))
