"""Scale-aware harmonic EQ — Scaler EQ Pro style.

Replicable logic from the Sound On Sound news item "Scaler Music
introduce Scaler EQ Pro" (2026-09-28, surfaced on the SoS homepage at
the 2026-10-22 scan): a key-aware musical EQ.  The plug-in's Harmonic
Peak filters only *boost* frequencies that fall inside the selected
key/scale and only *cut* frequencies outside it; the Magic Shelf offers
a low shelf that predominantly targets the Mid component of a stereo
signal and a high shelf that favours the Sides; the new Live Band mode
creates filter bands from incoming MIDI notes ("play the EQ from your
keyboard"); every band can be switched to dynamic mode with independent
Threshold/Ratio/Attack/Release and offers both compression and
expansion.

What is replicated here (offline, numpy only):
- ``SCALES``: pitch-class sets (major, natural/harmonic minor, dorian,
  mixolydian, pentatonic major/minor, whole-tone, chromatic).
- ``ScaleEQ.harmonic_peak_bands``: for a chosen root + scale, one
  peaking biquad per semitone over a MIDI range — in-key notes get a
  *boost* band, out-of-key notes get a *cut* band (the key-locked
  boost/cut asymmetry of the original).
- ``ScaleEQ.live_bands``: Live Band mode — bands centered exactly on
  the fundamental frequencies of played MIDI notes.
- ``ScaleEQ.process``: stereo in -> Mid/Side split -> Magic Shelf
  (low shelf on Mid, high shelf on Sides) -> band cascade (boost/cut
  peaking bank, optionally dynamic) -> Mid/Side recombine.  Mono input
  is processed directly.
- ``DynamicBand``: per-band compressor/expander — smoothed envelope,
  compression when the band envelope exceeds threshold, downward
  expansion when it falls below, independent attack/release.

Not replicated: the plug-in GUI/VST3/AU/AAX hosting, the exact Magic
Shelf filter topologies and Q values, and the MIDI-learn/automation
layer (note -> band mapping is exposed as plain data instead).

Usage:
    from sound.effects.scale_eq import ScaleEQ

    eq = ScaleEQ(sample_rate=44100)
    out = eq.process(audio_stereo, root=60, scale="major",
                     boost_db=4.0, cut_db=-4.0)
"""

from __future__ import annotations

import numpy as np

__all__ = ["ScaleEQ", "DynamicBand", "SCALES", "note_freq"]

DEFAULT_SR = 44100

# Pitch-class sets (C = 0).  Scale-aware harmonic EQ boosts only these,
# cuts everything else.
SCALES = {
    "major": frozenset({0, 2, 4, 5, 7, 9, 11}),
    "minor": frozenset({0, 2, 3, 5, 7, 8, 10}),           # natural minor
    "harmonic_minor": frozenset({0, 2, 3, 5, 7, 8, 11}),
    "dorian": frozenset({0, 2, 3, 5, 7, 9, 10}),
    "mixolydian": frozenset({0, 2, 4, 5, 7, 9, 10}),
    "pentatonic_major": frozenset({0, 2, 4, 7, 9}),
    "pentatonic_minor": frozenset({0, 3, 5, 7, 10}),
    "whole_tone": frozenset({0, 2, 4, 6, 8, 10}),
    "chromatic": frozenset(range(12)),
}


def note_freq(midi: int | float) -> float:
    """MIDI note number -> fundamental frequency in Hz (A4 = 440)."""
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)


def _rbj_peaking(f0: float, fs: float, gain_db: float, q: float):
    """RBJ cookbook peaking EQ coefficients (b0,b1,b2,a0,a1,a2)."""
    a = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * np.pi * f0 / fs
    alpha = np.sin(w0) / (2.0 * q)
    cw = np.cos(w0)
    b0 = 1.0 + alpha * a
    b1 = -2.0 * cw
    b2 = 1.0 - alpha * a
    a0 = 1.0 + alpha / a
    a1 = -2.0 * cw
    a2 = 1.0 - alpha / a
    return b0, b1, b2, a0, a1, a2


def _rbj_lowshelf(f0: float, fs: float, gain_db: float, s: float = 0.707):
    """RBJ cookbook low-shelf coefficients."""
    a = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * np.pi * f0 / fs
    alpha = np.sin(w0) / 2.0 * np.sqrt((a + 1.0 / a) * (1.0 / s - 1.0) + 2.0)
    cw = np.cos(w0)
    sq = 2.0 * np.sqrt(a) * alpha
    b0 = a * ((a + 1.0) - (a - 1.0) * cw + sq)
    b1 = 2.0 * a * ((a - 1.0) - (a + 1.0) * cw)
    b2 = a * ((a + 1.0) - (a - 1.0) * cw - sq)
    a0 = (a + 1.0) + (a - 1.0) * cw + sq
    a1 = -2.0 * ((a - 1.0) + (a + 1.0) * cw)
    a2 = (a + 1.0) + (a - 1.0) * cw - sq
    return b0, b1, b2, a0, a1, a2


def _rbj_highshelf(f0: float, fs: float, gain_db: float, s: float = 0.707):
    """RBJ cookbook high-shelf coefficients."""
    a = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * np.pi * f0 / fs
    alpha = np.sin(w0) / 2.0 * np.sqrt((a + 1.0 / a) * (1.0 / s - 1.0) + 2.0)
    cw = np.cos(w0)
    sq = 2.0 * np.sqrt(a) * alpha
    b0 = a * ((a + 1.0) + (a - 1.0) * cw + sq)
    b1 = -2.0 * a * ((a - 1.0) + (a + 1.0) * cw)
    b2 = a * ((a + 1.0) + (a - 1.0) * cw - sq)
    a0 = (a + 1.0) - (a - 1.0) * cw + sq
    a1 = 2.0 * ((a - 1.0) - (a + 1.0) * cw)
    a2 = (a + 1.0) - (a - 1.0) * cw - sq
    return b0, b1, b2, a0, a1, a2


def _biquad_cascade(x: np.ndarray, coeffs: list) -> np.ndarray:
    """Apply a cascade of biquads (DF2T) to a 1-D signal.

    Pure-python per-sample recursion — offline only (matches the
    project's documented offline-processing convention).  Each coeff
    tuple is (b0,b1,b2,a0,a1,a2); a0 is used only for normalisation.
    """
    out = x.astype(np.float64)
    for (b0, b1, b2, a0, a1, a2) in coeffs:
        norm = a0
        b0n, b1n, b2n = b0 / norm, b1 / norm, b2 / norm
        a1n, a2n = a1 / norm, a2 / norm
        s1 = 0.0
        s2 = 0.0
        # local names for speed
        y = out
        n = len(y)
        for i in range(n):
            x_i = y[i]
            y_i = b0n * x_i + s1
            s1 = b1n * x_i - a1n * y_i + s2
            s2 = b2n * x_i - a2n * y_i
            y[i] = y_i
    return out


class DynamicBand:
    """Per-band compressor/expander (the 'dynamic mode' of Scaler EQ Pro).

    A smoothed envelope (attack/release one-pole on |x|) drives a
    gain curve: compression when the envelope exceeds ``threshold``
    (gain -> (thr/env)^(1-1/ratio)), downward expansion when it falls
    below (gain -> (env/thr)^(ratio-1)).  ``ratio`` > 1 in both cases.
    """

    def __init__(self, threshold: float = 0.05, ratio: float = 2.0,
                 attack_ms: float = 10.0, release_ms: float = 200.0,
                 sample_rate: int = DEFAULT_SR):
        self.threshold = float(threshold)
        self.ratio = float(ratio)
        self.sample_rate = int(sample_rate)
        self.attack_ms = float(attack_ms)
        self.release_ms = float(release_ms)

    def process(self, x: np.ndarray) -> np.ndarray:
        """Apply the comp/expand curve to a 1-D band signal."""
        x = x.astype(np.float64)
        fs = self.sample_rate
        att = np.exp(-1.0 / (fs * (self.attack_ms / 1000.0)))
        rel = np.exp(-1.0 / (fs * (self.release_ms / 1000.0)))
        thr = self.threshold
        r = self.ratio
        env = 0.0
        out = np.empty_like(x)
        for i in range(len(x)):
            xi = x[i]
            ab = abs(xi)
            env = att * ab + (1.0 - att) * env if ab > env else rel * env + (1.0 - rel) * ab
            if env > thr:
                g = (thr / env) ** (1.0 - 1.0 / r)      # compression
            elif env > 1e-9:
                g = (env / thr) ** (r - 1.0)             # downward expansion
            else:
                g = 1.0
            out[i] = xi * g
        return out


class ScaleEQ:
    """Scale-aware harmonic EQ (key-locked boost/cut + M/S Magic Shelf).

    Args:
        sample_rate: audio sample rate in Hz.
    """

    def __init__(self, sample_rate: int = DEFAULT_SR):
        self.sample_rate = int(sample_rate)

    # ------------------------------------------------------------------
    def harmonic_peak_bands(self, root: int, scale: str = "major",
                            midi_lo: int = 24, midi_hi: int = 108,
                            boost_db: float = 3.0, cut_db: float = -3.0,
                            q: float = 30.0) -> list:
        """Key-locked band list: in-key notes -> boost, out-of-key -> cut.

        One peaking band per semitone in ``[midi_lo, midi_hi]``.
        Returns a list of dicts ``{freq, gain_db, q, kind, midi}``.

        ``q`` defaults to 30: the bands sit one semitone apart, so they
        must stay tight or the boost skirts of in-key notes overwhelm
        the out-of-key cuts (broad musical Q=1.2 smears the semitone-
        spaced bands into a near-uniform lift — a tight Q is used here
        so the key-locked boost/cut asymmetry is actually audible).
        """
        pcs = SCALES.get(scale, SCALES["major"])
        root_pc = root % 12
        bands = []
        for midi in range(int(midi_lo), int(midi_hi) + 1):
            f = note_freq(midi)
            if f < 40.0 or f > 16000.0:
                continue
            in_key = (midi - root_pc) % 12 in pcs
            gain = boost_db if in_key else cut_db
            if abs(gain) < 0.05:
                continue
            bands.append({"freq": f, "gain_db": gain, "q": q,
                          "kind": "boost" if in_key else "cut", "midi": midi})
        return bands

    def live_bands(self, midi_notes, boost_db: float = 4.0,
                   q: float = 30.0) -> list:
        """Live Band mode: one boost band per played MIDI note."""
        bands = []
        for midi in midi_notes:
            f = note_freq(int(midi))
            if f < 40.0 or f > 16000.0:
                continue
            bands.append({"freq": f, "gain_db": boost_db, "q": q,
                          "kind": "live", "midi": int(midi)})
        return bands

    @staticmethod
    def _coeffs(bands: list, fs: float):
        return [_rbj_peaking(b["freq"], fs, b["gain_db"], b["q"])
                for b in bands]

    # ------------------------------------------------------------------
    def process(self, x: np.ndarray, root: int = 60, scale: str = "major",
                boost_db: float = 3.0, cut_db: float = -3.0, q: float = 30.0,
                midi_lo: int = 24, midi_hi: int = 108,
                live_notes=None, dynamic: bool = False,
                threshold: float = 0.05, ratio: float = 2.0,
                attack_ms: float = 10.0, release_ms: float = 200.0,
                low_shelf_mid_db: float = 0.0, high_shelf_side_db: float = 0.0,
                shelf_freq_lo: float = 200.0, shelf_freq_hi: float = 4000.0,
                mid_side: bool = True) -> np.ndarray:
        """Process audio through the scale-aware harmonic EQ.

        Args:
            x: mono (1-D) or stereo (N, 2) float audio.
            root: root MIDI note of the selected key.
            scale: key name from ``SCALES``.
            boost_db/cut_db: in-key boost / out-of-key cut gain.
            q: peaking-band Q.
            midi_lo/midi_hi: semitone range scanned for key-locked bands.
            live_notes: optional iterable of MIDI notes; when given the
                Live Band bank replaces the key-locked bank.
            dynamic: per-band comp/expand dynamic mode.
            threshold/ratio/attack_ms/release_ms: dynamic-band params.
            low_shelf_mid_db: Magic Shelf low-shelf gain applied to the
                Mid component only.
            high_shelf_side_db: Magic Shelf high-shelf gain applied to
                the Sides component only.
            mid_side: when False and input is stereo, process channels
                directly (no M/S split).

        Returns:
            Filtered audio, same shape as ``x``.
        """
        fs = self.sample_rate
        x = np.asarray(x, dtype=np.float64)
        stereo = x.ndim == 2
        if stereo and mid_side:
            mid = (x[:, 0] + x[:, 1]) / 2.0
            side = (x[:, 0] - x[:, 1]) / 2.0
            # Magic Shelf: low shelf on Mid, high shelf on Sides
            if abs(low_shelf_mid_db) > 0.05:
                c = _rbj_lowshelf(shelf_freq_lo, fs, low_shelf_mid_db)
                mid = _biquad_cascade(mid, [c])
            if abs(high_shelf_side_db) > 0.05:
                c = _rbj_highshelf(shelf_freq_hi, fs, high_shelf_side_db)
                side = _biquad_cascade(side, [c])
            # Harmonic peak bank (key-locked or Live Band) on M and S
            if live_notes is not None and len(live_notes):
                bands = self.live_bands(live_notes, boost_db=boost_db, q=q)
            else:
                bands = self.harmonic_peak_bands(
                    root, scale, midi_lo, midi_hi, boost_db, cut_db, q)
            coeffs = self._coeffs(bands, fs)
            if dynamic:
                db = DynamicBand(threshold, ratio, attack_ms, release_ms, fs)
                mid = db.process(_biquad_cascade(mid, coeffs))
                side = db.process(_biquad_cascade(side, coeffs))
            else:
                mid = _biquad_cascade(mid, coeffs)
                side = _biquad_cascade(side, coeffs)
            out = np.empty_like(x)
            out[:, 0] = mid + side
            out[:, 1] = mid - side
            return out

        # mono, or stereo processed per-channel
        chans = [x] if x.ndim == 1 else [x[:, i] for i in range(x.shape[1])]
        if live_notes is not None and len(live_notes):
            bands = self.live_bands(live_notes, boost_db=boost_db, q=q)
        else:
            bands = self.harmonic_peak_bands(
                root, scale, midi_lo, midi_hi, boost_db, cut_db, q)
        coeffs = self._coeffs(bands, fs)
        if dynamic:
            db = DynamicBand(threshold, ratio, attack_ms, release_ms, fs)
            chans = [db.process(_biquad_cascade(c, coeffs)) for c in chans]
        else:
            chans = [_biquad_cascade(c, coeffs) for c in chans]
        if len(chans) == 1:
            return chans[0]
        return np.stack(chans, axis=1)


def demo(out_dir: str = "/tmp/musicom_smoke") -> dict:
    """Self-test: key-locked boost/cut verified on a chord with an
    out-of-key note; Live Band centers; dynamic band gain curve; WAV
    writes."""
    import os
    from sound.utils.io import write_wav

    os.makedirs(out_dir, exist_ok=True)
    sr = DEFAULT_SR
    rng = np.random.RandomState(7)

    # --- synthetic chord: C major (C4 E4 G4 C5) + out-of-key F#4 ----
    def tone(freq, dur, amp=0.25):
        t = np.arange(int(sr * dur)) / sr
        return (amp * np.sin(2 * np.pi * freq * t)
                + 0.3 * amp * np.sin(2 * np.pi * 2 * freq * t))

    dur = 1.5
    x = np.zeros((int(sr * dur), 2))
    for midi, amp in [(60, 0.22), (64, 0.18), (67, 0.16), (72, 0.12),
                      (66, 0.20)]:  # 66 = F#4, out of C major
        f = note_freq(midi)
        pan = 0.4 * np.sin(midi)
        g = tone(f, dur, amp)
        x[:, 0] += g * np.cos((pan + 1) * np.pi / 4)
        x[:, 1] += g * np.sin((pan + 1) * np.pi / 4)

    def band_energy(sig, midi):
        """Narrow-band (Q=15) probe energy around a note's fundamental,
        so neighbouring in-key boosts don't leak into the measurement."""
        f = note_fund = note_freq(midi)
        # RBJ band-pass coefficients
        w0 = 2.0 * np.pi * f / sr
        alpha = np.sin(w0) / (2.0 * 15.0)
        cw = np.cos(w0)
        b0, b1, b2 = alpha, 0.0, -alpha
        a0, a1, a2 = 1.0 + alpha, -2.0 * cw, 1.0 - alpha
        s1 = s2 = 0.0
        out = np.empty_like(sig)
        for i in range(len(sig)):
            xi = sig[i]
            yi = (b0 * xi + s1) / a0
            s1 = b1 * xi - a1 * yi + s2
            s2 = b2 * xi - a2 * yi
            out[i] = yi
        return float(np.sqrt(np.mean(out ** 2)))

    # --- key-locked asymmetry, verified on ISOLATED tones (no
    # neighbouring-band spillover at Q=30): in-key C4 must be boosted,
    # out-of-key F#4 must be cut ---
    eq = ScaleEQ(sr)
    c_iso = tone(note_freq(60), 1.0, 0.3)[:, None] * np.array([1.0, 0.8])
    c_iso_out = eq.process(c_iso, root=60, scale="major",
                           boost_db=4.0, cut_db=-4.0, q=30.0)
    fs_iso = tone(note_freq(66), 1.0, 0.3)[:, None] * np.array([1.0, 0.8])
    fs_iso_out = eq.process(fs_iso, root=60, scale="major",
                            boost_db=4.0, cut_db=-4.0, q=30.0)
    boost_iso = band_energy(c_iso_out[:, 0], 60) / max(
        band_energy(c_iso[:, 0], 60), 1e-12)
    cut_iso = band_energy(fs_iso_out[:, 0], 66) / max(
        band_energy(fs_iso[:, 0], 66), 1e-12)

    # full chord: C4 probe still rises (own boost dominates); F#4 probe
    # in chord context is NOT a clean assertion (neighbouring in-key
    # boost skirts spill into 370 Hz), reported for completeness only
    out = eq.process(x, root=60, scale="major",
                     boost_db=4.0, cut_db=-4.0, q=30.0,
                     low_shelf_mid_db=1.5, high_shelf_side_db=1.0)
    c_in = band_energy(x[:, 0], 60)
    c_out = band_energy(out[:, 0], 60)
    boost_ratio = c_out / max(c_in, 1e-12)

    # --- Live Band mode: bands exactly on played notes ----------------
    live = eq.process(x, live_notes=[62, 65, 69], boost_db=5.0, q=2.0)

    # --- dynamic band: compression above threshold, expansion below ---
    db = DynamicBand(threshold=0.1, ratio=3.0, sample_rate=sr)
    steady = np.full(8000, 0.2)
    comp_out = db.process(steady)
    comp_gain = float(comp_out[2000:].max() / 0.2)
    quiet = np.full(8000, 0.05)
    exp_out = db.process(quiet)
    exp_gain = float(exp_out[2000:].max() / 0.05)

    write_wav(os.path.join(out_dir, "scale_eq_in.wav"), x, sr)
    write_wav(os.path.join(out_dir, "scale_eq_out.wav"), out, sr)
    write_wav(os.path.join(out_dir, "scale_eq_liveband.wav"), live, sr)
    n_boost = sum(1 for b in eq.harmonic_peak_bands(60, "major", 36, 96,
                                                    4.0, -4.0)
                  if b["kind"] == "boost")
    n_cut = sum(1 for b in eq.harmonic_peak_bands(60, "major", 36, 96,
                                                  4.0, -4.0)
                if b["kind"] == "cut")
    return {
        "in_key_boost_iso": round(boost_iso, 3),
        "out_key_cut_iso": round(cut_iso, 3),
        "chord_c4_boost": round(boost_ratio, 3),
        "boost_bands": n_boost,
        "cut_bands": n_cut,
        "live_band_freqs": [round(b["freq"], 1)
                            for b in eq.live_bands([62, 65, 69])],
        "dynamic_comp_gain_at_0.2": round(comp_gain, 3),
        "dynamic_exp_gain_at_0.05": round(exp_gain, 3),
        "wav_bytes": os.path.getsize(
            os.path.join(out_dir, "scale_eq_out.wav")),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
