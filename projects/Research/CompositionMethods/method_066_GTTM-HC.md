# Method 066 — Generative Theory of Tonal Music Hierarchical Composition (GTTM-HC)

**Paradigm**: Rules-Based (Deterministic) · **ID**: 066 · **Acronym**: GTTM-HC
**Tonal Gravity**: Strict (Tonal Hierarchy) · **Metric Binding**: Grid-Locked · **Memory Depth**: Macro / Tree · **Time Complexity**: $\mathcal{O}(N \log N)$

## One-line
Inverts Lerdahl & Jackendoff's *A Generative Theory of Tonal Music* (1983) from an analysis theory into a generation method: compose the deep prolongational structure first (tonic triad + structural line), then recursively elaborate with diminutions governed by well-formedness and preference rules — the grouping tree is the macro-form, the metrical grid is the rhythm, and the prolongational branch types are the harmony and tension.

---

## 1. Source and lineage

The Generative Theory of Tonal Music (GTTM) is the foundational cognitive-musicology account of how an experienced listener unconsciously parses tonal music, developed by music theorist **Fred Lerdahl** and linguist **Ray Jackendoff** (*A Generative Theory of Tonal Music*, MIT Press, 1983). It was motivated by Leonard Bernstein's 1973 Charles Eliot Norton Lectures at Harvard, where Bernstein called for a "musical grammar" in the spirit of Chomsky's transformational-generative linguistics.

GTTM posits four interacting hierarchical systems, each defined by three rule classes:

| System | What it models | Rule classes |
|---|---|---|
| I. Grouping Structure | Segmentation into motives → phrases → periods → sections | GWFRs, GPRs, transformational rules |
| II. Metrical Structure | Hierarchical alternation of strong/weak beats | MWFRs, MPRs |
| III. Time-Span Reduction | Tree of "heads" (most important event per time-span) | TSRWFRs, TSRPRs |
| IV. Prolongational Reduction | Tree of tensing/relaxing patterns | PRWFRs, PRPRs |

- **Well-formedness rules (WFRs)**: what structural descriptions are *legal*.
- **Preference rules (PRs)**: which legal description a listener actually *hears* (soft, weighted, conflict-prone).
- **Transformational rules**: map distorted surfaces back to well-formed descriptions.

Algorithmic lineage: **ATTA** (Automatic Time-span Tree Analyzer, ISMIR 2005), **FATTA** (Full Automatic Time-span Tree Analyzer, ICMC 2007), and the ExGTTM analyzer (Hamanaka, Hirata & Tojo 2006, *Journal of New Music Research* 35(4)). Tension quantification: **Lerdahl & Krumhansl (2007), "Modeling Tonal Tension," *Music Perception* 24(4)**, building on Lerdahl's *Tonal Pitch Space* (2001).

**Gap filled in the Musicom catalog**: 034 PCFG does Chomskyan rewrite with free probabilistic rules; 056 SCCC does species counterpoint against a cantus firmus; 001 Skeleton-First drafts a structural grid — but none models the *listener's hierarchical hearing* (grouping + meter + reduction + tension) as the generative object. GTTM-HC is the Rules-Based, tonal-hierarchy counterpart to stochastic pitch generators (002/053) and the deterministic foil to free-grammar 034 PCFG.

---

## 2. Method description

GTTM is canonically an *analysis* theory (score → four trees). **GTTM-HC inverts it into a generation method**:

1. Compose the **deep prolongational structure** first — a Schenkerian-style skeleton: tonic triad with a descending structural line (e.g., $\hat{3} \to \hat{2} \to \hat{1}$ over I–V–I).
2. **Elaborate** each branch recursively with diminutions — passing tones, neighbor tones, arpeggiations — governed by the well-formedness rules.
3. Place the resulting events on the **metrical grid** (strong beats carry heads, weak subdivisions carry elaborations).
4. Read the **grouping structure** off the elaboration tree (parallel branches = parallel groups).

The four systems are generated in dependency order — meter constrains grouping, grouping + meter constrain time-span reduction, time-span reduction constrains prolongational reduction — so the whole composition is one self-consistent hierarchical description, exactly the object GTTM's rules adjudicate.

### Prolongational branch types (the harmonic/tension semantics)

| Branch type | Notation | Meaning | Tension |
|---|---|---|---|
| Strong prolongation | open node | same event sustained/embellished, no harmonic motion | relaxation |
| Weak prolongation | filled node | neighbor/arpeggiation motion within one harmony | mild tension |
| Progression | no node | actual harmonic movement | tension |

---

## 3. Extended mathematics

### 3.1 Metrical structure

A grid of levels $L_0 \succ L_1 \succ \dots \succ L_k$ (bar > beat > subdivision), each a regular strong/weak alternation. Beats at level $L_i$ are a subset of beats at $L_{i+1}$. Metrical strength of a surface position is the number of levels at which it is a strong beat:

$$\mathrm{strength}(t) = \left| \{ i : t \in \mathrm{strong}(L_i) \} \right|$$

### 3.2 Grouping preference rules (boundary scoring)

For an inter-onset gap between events $n_2$ and $n_3$ (with neighbors $n_1, n_4$):

- **GPR2 (Proximity)**: boundary if the inter-onset interval $n_2 \to n_3$ exceeds both $n_1 \to n_2$ and $n_3 \to n_4$.
- **GPR3 (Change)**: boundary if marked by register change (larger intervallic distance), dynamics change, articulation change, or length change.
- **GPR5 (Symmetry)**: prefer groupings approaching equal halves.
- **GPR6 (Parallelism)**: parallel segments form parallel parts of groups.

A boundary score is a weighted sum of these cues; boundaries are chosen greedily top-down subject to the grouping well-formedness rules (contiguous, exhaustive, non-overlapping groups).

### 3.3 Time-span reduction

For each group, the **head** is the event that is (a) on the strongest beat and (b) most harmonically stable (chord root/fifth over passing dissonance). Recursing gives the time-span tree.

### 3.4 Prolongational reduction

Connect heads into a tree with the three branch types above, satisfying PRWFRs (e.g., no crossing branches). The tree encodes the tensing/relaxing structure.

### 3.5 Tension model (Lerdahl–Krumhansl 2007, simplified)

For a chord/event $y$:

$$T(y) = T_{loc}(y) + T_{diss}(y) + T_{hier}(y)$$

- $T_{loc}(y) = \delta(y \to \text{tonic})$ — Tonal Pitch Space distance (circle-of-fifths steps + chord-space steps) from $y$ to the tonic.
- $T_{diss}(y)$ — sensory dissonance of the chord.
- $T_{hier}(y)$ — hierarchical branching penalty (progression > weak prolongation > strong prolongation = 0).

The sequence of $T(y)$ over heads is the piece's tension curve — and *is* the macro-form's HOME/LIFT/TENSE/TURN trajectory.

### 3.6 Elaboration operators (generation, the inverse of reduction)

Starting from the deep structure, repeatedly apply:

- **Passing**: insert a stepwise event between two heads a third apart.
- **Neighbor**: insert a step above/below a head and return.
- **Arpeggiation**: insert chord tones between heads.

Each elaboration preserves the parent's branch type and harmonic function, so the final tree is well-formed by construction.

### 3.7 Complexity

Grouping via boundary scoring + top-down segmentation is $\mathcal{O}(N \log N)$ (sort boundary strengths); time-span head selection $\mathcal{O}(N)$; prolongational tree build $\mathcal{O}(N)$; elaboration $\mathcal{O}(N)$ in surface events. Total $\mathcal{O}(N \log N)$ — deterministic, seedable.

---

## 4. Musical Elements Framework

- **PITCH**: From recursive prolongational elaboration of the deep structure. The structural line supplies the "heads"; diminutions (passing/neighbor/arpeggiation) fill between heads. Register is free; pitch-class content constrained by current harmony + stepwise-motion preference (PRPR).
- **RHYTHM**: Metrical structure is the engine — a multi-level strong/weak grid. Heads on strong beats; elaborations on weak subdivisions. Recursion depth controls surface density. MWFRs guarantee grid-locked, groove-compatible output.
- **HARMONY**: The prolongational tree itself. Strong prolongation = no chord change; progression = harmonic movement. Deep structure fixes the tonal plan (tonic prolongation, dominant preparation, cadence). Tension read directly off the tree.
- **STRUCTURE**: Top levels of grouping + prolongational trees. Piece = root group; children = sections; branch type per section = its function (progression-heavy = TENSE/LIFT, strong-prolongation-heavy = HOME). Parallel groups (GPR6) yield genuine ABA/rondo.
- **TEXTURE**: How the elaboration tree is distributed across voices. One tree monophonic = melody; one tree partitioned = homophonic; multiple per-voice trees = polyphonic counterpoint sharing the deep structure.

---

## 5. UnitMatrix Integration (Voices & Sections)

- **Rows (Voices)**: Each voice is (a) a partition of the single prolongational tree (homophonic), or (b) its own elaboration tree from the same deep structure with a different diminution pattern (polyphonic). All voices share metrical + grouping structures → grid-synchronized and phrase-aligned.
- **Columns (Sections)**: Each section = a top-level child of the root group. Prolongational branch type sets chord function: strong prolongation = HOME, progression = TENSE/TURN, weak prolongation = LIFT.
- **Cells** $U_{v,s}$:
  - `{PITCH}`: head pitch + diminutions elaborated to the cell's recursion depth.
  - `{RHYTHM}`: onset offsets from the metrical grid.
  - `{HARMONY}`: prolongational branch type (strong/weak/progression).
  - `{TEXTURE}`: number of active diminution branches at the surface.
- **Mapping flow**: deep structure → metrical grid → grouping tree → time-span tree → prolongational tree → recursive elaboration → voice distribution → fill cells → `validate()` → export.

---

## 6. Python implementation sketch

```python
import numpy as np
from dataclasses import dataclass, field

# --- Metrical grid: multi-level strong/weak beats ---------------------------
def metrical_grid(n_bars, beats_per_bar, levels):
    """levels: subdivisions per beat at each metrical level, e.g. [1, 2, 4]."""
    grid = []
    for bar in range(n_bars):
        for beat in range(beats_per_bar):
            for sub in range(levels[-1]):
                strength = sum(1 for lv in levels if sub % lv == 0)
                grid.append({"bar": bar, "beat": beat, "sub": sub,
                             "strength": strength,
                             "tick": (bar * beats_per_bar * levels[-1]
                                      + beat * levels[-1] + sub)})
    return grid

# --- Grouping: preference-rule boundary scoring -----------------------------
def boundary_scores(events):
    """GPR2 proximity + GPR3 change. events: list of (tick, pitch, vel, dur)."""
    scores = []
    for i in range(1, len(events)):
        ioi_prev = events[i][0] - events[i-1][0]
        ioi_next = events[i+1][0] - events[i][0] if i+1 < len(events) else ioi_prev
        prox = (ioi_prev > ioi_next) + (ioi_prev > 0)          # GPR2
        change = (abs(events[i][1] - events[i-1][1]) > 6) + \
                 (abs(events[i][2] - events[i-1][2]) > 20)     # GPR3
        scores.append((prox + change, i))
    return sorted(scores, reverse=True)

def grouping_tree(events, scores, max_groups=4):
    """Greedy top-down binary segmentation subject to GWFRs."""
    bounds = [0, len(events)]
    for strength, i in scores:
        if len(bounds) - 1 >= max_groups:
            break
        if i not in bounds and 0 < i < len(events):
            bounds.append(i)
    bounds.sort()
    return [events[a:b] for a, b in zip(bounds[:-1], bounds[1:])]

# --- Prolongational tree + tension -----------------------------------------
@dataclass
class PNode:
    pitch: int                    # head pitch (MIDI)
    branch: str = "progression"   # strong | weak | progression
    children: list = field(default_factory=list)

def tonal_tension(pitch, tonic, chord_roots):
    """Simplified Lerdahl-Krumhansl: pitch-space distance + branching penalty."""
    pc = pitch % 12
    fifths = min((pc - tonic) % 12, (tonic - pc) % 12)
    return fifths + (0 if pc in chord_roots else 2)

def elaborate(node, depth, chord_tones, rng):
    """Recursive prolongational expansion: passing / neighbor / arpeggiation."""
    if depth == 0 or not node.children:
        return [node.pitch]
    out = []
    kids = node.children
    for idx, child in enumerate(kids):
        out.extend(elaborate(child, depth - 1, chord_tones, rng))
        if idx < len(kids) - 1:
            nxt = kids[idx + 1].pitch
            gap = nxt - child.pitch
            if abs(gap) == 2:                       # passing tone
                out.append(child.pitch + gap // 2)
            elif abs(gap) > 2:                      # arpeggiation
                out.append(chord_tones[rng.integers(0, len(chord_tones))])
            else:                                   # neighbor tone
                out.append(child.pitch + (1 if rng.random() < 0.5 else -1))
    return out

# --- musicom engine integration (sketch) ------------------------------------
# from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit
# composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
# composer.create_matrix(num_voices=4, num_sections=4)
# ... add_voice / add_section ...
# for each section s (a root child), for each voice v (tree partition):
#   events = elaborate(section_tree[v], depth=recursion_depth, ...)
#   place heads on strong beats, elaborations on weak beats (metrical grid)
#   composer.fill_voice_section(voice, section, create_note_unit(pitch, dur, start_tick))
# ok, msg = composer.validate()   # MUST be True before to_midi
```

**Parameter set**: deep structure (tonic, structural line, tonal plan), metrical levels, recursion depth (surface density), preference-rule weights (GPR2/3/5/6), diminution mix (passing/neighbor/arpeggiation), voice distribution mode (partition vs. per-voice trees).

---

## 7. Pitfalls

1. **Analysis/generation direction confusion** — GTTM is canonically analysis; naive "analyze then resynthesize" reproduces input. Fix: generate top-down from deep structure; rules as construction constraints, not a parser.
2. **Sparse / staccato surface** — shallow recursion or heads-only placement gives the 011/032 gap-filled failure. Fix: elaborate to fill weak subdivisions, or add a continuous fill layer (sustained head-chord pads, 026 DPSM arpeggios).
3. **Branch-type / harmony mismatch** — "strong prolongation" while harmony changes violates PRWFR. Fix: enforce strong = no chord change, weak = same harmony, progression = chord change; validate tree against tonal plan.
4. **Metrical rigidity** — every head on beat 1 = stiff output. Fix: heads on strongest beat *within their time-span*; allow syncopation via sub-levels.
5. **Preference-rule ties** — GPR2/3/5/6 conflict; greedy picker unstable. Fix: weight PRs (GPR6 > GPR2 > GPR3) and break ties deterministically.
6. **Voice independence collapse** — partitioning one tree stacks parallel octaves. Fix: distinct voice registers; per-voice trees in polyphonic mode.
7. **Tension monotony** — same branch sequence every section = flat curve. Fix: vary prolongational plan per section; verify HOME/LIFT/TENSE/TURN arc via $T(y)$.
8. **Off-grid drift** — fractional-beat diminutions land between ticks. Fix: quantize to grid resolution; run `composer.validate()`.

---

## 8. Comparison with related methods

- **034 PCFG Recursion**: free weighted rewrite; GTTM-HC's rewrite rules are the WFRs/PRs of tonal hearing, non-terminals are prolongational branch types.
- **001 Skeleton-First**: structural grid from DNA seeds; GTTM-HC's skeleton is the deep prolongational structure — the skeleton *is* the tonal plan, meter is generated not assumed.
- **056 SCCC**: species counterpoint vs. cantus firmus; GTTM-HC replaces the CF with the structural line, species rules with prolongational branching.
- **051 SGLM / 052 QWC**: macro-form from graph spectra/topology; GTTM-HC derives form from grouping + prolongational trees — the tree *is* the form.
- **002 Markov / 053 LFC**: stochastic pitch with weak tonal gravity; GTTM-HC is deterministic with strict tonal gravity (every event anchored to the tonic via the reduction tree).

---

## 9. References

- Lerdahl, F., & Jackendoff, R. (1983). *A Generative Theory of Tonal Music*. MIT Press.
- Lerdahl, F. (2001). *Tonal Pitch Space*. Oxford University Press.
- Lerdahl, F., & Krumhansl, C. L. (2007). "Modeling Tonal Tension." *Music Perception* 24(4): 329–366.
- Lerdahl, F. (2009). "Genesis and Architecture of the GTTM Project." *Music Perception* 26: 187–194.
- Hamanaka, M., Hirata, K., & Tojo, S. (2006). "Implementing a Generative Theory of Tonal Music." *Journal of New Music Research* 35(4): 249–277.
- Hamanaka, M., Hirata, K., & Tojo, S. (2005). "ATTA: Automatic Time-span Tree Analyzer based on Extended GTTM." *ISMIR 2005*: 358–365.
- Hamanaka, M., Hirata, K., & Tojo, S. (2007). "FATTA: Full Automatic Time-span Tree Analyzer." *ICMC 2007*: 153–156.
- Hirata, K., Tojo, S., & Hamanaka, M. (2007). "Techniques for Implementing the Generative Theory of Tonal Music." *ISMIR 2007 Tutorial*.
- Bernstein, L. (1976). *The Unanswered Question: Six Talks at Harvard*. Harvard University Press.
