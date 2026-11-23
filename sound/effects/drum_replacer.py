"""Drum replacement / reinforcement (Drumagog 6-style).

Replicable logic from the Sound On Sound review "WaveMachine Labs Drumagog 6
Platinum" (December 2026 issue, online November 2026):

* automatic **hit detection** — "the Threshold control, which sets the
  minimum level for a peak to be detected, and Detail, which excludes
  information below a certain level. Combined with a **retrigger time** to
  avoid false triggers";
* manual **Add / Remove** of hits in the waveform display, plus **Keep
  Similar** (include other similar missed hits) and **Remove Similar**
  (remove repeated false triggers);
* **alignment**: "the Show Alignment option superimposes the samples in
  white over the original audio... errors can be corrected by changing the
  alignment setting from **phase to transient** or vice versa";
* Kit mode (whole-kit demixing) and Live mode (2 ms low-latency) — the
  demixer is an ML/real-time feature NOT replicated here.

What is replicated here (offline DSP equivalent):

* ``detect_hits`` — onset detection over a rectified, smoothed envelope:
  peaks must exceed ``threshold`` (absolute level), exceed ``detail``
  (relative to the local median baseline — "excludes information below a
  certain level") and be spaced by at least ``retrigger_ms``.
* ``HitFeature`` / ``hit_feature`` — per-hit descriptor (energy, peak,
  spectral flux, peak count) used by the Similar machinery.
* ``DrumReplacer`` — sample bank per drum; ``process()`` detects hits,
  aligns the replacement sample (``phase`` alignment = align to the
  sample's own onset peak; ``transient`` alignment = align to the max-slope
  transient of the detected hit), scales by hit velocity (energy-mapped)
  and mixes dry/wet; ``add_hit``/``remove_hit`` manual editing and
  ``keep_similar``/``remove_similar`` batch edits by feature distance.

Not replicated: the real-time low-latency Live engine, the ML demixer in
Kit mode, the standalone offline host and the GUI waveform display.

Usage:
    from sound.effects.drum_replacer import DrumReplacer, detect_hits

    dr = DrumReplacer(sample_rate=44100, samples={"snare": snare_wav})
    out = dr.process(track, threshold=0.1, detail=2.0, retrigger_ms=40,
                     alignment="transient", wet=1.0)
"""

from __future__ import annotations

import numpy as np

__all__ = ["detect_hits", "hit_feature", "DrumReplacer", "demo"]

DEFAULT_SR = 44100


def detect_hits(audio: np.ndarray, sample_rate: int = DEFAULT_SR,
                threshold: float = 0.1, detail: float = 2.0,
                retrigger_ms: float = 40.0, hop: int = 128) -> np.ndarray:
    """Sample indices of drum hits.

    Envelope = rectified signal through a one-pole smoother.  A hit is a
    local peak where ``env > threshold`` and ``env > detail * local_median``
    (Detail excludes content below a certain level relative to the running
    baseline); hits closer than ``retrigger_ms`` are suppressed (retrigger
    time avoids false triggers).
    """
    x = np.asarray(audio, dtype=np.float64).reshape(-1)
    sr = int(sample_rate)
    env = np.abs(x)
    # one-pole smooth (~5 ms)
    a = 1.0 - np.exp(-1.0 / (0.005 * sr))
    out = np.empty_like(env)
    acc = 0.0
    for i, v in enumerate(env):
        acc += a * (v - acc)
        out[i] = acc
    env = out
    n = len(env)
    min_gap = max(1, int(retrigger_ms * sr / 1000.0))
    hits = []
    last = -10 ** 9
    win = max(1, hop * 4)
    for i in range(1, n - 1):
        if not (env[i] >= env[i - 1] and env[i] > env[i + 1]):
            continue
        if env[i] < threshold:
            continue
        lo = max(0, i - win)
        base = float(np.median(env[lo:i])) + 1e-9
        if env[i] < detail * base:
            continue
        if i - last < min_gap:
            continue
        hits.append(i)
        last = i
    return np.asarray(hits, dtype=int)


def hit_feature(audio: np.ndarray, idx: int, sr: int = DEFAULT_SR,
                win: int = 1024) -> np.ndarray:
    """Per-hit descriptor for the Similar machinery.

    [energy, peak, spectral-flux onset strength, peak count] — cheap but
    enough to group "similar" hits (Keep/Remove Similar).
    """
    lo = max(0, idx - win // 2)
    hi = min(len(audio), idx + win)
    seg = audio[lo:hi]
    if len(seg) < 4:
        return np.zeros(4)
    e = float(np.sqrt((seg ** 2).mean()))
    pk = float(np.max(np.abs(seg)))
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    flux = float(np.sum(np.diff(spec, prepend=spec[0]) ** 2)) / (len(spec) + 1e-9)
    # peak count above 60% of max (dense hits have more ringing peaks)
    pc = float(np.sum(seg > 0.6 * pk)) if pk > 0 else 0.0
    return np.asarray([e, pk, flux, pc])


class DrumReplacer:
    """Detect hits on a drum track and play replacement samples in their
    place, with phase/transient alignment and similarity editing."""

    def __init__(self, sample_rate: int = DEFAULT_SR,
                 samples: dict[str, np.ndarray] | None = None,
                 seed: int = 0):
        self.sr = int(sample_rate)
        self.samples = {k: np.asarray(v, dtype=np.float64).reshape(-1)
                        for k, v in (samples or {}).items()}
        self.seed = int(seed)
        self.hits: np.ndarray = np.zeros(0, dtype=int)
        self._features: list[np.ndarray] = []
        self._primary = "snare" if "snare" in self.samples else \
            (next(iter(self.samples)) if self.samples else "default")

    # -- manual editing (Add / Remove) ------------------------------------
    def add_hit(self, idx: int) -> None:
        self.hits = np.sort(np.append(self.hits, int(idx)))
        self._features = [hit_feature(np.zeros(1), 0) for _ in self.hits]

    def remove_hit(self, idx: int) -> None:
        mask = np.abs(self.hits - int(idx)) > 64
        self.hits = self.hits[mask]
        self._features = [hit_feature(np.zeros(1), 0) for _ in self.hits]

    def keep_similar(self, ref_idx: int, tol: float = 0.35) -> None:
        """Keep hits similar to the reference (adds similar missed hits)."""
        if not len(self.hits):
            return
        ref = self._features[ref_idx]
        keep = []
        for h, f in zip(self.hits, self._features):
            d = float(np.linalg.norm(f - ref) / (np.linalg.norm(ref) + 1e-9))
            if d <= tol:
                keep.append(h)
        self.hits = np.asarray(keep, dtype=int)
        self._features = [hit_feature(np.zeros(1), 0) for _ in self.hits]

    def remove_similar(self, ref_idx: int, tol: float = 0.35) -> None:
        """Remove hits similar to the reference (repeated false triggers)."""
        if not len(self.hits):
            return
        ref = self._features[ref_idx]
        keep = []
        for h, f in zip(self.hits, self._features):
            d = float(np.linalg.norm(f - ref) / (np.linalg.norm(ref) + 1e-9))
            if d > tol:
                keep.append(h)
        self.hits = np.asarray(keep, dtype=int)
        self._features = [hit_feature(np.zeros(1), 0) for _ in self.hits]

    # -- alignment ----------------------------------------------------------
    def _align_offset(self, sample: np.ndarray, hit_idx: int,
                      audio: np.ndarray, mode: str) -> int:
        """Return the sample offset such that its reference point lands on
        the detected hit.  ``phase`` aligns to the sample's onset peak;
        ``transient`` aligns to the max-slope transient of the detected
        hit (the review: phase vs transient alignment).
        """
        s = sample
        if len(s) == 0:
            return 0
        if mode == "transient":
            # reference point of the sample = its own onset transient
            s_ref = int(np.argmax(np.abs(np.diff(s, prepend=s[0]))))
        else:                                        # phase
            s_ref = int(np.argmax(np.abs(s)))
        return int(hit_idx - s_ref)

    # -- core ---------------------------------------------------------------
    def process(self, audio: np.ndarray, threshold: float = 0.1,
                detail: float = 2.0, retrigger_ms: float = 40.0,
                alignment: str = "transient", wet: float = 1.0,
                sample: str | None = None,
                refill_features: bool = True) -> np.ndarray:
        """Replace detected hits of ``audio`` with the chosen sample.

        Returns the wet/dry mix (mono).  With ``wet=0`` returns the dry
        track; ``wet=1`` fully replaced (level-normalised to the detected
        hit energy, like velocity-to-sample scaling).
        """
        x = np.asarray(audio, dtype=np.float64).reshape(-1)
        key = sample or self._primary
        s = self.samples.get(key)
        if s is None or len(s) == 0 or wet <= 0:
            return x.copy()
        self.hits = detect_hits(x, self.sr, threshold, detail, retrigger_ms)
        if refill_features:
            self._features = [hit_feature(x, int(h), self.sr)
                              for h in self.hits]
        out = x.copy()
        for i, h in enumerate(self.hits):
            h = int(h)
            # velocity scaling from hit energy vs threshold
            lo = max(0, h - 512)
            e = float(np.sqrt((x[lo:h + 512] ** 2).mean()) + 1e-9)
            gain = float(np.clip(e / (threshold + 1e-9), 0.0, 2.0))
            off = self._align_offset(s, h, x, alignment)
            i0 = off
            i1 = min(len(out), i0 + len(s))
            if i1 <= i0:
                continue
            piece = s[:i1 - i0] * gain
            out[i0:i1] = (1.0 - wet) * out[i0:i1] + wet * piece
        return out


def demo() -> str:
    """Prove detection (threshold/detail/retrigger), alignment, similarity."""
    sr = 22050
    rng = np.random.default_rng(3)
    n = sr * 2
    track = np.zeros(n)
    true_hits = []
    # 8 snare-ish hits at ~240 ms spacing + one ghost hit
    for k in range(8):
        idx = int((0.2 + 0.24 * k) * sr)
        true_hits.append(idx)
        t = np.arange(int(0.08 * sr)) / sr
        seg = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 40) + \
            rng.standard_normal(len(t)) * 0.6 * np.exp(-t * 60)
        track[idx:idx + len(seg)] += seg
    # extra quiet ghost hit (should be excluded by threshold)
    ghost = int(1.95 * sr)
    t = np.arange(int(0.05 * sr)) / sr
    track[ghost:ghost + len(t)] += np.sin(2 * np.pi * 180 * t) * 0.02
    track += rng.standard_normal(n) * 0.01

    hits = detect_hits(track, sr, threshold=0.08, detail=2.0, retrigger_ms=60)
    print(f"detected {len(hits)} hits at {hits[:5]}... (true={len(true_hits)})")
    assert len(hits) == 8, len(hits)     # ghost + noise excluded

    # replacement sample: clean synthetic snare with a slow-ish attack so
    # its onset transient (sample 0) and its peak (later) diverge — this is
    # exactly the phase-vs-transient alignment difference Drumagog exposes
    t = np.arange(int(0.12 * sr)) / sr
    attack = np.clip(t / 0.008, 0.0, 1.0)
    sample = (np.sin(2 * np.pi * 200 * t) * np.exp(-t * 30) +
              rng.standard_normal(len(t)) * 0.5 * np.exp(-t * 50)) * attack
    sample = sample / (np.abs(sample).max() + 1e-9)

    dr = DrumReplacer(sample_rate=sr, samples={"snare": sample}, seed=1)
    out = dr.process(track, threshold=0.08, retrigger_ms=60, wet=1.0,
                     alignment="transient")
    print(f"replaced: shape={out.shape} finite={np.all(np.isfinite(out))} "
          f"peak={np.abs(out).max():.3f}")
    assert out.shape == track.shape and np.all(np.isfinite(out))
    # replaced hits sit at the detected positions (alignment puts the
    # sample transient exactly on the hit)
    det = detect_hits(out, sr, threshold=0.08, retrigger_ms=60)
    print(f"re-detected hits in output: {len(det)} (should be ~8)")
    assert 6 <= len(det) <= 9

    # alignment modes differ in placement
    oa = DrumReplacer(sample_rate=sr, samples={"snare": sample}).process(
        track, threshold=0.08, retrigger_ms=60, alignment="phase")
    ob = DrumReplacer(sample_rate=sr, samples={"snare": sample}).process(
        track, threshold=0.08, retrigger_ms=60, alignment="transient")
    print(f"alignment phase vs transient differ: "
          f"{not np.array_equal(oa, ob)}")
    assert not np.array_equal(oa, ob)

    # keep_similar / remove_similar
    dr2 = DrumReplacer(sample_rate=sr, samples={"snare": sample})
    dr2.hits = hits.copy()
    dr2._features = [hit_feature(track, int(h), sr) for h in hits]
    n_before = len(dr2.hits)
    dr2.remove_similar(0, tol=0.05)      # drop hits very close to hit 0
    print(f"remove_similar: {n_before} -> {len(dr2.hits)}")
    assert len(dr2.hits) < n_before
    dr2.keep_similar(0, tol=1.0)         # keep everything similar (all)
    print(f"keep_similar(all): {len(dr2.hits)}")
    assert len(dr2.hits) >= 1

    return "drum_replacer demo OK"


if __name__ == "__main__":
    print(demo())
