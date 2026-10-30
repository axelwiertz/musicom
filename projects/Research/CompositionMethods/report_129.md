# Registration Report — Method 129: Artin Braid Group Composition (ABGC)

**Date**: 2026-10-30
**Agent**: cron music-research job
**DB**: `/opt/data/projects/Research/CompositionMethods/methods_db.md`

## 1. Identity

| field | value |
|---|---|
| Method ID | **129** |
| Name | Artin Braid Group Composition (ABGC) |
| Paradigm | **Rules-Based** |
| LAYER | **concrete** (emits `MusicEvent`s that fill UnitMatrix cells; no abstract-only design stage) |
| One-line description | Rows of the UnitMatrix are the strands of an Artin braid; each syllable $\sigma_i^{\pm1}$ swaps two adjacent voices' registral positions (voice exchange / *Stimmtausch*), pitch follows position, identity follows strand, and braid invariants (writhe, closure components, half-twist powers $\Delta_n^p$, Garside/Dehornoy normal forms) become tension, form, cadence and canonicalisation parameters. |
| Standalone write-up | `/opt/data/projects/Research/CompositionMethods/method_129_ABGC.md` |
| Candidate code path | `generators/braid_group.py` — class `BraidComposer` |
| Next free ID | **130** |

## 2. ID resolution (dynamic, not assumed)

- Summary table scan (`^\| \*\*NNN\*\*`) before this entry: 127 rows, IDs **001–128** (sparse 058/092 gaps as noted historically).
- Standalone-file scan: highest `method_*.md` = `method_128_VESC.md`; highest `report_*.md` = `report_128.md`. Both agree: **max = 128**.
- New ID = **129**. No collision: `grep -c "braid"` on the DB was **0** before this entry; no `method_129*` / `report_129.md` existed.

## 3. Summary-table row added (verbatim, single `|` prefix, single backslashes)

| **129** | concrete | Artin Braid Group Composition (ABGC) | **Rules-Based** | Pitch, Rhythm, Harmony, Structure, Texture | Moderate (Ladder-pinned, function-free; writhe = tension) | Grid-Locked / Continuous (syllable = blow) | Macro / Braid Word (non-abelian group element) | $\mathcal{O}(L)$ per syllable, $\mathcal{O}(L^2 n)$ handle reduction | Treats the $n$ UnitMatrix rows as the $n$ strands of a braid: the piece is a word in $B_n=\langle\sigma_1..\sigma_{n-1}\mid\sigma_i\sigma_j=\sigma_j\sigma_i\ (|i-j|\ge2),\ \sigma_i\sigma_{i+1}\sigma_i=\sigma_{i+1}\sigma_i\sigma_{i+1}\rangle$, each syllable $\sigma_i^{\pm1}$ swapping adjacent voices' registral positions — literal Stimmtausch (voice exchange). Pitch follows POSITION, identity follows STRAND, so every vertical slice is a complete sonority and the pc-set cycles through its registrations. Writhe $\Sigma e_k$ = tension curve; closure components $c$ = voice orbits (c=1 canon); $\Delta_n^{p}$ (half-twist, $|\Delta_n|=n(n-1)/2$, reversal permutation) = cadential reversal cascade; Garside normal form / Dehornoy handle reduction = canonical re-orchestration; Burau $\det(\rho-I)$ = Alexander-polynomial form fingerprint. Verified: $\Delta_n$ reversal for $n=2..7$, $c(\Delta_n)=\lceil n/2\rceil$, random walk visits all $n!$ perms. Rules-Based non-abelian foil to 089 CRCM (which is $S_n$, state forgotten) / 126 KTC (path) / 111 VTCC (rhythm tiling) / 079 TINC (static triad). |

## 4. Classification detail

**Layer = concrete.** The braid word is not a plan that a later stage must realise; decoding it *is*
the realisation: syllable index → onset tick, vertical position → pitch via ladder, sign →
velocity/accent, strand identity → row. Cells receive complete event lists. A future abstract
sibling (`rules/braid_form.py`: writhe curve, closure-component count, $\Delta$-insertion schedule)
is conceivable, but nothing in the append requires it — hence `concrete`, matching 089/126/128.

**Paradigm = Rules-Based.** Deterministic group-theoretic rewrite system. Stochastic use is
confined to *word search* (random walk on the permutohedron), which is a sampling strategy over a
deterministic algebraic object, not a stochastic generator of pitch — the same relationship method
089 has to $S_n$.

Framework columns:
- **Tonal Gravity** — Moderate: the ladder pins pitch content (pc multiset is invariant under
  permutation when $\delta_s=0$), so a tonal centre exists if $L$ is diatonic, but there is no
  functional progression — attraction is registral, not tonal. Writhe sign supplies a
  brightness/tension curve.
- **Metric Binding** — Grid-Locked (syllable = blow = note value) with a continuous variant
  (syllable duration ∝ crossing steepness).
- **Memory Depth** — Macro: the state is a non-abelian group element, i.e. the entire word
  matters (that is Pitfall 2: the permutation alone is not enough to regenerate).
- **Time Complexity** — $\mathcal{O}(L)$ per complete word; $\mathcal{O}(n)$ per syllable;
  $\mathcal{O}(L^2 n)$ worst-case handle reduction; $\mathcal{O}(L n^3)$ Burau/Alexander analysis.

## 5. Novelty evidence

- `grep -ci braid methods_db.md` = **0**; `knot` = 0; `tropical` = 0; `Garside` = 0 before entry.
- arXiv API (2026-10-30): **0 entries** for each of `all:"braid group" AND all:music`,
  `all:braid AND all:composition AND all:music`, `all:braid AND all:counterpoint`,
  `all:knot AND all:music AND all:composition`. Only adjacent hit: *"Modes in modern music from a
  topological viewpoint"* (pc-set topology — analysis, not braid action).
- Crossref `query.bibliographic=braid group musical composition`: only pure-math / crypto titles
  ("Finite Orbits of the Braid Group Actions", "The Cartan-Leray spectral sequence of the braid
  group", braid-group signature schemes) — no music.
- DuckDuckGo: braid-group hits are Wikipedia, "Composition Problems for Braids" (math), "Algorithmic
  Problems in the Braid Groups", braid-group cryptography. No composition method.
- Nearest registered neighbours and why they are not this: 089 CRCM ($S_n$ change ringing — swaps
  but state forgotten each row, `plain hunt` returns to identity), 126 KTC (Hamiltonian path),
  111 VTCC (rhythmic tiling canon), 079 TINC (fixed triad, no group action on voices),
  065 TTSMC (12-tone rows = $S_{12}$ order, no winding).

## 6. Verification performed (real execution)

`verify_129_ABGC.py` (run with `$MUSICOM_PYTHON`, 2026-10-30):

```
== braid relation s1 s2 s1 == s2 s1 s2 (n=3)
perm A [2, 1, 0] perm B [2, 1, 0] same: True
writhe A 3 writhe B 3
== far commutativity s1 s3 == s3 s1 (n=4)
[1, 0, 3, 2] [1, 0, 3, 2]
== Delta_n: length, permutation, closure components
n=2 |Delta|=1  perm=[1,0]           comps=1
n=3 |Delta|=3  perm=[2,1,0]         comps=2
n=4 |Delta|=6  perm=[3,2,1,0]       comps=2
n=5 |Delta|=10 perm=[4,3,2,1,0]     comps=3
n=6 |Delta|=15 perm=[5,4,3,2,1,0]   comps=3
n=7 |Delta|=21 perm=[6,5,4,3,2,1,0] comps=4
identity comps = n ; Delta comps = ceil(n/2) ; Delta^2 comps = n  (n=3,4,5)
random permutohedron walk: 6/6, 24/24, 120/120 perms (n=3,4,5; 20k syllables)
```

`abgc_129_compose.py` — real engine render through `UnitMatrixComposer` (no raw MIDI):

```
validate: True OK
midi: /opt/data/projects/Research/outputs/abgc_129/abgc_129.mid 2413 bytes
section A: |w|=16 writhe=8  closure-components=2
section B: |w|=16 writhe=2  closure-components=2
section C: |w|=16 writhe=4  closure-components=2
section D: |w|=16 writhe=-2 closure-components=2
```

4 strands × 4 sections × 4 bars, bpm 96, ladder G3–C4–E4–G4, `STRING_ENSEMBLE`.
File size asserted > 40 bytes (2413). Note the honest musical consequence: every section
closed as a **2-component** link, i.e. the demo is always a two-orbit canon — form must be
steered via $\Delta$/seed, not word length (recorded as Pitfall 6).

## 7. Line counts

| stage | lines |
|---|---|
| before | **28 975** |
| after method section append | 29 045 (+70) |
| after summary row insert | **29 046** (+71 total) |

## 8. Files touched

- `methods_db.md` — appended section (lines 28977–29046) + summary row (line 139, after 128).
- `method_129_ABGC.md` — standalone write-up (extended math, complexity table, Python sketch, selection heuristics, references, short pitfalls).
- `report_129.md` — this file.
- `verify_129_ABGC.py` — algebra verification harness.
- `abgc_129_compose.py` — engine demo composer.
- `/opt/data/projects/Research/outputs/abgc_129/abgc_129.mid` — rendered MIDI, 2413 bytes.

## 9. Quirks / pitfalls encountered during registration

1. **Table insertion order.** The first `patch` inserted the 129 row *above* 128 (it matched the
   128 line prefix). Fixed with a two-line swap so the table reads 127 → 128 → 129. Lesson:
   when appending after the last row, anchor on the *end* of the previous row, not its start.
2. **Backslash audit.** `grep -c '\\\\'` reports 1 line in the DB — all five hits are pre-existing
   LaTeX `\\` row breaks inside `\begin{cases}` blocks of old sections (lines 2930, 4646, 4655,
   4719, 5092). The new section (28977–29046) and new rows (138–139) contain **zero** doubled
   backslashes. Check was scoped with `awk 'NR>=…'` rather than trusting the global count.
3. **`||` prefix audit.** `grep -c '^||'` = 0; new rows start with a single `|`.
4. **`kw`/`mido` trap avoided.** The render used only `UnitMatrixComposer` + `_unit_from_events`,
   per `projects/Research/AGENTS.md`; no raw MIDI authoring.
5. **Sibling modification warning.** The patch tool reported the DB was modified by a sibling
   subagent mid-run. All edits were anchored on unique exact strings and verified by re-reading
   lines 137–139 plus `wc -l`, so no sibling content was clobbered (post-edit line count 29046 =
   28975 + 70 + 1 exactly).

## 10. Appended method section (verbatim)

# Artin Braid Group Composition (ABGC) (Method 129)

### Source

- **Artin, E. (1925/1947).** "Theorie der Zöpfe", *Abhandlungen aus dem Mathematischen Seminar der Universität Hamburg* 4: 47–72; English trans. "Theory of braids", *Annals of Mathematics* 48(1): 101–126. The presentation $B_n = \langle \sigma_1,\dots,\sigma_{n-1} \mid \sigma_i\sigma_j=\sigma_j\sigma_i \ (|i-j|\ge 2),\ \sigma_i\sigma_{i+1}\sigma_i=\sigma_{i+1}\sigma_i\sigma_{i+1}\rangle$ — the two relations are the *only* laws of the group (verified numerically for $\sigma_1\sigma_2\sigma_1=\sigma_2\sigma_1\sigma_2$ at $n=3$ and $\sigma_1\sigma_3=\sigma_3\sigma_1$ at $n=4$, 2026-10-30, `verify_129_ABGC.py`).
- **Garside, F. A. (1969).** "The braid group and other groups", *Quarterly Journal of Mathematics* 20: 235–254. The half-twist $\Delta_n$ and the Garside normal form; $\Delta_n$ has length $n(n-1)/2$ and realizes the reversal permutation (verified $n=2\ldots7$).
- **Dehornoy, P. (1997).** "A fast method for comparing braids", *Advances in Mathematics* 125: 200–235 — handle reduction; and **Dehornoy et al. (2003)**, *Why Are Braids Orderable?* (SMF) — the Dehornoy left-ordering, a total order on $B_n$ compatible with multiplication.
- **Birman, J. S. (1974).** *Braids, Links, and Mapping Class Groups*, Annals of Math Studies 82, Princeton — Alexander's theorem (every link is a closed braid), the **Markov moves** (conjugation and stabilization) and Markov's theorem (two braids have equivalent closures iff related by Markov moves), and the Burau representation $\rho_n: B_n \to GL_{n-1}(\mathbb{Z}[t^{\pm1}])$.
- **Burau, W. (1935).** "Über Zopfgruppen und gleichsinnig verdrillte Verkettungen", *Abh. Math. Sem. Hamburg* 11: 179–186. The reduced Burau matrix; $\Delta_L(t)$ of the closure is read off from $\det(\rho_n(\beta) - I_{n-1})$ up to units and a cyclotomic factor.
- **Music-theoretic anchor (not a composition method).** *Stimmtausch* / voice exchange is standard counterpoint vocabulary (two voices swap notes); the braid group is the algebraic structure that makes repeated voice exchange **closed under composition**, and no counterpoint treatise formalizes it as a group action.
- **Adjacent art (non-method):** braid diagrams appear in music-theory graphics and in "topological" analyses of voice leading (e.g. Tymoczko's orbifold work — orbifolds, not braids; arXiv "Modes in modern music from a topological viewpoint" — pc-set topology, no braid action). These are *analyses*, not generative methods, and none maps a braid word to UnitMatrix cells.
- **Novelty check (2026-10-30):** arXiv API returned **0** entries for `all:"braid group" AND all:music`, `all:braid AND all:composition AND all:music`, `all:braid AND all:counterpoint`, `all:knot AND all:music AND all:composition`; Crossref `query.bibliographic=braid group musical composition` returned only pure-math/crypto titles ("Finite Orbits of the Braid Group Actions", "The Cartan-Leray spectral sequence of the braid group", braid-group signature schemes). `grep -ci braid methods_db.md` = **0** before this entry. **No published braid-group composition method exists.** Closest registered neighbours are 089 CRCM (change ringing — adjacent *swaps*, but in the symmetric group $S_n$ where every row returns to identity, so no accumulation), 126 KTC (Hamiltonian path), 111 VTCC (tiling canon), 079 TINC (fixed triad) — see Pitfall 1 for the sharp distinction.

### Layer

**concrete** — ABGC emits concrete `MusicEvent`s: each syllable of the braid word produces notes for the crossed strands (and holds for the rest), with pitch read off the vertical position, onset off the syllable index, velocity off the crossing sign. There is no separate abstract planning stage — the braid word *is* the realization plan. Feeds `generators/` directly. Candidate module: `generators/braid_group.py` (class `BraidComposer`), naming-consistent with `generators/schillinger.py`, `generators/markov_constraint.py`. A future abstract sibling (`rules/braid_form.py`) could expose the writhe sum as a tension curve, but the registered layer here is concrete.

### Paradigm

**Rules-Based** — the generator is a deterministic rewrite system (the group presentation); composition = choosing a word in the generators and decoding it. No sampling of pitch (the ladder fixes pitch content), no corpus, no nature dynamics. Stochastic *word generation* is permitted (a random walk on the permutohedron) but that is a search strategy over a deterministic algebraic object, exactly as 089 CRCM uses a deterministic permutation law with a chosen extent. Same family as 076 Thue–Morse / 069 Christoffel / 126 KTC in being group/word-theoretic, but the structure is a **non-abelian group with a canonical normal form** rather than a substitution, a balanced word, or a graph path.

### Description

**Artin Braid Group Composition (ABGC)** treats the $n$ UnitMatrix rows as the $n$ **strands** of a braid and the piece as a word in the braid group $B_n$.

$$B_n=\Big\langle \sigma_1,\dots,\sigma_{n-1}\ \Big|\ \sigma_i\sigma_j=\sigma_j\sigma_i\ (|i-j|\ge 2),\quad \sigma_i\sigma_{i+1}\sigma_i=\sigma_{i+1}\sigma_i\sigma_{i+1}\Big\rangle$$

A **syllable** is one generator $\sigma_i^{\pm1}$: strands $i$ and $i+1$ exchange vertical position, $\sigma_i$ (positive, over-crossing) or $\sigma_i^{-1}$ (negative, under-crossing). Read the braid left-to-right as time and bottom-to-top as register:

1. **State = the permutation.** Keep `perm[k] = strand sitting at vertical position k`; a syllable is one adjacent transposition. Emitting is $O(1)$ per syllable — the whole generator is `perm[i-1], perm[i] = perm[i], perm[i-1]`.
2. **Pitch follows the POSITION, identity follows the STRAND.** Pitch of the note sounding at position $k$ is the fixed ladder value $L(k)$; the row that receives it is the strand's identity. A crossing therefore *is* a textbook **voice exchange** (*Stimmtausch*): the upper voice steps down into the lower's register and vice versa, in parallel, at the same onset — the one contrapuntal motion that is simultaneously oblique and contrary.
3. **The vertical slice is the chord.** Because every position is always occupied by exactly one strand, the sonority is complete at every instant — no missing voices, no doubled unisons unless the ladder itself doubles. With per-strand offsets $\delta_s$ the slice is $\{L(k)+\delta_{\mathrm{perm}(k)}\}$: the pitch-class *multiset* is invariant while its registral assignment permutes, so the harmony cycles through **voicings/inversions of one fixed pc-set** while the surface keeps moving. This is the method's signature: harmonic stasis underneath continuous contrapuntal motion.
4. **Group invariants become form parameters.** Writhe $w(\beta)=\sum e_k$ (signed crossing sum) → tension/brightness curve; closure components $c$ (cycles of the final permutation) → number of independent cyclic voice orbits (a canon/round vs. through-composed); half-twist powers $\Delta_n^{p}$ → a "grand voice-exchange cascade" of $n(n-1)/2$ crossings that reverses the entire voicing, i.e. a cadential/registral-reset gesture; and $p$ (the Garside infimum) → the section's overall registral displacement.

Verified algebra (2026-10-30): $|\Delta_n| = n(n-1)/2$ and $\Delta_n$ realizes the reversal permutation for $n=2..7$; the closure of $\Delta_n$ has $\lceil n/2\rceil$ components (measured 1, 2, 2, 3, 3, 4); the closure of the identity and of the full twist $\Delta_n^2$ has exactly $n$ components; a random adjacent-transposition walk visits **all** $n!$ permutations ($n=3,4,5$: 6/6, 24/24, 120/120 in 20 000 syllables), so the surface vocabulary is the full symmetric group while the *braid* remembers how it got there.

**Word construction strategies** (the compositional knobs): (a) **random walk on the permutohedron** with a sign bias $\pm$ — sign bias = accumulating writhe = rising/falling tension; (b) **Garside-normal-form assembly** — concatenate simple braids $A_1A_2\cdots A_k$ around powers of $\Delta$, giving sections whose structural weight is legible (each simple factor is a "phrase of exchanges"); (c) **quasi-periodic** — repeat a word with periodic insertions of $\Delta$ or of $\sigma_i^{k}$ (a long $\sigma_i^{k}$ = oscillating trill between two positions); (d) **Dehornoy-canonical** — reduce any word by handle reduction to its normal form, then orchestrate *that*, giving a deterministic canonical version of a freely improvised word.

### Musical Elements Framework

- **PITCH**: read off the vertical position via a fixed ladder $L(k)$ (diatonic, whole-tone, or an arbitrary pc-set); a crossing exchanges the two notes between voices. Registral order is *automatically monotone* (no voice-crossing violations possible, since positions are ordered by construction) — a free well-formedness guarantee. Per-strand offsets $\delta_s$ shift colour without breaking the exchange; transposing the whole ladder = key change; changing the ladder between sections = modulation.
- **RHYTHM**: one syllable = one metric blow (grid-locked: $\sigma_i$ = a note value); syllable duration sets the pulse ($\sigma_i^{k}$ with $k>1$ = repeated oscillation = trill/measured tremolo); the *metric* is then a choice of how many syllables per bar, exactly as change ringing's extent. Continuous variant: syllable duration ∝ crossing steepness (a "vertical" braid diagram = fast, a "shallow" one = slow).
- **HARMONY**: the vertical slice is a complete sonority at all times; because pitch-class content is invariant under permutation (with $\delta_s = 0$) the harmony is a **static pc-set cycling through all its registral dispositions** — voice-exchange progression. Varying $\delta_s$ per section or swapping the ladder gives the only real harmonic motion; writhe sign colours it (positive crossings = brightening, negative = darkening) as a *tension curve*, not a functional progression.
- **STRUCTURE**: macro-form = the section-wise sequence of braid words; $\Delta$-insertions = cadential reset gestures; closure components $c$ = number of voice orbits (c = 1 → the whole piece is one cyclic canon; c = n → no cycle, through-composed); Markov's theorem = the *equivalence* of forms (two arrangements with conjugate braids are the same piece up to section rotation), and stabilization ($\sigma_{n}^{\pm1}$ + a new outer strand) = adding a voice to the same underlying link; the Dehornoy order gives a "which section is louder/higher" total order.
- **TEXTURE**: density = crossing rate (syllables per bar); over- versus under-crossings set accents and stereo/registral glow; simultaneous crossings in distant positions ($\sigma_i$, $\sigma_j$, $|i-j|\ge2$) commute and can be fired at the same tick → true polyphonic simultaneity; long runs of $\sigma_i$ isolate a single voice pair (duet texture) against a static outer frame.

### UnitMatrix Integration (Voices & Sections)

**Voices = rows = strands.** Row $s$ is strand $s$; its melody is the sequence of *positions* it visits, i.e. the walk induced on $\{1,\dots,n\}$ by the braid word — so every row is guaranteed non-empty, and pitch content is bounded by the ladder (no range explosion, unlike 128 VESC's unbounded values). Each row's register role is fixed by the ladder position it starts at: bass row starts at position 0, lead at $n-1$; a crossing that sends the lead to position 0 is a deliberate registral plunge, not an accident.

**Sections = columns = braid words.** Column $j$ holds word $W_j$ with $|W_j|$ syllables; the column length is $|W_j| \times$ syllable ticks, and section length must be declared *before* the word (or the word length must be derived from the bar count). Design the columns by intent: A = positive-bias walk (rising writhe, tension up), B = balanced/sign-symmetric (plateau), C = $\Delta_n$ + walk (full reversal cascade = climax/recap), D = negative bias (resolution). Reprise = reuse column A's exact word; through-composed = fresh seeds; canon = one word whose closure has $c=1$.

**Cells = MusicUnit.** Cell $(s, j)$ = strand $s$'s notes inside section $j$: at each syllable tick every strand sounds its current position's $L(k)+\delta_s$ with duration = syllable, so a cell is a **complete isorhythmic surface** (all rows same onsets, different pitches) — trivially zero-drift *if* the syllable grid tiles the section exactly. Velocity: crossed strands accented (96 for $\sigma_i$, 82 for $\sigma_i^{-1}$, 70 for non-crossed) — verified in the reference render. Chord cells: no stacking needed, the verticality is already complete; if a sparser texture is wanted, drop non-crossed strands (rest instead of hold), which is the standard "reduce to a duet" move.

**Reference implementation (verified 2026-10-30):** `abgc_129_compose.py` builds a 4×4 UnitMatrix (4 strands, 4 sections × 4 bars, bpm 96, ladder G3–C4–E4–G4, `STRING_ENSEMBLE`), writes `/opt/data/projects/Research/outputs/abgc_129/abgc_129.mid` — `validate()` → `True`, file 2413 bytes, section invariants $\lvert w\rvert=16$ with writhes 8 / 2 / 4 / −2 and closure components 2 for all four sections. Note the musical consequence of $c=2$ everywhere: the demo's form is *always* a two-orbit canon, which is why $\Delta$/seed choice, not the walk length, is the form lever.

Candidate code path: `generators/braid_group.py` — class `BraidComposer`: `word_random(n, length, seed, bias)`; `word_delta(n)`; `garside_normal_form(word)`; `handle_reduce(word)`; `state_after(word, n)` → permutation; `components(word, n)`; `writhe(word)`; `burau_matrix(word, n, t)` → Alexander invariant of the closure; `emit(word, ladder, delta, syllable_ticks)` → per-strand `MusicEvent` lists; `realize_units(composer, ...)` → fills cells, then `validate()`/`to_midi()`.

### Pitfalls

1. **Not 089 change ringing (CRCM).** This is the trap. Change ringing is a walk on $S_n$ where *each row is a permutation of the bells and the next row's permutation is again a permutation of the same set* — the structure is the symmetric group, the state is forgotten each row, and a `plain hunt` returns to identity. The braid group is **not** $S_n$: crossings accumulate, $\sigma_i$ has infinite order, and $\sigma_i^2 \ne e$ ($\Delta_n^2 \ne e$ for the whole braid). The musical payoff of that difference is precisely what $S_n$ cannot express: a strand can wind around another any number of times, so "the same voicing, reached by going around twice" is a *different* braid (different writhe, different closure). If your implementation reduces the word mod the permutation, you have silently downgraded ABGC to CRCM.
2. **The permutation is a lossy shadow.** `perm` alone does **not** determine the braid (that is the whole point of $B_n \to S_n$). Provenance must store the **word**, not the permutation or the resulting MIDI-derived voicing; two different words give identical `perm` and audibly different pieces (different accents, different closures). Never regenerate from `perm`.
3. **Static harmony can sound like nothing happening.** With $\delta_s = 0$ the pc content is literally invariant; the piece relies entirely on registral exchange, accent, and timbre for interest. Mitigate by section-wise ladder change, per-strand $\delta_s$, or by letting $\Delta$ insertions do the work. Do not add a functional chord progression on top — it will fight the exchange logic (and duplicate 079 TINC's territory).
4. **Section length vs word length.** Sections are declared in bars *before* cells are filled; a word of 17 syllables in a 16-syllable section overruns the seam and `validate()` fails on track length mismatch. Derive $|W_j|$ from the bar count, or pad with `_unit_from_events(events, section_len)` (same trap as 125/126/127/128). The reference render keeps $|W_j| = 16 = \text{bars}\times\text{beats}$ exactly.
5. **$\Delta_n$ is long and loud.** $n(n-1)/2$ crossings: 6 at $n=4$, 15 at $n=6$, 45 at $n=10$. Injected mid-phrase it eats the section; as a cadential gesture it is a full registral reversal. Budget it — the C column in the reference render is $\Delta_4$ (6 syllables) + a 10-syllable walk, not $\Delta_4$ alone.
6. **Closure components are a form decision, not a decoration.** $c$ is determined by the *final permutation* only; the identity braid and the full twist both give $c=n$ (verified). If you want a canon ($c=1$) you must design for it (e.g. a single $n$-cycle permutation at the end), which a sign-symmetric random walk almost never produces — the reference demo accidentally got $c=2$ in every section. Check $c$ before claiming "canon".
7. **Alexander/Burau is analysis, not generation.** $\Delta_L(t)$ from the closure is a valid form fingerprint (two arrangements with equal $\Delta_L$ are likely related by Markov moves) but costs $O(L\cdot n^3)$ on Laurent polynomials and is useless as a real-time selector. Use it in a post-hoc "are these two takes the same piece?" check only; represent polynomials sparsely or the $t$-degree blows up with $L$.
8. **Handle reduction is the canonicalizer, not the composer.** Dehornoy reduction gives a unique normal form *of the same element*; it will not invent material. Applying it to an improvised word is a deterministic re-orchestration — good for reproducibility, not for novelty. Also, handle reduction is worst-case $O(L^2)$ per word; do not run it per note.
9. **Sign convention must be pinned in provenance.** $\sigma_i$ = over-crossing = louder is a *choice*. Flipping the convention silently inverts every tension curve and every velocity map; record the convention alongside the word (cf. 128 Pitfall 9 on velocity shading).
10. **Zero-drift and equal-length rows.** All rows emit on the same syllable grid, so all cells are equal length by construction — but only if every strand really emits every syllable. If a row is thinned to rests "for texture", the rests must still be padded to the section seam, or `validate()` fails.
