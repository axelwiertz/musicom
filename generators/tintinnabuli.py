"""Arvo Pärt tintinnabuli + isorhythm generators.

Implements two of Pärt's core technical procedures, promoted from the
`research/` folder idea (``arvo_project.py``):

1. **Tintinnabuli** — two-voice counterpoint where a stepwise M-voice
   (melodic, moves within a mode) is shadowed by a T-voice that only ever
   uses tones of a single tintinnabuli triad (usually the tonic chord). The
   T-voice sits at a chosen *position* relative to the M-voice.

2. **Isorhythm** — a repeating rhythmic pattern (*talea*) is applied cyclically
   to a pitch pattern (*color*). Pärt used isorhythm to lock voices into a
   shared, relentless pulse.

Both generators subclass ``MusicGenerator`` and operate on ``MusicUnit`` /
``MusicEvent``.

Usage:
    from generators.tintinnabuli import TintinnabuliGenerator

    gen = TintinnabuliGenerator(tonic=60, mode='major')
    m = gen.m_voice([62, 64, 67, 64])     # stepwise-conformed melody
    t = gen.t_voice(m.pitches, position=1)  # T-voice above the melody
    duet = m + t
"""

from typing import List, Optional, Sequence

from structures.unit import MusicUnit, MusicEvent
from generators.base import MusicGenerator

# Diatonic interval patterns (in semitones above the tonic), Pärt standard modes.
MODE_PATTERNS = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'natural minor': [0, 2, 3, 5, 7, 8, 10],
    'harmonic minor': [0, 2, 3, 5, 7, 8, 11],
    'dorian': [0, 2, 3, 5, 7, 9, 10],
    'phrygian': [0, 1, 3, 5, 7, 8, 10],
    'lydian': [0, 2, 4, 6, 7, 9, 11],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10],
}

# Minor triad as ascending (semitone offsets), the Pärt tintinnabuli triad.
TRIAD_ASC = (0, 3, 7)   # root, minor 3rd, 5th
TRIAD_MAJ = (0, 4, 7)


def _pc(midi: int) -> int:
    return midi % 12


class TintinnabuliGenerator(MusicGenerator):
    """Generates Pärt's M-voice and T-voice pair.

    The M-voice is inherently stepwise (conjunct). Given a raw melodic
    fragment, ``m_voice`` snaps each note to the nearest degree of the chosen
    mode (preserving the tintinnabuli's inherent stepwise tendency). The
    T-voice takes every M-note and finds the tintinnabuli triad tone nearest to
    it within the T-voice's octave register, at a configurable *position*.
    """

    def __init__(
        self,
        tonic: int = 60,
        mode: str = 'major',
        triad: Optional[Sequence[int]] = None,
        t_register: int = 48,   # C3 default T-voice register
    ):
        super().__init__()
        self.tonic = tonic
        self.mode = mode
        if mode not in MODE_PATTERNS:
            raise ValueError(f"unknown mode '{mode}'; choose from {list(MODE_PATTERNS)}")
        self.scale_offsets = MODE_PATTERNS[mode]
        self.triad = tuple(triad) if triad is not None else \
            TRIAD_MAJ if mode == 'major' else TRIAD_ASC
        # T-voice register center (a MIDI pitch inside which triad tones live).
        self.t_register = t_register

    # -- helpers ---------------------------------------------------------

    def _scale_pitch(self, degree_offset: int) -> int:
        """Absolute MIDI pitch for a diatonic degree offset from the tonic."""
        octave, idx = divmod(degree_offset, len(self.scale_offsets))
        return self.tonic + octave * 12 + self.scale_offsets[idx]

    def m_voice(self,
                melody: MusicUnit | Sequence[int],
                volume: int = 90) -> MusicUnit:
        """Return the M-voice: a melodic unit, stepped onto the mode.

        Args:
            melody: a ``MusicUnit`` or a list of MIDI pitches. If a bare list
                is given, each pitch is rendered as a single one-beat event.
            volume: velocity for generated events.

        Returns:
            A ``MusicUnit`` where every pitch falls on the chosen mode degrees.
        """
        if isinstance(melody, MusicUnit):
            units = melody
            raw_pitches = melody.pitches
        else:
            raw_pitches = [int(p) for p in melody]
            units = None

        # Snap each raw pitch to the nearest scale pitch by absolute distance.
        snapped = []
        for p in raw_pitches:
            degree_rel = p - self.tonic
            octave_floor = degree_rel // 12
            within = (degree_rel % 12 + 12) % 12
            # nearest scale step to `within`
            best_off, best_d = None, 999
            for off in self.scale_offsets:
                d = abs(within - off)
                if d < best_d:
                    best_d, best_off = d, off
            snapped.append(
                self.tonic + octave_floor * 12 + best_off
            )

        out = MusicUnit()
        if units is not None:
            # Preserve the original rhythm (start/end ticks), only fix pitches.
            for ev, sp in zip(units.events, snapped):
                out.add_event(MusicEvent(
                    pitch=sp, volume=ev.volume,
                    start_tick=ev.start_tick, end_tick=ev.end_tick,
                ))
        else:
            for i, sp in enumerate(snapped):
                out.add_event(MusicEvent(
                    pitch=sp, volume=volume,
                    start_tick=i, end_tick=i + 1,
                ))
        return out

    def t_voice(self,
                m_pitches: Sequence[int],
                position: int = 0,
                volume: int = 80,
                start_ticks: Optional[Sequence[int]] = None,
                end_ticks: Optional[Sequence[int]] = None) -> MusicUnit:
        """Return the T-voice shadowing ``m_pitches``.

        For each M-note, pick the tintinnabuli triad tone nearest to it in the
        T-voice register. ``position`` selects which triad tone:

            - position 0: the triad tone nearest the M-note.
            - positive: count *outward* from the nearest (away from the triad
              core toward higher registers).
            - negative: count *inward* (toward lower registers).

        Args:
            m_pitches: M-voice pitches (one T note per M note).
            position: T-voice position relative to the M-voice.
            volume: velocity for T-voice events.
            start_ticks: optional onset ticks (defaults to 0,1,2,..).
            end_ticks: optional end ticks (defaults to start+1).

        Returns:
            A ``MusicUnit`` containing only tonic-triad tones.
        """
        if start_ticks is None:
            start_ticks = list(range(len(m_pitches)))
        if end_ticks is None:
            end_ticks = [s + 1 for s in start_ticks]

        triad_asc = sorted((self.triad[0], self.triad[1], self.triad[2]))
        out = MusicUnit()
        for mp, s, e in zip(m_pitches, start_ticks, end_ticks):
            # tone pool: triad tones across a few octaves around t_register
            reg = ((self.t_register - self.tonic) // 12)
            base = self.tonic + reg * 12
            pool = [base + off + k * 12 for off in triad_asc for k in (-1, 0, 1, 2)]
            # sort by distance from the M-note; position selects which nearest
            # triad tone (python negative index handles position < 0).
            dists = sorted(pool, key=lambda t: abs(t - int(mp)))
            pick = dists[position]
            out.add_event(MusicEvent(
                pitch=int(pick), volume=volume, start_tick=int(s), end_tick=int(e),
            ))
        return out

    def duet(self,
             melody: MusicUnit | Sequence[int],
             position: int = 1,
             m_volume: int = 90,
             t_volume: int = 80) -> MusicUnit:
        """Combine M-voice and T-voice into a single tintinnabuli duet."""
        m = self.m_voice(melody, volume=m_volume)
        starts = [e.start_tick for e in m.events]
        ends = [e.end_tick for e in m.events]
        t = self.t_voice(m.pitches, position=position, volume=t_volume,
                         start_ticks=starts, end_ticks=ends)
        both = m.clone()
        for ev in t.events:
            both.add_event(ev)
        return both

    def generate(self) -> List[MusicUnit]:
        """Concrete ``MusicGenerator.generate``: return a default duet."""
        return [self.duet([self.tonic, self.tonic + 4, self.tonic + 7, self.tonic + 5])]


def isorhythmize(
    color: Sequence[int],
    talea: Sequence[float],
    ticks_per_beat: int = 480,
    start_pitch: int = 60,
    volume: int = 90,
) -> MusicUnit:
    """Apply an isorhythmic *talea* to a pitch *color*.

    Pärt-style isorhythm cyclically maps the repeating pitch sequence
    ``color`` onto the repeating duration sequence ``talea``. The talea gives
    note lengths (in beats); the color gives pitches. Both cycle independently
    (their LCM defines the full period).

    Args:
        color: pitch pattern, cycled to provide consecutive pitches.
        talea: duration pattern (in beats), cycled to give note lengths.
        ticks_per_beat: tick resolution.
        start_pitch: unshifted base (``color`` values are semitone offsets).
        volume: velocity for all events.

    Returns:
        A ``MusicUnit`` with non-overlapping consecutive events.
    """
    if not color or not talea:
        raise ValueError("color and talea must be non-empty")
    out = MusicUnit()
    tick = 0
    n = max(len(color), len(talea))
    for i in range(n):
        p = start_pitch + color[i % len(color)]
        dur_beats = talea[i % len(talea)]
        dur = max(1, int(dur_beats * ticks_per_beat))
        out.add_event(MusicEvent(
            pitch=int(p), volume=volume,
            start_tick=int(tick), end_tick=int(tick + dur),
        ))
        tick += dur
    return out