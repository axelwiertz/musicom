# Report — Method 086: Hidden Markov Model Latent-State Composition (HMM-C)

## Summary
- **Method name**: Hidden Markov Model Latent-State Composition
- **Acronym**: HMM-C
- **ID**: 086 (dynamically resolved: max existing algorithmic ID = 085 NMF-C → 086)
- **Paradigm**: Stochastic
- **LAYER**: **concrete** (emits note/chord events into UnitMatrix cells via sampling/Viterbi-decoding an emission from a hidden state; feeds `generators/`)
- **One-line description**: Generates music as the emission from a hidden Markov chain — latent states are tonal functions/chord regions/sections, observed tokens are pitch classes, rhythmic cells, and velocity levels. The transition matrix $A$ encodes the harmonic grammar (state→state movement = chord progression), the emission matrix $B$ encodes the surface vocabulary, and the initial distribution $\pi$ seeds the piece. Composition = sample or Viterbi-decode the hidden state path (forced per section), then emit from $B$; Baum–Welch (EM) learns $A$ and $B$ from a corpus.

## ID resolution
- Scanned the summary table (`| **NNN** |` rows) at top of `methods_db.md`. Highest numeric algorithmic ID: **085** (Non-negative Matrix Factorization Composition, NMF-C), at table row line 95.
- Cross-checked standalone `method_*.md` files: `method_085_NMFC.md` highest. (Historical gap: 058 NODE-CTC still unregistered — pre-existing, not touched.)
- Cross-checked `report_*.md` files: `report_085.md` confirmed max = 085.
- Next ID = **086**. Collision-free: grep for hidden markov / HMM / Baum–Welch / Viterbi / forward-backward / Kalman / linear-dynamical surfaced NO existing HMM composition method. (The only "Viterbi" hits were SP-044 Concatenative Sound Synthesis and SP-053 VBAP, both absolute-layer DSP/synthesis, not composition; the only "state-space" hit was 060 S4SC, a deep continuous model, not a discrete latent HMM.)

## Classification details
| Field | Value |
|---|---|
| Method ID | 086 |
| Layer | concrete |
| Method Name | Hidden Markov Model Latent-State Composition (HMM-C) |
| Paradigm | Stochastic |
| Primary Elements | Pitch, Rhythm, Harmony, Structure, Texture |
| Tonal Gravity | Strong (Functional-grammar) |
| Metric Binding | Grid-Locked / Continuous |
| Memory Depth | Meso / Hidden Chain |
| Time Complexity | $\mathcal{O}(I \cdot T \cdot S^2)$ train, $\mathcal{O}(T \cdot S^2)$ Viterbi |

## Summary-table row (inserted at line 96, after 085, before the Sound Production header)
```
| **086** | concrete | Hidden Markov Model Latent-State Composition (HMM-C) | **Stochastic** | Pitch, Rhythm, Harmony, Structure, Texture | Strong (Functional-grammar) | Grid-Locked / Continuous | Meso / Hidden Chain | $\mathcal{O}(I \cdot T \cdot S^2)$ train, $\mathcal{O}(T \cdot S^2)$ Viterbi | Generates music as the emission of a hidden Markov chain: latent states are tonal functions/chord regions/sections, emissions are pitch classes, rhythmic cells, and velocity levels. Transition matrix $A$ = harmonic grammar (state→state = chord progression), emission matrix $B$ = surface vocabulary, initial $\pi$ = opening. Composition = sample or Viterbi-decode the hidden path (forced per section), then emit; Baum–Welch (EM) learns $A,B$ from a corpus. Latent-state generalization of 002 Markov; discrete-state ancestor of 059 ESN-RC / 060 S4SC; hidden-variable counterpart to 064 MRFCC's spatial lattice. |
```

## Line counts
- **Before (append)**: 17348 lines
- **After (detail-section append via `cat >>`)**: 17446 lines (+98)
- **After (summary row via patch)**: 17447 lines (+1)
- **Delta**: +99 lines total

## Files
- **Standalone file**: `/opt/data/repos/musicom/projects/Research/CompositionMethods/method_086_HMM-C.md`
- **Report file**: `/opt/data/repos/musicom/projects/Research/CompositionMethods/report_086.md`
- **DB**: `/opt/data/repos/musicom/projects/Research/CompositionMethods/methods_db.md` (summary row at line 96 + full section at line 17350)
- **Temp file**: `_temp_method_086.md` written, appended, and removed (per workflow).

## Candidate code path
- **Module**: `generators/hmm_composition.py` (new, alongside existing generator modules).
- **Public API sketch**: `class HMMComposer` with `n_states`, `n_symbols`, `seed`; methods `set_functional_prior(self_loop, off)` (hand-seed a HOME→LIFT→TENSE→TURN functional grammar), `sample_path(T, allowed)` (sample a hidden state path with per-t section forcing), `emit(q)` (sample emissions), `forward_backward(obs)` (log-domain inference), `baum_welch(obs, n_iter)` (EM training), `viterbi(obs)` (best-path decode). All log-space to avoid underflow; deterministic per seed.
- **Abstract-layer note**: the hidden-state path is an abstract-layer object (a tension/function curve over HOME/LIFT/TENSE/TURN that could seed `rules/subset_network.py` ABS-001/002), but as documented the method realizes events, so it is concrete.

## Complete method section text appended
Headers: ### Source, ### Layer, ### Description, ### Technical Mechanics, ### Musical Elements Framework, ### UnitMatrix Integration (Voices & Sections), ### Pitfalls, ### Comparison With Related Methods, ### References. (Identical to the content that was in `_temp_method_086.md`, now folded into `methods_db.md` at line 17350 and expanded with a Python sketch + references in `method_086_HMM-C.md`.)

## Quirks / pitfalls hit
1. **Table row placement**: the composition-method summary table ends at line 95 (`085`), immediately followed by `# Sound Production Methods Framework`. The new `086` row was inserted via `patch` (replace of the `085` row + following header), not appended — appending would have landed the row inside the Sound Production section. Verified at line 96.
2. **LaTeX escape check**: re-read line 96 after patching — single backslashes `$\mathcal{O}(I \cdot T \cdot S^2)$`, `$\pi$`. Grep for `\\mathcal`, `\\pi`, `\\approx` returned **0 matches** (no double-escape). Clean.
3. **`||` prefix check**: grep for `^|| **086` returned **0 matches**; new row starts with single `|`. Clean.
4. **`_warning` on patch**: the patch tool warned the file was "modified since last read" — this is the expected `cat >>` append from step 5b, not an external editor. Re-read line 96 after patching to confirm the row landed correctly.
5. **Paradigm placement rationale**: classified **Stochastic** (probabilistic latent-state generative model) rather than AI-Driven. The DB tags 059 ESN-RC (untrained reservoir) as Nature-Led and 060 S4SC / 054 ATS (gradient-trained deep nets) as AI-Driven; Baum–Welch EM is a classical maximum-likelihood fit, not deep learning, so HMM-C sits with the classical stochastic family (002 Markov, 045 Hawkes, 061 GPC, 068 CME-SSA). Consistent with the "stochastic = probabilistic generative process" convention.
6. **Gap exploited**: DB has *observed*-state sequence models (002 Markov), *point-process* models (045 Hawkes, 068 CME-SSA), *continuous* state models (059 ESN-RC, 060 S4SC, 061 GPC), and *spatial* latent models (064 MRFCC) — but **no discrete hidden-state sequential model**. HMM-C fills the "latent-state generative grammar" gap, and is the interpretable ancestor of the deep sequence family (the same A/B/π object chord-recognizers fit is here sampled from to compose). It directly extends the classical HMM-in-music lineage (Ponsford–Wiggins–Mellish 1999, Raphael 2002, Sheh–Ellis 2003, Allan–Williams 2005).
7. **grep exit-code note**: `grep -c` returns exit code 1 when the count is 0, which broke a `&&`-chained verification command mid-way. Re-ran the remaining checks separately (all clean). No data impact.

## Next free ID
**087**
