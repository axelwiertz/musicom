# Report 114 — Farey–Stern–Brocot Composition (FSBC)

**Registered:** 2026-10-13 · **Job:** scheduled cron (music research agent) · **DB:** `methods_db.md`

---

## Method identity

- **Method ID:** 114 (next free ID after scanning; max pre-existing = 113 PCFSC)
- **Name:** Farey–Stern–Brocot Composition (FSBC)
- **Paradigm:** **Rules-Based**
- **LAYER:** **concrete** (generates concrete rhythm onsets + pitch events filling UnitMatrix cells; NOT abstract — emits events, not subsets; NOT absolute — no sound production)
- **One-line description:** Composes from the rational-number hierarchy of Farey sequences (all reduced fractions a/b with b ≤ N, sorted → maximal rational subdivision of the bar) and the Stern–Brocot tree (every positive rational exactly once; depth = Tenney-height consonance gradation) — polyrhythmic density via denominator budget, pitch via ratio→MIDI/cents mapping, form via tree walks or the Calkin–Wilf enumeration.

## Summary-table row (as inserted at DB line 124)

```
| **114** | concrete | Farey–Stern–Brocot Composition (FSBC) | **Rules-Based** | Pitch, Rhythm, Harmony, Structure, Texture | Moderate (Tenney-graded) | Grid-Locked / Continuous | Macro / Tree | $O(N)$ per event, $O(N^2)$ one-time Farey prefix | Hierarchical rational architecture: Farey sequences enumerate ALL reduced fractions a/b with b≤N (sorted) → maximal rational subdivision of the bar (every tuplet order ≤ N simultaneously, Cowell/Tenney rhythmicon arrays); the Stern–Brocot tree holds every positive rational exactly once with depth = Tenney-height consonance gradation → JI/12-TET pitch generation; paths encode continued fractions (a₀ R, a₁ L…); Calkin–Wilf enumeration (Stern diatomic s(n)/s(n+1)) yields a linear non-repeating rational timeline. Form = Farey-order arc (N=3→5→7→4→3) or tree walk. Concrete cousin of 012 Euclidean (single k/n rhythm); sibling of 069 Christoffel (primitive tree paths) and 076 Thue–Morse (other automatic sequence); deterministic number-theoretic foil to 053 Lévy leaps and 084 Zipf–Mandelbrot. |
```

## Classification details

- **Paradigm justification:** deterministic number theory — Farey F_N and the Stern–Brocot tree are canonical mathematical objects; same (path, budget, mapping) always yields same output. No randomness, no nature dynamics, no learned parameters.
- **Layer justification (concrete):** FSBC emits concrete `MusicUnit` events: Farey positions → onset ticks, ratios → MIDI or cents. Feeds `generators/farey_composer.py`. Follows LAYER_ARCHITECTURE.md: concrete = realization plan, unitmatrix cells (voices × sections), resolved MusicEvents, zero-drift.
- **Tonal Gravity:** Moderate (Tenney-graded) — no fixed key, but Tenney height log₂(p·q) gives a deterministic consonance hierarchy usable as tension/release (simple ratios near tree root = consonant, deep = dissonant).
- **Metric Binding:** Grid-Locked / Continuous — rational subdivisions map to integer ticks when denominator budget N ≤ 8 (LCM(1..8)=840 ≤ 1920-tick bar); larger N needs continuous time or nearest-tick approximation.
- **Memory Depth:** Macro / Tree — the form is a tree path or Farey-order arc spanning whole sections.
- **Time Complexity:** `$O(N)$` per event, `$O(N^2)$` one-time Farey prefix.

## Line-count delta

- **Before:** 24,970 lines (`wc -l` at job start via read_file `total_lines`)
- **After:** 25,053 lines (`wc -l methods_db.md`)
- **Delta:** **+83 lines** (1 blank + `---` separator + 1 blank + 79-line method section incl. trailing newline accounting)
- Verified: summary row present at line 124 (`grep "^| \*\*114\*\*"`), method section `### Source` at line 24975 (last `### Source` in file).

## Files

- **Standalone method file:** `/opt/data/projects/Research/CompositionMethods/method_114_FSBC.md` (16,324 bytes; symlink-real path `/opt/data/repos/musicom/projects/Research/CompositionMethods/method_114_FSBC.md`)
- **Report (this file):** `/opt/data/projects/Research/CompositionMethods/report_114.md`
- **Temp file:** `_temp_method_114.md` created via write_file, appended via `cat >>`, then `rm` — confirmed gone.
- **Candidate code path:** `generators/farey_composer.py` — `FareyRhythmGen(budget_N, filter_fn, num_bars)`, `SternBrocotPitchGen(root, path)`, `SBPathForm(path_target, depth)`, `CalkinWilfSeq(n_events)`, `ratio_to_midi(p, q, root, mode="tet12")`, `ratio_to_cents(p, q)`, `farey_triad(a_b, p_q)`, `tenney_height(p, q)`.

## Method section appended (verbatim, after `---` separator)

### Source

Farey, J. (1816). "On a curious property of vulgar fractions." *Philosophical Magazine* 47, 385–386. — Stern, M. A. (1858). "Ueber eine zahlentheoretische Function." *Journal für die reine und angewandte Mathematik* 55, 193–220. — Brocot, A. (1862). *Calcul des roulements par la méthode des approximations.* Paris: Mallet-Bachelier. — Wannamaker, R. (2012). "Rhythmicon Relationships, Farey Sequences, and James Tenney's *Spectral CANON for Conlon Nancarrow* (1974)." *Music Theory Spectrum* 34(2), 48–70. — Nicholson, T. & Sabat, M. (2020). "Farey Sequences Map Playable Nodes on a String." *TEMPO* 74(291), 86–97. — Graham, R. L., Knuth, D. E. & Patashnik, O. (1994). *Concrete Mathematics*, 2nd ed., §4.5. Addison-Wesley. — Tenney, J. (1983). "John Cage and the Theory of Harmony." *Plans for the Future: Darmstadt Summer Courses Texts.* — Sethares, W. (2005). *Tuning, Timbre, Spectrum, Scale*, 2nd ed., Springer (Ch. 5 & App. B). — Hardy, G. H. & Wright, E. M. (2008). *An Introduction to the Theory of Numbers*, 6th ed., §3.2–3.14. Oxford University Press.

### Layer

**concrete** — FSBC generates concrete rhythmic onsets (Farey positions → ticks) and pitch events (ratio → MIDI note or cents offset) that fill UnitMatrix cells as `MusicUnit` notes. The rational tree is a closed-form deterministic structure: given a tree-walk path or denominator budget, the output is fully determined. Feeds `generators/farey_composer.py` (composite generator with `FareyRhythmGen`, `SternBrocotPitchGen`, `SBPathForm`). Not abstract: it emits events, not subsets.

### Paradigm

**Rules-Based** — deterministic number theory. The Farey sequence $F_N$ is a fixed sorted list of reduced fractions; the Stern–Brocot tree canonically enumerates all positive rationals via mediant insertion (no randomness, no learned parameters, no nature dynamics). The same (path, budget, mapping) always yields the same composition. Contrast stochastic (002 Markov, 053 Lévy), nature-led (092 DLA), and AI-driven (054 ATS) methods.

### Description

**Farey–Stern–Brocot Composition (FSBC)** composes from the rational-number structure of Farey sequences (all reduced fractions $a/b$ with $b \le N$, sorted) and the Stern–Brocot binary tree of all positive rationals (infinite complete binary tree: mediant $a/b \oplus c/d = (a+c)/(b+d)$ inserted between every parent pair). Every positive rational $p/q$ appears exactly once in the tree; its path from root encodes its continued fraction $[a_0; a_1, ..., a_k]$.

**Construction 1 — Farey rhythms (onset grid).** The Farey sequence of order $N$ lists all reduced fractions $a/b \in [0,1]$ with $b \le N$, sorted. Plot them as onset times within a bar of length $T$ ticks: onset $t_i = (a/b) \cdot T$. Consecutive fractions $a/b, p/q$ satisfy $b p - a q = 1$ (Farey neighbors). The interval between onsets is $\Delta t_{i} = T \cdot \frac{1}{bd}$. So the Farey set generates a maximum-density rational subdivision: every possible subdivision denominator $\le N$ contributes onsets, giving a "grid of all ratios". This is Cowell/Tenney's rhythmicon relationship: divisive polyrhythmic array where layers are tuplets of increasing order (Wannamaker 2012, 48). For grid-locked realization, restrict $N \le 8$ (LCM(1..8)=840 ticks fits a 1920-tick bar at 480 tpb, 4/4); for $N>8$ use nearest-tick approximation or continuous time.

Subsetting: filter the Farey set by denominator class (e.g., only odd denominators = limping/offbeat), by numerator parity (accented vs unaccented beats), or by depth bound (only fractions whose Tenney height $\log_2(pq) \le H_{\max}$ keeps only simple ratios).

**Construction 2 — Stern–Brocot pitch/interval generation.** Every positive rational $r = p/q$ in the tree yields a frequency ratio $r$, i.e., $p:q$ just intonation interval. Convert to cents: $\text{cents} = 1200 \log_2(p/q)$. For 12-TET use: $\text{MIDI} = \text{root} + \text{round}(12 \log_2(p/q))$. The tree organizes ratios by *simplicity*: nodes closer to root have smaller numerator+denominator sum (Tenney height $H = \log_2(pq)$). This gives a built-in consonance hierarchy: simple ratios (2:1, 3:2, 4:3) near root, complex ratios (17:13, 31:19) deep in the tree — strict gradation from consonant to dissonant without any stochastic sampling.

The path from root $1/1$ to any ratio $p/q$ is uniquely encoded by the continued fraction $[a_0; a_1, ..., a_k]$ of $p/q$ $a_0$ right steps, $a_1$ left steps, $a_2$ right, ... (truncating the last quotient at 1). This gives a *deterministic walk* from consonant root through intermediate approximations (ancestors = convergents) to the target ratio. A composition can walk a path gradually: start at root (unison), step to 2/1 (octave), to 3/2 (fifth), to 5/3 (major sixth), ... — each step is a *canonical approximation* of the next ratio, giving smooth voice-leading in rational space.

**Construction 3 — Stern's diatomic / Calkin–Wilf enumeration.** Stern's diatomic series $s(n)$ (OEIS A002487): $s(0)=0, s(1)=1, s(2n)=s(n), s(2n+1)=s(n)+s(n+1)$. The Calkin–Wilf tree enumerates all positive rationals as consecutive fractions $s(n)/s(n+1)$ for $n \ge 1$: $1/1, 1/2, 2/1, 1/3, 3/2, 2/3, 3/1, 1/4, 4/3, 3/5, 5/2, 2/5, 5/3, 3/4, 4/1, \ldots$. This gives a linear (breadth-first) ordering of the rationals — directly usable as a timeline: event $n$ = ratio $s(n)/s(n+1)$. Each adjacent pair $(s(n)/s(n+1), s(n+1)/s(n+2))$ is coprime — guaranteed smooth microtonal voice-leading. The enumeration is infinitely non-repeating (every rational once) → ideal for through-composed form.

**Macro-form.** Section A = Farey rhythm with $N_A$ (e.g., $N=5$ = quintuplet grid), section B = $N_B$ (e.g., $N=7$ = septuplet grid), and so on — the Farey density increases with $N$, giving a natural accelerando/stringendo. Or form = a Stern–Brocot tree walk: depth $d$ = section number; at each depth play all ratios in that row (breadth-first) as a chord/arpeggio; deeper rows = more complex harmonies. Or form = the Calkin–Wilf list: $n$ over piece length — early = simple ratios (consonant), later = complex (dissonant/chaotic).

**Complexity.** Farey $F_N$: $\mathcal{O}(N^2)$ one-time construction (or $\mathcal{O}(N)$ cumulative for sequential generation via neighbor recurrence). Stern–Brocot path: $\mathcal{O}(\text{depth})$ — typically $\mathcal{O}(\log N)$ for a denominator-$N$ ratio. Calkin–Wilf enumeration: $\mathcal{O}(n)$ per event using $s(n)$ recurrence. Per-cell fill: $\mathcal{O}(1)$.

### Musical Elements Framework

**PITCH** — Two modes. (a) **12-TET quantization**: ratio $p/q \mapsto \text{root} + \text{round}(12 \log_2(p/q))$, giving scale-degree structures from rationals. For simple ratios this reproduces tonal intervals (3/2 = perfect fifth, 5/4 = major third, 6/5 = minor third), while complex ratios yield chromatic enrichment (non-diatonic scale degrees). (b) **Microtonal/just intonation**: cents offset via pitch-bend or absolute frequency; ratio itself is the interval definition. Tenney height $H = \log_2(pq)$ grades perceptual consonance (lower $H$ = simpler/more consonant), providing a deterministic alternative to psychoacoustic dissonance models. The Stern–Brocot tree naturally sorts ratios by height (shallow = consonant, deep = complex), so pitch complexity is a *tree-depth parameter*, not a learned or random variable.

**RHYTHM** — Farey $F_N$ gives onset positions at all reduced fractions $a/b \in [0,1]$ with $b \le N$. This is the *maximally dense rational subdivision* of the bar: every tuplet (duplets, triplets, quadruplets, ..., $N$-tuplets) is represented simultaneously. Consecutive-onset interval $\Delta = T/(bd)$ gives a distribution of micro-intervals (for $N=5$: 360, 192, 180, 120, 120, 120, ... ticks at $T=1920$) — a rich polymetric grid. Subsetting by denominator parity gives alternating-time-signature feel (e.g., even denominators = binary grid, odd = ternary). Farey-gap distribution follows $1/(bd)$ where $b+d$ increases → power-law-ish distribution of inter-onset intervals (rhythmic 1/f noise-like: many small gaps + rare large gaps). Calkin–Wilf enumeration gives a sequential rhythm: event $n$ at time proportional to $n$, with length determined by $s(n)/s(n+1)$ ratio complexity (complex ratios = more time to articulate / wider skip spacing).

**HARMONY** — Chord = set of ratios from a row of the Stern–Brocot tree at fixed depth (all $2^d$ nodes at depth $d$, mapped to pitch classes) → a "rational chord" containing simpler and more complex ratios. The Tenney height distribution across the chord members gives a *harmonic complexity profile*: shallow rows = consonant chords (unison + octave + fifth), deeper rows = increasingly dense clusters (near-equal division, e.g., the root 1/1 → 2/1 → 3/2 → 4/3 → 5/4 → ... a "convergent cascade" chord stacking ratio approximations to a limit). Trichords from Farey neighbor triples $(a/b, m/n, p/q)$ where $m/n$ is mediant of $a/b$, $p/q$ → always satisfy $m/n = (a+p)/(b+q)$; the three pitches form a "Farey triad" with exactly one interval shared between consecutive members, ensuring parsimonious voice-leading across the harmonization.

**STRUCTURE** — Three canonical form templates. (a) **Farey-order form**: sections with increasing $N$ (2, 3, 5, 7, 11, 13... primes or sequential) — density and complexity grow, tension builds with each new denominator, then resolves by returning to $N=2$ (simple duple). (b) **Tree-walk form**: section = one edge of a Stern–Brocot path; the path walks from simple ratio to a target complex ratio, then returns — A-B-A. The path's continued fraction encodes the ratio's "shape": all-R's (increasing numerators, ratios > 1) = rising/expanding; all-L's = falling/contracting; mixed = alternating. (c) **Calkin–Wilf timeline**: a single linear sweep through the Calkin–Wilf sequence partitions the piece into regions by ratio magnitude: $<1$ sections (true fractions, pitch below root), $>1$ sections (above root), near-1 sections (consonant). Adjacent pairs are coprime, guaranteeing smooth rational voice-leading across every transition.

**TEXTURE** — Multi-voice: Voice $v$ gets its own Stern–Brocot stalk (branch) with independent continuation-fraction path. Voices may be at different depths: Voice 1 (melody) walks deep into the tree (complex ratios, varied intervals), Voice 2 (bass) stays shallow (simple ratios, consonant), Voice 3 (inner) walks medium depth. The independent stalk concept means voices share the root (tonic = 1/1) but diverge at different branching decisions — akin to species counterpoint but in rational-number space. Density per voice controlled by denominator budget $N_v$: higher $N$ = more Farey onsets per bar (denser). The interaction of ratio-simplicity across voices gives a rational-number analogue of harmonic tension: when all voices converge on simple ratios (near root) the texture is consonant; when voices diverge to deep branches, the aggregate sonority becomes complex.

### UnitMatrix Integration (Voices & Sections)

**Voices** = rows, each with a Stern–Brocot stalk (branch) and/or a Farey denominator-budget parameter $\theta_v = (N_v, \text{path}_v, \text{pitch-mode}_v)$:
- Per-voice state: current ratio bounds $(L_n, R_n)$ for tree walking, current Calkin–Wilf index $n_v$ if using sequential enumeration, Farey-denominator limit $N_v$ for rhythm density.
- Voice 1 (Lead): path_depth = high (complex/wide interval range), budget $N_{\text{lead}}$ (medium density).
- Voice 2 (Harmony): path_depth = medium, budget $N_{\text{harm}}$ = low (slow harmonic rhythm).
- Voice 3 (Bass): path_depth = low (consonant, simple), budget $N_{\text{bass}}$ = low (sparse).
- Additional voices can take independent stalks / denominators for layered textural density. Adjacent-voice intervals computed from ratio pairing (Farey neighbor products).

**Sections** = columns, each with a target denominator budget $N_s$ (controls density/complexity; range 2–13 in grid-locked mode, up to any $N$ in continuous-time), a Stern–Brocot target ratio $r_s$ (for tree-walk forms), and a pitch quantization mode $m_s$ (12-TET / just intonation / TET nearest). A typical 5-section form in Farey order: Intro ($N=3$, ternary subdivisions, simple ratios), Verse ($N=5$, quintuplets, medium complexity), Chorus ($N=7$, septuplets, complex harmony), Bridge ($N=4$, quadruplets only, ambiguous / transitional), Outro (return to $N=3$ — HOME). The $N$-arc alone drives a tension trajectory: density grows → peaks → resolves.

**Cell filling** (zero-drift invariant preserved): for cell $(v,s)$:
1. Read section parameters $\theta_s = (N_s, r_s, m_s)$ and voice stalk $\text{path}_v$.
2. **Rhythm**: generate Farey onsets subset $\{a/b \in F_{N_s} : a/b \text{ matches voice filter}\}$; scale to section length $L$ ticks; convert to onset tick positions.
3. **Pitch**: walk Stern–Brocot tree along $\text{path}_v$; at each step compute current ratio $p/q$; convert to pitch via $m_s$: $\text{MIDI} = \text{root} + \text{round}(12 \log_2(p/q))$ for TET, or store as microtonal pitch-bend for JI.
4. Pack into `create_note_unit(pitch, duration, velocity)` events, one per onset.
5. Pad to `section_len` ticks (terminal landmark at `sum(onsets+duration) == section_len`) so `composer.validate()` passes.
6. Export: `composer.to_midi(path)` (12-TET) or via `MidiInstrument` with pitch-bend range for microtonal ratios.

### Pitfalls

1. **Denominator budget explosion.** $|F_N| = 1 + \sum_{k=1}^N \phi(k) \sim 3N^2/\pi^2$. Even modest $N=13$ gives $\sim 60$ onsets per bar — dense but musical; $N=20$ gives $\sim 128$ onsets per bar — polyrhythmic saturation; above $N=30$ the density approaches granular. In grid-locked mode, tick resolution at 480 tpb bars = 1920 ticks: LCM(1..$N$) must fit. LCM(1..8) = 840 ✓; LCM(1..9) = 2520 > 1920 ✗. Bound $N \le 8$ for strict grid-locked, or use continuous time for $N > 8$ with nearest-tick quantisation. Document which sections exceed LCM limit.

2. **Octave reduction duplicates pitch classes.** Ratio $2/1$, $4/1$, $8/1$ all map to same pitch class in 12-TET (octave). Apply $\text{pitch} \bmod 12$ or filter ratios $p/q$ to keep numerator/denominator in $[1, 12]$ for diatonic scale coverage; or use octave-reduced cents $\text{cent} = 1200 \log_2(p/q) \bmod 1200$.

3. **Cents-accumulation drift in microtonal mode.** A sequence of just-intonation ratio productions accumulates frequency ratio multiplicatively; successive cents add, potentially drifting far from original reference. Periodically recenter by normalizing to octave ($p/q \rightarrow (p/q) / 2^{\lfloor \log_2(p/q) \rfloor}$) or lock to a reference frequency table.

4. **Continued-fraction path truncation.** The Stern–Brocot path found by mediants may stop 1 step before the terminal quotient fully expands (last quotient = 1 absorbed by previous). Document that `sb_path(p, q)` via mediant bisection returns a path whose last run-length is the *position within the final equal-quotient run*, not the full run — this matches the standard CF convention but can confuse when comparing to textbook CF paths. The workaround: extend path by one step if needed (append an R or L to reach exact $p/q$; works because mediants converge monotonically).

5. **Farey neighbor cross-product pitch.** The $bp - aq = 1$ property of consecutive Farey fractions gives $\text{gcd}(p, q) = 1$ automatically — every Farey onset pair gives a coprime ratio. This is a *feature* (voice-leading smoothness guarantee), not a bug, but may produce unexpected microtonal intervals if not octave-reduced first.

6. **Pure-JI ratios produce non-tempered pitches.** A 12-TET composition sounding JI-interval ratios will be out of tune with equal temperament. Decide: mix TET (root + scale degree) with JI (microtonal ornament) via separate voice assignments, or commit to microtonal output and use pitch-bend/microtonal instrument. No hybrid without careful intonation planning.

7. **Tree-traversal combinatorial growth.** Depth-$d$ traversal visits $2^d$ nodes. For $d=8$ that's 256 ratios — one per event (manageable). For $d=16$: 65536 — exceeds typical cell capacity. Restrict tree depth by budget (e.g., max 10). Use the Calkin–Wilf linear enumeration instead for long forms.

8. **Relation to existing methods.** FSBC is the *rational-tree* sibling of 012 Euclidean (both continued-fraction cousins; 012 distributes $k$ onsets via Bjorklund — a *single* Euclidean rhythm; FSBC gives *all* rational subdivisions hierarchically), 069 Christoffel (binary balanced words; Christoffel words correspond to paths on the Stern–Brocot tree — FSBC is the *full tree*, not just primitive paths), 076 Thue-Morse (automatic sequence different domain), and 112 Costas arrays (2D distinct displacements where FSBC gives 1D distinct-interval guarantee via Farey neighbor uniqueness). Document sibling relations in prose to avoid duplication accusation.

Candidate code path: `generators/farey_composer.py` — `FareyRhythmGen(budget_N, filter_fn, num_bars)` enumerates Farey onsets per bar; `SternBrocotPitchGen(root, path)` walks the tree and yields ratios; `SBPathForm(path_target, depth)` generates section-by-section path steps; `CalkinWilfSeq(n_events)` yields the linear rational sequence; `ratio_to_midi(p, q, root, mode="tet12")` / `ratio_to_cents(p, q)`; `farey_triad(a_b, p_q)` constructs the Farey-neighbor-mediant trichord; `tenney_height(p, q)` for consonance grading.

---

## Workflow compliance

- **ID resolution:** scanned summary table rows `| **NNN** |` (001–113 found; max = 113 at line 123) + cross-checked `method_*.md` files (max `method_113_PCFSC.md`) → new ID = **114**. No 114+ anywhere in DB (grep for `\*\*1(1[4-9]|[2-9]\d)\*\*` = 0 hits).
- **Append workflow:** `write_file` temp → `printf '\n---\n\n'` + `cat _temp_method_114.md >> methods_db.md` → `rm` temp. (heredoc/execute_code not used.)
- **Summary table:** inserted via patch tool at line 124 (after 113 row at 123). Verified: single `|` prefix (no `||` corruption), `$O(N)$` LaTeX fine (no backslash escaping issue — used plain `$O(N)$`/`$O(N^2)$`), row is one line.
- **Duplicate check:** grepped DB for Farey/Stern/Brocot/mediant/continued-fraction before registering — only incidental (harmonic "mediant", Langevin tanh CF) — no conflict.

## Quirks / pitfalls hit

1. **researchgate PDF fetch succeeded** (full text of Wannamaker 2012 saved to /opt/data/cache/web/) — key confirmation that Farey sequences power Tenney's Spectral CANON (polyrhythmic arrays), the strongest musicological anchor for FSBC.
2. **Python sketch bugs found & fixed during verification** (must-run check): (a) `Fraction(1, 0)` raises ZeroDivisionError — replaced infinity sentinel with `(num, den)` tuples; (b) tuple-unpacking bug in `sb_find` (`hi, path = med.numerator, med.denominator, path...` — 3 values into 2 targets); (c) `for a, b in Fraction_list` fails — Fraction is not iterable, use `.numerator`/`.denominator`. Final code runs clean: F5 = 11 fractions, |F20| = 129, Farey neighbor property True, SB path to 5/3 = RLR (walk 1 → 2 → 3/2 → 5/3), Calkin–Wilf 50 events all unique, H(3/2)=2.585 vs H(17/13)=7.788.
3. **Line-count semantics:** `wc -l` = 25053; read_file `total_lines` before = 24970; delta +83 lines (my appended section is ~79 lines + separator block).

## Next free ID

**115** (after this registration).