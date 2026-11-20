# Method 147 — Metric Modulation Tempo-Network Composition (MMTC)

- **ID:** 147
- **Paradigm:** Rules-Based (exact rational arithmetic; no stochastic component — the only "choice" is the planned ratio chain, seeded like 144–146)
- **Layer:** concrete (LAYER_ARCHITECTURE.md) — emits MusicEvents with onsets/durations in ticks on rational pulse grids, i.e. fills UnitMatrix cells; optional tempo map for mode A
- **Family:** rhythm/tempo. Siblings: 012 Euclidean (hit distribution at one tempo), 026 DPSM (phase offset at one tempo), 144 LSPC (gap structure in a block), 018 Schillinger (resultant rhythms). MMTC is the only method whose parameter is the **pulse rate itself**.
- **One-liner:** compose form as a walk on the tempo lattice — every station tempo is a rational multiple of the previous one ($T_2/T_1 = m/n$, justified by an audible pivot note value), so the piece is a chain in $\mathbb{Q}^+$, a closed chain is a reprise by tempo alone, and rational coincidence forces every modulation seam to be a point where all voices already agree.

---

## 1. The pivot law

A metric modulation is a tempo change with a warrant: a note value heard before the change is *made equal* to a note value after it. If $n$ values of the pivot at tempo $T_1$ occupy the same span as $m$ values at $T_2$:

$$n\,d_1 = m\,d_2, \qquad d_i = \text{(pivot length in beats)}\cdot\frac{60}{T_i}.$$

With the same pivot value on both sides ($d_1 = d_2$ as note values, different durations):

$$\boxed{\frac{T_2}{T_1} = \frac{m}{n}}$$

which is the standard performance formula "new tempo / old tempo = number of pivot values in the new measure / number in the old measure".

Carter's worked example (*Eight Etudes and a Fantasy*, Fantasy mm. 16–17): 2 half notes at quarter = 84 ↔ 3 half notes. $T_2 = 84\cdot 3/2 = 126$. Check the spans: $2\times 2$ beats at 84 = 2.857 s; $3\times 2$ beats at 126 = 2.857 s. And $126 = 84\cdot 3/2$ is exactly dotted-quarter = 84.

**Consequences.** (i) Every modulation is a rational multiplier — the technique is arithmetic. (ii) The direction matters: $m$ counts in the *new* unit. Inverting gives 56, a plausible but wrong answer. (iii) The pivot must be *audible on both sides*; a pivot that only exists in the arithmetic is a silent modulation (the third of Wikipedia's three performance challenges).

## 2. The tempo lattice

Tempi form the multiplicative group $\mathbb{Q}^+$; in $\log T$ it is the free abelian group on the primes. Restricting to pivots with small factors gives the alphabet

$$A_K = \{\,n/m : 1\le n,m\le K\,\},\qquad |A_K| = 1 + 2\sum_{q=2}^{K}\varphi(q),$$

so $|A_7| = 1 + 2(1+2+2+4+2+6) = 35$.

**Tempo classes mod doubling.** $T\mapsto 2T$ is the tempo analogue of octave equivalence ("the same music twice as fast"). Reducing each ratio to its odd part ($r = 2^k\cdot \text{odd}/\text{odd}$) collapses $A_7$'s 35 ratios onto **13** classes = the odd/odd fractions of $\{1,3,5,7\}$. Thus $3/2$ and $3/1$ are one class. Two distinct closure notions follow:

- **exact cycle:** $\prod_i r_i = 1$ — the tempo literally returns;
- **octave cycle:** $\prod_i r_i = 2^k$ — returns to the same tempo class, sounding like a reprise at a different speed.

**Cycle counts over $A_7$** (brute force, verified twice): 469 chains of length 3 and 10 459 of length 4 satisfy $\prod r_i = 1$. The length-3 count was re-derived independently as the number of pairs $r,s\in A_7$ with $(rs)^{-1}\in A_7$ — 469 both ways. Rotation is not a free action on chains, so 469 is *not* a multiple of 35 (469 = 13·35 + 14) — a small trap for anyone expecting symmetry by rotation.

**The tempo graph.** Vertices = tempi in $[T_{\min}, T_{\max}]$; edges = ratios in $A_K$; edge weight $|\log r|$ (perceived abruptness). Chain design = path search; exact return = cycle constraint; all chains of length $d$ = $\mathcal{O}(K^d)$ enumeration, or Dijkstra at $\mathcal{O}(V+E)$ per query.

## 3. Two realisation modes

| | mode A — tempo map | mode B — tuplet notation |
|---|---|---|
| MIDI | $k$ `set_tempo` events | one tempo |
| pulse | unchanged ticks | $L = \mathrm{TPB}\cdot m/n$ ticks |
| seconds | scale by $T_1/T_2$ | unchanged |
| expresses | sequential modulation, whole ensemble | simultaneous tempi, per-voice grids |
| zero drift | automatic (ticks untouched) | needs integer $L$ and a common section multiple |

Numeric check: 480 ticks = 0.500 s at 120 bpm, 0.333 s at 180 bpm — ticks are tempo-map invariant, seconds are not.

**Integrality constraint in mode B.** $L\in\mathbb{Z}$ requires $n \mid \mathrm{TPB}$. At TPB 480: $n \in \{2,3,4,5,6,8,10,12\}$; 7, 9, 11-tuplets are impossible. Fix by raising TPB: 3360 = $2^5\cdot3\cdot5\cdot7$ covers 7; 10080 = $2^5\cdot3^2\cdot5\cdot7$ covers 7 and 9.

## 4. Coincidence lemma (and why zero drift is the same law)

**Lemma.** For rationals $a_i/b_i$ in lowest terms, the least positive common multiple is

$$\operatorname{lcm}_{\mathbb{Q}}\!\left(\frac{a_1}{b_1},\dots,\frac{a_k}{b_k}\right) = \frac{\operatorname{lcm}(a_1,\dots,a_k)}{\gcd(b_1,\dots,b_k)}.$$

*Proof.* $x$ is a multiple of $a_i/b_i$ for all $i$ iff $x\,b_i/a_i\in\mathbb{Z}$ for all $i$. With $D=\operatorname{lcm}(a_i)$ and $G=\gcd(b_i)$, $x=D/G$: then $x b_i/a_i = (D/a_i)(b_i/G)\in\mathbb{Z}$, and any smaller $x$ fails for some $i$. $\square$

Verified: $\operatorname{lcm}(3/2,4/3)=12$ (= 8 pulses of 3/2 and 9 of 4/3); $\operatorname{lcm}(2/3,4/5)=4$; $\operatorname{lcm}(1/2,1/3)=1$. Demo: $\operatorname{lcm}(480,320,360,960)=2880$ ticks = 6 beats, holding 6/9/8/3 pulses.

**Corollary (zero drift).** A row's units must sum to the section length. If a section is tiled by pulses $L_{v}$ for each active voice $v$, the section length $S$ must be an integer multiple of every $L_v$, i.e. $S = m\cdot\operatorname{lcm}_{\mathbb{Q}}(L_v)$. So **the engine's zero-drift invariant is exactly the coincidence condition**: a modulation may only be cut where all voices coincide. In practice, choose $S$ first, then the ratios must tile it — the invariant reaches back and constrains the compositional choice.

**Carter's 216:175.** Coprime, so the least coincidence is $216\cdot175 = 37\,800$ unit pulses (the maximal period for numbers of that size). At a ~32 ms unit that is 20.16 min — matching Wikipedia's "coincides at only two points over its 20+ minutes". Near-coprime pairs are chosen *because* they maximise the period; structural polyrhythm is arithmetic theatre.

## 5. Reference implementation sketch

```python
"""generators/metric_modulation.py — MMTC (proposed)."""
from fractions import Fraction
from math import gcd, lcm

def ratio_alphabet(K: int) -> set[Fraction]:
    return {Fraction(n, m) for n in range(1, K + 1) for m in range(1, K + 1)}

def pulse_ticks(ratio: Fraction, tpb: int) -> int:
    """Tempo ratio n/m -> pulse length in ticks (inverse of tempo)."""
    L = Fraction(tpb, 1) / ratio
    if L.denominator != 1:
        raise ValueError(f"ratio {ratio} does not tile TPB={tpb}")
    return int(L)

def q_lcm(pulses) -> Fraction:
    return Fraction(lcm(*[p.numerator for p in pulses]),
                    gcd(*[p.denominator for p in pulses]))

def tempo_chain(t0: Fraction, ratios) -> list[Fraction]:
    out, t = [t0], t0
    for r in ratios:
        t *= r
        out.append(t)
    return out

def is_cycle(ratios) -> bool:
    p = Fraction(1)
    for r in ratios:
        p *= r
    return p == 1

def is_octave_cycle(ratios) -> bool:
    p = Fraction(1)
    for r in ratios:
        p *= r
    return p.denominator == 1 and (p.numerator & (p.numerator - 1)) == 0

def tile_station(section_ticks: int, pulse: int, pitches, velocity=90):
    """One cell: n = S/L events of length L, closing exactly on the seam."""
    assert section_ticks % pulse == 0
    n = section_ticks // pulse
    return [(pitches[k % len(pitches)], k * pulse, (k + 1) * pulse, velocity)
            for k in range(n)]

def plan(ratios, tpb=480, base_bpm=120, section_ticks=None):
    """Resolve a ratio chain into stations; derive the minimal valid section."""
    tempi = tempo_chain(Fraction(base_bpm), ratios)
    pulses = [pulse_ticks(r, tpb) for r in ratios]
    if section_ticks is None:
        section_ticks = int(q_lcm([Fraction(p) for p in pulses]))
    assert all(section_ticks % p == 0 for p in pulses)
    return {"tempi": tempi, "pulses": pulses, "section_ticks": section_ticks}
```

Integration: emit one `MusicUnit` per (voice, station) from `tile_station`, append the terminal pitch-0 pad event, `validate()`, then `to_midi()`. For mode A pass `tempo_map=[(station_start_tick, bpm), ...]` — currently `UnitMatrixComposer.to_midi` writes a single `set_tempo` at tick 0 (lines 205–213), so that parameter is the one required engine change.

## 6. Verification

`_web147_mmc/verify_mmc_math.py` — **31/31 pass**:
pivot law (84·3/2 = 126; spans 2.857 s = 2.857 s), dotted-quarter identity, tempo cycle 84→126→168→84, rational lcm trio, coincidence divisibility, gcd(216,175) = 1 and 216·175 = 37 800 ≈ 20.16 min, zero-drift section 2880 with 6/9/8 pulses, $|A_7| = 35$, 469/10 459 cycles, 13 tempo classes, tick invariance, TPB divisibility, TPB 3360/10080 fixes.

`_web147_mmc/compose_mmc_demo.py` — 3 voices × 4 stations (120 → 180 → 240 → 120), 2880-tick sections, `validate() → True "OK"`, total 11 520 ticks, MIDI 514 B, WAV 3.39 MB. Outputs in `projects/Research/outputs/mmc_147/`.

## 7. References

- Wikipedia, "Metric modulation" — https://en.wikipedia.org/wiki/Metric_modulation (fetched 2026-11-20). Definition, Goldman attribution, Carter's preference for "tempo modulation", "proportional tempi", the determination formula, the 84 → 126 example, mutually prime metres, the three performance challenges, repertory list, Benadon's tempo networks / beat subdivision spaces.
- Wikipedia, "Elliott Carter" — https://en.wikipedia.org/wiki/Elliott_Carter (fetched 2026-11-20). Stratification ("each instrumental voice … its own set of tempos"), structural polyrhythm as a formal device, *Night Fantasies* 216:175 coincidence over 20+ minutes, the continuous acceleration/deceleration aesthetic.
- Benadon, F., "Towards a Theory of Tempo Modulation," *Perspectives of New Music* 42/1 (2004) — cited as attributed by the Wikipedia article; paywalled, no page-level claims taken.
- Carter, E., *Collected Essays and Lectures, 1937–1995* (Rochester, 1997) — source of the "time screen" / tempo-stratification writings referenced indirectly above.
- Musicom engine: `workflows/unitmatrix_composer.py` (zero-drift gate), `structures/metrical.py` (metrical tree, per-level periods in seconds), `workflows/unitmatrix_composer.py::to_midi` (single `set_tempo` — the mode-A gap).

## 8. Pitfalls (short list)

1. TPB divisibility: mode B cannot express a 7-tuplet at TPB 480; raise TPB or restrict the alphabet.
2. Ratio direction: $T_2/T_1 = m/n$; pulse is the inverse ($L = \mathrm{TPB}\cdot m/n$).
3. Constant-tempo export makes a modulation inaudible; choose mode up front.
4. Octave closure ($\prod r = 2^k$) ≠ exact closure ($\prod r = 1$).
5. Pivot must exist in the sounding texture on both sides.
6. A global tempo map cannot express simultaneous tempi — stratification needs per-voice grids.
7. Apply humanisation after the station grid; jitter must not cross a seam.
