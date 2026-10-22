"""Six-oscillator always-on drone voice — Impact Soundworks Circle
Drone Of Doom style.

Replicable logic from the Sound On Sound review "Impact Soundworks
Circle Drone Of Doom" (November 2026 issue, surfaced on the SoS
homepage at the 2026-10-22 scan): a Kontakt instrument emulating Sam
Battle's (Look Mum No Computer) one-off hardware drone.  The engine
combines six oscillators that are always on, whose individual tuning
can be adjusted over +/-3600 cents (+/-36 semitones) with an outer ring
of knobs, plus a Random Tune button; a middle ring provides per-
oscillator waveshaping, drone-friendly attack/release amplifier
envelope, reverb, "Thick" (a global detuning + stereo adjustment of the
six oscillators) and "More" (adds unison voices); an inner ring adds
filter/EQ, and the dead-centre "Unity" knob scales the tuning offsets
for every oscillator (all converge to the root).

What is replicated here (offline, numpy only):
- ``CircleDrone``: 6 always-on oscillators with per-oscillator tuning
  offsets in cents (range +/-3600), selectable waveforms
  (saw/square/tri/sine), per-oscillator tanh waveshaping drive,
  stereo pan placement and ``thick`` (global detune multiplier +
  stereo width).
- ``unison``: ``more`` extra detuned voices per oscillator (seeded
  spread) with 1/sqrt(n) amplitude compensation.
- ``unity``: a single scalar that scales ALL tuning offsets — at
  ``unity=0`` every oscillator converges on the root frequency.
- ``random_tune(seed)``: the Random Tune button — per-oscillator
  offsets drawn uniformly from [-3600, +3600] cents.
- drone-length attack/release envelope, 2-pole resonant low-pass
  filter, and a compact Schroeder reverb tail (4 combs + 2 allpasses).

Not replicated: the Kontakt instrument UI/playback engine, the
snapshot preset library, the exact hardware's analog circuitry and
"Unity" taper, and the EQ section (filter approximates it).

Usage:
    from sound.synthesis.circle_drone import CircleDrone

    d = CircleDrone(sample_rate=44100)
    audio = d.render(duration_sec=4.0, root_hz=110.0, seed=3)
"""

from __future__ import annotations

import numpy as np

__all__ = ["CircleDrone", "DETUNE_RANGE_CENTS"]

DEFAULT_SR = 44100
DETUNE_RANGE_CENTS = 3600.0

_WAVEFORMS = ("saw", "square", "tri", "sine")


def _osc_sample(phase: np.ndarray, wave: str) -> np.ndarray:
    """Waveform lookup from normalised phase in [0, 1)."""
    if wave == "saw":
        return 2.0 * phase - 1.0
    if wave == "square":
        return np.where(phase < 0.5, 1.0, -1.0)
    if wave == "tri":
        return 2.0 * np.abs(2.0 * phase - 1.0) - 1.0
    return np.sin(2.0 * np.pi * phase)


class CircleDrone:
    """Six always-on oscillator drone voice.

    Args:
        sample_rate: Hz.
        detune_cents: length-6 array of per-oscillator tuning offsets
            (default: an asymmetric +/-12-semitone spread).
        waveforms: per-oscillator waveform names
            (saw/square/tri/sine).
        waveshape_drive: per-oscillator tanh drive (0 = bypass).
        more: unison voices per oscillator (added detuned copies).
        unison_spread_cents: RMS spread of unison detuning.
        thick: global detune multiplier (1.0 = full, 0.5 = half).
        width: stereo width 0..1 (pan spread of the six oscillators).
        unity: scales ALL tuning offsets (1.0 = full detune, 0.0 =
            every oscillator at the root).
        filter_cutoff: 2-pole LP cutoff in Hz.
        filter_res: filter resonance Q.
        env_attack / env_release: seconds.
        reverb_mix: wet fraction 0..1.
        reverb_decay: Schroeder comb feedback 0..~0.95.
        gain: output gain.
    """

    def __init__(self, sample_rate: int = DEFAULT_SR,
                 detune_cents=None, waveforms=None, waveshape_drive=None,
                 more: int = 1, unison_spread_cents: float = 8.0,
                 thick: float = 1.0, width: float = 0.8, unity: float = 1.0,
                 filter_cutoff: float = 6500.0, filter_res: float = 0.9,
                 env_attack: float = 0.4, env_release: float = 1.5,
                 reverb_mix: float = 0.25, reverb_decay: float = 0.72,
                 gain: float = 0.85):
        self.sample_rate = int(sample_rate)
        self.detune_cents = np.asarray(
            detune_cents if detune_cents is not None
            else [0.0, 300.0, -400.0, 700.0, -900.0, 1200.0],
            dtype=np.float64)
        self.waveforms = list(waveforms if waveforms is not None
                              else ["saw", "saw", "square", "saw",
                                    "tri", "saw"])
        self.waveshape_drive = np.asarray(
            waveshape_drive if waveshape_drive is not None
            else [0.6, 1.2, 0.0, 1.8, 0.3, 2.2], dtype=np.float64)
        self.more = int(more)
        self.unison_spread_cents = float(unison_spread_cents)
        self.thick = float(thick)
        self.width = float(width)
        self.unity = float(unity)
        self.filter_cutoff = float(filter_cutoff)
        self.filter_res = float(filter_res)
        self.env_attack = float(env_attack)
        self.env_release = float(env_release)
        self.reverb_mix = float(reverb_mix)
        self.reverb_decay = float(reverb_decay)
        self.gain = float(gain)

    # ------------------------------------------------------------------
    def random_tune(self, seed: int = 0) -> np.ndarray:
        """Random Tune: per-oscillator offsets uniform in +/-3600 cents."""
        rng = np.random.RandomState(seed)
        self.detune_cents = rng.uniform(-DETUNE_RANGE_CENTS,
                                        DETUNE_RANGE_CENTS, 6)
        return self.detune_cents.copy()

    def effective_cents(self, unity: float | None = None) -> np.ndarray:
        """Per-oscillator offsets after Unity scaling + Thick."""
        u = self.unity if unity is None else unity
        return self.detune_cents * self.thick * u

    # ------------------------------------------------------------------
    def _filter_lp(self, x: np.ndarray) -> np.ndarray:
        """One 2-pole resonant low-pass (RBJ) applied in place."""
        fs = self.sample_rate
        w0 = 2.0 * np.pi * self.filter_cutoff / fs
        alpha = np.sin(w0) / (2.0 * self.filter_res)
        cw = np.cos(w0)
        b0 = (1.0 - cw) / 2.0
        b1 = 1.0 - cw
        b2 = b0
        a0 = 1.0 + alpha
        a1 = -2.0 * cw
        a2 = 1.0 - alpha
        s1 = s2 = 0.0
        out = np.empty_like(x)
        for i in range(len(x)):
            xi = x[i]
            yi = (b0 * xi + s1) / a0
            s1 = b1 * xi - a1 * yi + s2
            s2 = b2 * xi - a2 * yi
            out[i] = yi
        return out

    def _schroeder_reverb(self, x: np.ndarray) -> np.ndarray:
        """Compact Schroeder tail (4 combs + 2 allpasses) per channel."""
        fs = self.sample_rate
        comb_ms = [29.7, 37.1, 41.1, 43.7]
        ap_ms = [5.0, 1.7]
        fb = self.reverb_decay
        damp = 0.35
        out = np.empty_like(x)
        wet = np.zeros_like(x)
        for ch in range(x.shape[1]):
            sig = x[:, ch]
            # combs in parallel
            acc = np.zeros_like(sig)
            for ms in comb_ms:
                d = max(2, int(round(fs * ms / 1000.0)))
                buf = np.zeros(d)
                lp = 0.0
                for i in range(len(sig)):
                    delayed = buf[i % d]
                    lp = delayed * (1.0 - damp) + lp * damp
                    buf[i % d] = sig[i] + fb * lp
                    acc[i] += delayed
            acc /= len(comb_ms)
            # two allpasses in series
            for ms in ap_ms:
                d = max(2, int(round(fs * ms / 1000.0)))
                buf = np.zeros(d)
                g = 0.5
                for i in range(len(sig)):
                    x_in = acc[i]
                    delayed = buf[i % d]
                    acc[i] = -g * x_in + delayed
                    buf[i % d] = x_in + g * delayed
            wet[:, ch] = acc
        out = x * (1.0 - self.reverb_mix) + wet * self.reverb_mix
        return out

    # ------------------------------------------------------------------
    def render(self, duration_sec: float, root_hz: float = 110.0,
               unity: float | None = None,
               seed: int | None = None) -> np.ndarray:
        """Render a stereo drone of ``duration_sec`` seconds.

        Args:
            duration_sec: seconds of audio.
            root_hz: root frequency (all oscillators derive from it).
            unity: override for the Unity knob (None = instance value).
            seed: RNG seed for unison voice detuning.

        Returns:
            Stereo float array of shape (N, 2), peak-normalised to 0.95.
        """
        fs = self.sample_rate
        n = int(fs * duration_sec)
        rng = np.random.RandomState(0 if seed is None else seed)
        cents = self.effective_cents(unity)
        freqs = root_hz * 2.0 ** (cents / 1200.0)
        n_osc = 6
        pans = np.linspace(-1.0, 1.0, n_osc) * self.width
        buf = np.zeros((n, 2))
        total_voices = 0
        for o in range(n_osc):
            f = freqs[o]
            wave = self.waveforms[o % len(self.waveforms)]
            drive = float(self.waveshape_drive[o % 6])
            phase = rng.rand()  # random initial phase per oscillator
            dphi = f / fs
            # unison voices
            nv = 1 + self.more
            for v in range(nv):
                if v == 0:
                    fv = f
                    ph = phase
                else:
                    fv = f * 2.0 ** (rng.normal(0.0,
                                                self.unison_spread_cents)
                                      / 1200.0)
                    ph = rng.rand()
                ph_step = fv / fs
                p = ph
                # sample loop for this voice
                voice = np.empty(n)
                for i in range(n):
                    voice[i] = _osc_sample(p, wave)
                    p += ph_step
                    p -= np.floor(p)
                if drive > 0.02:
                    voice = np.tanh(drive * voice) / np.tanh(drive)
                total_voices += 1
                # pan
                pan = pans[o]
                gl = np.cos((pan + 1.0) * np.pi / 4.0)
                gr = np.sin((pan + 1.0) * np.pi / 4.0)
                buf[:, 0] += voice * gl
                buf[:, 1] += voice * gr
        buf /= np.sqrt(max(total_voices, 1))
        # filter
        buf[:, 0] = self._filter_lp(buf[:, 0])
        buf[:, 1] = self._filter_lp(buf[:, 1])
        # drone-length envelope (attack in, release out)
        env = np.ones(n)
        na = min(max(1, int(fs * self.env_attack)), n)
        nr = min(max(1, int(fs * self.env_release)), n)
        env[:na] = np.linspace(0.0, 1.0, na)
        env[-nr:] *= np.linspace(1.0, 0.0, nr)
        buf *= env[:, None]
        # reverb tail
        buf = self._schroeder_reverb(buf)
        # gain + normalize
        buf *= self.gain
        peak = np.max(np.abs(buf))
        if peak > 0:
            buf = buf / peak * 0.95
        return buf

    # ------------------------------------------------------------------
    def spectral_centroid(self, x: np.ndarray) -> float:
        """Mean spectral centroid (Hz) of the mix of both channels."""
        fs = self.sample_rate
        spec = np.abs(np.fft.rfft(x[:, 0]) ) + np.abs(np.fft.rfft(x[:, 1]))
        freqs = np.fft.rfftfreq(len(x), 1.0 / fs)
        s = float(spec.sum())
        return float((freqs * spec).sum() / s) if s > 0 else 0.0


def demo(out_dir: str = "/tmp/musicom_smoke") -> dict:
    """Self-test: Unity convergence (chaotic vs unison) + random tune
    range + WAV writes."""
    import os
    from sound.utils.io import write_wav

    os.makedirs(out_dir, exist_ok=True)
    sr = DEFAULT_SR

    d = CircleDrone(sample_rate=sr, more=2, reverb_mix=0.25)
    d.random_tune(seed=11)
    cents_full = d.effective_cents(1.0).copy()
    cents_zero = d.effective_cents(0.0).copy()

    chaotic = d.render(duration_sec=4.0, root_hz=110.0, unity=1.0, seed=5)
    unison = d.render(duration_sec=4.0, root_hz=110.0, unity=0.0, seed=5)

    c_chaos = d.spectral_centroid(chaotic)
    c_uni = d.spectral_centroid(unison)
    spread_chaos = float(np.std(cents_full))
    spread_zero = float(np.std(cents_zero))
    # root-energy dominance: correlation with root sine at 110 Hz
    t = np.arange(len(unison)) / sr
    ref = np.sin(2 * np.pi * 110.0 * t)
    root_energy_uni = float(np.abs(np.dot(unison[:, 0], ref)) / len(unison))
    root_energy_chaos = float(
        np.abs(np.dot(chaotic[:, 0], ref)) / len(chaotic))

    write_wav(os.path.join(out_dir, "circle_drone_chaotic.wav"),
              chaotic, sr)
    write_wav(os.path.join(out_dir, "circle_drone_unison.wav"),
              unison, sr)
    return {
        "detune_range_cents": DETUNE_RANGE_CENTS,
        "unity1_detune_std_cents": round(spread_chaos, 1),
        "unity0_detune_std_cents": round(spread_zero, 3),
        "centroid_chaotic_hz": round(c_chaos, 1),
        "centroid_unison_hz": round(c_uni, 1),
        "root_energy_chaotic": round(root_energy_chaos, 5),
        "root_energy_unison": round(root_energy_uni, 5),
        "chaotic_wav_bytes": os.path.getsize(
            os.path.join(out_dir, "circle_drone_chaotic.wav")),
        "unison_wav_bytes": os.path.getsize(
            os.path.join(out_dir, "circle_drone_unison.wav")),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
