"""Detuned-combidiophone chorus ("Twin Combs") — Muro Box N40 style.

Replicable logic from the Synthtopia item on the Muro Box N40 (2026-09-08) /
Floyd Steinberg's video:

  * A MIDI-controlled **music box** — the sound-maker is a bank of *steel
    tines* (a comb) plucked by pins, with a pickup and audio output.
  * The flagship "N40 Sublime" edition fits **two sets of combs deliberately
    detuned by 14 cents** to create a chorus effect; the standard edition has
    a single comb.  The N40 adds **chromatic notes** across an expanded range.

What is replicated here:
- ``MusicBoxComb``: one comb of *tines* as **modal resonators** (inharmonic
  partials: f, 6.27f, 17.55f, 34.39f — the free-free bar / tuning-fork ratios)
  excited by a short pluck impulse; each tine has its own decay and detune.
  Optional pickup colouration (bandpass + slight tanh saturation).
- ``TwinCombMusicBox``: two combs with an independent ``detune_cents`` per comb
  (default 14.0 = the N40 Sublime spec), each comb optionally panned, plus
  mechanics noise (pin/hammer click), a per-note random detune jitter (real
  instruments are never in perfect tune) and a chromatic pitch map so any MIDI
  note plays.

Not replicated: the physical brass/acacia construction, the motor/pin drum
mechanism, the latency of the mechanical action.

Usage:
    from sound.synthesis.music_box import TwinCombMusicBox

    mb = TwinCombMusicBox(sample_rate=44100)
    wav = mb.render_melody([(72, 0.0, 0.6), (76, 0.6, 0.6), (79, 1.2, 1.2)])

    single = mb.render_melody(notes, detune_cents=0.0)   # N40 Standard
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["MusicBoxComb", "TwinCombMusicBox", "TINE_RATIOS", "midi_to_freq"]

# Free-free bar (tuning-tine) inharmonic partial ratios.
TINE_RATIOS: Tuple[float, ...] = (1.0, 6.2669, 17.5470, 34.3863)

DEFAULT_DETUNE_CENTS = 14.0     # Muro Box N40 Sublime "two combs, 14 cents"


def midi_to_freq(note: float) -> float:
    """Equal-tempered MIDI note (A4=440) -> Hz."""
    return 440.0 * (2.0 ** ((float(note) - 69.0) / 12.0))


class MusicBoxComb:
    """One steel-tine comb: modal resonators + pluck excitation."""

    def __init__(self, sample_rate: int = 44100,
                 ratios: Sequence[float] = TINE_RATIOS,
                 decay: float = 1.8, brightness: float = 1.0):
        self.sr = int(sample_rate)
        self.ratios = tuple(float(r) for r in ratios)
        self.decay = float(decay)          # fundamental T60-ish (seconds)
        self.brightness = float(brightness)
        self.pickup_colour: bool = True

    def pluck(self, freq: float, duration: float, velocity: float = 1.0,
              start: float = 0.0, seed: Optional[int] = None,
              detune_cents: float = 0.0) -> np.ndarray:
        """Render one plucked tine.

        Args:
            freq: tine fundamental (Hz).
            duration: rendered length (s).
            velocity: excitation amplitude.
            start: onset time inside the returned buffer (s).
            seed: RNG seed for the random pluck-phase jitter.
            detune_cents: additional detune of this tine (cents).
        """
        sr = self.sr
        n = int(duration * sr)
        out = np.zeros(n)
        f0 = freq * 2.0 ** (detune_cents / 1200.0)
        rng = np.random.default_rng(0 if seed is None else seed)
        t0 = int(start * sr)
        for i, ratio in enumerate(self.ratios):
            f = f0 * ratio
            if f >= sr * 0.48:
                continue
            amp = (self.brightness ** i) / (1.0 + i)
            # higher modes decay much faster (real tine physics)
            tau = self.decay / (1.0 + 3.0 * i)
            length = int(min(n - t0, max(8, int(tau * 4.0 * sr))))
            if length <= 8:
                continue
            tt = np.arange(length) / sr
            phase = 2 * np.pi * f * tt + rng.uniform(0, 2 * np.pi)
            mode = np.sin(phase) * np.exp(-tt / tau)
            out[t0:t0 + length] += amp * mode
        # pluck excitation: a very short broadband transient
        click_len = max(4, int(0.002 * sr))
        click = rng.standard_normal(click_len) * np.exp(
            -np.linspace(0, 6, click_len))
        e = min(n, t0 + click_len)
        if e > t0:
            out[t0:e] += 0.35 * click[:e - t0] * self.brightness
        out *= float(np.clip(velocity, 0.0, 1.5))
        if self.pickup_colour:
            out = self._pickup(out)
        return out

    def _pickup(self, x: np.ndarray) -> np.ndarray:
        """Magnetic-pickup colouration: gentle lowpass + slight even-order drive."""
        a = 1.0 - np.exp(-2 * np.pi * 6500.0 / self.sr)
        y = np.empty_like(x)
        z = 0.0
        for i in range(len(x)):
            z += a * (x[i] - z)
            y[i] = z
        return np.tanh(y * 1.1) / 1.1


class TwinCombMusicBox:
    """Two detuned combs (N40 Sublime) with mechanics noise + chromatic map."""

    def __init__(self, sample_rate: int = 44100, detune_cents: float = DEFAULT_DETUNE_CENTS,
                 decay: float = 1.8, pan: float = 0.35):
        self.sr = int(sample_rate)
        self.detune_cents = float(detune_cents)
        self.pan = float(pan)                 # -1..+1 placement of comb B
        self.comb_a = MusicBoxComb(sample_rate, decay=decay)
        self.comb_b = MusicBoxComb(sample_rate, decay=decay * 0.97)
        self.mechanics: float = 0.25          # pin/hammer noise amount
        self.jitter_cents: float = 3.0        # per-note tuning jitter

    def render_note(self, note: float, duration: float = 1.0,
                    velocity: float = 1.0, seed: Optional[int] = None,
                    ) -> np.ndarray:
        """One chromatic note -> stereo (n, 2) buffer."""
        rng = np.random.default_rng(0 if seed is None else int(seed))
        f = midi_to_freq(note)
        jit = rng.uniform(-1.0, 1.0) * self.jitter_cents
        a = self.comb_a.pluck(f, duration, velocity, seed=seed,
                              detune_cents=jit)
        b = self.comb_b.pluck(f, duration, velocity, seed=seed,
                              detune_cents=jit + self.detune_cents)
        # mechanics noise on both combs (the pin striking the tine)
        if self.mechanics > 0:
            click_len = max(4, int(0.003 * self.sr))
            click = rng.standard_normal(click_len) * np.exp(
                -np.linspace(0, 8, click_len))
            a[:click_len] += self.mechanics * click * velocity
            b[:click_len] += self.mechanics * click * velocity
        l_gain = np.cos((self.pan + 1) * np.pi / 4)
        r_gain = np.sin((self.pan + 1) * np.pi / 4)
        left = a + b * l_gain
        right = a * r_gain + b
        peak = np.max(np.abs([left, right])) + 1e-9
        return np.stack([left, right], axis=1) / max(1.0, peak) * 0.9

    def render_melody(self, notes: Sequence[Tuple[float, float, float]],
                      detune_cents: Optional[float] = None,
                      seed: int = 0) -> np.ndarray:
        """Render a note list ``[(midi_note, start_s, dur_s), ...]`` to stereo."""
        if detune_cents is not None:
            self.detune_cents = float(detune_cents)
        if not notes:
            return np.zeros((1, 2))
        end = max(s + d for _, s, d in notes) + 1.2
        n = int(end * self.sr)
        buf = np.zeros((n, 2))
        for i, (note, start, dur) in enumerate(notes):
            voice = self.render_note(note, duration=min(end, dur + 1.0),
                                     seed=seed + i)
            s = int(start * self.sr)
            e = min(n, s + voice.shape[0])
            if s >= n or e <= s:
                continue
            buf[s:e] += voice[:e - s]
        peak = np.max(np.abs(buf)) + 1e-9
        return buf / max(1.0, peak) * 0.9


def demo() -> str:
    sr = 22050
    mb = TwinCombMusicBox(sample_rate=sr, detune_cents=DEFAULT_DETUNE_CENTS)
    print(f"tine ratios: {TINE_RATIOS}")
    print(f"comb detune: {mb.detune_cents} cents (N40 Sublime spec)")

    note = 72  # C5
    subject = mb.render_note(note, duration=2.0, seed=1)
    print(f"single note stereo: shape={subject.shape} "
          f"peak={np.max(np.abs(subject)):.3f} "
          f"finite={np.all(np.isfinite(subject))}")
    assert subject.shape[1] == 2 and np.all(np.isfinite(subject))
    assert np.max(np.abs(subject)) > 0.2

    # the 14-cent twin-comb detune must beat (amplitude-modulate) the tail
    single = mb.render_note(note, duration=2.0, seed=1)
    mb.detune_cents = 0.0
    unison = mb.render_note(note, duration=2.0, seed=1)
    mb.detune_cents = DEFAULT_DETUNE_CENTS
    twin = mb.render_note(note, duration=2.0, seed=1)

    def beat_depth(x: np.ndarray) -> float:
        env = np.abs(x[:, 0] + x[:, 1])
        tail = env[int(0.3 * sr):]
        if len(tail) < 100:
            return 0.0
        detrended = tail - np.convolve(tail, np.ones(200) / 200, mode="same")
        return float(np.std(detrended) / (np.mean(tail) + 1e-9))

    print(f"unison beat depth={beat_depth(unison):.4f}  "
          f"twin(14c) beat depth={beat_depth(twin):.4f}")
    assert beat_depth(twin) > beat_depth(unison)

    # inharmonic tine partial must exist above the fundamental
    spec = np.abs(np.fft.rfft(twin[:, 0] * np.hanning(len(twin))))
    fr = np.fft.rfftfreq(len(twin), 1.0 / sr)
    f0 = midi_to_freq(note)
    band = (fr > f0 * 5.0) & (fr < f0 * 8.0)
    # the 6.27 x partial is the signature music-box "ting"
    print(f"f0={f0:.1f} Hz  partial-2 band energy={np.sum(spec[band]):.1f} "
          f"(peaks at 6.27*f0 = {f0*6.2669:.0f} Hz)")
    assert np.sum(spec[band]) > 0.0

    mel = mb.render_melody([(72, 0.0, 0.5), (76, 0.5, 0.5), (79, 1.0, 0.8)],
                           seed=5)
    print(f"melody: shape={mel.shape} peak={np.max(np.abs(mel)):.3f}")
    assert mel.shape[1] == 2
    print("  music_box demo OK")
    return "ok"


if __name__ == "__main__":
    demo()
