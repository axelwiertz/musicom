"""Four-operator FM groovebox with a four-track step sequencer.

Models the "Digitone / OP-Z / Volca FM" class of box: a compact 4-op FM voice
(no arbitrary operator matrix -- a fixed set of 8 *algorithms*) under a 4-track
step sequencer, where every step can carry its own note, velocity, length and
**parameter locks** on FM-specific parameters (operator ratios, index, feedback,
algorithm).  Ratchets sub-divide a step; probability makes a step conditional;
"tie" merges a step into the next (the 303 slide equivalent).

Signal model per voice (classic 4-op):

    car1 = sin(phase_a + index_b * sin(phase_b + ...))

Algorithms are given as a modulation list: ``(source, target, depth_key)``
where target 0 is the carrier output.  Operators 1 and 2 are carriers in the
classic "1->2->3->4" algorithm, so the algorithm table is data, not code.

The sequencer emits absolute-tick events ``(track, start_tick, dur_tick, midi,
velocity)`` -- no floating bar positions -- so the results drop straight into
the Musicom absolute-tick model.
"""

from __future__ import annotations

import numpy as np

__all__ = ["FMPatch", "FMVoice", "FMGroovebox", "demo"]

# Algorithm table: (operator modulators).  op 4 is the top modulator.
# Each entry: list of (modulator_op, carrier_op, index_scale)
ALGORITHMS = {
    1: [(4, 3, 1.0), (3, 2, 1.0), (2, 1, 1.0)],          # 4>3>2>1 serial
    2: [(4, 3, 1.0), (3, 1, 1.0), (2, 1, 0.7)],          # two mods into carrier
    3: [(4, 3, 1.0), (3, 2, 0.8), (2, 1, 0.5), (4, 1, 0.3)],
    4: [(4, 2, 1.0), (3, 2, 1.0), (2, 1, 1.0)],          # stack into op2
    5: [(4, 3, 1.0), (3, 1, 0.6), (2, 4, 0.4)],          # feedback-ish branch
    6: [(3, 2, 1.0), (4, 1, 0.9), (2, 1, 0.6)],          # parallel pairs
    7: [(4, 1, 1.0), (3, 2, 1.0)],                       # two independent pairs
    8: [(2, 1, 1.0), (4, 3, 0.0)],                        # additive-ish
}


class FMPatch:
    """One 4-operator voice configuration."""

    def __init__(self, algorithm: int = 1, ratios=(1.0, 2.0, 3.0, 1.0),
                 levels=(1.0, 0.8, 0.5, 0.4), index: float = 3.0,
                 feedback: float = 0.0, attack: float = 0.004,
                 decay: float = 0.25, sustain: float = 0.35,
                 release: float = 0.2, bright: float = 1.0):
        self.algorithm = algorithm
        self.ratios = list(ratios)
        self.levels = list(levels)
        self.index = index          # global FM depth multiplier
        self.feedback = feedback    # op1 self-feedback (0..1)
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.bright = bright        # key-scaling of index (velocity-ish)

    def copy(self) -> "FMPatch":
        return FMPatch(self.algorithm, tuple(self.ratios), tuple(self.levels),
                       self.index, self.feedback, self.attack, self.decay,
                       self.sustain, self.release, self.bright)

    def with_lock(self, **locks) -> "FMPatch":
        """Return a copy with per-step parameter locks applied.

        Recognised locks: algorithm, index, feedback, ratio0..ratio3,
        level0..level3, decay.
        """
        p = self.copy()
        for k, v in locks.items():
            if k in ("algorithm", "feedback", "index", "decay"):
                setattr(p, k, float(v) if k != "algorithm" else int(v))
            elif k.startswith("ratio") and k[-1].isdigit():
                p.ratios[int(k[-1])] = float(v)
            elif k.startswith("level") and k[-1].isdigit():
                p.levels[int(k[-1])] = float(v)
        return p


class FMVoice:
    """Render one note of a patch.  Simple 4-op phase-modulation core."""

    def __init__(self, sample_rate: int = 44100):
        self.sr = sample_rate

    def _env(self, n: int, gate: int, p: FMPatch) -> np.ndarray:
        t = np.arange(n) / self.sr
        a = max(1e-4, p.attack)
        d = max(1e-4, p.decay)
        env = np.where(t < a, t / a, p.sustain + (1.0 - p.sustain) *
                       np.exp(-(t - a) / d))
        if gate < n:
            rel = np.exp(-(np.arange(n - gate) / self.sr) / max(1e-4, p.release))
            env[gate:] *= rel
        return env

    def render(self, midi: float, dur_s: float, p: FMPatch,
               velocity: float = 0.8) -> np.ndarray:
        f0 = 440.0 * 2.0 ** ((midi - 69.0) / 12.0)
        n = max(16, int(dur_s * self.sr))
        gate = n
        n = gate + int(0.08 * self.sr)          # release tail
        t = np.arange(n) / self.sr

        phases = [2.0 * np.pi * f0 * r * t for r in p.ratios]
        idx = p.index * (0.4 + 0.6 * velocity) * p.bright
        ops = [None] * 4
        # evaluate in order 4 -> 1 so modulators exist first
        for op in (4, 3, 2, 1):
            ops[op - 1] = np.sin(phases[op - 1])
        out = np.zeros(n)
        for _ in range(2):                       # two passes converge the chain
            for mod, car, scale in ALGORITHMS.get(p.algorithm, ALGORITHMS[1]):
                ops[car - 1] = np.sin(phases[car - 1] +
                                      idx * scale * p.levels[mod - 1] *
                                      ops[mod - 1])
        # op1 self-feedback (Yamaha-style: previous sample in the phase)
        if p.feedback > 0:
            fb = np.zeros(n)
            for i in range(1, n):
                fb[i] = np.sin(phases[0][i] + p.feedback * 3.0 * fb[i - 1])
            ops[0] = fb
        for op in range(4):
            out += p.levels[op] * ops[op]
        out *= self._env(n, gate, p)
        out *= 0.22 / max(1.0, np.max(np.abs(out)) + 1e-9)
        return out


class Step:
    __slots__ = ("on", "midi", "vel", "len", "ratchet", "prob", "tie", "locks")

    def __init__(self, on=False, midi=60, vel=100, length=0.9,
                 ratchet=1, prob=1.0, tie=False, locks=None):
        self.on = on
        self.midi = midi
        self.vel = vel
        self.len = length
        self.ratchet = ratchet
        self.prob = prob
        self.tie = tie
        self.locks = locks or {}


class FMTrack:
    def __init__(self, name: str, patch: FMPatch, steps: int = 16,
                 division: float = 4.0, swing: float = 0.0):
        self.name = name
        self.patch = patch
        self.steps = [Step() for _ in range(steps)]
        self.division = division      # steps per beat (4 = 16ths)
        self.swing = swing

    def set(self, i: int, **kw):
        s = self.steps[i % len(self.steps)]
        for k, v in kw.items():
            setattr(s, "len" if k == "length" else k, v)
        s.on = True
        return self


class FMGroovebox:
    """4-track / N-step FM sequencer producing absolute-tick events."""

    def __init__(self, bpm: float = 120.0, ticks_per_beat: int = 480,
                 sample_rate: int = 44100):
        self.bpm = bpm
        self.tpb = ticks_per_beat
        self.sr = sample_rate
        self.tracks: dict[str, FMTrack] = {}

    def add_track(self, name: str, patch: FMPatch | None = None, **kw) -> FMTrack:
        tr = FMTrack(name, patch or FMPatch(), **kw)
        self.tracks[name] = tr
        return tr

    # ------------------------------------------------------------------
    def generate(self, bars: int = 1, seed: int = 0) -> list[tuple]:
        """Return events ``(track, start_tick, dur_tick, midi, velocity)``.

        Ratchets split a step into k evenly spaced sub-hits; probability is
        resolved against a seeded RNG so runs are reproducible; a ``tie``
        extends the previous event instead of retriggering.
        """
        rng = np.random.default_rng(seed)
        events: list[tuple] = []
        for tr in self.tracks.values():
            step_ticks = self.tpb / tr.division      # division = steps per beat
            total = int(round(bars * 4 * tr.division))
            prev_idx = None
            for i in range(total):
                s = tr.steps[i % len(tr.steps)]
                if not s.on:
                    prev_idx = None
                    continue
                if s.prob < 1.0 and rng.random() > s.prob:
                    prev_idx = None
                    continue
                pos = i * step_ticks
                if tr.swing and i % 2:
                    pos += tr.swing * step_ticks * 0.5
                if s.tie and prev_idx is not None:
                    k = min(prev_idx, len(events) - 1)
                    if k >= 0:
                        tn, st, du, mi, ve = events[k]
                        events[k] = (tn, st, du + int(step_ticks), mi, ve)
                    continue
                sub = s.ratchet if s.ratchet > 0 else 1
                for r in range(sub):
                    st = int(round(pos + r * step_ticks / sub))
                    du = int(round(step_ticks / sub * s.len))
                    events.append((tr.name, st, max(1, du), s.midi,
                                   int(s.vel * (1.0 - 0.08 * r))))
                prev_idx = len(events) - 1
        events.sort(key=lambda e: (e[1], e[0]))
        return events

    def render(self, events: list[tuple], tail_s: float = 0.5) -> np.ndarray:
        """Mix events to audio using each track's patch (+ its step locks)."""
        voice = FMVoice(self.sr)
        sec_per_tick = 60.0 / (self.bpm * self.tpb)
        length = int((max(e[1] + e[2] for e in events) * sec_per_tick + tail_s)
                     * self.sr)
        buf = np.zeros(length)
        for track, st, du, midi, vel in events:
            tr = self.tracks[track]
            patch = tr.patch
            # find the step that generated this onset to honour its locks
            step_ticks = self.tpb / tr.division
            idx = int(round(st / step_ticks)) % len(tr.steps)
            lock = tr.steps[idx].locks
            if lock:
                patch = patch.with_lock(**lock)
            sig = voice.render(midi, du * sec_per_tick, patch, vel / 127.0)
            o = int(st * sec_per_tick * self.sr)
            end = min(length, o + sig.size)
            buf[o:end] += sig[:end - o]
        peak = np.max(np.abs(buf)) or 1.0
        if peak > 0.99:
            buf *= 0.99 / peak
        return buf


def demo() -> None:
    gb = FMGroovebox(bpm=124)
    bass = gb.add_track("bass", FMPatch(algorithm=1, ratios=(1, 2, 1, 3),
                                        levels=(1, .9, .2, .6), index=4.2,
                                        decay=0.18, sustain=0.2))
    bell = gb.add_track("bell", FMPatch(algorithm=5, ratios=(1, 3.5, 7, 1),
                                        levels=(.8, .5, .4, 1), index=2.1,
                                        decay=0.9, sustain=0.0, release=0.5))
    # acid-ish 16th bass line with ratchets + parameter lock
    for i, m in enumerate([36, 36, 43, 36, 39, 36, 41, 43]):
        bass.set(i * 2, midi=m, vel=110 if i % 2 == 0 else 78,
                 ratchet=2 if i == 6 else 1, length=0.8)
    bass.set(6, locks={"index": 7.5})
    for i, m in enumerate([72, 79, 84, 79]):
        bell.set(i * 4 + 2, midi=m, vel=90, prob=0.85, length=1.4)
    ev = gb.generate(bars=2, seed=7)
    print(f"{len(ev)} events, last tick {max(e[1] + e[2] for e in ev)}")
    for e in ev[:6]:
        print("  ", e)
    audio = gb.render(ev)
    print(f"audio {audio.size / gb.sr:.2f}s, rms "
          f"{np.sqrt(np.mean(audio ** 2)):.4f}")
    assert audio.size > 1000 and np.max(np.abs(audio)) > 0.01


if __name__ == "__main__":
    demo()
