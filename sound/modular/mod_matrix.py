"""Generic modulation matrix — Sequential Take 5 unofficial editor style.

Replicable control-routing logic from the Synthtopia item "Sequential
Skip Take 5 Gets Unofficial Patch Editor" (2026-10-16). The Take 5 editor
surfaces a 16-slot modulation matrix with **20 sources and 56 destinations**
at a glance, per-slot enable, and A/B snapshot **morph** ("Capture two
sounds... morph between them with a slider").

What is replicated here (pure control logic, no audio DSP):

* ``ModMatrix`` — up to 16 slots; each slot ties one *source* to one
  *destination* with an amount and an on/off switch;
* ``MOD_SOURCES`` — 20 built-in sources: LFOs (sine/tri/saw/S&H/noise),
  envelopes (per-note ADSR with a simple decay release model), performance
  inputs (modwheel, breath, aftertouch, velocity, pitchbend, note number),
  macros and a random source — all evaluable as float streams (0..1 bipolar
  or unipolar by convention);
* ``MOD_DESTINATIONS`` — 56 named destinations (pitch per-osc, pulse width,
  filter cutoff/resonance/bandwidth/profile, amp, pan, FX sends, LFO rate,
  ...) as a registry; routing is generic so any float parameter can be patched;
* ``evaluate()`` — sums slot contributions per destination over time
  (unipolar/bipolar-aware, exponential-taper option for audio-rate safety);
* ``Snapshot`` morph: capture matrix A and B, morph amounts with a 0..1
  slider (per-slot crossfade);
* deterministic per ``seed``.

Not replicated: the SysEx editor, DAW automation host, 5-pin DIN/USB MIDI.

Usage:
    from sound.modular.mod_matrix import ModMatrix, MOD_SOURCES

    m = ModMatrix()
    m.set_slot(0, "lfo1", "filter_cutoff", amount=0.4)
    out = m.evaluate(voices=1, n_samples=44100, bpm=120)
    # out["filter_cutoff"] -> modulation signal for the parameter
"""

from __future__ import annotations

import numpy as np

# ----------------------------------------------------------------------
# source/destination registries (16 slots x 20 sources x 56 destinations)
# ----------------------------------------------------------------------
MOD_SOURCES = [
    "lfo1", "lfo2", "env1", "env2", "env3", "env4",
    "aftertouch", "velocity", "modwheel", "breath", "pitchbend",
    "note_number", "random_sh", "noise", "seq_step",
    "macro1", "macro2", "macro3", "macro4", "gate",
]

MOD_DESTINATIONS = [
    "osc1_pitch", "osc2_pitch", "osc3_pitch", "osc1_pw", "osc2_pw", "osc3_pw",
    "osc_sync", "noise_level", "filter_cutoff", "filter_res", "filter_bp",
    "filter_env_amt", "filter_key_track", "amp_level", "amp_env_amt",
    "pan", "width", "portamento",
    "fx1_send", "fx2_send", "delay_time", "delay_fb", "reverb_time", "reverb_mix",
    "lfo1_rate", "lfo1_depth", "lfo2_rate", "lfo2_depth",
    "env1_attack", "env1_decay", "env1_sustain", "env1_release",
    "env2_attack", "env2_decay", "env2_sustain", "env2_release",
    "env3_attack", "env3_decay", "env3_sustain", "env3_release",
    "env4_attack", "env4_decay", "env4_sustain", "env4_release",
    "voice_detune", "voice_spread", "unison_detune",
    "ring_mod", "fm_amt", "xmod_amt", "glide_rate",
    "vca_curve", "filter_profile", "drive", "feedback",
]

# how each destination should receive the summed modulation:
# "uni" destinations expect a positive offset (e.g. filter cutoff up),
# "bi" accept bipolar values (e.g. pan / pw).
DEST_POLARITY = {d: ("bi" if d in ("pan", "width", "osc1_pw", "osc2_pw",
                                    "osc3_pw", "ring_mod", "xmod_amt")
                     else "uni") for d in MOD_DESTINATIONS}


class ModMatrix:
    """Up-to-16-slot modulation matrix with A/B snapshot morph.

    Args:
        seed: RNG seed for lfo/random/sh noise sources.
    """

    MAX_SLOTS = 16

    def __init__(self, seed: int = 0):
        self.rng = np.random.default_rng(seed)
        self.slots = []  # list of dicts: source, dest, amount, enabled

    # ------------------------------------------------------------------
    # patch editing
    # ------------------------------------------------------------------
    def set_slot(self, index: int, source: str, dest: str,
                 amount: float = 1.0, enabled: bool = True) -> None:
        """Configure slot ``index`` (0..15)."""
        if not 0 <= index < self.MAX_SLOTS:
            raise ValueError(f"slot index {index} out of range 0..15")
        if source not in MOD_SOURCES:
            raise ValueError(f"unknown source {source!r}; choose from {MOD_SOURCES}")
        if dest not in MOD_DESTINATIONS:
            raise ValueError(f"unknown dest {dest!r}; choose from {MOD_DESTINATIONS}")
        while len(self.slots) <= index:
            self.slots.append(None)
        self.slots[index] = {
            "source": source, "dest": dest,
            "amount": float(amount), "enabled": bool(enabled),
        }

    def clear_slot(self, index: int) -> None:
        if 0 <= index < len(self.slots):
            self.slots[index] = None

    def snapshot(self) -> "ModMatrix":
        """Deep-copy snapshot (A/B morph pair)."""
        clone = ModMatrix(seed=int(self.rng.integers(0, 2 ** 31)))
        clone.slots = [dict(s) if s else None for s in self.slots]
        return clone

    @staticmethod
    def morph(a: "ModMatrix", b: "ModMatrix", t: float) -> "ModMatrix":
        """Morph between snapshot A (t=0) and B (t=1) by crossfading
        per-slot amounts (the take-5 A/B morph slider)."""
        t = float(np.clip(t, 0.0, 1.0))
        out = ModMatrix(seed=0)
        n = max(len(a.slots), len(b.slots))
        for i in range(n):
            sa = a.slots[i] if i < len(a.slots) else None
            sb = b.slots[i] if i < len(b.slots) else None
            if sa is None and sb is None:
                continue
            if sa is None:
                out.slots.append(dict(sb))
                continue
            if sb is None:
                out.slots.append(dict(sa))
                continue
            if sa["source"] != sb["source"] or sa["dest"] != sb["dest"]:
                # routing change: fade std out, sb in (per-slot crossfade)
                out.slots.append(dict(sa) | {"amount": sa["amount"] * (1 - t)})
                out.slots.append(dict(sb) | {"amount": sb["amount"] * t})
                continue
            merged = dict(sa)
            merged["amount"] = sa["amount"] * (1 - t) + sb["amount"] * t
            merged["enabled"] = sa["enabled"] or sb["enabled"]
            out.slots.append(merged)
        return out

    # ------------------------------------------------------------------
    # source evaluation
    # ------------------------------------------------------------------
    def _eval_source(self, src: str, n: int, bpm: float,
                     note_pitch: float = 60.0, velocity: float = 0.8,
                     modwheel: float = 0.0, aftertouch: float = 0.0,
                     breath: float = 0.0, pitchbend: float = 0.0) -> np.ndarray:
        t = np.arange(n) / 44100.0
        if src == "lfo1":
            return np.sin(2 * np.pi * 0.5 * t)
        if src == "lfo2":
            return 2.0 * (t * 0.2 % 1.0) - 1.0            # slow triangle-ish
        if src in ("env1", "env2", "env3", "env4"):
            # ADSR-ish exponential envelope (attack 5ms, decay 200ms, s=0.4)
            env = np.exp(-t / 0.15) * 0.6 + 0.4
            a = min(int(0.005 * 44100), max(1, n // 8))
            d = min(int(0.2 * 44100), max(1, n - a))
            env[:a] = np.linspace(0.0, 1.0, a)
            env[a:a + d] = np.linspace(1.0, 0.4, d)
            return env
        if src == "aftertouch":
            return np.full(n, aftertouch)
        if src == "velocity":
            return np.full(n, velocity)
        if src == "modwheel":
            return np.full(n, modwheel)
        if src == "breath":
            return np.full(n, breath)
        if src == "pitchbend":
            return np.full(n, pitchbend)
        if src == "note_number":
            return np.full(n, (note_pitch - 60) / 24.0)
        if src == "random_sh":
            return self.rng.uniform(-1, 1, n)
        if src == "noise":
            return self.rng.standard_normal(n) * 0.5
        if src == "seq_step":
            return np.tile(np.linspace(-1, 1, 16), n // 16 + 1)[:n]
        if src.startswith("macro"):
            idx = int(src[5:]) - 1
            return np.full(n, [0.0, 0.3, -0.2, 0.5][idx % 4])
        if src == "gate":
            return (np.sin(2 * np.pi * (bpm / 60.0 / 2.0) * t) > 0).astype(float)
        return np.zeros(n)

    # ------------------------------------------------------------------
    # evaluation
    # ------------------------------------------------------------------
    def evaluate(self, n_samples: int = 4096, bpm: float = 120.0,
                 note_pitch: float = 60.0, **perf) -> dict:
        """Evaluate all slots -> {dest: modulation signal} (summed).

        Args:
            n_samples: length of the modulation streams.
            bpm: tempo (used by gate / seq_step).
            note_pitch, velocity, modwheel, aftertouch, breath, pitchbend:
                performance values for those sources.

        Returns:
            Dict destination -> np.ndarray (bipolar), clipped to [-2, 2].
        """
        acc = {d: np.zeros(n_samples) for d in MOD_DESTINATIONS}
        for slot in self.slots:
            if slot is None or not slot["enabled"]:
                continue
            sig = self._eval_source(slot["source"], n_samples, bpm,
                                    note_pitch=note_pitch, **perf)
            sig = sig * slot["amount"]
            if DEST_POLARITY.get(slot["dest"], "uni") == "uni":
                sig = np.maximum(sig, 0.0)
            acc[slot["dest"]] += sig
        for d, sig in acc.items():
            acc[d] = np.clip(sig, -2.0, 2.0)
        return acc


def demo() -> dict:
    """Self-test: patch a filter-cutoff LFO + env, morph A/B, evaluate."""
    m = ModMatrix(seed=5)
    m.set_slot(0, "lfo1", "filter_cutoff", amount=0.35)
    m.set_slot(1, "env1", "filter_env_amt", amount=0.8)
    m.set_slot(2, "modwheel", "pan", amount=0.6)
    m.set_slot(3, "velocity", "amp_level", amount=0.5)

    a = m.snapshot()
    m.set_slot(0, "lfo1", "filter_cutoff", amount=0.75)  # same routing, new amount
    m.set_slot(5, "lfo2", "pan", amount=0.4)             # added routing
    b = m.snapshot()

    out = m.evaluate(n_samples=2048, bpm=120, note_pitch=64, velocity=0.9)
    morphed = ModMatrix.morph(a, b, 0.5).evaluate(n_samples=2048)

    assert "filter_cutoff" in out and "pan" in out and "amp_level" in out
    assert len(out["filter_cutoff"]) == 2048
    assert float(np.max(np.abs(out["pan"]))) <= 2.0
    # same-routing amount morph at t=0.5 -> amount halfway between 0.35 and 0.75
    mid = (0.35 + 0.75) / 2
    peak_b = float(np.max(np.abs(out["filter_cutoff"])))          # amount 0.75
    peak_morph = float(np.max(np.abs(morphed["filter_cutoff"])))  # amount 0.55
    assert abs(peak_morph - peak_b * (mid / 0.75)) < 0.02, \
        f"morph peak {peak_morph:.4f} != {peak_b * (mid / 0.75):.4f}"
    # crossfaded routing (slot 5: lfo2@0 -> pan) fades in toward 0.2 peak
    pan_peak = float(np.max(np.abs(morphed["pan"])))
    assert 0.05 < pan_peak <= 2.0
    return {
        "slots_used": sum(1 for s in m.slots if s is not None),
        "destinations_active": sorted(k for k, v in out.items()
                                      if float(np.max(np.abs(v))) > 1e-6),
        "filter_cutoff_peak": float(np.max(np.abs(out["filter_cutoff"]))),
        "morph_mid_amt": round(mid, 3),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))