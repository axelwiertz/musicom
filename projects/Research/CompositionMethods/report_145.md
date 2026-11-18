# Report — Method 145: Dyck Path Ballot Composition (DPBC)

**Job:** music-research cron (one new method per run) · **Date:** 2026-11-18
**Primary record:** this file · **DB:** `projects/Research/CompositionMethods/methods_db.md`
**Status:** COMPLETE — method researched, math verified (8/8 checks + engine demo), appended to DB, summary row added, standalone file written.

---

## 1. Identity block

| field | value |
|---|---|
| **Method ID** | **145** |
| **Name** | Dyck Path Ballot Composition |
| **Acronym** | DPBC |
| **Paradigm** | **Rules-Based** (deterministic ballot/balance law + closed-form counts; the only stochastic element is the *seed* choosing which valid curve, same stance as 144 LSPC's solution choice) |
| **Layer** | **abstract** (LAYER_ARCHITECTURE.md — tension curve / contour prototype / phrase-arch grammar / form-space counts, all register-invariant; emits *no* concrete events; the concrete layer maps height → scale degree, steps → slots, returns → cadence cells) |
| **One-line description** | Compose each section from a Dyck path — an $n$-up/$n$-down walk that never falls below 0 and must end at 0 (Bertrand's ballot law; counted by Catalan $C_n$) — so height is an *enforced* tension curve: HOME is a hard floor, returns to 0 are cadences (TURN), arches are phrases (LIFT), peaks are climaxes (TENSE). |
| **Candidate code path** | `rules/dyck_paths.py` (new abstract module: `catalan`, `narayana`, `sample_dyck` first-return recursion, `stats`, `tension_contract` — feeds `rules/subset_network.py`) + `generators/dyck_contour.py` (new concrete adapter: `path_to_cell` → MusicUnit, zero-drift padding) |
| **Standalone file** | `projects/Research/CompositionMethods/method_145_DPBC.md` |
| **Prototype dir** | `projects/Research/CompositionMethods/_web145_dpbc/` (verify_dpbc_math.py, compose_dpbc_demo.py, fetched sources) |
| **Demo outputs** | `projects/Research/outputs/dpbc145/` — `dpbc_145_demo.mid` (426 B), `.wav` (2.4 MB, FluidSynth), `.ogg` (163 KB), `.mid.provenance.json`, `dpbc_145_demo_report.json` |

## 2. ID resolution (dynamic, not assumed)

- Summary-table scan (`grep -oE '^\|\s*\*\*[0-9]{3}\*\*'` → extract IDs, sort -n, tail): max **144** (rows 001–144 present; 058 the only gap inside the range, 143 rows total).
- Standalone-file cross-check `method_*.md` / `report_*.md`: max **144** (method_144_LSPC.md, report_144.md).
- Table and file scan agree → **next free ID = 145**. Post-append check: grep for `146` → 0 hits (next free = **146**).

## 3. Line counts

| point | `wc -l methods_db.md` |
|---|---|
| at job start (first read) | 31 840 |
| after appending method 145 section (`cat >>`) | **31 930** (+90: 1 blank separator + 89 section lines) |
| after inserting the summary-table row (patch) | **31 931** (+1) |
| **my delta** | **+91 lines** |

## 4. Summary-table row (as inserted, line 155)

```
| **145** | abstract | Dyck Path Ballot Composition (DPBC) | **Rules-Based** | Pitch, Rhythm, Structure, Texture | Strong (Ballot-law: HOME = height-0 hard floor, LIFT = arch ascent, TENSE = peak height, TURN = return to 0) | Grid-Locked / Continuous (abstract curve; slot grid at realization) | Macro / Path (full-prefix ballot constraint) | $\mathcal{O}(N)$ walk + $\mathcal{O}(N)$ uniform sample (first-return recursion) | Composes each section from a Dyck path — $n$ up / $n$ down steps, never below 0, ending at 0 (Bertrand's ballot law; count = Catalan $C_n = \binom{2n}{n}/(n+1)$, $C_8 = 1430$): height = tension (HOME is a hard floor, TURN = return = cadence cell, TENSE = peak), arches = phrases (#$k$-arch = $[x^n](x\,C(x))^k$; primitive = $C_{m-1}$), peaks = climax schedule (Narayana $N(n,k)$), Chung–Feller equipartition = exactly $C_n$ paths at every above-axis balance $2k$ (LIFT/TURN register dial), uniform sampling via first-return recursion $P(j) = C_{j-1}C_{n-j}/C_n$ (naive rotate-to-minimum is biased). Motzkin level steps add rests ($M_n$). Abstract tension-curve/contour method — first Catalan-family method in the DB; discrete ballot-law foil to 048 RBMPD (soft barrier) / 095 CTC (general contours) / 066 GTTM (tree vs flat line); context-free-language counterpart to 130 SFT (regular). Feeds rules/dyck_paths.py → rules/subset_network.py. |
```

Classification columns, spelled out:

| column | value | rationale |
|---|---|---|
| Layer | abstract | tension curve + U/D contour + arch/phrase grammar + exact counts; register-invariant; no events; feeds rules/subset_network.py |
| Paradigm | Rules-Based | the ballot law is a hard, exact grammar; closed-form counts (Catalan/Narayana/Chung–Feller); seed only selects *which* valid curve |
| Primary elements | Pitch, Rhythm, Structure, Texture | pitch via height→degree mapping (contour prototype); rhythm via step grid + cadence cells; structure via arch decomposition + path sequence; texture via per-voice curves |
| Tonal gravity | Strong | HOME = height-0 **hard floor enforced by law** (not a tendency); TENSE = peak height; TURN = forced return to 0; LIFT = arch ascent |
| Metric binding | Grid-Locked / Continuous | abstract curve is step-timed (any grid); concrete layer fixes the slot grid |
| Memory depth | Macro / Path | the constraint is a **full-prefix** condition (every prefix must stay ≥ 0); semilength $n$ = phrase length; macro-form = path sequence |
| Time complexity | $\mathcal{O}(N)$ walk + $\mathcal{O}(N)$ uniform sample | first-return recursion with memoized Catalan; no enumeration (counts are closed form) |

## 5. Classification decision trail (DB de-duplication)

Grepped the DB before choosing: `Catalan` → 0 hits as a *method* (only prose: "Catalan" appears in 069 CWCC's Christoffel/maximal-evenness text and 114 FSBC's Stern–Brocot text — neither is a ballot-walk method); `Dyck` → 0; `ballot` → 0; `Motzkin` → 0; `Narayana` → 0; `Chung` → 0. **First Catalan-family method in the DB.**

Nearest neighbours, all distinct (documented in the section's Pitfalls 7):
- **095 CTC** (Contour Theory, abstract): classifies *general* contours (CAS/CSeg, I/R/RI). DPBC is a *constrained subfamily* with an exact tension law + exact counts.
- **048 RBMPD** (reflected Brownian): continuous, soft reflecting barrier, no balance law. DPBC = discrete, exactly balanced, hard floor, forced final return.
- **053 LFC** (Lévy flight): heavy-tailed jumps. DPBC = strictly ±1 steps.
- **066 GTTM-HC**: hierarchical prolongational *tree* via preference rules. DPBC = the flat 1D "structural line" itself, exact and non-hierarchical.
- **130 SFT-C**: *regular* word languages (forbidden words). Dyck language is context-free, provably not regular — the formal-language boundary.
- **076 PTM-ASC** (Thue–Morse): one fixed substitution sequence. DPBC = a *family* sampled under a balance law.
- **012 Euclidean**: rhythms only. DPBC = pitch/tension contour; rhythm delegated to the concrete layer.

Chosen paradigm **Rules-Based** (not Stochastic): every curve satisfies a deterministic law; the RNG only picks which curve (uniformly), exactly like 144's seeded solution choice.

## 6. Research provenance (sources fetched 2026-11-18, saved in `_web145_dpbc/`)

1. **Wikipedia: "Catalan number"** (`wiki_catalan.html`): $C_n = \frac{1}{n+1}\binom{2n}{n}$; Dyck words; André 1887 reflection proof; Mingantu 1730s; ballot interpretation; asymptotics.
2. **Wikipedia: "Bertrand's ballot theorem"** (`wiki_ballot.html`): $b(p,q) = \frac{p-q}{p+q}\binom{p+q}{p}$; André's permutation proof; cycle lemma; ties-allowed variant.
3. **Wikipedia: "Narayana number"** (`wiki_narayana.html`): $N(n,k) = \frac{1}{k}\binom{n-1}{k-1}\binom{n}{k-1}$; Dyck words with $k$ peaks; row sums = $C_n$.
4. **Wikipedia: "Dyck language"** (`wiki_dyck.html`): context-free, non-regular (contrast with 130 SFT regular languages).
5. **OEIS A000108** (`a000108.txt`, `curl ...&fmt=text`): Catalan $1,1,2,5,14,42,\dots,3814986502092304$ (n=30).
6. **OEIS A001263** (`a001263.txt`): Narayana triangle rows.
7. **OEIS A001006** (Motzkin, verified against formula, cited in section): $1,1,2,4,9,21,51,127,323,835,2188$.
8. **Chung, K. L. & Feller, W. (1949).** "On fluctuations in coin-tossing." *PNAS* 35(10), 605–608 — equipartition theorem (verified computationally, see §7).
9. Web search for prior art (`DuckDuckGo`/`lite`, `Bing`, `Mojeek`): search engines blocked/captcha'd (see §8); no established "Dyck-path composition" method surfaced — novelty claim rests on the DB grep (§5) + combinatorics literature (ballot/Dyck are classical, their *use as a compositional tension grammar* is the new contribution).

## 7. Verification (real execution, not fabricated)

**Math — `_web145_dpbc/verify_dpbc_math.py`, 8/8 checks PASSED:**
1. Catalan $C_n$ n=0..20 == OEIS A000108.
2. Brute-force Dyck counts n=1..8 == $C_n$ (1430 at n=8).
3. Bertrand strict-lead ballot == $\frac{p-q}{p+q}\binom{p+q}{p}$ for 7 (p,q) pairs.
3b. Ties-allowed ballot p=q=n == $C_n$ (the Dyck law).
4. Narayana peak distribution $N(n,k)$ exact n=1..8; sum = $C_n$.
5a. Primitive (single-return) paths of semilength $m$ == $C_{m-1}$.
5b. $k$-arch counts == $[x^n](x\,C(x))^k$ (first-return GF), n=1..8.
6. Chung–Feller equipartition: exactly $2k$ steps above axis → $C_n$ each, all $k$, n≤5; $(n{+}1)C_n = \binom{2n}{n}$.
7. Uniform sampler (first-return recursion): n=10, N=20 000 — mean peaks 5.510 (theory 5.500), mean arches 2.517 (theory 2.500).
8. Motzkin $M_n$ n=0..10 == OEIS A001006.

**Engine demo — `_web145_dpbc/compose_dpbc_demo.py`** (musicom engine only, per AGENTS.md): 3 voices × 2 sections (Lead = two seeded Dyck curves `UUUUDDUDUDUDUDDD` / `UUDUDDUDUUDUDUDD`, Bass = tonic pedal, Pad = held chord), `validate() → True "OK"`, MIDI 426 B (>40 B assert), FluidSynth WAV 2.4 MB, OGG 163 KB, provenance JSON written. Also found during dev: a 1-bar section (16 eighths = 2 bars) caused "Track length mismatch [7680, 3840, 3840]" — fixed by 2-bar sections; tail-rest padding conditional on `slot*slot_ticks < section_ticks`.

## 8. Quirks / pitfalls hit during this job

1. **Ballot off-by-one in my own verification.** First brute-force ballot returned 3 for (3,1) instead of 2 — I had implemented *ties-allowed* (place D when lead ≥ 1), which is the Dyck law, not strict lead (requires lead ≥ 2 before D). Turned into a *feature*: both variants are documented (strict = excursions/primitive $C_{n-1}$; ties = Dyck $C_n$) and are Pitfall 1 of the method section.
2. **Peaks ≠ arches.** Initially asserted arch distribution == Narayana peaks; exhaustively false (n=3: peaks (1,3,1), arches (2,2,1)). Replaced with the correct arch identity $[x^n](x\,C(x))^k$ — now Pitfall 2.
3. **Rotate-to-minimum sampling is biased.** First sampler (cycle lemma rotation) gave mean peaks 1.83 vs 5.50 theory at n=10. Diagnosed: weights each path by $1/\text{arches}$ (UUDD: 4 balanced words, UDUD: 2 at n=2). Replaced with first-return recursion — now Pitfall 3.
4. **Chung–Feller counting convention.** "Steps above the axis" must count step *interiors* (U from h≥0, D from h≥1), and only balanced words (exactly n up) — first attempt counted endpoints and all 2^(2n) words. Fixed; verified n≤5.
5. **Search engines blocked.** DDG (html + lite) → captcha; Mojeek → empty; Bing → irrelevant (Catalan *language* results). Fell back to direct fetches: Wikipedia ×4 + OEIS ×2 + literature (Chung–Feller 1949). Sufficient for a classical-combinatorics method.
6. **Provenance API mismatch.** `write_provenance` accepts only `(artifact_path, classification, generator, sources, parameters, notes)` — extra kwargs (`method_id`) raise TypeError; classification must be `"ai-generated"` (not `AI_GENERATED`).
7. **MidiInstrument enum is small** — only FLUTE/BASS/STRING_ENSEMBLE/PIANO/etc. exist; `PIZZICATO_STRINGS`/`STRING_ENSEMBLE_1` don't. Used real names.
8. **Zero-drift demo bug**: 16 eighth-note slots need 2 bars (3840 ticks), not 1 (1920); lead row came out 7680 ticks vs 3840 for the others → validate failed. Fixed with 2-bar sections + conditional tail rest.
9. **Table-row patch anchors**: matched on the unique row-144 tail `Feeds generators/langford_pairing.py. |` + the following blank line + next section header — no `||` prefix introduced (grep `^||` count 0) and single-backslash LaTeX preserved (od byte check: `\mathcal{O}`).

## 9. Appended method section (complete text, as appended to methods_db.md, now lines 31842–31930)

```markdown
# Dyck Path Ballot Composition (DPBC) (Method 145)

### Source

- **Wikipedia: "Catalan number"** (rev. 2026-11-02, fetched 2026-11-18 via curl) — $C_n = \frac{1}{n+1}\binom{2n}{n} = \binom{2n}{n} - \binom{2n}{n+1}$; the sequence $1,1,2,5,14,42,132,429,1430,\dots$; Dyck words of length $2n$ ("no initial segment has more Y's than X's"); Désiré André's 1887 reflection-counting proof; Mingantu's 1730s discovery; the Bertrand-ballot interpretation ($C_n$ = ways for candidate A with $n{+}1$ votes to lead B with $n$); asymptotics $C_n \sim 4^n/(n^{3/2}\sqrt{\pi})$.
- **Wikipedia: "Bertrand's ballot theorem"** (fetched 2026-11-18) — the ballot number $b(p,q) = \frac{p-q}{p+q}\binom{p+q}{p}$ (A strictly ahead throughout, $p > q$); André's bijective/permutation proof (often mislabeled "reflection principle"); the cycle-lemma proof; the ties-allowed variant (A never behind), which for $p = q = n$ is exactly the Dyck count $C_n$.
- **Wikipedia: "Narayana number"** (fetched 2026-11-18) — $N(n,k) = \frac{1}{k}\binom{n-1}{k-1}\binom{n}{k-1} = \frac{1}{n}\binom{n}{k}\binom{n}{k-1}$; counts Dyck paths of semilength $n$ with exactly $k$ peaks; $\sum_k N(n,k) = C_n$; row $n{=}8$: $1,28,196,490,490,196,28,1$.
- **Wikipedia: "Dyck language"** (fetched 2026-11-18) — the Dyck language is a canonical **context-free** language (balanced parentheses) and is provably **not regular** — the precise formal-language contrast with 130 SFT-C (subshifts of finite type are regular languages).
- **Chung, K. L. & Feller, W. (1949).** "On fluctuations in coin-tossing." *PNAS* 35(10), 605–608 — the equipartition theorem verified here computationally: among all $\binom{2n}{n}$ balanced $\pm1$ paths, **exactly $C_n$** have exactly $2k$ steps strictly above the axis, for every $k = 0..n$ (hence $(n{+}1)C_n = \binom{2n}{n}$).
- **OEIS A000108** (Catalan), **A001263** (Narayana triangle), **A001006** (Motzkin numbers: level-step generalization $1,1,2,4,9,21,51,127,323,835,2188$). Fetched 2026-11-18 via `curl oeis.org/...&fmt=text`.
- **Verified prototype (this document):** `_web145_dpbc/verify_dpbc_math.py` — 8/8 combinatorial checks pass (see Description); `_web145_dpbc/compose_dpbc_demo.py` — engine demo, `validate() → True "OK"`, MIDI 426 B, WAV 2.4 MB (FluidSynth), OGG 163 KB, provenance written. Sources fetched into `_web145_dpbc/` (wiki_catalan.html, wiki_ballot.html, wiki_narayana.html, wiki_dyck.html, a000108.txt, a001263.txt).

### Layer

**abstract** (LAYER_ARCHITECTURE.md). DPBC designs the *composition plan*: a tension curve (height = tension), a contour prototype (the U/D word), a phrase partition (arches), and exact form-space counts ($C_n$) — all **register-invariant** (the abstract object is a walk, not a pitch sequence). It emits no concrete events; the concrete layer maps height → scale degree, steps → slots, returns → cadence cells. It is the *first Catalan-family method* in the DB and a discrete, law-enforced tension-curve generator for `rules/subset_network.py`. Candidate code path: `rules/dyck_paths.py` (new abstract module: path sampling, arch/peak statistics, Chung-Feller balance dial) + `generators/dyck_contour.py` (new concrete adapter: height → scale degree, step → duration, cadence cells).

### Description

DPBC composes a section from a **Dyck path** of semilength $n$: a walk of $2n$ unit steps, $n$ up and $n$ down, whose partial sums never go negative and which ends at height 0. The **ballot law** (Bertrand 1887 / André 1887) is the compositional grammar: in every prefix of the piece, the number of up-steps is never less than the number of down-steps — a melody that may climb anywhere but may **never fall below its starting point** until the final cadence, and that *must* return exactly to it at the end. The count of distinct such tension curves is the Catalan number $C_n = \frac{1}{n+1}\binom{2n}{n}$ ($C_8 = 1430$ sixteen-step curves, $C_{16} = 35{,}357{,}670$), so the semilength is simultaneously a *length* and a *form-space size*: choosing $n$ fixes how many distinct "harmonic journeys" exist.

Height is tension, and the law makes the grammar exact:

- **HOME is a hard floor, not a tendency.** Height 0 = tonic; the ballot law *forbids* the curve from ever going below it (unlike 048 RBMPD's soft reflecting barrier) and *forces* the final return (unlike 023's bounded wander). The tonic is not preferred — it is **enforced**.
- **TURN = return to 0** = cadence: a Dyck path returns to 0 exactly at its arch boundaries; every return is a structural TURN (phrase end / cadence cell / rest).
- **LIFT = arch ascent**: the path decomposes uniquely into **arches** (primitive excursions that touch 0 only at their ends); # primitive paths of semilength $m$ is $C_{m-1}$ (verified), and the number of $k$-arch paths of semilength $n$ is $[x^n](x\,C(x))^k$ where $C(x) = (1-\sqrt{1-4x})/(2x)$ is the Catalan generating function (verified $n \le 8$). Arches are phrases; arch count is the phrase-partition dial.
- **TENSE = peak height**: peaks (U-then-D pairs) are climax points; the number of paths with exactly $k$ peaks is the Narayana number $N(n,k) = \frac{1}{k}\binom{n-1}{k-1}\binom{n}{k-1}$ (verified $n \le 8$), so peak *count* is a user-set parameter with a known count of realizations, and peak *height* is the direct TENSE dial.
- **LIFT/TURN register balance = the Chung–Feller dial**: among all $\binom{2n}{n}$ balanced words, exactly $C_n$ have exactly $2k$ steps strictly above the axis — the same count for *every* $k = 0..n$ (verified $n \le 5$; implies $(n{+}1)C_n = \binom{2n}{n}$). Choose $k$ = how many of the $2n$ slots live in the upper register; every choice has exactly $C_n$ realizations. This is an exact, provable equipartition of the LIFT/TURN balance.

**Uniform sampling (the variation axis).** The naive route — pick a random balanced word and rotate it to the first global minimum — is **biased** (it weights a Dyck path by $1/\text{arches}(D)$: at $n=2$, UUDD receives 4 balanced words, UDUD receives 2; measured). The correct uniform sampler is the **first-return recursion**: $\mathrm{Dyck}(n) = \text{arch}(j) + \mathrm{Dyck}(n-j)$ where the first arch has semilength $j$ with probability $C_{j-1}C_{n-j}/C_n$, and a primitive arch is $\mathrm{U} + \mathrm{Dyck}(j-1) + \mathrm{D}$. Verified: 20 000 samples at $n=10$ give mean peaks $5.510$ (theory $5.500$) and mean arches $2.517$ (theory $2.500$). Because $C_n$ is huge, the *seed* is the piece's identity — same $n$, different seed, different curve (the same "same-orchestra, different-counterpoint" stance as 144 LSPC's solution choice).

**Generalizations.** **Motzkin paths** add level steps (no height change) — rests or repeated notes; counts follow Motzkin numbers $M_n$ (OEIS A001006, verified $n \le 10$), which grow slower than Catalan: adding rests changes the enumeration law. **Multi-path texture**: independent voices = independent Dyck paths (possibly sharing a return schedule for "cadence sync"). **Concatenation**: any sequence of Dyck paths is itself a valid walk — section seams are exact returns to 0, so section chains are always legal (macro-form = path sequence).

Measured facts (all from the prototype logs):

| audit | result |
|---|---|
| Catalan counts | $C_n$ for $n=0..20$ exact match to OEIS A000108 (incl. $C_8=1430$, $C_{16}=35\,357\,670$) |
| brute-force Dyck counts | semilength $n=1..8$ exhaustive == $C_n$ (14 at $n=4$, 132 at $n=6$, 1430 at $n=8$) |
| Bertrand strict-lead ballot | $b(p,q) = \frac{p-q}{p+q}\binom{p+q}{p}$ exact for 7 (p,q) pairs (2, 2, 3, 5, 9, 14, 28) |
| ties-allowed ballot | $p=q=n$: count == $C_n$ (the Dyck law; strict-lead needs $p=n{+}1, q=n$) |
| Narayana peaks | $N(n,k)$ exact $n=1..8$; $\sum_k = C_n$; row $n{=}8$: 1,28,196,490,490,196,28,1 |
| primitive arches | # primitive (single-return) paths of semilength $m$ == $C_{m-1}$ ($m=1..7$) |
| arch-GF | # $k$-arch paths == $[x^n](x\,C(x))^k$ for $n=1..8$ |
| Chung-Feller | exactly $2k$ steps above axis: $C_n$ each, all $k$, $n \le 5$; $(n{+}1)C_n = \binom{2n}{n}$ |
| uniform sampler | first-return recursion: mean peaks 5.510 vs 5.500, mean arches 2.517 vs 2.500 ($n=10$, 20 000 samples) |
| Motzkin | level-step paths $M_n$ == OEIS A001006 ($n \le 10$) |
| rotation bias | naive rotate-to-minimum weights path by 1/arches (UUDD: 4 words, UDUD: 2 at $n=2$) — do not use |

### Technical Mechanics

**1. The law as a hard constraint.** A Dyck path $w \in \{U,D\}^{2n}$ satisfies $\sum_i w_i = 0$ and $\sum_{i \le t} w_i \ge 0$ for all $t$. Equivalently (ballot form): in every prefix, $\#U \ge \#D$, with equality only at arch boundaries and the end. The count is $C_n$; the *strict*-lead variant ($\#U > \#D$ in every nonempty prefix) is the excursion/primitive case and equals $C_{n-1}$ — the strict vs ties-allowed off-by-one is the method's first trap (see Pitfalls 1).

**2. Enumeration without enumeration.** All structure is countably closed form: $C_n$ (all paths), $N(n,k)$ (peaks), $[x^n](x\,C(x))^k$ (arches), Chung-Feller (register balance), $M_n$ (Motzkin with rests). The composer never enumerates; it samples (first-return recursion) and counts (closed forms), so cost is $\mathcal{O}(n)$ per path plus $\mathcal{O}(n)$ one-time Catalan table.

**3. The four dials.** (a) *Semilength $n$* — phrase length AND form-space size ($C_n$ distinct curves). (b) *Seed* — uniform path choice = variation (the only stochastic element; deterministic given seed, same stance as 144). (c) *Chung-Feller balance $k$* — how many of the $2n$ steps sit above the axis (register/energy balance; every $k$ has exactly $C_n$ realizations). (d) *Mapping* — U/D step sizes, height→degree curve, level-step (rest) insertion at the concrete layer.

**4. Arch/phrase grammar.** Decompose $w = A_1 A_2 \cdots A_k$ into primitive arches; $A_i = \mathrm{U}\, m_i \,\mathrm{D}$ where $m_i$ is an arbitrary Dyck path of semilength $|A_i| - 1$. Phrase $i$ spans arch $A_i$; arch boundary = cadence. Peak placement within an arch is a Narayana-structured micro-grammar (a peak = U immediately followed by D).

**5. Score realization.** Abstract: choose $(n, k, \text{seed})$; sample $w$; split into arches. Concrete: height $h(t)$ → scale degree $\text{root} + h(t)$ (the ballot law guarantees $h \ge 0$, so the tonic is a hard floor); each step = one grid slot; returns to 0 = cadence cells (long note, rest, or chord change); peaks = climax (velocity/density boost); arches = phrase slurring. The demo (semilength 8, two sections, C major): path A `UUUUDDUDUDUDUDDD` (5 peaks, 1 arch, max height 4) → section A climbs to the upper octave in one long phrase and falls back at the cadence; path B `UUDUDDUDUUDUDUDD` (6 peaks, 3 arches, max height 2) → three short phrases in a narrow register; 3 voices × 2 sections, `validate() → True "OK"`, MIDI 426 B (16 lead notes read back, 2 bars/section, 480 tpb).

### Musical Elements Framework

- **PITCH**: the abstract layer yields a *contour prototype* (U/D word + height curve), register-invariant by construction — the same object can be realized in any key/register without re-solving (the abstract-layer invariant). The concrete adapter maps height → scale degree; because the ballot law keeps height $\ge 0$, the tonic is a **hard floor** — a stronger, exact tonal-gravity claim than any tendency-based method (contrast 002/053/048). Peak height = registral climax; Chung-Feller $k$ = how much of the piece lives in the upper register.
- **RHYTHM**: the abstract curve is step-timed (uniform slots); rhythm enters at the concrete layer (step = eighth/sixteenth; level steps = rests/repeats via Motzkin). The only intrinsic rhythmic accents are the **returns to 0** (cadence cells: long note/rest) — the TURN points — and the **peaks** (climax onsets). This is a deliberate flatness: DPBC is a *pitch/tension* grammar, not a density grammar (see Pitfalls 5).
- **HARMONY**: none implied by the law; returns to 0 are the harmonic-rhythm points (chord changes land on cadences by construction — "harmony by return schedule", the abstract analogue of 144's "harmony by scheduling"). At realization: tonic at height 0, dominant/upper-structure at peaks, subdominant mid-arch — the tension curve directly suggests a functional map.
- **STRUCTURE**: the macro-form is a *sequence of Dyck paths* (one per section; concatenation is always legal — seams are exact returns to 0, so zero-drift is free). The arch decomposition is the phrase tree; $C_n$ is the form-space count; Narayana peaks parameterize climax density; Chung-Feller $k$ sets the register arc. Nested structure: an arch's interior is itself a Dyck path — recursion gives a self-similar phrase grammar (each phrase is a miniature of the whole, the discrete analogue of 066 GTTM's recursive diminution, but flat and exact rather than tree-based and preference-guided).
- **TEXTURE**: monophonic by default (one curve = one voice); polyphony = independent curves per voice, with optional shared return schedule ("cadence sync" — all voices turn together) or deliberately offset arches (hocket-ish overlap, distinct from 111 VTCC's strict tiling). Peak-density and Chung-Feller balance per voice control registral spread.

### UnitMatrix Integration (Voices & Sections)

**Abstract-layer contract.** DPBC fills the abstract plan, not cells: per (voice, section) it supplies `{curve: U/D word, height profile, arches: [(start_slot, end_slot, peak_height)], peak_flags, chung_feller_k}` — register-invariant, tick-free. The concrete adapter consumes this contract and produces `MusicUnit`s.

**Voices = rows = one Dyck path per voice.** Row $v$'s curve is independent (seed per voice, e.g. `seed * 101 + row` like the humanizer's child-seed rule); shared return schedule = harmonic sync. Row params: `{semilength n_v, seed, chung_feller k_v, mapping (step size, degree curve), instrument}`.

**Sections = columns = one path per section** (or a path per voice per section). Column $j$ holds `{semilength n_j, seed_j, k_j}`; a column change is a *curve* change (macro-form = path sequence). Seam safety: every path ends at height 0 by law, so section seams are exact returns — cadence cells land on seams, and the zero-drift invariant is preserved by the concrete adapter's padding (each cell ends exactly at `section_len` ticks).

**Cells = MusicUnit.** At realization, cell $(v,j)$: step slots map to tick offsets (slot $\times$ slot_ticks); height → pitch; return slots → cadence cells (long note / rest); peak slots → accent velocity; tail rest pads the cell to full section length (the `_unit_from_events` pattern). Demo (3 voices × 2 sections, 120 bpm, 480 tpb, 16 eighth-slots per 2-bar section): Lead = the two curves above (16 notes each), Bass = tonic pedal, Pad = held chord per section; `validate() → True "OK"`; MIDI 426 B, 16 lead notes read back per section, WAV 2.4 MB, OGG 163 KB.

**Composition path.** Abstract: `choose (n_j, k_j, seed_j) per section → sample_dyck(n_j) → arch split → tension contract` → concrete: `height→degree, slot→tick, returns→cadence cells, fill_voice_section, validate()` → absolute (any SP renderer). Canonical loop: `n → first-return sample → arches → map to cells → validate() → to_midi()`.

### Pitfalls

1. **Strict-lead vs ties-allowed (the off-by-one that breaks the count).** Strict lead ($\#U > \#D$ in every nonempty prefix) is *not* the Dyck law — it counts excursions and equals $C_{n-1}$; the Dyck/ballot law allows ties ($\#U \ge \#D$, returns to 0 allowed). Implementing the ballot check as "place D only when lead $> 0$" actually computes the *strict* variant (my first verification attempt failed exactly here: it returned 3 for ballot(3,1) instead of 2). Correct rules: ties-allowed places D when lead $\ge 1$ *before* the step; strict requires lead $\ge 2$. Test vectors: $C_3 = 5$ (ties), ballot(3,1) = 2, ballot(4,2) = 5.
2. **Peaks ≠ arches (a classic misattribution).** Narayana $N(n,k)$ counts paths with $k$ *peaks*; the number of $k$-*arch* paths is a different sequence, $[x^n](x\,C(x))^k$ (at $n=3$: peaks $(1,3,1)$, arches $(2,2,1)$ — verified exhaustively). Pick the right statistic for the claim: peaks = climax count, arches = phrase count.
3. **Rotate-to-minimum sampling is biased.** Choosing a uniform balanced word and rotating it to its first global minimum yields Dyck paths with probability proportional to $1/\text{arches}(D)$ — flat, low-arch paths are over-represented (UUDD gets 4 words vs UDUD's 2 at $n=2$; measured mean peaks 1.83 vs 5.50 at $n=10$). Use the first-return recursion, which is provably uniform.
4. **Register blow-up.** Peak height grows with $n$ (a path can reach height $n$); mapping height linearly to scale degree exceeds practical registers. Fold the degree map (octave fold, or height → degree with a cap + level steps) — the ballot law still holds on the *height* walk regardless of the pitch mapping.
5. **Flat rhythm by default.** Uniform step slots plus only-return/peak accents means no density contour. Add Motzkin level steps (rests/repeats — but then the Catalan enumeration no longer applies; use $M_n$), vary slot duration at peaks, or let cadence cells stretch (the demo keeps it literal).
6. **Seeding is identity.** $C_8 = 1430$, $C_{16} \approx 35$M — two runs with different seeds produce different pieces that both satisfy the law; record the seed (provenance) or the piece is not reproducible. Same stance as 144's solution choice.
7. **Neighbour audit.** 095 CTC classifies *general* contours (CAS/CSeg, I/R/RI transforms) — DPBC is a *constrained subfamily* with an exact tension law (HOME floor, forced final return) and exact counts; 048 RBMPD is continuous reflected Brownian (soft barrier, no balance law) — DPBC is the discrete, exactly-balanced ballot-law counterpart; 053 LFC has heavy-tailed jumps — DPBC is strictly $\pm1$; 066 GTTM-HC is a hierarchical prolongational *tree* — DPBC is the flat 1D "structural line" itself; 130 SFT-C generates *regular* word languages (forbidden words) — the Dyck language is **context-free and provably not regular** (balanced parentheses), the formal-language boundary between the two; 076 Thue-Morse is a fixed substitution sequence — DPBC is a *family* sampled under a balance law. Also distinct from 012 Euclidean (rhythms only): DPBC's object is a pitch/tension contour; rhythm is delegated to the concrete layer.
8. **Motzkin changes the count law.** Adding level steps (rests) changes the enumerating sequence from Catalan to Motzkin ($M_8 = 1278$ vs $C_8 = 1430$) — do not quote Catalan counts for a piece that contains rests; quote $M_n$ (or per-step weighted counts).
```

## 10. Deliverables checklist

- [x] ID resolved dynamically → 145 (table max 144, file max 144, no 145 anywhere before writing; post-append: 146 free)
- [x] Layer classified first → **abstract** (tension curve / contour / phrase grammar, register-invariant, feeds rules/subset_network.py)
- [x] Paradigm → **Rules-Based**; novelty checked against all 144 existing methods (esp. 095 CTC, 048 RBMPD, 053 LFC, 066 GTTM, 130 SFT, 076 PTM, 012 Euclidean) — first Catalan-family method
- [x] Researched with web sources (Wikipedia ×4, OEIS ×3, Chung–Feller 1949) + computational verification (8/8 math checks, engine demo validate OK)
- [x] Musical Elements Framework (PITCH / RHYTHM / HARMONY / STRUCTURE / TEXTURE) + UnitMatrix integration (Voices/Sections/Cells) + Pitfalls (8)
- [x] Appended via `write_file` → `cat >>` → `rm` (no heredoc/execute_code); temp file removed
- [x] Summary row added (line 155), single `|` prefix (grep `^||` → 0), single-backslash LaTeX verified via od byte check
- [x] Standalone `method_145_DPBC.md` (extended math §1, Python implementation sketch §2, references §3)
- [x] `wc -l` + grep verification done (§3: 31 840 → 31 931; section header line 31842; row line 155)
- [x] Report written (this file)

**Next free ID: 146.**
