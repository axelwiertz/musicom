"""Extract the NumPy sketch from sound_method_SP-132_RSDA.md and actually run it."""
import io, re
import numpy as np

MD = "/opt/data/projects/Research/CompositionMethods/sound_method_SP-132_RSDA.md"
txt = io.open(MD, encoding="utf-8").read()
blk = re.search(r"## 3\. Reference implementation.*?```python\n(.*?)```", txt, re.S).group(1)
# drop the trailing automation lines (they need a signal; we supply our own)
code = blk.split("# automation")[0]
ns = {}
exec(compile(code, "sketch", "exec"), ns)

fs = 16000
t = np.arange(int(1.5*fs))/fs
x = (0.5*np.sin(2*np.pi*220*t) + 0.3*np.sin(2*np.pi*660*t)
     + 0.05*np.random.default_rng(0).standard_normal(len(t)))
out = ns["rotary"](x, fs=fs, fc=800.0, rpm_horn=400, rpm_drum=340)
print("sketch OK")
print("  in :", x.shape, "out:", out.shape, "same length:", x.shape == out.shape)
print(f"  peak={np.max(np.abs(out)):.3f} rms_in={np.sqrt(np.mean(x**2)):.4f} "
      f"rms_out={np.sqrt(np.mean(out**2)):.4f}")
print("  finite:", bool(np.all(np.isfinite(out))))
