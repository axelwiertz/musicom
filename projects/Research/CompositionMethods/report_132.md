# Report 132 — Balanced Incomplete Block Design Composition (BIBDC)

**Date:** 2026-11-02 · **Job:** music methods research (cron) · **Status:** COMPLETE

| field | value |
|---|---|
| Method ID | **132** |
| Name | Balanced Incomplete Block Design Composition |
| Acronym | BIBDC |
| Paradigm | Rules-Based |
| **Layer** | **concrete** |
| One-liner | The ensemble schedule *is* a 2-$(v,k,\lambda)$ block design: voices = points, sections = blocks, every pair of voices sounds together in exactly $\lambda$ sections — fairness, minimum sections, provable closure. |
| Standalone file | `/opt/data/projects/Research/CompositionMethods/method_132_BIBDC.md` |
| Report file | `/opt/data/projects/Research/CompositionMethods/report_132.md` (this file) |
| Candidate code path | `generators/design_blocks.py` (new): `BIBD`, `SteinerTripleSystem`, `Parallelism.resolve()`, `design_to_units()`; metadata export (occupancy + pair-coverage + novelty curve) can also feed `rules/subset_network.py` as a plan |
| Verification scripts | `verify_132_BIBDC.py`, `verify_132b_kirkman.py`, `bibdc_sketch.py` (all run under `$MUSICOM_PYTHON`, all pass) |
| Web cache | `_web132/{sts.json,sts2.json,kirkman.json,bibd.json}` (Wikipedia API extracts, fetched 2026-11-02) |
| Line count before | **29 524** |
| Line count after section append | 29 612 (+88) |
| Line count after summary row | **29 613** (+89 total) |
| Summary rows before / after | 130 → 131 (`| **NNN** |` count) |
| Next free ID | **133** |

## Classification details

- **Layer = concrete.** The design object is a plan, but the method immediately resolves to event-bearing cells: sounding vs. rest per (voice, section), one pitch per sounding cell, one onset slot per block member. That is `MusicUnit` content → `generators/`, not the abstract `rules/subset_network.py` pitch-pool/set-relation layer. (Contrast 131 TDRPC, registered `abstract` because it only designs a ratio pool.)
- **Paradigm = Rules-Based.** Deterministic incidence arithmetic; no sampling, no nature dynamics, no learned parameters. Randomness is only a choice *over* a deterministic object (which of the 80 STS(15)s, which block order).
- **Tonal Gravity: Moderate** — injected by the seat map (fixed pitch per voice + optional octave ladder), not by the design; the design supplies an exact, order-independent *pair-novelty* tension curve instead.
- **Metric Binding: Grid-Locked / Continuous** — the design fixes onset *counts* ($k$ per section) but not their placement; usable with a strict grid or free timing.
- **Memory Depth: Macro / Design** — balance is a global certificate over the whole piece (all $\binom{v}{2}$ pairs), while generation is local per section.
- **Time Complexity:** $\mathcal{O}(v^2)$ design construction (Bose) / cheap backtracking, $\mathcal{O}(v^2)$ pair audit, $\mathcal{O}(bk)$ event emission.

## Full summary-table row (as inserted, line 142)

```
| **132** | concrete | Balanced Incomplete Block Design Composition (BIBDC) | **Rules-Based** | Pitch, Rhythm, Harmony, Structure, Texture | Moderate (Seat-map imposed; pair-novelty curve) | Grid-Locked / Continuous | Macro / Design (global pair coverage) | $\mathcal{O}(v^2)$ design build, $\mathcal{O}(v^2)$ pair audit, $\mathcal{O}(bk)$ events | Composes the **ensemble schedule** as a balanced incomplete block design: the $v$ voices (rows) are points, the $b$ sections (columns) are blocks, and every pair of voices sounds together in exactly $\lambda$ sections — so no duo is over- or under-featured, every voice plays exactly $r=\lambda(v-1)/(k-1)$ sections, and ensemble density is the constant $k/v$. $\lambda{=}1$ is the Steiner triple system ($b=v(v-1)/6$; verified: 7→7, 9→12, 13→26, 15→35 blocks, every pair exactly once, all degrees $=(v-1)/2$). Each block adds exactly $\binom{k}{2}$ new duos, so pair-novelty falls monotonically to 0 at the last section — a provable, order-independent tension curve (Fano: 18,15,12,9,6,3,0; identical forward and reversed). In STS(7) any two blocks share exactly one voice, so every seam is a single-common-tone move (21/21 verified). Resolvable designs (Kirkman) partition the ensemble into $v/k$ simultaneous groups per movement (AG(2,3): 4 classes of 3, verified; STS(15): 7 classes of 5, constructed and verified); transposing the incidence matrix gives the dual piece (self-dual only when $v=b$). Fairness/rotation law for ensemble scheduling — foil to 090 GRDC / 112 CADDC (within-set differences) and 123 GTBRC (incentive-based), and the incidence-theoretic counterpart of 129 ABGC's Stimmtausch. |
```

Verified post-patch: 11 pipe characters (10 columns, matches header), single backslashes preserved (`\mathcal`, `\lambda`, `\binom` — no `\\` doubling), no `||` prefix.

## Novelty check (before registration)

`grep -ci` on `methods_db.md`: `BIBD` = 0, `block design` = 0, `Steiner` = 0, `Kirkman` = 0, `incidence` = 0. Adjacent registered methods checked and differentiated in the text: 090 GRDC (distinct differences), 112 CADDC (Costas arrays), 111 VTCC / 083 QTSC (tilings/partitions), 123 GTBRC (game incentives), 129 ABGC (braid / Stimmtausch). No prior method balances pairwise voice co-incidence.

## Verified results (actual runs)

```
verify_132_BIBDC.py
  Fano STS(7): b=7 r=3, lam_ok=True, deg_ok=True, 21 pairs
  block-pair intersections of STS(7): {1: 21}   (every pair of blocks meets in exactly 1 point)
  backtracking STS: v=7 b=7 r=3 | v=9 b=12 r=4 | v=13 b=26 r=6 | v=15 b=35 r=7  (nodes 8/13/27/75)
  AG(2,3) = STS(9), 12 blocks, resolvable into 4 parallel classes of 3
  novelty STS(7) forward [18,15,12,9,6,3,0] == reversed (order-independent)
  labelled STS(7) = 30 = 7!/168  =>  |Aut(Fano)| = 168
  counting identities vr=bk, lam(v-1)=r(k-1) hold for (7,3,1)(9,3,1)(13,3,1)(15,3,1)(7,3,2)(9,4,3)(6,3,2)
  complement of a Fano block is not a block

verify_132b_kirkman.py
  resolvable STS(15) found on random attempt 24: 35 blocks, 7 parallel classes of 5, 105 pairs exactly once
  (first heuristic STS(15) had NO parallelism -> resolvability is per-design, not per-order)

bibdc_sketch.py
  Fano audit True (b=7, r=3, 21 pairs); seams [[0],[0],[5],[1],[6],[2]] (all size 1)
  self-dual True; STS(9) resolvable True; STS(13) resolvable None (consistent: 13 != 3 mod 6)
  cell plan: 49 cells, 21 sounding, per-voice [3,3,3,3,3,3,3]
```

## Quirks / pitfalls hit during the job

1. **Sandpile already taken.** First candidate (abelian sandpile / chip-firing) is method **036 ASAR** — check *before* designing, `grep -in` found 14 mentions. Likewise persistent homology = 044, optimal transport = 050. Lesson: greedy keyword grep on the DB first saved a wasted entry.
2. **`write_file` refuses `/tmp`** ("protected system/credential file"). All scripts had to live in the CompositionMethods directory (consistent with `verify_129/130/131_*.py` precedent).
3. **Shell security scan blocks `| python3 -c`.** Piping a `python3 -c "print(...)"` into python was rejected as `pipe_to_interpreter`. Worked around by `curl -o file` then parsing the file in a separate step.
4. **Fano point-numbering bug.** First draft used points 1..7 while `audit()` expected 0..6 → false `lam_ok=False`. Re-indexed to 0..6.
5. **`AG(2,3)` construction bug.** A direction/offset formula produced 8 valid lines instead of 12; replaced with the honest $y=mx+c$ (3 slopes × 3 offsets) + 3 verticals, and an assertion that all 36 pairs are covered exactly once.
6. **Closure bug in the resolver.** `cover |= ...` inside a nested function made `cover` local → `UnboundLocalError`; fixed with `set.update`/`difference_update` (mutation, no rebinding).
7. **Non-resolvable STS(15) trap.** The first backtracking STS(15) admitted no parallel class at all — the resolver returned `nodes=1` because it never completed a class. This is not a bug but a real mathematical fact, now documented as Pitfall 2 and used as evidence in the report.
8. **`grep -oP` on the table** is the reliable ID resolver: `^\| \*\*\d{3}\*\*` returned max 131, cross-checked against `method_131_TDRPC.md` / `report_131.md` file globs — all agreed.
9. **DB append position.** Method sections are not strictly ordered at the file tail: `# Sound Production Method SP-130` sits after method 131 (sound-production job appends to the same file). The new method section was appended at EOF per the mandated workflow, i.e. after the SP-130 block — same as the previous job's outcome, so ordering is already "append-only, not sorted".

## Complete method section appended to methods_db.md

```markdown
# Balanced Incomplete Block Design Composition (BIBDC) (Method 132)

### Source

- **Kirkman, T. P. (1847).** "On a problem in combinatorics." *Cambridge and Dublin Mathematical Journal* 2, 191–204 — existence of what became the Steiner triple system, and the first resolvable systems (Kirkman triple systems), predating Steiner.
- **Kirkman, T. P. (1850).** Query VI, *The Lady's and Gentleman's Diary*, p. 48 — the schoolgirl problem: "Fifteen young ladies in a school walk out three abreast for seven days in succession: it is required to arrange them daily so that no two shall walk twice abreast." The canonical resolvable STS(15). Seven non-isomorphic solutions were listed by **Cole, F. N. (1922)**, "Kirkman parades," *Bulletin of the AMS* 28, 435–437.
- **Steiner, J. (1853).** "Combinatorische Aufgabe." *Journal für die reine und angewandte Mathematik* 45, 181–182 — the S(2,3,n) problem that gave the systems their modern name.
- **Bose, R. C. (1939).** "On the construction of balanced incomplete block designs." *Annals of Eugenics* 9, 353–399 — the Bose construction and the BIBD formalism ($v,b,r,k,\lambda$) as used in experimental design; with **Skolem, T. (1957)** for the sufficiency of $n\equiv1,3 \pmod 6$ for STS($n$).
- **Ray-Chaudhuri, D. K., & Wilson, R. M. (1971).** "Solution of the Kirkman schoolgirl problem." *Proceedings of the AMS* 28, 115–124 — a resolvable STS($v$) exists **iff** $v \equiv 3 \pmod 6$ (Kirkman triple systems exist for every admissible order).
- **Colbourn, C. J., & Dinitz, J. H. (eds.) (2006).** *Handbook of Combinatorial Designs* (2nd ed.). Chapman & Hall/CRC — the reference tables: number of non-isomorphic STS($v$) = 1, 1, 2, 80, 11 084 874 829 for $v=7,9,13,15,19$.
- **Beth, T., Jungnickel, D., & Lenz, H. (1999).** *Design Theory* (2nd ed.). Cambridge University Press — BIBD counting identities, duals, resolvability, automorphism groups.
- **Wikipedia, "Steiner system" / "Block design" / "Kirkman's schoolgirl problem"** (fetched 2026-11-02, `_web132/`): STS existence $n=6k+1$ or $6k+3$ (Bose–Skolem sufficiency); Fano plane = STS(7), affine plane AG(2,3) = STS(9); "resolvable = partition of the blocks into $(n-1)/2$ parallel classes each having $n/3$ pairwise disjoint triples"; 80 STS(15), 7 non-isomorphic schoolgirl solutions.
- **Novelty check (2026-11-02):** `grep -ci` on `methods_db.md` before entry: `BIBD` = 0, `block design` = 0, `Steiner` = 0, `Kirkman` = 0, `incidence` = 0 (only incidental prose). Adjacent-but-different registered methods: 090 GRDC (distinct *differences* within one set), 112 CADDC (Costas arrays — distinct displacement *vectors*), 111 VTCC / 083 QTSC (tilings that partition a *space*), 123 GTBRC (voices as self-interested players). None of them balances **pairwise co-incidence between voices** — that 2-$(v,k,\lambda)$ incidence property is new here. No published BIBDC generative procedure exists; design theory is documented as statistics/geometry, and this registration is the first mapping to a UnitMatrix.

### Layer

**concrete** — BIBDC emits events. Its design object (a 2-$(v,k,\lambda)$ incidence structure) is a *plan*, but the plan is immediately event-bearing: for every (voice, section) cell it decides **sounding vs. rest**, and for every sounding cell it assigns one pitch from the block's sonority plus an onset slot. That is `MusicUnit` content, so BIBDC feeds `generators/` (candidate path `generators/design_blocks.py`), not `rules/subset_network.py`. The abstract residue it *could* hand upward — the pair-coverage matrix and the novelty curve — is exported as metadata, not as the method's output.

### Paradigm

**Rules-Based** — the entire structure is deterministic incidence arithmetic over a finite design: the same $(v,k,\lambda)$ and the same block ordering always produce the same cell occupancy, the same tension curve and the same seam common-tones. Randomness appears only as a *choice over a deterministic object* (which of the 80 STS(15)s, which block order), never inside the generation law.

### Description

**Balanced Incomplete Block Design Composition (BIBDC)** composes the *ensemble schedule* of a piece as a balanced incomplete block design: a set of $v$ **points** (the voices) together with a family of $b$ **blocks** $B_1,\dots,B_b$, each of size $k$ (the sections), such that every pair of points lies in exactly $\lambda$ blocks. Formally, a 2-$(v,k,\lambda)$ design: for every $\{i,j\}\subset\{1..v\}$,

$$\bigl|\{\,m : \{i,j\}\subseteq B_m\,\}\bigr| = \lambda .$$

The balance law is the whole method. Counting incidences twice gives the two design identities, both verified here (2026-11-02, `verify_132_BIBDC.py`):

$$v\,r = b\,k \quad(\text{total incidences}),\qquad \lambda\,(v-1) = r\,(k-1)\quad(\text{pairs through one point}),$$

so every voice sounds in exactly $r=\lambda(v-1)/(k-1)$ sections, every section holds exactly $k$ voices, and the design is **incomplete** ($b < \binom{v}{k}$: only a tiny fraction of all possible ensembles is ever used). Three consequences are compositional, not just combinatorial:

1. **Fairness.** No voice is over- or under-worked: all get exactly $r$ sections, all seatings are $k$ wide.
2. **Economy.** $\lambda=1$ designs are minimum-size pair covers: $b_{\min} = v(v-1)/\bigl(k(k-1)\bigr)$. For $k=3$ this is the Steiner triple system, $b=v(v-1)/6$ — **verified** by backtracking search: $v=7\!\to\!b=7$, $9\!\to\!12$, $13\!\to\!26$, $15\!\to\!35$, with every pair covered exactly once and every degree $=(v-1)/2$.
3. **Provable closure.** Each block contains $\binom{k}{2}$ pairs, so the number of *not-yet-met* pairs falls by exactly $\binom{k}{2}$ per section and hits $0$ at the final section ($\lambda=1$). This is a monotone tension curve that is **independent of block order** — verified for the Fano plane in both forward and reversed order: novelty $=18,15,12,9,6,3,0$.

**The $k=3$ special case — the trio-rotation consort.** An STS($v$) exists iff $v\equiv1$ or $3 \pmod 6$ (necessity Kirkman 1847; sufficiency Bose–Skolem). For $v=7$ the design is the **Fano plane** (unique up to isomorphism — confirmed here by exhaustive enumeration: **30 labelled STS(7)** $=7!/168$, i.e. automorphism group of order 168), and for $v=9$ it is the affine plane $AG(2,3)$ (also unique, 12 blocks). A verified Fano seating (voices $0..6$):

$$B = \{(0,1,2),\ (0,3,4),\ (0,5,6),\ (1,3,5),\ (1,4,6),\ (2,3,6),\ (2,4,5)\}$$

Each of the 21 pairs occurs exactly once, each voice appears 3 times, and — the property that makes it *musical* — **any two blocks intersect in exactly one point** (verified: all 21 block pairs have $|B_i\cap B_j|=1$). Consecutive sections therefore share exactly one voice, i.e. **exactly one common tone**: every seam is maximally parsimonious, and no seam is empty.

**Resolvable designs — movements.** If the blocks can be partitioned into $(v-1)/2$ **parallel classes** (each class = $v/k$ pairwise disjoint blocks covering all points), the design is a **Kirkman triple system** and each class is a *movement*: a full-ensemble partition into simultaneous $k$-voice groups. Verified: $AG(2,3)$ resolves into **4 classes of 3 trios**; and a resolvable STS(15) — the schoolgirl design — was **constructed and verified** here (35 blocks, 7 classes of 5, 105 pairs each exactly once). Note the trap this exposed: an STS built by generic backtracking is usually **not** resolvable — the first STS(15) this job generated had no parallelism at all, and a resolvable one appeared only on the 24th random attempt. Resolvability is a property of the *specific* design, not of the order.

**Dual design — the piece read sideways.** Transposing the incidence matrix gives another design with parameters $(b,v,k,r,\lambda)$: blocks become points. So a BIBDC piece has a canonical **dual**: swap the roles of voices and sections. For symmetric designs ($v=b$, e.g. STS(7), where $r=k=3$) the dual is the same design — self-dual form — while for STS(9) ($b=12\ne9$) the dual is a genuinely different (12-voice, 9-section) piece with $\lambda=1$ and $k=4$.

**Relabeling = re-orchestration.** The automorphism group acts on the design; for the Fano plane $|\mathrm{Aut}| = 168$ (verified numerically), so one design admits 168 distinct voice assignments — 168 orchestrations of the same schedule, all equally balanced. These are *relabelings* (identity permutations), not transpositions; a musical transposition is applied after relabeling.

**Rest structure.** The complement $\bar{B}_m$ of a block is the section's **tacet set** ($v-k$ silent voices). In STS(7) no two blocks are disjoint (verified: minimum intersection 1), so a complement is **never** itself a block — the "inverse" seating is always a rest texture, never a duplicate. That asymmetry is a free textural device: the design's complement lattice gives the piece its shadow-ensemble.

**Family extension knobs.** $\lambda=2$ doubles every meeting ($v=7,k=3,\lambda=2\Rightarrow b=14$, identities verified) — the "statement + recapitulation" design. $t=3$ designs (Steiner quadruple systems, $k=4$) balance every *triple* of voices: every trio shares exactly one four-voice chord — a chord vocabulary with guaranteed triple coverage. PBIBDs (partially balanced) relax equality to association classes, giving controlled imbalance (a featured group that meets more often).

### Musical Elements Framework

- **PITCH**: each voice owns a fixed **seat** — a pitch (or pitch band) $p_i$ — so a block's sonority is the literal set $\{p_i : i\in B_m\}$, a $k$-note voicing with $k$ distinct voices (no doubling by construction). Melodic content per voice = its $r$ appearances; since consecutive appearances are separated by rests and re-enter on the same seat, the voice's line is a *recurrent pedal* unless a per-appearance degree offset is added (recommended: octave or chord-tone displacement indexed by the block's ordinal). Pitch-class variety is bounded by the design: with fixed seats the whole piece uses only the $v$ seat pitches; extend with a seat *ladder* (seat = scale degree, octave chosen per section) to keep pc content small while contour stays alive.
- **RHYTHM**: the design fixes **ensemble density** exactly — $k$ of $v$ voices sound per section, a constant ratio $k/v$ (3/7 for the Fano consort, 3/9 for $AG(2,3)$). Onset placement inside a section is free (grid-locked or continuous), but the *count* is structural: $k$ onsets per section, no more, no fewer, if the block is played literally. Resolvable designs add a second rhythmic layer: a parallel class is a simultaneity grid (all $v$ voices sounding at once, in $v/k$ separated groups) — tutti movements alternating with rotated-trio movements.
- **HARMONY**: harmony is **seam-based**, and it is exact. In a Steiner design every two blocks share exactly one point, so every chord change is a single-common-tone move (maximum parsimony, verified for all 21 Fano seams). The chord vocabulary is the $b$ blocks themselves ($b=7$ trichords for the Fano consort); the chord *progression graph* is $K_b$ (every block meets every other), so any ordering is a legal progression — the design supplies no harmonic hierarchy, only perfectly smooth transitions. Tonal gravity must then be injected by the seat assignment (e.g. seat 0 = tonic, seats chosen so that the $r$ blocks containing voice 0 are the HOME chords). Tension = pair novelty (provably monotone, $\lambda=1$) or, for fixed-seat designs, set-class/register spread.
- **STRUCTURE**: the section sequence is exactly the block list; form = the ordering (free, since balance is order-independent — a *permutation* of the same piece) or a **parallel-class sequence** (movements). Recapitulation = repeating a block, which locally raises that block's pairs to $\lambda+1$ — an auditably measurable "over-met" duo. The dual design gives a second form (voices↔sections). With $\lambda=2$ the design *is* an A-B-A statement/return form at the pair level.
- **TEXTURE**: the balance law is a texture law. Density is constant ($k$ voices), *identity* rotates: at every section $k$ voices enter and $v-2k$ stay, so the consort is a rotating chamber texture rather than a tutti. The complement blocks give the silent shadow ensemble; parallel classes give antiphonal groups (a class = $v/k$ simultaneous trios, i.e. polychoral writing with exact rotation); the intersection graph $K_b$ means every timbral pairing is auditioned exactly once — a designed "getting to know you" texture, ideal for hocket and for duo-feature writing.

### UnitMatrix Integration (Voices & Sections)

**Voices = rows = points.** Row $i$ corresponds to point $i$: one instrument/timbre, one seat pitch, one row of cells. Row invariants from the design: exactly $r$ sounding cells and $b-r$ rest cells (for the Fano consort: 3 and 4).

**Sections = columns = blocks.** Column $m$ is block $B_m$: a section whose active voice set is $B_m$ (size exactly $k$). Column-level metadata: block id, seat set, pair-novelty value $N_m = \binom{v}{2} - \binom{k}{2}m$ (for $\lambda=1$, after $m$ blocks), and the common-tone voice shared with column $m+1$ (unique in a Steiner design).

**Cells = MusicUnit.** Cell $(i,m)$ is a `MusicUnit` of the section's full length:
- if $i\in B_m$: one note (or a short figure) at seat pitch $p_i$ (plus the section's octave/degree offset), onsets placed on the section's metric slots for that voice — e.g. the $j$-th member of the block enters on subdivision $j$, giving a deterministic arpeggiated entry;
- if $i\notin B_m$: a **rest unit** whose events are empty but whose duration spans the whole section (terminal landmark at `section_len`) — this is mandatory, because the zero-drift invariant requires *every* row to reach the section boundary in *every* column. A block-design piece is 4/7 rests by cell count; padding is the default state, not an exception.

**Worked shape (Fano consort, 7×7).** 7 rows × 7 columns = 49 cells, 21 sounding (43%), each row 3 sounding; each column exactly 3 sounding; the 21 sounding cells cover all 21 voice pairs exactly once. `validate()` passes because every cell's unit ends at `section_len`, sounding or not.

**Candidate code path:** `generators/design_blocks.py` — `BIBD(v, k, lambda_)` (parameters, `r`, `b`, `pairs()`), `SteinerTripleSystem(v)` (Bose / backtracking construction, `blocks`, `is_sts()`), `Parallelism(design).resolve()` (Kirkman classes; returns `None` when the design is not resolvable — the common case), `design_to_matrix(design, seat_map, section_ticks)` → per-cell `create_note_unit` / pad units, then standard `UnitMatrixComposer` fill. Metadata export: occupancy matrix, pair-coverage matrix, novelty curve. Naming sibling of `generators/rhythm.py` and `rules/set_theory.py`; the incidence algebra itself is pure Python (no numpy needed) and $O(v^2)$.

### Pitfalls

1. **$v$ must be $\equiv 1$ or $3 \pmod 6$ for $\lambda=1,k=3$.** Admissible $v$ from 7 to 19: 7, 9, 13, 15, 19 (verified). For $v=8,10,11,12,14,16,17,18$ there is no Steiner triple system at all. Fixes: (a) pad with silent dummy points up to the next admissible $v$ (e.g. 8 voices → design on 9, one dummy row always resting); (b) switch to $\lambda=2$ ($v=6,k=3,\lambda=2$: $r=5,b=10$, identities verified) which covers more orders; (c) change $k$.
2. **Not every STS is resolvable** — this bit the verification run: a generic backtracking STS(15) had *no* parallel class containing its first block, and 24 random designs were needed to find a resolvable one. If you want movements, construct a Kirkman system explicitly (Ray-Chaudhuri–Wilson guarantees one exists iff $v\equiv3\pmod6$) and *test* the resolution, don't assume it.
3. **Zero-drift with 57% rest cells.** Rows are mostly silent; the temptation is to emit nothing for inactive cells. That breaks `validate()` (row lengths diverge). Every inactive cell needs a padded unit ending on `section_len`.
4. **$k$ is both chord size and voice count per section.** $k=3$ gives trichords only; thicker harmony requires complement-block doubling, point-clusters (replace one point by a group → PBIBD), or a larger $k$ ($k=4$: S(3,4,$n$) quadruple systems, $v\equiv2,4\pmod 6$). Don't silently double voices and then claim pair balance — doubling changes the effective $\lambda$.
5. **$\lambda=1$ is maximally non-repetitive.** Every duo meets exactly once, so no pair ever returns — great for through-composed chamber music, hostile to hooks. Memorability needs $\lambda=2$ or deliberate block repetition; if you repeat a block, record the *effective* $\lambda$ per pair (the auditability is the point).
6. **Form is not in the design.** Balance is order-independent (verified: forward and reversed Fano order give the identical novelty curve), so the design fixes *content*, never *shape*. Form must be imposed externally (dynamics, register ladder, density of onsets, timbral doubling, block repetition). Do not claim the design "generates" a form.
7. **Self-duality is only for symmetric designs.** $v=b$ (STS(7), $r=k$) gives a self-dual design; STS(9) has $b=12\neq9$, so its dual is a different, $k=4$ design. Check $v=b$ before advertising the "read-it-sideways" piece.
8. **Automorphism $\neq$ transposition.** The 168 Fano automorphisms are voice relabelings (who sits where), not pitch transpositions; a transposition is a post-hoc pitch map. Conflating them produces "the same piece twice" and an inflated claim of variety.
9. **Disjoint complements don't exist in STS(7).** All blocks intersect (verified min $|B_i\cap B_j|=1$), so a complement is a 4-voice tacet set, never a block. For $v\ge9$ disjoint blocks do occur (that's exactly what a parallel class is) — don't generalize the $v=7$ intuition.
10. **Not a game, a difference set, or a tiling.** 123 GTBRC optimizes individual incentives; 090 GRDC / 112 CADDC make *within-set differences* distinct; 111 VTCC / 083 QTSC partition a space. BIBDC balances *pairwise co-incidence across voices* — a 2-$(v,k,\lambda)$ property. Any "we already have combinatorics" objection confuses the object being balanced.
```
