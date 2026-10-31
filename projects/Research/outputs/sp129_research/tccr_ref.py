"""SP-129 TCCR reference implementation — verified variant (causal L-tap design)."""
import numpy as np
from numpy.fft import rfft, irfft, rfftfreq
from scipy.signal import fftconvolve

FS, C, A = 48000, 343.0, 0.0875
FC = C / (2 * np.pi * A)                       # ~624 Hz head-shadow corner


def plant(n, span_deg=60.0, dist=1.0, fs=FS, shadow_hz=FC):
    """2x2 speaker->ear responses. Rows = ears, cols = speakers."""
    f = rfftfreq(n, 1 / fs)
    th = np.deg2rad(span_deg / 2.0)
    spk = np.array([[dist * np.cos(th), dist * np.sin(th)],
                    [dist * np.cos(th), -dist * np.sin(th)]])
    ears = np.array([[0.0, -A], [0.0, A]])     # interaural axis = y
    w = 2j * np.pi * f
    H = np.zeros((2, 2, f.size), complex)
    for e in range(2):
        for s in range(2):
            r = np.linalg.norm(spk[s] - ears[e])
            h = np.exp(-w * r / C) / r
            if e != s:
                h /= (1 + w / (2 * np.pi * shadow_hz))        # contralateral shadow
            H[e, s] = h
    return H, f


def invert(H, beta=1e-4):
    """C = H^H (H H^H + beta I)^-1 per bin (exact inverse at beta=0)."""
    Cc = np.empty_like(H)
    for k in range(H.shape[2]):
        h = H[:, :, k]
        Cc[:, :, k] = h.conj().T @ np.linalg.inv(h @ h.conj().T + beta * np.eye(2))
    return Cc


def shuffler(H, gmax_db=18.0):
    """Cooper-Bauck sum/difference form; gain-capped difference filter."""
    hs, ho = H[0, 0], H[1, 0]
    cs, cd = 1 / (hs + ho), 1 / (hs - ho)
    lim = 10 ** (gmax_db / 20)
    cd = np.where(np.abs(cd) > lim, lim * np.exp(1j * np.angle(cd)), cd)
    Cc = np.empty_like(H)
    for k in range(H.shape[2]):
        Cc[:, :, k] = 0.5 * np.array([[cs[k] + cd[k], cs[k] - cd[k]],
                                      [cs[k] - cd[k], cs[k] + cd[k]]])
    return Cc


def design(span_deg=60.0, dist=1.0, latency_ms=13.7, L=8192, form="shuffler",
           beta=1e-4, gmax_db=18.0, fs=FS):
    """Causal L-tap cancellation IRs, (2,2,L).

    latency_ms is the TOTAL pre-delay of the chain (plant delay + headroom for the
    non-minimum-phase tail). The L-tap truncation can only cancel to the extent the
    inverse's tail fits inside that budget -- see the measured trade-off table.
    """
    n = 4 * L
    H, f = plant(n, span_deg, dist, fs)
    Cc = shuffler(H, gmax_db) if form == "shuffler" else invert(H, beta)
    th = np.deg2rad(span_deg / 2.0)
    spk = np.array([[dist * np.cos(th), dist * np.sin(th)],
                    [dist * np.cos(th), -dist * np.sin(th)]])
    ears = np.array([[0.0, -A], [0.0, A]])
    r_max = max(np.linalg.norm(spk[s] - ears[e]) for s in (0, 1) for e in (0, 1))
    Cc = Cc * np.exp(-2j * np.pi * f * latency_ms * 1e-3)   # delay -> causal
    ir = irfft(Cc, n, axis=-1)[..., :L]
    t, tail = np.arange(L), int(0.75 * L)
    w = np.ones(L)
    w[tail:] = 0.5 * (1 + np.cos(np.pi * (t[tail:] - tail) / (L - tail)))
    return ir * w, r_max / C


def process(x, ir):
    """x: (2, N) binaural bus -> (2, N) speaker feed (delayed by latency_ms)."""
    y = np.zeros_like(x)
    for o in range(2):
        for i in range(2):
            y[o] += fftconvolve(x[i], ir[o, i])[:x.shape[1]]
    return y


if __name__ == "__main__":
    n = 32768
    H, f = plant(n)
    for lat in [3.0, 5.5, 8.0, 11.0, 13.7, 21.0]:
        ir, _ = design(latency_ms=lat, L=8192)
        IR = rfft(ir, n, axis=-1)
        P = np.stack([H[:, :, k] @ IR[:, :, k] for k in range(f.size)], axis=2)
        b = (f >= 500) & (f <= 8000)
        print(f"latency {lat:>5.1f} ms -> xtalk 500-8k {20*np.log10(np.abs(P[:,:,b]).max(axis=2)[1,0]):>7.2f} dB")

    ir, _ = design(latency_ms=13.7)
    N = 48000
    sig = np.sin(2 * np.pi * 440 * np.arange(N) / FS)
    for name, B in [("centre", np.stack([sig, sig])), ]:
        S = process(B, ir)
        E = np.zeros_like(B)
        for a in range(2):
            for b2 in range(2):
                E[a] += fftconvolve(S[b2], irfft(H[a, b2], 32768)[:8192])[:N]
        e = 20 * np.log10(np.sqrt(((E - B)[:, 4000:]**2).mean()) / np.sqrt((B[:, 4000:]**2).mean()))
        print(f"closed-loop {name} image error: {e:.1f} dB")
