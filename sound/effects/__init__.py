"""Audio effects - transform audio signals.

Includes algorithmic reverb, digital filters, subtractive synthesis, and mastering tools.
"""

from .reverb import AlgorithmicReverb, Freeverb, apply_reverb
from .filter import (StateVariableFilter, BiquadFilter, SubtractiveVoice, 
                     apply_filter)
from .mastering import (LUFSMeter, LoudnessMetrics, measure_lufs, normalize_to_lufs,
                        StereoImager, Limiter, DynamicEQ, MasteringChain)
from .production_chain import ProductionChain, ProductionReport, StageResult
from .vowel_filter import VowelFilterBank, VOWEL_FORMANTS
from .tape_delay import TapeDelay, SamplePlayer, DrumMachine

__all__ = [
    "AlgorithmicReverb", "Freeverb", "apply_reverb",
    "StateVariableFilter", "BiquadFilter", "SubtractiveVoice", "apply_filter",
    "LUFSMeter", "LoudnessMetrics", "measure_lufs", "normalize_to_lufs",
    "StereoImager", "Limiter", "DynamicEQ", "MasteringChain",
    "ProductionChain", "ProductionReport", "StageResult",
    "VowelFilterBank", "VOWEL_FORMANTS",
    "TapeDelay", "SamplePlayer", "DrumMachine",
]
