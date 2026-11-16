# Report — Method 144: Langford–Skolem Distance-Pairing Composition (LSPC)

**Job:** music-research cron (one new method per run) · **Date:** 2026-11-16
**Primary record:** this file · **DB:** `projects/Research/CompositionMethods/methods_db.md`
**Status:** COMPLETE — method researched, verified with a running prototype, appended to DB, summary row added, standalone file written.

---

## 1. Identity block

| field | value |
|---|---|
| **Method ID** | **144** |
| **Name** | Langford–Skolem Distance-Pairing Composition |
| **Acronym** | LSPC |
| **Paradigm** | **Rules-Based** (deterministic combinatorial construction; seeded solution choice is the variation axis) |
| **Layer** | **concrete** (fills UnitMatrix cells with resolved `MusicEvent`s; zero-drift grid applies) |
| **One-line description** | Composes a block as a perfect partition of $2n$ metric slots into $n$ pairs, where the two statements of symbol $k$ are separated by exactly $k$ intervening slots (Langford, iff $n\equiv0,3\bmod4$) or exactly $k$ slots (Skolem, iff $n\equiv0,1\bmod4$), hooked Skolem covering $n\equiv2,3$ — every slot filled once, every return delay $\{2..n{+}1\}$ present exactly once. |
| **Candidate code path** | `generators/langford_pairing.py` (new module: `family(n)`, `solve(n, fam, seed)`, `audit(seq, n, fam)`, `realize(...)` matrix fill). Exact-cover (Knuth Algorithm X / dancing links) for production; the prototype's largest-first backtracker is the reference. |
| **Standalone file** | `projects/Research/CompositionMethods/method_144_LSPC.md` |
| **Prototype dir** | `projects/Research/CompositionMethods/_web144_lspc/` |

## 2. ID resolution (dynamic, not assumed)

- Summary-table scan `grep -oP '^\| \*\*\K[0-9]{3}(?=\*\*)'` → max **143**; 142 numeric rows present.
- Standalone-file cross-check `method_*.md` / `report_*.md` → max **143** (`method`+`report` for 143; `_web143` dir exists).
- Gap analysis (`awk` run-length over sorted IDs): `001-057`, `059-143` — only 058 missing inside the range, so the file scan and table agree.
- **Next free ID = 144.** No 144 anywhere (verified before writing).
- Note: the DB also holds **SP-*** (sound-production) and **HC-*** (human-craft) numbering in separate ranges; SP-143 and HC-093 were appended by *sibling cron agents while this job ran* — see §8 quirks.

## 3. Line counts

| point | `wc -l methods_db.md` |
|---|---|
| at job start (first read) | 31 665 |
| at section-append time | **31 747** (grew in between: sibling agents appended SP-143 + HC-093) |
| after appending method 144 section | **31 839** (+92: 2 blank separator + 90 section lines) |
| after inserting the summary-table row | **31 840** (+1) |
| **my delta** | **+93 lines** |

## 4. Summary-table row (as inserted, line 154)

```
| **144** | concrete | Langford–Skolem Distance-Pairing Composition (LSPC) | **Rules-Based** | Pitch, Rhythm, Harmony, Structure, Texture | Weak (Register-ladder only; no functional harmony — the symbol is a lag, not a scale degree) | Grid-Locked (slot grid; one slot = one subdivision) | Local (pair span ≤ $n+1$ slots) | $\mathcal{O}(2^n \cdot n)$ bitset DP / exact cover; first solution 40–13 651 nodes at $n=15..32$; $\mathcal{O}(n)$ published constructions | Composes each block as a **distance-pairing sequence**: a perfect partition of $2n$ slots into $n$ pairs where symbol $k$'s two occurrences are $k+1$ slots apart (Langford, exists iff $n\equiv0,3 \pmod 4$) or $k$ slots apart (Skolem, iff $n\equiv0,1 \pmod 4$); hooked Skolem ($2n+1$ slots, one hook) covers $n\equiv2,3$ — the voice count selects the grammar, and **every $n$ is realizable**. Density is exactly 1.000 in the Langford/Skolem families ($2n$ events, 0 empty; hooked = exactly one hole, $2n/(2n+1)$) and the lag spectrum is $\{2,\dots,n+1\}$ complete, so the block is simultaneously a canon at every delay with each voice's re-entry on its own unique lag; $\sum$ lags $= n(n+3)/2$ (Langford) / $n(n+1)/2$ (Skolem). Counts match OEIS: $L(7)=52$, $L(8)=300$, $L(11)=35584 = 2\times$A014552; Skolem $n{=}8$: 504, $n{=}9$: 2656 = A004075. Reversal preserves the law, relabelling $k\mapsto n+1-k$ destroys it (verified). Interlacing ratio falls with $n$ (0.667 at $n{=}4$ → 0.394 at $n{=}12$) = the texture dial. Demo: 8×4 matrix, 16 events, validate OK, MIDI 375 B. Rainbow pair-tiling dual of 090 GRDC / 112 CADDC and the pair-case counterpart of 111 VTCC (OEIS names the Skolem case "super perfect rhythmic tiling with pairs"); first Langford/Skolem method in the DB. Feeds generators/langford_pairing.py. |
```

Classification columns, spelled out:

| column | value | rationale |
|---|---|---|
| Layer | concrete | emits resolved events into cells; slot grid is a tick grid |
| Paradigm | Rules-Based | hard combinatorial law + deterministic solver; RNG only picks *which* solution |
| Primary elements | Pitch, Rhythm, Harmony, Structure, Texture | rhythm/identity is the core; pitch/harmony arrive via the mapping; structure via the residue class; texture via interlacing |
| Tonal gravity | Weak | no functional harmony; only a registral ladder if the caller maps $k\to$ scale degree |
| Metric binding | Grid-Locked | slots are fixed subdivisions; block length $2n$ slots |
| Memory depth | Local | each row's obligation spans $\le n+1$ slots |
| Time complexity | $\mathcal{O}(2^n n)$ bitset DP / exact cover; $\mathcal{O}(n)$ published constructions | measured first-solution cost 40–13 651 nodes at $n=15..32$; naive search fails at $n=36$ |

## 5. Classification decision trail (DB de-duplication)

Grepped before choosing (hit counts in `methods_db.md`): `Costas` 22, `Golomb` 34, `Langford` **0**, `Skolem` 3 (all = "Bose–Skolem" in method 132 BIBDC), `tiling canon` 4 (method 111 VTCC), `maximally even` 9, `Sturmian` 26, `Christoffel` 58, `WFC` 16 (method 033), `Physarum` 6, `ant colony` 6, `Kuramoto` 9, `Penrose` 9, `Voronoi` 17.

- **033 WFCGS** already owns wave-function-collapse → the first candidate (WFC) was rejected as a duplicate.
- Adjacent distinct-difference designs **090 GRDC** (Golomb ruler) and **112 CADDC** (Costas array) exist; LSPC is the *pair-covering* dual (repeated labels at prescribed distances vs distinct distances between single marks), i.e. a genuinely different constraint object, and `Langford` had zero hits.
- **111 VTCC** (Vuza tiling canon) is the nearest tiling method; LSPC tiles with $n$ distinct 2-point tiles each used once (OEIS: "super perfect rhythmic tiling with pairs"), not with translates of one motif. Positioned explicitly in both DB section and standalone.
- Chosen paradigm **Rules-Based** (not Stochastic): the sequence space is enumerated deterministically; the seed only selects a solution.

## 6. Research provenance (sources fetched)

1. **OEIS A014552** (`curl https://oeis.org/search?q=id:A014552&fmt=text`, 2026-11-16): `0,0,1,1,0,0,26,150,0,0,17792,108144,...`, comment "a(n) > 0 iff n == 0 or 3 (mod 4)", cross-ref A176127 = 2·A014552, cites Priday 1959, Davies 1959, Simpson 1983, Knuth TAOCP 4A §7.1.1, Nordh 2008.
2. **OEIS A004075** (same fetch): Skolem counts `1,1,0,0,6,10,0,0,504,2656,...`; comment — *"Number of super perfect rhythmic tilings of [0,2n-1] with pairs"* (the musical framing citation).
3. **Wikipedia "Langford pairing"** (API extract + summary, rev. 2026-09-03): definition, $n=3$ example `2,3,1,2,1,3`, existence $n\equiv0,3$, exact-cover remark, references (Langford 1958, Skolem 1957, Nordh 2008, Knuth 2008).
4. Cited from the OEIS reference list (not fetched directly): Priday 1959 (necessity), Davies 1959 (construction), O'Keefe 1961 (hooked Skolem), Simpson 1983 (perfect/hooked Langford), Assarpour–Bar-Noy–Liu 2015 (arXiv:1507.00315, counting).

## 7. Verification (measured, not asserted)

Prototype scripts (all run with `$MUSICOM_PYTHON` = `/opt/data/micromamba/envs/musicom/bin/python`, Python 3.11.15) and their logs live in `_web144_lspc/`.

| # | check | result |
|---|---|---|
| 1 | Langford existence by exhaustive first-solution search, $n=1..12$ | exists exactly for $n\%4\in\{0,3\}$ — 12/12 |
| 2 | Langford solution counts | $L(3){=}2$, $L(4){=}2$, $L(7){=}52$, $L(8){=}300$, $L(11){=}35584$ = $2\times$A014552 (1,1,26,150,17792) exact |
| 3 | Skolem existence, $n=1..12$ | exactly $n\%4\in\{0,1\}$ — 12/12 |
| 4 | Skolem counts vs A004075 | $n{=}4$:6, 5:10, 8:504, 9:2656 exact; 0 for $n\equiv2,3$ |
| 5 | Hooked Skolem repairs the void | plain 0 / hooked > 0 at $n=2,3,6,7,10$; hook redundant for $n\equiv0,1$ |
| 6 | Perfect-cover audit | $2n$ slots, $2n$ events, 0 empty, density 1.000 (Langford/Skolem); hooked density $2n/(2n+1)$ |
| 7 | Lag-spectrum completeness | Langford $\{2..n{+}1\}$, Skolem $\{1..n\}$, one each — $n=7,8,11$ verified |
| 8 | Sum laws | Langford $n(n{+}3)/2$ (35/44/90); Skolem $n(n{+}1)/2$ (10/45/325) |
| 9 | Totality $n=1..35$ | one valid piece per $n$ in the theorem's family, 35/35 |
| 10 | Scaling | first solution: $n{=}15$:134 nodes, 16:494, 19:377, 20:956, 23:328, 24:2797, 27:13620, 28:13651, 31:40, 32:41 (all ≤0.03 s); $n{=}36$: 5 M-node budget exhausted in 9.1 s (honest limit) |
| 11 | Symmetry | reversal preserves the law ($n{=}7$); $k\mapsto n{+}1{-}k$ destroys it |
| 12 | Interlacing ratio | 0.667 ($n{=}3,4$) → 0.524 ($n{=}7$) → 0.455 ($n{=}11$) → 0.394 ($n{=}12$) |
| 13 | **Engine demo** | 8 voices × 4 sections, Langford $L(2,8)$; `validate() → (True, "OK")`; MIDI 375 B; `mido` read-back: 8 tracks × 2 notes at 48,50,52,53,55,57,59,60, `ticks_per_beat=480`; 4 onsets per section; lag spectrum `[2..9]` complete |
| 14 | Standalone-file code sketch executed | `solve()`/`audit()` from `method_144_LSPC.md` run for $n=1..20$: law True for all, hook hole exactly 1 for $n\equiv2$, densities correct |

Demo artifacts: `_web144_lspc/lspc_144_langford8.mid` (375 B), `_web144_lspc/lspc_144_demo_report.json`.

## 8. Quirks / pitfalls hit during this job

1. **Concurrent sibling agents.** `methods_db.md` grew from 31 665 → 31 747 lines between my first read and my append (SP-143 sound method + HC-093 human method, appended by other cron jobs). The patch tool warned "*modified by sibling subagent … after this agent's last read*". Mitigation: the append used `cat >>` (append-only, cannot clobber), and the table-row insert used a unique anchor (the tail of row 143) — verified present exactly once afterwards.
2. **OEIS memory trap.** I "recalled" $L(11)=177997$; the actual A014552 term is **17792** (oriented 35584). My measured count matched the real OEIS value — the memory was wrong, the code was right. Lesson: fetch OEIS, never quote from memory.
3. **Budget-capped search is not a proof.** The first verifier printed `exists=False` for $n=13,14$ — those were 3 M-node budget terminations, not nonexistence proofs. Reworded the doc so impossibility rests on the parity theorem + exhaustive enumeration for $n\le12$, and the $n{=}36$ cap is stated openly.
4. **Off-by-one in the hooked density.** Initial claim "density 1.000 for every piece built" was false for hooked Skolem ($2n+1$ slots, one hole). Caught by running the standalone sketch for $n=2,6,10$; corrected in DB section, DB summary row, and standalone file.
5. **`-1` vs `0` sentinel.** The prototype's slot array uses `-1` for "unfilled"; `if s:` treats `-1` as truthy → hooked blocks reported 13/13 filled. Fixed with `if s > 0` and `max(s, 0)` on output (standalone sketch re-verified $n=1..20$).
6. **Python import side-effects.** `verify_lspc2.py` ran its own top-level loop when imported by `verify_lspc3.py`, causing a 600 s hang in the *first* run. Fixed by making v3 self-contained (no cross-import of script modules — job scripts should be import-safe or duplicated).
7. **No `MidiInstrument.MARIMBA`.** The enum only defines 9 GM programs; marimba needed the raw GM program number `12` (0-based). Documented in the demo script comment.
8. **Name collision — two Skolems.** Thoralf Skolem (sequence theory, 1957, this method) vs the *Bose–Skolem* sufficiency theorem for Steiner triple systems (cited by 132 BIBDC). `grep -i skolem` hits both; the DB section flags it explicitly.
9. **Table patch hygiene.** No LaTeX double-escaping (`grep -c '\\\\mathcal'` on row 144 = **0**) and no `||` row prefix (`grep -c '^||'` = **0**) after the edit; row is a single `| **144** |` line at line 154.

## 9. Full method section text as appended

(The exact text, minus the two leading blank separator lines, appended to `methods_db.md`.)

---

# Langford–Skolem Distance-Pairing Composition (LSPC) (Method 144)

### Source

- **Langford, C. Dudley (1958).** "Problem" (Problem 2781), *Mathematical Gazette* 42(341), 228 — posed the puzzle: arrange $1,1,2,2,\dots,n,n$ so that the two $k$'s have exactly $k$ numbers between them. **Priday, C. J. (1959).** "On Langford's Problem I," *Math. Gaz.* 43, 250–255 — necessity of $n \equiv 0,3 \pmod 4$. **Davies, R. O. (1959).** "On Langford's Problem II," *Math. Gaz.* 43, 253–255 — construction (sufficiency).
- **Skolem, Thoralf (1957).** "On certain distributions of integers in pairs with given differences," *Mathematica Scandinavica* 5, 57–68 — the distance-$k$ sibling (pairs exactly $k$ slots apart), with existence iff $n \equiv 0,1 \pmod 4$; Skolem used the sequences to build Steiner triple systems.
- **O'Keefe, E. S. (1961).** "Verallgemeinerung eines Skolemschen Problems," *Math. Scand.* — **hooked** Skolem sequences ($2n+1$ slots, one hook slot) for the residue classes $n \equiv 2,3 \pmod 4$. **Simpson, J. E. (1983).** "Langford sequences: perfect and hooked," *Discrete Mathematics* 44(1), 97–104 — the perfect/hooked classification.
- **Nordh, Gustav (2008).** "Perfect Skolem sets," *Discrete Mathematics* 308(9), 1653–1664 (arXiv:math/0506155).
- **Knuth, D. E. (2008).** *The Art of Computer Programming*, Vol. 4A, §7.1.1 — listing Langford pairings as an **exact cover** instance (Algorithm X / dancing links); the implementation route used here.
- **OEIS A014552** — "Number of solutions to Langford (or Langford-Skolem) problem (up to reversal)": $0,0,1,1,0,0,26,150,0,0,17792,108144,\dots$ with the comment "$a(n) > 0$ iff $n \equiv 0$ or $3 \pmod 4$"; **A176127** $= 2\cdot$A014552 (oriented count); **A004075** — Skolem sequences, whose OEIS comment names them exactly what this method uses: *"Number of super perfect rhythmic tilings of $[0,2n-1]$ with pairs."* Fetched 2026-11-16 (`curl oeis.org/search?q=id:A014552&fmt=text`).
- **Wikipedia: "Langford pairing"** (rev. 2026-09-03, fetched 2026-11-16) — definition, the $n=3$ example `2,3,1,2,1,3`, the A014552 series and the exact-cover remark.
- **Verified prototype (this document):** `_web144_lspc/verify_lspc.py`, `verify_lspc2.py`, `verify_lspc3.py` (+ logs), and the engine demo `_web144_lspc/compose_lspc_demo.py` (`lspc_144_langford8.mid`, 375 B, `lspc_144_demo_report.json`). All numbers quoted below are measured; 20/20 audits pass.

### Layer

**concrete** (LAYER_ARCHITECTURE.md). LSPC emits resolved `MusicEvent`s into UnitMatrix cells — onsets, pitches, durations and velocities are all fixed by the construction, and the slot model is a tick grid, so the zero-drift invariant applies directly. It is *not* an abstract pool method: it decides no pitch-class set relations and no tension curve (those come from the pitch mapping / column assignment it is given). Candidate code path: `generators/langford_pairing.py` (a new generator module; the search should reuse the exact-cover machinery rather than a bespoke backtracker).

### Description

LSPC composes a section as a **distance-pairing sequence**: a perfect partition of a $2n$-slot timeline into $n$ pairs, where the pair belonging to symbol $k$ is separated by *exactly* $k$ intervening slots (**Langford**, distance $k+1$) or is exactly $k$ slots apart (**Skolem**, distance $k$). Each symbol is a voice; its two statements are the voice's only two events in the block. The result is a **hocket with a complete echo spectrum**: in the Langford and Skolem families every slot carries exactly one event (density 1.0, no gap, no doubling — the hooked family has exactly one hole by theorem), every voice speaks exactly twice, and the set of return delays is $\{2,3,\dots,n+1\}$ — *every* lag class appears exactly once, so the block is simultaneously a canon at every delay from 2 slots up to $n+1$ slots, with each voice's re-entry falling on its own unique delay. There is no reinforcement anywhere and no hole anywhere: the sequence is an exact cover of the timeline by translated two-point tiles whose differences are all distinct — the *pair-tiling* dual of 090 GRDC (Golomb ruler: distinct distances between marks) and of 111 VTCC (Vuza: one motif, many translations).

Existence is a hard arithmetic constraint, and that constraint is the compositional grammar:

- **Langford** $L(2,n)$ exists **iff** $n \equiv 0,3 \pmod 4$ (Priday 1959 / Davies 1959).
- **Skolem** exists **iff** $n \equiv 0,1 \pmod 4$ (Skolem 1957).
- **Hooked Skolem** ($2n+1$ slots, one hook) exists **iff** $n \equiv 2,3 \pmod 4$ (O'Keefe 1961).

The three families are complementary, so **every voice count is realizable** — $n \equiv 0$: Langford *and* Skolem; $n \equiv 1$: Skolem; $n \equiv 2$: hooked Skolem only; $n \equiv 3$: Langford *and* hooked. The composer therefore never "fails to allocate": the ensemble size selects the family, and the family is the piece's grammar. Because the residue class of $n$ is forced, the *number of voices is the form decision* — a rare property among generative methods.

Measured facts (all from the prototype logs):

| audit | result |
|---|---|
| Langford existence, exhaustive $n=1..12$ | exists exactly for $n\%4\in\{0,3\}$ — 12/12 agreement with the theorem |
| Langford solution counts | $L(3)=2$, $L(4)=2$, $L(7)=52$, $L(8)=300$, $L(11)=35584$ = $2\times$A014552 (1, 1, 26, 150, 17792) — **exact match** |
| Skolem counts vs A004075 | $n=4$: 6, $n=5$: 10, $n=8$: 504, $n=9$: 2656 — **exact match**; $n\equiv2,3$ give 0 |
| hooked Skolem repairs the void | $n=2,3,6,7,10$: plain 0 solutions, hooked > 0 — repair verified; for $n\equiv0,1$ the hook is redundant (plain already exists) |
| perfect cover | $2n$ slots, $2n$ events, 0 empty, density $=1.000$ for every Langford/Skolem piece built; the hooked family carries exactly one hole by theorem (density $2n/(2n+1)$ = 0.923 at $n{=}6$, 0.973 at $n{=}18$) |
| lag spectrum | Langford $\{2,\dots,n+1\}$, Skolem $\{1,\dots,n\}$ — complete, one occurrence each |
| sum of lags | Langford $\sum = n(n+3)/2$ (7→35, 8→44, 12→90); Skolem $\sum = n(n+1)/2$ (4→10, 9→45, 25→325) |
| totality | one valid piece constructed for **every** $n=1..35$ in the theorem's family |
| scaling | first solution in 40–13 651 nodes for $n=15..32$ (≤0.03 s); naive search on $n=36$ exhausted a 5 M-node budget in 9.1 s → use exact cover / published constructions beyond ~$n=32$ |
| symmetry | reversal preserves the law ($n=7$ verified); relabelling $k \mapsto n+1-k$ **destroys** it |

### Technical Mechanics

**1. Slot model and the two laws.** Let the block have $2n$ slots $0..2n-1$ and let $\pi$ be the symbol at each slot. Langford: for each $k$, $\pi(i)=\pi(j)=k \Rightarrow j-i=k+1$. Skolem: $\Rightarrow j-i=k$. Both are *exact-cover* problems: place $n$ disjoint 2-element tiles $\{i, i+d_k\}$ with $d_k$ prescribed, covering $[0,2n)$ exactly (Knuth 4A §7.1.1). The Langford/Skolem distinction is one slot wide, and it is the difference between "the return is *after* $k$ other voices" and "the return is *at* distance $k$" — musically, a delayed answer versus an immediate echo.

**2. Why existence is arithmetic.** Count slot parities. A pair at distance $k+1$ straddles one even and one odd slot iff $k+1$ is odd, i.e. iff $k$ is **even**; a pair whose $k$ is odd sits in two slots of the *same* parity. The $\lfloor n/2\rfloor$ even symbols therefore consume $\lfloor n/2\rfloor$ even and $\lfloor n/2\rfloor$ odd slots, leaving $\lceil n/2\rceil$ even and $\lceil n/2\rceil$ odd slots to be covered by the $\lceil n/2\rceil$ odd symbols in same-parity pairs — which requires $\lceil n/2\rceil$ to be even, i.e. exactly $n \equiv 0,3 \pmod 4$ (checked at $n=1..12$: $n=1,2,5,6,9,10$ give $\lceil n/2\rceil$ odd and zero solutions). Skolem's condition follows the same count with distance $k$: $k$ odd pairs straddle both parities, forcing $\lfloor n/2\rfloor$-type balance and hence $n\equiv 0,1 \pmod 4$.

**3. Search and construction.** Largest-symbol-first backtracking with a "both slots free" test is enough for small $n$ (measured node counts above) but is exponential in the worst case; Knuth's exact-cover formulation (dancing links) or a bitset DP over (placed set, occupancy mask) is the production route, and Davies/Skolem/O'Keefe give $\mathcal{O}(n)$ explicit constructions for the admissible classes. The number of distinct solutions is astronomically large ($39\,809\,640$ for $n=15$, $326\,721\,800$ for $n=16$ — A014552, up to reversal), so a *seeded choice of solution* is the method's variation generator: the same voice count with a different solution is a different piece (a "same-orchestra, different-counterpoint" variation), and because every solution shares the invariants, style stays constant while detail changes.

**4. Musical mapping (the four dials).**
 - *Symbol → voice*, *slot → metric position*: the sequence is read left to right as the block's rhythmic surface; voice $k$ plays exactly at its two slots.
 - *Lag → canon delay*: the pair span is the voice's return time; the complete lag spectrum means the block has exactly one canon at each delay.
 - *Residue class of $n$ → family → grammar*: $n\equiv2$ is the only class that needs the hook, and the hook is a mandatory single rest — the block has exactly one hole by theorem, which is a usable structural accent (the "breath" of the form).
 - *Solution choice → texture*: the **interlacing count** (number of voice pairs whose intervals cross, i.e. the chord-diagram/Gauss-word crossings) measures how tangled the hocket is. Measured on first solutions: Langford $n=3$: 2/3 crossing pairs, $n=4$: 4/6, $n=7$: 11/21, $n=8$: 15/28, $n=11$: 25/55, $n=12$: 26/66 — the ratio *falls* with $n$, so large ensembles auto-settle into a stratified, less tangled texture unless you deliberately pick highly interlaced solutions.

**5. Score realization.** The $2n$-slot block is one paragraph; repeating the block is the form cycle, transposing it per repetition is the key scheme, and rotating it by $r$ slots is a phase shift that keeps the perfect cover (translation invariance of the law). Because the law is translation-invariant, joining two blocks at a seam never breaks the cover — the zero-drift padding is a single rest over the hook only.

### Musical Elements Framework

- **PITCH**: not generated by the sequence — LSPC is a *rhythm/identity* construction that needs a pitch mapping. Standard mappings: (a) *registral ladder* — pitch$(k) = \text{root} + \text{scale}[k-1]$, so the symbol is both voice and register (verified in the demo: C major from C3 → `48,50,52,53,55,57,59,60`); (b) *decoupled permutation* — assign pitches to symbols by a separate rule (e.g. a subset-network walk) so that lag and register are independent; (c) *unison/octave doubling* — all voices on one pitch class to expose pure rhythm (the "drum-choir" reading). Because the sequence is **not** invariant under $k \mapsto n+1-k$, pitch inversion must be re-solved, not relabelled — a genuine constraint on inversion-based variation.
- **RHYTHM**: this is the method's core. The block is a *metric tiling by pairs* with density exactly 1.0 — every subdivision of the $2n$ grid is used exactly once, so there is **no density contrast at all inside the block** (a real limitation, see Pitfalls 4). What varies is the *lag structure*: onset-to-return distances $2..n+1$ occur once each, so the autocorrelation of the block is uniform at every lag — a "flat" rhythm whose interest is entirely contrapuntal, not accentual. Sub-blocking (slot grouping into beats) yields bars with exactly $\text{slots}/\text{bar}$ onsets each; the demo's 16 slots over 4 bars give exactly 4 onsets per bar (measured: `{0:4, 1:4, 2:4, 3:4}`).
- **HARMONY**: none is implied; the pitch mapping decides consonance. Because each voice holds a single pitch for the whole block, vertical sonorities are *subsets of the mapping's chord* determined by which voices happen to overlap — LSPC is a "harmony-by-scheduling" engine. A useful trick: choose the pitch mapping so that the *interlacing* pairs are consonant and the non-interlacing pairs are not, which makes the harmonic tension track the tangle metric rather than the meter.
- **STRUCTURE**: the residue class of the voice count picks the family, so form is decided *before* any pitch decision; block repetition (with transposition or rotation) is the form cycle; solution choice is the variation axis. Nested use — a Langford block per section, with the section's own duration as the block length — gives a fractal form whose every level is a perfect cover.
- **TEXTURE**: hocket between $n$ monophonic voices, maximum density, uniform onset spacing, no doubling. The interlacing ratio (measured 0.667 at $n=4$ down to 0.394 at $n=12$) is the texture dial: high interlacing = woven/tangled counterpoint; low = stratified layers. Register spread of the pitch ladder sets perceived polyphony: a narrow ladder fuses the hocket into one shimmering line, a wide ladder (two octaves) makes it a conversation.

### UnitMatrix Integration (Voices & Sections)

**Voices = rows = symbols $k$.** Row $k$ is one monophonic voice whose entire content in the block is two `MusicEvent`s at its two slots. Row parameters: `{symbol k, pitch, instrument, velocity}`. Because $k$ also fixes the lag, a row's identity *is* its return delay — the row's "memory span" is $\le n+1$ slots by construction.

**Sections = columns = metric windows.** The block is chopped into $S$ sections of $g$ slots each ($2n = S \cdot g$); column $j$ holds slots $[jg, (j+1)g)$. The column is the bar/phrase window; a column change is a *metric* change (slot = 8th, 16th, triplet), not a harmonic one. Splitting must be *slot-aligned*: a pair may straddle a section seam, and that is fine — the two events live in different columns of the same row, and each cell stays equal-length, so the zero-drift invariant holds.

**Cells = MusicUnit.** Cell $(k, j)$: if symbol $k$ occurs in window $j$, the unit holds that note at its in-cell offset (duration = one slot, clamped at the seam); otherwise it holds a full-length rest (`create_empty_unit(section_ticks)`). The demo (8 voices × 4 sections, 4 quarter slots per bar at 120 bpm, 480 tpb): sequence `8-3-7-2-6-3-2-4-5-8-7-6-4-1-5-1`, 16 cells filled of 32, `validate() → True "OK"`, MIDI 375 B, 16 notes read back with `mido` (each track exactly 2 notes at its own pitch, `ticks_per_beat=480`), lag spectrum `[2..9]` complete, 4 onsets per section.

**Composition path.** Abstract (optional subset/pitch-mapping choice) → **concrete LSPC** (block generation, family selection by $n \bmod 4$, solution search, cell fill, `validate()`) → absolute (any SP renderer). Canonical loop:
`n → family(n%4) → solve_block(n, seed) → split into S windows → fill_voice_section per cell → validate() → to_midi()`.

### Pitfalls

1. **The one-slot convention error (the classic).** Langford's pair for $k$ is $k+1$ slots apart ($k$ *intervening*), Skolem's is exactly $k$ apart. Off by one and the search "proves" that Langford has no solution for $n=3$ — the very case that works. Always test against the two canonical examples: Langford $n=3$ = `2,3,1,2,1,3` (or its mirror `3,1,2,1,3,2`) and $n=4$ = `4,1,3,1,2,4,3,2`; Skolem $n=4$ = `4,2,3,2,4,3,1,1`.
2. **Existence trap — the ensemble size is a hard constraint.** There is no Langford pairing for $n \equiv 1,2 \pmod 4$ (verified $n=1,2,5,6,9,10$: zero solutions). Asking for a 6-voice Langford piece is asking for a proof of nonexistence: switch to hooked Skolem ($n\equiv2$) or change the voice count. Any solver without a node budget will hang here — the prototype spent 3 M nodes "searching" $n=13,14$ before the cap fired.
3. **The hook is a rest, not a silence you can ignore.** A hooked Skolem block has $2n+1$ slots and exactly one hole. If the hole is left unaccounted, the row lengths no longer match and `validate()` fails ("Track length mismatch"); if the hole is placed mid-block, the timeline is no longer a perfect cover and the "no gap" claim is false. Pin the hook to the block end (or convert it to an explicit full-length rest cell).
4. **Density is constant by construction — flatness is the default.** Exactly one event per slot means the block has no density contour at all; played literally it is a machine-gun of equally spaced onsets. Fixes: vary velocity by lag (longer delay = stronger return), let note length run to the re-entry (canon-style sustain, clamped at seams), thin the block by *dropping* slots (giving up perfect cover for groove) or use the family's hook as the one structural breath.
5. **Relabelling is not free.** $k \mapsto n+1-k$ breaks the distance law (verified $n=7$: the relabelled sequence is not a Langford pairing) because the label *is* the distance. Transposition of pitches, rotation of the block, and reversal of the block all preserve the law; relabelling does not. Inversion-based variation must re-run the solver with inverted pitch mapping, never permute the sequence.
6. **Symbol-as-register skews the texture.** If pitch$(k)=$ ladder position, then the highest voice always returns last and the bass always returns first — the hocket is systematically bottom-heavy. Decouple the pitch mapping from $k$ when you want register independence (the demo's ladder is the simple, skewed case).
7. **Search cost is not linear in practice.** First solutions are cheap (134 nodes at $n=15$, 40 nodes at $n=31$), but *all* solutions or an unlucky instance explodes ($n=36$: 5 M nodes / 9.1 s without success). Production code needs exact cover (Knuth's Algorithm X), a bitset DP, or the published $\mathcal{O}(n)$ constructions; never ship the naive backtracker with an unbounded loop.
8. **Neighbour audit — three adjacent methods, three different objects.** 090 GRDC places marks so that *all pairwise distances are distinct* (a set, one voice); 112 CADDC places dots so that *all displacement vectors are distinct* (2D, permutation); 111 VTCC tiles the cycle with *translations of one motif* (a factorization of $\mathbb{Z}_n$). LSPC tiles the line with $n$ **distinct two-point tiles, each used exactly once**, and its differences are $\{1..n\}$ — a *rainbow* pair-tiling. OEIS's own name for the Skolem case is "super perfect rhythmic tiling of $[0,2n-1]$ with pairs" (A004075), which is the correct citation to use; calling LSPC simply a "tiling canon" invites confusion with 111. Also: **Skolem the sequence-theorist (1957) ≠ Skolem of the Bose–Skolem sufficiency theorem for Steiner triple systems** used by 132 BIBDC — same author, different theorem, and grep on "Skolem" hits both.
9. **Not the same as "Langford–Skolem problem" solutions being rare.** $n=15$ has 39 809 640 unoriented solutions (A014552) — the space is enormous, so "the" Langford piece does not exist; seed the solution choice and record the seed, or two runs will disagree while both claim to be canonical.

---

## 10. Deliverables checklist

- [x] ID resolved dynamically → 144 (table max 143, file max 143, no 144 file)
- [x] Layer classified first → **concrete**
- [x] Paradigm → **Rules-Based**; novelty checked against 143 existing methods (esp. 033, 090, 111, 112, 132)
- [x] Researched with web sources (OEIS ×2, Wikipedia) + literature citations
- [x] Musical Elements Framework (PITCH / RHYTHM / HARMONY / STRUCTURE / TEXTURE) + UnitMatrix integration
- [x] Appended via `write_file` → `cat >>` → `rm` (no heredoc/execute_code)
- [x] Summary row added (line 154), no `\\` double-escape, no `||` prefix, verified by re-read
- [x] Standalone `method_144_LSPC.md` (extended math, executed Python sketch, references, artifacts)
- [x] `wc -l` + grep verification done (§3, §7)
- [x] Report written (this file)

**Next free ID: 145.**
