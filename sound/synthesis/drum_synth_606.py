"""606-style drum synthesis engine — AudioKit Pro Super 606-style.

Replicable logic from AudioKit Pro's Super 606 (Synthtopia 2026-08-25):
a drum machine that synthesizes its sounds (no samples) with a dedicated
drum synthesis engine — XL kick, snare, analog toms, clap, and metallic
hi-hats — plus 606-style sequencing features (flams, ratchets, ghost
notes, per-track last-step, polyrhythms, swing).

What is replicated here (all synthesis — the sounds themselves):
- Kick (XL): pitch-swept sine + click transient; XL mode adds a longer
  pitch sweep and body boost (the "XL kick" trick).
- Snare: tonal triangle/sine body + wideband noise burst through a
  bandpass, with independent body/noise decay (the classic two-oscillator
  drum recipe).
- Toms: pitch-swept sine with tuned resonant peak and fast decay.
- Clap: 3-5 closely-spaced noise bursts (multi-burst) + lowpass, the
  classic clap synthesis.
- Metallic hi-hats: square/triangle oscillator XOR-ed with noise through
  a highpass — the metallic "XOR noise" trick behind cymbal synthesis.
- Flam: two hits offset by a small delay (9 configurable types collapsed
  to offset + velocity scaling).

Not replicated: the AUv3 app, Ableton Link sync, MIDI import, WAV/stem
export, the Magic Pattern Generator / Smart Fills (UI + heuristics).

Usage:
    from sound.synthesis.drum_synth_606 import DrumSynth606

    ds = DrumSynth606(sample_rate=44100)
    kick = ds.kick(decay=0.4, xl=True)
    snare = ds.snare(body_decay=0.12, noise_decay=0.25)
    hat = ds.hat(closed=True, metallic=0.8)
    beat = ds.render_sequence(steps=[...], bpm=120)
"""

from typing import List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["DrumSynth606", "FLAM_TYPES", "DEFAULT_STEPS"]


FLAM_TYPES: Tuple[str, ...] = (
    "none", "tight", "medium", "wide", "ahead", "double",
    "triple", "flam_roll", "rushed", "dragged",
)


class DrumSynth606:
    """Synthesized 606-style drum voices (no samples)."""

    def __init__(self, sample_rate: int = 44100):
        self.sr = int(sample_rate)

    # ------------------------------------------------------------------ #
    # voices
    # ------------------------------------------------------------------ #
    def kick(self, decay: float = 0.35, xl: bool = False,
             pitch_start: float = 150.0, click: float = 0.3) -> np.ndarray:
        """Bass drum: pitch-swept sine + click transient.

        Args:
            decay: Body decay in seconds.
            xl: XL mode — longer sweep + extra low body.
            pitch_start: Initial pitch of the downward sweep (Hz).
            click: Amount of transient click (0..1).
        """
        n = int(self.sr * decay * (1.25 if xl else 1.0))
        t = np.arange(n) / self.sr
        if xl:
            sweep = pitch_start * np.exp(-t * 14.0) + 40.0
            body = np.sin(2 * np.pi * np.cumsum(sweep) / self.sr)
            body += 0.6 * np.sin(2 * np.pi * 60.0 * t) * np.exp(-t * 6.0)
            env = np.exp(-t * 7.0)
        else:
            sweep = pitch_start * np.exp(-t * 22.0) + 45.0
            body = np.sin(2 * np.pi * np.cumsum(sweep) / self.sr)
            env = np.exp(-t * 9.0)
        out = body * env
        if click > 0:
            click_len = int(self.sr * 0.004)
            c = np.zeros(n)
            c[:click_len] = np.linspace(1.0, 0.0, click_len) * click
            out += c
        return _normalize(out)

    def snare(self, body_decay: float = 0.10, noise_decay: float = 0.22,
              tone_freq: float = 180.0, snap: float = 0.7) -> np.ndarray:
        """Snare: tonal body + bandpassed noise burst with separate decays.

        Args:
            body_decay: Tonal (drumhead) decay in seconds.
            noise_decay: Noise (rattle) decay in seconds.
            tone_freq: Tonal body frequency (Hz).
            snap: Noise level (0..1).
        """
        n = int(self.sr * max(body_decay, noise_decay) * 1.2)
        t = np.arange(n) / self.sr
        body = np.sin(2 * np.pi * tone_freq * t) * np.exp(-t / body_decay)
        rng = np.random.default_rng(0)
        noise = rng.standard_normal(n) * np.exp(-t / noise_decay)
        noise = _bandpass(noise, 1200.0, 7000.0, self.sr)
        out = body + snap * 0.9 * noise
        return _normalize(out)

    def tom(self, freq: float = 180.0, decay: float = 0.3,
            pitch_sweep: float = 1.6) -> np.ndarray:
        """Analog tom: pitch-swept sine with resonant character."""
        n = int(self.sr * decay * 1.3)
        t = np.arange(n) / self.sr
        sweep = freq * (1.0 + (pitch_sweep - 1.0) * np.exp(-t * 30.0))
        body = np.sin(2 * np.pi * np.cumsum(sweep) / self.sr)
        # second harmonic adds "tuning" presence
        body += 0.35 * np.sin(2 * np.pi * np.cumsum(sweep * 2.0) / self.sr)
        env = np.exp(-t / decay)
        return _normalize(body * env)

    def clap(self, decay: float = 0.25, bursts: int = 4,
             burst_gap: float = 0.011) -> np.ndarray:
        """Clap: multi-burst filtered noise (3-5 closely spaced bursts)."""
        n = int(self.sr * decay)
        rng = np.random.default_rng(1)
        noise = rng.standard_normal(n)
        # build burst envelope: repeated decaying pulses
        env = np.zeros(n)
        t = np.arange(n) / self.sr
        for i in range(bursts):
            start = int((0.01 + i * burst_gap) * self.sr)
            if start < n:
                env[start:] += np.exp(-(t[start:] - t[start]) / 0.02)
        noise *= env
        noise = _lowpass(noise, 3500.0, self.sr)
        return _normalize(noise)

    def hat(self, closed: bool = True, metallic: float = 0.7,
            decay: Optional[float] = None) -> np.ndarray:
        """Metallic hi-hat: XOR'd square + noise through a highpass.

        The metallic character comes from multiplying a square wave with
        noise (the "XOR" trick), which creates dense inharmonic sidebands
        like real cymbal metal.
        """
        if decay is None:
            decay = 0.05 if closed else 0.35
        n = int(self.sr * decay * 1.3)
        t = np.arange(n) / self.sr
        rng = np.random.default_rng(2)
        noise = rng.standard_normal(n)
        sq = np.sign(np.sin(2 * np.pi * 3000.0 * t))
        metal = sq * noise
        mixed = metallic * metal + (1.0 - metallic) * noise
        mixed = _highpass(mixed, 6500.0, self.sr)
        env = np.exp(-t / decay)
        return _normalize(mixed * env)

    # ------------------------------------------------------------------ #
    # 606-style sequencing helpers
    # ------------------------------------------------------------------ #
    def flam(self, voice: np.ndarray, kind: str = "medium",
             offset_ms: Optional[float] = None,
             second_vel: float = 0.8) -> np.ndarray:
        """Add a flam (two hits, second slightly offset) to a voice.

        Args:
            voice: Single-hit sample (the main hit).
            kind: One of FLAM_TYPES (offset presets; "ahead" plays the
                  grace note before the beat).
            offset_ms: Manual offset in ms (overrides preset).
            second_vel: Velocity scaling of the grace hit.
        """
        if kind == "none":
            return voice
        if kind not in FLAM_TYPES:
            raise ValueError(f"unknown flam type {kind!r}")
        if offset_ms is None:
            offsets = {"tight": 8.0, "medium": 18.0, "wide": 35.0,
                       "ahead": -18.0, "double": 12.0, "triple": 9.0,
                       "flam_roll": 22.0, "rushed": 6.0, "dragged": 45.0}
            offset_ms = offsets[kind]
        shift = int(offset_ms * self.sr / 1000.0)
        n = len(voice) + abs(shift)
        out = np.zeros(n)
        if shift >= 0:
            out[:len(voice)] += voice
            out[shift:shift + len(voice)] += second_vel * voice
        else:  # ahead of the beat: grace note first
            out[:len(voice)] += second_vel * voice
            out[-shift:-shift + len(voice)] += voice
        return _normalize(out)

    def render_sequence(self, steps: Sequence[int], bpm: float = 120.0,
                        swing: float = 0.0,
                        voices: Optional[List[np.ndarray]] = None
                        ) -> np.ndarray:
        """Place single hits on a 16-step grid.

        Args:
            steps: 16 entries; 0 = rest, else velocity (1..127).
            bpm: Tempo (16th-note steps).
            swing: 0..1 shift applied to odd steps.
            voices: Pre-rendered hit per step index (default: kick for
                    all non-zero steps).
        """
        if len(steps) != 16:
            raise ValueError("steps must have length 16")
        step_s = 60.0 / bpm / 4.0
        total = int(self.sr * step_s * 16 * 1.1)
        out = np.zeros(total)
        for i, vel in enumerate(steps):
            if vel <= 0:
                continue
            hit = (voices[i] if voices is not None else
                   self.kick(decay=0.3))
            start = int(self.sr * step_s * (i + (swing * 0.5 if i % 2 else 0)))
            end = min(start + len(hit), total)
            out[start:end] += (vel / 127.0) * hit[:end - start]
        return _normalize(out)


def _normalize(x: np.ndarray) -> np.ndarray:
    peak = np.max(np.abs(x)) or 1.0
    return x / peak


def _lowpass(x: np.ndarray, cutoff: float, sr: int) -> np.ndarray:
    """Simple one-pole lowpass."""
    a = np.exp(-2.0 * np.pi * cutoff / sr)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1.0 - a) * x[i] + a * acc
        y[i] = acc
    return y


def _highpass(x: np.ndarray, cutoff: float, sr: int) -> np.ndarray:
    """First-order highpass (complement of one-pole lowpass)."""
    a = np.exp(-2.0 * np.pi * cutoff / sr)
    y = np.empty_like(x)
    prev_x, prev_y = 0.0, 0.0
    for i in range(len(x)):
        y[i] = a * prev_y + a * (x[i] - prev_x)
        prev_x, prev_y = x[i], y[i]
    return y


def _bandpass(x: np.ndarray, lo: float, hi: float, sr: int) -> np.ndarray:
    """Crude bandpass = lowpass then highpass (cascade)."""
    return _highpass(_lowpass(x, hi, sr), lo, sr)


def demo() -> None:
    """Render each voice and a short 606-style beat; report stats."""
    ds = DrumSynth606(sample_rate=22050)
    kick = ds.kick(decay=0.35, xl=True)
    snare = ds.snare()
    hat = ds.hat(closed=True)
    hat_o = ds.hat(closed=False)
    tom_l = ds.tom(freq=140.0)
    tom_h = ds.tom(freq=240.0)
    clap = ds.clap()
    print(f"kick  len={len(kick)} peak={np.max(np.abs(kick)):.3f}")
    print(f"snare len={len(snare)} peak={np.max(np.abs(snare)):.3f}")
    print(f"hat   len={len(hat)}   peak={np.max(np.abs(hat)):.3f}")
    print(f"hat-o len={len(hat_o)} peak={np.max(np.abs(hat_o)):.3f}")
    print(f"tom   len={len(tom_l)} peak={np.max(np.abs(tom_l)):.3f}")
    print(f"clap  len={len(clap)} peak={np.max(np.abs(clap)):.3f}")
    fl = ds.flam(snare, kind="medium")
    print(f"flam  len={len(fl)} (snare {len(snare)} + offset)")
    # 606-style beat: kick 0,4,8,12; snare 4,12; hats every odd step
    steps = [120, 0, 0, 0, 90, 0, 0, 0,
             110, 0, 0, 0, 95, 0, 0, 0]
    voices = [kick, None, None, None, snare, None, None, None,
              kick, None, None, None, snare, None, None, None]
    beat = ds.render_sequence(steps, bpm=124.0, swing=0.15, voices=voices)
    print(f"beat  len={len(beat)} dur={len(beat) / 22050:.2f}s "
          f"peak={np.max(np.abs(beat)):.3f}")


if __name__ == "__main__":
    demo()
