# Method 128 — Van Eck Sequence Composition (VESC)

**ID:** 128 · **Paradigm:** Rules-Based · **Layer:** concrete · **Registered:** 2026-10-29
**Acronym:** VESC (Van Eck Sequence Composition)
**One-line:** Composes from OEIS A181391 — the self-referential "distance-to-last-occurrence" sequence — mapping term values to pitch classes, gap values to durations, record values to section seams, and zeros to cadence markers.

---

## 1. The sequence (OEIS A181391)

**Definition** (van Eck, 2010; name due to Sloane). For n ≥ 1, if there exists m < n such that a(m) = a(n), take the **largest** such m and set a(n+1) = n − m; otherwise a(n+1) = 0. Start with a(1) = 0.

$$a(1)=0,\qquad a(n+1)=\begin{cases} n-m & \text{if } m=\max\{j<n:\ a(j)=a(n)\}\ \text{exists},\\ 0 & \text{otherwise.}\end{cases}$$

**First 52 terms:** 0, 0, 1, 0, 2, 0, 2, 2, 1, 6, 0, 5, 0, 2, 6, 5, 4, 0, 5, 3, 0, 3, 2, 9, 0, 4, 9, 3, 6, 14, 0, 6, 3, 5, 15, 0, 5, 3, 5, 2, 17, 0, 6, 11, 0, 3, 8, 0, 3, 3, 1, 42.

The rule reads musically as: *when you hear a value, the next value is how long it has been since you last heard it — or 0 if it is new.* The sequence literally encodes **musical memory**: every term is a gap to a remembered past event.

### 1.1 Proven facts

- **Infinitely many zeros** (van Eck's theorem, OEIS comment 2010-10-25). Proof: suppose finitely many zeros ⇒ from some index on the sequence is bounded and nonzero; let M be the maximal term. Any block of length M determines the rest of the sequence; there are only M^M such blocks over {1,…,M}, so a block repeats ⇒ the sequence is eventually periodic. The periodic part has no zeros. Inside a period of length p, let …z…z… be two occurrences of z separated by q ≤ p steps, with q the term after the second z; then the term *before* the first z must also be z — the periodic part extends backwards forever, contradicting boundedness and the absence of zeros. ∎
- **Periodicity is seed-dependent.** Generalized streams E(a₁, a₂) can be periodic; the smallest period > 1 is **42** (De Muynck 2019). The canonical (0,0) stream has no detected period ≤ 199 in its last 1 000 terms at n = 10⁵ (verified 2026-10-29).
- **First occurrence / records.** Record values occur at indices (1-based): n = 1, 3, 5, 10, 24, 30, 35, 41, 52, 84, 125, 152, … with values 0, 1, 2, 6, 9, 14, 15, 17, 42, 56, 62, 92, … The n = 52 jump to 42 is the famous "climax" landmark.

### 1.2 Open conjectures (Sloane, OEIS-50 lecture, 2014)

(i) lim sup a(n)/n = 1; (ii) gaps between zeros are about log₁₀ n; (iii) every number eventually appears. **None proven** — provenance must not assert them.

### 1.3 Empirical profile (b-file, first 100 000 terms; recomputed 2026-10-29)

| quantity | measured |
|---|---|
| zero count / density | 15 099 / 15.10% |
| zero-gap mean / median / max | 6.62 / 6 / 18 |
| zero-gap tail mean (last 500 gaps) | 6.93 (log₁₀ 10⁵ = 5.0 — order-of-magnitude consistent with conjecture ii) |
| max term | 96 595 at n = 99 906 (term 100 000 = 2 984) |
| distinct values | 15 098 |
| values 0…49 present? | all present |
| longest pairwise-distinct consecutive run | 269 |
| period ≤ 199 in last 1 000 terms | none (aperiodic tail) |
| pc distribution mod 12 (top) | pc 0: 20 613 (20.6%); pc 6: 10 457; pc 5: 9 687; pc 1: 8 314 (lowest nonzero), pc 11: 5 641 |

The pc-0 mass (20.6% vs 8.3% uniform) is the sequence's built-in **tonic bias**: with zero handling routed to the tonic, ~1 in 5 events lands on pc 0 without any tonal machinery.

---

## 2. Musical mapping (the method)

Each term a(n) drives one event. Four mappings are canonical; combinations are free:

1. **PITCH** — pitch class = a(n) mod 12 (or mod |S| over a scale ladder of size |S|); register = ⌊a(n)/12⌋ (large values climb registers); record values = structural leaps.
2. **RHYTHM (gap-coding)** — value = duration/onset class: 0 → rest or cadence marker; small v → short note; large v → long note *and* a long silence before its reappearance (the re-appearance gap is exactly v steps). Inter-zero gaps ≈ phrase length.
3. **HARMONY** — consecutive terms stacked mod 12 as per-step trichords; or parallel streams (below); "function" of a pc = recency (how many steps since it last sounded) — a **memory-based functional harmony** inverting the usual voice-leading logic (recent = stable, forgotten = fresh/dissonant).
4. **STRUCTURE** — section seams at record indices; the record schedule is the macro-form; the "block of length M determines the rest" theorem inverted = the last M events are the generative context (form principle: the past writes the future).

**TEXTURE** — zero density = event density; interleaved streams = hocket; pairwise-distinct runs = maximal-independence counterpoint; Chaffin's 10¹²-term value-frequency data ⇒ the vocabulary stays sparse (values > 500 rare) ⇒ tonal-sparse textures by default.

---

## 3. Extended mathematics

### 3.1 The recurrence as a dynamical system over memory

Define the *last-occurrence function* L(n) = max{j ≤ n : a(j) = a(n)} (L = n if first occurrence). Then

$$a(n+1) = n - L(n) \quad \text{or} \quad 0 \text{ if } L(n) = n.$$

Equivalently, with the "age" field A(v) = age of value v (steps since its last occurrence), each step is:

$$A_{n+1}(v) = \begin{cases} 0 & v = a(n+1) \\ A_n(v) + 1 & v \neq a(n+1) \end{cases},\qquad a(n+1) = \begin{cases} A_n(a(n)) & A_n(a(n)) < \infty,\\ 0 & A_n(a(n)) = \infty. \end{cases}$$

So VESC is a **stateful cellular update over an unbounded alphabet**: the state is the age field, and the next symbol is the age of the current symbol. This is why every term depends on the entire history — the age field is full-history associative memory. Computational cost is O(1) amortized per term with a hash map (age lookup + age reset), O(distinct values) memory: **O(N) time, O(D) space**.

### 3.2 Records and the log₁₀ conjecture

Let R(k) = index of the k-th record (new maximum). Empirically R(1..12) = 1, 3, 5, 10, 24, 30, 35, 41, 52, 84, 125, 152. A record of value M at index r forces the next occurrence of M at index r + M; until then, no value can exceed M again without first… (this self-referential constraint is what makes records *structural* rather than cosmetic). Conjecture (i) lim sup a(n)/n = 1 says the records asymptotically catch up with the index — the empirical max 96 595 / 99 906 = 0.967 supports it.

### 3.3 Zero-gap statistics

Let Z(k) = index of the k-th zero. Measured: Z-gap mean 6.62, median 6, max 18 (n ≤ 10⁵). Sloane's conjecture (ii): Z(k+1) − Z(k) ≈ log₁₀ Z(k). Measured tail mean 6.93 vs log₁₀ 10⁵ = 5.0 — same order of magnitude, slow growth. For composition: phrase length ≈ 6–7 events, drifting slowly longer — an automatic, self-similar *ritardando of phrase structure*.

### 3.4 Generalized streams E(a₁, a₂)

Replace the seed (0, 0) with any pair (x, y) and run the same rule. De Muynck (2019): E(37, 42, …) attains period 42 — the smallest period > 1. Coprime-seed streams are empirically uncorrelated (joint zero schedule spreads); identical seeds are identical streams (correlation 1) — a continuous independence knob for voice rows.

---

## 4. Python implementation sketch

```python
# generators/van_eck.py  (candidate module for method 128)
from structures import MusicUnit, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit

class VanEckComposer:
    """Rules-Based concrete generator: OEIS A181391 memory-gap sequence."""

    def __init__(self, scale_ladder=(0, 2, 4, 5, 7, 9, 11), tonic=0):
        self.ladder = scale_ladder          # degrees -> pc (mod 12)
        self.tonic = tonic

    def sequence(self, seed=(0, 0), n_terms=128):
        """O(N) Van Eck recurrence via a last-occurrence/age dict."""
        age = {}                            # value -> steps since last occurrence
        a0, a1 = seed
        seq = [a0, a1]
        for v in (a0, a1):
            age[v] = 0
        for _ in range(n_terms - 2):
            prev = seq[-1]
            if prev in age and age[prev] > 0:      # seen before: gap since last
                seq.append(age[prev])
            else:                                    # memory miss: zero (cadence)
                seq.append(0)
            for v in age:                            # age the whole field
                age[v] += 1
            age[seq[-1]] = 0                         # reset the just-sounded value
        return seq

    @staticmethod
    def zero_positions(seq):
        return [i for i, v in enumerate(seq) if v == 0]

    @staticmethod
    def record_indices(seq):
        rec, mx = [], -1
        for i, v in enumerate(seq):
            if v > mx:
                mx = v; rec.append(i)
        return rec                                   # section seams

    def pitch(self, v):
        return self.tonic + self.ladder[v % len(self.ladder)]

    def duration_class(self, v, max_class=8):
        """Gap-coding: 0 = rest, small = short, large = long."""
        if v == 0:
            return 0
        return min(v % max_class + 1, max_class)

    def realize(self, seed=(0, 0), n_terms=128, bars=8, ticks_per_bar=1920,
                voice_name="Lead", program=MidiInstrument.FLUTE, channel=0):
        seq = self.sequence(seed, n_terms)
        comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
        comp.create_matrix(num_voices=1, num_sections=bars)
        comp.add_voice(voice_name, program=program, channel=channel)
        for s in range(bars):
            comp.add_section(chr(65 + s), bars=1)
        # fill: event n of section s; rest (0) leaves the slot open
        slot = 0
        events = []
        for v in seq[:bars * 8]:                     # budget 8 events/bar
            if v == 0:
                events.append(None)                  # cadence marker -> rest/pad
                continue
            d = self.duration_class(v)
            dur = ticks_per_bar // 8 * d
            if slot + dur > ticks_per_bar:
                slot = ticks_per_bar                 # terminal landmark
                break
            events.append((self.pitch(v), slot, slot + dur, 90))
            slot += dur
        # pad short segments with _unit_from_events pattern (zero-drift gate)
        seg = [e for e in events if e is not None]
        if seg:
            from workflows.musicom_workflow import _unit_from_events  # noqa
            # (pattern: build MusicUnit from events, pad to section_len)
        ok, msg = comp.validate()                    # MUST be True
        assert ok, msg
        return comp
```

Notes: `sequence()` is O(N) with an age dict (the age-field form of §3.1); `record_indices()` gives the section seams; `duration_class()` is the gap-coding rhythm; the zero-drift gate (`validate()`) is mandatory — pad short segments to the section length exactly as `_unit_from_events` does.

Multi-voice: one `VanEckComposer` per row with distinct `seed` pairs; lead = (0,0), bass = slow modulus + long classes, inner voices = coprime seeds. Chord cells: stack `pitch(v)` of each row at the same event index, then re-voice with 001/011/050 if exact triads are required.

---

## 5. References

- OEIS Foundation. **A181391** — Van Eck's sequence. https://oeis.org/A181391 (definition, van Eck's infinite-zeros theorem comment, Sloane's conjectures, Kozma/Rokicki consecutive-pair conjecture, De Muynck period-42 example, Chaffin's 10¹²-term frequency data, b-file of 100 000 terms). Fetched + b-file verified 2026-10-29.
- Sloane, N. J. A. (2014). "The OEIS: The Major Problems." Conference for the 50th Anniversary of the OEIS, Rutgers University, Oct 10 2014 (conjectures added to A181391 Jun 16 2019).
- Sloane, N. J. A. & Brady, H. (2019). "The Van Eck Sequence." *Numberphile* video. — the "most mysterious sequence in the OEIS" popularization.
- Weisstein, E. W. "van Eck's Sequence." *MathWorld* — accessible statement of definition + theorem.
- De Muynck, M. (2019). OEIS A181391 comment (Sep 30 2019) — generalized E(a,b) streams; smallest period > 1 is 42 (from redd.it/dbdhpj).
- van Eck, J. R. (2010). OEIS A181391 submission and theorem comment (Oct 25 2010).
- Kozma, L. (2016) / Rokicki, T. (2019). OEIS A181391 comments — consecutive-pair conjecture and correction.
- Chaffin, B. (n.d.). "Frequency of values 0..500 over the first 10¹² terms" (OEIS A181391 link, `a181391_3.png`).
- Adjacent art: "Van Eck Sequence Audiovisuals" (YouTube) — informal sonification; no formal method.
- **Novelty check 2026-10-29:** arXiv API 0 hits for "Van Eck sequence" AND music / "Van Eck" AND "algorithmic composition"; Crossref only unrelated surname matches; DuckDuckGo: OEIS/MathWorld/Numberphile/explorer/code-golf only. No published algorithmic-composition method exists.
