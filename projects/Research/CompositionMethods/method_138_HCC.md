# Method 138 — Huffman Coding Composition (HCC)

**Paradigm:** Rules-Based · **Layer:** concrete · **Registered:** 2026-11-09
**Candidate code path:** `generators/huffman_code.py`
**Prototype:** `_web139/hcc_sketch.py` (runs on the musicom python; output `_web139/hcc_sketch_output.txt`, validate() OK, MIDI 906 B), fact-checks in `_web139/verify_138_HCC.py` (24 checks, all pass; log `_web139/verify_138_output.txt`)

---

## 1. The idea in one line

Compose the piece as a **message over a weighted motif vocabulary** and let Huffman's optimal prefix code *be* the music: the code tree is simultaneously the metric-subdivision skeleton (Kraft equality $\sum 2^{-\ell_i}=1$ tiles the bar exactly — zero drift by construction), the melodic decoder (codeword bits = stepwise contour: `0` down, `1` up), and the motivic non-overlap law (prefix-freeness).

## 2. The information theory

**Setup (Huffman 1952).** Alphabet $A=\{a_1,\dots,a_n\}$ with positive weights $W=(w_1,\dots,w_n)$ (frequencies/probabilities, usually $\sum w_i=1$). Output a prefix-free binary code $C(W)=(c_1,\dots,c_n)$ minimizing the **weighted path length**

$$L(C)=\sum_{i=1}^{n} w_i\,\ell_i,\qquad \ell_i=\mathrm{len}(c_i).$$

The greedy: repeatedly merge the two least-weight nodes into a new node of summed weight (priority queue, $O(n\log n)$; two-queue linear $O(n)$ when presorted, van Leeuwen 1976). The tree has $n$ leaves and $n-1$ internal nodes; every leaf depth $\ell_i\le n-1$ (verified).

**Kraft inequality (Kraft 1949).** Any prefix code over a $D$-ary alphabet satisfies

$$\sum_{i=1}^{n} D^{-\ell_i}\le 1,$$

with equality iff the code is **complete** (a full tree — every internal node has all $D$ children). Huffman codes over complete trees attain equality; verified for all five test weight sets to $10^{-9}$. Musical reading: $\ell_i$ = metric depth of motif $i$'s anchor; the bar holds $2^L$ slots, motif $i$ occupies $2^{L-\ell_i}$ of them; equality = the motifs **exactly tile the bar** — no gaps, no overlaps. This is a rhythmic zero-drift invariant *by construction* (the symbolic analogue of 111 VTCC's hocket, but from a probability budget instead of a rhythm factorization).

**Entropy bound (Shannon 1948; CLRS §16.3).** With $H=-\sum w_i\log_2 w_i$,

$$H\ \le\ L\ <\ H+1,$$

and $L=H$ exactly when all weights are dyadic ($w_i=2^{-\ell_i}$). Verified on normalized sets: wiki5 $H=2.2047$, $L=2.2500$; four $H=1.7394$, $L=1.8500$; zipf10 $H=2.8765$, $L=2.9340$; flat8 $L=H=3.0000$; dyadic $L=H=1.7500$.

**Optimality.** Huffman's code minimizes $L$ among all symbol-by-symbol prefix codes for a known i.i.d. distribution (exchange-argument proof). Verified by brute-force enumeration of *all* prefix codes: wiki5 $L=2.25$ and four $L=1.85$ are exact minima. Not globally optimal (arithmetic coding can do better); worst-case inefficiency $L-H$ is unbounded when some $w_i>1/2$ — cap with length-limited codes.

**Complexity.** Build $O(n\log n)$ (heap) / $O(n)$ (presorted two-queue); emit $O(N)$ per event. Deterministic: byte-identical per input.

## 3. The musical mapping

| Code object | Musical reading |
|---|---|
| weights $w_i$ | tonal gravity: rank-1 (heaviest) motif = HOME anchor; flat weights = TENSE |
| codeword $c_i$ | motif $i$'s melodic contour: bit `0` = one scale degree down, `1` = one up; step-sum = pitch offset from the voice anchor |
| prefix-freeness | motivic non-overlap: no contour is a prefix of another — unambiguous material (1-D counterpart of 112 CADDC's thumbtack) |
| $\ell_i$ (code length) | metric depth / rhythmic weight: rare motifs are short and fast ($2^{L-\ell_i}$ slots), salient motifs long and structural |
| Kraft equality | exact meter packing: motifs tile the bar, zero drift by construction |
| in-order leaf walk | the timeline: leaves fire left-to-right at their subtree starts (verified: spans tile $[0,2^L)$ exactly, onsets monotone) |
| entropy $H$ | tension/complexity knob: peaked weights = redundant HOME, flat = information-dense TENSE; $L-H$ = built-in predictability |
| adaptive Huffman (FGK/Vitter) | developing variation: the tree re-weights as the message unfolds; the sibling property (Gallager 1978) = a voice-leading law |
| canonical Huffman | a total order on codewords = scale-degree order: the code is a scale in disguise; lengths stable under re-encoding (literal repeats stay repeatable) |
| unequal letter costs (Karp 1961; Golin 1998) | leap-vs-step dial $(c_0,c_1)$: $c_1\approx c_0$ = conjunct, $c_1\gg c_0$ = leaping (constructive counterpart of 053 Lévy's $\alpha$) — requires Karp's DP, greedy is then suboptimal |
| n-ary Huffman | meter: complete $m$-ary subdivision tree iff $n\equiv 1\pmod{m-1}$ (verified: ternary 5 ✓ / 6 ✗, quaternary 10 ✓) — 3/4 needs 5,9,13… motifs, 4/4 needs 4,10,16… |
| length-limited (package-merge) | registral-range cap: $\ell_{\max}$ bounds melodic wander, $O(nL)$ |
| min-variance tie-break | balanced phrasing: merge oldest pair on ties; provably minimizes the longest codeword (verified: 9 equal weights → $\lceil\log_2 9\rceil=4$ vs comb's $n-1=8$) |

## 4. Musical Elements Framework

- **PITCH**: codewords = stepwise contours over a scale; canonical order maps codeword rank → scale-degree rank; unequal letter costs shape the interval vocabulary; blocked codes (pairs) = two-note gestures.
- **RHYTHM**: the in-order leaf schedule is the rhythm — onsets at weight-determined subtree starts, durations $2^{L-\ell_i}$; Kraft equality = perfect packing; arity = meter; $H$ = density knob.
- **HARMONY**: vertical tree slices = simultaneities; per-section weight vectors = chord functions; adaptive rotation = re-voicing (sibling property); canonical re-encoding = homometric re-voicing (same lengths, new labels).
- **STRUCTURE**: sections = successive weight vectors / re-weighted trees; entropy arc $H(\text{section})$ = tension curve; adaptive Huffman = continuous development; the code table is a compressed score — the piece is its own compression.
- **TEXTURE**: one tree per voice; polyphony = simultaneous in-order walks; per-voice Kraft budget = an information budget bounding density; depth = registral layer.

## 5. UnitMatrix Integration (Voices & Sections)

**Voices = rows = trees.** Row $v$ carries its own Huffman tree over the shared (or private) motif vocabulary; independent weight vectors = independent but budget-exact parts; per-voice child seed (`seed*101 + row`).

**Sections = columns = weight epochs.** Each column assigns a weight vector; column change = re-weighted tree = re-harmonization/development; the entropy arc across columns is the form's tension curve; per-column arity = meter changes.

**Cells = MusicUnit.** Per cell: in-order walk of the section's tree; each leaf → (pitch from codeword step-sum folded to the scale, onset at subtree start × slot, duration span × slot, velocity from weight rank). Leaves at the same slot become one chord unit. Every cell must end at `section_len` — pad via `_unit_from_events`; then `validate()`.

## 6. Implementation sketch (runs on the musicom python — `_web139/hcc_sketch.py`)

```python
import heapq, math
from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer

BAR = 1920                                    # ticks per bar

class _Node:
    __slots__ = ('w', 'sym', 'left', 'right')
    def __init__(self, w, sym=None, left=None, right=None):
        self.w, self.sym, self.left, self.right = w, sym, left, right
    def __lt__(self, o):                      # min-variance: leaves before internal on ties
        a = (self.w, 0 if self.sym is None else 1, self.sym or '')
        b = (o.w, 0 if o.sym is None else 1, o.sym or '')
        return a < b

def huffman(weights):                         # weights: [(sym, w)] -> (codes, root)
    heap = [_Node(w, s) for s, w in weights]
    heapq.heapify(heap)
    while len(heap) > 1:
        a, b = heapq.heappop(heap), heapq.heappop(heap)
        heapq.heappush(heap, _Node(a.w + b.w, None, a, b))
    codes = {}
    def walk(n, pre):
        if n.sym is not None:
            codes[n.sym] = pre
            return
        walk(n.left, pre + '0')
        walk(n.right, pre + '1')
    walk(heap[0], '')
    return codes, heap[0]

def in_order_schedule(root, L):               # (sym, start_slot, span_slots); tiles [0, 2^L)
    out = []
    def rec(n, start, span):
        if n.sym is not None:
            out.append((n.sym, start, span))
            return
        half = span // 2
        rec(n.left, start, half)
        rec(n.right, start + half, half)
    rec(root, 0, 2 ** L)
    return out

SCALE = [0, 2, 4, 5, 7, 9, 11]                # C-major degrees (semitones)

def pitch_for(code, anchor_deg, base):        # bit 0 = down, 1 = up; fold mod 7
    steps = sum(1 if b == '1' else -1 for b in code)
    return base + (anchor_deg + steps) // 7 * 12 + SCALE[(anchor_deg + steps) % 7]

def fill_cell(composer, voice, section, weights, L, slot):
    codes, root = huffman(list(zip(MOTIFS, weights)))
    events = []
    for sym, start_slot, span in in_order_schedule(root, L):
        rank = MOTIFS.index(sym) + 1
        events.append(MusicEvent(
            pitch=pitch_for(codes[sym], ANCHOR_DEG[voice][0], ANCHOR_DEG[voice][1]),
            volume=max(40, 104 - 8 * rank),
            start_tick=start_slot * slot,
            end_tick=(start_slot + span) * slot,
        ))
    composer.fill_voice_section(voice, section, MusicUnit(events=events))

# engine spine: create_matrix -> add_voice -> add_section -> fill_voice_section
# -> validate() (zero-drift gate, MUST be True) -> to_midi(out_path)
```

Measured (sketch run): all four sections show Kraft $=1.000000$; schedules tile the bar exactly (section A durations 960+240+240+120+30+30+60+240 = 1920 ticks); entropy arc $H$: A 2.400 → B 2.942 → A′ 2.518 → C 2.749 (HOME → TENSE → re-peak → cadence); `validate() -> True: OK`; MIDI 906 bytes.

## 7. References

- Huffman, D. A. (1952). "A Method for the Construction of Minimum-Redundancy Codes." *Proc. IRE* 40(9), 1098–1101. doi:10.1109/JRPROC.1952.273898
- Shannon, C. E. (1948). "A Mathematical Theory of Communication." *Bell Syst. Tech. J.* 27, 379–423 & 623–656
- Kraft, L. G. (1949). "A device for quantizing, grouping, and coding amplitude-modulated pulses." MIT MS thesis
- Fano, R. M. (1949). "The transmission of information." MIT RLE report (Shannon–Fano, the non-optimal predecessor)
- van Leeuwen, J. (1976). "On the construction of Huffman trees." *ICALP* 382–410 (linear-time two-queue build)
- Cormen, Leiserson, Rivest & Stein (2001). *Introduction to Algorithms*, 2nd ed., §16.3 (optimality proof; $H\le L<H+1$)
- Hu, T. C., & Tucker, A. C. (1971). "Optimal computer search trees and variable-length alphabetical codes." *SIAM J. Appl. Math.* 21(4), 514–532 (alphabetic/canonical codes; Garsia–Wachs 1977)
- Karp, R. M. (1961). "Minimum-redundancy coding for the discrete noiseless channel." *IRE Trans. IT* 7(1), 27–38; Golin, M. J. (1998). *IEEE Trans. IT* 44(5), 1770–1781 (unequal letter costs)
- Gallager, R. G. (1978). "Variations on a theme by Huffman." *IEEE Trans. IT* 24(6), 668–674 (adaptive FGK; sibling property)
- Vitter, J. S. (1987). "Design and analysis of dynamic Huffman codes." *J. ACM* 34(4), 825–845
- Wikipedia, "Huffman coding" (cached `_web138/wiki_huffman.html`; text `_web139/huffman.txt`)
- arXiv prior-art check (2026-11-09, `_web139/q_*.xml`): no musical use of Huffman/prefix/entropy coding found (see DB section ### Source)
- DB novelty check (2026-11-09): `huffman`/`prefix code`/`kraft`/`shannon-fano`/`codeword`/`source coding`/`entropy coding` all = 0 hits in `methods_db.md` before entry. Adjacent-but-different: 084 ZMRC (statistical rank-frequency), 130 SFT-C (entropy as measure), 002 Markov (probabilistic), 034 PCFG (grammar tree), 077 DBUC (exhaustive windows), 111 VTCC (additive tiling)

## 8. Pitfalls (full list in the DB section)

Kraft equality needs a complete tree (1) · symbol-by-symbol optimality only, no context (2) · unbounded worst case when $w_{\max}>1/2$ — use package-merge (3) · entropy ≠ valence, anchor HOME on the tonic (4) · in-order placement is tree geometry, not weights (5) · fold contours after decoding, never during (6) · adaptive Huffman changes repeats (7) · n-ary completeness restricts meters (8) · unequal letter costs invalidate the greedy (9) · zero-drift still needs `_unit_from_events` padding (10) · not a re-skin of 084/130/002/034/077/111 (11).
