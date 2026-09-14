# -*- coding: utf-8 -*-
"""Generator package — lazily resolved exports (PEP 562 ``__getattr__``).

IMPORTANT INVARIANT
-------------------
Importing this package, or any of its submodules (e.g.
``generators.generator_registry``), MUST NOT pull in the heavy / legacy
``musicpy`` or ``music21`` dependency tree.

Why this matters (regression history)
-------------------------------------
This ``__init__`` used to eagerly import every generator. Because Python runs
a package's ``__init__`` on *any* submodule import, importing the method
registry — a pure data table — dragged in the whole legacy bridge:

    generators.chord_degrees -> converters.musicpy_converter   (import musicpy)
                             -> converters.music21_pattern     (music21)
    generators.harmonics     -> from music21 import note, interval

``workflows/selector.py`` and ``workflows/paths.py`` both do
``from generators.generator_registry import GENERATOR_REGISTRY``, so *every*
method-selection session loaded musicpy + music21. A composition job once
burned its entire budget "fixing converters" it had no business touching
instead of composing. That is the bug this lazy module prevents.

Compatibility
-------------
Names resolve on first attribute access, so all existing forms keep working:

    from generators import RhythmGenerator          # 75 project scripts
    from generators import TonalNetworkGenerator
    from generators import TintinnabuliGenerator, isorhythmize
    import generators; generators.ChordDegreeGenerator

Resolved values are memoized into this module's globals, so the import cost
is paid once and only for the generators actually used.
"""

import importlib
from typing import Dict, Tuple

# name -> (submodule, attribute name within it)
_LAZY_EXPORTS: Dict[str, Tuple[str, str]] = {
    "ChordDegreeGenerator": (".chord_degrees", "ChordDegreeGenerator"),
    "RhythmGenerator": (".rhythm", "RhythmGenerator"),
    "HarmonicsGenerator": (".harmonics", "HarmonicsGenerator"),
    "GeneticGenerator": (".genetic", "GeneticGenerator"),
    "PatternGenerator": (".pitchpattern", "PatternGenerator"),
    "StochasticGenerator": (".stochastic", "StochasticGenerator"),
    "MarkovChainGenerator": (".chain", "MarkovChainGenerator"),
    "TintinnabuliGenerator": (".tintinnabuli", "TintinnabuliGenerator"),
    "isorhythmize": (".tintinnabuli", "isorhythmize"),
    "TonalNetworkGenerator": (".tonal_network", "TonalNetworkGenerator"),
}

__all__ = list(_LAZY_EXPORTS)


def __getattr__(name: str):
    """Resolve an exported generator name on first access (PEP 562)."""
    try:
        module_name, attr = _LAZY_EXPORTS[name]
    except KeyError:
        raise AttributeError(
            f"module {__name__!r} has no attribute {name!r}"
        ) from None
    value = getattr(importlib.import_module(module_name, __name__), attr)
    globals()[name] = value  # memoize: pay the import cost once
    return value


def __dir__():
    return sorted(set(globals()) | set(_LAZY_EXPORTS))
