# Method 116 — Petri Net Composition (PNC)

- **ID**: 116
- **Acronym**: PNC
- **Paradigm**: Rules-Based
- **Layer**: concrete
- **Candidate code path**: `generators/petri_net_composition.py`

---

## Overview

Petri Net Composition (PNC) uses P-timed Petri nets with probabilistic arc weights as the generative engine for symbolic music. A Petri net is a directed bipartite graph of **places** (holding music objects) and **transitions** (carrying music operators). Tokens in places enable transitions; firing a transition consumes input tokens, applies a music operator, and deposits output tokens. The net execution trace *is* the composition.

## Formal Definition

A **P-timed Music Petri Net** is a 9-tuple:

$$\mathbf{PN} = (P, T, A, c, m_0, w_t, w_p, \tau, \mathcal{O})$$

where:

- $P$ = finite set of **places**, each associated with a **music object** $o \in \mathcal{O}$
- $T$ = finite set of **transitions**, each carrying a **music operator** $f: \mathcal{O}^* \to \mathcal{O}^*$
- $A \subseteq (P \times T) \cup (T \times P)$ = finite set of directed **arcs**
- $c: P \to \mathbb{N}$ = **capacity** of each place
- $m_0: P \to \mathbb{N}_0$ = **initial marking** (token count per place), with $m_0(p) \leq c(p)$
- $w_t: A \to \mathbb{N}$ = **token arc weight** (how many tokens consumed/produced per firing)
- $w_p: A \to \mathbb{N}_0$ = **probabilistic arc weight** (controls non-deterministic choice among enabled transitions)
- $\tau: P \to \mathbb{R}^+_0$ = **P-timing** (duration in ticks tokens are blocked in a place)
- $\mathcal{O}$ = set of **music objects** (notes, chords, motifs, phrases, silence)

### Firing Rule

A transition $t \in T$ is **enabled** at marking $m$ iff:

1. $\forall p \in \text{IN}(t): m(p) \geq w_t(p,t)$
2. $\forall p \in \text{OUT}(t): c(p) - m(p) \geq w_t(t,p)$

where $\text{IN}(t) = \{p \in P \mid (p,t) \in A\}$ and $\text{OUT}(t) = \{p \in P \mid (t,p) \in A\}$.

When multiple transitions are enabled, the firing probability of $t$ is:

$$P(t \mid m) = \frac{\sum_{\text{arcs from } m\text{-enabled places to } t} w_p(\text{arc})}{\sum_{t' \in \text{Enabled}(m)} \sum_{\text{arcs to } t'} w_p(\text{arc})}$$

When $t$ fires, it transforms the marking $m \to m'$:

$$m'(p) =
\begin{cases}
m(p) - w_t(p,t) & p \in \text{IN}(t) \setminus \text{OUT}(t) \\
m(p) + w_t(t,p) & p \in \text{OUT}(t) \setminus \text{IN}(t) \\
m(p) - w_t(p,t) + w_t(t,p) & p \in \text{IN}(t) \cap \text{OUT}(t) \\
m(p) & \text{otherwise}
\end{cases}$$

Additionally, the transition's music operator $f_t$ is applied to the music objects from the input places, producing the output music objects placed in $\text{OUT}(t)$.

### Timing Constraint

A token arriving at place $p$ at time $t_0$ is blocked for $\tau(p)$ ticks and can only enable outgoing transitions at time $t \geq t_0 + \tau(p)$. During the blocked interval the place's music object is "playing" — its pitch/duration content is emitted as `MusicEvent` structures.

---

## Music Operators

| Operator | Symbol | Effect |
|---|---|---|
| Identity | $\text{id}$ | Pass through unchanged |
| Transposition | $T_n$ | Shift all pitches by $n$ semitones |
| Inversion | $I$ | Invert pitch intervals: $p \mapsto -p \pmod{12}$ |
| Retrogradation | $R$ | Reverse the temporal order of events |
| Concatenation | $\text{seq}$ | Sequence objects left-to-right |
| Fusion | $\text{fus}$ | Superimpose pitch sets into a chord |
| Split | $\text{sp}$ | Decompose into $k$ constituent objects |
| Time-scale | $\text{sc}_\alpha$ | Multiply all $\tau$ by factor $\alpha$ |
| Silence | $\emptyset$ | Replace object with rest of equal duration |
| Null | $\cdot$ | No operator (structural transition only) |

---

## Python Implementation Sketch

```python
import numpy as np
from dataclasses import dataclass, field
from typing import Any
from structures import MusicEvent, MusicUnit
from workflows.unitmatrix_composer import UnitMatrixComposer

# --- Music Object ---
@dataclass
class MusicObject:
    """A musical entity attached to a Petri net place."""
    pitches: list[int]       # MIDI pitches (single note, chord, or empty for rest)
    duration_ticks: int      # = tau(p) in the formal model
    velocity: int = 64

    def to_events(self, start_tick: int) -> list[MusicEvent]:
        return [MusicEvent(p, self.velocity, start_tick, start_tick + self.duration_ticks)
                for p in self.pitches]

# --- Petri Net Data Structures ---
@dataclass
class Token:
    place_id: int
    arrival_tick: int
    released: bool = False

@dataclass
class Place:
    object: MusicObject
    capacity: int = 1
    timing_ticks: int = 480  # tau(p)
    tokens: list[Token] = field(default_factory=list)

@dataclass
class Transition:
    operator: str              # "id" | "Tn" | "I" | "R" | "seq" | "fus" | ...
    operator_param: Any = None

@dataclass
class Arc:
    source_id: int             # place index or transition index
    target_id: int
    token_weight: int = 1
    prob_weight: int = 1

# --- Simulation Engine ---
class PetriNetComposer:
    def __init__(self, places: list[Place], transitions: list[Transition],
                 arcs: list[Arc], initial_marking: list[list[Token]],
                 bpm: int = 120, ticks_per_beat: int = 480):
        self.places = places
        self.transitions = transitions
        self.arcs = arcs
        self.marking = initial_marking  # list of token lists per place
        self.tick = 0
        self.events: list[MusicEvent] = []       # emitted event list
        self.composer = UnitMatrixComposer(bpm=bpm, ticks_per_beat=ticks_per_beat)

    def _arcs_to(self, node_id: int, is_place: bool) -> list[Arc]:
        """Get all arcs incoming to node_id."""
        if is_place:
            return [a for a in self.arcs if not isinstance(a.source_id, bool)
                    and a.target_id == node_id  # arcs from transitions to this place
                    and not hasattr(self.transitions[a.source_id] if a.source_id < len(self.transitions) else None, 'dummy')]  # simplified
        # Simplified: arcs from places to this transition
        return [a for a in self.arcs if a.target_id == node_id]

    def _arcs_from(self, node_id: int, is_place: bool) -> list[Arc]:
        if is_place:
            return [a for a in self.arcs if a.source_id == node_id
                    and not isinstance(a.target_id, bool)]
        return [a for a in self.arcs if a.source_id == node_id]

    def _enabled_transitions(self) -> list[int]:
        enabled = []
        for t_idx in range(len(self.transitions)):
            in_arcs = [a for a in self.arcs if isinstance(a.source_id, int)
                       and not isinstance(self.places[a.source_id] if a.source_id < len(self.places) else None, Transition)
                       and a.target_id == t_idx]  # arcs from places to t
            satisfied = True
            for a in in_arcs:
                p = self.places[a.source_id]
                # Check tokens available (released)
                released_tokens = sum(1 for tok in p.tokens
                                      if tok.released and self.tick >= tok.arrival_tick + p.timing_ticks)
                if released_tokens < a.token_weight:
                    satisfied = False
                    break
            # Check output place capacity
            out_arcs = [a for a in self.arcs if a.source_id == t_idx]
            for a in out_arcs:
                p = self.places[a.target_id]
                if len(p.tokens) + a.token_weight > p.capacity:
                    satisfied = False
                    break
            if satisfied:
                enabled.append(t_idx)
        return enabled

    def _select_transition(self, enabled: list[int]) -> int | None:
        if not enabled:
            return None
        if len(enabled) == 1:
            return enabled[0]
        # Probabilistic selection via arc weights
        weights = []
        for t_idx in enabled:
            in_arcs = [a for a in self.arcs if a.target_id == t_idx
                       and isinstance(a.source_id, int)]
            total_w = sum(a.prob_weight for a in in_arcs)
            weights.append(max(total_w, 1))
        total = sum(weights)
        r = np.random.randint(0, total)
        cum = 0
        for i, t_idx in enumerate(enabled):
            cum += weights[i]
            if r < cum:
                return t_idx
        return enabled[-1]

    def _fire(self, t_idx: int):
        t = self.transitions[t_idx]
        in_arcs = [a for a in self.arcs if a.target_id == t_idx
                   and isinstance(a.source_id, int)]
        out_arcs = [a for a in self.arcs if a.source_id == t_idx]

        # Collect input music objects
        input_objects = []
        for a in in_arcs:
            p = self.places[a.source_id]
            # Consume tokens
            consumed = 0
            for tok in p.tokens:
                if tok.released and self.tick >= tok.arrival_tick + p.timing_ticks:
                    p.tokens.remove(tok)
                    consumed += 1
                    if consumed >= a.token_weight:
                        break
            if consumed > 0:
                input_objects.append(p.object)

        # Apply operator
        output_objects = self._apply_operator(t, input_objects)

        # Deposit output tokens
        for a in out_arcs:
            p = self.places[a.target_id]
            for _ in range(a.token_weight):
                new_tok = Token(place_id=a.target_id, arrival_tick=self.tick, released=True)
                p.tokens.append(new_tok)
            # Emit events
            for obj in output_objects:
                for ev in obj.to_events(self.tick):
                    self.events.append(ev)

    def _apply_operator(self, t: Transition, objs: list[MusicObject]) -> list[MusicObject]:
        if t.operator == "id" or not objs:
            return objs
        elif t.operator == "Tn":
            n = t.operator_param
            return [MusicObject(
                pitches=[(p + n) % 128 for p in obj.pitches],
                duration_ticks=obj.duration_ticks,
                velocity=obj.velocity
            ) for obj in objs]
        elif t.operator == "fus":
            # Superimpose all pitches
            all_pitches = []
            max_dur = 0
            for obj in objs:
                all_pitches.extend(obj.pitches)
                max_dur = max(max_dur, obj.duration_ticks)
            return [MusicObject(
                pitches=sorted(set(p for p in all_pitches if 0 <= p < 128)),
                duration_ticks=max_dur,
                velocity=objs[0].velocity if objs else 64
            )]
        elif t.operator == "seq":
            # Concatenation: return all with cumulative timing captured elsewhere
            return objs
        else:
            return objs

    def simulate(self, max_ticks: int = 1920 * 64):
        """Run Petri net simulation."""
        while self.tick < max_ticks:
            enabled = self._enabled_transitions()
            t_idx = self._select_transition(enabled)
            if t_idx is None:
                # Deadlock — advance clock to next token release
                next_release = float('inf')
                for p in self.places:
                    for tok in p.tokens:
                        release_time = tok.arrival_tick + p.timing_ticks
                        if release_time > self.tick:
                            next_release = min(next_release, release_time)
                if next_release == float('inf'):
                    break
                self.tick = next_release
                continue
            self._fire(t_idx)
            self.tick += 1  # minimal advance; real implementation advances to next transition

        return self.events

    def to_unit_matrix(self, voices: list[str], sections: list[str], section_len_ticks: int) -> str:
        """Layout events into UnitMatrix and export MIDI."""
        # Group events by tick range per (voice, section) cell
        # Simplified: distribute events evenly across voices by token lineage
        voice_events = [[] for _ in voices]
        for ev in self.events:
            voice_idx = hash(str(ev)) % len(voices)
            voice_events[voice_idx].append(ev)

        comp = self.composer
        comp.create_matrix(len(voices), len(sections))
        for v, name in enumerate(voices):
            comp.add_voice(name, program=0, channel=v)
        for s, name in enumerate(sections):
            comp.add_section(name, bars=section_len_ticks // 1920)

        for v_idx in range(len(voices)):
            for s_idx in range(len(sections)):
                cell_start = s_idx * section_len_ticks
                cell_end = cell_start + section_len_ticks
                cell_events = [ev for ev in voice_events[v_idx]
                               if cell_start <= ev.start_tick < cell_end]
                # Pad to section length
                if cell_events:
                    comp.fill_voice_section(
                        voices[v_idx], sections[s_idx],
                        MusicUnit(events=cell_events, duration_ticks=section_len_ticks)
                    )

        ok, msg = comp.validate()
        assert ok, f"Zero-drift violation: {msg}"
        out_path = "/tmp/pnc_composition.mid"
        comp.to_midi(out_path)
        return out_path
```

---

## References

- Haus, G. & Rodriguez, A. (1988). "Music description and processing by Petri nets." *Advances in Petri Nets 1988*, LNCS 340, pp. 175–199, Springer.
- Haus, G. & Rodriguez, A. (1993). "Formal music representation; a case study: the model of Ravel's Bolero by Petri nets." In *Music Processing*, G. Haus (Ed.), Computer Music and Digital Audio Series, pp. 165–232, A-R Editions, Madison.
- Baratè, A., Haus, G. & Ludovico, L.A. (2007). "Petri Nets Applicability to Music Analysis and Composition." *Proceedings of the International Computer Music Conference (ICMC 2007)*, Copenhagen, pp. 97–100.
- Baratè, A., Haus, G. & Ludovico, L.A. (2014). "Real-time Music Composition through P-timed Petri Nets." *Proceedings of ICMC-SMC 2014*, Athens, pp. 408–415.
- Baratè, A. (2008). "Music Description and Processing: An Approach Based on Petri Nets and XML." In *Petri Net, Theory and Applications*, V. Kordic (Ed.), IntechOpen.
- Haus, G. & Sametti, A. (1991). "Scoresynth: a system for the synthesis of music scores based on Petri nets and a music algebra." *Computer* 24(7), pp. 56–60.
- Degli Antoni, G. & Haus, G. (1983). "Music and causality." *Proc. 1982 ICMC*, pp. 279–296.
- Petri, C. A. (1962). "Kommunikation mit Automaten." PhD thesis, Technical University of Darmstadt. — The original Petri net formalism.
- Murata, T. (1989). "Petri nets: Properties, analysis and applications." *Proceedings of the IEEE* 77(4), 541–580. — The comprehensive survey.