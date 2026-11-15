# -*- coding: utf-8 -*-
"""Calibrate WOODBLOCK_MODES decay rates against ResonatorBank semantics."""
import sys

import numpy as np

sys.path.insert(0, "/opt/data/repos/musicom")
from sound.synthesis.modal import ModalSynth  # noqa: E402

SR = 22050
ms = ModalSynth(sample_rate=SR)


def measure(modes, dur=0.6):
    a = ms.render_custom(modes, duration=dur, excitation="impulse")
    peak = float(np.max(np.abs(a)))
    thr = 0.001 * peak
    idx = np.nonzero(np.abs(a) > thr)[0]
    t60 = (idx[-1] / SR * 1000) if len(idx) else 0.0
    # RMS at 20 ms and 60 ms
    def rms(t0, t1):
        s = a[int(t0 * SR):int(t1 * SR)]
        return float(np.sqrt(np.mean(s ** 2))) / peak if len(s) else 0.0
    return peak, t60, rms(0.02, 0.04), rms(0.06, 0.08), rms(0.15, 0.17)


print(f"{'decay mult':>10} {'peak':>7} {'len_ms':>7} {'r@30ms':>7} {'r@70ms':>7} {'r@160ms':>8}")
for mult in (1, 2, 4, 6, 8, 12):
    modes = [(430.0, 1.00, 25.0 * mult), (860.0, 0.45, 35.0 * mult),
             (1040.0, 0.30, 45.0 * mult), (1720.0, 0.18, 60.0 * mult),
             (2150.0, 0.10, 80.0 * mult), (3100.0, 0.06, 100.0 * mult)]
    peak, t60, r1, r2, r3 = measure(modes)
    print(f"{mult:>10} {peak:7.3f} {t60:7.1f} {r1:7.3f} {r2:7.3f} {r3:8.3f}")

print("\n--- chosen candidate: mult 4 ---")
modes = [(430.0, 1.00, 100.0), (860.0, 0.45, 140.0), (1040.0, 0.30, 180.0),
         (1720.0, 0.18, 240.0), (2150.0, 0.10, 320.0), (3100.0, 0.06, 400.0)]
a = ms.render_custom(modes, duration=0.4, excitation="impulse")
spec = np.abs(np.fft.rfft(a[:2048]))
freqs = np.fft.rfftfreq(2048, 1 / SR)
top = sorted(np.argsort(spec)[-6:])
print("spectral peaks:", [(round(float(freqs[i])), round(float(spec[i] / spec.max()), 2)) for i in top])
peak, t60, r1, r2, r3 = measure(modes)
print(f"peak={peak:.3f} len_ms={t60:.1f} r@30={r1:.3f} r@70={r2:.3f} r@160={r3:.3f}")
print("centroid:", float(np.sum(freqs * spec) / np.sum(spec)))
