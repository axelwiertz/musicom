# Method 146 — Hindemith Harmonic Fluctuation Composition (HHFC)

- **ID:** 146
- **Paradigm:** Rules-Based (fully deterministic: published classification tables, root rule, progression-value table, tonal-centre and cadence rules; no stochastic element at all — the only "variation" is the composer's plan choice, seeded like 144/145).
- **Layer:** abstract (LAYER_ARCHITECTURE.md) — chord-group sequence (tension ladder I–VI), root-progression plan (Stufengang), the **harmonic fluctuation** tension curve (Kraftverlauf), tonal-centre and cadence schedules; all register-invariant and tick-free, no concrete events. Feeds `rules/subset_network.py` via new `rules/hindemith_harmony.py`; concrete adapter `generators/hindemith_harmony.py`.
- **One-liner:** compose the harmonic plan from Hindemith's *Craft of Musical Composition* I (1937/1942) — every chord classified into groups I–VI by interval content, root progressions scored by the published value table (P5/P4 = +2 … tritone = −3), the running sum of which is the **harmonic fluctuation** tension curve; tonal centres form by the 3-chord rule (2 with tritone), and the final chord is a cadence TURN by position alone.
- **First Hindemith / harmonic-fluctuation (Kraftverlauf) method in the DB.** Rules-Based harmonic-tension counterpart to 145 DPBC (melodic contour tension), 006 Cadence & Closure (classical functional cadences), 066 GTTM-HC (prolongational tree); the first complete published tonal-harmony grammar (groups + progressions + centres + cadence) that is neither classical-functional nor serial.

---

## 1. The mathematics

### 1.1 Chord groups I–VI (the tension ladder)

Every chord (any combination of ≥ 3 tones, any intervals — Hindemith rejects tertian construction) is classified by **interval content** into six groups (Hindemith, Craft I, "Tabelle zur Akkordbestimmung"; transmitted verbatim by Wikipedia DE *Unterweisung im Tonsatz*):

| rule (interval content) | group |
|---|---|
| no tritone, no 2nds or 7ths | **I** — major/minor triads + 6th chords (6 chords: C E G, C E♭ G; C E♭ A♭, C E A, C F A, C F A♭) |
| no tritone, with 2nds or 7ths | **III** — sus/add/9th chords (largest class: 33 of 55 trichords) |
| tritone, **no minor 2nd, no major 7th** (tritone subordinate) | **II** — dominant 7ths, 7-9 chords, whole-tone stacks (root still determinable) |
| tritone, **with minor 2nd or major 7th** (tritone subordinate) | **IV** — dim-7-flavoured (m2/M7 + tritone) |
| root indeterminate (published): augmented triad {0,4,8}; {0,5,11} (C F B) | **V** |
| root indeterminate, **tritone dominant**: tones ⊆ {0,3,6,9} (diminished triad, dim7, inversions) | **VI** |

Tension ranks I < II < III < IV < V < VI (dissonance degree); the tritone is the load-bearing interval (presence → column B; subordination vs dominance → II/IV vs VI). **Verified (this document): all 84 example chords of the published table classify into their published groups; the 55 non-octave-doubled trichords within the octave distribute I=6, II=6, III=33, IV=5, V=2, VI=3.**

### 1.2 Root determination

The root is the **lower tone of the chord's most consonant interval** (octave ignored), with the Reihe-2 consonance ranking

$$P5 \succ P4 \succ M3 \succ m6 \succ m3 \succ M6 \succ M2 \succ m7 \succ m2 \succ M7 \succ \text{tritone}.$$

Verified: major/minor triad → root (= bass); dominant 7th → root; C E♭ A♭ → root E♭ (above the bass, P4 rule); sus2/sus4 → root. The inversion family (C E A, C F A, C F A♭ — Group I-2) is published as **root-above-bass** although the mechanical P5-first rule returns the bass (C–A is a P5) — Hindemith's rule is perceptual/heuristic, the published table is the authority (Pitfall 4).

### 1.3 Root progressions and their values

A chord sequence is reduced to its **root line** ("like applying logarithms in the realm of numbers"). Each step is scored by the interval class between roots (canonical published table, direction-symmetric):

| interval class (ascending) | unison | P5/P4 | M3/m3/M6/m6 | M2/m7 | m2/M7 | tritone |
|---|---|---|---|---|---|---|
| value | 0 | +2 | +1 | −1 | −2 | −3 |

The values are monotone along Reihe 2 (verified: [2,2,1,1,1,1,−1,−1,−2,−2,−3] non-increasing). Strongest motion = fifth/fourth (+2); weakest = tritone (−3); the steepest descent = minor second (−2).

### 1.4 Harmonic fluctuation (Kraftverlauf)

The **harmonic fluctuation** is the running sum of progression values over the root line:

$$F(t) = \sum_{i < t} v(\mathrm{root}_i, \mathrm{root}_{i+1}), \qquad v(a,b) = \text{value of interval class }(b-a) \bmod 12.$$

The curve is an explicit, closed-form tension profile: climb = LIFT, high plateau = TENSE, stepwise descent = resolution, cadential jump = TURN. Canonical examples (verified): I–V–I (C–G–C) → [0, 2, 4]; I–IV–V–I (C–F–G–C) → **[0, 2, 1, 3]** (rise into the subdominant, dip on the stepwise F→G, strongest cadential jump G→C); repeated tonic → flat. Unlike 145 DPBC's ballot law, the curve is a *profile*: it need not return to 0.

### 1.5 Tonal centres and cadence

- **Tonal centre (HOME):** three successive tritone-free chords whose roots form a broken triad fix a centre = the triad's root (verified: C–E–G → C; A–C–E → A; C–F–G is *not* a triad → no centre). With tritone chords, **two** suffice and the tonic is the root of the resolution chord (V7→I in 2 chords).
- **Stufengang (degree-progression):** the roots of large harmonic spans follow **Reihe 1** — the harmonic-series affinity order C, G, F, A, E, E♭, A♭, D, B♭, D♭, B, F♯ (verified identical to the *Ludus Tonalis* key order) — giving modulation by affinity.
- **Cadence (TURN):** a final chord becomes tonic **by position alone** — Hindemith accepts even unusual closing progressions (his example: minor sixth, minor second, tonic). Closure is structural, not functional.

### 1.6 Melodic grammar (abstract flank)

Melody = broken chords (**Melodiestufengang**, same degree rules, weakened) + **Sekundgang** (second-progression): stepwise lines connecting melodic high/low points; the ideal is both "in schöner Ausgeglichenheit" (beautiful balance). A rules-based melodic constraint (stepwise completion of leaps) — the harmonic flank of 081 NIRMC.

---

## 2. Python implementation sketch

```python
"""rules/hindemith_harmony.py -- abstract harmonic-plan generator (Method 146 HHFC)."""
# interval-content classification (pc sets, semitone distances)
TRITONE, M2, M7, m2, M7b = 6, 2, 10, 1, 11          # m2=1, M2=2, m7=10, M7=11

def classify_group(pcs: tuple[int, ...]) -> str:
    """Hindemith chord group I-VI by interval content + published V/VI exceptions."""
    iv = sorted(abs(a - b) for i, a in enumerate(pcs) for b in pcs[i + 1:])
    if set(pcs) in ({0, 4, 8}, {0, 5, 11}):          # rootless V (published)
        return "V"
    if len(pcs) >= 3 and set(pcs).issubset({0, 3, 6, 9}):   # dim7 family
        return "VI"
    tri, has2, has7 = 6 in iv, any(d in (1, 2) for d in iv), any(d in (10, 11) for d in iv)
    if not tri:
        return "I" if not (has2 or has7) else "III"
    return "II" if not (1 in iv or 11 in iv) else "IV"

RANK = {7:0, 5:1, 4:2, 8:3, 3:4, 9:5, 2:6, 10:7, 1:8, 11:9, 6:10}   # Reihe 2

def root_of(pcs: tuple[int, ...]) -> int:
    """Lower tone of the most consonant interval (Hindemith root rule)."""
    best = min(((abs(a - b), a) for i, a in enumerate(pcs) for b in pcs[i + 1:]),
               key=lambda t: (RANK[t[0]], t[1]))
    return best[1]

PROG_VALUE = {0: 0, 1: -2, 2: -1, 3: 1, 4: 1, 5: 2, 6: -3, 7: 2, 8: 1, 9: 1,
              10: -1, 11: -2}

def fluctuation(roots: list[int]) -> list[int]:
    """Harmonic fluctuation (Kraftverlauf) = cumulative sum of progression values."""
    out, acc = [0], 0
    for a, b in zip(roots, roots[1:]):
        acc += PROG_VALUE[(b - a) % 12]
        out.append(acc)
    return out

def tonal_centre(roots: list[int]) -> int | None:
    """3 tritone-free triad roots -> centre (triad root); else None."""
    if len(roots) != 3:
        return None
    s = set(roots)
    for c in s:
        if {(c + 3) % 12, (c + 7) % 12}.issubset(s) or {(c + 4) % 12, (c + 7) % 12}.issubset(s):
            return c
    return None

def tension_contract(roots, groups, seed):
    """Abstract-layer contract: group/root plan + fluctuation curve + centres.
    (register-invariant, tick-free; seed only for plan choice, not for the rules)."""
    return {"roots": roots, "groups": groups, "fluctuation": fluctuation(roots),
            "centres": [tonal_centre(roots[i:i+3]) for i in range(len(roots) - 2)],
            "cadence": "TURN-by-position on final chord", "seed": seed}
```

```python
"""generators/hindemith_harmony.py -- concrete adapter (abstract plan -> UnitMatrix)."""
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit, create_chord_unit

# per-group voicing: (root in bass? chord tones above C3)
VOICING = {"I":   (True,  [0, 4, 7]),
           "I-2": (False, [9, 0, 5]),     # root-above (6th-chord) family
           "II":  (True,  [7, 11, 2, 5]), # dominant 7th (tritone B-F)
           "III": (True,  [0, 5, 7]),     # sus
           "IV":  (True,  [7, 10, 1, 5]),
           "V":   (True,  [0, 4, 8]),
           "VI":  (True,  [0, 3, 6, 9])}

def plan_to_cells(roots, groups, section_ticks, c2=36, volume=96):
    """Each section = one chord: bass (root/bass placement) + chord unit + lead arp."""
    out = []
    for root, grp in zip(roots, groups):
        in_bass, tones = VOICING[grp]
        bass = c2 + 12 + (root if in_bass else (root + tones[1]) % 12)
        chord = [c2 + 24 + t for t in tones]
        out.append((bass, chord, section_ticks))
    return out

# engine loop:
# composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
# composer.create_matrix(3, 4); add_voice("Bass", BASS, 0) ...
# composer.fill_voice_section("Bass", "A", create_note_unit(bass_A, 3840))
# composer.fill_voice_section("Chord", "A", create_chord_unit(chord_A, 3840))
# ok, msg = composer.validate()   # zero-drift gate -- MUST be True
# composer.to_midi("hhfc.mid")
```

---

## 3. References

- **Hindemith, P. (1937).** *Unterweisung im Tonsatz I: Theoretischer Teil.* Schott, Mainz. English trans. A. Mendel (1942), *The Craft of Musical Composition, Book I: Theory.* — the classification table (pp. 86–98), root rule (pp. 66–70), progression values (pp. 96–100), harmonic fluctuation, tonal centres, cadence rule (pp. 113–120), melody (pp. 150–186). (Lending-restricted on archive.org — numeric value table cited from the published edition; classification verified live via Wikipedia DE's verbatim transcription.)
- **Wikipedia DE: "Unterweisung im Tonsatz"** (fetched 2026-11-19 via curl) — reproduces the complete classification table with all example chords; Reihe 1 table (C 64 Hz base: C, G, F, A, E, E♭, A♭, D, B♭, D♭, B, G♭/F♯); root rule statement; Grundtonschritte/logarithm analogy; Führungstöne; tonal-centre and cadence rules; Melodiestufengang/Sekundgang.
- **Wikipedia EN: "Paul Hindemith"** (fetched 2026-11-19) — "classifies chords in six categories, on the basis of dissonance, whether they contain a tritone, and whether they clearly suggest a root or tonal centre"; "tonal but non-diatonic… free use of all the twelve tones"; Ludus Tonalis description.
- **Wikipedia EN: "Ludus Tonalis"** (fetched 2026-11-19) — tonal centres proceed in "Serie 1": C–G–F–A–E–E♭–A♭–D–B♭–D♭–B–F♯ (cross-check 7, verified equal to Reihe 1).
- **Neumeyer, D. (1986).** *The Music of Paul Hindemith.* Yale University Press — authoritative secondary analysis of the progression values and fluctuation analyses.
- **Verified artifacts (this run, 2026-11-19):** `_web146_hhfc/verify_hhfc_math.py` (120/120 checks; 84/84 published-table chords; distribution I=6 II=6 III=33 IV=5 V=2 VI=3; curves [0,2,4] / [0,2,1,3]; Reihe 1 == Ludus Tonalis), `_web146_hhfc/compose_hhfc_demo.py` (engine demo, `validate() → True "OK"`, MIDI 780 B), outputs in `/opt/data/projects/Research/outputs/hhfc146/` (MIDI 780 B, WAV 3.8 MB, OGG 436 KB, provenance JSON). Sources fetched into `_web146_hhfc/`.
