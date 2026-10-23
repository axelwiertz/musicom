# REPORT — Method 123: Game-Theoretic Best-Response Composition (GTBRC)

**Date:** 2026-10-23 · **Job:** music research / methods-DB append · **Status:** complete and verified

| field | value |
|---|---|
| **Method ID** | **123** |
| **Name** | Game-Theoretic Best-Response Composition |
| **Acronym** | GTBRC |
| **Paradigm** | **Rules-Based** (strategic / game-theoretic — the first such method in the catalogue) |
| **Layer** | **concrete** (generates UnitMatrix events; feeds `generators/`; optional abstract pre-pass → `rules/subset_network.py`) |
| **One-line description** | Treats the UnitMatrix as a non-cooperative congestion game — rows are players, columns are rounds, cells are equilibria — where each voice minimises a private taste plus a convex cost for sharing a (register band × metric slot) resource, which makes the game an *exact potential game*: best-response dynamics provably terminates at a pure Nash equilibrium, the potential recorded along the way is the tension curve, and the price of anarchy measures the cost of selfishness. |
| **Resolved next ID** | table scan max = 122 (line 132), standalone `method_*.md` max = 122, `report_*.md` max = 122 → **new ID = 123** |
| **Next free ID after this job** | **124** |
| **DB line count before** | 27 701 |
| **DB line count after** | 27 809 (**+108**: +1 summary row, +107 method section) |
| **Summary row location** | line **133** of `methods_db.md` (immediately after 122) |
| **Method section location** | lines **27703–27809** (appended at EOF) |
| **Standalone file** | `method_123_GTBRC.md` (12 013 bytes) |
| **Candidate code path** | `generators/game_theoretic.py` — class `GameTheoreticComposer` (`build_strategies()`, `resource_loads()`, `cost()`, `potential()`, `best_response()`, `fictitious_play()`, `logit_response()`, `correlated_equilibrium()`, `realize_profile()`), consumed by `workflows/unitmatrix_composer.py`; abstract pre-pass (equilibrium-set enumeration + Φ weighting) → `rules/subset_network.py` |
| **Validation harness** | `projects/Research/outputs/gtbrc_validate/gtbrc_verify.py` (potential/theorem checks, brute-force NE + PoA, hocket, logit dial), `gtbrc_demo.py` (engine integration, MIDI) |
| **Artifacts** | `gtbrc_demo.mid` (494 bytes, 38 notes, 20.0 s), `validate() -> True OK`, `preflight_check.py` COMPLIANT |

## 1. Summary-table row (as written, line 133)

```
| **123** | concrete | Game-Theoretic Best-Response Composition (GTBRC) | **Rules-Based** | Pitch, Rhythm, Harmony, Structure, Texture | Moderate (Incentive-guided) | Grid-Locked | Local / Round (profile + play history) | $\mathcal{O}(I \cdot V \cdot \lvert S \rvert \cdot R)$ | Treats the UnitMatrix as a non-cooperative game: rows are **players**, columns are **rounds**, a cell is the outcome of one round. A resource is a (register band × metric slot) pair; voice $i$'s strategy is the set of resources its gesture occupies plus a pitch class on each, and its cost is $c_i(s)=\mathrm{priv}_i(s_i)+\sum_{r\in s_i}\left(w_1 n_r+w_2 n_r^2\right)$ — Rosenthal's congestion game, hence an **exact potential game** with $\Phi(s)=\sum_i \mathrm{priv}_i(s_i)+\sum_r\sum_{k\le n_r}\left(w_1 k+w_2 k^2\right)$. Each strictly improving unilateral move lowers $\Phi$ by exactly $\Delta c_i$, so best-response dynamics has the finite improvement property and always ends at a pure Nash equilibrium (verified: 0 potential violations, 200/200 and 30/30 × 6 configurations terminated, ≤5 sweeps, mean 1.93–2.53). Three consequences no other method has: (i) $\Phi$ recorded along the descent **is** the tension curve, with units (demo sections 46.0→36.5 and 53.5→29.5, monotone); (ii) the convex congestion term gives emergent hocket — equilibrium max load per resource **1.00** vs 1.43 / 1.87 / 2.13 from a random start at 3 / 4 / 5 voices; (iii) the price of anarchy $\Phi(\text{worst NE})/\Phi(\text{OPT})$ measures the cost of selfishness (worst 1.083, mean 1.027; 45–69 distinct pure equilibria by brute force). Tonality is a *private incentive*, not a constraint — a voice gravitates to the tonic because it pays. Variants: fictitious play, logit/quantal response (strategy entropy 9.94→3.81 nats over $\lambda=0\to20$), correlated equilibrium (conductor signal), and the zero-sum Xenakis *Duel* case, which has no potential and must be solved as an LP. Anti-central-planner to 056 SCCC / 064 MRFCC / 078 IMEC / 097 MaxEnt-C: the global energy is a theorem about individual incentives and the optimisation is performed by the voices themselves. |
```

Post-patch checks on this row: **10 cells** (awk field count), **0** occurrences of `\\` (single-escaped LaTeX preserved), no `||` prefix, table continuity preserved (next line is the blank line before `# Maximum Entropy Composition (MaxEnt-C) (Method 097)`).

## 2. Classification detail

| column | value | why |
|---|---|---|
| Layer | **concrete** | Every round resolves to a strategy profile and every voice's strategy is expanded into real `MusicEvent(pitch, volume, start_tick, end_tick)` inside a UnitMatrix cell. An *optional* abstract pre-pass exists — the pure-equilibrium set is finite (45–69 distinct) and can be exported as a weighted verticality pool to `rules/subset_network.py` — but the descent path, which is what makes the music, is concrete-only. |
| Paradigm | **Rules-Based** (strategic) | No RNG in the default mode beyond seeded tie-breaking, no fitness, no simulation, no learning. It is a *distinct family* from the other constraint methods because the optimisation is distributed: there is no global objective; each voice minimises its own cost, and the global energy is a theorem about those incentives. |
| Primary elements | Pitch, Rhythm, Harmony, Structure, Texture | All five: pitch = resource pitch classes + tonal private term; rhythm = metric-slot resources + convex congestion (hocket); harmony = the profile and Φ; structure = rounds and payoff discontinuities; texture = V, w₂, λ, PoA. |
| Tonal gravity | **Moderate (Incentive-guided)** | Tonality is a private payoff term (distance from the section chord), never a hard constraint. A voice may leave the chord if the congestion saving outweighs the tonal penalty — which is exactly the behaviour that produces non-chord tones at the right moments. |
| Metric binding | **Grid-Locked** | Resources *are* metric slots. Rubato/swing cannot be expressed and must be applied afterwards by `transformers.humanize` (which preserves zero-drift); putting timing jitter into the payoff would invalidate the verified potential. |
| Memory depth | **Local / Round** | State = the current profile (best response) or the empirical play history (fictitious play). No macro-form memory: form is a sequence of independent rounds differing only in payoff table. |
| Time complexity | $\mathcal{O}(I \cdot V \cdot \lvert S \rvert \cdot R)$ | One cost evaluation is $\mathcal{O}(\lvert s_i \rvert + R)$; one sweep is $V$ such evaluations; $I$ sweeps to convergence. Measured $I \le 5$. Brute-force equilibrium enumeration is $\mathcal{O}(\lvert S \rvert^V)$ — exponential, capped at $V=4$ in the demos. |

## 3. Verified numbers (real runs, no estimates)

**Theorem checks** — `gtbrc_verify.py`, 380 best-response runs total:

| check | result |
|---|---|
| improving moves that raise Φ (exactness violations) | **0** |
| runs terminating at a pure NE (0 profitable deviations) | **200/200** and **30/30** in each of 6 configurations |
| sweeps to convergence | mean 1.93–2.53, **max 5** |
| improving moves | mean 3.1, max 5 |
| distinct pure NE (brute force over all 12ᴿ profiles) | 45 (4 bands × 16 slots, V=4); 15 / 30 / 69 for V=2/3/4 at 3 bands × 8 slots |
| price of anarchy Φ(worst NE)/Φ(OPT) | **1.083** worst, 1.027 mean (V=4, 3 bands); 1.000 in the other five configurations |
| max load per (band, slot) resource, equilibrium vs random start | **1.00** vs 1.43 / 1.87 / 2.13 for V = 3 / 4 / 5 |
| logit strategy entropy, λ = 0 → 20 | 9.940 → 3.807 nats (monotone) |

**Engine demo** — `gtbrc_demo.py`, 4 voices (Bass/Trumpet/String ensemble/Flute) × 4 sections × 2 bars at 96 BPM, 16 slots × 240 ticks, chords Cmaj7 → Fmaj7 → Ebmaj7 → G7, w₁=1.0, w₂=1.5:

```
section A: sweeps=2  Phi 46.0 -> 36.5   (2 improving moves)
section B: sweeps=2  Phi 53.5 -> 29.5   (4)
section C: sweeps=2  Phi 48.5 -> 29.5   (4)
section D: sweeps=4  Phi 53.5 -> 29.5   (4)
validate: True OK
midi gtbrc_demo.mid bytes=494 notes=38 duration=20.0s
preflight_check.py: COMPLIANT
```

Note the emergent structural fact: section A settles at Φ = 36.5 while B, C and D all settle at 29.5 — the opening is the one section that cannot fully resolve *given the payoff*, and that reading was not designed in.

## 4. Novelty argument (why this is not a duplicate)

Checked the whole 001–122 table plus a full-text grep for `nash|game theor|payoff|best.response|equilibri`: **no game-theoretic method exists** (the only hits are the physical/statistical "equilibrium" of 064 MRFCC and 078 IMEC, i.e. thermodynamic equilibria of a globally given energy). Nearest neighbours and the distinctions:

- **056 SCCC** — species counterpoint as *one* agent enforcing hard rules: a central planner.
- **064 MRFCC / 078 IMEC** — a global energy is assumed a priori and sampled by MCMC: central sampler, thermodynamic equilibrium.
- **055 SAMC / 097 MaxEnt-C** — a single optimiser over a global objective.
- **041 ACOPF / 117 PSOC / 003 Genetic** — cooperative swarm/evolution with a shared fitness.
- **062 RLPOC / 063 MCTS-GC** — one decision-maker searching.
- **050 OTVL** — a single global transport optimum.
- **GTBRC** — *no* global objective: utilities are owned by the voices, the potential is derived, termination is a theorem (FIP), and the price of anarchy is a measurable compositional quantity. Historically rooted in Xenakis's *Duel* / *Strategie*, which delegated the game to live performers and never formalised the composer's side.

## 5. Quirks / pitfalls hit during this job

1. **A real bug that nearly produced a false negative.** The first verifier counted the mover's own contribution twice in `load_r` while computing the cost of the *current* strategy. Costs were then inconsistent with Φ, exactness broke silently, and the dynamics cycled: **0/200 runs** reached an equilibrium, all hit the 5000-sweep cap, **500 576** "potential-decrease" observations. After excluding the mover from the load, 200/200 converged in ≤5 sweeps with 0 violations. Lesson recorded in the method's Pitfalls #1: always assert $\Delta\Phi = \Delta c_i$ per move.
2. **Sign of the Lyapunov argument.** With costs (not utilities), improving moves *decrease* Φ. The first monotonicity check was written as "Φ must increase" and reported violations that were in fact the correct behaviour; the check now asserts "no increase" and that improving moves are strict decreases.
3. **`_unit_from_events` is mandatory** for the last cell: a voice may have no onset in the final slot, and without the terminal landmark the zero-drift gate fails. Padding to `section_len` fixed it.
4. **Engine API drift:** `MidiInstrument` has only a handful of members (no `CELLO`/`VIOLA`/`TROMBONE` — use `BASS`, `TRUMPET`, `STRING_ENSEMBLE`), and `UnitMatrixComposer.set_unit` takes integer `(row, col)`; use `fill_voice_section(name, section, unit)` for name-addressed cells. The first draft used the wrong names and would have raised at runtime (caught by lint, not by the engine).
5. **Table-cell pipe hazard:** `|S|` inside the summary row would split the table. Written as `\lvert S \rvert`. Same reason `\lvert s_i \rvert` replaced `|s_i|` in the standalone file.
6. **PoA is boring when the game is cooperative.** Five of six configurations measured PoA = 1.000 exactly; only the crowded 4-voice/3-band case showed 1.083. Reported honestly rather than tuned into a nicer number — it is a real property of congestion games with generous resource supply.
7. **Web access:** the environment has no `web_search` tool; the reference set was verified by fetching Wikipedia summaries over `curl` (potential games: Monderer–Shapley 1996 confirmed). All game-theory citations are classical and their content is standard; the Xenakis *Duel*/*Strategie* facts come from *Formalized Music* (1971) and are unchanged since method 025's sources.
8. **Heredoc/`execute_code` not used** for the DB writes: section written with `write_file`, appended with `cat >>`, temp file removed with `rm`. Summary row inserted with the `patch` tool and re-read/verified afterwards.

## 6. Complete method section appended to `methods_db.md` (verbatim, lines 27703–27809)

# Game-Theoretic Best-Response Composition (GTBRC) (Method 123)

### Source

Game theory: von Neumann, J. & Morgenstern, O. (1944). *Theory of Games and Economic Behavior.* Princeton University Press. — Nash, J. F. (1950). "Equilibrium points in n-person games." *PNAS* 36(1), 48–49; Nash, J. F. (1951). "Non-cooperative games." *Annals of Mathematics* 54(2), 286–295. — Brown, G. W. (1951). "Iterative solution of games by fictitious play." In *Activity Analysis of Production and Allocation* (Koopmans, ed.), Wiley, 374–376. — Robinson, J. (1951). "An iterative method of solving a game." *Annals of Mathematics* 54(2), 296–301 (fictitious play converges in zero-sum games). — Rosenthal, R. W. (1973). "A class of games possessing pure-strategy Nash equilibria." *International Journal of Game Theory* 2(1), 65–67 (congestion games and the potential that carries his name). — Aumann, R. J. (1974). "Subjectivity and correlation in randomized strategies." *Journal of Mathematical Economics* 1(1), 67–96 (correlated equilibrium). — McKelvey, R. D. & Palfrey, T. R. (1995). "Quantal response equilibria for normal form games." *Games and Economic Behavior* 10(1), 6–38 (the logit rationality dial used below). — Monderer, D. & Shapley, L. S. (1996). "Potential games." *Games and Economic Behavior* 14(1), 124–143 (exact potential ⇔ finite improvement property). — Koutsoupias, E. & Papadimitriou, C. (1999). "Worst-case equilibria." *STACS '99*, LNCS 1563, 404–413 (price of anarchy). — Hart, S. & Mas-Colell, A. (2000). "A simple adaptive procedure leading to correlated equilibrium." *Econometrica* 68(5), 1127–1150 (regret matching). — Fudenberg, D. & Levine, D. K. (1998). *The Theory of Learning in Games.* MIT Press. — Roughgarden, T. (2005). *Selfish Routing and the Price of Anarchy.* MIT Press. — Young, H. P. (2004). *Strategic Learning and Its Limits.* Oxford University Press. — Shoham, Y. & Leyton-Brown, K. (2009). *Multiagent Systems: Algorithmic, Game-Theoretic, and Logical Foundations.* Cambridge University Press.

Musical lineage. Xenakis, I. (1971). *Formalized Music: Thought and Mathematics in Composition.* Indiana University Press — in particular the chapter on strategy, documenting *Duel* (1959) for two orchestras and *Strategie* (1959–62) for two orchestral teams, in which the ensembles are **players** who choose from payoff matrices of musical characteristics and an umpire scores the round. Those pieces are the direct precedent: the *performance* is a game. What no method in this catalogue has done is formalise the **composer's** side of that game — i.e. write the payoff matrix, solve it, and read the equilibrium out as the score. Related agent-based music systems (Eigenfeldt & Pasquier's *Kinetic Engine*; Blackwell's *swarm music*; Biles's *GenJam*) use agents but with a shared fitness or a jam-session protocol, not with individually owned utilities and an equilibrium concept. Game-theoretic listening: Huron, D. (2006). *Sweet Anticipation.* MIT Press (expectation as reward — the private utility of a tonal gesture); Lerdahl, F. (2001). *Tonal Pitch Space.* Oxford University Press (tonal attraction as a distance metric, used below as the pitch term of the private cost).

### Layer

**concrete** — every round resolves to a strategy profile, and each voice's strategy is expanded into real `MusicEvent`s (pitch, onset, duration, velocity) that fill the UnitMatrix cell. Nothing is left abstract; the game is resolved per (voice, section) and immediately realised. Feeds `generators/`.

An **abstract** pre-pass is natural: with the strategy catalogue and payoff weights fixed, the set of pure equilibria is a finite, enumerable object (45–69 distinct equilibria in the demos below), so the *equilibrium verticality pool* of a section can be exported to `rules/subset_network.py` as a weighted pool and used by any concrete method downstream. But the path of descent — which equilibrium you land in, and how you get there — is what makes the music, and that only exists at the concrete layer.

### Paradigm

**Rules-Based** (strategic). There is no randomness in the default pure-strategy mode (only seeded tie-breaking), no fitness landscape, no physical simulation and no learnt parameter. What makes it a distinct *family* rather than another constraint solver is the direction of the optimisation: 056 SCCC, 055 SAMC, 064 MRFCC and 097 MaxEnt-C all optimise **one global objective from the outside** — a central planner; GTBRC has **no global objective at all**. Each voice minimises its own cost, and the global "energy" (the potential) is a *theorem about the incentives*, not a design choice. That inversion is what gives the method its two unique products: a provable termination guarantee, and a quantitative measure of decentralisation (the price of anarchy) that no other method can express.

### Description

**Game-Theoretic Best-Response Composition (GTBRC)** treats the UnitMatrix as a non-cooperative game. Rows are **players** (voices), columns are **rounds** (sections), and a cell is the realised outcome of the equilibrium played in that round.

**The game.** A *resource* is an elementary musical slot $r = (b, t)$: a register band $b$ crossed with a metric slot $t$. This is the only place a voice can put an onset. Voice $i$'s pure strategy $s_i \in S_i$ is a finite **set of resources** plus the pitch content attached to them — i.e. a gesture (a rhythm in a register). Let $n_r(s) = |\{j : r \in s_j\}|$ be the load of resource $r$ under profile $s$. Voice $i$'s cost is

$$c_i(s) \;=\; \underbrace{\mathrm{priv}_i(s_i)}_{\text{own taste}} \;+\; \sum_{r \in s_i} c_r\bigl(n_r(s)\bigr), \qquad c_r(k) \;=\; w_1 k + w_2 k^2 .$$

$\mathrm{priv}_i$ is the voice's **private** cost — tessitura pull toward its home band, density preference, and distance of its pitch classes from the section's chord (so *tonal gravity is an incentive, not a constraint*). $c_r$ is the **congestion** cost: linear crowding plus a convex penalty for piling up. Costs are separable per resource and depend only on the load, so this is exactly Rosenthal's congestion game.

**The theorem.** Define the potential

$$\Phi(s) \;=\; \sum_i \mathrm{priv}_i(s_i) \;+\; \sum_r \sum_{k=1}^{n_r(s)} c_r(k).$$

Then for every player $i$ and every unilateral deviation $s_i'$,

$$c_i(s_i, s_{-i}) - c_i(s_i', s_{-i}) \;=\; \Phi(s_i, s_{-i}) - \Phi(s_i', s_{-i}),$$

i.e. the game is an **exact potential game** (Monderer–Shapley 1996). Two consequences follow immediately and are the reason this method is in the catalogue:

1. **Best-response dynamics terminates.** Every strictly improving move lowers $\Phi$ by exactly that amount; $\Phi$ is bounded below on the finite strategy space, so no cycle is possible and the process stops at a pure Nash equilibrium — the *finite improvement property*. There is no annealing schedule, no convergence criterion to tune, no risk of the generator wandering forever.
2. **$\Phi$ is a tension curve.** Because $\Phi$ is a scalar potential that decreases monotonically along the actual path taken by the music, the recorded sequence $\Phi(s^{(0)}), \Phi(s^{(1)}), \dots, \Phi(s^{\mathrm{NE}})$ *is* a harmonic tension curve with a meaning: it measures how much tension remains unresolved for the players. No other method in the catalogue produces a tension curve that is simultaneously a Lyapunov function of its own process.

**Verified invariants** (script `projects/Research/outputs/gtbrc_validate/gtbrc_verify.py`, exhaustive over the strategy space where feasible):

| property | statement | measured |
|---|---|---|
| exactness | no improving move ever raises $\Phi$ | 0 violations over all runs (40/40 + 30/30 × 6 configs) |
| termination | every run ends at a pure Nash equilibrium (0 profitable deviations) | 40/40 and 30/30 in every configuration |
| speed | sweeps to convergence | mean 1.93–2.53, **max 5** |
| improving moves | unilateral deviations before rest | mean 3.1, max 5 |
| multiplicity | distinct pure equilibria (brute force, 12⁴ profiles) | 45 (4 bands/16 slots) and 69 (3 bands/8 slots) |
| price of anarchy | $\Phi(\text{worst NE})/\Phi(\text{OPT})$ | **1.083** worst, 1.027 mean (4 voices, 3 bands); 1.000 elsewhere |
| hocket | max load on any (band, slot) resource, equilibrium vs random start | **1.00** vs 1.43 / 1.87 / 2.13 for 3 / 4 / 5 voices |
| rationality dial | logit (quantal-response) strategy entropy at $\lambda = 0 \to 20$ | 9.940 → 3.807 nats |

**Variants** (all four are the same game, different solution concepts — this is the method's parameter space):

- **Pure best response** (default): deterministic, seeded tie-breaking, converges in ≤5 sweeps.
- **Fictitious play** (Brown 1951; Robinson 1951): each voice best-responds to the empirical frequency of the others' past choices. Converges in zero-sum games; in potential games it converges to the equilibrium set. Slower, smoother, and it makes repeated sections *develop* rather than repeat.
- **Logit / quantal response** (McKelvey–Palfrey 1995): play $s_i$ with probability $\propto \exp(-\lambda\, c_i(s_i,s_{-i}))$. $\lambda = 0$ is uniform noise, $\lambda \to \infty$ is best response. This is the *rubato and risk* dial: intermediate $\lambda$ gives a voice that usually does the sensible thing but occasionally takes a bad-but-interesting gesture. (Measured entropy falls monotonically 9.940 → 3.807 nats as $\lambda$ goes 0 → 20.)
- **Correlated equilibrium** (Aumann 1974; Hart–Mas-Colell 2000 regret matching): a public randomising device — the "conductor" — correlates the voices' choices, which strictly enlarges the achievable set of stable sonorities and removes the coordination failures that pure NE multiplicity implies. Use this when the section must land on one specific verticality.
- **Zero-sum duel** (the Xenakis case): two voices, $u_1 = -u_2$, solved by linear programming for the mixed-strategy minimax. No potential exists (zero-sum games are harmonic, not potential, games), so best-response dynamics can cycle — this variant *must* be solved as an LP or by fictitious play, never by naive best response.

**Position in the catalogue.** 056 SCCC is a single agent enforcing species rules globally; 064 MRFCC and 078 IMEC sample a globally-defined energy by MCMC; 041 ACOPF and 117 PSOC optimise a shared fitness with a swarm; 062 RLPOC and 063 MCTS-GC search from one decision-maker's point of view; 097 MaxEnt-C fixes the least-committed distribution. GTBRC is the only method whose "energy" is *derived from individually owned utilities*, whose optimisation is performed by the voices themselves, and which therefore comes with a termination theorem and a measurable cost of selfishness. Its historical root (Xenakis's game pieces) is in the catalogue's blind spot precisely because those works delegated the game to live performers.

**Cost.** One cost evaluation is $\mathcal{O}(|s_i| + R)$; one sweep is $\mathcal{O}(V \cdot |S|)$ evaluations; termination needs $I \le (\Phi_0 - \Phi_{\min})/\delta$ sweeps with $\delta$ the minimum strict improvement (with integer-scaled weights, $\delta \ge 1/L$ for denominator $L$). In practice $I \le 5$. Brute-force verification of the equilibrium set is $\mathcal{O}(|S|^V)$ — exponential, which is why the demos cap $V$ at 4 (12⁴ = 20 736 profiles).

### Musical Elements Framework

**PITCH**: Pitch enters twice, at different levels. *Within* a strategy, each occupied slot carries a pitch class — sampled from the section chord (85 %) or a neighbour tone (15 %) — so a gesture is a melodic fragment, not just a rhythm. *Across* the profile, the private term $\mathrm{priv}_i$ charges each voice for its distance from the section's chord, so **tonal gravity is an individual incentive**: a voice gravitates to the tonic because gravitating *pays*, not because a rule forbids leaving. The equilibrium condition is a precise definition of good voice leading that the catalogue previously only had informally: *a voicing is stable iff no single voice can improve its own situation by moving alone* — which is exactly the local-optimality condition 050 OTVL and 011 graph search approximate globally. Because the stable points are local optima of $\Phi$, not global ones, GTBRC produces voicings that are *locally* impeccable and *globally* surprising — measured price of anarchy 1.083 means up to 8.3 % worse than a benevolent planner would choose, which is a musically audible amount of "character".

**RHYTHM**: The resource set is (register band × metric slot), and the quadratic congestion term $w_2 k^2$ makes doubling expensive. The result is **emergent hocket**: measured max load on any single (band, slot) resource is exactly **1.00** at equilibrium versus 1.43 / 1.87 / 2.13 for 3 / 4 / 5 voices from a random start — the voices partition the metric grid among themselves without any interlocking rule being written. $w_2$ is therefore a compositional dial from *heterophony* ($w_2 \to 0$: everyone piles onto the downbeat, which is what unison playing is) through *polyphony* to *total interlock* ($w_2$ large: one voice per slot, the texture of a hocket or a kotekan). Because the resource is a metric slot, the method is grid-locked by construction: rubato and swing must be applied afterwards by `transformers.humanize`, never inside the payoff (a humanised payoff is no longer a potential game).

**HARMONY**: A chord is a **strategy profile**, and the harmonic energy is $\Phi$. Three consequences. (i) *Resolution is provable*: within a section, $\Phi$ decreases monotonically, so the music is always heading somewhere and always arrives. (ii) *Tension is measurable*: $\Phi(s) - \Phi(s^{\mathrm{NE}})$ is the exact amount of unrealised improvement available to the ensemble — a tension value with units, recorded for free at every step (demo: section A descends 46.0 → 42.5 → 36.5; B 53.5 → 48.0 → 43.0 → 38.0 → 29.5; C 48.5 → … → 29.5; D 53.5 → … → 29.5). (iii) *Tonal function is a payoff discontinuity*: modulation is a change of the private chord term at a section boundary, which moves the equilibrium and therefore the harmony, without any voice "deciding" to modulate. Consonance is not enforced pairwise — the price of anarchy is the precise statement of how much consonance is lost by letting voices be selfish.

**STRUCTURE**: Sections are **rounds**, and the seam between sections is the only place the music may jump, because inside a round the dynamics is a descent and descents do not leap. Form is a *path of equilibria*: the sequence $\Phi(s^{\mathrm{NE}}_1), \Phi(s^{\mathrm{NE}}_2), \dots$ is the macro-tension curve, and a section whose equilibrium potential is high is a section that has not resolved (in the demo, A settles at 36.5 while B, C, D all settle at 29.5 — A is structurally the "unresolved" opening, and that fact was not designed, it fell out of the payoff). Because pure equilibria are multiple (45–69 measured), repeated sections can be *literally* repeated by fixing the start profile and seed, or *developed* by changing only the start profile — the same game, a different basin, a different but equally stable verse.

**TEXTURE**: The number of players $V$, the congestion weight $w_2$ and the rationality $\lambda$ are three independent texture dials that all mean something: $V$ is polyphony, $w_2$ is the pressure toward interlock (measured load spreading), and $\lambda$ is *how consistently each voice pursues its own interest* — at $\lambda \to 0$ the texture dissolves into statistically independent gestures (entropy 9.940 nats ≈ maximum), at $\lambda \to \infty$ it freezes into the equilibrium (3.807 nats). The price of anarchy is the fourth and most unusual dial: it quantifies how "individualistic" the result sounds, because it is literally the ratio between what selfish voices achieve and what a cooperative planner would have achieved.

### UnitMatrix Integration (Voices & Sections)

**Voices (rows)** = players. Each row owns a strategy catalogue $S_i$ (12 gestures in the demos) and a private cost function, i.e. a tessitura, a density taste and a pitch preference. The row's matrix index is its player index; a row's instrument is what makes its strategies legible (the same strategy played by flute and by bass is not the same gesture, so timbre is the reason to keep the register bands wide).

**Sections (columns)** = rounds. Each column has its own payoff table (chord for the private term, congestion weights, strategy catalogue seed) and its own resolved profile. Column length is free — it is the number of slots $T$ times the slot duration — unlike 122 HCSC where section length is forced by $(d,k)$. The natural default is 16 eighth-note slots (2 bars at 4/4).

**Cells (MusicUnit)** = the events of voice $i$ in section $r$, expanded from $s_i^{r,\mathrm{NE}}$:

1. Build the resource set $\{(b,t)\}$ and pitch list from the equilibrium strategy; onset $= t \cdot \text{slot\_ticks}$.
2. Duration = distance to that voice's next onset (clipped to a maximum, e.g. 4 slots) — the rest of the slot is silence, which is what makes the hocket audible.
3. Emit `MusicEvent(pitch = base[b] + pc, volume, start_tick, end_tick)` per onset.
4. Pad with `_unit_from_events(events, section_len)` so the terminal landmark lands exactly on the section seam — required, because a voice may have no onset in the last slot and the zero-drift gate will otherwise fail.
5. Record $\Phi$ at every improving move to produce the section's tension curve.

**Verified engine integration** (`projects/Research/outputs/gtbrc_validate/gtbrc_demo.py`): 4 voices (Bass/Trumpet/String ensemble/Flute) × 4 sections × 2 bars at 96 BPM, 16 slots of 240 ticks, chords Cmaj7 → Fmaj7 → Ebmaj7 → G7, $w_1 = 1.0$, $w_2 = 1.5$: `validate() -> True: OK`, 494-byte / 20.0 s MIDI, 38 notes, 16 cells, 4 sections resolved in 2, 2, 2 and 4 sweeps, monotone $\Phi$ descent in every section, `preflight_check.py` COMPLIANT.

Candidate code path: `generators/game_theoretic.py` (class `GameTheoreticComposer`, methods `build_strategies()`, `resource_loads()`, `cost()`, `potential()`, `best_response()`, `fictitious_play()`, `logit_response()`, `realize_profile()`), consumed by `workflows/unitmatrix_composer.py`; the abstract pre-pass (equilibrium set enumeration + $\Phi$ weighting) feeds `rules/subset_network.py`.

### Pitfalls

1. **The potential is not free — verify it.** Exactness holds only for the congestion form $c_i = \mathrm{priv}_i(s_i) + \sum_{r \in s_i} c_r(n_r)$. Add one genuine *pairwise* term (e.g. a consonance table on the interval between two voices' pitch classes) and the game is generally no longer potential: improving moves can cycle forever. This is not hypothetical — the first implementation of the verifier here had an off-by-one in the load (own contribution counted twice), which silently destroyed exactness: 0/200 runs reached an equilibrium, every run hit the 5000-sweep cap with 500 576 potential-decrease violations. After fixing the load to exclude the mover, 200/200 runs converged in ≤5 sweeps with 0 violations. **The test is cheap: assert $\Delta\Phi = \Delta c_i$ on every move, in every run.** If you need pairwise interval terms, move them into the private term (per-voice interval preference against the *chord*, not against another voice) or accept that you are no longer in this method.
2. **Equilibrium is not beauty.** The method guarantees stability with respect to the payoff you wrote. A payoff with the wrong weights converges perfectly to bad music. Write the payoff, audition, rewrite the payoff — the game is a synthesis of your preferences, not a substitute for them.
3. **Equilibrium multiplicity defeats literal repetition.** 45–69 distinct pure equilibria in the demos means the same section played twice from different starts will differ. That is a feature for development and a bug for a chorus that must repeat exactly: pin the start profile and the RNG seed for repeats.
4. **$w_2 = 0$ is not a neutral default.** With no congestion term every voice converges onto the same attractive slot (max load jumps from 1.00 to the random baseline 1.4–2.1) — the texture collapses to unison. Conversely $w_2$ too large drives voices out of their tessitura to escape each other, producing correct-but-unidiomatic spacing. Keep the private tessitura term strong enough to preserve identity.
5. **Pure NE is a coordination failure waiting to happen.** Different equilibria are not equally good (measured worst/opt ratio 1.083), and best response cannot tell them apart. If the section must land on a specific verticality, use the correlated-equilibrium variant (a conductor signal) — that is exactly the problem correlated equilibrium was invented for.
6. **Zero-sum is a different beast.** The Xenakis *Duel* case has no potential; naive best response cycles. Solve it as an LP (mixed minimax) or by fictitious play, and expect slow ($\mathcal{O}(1/\sqrt{t})$) convergence — never run it inside a real-time loop.
7. **Grid-lock is structural.** Resources are metric slots, so the method cannot express rubato, swing or expressive timing. Humanise afterwards (`transformers.humanize.humanize_composer`), which preserves zero-drift; do not put timing jitter into the payoff, because then the game is no longer the game you verified.
8. **Tie-breaking must be deterministic.** With float costs, near-ties are common; unseeded tie-breaking makes the piece irreproducible and the golden-hash tests impossible. Use integer-scaled costs, an explicit epsilon, and a seeded RNG for tie order.
9. **Cost of verification is exponential.** Enumerating all pure equilibria is $\mathcal{O}(|S|^V)$; $V = 6$ with 12 strategies is 3 M profiles and $V = 8$ is 430 M. Verify the potential on sampled paths, and reserve exhaustive enumeration for $V \le 4$.
