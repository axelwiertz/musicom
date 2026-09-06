# Tintinnabuli Composition (TINC) — Method 079

**Paradigm:** Rules-Based (Deterministic)
**Layer:** concrete
**ID:** 079
**Acronym:** TINC
**Tonal Gravity:** Strict (Static Triad)
**Metric Binding:** Grid-Locked / Continuous
**Memory Depth:** Meso / Phrase
**Time Complexity:** $\mathcal{O}(N)$

## One-line description
Realize Arvo Pärt's tintinnabuli style ("1 + 1 = 1"): project a stepwise diatonic M-voice note-by-note onto a single fixed tonic triad to form a triad-locked T-voice; every dyad contains exactly one triad tone, yielding constant consonance and a bell-like sacred-minimalist texture with no functional harmony.

## Source
Invented by **Arvo Pärt in 1976** after an eight-year silence (1968–1976) studying Gregorian chant and early polyphony. First heard in *Für Alina* (1976), *Cantus in Memoriam Benjamin Britten* (1977), *Tabula Rasa* (1977), *Spiegel im Spiegel* (1978), *Fratres* (1977). Pärt's own formulation is **"1 + 1 = 1"**: a melodic voice (the "subjective" human world) joins a triadic voice (the "objective" immutable triad), and the two are heard as one. Definitive analysis: Hillier (1997), *Arvo Pärt*, Oxford UP.

## Full math

Two voices from one mode $M$ and one tonic triad $T = \{c, e, g\}$.

**M-voice (stepwise):**
$$|m_{i+1} - m_i| \le 2 \quad \text{(semitones, within mode } M)$$

**T-voice (triad-locked projection)** with position sequence $p_i \in \{+1,-1\}$:
$$t_i = \begin{cases} \min\{t \in T : t \ge m_i\} & p_i = +1\ \text{(superior)} \\ \max\{t \in T : t \le m_i\} & p_i = -1\ \text{(inferior)} \end{cases}$$

Every sonority $(m_i, t_i)$ contains exactly one triad tone. There is no functional progression; the harmony is the static field of one triad, colored by which tone (root/third/fifth) each dyad contains and by the interval span (unison/second/third).

**Structure** = the position pattern $P$ (constant-above, constant-below, alternating, per-section) + additive processes (notes added/dropped one at a time, Cantus-style).

**Cost**: $\mathcal{O}(N)$ — one projection (binary search over sorted triad tones) + one note emission per M-note. Deterministic per seed.

## Python implementation sketch

```python
import bisect

def tintinnabuli(m_voice, triad, positions, octave_shift=0):
    """Project a stepwise M-voice onto a tonic triad (T-voice)."""
    tones = sorted(pc + 12 * o for o in range(-1, 9) for pc in triad)
    dyads = []
    for m, p in zip(m_voice, positions):
        i = bisect.bisect_left(tones, m)
        t = tones[min(i, len(tones)-1)] if p >= 0 else tones[max(i-1, 0)]
        dyads.append((m, t))
    return dyads

# C-Ionian stepwise M-voice, alternating above/below T-voice:
m = [60, 62, 64, 65, 64, 62, 60, 62]   # C D E F E D C D
pos = [+1, -1, +1, -1, +1, -1, +1, -1]
dyads = tintinnabuli(m, [0, 4, 7], pos)
# -> [(60,60),(62,60),(64,64),(65,64),(64,64),(62,60),(60,60),(62,60)]
```

## Musicom integration

```python
# from structures import MusicUnit, MidiInstrument
# from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit
# composer = UnitMatrixComposer(bpm=60, ticks_per_beat=480, beats_per_bar=4)
# composer.create_matrix(num_voices=2, num_sections=S)
# composer.add_voice("M-voice", program=MidiInstrument.FLUTE, channel=0)
# composer.add_voice("T-voice", program=MidiInstrument.MARIMBA, channel=1)
# for s, (mode, triad, pospat) in enumerate(section_specs):
#     m_line = stepwise_line(mode, n_notes=additive_len(s))
#     for i, (m, t) in enumerate(tintinnabuli(m_line, triad, pospat)):
#         composer.fill_voice_section("M-voice", s, create_note_unit(m, dur, tick=i))
#         composer.fill_voice_section("T-voice", s, create_note_unit(t, dur, tick=i))
# ok, msg = composer.validate()   # MUST be True before to_midi (per AGENTS.md)
```

## Candidate code path
`generators/tintinnabuli.py` — new module alongside `markov.py`, `euclidean.py`, etc. Exposes `stepwise_line(mode, n)`, `tintinnabuli(m_voice, triad, positions)`, and a `generate_section(mode, triad, pospat, n_notes)` that returns per-voice event lists for `UnitMatrixComposer.fill_voice_section`.

## Pitfalls
1. Unison collapse at triad tones is *idiomatic*, not a bug — keep unisons (they are the "1" in 1+1=1).
2. The T-voice must be a *function* of the M-voice, never free — a free T-voice degrades into broken chords.
3. Enforce $|m_{i+1}-m_i| \le 2$ on the M-voice or the chant quality is lost.
4. Keep the T-voice near the M-voice's octave (bell-like intimacy).
5. Position sequence $P$ must be slow and deterministic; random per-note flipping is non-Pärtian.
6. No chord progressions, no chromatic passing chords — the triad is the entire harmonic universe.
7. Decouple rhythm sparingly (additive breathing texture); strict homorhythm throughout sounds mechanical.

## References
- Pärt, A. (1976). *Für Alina*; (1977) *Cantus in Memoriam Benjamin Britten*, *Tabula Rasa*, *Fratres*; (1978) *Spiegel im Spiegel*.
- Hillier, P. (1997). *Arvo Pärt*. Oxford University Press.
- Kareda, S. (2007). "Back to the Source." In *Tintinnabuli: Music of Arvo Pärt*. Muziekcentrum Nederland.
- Pärt, A. (c. 1990s). "Tintinnabuli — mein persönlicher Weg."
