"""Switched discrete distortion-topology engine — Teaching Machines FuzzBillion style.

Replicable logic from the Sound On Sound review of the Teaching Machines
FuzzBillion (SOS, September 2026 issue):

    11 numerical switches, each with 10 positions (0-9), followed by a gain
    knob.  "The switches relate to various diodes and amplifiers (germanium,
    silicon, LED, etc) and each of those makes its own contribution to the
    overall distortion sound" -> 10**11 distinct circuit variations.  Input and
    output can each be switched between high-impedance instrument level and
    transformer-balanced line level.

What is replicated here:
- **Discrete element bank**: ten documented nonlinear transfer functions with
  distinct knee/symmetry characteristics:
    0 bypass, 1 transformer core saturation (tanh), 2 asymmetric tube stage,
    3 JFET square-law stage, 4 germanium antiparallel diode pair (0.30 V knee),
    5 silicon antiparallel pair (0.65 V knee), 6 single-diode asymmetric clamp
    (even harmonics / octave-up), 7 LED antiparallel pair (1.80 V knee),
    8 CMOS inverter hard clip, 9 op-amp rail clip with foldback of the residue.
  Each diode pair is modelled with the exact antiparallel transfer
  `y = Vk * asinh(x / Vk)` (slope 1 at origin, logarithmic squeeze above the
  knee Vk), which is why a germanium switch sounds squashed/soft and an LED
  switch sounds bright/hard for the same input.
- **Serial chain of 11 independently switched stages** -> ``10 ** 11`` exact
  circuit combinations (``circuit_count()``).  Switch order *is* signal order.
- **Instrument / line level I/O** as two drive trims (line = hotter into the
  same clippers, so more saturation) with output compensation.
- Pre-gain knob and output level, plus helpers to profile the harmonic
  signature of any code (spectral centroid) and to draw random circuits.

Not replicated: the physical enclosure, the numerical switch hardware, the
exact measured component selection of the original 11 circuit blocks (only the
class of each element is modelled).

Usage:
    from sound.effects.topology_distortion import FuzzBillion

    fb = FuzzBillion(sample_rate=44100)
    fb.code = (4, 5, 3, 2, 8, 0, 6, 7, 1, 9, 4)     # 11 switches, 0-9
    out = fb.process(audio, gain=2.0, io_mode="line")

    fb.random_circuit(seed=7)                       # random circuit variant
    print(fb.profile())                             # centroid / harmonic mix
"""

from __future__ import annotations

import random
from typing import Callable, Dict, List, Sequence, Tuple

import numpy as np

__all__ = [
    "ELEMENTS",
    "ELEMENT_NAMES",
    "TopologyStage",
    "FuzzBillion",
    "circuit_count",
    "code_from_switches",
    "switches_from_code",
    "random_code",
]

# Knee voltages (V) of the antiparallel diode pairs.
GERMANIUM_VK = 0.30
SILICON_VK = 0.65
LED_VK = 1.80


# --------------------------------------------------------------------- elements
def _bypass(x: np.ndarray) -> np.ndarray:
    return x.copy()


def _transformer(x: np.ndarray) -> np.ndarray:
    """Transformer/inductor core saturation: odd-harmonic tanh knee at 1.0."""
    return np.tanh(x)


def _tube(x: np.ndarray) -> np.ndarray:
    """Asymmetric single-ended stage: square term -> even harmonics, then tanh."""
    return np.tanh(x + 0.25 * x * x)


def _jfet(x: np.ndarray) -> np.ndarray:
    """JFET common-source square-law transfer y = x - x^2/2 with supply rails."""
    return np.clip(x - 0.5 * x * x, -1.2, 1.2)


def _ge_pair(x: np.ndarray) -> np.ndarray:
    """Germanium antiparallel diode pair, 0.30 V knee (soft, early squeeze)."""
    return GERMANIUM_VK * np.arcsinh(x / GERMANIUM_VK)


def _si_pair(x: np.ndarray) -> np.ndarray:
    """Silicon antiparallel diode pair, 0.65 V knee."""
    return SILICON_VK * np.arcsinh(x / SILICON_VK)


def _asym_diode(x: np.ndarray) -> np.ndarray:
    """Single silicon diode to ground: clamps one polarity only (even/octave)."""
    vk = SILICON_VK
    return (x - vk * np.log1p(np.exp(x / vk)) + 0.44 * vk)


def _led_pair(x: np.ndarray) -> np.ndarray:
    """LED antiparallel pair, 1.80 V knee (stays clean, then cracks hard)."""
    return LED_VK * np.arcsinh(x / LED_VK)


def _cmos(x: np.ndarray) -> np.ndarray:
    """CMOS inverter logic-stage hard clip at the supply rails."""
    return np.clip(x, -1.0, 1.0)


def _opamp_rail(x: np.ndarray) -> np.ndarray:
    """Op-amp output stage: rail clip at +/-0.85 V with foldback of the residue."""
    rail = 0.85
    clipped = np.clip(x, -rail, rail)
    return clipped - 0.35 * (x - clipped)


ELEMENTS: Tuple[Callable[[np.ndarray], np.ndarray], ...] = (
    _bypass,
    _transformer,
    _tube,
    _jfet,
    _ge_pair,
    _si_pair,
    _asym_diode,
    _led_pair,
    _cmos,
    _opamp_rail,
)

ELEMENT_NAMES: Tuple[str, ...] = (
    "bypass",
    "transformer-saturation",
    "tube-asymmetric",
    "jfet-squarelaw",
    "germanium-pair",
    "silicon-pair",
    "single-diode-clamp",
    "led-pair",
    "cmos-inverter",
    "opamp-rail-foldback",
)

NUM_SWITCHES = 11
NUM_ELEMENT_OPTIONS = len(ELEMENTS)


# ----------------------------------------------------------------------- helpers
def circuit_count() -> int:
    """Total number of distinct switch settings: 10 options on 11 switches."""
    return NUM_ELEMENT_OPTIONS ** NUM_SWITCHES


def code_from_switches(switches: Sequence[int]) -> Tuple[int, ...]:
    """Validate a switch list and return it as a tuple (signal order)."""
    if len(switches) != NUM_SWITCHES:
        raise ValueError(f"need {NUM_SWITCHES} switch values, got {len(switches)}")
    code = tuple(int(s) for s in switches)
    for s in code:
        if not 0 <= s < NUM_ELEMENT_OPTIONS:
            raise ValueError(f"switch value {s} out of range 0-{NUM_ELEMENT_OPTIONS-1}")
    return code


def switches_from_code(code: Sequence[int]) -> Tuple[int, ...]:
    return code_from_switches(code)


def random_code(seed: int | None = None) -> Tuple[int, ...]:
    rng = random.Random(seed)
    return tuple(rng.randrange(NUM_ELEMENT_OPTIONS) for _ in range(NUM_SWITCHES))


class TopologyStage:
    """One switched circuit block: element index + human-readable name."""

    def __init__(self, element: int = 4):
        self.element = int(element) % NUM_ELEMENT_OPTIONS

    @property
    def name(self) -> str:
        return ELEMENT_NAMES[self.element]

    def apply(self, x: np.ndarray) -> np.ndarray:
        return ELEMENTS[self.element](np.asarray(x, dtype=np.float64))

    def __repr__(self) -> str:  # pragma: no cover - convenience
        return f"TopologyStage({self.element}:{self.name})"


# ------------------------------------------------------------------------ engine
class FuzzBillion:
    """Serial chain of 11 switched nonlinear stages (FuzzBillion-style).

    Parameters
    ----------
    sample_rate : int
        Sampling rate in Hz (only used for the spectral helpers).
    """

    def __init__(self, sample_rate: int = 44100):
        self.sr = int(sample_rate)
        self.code: Tuple[int, ...] = (4,) * NUM_SWITCHES   # all-germanium chain
        self.gain: float = 1.0                             # pre-gain knob
        self.level: float = 1.0                            # output level
        self.io_mode: str = "inst"                         # "inst" | "line"

    # -- switch level API ---------------------------------------------------
    def set_switch(self, index: int, value: int) -> None:
        code = list(self.code)
        code[index] = int(value) % NUM_ELEMENT_OPTIONS
        self.code = tuple(code)

    def random_circuit(self, seed: int | None = None) -> Tuple[int, ...]:
        self.code = random_code(seed)
        return self.code

    def circuit_name(self) -> str:
        return " -> ".join(ELEMENT_NAMES[i] for i in self.code)

    # -- I/O impedance switch ----------------------------------------------
    def _io_trims(self, io_mode: str) -> Tuple[float, float]:
        """Return (in_trim, out_trim) for instrument vs line level."""
        if io_mode == "line":
            return 1.6, 1.0 / 1.6      # hotter in, compensated out
        return 1.0, 1.0                # high-impedance instrument

    # -- processing ---------------------------------------------------------
    def process(self, audio: np.ndarray, code: Sequence[int] | None = None,
                gain: float | None = None, level: float | None = None,
                io_mode: str | None = None) -> np.ndarray:
        """Run the signal through the switched chain.

        Args:
            audio: input signal (any shape, processed flat).
            code: optional switch tuple (11 values 0-9).
            gain: optional pre-gain override.
            level: optional output level override.
            io_mode: "inst" (default) or "line".

        Returns:
            float64 array with the same shape as ``audio``.
        """
        x = np.asarray(audio, dtype=np.float64)
        shape = x.shape
        x = x.reshape(-1)
        switches = code_from_switches(code) if code is not None else self.code
        g = self.gain if gain is None else float(gain)
        lvl = self.level if level is None else float(level)
        in_trim, out_trim = self._io_trims(io_mode or self.io_mode)

        y = x * g * in_trim
        for element in switches:
            y = ELEMENTS[element](y)
        y = y * lvl * out_trim
        return y.reshape(shape)

    def profile(self, freq: float = 220.0, seconds: float = 0.5,
                code: Sequence[int] | None = None,
                gain: float | None = None) -> Dict[str, float]:
        """Measure the harmonic signature of a circuit on a steady sine.

        Returns dict with spectral centroid (Hz), THD-ish energy ratio and
        the top harmonic index — a cheap fingerprint used by the smoke tests.
        """
        n = int(self.sr * seconds)
        tt = np.arange(n) / self.sr
        tone = 0.5 * np.sin(2 * np.pi * freq * tt)
        out = self.process(tone, code=code, gain=gain)
        spec = np.abs(np.fft.rfft(out * np.hanning(n)))
        fr = np.fft.rfftfreq(n, 1.0 / self.sr)
        total = float(np.sum(spec)) + 1e-18
        centroid = float(np.sum(fr * spec) / total)
        fund_bin = int(round(freq / (self.sr / n)))
        lo, hi = max(0, fund_bin - 2), fund_bin + 3
        fund = float(np.sum(spec[lo:hi])) + 1e-18
        harm = float(np.sum(spec)) - fund
        return {"centroid": centroid, "harmonic_ratio": harm / fund,
                "peak": float(np.max(np.abs(out)))}


def demo() -> str:
    """Exercise the switch matrix and print a real measurement report."""
    sr = 44100
    fb = FuzzBillion(sample_rate=sr)

    total = circuit_count()
    print(f"switch options per position: {NUM_ELEMENT_OPTIONS}")
    print(f"switches (serial stages):     {NUM_SWITCHES}")
    print(f"distinct circuits:            {total:,} (10**11 = {10**11:,})")
    assert total == 10 ** 11

    # same single-switch change at position 0 -> different output
    n = int(sr * 0.25)
    tt = np.arange(n) / sr
    tone = 0.6 * np.sin(2 * np.pi * 110.0 * tt)
    ge = fb.process(tone, code=(4,) + (0,) * 10)
    led = fb.process(tone, code=(7,) + (0,) * 10)
    print(f"germanium[0] vs led[0] identical? {np.allclose(ge, led)}")
    assert not np.allclose(ge, led)

    # knee ordering: germanium squeezes hardest -> highest centroid
    c_ge = fb.profile(code=(4,) + (0,) * 10)["centroid"]
    c_si = fb.profile(code=(5,) + (0,) * 10)["centroid"]
    c_led = fb.profile(code=(7,) + (0,) * 10)["centroid"]
    print(f"centroid Ge={c_ge:7.1f} Hz  Si={c_si:7.1f} Hz  LED={c_led:7.1f} Hz")
    assert c_ge > c_si > c_led

    # whole chain stays bounded; line level drives it harder
    fb.random_circuit(seed=7)
    inst = fb.process(tone, gain=3.0, io_mode="inst")
    line = fb.process(tone, gain=3.0, io_mode="line")
    print(f"random circuit: {fb.circuit_name()}")
    print(f"inst peak={np.max(np.abs(inst)):.3f}  line peak={np.max(np.abs(line)):.3f}")
    assert np.all(np.isfinite(inst)) and np.max(np.abs(inst)) < 4.0
    assert not np.allclose(inst, line)

    print("  topology_distortion demo OK")
    return "ok"


if __name__ == "__main__":
    demo()
