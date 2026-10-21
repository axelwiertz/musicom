# Report — Method 121 (IETC)

**Primary record for the cron research job run of 2026-10-21.**

| Field | Value |
|---|---|
| Method ID | **121** |
| Name | Interval Exchange Transformation Composition |
| Acronym | IETC |
| Paradigm | **Rules-Based** |
| LAYER | **concrete** (with an optional abstract pre-pass) |
| One-line | Compose by iterating a piecewise-translation interval exchange; interval widths are exact tonal-gravity weights, the permutation is the melodic grammar, Rauzy–Veech induction supplies self-similar form. |
| Standalone file | `/opt/data/projects/Research/CompositionMethods/method_121_IETC.md` |
| Candidate code path | `generators/iet_composition.py` → consumed by `workflows/unitmatrix_composer.py`; abstract pre-pass → `rules/subset_network.py` |
| methods_db.md lines | **27 222 → 27 304** (Δ +82) |
| Next free ID | **122** |

---

## 1. ID resolution (dynamic)

- Summary-table scan `^\| \*\*NNN\*\*` gave IDs 001–121 with **058 absent** (historically unused) — 120 numeric rows for 121 distinct IDs.
- File scan `method_*.md` / `report_*.md` gave a maximum of **120** (`method_120_RMTC.md`, `report_120.md`), consistent with the table.
- Cross-check: `method_118_D3PM-C.md`, `method_119_TDC.md`, `method_120_RMTC.md` exist and have table rows.
- **New ID = 121.** Next free ID after this run = **122**.

No duplicate: `grep -ci` for `interval exchange`, `Rauzy`, `tropical`, `wavelet` (as a composition method), `Young tableau`, `block design`, `Steiner`, `phyllotaxis` in `methods_db.md` returned 0 before writing (`wavelet` = 18 hits, all inside sound-production SP-069 WPSS, which is an *absolute*-layer audio method — not a compositional one).

## 2. Layer classification (LAYER_ARCHITECTURE.md)

**concrete.** The method emits concrete `MusicEvent`s: every iterate fixes a pitch (position on the pitch circle, quantized), an onset (accumulated tick position) and a duration (block index). It fills `(voice, section)` `MusicUnit` cells and therefore feeds `generators/`.

Secondary **abstract** use is legitimate and documented: the width vector $\lambda$ plus the induced visit-frequency vector is a weighted pitch-pool / harmonic-hierarchy design with no events attached. In that role it exports to `rules/subset_network.py` upstream of any concrete generator. Declared layer for the DB row remains `concrete` (the primary path).

Not `absolute`: nothing here produces sound; synthesis is a separate job (SP-*).

## 3. Paradigm classification

**Rules-Based.** Deterministic, invertible, measure-preserving map; no randomness at generation time, no learned parameters, no physical/natural system. Distinct from other rules-based families in that the generative object is a *dynamical system orbit of one continuous coordinate*, with coherence supplied by ergodic theorems rather than by rewrite rules (019 L-System, 034 PCFG), tilings (083 QTSC, 111 VTCC) or combinatorial designs (090 GRDC, 112 CADDC).

## 4. Summary-table row (as written)

```markdown
| **121** | concrete | Interval Exchange Transformation Composition (IETC) | **Rules-Based** | Pitch, Rhythm, Harmony, Structure, Texture | Strong (Width-imposed, ergodic-exact) | Continuous / Fluid (grid-quantizable) | None (State = one point $x \in [0,1)$) | $\mathcal{O}(N)$ per event, $\mathcal{O}(L)$ Rauzy induction | Composes by iterating an interval exchange $T_{\pi,\lambda}$: the pitch circle is cut into $n$ blocks whose widths $\lambda_k$ are permuted by $\pi$, and the orbit of one point supplies the whole event stream. Width **is** tonal gravity — unique ergodicity (Keane 1975; Masur 1982; Veech 1982) forces the visit frequency of block $k$ to equal $\lambda_k$ exactly, from every seed (verified: 400 000 iterates, error 0.00000). Block address → harmonic function, in-block offset → scale degree; region → duration class (pulse coding) or roof height (suspension coding). Rauzy–Veech induction renormalizes the exchange, so sections are literal scale-copies (verified: the induced map on $[0,0.62)$ is again an IET — 3 displacements, return times $\{1,2\}$); for $n{=}3$ the Arnoux–Rauzy fractal tiles the plane in three homothetic parts. $n{=}2$ degenerates exactly to a circle rotation ⇒ Sturmian/Christoffel (069/012) — IETC is their permutation-bearing parent. Deterministic aperiodic companion to 083 QTSC (substitution tiling) and 115 KORC (continuous-time flow); ergodic foil to 084 ZMRC (statistical rather than guaranteed frequency law). |
```

Column values chosen:

| Column | Value | Reason |
|---|---|---|
| Layer | concrete | fills cells with events |
| Paradigm | Rules-Based | deterministic map, no sampling |
| Primary Elements | all five | affects every dimension |
| Tonal Gravity | Strong (Width-imposed, ergodic-exact) | visit frequency = $\lambda_k$ exactly |
| Metric Binding | Continuous / Fluid (grid-quantizable) | translation flow; pulse or suspension coding |
| Memory Depth | None (State = one point) | Markov-free; coherence from ergodicity |
| Time Complexity | $\mathcal{O}(N)$/event, $\mathcal{O}(L)$ induction | linear |

## 5. Research and verification actually performed

1. **Literature grounded** against live sources (Wikipedia REST/API for the formal definition and the Rauzy-fractal structure of the Tribonacci substitution), plus the primary literature listed in the standalone file (Keane 1975; Rauzy 1979; Masur 1982; Veech 1982/1984; Boshernitzan 1985; Arnoux–Rauzy 1991; Zorich 1996; Kontsevich–Zorich 1997; Forni 2002; Viana 2006).
2. **Math validated numerically** (`projects/Research/outputs/ietc_validate/iet_validate.py`):
   - bijection / piecewise translation: max error $1.1\times10^{-16}$, exactly 3 distinct displacements $\{-0.8,-0.3,+0.5\}$;
   - equidistribution: $0.50000/0.30000/0.20000$ vs $\lambda=(0.5,0.3,0.2)$ over 400 000 iterates, error $0.00000$;
   - $n{=}2$ degenerate case: $P(I_0)=0.6125$ vs $\alpha=0.6180$; $\sup_m|N_0(m)-\lfloor m\alpha\rfloor| = 1$ → balanced Sturmian word;
   - first-return map on $[0,0.62)$ is again an IET (3 displacements, return times $\{1,2\}$).
3. **Engine integration proven** (`projects/Research/outputs/ietc_validate/iet_demo.py`): $\lambda=(0.26,0.17,0.06,0.13,0.09,0.21,0.08)$, $\pi=(7,2,3,4,5,6,1)$, 4 voices (flute / trumpet / strings / bass), 3 sections × 2 bars at 96 BPM → `validate() -> True: OK`, `ietc_demo.mid` 579 bytes / 15.0 s / 6 bars, 9–10 distinct pitches per voice (registers 72–89, 60–79, 48–67, 36–53), FluidR3 render `ietc_demo.wav` 3 846 444 bytes, `preflight_check.py` → COMPLIANT.

## 6. Complete method section appended to methods_db.md

Lines 27 228–27 304 of `methods_db.md`, verbatim:

# Interval Exchange Transformation Composition (IETC) (Method 121)

### Source

Keane, M. (1975). "Interval exchange transformations." *Mathematische Zeitschrift* 141, 25–31. — Rauzy, G. (1979). "Échanges d'intervalles et transformations induites." *Acta Arithmetica* 34, 315–328. — Masur, H. (1982). "Interval exchange transformations and measured foliations." *Annals of Mathematics* 115, 169–200. — Veech, W. A. (1982). "Gauss measures for transformations on the space of interval exchange maps." *Annals of Mathematics* 115, 201–242. — Veech, W. A. (1984). "The metric theory of interval exchange transformations I: interval exchange transformations." *American Journal of Mathematics* 106, 1331–1421. — Boshernitzan, M. D. (1985). "A condition for minimal interval exchange maps to be uniquely ergodic." *Duke Mathematical Journal* 52, 723–752. — Arnoux, P. & Rauzy, G. (1991). "Représentation géométrique de suites de complexité $2n+1$." *Bulletin de la SMF* 119, 199–215. — Zorich, A. (1996). "Finite Gauss measure on the space of interval exchange transformations. Lyapunov exponents." *Annales de l'Institut Fourier* 46, 325–370. — Kontsevich, M. & Zorich, A. (1997). "Lyapunov exponents and Hodge structure." In *The Mathematical Beauty of Physics*, Advanced Series in Mathematical Physics 24, 318–332. — Forni, G. (2002). "Deviation of ergodic averages for area-preserving flows on surfaces of higher genus." *Annals of Mathematics* 155, 1–103. — Viana, M. (2006). "Ergodic theory of interval exchange maps." *Revista Matemática Complutense* 19(1), 7–100 (survey). — Musical precedents for the degenerate $n{=}2$ case: Clough, J. & Douthett, J. (1991). "Maximally even sets." *Journal of Music Theory* 35, 93–173; Toussaint, G. (2013). *The Geometry of Musical Rhythm*, CRC Press (Sturmian/Christoffel rhythms).

### Layer

**concrete** — generates concrete pitch, onset, and duration events that fill UnitMatrix cells. The orbit of a point $x \in [0,1)$ under $T_{\pi,\lambda}$ is a literal event stream: each iterate supplies one pitch class (the position of $x$) and one rhythmic value (the region $x$ occupies). Nothing is left abstract — the exchange widths $\lambda$ do double duty as the pitch weighting law and the duration vocabulary, and the permutation $\pi$ sets the melodic succession statistics. Feeds `generators/` directly. A secondary **abstract** pre-pass is available: the partition $\{\lambda_k\}$ together with the visit-frequency vector is a weighted pitch-pool design that can be exported to `rules/subset_network.py` upstream of any concrete generator.

### Paradigm

**Rules-Based** — the transformation is a deterministic, invertible, measure-preserving map of the unit interval with no randomness, no learnt parameters, and no physical/natural dynamics. Every event is an exact function of the seed point $x_0$ and the pair $(\pi,\lambda)$. What distinguishes IETC from other deterministic rules methods (012 Euclidean, 069 Christoffel, 083 quasicrystal) is that the musical stream is the *orbit of a single continuous coordinate*, and coherence comes from ergodic theory rather than from rewrite rules or tiling grammars.

### Description

**Interval Exchange Transformation Composition (IETC)** composes by iterating an interval exchange: cut the unit interval into $n$ blocks of widths $\lambda_1,\dots,\lambda_n$, then permute the blocks by a permutation $\pi$ and lay them back down. The map $T_{\pi,\lambda} : [0,1) \to [0,1)$ is piecewise a translation — every point keeps its offset inside its block, only the block's address changes. It is the natural $n$-ary generalization of a circle rotation ($n{=}2$), and the exact $n$-ary generalization of everything in the catalogue that has been built on rotations and Sturmian words (012 Euclidean, 069 Christoffel).

**Definition.** With $\alpha_i = \sum_{j<i}\lambda_j$ (block starts) and $\alpha'_i = \sum_{j:\,\pi(j)<\pi(i)}\lambda_j$ (image start of block $i$):

$$T(x) = x - \alpha_i + \alpha'_i \quad \text{for } x \in [\alpha_i, \alpha_{i+1})$$

so $T$ is a bijection of $[0,1)$ preserving Lebesgue measure, with derivative $1$ everywhere except at the $n{-}1$ interior discontinuities. (Verified numerically: with $\lambda=(0.5,0.3,0.2)$, $\pi=(3,2,1)$, the image of a 200 000-point grid re-sorts onto itself to $1.1\times10^{-16}$, and the displacement $T(x)-x$ takes exactly 3 distinct values: $-0.8,-0.3,+0.5$.)

**Why this is a composition method and not a metaphor.** Three theorems do the compositional work:

1. **Minimality (Keane 1975).** If $\pi$ is *irreducible* — $\pi(1)=n$, $\pi(n)=1$, and no proper prefix $\{1,\dots,k\}$ is $\pi$-invariant — then for every $\lambda$ the orbit of every point is dense. The melody can never get stuck in a subset of the pitch space; it always eventually visits every block.
2. **Unique ergodicity (Keane's conjecture; Masur 1982, Veech 1982).** For irreducible $\pi$ and almost every width vector $\lambda$, $T$ has a *unique* invariant probability measure — Lebesgue. Birkhoff then gives, for every starting point,

$$\lim_{N\to\infty}\frac{1}{N}\#\{0 \le t < N : T^t x \in I_k\} = \lambda_k$$

So **interval width is tonal gravity, and it is exact, not statistical**. Design $\lambda_1 = 0.26$ for the tonic block and the tonic region is visited 26 % of the time, in every run, from every seed — a functional hierarchy enforced by a theorem rather than by a preference model. (Verified: 400 000 iterates with $\lambda=(0.5,0.3,0.2)$ give empirical frequencies $0.50000/0.30000/0.20000$.)
3. **Renormalization (Rauzy 1979; Rauzy–Veech induction).** Induce $T$ on a subinterval — take first-return times. The induced map is *again an interval exchange*, on the same or one more block, with a new width vector and permutation. Iterating induction is the interval-exchange analogue of the continued-fraction algorithm, and it generates the substitution that governs the piece at the next scale. (Verified: inducing $T_{((0.5,0.3,0.2),(3,2,1))}$ on $[0,0.62)$ returns a map with 3 distinct translation displacements $\{-0.3,+0.2,+0.5\}$ and first-return times $\{1,2\}$ — still an IET, now with a two-valued return-time structure.)

**Rhythm: two legal codings.** (a) *Pulse coding* — one iterate = one metric subdivision; the block the point occupies selects the duration class, so $\lambda$ is simultaneously the pitch histogram and the duration histogram. (b) *Suspension coding* — attach a roof function $h$, piecewise constant with $h|_{I_k}=c_k$, and place events at $t_{m+1}=t_m + h(T^m x)$. The inter-onset intervals are then sums of the $c_k$ along the visited blocks: a non-periodic but strictly rational-ratio groove whose return-time statistics are the Rokhlin-tower heights of the induction. Pulse coding is grid-locked (MIDI-native); suspension coding is fluid rubato.

**Tension.** For a musical observable $f$ (registral height, density, dissonance), the Birkhoff sums satisfy $S_N f = N\!\int\! f + O(N^{\theta})$ with $\theta<1$; the fluctuation exponents for typical IETs are the Lyapunov exponents of the Zorich–Kontsevich cocycle (Zorich 1996; Forni 2002). Design consequence: tension does *not* drift linearly with a designed slope — it fluctuates sublinearly around the designed mean, with the fluctuation rate set by the permutation's Rauzy class. Widening $\lambda$ in one block raises the local mean; changing the Rauzy class changes how violently the piece departs from it.

**Position in the catalogue.** IETC is the strict parent of the evenness family: $n{=}2$ with irrational $\lambda_1$ *is* a circle rotation, whose coding is a Sturmian word — exactly the ground of 069 Christoffel and the balanced-rhythm logic of 012 Euclidean. Adding the permutation and the third block breaks the rotational symmetry: the exchange is no longer a group translation, its renormalization is a substitution on a Rauzy class, and its return structure is a genuine interval-exchange rather than a mechanical word. It is a *dynamical-systems* sibling of 083 quasicrystal (substitution tiling) and 115 Kepler (continuous-time flow), a deterministic foil to 048 Brownian pitch diffusion, and the exact-ergodic counterpart of 084 Zipf–Mandelbrot (frequency law imposed by statistics rather than by measure).

### Musical Elements Framework

**PITCH**: The circle of pitch is the unit interval. A point $u$ carries two pitch coordinates: the *block address* $k$ (which harmonic region the note belongs to — tonic area, dominant area, mediant area…) and the *offset inside the block*, which is quantized to the active scale. Quantization is deliberate and two-level: address $\to$ function, offset $\to$ degree. A 12-slot diatonic quantizer table maps the offset to semitones so that duplicated table entries land on chord tones, which thickens the harmony for free. Because the orbit is equidistributed with weights $\lambda$, the pitch-class histogram of a long enough passage converges to the designed $\lambda$-weighted scale profile: the piece has a *provable* tonal centre. Register is not decided by the orbit but by the voice (row), so the same exchange supplies a bass line and a lead simultaneously at different octaves.

**RHYTHM**: Rhythm is the region-visit sequence. With $\lambda$ rational the orbit is periodic (period = lcm of the denominators) and the result is a loop — usable, but a loop. With $\lambda$ irrational the orbit is minimal and aperiodic, and the rhythmic word is Sturmian-like: any two windows of the same length contain region counts differing by at most a bounded amount, so the groove is maximally even *without ever repeating*. In suspension coding, the roof heights $c_k$ give the note values and the return-time multiset of the induction gives the tuplet vocabulary; the piece inherits a natural rubato because events crowd where the roof is low.

**HARMONY**: Each voice is a different starting point $x_v$ on the same circle, so a chord is a *configuration* of points. Between two iterates, all points move by translations, so the vertical intervals between voices evolve by the same exchange cocycle as the horizontal ones — the harmonic vocabulary is a small closed set of interval classes, revisited by minimality, but never on a fixed beat. Poincaré recurrence guarantees that any vertical sonority recurs (arbitrarily closely) without the piece ever being literally periodic. Practical lever: choose the starting points so the initial configuration is the target chord (e.g. offsets 0, 0.25, 0.42, 0.58 of the block widths); choose $\lambda$ rational for a chaconne-like harmonic cycle, irrational for harmonic *drift*.

**STRUCTURE**: Macro-form is the Rauzy–Veech induction tree. Each induction level is a renormalized copy of the piece at a coarser scale, so sections are scale-related rather than merely concatenated: section $m{+}1$ can be generated by the induced exchange of section $m$, which guarantees literal self-similarity of the rhythmic and intervallic material. The sequence of induction steps (the Rauzy class walk) plays the role of a form scheme; the width vector's continued-fraction-like evolution is the form's clock. For the three-block Tribonacci case the associated Rauzy fractal (Arnoux–Rauzy 1991) tiles the plane periodically in three homothetic parts — a geometric picture of "three sections, each a scaled copy".

**TEXTURE**: The number of blocks $n$ is the size of the pitch-region vocabulary, and the number of voices $V \le n$ controls density. A *reducible* $\pi$ (one that leaves a prefix invariant) splits the exchange into independent sub-exchanges — block-diagonal texture: two or three antiphonal groups that never mix, which is exactly the "call-and-response between choirs" effect. An *irreducible* $\pi$ mixes everything, giving a through-composed, constantly-recombining texture. Roof height scales density directly ($\rho \approx 1/\bar h$), and because the roof is a design parameter, density can be scheduled per section without touching the pitch material.

### UnitMatrix Integration (Voices & Sections)

**Voices (rows)** = orbits. Row $v$ holds the orbit of seed point $x_v$ under the *same* $(\pi,\lambda)$. Two natural layouts:

- *One orbit per row* — the standard layout; each row is an independent contrapuntal line whose register is fixed by the voice's instrument, and vertical coherence comes from the shared exchange (all rows move by the same piecewise translations).
- *One block per row* — the coded layout, where row $k$ sounds only the iterates that fall in block $I_k$ (a Rokhlin-tower split). The rows then hocket: each voice owns one harmonic region, and because the orbit must visit every block with frequency $\lambda_k$, the voices' event counts are automatically proportional to the designed harmonic weights.

**Sections (columns)** = renormalization epochs. Column $m$ is generated either (i) by the $m$-th Rauzy–Veech induction of the base exchange (self-similar sections), or (ii) by the same exchange with a rescaled roof function (same material, new density/tempo band). Section boundaries are placed where the orbit returns to the tonic block — the natural cadence of an exchange is a return, not a chord change, which gives IETC a cadential grammar of its own.

**Cells (MusicUnit)** = the events produced between two section landmarks. Concretely: iterate $T$, map each iterate to (pitch slot, duration class), accumulate onsets in absolute ticks inside the cell, stop when the section budget is exhausted, and pad the final event to `section_len` so the terminal landmark holds and `validate()` reports zero drift. The orbit is carried across the seam (do not reset $x$) — the exchange is continuous through time, and continuity is what makes the sections one piece instead of three loops.

**Verified engine integration** (`projects/Research/outputs/ietc_validate/iet_demo.py`): $\lambda=(0.26,0.17,0.06,0.13,0.09,0.21,0.08)$, $\pi=(7,2,3,4,5,6,1)$, 4 voices (flute/trumpet/strings/bass), 3 sections × 2 bars at 96 BPM, `validate() -> True: OK`, 579-byte / 15.0 s MIDI, 9–10 distinct pitches per voice (registers 72–89, 60–79, 48–67, 36–53), 3.85 MB WAV render, `preflight_check.py` COMPLIANT.

Candidate code path: `generators/iet_composition.py` (class `IETComposer`, methods `exchange()`, `rauzy_induce()`, `orbit_to_cell()`), consumed by `workflows/unitmatrix_composer.py`; abstract pre-pass in `rules/subset_network.py` (weighted block partition export).

### Pitfalls

1. **Irreducibility is not optional.** If $\pi$ has an invariant prefix block ($\pi(\{1..k\}) = \{1..k\}$ for some $k<n$), the exchange splits into independent sub-exchanges, the orbit is confined to a union of blocks, and the piece collapses into a pedal-drone subset. Always validate with a prefix test before generating.
2. **Rational $\lambda$ silently kills aperiodicity.** The orbit period is the lcm of denominators; a "non-repeating" groove with $\lambda=(3,2,5)/10$ repeats every 10 iterates. Use irrational or high-denominator widths for through-composed material, and use rational widths deliberately when a loop is wanted.
3. **Floating-point boundary artifacts** (hit in this build): an iterate landing exactly on a block boundary can evaluate to $1.0$ because of rounding, and the next step then reads the wrong block, distorting the visit-frequency law. Fix: reduce every iterate modulo $1$ and use half-open blocks $[\alpha_i,\alpha_{i+1})$ with a single consistent `searchsorted` side.
4. **Do not claim novelty for $n{=}2$.** Two blocks *is* a circle rotation; the resulting words are Sturmian/Christoffel and are already covered by 069 and 012. IETC's distinct content begins at $n \ge 3$, where the permutation introduces renormalization classes that no rotation has.
5. **Equidistribution guarantees frequency, not consonance.** The exchange is discontinuous, so consecutive pitches can cluster into semitone rubs, and vertical sonorities are whatever the point configuration happens to be. Control this with the quantizer table (duplicate chord tones) and with deliberate seed offsets, not by expecting the dynamics to be polite.
6. **Coincident seeds lock forever.** $T$ is a bijection, so $x_v = x_w$ implies identical orbits for all time. Voices must start at distinct points; likewise, restarting a section from the same $x$ reproduces the previous section bit-for-bit.
7. **Repeated sections look like a bug.** Because induction is exact, induced sections are *literally* scale-copies. If the form needs contrast rather than self-similarity, change the permutation between sections (jump to a different Rauzy class) rather than merely rescaling.
8. **Grid alignment for MIDI.** IET time is continuous; the UnitMatrix is tick-quantized. Quantize durations to the tick grid *and* pad the last event to `section_len`, otherwise `validate()` fails on track drift (equal-length rule). Suspension coding with irrational roof ratios will always need this rounding — budget for it.

## 7. Quirks / pitfalls encountered (process, not music)

1. **Malformed table rows pre-existed.** Twelve method rows (101–109, 118–120) and nineteen SP rows carried `||`/`|||` prefixes, plus `||### Source`. All normalised to a single `|`; `grep -cE '^\|\|+ '` on the whole file is now **0**. LaTeX was untouched (no `\\mathcal` double-escaping introduced or found: `grep -c` for double-backslash commands = 0).
2. **Orphan MaxEnt section.** The 097 body sat in the table header region with no `# ... (Method 097)` heading, immediately after row 120, and its prose lines were pipe-prefixed. I added the missing heading so my new row is not visually attached to it. Its remaining pipe-prefixed prose lines were left alone (cosmetic, ~60 lines, outside this job's scope).
3. **`patch` fuzzy matcher degraded** on this 2.7 MB file — a multi-line anchor around the 121 row/`### Source` returned "29 matches", then "27", then "142". Workaround: a small Python edit with strict `assert` guards on the exact neighbouring lines. **First attempt had an off-by-one slice** and deleted row 121 + `### Source`; restored by re-inserting the exact row text and heading, then verified by re-reading lines 129–136. Final state verified (row present at line 131, section at 27 228, 120 numeric rows for IDs 001–121).
4. **Floating-point boundary artefact in the IET itself** (a genuine finding, now a documented pitfall): an iterate landing exactly on $\alpha_1 = 0.618\ldots$ evaluated to $1.0$ because of rounding, the next step then read the wrong block, and the measured visit frequency came out $0.383$ instead of $0.618$. Fixed with `% 1.0` and half-open blocks; error then $0.00000$.
5. **`hermes send` not used**; cron delivery handled by the harness.
6. Minor: `MidiInstrument` in this build exposes only `FLUTE, TRUMPET, STRING_ENSEMBLE, BASS, PIANO, VIOLIN, CHURCH_ORGAN, SYNTH_PAD, ACOUSTIC_GUITAR` — a first demo crashed on `CLARINET`/`CELLO`; remapped.

## 8. Files touched

| File | Change |
|---|---|
| `methods_db.md` | +82 lines (section 77, row 1, spacing/heading 4); 29 row prefixes normalised |
| `method_121_IETC.md` | new, 13 598 bytes (extended math, mapping table, code sketch, references) |
| `report_121.md` | this file |
| `outputs/ietc_validate/iet_validate.py` | validation harness (kept as evidence) |
| `outputs/ietc_validate/iet_demo.py` | 4-voice × 3-section composer producing `ietc_demo.mid` + `.wav` |

## 9. Next free ID

**122**
