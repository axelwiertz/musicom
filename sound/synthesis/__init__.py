"""Synthesis engines — sound generation methods."""

from .modal import ResonatorBank, ModalSynth
from .granular import AperiodicGranulator
from .phase_mod import PhaseModSynth, FDSSynth
from .additive import SoundWave, synthesize_wave
from .vocal import FormantVocalGuide
from .polysynth import PolyVoice, Oscillator, EnvelopeGenerator, LFO, MultimodeFilter, StepSequencer, Arpeggiator
from .bowed import BowedString

__all__ = [
    "ResonatorBank",
    "ModalSynth",
    "AperiodicGranulator",
    "PhaseModSynth",
    "FDSSynth",
    "SoundWave",
    "synthesize_wave",
    "FormantVocalGuide",
    "PolyVoice",
    "Oscillator",
    "EnvelopeGenerator",
    "LFO",
    "MultimodeFilter",
    "StepSequencer",
    "Arpeggiator",
    "BowedString",
]
