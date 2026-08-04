"""Synthesis engines — sound generation methods.

Modal synthesis, granular synthesis, phase modulation, additive synthesis,
and vocal synthesis.
"""

from .modal import ResonatorBank, ModalSynth
from .granular import AperiodicGranulator
from .phase_mod import PhaseModSynth, FDSSynth
from .additive import SoundWave, synthesize_wave
from .vocal import FormantVocalGuide

__all__ = [
    "ResonatorBank",
    "ModalSynth",
    "AperiodicGranulator",
    "PhaseModSynth",
    "FDSSynth",
    "SoundWave",
    "synthesize_wave",
    "FormantVocalGuide",
]
