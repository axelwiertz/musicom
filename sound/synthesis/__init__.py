"""Synthesis engines — sound generation methods."""

from .modal import ResonatorBank, ModalSynth
from .granular import AperiodicGranulator
from .phase_mod import PhaseModSynth, FDSSynth
from .additive import SoundWave, synthesize_wave
from .vocal import FormantVocalGuide
from .singing_voice import SingingVoice
from .polysynth import PolyVoice, Oscillator, EnvelopeGenerator, LFO, MultimodeFilter, StepSequencer, Arpeggiator
from .bowed import BowedString
from .mass_spring import MassSpringSystem, Body, Spring
from .scale_quantizer import ScaleQuantizer, ProbabilityEngine, ScaleModeMIDI
from .voice_allocator import VoiceAllocator, ModulationMatrix
from .polyrhythm import PolyrhythmicArp
from .binaural import HaasDelay, BinauralSynth
from .west_coast import Wavefolder, LowpassGate, WestCoastVoice

__all__ = [
    "ResonatorBank",
    "ModalSynth",
    "AperiodicGranulator",
    "PhaseModSynth",
    "FDSSynth",
    "SoundWave",
    "synthesize_wave",
    "FormantVocalGuide",
    "SingingVoice",
    "PolyVoice",
    "Oscillator",
    "EnvelopeGenerator",
    "LFO",
    "MultimodeFilter",
    "StepSequencer",
    "Arpeggiator",
    "BowedString",
    "MassSpringSystem",
    "Body",
    "Spring",
    "ScaleQuantizer",
    "ProbabilityEngine",
    "ScaleModeMIDI",
    "VoiceAllocator",
    "ModulationMatrix",
    "PolyrhythmicArp",
    "HaasDelay",
    "BinauralSynth",
    "Wavefolder",
    "LowpassGate",
    "WestCoastVoice",
]
