# HC-035 — Shona Mbira Kushaura/Kutsinhira Interlocking (Two-Hand Ostinato + Inherent-Pattern Streaming)

**Method ID:** HC-035
**Layer:** concrete (target when implemented) — human-craft knowledge; realizes material through the UnitMatrix
**Tradition:** Shona music of Zimbabwe — mbira dzavadzimu lamellophone tradition (Southern Africa)
**Primary Elements:** PITCH, RHYTHM, TEXTURE, STRUCTURE
**Status:** ✅ Documented

---

## 1. What it is

The **mbira dzavadzimu** ("voice of the ancestors") is the national instrument
of the Shona people of Zimbabwe — a lamellophone of 22–28 staggered metal tines
mounted on a wooden soundboard, set inside a large gourd resonator (*deze*).
Two to three players interlock their parts around a single cyclic melody, using
a two-hand division of labour (left thumb = low ostinato bass line, right
thumb + index = upper melody) and a **kushaura / kutsinhira call-and-interlock**
between players.

The craft signature documented here is not algorithmic: it is the **cognitive
phenomenon of "inherent patterns"** — the melodies a player *hears* emerging
from the interlocked, cross-rhythmic composite that no single hand literally
plays. A mbira player composes/improves by ear against these phantom inner
lines (auditory streaming), so the "composition method" is fundamentally about
*designing an interlock whose sum contains more music than either part states*.

Key facts anchoring this entry:

- **Two-hand partition**: left hand plays the low ostinato bass line, right hand
  plays the upper melody; the composite melody is an embellishment of a **3:2
  cross-rhythm (hemiola)**.
- **Kushaura / kutsinhira**: *kushaura* = the leading/reference part (the
  "caller"); *kutsinhira* = the responding second player who "interlocks" a
  complementary, phase-offset part into the first player's gaps (Paul Berliner,
  *The Soul of Mbira*).
- **A single mbira is incomplete**: Shona practice explicitly holds that
  polyrhythm only emerges with *two players at once* — pairing is mandatory.
- **Heptatonic, non-equal tuning**: low notes at centre of the keyboard, high
  notes fanning left and right; adjacent tines do not sit on the Western
  tempered grid. Named tunings: *Nyamaropa* (~Mixolydian, oldest), *Dambatsoko*
  (~Ionian, Mujuru lineage), *Dongonda*, *Katsanzaira* (~Dorian, highest),
  *Mavembe/Gandanga* (~Phrygian), *Nemakonde*, *Saungweme*.
- **Hosho** (gourd rattle) supplies the ground pulse; singers add **huro** (high
  emotional notes at top of range) and **mahon'era** (soft breathy low voice).
- Played at the **bira**, an all-night ancestor-spirit ceremony, where the
  cyclic repetition + micro-variation drives trance possession. UNESCO
  Intangible Cultural Heritage (2020).

---

## 2. Layer classification

`layer: concrete (target when implemented)` — same tag as all HC-* rows. The
mbira interlock is human-craft *knowledge*: no generator in
`generator_registry` and no ABS-* spec. When implemented it realizes a fixed
cyclic pattern as UnitMatrix rows (kushaura spine + kutsinhira interlock +
hosho pulse + vocal), with "inherent pattern" emergence as the encoded
behaviour of the two-part interlock.

---

## 3. Craft procedure (how a human does it, step by step)

1. **Tune to one named tuning** — select *Nyamaropa* / *Mavembe* / *Dongonda* /
   etc. The heptatonic set is fixed for the whole piece; no chromatic
   alteration during play.
2. **Learn the piece orally** — rote transmission: master demonstrates tines by
   position + a sung pattern (vocables); no staff notation.
3. **Fix the cyclic length** — the piece is a closed loop (e.g. 4 phrases × 12
   pulses = 48-pulse fundamental cycle). Everything is a repeat of, or a small
   variation on, this cycle.
4. **Partition the hands** — left thumb locks the low ostinato bass line
   (the harmonic-rhythm spine); right thumb + index carry the upper melody.
   Each hand's part is practiced in isolation first.
5. **Inhale the kushaura part** — the leading/reference pattern, learned
   note-for-note as the "caller's" version.
6. **Learn the kutsinhira part** — the responder's complementary pattern,
   designed so its onsets land in the *gaps* and on *alternate pulses* of the
   kushaura part (phase offset).
7. **Interlock** — both players play together; the composite must sound denser
   and more continuous than either solo part. The 3:2 relationship inside each
   hand's part (bass ostinato vs upper melody) carries over to the
   between-player interlock.
8. **Lay the hosho pulse** — the gourd rattle's ground pattern is the reference
   grid the mbira parts cross against.
9. **Add voice** — *huro* (high, emotional) and *mahon'era* (soft, low) weave
   around the mbira cycle; text/contour are secondary to register contrast.
10. **Play the bira** — sustain the loop for hours. The player *listens for the
    inherent patterns* (phantom inner melodies produced by the interlock) and
    plays small variations *off* them — octave shifts, passing notes, register
    displacement — never rewriting the cycle. Variation feeds trance; the cycle
    itself never yields.

---

## 4. Practitioner examples

- **Thomas Mapfumo** ("The Lion of Zimbabwe") — created *chimurenga*; asked
  guitarist **Joshua Dube** (per some sources **Jonah Sithole**) to *transcribe
  the mbira to electric guitar*, transplanting the two-hand/interlock mbira
  pattern onto guitar on *Take One* (1974).
- **Stella Chiweshe** — pioneering female mbira master; brought the dzavadzimu
  craft to international stages.
- **Ephat Mujuru** — early teacher of mbira dzavadzimu in the United States
  (Mujuru family; *Dambatsoko* tuning named after their ancestral grounds).
- **Dumisani Maraire** — brought marimba/mbira to the American Pacific
  Northwest; originated mbira nyunga-nyunga number notation.
- **Paul Berliner** — ethnomusicologist; *The Soul of Mbira* (1978) is the
  canonical documentation of kushaura/kutsinhira and inherent patterns.
- **Erica Azim, Cosmas Magaya, Chartwell Dutiro** — transmission of dzavadzimu
  repertoire to non-Shona students (Magaya/Azim method).
- **Garikayi Tirikoti** — "mbira orchestra" of seven tunings on one scale.
- Canonical pieces: *Nhemamusasa*, *Kariga Mombe*, *Taireva*, *Mahororo*,
  *Nyamaropa*, *Chakwi*.

---

## 5. UnitMatrix mapping (Musicom engine)

### Voices & Sections

| Voice | Role | Content | Invariance |
|---|---|---|---|
| Voice 0 | **kushaura spine** (leading mbira) | LH low ostinato bass line + RH upper melody; reference pattern | cycle-locked, reference form |
| Voice 1 | **kutsinhira interlock** (second mbira) | complementary phase-offset pattern filling Voice 0's gaps | interlock offset fixed |
| Voice 2 | **hosho pulse** | gourd-rattle ground pulse (subdivision grid) | continuous, invariant |
| Voice 3 | **vocal (huro/mahon'era)** | high + low register vocal lines woven at cycle boundaries | register-polar pairing |
| Voice 4 | **optional transcription layer** | mbira composite doubled on guitar/keys (chimurenga style) | composite mirror |

**Sections** = the cyclic phrase units. Model the fundamental cycle as ONE
section + a variation index (e.g. `C0 → C1 → C2 …`), NOT as through-composed
form: the mbira is a closed loop that repeats with micro-variation. For a bira
macro-arc, wrap sections as `cycle × N repetitions → vocal entry → climax →
cycle returns`, density increasing toward the trance peak.

### Rules to encode

- **Cyclic invariance** — Voice 0 & Voice 1 locked to a fixed cycle length; no
  phrase ever escapes the loop.
- **Hand partition** — LH = low ostinato (register floor), RH = upper melody
  (register ceiling); the bass line is continuous, the melody is sparser.
- **Interlock offset** — kutsinhira (Voice 1) onsets land on complementary
  pulse positions; strictly no unison at the same pulse with Voice 0.
- **3:2 cross-rhythm floor** — hemiola between bass ostinato and upper melody
  inside each part, and between the two players.
- **Heptatonic pitch-set constraint** — single named tuning per piece; no
  chromatic alteration; non-tempered intervals approximated to nearest scale
  degree (or 12TET quantization is a concession, not a feature).
- **Hosho pulse invariance** — Voice 2 never stops.
- **Inherent-pattern emergence** — composite line density > any single hand;
  this is the "sparse method + continuous fill" analog in the interlock itself.
- **Variation-not-invention** — octave shift, passing note, register
  displacement only; cycle identity preserved.
- **Vocal register pairing** — huro (high) + mahon'era (low); no mid-tessitura
  crowding against the mbira composite.
- **Single-part-incomplete rule** — always render two interlocked parts; a
  lone kushaura line is deliberately invalid output.

### Element mapping

**PITCH** (heptatonic tuning + hand-register partition, primary),
**RHYTHM** (3:2 cross-rhythm + hosho pulse + interlock offset, primary),
**TEXTURE** (interlocked pairing + inherent-pattern streaming, primary),
**STRUCTURE** (cyclic form + variation-not-invention, secondary).
**HARMONY** is implicit only — the low ostinato supplies a pedal/root anchor,
but there is no functional chord progression.

---

## 6. Quirks / pitfalls

- **"Composition" is a misleading frame** — the mbira composer *designs an
  interlock*, not a melody; the "melody" the listener hears is an emergent sum.
  Encoding it as a single lead line gets it exactly wrong.
- **Hand partition is the engine** — collapse LH/RH into one monophonic line
  and the 3:2 cross-rhythm (and the inherent patterns) vanish.
- **Kutsinhira ≠ harmony part** — it is a *phase-offset interlock*, pitched in
  the same register space, not a chordal underlay; naive "harmonizer" output is
  a category error.
- **Tuning is non-tempered** — Mbira tunings sit off the 12TET grid; treat
  nearest-scale-degree quantization as an audible compromise to document, not
  silently bake in.
- **Cycles, not sections** — modelling the piece as through-composed A/B form
  loses the loop identity that drives the bira trance; use a single cycle +
  variation index.
- **Single mbira = incomplete** — the pair rule is a hard gate or the core
  texture collapses.