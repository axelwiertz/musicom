"""Package for music composition structures."""
from .unit import MusicUnit, MusicEvent
from .time import MusicLinearTime, TempoRange, TimeConverter
from .timegrid import MusicTimeGrid, MusicRhythmPattern
from .project import MusicSection, MusicVoice, MusicProject
from .matrix import UnitMatrix
from .instrument import MidiChannel, MidiInstrument, MidiPercussion
from .pitch import MusicPitch, MusicPitchClass, MusicPitchGrid, Direction, MusicPitchRange
from .metrical import MetricalNode, HierarchicalEvent, QuantizedEvent, \
    seconds_to_ticks, quantize_onsets_to_ticks, build_common_tree, assign_metrical_level

# ---------------------------------------------------------------------------
# QUARANTINED names — resolved LAZILY (PEP 562), not at import time.
#
# The mode-centric pitch-class model now lives in legacy/pitchclass.py. It is
# not reachable from compose() and is partly broken, but it still has live
# consumers, so the names stay importable from here.
#
# Lazy resolution is required, not stylistic: legacy/pitchclass.py imports
# structures.pitch, which triggers this package __init__. Importing legacy
# eagerly here would therefore import a partially-initialised module and
# raise ImportError. Resolving on first attribute access breaks the cycle.
#
# New code should use rules/patterns.py instead.
# ---------------------------------------------------------------------------
_LEGACY_EXPORTS = frozenset({
    "MusicPitchClassSet", "Cardinality", "PatternType", "PatternRotation",
    "PatternGraph", "create_subpattern",
})


def __getattr__(name: str):
    """Resolve quarantined System A names on first access (PEP 562)."""
    if name in _LEGACY_EXPORTS:
        import legacy.pitchclass as _legacy
        return getattr(_legacy, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | _LEGACY_EXPORTS)

__all__ = [
    "MusicEvent",
    "MusicUnit",
    "MusicTimeGrid",
    "MusicLinearTime",
    "TempoRange",
    "TimeConverter",
    "MusicRhythmPattern",
    "MusicPitchClassSet",
    "MusicPitchClassSet",  # Keep for backward compatibility
    "Cardinality",
    "PatternType",
    "PatternRotation",
    "PatternGraph",

    "MusicSection",
    "MusicVoice",
    "MusicProject",
    "UnitMatrix",

    'MidiInstrument',
    'MidiPercussion',
    'MidiChannel',

    'MusicPitchClass',
    'MusicPitch',
    'MusicPitchGrid',
    'Direction',
    'MusicPitchRange',

]