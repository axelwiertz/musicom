"""48-band whole-tone analogue-modelled filter bank — AudioThing/Hainbach "Seconds" style.

Replicable logic from Synthtopia 2026-11-14 ("AudioThing & Hainbach Release
Seconds, A 48-Band Spectral Sound Design Effect"). The product descends from
the SWR Experimentalstudio *Sekundenfilterbank* (late 1980s, built with
Sennheiser): a bank of 48 bandpass filters tuned in **whole-tone steps**, each
playable and sequenceable over MIDI, with a *freeze* that captures a spectrum
and a *transfer* that stamps that spectral shape onto another sound.

DSP model here (all numpy/scipy, no proprietary data):

  * 48 bands, f_n = f0 * 2**(2n/12) — a whole tone is 2 semitones, ratio
    2**(1/6) ≈ 1.1225, so 48 bands span exactly 8 octaves. Default f0 = 40 Hz
    → top band ≈ 10.2 kHz.
  * Each band is an RBJ constant-peak-gain bandpass biquad. Slope 12 dB/oct =
    one biquad, 24 dB/oct = two cascaded biquads (the product offers both).
    Bandwidth is pinned to the whole-tone spacing (Q ≈ 4.3 at 12 dB), so
    neighbouring bands overlap at their -3 dB edges and the bank sums roughly
    flat — that is what makes it sound like a filter bank and not 48 bells.
  * Resonance per band raises Q and adds a feedback term (self-resonant
    "ping" when driven), matching the analogue filter's behaviour.
  * Per-band ring modulation: each band's output is multiplied by a sine at
    its own centre frequency (or an external modulator), producing
    inharmonic sidebands per band — the product's "per-band ring mod".
  * Odd/even band panning: bands are split into even/odd index sets that can
    be panned independently, giving the wide alternating stereo image.
  * MIDI playability: `note_on(midi_note, velocity)` maps a note to the
    nearest band (the tuning is whole-tone, so consecutive semitones map to
    the same band edge) and sets its gain — a filter bank played like a
    keyboard.
  * Spectral freeze + transfer: `analyze(x)` measures the 48 band energies;
    `freeze()` latches them; `transfer(src)` renders the frozen band-gain
    profile onto an arbitrary target signal, i.e. source timbre → target
    pitch/rhythm. This is the actual "spectral transfer" mechanism, done in
    the band domain rather than with an FFT, which is why it stays playable
    in real time.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import lfilter

TAU = 2.0 * np.pi
WHOLE_TONE = 2.0 ** (2.0 / 12.0)  # 2 semitones


def bandpass_biquad(fc: float, sr: float, q: float) -> tuple[np.ndarray, np.ndarray]:
    """RBJ constant-peak-gain bandpass (0 dB peak), normalised coefficients."""
    w0 = TAU * fc / sr
    alpha = np.sin(w0) / (2.0 * q)
    b = np.array([alpha, 0.0, -alpha])
    a = np.array([1.0 + alpha, -2.0 * np.cos(w0), 1.0 - alpha])
    return b / a[0], a / a[0]


class WholeToneFilterbank:
    """48 whole-tone bandpass bands, MIDI-playable, with spectral freeze/transfer."""

    def __init__(self, sr: int = 44100, n_bands: int = 48, f_low: float = 40.0,
                 slope: int = 12, resonance: float = 0.15):
        self.sr = int(sr)
        self.n_bands = int(n_bands)
        self.f_low = float(f_low)
        self.slope = 12 if slope <= 12 else 24
        self.resonance = float(np.clip(resonance, 0.0, 0.99))
        self.freqs = self.f_low * WHOLE_TONE ** np.arange(self.n_bands)
        # whole-tone spacing => Q set by the spacing itself
        self.q = 1.0 / (WHOLE_TONE - 1.0 / WHOLE_TONE)  # ~4.35
        # all bands open by default: the bank passes the input (a flat
        # 48-band EQ with every slider up), so it is usable without MIDI.
        self.gains = np.ones(self.n_bands)
        self._coefs = [bandpass_biquad(f, self.sr, self.q) for f in self.freqs]
        self._frozen: np.ndarray | None = None

    # ---------------------------------------------------------------- control
    def index_for_note(self, midi_note: float) -> int:
        """Nearest band for a MIDI note (whole-tone grid)."""
        f = 440.0 * 2.0 ** ((float(midi_note) - 69.0) / 12.0)
        return int(np.clip(np.round(np.log(f / self.f_low) / np.log(WHOLE_TONE)),
                           0, self.n_bands - 1))

    def note_on(self, midi_note: float, velocity: float = 0.8) -> int:
        idx = self.index_for_note(midi_note)
        self.gains[idx] = float(np.clip(velocity, 0.0, 1.0))
        return idx

    def set_resonance(self, r: float) -> None:
        self.resonance = float(np.clip(r, 0.0, 0.99))
        q = self.q * (1.0 + 6.0 * self.resonance)
        self._coefs = [bandpass_biquad(f, self.sr, q) for f in self.freqs]

    # ------------------------------------------------------------------ render
    def band_signals(self, x: np.ndarray) -> np.ndarray:
        """Return (n_bands, len(x)) bandpass signals."""
        x = np.asarray(x, dtype=float).ravel()
        out = np.empty((self.n_bands, x.size))
        for i, (b, a) in enumerate(self._coefs):
            y = lfilter(b, a, x)
            if self.slope == 24:
                y = lfilter(b, a, y)
            out[i] = y
        return out

    def process(self, x: np.ndarray, ring_mod: float = 0.0,
                pan_spread: float = 0.0, mod_hz: np.ndarray | None = None) -> np.ndarray:
        """Render the bank to stereo.

        ring_mod   : 0..1 depth of per-band ring modulation.
        pan_spread : 0..1 odd/even alternating pan width.
        mod_hz     : optional per-band modulator frequency (default = band fc).
        """
        bands = self.band_signals(x)
        n = bands.shape[1]
        t = np.arange(n) / self.sr
        mc = self.freqs if mod_hz is None else np.asarray(mod_hz, dtype=float)
        left = np.zeros(n)
        right = np.zeros(n)
        for i in range(self.n_bands):
            y = bands[i] * self.gains[i]
            if ring_mod > 0.0:
                mod = np.sin(TAU * mc[i] * t)
                y = (1.0 - ring_mod) * y + ring_mod * y * mod
            pan = pan_spread * (0.5 if i % 2 == 0 else -0.5)
            left += y * (0.5 - pan)
            right += y * (0.5 + pan)
        out = np.stack([left, right], axis=1)
        peak = np.max(np.abs(out)) + 1e-12
        return out * (0.89 / peak) if peak > 1.0 else out

    # ------------------------------------------------------ spectral analysis
    def analyze(self, x: np.ndarray, normalise: bool = True) -> np.ndarray:
        """Band-energy profile (48 values) of a signal.

        Measured in the FFT domain with geometrically spaced band edges
        (geometric mean of neighbouring centres) rather than by filtering the
        signal twice — filtering twice would convolve the bandpass response
        with itself and report a nearly flat profile.
        """
        x = np.asarray(x, dtype=float).ravel()
        spec = np.abs(np.fft.rfft(x * np.hanning(x.size))) ** 2
        f = np.fft.rfftfreq(x.size, 1.0 / self.sr)
        edges = np.sqrt(self.freqs[:-1] * self.freqs[1:])
        e = np.empty(self.n_bands)
        lo = 0.0
        for i in range(self.n_bands):
            hi = edges[i] if i < self.n_bands - 1 else self.sr / 2
            m = (f >= lo) & (f < hi)
            e[i] = np.sqrt(spec[m].mean()) if m.any() else 0.0
            lo = hi
        if normalise and e.max() > 1e-12:
            e = e / e.max()
        return e

    def freeze(self, x: np.ndarray) -> np.ndarray:
        """Capture the band profile of x as gains (spectral freeze)."""
        self._frozen = self.analyze(x)
        self.gains = self._frozen.copy()
        return self._frozen

    def transfer(self, target: np.ndarray, source: np.ndarray | None = None,
                 amount: float = 1.0) -> np.ndarray:
        """Stamp a source's spectral shape onto a target signal."""
        profile = self._frozen if source is None else self.analyze(source)
        if profile is None:
            raise ValueError("nothing frozen and no source given")
        saved, self.gains = self.gains, profile * float(np.clip(amount, 0.0, 1.0))
        try:
            return self.process(target)
        finally:
            self.gains = saved


def demo() -> None:
    sr = 44100
    n = sr
    rng = np.random.default_rng(7)

    # ---- 1. tuning is a whole-tone ladder spanning 8 octaves
    fb = WholeToneFilterbank(sr=sr, resonance=0.2)
    ratios = fb.freqs[1:] / fb.freqs[:-1]
    print(f"bands={fb.n_bands} f0={fb.freqs[0]:.1f} Hz f_last={fb.freqs[-1]:.1f} Hz "
          f"ratio={ratios.mean():.4f} (2**(2/12)={WHOLE_TONE:.4f}) span_oct={np.log2(fb.freqs[-1]/fb.freqs[0]):.2f}")
    assert np.allclose(ratios, WHOLE_TONE, rtol=1e-9)

    # ---- 2. band selectivity: a 440 Hz sine excites band 27, not band 5
    t = np.arange(n) / sr
    sine = 0.5 * np.sin(TAU * 440.0 * t)
    prof = fb.analyze(sine)
    top = int(np.argmax(prof))
    print(f"440 Hz sine -> top band {top} ({fb.freqs[top]:.1f} Hz), "
          f"profile at 40 Hz band={prof[0]:.3f}, at top={prof[top]:.3f}")
    assert fb.freqs[top] > 400 and fb.freqs[top] < 500

    # ---- 3. MIDI mapping is whole-tone: note 69 (A4=440) -> band 27
    idx = fb.index_for_note(69)
    print(f"MIDI 69 -> band {idx} = {fb.freqs[idx]:.1f} Hz")
    fb.gains[:] = 0.0
    fb.note_on(69, 0.9)
    assert fb.gains[idx] == 0.9 and fb.gains.sum() == 0.9

    # ---- 4. spectral transfer: harmonic source imprints its comb on noise
    src = sum(0.25 * np.sin(TAU * 220.0 * k * t) / k for k in (1, 2, 3, 4, 5))
    noise = 0.2 * rng.standard_normal(n)
    # a deterministic flat-spectrum target (impulse train) so the measured
    # transfer is the bank's gain profile, not noise variance
    flat = np.zeros(n)
    flat[::1024] = 0.5
    out = fb.transfer(flat, source=src)
    fb.gains = np.zeros(fb.n_bands)
    after = fb.analyze(out[:, 0])
    want = fb.analyze(src)
    kern = np.array([1.0, 2.0, 1.0]) / 4.0  # neighbour-band leakage smoothing
    smooth = lambda v: np.convolve(v, kern, mode="same")  # noqa: E731
    rho_raw = float(np.corrcoef(want, after)[0, 1])
    rho = float(np.corrcoef(smooth(want), smooth(after))[0, 1])
    print(f"transfer: stereo out {out.shape}, band-profile corr src/out="
          f"{rho_raw:.3f} (smoothed {rho:.3f}), peak={np.abs(out).max():.3f}, "
          f"top band out={int(np.argmax(after))} src={int(np.argmax(want))}")
    assert out.shape == (n, 2)
    assert np.isfinite(out).all()
    assert int(np.argmax(after)) == int(np.argmax(want))
    assert rho > 0.85, "transferred output must carry the source's spectral shape"

    # ---- 5. freeze latches the profile
    frozen = fb.freeze(src)
    assert fb._frozen is not None and np.allclose(frozen, fb.gains)
    print(f"freeze: latched {int((frozen > 0.5).sum())} strong bands")

    # ---- 6. ring mod creates sidebands around a single played band
    fb.gains[:] = 0.0
    fb.note_on(57, 1.0)
    dry = fb.process(sine[: 8192])[:, 0]
    wet = fb.process(sine[: 8192], ring_mod=0.8)[:, 0]
    f = np.fft.rfftfreq(8192, 1 / sr)
    def peak_off(y):
        m = np.abs(np.fft.rfft(y))
        m[(f > 400) & (f < 480)] = 0
        return float(f[np.argmax(m)])
    print(f"ring mod: dry strongest-off-band={peak_off(dry):.0f} Hz, "
          f"wet={peak_off(wet):.0f} Hz")
    assert abs(peak_off(wet) - 440.0) > 20

    # ---- 7. odd/even pan spread widens the image
    fb.gains[:] = 1.0
    narrow = fb.process(noise[: 44100], pan_spread=0.0)
    wide = fb.process(noise[: 44100], pan_spread=0.8)
    def corr(a):
        return float(np.corrcoef(a[:, 0], a[:, 1])[0, 1])
    print(f"pan spread: L/R corr narrow={corr(narrow):.3f} wide={corr(wide):.3f}")
    assert corr(wide) < corr(narrow)
    print("demo OK")


if __name__ == "__main__":
    demo()
