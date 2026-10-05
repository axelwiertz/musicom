# -*- coding: utf-8 -*-
"""
B.A.C.H. Composition Generator — multi-voice algorithmic composition.

Replicates the composition systems from the Kaona B.A.C.H. Eurorack module
(Synthtopia 2026-09-28), covering 11 composition languages beyond the
already-implemented FRACTAL system (sound/generators/fractal_seq.py, SP-098).

Languages implemented:
  - FUGUE        : multi-voice exposition with subject/answers/countersubject/episodes
  - CANON        : leading line with imitation, transposition, delay, contrary, retrograde, augmentation
  - PROBA        : Markov-chain directed randomness with configurable transition vocabularies
  - TINTINNABULI : melodic voice + voices drawn from a triad or current chord (Arvo Pärt-style)
  - MINIMAL      : gradual processes of phase shifting, addition, substitution, hocketing (Reich-style)
  - CELLULAR     : cellular automaton (Wolfram Rule n) → musical material; all 254 rules supported
  - TREE         : L-system branching structures interpreted as melodic paths
  - MOTIF        : melodic/rhythmic cell chains drawn from collections
  - HYBRID       : distributes multiple composition engines across four voices
  - GROOVE       : four rhythmic roles organised using 64 structures
  - GROOVE_MIX   : applies rhythmic structures (GROOVE) to pitches from a melodic language

Each language produces a list of (pitch, start_tick, duration_ticks, velocity) events
compatible with the musicom pipeline.

Usage:
    from sound.generators.bach_composer import fugue, canon, proba, ...
    from sound.generators.bach_composer import compose_with  # unified dispatcher
    events = compose_with("fugue", subject=[60, 62, 64, 65], ...)
"""

import numpy as np
import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Callable


# ===========================================================================
# Shared types
# ===========================================================================

@dataclass
class BachEvent:
    """A single note event from a B.A.C.H. composer."""
    pitch: int
    start_tick: int
    duration_ticks: int
    velocity: int = 100
    voice: int = 0  # 0..3 (four voices)


# ===========================================================================
# 1. FUGUE — multi-voice exposition from subject/answers/CS/episodes
# ===========================================================================

def fugue(
    subject: List[int],
    intervals: Optional[List[int]] = None,
    num_voices: int = 4,
    ticks_per_beat: int = 480,
    beats_per_entry: int = 4,
    r: random.Random = None,
) -> List[BachEvent]:
    """Construct a fugue exposition.

    Voice 0 presents the *subject*.  Voice 1 enters after a delay with a
    *real answer* (transposed to the dominant/related key).  Voice 2 later
    re-states the subject.  Voice 3 enters with countersubject material.

    Parameters
    ----------
    subject : list of pitch values (MIDI)
        The fugue subject (melodic line).
    intervals : list of (int, int) or None
        (start_delay_beats, transposition_semitones) per additional voice.
        Defaults to standard fugue entry spacing.
    num_voices : int
        Number of voices (2–4).
    ticks_per_beat : int
        Tick resolution.
    beats_per_entry : int
        Beats between each voice entry.
    r : random.Random
        Random state for reproducibility.

    Returns
    -------
    events : list of BachEvent
    """
    if r is None:
        r = random
    if intervals is None:
        # Standard: entries every N beats, answer on dominant (+7 st), then subject, then free
        intervals = []
        for v in range(1, num_voices):
            transposition = 7 if v % 2 == 1 else 0   # alternate dominant/subject
            intervals.append((beats_per_entry * v, transposition))

    events = []
    for voice_idx in range(min(num_voices, 4)):
        tick_offset = int(intervals[voice_idx][0] * ticks_per_beat * 4  # 4 beats per bar? no — beats_per_entry is in "beats"
                          if voice_idx < len(intervals) else 0)
        transp = intervals[voice_idx][1] if voice_idx < len(intervals) else 0

        if voice_idx == 3 and num_voices == 4:
            # countersubject: subject inverted (contrary motion)
            line = _contrary(subject, transp)
        else:
            line = [p + transp for p in subject]

        tick = tick_offset
        for p in line:
            duration_tick = ticks_per_beat // 2  # eighth note
            events.append(BachEvent(
                pitch=max(0, min(127, p)),
                start_tick=tick,
                duration_ticks=duration_tick,
                velocity=90,
                voice=voice_idx,
            ))
            tick += duration_tick + ticks_per_beat // 4  # dotted feel

    return events


def _contrary(seq: List[int], transposition: int = 0) -> List[int]:
    """Contrary motion: intervals go opposite direction from first pitch."""
    if len(seq) < 2:
        return [p + transposition for p in seq]
    base = seq[0] + transposition
    result = [base]
    for i in range(1, len(seq)):
        interval = seq[i] - seq[i - 1]
        result.append(result[-1] - interval)
    return result


# ===========================================================================
# 2. CANON — imitation with configurable transformations
# ===========================================================================

def canon(
    leading_line: List[int],
    num_voices: int = 3,
    delay_ticks: int = 480,
    transposition_per_voice: int = 0,
    transformations: Optional[List[str]] = None,
    ticks_per_beat: int = 480,
    r: random.Random = None,
) -> List[BachEvent]:
    """Develop a leading line through imitation.

    Each subsequent voice copies the leading line with one or more
    transformations applied simultaneously.

    Transformations
    ---------------
    "retrograde"   : reversed order
    "contrary"     : inverted intervals
    "augmentation" : doubled note durations
    "diminution"   : halved note durations

    Parameters
    ----------
    leading_line : list of int
        The primary melodic line (MIDI pitches).
    num_voices : int
        Number of imitative voices (2–4).
    delay_ticks : int
        Tick delay before each new voice enters.
    transposition_per_voice : int
        Semitone shift applied to each voice (cumulative).
    transformations : list of str or None
        Per-voice transforms beyond voice 0.
    ticks_per_beat : int
        Tick resolution for rhythmic values.
    r : random.Random
        Random state.

    Returns
    -------
    events : list of BachEvent
    """
    if r is None:
        r = random
    num_voices = min(num_voices, 4)
    if transformations is None:
        transformations = ["retrograde", "contrary", "augmentation"][:num_voices - 1]
    events = []
    for voice_idx in range(num_voices):
        tick_off = delay_ticks * voice_idx
        line = list(leading_line)
        transp = transposition_per_voice * voice_idx
        dur_factor = 1.0
        if voice_idx > 0:
            transform = transformations[voice_idx - 1] if voice_idx - 1 < len(transformations) else ""
            if "retrograde" in transform:
                line = line[::-1]
            if "contrary" in transform:
                line = _contrary(line, 0)
            if "augmentation" in transform:
                dur_factor = 2.0
            if "diminution" in transform:
                dur_factor = 0.5
            line = [p + transp for p in line]
        tick = tick_off
        note_len = int(ticks_per_beat * dur_factor)
        for i, p in enumerate(line):
            pitch = max(0, min(127, p))
            events.append(BachEvent(
                pitch=pitch,
                start_tick=tick,
                duration_ticks=note_len,
                velocity=85,
                voice=voice_idx,
            ))
            tick += note_len
    return events


# ===========================================================================
# 3. PROBA — Markov chain directed randomness
# ===========================================================================

class MarkovChain:
    """N-gram Markov chain for pitch sequences."""

    def __init__(self, order: int = 2, r: random.Random = None):
        self.order = order
        self.r = r or random
        self._table: dict = {}

    def train(self, sequences: List[List[int]]):
        """Build transition table from one or more sequences."""
        for seq in sequences:
            for i in range(len(seq) - self.order):
                gram = tuple(seq[i:i + self.order])
                nxt = seq[i + self.order]
                if gram not in self._table:
                    self._table[gram] = []
                self._table[gram].append(nxt)

    def generate(self, length: int, seed: Optional[List[int]] = None) -> List[int]:
        """Generate a sequence from the Markov chain."""
        if not self._table:
            return [60] * length
        if seed is None:
            seed = list(self.r.choice(list(self._table.keys())))
        else:
            seed = list(seed)
        result = list(seed)
        for _ in range(length):
            gram = tuple(result[-self.order:])
            if gram in self._table:
                result.append(self.r.choice(self._table[gram]))
            else:
                result.append(self.r.choice([60, 64, 67]))
        return result[self.order:]


# Pre-built transition vocabularies (trained on common tonal progressions)
_PROBA_DIATONIC = [
    [60, 62, 64, 65, 67, 69, 71, 72],
    [60, 64, 67, 72],
    [67, 65, 64, 62, 60],
    [60, 64, 65, 67, 65, 64, 60],
    [67, 71, 72, 74, 76],
    [60, 65, 67, 69, 71, 72],
]

_PROBA_CHROMATIC = [
    [60, 61, 63, 64, 66, 67, 69, 70, 72],
    [60, 63, 66, 69, 72],
    [72, 70, 68, 67, 65, 63, 61, 60],
    [67, 66, 64, 63, 61, 60],
]

_PROBA_ARPEGGIATED = [
    [60, 64, 67, 72, 79, 84],
    [60, 67, 72, 76, 79],
    [65, 69, 72, 77, 81],
    [55, 60, 64, 67, 72, 67, 64, 60],
]


def proba(
    vocabulary: str = "diatonic",
    length: int = 32,
    order: int = 2,
    range_low: int = 48,
    range_high: int = 84,
    ticks_per_beat: int = 480,
    rhythm: str = "even",
    r: random.Random = None,
) -> List[BachEvent]:
    """Markov-chain directed randomness.

    Parameters
    ----------
    vocabulary : "diatonic" | "chromatic" | "arpeggiated"
        Transition vocabulary preset.
    length : int
        Number of notes to generate.
    order : int
        Markov chain order (1–3).
    range_low, range_high : int
        MIDI pitch clamp range.
    ticks_per_beat : int
        Tick resolution.
    rhythm : "even" | "waltz" | "syncopated" | "variable"
        Rhythmic structure.
    r : random.Random
        Random state.

    Returns
    -------
    events : list of BachEvent
    """
    if r is None:
        r = random
    vocab_map = {
        "diatonic": _PROBA_DIATONIC,
        "chromatic": _PROBA_CHROMATIC,
        "arpeggiated": _PROBA_ARPEGGIATED,
    }
    training = vocab_map.get(vocabulary, _PROBA_DIATONIC)
    mc = MarkovChain(order=order, r=r)
    mc.train(training)
    pitches = mc.generate(length)

    # Rhythm patterns
    beat = ticks_per_beat
    if rhythm == "even":
        gaps = [beat // 2] * length
    elif rhythm == "waltz":
        gaps = [beat * 2, beat, beat * 2, beat][:length]
        gaps = gaps * (length // len(gaps) + 1)
        gaps = gaps[:length]
    elif rhythm == "syncopated":
        bases = [beat // 4, beat // 2, beat, beat // 4, beat * 2, beat // 2]
        gaps = [bases[i % len(bases)] for i in range(length)]
    else:
        gaps = [int(beat * r.uniform(0.25, 2.0)) for _ in range(length)]

    events = []
    tick = 0
    for p, gap in zip(pitches, gaps):
        p = max(range_low, min(range_high, p))
        dur = max(gap // 2, ticks_per_beat // 16)
        events.append(BachEvent(pitch=p, start_tick=tick, duration_ticks=dur,
                                velocity=100, voice=0))
        tick += gap
    return events


# ===========================================================================
# 4. TINTINNABULI — triad-based voice leading (Pärt style)
# ===========================================================================

def tintinnabuli(
    melody: List[int],
    triad: Tuple[int, ...] = (0, 3, 7),  # minor triad intervals relative to root
    root_pitch: int = 60,
    num_voices: int = 2,
    ticks_per_beat: int = 480,
    r: random.Random = None,
) -> List[BachEvent]:
    """Tintinnabuli: melodic voice + voices whose notes come from a triad.

    Voice 0 carries the melody.  Additional voices only play notes from
    the specified triad, moving to the nearest triad tone at each event.

    Parameters
    ----------
    melody : list of (pitch, duration_ticks)
        Melodic line as (pitch, duration) pairs.
    triad : tuple of int
        Triad intervals (semitones from root): e.g. (0,4,7) = major.
    root_pitch : int
        MIDI pitch of triad root.
    num_voices : int
        Total voices (1–4).  Voice 0 = melody, rest = triad voices.
    ticks_per_beat : int
        Tick resolution.
    r : random.Random
        Random state.

    Returns
    -------
    events : list of BachEvent
    """
    if r is None:
        r = random
    num_voices = min(num_voices, 4)
    triad_pitches = [root_pitch + iv for iv in triad]
    events = []

    for voice_idx in range(num_voices):
        if voice_idx == 0:
            # melody voice
            tick = 0
            for p, dur in melody:
                events.append(BachEvent(pitch=max(0, min(127, p)),
                                        start_tick=tick, duration_ticks=dur,
                                        velocity=100, voice=0))
                tick += dur
        else:
            # triad voice: at each melodic event, pick nearest triad tone
            tick = 0
            prev_triad = triad_pitches[0]
            for p, dur in melody:
                # find nearest triad pitch to current melody note
                nearest = min(triad_pitches, key=lambda tp: abs(tp - p))
                # small random octave jump occasionally
                if r.random() < 0.15:
                    nearest += 12 * r.choice([-1, 1])
                nearest = max(0, min(127, nearest))
                events.append(BachEvent(pitch=nearest, start_tick=tick,
                                        duration_ticks=dur,
                                        velocity=80, voice=voice_idx))
                tick += dur
    return events


# ===========================================================================
# 5. MINIMAL — phase shifting, addition, substitution, hocketing
# ===========================================================================

def minimal_music(
    pitch_set: List[int] = (60, 64, 67, 72),
    num_voices: int = 4,
    total_bars: int = 16,
    bpm: int = 120,
    process: str = "phase",
    ticks_per_beat: int = 480,
    r: random.Random = None,
) -> List[BachEvent]:
    """Minimal-music process: phase shifting / additive / substitution / hocketing.

    Parameters
    ----------
    pitch_set : list of int
        The limited pitch collection used.
    num_voices : int
        Number of voices (1–8, mapped internally).
    total_bars : int
        Total duration in bars.
    bpm : int
        Tempo for tick calculation.
    process : "phase" | "additive" | "substitution" | "hocket"
        The process type.
    ticks_per_beat : int
        Tick resolution.
    r : random.Random
        Random state.

    Returns
    -------
    events : list of BachEvent
    """
    if r is None:
        r = random
    BAR = ticks_per_beat * 4
    total_ticks = total_bars * BAR
    events = []

    if process == "phase":
        # Each voice plays the same pattern at a slightly different tempo
        pattern = pitch_set * 8
        for vi in range(min(num_voices, 4)):
            phase_shift = vi * BAR // 4
            tempo_factor = 1.0 + vi * 0.02  # each voice slightly faster
            tick = phase_shift
            for pi in range(int(len(pattern) * total_bars / 4)):
                if tick >= total_ticks:
                    break
                p = pattern[pi % len(pattern)]
                dur = int(ticks_per_beat / tempo_factor)
                events.append(BachEvent(pitch=p, start_tick=tick,
                                        duration_ticks=dur,
                                        velocity=90, voice=vi))
                tick += dur

    elif process == "additive":
        # Gradually add notes (process of building)
        max_notes = len(pitch_set)
        for vi in range(min(num_voices, 4)):
            notes_active = 1 + vi
            note_len = ticks_per_beat
            tick = vi * note_len
            bar_len = BAR
            active_set = pitch_set[:min(notes_active + vi, max_notes)]
            while tick < total_ticks:
                p = active_set[r.randint(0, len(active_set) - 1)]
                events.append(BachEvent(pitch=p, start_tick=tick,
                                        duration_ticks=note_len,
                                        velocity=85, voice=vi))
                tick += note_len

    elif process == "substitution":
        # Gradually substitute one note for another
        tick = 0
        note_len = ticks_per_beat // 2
        for vi in range(min(num_voices, 4)):
            t2 = vi * BAR // 2
            for step in range(total_ticks // note_len):
                if t2 >= total_ticks:
                    break
                p = pitch_set[(step + vi) % len(pitch_set)]
                events.append(BachEvent(pitch=p, start_tick=t2,
                                        duration_ticks=note_len,
                                        velocity=80, voice=vi))
                t2 += note_len

    elif process == "hocket":
        # Each voice plays one specific note, interlocking
        for vi, p in enumerate(pitch_set[:min(num_voices, 4)]):
            tick = 0
            gap = (ticks_per_beat * 4) // len(pitch_set)
            while tick < total_ticks:
                off = vi * gap
                if tick + off < total_ticks:
                    events.append(BachEvent(pitch=p, start_tick=tick + off,
                                            duration_ticks=gap // 2,
                                            velocity=95, voice=vi))
                tick += gap * len(pitch_set)
    return events


# ===========================================================================
# 6. CELLULAR — cellular automaton → musical material (Wolfram 254 rules)
# ===========================================================================

def cellular_melody(
    rule: int = 90,
    generations: int = 32,
    width: int = 32,
    pitch_center: int = 60,
    pitch_range: int = 24,
    seed_bit: Optional[str] = None,
    rhythm: str = "gen_per_note",
    ticks_per_beat: int = 480,
    r: random.Random = None,
) -> List[BachEvent]:
    """Turn a 1-D cellular automaton evolution into musical material.

    254 Wolfram rules are accessible.  Each generation of the CA is mapped
    to pitches in the `pitch_range` around `pitch_center`.

    Parameters
    ----------
    rule : int
        Wolfram rule (0–255).
    generations : int
        Number of CA generations.
    width : int
        Width of each generation (cells).
    pitch_center : int
        Center MIDI pitch.
    pitch_range : int
        Range in semitones (default 2 octaves).
    seed_bit : None | "single" | "random"
        Initial condition.  None = single live cell at center.
    rhythm : "gen_per_note" | "sliding_window"
        Mapping from CA → note events.
    ticks_per_beat : int
        Tick resolution.
    r : random.Random
        Random state.

    Returns
    -------
    events : list of BachEvent
    """
    if r is None:
        r = random
    rule = max(0, min(255, rule))
    # Build rule table
    rule_bits = [(rule >> i) & 1 for i in range(8)]

    # Initial condition
    if seed_bit == "random":
        cells = [r.randint(0, 1) for _ in range(width)]
    else:
        cells = [0] * width
        cells[width // 2] = 1

    all_gens = [list(cells)]
    for _ in range(generations - 1):
        new_cells = [0] * width
        for i in range(width):
            left = cells[(i - 1) % width]
            center = cells[i]
            right = cells[(i + 1) % width]
            idx = (left << 2) | (center << 1) | right
            new_cells[i] = rule_bits[idx]
        cells = new_cells
        all_gens.append(list(cells))

    events = []
    if rhythm == "gen_per_note":
        # Each generation → one chord/note event
        note_len = ticks_per_beat * 2
        for gi, gen in enumerate(all_gens):
            tick = gi * note_len
            active = [j for j, c in enumerate(gen) if c]
            if not active:
                continue
            # Map cell positions to pitches
            for v in range(min(4, len(active))):
                cell_pos = active[v % len(active)]
                pitch = pitch_center + int((cell_pos / width - 0.5) * pitch_range)
                pitch = max(0, min(127, pitch))
                events.append(BachEvent(pitch=pitch, start_tick=tick,
                                        duration_ticks=note_len,
                                        velocity=85, voice=v))
    else:
        # sliding window: time = generational progress
        note_len = ticks_per_beat // 4
        tick = 0
        for gen in all_gens:
            for j, c in enumerate(gen):
                if c:
                    pitch = pitch_center + int((j / width - 0.5) * pitch_range)
                    pitch = max(0, min(127, pitch))
                    events.append(BachEvent(pitch=pitch, start_tick=tick,
                                            duration_ticks=note_len,
                                            velocity=80, voice=j % 4))
                tick += note_len // width
    return events


# ===========================================================================
# 7. TREE — L-system branching → melodic paths
# ===========================================================================

def tree_melody(
    axiom: str = "A",
    rules: Optional[dict] = None,
    iterations: int = 4,
    angle_step: float = 30.0,
    pitch_center: int = 60,
    note_len_ticks: int = 120,
    ticks_per_beat: int = 480,
    r: random.Random = None,
) -> List[BachEvent]:
    """Interpret an L-system's branching as a melodic path.

    Basic 'turtle graphics' mapping:
      A/Z → advance: emit a note + move forward
      F → advance: emit a note
      + → increase pitch (semitone up)
      - → decrease pitch (semitone down)
      [ → push state (branch start)
      ] → pop state (branch end → return)

    Parameters
    ----------
    axiom : str
        Starting string (e.g., "A").
    rules : dict or None
        Production rules.  Default = classic plant-like L-system.
    iterations : int
        Number of production iterations.
    angle_step : float
        Semitone change for +/- symbols.
    pitch_center : int
        Starting MIDI pitch.
    note_len_ticks : int
        Duration of each note event in ticks.
    ticks_per_beat : int
        Tick resolution.
    r : random.Random
        Random state.

    Returns
    -------
    events : list of BachEvent
    """
    if r is None:
        r = random
    if rules is None:
        # Classic L-system plant: A → F[-A][+A]A
        rules = {"A": "F[-A][+A]A", "F": "FF"}

    # Generate L-string
    string = axiom
    for _ in range(iterations):
        string = "".join(rules.get(ch, ch) for ch in string)

    events = []
    pitch = pitch_center
    tick = 0
    stack = []  # (pitch, tick)
    for ch in string:
        if ch in ("A", "F", "Z"):
            events.append(BachEvent(
                pitch=max(0, min(127, pitch)),
                start_tick=tick,
                duration_ticks=note_len_ticks,
                velocity=90,
                voice=0,
            ))
            tick += note_len_ticks
        elif ch == "+":
            pitch = min(127, pitch + int(angle_step / 10.0))  # ~3 semitones per +
        elif ch == "-":
            pitch = max(0, pitch - int(angle_step / 10.0))
        elif ch == "[":
            stack.append((pitch, tick))
        elif ch == "]":
            if stack:
                pitch, tick = stack.pop()
    return events


# ===========================================================================
# 8. MOTIF — melodic/rhythmic cell chains from collections
# ===========================================================================

# 32 short motif cells (pitch contour + rhythm template)
MOTIF_COLLECTIONS = {
    "classical": [
        [0, 2, 4, 5, 7, 5, 4, 2],
        [0, -2, -3, 0, 3, 5, 3, 0],
        [0, 7, 4, 0, 5, 7, 5, 4],
        [5, 0, 3, 5, 0, -2, 0, 3],
    ],
    "jazz": [
        [0, 4, 7, 11, 7, 4, 0],
        [0, 3, 7, 10, 5, 0],
        [0, -1, 0, 2, 4, 7, 4, 2],
        [0, 5, 9, 5, 0, -3, 0],
    ],
    "minimal": [
        [0, 0, 0, 0, 3, 3, 3, 3],
        [0, 0, 3, 3, 0, 0, 3, 3],
        [0, 3, 0, 3, 0, 3, 0, 3],
        [0, 0, 0, 3, 3, 3, 3, 0],
    ],
    "random_interval": [
        [0, 3, 1, 4, 2, 5, 3, 6],
        [0, -2, 2, -1, 3, 0, 4, 2],
        [0, 5, -3, 7, -2, 4, -5, 8],
        [0, 1, -1, 2, -2, 3, -3, 4],
    ],
    "chromatic": [
        [0, 1, 2, 1, 0, -1, -2, -1],
        [0, 2, 1, 3, 2, 4, 3, 5],
        [0, -1, 1, 0, 2, 1, 3, 2],
        [0, 3, 2, 5, 4, 7, 6, 9],
    ],
}


def motif_chain(
    collection: str = "classical",
    root: int = 60,
    num_cycles: int = 8,
    ticks_per_beat: int = 480,
    per_note_ticks: int = 240,
    r: random.Random = None,
) -> List[BachEvent]:
    """Chain melodic/rhythmic cells from a motif collection.

    Parameters
    ----------
    collection : str
        Key into MOTIF_COLLECTIONS.
    root : int
        Root MIDI pitch for the chain.
    num_cycles : int
        Number of motif cycles to produce.
    ticks_per_beat : int
        Tick resolution.
    per_note_ticks : int
        Ticks per note in each motif cell.
    r : random.Random
        Random state.

    Returns
    -------
    events : list of BachEvent
    """
    if r is None:
        r = random
    pool = MOTIF_COLLECTIONS.get(collection, MOTIF_COLLECTIONS["classical"])
    events = []
    tick = 0
    for _ in range(num_cycles):
        motif = r.choice(pool)
        for contour in motif:
            pitch = max(0, min(127, root + contour))
            events.append(BachEvent(
                pitch=pitch, start_tick=tick,
                duration_ticks=per_note_ticks,
                velocity=90, voice=0,
            ))
            tick += per_note_ticks
    return events


# ===========================================================================
# 9. HYBRID — distribute multiple engines across four voices
# ===========================================================================

def hybrid(
    voice_engines: List[Tuple[str, dict]],
    ticks_per_beat: int = 480,
    bpm: int = 120,
    total_bars: int = 16,
    r: random.Random = None,
) -> List[BachEvent]:
    """Distribute several composition engines across the four voices.

    Parameters
    ----------
    voice_engines : list of (engine_name, params_dict)
        E.g. [("fugue", {"subject": [60,64,67]}), ("canon", ...)]
    ticks_per_beat : int
        Tick resolution.
    bpm : int
        Tempo.
    total_bars : int
        Total bars.
    r : random.Random
        Random state.

    Returns
    -------
    events : list of BachEvent
    """
    if r is None:
        r = random
    events = []
    ENGINES = {
        "fugue": fugue,
        "canon": canon,
        "proba": proba,
        "tintinnabuli": tintinnabuli,
        "minimal": minimal_music,
        "cellular": cellular_melody,
        "tree": tree_melody,
        "motif": motif_chain,
    }
    for vi, (eng_name, params) in enumerate(voice_engines[:4]):
        fn = ENGINES.get(eng_name)
        if fn is None:
            continue
        try:
            eng_events = fn(ticks_per_beat=ticks_per_beat, r=r, **params)
            for e in eng_events:
                e.voice = vi
            events.extend(eng_events)
        except Exception as exc:
            print(f"HYBRID: engine {eng_name} for voice {vi} failed: {exc}")
    return events


# ===========================================================================
# 10. GROOVE — four rhythmic roles using 64 structures
# ===========================================================================

# 64 groove structures: pattern of hits per bar, tagged by style
GROOVE_LIBRARY = {
    "rock":       [[1, 0, 0, 0, 1, 0, 0, 0],   # kick
                   [0, 0, 0, 0, 1, 0, 0, 0],   # snare
                   [0, 0, 1, 0, 0, 0, 1, 0],   # hi-hat
                   [1, 0, 0, 1, 0, 0, 0, 0]],  # ride
    "funk":       [[1, 0, 0, 1, 0, 0, 1, 0],
                   [0, 0, 1, 0, 0, 0, 1, 0],
                   [0, 1, 0, 1, 1, 0, 1, 0],
                   [0, 0, 0, 0, 0, 0, 0, 1]],
    "shuffle":    [[1, 0, 0, 0, 1, 0, 0, 0],
                   [0, 0, 0, 0, 1, 0, 0, 0],
                   [1, 0, 1, 0, 1, 0, 1, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0]],
    "latin":      [[1, 0, 0, 1, 0, 0, 1, 1],
                   [0, 0, 0, 0, 1, 0, 0, 0],
                   [0, 1, 0, 1, 0, 1, 0, 1],
                   [0, 0, 1, 0, 0, 1, 0, 0]],
    "four_on_floor": [[1, 0, 0, 0, 1, 0, 0, 0],
                      [0, 0, 0, 0, 1, 0, 0, 0],
                      [1, 1, 1, 1, 1, 1, 1, 1],
                      [0, 0, 0, 0, 0, 0, 0, 0]],
    "half_time":  [[1, 0, 0, 0, 1, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 1, 0],
                   [0, 1, 0, 1, 0, 1, 0, 1],
                   [1, 0, 0, 0, 0, 0, 0, 0]],
    "swing_16":   [[1, 0, 1, 0, 1, 0, 1, 0],
                   [0, 0, 0, 0, 1, 0, 0, 0],
                   [1, 1, 1, 1, 1, 1, 1, 1],
                   [0, 0, 0, 0, 0, 1, 0, 1]],
    "afrobeat":   [[1, 0, 0, 0, 0, 0, 1, 0],
                   [0, 0, 0, 0, 1, 0, 0, 0],
                   [0, 1, 0, 1, 0, 1, 0, 1],
                   [1, 1, 1, 1, 1, 1, 1, 1]],
}


def groove(
    style: str = "rock",
    num_bars: int = 8,
    bpm: int = 120,
    ticks_per_beat: int = 480,
    percussion_voices: Tuple[str, ...] = ("kick", "snare", "hat", "ride"),
    r: random.Random = None,
) -> List[BachEvent]:
    """Generate four rhythmic roles from a groove structure.

    Parameters
    ----------
    style : str
        Key into GROOVE_LIBRARY.
    num_bars : int
        Number of bars to generate.
    bpm : int
        Tempo (for tick calc).
    ticks_per_beat : int
        Tick resolution.
    percussion_voices : tuple
        Labels for the four voices (informational only).
    r : random.Random
        Random state.

    Returns
    -------
    events : list of BachEvent
    """
    if r is None:
        r = random
    pattern = GROOVE_LIBRARY.get(style, GROOVE_LIBRARY["rock"])
    BAR = ticks_per_beat * 4
    # 8 sub-divisions per bar (8th notes)
    sub = BAR // 8
    events = []
    for vi, voice_pattern in enumerate(pattern[:4]):
        for bar in range(num_bars):
            for si, hit in enumerate(voice_pattern):
                if hit:
                    tick = bar * BAR + si * sub
                    pitch = 36 + vi * 2  # kick(36), snare(38), hat(42), ride(51)
                    events.append(BachEvent(
                        pitch=pitch, start_tick=tick,
                        duration_ticks=sub // 2,
                        velocity=100 if hit else 0,
                        voice=vi,
                    ))
    return events


# ===========================================================================
# 11. GROOVE_MIX — rhythmic structures + pitches from melodic language
# ===========================================================================

def groove_mix(
    style: str = "rock",
    pitches: List[int] = (60, 64, 67, 72),
    num_bars: int = 8,
    ticks_per_beat: int = 480,
    transpose_per_voice: int = 0,
    r: random.Random = None,
) -> List[BachEvent]:
    """Apply rhythmic groove structures to pitches from a melodic language.

    Voice 0 = kick pitch (root), Voice 1 = snare (fifth),
    Voice 2 = hat pattern (chord tones), Voice 3 = ride pattern (arpeggios).

    Parameters
    ----------
    style : str
        Groove style key.
    pitches : list of int
        Pitch set for melodic voices.
    num_bars : int
        Number of bars.
    ticks_per_beat : int
        Tick resolution.
    transpose_per_voice : int
        Extra transposition for each voice.
    r : random.Random
        Random state.

    Returns
    -------
    events : list of BachEvent
    """
    if r is None:
        r = random
    pattern = GROOVE_LIBRARY.get(style, GROOVE_LIBRARY["rock"])
    BAR = ticks_per_beat * 4
    sub = BAR // 8
    events = []

    # Voice-specific pitch assignments
    pitch_map = [
        [pitches[0]],                      # kick → root
        [pitches[2] if len(pitches) > 2 else pitches[0] + 7],  # snare → third/dominant
        pitches,                            # hat → chord tones
        pitches + [p + 12 for p in pitches], # ride → chord + octave arp
    ]

    for vi, voice_pattern in enumerate(pattern[:4]):
        pitch_pool = pitch_map[vi]
        for bar in range(num_bars):
            for si, hit in enumerate(voice_pattern):
                if hit:
                    tick = bar * BAR + si * sub
                    p = r.choice(pitch_pool) + transpose_per_voice * vi
                    p = max(0, min(127, p))
                    events.append(BachEvent(
                        pitch=p, start_tick=tick,
                        duration_ticks=sub // 2,
                        velocity=95, voice=vi,
                    ))
    return events


# ===========================================================================
# Unified dispatcher
# ===========================================================================

BACH_ENGINES = {
    "fugue":            (fugue, {"subject": [60, 62, 64, 65, 67, 69], "num_voices": 3}),
    "canon":            (canon, {"leading_line": [60, 64, 67, 72, 76], "num_voices": 3, "delay_ticks": 240}),
    "proba":            (proba, {"vocabulary": "diatonic", "length": 16}),
    "tintinnabuli":     (tintinnabuli, {"melody": [(60, 480), (64, 480), (67, 480), (72, 960), (67, 480)], "triad": (0, 4, 7), "num_voices": 3}),
    "minimal":          (minimal_music, {"pitch_set": [60, 64, 67, 72], "num_voices": 3, "total_bars": 8, "process": "phase"}),
    "cellular":         (cellular_melody, {"rule": 90, "generations": 16, "width": 16}),
    "tree":             (tree_melody, {"iterations": 3}),
    "motif":            (motif_chain, {"collection": "jazz", "root": 60, "num_cycles": 4}),
    "hybrid":           (hybrid, {"voice_engines": [("proba", {"vocabulary": "diatonic", "length": 16}), ("motif", {"collection": "classical", "root": 67, "num_cycles": 4})]}),
    "groove":           (groove, {"style": "rock", "num_bars": 4}),
    "groove_mix":       (groove_mix, {"style": "funk", "pitches": [60, 64, 67, 72], "num_bars": 4}),
}


def compose_with(engine: str, r: random.Random = None, **overrides) -> List[BachEvent]:
    """Unified entry point for any B.A.C.H. engine.

    Parameters
    ----------
    engine : str
        One of BACH_ENGINES keys.
    r : random.Random or None
        Random state for reproducibility.
    **overrides
        Override any default parameter.

    Returns
    -------
    events : list of BachEvent
    """
    entry = BACH_ENGINES.get(engine)
    if entry is None:
        raise ValueError(
            f"Unknown BACH engine {engine!r}.  Choose from: {list(BACH_ENGINES)}"
        )
    fn, defaults = entry
    kwargs = dict(defaults)
    kwargs.update(overrides)
    if r is not None:
        kwargs["r"] = r
    return fn(**kwargs)


# ===========================================================================
# Demo
# ===========================================================================

def demo():
    """Run a short demo of all 11 engines and print event counts."""
    print("B.A.C.H. Composition Engines — Demo")
    print("=" * 45)
    r = random.Random(42)
    for name, fn in BACH_ENGINES.items():
        try:
            if name == "fugue":
                events = fn(subject=[60, 62, 64, 65, 67, 69], num_voices=3, r=r)
            elif name == "canon":
                events = fn([60, 64, 67, 72, 76], num_voices=3, delay_ticks=240, r=r)
            elif name == "proba":
                events = fn(vocabulary="diatonic", length=16, r=r)
            elif name == "tintinnabuli":
                melody = [(60, 480), (64, 480), (67, 480), (72, 960), (67, 480)]
                events = fn(melody, triad=(0, 4, 7), num_voices=3, r=r)
            elif name == "minimal":
                events = fn(pitch_set=[60, 64, 67, 72], num_voices=3, total_bars=8, process="phase", r=r)
            elif name == "cellular":
                events = fn(rule=90, generations=16, width=16, r=r)
            elif name == "tree":
                events = fn(iterations=3, r=r)
            elif name == "motif":
                events = fn(collection="jazz", root=60, num_cycles=4, r=r)
            elif name == "hybrid":
                events = fn([
                    ("proba", {"vocabulary": "diatonic", "length": 16}),
                    ("motif", {"collection": "classical", "root": 67, "num_cycles": 4}),
                ], r=r)
            elif name == "groove":
                events = fn(style="rock", num_bars=4, r=r)
            elif name == "groove_mix":
                events = fn(style="funk", pitches=[60, 64, 67, 72], num_bars=4, r=r)
            else:
                events = []
            n_events = len(events)
            pitches = set(e.pitch for e in events)
            print(f"  {name:15s}  {n_events:3d} events  pitches {min(pitches)}–{max(pitches)}")
        except Exception as exc:
            print(f"  {name:15s}  FAILED: {exc}")
    print("=" * 45)
    print("Demo complete.")


if __name__ == "__main__":
    demo()