# Narmour Implication-Realization Melodic Composition (NIRMC)

**Method ID**: 081
**Paradigm**: Rules-Based
**Layer**: concrete (emits note events into UnitMatrix cells; feeds `generators/`)
**Candidate code path**: `generators/narmour_ir.py`
**Acronym**: NIRMC

## One-line description
Generates melody by treating every interval as an *implication* — each successor either realizes the expectation (same registral direction; similar size if small, gap-fill if large) or denies it (surprise → tension → a compensating implication) — with the realization/denial budget per section governing macro-form.

## Extended math

Let a melody be a sequence of pitches $p_0, p_1, \dots, p_N$ (integers, MIDI or semitones). The **signed interval** at step $t$ is

$$s_t = p_{t+1} - p_t.$$

Narmour's bottom-up implication of the pair $(s_{t-1}, s_t)$ is a probability mass over the next interval $s_{t+1}$, governed by two Gestalt principles:

**Registral direction (R).** The direction of $s_t$ implies the direction of $s_{t+1}$:
$$\mathrm{sign}(s_{t+1}) = \mathrm{sign}(s_t) \quad \text{(continue)},\quad\text{with } s_t = 0 \Rightarrow \text{lateral (duplication, D)}.$$

**Intervallic motion (I).** The size of $s_t$ implies the size of $s_{t+1}$:
$$|s_t| \le 6 \;\Rightarrow\; |s_{t+1}| \approx |s_t| \quad(\text{similar, within } \pm 3),$$
$$|s_t| > 6 \;\Rightarrow\; |s_{t+1}| < |s_t| \quad(\text{gap-fill: large leaps return toward the abandoned register}).$$

Combining R and I gives five **archetypes** (realized structures), indexed by direction $d \in \{-1,0,+1\}$ and a size relation $\rho \in \{\text{same},\text{similar},\text{smaller}\}$:

| Archetype | Direction | Size relation | Definition |
|---|---|---|---|
| P (Process) | same | similar | $\mathrm{sign}(s_{t+1})=\mathrm{sign}(s_t)$, $|s_{t+1}| \approx |s_t|$ |
| IP (Intervallic Process) | same | same | $s_{t+1} = s_t$ |
| D (Duplication) | lateral | — | $s_t = 0$ |
| R (Reversal) | opposite | similar | $\mathrm{sign}(s_{t+1})=-\mathrm{sign}(s_t)$, $|s_{t+1}| \approx |s_t|$ |
| IR (Intervallic Reversal) | opposite | same | $s_{t+1} = -s_t$ |

A **realization** is any successor whose direction/size is consistent with the archetype table given the current interval; a **denial** violates R and/or I. The generator maintains a **realization rate** $r \in [0,1]$: with probability $r$ it draws a realized successor, with probability $1-r$ a denied successor.

**Implicative chain.** Because a denial *itself* implies a compensating continuation, the process is a Markov chain over $(p_{t-1}, p_t, \text{state})$ where the state records the *pending* implication — specifically, a large leap sets a pending gap-fill target $g$ (the register of the pre-leap note). This gives the generator longer-than-order-1 memory without a hand-tuned context window:

$$g_t = \begin{cases} p_{t-1} & \text{if } |s_t| > 6 \text{ (register to be refilled)} \\ g_{t-1} & \text{otherwise} \end{cases}$$

The gap-fill implication is resolved when a successor lands within a small tolerance of $g_t$ (typically a scale step), after which $g$ is cleared. Nested implicative chains correspond to filling at multiple hierarchical levels: a macro-implication (section-level registral trajectory) is elaborated by micro-implications (local diminutions), mirroring Narmour's hierarchical (top-down) system.

**Cost.** The decision per note is $\mathcal{O}(1)$ (evaluate R and I against the current interval, check the pending gap-fill, draw a target from the chord-tone pool). Total generation cost is $\mathcal{O}(N)$ for $N$ notes. Deterministic per seed.

## Python implementation sketch

```python
"""Narmour Implication-Realization melodic generator (Method 081, NIRMC)."""
import random

SMALL = 6        # semitones: intervals <= SMALL are "small" (imply similar-size)
TOL = 3          # "similar size" tolerance (Narmour's +/- 3 semitones)

def implied_successor(prev, curr, chord_tones, realization_rate, rng):
    """Return the next pitch, the archetype used, and whether it realized/denied."""
    s = curr - prev                      # signed interval
    realized = rng.random() < realization_rate
    direction = 0 if s == 0 else (1 if s > 0 else -1)

    if realized:
        if s == 0:                        # D: duplication (lateral)
            nxt, arch = curr, "D"
        else:
            if abs(s) <= SMALL:           # small -> similar size
                size = abs(s) + rng.randint(-TOL, TOL)
                if rng.random() < 0.5:    # R (reversal, opposite) vs P (process, same)
                    nxt, arch = curr - direction * size, "R"
                else:
                    nxt, arch = curr + direction * size, "P"
            else:                         # large -> gap-fill (smaller, opposite)
                size = max(1, abs(s) - rng.randint(1, abs(s) - 1))
                nxt, arch = curr - direction * size, "R"
    else:                                  # denial: violate direction and/or size
        # canonical denial: leap further in the same direction (denies I: large->small)
        if s == 0:
            nxt, arch = curr + rng.choice([-1, 1]) * rng.randint(7, 12), "denial"
        else:
            size = rng.randint(SMALL + 1, 12)   # large (violates gap-fill expectation)
            nxt, arch = curr + direction * size, "denial"

    return snap_to_chord(nxt, chord_tones, rng), arch

def snap_to_chord(pitch, chord_tones, rng):
    """Pull the note toward the nearest chord tone (harmonic anchor); keep non-chord
    on denials for dissonance. Optional: skip snapping when arch == 'denial'."""
    if not chord_tones:
        return pitch
    # project pitch class onto nearest chord tone in the same octave neighborhood
    candidates = []
    for root in chord_tones:
        for octv in (-1, 0, 1):
            candidates.append(root + 12 * octv)
    return min(candidates, key=lambda c: abs(c - pitch))

def compose_melody(seed_pitch, n_notes, chord_tones, realization_rate=0.7, seed=0):
    rng = random.Random(seed)
    line = [seed_pitch, seed_pitch + rng.choice([-2, -1, 1, 2])]  # small opening interval
    for _ in range(n_notes - 2):
        nxt, arch = implied_successor(line[-2], line[-1], chord_tones, realization_rate, rng)
        line.append(nxt)
    return line
```

**Musicom integration** (engine authors the MIDI; real imports per AGENTS.md):
```python
# from structures import MusicUnit
# from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit
# composer = UnitMatrixComposer(bpm=100, ticks_per_beat=480, beats_per_bar=4)
# composer.create_matrix(num_voices=V, num_sections=S)
# for v in range(V): composer.add_voice(f"voice{v}", ...)
# for s in range(S):
#     rr, chords = section_specs[s]          # realization rate + chord-tone pool per section
#     for v in range(V):
#         line = compose_melody(seed_v[v], notes_per_section, chords, realization_rate=rr, seed=hash((s,v)))
#         for i, pitch in enumerate(line):
#             composer.fill_voice_section(f"voice{v}", s, create_note_unit(pitch, dur, tick=i))
# ok, msg = composer.validate()   # MUST be True before to_midi (per AGENTS.md)
```

## References
- Narmour, E. (1990). *The Analysis and Cognition of Basic Melodic Structures: The Implication-Realization Model*. University of Chicago Press.
- Narmour, E. (1992). *The Analysis and Cognition of Melodic Complexity*. University of Chicago Press.
- Meyer, L. B. (1956). *Emotion and Meaning in Music*. University of Chicago Press.
- Meyer, L. B. (1973). *Explaining Music*. University of California Press.
- Krumhansl, C. L. (1995). "Music psychology and music theory: problems and prospects." *Music Theory Spectrum* 17(1), 53–80.
- Schellenberg, E. G. (1996/1997). "Expectancy in melody: tests of the implication-realization model." *Journal of Experimental Psychology: Human Perception and Performance* 22/23.
- Cuddy, L. L., & Lunney, C. A. (1995). "Expectancies generated by melodic intervals: perceptual judgments of melodic continuity." *Music Perception* 12(4), 451–462.
