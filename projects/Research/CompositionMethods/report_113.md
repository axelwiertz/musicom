# Report — Method 113: Pitch-Class Fourier Spectrum Composition (PCFSC)

**Method ID:** 113 (next free ID after this = **114**)
**Method Name:** Pitch-Class Fourier Spectrum Composition (PCFSC)
**Paradigm:** Rules-Based
**LAYER:** abstract
**One-line description:** Composes pitch-class pools, progressions, and tension curves in Amiot's Fourier space over ℤ₁₂ — chord/scale *quality* is the magnitude spectrum |f(k)| of the pc-set, tonic *position/function* is the Fourier phase, and a designed phase walk IS the composition; the abstract layer emits (pool sequence, phase schedule, tension curve) that feeds rules/subset_network.py.

---

## 1. Summary-table row (appended after the 112 row, now line 123 of methods_db.md)

```
| **113** | abstract | Pitch-Class Fourier Spectrum Composition (PCFSC) | **Rules-Based** | Pitch, Harmony, Structure, Texture | Strong (Fourier-phase-guided) | Grid-Locked / Continuous | Meso / Phase Trajectory | $\mathcal{O}(4096 \cdot 12)$ profile match, $\mathcal{O}(12)$/step gen | Designs pitch-class sets and progressions in the DFT over $\mathbb{Z}_{12}$ (Amiot 2016): chord/scale quality = magnitude spectrum $\lvert f_A(k) \rvert$ of the pc-set — whole-tone energy only at k=0,6; octatonic only at k=0,4,8; the 7-note ME (diatonic class) attains the max fifth-coefficient $\lvert f(5) \rvert = 2+\sqrt{3}$ (verified by exhaustive $\binom{12}{7}$ search); major/minor triads are magnitude-twins — mode lives in PHASE, not magnitude (verified: identical $|f|$ arrays, different $\arg f_5$). Tonic position/function = Fourier phase; transposition = phase rotation (verified: $T_7$ rotates $\arg f_1$ by $7\pi/6$). Composition = a trajectory in Fourier space: per-section target magnitude profile + designed phase walk yield the pitch-pool sequence and tension curve; tension = weighted Fourier-space distance between successive sets (Bernardes TIV 2016); magnitude-twin complement pairs (diatonic $\cong$ pentatonic) drive subset pairing. Abstract layer: feeds rules/subset_network.py. Fourier cousin of 039 SMA (audio-domain) and 051 SGLM (spectral-graph); phase-driven foil to 095 CTC and 104 PSSC. |
```

Classification columns: Tonal Gravity = Strong (Fourier-phase-guided) · Metric Binding = Grid-Locked / Continuous · Memory Depth = Meso / Phase Trajectory · Time Complexity = `$\mathcal{O}(4096 \cdot 12)$` profile match, `$\mathcal{O}(12)$`/step gen · Primary Elements = Pitch, Harmony, Structure, Texture · Layer = abstract.

## 2. Line counts

- methods_db.md **before**: 24,800 lines
- methods_db.md **after**: 24,879 lines (`wc -l`; last physical line 24,880 without trailing newline)
- **Delta: +79 lines** = +78 appended section lines + 1 summary-table row (inserted at line 123, i.e. immediately after the 112 row)
- Appended section: separator `---` at line 24,803; `### Source` at 24,804; `### Layer` 24,808; `### Paradigm` 24,812; `### Description` 24,816; `### Musical Elements Framework` 24,849; `### UnitMatrix Integration (Voices & Sections)` 24,861; `### Pitfalls` 24,869; `Candidate code path:` 24,880 (final physical line).

## 3. Artifacts

- Standalone write-up: `/opt/data/projects/Research/CompositionMethods/method_113_PCFSC.md` (extended math incl. verified spectra table, Python implementation sketch with demo, UnitMatrix filling sketch, references, distinguishing-method section)
- This report: `/opt/data/projects/Research/CompositionMethods/report_113.md`
- Appended section (verbatim copy below): `methods_db.md` lines 24,803–24,880

## 4. Classification details

- **Layer — abstract.** Justification: PCFSC outputs pitch-class *pools* (subsets of ℤ₁₂), a *progression* (Fourier-space trajectory / pool sequence), and a *tension curve* — all transposition- and register-invariant, no concrete events. Matches LAYER_ARCHITECTURE.md abstract-row contract ("subset pc-set sequences, tension curves, pattern network, form") and feeds `rules/subset_network.py` exactly like the three existing abstract methods 095 CTC, 099 SSMC, 104 PSSC. It is the fourth abstract-layer method in the DB (95/99/104/113) and the only abstract method that designs *sonority identity* (quality spectrum) + *position* (phase) rather than shape (095) or transition cost (104).
- **Paradigm — Rules-Based.** Deterministic algebraic construction: exact DFT over ℤ₁₂; profile matching is exhaustive search over the closed-form space of 4096 subsets (no randomness in the objective or the tie-break — lexicographic first-best); maximally-even pools by generator-window construction; phase walks are designed curves. No stochastic sampling (contrast 084 ZMRC), no nature dynamics (contrast 040 Perlin), no learned parameters (contrast 042/046/054).
- **Relationship check (no duplication):** 039 SMA is a Fourier method over *audio frames* (different domain; concrete layer, Stochastic), 051 SGLM is *spectral graph* eigenvalues (different spectrum; concrete), 025 Sieve is congruence-based pitch selection (no DFT), 080 MMLT is subset symmetry (no DFT). No existing method uses the DFT of pitch-class sets for *quality/phase design* — confirmed novel.

## 5. Verified numeric facts (computed for this registration with `$MUSICOM_PYTHON` + numpy)

| Claim | Verified value |
|---|---|
| major/minor triad magnitude-twin | |f| arrays identical to 3 decimals; phases differ ($\arg f_5$ = −0.785 vs +0.262) |
| ICV→magnitude identity | $|f(k)|^2 = n+2\sum_j \mathrm{icv}(j)\cos(2\pi k(j+1)/12)$ holds for maj/min/diatonic, all k |
| transposition = phase rotation | $T_7$ on Ionian: $\arg f_1$ shift = 3.6652 rad = $7\pi/6$ ✓ |
| whole-tone / octatonic spectra | WT nonzero only k∈{0,6}; oct nonzero only k∈{0,4,8} |
| complement twins | Ionian $\{0,2,4,5,7,9,11\}$ ≅ pentatonic at k=1..11 |
| max fifth-coefficient | max $|f_5|$ over all 792 seven-note sets = 3.7321 = 2+√3; attained by the ME (Ionian/Lydian) class and by {0,1,3,5,6,8,10} |

## 6. Quirks / pitfalls hit during registration

1. **Backslash pitfall (KNOWN):** the file convention is SINGLE backslashes (58 rows verified `\mathcal{O}(N)$`, only 1 stray double). The patch tool did NOT double-escape this time — post-patch grep of row 113 found 0 `\\` sequences and all LaTeX commands intact (`\mathcal`×2, `\arg`×2, `\lvert`/`\rvert`×2, `\binom`, `\sqrt`, `\mathbb`, `\cong`, `\pi`, `\cdot`). Verified per instruction.
2. **`||` prefix pitfall (KNOWN):** row 113 starts with a single `|` — grep `^\|\|` = 0 matches. Note rows 101–109 in the table historically carry `|||`/`||||` prefixes from an old patch bug (left untouched — out of scope); the pre-existing `|||### Source` line at 123 (now line 124 after insert) is also a legacy artifact, not mine.
3. **Row-anchor subtlety:** the insert anchor was the 112-row tail + the malformed `|||### Source` line; the patch applied cleanly and the diff shows correct placement between 112 and the old line.
4. **ID resolution:** summary-table scan gave max = 112 (rows 001–100, 110–112); standalone file scan gave max = 112 (`method_112_CADDC.md`, `report_112.md`). **113 was never used** — confirmed no `method_113*`/`report_113*` pre-existing. Historic sparse IDs (101–109 have table rows with `|||` prefixes but standalone files exist; 058 missing) did not affect the max.
5. **Formatting quirk:** the most recent algorithmic append (112) has NO `# Name — ID` top-level header (starts directly at `---` + `### Source`), unlike SP-* sound sections. Matched 112's convention exactly; the section includes `### Paradigm` (as 112 does) in addition to the six mandated headers.
6. **My own math-honesty fix:** my first hypothesis "diatonic maximizes |f5| uniquely" was WRONG — the max is shared by several sets (the ×5-image-consecutive family). The write-up states the verified claim precisely ("attains", not "uniquely maximizes") and adds the correction as Pitfall 3.

## 7. Candidate code path

`rules/fourier_pc_spectra.py` (rules/ — abstract layer, NOT generators/): `pc_set_dft(pcs)` (vectorized complex 12-vector), `profile(pcs)` (normalized magnitudes |f|/n), `match_profile(target_mags, cardinality, weights)` (exhaustive 4096-set scan), `me_set(n, g)` (maximally-even generator window), `phase_walk(phi0, v, ks, n_steps)` (per-coefficient phase schedule), `fourier_tension(fA, fB)` (TIV-style weighted Fourier distance), `complement_pair(pcs)`. Feeds `rules/subset_network.py` (abstract layer) with per-section (pool, phase schedule, tension) records; concrete realization via `rules/realize.py` → UnitMatrix cells (`create_note_unit`/`create_chord_unit`), zero-drift pad to `section_len`.

---

## Appendix — complete appended method section (verbatim, methods_db.md lines 24,803–24,880)

---

### Source

Emmanuel Amiot, *Music through Fourier Space: Discrete Fourier Transform in Music Theory* (Springer, 2016) — the definitive treatment: pc-set DFT, magnitudes/phases, maximally even sets, complement isospectrality. — Amiot, E. (2007). "David Lewin and Maximally Even Sets." *Journal of Mathematics and Music* 1(2), 63–93. — Lewin, D. (1959). "Intervallic Relations between Two Collections of Integers." *Journal of Music Theory* 3(2), 298–301 (the original Fourier-system idea); Lewin, D. (2001). "Special Cases of the Interval Function between Pitch-Class Sets x and y." *JMT* 45(1). — Quinn, I. (2006). "General Equal-Tempered Harmony: Parts 2 and 3." *Perspectives of New Music* 44(2) / *Iowa City* 45(1); Quinn, I. (2004). *A Unified Theory of Chord Quality in Equal Temperaments* (PhD diss., University of Rochester) — chord quality = Fourier magnitudes. — Yust, J. (2019). "Stylistic Information in Pitch-Class Distributions." *Journal of New Music Research* 48(2), with the phase-side results; Yust, J. (2017). "Review of Amiot, Music through Fourier Space." *Music Theory Online* 23(3); Chiu, Y.-M. (2021). "Macroharmonic Progressions through the Discrete Fourier Transform." *Music Theory Online* 27(3). — Bernardes, G., Cocharro, D., Guedes, C., & Davies, M. E. P. (2016). "Harmony Generation Driven by a Perceptually Motivated Tonal Interval Space." *ACM Computers in Entertainment* 14(2), 6 — the Tonal Interval Vector (weighted DFT of chroma) as a working harmony-generation objective. — Amiot, E. & Sethares, W. (2011). "An Algebra for Periodic Rhythms and Scales." *Computer Music Journal* 35(1) — the rhythm-side DFT dual.

### Layer

**abstract** — PCFSC designs pitch-class *pools* (subsets of $\mathbb{Z}_{12}$), their *progressions* (Fourier-space trajectories), and the *tension curve* (Fourier distance between successive sets). It emits no concrete events: no pitches, onsets, or durations are fixed until a realize layer maps each pool to actual notes (register, voicing, voice-leading via `rules/realize.py`). Output contract matches the abstract layer exactly — a transposition- and register-invariant plan — and feeds `rules/subset_network.py` like 095 CTC / 099 SSMC / 104 PSSC. Candidate module `rules/fourier_pc_spectra.py` (rules/, not generators/).

### Paradigm

**Rules-Based** — deterministic, algebraic construction. The DFT over $\mathbb{Z}_{12}$ is exact mathematics: given a target Fourier profile and phase schedule, the pc-set sequence is found by exhaustive search (2¹² = 4096 subsets — closed-form, no randomness) or by direct maximally-even/coset construction; the phase walk is a designed curve. No stochastic sampling (contrast 084 ZMRC), no nature dynamics (contrast 040 Perlin), no learned parameters (contrast 042 NST / 046 VAE-LSI). The only freedom is compositional: which profile, which phase anchors, which walk — all chosen deterministically; same inputs, same plan.

### Description

**Pitch-Class Fourier Spectrum Composition (PCFSC)** composes from the **discrete Fourier transform of a pitch-class set** — the map that sends a subset $A \subseteq \mathbb{Z}_{12}$ to its 12 Fourier coefficients

$$f_A(k) = \sum_{a \in A} e^{2\pi i k a / 12}, \qquad k = 0, 1, \dots, 11.$$

This is Amiot's "Fourier space" (2016): every pc-set becomes a vector of complex numbers; two views of the same vector carry two different musical readings:

- **Magnitude $|f_A(k)|$ = the *quality* spectrum.** $|f_A(k)|$ measures how strongly the set is structured by the $k$-th even division of the octave (whole-tone for $k=6$, diminished-seventh for $k=3$, augmented-triad for $k=4$, ...). Verified spectra (all computed with $e^{2\pi i/12}$):

  | set | $|f|$ profile (k=0..11) | reading |
  |---|---|---|
  | whole-tone $\{0,2,4,6,8,10\}$ | $[6,0,0,0,0,0,6,0,0,0,0,0]$ | energy only at $k=0,6$ — pure tritone/whole-tone division |
  | octatonic $\{0,1,3,4,6,7,9,10\}$ | $[8,0,0,0,4,0,0,0,4,0,0,0]$ | energy only at $k=0,4,8$ — the diminished-seventh lattice |
  | diatonic (Ionian) $\{0,2,4,5,7,9,11\}$ | $[7,\,{.}27,\,1,\,1,\,1,\,3.73,\,1,\,3.73,\,1,\,1,\,1,\,{.}27]$ | peak at $k=5,7$ = the fourth/fifth direction |
  | pentatonic $\{0,2,4,7,9\}$ | same as diatonic at $k{=}1..11$ (cardinality 5 at $k{=}0$) | complement twin |
  | major triad $\{0,4,7\}$ | $[3,\;{.}52,\;1,\;2.24,\;1.73,\;1.93,\;1,\;1.93,\;1.73,\;2.24,\;1,\;{.}52]$ | broad spread |
  | minor triad $\{0,3,7\}$ | **identical to major** | magnitude cannot see mode! |

  The magnitude spectrum is a *Fourier transform of the interval-class vector* — verified: $|f_A(k)|^2 = n + 2\sum_{j=0}^{5} \mathrm{icv}(j)\cos(2\pi k(j{+}1)/12)$ holds for every tested set (maj/min/diatonic) — which is why major and minor triads, sharing the ICV $[001110]$, are magnitude-twins (Lewin 1959; Quinn 2006: chord quality *is* the magnitude profile).

- **Phase $\arg f_A(k)$ = the *position*/function.** Transposition by $t$ rotates every phase by exactly $2\pi k t/12$ (verified numerically: $T_7$ shifts $\arg f_1$ by $7\pi/6$), so phase pins the set's *location* on the transposition circle; magnitudes are invariant. Major vs minor differ *only* in phase (verified: $\arg f_5$ = $-0.785$ for C major vs $+0.262$ for C minor) — Yust's reading of Fourier phase as tonal function (2019): the phase of the dominant coefficient tracks where the collection "hears" its tonic, dominant, and mode.

**Compositional machinery** (all steps deterministic):

1. **Profile design.** A section's harmony is a target magnitude profile $\{T_k\}$, $k \in 1..11$ (with $T_0$ = cardinality). Style knowledge lives here as *spectral archetypes*: tonal = energy at $k=5,7$; whole-tone/haze = energy at $k=6$; octatonic/dramatic = energy at $k=4,8$; atonal noise = flat profile. Verified extremal facts: the 7-note maximally-even class (Lydian/Ionian) *attains* the maximum possible fifth-coefficient, $|f_5| = 2+\sqrt{3} \approx 3.732$ (exhaustive check over all $\binom{12}{7} = 792$ sets; the $k{=}5$ max is also attained by the non-ME set $\{0,1,3,5,6,8,10\}$, so "fifthiness" alone does not pin the diatonic — combine with Me). The regular divisions are exact: $|f_4(\text{aug triads})| = 3$, $|f_3(\dim7)| = 4$, $|f_6(\text{whole-tone})| = 6$, $|f_4(\text{octatonic})| = 4$.
2. **Set matching.** Match pc-sets by normalized profile distance $D(A) = \sum_k w_k (|f_A(k)|/n - T_k)^2$, minimized by exhaustive search over all 4096 subsets (trivial cost) — or direct construction: cosets of the kernel of $k \mapsto ka$ for the regular divisions, and the one-generator window $\{0, g, 2g, \dots, (n{-}1)g\} \bmod 12$ ($\gcd(g,12)=1$) for ME pools. Either way the pool list is closed-form.
3. **Phase trajectory (the actual composition).** The tonic/anchor position is a designed phase curve $\phi(k, t)$ for the dominant coefficients — a continuous walk $\phi(t) = \phi_0 + v \cdot t$ *is* a transposition drift (TURN), a step to a new anchor *is* a modulation (LIFT/TENSE), a return to the opening phase *is* a resolution (HOME). Because phase rotates phases at rate $k$ per transposition step, a single designed phase curve yields *coefficient-specific* motion — e.g. $+|f_5|$ weight pulls the fifth-layer, $-|f_6|$ suppresses the tritone layer — a genuinely new control surface: you steer harmony by *directly specifying which Fourier layers are active and where they point*.
4. **Tension curve.** Tension between successive sets = weighted distance in Fourier space, $\|f_{A_{t+1}} - f_{A_t}\|$ (the Bernardes Tonal-Interval-Space distance, 2016); harmonic rhythm = the phase velocity $v = \Delta\phi/\Delta t$. Both are outputs of the abstract layer, delivered with the pool sequence.
5. **Complement pairing.** $A$ and its complement have identical magnitudes at all $k \neq 0$ (verified: diatonic $\cong$ pentatonic), so a pool and its complement are two *densities of the same harmony* — the abstract layer exposes this pair structure for texture layering.

**Complexity.** Profile match: $\mathcal{O}(4096 \cdot 12)$ one-time per section (closed-form; or $\mathcal{O}(n)$ by construction). Phase walk and tension: $\mathcal{O}(1)$ per step. Total $\mathcal{O}(12)$ per generated position — cheaper than any trained method and cheaper than 051 SGLM's eigendecomposition; only the 4096-subset profile scan is non-constant, and it is per-section, not per-event.

### Musical Elements Framework

**PITCH**: The abstract output is a *sequence of pc-pools* (one per position) plus a phase schedule; actual pitch events are realized downstream (`rules/realize.py`, register/voicing). The pool's cardinality (the $T_0$ constraint) sets the pitch vocabulary per position — sparse pools (triads) for melody, full pools (7–8 note ME sets) for drones. Pitch *role* is Fourier-native: scale steps weighted by their contribution to $|f_5|$ are "fifth-functional" (dominant-side), steps contributing to $|f_6|$ are tritone/tension carriers. Conjunctness is *not* guaranteed by the abstract layer — the phase walk is pitch-set motion, not step motion; stepwise leading is installed at realize time (or by choosing pools whose successive intersection is large, which *is* controllable in Fourier space: overlapping magnitude profiles yield parsimonious pool overlaps).

**RHYTHM**: Two channels. (a) **Harmonic rhythm** = phase velocity $v = \Delta\phi/\Delta t$ of the anchor coefficient: slow $v$ = long pools (static harmony), fast $v$ = fast-changing pools (harmonic density); a $v$-curve over the piece is a designed tension/rhythm envelope. (b) **Onset patterns** via the rhythm-side DFT dual (Amiot–Sethares 2011): an onset set $R \subseteq \mathbb{Z}_{16}$ has the same Fourier algebra; the same profile machinery schedules accents/onsets with a chosen evenness spectrum (e.g. energy at $k=4$ of a 16-grid = 4-on-the-floor, energy at odd $k$ = swung/limping). The two channels are independent profiles — meter and harmony each get their own spectrum.

**HARMONY**: The core element. Chord/scale quality = magnitude profile (Quinn); harmonic function = phase of the dominant coefficient (Yust); progression = a path through Fourier space; voice-leading smoothness = overlap between consecutive pools (profile similarity); resolution = phase return to the opening anchor; mode (major/minor) = *phase choice*, since magnitude is mode-blind — a fact most harmonic theories miss and PCFSC exposes directly. The TIV distance of Bernardes et al. (2016) is exactly the tension channel here, which is the same machinery their *automatic harmony generator* uses.

**STRUCTURE**: Macro-form = a designed trajectory through *quality space*: each section is a (profile target, anchor phase, phase-velocity) triple. Verified-typical arc: Intro — whole-tone-ish profile (energy at 6, ambiguous gravity), anchor $\phi_0$; Verse — diatonic profile (energy at 5,7), anchor T, slow $v$; Chorus — triad-profile pools with dominant-phase excursions (an excursion is a temporary phase target, i.e. a temporary transposition/function); Bridge — octatonic profile (energy at 4,8), high phase velocity; Outro — return to the intro profile at anchor $\phi_0$ (HOME). Modulation = a phase step to a new anchor; the step size *is* the transposition interval, visible in every coefficient.

**TEXTURE**: Complement twins give built-in layering: a diatonic pool and its pentatonic complement are the "same harmony at two densities", so a melody pool (pentatonic, sparse) over a drone pool (diatonic, full) cannot clash — they share one quality spectrum. Per-voice phase roles (below) create heterophonic drift — voices exploring the same quality at different phase rates. The magnitude profile's *flatness* sets textural evenness: peaked profiles = one dominant sonority (homophony), flat profiles = non-hierarchical pointillism.

### UnitMatrix Integration (Voices & Sections)

**Voices** = rows, each with a *Fourier role*: assign voice $v$ the phase target of coefficient $k_v$ — e.g. Voice 1 (Melody) tracks the $k=1$ phase (tonic-drift contour), Voice 2 (Harmony) tracks $k=5$ (fifth/dominant side), Voice 3 (Bass) tracks $k=7$ (= $|f_7| = |f_5|$, the fourth side, grounding), higher voices track $k=3,4$ for color layers. Voices share the section's magnitude profile (same quality region) but walk their coefficient's phase at per-voice rates — shared quality, independent position = coherent-but-independent polyphony. Each cell $(v,s)$ then holds a *realized pool*: the abstract layer hands `rules/subset_network.py` the pool sequence + phase schedule; the concrete layer realizes each pool into `MusicUnit`s (voicing, register, articulation via `create_note_unit`/`create_chord_unit` or `rules/realize.py`'s `realize_progression(..., smooth=True)` for voice-leading continuity).

**Sections** = columns, each a (profile, anchor, velocity) triple: the abstract-section map. A typical 5-section form in quality space: Intro (whole-tone profile, anchor $\phi_A$, $v{=}0$), Verse (diatonic profile, $\phi_T$, slow), Chorus (triad-profile pools + dominant excursions, medium $v$), Bridge (octatonic profile, wandering $\phi$, fast), Outro (return to Intro triple — HOME). Section seams = phase-step events or profile swaps; because every section is a closed-form set family, the transition between any two sections is a *computed* minimal-phase-step modulation rather than a hand-written pivot.

**Cell filling** (concrete layer, zero-drift invariant untouched): 1. read section triple $s$; 2. match (or construct) the pc-pool for the section's positions; 3. per voice, walk the coefficient-$k_v$ phase schedule → pool transposition/selection per position; 4. realize each pool to events with `rules/realize.py` (register wraps octaves, smooth voice-leading across positions), pack into `MusicUnit`s and pad to `section_len` (terminal landmark) so `composer.validate()` passes. `Voices` = rows, `Sections` = columns, `Cells` = per-voice per-section MusicUnits, exactly per the abstract→concrete contract in LAYER_ARCHITECTURE.md.

### Pitfalls

1. **Magnitude is mode-blind (and quality-blind to inversion of the ICV)**. Major and minor triads have *identical* magnitudes (verified), and any two sets with the same ICV do. Design only magnitude profiles and the piece is a mode-less "neutral" harmony; mode, function, and position live in phase. Always specify phase targets for the dominant coefficients, not just magnitudes.
2. **Phase is only meaningful where magnitude is large** (Yust). $|f_A(6)| = 0$ for the whole-tone set — a phase target there is noise. Gate phase constraints by magnitude: constrain $\arg f_k$ only when $|f_k| > \varepsilon$ (e.g. half the coefficient's extremum).
3. **Profiles are not unique** — the $k{=}5$ maximum $2+\sqrt3$ is attained by several 7-note sets (verified), and complements share all $k\neq0$ magnitudes. A magnitude target is a *family* of pools; pin the family with cardinality ($T_0$), ME-ness, or explicit phase checks, or the same profile will silently produce unrelated sonorities.
4. **The ICV identity double-counts** — $|f(k)|^2$ is determined by the ICV, so imposing both a full ICV target *and* a magnitude profile is redundant at best, contradictory at worst. Pick one representation; the Fourier one is the better-conditioned (it diagonalizes transposition).
5. **$k=0$ (cardinality) dominates naive profile distance** — a 12-note profile distance grossly exaggerates cardinality mismatch. Normalize by $n$ (use $|f|/n$) and drop or down-weight $k=0$ when the goal is *quality*, not density.
6. **Phase walk = transposition drift by construction** — a continuous phase curve continuously transposes the pool, which the ear hears as panning/shimmer, not melody. This is desirable only in controlled doses; for stable tonality use piecewise-constant phase with steps, or slow $v$ and let the realize layer re-anchor registers.
7. **Abstract layer delivers pools, not notes** — a pool sequence has no durations, velocities, or voicings; skipping the realize step produces a plan, not a piece. Pair PCFSC with a concrete voice-leading realizer (001, 011, 050, 056) and keep the zero-drift gate.
8. **Rhythm-side duality has its own conventions** — the 16-pulse DFT uses $\mathbb{Z}_{16}$, so its "tonic phase" behaves differently from $\mathbb{Z}_{12}$; don't mix anchor-phase semantics across grids, and remember onset sets are usually *sparse* (few pcs) so magnitudes are small — normalize for comparison.

Candidate code path: `rules/fourier_pc_spectra.py` — `pc_set_dft(pcs)` (vectorized $f_A(k)$, returns complex 12-vector), `profile(pcs)` (normalized magnitudes $|f|/n$), `match_profile(target_mags, cardinality=None, weights=None)` (exhaustive 4096-set scan with normalized distance), `me_set(n, g)` (maximally-even pool by generator window), `phase_walk(phi0, v, ks, n_steps)` (designed phase schedule per coefficient), `fourier_tension(fA, fB)` (weighted Fourier distance, the TIV-style tension channel), and `complement_pair(pcs)` (the magnitude-twin). Feeds `rules/subset_network.py` (abstract layer) with per-section (pool, phase schedule, tension) records; concrete realization via `rules/realize.py`.

---

End of report.