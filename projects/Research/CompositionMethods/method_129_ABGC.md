# Method 129 — Artin Braid Group Composition (ABGC)

- **Paradigm**: Rules-Based
- **Layer**: concrete (emits `MusicEvent`s that fill UnitMatrix cells)
- **Module**: `generators/braid_group.py`, class `BraidComposer`
- **DB section**: `methods_db.md` → `# Artin Braid Group Composition (ABGC) (Method 129)`

Treats the $n$ rows of a UnitMatrix as the $n$ strands of an Artin braid; a section is a
word in $B_n$; a syllable is one adjacent transposition of two voices' registral
positions, i.e. one *Stimmtausch* (voice exchange).

---

## 1. The algebraic object

$$B_n=\Big\langle \sigma_1,\dots,\sigma_{n-1}\ \Big|\ \sigma_i\sigma_j=\sigma_j\sigma_i\ \ (|i-j|\ge 2),\qquad \sigma_i\sigma_{i+1}\sigma_i=\sigma_{i+1}\sigma_i\sigma_{i+1}\Big\rangle$$

Two relations, nothing else. $\sigma_i$ crosses strand $i$ over strand $i+1$;
$\sigma_i^{-1}$ crosses under. Verified numerically 2026-10-30:

| law | test | result |
|---|---|---|
| braid relation | $\sigma_1\sigma_2\sigma_1$ vs $\sigma_2\sigma_1\sigma_2$ at $n=3$ | identical permutation `[2,1,0]`, equal writhe 3 ✓ |
| far commutativity | $\sigma_1\sigma_3$ vs $\sigma_3\sigma_1$ at $n=4$ | identical `[1,0,3,2]` ✓ |

Key structural facts used compositionally:

1. **$B_n \twoheadrightarrow S_n$** — forgetting winding gives the permutation. The map has
   infinite kernel ($\sigma_i$ has infinite order; $\sigma_i^2 \ne e$). *The permutation is a
   lossy shadow*: it is exactly what change ringing (method 089) keeps and what a braid
   refuses to forget.
2. **Half-twist (Garside)**: $\Delta_n=\sigma_1\cdots\sigma_{n-1}\;\sigma_1\cdots\sigma_{n-2}\;\cdots\;\sigma_1$,
   $|\Delta_n|=n(n-1)/2$, realizes the reversal permutation $k\mapsto n-1-k$. Verified $n=2..7$
   with lengths 1,3,6,10,15,21.
3. **Garside normal form**: every braid $= \Delta_n^{p}\,A_1A_2\cdots A_k$ with $A_i$ simple
   (divisors of $\Delta$). $p$ = infimum = global registral displacement; the $A_i$ = phrase-scale
   exchange blocks.
4. **Closure components**: closing the braid (join top to bottom) gives a link whose component
   count $c$ = number of cycles of the final permutation. Measured: $c(\Delta_n)=\lceil n/2\rceil$
   (1,2,2,3,3,4 for $n=2..7$); $c(\text{id})=c(\Delta_n^2)=n$.
5. **Markov moves** (conjugation $+$ stabilization) generate link equivalence ⇒ *form equivalence*
   up to section rotation and voice addition.
6. **Dehornoy order**: $B_n$ is left-orderable via handle reduction ⇒ a total order on words,
   hence a canonical "which section is higher/louder" ranking and a unique normal form.
7. **Burau representation** $\rho_n:B_n\to GL_{n-1}(\mathbb Z[t^{\pm1}])$; the Alexander polynomial
   of the closure is read from $\det(\rho_n(\beta)-I_{n-1})$ up to units and a cyclotomic factor
   (Birman 1974, Thm 3.11). A form fingerprint, not a generator.

## 2. Musical mapping

State: `perm[k]` = strand sitting at vertical position $k$. One syllable:

```python
perm[i-1], perm[i] = perm[i], perm[i-1]
```

- **Pitch follows POSITION, identity follows STRAND.** Position $k$ has ladder value $L(k)$;
  the row is the strand. A crossing therefore exchanges two notes between two voices at one
  onset — voice exchange. Registral order is monotone *by construction*: voice crossing is
  impossible, and no well-formedness repair is ever needed.
- **Vertical slice = complete chord.** Every position is always occupied ⇒ all $n$ voices
  sound at every syllable; with per-strand offsets $\delta_s$ the slice is
  $\{L(k)+\delta_{\mathrm{perm}(k)}\}$: the pc multiset is invariant, its registration permutes.
  Result: static pitch-class content under continuous contrapuntal motion (the signature).
- **Writhe** $w(\beta)=\sum_k e_k$ = tension/brightness curve.
- **Closure components** $c$ = number of cyclic voice orbits: $c=1$ ⇒ whole piece is one canon;
  $c=n$ ⇒ through-composed.
- **$\Delta_n^p$** = $n(n-1)/2$ crossings that reverse the entire voicing = cadential /
  registral-reset gesture; $p$ = section-level register shift.

## 3. Complexity

| operation | cost |
|---|---|
| emit one syllable (one swap + $n$ events) | $\mathcal O(n)$ per syllable, $\mathcal O(1)$ amortized per event |
| generate a word of length $L$ | $\mathcal O(L)$ |
| closure components | $\mathcal O(n)$ |
| Garside normal form | $\mathcal O(L^2)$ (practical) |
| handle reduction (Dehornoy) | worst case $\mathcal O(L^2)$ elementary steps |
| Burau / Alexander of closure | $\mathcal O(L\, n^3)$ on Laurent polys (analysis only) |

Surface vocabulary: a random adjacent-transposition walk visits **all** $n!$ permutations
(verified 6/6, 24/24, 120/120 for $n=3,4,5$ over 20 000 syllables) — full symmetric-group
variety on the surface, non-abelian memory underneath.

## 4. Python implementation sketch

```python
from structures import MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.musicom_workflow import _unit_from_events

def word_delta(n):
    return [(i, +1) for k in range(n - 1, 0, -1) for i in range(1, k + 1)]

def emit(word, ladder, delta, t0, syl):
    perm = list(range(len(ladder)))
    rows = [[] for _ in ladder]
    for t, (i, e) in enumerate(word):
        start = t0 + t * syl
        cross = {perm[i - 1], perm[i]}
        perm[i - 1], perm[i] = perm[i], perm[i - 1]
        for pos, strand in enumerate(perm):
            vel = 96 if (strand in cross and e > 0) else (82 if strand in cross else 70)
            rows[strand].append(MusicEvent(pitch=ladder[pos] + delta[strand],
                                           volume=vel, start_tick=start,
                                           end_tick=start + syl))
    return rows           # one list of events per UnitMatrix row

# composer.create_matrix / add_voice / add_section, then per cell:
# composer.fill_voice_section(f"Strand{v}", name, _unit_from_events(rows[v], SEC_LEN))
# ok, msg = composer.validate()  -> must be True ; to_midi(path)
```

Reference render: `abgc_129_compose.py` → 4 strands × 4 sections × 4 bars, bpm 96, ladder
G3–C4–E4–G4, `STRING_ENSEMBLE`; `validate()` True, MIDI 2413 bytes,
`projects/Research/outputs/abgc_129/abgc_129.mid`.

## 5. Selection heuristics

| want | do |
|---|---|
| rising tension | sign bias $+\varepsilon$ on the walk (writhe grows) |
| plateau | sign-symmetric walk (writhe ≈ 0) |
| cadence / reset | insert $\Delta_n$ |
| canon / round | force a single $n$-cycle final permutation ($c=1$) |
| through-composed | sign-symmetric walk, $c=n$, fresh seeds per column |
| trill / measured tremolo | $\sigma_i^{k}$ with $k\gg1$ |
| duet texture | restrict the word to one generator index |
| canonical re-orchestration | handle-reduce first, then emit |

## 6. References

- Artin, E. (1925/1947). *Theorie der Zöpfe*; *Theory of braids*, Ann. of Math. 48(1):101–126.
- Garside, F. A. (1969). *The braid group and other groups*, Quart. J. Math. 20:235–254.
- Birman, J. S. (1974). *Braids, Links, and Mapping Class Groups*, Ann. Math. Studies 82.
- Burau, W. (1935). *Über Zopfgruppen und gleichsinnig verdrillte Verkettungen*, Abh. Math. Sem. Hamburg 11:179–186.
- Dehornoy, P. (1997). *A fast method for comparing braids*, Adv. Math. 125:200–235.
- Dehornoy, Dynnikov, Rolfsen, Wiest (2003). *Why Are Braids Orderable?*, SMF.
- Kassel & Turaev (2008). *Braid Groups*, GTM 247, Springer.
- Counterpoint: *Stimmtausch* / voice exchange, standard species-counterpoint vocabulary (cf. method 056 SCCC).

## 7. Pitfalls (short form)

1. Reducing mod permutation downgrades ABGC to 089 CRCM — store the **word**.
2. $\delta_s=0$ everywhere ⇒ invariant pc-set ⇒ risk of "nothing happening"; vary ladder/$\delta$ per section.
3. Section length must equal $|W_j|\times$ syllable ticks, else zero-drift/`validate()` failure.
4. $\Delta_n$ costs $n(n-1)/2$ syllables — budget it.
5. $c$ is a form decision determined by the final permutation; check it before claiming canon.
6. Sign convention ($\sigma_i$ = louder) must be recorded in provenance.
7. Burau/Alexander is post-hoc analysis, not a real-time generator.
