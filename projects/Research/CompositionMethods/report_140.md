# Report — Method 140: Latent Dirichlet Allocation Texture-Archetype Composition (LDATAC)

**Date:** 2026-11-11 · **Agent:** music research cron job · **Status:** complete, verified, appended.

| Field | Value |
|---|---|
| Method ID | **140** (max existing was 139; next free = **141**) |
| Name | Latent Dirichlet Allocation Texture-Archetype Composition |
| Acronym | **LDATAC** |
| Paradigm | **AI-Driven** (unsupervised Bayesian topic model) |
| Layer | **concrete** (emits `MusicEvent`s filling UnitMatrix cells; also carries an abstract shadow via the simplex $\theta_d$) |
| One-line description | Compose the piece as a topic model: sections are documents, notes are gesture-token words, texture archetypes are topics; sample the Dirichlet–multinomial posterior predictive $p(w\mid d)=\sum_k\hat\theta_{dk}\hat\phi_{kw}$, one draw per note. |
| `methods_db.md` lines before | **31017** |
| `methods_db.md` lines after | **31102** (+85: +84 section, +1 table row) |
| Method section location | lines **31019–31102** (end of file) |
| Summary row location | line **150** (immediately after the 139 LSAC row) |
| Standalone file | `/opt/data/projects/Research/CompositionMethods/method_140_LDATAC.md` |
| Candidate code path | `generators/lda_topics.py` (`GestureVocabulary`, `ArchetypeModel.fit/gibbs/canonicalize/posterior_predictive/sample_cell/tension_curve`); optional corpus front-end `analysis/tokenize.py` |
| Verification script | `_web140/verify_140_LDATAC.py` → `_web140/verify_140_output.txt` (**11/11 pass**) |
| Demo MIDI | `_web140/ldatac_140.mid` (8983 B, `validate() == True`, 1049 events) |
| Web cache | `_web140/` (`wiki_lda.json`, `s2.json` (429), `oa1.json`, `oa_tonal.json`, `cr_tonal.json`, `cr_gen.json`, `oa_gen.json`) |

---

## 1. ID resolution (dynamic, not assumed)

```
grep -oP '^\| \*\*\K[0-9]{3}' methods_db.md | sort -n | tail   → 125 … 139
ls method_*.md report_*.md | extract 3-digit                   → 134,135,136,137,138,139
```
Both agree: **max = 139** ⇒ new ID **140**. Table header read at top of file (`| Method ID | Layer | Method Name | Paradigm | Primary Elements | Tonal Gravity | Metric Binding | Memory Depth | Time Complexity | Description / UnitMatrix Integration |`, 10 columns), so the new row carries a **Layer** column at position 2.

## 2. Layer classification (decided first)

**concrete.** The method's output is per-cell event lists with pitch, tick onset, tick duration and velocity — the things that fill UnitMatrix cells. The abstract shadow (the $\theta_d$ simplex, its KL tension curve) is noted but the primary artifact is a realized matrix. Not absolute (no synthesis, no rendering).

## 3. Paradigm

**AI-Driven** — a probabilistic graphical model (LDA plates: $K$ topics × $S$ documents × $N_d$ tokens), parameters *learned* from a corpus by collapsed Gibbs, then sampled. Distinct from Rules-Based (no hand-written rules: 066 GTTM-HC, 034 PCFG) and from Nature-Led (no physical process).

## 4. Novelty audit

`grep -ic` before entry: `latent dirichlet` **0**, `topic model` **0**, `LDA` (word-boundary) **0**, `bag of words` 0, `perplexity` 0, `plate notation` 0. `archetype` = 15 hits, all descriptive prose (Narmour P/R/I archetypes at line 16754; loose "textural archetype" at 21959; "structural archetypes" at 6920) — no topic-model method.

Music-LDA literature found is **analysis/classification only** (tonal profiles 2021, raga ID 2011, mood classification 2016); none uses the posterior predictive as a *generator*. Documents checked:
- Moss & Rohrmeier 2021, *Music & Science* 4, doi:10.1177/20592043211048827 (verified via Crossref + OpenAlex: authors, journal, year).
- Raga ID, doi:10.3844/jcssp.2011.1711.1716; Hindi-lyrics mood, doi:10.1109/incite.2016.7857593 (from OpenAlex `latent dirichlet allocation music` search).
- OpenAlex/Crossref queries for "LDA + music generation" returned only NLP/deep-generation papers — no LDA generative composition.

## 5. Verification (11/11)

| # | Check | Measured |
|---|---|---|
| 1 | topic → archetype recovery (cosine, 1-1 match) | 0.991 / 0.9938 / 0.9976 |
| 2 | per-section mixture recovery | mean 0.9944, min 0.9410 |
| 3 | held-out perplexity vs uniform | 9.282 vs 30.0 |
| 4 | exchangeability (shuffled doc likelihood) | \|Δlog p\| = 0.0 exact |
| 5 | determinism (same seed) | max\|Δφ\| = 0.0 |
| 6 | α → mean θ entropy | 0.289 / 0.551 / 0.943 nats at α = 0.05 / 1 / 8 (max ln 3 = 1.099) |
| 7a | zero drift | 32/32 cells end at 7680 ticks |
| 7b | tension curve spread | KL = [0.441, 0.111, 0.029, 0.314, 0.765, 0.116, 0.094, 0.441], 26× |
| 8 | engine build | `validate()` True ('OK'), 1049 events, 8983 B MIDI |
| 9 | held-out mixture inference (continuation) | mean 0.9950, min 0.9774 |
| 10 | K=5 over-specification | archetypes still covered: 0.995 / 0.998 / 0.991 |

Prototype: 4 voices × 8 sections × 4 bars, tpb 480, bpm 96, programs FLUTE / SYNTH_PAD / BASS / VIOLIN.

## 6. Summary-table row (verbatim as written)

```
| **140** | concrete | Latent Dirichlet Allocation Texture-Archetype Composition (LDATAC) | **AI-Driven** | Pitch, Rhythm, Harmony, Structure, Texture | Moderate (Mixture-of-archetypes: HOME = $\theta_d$ nearest the corpus mean / $\min_d \mathrm{KL}$, TENSE = $\max_d \mathrm{KL}(\theta_d \,\Vert\, \bar\theta)$; key fixed at realization, tokens are intervals) | Grid-Locked (token durations quantize to the tick grid) | Meso/Phrase (per-section $\theta_d$; bag-of-tokens inside a cell) | $\mathcal{O}(I \cdot N \cdot K)$ collapsed Gibbs; generation $\mathcal{O}(N \cdot K)$; exact posterior intractable | Composes the UnitMatrix as a **topic model over gesture tokens**: each section = a document, each cell's notes = words drawn from a **texture archetype** (topic), with the Dirichlet–multinomial composition rule $p(w\mid d)=\sum_k \hat\theta_{dk}\hat\phi_{kw}$ (Blei–Ng–Jordan 2003; collapsed Gibbs, Griffiths–Steyvers 2004). $\alpha$ = per-section purity (verified mean $\theta$ entropy 0.289 → 0.551 → 0.943 nats for $\alpha$ = 0.05/1/8, max $\ln 3$), $\eta$ = archetype crispness, per-voice $\beta_v$ = row identity (bass 0.8 ostinato, pad 0.8 sustain); the KL profile $D_d=\mathrm{KL}(\theta_d \,\Vert\, \bar\theta)$ is the tension curve (verified 26× spread, 0.029→0.765). Exchangeable by construction — retrograde has identical likelihood ($\lvert\Delta\log p\rvert=0.0$), so order is delegated to the rhythm layer; duration clamp $\min(d_n, L-t_n)$ gives zero drift by construction (32/32 cells exact). Recovers planted archetypes at cosine 0.991–0.998, mixtures 0.994, held-out ppl 9.28 vs uniform 30.0; HDP (Teh 2006) infers $K$. 11/11 checks pass; 4×8 matrix, 1049 events, validate OK. Feeds generators/lda_topics.py. AI-Driven sibling of 086 HMM-C / 085 NMF-C; foil to 034 PCFG / 066 GTTM-HC / 118 D3PM. |
```

Post-patch validation of that row: 10 columns (`split on |` → 10 fields), 11 pipe characters, no `||` prefix, **0** occurrences of double-escaped `\\` (LaTeX backslashes are single).

## 7. Classification columns rationale

- **Tonal Gravity — Moderate.** No functional-harmony machinery: gravity comes from the corpus' archetypes (which intervals that style uses) + the realization-time scale map. The *tension* axis is not harmonic function but simplex distance: HOME = $\min_d \mathrm{KL}(\theta_d\Vert\bar\theta)$, TENSE = $\max_d$, LIFT = a newly introduced archetype, TURN = an off-corpus blend. Tokens are intervals ⇒ transposition-invariant, key assigned at realization.
- **Metric Binding — Grid-Locked.** Token durations are tick-quantized (120/240/480), cells fill to exact `section_len`; the model itself is metric-agnostic, but the realization contract is grid-locked.
- **Memory Depth — Meso/Phrase.** Per-section $\theta_d$ is the context; inside a cell the model is a bag (memoryless, exchangeable). Order must be recovered from an external rhythm layer.
- **Time Complexity.** Gibbs sweep $\mathcal{O}(NK)$ × $I$ iterations; generation $\mathcal{O}(NK)$; exact posterior inference intractable in general (Blei 2003) — the sampler is the method, not an optimization.

## 8. Method section (verbatim, as appended to `methods_db.md`)

# Latent Dirichlet Allocation Texture-Archetype Composition (LDATAC) (Method 140)

### Source

- **Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003).** "Latent Dirichlet Allocation." *Journal of Machine Learning Research* 3, 993–1022 — the model: documents as mixtures over topics, topics as distributions over words, Dirichlet priors on both simplices; variational inference and the intractability of the exact posterior.
- **Griffiths, T. L., & Steyvers, M. (2004).** "Finding scientific topics." *PNAS* 101 (Suppl. 1), 5228–5235, doi:10.1073/pnas.0307752101 — the **collapsed Gibbs sampler** used here: $\theta$ and $\phi$ are integrated out analytically (Dirichlet–multinomial conjugacy), leaving only the per-token topic indicators $z_{dn}$ to be resampled.
- **Pritchard, J. K., Stephens, M., & Donnelly, P. (2000).** "Inference of population structure using multilocus genotype data." *Genetics* 155(2), 945–959 — the admixture model: each individual (here: each section) is a *mixture* of $K$ ancestral populations (here: texture archetypes) with proportions on the simplex. The cleanest statement of the composition idea.
- **Teh, Y. W., Jordan, M. I., Beal, M. J., & Blei, D. M. (2006).** "Hierarchical Dirichlet Processes." *JASA* 101(476), 1566–1581, doi:10.1198/016214506000000302 — the nonparametric extension: $K$ is inferred (Chinese-restaurant-franchise), so the composer does not have to fix the archetype count.
- **Moss, F. C., & Rohrmeier, M. (2021).** "Discovering Tonal Profiles with Latent Dirichlet Allocation." *Music & Science* 4, doi:10.1177/20592043211048827 — LDA applied to pitch-class distributions to recover tonal profiles: **analysis**, not generation. The nearest music-theoretical precedent, and the paper this method inverts.
- **LDA in music, prior art (all discriminative):** "Latent Dirichlet Allocation Model for Raga Identification of Carnatic Music," *J. Computer Science* 7(11), 2011, doi:10.3844/jcssp.2011.1711.1716; "Music mood classification based on lyrical analysis … using LDA," INCITE 2016, doi:10.1109/incite.2016.7857593. Both *classify* existing music; neither samples a piece.
- **Wikipedia** "Latent Dirichlet allocation" (pageid 4605351, rev. 2026-10-19, cached `_web140/wiki_lda.json`), 200 OK.
- **Novelty check (2026-11-11)** `grep -ic` on `methods_db.md` before entry: `latent dirichlet` = **0**, `topic model` = **0**, `LDA` (word-boundary) = **0**, `bag of words` = 0, `perplexity` = 0, `plate notation` = 0, `archetype` = 15 (all descriptive prose — Narmour's P/R/I *archetypes* at 16754, loose "textural archetype" wording at 21959, "structural archetypes" at 6920 — no topic-model method). Adjacent-but-different: **086 HMM-C** (latent *chain*, memory-1 transition matrix — LDA has no transitions and is exchangeable), **085 NMF-C** (non-generative matrix factorization — no Dirichlet prior, no per-token latent assignment, no posterior predictive), **034 PCFG** (grammar recursion), **066 GTTM-HC** (rule-based hierarchy), **046 VAE-LSI / 118 D3PM** (deep generative models with continuous / denoising latents), **084 ZMRC** (rank–frequency, no latent structure), **105 PURC** (reinforcement, no corpus), **087 MVS-C** (hand-written multiple viewpoints). No DB method composes by *learning a mixture model over gesture tokens and sampling its posterior predictive*; LDATAC fills the **conjugate-Bayesian topic-model** gap.
- **Verified prototype for this document:** `_web140/verify_140_LDATAC.py`, log `_web140/verify_140_output.txt` — **11/11 checks pass** (numbers quoted throughout; MIDI `_web140/ldatac_140.mid`, 8983 B, `validate() == True`).

### Layer

**concrete** — LDATAC emits `MusicEvent`s that fill UnitMatrix cells: every token carries a pitch step, a tick duration and a velocity class, and every cell is filled to exactly `section_len` ticks (verified 32/32 cells). The *corpus* it learns from may live on the abstract layer (pitch-class sets, tension curves), and the section mixture $\theta_d$ doubles as an abstract-form object (its KL profile is the tension curve), but the method's primary artifact is a fully realized voice × section matrix — it feeds `generators/`, not `rules/subset_network.py`.

### Paradigm

**AI-Driven** — unsupervised statistical learning from a corpus: a probabilistic graphical model (plate notation: $K$ topics × $S$ documents × $N_d$ tokens) with Dirichlet priors, fitted by collapsed Gibbs sampling, then sampled. Nothing is rule-derived (contrast 066 GTTM-HC / 034 PCFG) and nothing is a physical process (contrast the Nature-Led family): the musical knowledge lives in the *learned parameters* $\hat\phi_k$, and the compositional act is a draw from a conjugate posterior predictive.

### Description

LDATAC composes the piece as a **topic model**: the corpus is the style, documents are **sections**, words are **gesture tokens**, and topics are **texture archetypes**. For each section $d$ a mixing proportion $\theta_d \sim \mathrm{Dir}(\alpha)$ says how much of each archetype the section contains; for each token position $n$, a topic $z_{dn} \sim \mathrm{Cat}(\theta_d)$ is drawn and the token itself from that archetype's distribution $w_{dn} \sim \mathrm{Cat}(\phi_{z_{dn}})$, $\phi_k \sim \mathrm{Dir}(\eta)$.

$$\theta_d \sim \mathrm{Dir}(\alpha),\qquad z_{dn}\mid\theta_d \sim \mathrm{Cat}(\theta_d),\qquad w_{dn}\mid z_{dn}{=}k \sim \mathrm{Cat}(\phi_k),\qquad \phi_k \sim \mathrm{Dir}(\eta)$$

The mathematical spine, as used here:

1. **Token definition.** A token is a notated gesture atom $w = (s, d, v)$: diatonic **step** $s \in \{-2,-1,0,+1,+2\}$, **duration** $d \in \{120,240,480\}$ ticks (16th / 8th / quarter at `ticks_per_beat=480`), **velocity class** $v \in \{64,100\}$ — $V = 30$ tokens in the verified demo. The vocabulary is the *instrument*; widen it (add articulation, ornament, register band) and the archetypes become richer but harder to identify (Pitfall 4). Because tokens hold **intervals**, $\phi_k$ is transposition-invariant — the key is chosen at realization, not learned — which is exactly why the model is key-agnostic and can be re-used across transpositions.
2. **Collapsed Gibbs sampler (Griffiths & Steyvers 2004).** With $\theta$ and $\phi$ integrated out, the only latent variables are the topic indicators; the update is

$$p(z_{dn}=k \mid z_{-dn}, w) \;\propto\; \big(n^{(d)}_k + \alpha_k\big)\,\frac{n^{(k)}_w + \eta_w}{n^{(k)} + \sum_{w'}\eta_{w'}}$$

   where $n^{(d)}_k$ counts tokens of document $d$ assigned to topic $k$, $n^{(k)}_w$ counts token $w$ assigned to topic $k$, and $n^{(k)}$ is the topic's total count. One sweep costs $\mathcal{O}(N K)$; the demo runs 300 sweeps at $K{=}3$, $S{=}48$ docs × 28 tokens in well under a second. Exact posterior inference is intractable in general (Blei 2003), so the sampler *is* the method.
3. **The composition rule is the posterior predictive.** After fitting,

$$\hat\theta_{dk} = \frac{n^{(d)}_k+\alpha_k}{n^{(d)}+K\alpha},\qquad \hat\phi_{kw} = \frac{n^{(k)}_w+\eta_w}{n^{(k)}+V\eta},\qquad p(w \mid d) = \sum_{k=1}^{K}\hat\theta_{dk}\,\hat\phi_{kw}$$

   This Dirichlet-compound-multinomial is the *generative* operator: to write a cell, draw $w \sim p(\cdot\mid d)$ repeatedly. No re-fitting, no decoding, no beam search — the model *is* the composer, which is what distinguishes LDATAC from 085 NMF-C (a factorization you must invert by hand) and from 086 HMM-C (a chain you must roll forward).
4. **Verification that the mixture is real.** Planted $K{=}3$ archetypes (ostinato / sustain / flourish as product distributions over step × duration × dynamics), 48 synthetic sections: recovered topics match the planted ones at cosine **0.991 / 0.994 / 0.998** (greedy 1-1 match), recovered per-section mixtures at mean cosine **0.994** (min 0.941), held-out perplexity **9.28** vs the uniform baseline **30.0**, and a held-out section's mixture is re-inferred from its tokens alone at cosine **0.995** (min 0.977). The model recovers the texture plan from the notes — so the notes can be generated *from* the plan.
5. **$\alpha$ is the section-purity dial; $\eta$ is the archetype-crispness dial.** $\alpha \ll 1$ makes each section nearly a single archetype (measured mean $\theta$ entropy **0.289 nats** at $\alpha{=}0.05$), $\alpha \approx 1$ mixes (0.551), $\alpha \gg 1$ smears every section toward the corpus mean (**0.943** of the maximum $\ln 3 = 1.099$ at $\alpha{=}8$). $\eta$ does the same to $\phi_k$: small $\eta$ → crisp, near-deterministic gestures; large $\eta$ → a uniform token gabble that sounds like nothing.
6. **Exchangeability is a theorem, and a compositional limitation.** LDA is a bag-of-words model: the likelihood of a cell is invariant under permutation of its tokens (de Finetti exchangeability — verified, $|\Delta \log p| = 0.0$ exactly). So the *retrograde of a cell has the same probability as the cell*. LDATAC therefore has **no opinion about order**: order must be supplied by the rhythm layer (e.g. 012 Euclidean groove locking assigns token slots) or by upgrading tokens to bigrams. Stated plainly rather than hidden — it is the method's defining trade: mixture structure for free, sequence structure not included.
7. **Tension curve from the simplex.** With $\bar\theta = \frac{1}{S}\sum_d \theta_d$,

$$D_d = \mathrm{KL}\big(\theta_d \,\|\, \bar\theta\big) = \sum_k \theta_{dk}\log\frac{\theta_{dk}}{\bar\theta_k}$$

   $D_d \approx 0$ = the section *is* the corpus mean (HOME); $\max_d D_d$ = the most idiomatic-archetype-dominated section (TENSE); moving to a *newly introduced* archetype mid-piece is LIFT; a section at an archetype the corpus never blends that way is TURN. The designed 8-section plan below spans **26×** in $D_d$ (0.029 → 0.765), i.e. a usable dynamic range.
8. **Voice identity without breaking the model.** A per-voice Dirichlet bias $\beta_v$ re-weights the section mixture per row: $p(z{=}k \mid d,v) \propto \theta_{dk}\beta_{vk}$, $\beta_v \sim \mathrm{Dir}(\delta_v)$. Bass gets $\beta \approx (0.8,0.2,0.0)$ over (ostinato, sustain, flourish), pad $(0.1,0.8,0.1)$, lead $(0.7,0.2,0.1)$ — the same section mixture rendered as four different *instrumental* readings. $\beta_v$ is the UnitMatrix row prior; without it every row of a column sounds like the same archetype mixture, i.e. four copies of one texture.
9. **Nonparametric option.** Fixing $K$ is the main structural commitment. The HDP (Teh 2006) replaces $\mathrm{Dir}(\alpha)$ with a CRP/CRF hierarchy, giving a Chinese-restaurant-franchise prior over archetypes and inferring $K$ — the composition analogue of "how many textures does this style actually have?", answered by the corpus.

### Musical Elements Framework

- **PITCH**: tokens carry *interval steps*, realized by cumulative summation along each voice's register ladder ($p_{n+1} = p_n + s_n$, clipped to $[36,88]$ in the demo — 1049 events generated without a single out-of-range pitch), then mapped through the key's scale at realization. $\phi_k$ is therefore transposition-invariant and the piece is key-agnostic; tonal gravity comes from the *corpus* (its archetypes encode which intervals that style actually uses) plus the realization-time scale map, not from a functional-harmony rule.
- **RHYTHM**: the duration coordinate of the token is the entire rhythmic surface. Local density follows the mixture: $\mathbb{E}[\text{tokens per section}] = L \big/ \sum_{k}\theta_{dk}\,\mathbb{E}[d\mid k]$, so a sustain-heavy section is automatically sparse (480-tick tokens) and a flourish-heavy one dense (120-tick). $\eta$ sets duration *variance* inside an archetype. Order within the cell is **not** modelled (Pitfall 1): slot the tokens with 012 Euclidean / 016 groove anchors if a groove is needed, otherwise accept a "gesture-cloud" rhythm.
- **HARMONY**: two routes. (a) *Textural harmony*: $\theta_d$ is the harmonic object — the section's interval-content is the mixture of archetype interval distributions, and $\mathrm{KL}$ drift is the harmonic tension curve. (b) *Functional harmony* (recommended for tonal styles): replace the interval-step coordinate with a **pitch-class-set degree** coordinate (token = (pc, dur, dyn) or (chord-tone index, dur, dyn)); $\phi_k$ then encodes which pcs that texture favours, and columns become chord-density-weighted pc-set aggregates, directly feedable to 113 PCFSC-style analysis. Column-to-column pc drift is the progression.
- **STRUCTURE**: the $\theta$ matrix *is* the form. $\alpha<1$ yields block form for free (nearly-pure sections, hard seams); $\alpha\approx1$ yields through-composed morphing; an HDP with growing $K$ yields a form that introduces new archetypes as it proceeds. Section ordering is unconstrained by the model — deliberately, since form order is a composer decision, not a statistical one.
- **TEXTURE**: the method's namesake and strongest axis. A section's texture is a *point on the simplex*, so texture changes are continuous: sliding $\theta_d$ from $(0.8,0.2,0)$ to $(0,0.2,0.8)$ over four sections crossfades ostinato → flourish while the corpus keeps every intermediate blend idiomatic. $\beta_v$ spreads the blend across rows (bass on the ostinato pole, pad on the sustain pole), which is precisely the "one texture, four functions" arrangement gesture.

### UnitMatrix Integration (Voices & Sections)

**Voices = rows.** Row $v$ is governed by two row-constant objects: the register ladder (pitch realization) and the archetype bias $\beta_v$. The row is therefore a *style-filtered reading* of the column's mixture — row identity is "which archetypes this instrument is allowed to speak", not a melodic line. Verified mapping: Lead $(0.7,0.2,0.1)$, Pad $(0.1,0.8,0.1)$, Bass $(0.8,0.2,0.0)$, Counter $(0.3,0.3,0.4)$.

**Sections = columns.** Column $d$ is one *document*: its $\theta_d$ (8 sections, hand-set plan in the demo, or inferred from a reference corpus) fixes the column's archetype mixture, hence its density, dynamic profile and interval content. Because every column lives on the same simplex, column similarity is $\mathrm{KL}$ — the tension curve $D_d = \mathrm{KL}(\theta_d\|\bar\theta)$ is read straight off the columns (verified $0.029 \to 0.765$, 26× spread).

**Cells = MusicUnit.** Cell $(v,d)$ is a token run: draw $z \sim \mathrm{Cat}(\theta_d \circ \beta_v)$, then $w \sim \mathrm{Cat}(\phi_z)$, then advance the clock by the token's duration **clamped to the cell end**:

$$t_0 = 0,\qquad t_{n+1} = t_n + \min(d_n,\; L - t_n),\qquad \text{stop when } t_n = L$$

   which makes $t_N = L$ exactly — zero drift **by construction**, no padding step (verified: 32/32 cells end at 7680 ticks for 4 bars at tpb 480). Each token becomes `MusicEvent(pitch=p_n, volume=v_n, start_tick=t_n, end_tick=t_{n+1})`; the unit goes through `fill_voice_section` → `validate()` → `to_midi()` on the standard spine. Verified end-to-end: 4 voices × 8 sections × 4 bars, **1049 events**, `validate() == True`, MIDI **8983 B** (`_web140/ldatac_140.mid`).

**Candidate code path:** `generators/lda_topics.py` (new concrete generator, sibling of `generators/markov_constraint.py`) — `GestureVocabulary(steps, durs, dyns)` (token ↔ tuple bijection, `V` known), `ArchetypeModel.fit(corpus_tokens, K, alpha, eta, iters, seed)` (collapsed Gibbs → $\hat\theta$, $\hat\phi$), `.canonicalize()` (sort topics by mean duration so labels are seed-stable), `.posterior_predictive(voice_beta)` (the $p(w|d)$ mixture), `.sample_cell(theta_d, beta_v, section_len, rng)` (duration-clamped token run → `MusicUnit`), `.tension_curve()` ($D_d$ and argmin/argmax). Optional analysis front-end to *build* the corpus from MIDI: `analysis/tokenize.py` (interval/step + duration + velocity quantization). Cost: fit $\mathcal{O}(I N K)$, generation $\mathcal{O}(N K)$, memory $\mathcal{O}(K V + S K)$.

### Pitfalls

1. **The bag has no order — and the model knows it.** Exchangeability is exact ($|\Delta\log p| = 0.0$ measured), so a cell, its retrograde and any permutation are *the same object* to LDATAC. If the result sounds like a shuffled gesture cloud, that is the method working as specified, not a bug: assign slots from a rhythm layer (012 Euclidean, 016 groove anchors) or promote tokens to bigrams/trigrams (bigram-LDA) when directed motion is required.
2. **Short documents make $\theta$ meaningless.** A 4-event cell has a posterior for $\theta$ so wide that the "mixture" is just the prior. Keep documents at section scale (≥ $8$ sections, ≥ 20 tokens each, as in the verified 48×28 corpus), or share $\theta$ across a phrase (hierarchical / HMM-LDA) instead of per-cell.
3. **Label switching breaks reproducibility of *names*.** The likelihood is invariant under permutation of topics, so "archetype 2" can be sustain in one seed and flourish in the next while the music is identical. Canonicalize (sort by mean duration, then by entropy) before writing any per-topic automation.
4. **$\alpha$ and $\eta$ extremes both destroy the piece.** $\alpha{=}0.05$ → each section is one archetype (entropy 0.29 nats: blocky, no blends); $\alpha{=}8$ → every section ≈ corpus mean (0.94 of $\ln 3$: oatmeal, tension curve flat). Large $\eta$ flattens $\phi_k$ into uniform gabble. Tune $\alpha\in[0.1,1]$, $\eta\approx 10^{-2}/V$ as a starting point and *measure* the $\theta$ entropy and the $D_d$ spread before composing.
5. **Homogeneous corpus = no form.** If the corpus has one style, all $\theta_d \approx \bar\theta$, $D_d \approx 0$, and the tension curve disappears (the reason the demo uses an explicitly designed 8-point $\theta$ plan rather than a fit for the form). Check $\max_d D_d / \min_d D_d$ — under ~2 means "no form".
6. **Corpus mismatch is silent.** $\phi_k$ can only express gestures present in the corpus' vocabulary; asking for a metal section from a chorale corpus yields chorale-shaped gestures with a loud velocity column, and the model reports nothing wrong. Fix: broaden the tokenizer or use the HDP with a mixed corpus; do not "fix" it by raising $\alpha$.
7. **Clamp last, clamp once.** The duration clamp must be applied at *draw* time ($\min(d_n, L-t_n)$) — clamping the assembled unit afterwards, or trimming overflow events, leaves the cell short and the matrix drifts. Verified: 32/32 cells exact after six sections of running out of room.
8. **Do not mistake it for its neighbours.** 085 NMF-C factorizes a matrix and has no probabilistic sampling and no per-token latent assignment (you must invert it); 086 HMM-C has a transition matrix and therefore memory-1 *sequential* structure (LDATAC has no transitions at all); 034 PCFG generates by grammar recursion (syntax, no corpus statistics); 066 GTTM-HC applies rules; 046 VAE-LSI / 118 D3PM learn deep continuous/denoising latents and need gradients. LDATAC's distinguishing content is exactly the conjugate closed form: **the composition operator is $p(w|d)=\sum_k\hat\theta_{dk}\hat\phi_{kw}$, and the control surface is a simplex.**
