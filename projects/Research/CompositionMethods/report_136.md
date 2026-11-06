# Report 136 — Collatz Hailstone Composition (CHC)

- **Method ID:** 136 (next free ID after registration: **137**)
- **Method name:** Collatz Hailstone Composition (CHC)
- **Paradigm:** Rules-Based
- **LAYER:** concrete (emits events filling UnitMatrix cells; feeds `generators/` — see LAYER_ARCHITECTURE.md)
- **One-line description:** Each UnitMatrix voice is one hailstone trajectory of the Collatz 3n+1 (shortcut) map — parity = gesture, bit-length = register, total stopping time = row length, the universal 4→2→1 absorbing cycle = provable HOME cadence, record-holder seeds (OEIS A006877) = macro-form.
- **Registered:** 2026-11-06 (cron, autonomous)

## Classification

| Attribute | Value |
|---|---|
| Paradigm | **Rules-Based** (deterministic arithmetic recursion; no randomness, no corpus, no fitness, no learning) |
| Layer | **concrete** |
| Primary Elements | Pitch, Rhythm, Harmony, Structure, Texture |
| Tonal Gravity | Moderate (4-2-1 cadence-pinned; provable HOME, wild middle) |
| Metric Binding | Grid-Locked / Continuous (step slots, fold-quantized) |
| Memory Depth | None (state = current integer) |
| Time Complexity | $\mathcal{O}(N)$ per trajectory ($O(1)$ per step; bounded in practice) |

## Full summary-table row (as appended to methods_db.md)

```
| **136** | concrete | Collatz Hailstone Composition (CHC) | **Rules-Based** | Pitch, Rhythm, Harmony, Structure, Texture | Moderate (4-2-1 cadence-pinned) | Grid-Locked / Continuous (step slots) | None (State = current integer) | $\mathcal{O}(N)$ per trajectory | Composes by iterating the Collatz 3n+1 map (shortcut form): each voice = one hailstone trajectory of a seed; parity bit = operation/gesture (even = halving, odd = multiplying), bit-length = register/velocity, total stopping time $\sigma(n)$ = row length (verified: seed 27 → 111 non-shortcut steps / 70 shortcut, peak 9232/4616), the universal 4→2→1 tail = provable HOME cadence, record-holder seeds (OEIS A006877: 1,2,3,6,7,9,18,25,27,54,73,97,129,171,231,313,327,649,703,871,1161,2223,2463,2919,3711,6171; prefix verified) = macro-form ladder; parity congruence (m≡n mod 2^k ⇔ first k parity bits agree; bijection verified mod 2^6) and T^k(2^k a+b)=3^c a+d (T⁴(16a+3)=9a+2 verified) give provable canon/voice-leading; seeds 27/54/73/97 merge on one trunk (shared peak 4616, universal 4-2-1 tail; verified). Feeds generators/collatz_hailstone.py. |
```

## Line counts

- Before: **30278** lines (`wc -l` pre-append)
- After: **30359** lines (`wc -l` post-append)
- Delta: **+81** = +80 (method section, appended via temp file `cat >>`) + 1 (summary-table row, inserted after row 135 with the patch tool)

## Files

- Standalone write-up: `/opt/data/projects/Research/CompositionMethods/method_136_CHC.md`
- Report (this file): `/opt/data/projects/Research/CompositionMethods/report_136.md`
- Method section in DB: `methods_db.md` lines 30280–30359 (header `# Collatz Hailstone Composition (CHC) (Method 136)` at line 30280; summary row `| **136** |` at line 146)
- Fact-check script: `_web137/verify_136_CHC.py` (12 checks, all pass)
- Web cache: `_web137/wiki_collatz.txt`, `_web137/arxiv_collatz_music.xml`, `_web137/arxiv_collatz_composition.xml`
- Demo: `projects/Research/outputs/chc136_demo/chc136_demo.mid` (2847 B) + `compose_chc136_demo.py` + provenance; `validate()` OK, preflight compliant

## Candidate code path

`generators/collatz_hailstone.py` (new module): `CollatzMap.step` ($O(1)$ shortcut map), `HailstoneTrajectory.run` (orbit + parity + peak + stopping time), `RecordTable.records` (A006877/A006884 ladders), `ParityVector.encode` (residue-class congruence), `CollatzPlan.to_events` (fold → per-section `MusicEvent` lists → `_unit_from_events` → `UnitMatrixComposer.fill_voice_section → validate() → to_midi()`). This is a concrete-layer generator, so it feeds `generators/` (per LAYER_ARCHITECTURE.md).

## Verification results (all real, from `_web137/verify_136_CHC.py` + musicom demo)

1. Seed 27: 111 non-shortcut steps, 41 odd steps, peak 9232 (Wikipedia canonical, re-verified).
2. Record-holder seeds A006877 prefix (through 6171, 26 seeds) reproduced by brute force.
3. Max total stopping time <10^5 → 77031 @ 350 steps; <10^6 → 837799 @ 524 steps.
4. Parity congruence: first k parity bits of n and n+2^k identical; differ for n+3 (k≥2).
5. Parity-vector map mod 2^6 is a bijection (64/64 distinct vectors).
6. Absorbing cycle 4→2→1 confirmed.
7. $2^k a+b$ identities under the shortcut map: T²(4a+1)=3a+1, T⁴(16a+3)=9a+2, T⁵(32a+1)=27a+2 (all a checked); the non-shortcut $f$ version fails — pitfall #5.
8. Bohm–Sontacchi: parity word "10" → rational 1/1 = 1 (generator of 1→2→1).
9. Powers of two: 2^10 → 1 in exactly 10 steps, never rising.
10. Record peaks A006884 prefix (through 1819) reproduced.
11. Determinism: same seed → identical trajectory.
12. De Mol 2-tag system (a→bc, b→a, c→aaa): a^5 halts as 'a' in 20 tag steps.
13. Demo (musicom engine): seeds [27,54,73,97] → rows 71/72/74/76 slots (incl. terminal 1), 6 sections × 20 slots, validate() True, MIDI 2847 B, preflight COMPLIANT. Shortcut trajectories: 70/71/73/75 steps, all sharing peak 4616 and the 4-2-1 tail (54→27; 97→73→47 trunk merges).

## Quirks / pitfalls hit during the job

- **Plain-HTTP security block:** arXiv API must be fetched over HTTPS (`export.arxiv.org`), not HTTP — the security scan rejects unencrypted URLs in exec contexts.
- **Patch-tool LaTeX double-escape risk:** verified the inserted table row byte-level — exactly 1 backslash before `mathcal` (matches row 135); single-pipe prefix intact. No `\\` or `||` corruption.
- **Two maps, two numbers:** 111 steps/9232 (non-shortcut) vs 70 steps/4616 (shortcut) for seed 27 — must always label which map; peaks differ because the shortcut merges the odd-value step.
- **Wikipedia's "41 steps through odd numbers" excludes the terminal 1** (42 odd values in the trajectory incl. terminal) — first assertion failed until corrected.
- **The $2^k a+b$ identity holds only for the shortcut map** (my first check applied the non-shortcut $f$ and failed; reading the Wikipedia parity-vector section context resolves it).
- **MIDI pitch overflow:** naive bit-length folding exceeded 127; clamped at 120 and lowered per-voice base to 36.
- **Provenance API:** `write_provenance` accepts only `sources`/`parameters`/`notes` kwargs — the initial `method=`/`seeds=` kwargs raised TypeError; packed them into `parameters`.
- **`fill_voice_section` takes one unit, no offset arg:** per-section units built from `MusicEvent` lists via `_unit_from_events(events, section_len)` (the sanctioned zero-drift pattern).
- **MidiInstrument enum is small:** `LEAD_8_BASS_LEAD` does not exist; used STRING_ENSEMBLE/PIANO/VIOLIN/FLUTE.
- **`_web136` already taken** by the SP-134 job's cache — used `_web137` for this job's cache.
- **Demo row lengths** (71/72/74/76 including terminal 1) vs steps (70/71/73/75) — off-by-one from including the terminal 1 in the values list; documented as steps = len-1.

## Complete method section text appended to methods_db.md

```markdown
# Collatz Hailstone Composition (CHC) (Method 136)

### Source

- **Collatz, Lothar (1937).** The 3n+1 iteration (introduced 1937, two years after his doctorate); also known as Ulam's conjecture, Kakutani's problem, the Syracuse problem (name proposed by Hasse in the 1950s at Syracuse University), the hailstone problem, and "wondrous numbers" — see Maddux & Johnson (1997), *Logo: A Retrospective*, p. 160, for the alias list.
- **Wikipedia, "Collatz conjecture"** (rev. 2026-11-05; cached `_web137/wiki_collatz.txt`) — statement, hailstone terminology, empirical record tables, parity-vector theory, cycles, undecidable generalizations; the reference corpus for every number quoted and re-verified below.
- **Terras, R. (1976).** "A stopping time problem on the positive integers." *Acta Arithmetica* 30(3), 241–252 — almost every positive integer has finite stopping time; the set of integers with finite stopping time has natural density 1; proof via the distribution of parity vectors and the central limit theorem.
- **Lagarias, J. C. (1985).** "The 3x+1 problem and its generalizations." *American Mathematical Monthly* 92(1), 3–23 — the classical survey; the standard 3/4 geometric-mean growth heuristic is stated and qualified there.
- **Lagarias, J. C. (ed.) (2010).** *The Ultimate Challenge: The 3x+1 Problem.* American Mathematical Society — the definitive collected volume on the problem.
- **Conway, J. H. (1972).** "Unpredictable iterations." *Proc. 1972 Number Theory Conf., Univ. Colorado, Boulder*, 49–52 — a natural generalization of Collatz (piecewise maps $g(n)=a_i n+b_i$ for $n\equiv i \pmod P$ with rational $a_i,b_i$) is algorithmically undecidable; formalized as the FRACTRAN language. Kurtz & Simon later proved the universally quantified problem is $\Pi^0_2$-complete, even with the modulus $P$ fixed to 6480.
- **Eliahou, S. (1993).** "The 3x+1 problem: new lower bounds on nontrivial cycle lengths." *Discrete Mathematics* 118, 45–56 — the period $p$ of any non-trivial cycle has the form $p = 301994a + 17087915b + 85137581c$ with $a,b,c$ nonnegative, $a+b\ge1$. Hercher (2023) extended this to: no $m$-cycles with $m \le 91$; the best known cycle-length bound (as of 2025) is 217 976 794 617 (355 504 839 929 without shortcut).
- **De Mol, L. (2008).** "Tag systems and Collatz-like functions." *Theoretical Computer Science* 390(1), 92–101 — hailstone sequences are computed by the 2-tag system with production rules $a \to bc,\ b \to a,\ c \to aaa$; the Collatz conjecture is equivalent to the halting of this tag system.
- **Guy, R. K. (2004).** *Unsolved Problems in Number Theory* (3rd ed.), Springer, problem E16 "The 3x+1 problem", pp. 330–336.
- **OEIS** — A006577 (total stopping times), A006877 (record-holder seeds, total stopping time records), A006884 (record peaks), A008884 (the 27-trajectory). All prefixes quoted below re-verified by direct computation.
- **arXiv prior-art check (2026-11-06):** `all:"Collatz" AND all:"music"` → **0 records**; `all:"Collatz" AND all:"composition"` → **5 records**, all pure mathematics on the conjecture itself (parity-vector parameterization, generalized $px{+}1$ maps, binary-string proof attempts) — none musical. Cached `_web137/arxiv_collatz_music.xml`, `_web137/arxiv_collatz_composition.xml`. Informal note-per-step sonifications of hailstone trajectories circulate online (seed 27 is a favorite) and OEIS hosts audio renderings of step-count sequences; none formalizes a trajectory→UnitMatrix mapping or a stopping-time macro-form grammar.
- **Novelty check (2026-11-06):** `grep -ci` on `methods_db.md` before entry: `collatz` = 0, `hailstone` = 0, `3n+1` = 0, `stopping time` = 0, `parity vector` = 0. Adjacent-but-different registered methods: **076** Thue–Morse (parity-of-digit-sum automatic sequence; substitution $0{\to}01,1{\to}10$ — no multiplicative recursion, no absorbing cycle), **128** Van Eck (self-referential gap distances; no multiply/divide dichotomy), **114** FSBC (Farey/Stern–Brocot fraction enumeration; static, non-iterated), **121** IETC (measure-preserving interval exchange; no contraction), **043** SATM / **107** SDEC (continuous ODE/SDE chaos; not discrete arithmetic), **049** IFS (contractive affine maps only — Collatz *alternates* expansion and contraction toward a universal sink). CHC is the first *arithmetic iterated-map* method (deterministic integer recursion with an absorbing 4-2-1 cycle) in the DB.
- **Reference prototype verified for this document:** `_web137/verify_136_CHC.py` — 12 fact-checks, all pass (numbers inline below); end-to-end musicom demo at `projects/Research/outputs/chc136_demo/` (`validate()` OK, preflight compliant).

### Layer

**concrete** — CHC emits events that fill UnitMatrix cells: each voice's trajectory is resolved into a per-step sequence of (pitch, onset, duration, velocity) events, quantized to grid slots and padded to section length. The hailstone shape doubles as a tension plan, but the method's primary output is a resolved cell schedule, not a plan. Feeds `generators/` directly (candidate module `generators/collatz_hailstone.py`: `CollatzMap.step`, `HailstoneTrajectory.run`, `RecordTable.records`, `ParityVector.encode`, `CollatzPlan.to_events`).

### Paradigm

**Rules-Based** — deterministic arithmetic recursion (Collatz 1937). No randomness, no corpus, no fitness function, no learning. Same seed + same folding parameters give the same piece (verified: trajectory recomputation is byte-identical; demo deterministic).

### Description

**Collatz Hailstone Composition (CHC)** composes from the 3n+1 iteration itself: every voice is one *hailstone trajectory* — the orbit of an integer seed under

$$f(n)=\begin{cases}n/2 & n\equiv 0 \pmod 2,\\ 3n+1 & n\equiv 1 \pmod 2\end{cases}$$

or, in the "shortcut" form used throughout (it halves the step count without changing the dynamics),

$$T(n)=\begin{cases}n/2 & n\equiv 0 \pmod 2,\\ (3n+1)/2 & n\equiv 1 \pmod 2.\end{cases}$$

The Collatz conjecture (open since 1937; verified by computer for all $n \le 2.36\times10^{21}$ as of the 2026 reference revision) asserts that every trajectory reaches the absorbing cycle **4 → 2 → 1**. Whether or not it holds for all $n$, the *known* structure of the map is what makes it a compositional engine:

- **Hailstone shape = tension arc.** Trajectories alternate ascents and descents "like hailstones in a cloud": the value series is a built-in crescendo–diminuendo plan with a unique peak. Canonical seed 27: **111 steps** (non-shortcut; **41 steps through odd numbers**), climbing from 27 to a peak of **9232**, then collapsing through 4-2-1 (all verified). Under the shortcut map the same trajectory is **70 steps** with peak **4616** (the odd-value 9232 is merged into a single step).
- **Parity = operation = gesture.** Each step's parity bit says which operation fires: even ⇒ halve (a descending "division" gesture), odd ⇒ multiply-and-add (an ascending "multiplication" gesture). The parity sequence *is* the sequence of operations — a binary "score" that the trajectory reads left to right.
- **Stopping time = length.** The **total stopping time** $\sigma(n)$ (steps to 1; OEIS A006577) sets the row length a priori. **Record-holder seeds** (A006877: 1, 2, 3, 6, 7, 9, 18, 25, 27, 54, 73, 97, 129, 171, 231, 313, 327, 649, 703, 871, 1161, 2223, 2463, 2919, 3711, 6171, …) give successively longer rows; below $10^5$ the longest is **77031** at **350 steps**, below $10^6$ it is **837799** at **524 steps** (both verified). Powers of two are the minimal rows: $\sigma(2^k)=k$, never rising (verified for $2^{10}$).
- **4-2-1 tail = universal cadence.** Every trajectory ends 4 → 2 → 1 — a built-in, *unavoidable* HOME. Cadence placement is provable, not designed: the last three values of every row are fixed. The negative cycles (−1, −5, −17) are irrelevant for composition over positive seeds.
- **Parity-vector determinism.** The first $k$ parity bits of $n$ and $m$ agree **iff** $n \equiv m \pmod{2^k}$ (Terras/Everett; verified: the map residue $\bmod 2^k$ → parity vector is a bijection, 64/64 distinct vectors for $k=6$). Two seeds in the same residue class share $k$ identical opening gestures; different cycles must carry different parity words.
- **Bohm–Sontacchi rationals.** Any periodic parity word is generated by exactly one rational
$$\frac{3^{m-1}2^{k_0}+\cdots+3^0 2^{k_{m-1}}}{2^n-3^m},$$
where the cycle has length $n$ and $m$ odd entries at indices $k_0<\cdots<k_{m-1}$. The positive cycle's word "10" yields $1/1 = 1$ — the generator of 1→2→1 (verified).
- **$2^k a + b$ structure.** $T^k(2^k a + b) = 3^c a + d$ where $c$ = number of odd steps and $d = T^k(b)$ (verified: $T^2(4a{+}1)=3a{+}1$, $T^4(16a{+}3)=9a{+}2$, $T^5(32a{+}1)=27a{+}2$ for all checked $a$). This gives *algebraic* voice-leading: seeds in the same residue class converge identically for $k$ steps, then diverge — a provable canon/unison structure.
- **Trunk merging.** Record-holder seeds coalesce: 54→27 immediately, 97→73→…→47 joins the 27-trunk at 47; hence seeds 27/54/73/97 share the same peak (4616 shortcut) and the same 4-2-1 tail — a provable tutti climax and universal closing chord (verified).
- **Undecidability as a design boundary.** Conway 1972: generalizing the map to $g(n)=a_i n+b_i$ per residue class $\pmod P$ (rational $a_i,b_i$, FRACTRAN) is undecidable; Kurtz–Simon: $\Pi^0_2$-complete even at $P=6480$. The 3n+1 map itself is $O(1)$ per step, but a composer who generalizes the map to encode arbitrary grammar forfeits termination guarantees.

### Musical Elements Framework

- **PITCH**: value → pitch by folding: register = bit-length $\lfloor\log_2 a_n\rfloor$ (the trajectory's altitude), scale degree = residue $a_n \bmod |\text{scale}|$ (or pc = $a_n \bmod 12$). The hailstone shape then reads directly as a registral arch — seed 27 spans 5 octaves (27 → 9232) before the 4-2-1 collapse. Bias the fold so that the tail residues (4, 2, 1) map to the tonic degree for a built-in cadence pitch.
- **RHYTHM**: step = one grid slot; parity = gesture class (even = short/quiet "division" cell, odd = longer/louder "multiplication" cell); duration may be $\propto \log_2 a_n$ (the peak sustains longest) or constant with velocity $\propto$ bit-length. The parity vector is the rhythmic score; $\sigma(n)$ is the row length in slots; the 41 odd steps of 27 are its accents.
- **HARMONY**: multi-voice simultaneities from congruent seeds — seeds in the same residue class $\bmod 2^k$ share $k$ identical leading steps (a *provable* canon), and the $2^k a + b$ identities give exact two-voice moves (a row seeded $4a{+}1$ lands on $3a{+}1$ after two steps — a suspension resolved by the map, not by the composer). Trunk merging aligns voices on a common peak and a common 4-2-1 closing chord.
- **STRUCTURE**: sections = trajectory segments (climb / peak plateau / descent / 4-2-1 tail), cut at stopping-time milestones; macro-form = a seed schedule (exposition on a short seed, climax on a record seed with a huge peak, recapitulation on its double $2n$, whose trajectory shares the tail). $\sigma(n)$ fixes total length a priori; the peak step fixes the climax position (seed 27: peak at step 45 of 70 shortcut).
- **TEXTURE**: density = number of rows in their climbing phase (above their start value) per section; peak rows sound loudest/longest; the tail thins every row to the unison 4-2-1. Record-peak seeds (A006884: 1, 2, 3, 7, 15, 27, 255, 447, 639, 703, 1819, …; prefix verified) give a built-in polyphonic hierarchy — bigger seeds = higher, louder voices.

### UnitMatrix Integration (Voices & Sections)

**Voices = rows = seeds.** Row $v$ starts from seed $s_v$ and runs its trajectory; a row's events are its trajectory values folded to pitch, one grid slot per step. Voice hierarchy by seed size: small seeds = low, slow-note bass-like rows; record seeds = high, florid rows. Per-voice child seed (`seed*101 + row`) keeps multi-row runs reproducible.

**Sections = columns = trajectory segments.** The governing seed's trajectory is cut at stopping-time milestones into $S$ segments (e.g. climb → peak plateau → descent → 4-2-1 tail). Each column holds the folded events of all rows still sounding there; rows that finished early loop their 4-2-1 tail cell as an ostinato until the matrix ends — every row must end on the section's terminal landmark at `section_len` (the zero-drift invariant).

**Cells = MusicUnit.** Step $k$ of row $v$ → one note unit (pitch = fold($a_k$), duration = slot or $\propto \log_2 a_k$, velocity = $\propto$ bit-length), built per section from `MusicEvent` lists via `_unit_from_events(events, section_len)`; the 4-2-1 tail cells can be a chord unit on the tail-derived pcs. Verified end-to-end (musicom engine): 4 voices (record seeds 27, 54, 73, 97) × 6 sections of 20 slots, longest row 75 shortcut steps (seed 97) → `validate()` **True**, zero drift, MIDI 2847 bytes, Research preflight compliant; demo at `projects/Research/outputs/chc136_demo/chc136_demo.mid`.

**Candidate code path:** `generators/collatz_hailstone.py` — `CollatzMap.step(n)` (shortcut map, $O(1)$), `HailstoneTrajectory.run(seed)` (full orbit, parity bits, peak, peak step, stopping time; $O(\sigma)$), `RecordTable.records(limit)` (A006877/A006884 record ladders), `ParityVector.encode(seed, k)` (residue-class congruence), `CollatzPlan.to_events(...)` (fold → `MusicEvent` list, pads finished rows with the 4-2-1 tail, consumes per-section event lists through `_unit_from_events`), wired to the standard `UnitMatrixComposer.fill_voice_section → validate() → to_midi()` spine. Cost: $\mathcal{O}(N)$ per trajectory (each step $O(1)$; total stopping times stay modest — under $10^{12}$ the record is 1348 steps).

### Pitfalls

1. **Two maps, two step counts.** Non-shortcut $f$ gives 111 steps / peak 9232 for 27; shortcut $T$ gives 70 steps / peak 4616. Quote which map; never mix tables (A006577 etc. are conventionally non-shortcut).
2. **Stopping time vs total stopping time.** "Stopping time" = first step below the start value; "total stopping time" = steps to 1. Record tables (A006877) are *total* stopping time records — do not feed A006877 seeds into a piece that needs short openings without checking $\sigma$ first.
3. **Convergence is a conjecture.** Verified to $2.36\times10^{21}$ and observed always to converge, but unproven in general. Guard the generator with a step cap (e.g. $10^4$ steps) and treat non-convergence as a design license (an open-ended row), not a crash.
4. **Zero-drift: rows end at different times.** Rows have different $\sigma$; finished rows must be padded (4-2-1 tail ostinato) to the section length via `_unit_from_events`, or `validate()` reports track-length mismatch — same rule as any other feeder.
5. **Parity congruence is only $\bmod 2^k$.** "Seeds that open identically" must differ by a multiple of $2^k$; and the identity $T^k(2^k a+b)=3^c a+d$ holds only under the shortcut map — applying it with non-shortcut $f$ breaks (verified: $f^4(16a{+}3) \ne 9a{+}2$, but $T^4(16a{+}3)=9a{+}2$).
6. **Trunk merging collapses voices.** Seeds 27/54/73/97 all merge (54→27; 97→73→…→47), so after the merge point the voices play identical material in parallel. If independent polyphony is wanted past the merge, choose seeds with non-mergeing orbits (or transpose rows).
7. **The climax position is fixed by the seed.** Peak step is a property of the seed (27: step 45/70); you cannot move the climax without changing the seed. Use record-peak seeds (A006884) when a *late, huge* climax is wanted.
8. **Fold bias.** Plain residue folding can land the tail values (4, 2, 1) on non-tonic degrees; if the 4-2-1 chord must be the tonic, bias the fold (offset the degree table or fold $\bmod 5$) so the tail residues map to scale-degree 1.
9. **Undecidability applies to generalizations, not to 3n+1.** Generalizing the map (modulus $P$, rational $a_i$) to encode musical grammar is undecidable in general (Conway 1972; $\Pi^0_2$-complete even at $P=6480$) — no termination guarantee for custom moduli; stick to 3n+1 for provable behavior, or embrace non-termination as an aleatoric feature.
10. **Not a re-skin of adjacent methods.** 076 Thue–Morse is a substitution-sequence (no arithmetic recursion, no sink), 128 Van Eck is gap self-reference (no multiply/divide dichotomy), 049 IFS is contraction-only (Collatz *alternates* expansion and contraction), 121 IETC is measure-preserving (no absorbing cycle). The 4-2-1 absorbing cycle and the parity-as-operation score are the signature — if a passage should "hover without ending", that is IETC/IFS territory; if it must *provably end on the tonic*, that is CHC.
```
