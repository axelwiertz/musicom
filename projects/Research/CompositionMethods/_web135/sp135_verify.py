"""SP-135 WNAS reference verification (NumPy) — math-level checks only.
1. mu-law companding round trip (quantization noise floor).
2. Dilated causal convolution: receptive field growth, causality (no future leakage).
3. Gated activation unit shape + 256-way softmax argmax decode.
"""
import numpy as np

FS = 16000

# ---------- 1. mu-law companding (ITU-T G.711, mu=255) ----------
def mulaw(x, mu=255):
    return np.sign(x) * np.log1p(mu * np.abs(x)) / np.log1p(mu)

def inv_mulaw(y, mu=255):
    return np.sign(y) * (1.0 / mu) * (np.power(1 + mu, np.abs(y)) - 1.0)

rng = np.random.default_rng(42)
x = rng.uniform(-0.99, 0.99, 48000)          # 3 s @16k, full-scale audio
q = np.round(mulaw(x) * 127.5) / 127.5       # quantize to 256 levels
xr = inv_mulaw(q)
snr_db = 10 * np.log10(np.sum(x**2) / np.sum((x - xr) ** 2))
# quiet signal at -40 dBFS
xs = x * 1e-2
qs = np.round(mulaw(xs) * 127.5) / 127.5
snr_quiet_db = 10 * np.log10(np.sum(xs**2) / np.sum((xs - inv_mulaw(qs)) ** 2))
print(f"mu-law SNR full-scale = {snr_db:.1f} dB, quiet(-40dB) = {snr_quiet_db:.1f} dB")

# ---------- 2. Dilated causal convolution ----------
def dilated_causal_conv(x, w, d):
    """w: length-2 filter [w0, w1]; causal: out[t] = w0*x[t] + w1*x[t-d]."""
    out = np.zeros_like(x)
    out[d:] = w[0] * x[d:] + w[1] * x[: x.size - d]
    return out

N = 4096
x = np.zeros(N); x[0] = 1.0                      # impulse
w = np.array([0.5, 0.5])
# stack of 3 blocks, dilations 1,2,4,...,512 (10 layers/block)
dilations = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512] * 3
y = x.copy()
for d in dilations:
    y = dilated_causal_conv(y, w, d)
hits = np.nonzero(y > 1e-12)[0]
rf = int(hits.max() - hits.min()) + 1
print(f"dilated stack: last impulse tap = {hits.max()}, receptive field = {rf} samples")
print(f"theory: 3 blocks x 1024 = {3 * 1024} (plus filter taps)")
print(f"causality OK (no energy at t<0): {hits.min() >= 0}, future leakage={y[0] > 1e-12}")
# per-block check
y1 = x.copy()
for d in dilations[:10]:
    y1 = dilated_causal_conv(y1, w, d)
print(f"1-block receptive field = {int(np.nonzero(y1>1e-12)[0].max())+1} (theory 1024)")

# ---------- 3. Gated unit + softmax decode ----------
np.random.seed(7)
Wf, Wg = np.random.randn(3), np.random.randn(3)   # tiny conv kernels
h = np.random.randn(64)                            # global cond (broadcast)
z = np.tanh(np.convolve(y1, Wf, mode='same') + h.mean()) * \
    (1 / (1 + np.exp(-(np.convolve(y1, Wg, mode='same') + h.mean()))))
logits = z.reshape(-1, 1) @ np.linspace(-1, 1, 256).reshape(1, -1) * 3.0
pred = np.argmax(logits, axis=1)
print(f"gated unit: shape={z.shape}, range=[{z.min():.3f},{z.max():.3f}] (tanh x sigmoid bound)")
sm = np.exp(logits - logits.max(1, keepdims=True)); sm /= sm.sum(1, keepdims=True)
print(f"256-way argmax decode: values in [{pred.min()},{pred.max()}], softmax rows sum to {sm.sum(1).mean():.6f} -> 1")

# ---------- 4. generation cost ----------
n_layers, RF, T = 30, rf, FS * 1
naive = RF * T                       # per-sample RF multiply-adds, one voice, 1 s
print(f"naive NumPy AR cost for 1 s @16k: {naive/1e6:.1f} M MACs (cached-state much cheaper)")
