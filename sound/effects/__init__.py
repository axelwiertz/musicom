"""Audio effects - transform audio signals.

Includes algorithmic reverb, digital filters, subtractive synthesis, and mastering tools.
"""

from .reverb import AlgorithmicReverb, Freeverb, apply_reverb
from .filter import (StateVariableFilter, BiquadFilter, SubtractiveVoice, 
                     apply_filter)
from .mastering import (LUFSMeter, LoudnessMetrics, measure_lufs, normalize_to_lufs,
                        StereoImager, Limiter, DynamicEQ, MasteringChain,
                        master, true_peak_limit, glue_compress, high_pass,
                        target_for_style, LOUDNESS_TARGETS, GENRE_LUFS)
from .production_chain import ProductionChain, ProductionReport, StageResult
from .vowel_filter import VowelFilterBank, VOWEL_FORMANTS
from .tape_delay import TapeDelay, SamplePlayer, DrumMachine
from .fdn_reverb import FDN
from .multiband import LinkwitzRiley, MultibandCompressor, MultibandSynth
from .quantize_mod import QuantizeModulator, ModRouter, QuantizeChain
from .ir_designer import design_ir, IR_RECIPES

__all__ = [
    "AlgorithmicReverb", "Freeverb", "apply_reverb",
    "StateVariableFilter", "BiquadFilter", "SubtractiveVoice", "apply_filter",
    "LUFSMeter", "LoudnessMetrics", "measure_lufs", "normalize_to_lufs",
    "StereoImager", "Limiter", "DynamicEQ", "MasteringChain",
    "master", "true_peak_limit", "glue_compress", "high_pass",
    "target_for_style", "LOUDNESS_TARGETS", "GENRE_LUFS",
    "ProductionChain", "ProductionReport", "StageResult",
    "VowelFilterBank", "VOWEL_FORMANTS",
    "TapeDelay", "SamplePlayer", "DrumMachine",
    "FDN",
    "LinkwitzRiley", "MultibandCompressor", "MultibandSynth",
    "QuantizeModulator", "ModRouter", "QuantizeChain",
]