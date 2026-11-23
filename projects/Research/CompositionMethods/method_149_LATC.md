# Method 149 — Langton's Ant / Turmite Trajectory Composition (LATC)

- **ID:** 149
- **Paradigm:** Rules-Based (deterministic finite-state rule table; no sampling, no training, no physics — the complexity is emergent, not injected)
- **Layer:** concrete (LAYER_ARCHITECTURE.md) — one ant step = one note event (pitch, onset, duration, velocity) on a discrete lattice, i.e. fills UnitMatrix cells; the (rule table, seed pose, grid init) tuple is the plan, the simulated trajectory is the realized cell
- **Family:** agent-based grid rewrite (turmite). Siblings: 021 CA (synchronous *field* update — the turmite is a *moving agent*), 031 Boids (agents in *continuous* space — turmites are discrete-lattice), 041 ACOPF (pheromone path *optimization* — no grid rewrite), 082 RBN (random Boolean *networks* — cites Langton 1990 only), 030 RDTP (PDE fields), 092 DLA (sticking particles, no turning rules), 093 PPNC (static connectivity), 148 JCOC (elimination-order permutations). **LATC is the DB's first moving-agent grid-rewrite system.**
- **One-liner:** compose from the deterministic dynamics of a turmite (Langton's ant 1986 being the canonical 2-colour case): one agent on a square lattice reads its cell, turns 90° (white→clockwise, black→counter-clockwise, name "RL"), flips the colour, advances; the path = melodic contour, the colour field = texture/memory, and the three regimes (symmetric simplicity → pseudo-random chaos until step 9,977 → a 104-step-period highway drifting (−2,−2) per period) compose a built-in chaos→order macro-form; multi-colour turmites give the rule zoo (RLR chaotic, RLLR/LLRR Truchet-symmetric), a torus wraps the finite state space into a literal loop, a bounded board gives an escape coda, multiple ants are voices, and turmites are Turing-universal (Gajardo–Moreira–Goles 2002; Maldonado et al. 2017).

---

## 1. The move law

A turmite is a Turing machine with an orientation plus a state whose "tape" is an infinite 2D grid (terms: *ant*, *vant*; "tur-mite" coined by A. K. Dewdney 1989 from "Turing machine" + "termite", after Greg Turk's creatures; Allen H. Brady 1988 independently proposed "TurNing machines"). Langton's ant is the canonical relative turmite on a square lattice with 2 colours and 1 state.

Per timestep, the ant: (1) **turns** on the spot by a multiple of 90°; (2) **changes** the colour of the cell it stands on; (3) **moves** forward one square. The actions come from a state-transition table keyed by (internal state, cell colour). For Langton's ant:

- at a **white** square: turn 90° **clockwise**, flip the colour, move forward;
- at a **black** square: turn 90° **counter-clockwise**, flip the colour, move forward.

Formally, with grid $g: \mathbb{Z}^2 \to \{0,1\}$ (0 = white), pose $(p,d)$, $d \in \{\mathrm{N,E,S,W}\}$:

$$d \leftarrow d + \sigma(g(p)),\qquad \sigma(0)=+1,\ \sigma(1)=-1;\qquad g(p) \leftarrow 1 - g(p);\qquad p \leftarrow p + \vec e_d.$$

**The whole method is that law plus a rule table.** The agent's own past flips the cells that determine its future — the grid is a physical memory of the trajectory (musical memory made literal). Nothing is sampled, learned, or force-fit; the structure is emergent.

**Multi-colour extension (Turk–Propp).** More colours, modified cyclically; the rule is named by the turn letter per successive colour: "RL" = Langton's ant; "RLLR" = 4-colour ant with turns $[R,L,L,R]$ cycling. General state transition: colour $c$ → turn $\sigma_k(c)$, colour $c \leftarrow (c+1) \bmod k$. Multi-state turmites allow the ant itself to change state (state table over (state, colour)); behaviours include highways, chaotic growth, spiral growth, and rare periodic loops.

## 2. The three-phase arc (macro-form for free)

From an all-white grid the ant passes through three regimes (Pratchett–Stewart–Cohen 1999; Wikipedia):

1. **Simplicity.** First few hundred moves: small, often symmetric patterns — a built-in opening motif.
2. **Chaos.** A large irregular pattern appears; the ant traces a pseudo-random path until step **9,977** — a built-in development section.
3. **Emergent order.** The ant builds a recurrent **"highway" pattern of 104 steps** that repeats indefinitely — a built-in ostinato/loop.

Measured (this run, `_web149_latc/verify_latc.py`): highway onset at step 9,976 (0-based indexing; Wikipedia's 9,977 is 1-based); period exactly **104**; drift per period **Δ = (−2,−2)** cells — the highway translates diagonally at 45°, two cells per axis per period. The highway is conjectured to be the attractor of *all* finite configurations (open problem — the **Highway conjecture**; generalized versions fail, Lutfalla 2025). What *is* proven: the trajectory is always **unbounded** regardless of the initial configuration (Bunimovich–Troubetzkoy 1992, *Recurrence properties of Lorentz lattice gas cellular automata*; the result is often misattributed as the "Cohen–Kong theorem", cf. Stewart 1994, *The Ultimate in Anty-Particles*, Scientific American).

**Musical reading of the arc.** The piece composes its own narrative: symmetric germ → unstable, wide-ranging development → locked groove with a built-in transposition (the drift). Macro-form is *detected*, not imposed: the symmetry-end and highway-onset are measurable landmarks (see §6 `phase_split`).

## 3. Computation: the ant is a computer

- **8-state CA view.** Langton's ant can be described as a cellular automaton where the ant-cell has 8 colours encoding (cell colour × direction) — Gajardo, Moreira & Goles (2002). Reading the colour bit from the high bits of $4b + d$ reproduces the identical trajectory (verified over 10,000 steps, §7 check 9). This is the bridge by which the abstract layer can treat LATC as a CA grammar.
- **P-hardness / universality / undecidability.** Gajardo–Moreira–Goles (2002, *Discrete Applied Mathematics* 117:41–50; arXiv:nlin/0306022) construct **any boolean circuit** from the trajectory of a single ant → P-hardness; simulating 1D CAs and Turing machines gives universality and undecidability of reachability.
- **Turmites ≡ Turing machines.** Nontrivial turmites are Turing-universal (Maldonado, Gajardo, Hellouin de Menibus & Moreira 2017, arXiv:1702.05547); general turmites are exactly equivalent in power to 1D Turing machines (either simulates the other).

Consequence for composition: **any rule table is a legitimate grammar** — the method is a programmable composer whose programs are 2D Turing-machine transition tables.

## 4. The turmite zoo

| variant | behaviour (measured this run where noted) |
|---|---|
| "RL" (Langton's ant) | highway after 9,976 steps; period 104; drift (−2,−2) |
| "RLR" (3 colours) | chaotic growth; **no highway** in 30,000 steps; max radius 50 |
| "RLLR" (4 colours) | bounded/symmetric growth; no highway; max radius 26 at 30k; **horizontal-reflection symmetry at 3/120 sampled times** (Truchet-tile proof: cyclic names containing "LL" or "RR" pairs produce repeatedly symmetric patterns) |
| "LLRR" (4 colours) | symmetric growth; reflection symmetry at 8/120 samples; RL control 0/56 |
| multi-state turmites | highways, chaotic growth, spiral growth |
| multi-ant systems | shared-grid interaction; **sync vs async updating gives different results** (Belgacem–Fatès 2012); Pegg's split-and-annihilate collision rule |
| other lattices | triangular (Paterson's worms — turmites on triangle *edges*), hexagonal (Hutton), 3D turmites; 1D relative turmites ("flippers", Brady) are trivial |
| busy beavers | Brady: 2-state 2-colour machine prints 37 ones / halts after 121 steps; Pegg's annihilation busy beaver |

Torus wrap: on a finite torus the state space (position × direction × grid) is finite, so the ant **eventually cycles** — a literal loop form. Measured: 4×4 torus → cycle onset 42, period 96; 5×5 torus → onset 63, period 11,710. Bounded non-wrapping board: the ant **walks off** the region (measured: 901 steps on a 21×21 board) — an escape coda.

## 5. Musical mapping (Musical Elements Framework + UnitMatrix)

**PITCH.** The path coordinate (typically the row, $y$) is the pitch axis: $\mathrm{pitch}_t = \mathrm{ladder}[\,y_t \bmod L\,]$ (or nearest-ladder quantization). Consecutive steps move at most one lattice unit unless a turn sends the ant sideways — a **restricted ±1/0 walk**: conjunct melody by construction (contrast 053 Lévy's heavy-tailed leaps). Highway drift = built-in transposition (−2 ladder steps per 104 units); chaos phase = wide aperiodic contour; simplicity phase = small symmetric arcs; direction changes = melodic turning points; same-cell-revisited-in-the-other-colour = neighbour-tone returns.

**RHYTHM.** Lattice steps are the time grid: uniform step = isochronous stream; colour-gated steps = variable density. The **104-step highway period** is a 104-unit groove; the drift transposes it by −2 degrees per period (a tonal descent in the loop). Flip-density per window drives velocity/articulation arcs. Torus cycle length (96 / 11,710 …) = the loop's duration. Optional "audible trail": recently flipped cells emit short ornament echoes — the grid as a deterministic delay line.

**HARMONY.** Not generated directly; per-section path **centroid** (mean grid coordinate) quantized to a ladder root gives a chord-root plan; the drift Δ per highway period gives a systematic root transposition (mod 12 → a deterministic progression). Multi-colour tables can be read as chord grammars (colour = chord-quality class; colour transitions = progression); multi-ant shared grids create emergent harmonic stacks.

**STRUCTURE.** The signature axis. Phase = form: simplicity = opening/motif; chaos = development; highway = ostinato/loop (repeatable with built-in transposition); torus cycle = literal A-section; bounded-board escape = coda. Boundaries measurable (symmetry-end, highway-onset) — form is detected, not imposed. Multi-ant = layered forms with phase offsets.

**TEXTURE.** The colour field is the texture state: colour distribution = density/register colouring; the trail = ornament layer; **ant hocketing** — grid transposed to (voice × time), the ant's row = the sounding voice — gives a single-agent hocket (every column one voice). Same-rule different-start ants = phase texture (combinatorial sibling of 026 DPSM); different rules = stratified textures (chaotic ant over a symmetric ant).

**UnitMatrix integration.** *Rows = voices = ants*: `{rule_name, start_pos, start_dir, grid_init, shared_or_private_grid, update_semantics, torus|bounded_board|None, pitch_ladder, step_to_tick, seed}`. *Columns = sections = trajectory windows*: `{phase_label, window_len_steps, quantize_map, velocity_arc, trail_layer}`; the colour field **persists across columns** — section $j$'s flips shape section $j+1$'s turns (cross-section coupling unique to this method). *Cells = MusicUnit*: one event per step — pitch = ladder quantized path coordinate, onset = step × `step_to_tick`, duration = one step (window-final event extended to the seam), velocity = flip-density arc. Rows equal length **by construction** → `validate()` passes.

**Composition path.** `pick rule table + seed pose → simulate T steps (O(T)) → detect phases → split into section windows → map steps to MusicEvents → group by voice → MusicUnit per cell → validate() → to_midi() → any SP renderer`.

## 6. Reference implementation sketch

```python
"""generators/langton_ant.py — LATC (proposed)."""
from collections import defaultdict

N, E, S, W = 0, 1, 2, 3                 # directions; clockwise = +1 mod 4
CW, CCW = 1, -1
DX = ((0, 1), (1, 0), (0, -1), (-1, 0))

def ant_step(grid, pos, d, turn_rules):
    """One Langton-ant step: turn by current cell colour, flip, advance."""
    x, y = pos
    col = grid.get((x, y), 0)            # 0 = white
    d = (d + turn_rules[col]) % 4
    grid[(x, y)] = 1 - col
    dx, dy = DX[d]
    return (x + dx, y + dy), d

def run_ant(steps, turn_rules=(CW, CCW), start=(0, 0), torus=None):
    """Simulate one ant; returns position log (before each move)."""
    grid, pos, d = {}, start, N
    log = []
    for _ in range(steps):
        log.append(pos)
        pos, d = ant_step(grid, pos, d, turn_rules)
        if torus:
            w, h = torus
            pos = (pos[0] % w, pos[1] % h)
    return grid, log

def highway_detect(log, period=104, window=2000, lo=6000, hi=30000):
    """Two-phase: scan for t0 with 3 equal consecutive periods, then verify a
    window. Returns (onset, drift_per_period) or (None, None)."""
    for t0 in range(lo, hi - 3 * period):
        dv = (log[t0 + period][0] - log[t0][0], log[t0 + period][1] - log[t0][1])
        if ((log[t0 + 2*period][0] - log[t0 + period][0],
             log[t0 + 2*period][1] - log[t0 + period][1]) == dv and
                (log[t0 + 3*period][0] - log[t0 + 2*period][0],
                 log[t0 + 3*period][1] - log[t0 + 2*period][1]) == dv):
            if all((log[t + period][0] - log[t][0],
                    log[t + period][1] - log[t][1]) == dv
                   for t in range(t0, t0 + window)):
                return t0, dv
    return None, None

def phase_split(log, simplicity_cap=500):
    """Return section boundaries from the measured regimes."""
    onset, _ = highway_detect(log) or (None, None)
    # simplicity end: first revisit of the 4-fold symmetric prefix (approx: cap)
    return [0, simplicity_cap, onset, len(log)] if onset else [0, simplicity_cap, len(log)]

class Turmite:
    """Multi-colour cyclic turmite. name = turn letters (L/R) per colour."""
    def __init__(self, name, start=(0, 0)):
        self.rules = tuple(CCW if c == "L" else CW for c in name)
        self.ncol = len(self.rules)
        self.grid, self.pos, self.d = {}, start, N
    def step(self):
        col = self.grid.get(self.pos, 0)
        self.d = (self.d + self.rules[col % self.ncol]) % 4
        self.grid[self.pos] = (col + 1) % self.ncol
        dx, dy = DX[self.d]
        self.pos = (self.pos[0] + dx, self.pos[1] + dy)

def trajectory_to_units(log, ladder, step_to_tick, velocity_arc=None, section_len=None):
    """Map a position log to (pitch, start_tick, end_tick, velocity) events.
    pitch = ladder[y mod len(ladder)]; last event extended to section_len."""
    events = []
    for i, (x, y) in enumerate(log):
        start = i * step_to_tick
        end = (i + 1) * step_to_tick
        if section_len and i == len(log) - 1:
            end = section_len                      # seam-anchored terminal event
        vel = velocity_arc[i] if velocity_arc else 90
        events.append((ladder[y % len(ladder)], start, end, vel))
    return events
```

Integration: emit one `MusicUnit` per (voice, section) from `trajectory_to_units`; all voices' windows share the section length → `validate()` passes by construction (zero drift designed in, as in 144/147/148).

## 7. Verification

`_web149_latc/verify_latc.py` → `_web149_latc/verify_latc_results.txt` — **16/16 pass**: (1) first-8-step positions exactly `(0,0),(1,0),(1,-1),(0,-1),(0,0),(-1,0),(-1,1),(0,1)`; (2) highway onset 9,976 ≈ Wikipedia 9,977; (3) period 104 over a 2,000-step window; (4) drift (−2,−2) per period; (4b) drift holds to step 30,000; (5) unbounded growth — max radius 11→22→29→211→403 at 1k/5k/10k/20k/30k steps; (6) 4×4 torus cycle onset 42 / length 96; (6b) 5×5 torus onset 63 / length 11,710; (7) determinism — identical logs, sha256 `8a6d9ab3759489a2`; (8a) "RL" highway onset 9,975; (8b) "RLR" no highway in 30k, max radius 50; (8c) "RLLR" no highway, max radius 26; (8d) RLLR horizontal-reflection symmetry 3/120 samples; (8e) LLRR 8/120 vs RL 0/56; (9) 8-state CA view ≡ ant trajectory over 10,000 steps; (10) 21×21 bounded board: escape after 901 steps.

## 8. References

- Wikipedia, "Langton's ant" — https://en.wikipedia.org/wiki/Langton%27s_ant (fetched live 2026-11-23 via the MediaWiki extract API). Rules, three modes of behaviour, highway (104 steps, onset 9,977), attractor conjecture, unboundedness (Bunimovich–Troubetzkoy 1992; misattributed Cohen–Kong), Gajardo et al. 2002 circuit construction, multi-colour Turk–Propp extension ("RL" naming, RLLR symmetry, Truchet tiles), multi-state turmites, multi-ant systems (Pegg splitting/annihilation), Paterson's worms, Langton's loops.
- Wikipedia, "Turmite" — https://en.wikipedia.org/wiki/Turmite (fetched live 2026-11-23). Definition, equivalence to 1D Turing machines, history (Langton 1986, Brady 1988, Turk → Dewdney "tur-mites" 1989, Rucker), relative vs absolute turmites, specification (L/R/N/U turns), behaviours (chaotic/spiral/highway/periodic), busy beavers (Brady 37 ones / 121 steps), other grids (triangular/hexagonal/3D, flippers).
- Langton, C. G. (1986). "Studying artificial life with cellular automata." *Physica D* 22(1–3), 120–149. doi:10.1016/0167-2789(86)90237-X.
- Gajardo, A., Moreira, A. & Goles, E. (2002). "Complexity of Langton's ant." *Discrete Applied Mathematics* 117(1–3), 41–50. doi:10.1016/S0166-218X(00)00334-6; arXiv:nlin/0306022. Boolean circuits, P-hardness, universality, undecidability.
- Maldonado, D., Gajardo, A., Hellouin de Menibus, B. & Moreira, A. (2017). "Nontrivial Turmites are Turing-universal." arXiv:1702.05547.
- Boon, J.-P. (2000). "How fast does Langton's ant move?" arXiv:cond-mat/0004331. Highway discrete dynamics; disordered → ordered transition.
- Lutfalla, V. (2025). "Sideways on the highways." arXiv:2505.05426. Generalized Highway conjecture fails generically.
- Etse, K. R. (2026). "How Long Can the Escaping Ant Be Confined?" arXiv:2606.26677. Escape-time bounds.
- Gale, D., Propp, J., Sutherland, S. & Troubetzkoy, S. (1995). "Further Travels with My Ant." *Mathematical Intelligencer* 17, 48–56. doi:10.1007/BF03024370; arXiv:math/9501233. Multi-colour ants, Truchet tiles.
- Belgacem, S. & Fatès, N. (2012). "Robustness of multi-agent models: the example of collaboration between turmites with synchronous and asynchronous updating." *Complex Systems* 21(3), 165–182. doi:10.25088/ComplexSystems.21.3.165.
- Bunimovich, L. A. & Troubetzkoy, S. E. (1992). "Recurrence properties of Lorentz lattice gas cellular automata." *Journal of Statistical Physics* 67(1–2), 289–302. doi:10.1007/BF01049035.
- Stewart, I. (1994). "The Ultimate in Anty-Particles." *Scientific American* 271(1), 104–107. The "Cohen–Kong" naming; proof that the ant is unbounded.
- Pegg, E., Jr. "Turmite." MathWorld — http://mathworld.wolfram.com/Turmite.html.
- Musicom engine: `workflows/unitmatrix_composer.py` (zero-drift gate), `structures/` (MusicUnit, MusicEvent), `rules/set_theory.py` (ladder/scale utilities).

## 9. Pitfalls (short list)

1. Highway conjecture is open — detect the phase, fall back to a step-budget form if no highway appears (generalized rules can fail to highway, Lutfalla 2025).
2. Unboundedness is real — quantize the pitch axis into a finite ladder (mod L) or cap the domain, or the register explodes after ~10k steps (radius 403 at 30k).
3. Torus cycles can be huge (5×5 → 11,710) — measure before promising an 8-bar loop.
4. Multi-ant semantics must be fixed (sync vs async differs; Belgacem–Fatès) or output is not reproducible.
5. 1D turmites ("flippers") are trivial — the method lives in 2D.
6. The chaos phase is the composition, not noise — don't filter it away.
7. Determinism is the contract — seed everything, golden-hash safe.
8. Neighbour audit: 021 (field CA), 031 (continuous agents), 041 (pheromone optimization), 082 (Boolean nets, cites Langton 1990 only), 030 (PDE), 092 (sticking), 148 (permutations). LATC = first moving-agent grid-rewrite (turmite) method in the DB.
9. Apply humanization after the lattice; jitter must not cross a section seam (the window-final event is the seam anchor).
