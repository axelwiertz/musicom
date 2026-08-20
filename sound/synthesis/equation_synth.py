"""Equation-to-waveform synthesizer — MathSynth-style.

Users write mathematical expressions using numpy functions; the expression
is evaluated sample-by-sample to generate waveforms. Supports time-variable
equations, frequency control, and polyphonic rendering.

Replicated from: MathSynth iOS app (synthtopia 2026-08-18).

Usage:
    from sound.synthesis.equation_synth import EquationSynth

    synth = EquationSynth(sample_rate=44100)
    audio = synth.render("sin(2*pi*f*t) + 0.5*sin(4*pi*f*t)", f=440.0, duration=1.0)
    # More complex:
    audio = synth.render("sin(2*pi*f*t) * exp(-3*t/dur)", f=220, duration=0.5)
"""

import numpy as np
from typing import Optional, Dict, Any

__all__ = ["EquationSynth"]

# Safe namespace for equation evaluation
_SAFE_FUNCS = {
    'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
    'asin': np.arcsin, 'acos': np.arccos, 'atan': np.arctan,
    'sinh': np.sinh, 'cosh': np.cosh, 'tanh': np.tanh,
    'exp': np.exp, 'log': np.log, 'log2': np.log2, 'log10': np.log10,
    'sqrt': np.sqrt, 'abs': np.abs,
    'floor': np.floor, 'ceil': np.ceil, 'round': np.round,
    'sign': np.sign, 'clip': np.clip,
    'pi': np.pi, 'e': np.e,
    'mod': np.mod, 'fmod': np.fmod,
    'max': np.maximum, 'min': np.minimum,
    'where': np.where,
}


class EquationSynth:
    """Render audio from mathematical equations.

    Equations are numpy-compatible expressions using t (time), f (frequency),
    dur (duration), and any custom parameters.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def render(self, equation: str, f: float = 440.0,
               duration: float = 1.0, amplitude: float = 0.8,
               **params) -> np.ndarray:
        """Render an equation to audio.

        Args:
            equation: Math expression using t, f, dur, pi, e, and numpy funcs.
            f: Base frequency in Hz.
            duration: Duration in seconds.
            amplitude: Output amplitude scaling.
            **params: Additional parameters available in the equation.

        Returns:
            Mono audio array.
        """
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        dur = duration

        # Build evaluation namespace
        namespace = dict(_SAFE_FUNCS)
        namespace['t'] = t
        namespace['f'] = f
        namespace['dur'] = dur
        namespace['sr'] = self.sample_rate
        namespace['n'] = np.arange(n_samples)
        namespace.update(params)

        # Evaluate
        try:
            result = eval(equation, {"__builtins__": {}}, namespace)
        except Exception as e:
            raise ValueError(f"Equation eval failed: {e}\n  equation: {equation}")

        result = np.asarray(result, dtype=np.float64)
        if result.ndim == 0:
            result = np.full(n_samples, float(result))
        if len(result) != n_samples:
            raise ValueError(f"Equation produced {len(result)} samples, expected {n_samples}")

        # Normalize and scale
        peak = np.max(np.abs(result))
        if peak > 0:
            result = result / peak * amplitude
        return result

    def render_chord(self, equation: str, frequencies: list,
                     duration: float = 1.0, **params) -> np.ndarray:
        """Render a chord by evaluating the equation at multiple frequencies.

        Args:
            equation: Math expression (should use f variable).
            frequencies: List of frequencies in Hz.
            duration: Duration in seconds.
            **params: Additional parameters.

        Returns:
            Mixed mono audio.
        """
        n_samples = int(duration * self.sample_rate)
        output = np.zeros(n_samples, dtype=np.float64)
        for freq in frequencies:
            voice = self.render(equation, f=freq, duration=duration, **params)
            output += voice
        # Normalize
        peak = np.max(np.abs(output))
        if peak > 0:
            output = output / peak * 0.8
        return output

    def render_polyphonic(self, equation: str, notes: list,
                          duration: float = 1.0, **params) -> np.ndarray:
        """Render polyphonic audio from MIDI note numbers.

        Args:
            equation: Math expression.
            notes: List of MIDI note numbers.
            duration: Duration in seconds.
            **params: Additional parameters.

        Returns:
            Mixed mono audio.
        """
        freqs = [440.0 * (2.0 ** ((n - 69) / 12.0)) for n in notes]
        return self.render_chord(equation, freqs, duration, **params)


def demo() -> str:
    """Render demo waveforms and return summary."""
    synth = EquationSynth(sample_rate=44100)

    # Simple sine
    a1 = synth.render("sin(2*pi*f*t)", f=440.0, duration=0.5)

    # Additive: fundamental + harmonics
    a2 = synth.render(
        "sin(2*pi*f*t) + 0.5*sin(4*pi*f*t) + 0.25*sin(6*pi*f*t)",
        f=220.0, duration=0.5
    )

    # FM-style
    a3 = synth.render(
        "sin(2*pi*f*t + 3*sin(2*pi*5*t))",
        f=440.0, duration=0.5
    )

    # Exponential decay
    a4 = synth.render(
        "sin(2*pi*f*t) * exp(-5*t/dur)",
        f=330.0, duration=1.0
    )

    # Chord
    a5 = synth.render_polyphonic(
        "sin(2*pi*f*t) + 0.3*sin(4*pi*f*t)",
        notes=[60, 64, 67],  # C major
        duration=1.0
    )

    lines = [
        f"sine 440Hz: {len(a1)} samples, peak={np.max(np.abs(a1)):.3f}",
        f"additive 220Hz: {len(a2)} samples, peak={np.max(np.abs(a2)):.3f}",
        f"FM 440Hz: {len(a3)} samples, peak={np.max(np.abs(a3)):.3f}",
        f"decay 330Hz: {len(a4)} samples, peak={np.max(np.abs(a4)):.3f}",
        f"C major chord: {len(a5)} samples, peak={np.max(np.abs(a5)):.3f}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(demo())
