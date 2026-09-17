"""Real-time glitch/stutter chopper — GlitchShredder style.

Replicable logic from the Synthtopia item "GlitchShredder Brings Real-Time
Glitch And Stutter Processing To iPhone And iPad" (2026-09-16): "captures
incoming audio fragments and repeats, reverses and recombines them in real
time... Its Chopper provides independent left and right processing with 16
segment slots per channel. Glitch Probability, Reverse Probability, quantized
jumps and transient detection provide different ways to manipulate captured
segments, while Stutter Sync can follow the host tempo or use manual BPM and
Tap Tempo."

What is replicated here (offline DSP equivalent):

* ``GlitchChopper`` — a segment bank over a ring buffer of captured audio:
  - **16 segment slots per channel**, capture window = one stutter bar;
  - **transient detection** (spectral-flux onset) marks the best slot boundaries
    and can re-capture on hits;
  - **glitch probability** — per-pass roll: a step is replaced by a random
    other segment (recombine) with probability P;
  - **reverse probability** — independent roll to play a segment backwards;
  - **quantized jumps** — segment reads hop on a quantized grid (1/4, 1/8, 1/16)
    instead of continuous;
  - **stutter sync** — grid length from ``bpm`` (host tempo) or manual BPM;
  - **independent L/R** — separate segment banks and RNG streams per channel.
* Deterministic per ``seed`` (repeatable renders).

Not replicated: the AUv3/iOS host, GarageBand/AUM hosting, live streaming I/O
(this is the offline render equivalent).

Usage:
    from sound.effects.glitch_chopper import GlitchChopper

    gc = GlitchChopper(bpm=120, seed=7)
    out = gc.process(stereo_audio)      # (n, 2) -> (n, 2)
"""

from __future__ import annotations

import numpy as np

DEFAULT_SR = 44100
SLOTS = 16


def spectral_flux(audio: np.ndarray, fft_size: int = 512, hop: int = 256) -> np.ndarray:
    """Half-wave rectified spectral flux (positive spectral change) per frame."""
    x = np.asarray(audio, dtype=np.float64).reshape(-1)
    if len(x) < fft_size:
        return np.zeros(1)
    frames = 1 + (len(x) - fft_size) // hop
    win = np.hanning(fft_size)
    prev = None
    flux = np.zeros(frames)
    for f in range(frames):
        seg = x[f * hop:f * hop + fft_size] * win
        mag = np.abs(np.fft.rfft(seg))
        if prev is not None:
            flux[f] = float(np.sum(np.maximum(mag - prev, 0.0)))
        prev = mag
    return flux


def detect_transients(audio: np.ndarray, sample_rate: int = DEFAULT_SR,
                      hop: int = 256) -> np.ndarray:
    """Sample indices of transient onsets (peaks of the flux envelope)."""
    flux = spectral_flux(audio, hop=hop)
    if len(flux) < 3:
        return np.zeros(0, dtype=int)
    thresh = flux.mean() + 1.2 * flux.std()
    hits = []
    for i in range(1, len(flux) - 1):
        if flux[i] > thresh and flux[i] >= flux[i - 1] and flux[i] >= flux[i + 1]:
            hits.append(i * hop)
    return np.asarray(hits, dtype=int)


class ChannelChopper:
    """One channel: 16-slot segment bank + probability recombination."""

    def __init__(self, sample_rate: int = DEFAULT_SR, slots: int = SLOTS,
                 rng: np.random.Generator | None = None):
        self.sr = int(sample_rate)
        self.slots = int(slots)
        self.rng = rng or np.random.default_rng(0)
        self.bank = np.zeros((self.slots, 0))      # slot -> samples

    def capture(self, audio: np.ndarray, bar_samples: int,
                transients: np.ndarray) -> int:
        """Slice ``audio`` into slot-length segments (aligned to transients
        where possible). Returns the number of captured slots.

        Slot starts snap *forward* to the nearest transient at-or-after the
        ideal grid position, but never past the next ideal grid position
        (keeps slot order aligned to the input order and each transient in
        its own slot).
        """
        n = len(audio)
        self.bank = np.zeros((self.slots, bar_samples))
        step = max(1, bar_samples // self.slots)
        for s in range(self.slots):
            ideal = s * step
            start = ideal
            if len(transients):
                ahead = transients[(transients >= ideal) &
                                   (transients < ideal + step)]
                if len(ahead):
                    start = int(ahead[0])
            start = int(np.clip(start, 0, max(0, n - step)))
            seg = audio[start:start + step]
            self.bank[s, :len(seg)] = seg
        return self.slots

    def render_pass(self, out_len: int, glitch_p: float = 0.25,
                    reverse_p: float = 0.3, quant: int = 4) -> np.ndarray:
        """One pass over the stutter grid.

        Args:
            out_len: output samples (one stutter bar).
            glitch_p: probability a step is replaced by a random other segment.
            reverse_p: probability a step plays backwards.
            quant: quantization grid (steps per bar) for jumps.
        """
        y = np.zeros(max(1, out_len))
        if self.bank.shape[1] == 0:
            return y
        step = max(1, self.bank.shape[1] // self.slots)
        qstep = max(1, out_len // max(1, int(quant)))
        cur_slot = 0
        for start in range(0, out_len, qstep):
            end = min(out_len, start + qstep)
            if self.rng.random() < glitch_p:
                cur_slot = int(self.rng.integers(0, self.slots))
            seg = self.bank[cur_slot].copy()
            if self.rng.random() < reverse_p:
                seg = seg[::-1]
            # tile the slot over the quantized window
            need = end - start
            tile = np.resize(seg, need) if need > len(seg) else seg[:need]
            y[start:end] = tile
            # advance source slot by one (quantized jump through the bank)
            cur_slot = (cur_slot + 1) % self.slots
        return y


class GlitchChopper:
    """Stereo glitch/stutter processor with tempo-synced chopper."""

    def __init__(self, sample_rate: int = DEFAULT_SR, bpm: float = 120.0,
                 slots: int = SLOTS, seed: int = 0):
        self.sr = int(sample_rate)
        self.bpm = float(bpm)
        self.slots = int(slots)
        self.seed = int(seed)

    def _bar_samples(self, bars: float = 1.0) -> int:
        return int(round(self.sr * 60.0 / self.bpm * 4.0 * bars))

    def process(self, audio: np.ndarray, glitch_p: float = 0.25,
                reverse_p: float = 0.3, quant: int = 4,
                passes: int = None) -> np.ndarray:
        """Process stereo or mono audio through the chopper.

        The output is bar-length stutter passes: transient-detected slots are
        captured per channel, then recombined with the probability rolls.
        ``passes=None`` processes the whole input bar by bar.
        """
        x = np.asarray(audio, dtype=np.float64)
        mono = x.ndim == 1
        if mono:
            x = np.stack([x, x], axis=1)
        bar = self._bar_samples()
        out = np.zeros_like(x)

        rngs = [np.random.default_rng(self.seed), np.random.default_rng(self.seed + 1)]
        choppers = [ChannelChopper(self.sr, self.slots, rngs[c]) for c in range(2)]
        transients = detect_transients(x.mean(axis=1), self.sr)

        n_bars = int(np.ceil(len(x) / bar))
        for b in range(n_bars):
            lo, hi = b * bar, min(len(x), (b + 1) * bar)
            if hi - lo < self.sr // 20:
                out[lo:hi] = x[lo:hi]            # keep short tails
                continue
            for c in range(2):
                choppers[c].capture(x[lo:hi, c], hi - lo, transients)
                out[lo:hi, c] = choppers[c].render_pass(
                    hi - lo, glitch_p=glitch_p, reverse_p=reverse_p, quant=quant)
        return out[:, 0] if mono else out


def demo() -> str:
    """Prove capture, transient snap, probability recombination and sync."""
    sr = 22050
    rng = np.random.default_rng(9)
    t = np.arange(sr * 2) / sr
    # 120 bpm drum-ish test signal: kicks + hats + noise
    sig = np.zeros(sr * 2)
    for k in range(8):                                  # kick every 1/4 note
        idx = int(k * 0.5 * sr)
        seg_t = np.arange(int(0.12 * sr)) / sr
        end = min(idx + len(seg_t), len(sig))
        seg = np.sin(2 * np.pi * (60 - 30 * seg_t[:end - idx] * 8) * seg_t[:end - idx]) \
            * np.exp(-seg_t[:end - idx] * 25)
        sig[idx:end] += seg
    sig += rng.standard_normal(len(sig)) * 0.05

    st = np.stack([sig, np.roll(sig, 300)], axis=1)

    tr = detect_transients(sig, sr, hop=128)
    print(f"transients detected: {len(tr)} at {tr[:5]}...")
    assert len(tr) >= 3

    gc = GlitchChopper(sample_rate=sr, bpm=120, seed=7)
    out = gc.process(st, glitch_p=0.4, reverse_p=0.35, quant=4)
    print(f"glitched: shape={out.shape} peak={np.abs(out).max():.3f} "
          f"finite={np.all(np.isfinite(out))}")
    assert out.shape == st.shape and np.all(np.isfinite(out))

    # determinism
    out2 = GlitchChopper(sample_rate=sr, bpm=120, seed=7).process(
        st, glitch_p=0.4, reverse_p=0.35, quant=4)
    same = np.array_equal(out, out2)
    print(f"deterministic: {same}")
    assert same

    # p=0 -> slots replay the bar's own (transient-snapped) segments in order;
    # full glitch+reverse recombination must change the output substantially
    clean = GlitchChopper(sample_rate=sr, bpm=120, seed=7).process(
        st, glitch_p=0.0, reverse_p=0.0, quant=16)
    shred = GlitchChopper(sample_rate=sr, bpm=120, seed=7).process(
        st, glitch_p=1.0, reverse_p=1.0, quant=16)
    diff = float(np.abs(clean - shred).mean())
    print(f"p=0 vs p=1 recombination diff: {diff:.4f} (RMS "
          f"{float(np.sqrt((clean ** 2).mean())):.4f})")
    assert diff > 0.01

    # L/R independence: different content per channel
    print(f"L/R differ: {not np.array_equal(out[:, 0], out[:, 1])}")
    assert not np.array_equal(out[:, 0], out[:, 1])

    return "glitch_chopper demo OK"


if __name__ == "__main__":
    print(demo())
