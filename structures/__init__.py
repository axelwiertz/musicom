"""
Musicom structures package
Music composition structures, theory, rhythm, and network representations
"""

from .circle import Circle
from .helix import Helix

# Core structures
from .composition import (
    PitchRegister,
    MusicTime,
    MusicUnit,
    MusicVoice,
    MusicSection,
    MusicComposition,
)

# Music theory
from .theory import (
    Diatonic,
    MusicPattern,
    MusicScale,
    MusicalInterval,
    PatternSequence,
    PitchClassSet,
)

# Rhythm
from .rhythm import (
    QuantizedEvent,
    MetricalNode,
    HierarchicalEvent,
    seconds_to_ticks,
)

# Sound wave synthesis
from .soundwave import (
    SoundWave,
    synthesize_wave,
)

# Network representations
from .network import (
    semitones_between,
    transpose_pc,
    triad,
    seventh,
    smooth_four_voice_leading,
    build_chromatic_graph,
    build_diatonic_graph,
    export_graph,
    plot_graph,
)

from .intervalnetwork import (
    make_chromatic_interval_network,
    to_networkx,
)

__all__ = [
    # Core structures
    'MusicUnit',
    'MusicVoice',
    'MusicSection',
    'MusicComposition',
    'Circle',
    'Helix',

    # Music theory
    'PitchRegister',
    'Diatonic',
    'MusicPattern',
    'MusicScale',
    'MusicalInterval',
    'PatternSequence',
    'PitchClassSet',

    # Rhythm
    'MusicTime',
    'QuantizedEvent',
    'MetricalNode',
    'HierarchicalEvent',
    'seconds_to_ticks',
    'euclidian',

    # Sound wave
    'SoundWave',
    'synthesize_wave',

    # Network
    'semitones_between',
    'transpose_pc',
    'triad',
    'seventh',
    'smooth_four_voice_leading',
    'build_chromatic_graph',
    'build_diatonic_graph',
    'export_graph',
    'plot_graph',
    'make_chromatic_interval_network',
    'to_networkx',
]

