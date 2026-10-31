import re, numpy as np
from numpy.fft import rfft, irfft
md = open('/opt/data/projects/Research/CompositionMethods/sound_method_SP-129_TCCR.md').read()
code = re.search(r"```python\n(.*?)```", md, re.S).group(1)
ns = {}
exec(code, ns)
print("code block executed OK; names:", [k for k in ("plant", "invert", "shuffler", "design", "process") if k in ns])
ir = ns['design'](latency_ms=13.7, L=8192)
print("IR", ir.shape, "peak", float(np.abs(ir[0, 0]).max()).__round__(3), "at", int(np.abs(ir[0, 0]).argmax()))
H = ns['plant'](32768)[0]
IR = rfft(ir, 32768, axis=-1)
f = np.fft.rfftfreq(32768, 1 / 48000)
b = (f >= 500) & (f <= 8000)
P = np.stack([H[:, :, k] @ IR[:, :, k] for k in range(f.size)], axis=2)
print("crosstalk 500-8k:", round(float(20 * np.log10(np.abs(P[:, :, b]).max(axis=2)[1, 0])), 1), "dB")
N = 48000
sig = np.sin(2 * np.pi * 220 * np.arange(N) / 48000)
S = ns['process'](np.stack([sig, sig]), ir)
print("process output finite:", bool(np.isfinite(S).all()), "rms:", round(float(np.sqrt((S**2).mean())), 4))
