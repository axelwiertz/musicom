# Report — HC-035 Shona Mbira Kushaura/Kutsinhira Interlocking (Two-Hand Ostinato + Inherent-Pattern Streaming)

**Date:** 2026-09-13
**Job:** daily-human-composition-research
**Method ID:** HC-035
**Layer:** concrete (target when implemented) — human-craft knowledge; realizes material through the UnitMatrix
**Next free ID after this:** HC-036

---

## 1. Method name & tradition

**Shona Mbira Kushaura/Kutsinhira Interlocking (Two-Hand Ostinato +
Inherent-Pattern Streaming).**

Southern African — the **mbira dzavadzimu** lamellophone tradition of the
**Shona people of Zimbabwe**, in the broader Eastern/Southern African
lamellophone family (mbira/sansi/kalimba, UNESCO Intangible Cultural Heritage
2020). Played at the all-night *bira* ancestor ceremony; paired players
interlock their parts around a cyclic melody, each hand locked into a
registered role, with the *audible* result being the "inherent patterns"
(phantom inner lines) that no single player physically plays.

**Rotation note:** prior tallies — Western Classical ×12, African/Afro-diasporic
×6, East/Southeast Asian ×5, Middle/Central Asian ×3, European folk ×3, Latin
American ×2, Arctic Indigenous ×1. This adds the first **Southern African**
entry and the first **lamellophone** tradition — distinct from the existing
West African Ewe (HC-005), Central African Pygmy (HC-014) and West African Kora
(HC-025) entries geographically and instrumentally.

## 2. Layer classification

`layer: concrete (target when implemented)` — same tag as every HC-* row. The
interlock is human-craft *knowledge*: no algorithmic generator in
`generator_registry`, no ABS-* spec. When implemented it maps to UnitMatrix
rows (kushaura spine + kutsinhira interlock + hosho pulse + vocal), with the
"inherent pattern" as the emergent sum of the two-part interlock.

## 3. Craft procedure (how a human does it, step by step)

1. **Tune to one named tuning** — *Nyamaropa* (~Mixolydian, oldest), *Mavembe*
   (~Phrygian), *Dongonda*, *Katsanzaira* (~Dorian), *Dambatsoko* (~Ionian).
   Heptatonic set fixed for the piece; no chromatic alteration mid-play.
2. **Learn orally** — master demonstrates tine positions + sung pattern; no
   staff notation.
3. **Fix the cycle** — closed loop (e.g. 4 phrases × 12 pulses = 48-pulse
   fundamental). Everything is its repetition or micro-variation.
4. **Partition hands** — LH thumb = low ostinato bass line; RH thumb+index =
   upper melody. Each hand rehearsed separately.
5. **Learn kushaura** — the leading/reference pattern (the "caller").
6. **Learn kutsinhira** — the responder's complementary phase-offset pattern
   landing in the kushaura's gaps and alternate pulses.
7. **Interlock** — the composite sounds denser/more continuous than either solo
   part; the 3:2 (hemiola) inside each part carries into the between-player
   relationship.
8. **Lay hosho pulse** — the gourd rattle's ground grid the mbira crosses.
9. **Add voice** — *huro* (high, emotional) + *mahon'era* (soft, low) at cycle
   boundaries.
10. **Play the bira** — sustain the loop for hours; the player hears the
    inherent patterns and varies *off* them (octave shift, passing note,
    register displacement), never rewriting the cycle. Variation drives trance;
    the cycle never yields.

## 4. Practitioner examples

- **Thomas Mapfumo** ("The Lion of Zimbabwe") — founded *chimurenga*; asked
  guitarist **Joshua Dube** (or per some sources **Jonah Sithole**) to
  *transcribe the mbira onto electric guitar*, transplanting the two-hand /
  interlock pattern onto guitar on *Take One* (1974).
- **Stella Chiweshe** — pioneering female mbira master, international
  ambassador of the dzavadzimu craft.
- **Ephat Mujuru** — early US teacher; *Dambatsoko* tuning named after the
  Mujuru ancestral burial grounds.
- **Dumisani Maraire** — brought marimba/mbira to the US Pacific Northwest;
  originated mbira nyunga-nyunga number notation.
- **Paul Berliner** — *The Soul of Mbira* (1978), canonical documentation of
  kushaura/kutsinhira and inherent patterns.
- **Erica Azim, Cosmas Magaya, Chartwell Dutiro** — dzavadzimu transmission to
  non-Shona students.
- **Garikayi Tirikoti** — "mbira orchestra" of seven tunings.
- Canonical pieces: *Nhemamusasa*, *Kariga Mombe*, *Taireva*, *Mahororo*,
  *Nyamaropa*, *Chakwi*.

## 5. UnitMatrix mapping (Musicom engine)

### Voices & Sections

| Voice | Role | Content | Invariance |
|---|---|---|---|
| Voice 0 | **kushaura spine** (leading mbira) | LH low ostinato bass + RH upper melody; reference pattern | cycle-locked, reference |
| Voice 1 | **kutsinhira interlock** (second mbira) | complementary phase-offset pattern filling V0 gaps | interlock offset fixed |
| Voice 2 | **hosho pulse** | gourd-rattle ground subdivision | continuous, invariant |
| Voice 3 | **vocal (huro/mahon'era)** | high + low register lines at cycle boundaries | register-polar pairing |
| Voice 4 | **optional transcription** | mbira composite doubled on guitar/keys (chimurenga) | composite mirror |

**Sections** = cyclic phrase units. Model the fundamental cycle as ONE section
plus a variation index (`C0 → C1 → C2 …`), not through-composed form — the
mbira is a closed loop with micro-variation. A bira macro-arc wraps
`cycle × N → vocal entry → climax → cycle returns`, density rising toward the
trance peak.

### Rules to encode

- **Cyclic invariance** — V0/V1 locked to fixed cycle length.
- **Hand partition** — LH = low ostinato (register floor), RH = upper melody
  (register ceiling); bass continuous, melody sparser.
- **Interlock offset** — kutsinhira onsets on complementary pulses; no unison
  at same pulse with kushaura.
- **3:2 hemiola floor** — between bass ostinato and upper melody in each part,
  and between players.
- **Heptatonic pitch-set constraint** — one tuning per piece; non-tempered
  intervals; 12TET quantization is a documented concession.
- **Hosho pulse invariance** — V2 never stops.
- **Inherent-pattern emergence** — composite density > any single hand (the
  interlock's own "continuous fill").
- **Variation-not-invention** — octave shift / passing note / register
  displacement only.
- **Vocal register pairing** — huro high + mahon'era low; no mid crowding.
- **Single-part-incomplete rule** — always two interlocked parts; a lone
  kushaura line is invalid output.

### Element mapping

**PITCH** (heptatonic tuning + hand-register partition, primary),
**RHYTHM** (3:2 cross-rhythm + hosho pulse + interlock offset, primary),
**TEXTURE** (interlocked pairing + inherent-pattern streaming, primary),
**STRUCTURE** (cyclic loop + variation-not-invention, secondary). **HARMONY**
implicit only — the low ostinato anchors a pedal/root, no functional
progression.

## 6. Table row added (human_methods_db.md)

```
| HC-035 | human (→concrete) | Shona Mbira Kushaura/Kutsinhira Interlocking (Two-Hand Ostinato + Inherent-Pattern Streaming) | Southern African — Shona mbira dzavadzimu lamellophone tradition (Zimbabwe); UNESCO ICH 2020; played at the bira ancestor ceremony | PITCH, RHYTHM, TEXTURE, STRUCTURE | Tune to one heptatonic tuning (Nyamaropa/Mavembe/Dongonda) → learn orally → fix closed cycle length → partition hands (LH=low ostinato bass, RH=upper melody) → learn kushaura reference part → learn kutsinhira responder phase-offset part filling kushaura gaps → interlock (composite > solo) → lay hosho gourd-rattle pulse → add huro (high) + mahon'era (low) vocal lines → play bira: listen for inherent patterns, vary by octave/passing-note/displacement, never rewrite cycle | Voice 0 = kushaura spine (LH ostinato + RH melody, reference, cycle-locked). Voice 1 = kutsinhira interlock (complementary phase-offset, fills V0 gaps). Voice 2 = hosho pulse (invariant ground grid). Voice 3 = vocal huro/mahon'era (register-polar). Voice 4 = optional guitar/key transcription (composite mirror, chimurenga). Sections = cyclic phrase units as one loop + variation index (C0→C1→C2), bira arc wraps cycle×N→vocal→climax→return. Rules: cyclic-invariance, hand-partition, interlock-offset (no unison), 3:2-hemiola-floor, heptatonic-set-constraint, hosho-invariance, inherent-pattern-emergence, variation-not-invention, vocal-register-pairing, single-part-incomplete gate | Thomas Mapfumo + Joshua Dube (chimurenga mbira-to-guitar transcription), Stella Chiweshe, Ephat Mujuru (Dambatsoko), Dumisani Maraire, Paul Berliner (The Soul of Mbira), Erica Azim, Cosmas Magaya, Chartwell Dutiro, Garikayi Tirikoti; pieces Nhemamusasa, Kariga Mombe, Taireva, Mahororo | ✅ Documented |
```

## 7. Verification

- `HC-035` present in detail file `human_method_HC-035_shona-mbira-kushaura-kutsinhira.md` ✓
- `HC-035` present in `human_methods_db.md` framework table ✓
- Highest ID = **HC-034** (prior); new = **HC-035**; next free ID = **HC-036** ✓
- No duplicate HC-035 in table ✓

## 8. Quirks / pitfalls

- **"Composition" is a misleading frame** — the composer designs an *interlock*,
  not a melody; the heard melody is an emergent sum. Encoding as a single lead
  line is exactly wrong.
- **Hand partition is the engine** — collapse LH/RH into one monophonic line and
  the 3:2 hemiola + inherent patterns vanish.
- **Kutsinhira ≠ harmony part** — it is a phase-offset interlock in the same
  register, not a chordal underlay; a naive harmonizer is a category error.
- **Tuning is non-tempered** — off the 12TET grid; document quantization as a
  compromise, do not silently bake in equal temperament.
- **Cycles, not sections** — through-composed A/B form loses the loop identity
  that drives the bira trance; use one cycle + variation index.
- **Single mbira = incomplete** — the pair rule is a hard gate or the core
  texture collapses.