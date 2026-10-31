import numpy as np
from numpy.fft import rfft, irfft, rfftfreq

FS, C, A = 48000, 343.0, 0.0875           # head radius
FC = C / (2 * np.pi * A)                   # ~624 Hz shadow corner

def plant(n, span_deg=60.0, dist=1.0, fs=FS, shadow_hz=FC):
    """2x2 speaker->ear frequency responses. Rows = ears, cols = speakers."""
    f = rfftfreq(n, 1 / fs)
    th = np.deg2rad(span_deg / 2)
    spk = np.array([[dist*np.cos(th),  dist*np.sin(th)],      # L
                    [dist*np.cos(th), -dist*np.sin(th)]])     # R
    ears = np.array([[0.0, -A], [0.0, A]])                    # interaural axis = y
    w = 2j * np.pi * f
    H = np.zeros((2, 2, f.size), complex)
    for e in range(2):
        for s in range(2):
            r = np.linalg.norm(spk[s] - ears[e])
            h = np.exp(-w * r / C) / r
            if e != s:
                h /= (1 + w / (2 * np.pi * shadow_hz))        # head shadow
            H[e, s] = h
    return H, f

def invert(H, beta=1e-4):
    C_ = np.empty_like(H)
    for k in range(H.shape[2]):
        h = H[:, :, k]
        C_[:, :, k] = h.conj().T @ np.linalg.inv(h @ h.conj().T + beta * np.eye(2))
    return C_

def shuffler(H, f, gmax_db=18.0):
    """Cooper-Bauck form with a gain-capped difference filter."""
    hs, ho = H[0, 0], H[1, 0]
    cs, cd = 1 / (hs + ho), 1 / (hs - ho)
    lim = 10 ** (gmax_db / 20)
    over = np.abs(cd) > lim
    cd = np.where(over, lim * np.exp(1j * np.angle(cd)), cd)   # bass management
    C_ = np.empty_like(H)
    for k in range(f.size):
        C_[:, :, k] = 0.5 * np.array([[cs[k] + cd[k], cs[k] - cd[k]],
                                      [cs[k] - cd[k], cs[k] + cd[k]]])
    return C_

def process(x, C_, n, pre_delay=144):       # x: (2, N); 3 ms pre-delay @48k
    """Overlap-save block convolution of a stereo buffer by C_ (2x2 x F)."""
    hop, y = n // 2, np.zeros_like(x)
    for start in range(0, x.shape[1], hop):
        seg = x[:, start:start + n]
        if seg.shape[1] < n:
            seg = np.pad(seg, ((0, 0), (0, n - seg.shape[1])))
        X = rfft(seg, n, axis=1)
        Y = np.stack([C_[o, 0] * X[0] + C_[o, 1] * X[1] for o in (0, 1)])
        y[:, start:start + hop] += irfft(Y, n, axis=1)[:, pre_delay:pre_delay + hop]
    return y
