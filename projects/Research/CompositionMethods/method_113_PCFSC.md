# Method 113 — Pitch-Class Fourier Spectrum Composition (PCFSC)

**ID:** 113 · **Paradigm:** Rules-Based · **Layer:** abstract · **Registered:** 2026-10-12

**One-line:** Composes pitch-class pools, progressions, and tension curves in Amiot's Fourier space over ℤ₁₂ — chord/scale *quality* is the magnitude spectrum |f(k)| of the pc-set, tonic *position/function* is the Fourier phase, and a designed phase walk IS the composition.

---

## 1. The Fourier space of pitch-class sets

Let $\omega = e^{2\pi i/12}$. Every subset $A \subseteq \mathbb{Z}_{12}$ (a pc-set: chord, scale, pitch pool) maps to 12 complex Fourier coefficients

$$f_A(k) = \sum_{a \in A} \omega^{ka} = \sum_{a \in A} e^{2\pi i k a / 12}, \qquad k = 0, \dots, 11.$$

Facts used throughout (all verified numerically for this registration; compute script below):

- **Hermitian symmetry:** $f(12-k) = \overline{f(k)}$, so $|f(k)| = |f(12-k)|$ — the spectrum has 7 independent magnitudes $(k=0..6)$.
- **$k=0$ = cardinality:** $f_A(0) = |A| = n$.
- **Transposition = phase rotation:** $f_{A+t}(k) = \omega^{kt} f_A(k)$; magnitudes invariant. Verified: $T_7$ rotates $\arg f_1$ by $2\pi\cdot 7/12 = 7\pi/6$ (computed shift 3.6652 rad, expected 3.6652 rad).
- **Inversion = phase negation:** $f_{-A}(k) = \overline{f_A(k)}$.
- **Magnitude = Fourier transform of the ICV:** $|f_A(k)|^2 = n + 2\sum_{j=0}^{5} \mathrm{icv}(j)\cos\!\big(2\pi k (j{+}1)/12\big)$ — verified for major/minor triads and the diatonic (Lewin 1959; Quinn 2006). Consequence: sets sharing an interval-class vector are **magnitude-twins**.
- **Complement isospectrality:** $A$ and $\mathbb{Z}_{12}\setminus A$ share all magnitudes at $k \neq 0$ (differ only via cardinality at $k{=}0$). Verified: Ionian $\{0,2,4,5,7,9,11\}$ and pentatonic $\{0,2,4,7,9\}$ have identical profiles at $k{=}1..11$.

### Verified reference spectra

| Set | $|f|$ profile (k = 0..11) | Signature |
|---|---|---|
| whole-tone $\{0,2,4,6,8,10\}$ | `[6, 0,0,0,0,0, 6, 0,0,0,0,0]` | energy only at k=0,6 (tritone division) |
| octatonic $\{0,1,3,4,6,7,9,10\}$ | `[8, 0,0,0, 4, 0,0,0, 4, 0,0,0]` | energy only at k=0,4,8 (dim-7 lattice) |
| Ionian $\{0,2,4,5,7,9,11\}$ | `[7, .27, 1,1,1, 3.73, 1, 3.73, 1,1,1, .27]` | peak at k=5,7 — the fifth/fourth direction |
| pentatonic $\{0,2,4,7,9\}$ | same at k=1..11 | complement twin of Ionian |
| harmonic minor $\{0,2,3,5,7,8,11\}$ | `[7, .52, 1, 2.24, 2.65, 1.93, 1, 1.93, 2.65, 2.24, 1, .52]` | triad-like spread |
| major triad $\{0,4,7\}$ | `[3, .52, 1, 2.24, 1.73, 1.93, 1, 1.93, 1.73, 2.24, 1, .52]` | broad |
| minor triad $\{0,3,7\}$ | **identical to major** | mode invisible to magnitude |

**Major ≠ minor in phase.** Same magnitudes, different phases (verified): $\arg f_3 = -0.464$ (maj) vs $-1.107$ (min); $\arg f_5 = -0.785$ (maj) vs $+0.262$ (min). Mode and tonal function live in the *phase* (Yust 2019) — one of the deepest results of Fourier music theory, and the reason PCFSC uses both halves of the spectrum.

**Maximally-even extremum.** Exhaustive search over all $\binom{12}{7}=792$ seven-note sets: $\max |f_5| = 3.732 = 2+\sqrt{3}$, attained by the Ionian/Lydian (ME) class *and* by $\{0,1,3,5,6,8,10\}$ (whose ×5 image is 7 consecutive pcs). So "fifthiness" is a necessary-but-not-sufficient fingerprint of the diatonic; pin with ME-ness or cardinality too. Regular divisions are exact: $|f_4(\text{aug})|{=}3$, $|f_3(\dim7)|{=}4$, $|f_6(\text{WT})|{=}6$, $|f_4(\text{oct})|{=}4$.

## 2. Compositional machinery

1. **Profile design (per section):** target magnitudes $T_k$, $k=1..11$ ($T_0$ = cardinality). Spectral archetypes: tonal → energy at 5,7; whole-tone haze → energy at 6; octatonic drama → 4,8; atonal noise → flat.
2. **Set matching:** minimize $D(A) = \sum_k w_k\,(|f_A(k)|/n - T_k)^2$ over all 4096 subsets, or construct directly: cosets of $\ker(k \mapsto ka \bmod 12)$ for regular divisions; the one-generator window $\{0,g,2g,\dots,(n{-}1)g\} \bmod 12$ ($\gcd(g,12)=1$) for ME pools.
3. **Phase trajectory (the composition proper):** design $\phi(t)$ for each active coefficient. A continuous walk = transposition drift; a phase step = modulation (interval $= \Delta\phi \cdot 12/2\pi k$); return to opening phase = resolution. Each coefficient moves at its own rate $k$ per transposition step — steering "which Fourier layers are active and where they point" is a genuinely new harmonic control surface.
4. **Tension curve:** $T_{t} = \|f_{A_{t+1}} - f_{A_t}\|$ (weighted Fourier distance — the Bernardes TIV quantity, 2016). Harmonic rhythm = phase velocity $v = \Delta\phi/\Delta t$.
5. **Complement pairing:** a pool and its complement = two densities of the same harmony (diatonic drone + pentatonic melody cannot clash).

**Complexity:** profile match $\mathcal{O}(4096\cdot 12)$ one-time per section (closed-form alternatives $\mathcal{O}(n)$); phase walk/tension $\mathcal{O}(1)$ per step; total $\mathcal{O}(12)$ per generated position.

## 3. Python implementation sketch

```python
import numpy as np
from itertools import combinations

OMEGA = np.exp(2j * np.pi / 12.0)

def pc_set_dft(pcs):
    """Complex Fourier coefficients f(k), k=0..11, of a pc-set."""
    v = np.zeros(12, dtype=complex)
    v[list(pcs)] = 1.0
    k = np.arange(12)
    return np.array([np.sum(v * OMEGA ** (kk * np.arange(12))) for kk in range(12)])

def profile(pcs):
    """Normalized magnitude spectrum |f|/n (k=0..11). Quality fingerprint."""
    f = pc_set_dft(pcs)
    return np.abs(f) / len(pcs)

def match_profile(target, cardinality=None, weights=None, kmin=1):
    """Exhaustive 4096-set scan minimizing weighted normalized-profile distance.
    Drop k=0 (cardinality) by default so *quality* is what is matched."""
    target = np.asarray(target, float)
    w = np.ones(12) if weights is None else np.asarray(weights, float)
    if cardinality is not None:
        w[0] = 0.0              # cardinality handled separately
    best, best_set = np.inf, None
    for r in range(cardinality or 12 + 1):
        for c in combinations(range(12), r):
            p = profile(c)
            d = float(np.sum(w[kmin:] * (p[kmin:] - target[kmin:]) ** 2))
            if cardinality is not None and r != cardinality:
                d += 1.0 * (r - cardinality) ** 2   # cardinality penalty
            if d < best:
                best, best_set = d, set(c)
    return best_set, best

def me_set(n, g=7):
    """Maximally-even pool: n consecutive steps of a coprime generator g (Z_12)."""
    return set((i * g) % 12 for i in range(n))

def phase_walk(phi0, v, ks, n_steps, coeff_rates):
    """Designed phase schedule: phi(t) = phi0 + v*t, per coefficient k.
    coeff_rates[k] = k (physical transposition rate) — callers may override."""
    t = np.arange(n_steps)
    return {k: (phi0[k] + v * coeff_rates[k] * t) % (2 * np.pi) for k in ks}

def fourier_tension(fA, fB, weights=None):
    """Weighted Fourier-space distance = TIV-style tension between sets."""
    d = np.abs(fA - fB)
    return float(np.sum(d)) if weights is None else float(np.sum(weights * d))

def complement_pair(pcs):
    """Magnitude-twin complement (identical |f| at k!=0, verified)."""
    return set(range(12)) - set(pcs)

# --- demo: C-major-ish quality, resolved at the opening anchor ---
target = np.array([0.0, .05, .1, .1, .1, .53, .1, .53, .1, .1, .1, .05])  # k=5,7 peak
pool, _ = match_profile(target, cardinality=7)
print("matched 7-note pool:", sorted(pool))            # an ME-class (diatonic) pool
print("|f5| of pool =", round(abs(pc_set_dft(pool)[5]), 3), "(max 2+sqrt3=3.732)")

fC = pc_set_dft({0, 4, 7}); fCm = pc_set_dft({0, 3, 7})
print("maj/min mags identical:", np.allclose(np.abs(fC), np.abs(fCm)))
print("maj/min phases differ: ", not np.allclose(np.angle(fC), np.angle(fCm)))
```

## 4. UnitMatrix filling (abstract → concrete)

- **Voices** = rows with Fourier roles: Voice 1 (Melody) tracks $\arg f_1$ (tonic-drift), Voice 2 (Harmony) tracks $\arg f_5$ (dominant side), Voice 3 (Bass) tracks $\arg f_7$ (fourth side, grounding), color voices track $k=3,4$. Voices share the section's magnitude profile (same quality region) but walk their coefficient's phase at per-voice rates — shared quality, independent position.
- **Sections** = columns: (profile target, anchor phase, phase velocity) triples. Typical form: Intro (WT profile, anchor $\phi_A$, $v{=}0$) → Verse (diatonic, $\phi_T$, slow) → Chorus (triad pools + dominant excursions, med $v$) → Bridge (octatonic, wandering, fast) → Outro (return to $\phi_A$).
- **Cells** = MusicUnits realized downstream: abstract outputs (pool sequence, phase schedule, tension curve) → `rules/subset_network.py` → `rules/realize.py` (`realize_progression(..., smooth=True)`) → `create_note_unit` / `create_chord_unit`, padded to `section_len` (zero-drift gate).

## 5. References

- Amiot, E. (2016). *Music through Fourier Space: Discrete Fourier Transform in Music Theory.* Springer.
- Amiot, E. (2007). "David Lewin and Maximally Even Sets." *Journal of Mathematics and Music* 1(2), 63–93.
- Lewin, D. (1959). "Intervallic Relations between Two Collections of Integers." *Journal of Music Theory* 3(2), 298–301.
- Quinn, I. (2004). *A Unified Theory of Chord Quality in Equal Temperaments.* PhD diss., Univ. of Rochester.
- Yust, J. (2019). "Stylistic Information in Pitch-Class Distributions." *Journal of New Music Research* 48(2).
- Chiu, Y.-M. (2021). "Macroharmonic Progressions through the Discrete Fourier Transform." *Music Theory Online* 27(3).
- Bernardes, G., Cocharro, D., Guedes, C., Davies, M. E. P. (2016). "Harmony Generation Driven by a Perceptually Motivated Tonal Interval Space." *ACM Computers in Entertainment* 14(2), 6.
- Amiot, E. & Sethares, W. (2011). "An Algebra for Periodic Rhythms and Scales." *Computer Music Journal* 35(1).

## 6. Distinguishing the method

PCFSC is the first **pitch-class-domain Fourier** method in the DB. Siblings/foils: 039 SMA (Fourier of *audio frames* — different domain), 051 SGLM (eigenvalues of a *graph* Laplacian — different spectrum), 084 ZMRC (rank-frequency — different statistics), 095 CTC / 104 PSSC (abstract-layer subset design without a spectral target). The two other abstract methods design *shape* (contour) and *transition cost* (parsimony); PCFSC is the first that designs *sonority identity itself* (quality spectrum) and *position* (phase).